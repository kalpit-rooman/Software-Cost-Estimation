# Project Log

Last updated: 2026-05-01 (Phase 5 + Phase 6 complete)

## Project Summary

This repository implements software development effort estimation on the China, COCOMO-81, and Desharnais datasets using baseline machine learning models, a 1D CNN regressor, and a PSO-tuned CNN workflow. The codebase has already moved beyond an initial notebook-only prototype: reusable source modules are in place, processed datasets have been generated, CNN and CNN+PSO model artifacts have been saved, and the evaluation layer now reports software-cost-estimation metrics beyond MAE and RMSE.

## What Has Been Completed

### Data and preprocessing

- Raw datasets for China, COCOMO-81, and Desharnais were added under `data/raw/`.
- Cleaned processed datasets were generated and saved under `data/processed/`.
- The notebook workflow from `01_eda.ipynb` to `05_pso.ipynb` was established and executed to move from exploration to tuning.
- Reusable loading and preprocessing logic was extracted into `src/data_loader.py` and `src/preprocess.py`.

### Baseline and deep-learning pipeline

- Baseline regressors were trained for comparison, including Linear Regression, Random Forest, and XGBoost where available.
- A reusable CNN pipeline was built for tabular effort-estimation inputs.
- Baseline CNN models were trained and saved for each dataset.
- CNN+PSO models were trained and saved for each dataset.

### Artifact generation

- Saved CNN artifacts are present under `models/`, including baseline and PSO-tuned `.h5` files.
- Best PSO hyperparameters were saved to `models/best_hyperparams.json`.
- Training histories were saved to `models/training_histories.json`.
- Metrics tables were saved under `results/metrics/`.

## Implemented Improvements

### CNN architecture and training improvements

Implemented in `src/cnn_model.py`:

- Added `BatchNormalization` after Conv1D blocks.
- Added tunable `dropout_rate` support.
- Added tunable `num_conv_layers` support.
- Added optional `MaxPooling1D` between convolution blocks when shape allows.
- Added `Dropout` before the output layer.
- Added `EarlyStopping` with `restore_best_weights=True`.
- Added `ReduceLROnPlateau` to lower the learning rate when validation loss stalls.
- Increased the default CNN training budget to 100 epochs while relying on callbacks to stop earlier when appropriate.

### PSO search-space improvements

Implemented in `src/pso_optimizer.py`:

- Expanded the PSO search space from the legacy 4-parameter setup to a 6-parameter setup.
- Added `dropout_rate` and `num_conv_layers` to the tunable dimensions.
- Increased PSO defaults to 15 particles and 25 iterations.
- Kept backward compatibility by allowing `decode_cnn_hyperparameters()` to handle both 4D and 6D position vectors.

### Evaluation improvements

Implemented in `src/evaluate.py`:

- Extended evaluation from MAE and RMSE to `mae`, `rmse`, `r2`, `mape`, `mdmre`, and `pred25`.
- Centralized metric saving under `results/metrics/`.

### Feature-engineering utilities

Implemented in `src/feature_engineering.py`:

- Added `log_transform_target()` and `inverse_log_transform()` helpers.
- Added low-variance feature removal.
- Added correlation-based feature selection.

## Saved PSO Hyperparameters

| Dataset | Filters | Kernel Size | Dense Units | Learning Rate | Dropout Rate | Conv Layers |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| china | 50 | 4 | 63 | 0.008510 | 0.221165 | 2 |
| cocomo81 | 75 | 6 | 132 | 0.008073 | 0.163265 | 2 |
| desharnais | 108 | 2 | 141 | 0.008723 | 0.269303 | 2 |

## Current Results Snapshot

### Best overall model per dataset

Source: `results/metrics/full_comparison.csv`

| Dataset | Best Model | Best RMSE |
| --- | --- | ---: |
| china | linear_regression | 1296.143 |
| cocomo81 | random_forest | 404.224 |
| desharnais | linear_regression | 1943.914 |

### CNN baseline vs CNN+PSO

Source: `results/metrics/cnn_vs_pso_metrics.csv` plus the 2026-04-25 delta check run from the terminal.

| Dataset | CNN Baseline RMSE | CNN+PSO RMSE | RMSE Delta | RMSE % Change | MAE Delta | R2 Delta |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| china | 4461.781 | 5577.415 | 1115.634 | 25.004% | 944.324 | -0.373 |
| cocomo81 | 642.338 | 575.724 | -66.614 | -10.370% | -51.717 | 0.263 |
| desharnais | 5772.434 | 3476.034 | -2296.400 | -39.782% | -2941.734 | 1.665 |

### Gap between CNN+PSO and the best available model

| Dataset | Best Model | Best RMSE | CNN+PSO RMSE | CNN+PSO Gap | Gap % |
| --- | --- | ---: | ---: | ---: | ---: |
| china | linear_regression | 1296.143 | 5577.415 | 4281.272 | 330.309% |
| cocomo81 | random_forest | 404.224 | 575.724 | 171.500 | 42.427% |
| desharnais | linear_regression | 1943.914 | 3476.034 | 1532.120 | 78.816% |

### Interpretation

- PSO improved over the baseline CNN on COCOMO-81 and Desharnais.
- PSO made the CNN worse on China.
- CNN+PSO is still behind the strongest classical baseline on all three datasets.
- The validation target from the project instructions, "CNN+PSO RMSE < Linear Regression RMSE on at least one dataset," is not yet satisfied.

## Current Repository State

### Present in the repository

- `src/` modules for data loading, preprocessing, CNN modeling, PSO tuning, evaluation, and feature engineering.
- Notebook sequence `01_eda.ipynb` to `05_pso.ipynb`.
- Processed datasets for all three data sources.
- Saved CNN and CNN+PSO model artifacts.
- Metrics CSVs comparing baselines and CNN variants.
- A FastAPI backend scaffold under `backend/` for prediction, health, and dataset-metadata endpoints.

### Still pending or incomplete

- `notebooks/06_cross_dataset_evaluation.ipynb` and `notebooks/07_visualizations.ipynb` are not present yet.
- A dedicated cross-validation module for the final 5-fold evaluation is not present yet.
- The `app/` Streamlit interface described in the plan is not present yet.
- Saved baseline `.pkl` artifacts are not visible in the current repository tree.
- Final comparison figures under `results/figures/` are not visible in the current repository tree.

