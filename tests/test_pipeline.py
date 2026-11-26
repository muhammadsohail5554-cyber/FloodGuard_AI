"""Failure-condition and temporal-leakage tests against the bundled real data."""
import unittest
import numpy as np
from src.pipeline import ROOT, FEATURES, load_data, validate_data, make_supervised, make_model, predict_checked

class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.d=load_data(ROOT/'data/raw/District_Level_Data.csv')
    def test_missing_column(self):
        with self.assertRaisesRegex(ValueError,'Missing required'):validate_data(self.d.drop(columns='year'))
    def test_duplicate_key(self):
        import pandas as pd
        with self.assertRaisesRegex(ValueError,'Duplicate'):validate_data(pd.concat([self.d,self.d.iloc[[0]]]))
    def test_invalid_percentage(self):
        d=self.d.copy();d.loc[0,'pct_flooded']=101
        with self.assertRaisesRegex(ValueError,'between'):validate_data(d)
    def test_zero_area(self):
        d=self.d.copy();d.loc[0,'area_km2']=0
        with self.assertRaisesRegex(ValueError,'positive'):validate_data(d)
    def test_nan_target(self):
        d=self.d.copy();d.loc[0,'pct_flooded']=np.nan
        with self.assertRaisesRegex(ValueError,'Non-finite'):validate_data(d)
    def test_empty(self):
        with self.assertRaisesRegex(ValueError,'empty'):validate_data(self.d.iloc[:0])
    def test_missing_file(self):
        with self.assertRaises(FileNotFoundError):load_data(ROOT/'data/does_not_exist.csv')
    def test_exact_lag(self):
        s=make_supervised(self.d);self.assertEqual(len(s),480)
        for row in s.itertuples():
            original=self.d[(self.d.district_code==row.district_code)&(self.d.year==row.year-1)].pct_flooded.iloc[0]
            self.assertAlmostEqual(row.prev_pct_flooded,original)
    def test_gap_not_bridged(self):
        d=self.d[~((self.d.district_code=='PK101')&(self.d.year==2023))]
        s=make_supervised(d);self.assertTrue(s[(s.district_code=='PK101')&(s.year==2024)].empty)
    def test_target_mutation_does_not_change_same_year_features(self):
        d=self.d.copy();original=make_supervised(d)
        d.loc[d.year==2025,'pct_flooded']=0
        changed=make_supervised(d)
        self.assertTrue(original[FEATURES].equals(changed[FEATURES]))
    def test_unseen_province(self):
        s=make_supervised(self.d);train=s[s.year==2023];model=make_model('ridge').fit(train[FEATURES],train.pct_flooded)
        row=s.iloc[[0]].copy();row['province_name']='Unseen region'
        self.assertTrue(np.isfinite(predict_checked(model,row)).all())
    def test_invalid_prediction_input(self):
        s=make_supervised(self.d);row=s.iloc[[0]].copy();row['prev_pct_flooded']=-1
        with self.assertRaisesRegex(ValueError,'0-100'):predict_checked(None,row)

if __name__=='__main__':unittest.main(verbosity=2)
