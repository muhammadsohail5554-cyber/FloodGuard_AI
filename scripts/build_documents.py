"""Rebuild report, proposal, audit and presentation PDF from actual run outputs."""
from pathlib import Path
import json
import csv
from html import escape
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfgen import canvas

ROOT=Path(__file__).resolve().parents[1]
R=ROOT/'reports';FIG=R/'figures'
summary=json.loads((R/'run_summary.json').read_text())
audit=json.loads((R/'data_audit.json').read_text())
validation=pd.read_csv(R/'validation_metrics.csv')
test=pd.read_csv(R/'test_metrics.csv')
regional=pd.read_csv(R/'province_errors.csv')
errors=pd.read_csv(R/'largest_errors.csv')
NAMES='M.Sohail (16032)  |  M.Umar (16031)'
NAVY=colors.HexColor('#123349');TEAL=colors.HexColor('#137F94');GRAY=colors.HexColor('#52606A')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyFG',fontName='Helvetica',fontSize=10.2,leading=14.7,spaceAfter=9,textColor=NAVY))
styles.add(ParagraphStyle(name='TitleFG',fontName='Helvetica-Bold',fontSize=25,leading=29,spaceAfter=16,textColor=NAVY))
styles.add(ParagraphStyle(name='HeadingFG',fontName='Helvetica-Bold',fontSize=15,leading=19,spaceAfter=10,textColor=TEAL))
styles.add(ParagraphStyle(name='SmallFG',fontName='Helvetica',fontSize=8.3,leading=11,spaceAfter=6,textColor=GRAY))
styles.add(ParagraphStyle(name='CellFG',fontName='Helvetica',fontSize=8.5,leading=11,textColor=NAVY))

def p(text,style='BodyFG'):return Paragraph(escape(str(text)).replace('\n','<br/>'),styles[style])
def table(headers,rows,widths=None):
    rows=[[p(x,'CellFG') for x in headers]]+[[p(x,'CellFG') for x in row] for row in rows]
    t=Table(rows,colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E7F1F4')),('VALIGN',(0,0),(-1,-1),'TOP'),
                           ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),
                           ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),
                           ('LINEBELOW',(0,0),(-1,0),.5,TEAL),('LINEBELOW',(0,1),(-1,-1),.25,colors.HexColor('#DCE3E7'))]))
    return t

def footer(c,doc):
    c.setFont('Helvetica',8);c.setFillColor(GRAY)
    c.drawString(44,28,'FloodGuard AI  |  Programming for Artificial Intelligence  |  Fall 2026')
    c.drawRightString(551,28,str(doc.page))

def write_pdf(name,pages):
    story=[];md=[]
    for i,page in enumerate(pages):
        if i:story.append(PageBreak())
        title,blocks=page;story.append(p(title,'TitleFG' if i==0 else 'HeadingFG'));md.append('# '+title+'\n')
        for block in blocks:
            if isinstance(block,str):story.append(p(block));md.append(block+'\n')
            elif block[0]=='table':
                _,heads,rows,widths=block;story.append(table(heads,rows,widths));story.append(Spacer(1,10))
                md.append('| '+' | '.join(heads)+' |\n| '+' | '.join(['---']*len(heads))+' |\n'+'\n'.join('| '+' | '.join(map(str,row))+' |' for row in rows)+'\n')
            elif block[0]=='image':
                _,filename,caption=block;im=Image(str(FIG/filename));ratio=im.imageHeight/im.imageWidth;im.drawWidth=493;im.drawHeight=493*ratio
                story.append(im);story.append(p(caption,'SmallFG'));md.append('!['+caption+'](figures/'+filename+')\n')
            elif block[0]=='small':story.append(p(block[1],'SmallFG'));md.append(block[1]+'\n')
    SimpleDocTemplate(str(R/(name+'.pdf')),pagesize=(595.28,841.89),leftMargin=44,rightMargin=44,topMargin=42,bottomMargin=45,title=name.replace('_',' '),author=NAMES).build(story,onFirstPage=footer,onLaterPages=footer)
    (R/(name+'.md')).write_text('\n'.join(md),encoding='utf-8')

metric_rows=[[r.experiment,f'{r.mae:.3f}',f'{r.mse:.3f}',f'{r.rmse:.3f}',f'{r.r2:.3f}'] for r in test.itertuples()]
val_rows=[[r.experiment,f'{r.mae:.3f}',f'{r.rmse:.3f}',f'{r.r2:.3f}'] for r in validation.itertuples()]