## Latest Session Note

### 2026-04-30 - Performance review and records log

- Reviewed the saved metric artifacts in `results/metrics/holdout_results.csv`, `results/metrics/full_comparison_final.csv`, and `results/metrics/cnn_vs_pso_metrics.csv`.
- Holdout snapshot: China best RMSE was `XGBoost` at `1467.3213518914497`; COCOMO81 best RMSE was `LinearRegression` at `395.08054838016204`; Desharnais best RMSE was `LinearRegression` at `1997.9377093894732`.
- Holdout `CNN_PSO` RMSE was `3463.5213999688585` on China, `624.2937991076277` on COCOMO81, and `22388.06464600845` on Desharnais.
- Final 5-fold snapshot: China best RMSE was `RandomForest` at `1285.6426800431962`; COCOMO81 best RMSE was `RandomForest` at `1032.5459839901773`; Desharnais best RMSE was `RandomForest` at `3464.0636729167513`.
- Final 5-fold `CNN_PSO` mean RMSE was `556066.5595478723` on China, `1493.908563780196` on COCOMO81, and `312039.21563477995` on Desharnais.
- `CNN_PSO_ensemble` improved the holdout RMSE relative to `CNN_PSO` on all three datasets, but the final 5-fold comparison still favors classical baselines.
- Validation: this log entry was derived directly from the saved CSV artifacts; no model or code artifacts were changed in this step.

### 2026-04-25 - Metrics review and logging setup

- Recomputed the direct delta between `cnn_baseline` and `cnn_pso` from the saved metric CSVs.
- Confirmed PSO improvements on COCOMO-81 and Desharnais, but a regression on China.
- Confirmed that the best overall models remain classical baselines, not CNN+PSO.
- Created a persistent project log so future progress, experiments, bug fixes, and metric updates can be recorded in one place.
- Added a dedicated skill to keep this log updated aggressively whenever project progress is reported.

## Chronological Log
### 2026-05-01 – Phase 5 (AI Orchestrator) + Phase 6 (Cost/Currency Layer) implemented

