# FloodGuard AI

**M.Sohail (16032) · M.Umar (16031)**  
Programming for Artificial Intelligence · Fall 2026 · CUSIT

A reproducible Python project that evaluates whether last season's district flood exposure can estimate the next season's flooded percentage. This is a historical academic experiment, not a live flood-warning service.

## Start here

1. Extract the ZIP completely. Do not run files inside the compressed folder.
2. Open a terminal in `FloodGuard_AI` and use Python 3.12.
3. Create and activate an environment, then install dependencies:

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate
python -m pip install -r requirements.txt
```

4. Run the workflow, tests and demonstration:

```bash
python -m src.pipeline
python -m unittest discover -s tests -v
python demo.py --district PK101 --year 2025
```

5. Open `notebooks/FloodGuard_AI.ipynb` in JupyterLab or VS Code, choose this Python environment and run all cells. The notebook already contains real execution outputs.

```bash
python -m jupyterlab notebooks/FloodGuard_AI.ipynb
```

The packaged notebook was executed with `python scripts/execute_notebook.py` using IPython in-process because the build environment disallowed Jupyter kernel sockets. It contains actual computed outputs. It remains a standard Jupyter notebook; native Jupyter frontend launch was not verified in this environment.

## What is included

| Folder | Contents |
|---|---|
| `data/raw` | Original district and tehsil CSVs; publisher's variable dictionary |
| `data/processed` | Validated district data and exact prior-year modelling table |
| `src` | Modular validation, feature preparation, EDA, training and evaluation |
| `notebooks` | Executed notebook with explanations, charts and test outputs |
| `reports` | Technical report, proposal, dataset audit, machine-readable metrics and six figures |
| `presentation` | Nine-slide PDF, slide text and speaker/demo notes |
| `models` | Validation-selected model fitted on target years 2023–2024 |
| `tests` | Twelve edge-condition and leakage checks |
| `docs` | References, data dictionary, contribution plan, task log and viva guide |
| `evidence` | Real test/demo output, source provenance and selection record |

## Result and interpretation

E1: Ridge with prior-year percentage. E2: Ridge with geography. E3: Random Forest with geography. Train on 2023, select using 2024 MAE, refit on 2023–2024, and evaluate 2025 once. Same districts recur across seasons, matching the intended known-district task.

The selected forest's 2025 MAE is **2.726 percentage points**, RMSE **6.016**, and R² **−0.978**. Persistence MAE is **4.388**, but a training-median predictor achieves **2.474**. The model therefore does not establish reliable added value. Negative R² and large regional errors must not be hidden. No classification accuracy is reported because this is regression.

Do not select a different model from the final test table without obtaining a new untouched evaluation period. The two stated classroom success criteria are met, but neither implies operational suitability.

## Data attribution

Abdullah Umer (2026), *A Multi-Resolution Geospatial Dataset of Monsoon Flood Extent and Spatial Clustering for Pakistan (2022–2025)*, Zenodo, version 1. DOI: https://doi.org/10.5281/zenodo.20100773. CC BY 4.0: https://creativecommons.org/licenses/by/4.0/. Accessed 24 November 2026. All three raw-file MD5 values match the publisher. Raw bytes are unchanged; derived data strip identifier whitespace, sort rows and add an exact preceding-year join. Full provenance is in `evidence/source_provenance.json`.

The original dictionary uses Windows-1252 encoding; read it using `encoding='cp1252'`. Numeric zero means no detected flooding, not proof of safety. The selected dataset has only four annual seasons and no rainfall or river predictors.

## Course requirements still needing student action

The supplied brief requires 3–4 members. Two were supplied; instructor resolution is still required. Git hosting and collaboration history are omitted at the user's request. No approvals, student commits, meetings or technical contributions are claimed. Both students must review the work and record actual contributions before submission. See `docs/SUBMISSION_CHECKLIST.md` and `docs/AI_ASSISTANCE.md`.

## Rebuilding documents

After running the notebook, run `python scripts/build_documents.py` to regenerate the PDF/Markdown deliverables from the stored metrics. `requirements.txt` pins main tested libraries; `requirements-lock.txt` records the full build environment for reference and is not the recommended installation list. Runtime timings may differ; seeded model metrics should match within numerical tolerance on the pinned versions.