body=[
('FloodGuard AI',[
 'Next-season district flood-exposure estimation across Pakistan',
 NAMES,
 'City University of Science & Information Technology (CUSIT)\nProgramming for Artificial Intelligence | Fall 2026\nCourse coordinator: Syed Muhammad Mohuddin\nPrepared: 24 November 2026',
 'Executive summary',
 'FloodGuard AI evaluates a small, transparent regression workflow for estimating the percentage of a district that will be detected as flooded in the next monsoon season. The proposed users are district preparedness analysts who need evidence about whether historical exposure can support preliminary research. No stakeholder consultation or institutional adoption is claimed.',
 'The real source dataset contains 640 district-season records: 160 districts observed in 2022–2025. An exact previous-year join produces 480 supervised examples. The model uses prior-season flooded percentage, district area and province, while excluding current-season flood measurements and derived spatial statistics. Three experiments compare two Ridge configurations with a Random Forest.',
 'Training targets are from 2023 and model selection uses 2024. After configuration selection, the model is refitted on 2023–2024 and evaluated on the untouched 2025 target period. The selected forest obtains MAE 2.726 percentage points, RMSE 6.016 and R² -0.978. Persistence obtains MAE 4.388, while the training-median benchmark obtains a better MAE of 2.474.',
 'The central finding is therefore a limitation: prior exposure and coarse geography do not establish dependable next-season predictive value. This package supplies a reproducible baseline, honest error analysis, executable demonstration and evidence for further research. It must not guide evacuation, compensation or operational resource allocation.',
 ('small','The report has ten body pages, followed by references. Detailed dictionaries, raw/clean data, metrics, tests, contribution plan and execution evidence accompany it. Git hosting is omitted at the user’s request; course compliance gaps are recorded separately.')]),
('2. Problem, stakeholder and objectives',[
 'Pakistan’s floods create a clear public-service problem. The 2022 post-disaster assessment reported damages and economic losses exceeding USD 30 billion [2]. This establishes the value of better preparedness, but does not imply that a small classroom model can supply safe operational advice.',
 'The proposed stakeholder is a district-level disaster-preparedness analyst. The analytical question is: for a district already present in the historical dataset, how accurately can the next season’s detected flooded percentage be estimated using information from the preceding season and static district metadata? The unit of prediction is a district-season, not a household, person or individual storm.',
 'The target is pct_flooded in target year t. Inputs are pct_flooded in t-1, area_km2 and province_name. This deliberately modest scope avoids inventing rainfall, river-flow, elevation or socioeconomic observations that the supplied data do not contain. It is a retrospective one-season-ahead evaluation, not an hourly or daily forecast.',
 ('table',['Criterion fixed before fitting','Evaluation rule','Observed outcome'],[
 ['C1: typical absolute error','2025 MAE ≤ 5 percentage points','2.726; met'],
 ['C2: beat a simple historical rule','At least 10% lower 2025 MAE than persistence','37.9% lower; met'],
 ['Additional diagnostic','Compare a training-median model and R²','Median is better; R² is negative']],[150,185,172]),
 'The criteria are educational design targets selected before the experiments. They were not set by a disaster-management authority. Their fulfilment is insufficient for deployment: the additional benchmark exposes a weakness that the first two criteria miss. A future acceptance test should require robust improvement across several unseen seasons and meaningful regional performance.',
 'The intended output is a reproducible table of estimates and errors that an analyst can inspect. It does not measure deaths, displacement, damage, crop loss or the probability that flooding will occur. Flood exposure and social vulnerability are different concepts. A low predicted percentage cannot establish that a district is safe.',
 'Problem approval is not evidenced. Flood preparedness fits the broad public-services motivation, but the final problem statement and the two-member team arrangement still need the course coordinator’s resolution.']),
('3. Background, related sources and dataset choice',[
 'The selected Zenodo record provides annual exposure summaries and spatial statistics [1]. Its district table directly matches a district-level analytical question. The project uses these observations to test next-season prediction; the source itself should not be interpreted as an operational forecasting model.',
 'The World Bank assessment [2] motivates preparedness through documented disaster impacts. FAO’s crop and flood products [3] show an alternative use of spatial observations for agricultural impact assessment. Those products could support later validation or additional features, but their imagery and crop labels are not part of the implemented training data.',
 'FloodTraces [4] describes complementary displacement, mobility and climate material. Its record is restricted, and combining such sources would require appropriate access and reconciliation of administrative codes. No restricted files are redistributed. scikit-learn’s guidance on leakage and metric selection [5,6] informs the evaluation design and the interpretation of regression error.',
 ('table',['Candidate','Observed size / time','Decision'],[
 ['District table [1]','640 rows; 13 columns; 160 units; 2022–2025','Selected: direct stakeholder fit and manageable audit'],
 ['Tehsil table [1]','2,308 rows; 11 columns; 577 units; 2022–2025','Compared and bundled; finer scale but no extra seasons'],
 ['FloodTraces [4]','Multiple data types; restricted record','Contextual alternative only; no model use']],[124,182,201]),
 'The two downloaded tabular candidates have no missing cells or duplicate unit-year keys. They are related products from the same publisher, not independent validation datasets. More tehsil rows would not fix the principal weakness: only four seasons are available. Finer spatial units also increase alignment work and do not justify a random split across correlated locations.',
 'The gap addressed is a small reproducible test of temporal transfer. The design asks whether earlier exposure plus simple geography predicts a later season better than basic alternatives. It does not claim a new satellite algorithm or a validated hydrological model. The outcome is useful even when the proposed model fails to outperform a constant benchmark.']),
('4. Dataset audit, dictionary and preparation',[
 'The source is attributed to Abdullah Umer, Zenodo version 1, DOI 10.5281/zenodo.20100773, under CC BY 4.0 [1]. The district CSV supplied by the user exactly matches the publisher’s MD5. The tehsil CSV and original dictionary were downloaded on 24 November 2026 and also match published checksums. Raw bytes remain unchanged; provenance records include SHA-256 hashes.',
 ('table',['Audit item','Finding'],[
 ['Rows / columns / unique districts','640 / 13 / 160'],['Season coverage','160 observations in each of 2022, 2023, 2024, 2025'],
 ['Missing cells / duplicate rows / duplicate keys','0 / 0 / 0'],['Zero target values',str(audit['zero_target_count'])+' district-season observations'],
 ['Categorical groups','Seven province/territory labels; metadata stable per district'],['Supervised rows','480 after exact preceding-year join']],[185,322]),
 'district_code is the joining key; district_name is a reporting label; province_name is categorical. area_km2 describes district area. flooded_km2 and pct_flooded describe the observed season. year establishes temporal order. gi_z, hotspot, lisa_quad, lisa_p, z_val and z_lag describe spatial statistics derived from the seasonal exposure. The full dictionary is included separately [7].',
 'The pipeline strips identifier whitespace, converts core numeric fields, checks finite values and positive areas, rejects duplicate district-year keys, and verifies the capped area-ratio formula. It sorts rows without dropping legitimate extreme observations. Missing targets are rejected rather than imputed. Because the current source is complete, training imputation serves only as a pipeline safeguard and does not modify any observed target.',
 'A zero denotes no detected flood extent in the source, not guaranteed absence of flooding. The publisher documents detection limitations; the project has no independent ground-truth validation. Boundary coverage reflects this source’s 160-unit snapshot and should not be read as a claim about every current administrative unit. No personal records are present; team names identify authors, not training subjects.']),
('5. Exploratory analysis and feature decisions',[
 'Exploratory plots use only 2022–2024. The 2025 holdout is reserved for final diagnostics. This boundary prevents later-season observations from shaping feature or model decisions. The source audit still checks the complete file’s schema and integrity; this does not fit preprocessing parameters or choose a model.',
 ('image','01_distribution.png','Figure 1. Development target distribution; district-season records are concentrated at low percentages with a long upper tail.'),
 'This skew motivates a robustly interpretable primary metric, MAE, and a median predictor. RMSE is retained because a few large mistakes can matter greatly. No target threshold is invented to turn the problem into classification, and no classification accuracy or confusion matrix is therefore appropriate.',
 ('table',['Additional EDA figure','Interpretation and consequence'],[
 ['02_year_comparison.png','Development means: 13.280% in 2022, 4.897% in 2023, 5.667% in 2024. Seasonal shifts motivate time ordering.'],
 ['03_province_exposure.png','Regional exposure differs. Province is tested as a feature; these are unweighted district means, not province-area flood rates.'],
 ['04_lag_relationship.png','Year-to-year relationships are imperfect and differ by target year. Compare persistence and a nonlinear alternative.']],[152,355]),
 'All four full-size charts and individual explanations are available in the notebook and reports folder. Current-year flooded area and every current-year spatial statistic are excluded despite their apparent association with the target. That association would be unavailable before the season and would inflate reported predictive skill.']),
('6. Methodology and chronological evaluation',[
 'An exact self-join links each district in target year t to that district’s observation in t-1. It is keyed by district_code and the shifted year, with one-to-one validation. The 160 first-year rows cannot be target examples because 2021 is absent. If a year is missing, the join does not silently substitute a more distant year.',
 ('table',['Stage','Targets used','Purpose'],[
 ['Initial fit','2023: 160 rows; lag comes from 2022','Fit each candidate and training-only preprocessing'],
 ['Validation','2024: 160 rows; lag comes from 2023','Choose configuration by MAE'],
 ['Final refit','2023–2024: 320 rows','Fit selected fixed configuration with more available history'],
 ['Final test','2025: 160 rows; lag comes from 2024','Report held-out metrics; no retuning']],[100,200,207]),
 'The same districts occur across splits intentionally: the intended task is forecasting later seasons for known districts. This does not establish generalisation to unseen districts or different administrative boundaries. Spatial correlation also means that 160 held-out rows are not necessarily 160 statistically independent observations.',
 'Ridge uses alpha=10. E1 includes only the lag; E2 adds district area and one-hot province indicators. Numeric preprocessing contains median imputation and standard scaling. Categories use one-hot encoding with unseen values ignored. These steps are inside a scikit-learn Pipeline and ColumnTransformer, so each fit learns only from its training rows [5]. District codes and names are not predictive features.',
 'The Random Forest uses 300 trees, maximum depth 6, minimum leaf size 5 and random seed 42. Its numeric scaling is retained for pipeline consistency, although trees do not require it. These settings constrain a small-data experiment; they are not a claim of optimal hyperparameters. Predictions are clipped to 0–100%, matching the physical target range.',
 'MAE is the mean absolute difference between observed and predicted percentages. MSE averages squared differences, RMSE is its square root, and R² compares squared error to variation around the test mean [6]. MAE and RMSE are in percentage points; MSE is in squared percentage points. A negative R² is allowed and is an important failure signal.']),
('7. Implementation and reliability',[
 'The project separates source data, processed data, reusable implementation, notebook explanation, model artefacts, tests and reporting. load_data and validate_data audit the input. make_supervised constructs the exact lag. make_model builds preprocessing and the estimator. predict_checked validates demo inputs and bounds the output. run executes the fixed experiment protocol and writes the evidence files.',
 'The notebook provides a guided execution of the modular code rather than a disconnected copy of the model. It displays the source audit, candidate dataset comparison, split counts, validation and final metrics, six charts, regional errors, test results and a working demonstration. All nine code cells executed successfully through IPython in-process. Standard Jupyter kernel launch was blocked by environment socket restrictions, so frontend launch remains unverified here.',
 ('table',['Reliability group','Verified cases'],[
 ['Input integrity','Missing columns/file; duplicate keys; empty dataset; zero area; out-of-range percentage; NaN target'],
 ['Time and leakage','Exact lag values; missing-year gap not bridged; changing final-year labels leaves that year’s features unchanged'],
 ['Prediction interface','Unseen province handled; invalid lag rejected'],
 ['Reproducible artefacts','Publisher checksums; deterministic model seed; executed notebook; saved CSV metrics and model']],[132,375]),
 'Twelve automated tests pass. These tests validate program behaviour, not forecast usefulness. Deliberately invalid test fixtures are separate from the real modelling data. The raw dictionary initially failed UTF-8 decoding because its source uses Windows-1252; the read path was corrected to cp1252 without altering the original bytes.',
 'The command-line demo retrieves a real district’s 2024 features, predicts its 2025 flooded percentage and displays the observed value. Unknown districts and unsupported target years receive clear errors. The saved model is restricted to this holdout demonstration; it has not been refitted into a 2026 deployment model.',
 'Git hosting is omitted as requested. The course’s collaboration requirement is therefore unfulfilled. Suggested responsibilities, real preparation activities and an empty meeting template are supplied, but no commits or student contributions are invented. The AI-assistance statement identifies how this package was prepared. Both students must be able to explain the entire workflow.']),
('8. Experiments and results',[
 'The experiment sequence tests a feature change and then a model change. E1 establishes a supervised linear baseline. E2 asks whether area and province help the same linear model. E3 uses the same expanded feature set with a nonlinear estimator. The winner is selected using only the 2024 validation MAE; the selection record is written before final-test scoring.',
 ('table',['Experiment','Val. MAE','Val. RMSE','Val. R²'],val_rows,[215,92,100,100]),
 'The forest has the lowest validation MAE, about 4.006, only 0.014 points below lag-only Ridge. This tiny difference is not evidence of statistically significant superiority. The forest also has worse validation RMSE, illustrating that a single average loss can favour a different error profile. The predetermined selection rule is retained.',
 ('table',['Final 2025 model','MAE','MSE','RMSE','R²'],metric_rows,[179,72,92,82,82]),
 'Every learned comparison model is refitted on 2023–2024 before final evaluation. The median benchmark learns only the training-target median, approximately 0.669%. Persistence simply carries the previous season’s observation forward. The final test table is a diagnostic comparison, not a second model-selection stage.',
 'The selected model meets both educational criteria: MAE is below 5 and is 37.9% lower than persistence. However, the constant training-median benchmark achieves better MAE and RMSE. The forest’s negative R² means its squared error exceeds that of the test-mean reference used by the metric. That reference is not itself a trained forecasting method.',
 'The appropriate conclusion is that the experiment is reproducible but the forecasting claim is not supported strongly enough. A different test winner must not simply replace the preselected model and be presented as independently validated. Further model changes require a new evaluation period or a properly nested temporal design.']),
('9. Error analysis, bias and limitations',[
 ('image','05_test_predictions.png','Figure 2. Final test predictions against observed percentages. The dashed identity line represents perfect predictions, not a fitted regression line.'),
 'The largest error is Jacobabad: observed 1.843%, predicted 44.529%, an absolute difference of 42.686 percentage points. Shikarpur, Larkana and Sohbatpur also receive substantial overpredictions. Pakpattan illustrates the opposite failure: observed 16.149% but predicted about 1.138%. These examples are genuine held-out records, not hypothetical cases.',
 ('table',['Province / territory','Districts','MAE (points)'],[[r.province_name,str(int(r.n)),f'{r.mae:.3f}'] for r in regional.itertuples()],[270,95,142]),
 'Sindh has the highest average error, while a single observation represents Islamabad. These small and uneven group sizes prevent a confident fairness claim. District averages also conceal within-district exposure and vulnerability. Region names are geographic categories, not proxies that establish household risk.',
 'The 2025 unweighted mean exposure is 2.479%, below all development seasons. Only one independent final season is available, so temporal uncertainty is substantial. The data lack pre-season rainfall, river conditions and verified ground observations. Sensor coverage, coarse aggregation, shifting flood regimes and correlated districts limit transfer. The model provides no calibrated predictive intervals.']),
('10. Recommendation, conclusion and next steps',[
 'For the proposed preparedness analyst, the defensible recommendation is to use this package as an auditable research baseline and a way to identify data needs. It should not automate decisions. A model that beats persistence yet loses to a constant baseline has not established reliable added value, even when its average MAE seems small.',
 'The implementation achieves the technical learning goals: public data acquisition with attribution, audit and dictionary, pandas/NumPy preparation, four explained EDA figures, two supervised estimator families, three experiments, chronological evaluation, regression metrics, reusable code, edge-case tests and reproducible outputs. Its evidence supports a critical conclusion rather than an optimistic deployment claim.',
 'Future work should first extend the number of seasons and independently verify the target observations. Add predictors genuinely available before the forecast date, such as appropriately lagged rainfall or river measures, with documented timestamps and spatial matching. Do not join post-event observations and then label the resulting model as an early-warning system.',
 'With more seasons, use rolling temporal evaluation and retain a final untouched period. Compare linear, nonlinear and simple constant/persistence baselines in each fold. Test unseen districts separately if geographic transfer becomes an objective. Consider target transformations, alternative losses or calibration only within development data; evaluate large misses and regional errors alongside aggregate MAE.',
 'Before any real decision support, obtain stakeholder-defined tolerances, an independent validation dataset, coverage checks, uncertainty reporting and a human review process. This dataset measures detected flood extent, not social vulnerability or losses. Any population or mobility enrichment would need its own access conditions, privacy review and verified geographic alignment.',
 ('table',['Team member','Proposed review / presentation focus','Evidence status'],[
 ['M.Sohail — 16032','Problem, data audit, features and EDA','Student review and actual contributions pending'],
 ['M.Umar — 16031','Models, evaluation, tests and demo','Student review and actual contributions pending']],[125,227,155]),
 'Both students must review all code and defend the full method. No claim is made that a semester of collaboration has occurred. The course requires 3–4 members, documented approval and Git evidence; the two-member arrangement and omitted repository remain outstanding submission matters. The contribution matrix, task log and viva guide are supplied to support genuine follow-through.'])]