**Phase 5 – AI-First Prediction Orchestrator:**
- Created abstract provider interface: `backend/services/ai_providers/base.py`
- Created OpenAI-compatible adapter (supports OpenAI, Groq, Mistral, etc. via base URL override): `backend/services/ai_providers/openai_compatible.py`
- Created Gemini adapter (v1beta REST, no SDK dependency): `backend/services/ai_providers/gemini.py`
- Created three prompt profiles (conservative, balanced, optimistic): `backend/services/prompts/profiles.py`
- Created AI response parser with JSON extraction fallback strategies: `backend/services/ai_response_parser.py`
- Created guardrails with range validation and list clamping: `backend/services/guardrails.py`
- Created AI orchestrator coordinating provider selection → prompt construction → parse → guardrail: `backend/services/ai_orchestrator.py`
- Updated `backend/core/config.py` to load `PREDICTION_MODE`, `AI_PROVIDER`, `AI_MODEL`, `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `GEMINI_API_KEY`, `GROQ_API_KEY`, `AI_PROFILE`, `DEFAULT_MONTHLY_RATE_INR` from `.env` via python-dotenv.
- Created `.env.example` with all configurable settings documented.

**Phase 6 – Effort-to-Cost and Currency Layer:**
- Created `backend/services/cost_converter.py`: `effort_to_inr(effort_months, monthly_rate_inr) → float`
- Created `backend/services/currency_converter.py`: static rate table (18 currencies), INR as base, `convert_from_inr() → (display_amount, rate)`
- Added schemas to `backend/schemas/request_response.py`: `EstimatedEffort`, `CostBreakdown`, `FinalPredictionResponse`, `FinalPredictionRequest`

**`POST /predict/final` endpoint added** (Phase 7 consolidation preview):
- Accepts `intake_id + follow_up_answers + target_currency + profile_id`
- Routes through mapper → effort prediction (AI mode or model mode) → cost derivation → currency conversion
- Returns `FinalPredictionResponse` with effort, cost_breakdown, confidence, assumptions, warnings
- Model mode uses `src/predictor.py` ensemble; AI mode calls the `AIOrchestrator`
- Mode controlled by `PREDICTION_MODE` env var (default: `model`)

**Validation:** All new files pass Pylance with no errors.
### 2026-04-30 - Performance review and records log

- Reviewed the current saved performance artifacts and recorded the exact values in the project log.
- Holdout results from `results/metrics/holdout_results.csv` show the best RMSE per dataset as `XGBoost` on China at `1467.3213518914497`, `LinearRegression` on COCOMO81 at `395.08054838016204`, and `LinearRegression` on Desharnais at `1997.9377093894732`.
- Holdout `CNN_PSO` RMSE remains `3463.5213999688585` for China, `624.2937991076277` for COCOMO81, and `22388.06464600845` for Desharnais.
- Final 5-fold results from `results/metrics/full_comparison_final.csv` show the best RMSE per dataset as `RandomForest` on China at `1285.6426800431962`, `RandomForest` on COCOMO81 at `1032.5459839901773`, and `RandomForest` on Desharnais at `3464.0636729167513`.
- Final `CNN_PSO` mean RMSE is `556066.5595478723` on China, `1493.908563780196` on COCOMO81, and `312039.21563477995` on Desharnais.
- `CNN_PSO_ensemble` gives a lower holdout RMSE than `CNN_PSO` on all three datasets, but the final 5-fold comparison still does not beat the strongest classical baselines.

### 2026-04-29 - CNN notebook rerun after interpretation fix

- Reran the final code cell in `notebooks/04_cnn.ipynb` after updating the prediction wording.
- Refreshed notebook outputs now report normalized effort values instead of person-months.
- Exact rerun outputs:
	- Best validation RMSE from PSO: `0.6392263206214015`
	- Best hyperparameters: `filters=24`, `kernel_size=4`, `dense_units=64`, `learning_rate=0.009290183207085701`, `dropout_rate=0.3060942398917824`, `num_conv_layers=3`, `batch_size=8`
	- Final TEST RMSE: `0.6902240729885462`
	- Final TEST MAE: `0.48763418616435467`
	- Example prediction output: `Model output = 1.24 -> Predicted normalized effort value for the selected project = 1.24`

### 2026-04-29 - CNN notebook output interpretation corrected

- Updated the final output wording in `notebooks/04_cnn.ipynb` so the reported prediction is described as a normalized effort value instead of person-months.
- Added an explicit note in the notebook that the model predicts normalized effort values, which can be inverse-transformed to actual effort.
- No metric values changed in this update; only the interpretation text was corrected.

### 2026-04-29 - CNN notebook final PSO-to-prediction flow executed

- Updated the final PSO cell in `notebooks/04_cnn.ipynb` to run this sequence end-to-end:
	1. tune on TRAIN and score on VALIDATION (`epochs=5`, `particles=6`, `iterations=6`),
	2. decode best hyperparameters,
	3. retrain CNN on `TRAIN + VALIDATION` for `10` epochs,
	4. evaluate on TEST with RMSE and MAE,
	5. print human-readable prediction meaning in person-months.
- Execution completed successfully in the notebook kernel.
- Exact run outputs from the executed cell:
	- Best validation RMSE from PSO: `1.2036168972279861`
	- Best hyperparameters: `filters=8`, `kernel_size=4`, `learning_rate=0.0041553978435462215`, `dropout_rate=0.3187021504122962`, `num_conv_layers=3`, `batch_size=8`
	- Final TEST RMSE: `1.068876836538165`
	- Final TEST MAE: `0.7630526601609989`
	- Example prediction output: `Model output = 0.69 -> Project needs 0.69 person-months`

### 2026-04-29 - PSO objective aligned to 5-epoch train and validation RMSE

- Updated `src/pso_optimizer.py` so `build_cnn_pso_objective(...)` now defaults to `epochs=5`.
- Updated the PSO objective training call to use TRAIN data only (`validation_split=0.0`) and disabled callbacks in this scoring path (`use_callbacks=False`) to match fixed-epoch objective evaluation.
- Kept objective scoring on the held-out VALIDATION split using RMSE as the returned score per particle.
- Validation: executed a smoke-test cell in `notebooks/04_cnn.ipynb` with one sample particle and confirmed output `Validation RMSE: 1.7408480752996467`.

### 2026-04-29 - Raw-data CNN preprocessing update

- Updated `src/preprocess.py` so categorical columns are label-encoded instead of one-hot encoded, keeping the feature matrix compact for the CNN path.
- Reworked the CNN notebook setup in `notebooks/04_cnn.ipynb` to load the raw datasets through `src.data_loader.load_all_raw_datasets()`, select a dataset key, split features and target, and use a 70/15/15 train/validation/test split.
- Applied `StandardScaler` only after the split, fitting on the training partition and reusing the scaler for validation and test features.
- Kept the CNN input reshape step in the notebook as `(samples, features, 1)` before training.
- Validation: executed the updated notebook setup cell and CNN training cell successfully; the notebook reported train/val/test shapes of `(56, 12, 1)`, `(12, 12, 1)`, and `(13, 12, 1)` for the active Desharnais run, and the training cell completed with best validation MAE `0.7518160939216614`.

### 2026-04-25 - Project log initialized

- Added `project_log/PROJECT_LOG.md` as the central documentation file for project history.
- Recorded the implemented architecture, PSO, evaluation, and feature-engineering improvements already present in the repository.
- Recorded the current model-performance snapshot from the saved metrics artifacts.
- Documented the main outstanding gap: CNN+PSO improves over the baseline CNN on two datasets, but still does not beat the best classical baseline on any dataset.

### 2026-04-25 - Reproducibility, leakage, and CV pipeline update

- Added global `SEED = 42` initialization to the training-side Python modules and notebook entry cells so random, NumPy, and TensorFlow seeding runs before splits, model builds, and PSO calls.
- Updated `src/pso_optimizer.py` so PSO now scores particles on validation RMSE only, with a dedicated objective builder that accepts `X_train`, `y_train`, `X_val`, and `y_val`.
- Narrowed the PSO search bounds to the new stable ranges and moved learning-rate search to log scale, while adding batch-size decoding to the 6D search vector.
- Added `src/cv_pipeline.py` with 5-fold cross-validation helpers for sklearn baselines, baseline CNN, and one-time-tuned CNN+PSO evaluation.
- Updated `src/feature_engineering.py` so the target transform is toggleable via `use_log_transform=True`, with inverse transformation applied before metric computation.
- Updated `notebooks/03_baselines.ipynb`, `notebooks/04_cnn.ipynb`, and `notebooks/05_pso.ipynb` to use the new seeding and log-target flow.
- Reworked `notebooks/05_pso.ipynb` to use a 60/20/20 train/validation/test split, keep the test split untouched during PSO, reuse fixed PSO hyperparameters for 5-fold CNN CV, and save `results/metrics/full_comparison_final.csv`.
- Local structural validation passed on the touched Python files and notebook edits, but the full training run and metric regeneration were intentionally left for Google Colab execution.

### 2026-04-25 - Google Colab notebook root-path fix

- Updated the setup cells in `notebooks/02_preprocessing.ipynb`, `notebooks/03_baselines.ipynb`, `notebooks/04_cnn.ipynb`, and `notebooks/05_pso.ipynb` to detect Google Colab, mount Google Drive, and resolve the repository root from common Drive locations.
- Added a recursive fallback search for the `Software-cost-Estimation` project folder in Drive so the notebooks no longer depend on `Path.cwd()` matching the repository root.
- Added a Colab-only `pyswarms` install step in `notebooks/05_pso.ipynb` before importing `src.pso_optimizer`, preventing the PSO notebook from failing on a fresh Colab runtime.
- Left `notebooks/01_eda.ipynb` unchanged in this pass because its Colab-specific setup had already been handled separately.
- Validation: reran the updated first code cell in each touched notebook locally; all four executed successfully and resolved `c:\Users\kalpi\OneDrive\Desktop\Software-cost-Estimation` as the project root, with downstream dataset loading succeeding in notebooks 3 to 5.

### 2026-04-25 - CNN+PSO status review from saved artifacts

- Reviewed the latest saved outputs in `results/metrics/cnn_vs_pso_metrics.csv`, `results/metrics/full_comparison_final.csv`, and the result cells in `notebooks/05_pso.ipynb`.
- Confirmed that the current saved CNN+PSO run improves over the baseline CNN on all three datasets in the leakage-free holdout comparison: China RMSE 4122.80 -> 2240.13, COCOMO-81 RMSE 641.16 -> 612.47, and Desharnais RMSE 5763.83 -> 4911.48.
- Confirmed that the final 5-fold comparison still favors classical baselines over CNN variants: China best RMSE is RandomForest at 1309.82 vs CNN_PSO at 7667.81, COCOMO-81 best RMSE is XGBoost at 1145.71 vs CNN_PSO at 1413.52, and Desharnais best RMSE is RandomForest at 3052.07 vs CNN_PSO at 5967.26.
- Observed high CNN variance across folds in `results/metrics/full_comparison_final.csv`, especially for China (CNN_PSO RMSE std 6777.83 and CNN_baseline RMSE std 8795.83), which suggests unstable generalization even though PSO improves the baseline CNN.
- Identified an evaluation caveat in the current pipeline: `src/preprocess.py` scales full datasets before they are saved, while later cross-validation in `notebooks/05_pso.ipynb` and `src/cv_pipeline.py` reuses those already scaled full-dataset features. That means fold-level scaling statistics are likely leaking into the final CV tables.
- Recommended next step: move preprocessing inside each CV fold, then rerun the final comparison and only after that invest in another CNN+PSO tuning pass.

### 2026-04-25 - Leakage fix, clean benchmark refactor, MLP expansion, and runtime-budgeted regeneration

- Updated `src/preprocess.py` so `preprocess_dataset()` returns encoded but unscaled features; added an inline leakage comment at the old full-dataset scaling point and restored `scale_numeric_features()` only as a notebook compatibility helper for `notebooks/02_preprocessing.ipynb`.
- Expanded `src/cv_pipeline.py` into the clean evaluation entry point: it now creates an untouched `X_main` / `X_holdout` split before any scaler fit, performs fold-local `StandardScaler` fits inside every CV split, evaluates holdout metrics exactly once, and writes the 9-model comparison schema (`LinearRegression`, `RandomForest`, `XGBoost`, `CNN_baseline`, `CNN_PSO`, `MLP_baseline`, `MLP_PSO`, `CNN_PSO_ensemble`, `MLP_PSO_ensemble`).
- Added `src/mlp_model.py`, `src/pso_mlp.py`, and `src/ensemble.py` to support MLP baselines, MLP+PSO tuning, and seeded CNN/MLP ensemble prediction.
- Updated `src/cnn_model.py` and `src/pso_optimizer.py` so CNN training uses shared `EarlyStopping` + `ReduceLROnPlateau` defaults, accepts fold-size hints for small-dataset architecture caps, and keeps PSO scaling confined to the train split.
- Added runner support in `scripts/run_clean_benchmark.py` for reduced local budgets (`training_epochs`, `tuning_epochs`, `n_particles`, `iters`, `ensemble_size`, `ensemble_epochs`) so the same clean benchmark path can be executed on a CPU-only Windows session without changing notebook defaults.
- Structural validation passed on the touched Python files: `src/preprocess.py`, `src/cv_pipeline.py`, `src/cnn_model.py`, `src/pso_optimizer.py`, `src/mlp_model.py`, `src/pso_mlp.py`, `src/ensemble.py`, and `scripts/run_clean_benchmark.py` all reported no editor errors after the refactor.
- Artifact regeneration is still runtime-bound locally. A reduced clean run with `--training-epochs 5 --tuning-epochs 3 --n-particles 2 --iters 1 --ensemble-size 2 --ensemble-epochs 5` is the current practical path for regenerating the new CSV/model artifacts in this environment.

### 2026-04-25 - Clean benchmark artifacts regenerated successfully


### 2026-05-01 - Next.js frontend added for production prediction demo

- Added a new `frontend/` package as a monorepo-style Next.js App Router application using TypeScript, Tailwind CSS, and modular React components.
- Implemented a single-page editorial interface with `Navbar`, `Hero`, `Features`, `DemoSection`, and `Footer` components, keeping the primary focus on the live prediction demo.
- Added `frontend/lib/api.ts` with typed `getDatasets()` and `predictCost()` helpers targeting the FastAPI backend at `http://localhost:8000` by default, with optional override through `NEXT_PUBLIC_API_BASE_URL`.
- Implemented `components/DemoSection.tsx` as a controlled client component with dataset loading from `/datasets`, input validation, loading and error states, POST integration with `/predict`, ensemble-first result presentation, model-comparison bars, and backend insight rendering.
- Added a dataset-aware payload translation layer in the demo so the compact UI inputs (`KLOC`, `Complexity`, `Team Experience`, `Reliability`) are converted into valid feature proxies for the China, COCOMO-81, and Desharnais baseline pipelines.
- Added `PROJECT_SETUP.md` at the repository root with separate backend and frontend startup commands for the monorepo workflow.
- Updated `.gitignore` to exclude `frontend/node_modules`, `frontend/.next`, and `frontend/out`.
- Validation: `npm install` completed successfully in `frontend/`, editor diagnostics reported no frontend errors, and `npm run build` completed successfully with a production Next.js build.

