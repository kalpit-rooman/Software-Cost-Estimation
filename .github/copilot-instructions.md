# Software Cost Estimation Project

## Project Context

Final year project: software development effort estimation using CNN optimized with PSO (Particle Swarm Optimization). Uses 3 datasets: COCOMO-81, Desharnais, China.

## Architecture

- `src/` — Reusable Python modules (data loading, preprocessing, CNN model, PSO optimizer, evaluation)
- `notebooks/` — Sequential Jupyter notebooks (01-07), each builds on previous
- `app/` — Streamlit web application
- `data/raw/` — Original datasets (never modify), `data/processed/` — Cleaned CSVs
- `models/` — Saved trained models (.h5 for CNN, .pkl for sklearn)
- `results/metrics/` — CSV metric files, `results/figures/` — Saved plots

## Code Style

- Python 3.10+, type hints on all function signatures
- Use existing src/ module patterns — each module has single responsibility
- Imports: stdlib → third-party → local (src.)
- Constants at module top: ROOT_DIR, path constants using pathlib.Path
- All model training must use random_state=42 for reproducibility

## Key Patterns

- Data loading: use `src.data_loader.load_all_raw_datasets()` — never load raw files directly
- Preprocessing: use `src.preprocess.preprocess_dataset()` pipeline — returns (X_scaled, y, target_col)
- CNN input: always reshape with `src.cnn_model.reshape_for_cnn()` before training
- Metrics: use `src.evaluate.compute_regression_metrics()` — always save via `save_metrics()`
- PSO: use `src.pso_optimizer.tune_cnn_with_pso()` — decode positions with `decode_cnn_hyperparameters()`

## Testing & Validation

- Verify CNN+PSO RMSE < Linear Regression RMSE on at least one dataset
- All models must be evaluated with 5-fold cross-validation for final results
- Streamlit app must load saved models from `models/`, never retrain at runtime

## Dependencies

tensorflow, scikit-learn, pyswarms, xgboost, pandas, numpy, scipy, matplotlib, seaborn, streamlit, plotly