refs=(ROOT/'docs/REFERENCES.md').read_text()
refblocks=[]
for line in refs.splitlines():
    if line[:1].isdigit():refblocks.append(('small',line.replace('**','')))
body.append(('References',refblocks+['Supporting artefacts: docs/ contains the complete project dictionary, contribution plan, task/reliability record, submission checklist and viva guide. evidence/ contains test output, demo output, checksums and the model-selection record.']))
write_pdf('Technical_Report',body)

proposal=[('Project proposal | FloodGuard AI',[
 NAMES+'\nCUSIT | Programming for Artificial Intelligence | Fall 2026',
 'Problem statement: Evaluate whether previous-season district flood exposure and simple geographic metadata can estimate next-season flooded percentage for the 160 districts represented in the Pakistan source dataset. The proposed stakeholder is a district disaster-preparedness analyst. Instructor approval and stakeholder consultation are not claimed.',
 'Motivation: Pakistan’s documented flood impacts make preparedness research relevant [2]. An annual public district table [1] enables a transparent beginner ML exercise. This project tests the limits of a historical exposure baseline instead of assuming that retrospective spatial statistics are valid forecast inputs.',
 'Data and target: Use the public CC BY 4.0 district dataset, 640 records over 2022–2025. Compare the tehsil alternative before finalising the district-level scope. Target pct_flooded in year t; candidate inputs are prior-year percentage, district area and province. Do not use same-year flood area or target-derived hotspot/LISA fields.',
 'Success criteria: (1) held-out 2025 MAE no greater than 5 percentage points; (2) at least a 10% MAE improvement over persistence. Also compare a training-median predictor, RMSE and R² so passing these criteria cannot conceal poor skill. These are classroom evaluation targets, not operational thresholds.',
 'Research question: Does adding simple geography or a nonlinear model improve a lag-only linear baseline on an independent later season? The objective is a reproducible comparison and a cautious stakeholder recommendation, not a deployment-ready warning service.',
 ('small','This proposal records the implemented design. Its success criteria were fixed before model fitting during package preparation; it is not represented as a previously submitted or approved semester proposal.')]),
('Implementation plan and expected deliverables',[
 'Method: Validate source keys and numeric ranges; preserve raw bytes; construct an exact t-1 join. Produce at least four development-only EDA charts. Train on 2023 and validate on 2024. Compare lag-only Ridge, Ridge plus geography, and Random Forest. Refit the fixed selected configuration on 2023–2024 and evaluate 2025 without test-driven tuning.',
 'Reliability: Check at least three edge cases, including duplicate keys, malformed inputs and missing-year gaps. Use deterministic settings, explicit errors, packaged data, a requirements file, an executed notebook and a working CLI demonstration. Document failed assumptions as clearly as successful checks.',
 'Planned roles: M.Sohail reviews domain research, sources, preprocessing and EDA. M.Umar reviews model comparison, testing and demonstration. Both review all code, verify results and practise the full viva. These are proposed responsibilities; actual individual evidence must be recorded after work is performed.',
 'Milestone order: problem discovery and source review; dataset audit; modular foundation; cleaning and EDA; supervised baseline; model comparison; integration and tests; final report and presentation. The course’s weeks 1–18 milestone history is not reconstructed or backdated.',
 'Deliverables: this two-page proposal, dataset audit and dictionary, raw and processed CSVs, executed notebook and source, metrics and charts, a ten-body-page technical report with references, nine presentation slides, demo instructions, contribution plan, factual preparation log and viva guide. A Git repository is omitted at the user’s request.',
 'Risks: only four seasons, limited predictive features, satellite observation uncertainty, spatial correlation and possible seasonal shifts. The two supplied names do not meet the brief’s stated 3–4-member rule. Approval and collaboration requirements require student/instructor follow-up.',
 ('small','Source review: [1] Umer, Zenodo district/tehsil data; [2] World Bank 2022 flood assessment; [3] FAO Pakistan crop/flood data; [4] FloodTraces contextual data; [5] scikit-learn leakage guidance; [6] scikit-learn metrics. Complete references and URLs: docs/REFERENCES.md. Prepared 24 November 2026.')])]