### 2026-05-01 - Editorial homepage redesign for the Next.js frontend

- Reworked the landing page presentation in `frontend/app/page.tsx`, `frontend/components/Navbar.tsx`, `frontend/components/Hero.tsx`, `frontend/components/Features.tsx`, and `frontend/components/Footer.tsx` to replace the earlier symmetric product-template look with a more distinctive editorial composition.
- Updated `frontend/app/globals.css` with a warmer paper palette, custom panel and section-wash utilities, and an archival-style diagram surface so the visual language feels closer to a publication layout than a generic SaaS dashboard.
- Restyled `frontend/components/DemoSection.tsx` so the live prediction demo remains the functional core of the page while visually matching the new editorial system.
- Constraint note: no Stitch MCP integration was available in the current tool environment, so the redesign was implemented directly in code as an original Heritage-inspired interpretation rather than by importing an external design system.
- Validation pending after this visual pass: rerun frontend diagnostics and a production Next.js build.

- Completed the reduced-budget clean benchmark run locally with `scripts/run_clean_benchmark.py --training-epochs 5 --tuning-epochs 3 --n-particles 2 --iters 1 --ensemble-size 2 --ensemble-epochs 5` and saved the regenerated outputs under `results/metrics/` and `models/`.
- Regenerated `results/metrics/holdout_results.csv` and `results/metrics/full_comparison_final.csv` with the full 9-model schema for each dataset, giving 27 data rows per file across China, COCOMO-81, and Desharnais.
- Regenerated MLP artifacts alongside the existing CNN outputs, including `models/mlp_baseline_china.h5`, `models/mlp_pso_china.h5`, `models/mlp_baseline_cocomo81.h5`, `models/mlp_pso_cocomo81.h5`, `models/mlp_baseline_desharnais.h5`, and `models/mlp_pso_desharnais.h5`.
- Holdout RMSE snapshot from `results/metrics/holdout_results.csv`: China best model XGBoost at 1467.3214, COCOMO-81 best model LinearRegression at 398.0482, and Desharnais best model LinearRegression at 1997.9377.
- Final 5-fold RMSE snapshot from `results/metrics/full_comparison_final.csv`: China best model RandomForest at 1285.6427, COCOMO-81 best model RandomForest at 999.3957, and Desharnais best model RandomForest at 3464.0637.
- The new neural rows are now persisted in the final comparison output for every dataset: `MLP_baseline`, `MLP_PSO`, `CNN_PSO_ensemble`, and `MLP_PSO_ensemble`.

