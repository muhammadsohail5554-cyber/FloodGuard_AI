# Presentation and demo notes

Total planned time: approximately 8 minutes 10 seconds, followed by questions. Both students should rehearse and adjust pacing.


## Slide 1: FloodGuard AI

Sohail, 30 seconds. Introduce the historical evaluation and say clearly that it is not a live warning system.


## Slide 2: Problem and proposed stakeholder

Sohail, 50 seconds. Context: World Bank 2022 PDNA, reference 2. No stakeholder interview or approval is claimed.


## Slide 3: Dataset and audit

Sohail, 60 seconds. Sources 1 and 7 in REFERENCES.md. Explain why more tehsil rows do not add seasons.


## Slide 4: Exploratory analysis

Sohail, 50 seconds. Explain skew and why a median benchmark matters. All plotted values are computed from bundled source data.


## Slide 5: Features and evaluation design

Umar, 60 seconds. Explain the exact lag join and training-only preprocessing. Sources 5 and 6; full method in pipeline.py.


## Slide 6: Three experiments

Umar, 45 seconds. Forest wins by a tiny margin. Selection metric was fixed; no claim of statistically significant superiority.


## Slide 7: Final holdout results

Umar, 60 seconds. Show all results, including the stronger median benchmark. Do not call MAE an accuracy percentage.


## Slide 8: Working demo and reliability

Umar, 90 seconds including demo. Use demo.py offline. Then show PK707 to demonstrate a large error rather than hiding it.


## Slide 9: Recommendation and team follow-through

Both, 45 seconds. No operational use. Source references and full attribution are in the accompanying report. Mention AI assistance and that proposed roles are not completed contributions.


## Demo sequence

1. Extract the project and install dependencies before presenting.

2. Run `python -m src.pipeline` if the model is missing.

3. Run `python demo.py --district PK101 --year 2025`. Explain that the input observation is from 2024.

4. Run `python demo.py --district PK707 --year 2025`. Discuss the severe error.

5. Run `python -m unittest discover -s tests -v` or show the saved actual test output.

6. Keep the executed notebook available as an offline fallback. No recorded demo video is claimed.