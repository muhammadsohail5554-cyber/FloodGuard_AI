# EDA findings

All four exploratory plots use 2022–2024, excluding the 2025 holdout.

1. **01_distribution.png:** Most district-season percentages are small; a few approach complete inundation. MAE represents typical absolute percentage-point error; RMSE highlights large misses. A constant predictor is a necessary benchmark.
2. **02_year_comparison.png:** Unweighted district means fall from 13.280% (2022) to 4.897% (2023), then rise to 5.667% (2024). These are observation-specific summaries, not national area-weighted rates. A row-random split would obscure season shifts.
3. **03_province_exposure.png:** Historical exposure varies by province. Province is therefore tested as a candidate feature, but its inclusion is not assumed to improve performance. Each district receives equal weight, so a large and small district count equally.
4. **04_lag_relationship.png:** Previous-season exposure does not determine next-season exposure. The lag relationship changes across seasons, motivating a nonlinear alternative and a persistence baseline.

Post-selection figures 05 and 06 are final test diagnostics, not EDA used for feature selection. The 2025 mean is 2.479%, below development seasons; this shift helps explain systematic overprediction in parts of Sindh.