### 2026-04-26 - Notebook runtime fixes and current CNN+PSO status check

- Reviewed the currently saved benchmark artifacts while debugging the notebooks. The persisted `CNN_PSO` holdout RMSE values are 6296.0099 for China, 642.5424 for COCOMO-81, and 5773.1931 for Desharnais from `results/metrics/holdout_results.csv`.
- Reviewed the persisted 5-fold comparison as well. The saved `CNN_PSO` RMSE mean values are 7707.2841 for China, 1548.4810 for COCOMO-81, and 6788.7100 for Desharnais from `results/metrics/full_comparison_final.csv`, which remain well behind the strongest classical baselines.
- Observed that `models/best_hyperparams.json` currently stores the same `cnn_pso` configuration for all three datasets, which is consistent with the latest persisted artifacts having been generated from a reduced-budget tuning run rather than a final long-budget experiment.
- Fixed `src/preprocess.py` so `scale_numeric_features()` now writes scaled numeric columns back with float-safe assignment, removing the pandas `LossySetitemError` / `TypeError` that broke `notebooks/02_preprocessing.ipynb` on newer pandas versions.
- Updated `notebooks/03_baselines.ipynb` so the main training cell builds baseline estimators via `src.cv_pipeline.get_baseline_model_builders()`, removing the `NameError` path when the old helper-definition cell was skipped.
- Replaced an accidentally saved markdown block in `notebooks/05_pso.ipynb` with a real code cell that runs `run_full_benchmark(...)`, so the downstream display and save cells no longer depend on undefined `benchmark_results`, `holdout_results`, and `full_comparison_final` variables.
- Updated the setup cells in `notebooks/02_preprocessing.ipynb`, `notebooks/03_baselines.ipynb`, `notebooks/04_cnn.ipynb`, and `notebooks/05_pso.ipynb` to use dynamic Colab detection through `importlib`, which removes the local unresolved-import noise around `google.colab` in normal VS Code environments.
- Validation: reran the previously failing preprocessing cell in `notebooks/02_preprocessing.ipynb`, reran the setup and training cells in `notebooks/03_baselines.ipynb`, and reran the setup cells in `notebooks/04_cnn.ipynb` and `notebooks/05_pso.ipynb` successfully.
- Current diagnostics after the fix pass show no code errors in `src/preprocess.py` or `notebooks/05_pso.ipynb`. The remaining notebook diagnostics are spelling/noise from notebook JSON and saved outputs rather than executable runtime failures.
- Remaining risk: `notebooks/05_pso.ipynb` was not rerun end-to-end at the full 100/30/15/25 benchmark budget in this local session because that full benchmark would be substantially heavier than the targeted runtime validation performed here.

### 2026-04-29 - Session start: results checkpoint before notebook 05_pso run

- User is about to run `notebooks/05_pso.ipynb` (full PSO tuning and benchmark).
- Saved artifacts status review:
  - Reduced-budget benchmark from 2026-04-25 persists in `results/metrics/` and `models/`.
  - `results/metrics/full_comparison_final.csv` contains 9-model comparison (27 rows): LinearRegression, RandomForest, XGBoost baselines, CNN_baseline, CNN_PSO, MLP_baseline, MLP_PSO, CNN_PSO_ensemble, MLP_PSO_ensemble.
  - `results/metrics/holdout_results.csv` contains holdout RMSE for all 9 models per dataset.
  - Holdout RMSE snapshot (reduced budget): China best 1467.32 (XGBoost), COCOMO-81 best 398.05 (LinearRegression), Desharnais best 1997.94 (LinearRegression).
  - 5-fold RMSE snapshot (reduced budget): China best 1285.64 (RandomForest), COCOMO-81 best 999.40 (RandomForest), Desharnais best 3464.06 (RandomForest).
  - CNN_PSO holdout RMSE reduced-budget values: China 6296.01, COCOMO-81 642.54, Desharnais 5773.19.
  - CNN_PSO 5-fold RMSE reduced-budget means: China 7707.28, COCOMO-81 1548.48, Desharnais 6788.71.
  - Best hyperparams in `models/best_hyperparams.json`: shared config across datasets (filters=8, kernel_size=4, lr=0.00416, dropout=0.319, conv_layers=3, batch_size=8).