write_pdf('Project_Proposal',proposal)

dictionary=[
 ['district_code','String / identifier','OCHA administrative code','Join/report only'],
 ['district_name','String / label','Administrative district name','Report only'],
 ['province_name','String / category','Province or territory name','One-hot predictor'],
 ['area_km2','Numeric / km²','Administrative area','Numeric predictor'],
 ['flooded_km2','Numeric / km²','Detected flooded area in this season','Excluded: outcome-derived'],
 ['pct_flooded','Numeric / %','min(100, 100 × flooded_km2 / area_km2)','Target only'],
 ['year','Integer / calendar year','Season represented by observation','Temporal split/join only'],
 ['gi_z','Numeric / z-score','Getis-Ord Gi* statistic on flood percentage','Excluded: same-year spatial statistic'],
 ['hotspot','String / category','Gi* significance/hotspot class','Excluded: same-year spatial statistic'],
 ['lisa_quad','String / category','Local spatial association quadrant','Excluded: same-year spatial statistic'],
 ['lisa_p','Numeric / p-value','Local Moran significance value','Excluded: same-year spatial statistic'],
 ['z_val','Numeric / standard score','Standardised flooded percentage','Excluded: transformed target'],
 ['z_lag','Numeric / spatial lag','Spatial lag of standardised target','Excluded: same-year target neighbours'],
 ['prev_pct_flooded','Numeric / % (derived)','Same district pct_flooded at exactly t-1','Lagged predictor']]
