# Individual viva preparation

Both members should answer every question; the proposed division of tasks is not a substitute for understanding.

1. **What is predicted?** Percentage of district area detected as flooded in the next monsoon season, a continuous regression target.
2. **What is one row?** One district in one target year, joined to that same district's exact preceding season.
3. **Why 480 model rows from 640 source rows?** The 160 records for 2022 have no 2021 history; they supply lag values but no supervised target examples.
4. **Why avoid random row splitting?** Future-season information could influence training. We train on 2023, choose using 2024 and hold out 2025.
5. **Can the same district occur in train and test?** Yes, intentionally: the task concerns future seasons for already observed districts. It does not test unseen-location generalisation.
6. **Which columns leak?** Current-year flooded area and spatial statistics use the current outcome. z_val is a standardised target, for example. Exclude them from inputs.
7. **Why pipelines?** Scaling, imputation and categorical encoding learn only from the training portion, then apply the same transformation to validation/test.
8. **What is one-hot encoding?** Separate binary indicator columns for province categories; no artificial numeric province ordering.
9. **Why Ridge?** A regularised linear baseline that limits coefficient size. alpha=10 was fixed rather than tuned using test performance.
10. **Why a forest?** It can model nonlinear relationships and interactions. Leaf size/depth limits restrain overfitting on a small training set.
11. **What are the three experiments?** Lag-only Ridge; Ridge with geography; forest with the same expanded inputs.
12. **How was the winner selected?** Lowest validation MAE among E1–E3. The difference between the forest and lag-only Ridge is tiny and not evidence of statistically significant superiority.
13. **What does MAE 2.726 mean?** Average absolute error of 2.726 percentage points of district area on the 2025 records; it is not 97.274% accuracy.
14. **Why report RMSE?** Squaring gives greater weight to large errors; the forest's RMSE of 6.016 shows that the average MAE hides severe misses.
15. **What does negative R² mean?** The predictions have greater squared error than a constant equal to the test-set mean. That mean is only a metric reference, not a deployable trained model.
16. **Which simple baseline wins on test MAE?** The median of training targets, at about 2.474 points, beats the selected forest. Report this openly.
17. **What is persistence?** Predict that next year's percentage equals last year's percentage. The selected model's MAE is about 37.9% lower, but this does not prove it beats all alternatives.
18. **Why no confusion matrix?** There are no class labels; the task is regression. Thresholding would create a different task requiring a justified operational threshold.
19. **What happens when a year is missing?** The exact lag join excludes the corresponding next-year example; it does not bridge the gap.
20. **Where are errors greatest?** Sindh has the largest province-average MAE in this holdout; Jacobabad has the largest district error. The one-district Islamabad result cannot establish fairness.
21. **Does zero mean no risk?** No. It means no flooding detected in the source observation, subject to coverage and sensor limitations.
22. **Why is this not deployment-ready?** Four seasons, one final test season, weak baselines comparison, missing weather/river drivers and substantial geographic error variation.
23. **What would you change next?** Add more independent years and predictors available at forecast time, then evaluate with rolling temporal and spatial holdouts.
24. **What did each student do?** Explain only actual reviewed/edited/tested work and show genuine evidence. Do not claim AI-prepared files as independent student development.

## Code practice

Locate `make_supervised` and explain its year increment and merge. Add a test for a blank district name. Explain why modifying 2025 target values leaves 2025 features unchanged. Describe the difference between the original 160-row training fit and the 320-row final refit. Reproduce a demo for PK707 and explain the large error rather than hiding it.