- Key observation: Classical baselines (RandomForest, XGBoost, LinearRegression) remain superior to CNN and CNN+PSO variants in both holdout and 5-fold evaluation under reduced training budgets.
- Next step: Full-budget run of `notebooks/05_pso.ipynb` with production epochs/particles/iterations to see if increased PSO search intensity and longer neural training close the gap to classical baselines or improve CNN generalization.

### 2026-05-01 - Leakage-safe baseline export script and pickle artifacts

- Added `scripts/save_baselines.py` as an end-to-end baseline export entry point that loads raw datasets, splits train/test, trains or reloads baseline models, evaluates RMSE and MAE, and saves `.pkl` artifacts.
- Added `src/baseline_models.py` to centralize the shared `LinearRegression`, `RandomForest`, and `XGBoost` builder configuration and file names.
- Added `build_feature_preprocessor()` to `src/preprocess.py` so tabular preprocessing now fits imputation, categorical encoding, and optional numeric scaling on the training split only.
- Updated `src/cv_pipeline.py` to reuse the shared baseline builder module instead of keeping a duplicate baseline-model definition.
- Saved baseline artifacts under dataset-specific subdirectories to preserve the requested file names without collisions across datasets: `models/china/{lr_model.pkl,rf_model.pkl,xgb_model.pkl}`, `models/cocomo81/{lr_model.pkl,rf_model.pkl,xgb_model.pkl}`, and `models/desharnais/{lr_model.pkl,rf_model.pkl,xgb_model.pkl}`.
- Full export validation ran successfully in the configured virtual environment with exact holdout metrics from `scripts/save_baselines.py`:
	- China: `LinearRegression` RMSE `1296.143319`, MAE `446.369674`; `RandomForest` RMSE `1604.754387`, MAE `384.539133`; `XGBoost` RMSE `1503.300169`, MAE `388.871586`.
	- COCOMO-81: `LinearRegression` RMSE `1922.377594`, MAE `1461.029797`; `RandomForest` RMSE `430.002079`, MAE `246.143128`; `XGBoost` RMSE `620.308905`, MAE `297.070859`.
	- Desharnais: `LinearRegression` RMSE `1943.914123`, MAE `1435.054687`; `RandomForest` RMSE `2294.399361`, MAE `1765.977451`; `XGBoost` RMSE `2245.187760`, MAE `1693.691995`.
- Reload-path validation also passed: rerunning the script logic with `reuse_existing=True` for China returned `loaded` status for `LinearRegression`, `RandomForest`, and `XGBoost`.

### 2026-05-01 - Phase 2 baseline ensemble module for saved `.pkl` models

- Extended `src/ensemble.py` without breaking the existing neural `ensemble_predict(...)` path used by `src/cv_pipeline.py`.
- Added a baseline-model ensemble layer that loads the saved sklearn pipelines from dataset-specific model directories and supports both simple averaging and configurable weighted averaging.
- Added `BaselineEnsemble`, `initialize_ensemble(...)`, `get_loaded_ensemble()`, and `predict_ensemble(input_features)` so FastAPI-style startup can load models once and request handlers can call a cached prediction function.
- Added `load_baseline_models(...)`, `simple_average_predictions(...)`, `weighted_average_predictions(...)`, `compare_predictions(...)`, and `compare_loaded_predictions(...)` for reusable ensemble operations and debugging.
- Fixed baseline prediction input handling so raw `np.ndarray` rows are reconstructed into pandas `DataFrame` objects using the saved pipeline feature names before prediction; this avoids the sklearn `ColumnTransformer` failure that occurs when named-column pipelines receive bare NumPy arrays.
- Made TensorFlow import lazy inside the neural-only `ensemble_predict(...)` function so the baseline `.pkl` ensemble path no longer pulls TensorFlow into API startup or emits TF runtime warnings.
- Validation: initialized the China baseline ensemble from `models/china` and predicted successfully from a raw NumPy feature row. Simple averaging returned `6886.097622022004`, with individual predictions `LinearRegression=7193.876004086845`, `RandomForest=7510.966666666666`, and `XGBoost=5953.4501953125`.
- Validation: weighted averaging also passed using weights `{LinearRegression: 0.2, RandomForest: 0.3, XGBoost: 0.5}`, returning `6668.790298473619` for the same China sample row.
- Final diagnostics: no editor errors remain in `src/ensemble.py` or `src/cv_pipeline.py` after the ensemble-module update.

### 2026-05-01 - Production prediction service module for saved baseline pipelines

- Added `src/config.py` to centralize dataset model directories, RMSE scores for `RandomForest`, `XGBoost`, and `LinearRegression`, model-output keys, and default inverse-RMSE ensemble weights.
- Added `src/predictor.py` as the FastAPI-ready prediction service layer for the saved sklearn pipeline artifacts.
- Implemented lazy dataset-model caching through `PredictionService`, with `load_models()` for explicit startup warmup and `get_prediction_service()` / `load_prediction_service()` singleton helpers for API integration.
- Implemented request-time conversion from raw input dictionaries to one-row pandas `DataFrame` payloads using the exact `feature_names_in_` schema embedded in the saved pipelines, so preprocessing remains inside the stored sklearn `Pipeline` objects and is never reapplied manually.
- Implemented individual predictions for `RandomForest`, `XGBoost`, and `LinearRegression`, plus ensemble prediction through both simple averaging and weighted averaging.
- Implemented automatic best-model selection from precomputed RMSE scores in `src/config.py`, returning the model name with the lowest configured RMSE for the selected dataset.
- Implemented safe input handling: unknown dataset keys raise a controlled dataset error, non-dictionary input raises `InvalidInputError`, unexpected input fields are ignored, and missing expected fields are inserted as `np.nan` so the fitted imputers inside the saved pipelines can handle them safely.
- Validation: warmed the full prediction service with `load_prediction_service()`, then predicted successfully for the China dataset from a raw sample dictionary. Returned output format matched the production contract with keys `rf_prediction`, `xgb_prediction`, `lr_prediction`, `ensemble_prediction`, and `best_model`.
- Validation: China sample output with simple averaging was `{'rf_prediction': 7510.966666666666, 'xgb_prediction': 5953.4501953125, 'lr_prediction': 7193.876004086845, 'ensemble_prediction': 6886.097622022004, 'best_model': 'LinearRegression'}`.
- Validation: China sample output with weighted averaging also succeeded using default inverse-RMSE weights, returning `ensemble_prediction = 6889.2255625265825`.
- Validation: a China request with the `AFP` field omitted still produced a prediction successfully, confirming that the stored imputers handle missing columns once the service injects `np.nan` placeholders.
- Validation: invalid non-dictionary input raised the expected controlled error `InvalidInputError: input_payload must be a dictionary-like object`.
- Final diagnostics: no editor errors remain in `src/config.py` or `src/predictor.py` after the prediction-service update.

