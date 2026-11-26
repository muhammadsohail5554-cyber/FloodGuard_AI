"""Audit real district data and evaluate next-season regression without target leakage.

Run from the project root: python -m src.pipeline
All model selection uses 2024 validation; 2025 is used only for final reporting.
"""
from pathlib import Path
import hashlib
import json
import platform
import time
import joblib
import numpy as np
import pandas as pd
import sklearn
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.dummy import DummyRegressor
from sklearn.base import clone
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ['district_code', 'district_name', 'province_name', 'area_km2',
            'flooded_km2', 'pct_flooded', 'year']
FEATURES = ['prev_pct_flooded', 'area_km2', 'province_name']
SEED = 42

def validate_data(df):
    """Reject ambiguous keys, invalid targets, and physically inconsistent areas."""
    missing = sorted(set(REQUIRED) - set(df.columns))
    if missing:
        raise ValueError(f'Missing required columns: {missing}')
    if df.empty:
        raise ValueError('Dataset is empty.')
    d = df.copy()
    for col in ['district_code', 'district_name', 'province_name']:
        if d[col].isna().any():
            raise ValueError(f'Missing identifier: {col}')
        d[col] = d[col].astype(str).str.strip()
        if d[col].eq('').any():
            raise ValueError(f'Blank identifier: {col}')
    for col in ['year', 'area_km2', 'flooded_km2', 'pct_flooded']:
        d[col] = pd.to_numeric(d[col], errors='raise')
        if not np.isfinite(d[col]).all():
            raise ValueError(f'Non-finite value in {col}')
    if (d.year % 1 != 0).any():
        raise ValueError('Year must be an integer.')
    d['year'] = d.year.astype(int)
    if d.duplicated(['district_code', 'year']).any():
        raise ValueError('Duplicate district-year keys.')
    if (d.area_km2 <= 0).any() or (d.flooded_km2 < 0).any():
        raise ValueError('Area must be positive and flooded area nonnegative.')
    if not d.pct_flooded.between(0, 100).all():
        raise ValueError('Flooded percentage must be between 0 and 100.')
    expected = np.minimum(100, 100*d.flooded_km2/d.area_km2)
    if not np.allclose(expected, d.pct_flooded, atol=1e-6):
        raise ValueError('Flooded percentage does not match the source area formula.')
    for col in ['area_km2', 'province_name', 'district_name']:
        if (d.groupby('district_code')[col].nunique() > 1).any():
            raise ValueError(f'District metadata changes across years: {col}')
    return d.sort_values(['district_code', 'year']).reset_index(drop=True)

def load_data(path):
    """Read CSV and validate; preserve actionable file/schema errors."""
    return validate_data(pd.read_csv(path))

def make_supervised(d):
    """Join the exact preceding year; never treat a two-year gap as one lag."""
    prior = d[['district_code', 'year', 'pct_flooded']].copy()
    prior['year'] += 1
    prior = prior.rename(columns={'pct_flooded': 'prev_pct_flooded'})
    result = d.merge(prior, on=['district_code', 'year'], how='inner', validate='one_to_one')
    return result[['district_code', 'district_name', 'year', *FEATURES, 'pct_flooded']].sort_values(['year', 'district_code']).reset_index(drop=True)

def make_model(kind, geography=True):
    """All learned preprocessing is fitted inside the training pipeline."""
    numeric = ['prev_pct_flooded', 'area_km2'] if geography else ['prev_pct_flooded']
    transformers = [('numeric', Pipeline([('impute', SimpleImputer(strategy='median')),
                                            ('scale', StandardScaler())]), numeric)]
    if geography:
        transformers.append(('province', OneHotEncoder(handle_unknown='ignore', sparse_output=False), ['province_name']))
    estimator = {'ridge': Ridge(alpha=10),
                 'forest': RandomForestRegressor(n_estimators=300, max_depth=6,
                           min_samples_leaf=5, random_state=SEED, n_jobs=1),
                 'median': DummyRegressor(strategy='median')}[kind]
    return Pipeline([('prepare', ColumnTransformer(transformers)), ('model', estimator)])

