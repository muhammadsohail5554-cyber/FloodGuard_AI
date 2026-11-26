"""Example: python demo.py --district PK101 --year 2025"""
import argparse
import joblib
from src.pipeline import ROOT, load_data, predict_checked

def main():
    parser=argparse.ArgumentParser(description='Educational estimate, not an operational flood warning.')
    parser.add_argument('--district',default='PK101');parser.add_argument('--year',type=int,default=2025)
    args=parser.parse_args()
    if args.year!=2025: parser.error('This saved evaluation model supports the 2025 holdout demonstration only.')
    data=load_data(ROOT/'data/raw/District_Level_Data.csv')
    previous=data[(data.district_code==args.district)&(data.year==args.year-1)]
    if len(previous)!=1: parser.error('District not found or preceding-year observation missing.')
    frame=previous.rename(columns={'pct_flooded':'prev_pct_flooded'})
    try: model=joblib.load(ROOT/'models/selected_model.joblib')
    except FileNotFoundError: parser.error('Run python -m src.pipeline first.')
    prediction=predict_checked(model,frame)[0]
    actual=data[(data.district_code==args.district)&(data.year==args.year)].pct_flooded.iloc[0]
    print(f'{previous.district_name.iloc[0]} ({args.district}), 2025 historical holdout')
    print(f'Predicted flooded area: {prediction:.3f}% | Observed: {actual:.3f}%')
    print('Academic demonstration only; this is not a live forecast or evacuation recommendation.')

if __name__=='__main__': main()