### 2026-05-01 - Standalone predictor validation script

- Added `test_predictor.py` at the repository root as a simple runnable validation script for the production prediction service in `src/predictor.py`.
- The script initializes the service once with `load_prediction_service()`, builds a valid `cocomo81` sample input from the first row of `data/processed/cocomo81_processed.csv`, and then exercises the public `predict_cost(...)` API.
- Covered scenarios: valid prediction, missing-field prediction with two fields removed, invalid dataset handling, invalid non-dictionary input handling, simple ensemble prediction, and weighted ensemble prediction with custom weights `{RandomForest: 0.5, XGBoost: 0.3, LinearRegression: 0.2}`.
- Validation: ran `python test_predictor.py` in the configured virtual environment and all six scenario checks passed without the script crashing.
- Observed `cocomo81` happy-path output: `rf_prediction=524.5173333333332`, `xgb_prediction=-273.9039001464844`, `lr_prediction=13267.811313421693`, `ensemble_prediction=4506.1415822028475`, `best_model='RandomForest'`.
- Observed missing-field output after removing `num` and `dev_mode`: `rf_prediction=402.99833333333316`, `xgb_prediction=459.2120666503906`, `lr_prediction=13486.30684585142`, `ensemble_prediction=4782.839081945048`, `best_model='RandomForest'`.
- Observed weighted-ensemble output with custom weights: `ensemble_prediction=2833.64975930706` while the individual model predictions remained unchanged from the happy-path run.
- Validation also confirmed the expected controlled errors: `InvalidDatasetError` for `invalid_dataset` and `InvalidInputError` for a non-dictionary payload.

### 2026-05-01 - FastAPI backend scaffold for production prediction service

- Added a dedicated backend structure under `backend/` with `main.py`, route modules for `/predict`, `/health`, and `/datasets`, shared Pydantic request/response models, and backend constants in `backend/core/config.py`.
- Implemented FastAPI startup using a lifespan context manager and warmed the production prediction service once per process through `load_prediction_service()`.
- Added CORS middleware configured for development with all origins, methods, and headers allowed.
- Mapped prediction-service errors to API responses: `InvalidDatasetError` returns HTTP 400, `InvalidInputError` returns HTTP 422, and uncaught exceptions return HTTP 500 with JSON error bodies.
- Implemented the `/predict` response contract expected by the frontend, including `rf_prediction`, `xgb_prediction`, `lr_prediction`, `ensemble_prediction`, `best_model`, and the fixed insight template `Best model for this dataset is {best_model}`.
- Updated `requirements.txt` to include `fastapi` and `uvicorn[standard]` so the backend can run in the project virtual environment with `uvicorn main:app --reload` from the `backend/` directory.
- Validation: installed the new backend dependencies in the configured virtual environment, then exercised the app with FastAPI `TestClient` through the real lifespan path.
- Validation results: `/health` returned HTTP 200 with `{"status": "ok"}`, `/datasets` returned the three supported datasets, invalid dataset requests returned HTTP 400, invalid-input requests returned HTTP 422, and CORS preflight responded successfully with the expected allow headers.
- Positive-path validation also succeeded with a real `china` payload built from `data/processed/china_processed.csv`, returning HTTP 200 and the expected prediction fields with `best_model='LinearRegression'`.
- Remaining integration step: wire the Next.js frontend to the new backend endpoints and decide whether to keep development-open CORS settings or narrow them for deployment.

### 2026-05-01 - Phase 0 contract freeze for universal AI-first estimator

- Added `PHASE0_CONTRACT_FREEZE.md` to lock the public and internal product contract before schema and orchestration rewrites.
- Documented the frozen public concepts for the estimator flow: universal project brief, prediction mode label, estimated effort, derived INR base cost, display currency, assumptions, warnings, confidence, and schema version.
- Documented internal-only concepts that must stay out of the public UI and API language: detected route, mapped feature vector, routing confidence/rationale, provider name, prompt profile, model adapter, and guardrail/runtime metadata.
- Captured the Phase 0 request/response contract draft with stable field names that support both AI mode and model mode behind one public shape.
- Captured a file-level cleanup plan for outdated wording and dataset/model exposure across backend contract files and frontend UI/copy touchpoints, including `backend/schemas/request_response.py`, `backend/routes/predict.py`, `backend/routes/meta.py`, `frontend/lib/api.ts`, and `frontend/components/DemoSection.tsx`.
- Validation: contract-freeze artifact created and aligned with the implementation roadmap requirement that users never see dataset names in the public estimation flow.
- Next step: execute Phase 1 by implementing the universal input schema in backend and frontend types while keeping the frozen naming and response shape.

### 2026-05-01 - Phase 1 universal input schema and normalization layer

- Implemented the Phase 1 universal public input models in `backend/schemas/request_response.py` with strict validation bounds and enums.
- Added `ComplexityLevel` and `ReliabilityLevel` enums with allowed categorical values `low`, `medium`, and `high`.
- Added `UniversalProjectBrief` fields and numeric bounds: `num_screens` (1-5000), `num_entities` (1-10000), `duration_months` (>0 to 120), `team_experience_years` (0-50), `pm_experience_years` (0-50), and `team_size` (1-1000).
- Added request-level Phase 1 model `UniversalPredictionRequest` with schema version support and currency validation/normalization to uppercase 3-letter codes (default `INR`).
- Added normalization output models and helper `normalize_universal_request(...)` so backend can validate and normalize universal payloads before later routing work.
- Added a dedicated backend endpoint `POST /predict/universal/normalize` in `backend/routes/predict.py` that returns the normalized universal payload.
- Updated `frontend/lib/api.ts` with matching shared Phase 1 types (`UniversalProjectBrief`, `UniversalPredictRequest`, `NormalizedUniversalPredictRequest`) using identical field names and categorical sets.
- Added frontend API helper `normalizeUniversalPayload(...)` to call the new backend normalization endpoint.
- Backward compatibility preserved for current demo runtime: legacy dataset-based `/predict` request/response types and methods remain unchanged during this phase.
- Validation: editor diagnostics report no errors in `backend/schemas/request_response.py`, `backend/routes/predict.py`, and `frontend/lib/api.ts` after the Phase 1 changes.
- Next step: Phase 2 routing and mapping modules to convert universal payloads into internal dataset-specific feature vectors.