def predict_checked(model, frame):
    """Predict bounded percentages; reject malformed demo inputs."""
    missing = set(FEATURES)-set(frame.columns)
    if missing or frame.empty:
        raise ValueError(f'Empty input or missing features: {sorted(missing)}')
    for col in ['prev_pct_flooded','area_km2']:
        if not np.isfinite(pd.to_numeric(frame[col], errors='raise')).all():
            raise ValueError(f'Invalid value: {col}')
    if not frame.prev_pct_flooded.between(0,100).all() or (frame.area_km2 <= 0).any():
        raise ValueError('Previous flood percentage must be 0-100 and area > 0.')
    if frame.province_name.isna().any() or frame.province_name.astype(str).str.strip().eq('').any():
        raise ValueError('Province is required.')
    return np.clip(model.predict(frame[FEATURES]), 0, 100)

def metrics(y, prediction):
    mse = mean_squared_error(y, prediction)
    return {'mae': float(mean_absolute_error(y,prediction)), 'mse': float(mse),
            'rmse': float(np.sqrt(mse)), 'r2': float(r2_score(y,prediction))}

def audit(d, raw_path):
    return {'rows': len(d), 'columns': len(d.columns), 'districts': int(d.district_code.nunique()),
            'years': sorted(map(int,d.year.unique())), 'missing': d.isna().sum().to_dict(),
            'duplicates': int(d.duplicated().sum()), 'duplicate_keys': int(d.duplicated(['district_code','year']).sum()),
            'zero_target_count': int(d.pct_flooded.eq(0).sum()),
            'year_summary': d.groupby('year').pct_flooded.agg(['count','mean','median','max']).round(6).reset_index().to_dict('records'),
            'province_counts': d[d.year.eq(2022)].province_name.value_counts().to_dict(),
            'raw_md5': hashlib.md5(Path(raw_path).read_bytes()).hexdigest(),
            'raw_sha256': hashlib.sha256(Path(raw_path).read_bytes()).hexdigest()}

def save_plot(path):
    plt.tight_layout()
    plt.savefig(path, dpi=170, bbox_inches='tight')
    plt.close()

def eda(d, path):
    """Exploratory plots use development years only, before final test evaluation."""
    path.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    dev=d[d.year<2025]
    fig,ax=plt.subplots(figsize=(8,3.7)); ax.hist(dev.pct_flooded,bins=30,color='#167D9A')
    ax.set(xlabel='District area flooded (%)',ylabel='District-season records',title='Development data: many low values and a long upper tail')
    save_plot(path/'01_distribution.png')
    fig,ax=plt.subplots(figsize=(8,3.7)); years=sorted(dev.year.unique())
    ax.boxplot([dev.loc[dev.year.eq(y),'pct_flooded'] for y in years],tick_labels=years)
    ax.set(xlabel='Monsoon season',ylabel='District area flooded (%)',title='Development seasons differ substantially')
    save_plot(path/'02_year_comparison.png')
    fig,ax=plt.subplots(figsize=(8,3.7)); vals=dev.groupby('province_name').pct_flooded.mean().sort_values()
    vals.plot.barh(ax=ax,color='#167D9A');ax.set(xlabel='Unweighted mean of district percentages (%)',ylabel='',title='Development exposure varies by province / territory')
    save_plot(path/'03_province_exposure.png')
    lag=make_supervised(d); lag=lag[lag.year<2025]
    fig,ax=plt.subplots(figsize=(8,3.7))
    for year, group in lag.groupby('year'): ax.scatter(group.prev_pct_flooded,group.pct_flooded,s=20,alpha=.65,label=str(year))
    ax.set(xlabel='Previous season flooded (%)',ylabel='Current season flooded (%)',title='Past flooding is informative, but not a direct forecast');ax.legend(title='Target year')
    save_plot(path/'04_lag_relationship.png')

