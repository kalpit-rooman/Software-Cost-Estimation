# Software Cost Estimation — Implementation Plan

## TL;DR

Upgrade the existing CNN+PSO software cost estimation project from a research prototype to a complete final year project by: (1) improving CNN+PSO to beat baselines, (2) adding rigorous cross-dataset evaluation with more metrics, (3) building a Streamlit web app for live prediction + model comparison dashboard, (4) writing a project report. Timeline: 1-2 weeks.

---

## Current State

- 5 notebooks (EDA → Preprocessing → Baselines → CNN → PSO) — all executed, results saved
- 3 datasets: COCOMO-81, Desharnais, China
- Baselines: LR (best, RMSE=1944), XGBoost (2245), RF (2283)
- CNN+PSO: RMSE=2453 (doesn't beat LR yet), raw CNN: RMSE=5690
- Evaluation: only on Desharnais, only MAE + RMSE, single 80/20 split
- No saved models, no web UI, no visualizations beyond basic EDA histograms

---

## Phase 1: Improve CNN+PSO Performance (Days 1-3)

> Goal: CNN+PSO should outperform all baselines

### Step 1.1 — Enhance CNN Architecture

- File: `src/cnn_model.py` → `build_cnn_regressor()`
- Add Batch Normalization after Conv1D
- Add Dropout (0.2-0.3) after Dense layers to prevent overfitting
- Add a second Conv1D layer (deeper model)
- Add optional MaxPooling1D between conv layers
- Make architecture tunable: expose `num_conv_layers`, `dropout_rate` as params

### Step 1.2 — Expand PSO Search Space

- File: `src/pso_optimizer.py`
- Add `dropout_rate` and `num_conv_layers` to search dimensions (6D instead of 4D)
- Increase particles: 10→15, iterations: 10→25
- Update `decode_cnn_hyperparameters()` for new dimensions
- Use validation loss (not just MAE) — consider RMSE as fitness

### Step 1.3 — Improve Training

- File: `src/cnn_model.py` → `train_cnn_model()`
- Add EarlyStopping callback (patience=10, restore_best_weights=True)
- Add ReduceLROnPlateau callback
- Increase max epochs to 100 (early stopping will regulate)
- Use larger validation split or k-fold within PSO objective

### Step 1.4 — Feature Engineering (new file)

- Create: `src/feature_engineering.py`
- Add log-transform for skewed effort targets (common in cost estimation)
- Add polynomial features for key interactions
- Add feature selection (remove low-variance / low-correlation features)

### Step 1.5 — Update Notebook 05_pso.ipynb

- Re-run with improved architecture + expanded PSO
- Verify CNN+PSO beats LR on Desharnais
- If still failing, try training on all 3 datasets combined

---

## Phase 2: Rigorous Evaluation (Days 3-5)

> Goal: Publication-quality metrics and cross-dataset validation

### Step 2.1 — Add More Metrics

- File: `src/evaluate.py` → `compute_regression_metrics()`
- Add: R² (coefficient of determination), MAPE (mean absolute percentage error), MdMRE (median magnitude of relative error), Pred(25) — % of estimates within 25% of actual
- These are standard in software cost estimation literature

### Step 2.2 — K-Fold Cross-Validation

- Create: `src/cross_validation.py`
- Implement 5-fold or 10-fold CV for all models
- Report mean ± std for each metric
- This replaces single 80/20 split for final results

### Step 2.3 — Cross-Dataset Evaluation

- Create: `notebooks/06_cross_dataset_evaluation.ipynb`
- Run ALL models on ALL 3 datasets (not just Desharnais)
- Generate per-dataset tables + aggregated comparison
- Identify which datasets suit CNN+PSO best

### Step 2.4 — Visualization Notebook

- Create: `notebooks/07_visualizations.ipynb`
- Grouped bar charts: all models × all datasets × each metric
- Training loss curves (CNN vs CNN+PSO)
- PSO convergence plot (fitness vs iteration)
- Radar/spider chart comparing model strengths
- Box plots from k-fold results
- Save all figures to `results/figures/`

### Step 2.5 — Save Trained Models

- After final training, save best models to `models/`
- CNN: save as .h5 or SavedModel format
- CNN+PSO: save as .h5 + save best hyperparams as JSON
- Baselines: save with joblib/pickle
- These are needed for the web app

---

## Phase 3: Streamlit Web Application (Days 5-8)

> Goal: Interactive demo for project presentation

### Step 3.1 — Project Structure

- Create: `app/` directory
  - `app/app.py` — main Streamlit entry point
  - `app/predict.py` — model loading + prediction logic
  - `app/pages/` — multi-page app

### Step 3.2 — Page 1: Home / Overview

- Project title, description, methodology summary
- Dataset overview cards (3 datasets with stats)
- Architecture diagram (can be a static image)

### Step 3.3 — Page 2: Predict Effort

- User selects dataset type (COCOMO/Desharnais/China)
- Form with input fields matching dataset features
- Select model (LR, RF, XGBoost, CNN, CNN+PSO)
- Click "Predict" → shows estimated effort
- Side-by-side comparison: all models' predictions for same input

### Step 3.4 — Page 3: Model Comparison Dashboard

- Interactive charts (Plotly) showing metrics across models/datasets
- Dropdown to filter by dataset
- Training history visualization
- PSO convergence visualization
- Best model recommendation

### Step 3.5 — Page 4: About / Methodology

- Explain CNN architecture
- Explain PSO optimization
- Show hyperparameter search results
- References

### Step 3.6 — Styling

- Dark/obsidian theme aligned with brand preference
- Custom CSS for polished look

---

## Phase 4: Documentation & Report (Days 8-10)

> Goal: Professional project submission

### Step 4.1 — Update README.md

- Installation instructions
- How to run notebooks
- How to launch web app (`streamlit run app/app.py`)
- Project structure explanation
- Results summary with key findings

### Step 4.2 — Project Report Structure (if writing report)

- Chapter 1: Introduction (problem statement, objectives, scope)
- Chapter 2: Literature Review (COCOMO, ML-based estimation, CNN for regression, PSO)
- Chapter 3: Methodology (datasets, preprocessing, model architectures, PSO integration)
- Chapter 4: Implementation (tools, code structure, web app design)
- Chapter 5: Results & Discussion (tables, charts, analysis)
- Chapter 6: Conclusion & Future Work
- References

---

## Relevant Files

### Existing (to modify)

- `src/cnn_model.py` — enhance architecture (BatchNorm, Dropout, deeper model)
- `src/pso_optimizer.py` — expand search space, more particles/iterations
- `src/evaluate.py` — add R², MAPE, MdMRE, Pred(25)
- `notebooks/05_pso.ipynb` — re-run with improvements
- `README.md` — comprehensive documentation update

### New files to create

- `src/feature_engineering.py` — log transforms, poly features, feature selection
- `src/cross_validation.py` — k-fold CV wrapper
- `notebooks/06_cross_dataset_evaluation.ipynb` — all models × all datasets
- `notebooks/07_visualizations.ipynb` — publication-quality charts
- `app/app.py` — Streamlit main app
- `app/predict.py` — model loading + inference
- `app/pages/` — multi-page Streamlit pages
- `results/figures/` — saved visualization PNGs

---

## Verification

1. **Performance**: CNN+PSO RMSE should be lower than Linear Regression (1944) on at least Desharnais
2. **Metrics**: All 5 models evaluated on all 3 datasets, with 5+ metrics each, using k-fold CV
3. **Web app**: `streamlit run app/app.py` launches successfully, predictions work, charts render
4. **Models saved**: `models/` contains .h5 and .pkl files
5. **Figures**: `results/figures/` has comparison bar charts, convergence plots, training curves
6. **README**: Fresh clone + `pip install -r requirements.txt` + notebook sequence works

---

## Decisions

- **Web framework**: Streamlit (fastest for ML demos, no frontend needed, good for academic projects)
- **Cross-validation**: 5-fold (balances robustness vs training time for 3 datasets)
- **Feature engineering**: Log-transform effort target (standard in cost estimation literature, addresses skew)
- **Presentation**: Web app IS the demo — no separate slides needed unless teacher requires it
- **Scope boundary**: NOT building a production deployment, just a local Streamlit app

---

## Further Considerations

1. **Combined dataset training**: If CNN+PSO still underperforms on individual small datasets, consider training on combined (all 3 datasets) after feature alignment — small datasets (63 rows for COCOMO-81) may limit CNN.
2. **LSTM alternative**: If CNN still struggles, a quick LSTM/Bi-LSTM variant could be added as another DL approach — more justifiable for sequential feature relationships.
3. **Report necessity**: Confirm with teacher if a formal report is required or if the web app + code + README suffices.