### 2026-05-01 - Implementation plan pivot to adaptive two-step intake flow

- Rewrote `IMPLEMENTATION_PLAN.md` to explicitly follow the approved user journey: limited universal intake questions, hidden internal route prediction, adaptive follow-up inputs, and final prediction.
- Updated plan wording to keep dataset names fully hidden in public UX while preserving internal route and mapping compatibility with China, COCOMO81, and Desharnais feature families.
- Reorganized roadmap for easier implementation by splitting the adaptive flow into explicit phases: route prediction service, follow-up question pack system, mapper/final assembly, two-step public API consolidation, and adaptive frontend UX.
- Added clearer execution guidance with completed foundations marked (Phase 0 and Phase 1) and an execution-friendly order for remaining phases.
- Updated verification checklist to include adaptive-stage requirements (Stage 1 limit, Stage 2 adaptive rendering, hidden dataset identifiers in public responses, final prediction from merged inputs).
- Validation: rewritten plan now directly matches the requested flow and remains compatible with AI-first delivery plus later model-mode integration.

### 2026-05-01 - Phase 2 route prediction service implementation

- Implemented `backend/services/router.py` with a deterministic `UniversalRouter` that scores all internal route families (`china`, `cocomo81`, `desharnais`) using weighted heuristics over Stage 1 universal fields.
- Added route confidence scoring, top-signal rationale generation, and neutral follow-up pack mapping (`adaptive_pack_alpha`, `adaptive_pack_beta`, `adaptive_pack_gamma`) so public responses do not expose dataset names.
- Extended `backend/schemas/request_response.py` with Phase 2 models:
	- `InternalRoute`
	- `RouteInferenceMetadata` (internal/admin metadata model)
	- `IntakeInferenceResponse` (public-safe Stage 1 intake response)
- Updated `backend/routes/predict.py` with new endpoint `POST /predict/intake`:
	- Validates and normalizes universal payload.
	- Infers hidden route and follow-up pack id.
	- Returns public-safe response with `intake_id`, `follow_up_pack_id`, `intake_version`, and `next_step`.
	- Caches internal route metadata in memory for future admin diagnostics.
- Added `backend/services/__init__.py` to register the new services package cleanly.
- Validation:
	- Editor diagnostics show no errors in `backend/schemas/request_response.py`, `backend/services/router.py`, and `backend/routes/predict.py`.
	- Runtime smoke test via FastAPI `TestClient` returned HTTP `200` for `POST /predict/intake` with response shape:
		- `intake_id` generated UUID
		- `follow_up_pack_id='adaptive_pack_gamma'`
		- `intake_version=1`
		- `next_step='collect_followup_inputs'`
- Plan tracking updated: `IMPLEMENTATION_PLAN.md` now marks Phase 2 status as completed.

### 2026-05-01 - Phase 3 and 4 implemented together (follow-up packs + mapper assembly)

- Implemented Phase 3 question-pack system in `backend/services/followup_questions.py` with a versioned registry keyed by hidden internal routes and neutral public labels.
- Added three adaptive follow-up packs:
	- `adaptive_pack_alpha` (volume/change details)
	- `adaptive_pack_beta` (implementation constraints and tooling)
	- `adaptive_pack_gamma` (process/data complexity)
- Added strict normalization and validation for Stage 2 answers (required fields, numeric bounds, select-option checks) via `normalize_followup_answers(...)`.
- Extended `backend/schemas/request_response.py` with new Phase 3 and 4 models:
	- `FollowUpInputType`, `FollowUpQuestionField`, `FollowUpQuestionPack`, `IntakeFollowUpResponse`
	- `FinalAssemblyRequest`, `MappingDiagnostics`, `FinalAssemblyResponse`
- Implemented Phase 4 mapper in `backend/services/mapper.py` as `UniversalMapper` with route-specific assembly functions for China, COCOMO81, and Desharnais-compatible internal vectors.
- Added mapping confidence and rationale diagnostics in the assembled output and included unresolved optional field tracking.
- Updated `backend/routes/predict.py` with new endpoints:
	- `GET /predict/followup/{intake_id}` to return dynamic follow-up questions
	- `POST /predict/final/assemble` to validate Stage 2 answers and assemble final mapped feature vector
- Added in-memory cache of normalized Stage 1 intake payloads to support Phase 4 final assembly using the same intake context.
- Added mapper tests in `backend/tests/test_mapper.py` covering key-field presence and diagnostics for all three internal routes.
- Updated `frontend/lib/api.ts` with shared Phase 3 and 4 types and helper methods:
	- `inferIntakeRoute(...)`
	- `getFollowUpQuestions(...)`
	- `assembleFinalInputs(...)`
- Validation:
	- Editor diagnostics report no errors in all touched backend and frontend files.
	- End-to-end API smoke test passed for intake -> follow-up -> final assembly:
		- `POST /predict/intake` returned HTTP `200`
		- `GET /predict/followup/{intake_id}` returned pack `adaptive_pack_gamma`
		- `POST /predict/final/assemble` returned HTTP `200` with `internal_route='desharnais'` and mapped features including `Adjustment`, `Length`, `ManagerExp`, and `PointsNonAdjust`.
	- Mapper test run passed: `Ran 3 tests ... OK` and `FAILED 0`.
- Plan tracking updated: `IMPLEMENTATION_PLAN.md` now marks Phase 3 and Phase 4 status as completed.