with (ROOT/'docs/data_dictionary.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.writer(f);w.writerow(['variable','type_and_units','meaning','model_role']);w.writerows(dictionary)

audit_pages=[('Dataset audit | FloodGuard AI',[
 NAMES+'\nAudit/access date: 24 November 2026',
 'Selected source: Abdullah Umer (2026), Zenodo record 20100773, version 1, DOI 10.5281/zenodo.20100773, CC BY 4.0. The district file came from the user; published checksums confirm byte-for-byte identity. The tehsil candidate and variable dictionary were obtained from the same public record. No restricted data are included.',
 ('table',['Candidate','Rows','Columns','Units','Years','Missing cells'],[
 ['District (selected)','640','13','160','2022–2025','0'],['Tehsil (alternative)','2,308','11','577','2022–2025','0']],[125,55,65,55,110,97]),
 'Both candidates have zero duplicate unit-year keys. The district unit matches the proposed stakeholder and the user’s nationwide scope within the source snapshot. The tehsil table is more granular, but represents the same four seasons. It is included for transparent comparison, not used to inflate sample size or independently validate the model.',
 ('table',['Raw file','Published and verified MD5'],[
 ['District_Level_Data.csv','a9d498bdbfbeef2350b43ce2e47c4d58'],
 ['Tehsil_Level_Data.csv','a27591f747c81ab52297af988282fd46'],
 ['Variable_Dictionary.csv','0bb1214925aacb6600a81c9a4a230891']],[200,307]),
 'Quality checks: no missing cells, duplicate rows or duplicate district-year keys in the district table. Core numbers are finite; area is positive; percentages lie in 0–100 and match the publisher’s capped ratio formula within 1e-6 tolerance. District area, name and province remain constant across the observed seasons. The original dictionary is Windows-1252 encoded.',
 'Attribution and modifications: raw files are unchanged. Derived data strip whitespace, sort observations and join the exact preceding year. Credit and licence remain in README and provenance. No household, telephone, medical or credential data occur in the training table. Existing geographic aggregate bias and sensor uncertainty are still relevant.']),
('Data dictionary and leakage decisions',[
 'The following mapping covers all 13 source fields plus the one engineered predictor. The original publisher dictionary is also bundled. Units and model roles must be preserved when explaining or extending the workflow.',
 ('table',['Variable','Type / units','Meaning','Use'],dictionary,[100,95,175,137]),
 ('small','pct_flooded is not a probability. A value of 10 means 10% of district area was detected as flooded in that season. Same-year spatial statistics cannot be used for an honest pre-season forecast. The engineered lag uses district_code and an exact year match, never just neighbouring row order.')]),
('Distribution, cleaning and known limitations',[
 ('table',['Season','Rows','Mean %','Median %','Maximum %'],[[str(int(x['year'])),str(int(x['count'])),f"{x['mean']:.3f}",f"{x['median']:.3f}",f"{x['max']:.3f}"] for x in audit['year_summary']],[95,70,114,114,114]),
 f"There are {audit['zero_target_count']} zero-target records out of 640. This is regression, so class balance is not defined. Target skew and the frequency of low/zero exposure are more relevant. Means here are unweighted across districts; they are not the percentage of Pakistan’s total land area flooded.",
 'The 2022–2024 plots support exploration; the 2025 distribution is described only in final diagnostics. Model targets number 480 after dropping the first year from supervised use. Training uses 160 targets in 2023, validation 160 in 2024, and final evaluation 160 in 2025. The selected model is refitted on 320 development targets.',
 'No outlier removal or synthetic observations are used. Extreme floods are legitimate observations unless shown otherwise. No target imputation or oversampling is performed. Numerical pipeline imputation learns from training only, although no source numeric values are missing. Categorical province encoding also learns from training only.',
 'The record describes detected inundation and has sensor/coverage limitations. Four annual observations per district cannot establish stable trend estimates. Districts are spatially correlated, the area/province features are coarse, and the training table contains no antecedent rainfall, topography or river conditions. A zero observation is not proof of zero hazard.',
 'Fairness and privacy: aggregates avoid direct personal records, but lower-resolution units can hide neighbourhood-level harm. Province error comparisons are descriptive, with only one Islamabad district. No fairness guarantee follows from them. Future population or mobility features would introduce separate privacy and licence obligations.',
 'Additional checksums, exact missing counts and regional record counts are stored in data_audit.json and source_provenance.json. The source/reference list includes two compared public tabular candidates and a restricted contextual alternative; restricted files were not obtained. The dataset is suitable for demonstrating the ML workflow, with clear limits on forecast claims.'])]
write_pdf('Dataset_Audit',audit_pages)

# Nine landscape PDF slides for offline presentation; editable deck is also linked.
slides=[
 {'title':'FloodGuard AI','body':['Next-season district flood-exposure estimation','M.Sohail 16032  |  M.Umar 16031','CUSIT · Programming for Artificial Intelligence · Fall 2026'],'note':'Sohail, 30 seconds. Introduce the historical evaluation and say clearly that it is not a live warning system.'},
 {'title':'Problem and proposed stakeholder','body':['District preparedness analysts need evidence about historical exposure.','Predict the next season’s flooded area percentage for known districts.','Targets: MAE ≤ 5 points and ≥ 10% improvement over persistence.','These are classroom targets, not operational acceptance criteria.'],'note':'Sohail, 50 seconds. Context: World Bank 2022 PDNA, reference 2. No stakeholder interview or approval is claimed.'},
 {'title':'Dataset and audit','body':['640 records · 160 districts · four seasons (2022–2025)','District table selected; 2,308-row tehsil alternative compared.','No missing cells or duplicate district-year keys.','Public Zenodo source; CC BY 4.0; publisher checksums verified.'],'note':'Sohail, 60 seconds. Sources 1 and 7 in REFERENCES.md. Explain why more tehsil rows do not add seasons.'},
 {'title':'Exploratory analysis','body':['Many low percentages and a long upper tail.','Seasonal and regional differences favour temporal evaluation.','Four EDA figures use 2022–2024 only.'],'figure':'01_distribution.png','note':'Sohail, 50 seconds. Explain skew and why a median benchmark matters. All plotted values are computed from bundled source data.'},
 {'title':'Features and evaluation design','body':['Inputs: prior-season percentage, district area and province.','Exclude current-season flood measurements and spatial statistics.','Fit 2023 → select on 2024 → refit 2023–2024 → test 2025.','Same districts across years; unseen districts are not tested.'],'note':'Umar, 60 seconds. Explain the exact lag join and training-only preprocessing. Sources 5 and 6; full method in pipeline.py.'},
 {'title':'Three experiments','body':['E1: Ridge, prior-season percentage only.','E2: Ridge, add area and one-hot province.','E3: Random Forest, same expanded features.','2024 MAE: 4.020 / 4.096 / 4.006; forest selected.'],'note':'Umar, 45 seconds. Forest wins by a tiny margin. Selection metric was fixed; no claim of statistically significant superiority.'},
 {'title':'Final holdout results','body':['Forest: MAE 2.726 points · RMSE 6.016 · R² −0.978.','Persistence MAE: 4.388; training-median MAE: 2.474.','Beating persistence does not establish useful forecasting skill.'],'figure':'06_test_mae.png','note':'Umar, 60 seconds. Show all results, including the stronger median benchmark. Do not call MAE an accuracy percentage.'},
 {'title':'Working demo and reliability','body':['python demo.py --district PK101 --year 2025','Display a real held-out prediction alongside the observation.','12 tests passed; nine notebook code cells executed.','Four seasons and uneven regional errors limit generalisation.'],'note':'Umar, 90 seconds including demo. Use demo.py offline. Then show PK707 to demonstrate a large error rather than hiding it.'},
 {'title':'Recommendation and team follow-through','body':['Keep the workflow as an auditable research baseline.','Add earlier seasons and weather/river predictors; validate again.','Sohail: proposed data/EDA review. Umar: proposed model/test review.','Actual contributions, team-size resolution and Git evidence remain pending.'],'note':'Both, 45 seconds. No operational use. Source references and full attribution are in the accompanying report. Mention AI assistance and that proposed roles are not completed contributions.'}
]
(ROOT/'presentation/slides.json').write_text(json.dumps(slides,indent=2,ensure_ascii=False))
(ROOT/'presentation/EDITABLE_PRESENTATION.txt').write_text('https://chatgpt.com/space/page_73fadf0efca08191bdd6f5a45b7235e3\nThe included PDF is the offline slide copy. The editable presentation can be exported through its interface.\n')
notes=['# Presentation and demo notes','Total planned time: approximately 8 minutes 10 seconds, followed by questions. Both students should rehearse and adjust pacing.']
out=ROOT/'presentation/FloodGuard_AI_Slides.pdf';c=canvas.Canvas(str(out),pagesize=(960,540));c.setTitle('FloodGuard AI');c.setAuthor(NAMES)
for i,s in enumerate(slides):
    c.setFillColor(colors.HexColor('#F7FAFB'));c.rect(0,0,960,540,fill=1,stroke=0)
    c.setFillColor(NAVY);c.setFont('Helvetica-Bold',35 if i else 48);c.drawString(48,465,s['title'])
    y=395
    if 'figure' in s:
        for line in s['body']:
            par=Paragraph(escape(line),ParagraphStyle('slide',fontName='Helvetica',fontSize=18,leading=25,textColor=NAVY));w,h=par.wrap(860,80);par.drawOn(c,48,y-h);y-=h+12
        c.drawImage(str(FIG/s['figure']),140,55,width=680,height=245,preserveAspectRatio=True,anchor='c',mask='auto')
    else:
        for line in s['body']:
            par=Paragraph(escape(line),ParagraphStyle('slide',fontName='Helvetica',fontSize=23 if i else 25,leading=33,textColor=NAVY));w,h=par.wrap(855,150);par.drawOn(c,48,y-h);y-=h+26
    c.setFont('Helvetica',10);c.setFillColor(GRAY);c.drawString(48,24,'FloodGuard AI | '+NAMES);c.drawRightString(912,24,f'{i+1} / 9');c.showPage()
    notes.extend([f"\n## Slide {i+1}: {s['title']}",s['note']])
c.save()
notes.extend(['\n## Demo sequence','1. Extract the project and install dependencies before presenting.','2. Run `python -m src.pipeline` if the model is missing.','3. Run `python demo.py --district PK101 --year 2025`. Explain that the input observation is from 2024.','4. Run `python demo.py --district PK707 --year 2025`. Discuss the severe error.','5. Run `python -m unittest discover -s tests -v` or show the saved actual test output.','6. Keep the executed notebook available as an offline fallback. No recorded demo video is claimed.'])
(ROOT/'presentation/SPEAKER_AND_DEMO_NOTES.md').write_text('\n\n'.join(notes),encoding='utf-8')
print('Generated technical report, two-page proposal, three-page audit and nine-slide PDF.')

if __name__=='__main__':pass
