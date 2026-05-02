# Project Log

Last updated: 2026-04-25

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

### Still pending or incomplete

- `notebooks/06_cross_dataset_evaluation.ipynb` and `notebooks/07_visualizations.ipynb` are not present yet.
- A dedicated cross-validation module for the final 5-fold evaluation is not present yet.
- The `app/` Streamlit interface described in the plan is not present yet.
- Saved baseline `.pkl` artifacts are not visible in the current repository tree.
- Final comparison figures under `results/figures/` are not visible in the current repository tree.

## Latest Session Note

### 2026-04-25 - Metrics review and logging setup

- Recomputed the direct delta between `cnn_baseline` and `cnn_pso` from the saved metric CSVs.
- Confirmed PSO improvements on COCOMO-81 and Desharnais, but a regression on China.
- Confirmed that the best overall models remain classical baselines, not CNN+PSO.
- Created a persistent project log so future progress, experiments, bug fixes, and metric updates can be recorded in one place.
- Added a dedicated skill to keep this log updated aggressively whenever project progress is reported.

## Chronological Log

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

### 2026-05-01 - Performance check and initial input schema clarification

- Reviewed the current saved evaluation artifacts used for model comparison: `results/metrics/full_comparison_final.csv`, `results/metrics/holdout_results.csv`, and per-dataset baseline files under `results/metrics/`.
- Verified current leaderboard from `results/metrics/full_comparison_final.csv` (5-fold means):
	- China: best RMSE_mean is `RandomForest` at `1285.642680`; best R2_mean is also `RandomForest` at `0.961891`.
	- COCOMO-81: best RMSE_mean is `XGBoost` at `953.789013`; best R2_mean is `RandomForest` at `0.520860`.
	- Desharnais: best RMSE_mean is `RandomForest` at `3464.063673`; best R2_mean is `XGBoost` at `0.383139`.
- Confirmed production inference path still uses saved sklearn baseline pipelines (`src/predictor.py`) and not CNN artifacts at runtime.
- Confirmed current public intake starts with a universal brief (`backend/schemas/request_response.py`) and frontend form fields in `frontend/components/EstimationFlow.tsx`: screens/pages, data entities, duration, team size, team experience, PM experience, complexity, reliability, optional notes, target currency, plus dataset-specific follow-up fields.
- Confirmed original dataset-native input schemas from raw data (via `src.data_loader.load_all_raw_datasets()` + `src.preprocess.identify_effort_column()`):
	- cocomo81 target `actual`; features: `num, dev_mode, rely, data, cplx, time, stor, virt, turn, acap, aexp, pcap, vexp, lexp, modp, tool, sced, loc`.
	- desharnais target `Effort`; features: `id, Project, TeamExp, ManagerExp, YearEnd, Length, Transactions, Entities, PointsNonAdjust, Adjustment, PointsAjust, Language`.
	- china target `Effort`; features: `ID, AFP, Input, Output, Enquiry, File, Interface, Added, Changed, Deleted, PDR_AFP, PDR_UFP, NPDR_AFP, NPDU_UFP, Resource, Dev.Type, Duration, N_effort`.
- Noted consistency risk to revisit: runtime RMSE constants in `src/config.py` (`MODEL_RMSE_SCORES`) do not match the currently saved baseline metric CSV values, which can affect reported `best_model` labels in prediction responses.

### 2026-05-01 - Runtime RMSE config synced to saved baseline metrics

- Updated `src/config.py` so `MODEL_RMSE_SCORES` now matches `results/metrics/baseline_metrics.csv` exactly for all three datasets and three baseline models.
- Applied exact RMSE values:
	- China: `RandomForest=1636.3238338522758`, `XGBoost=1467.3213518914497`, `LinearRegression=53165.28424556006`
	- COCOMO-81: `RandomForest=482.4925319563499`, `XGBoost=451.19558709684895`, `LinearRegression=395.08088778481056`
	- Desharnais: `RandomForest=2363.717631202568`, `XGBoost=2548.4416951395297`, `LinearRegression=1997.9362501688217`
- Impact: runtime `best_model` selection and derived inverse-RMSE ensemble weights are now aligned with the currently saved baseline evaluation artifact.
- Validation: checked `src/config.py` diagnostics after edit; no errors reported.

### 2026-05-01 - Frontend estimation flow redesigned to simplified multi-step UX

- Replaced the previous dataset-heavy estimate UI with a minimal progressive flow in `frontend/components/EstimationFlow.tsx`.
- Added reusable step components under `frontend/components/estimation/`:
	- `Step1ProjectType.tsx` (3-card project type selection)
	- `Step2CoreInputs.tsx` (three slider-based core inputs)
	- `Step3AdvancedInputs.tsx` (toggleable advanced inputs grouped into technical/team factors)
	- `InputCard.tsx`, `SliderInput.tsx`, `SelectInput.tsx`, and shared `types.ts`.
- Implemented internal-only mapping from simplified advanced choices to cost-driver concepts (`RELY`, `DATA`, `TIME`, `TOOL`, team capability proxy) and dataset-specific follow-up payloads before calling `submitDirectEstimate(...)`.
- Added a result section with "Estimated Effort" card and an "Explain Estimation" area containing an "Ask AI" trigger and Groq chatbot placeholder container.
- Validation pending: frontend dependency install and Next.js build/type check were not yet executed at this logging point.

### 2026-05-01 - Frontend flow validation pass after redesign

- Installed requested icon package in the frontend workspace: `@phosphor-icons/react`.
- Verified no editor diagnostics in all newly added estimation flow components.
- Executed frontend production build command from terminal and confirmed success (`npm run build` exit code `0`).

### 2026-05-02 - Production fix: Redis-backed intake cache for multi-worker reliability

- Replaced the process-local Stage 1 intake cache in `backend/routes/predict.py` with a shared cache store backed by Redis, removing the cross-worker `intake_id not found` failure mode in multi-worker deployments.
- Added a new cache service module at `backend/services/intake_cache.py` that:
	- stores `RouteInferenceMetadata` and `NormalizedUniversalPredictionRequest` as JSON in Redis with TTL,
	- uses namespaced keys per intake,
	- falls back to bounded in-memory cache only when Redis is not configured or temporarily unavailable,
	- enforces TTL expiry in fallback mode as well.
- Added production cache configuration knobs in `backend/core/config.py`:
	- `REDIS_URL`
	- `INTAKE_CACHE_TTL_SECONDS`
	- `MAX_CACHED_INTAKES`
- Updated `backend/.env.example` with Redis/intake cache settings and operational comments for production usage.
- Added `redis>=5.0` to `requirements.txt` so Redis-backed caching works in deployed environments.
- Validation: editor diagnostics reported no errors in the touched backend files (`backend/services/intake_cache.py`, `backend/routes/predict.py`, `backend/core/config.py`).
- Remaining deployment step: set `REDIS_URL` in production environment and ensure a reachable Redis instance before running multiple API workers.