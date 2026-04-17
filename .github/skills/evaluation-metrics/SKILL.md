---
name: evaluation-metrics
description: "Evaluate ML models for software cost estimation. Use when: adding metrics (R², MAPE, MdMRE, Pred25), implementing k-fold cross-validation, running cross-dataset evaluation, creating comparison visualizations, generating publication-quality charts, or saving results."
---

# Evaluation & Metrics

## When to Use

- Adding new metrics to `src/evaluate.py`
- Creating cross-validation in `src/cross_validation.py`
- Building evaluation notebook `notebooks/06_cross_dataset_evaluation.ipynb`
- Creating visualization notebook `notebooks/07_visualizations.ipynb`

## Metrics to Add (in `src/evaluate.py`)

Add to `compute_regression_metrics()`:

- **R²**: `sklearn.metrics.r2_score` — proportion of variance explained
- **MAPE**: `mean(abs((y_true - y_pred) / y_true)) * 100` — handle zero division
- **MdMRE**: `median(abs((y_true - y_pred) / y_true))` — robust to outliers
- **Pred(25)**: `mean(abs((y_true - y_pred) / y_true) <= 0.25) * 100` — % within 25%

## Cross-Validation Procedure

- File: `src/cross_validation.py`
- Use `sklearn.model_selection.KFold(n_splits=5, shuffle=True, random_state=42)`
- For CNN: rebuild model each fold (avoid weight leakage)
- Return dict: {metric_name: [fold1, fold2, ...fold5]} for mean ± std reporting

## Cross-Dataset Evaluation

- Notebook: `notebooks/06_cross_dataset_evaluation.ipynb`
- Load ALL 3 processed datasets
- Run ALL models (LR, RF, XGBoost, CNN, CNN+PSO) on EACH dataset
- Generate combined results DataFrame with columns: dataset, model, mae, rmse, r2, mape, mdmre, pred25

## Visualizations

- Notebook: `notebooks/07_visualizations.ipynb`
- Save all figures to `results/figures/`
- Required plots:
  1. Grouped bar chart: models × datasets for each metric
  2. Training loss curves: CNN vs CNN+PSO (from history)
  3. PSO convergence: best fitness vs iteration
  4. Box plots: k-fold metric distributions per model
  5. Heatmap: models (rows) × metrics (columns) for each dataset
- Use matplotlib/seaborn, figsize=(10,6), tight_layout, dpi=150
