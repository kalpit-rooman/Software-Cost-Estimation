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