def run(root=ROOT):
    root=Path(root); raw=root/'data/raw/District_Level_Data.csv'; d=load_data(raw)
    for sub in ['data/processed','reports/figures','models','evidence']:(root/sub).mkdir(parents=True,exist_ok=True)
    a=audit(d,raw); (root/'reports/data_audit.json').write_text(json.dumps(a,indent=2))
    d.to_csv(root/'data/processed/district_clean.csv',index=False)
    s=make_supervised(d);s.to_csv(root/'data/processed/supervised_lag1.csv',index=False)
    train=s[s.year.eq(2023)]; val=s[s.year.eq(2024)]; test=s[s.year.eq(2025)]
    if min(len(train),len(val),len(test))==0: raise ValueError('Need nonempty 2023/2024/2025 chronological splits.')
    eda(d,root/'reports/figures')
    candidates={'E1_Ridge_lag':make_model('ridge',False), 'E2_Ridge_geography':make_model('ridge'),
                'E3_Random_forest':make_model('forest')}
    rows=[]
    for name, model in candidates.items():
        start=time.perf_counter();model.fit(train[FEATURES],train.pct_flooded)
        rows.append({'experiment':name,**metrics(val.pct_flooded,predict_checked(model,val)), 'fit_seconds':time.perf_counter()-start})
    val_results=pd.DataFrame(rows);val_results.to_csv(root/'reports/validation_metrics.csv',index=False)
    chosen=val_results.sort_values(['mae','experiment']).iloc[0].experiment
    # Selection is locked here, before reading test outcomes.
    (root/'evidence/selection.json').write_text(json.dumps({'selected':chosen,'rule':'Lowest 2024 validation MAE among E1-E3; no test tuning','seed':SEED},indent=2))
    development=s[s.year<2025]; test_rows=[]; preds=test[['district_code','district_name','province_name','year','pct_flooded']].copy()
    for name, template in {**candidates,'B0_Training_median':make_model('median')}.items():
        model=clone(template).fit(development[FEATURES],development.pct_flooded)
        prediction=predict_checked(model,test); preds[name]=prediction
        test_rows.append({'experiment':name,**metrics(test.pct_flooded,prediction)})
        if name==chosen: joblib.dump(model,root/'models/selected_model.joblib')
    preds['B1_Persistence']=test.prev_pct_flooded.to_numpy()
    test_rows.append({'experiment':'B1_Persistence',**metrics(test.pct_flooded,preds.B1_Persistence)})
    test_results=pd.DataFrame(test_rows); test_results.to_csv(root/'reports/test_metrics.csv',index=False)
    preds['selected_prediction']=preds[chosen];preds['absolute_error']=abs(preds.pct_flooded-preds.selected_prediction)
    preds.to_csv(root/'reports/test_predictions.csv',index=False)
    groups=preds.groupby('province_name').apply(lambda g:pd.Series({'n':len(g),'mae':g.absolute_error.mean(),'mean_actual':g.pct_flooded.mean(),'mean_predicted':g.selected_prediction.mean()}),include_groups=False).reset_index()
    groups.to_csv(root/'reports/province_errors.csv',index=False)
    preds.nlargest(10,'absolute_error').to_csv(root/'reports/largest_errors.csv',index=False)
    fig,ax=plt.subplots(figsize=(8,3.7)); ax.scatter(preds.pct_flooded,preds.selected_prediction,color='#167D9A',alpha=.7)
    limit=max(preds.pct_flooded.max(),preds.selected_prediction.max())+1;ax.plot([0,limit],[0,limit],'--',color='#AB6325')
    ax.set(xlabel='Observed 2025 flooded (%)',ylabel='Predicted flooded (%)',title=f'Final holdout: {chosen}');save_plot(root/'reports/figures/05_test_predictions.png')
    fig,ax=plt.subplots(figsize=(8,3.7)); ax.barh(test_results.experiment,test_results.mae,color=['#167D9A']*3+['#87949D']*2)
    ax.set(xlabel='2025 mean absolute error (percentage points)',title='Final comparison - selection was made on 2024');save_plot(root/'reports/figures/06_test_mae.png')
    selected=test_results.set_index('experiment').loc[chosen];base=test_results.set_index('experiment').loc['B1_Persistence']
    summary={'selected_model':chosen,'selection_rule':'2024 validation MAE, E1-E3 only',
             'train_rows':len(train),'validation_rows':len(val),'refit_rows':len(development),'test_rows':len(test),
             'test_metrics':selected.to_dict(),'improvement_vs_persistence_pct':float(100*(1-selected.mae/base.mae)),
             'success_1_mae_le_5':bool(selected.mae<=5),'success_2_10pct_better_than_persistence':bool(selected.mae<=.9*base.mae),
             'python':platform.python_version(),'sklearn':sklearn.__version__,'pandas':pd.__version__,'numpy':np.__version__,
             'geographic_scope':'Future seasons for the same 160 districts; not unseen-district validation'}
    (root/'reports/run_summary.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2));return summary

if __name__=='__main__': run()
