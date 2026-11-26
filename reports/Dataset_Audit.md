# Dataset audit | FloodGuard AI

M.Sohail (16032)  |  M.Umar (16031)
Audit/access date: 24 November 2026

Selected source: Abdullah Umer (2026), Zenodo record 20100773, version 1, DOI 10.5281/zenodo.20100773, CC BY 4.0. The district file came from the user; published checksums confirm byte-for-byte identity. The tehsil candidate and variable dictionary were obtained from the same public record. No restricted data are included.

| Candidate | Rows | Columns | Units | Years | Missing cells |
| --- | --- | --- | --- | --- | --- |
| District (selected) | 640 | 13 | 160 | 2022–2025 | 0 |
| Tehsil (alternative) | 2,308 | 11 | 577 | 2022–2025 | 0 |

Both candidates have zero duplicate unit-year keys. The district unit matches the proposed stakeholder and the user’s nationwide scope within the source snapshot. The tehsil table is more granular, but represents the same four seasons. It is included for transparent comparison, not used to inflate sample size or independently validate the model.

| Raw file | Published and verified MD5 |
| --- | --- |
| District_Level_Data.csv | a9d498bdbfbeef2350b43ce2e47c4d58 |
| Tehsil_Level_Data.csv | a27591f747c81ab52297af988282fd46 |
| Variable_Dictionary.csv | 0bb1214925aacb6600a81c9a4a230891 |

Quality checks: no missing cells, duplicate rows or duplicate district-year keys in the district table. Core numbers are finite; area is positive; percentages lie in 0–100 and match the publisher’s capped ratio formula within 1e-6 tolerance. District area, name and province remain constant across the observed seasons. The original dictionary is Windows-1252 encoded.

Attribution and modifications: raw files are unchanged. Derived data strip whitespace, sort observations and join the exact preceding year. Credit and licence remain in README and provenance. No household, telephone, medical or credential data occur in the training table. Existing geographic aggregate bias and sensor uncertainty are still relevant.

# Data dictionary and leakage decisions

The following mapping covers all 13 source fields plus the one engineered predictor. The original publisher dictionary is also bundled. Units and model roles must be preserved when explaining or extending the workflow.

| Variable | Type / units | Meaning | Use |
| --- | --- | --- | --- |
| district_code | String / identifier | OCHA administrative code | Join/report only |
| district_name | String / label | Administrative district name | Report only |
| province_name | String / category | Province or territory name | One-hot predictor |
| area_km2 | Numeric / km² | Administrative area | Numeric predictor |
| flooded_km2 | Numeric / km² | Detected flooded area in this season | Excluded: outcome-derived |
| pct_flooded | Numeric / % | min(100, 100 × flooded_km2 / area_km2) | Target only |
| year | Integer / calendar year | Season represented by observation | Temporal split/join only |
| gi_z | Numeric / z-score | Getis-Ord Gi* statistic on flood percentage | Excluded: same-year spatial statistic |
| hotspot | String / category | Gi* significance/hotspot class | Excluded: same-year spatial statistic |
| lisa_quad | String / category | Local spatial association quadrant | Excluded: same-year spatial statistic |
| lisa_p | Numeric / p-value | Local Moran significance value | Excluded: same-year spatial statistic |
| z_val | Numeric / standard score | Standardised flooded percentage | Excluded: transformed target |
| z_lag | Numeric / spatial lag | Spatial lag of standardised target | Excluded: same-year target neighbours |
| prev_pct_flooded | Numeric / % (derived) | Same district pct_flooded at exactly t-1 | Lagged predictor |

pct_flooded is not a probability. A value of 10 means 10% of district area was detected as flooded in that season. Same-year spatial statistics cannot be used for an honest pre-season forecast. The engineered lag uses district_code and an exact year match, never just neighbouring row order.

# Distribution, cleaning and known limitations

| Season | Rows | Mean % | Median % | Maximum % |
| --- | --- | --- | --- | --- |
| 2022 | 160 | 13.280 | 1.658 | 98.726 |
| 2023 | 160 | 4.897 | 0.445 | 72.470 |
| 2024 | 160 | 5.667 | 0.822 | 69.690 |
| 2025 | 160 | 2.479 | 0.286 | 19.116 |

There are 104 zero-target records out of 640. This is regression, so class balance is not defined. Target skew and the frequency of low/zero exposure are more relevant. Means here are unweighted across districts; they are not the percentage of Pakistan’s total land area flooded.

The 2022–2024 plots support exploration; the 2025 distribution is described only in final diagnostics. Model targets number 480 after dropping the first year from supervised use. Training uses 160 targets in 2023, validation 160 in 2024, and final evaluation 160 in 2025. The selected model is refitted on 320 development targets.

No outlier removal or synthetic observations are used. Extreme floods are legitimate observations unless shown otherwise. No target imputation or oversampling is performed. Numerical pipeline imputation learns from training only, although no source numeric values are missing. Categorical province encoding also learns from training only.

The record describes detected inundation and has sensor/coverage limitations. Four annual observations per district cannot establish stable trend estimates. Districts are spatially correlated, the area/province features are coarse, and the training table contains no antecedent rainfall, topography or river conditions. A zero observation is not proof of zero hazard.

Fairness and privacy: aggregates avoid direct personal records, but lower-resolution units can hide neighbourhood-level harm. Province error comparisons are descriptive, with only one Islamabad district. No fairness guarantee follows from them. Future population or mobility features would introduce separate privacy and licence obligations.

Additional checksums, exact missing counts and regional record counts are stored in data_audit.json and source_provenance.json. The source/reference list includes two compared public tabular candidates and a restricted contextual alternative; restricted files were not obtained. The dataset is suitable for demonstrating the ML workflow, with clear limits on forecast claims.
