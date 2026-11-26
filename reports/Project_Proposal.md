# Project proposal | FloodGuard AI

M.Sohail (16032)  |  M.Umar (16031)
CUSIT | Programming for Artificial Intelligence | Fall 2026

Problem statement: Evaluate whether previous-season district flood exposure and simple geographic metadata can estimate next-season flooded percentage for the 160 districts represented in the Pakistan source dataset. The proposed stakeholder is a district disaster-preparedness analyst. Instructor approval and stakeholder consultation are not claimed.

Motivation: Pakistan’s documented flood impacts make preparedness research relevant [2]. An annual public district table [1] enables a transparent beginner ML exercise. This project tests the limits of a historical exposure baseline instead of assuming that retrospective spatial statistics are valid forecast inputs.

Data and target: Use the public CC BY 4.0 district dataset, 640 records over 2022–2025. Compare the tehsil alternative before finalising the district-level scope. Target pct_flooded in year t; candidate inputs are prior-year percentage, district area and province. Do not use same-year flood area or target-derived hotspot/LISA fields.

Success criteria: (1) held-out 2025 MAE no greater than 5 percentage points; (2) at least a 10% MAE improvement over persistence. Also compare a training-median predictor, RMSE and R² so passing these criteria cannot conceal poor skill. These are classroom evaluation targets, not operational thresholds.

Research question: Does adding simple geography or a nonlinear model improve a lag-only linear baseline on an independent later season? The objective is a reproducible comparison and a cautious stakeholder recommendation, not a deployment-ready warning service.

This proposal records the implemented design. Its success criteria were fixed before model fitting during package preparation; it is not represented as a previously submitted or approved semester proposal.

# Implementation plan and expected deliverables

Method: Validate source keys and numeric ranges; preserve raw bytes; construct an exact t-1 join. Produce at least four development-only EDA charts. Train on 2023 and validate on 2024. Compare lag-only Ridge, Ridge plus geography, and Random Forest. Refit the fixed selected configuration on 2023–2024 and evaluate 2025 without test-driven tuning.

Reliability: Check at least three edge cases, including duplicate keys, malformed inputs and missing-year gaps. Use deterministic settings, explicit errors, packaged data, a requirements file, an executed notebook and a working CLI demonstration. Document failed assumptions as clearly as successful checks.

Planned roles: M.Sohail reviews domain research, sources, preprocessing and EDA. M.Umar reviews model comparison, testing and demonstration. Both review all code, verify results and practise the full viva. These are proposed responsibilities; actual individual evidence must be recorded after work is performed.

Milestone order: problem discovery and source review; dataset audit; modular foundation; cleaning and EDA; supervised baseline; model comparison; integration and tests; final report and presentation. The course’s weeks 1–18 milestone history is not reconstructed or backdated.

Deliverables: this two-page proposal, dataset audit and dictionary, raw and processed CSVs, executed notebook and source, metrics and charts, a ten-body-page technical report with references, nine presentation slides, demo instructions, contribution plan, factual preparation log and viva guide. A Git repository is omitted at the user’s request.

Risks: only four seasons, limited predictive features, satellite observation uncertainty, spatial correlation and possible seasonal shifts. The two supplied names do not meet the brief’s stated 3–4-member rule. Approval and collaboration requirements require student/instructor follow-up.

Source review: [1] Umer, Zenodo district/tehsil data; [2] World Bank 2022 flood assessment; [3] FAO Pakistan crop/flood data; [4] FloodTraces contextual data; [5] scikit-learn leakage guidance; [6] scikit-learn metrics. Complete references and URLs: docs/REFERENCES.md. Prepared 24 November 2026.
