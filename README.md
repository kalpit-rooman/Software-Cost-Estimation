# Software Cost Estimation (CNN + PSO)

This project estimates software development effort using:
- Baseline ML models (Linear Regression, Random Forest, XGBoost)
- A 1D CNN regressor
- PSO (Particle Swarm Optimization) to tune CNN hyperparameters

The workflow is organized so baseline models are trained first, then CNN, then CNN+PSO for fair comparison.

## Project Structure

```text
Software-cost-Estimation/
|-- data/
|   |-- raw/
|   |   |-- COCOMO-81.csv
|   |   |-- Desharnais.csv
|   |   `-- china.arff
|   `-- processed/
|-- notebooks/
|   |-- 01_eda.ipynb
|   |-- 02_preprocessing.ipynb
|   |-- 03_baselines.ipynb
|   |-- 04_cnn.ipynb
|   `-- 05_pso.ipynb
|-- results/
|   `-- metrics/
|-- src/
|   |-- data_loader.py
|   |-- preprocess.py
|   |-- cnn_model.py
|   |-- pso_optimizer.py
|   `-- evaluate.py
`-- requirements.txt
```

## Notebook Workflow

Run notebooks in this order:

1. `01_eda.ipynb`
- Loads `COCOMO-81.csv`, `Desharnais.csv`, and `china.arff`
- Prints `shape`, `head()`, `info()`, `describe()`
- Reports missing values and categorical columns
- Identifies effort target column
- Plots effort histograms

2. `02_preprocessing.ipynb`
- Drops duplicates
- Handles missing values
- Encodes categorical columns
- Scales numeric features
- Saves cleaned datasets to `data/processed/`

3. `03_baselines.ipynb`
- Trains Linear Regression, Random Forest, and XGBoost (if installed)
- Evaluates MAE and RMSE
- Saves metrics to `results/metrics/baseline_metrics.csv`

4. `04_cnn.ipynb`
- Builds and trains a simple 1D CNN for effort prediction
- Evaluates MAE and RMSE
- Saves metrics to `results/metrics/cnn_metrics.csv`

5. `05_pso.ipynb`
- Uses PySwarms to tune CNN hyperparameters
- Trains CNN with tuned parameters
- Compares CNN vs CNN+PSO
- Saves metrics to `results/metrics/cnn_vs_pso_metrics.csv`

## Setup

### 1. Create and activate virtual environment

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Launch Jupyter

```powershell
jupyter notebook
```

Open the `notebooks/` directory and run notebooks from 01 to 05.

## Requirements

Core packages used in this project:
- TensorFlow
- scikit-learn
- PySwarms
- XGBoost
- pandas, numpy, scipy
- matplotlib, seaborn
- jupyter

See `requirements.txt` for versions.

## Source Modules

- `src/data_loader.py`: Load CSV and ARFF datasets
- `src/preprocess.py`: Cleaning, encoding, scaling, and processed-data saving
- `src/cnn_model.py`: 1D CNN model build and training utilities
- `src/pso_optimizer.py`: PSO tuning helpers for CNN hyperparameters
- `src/evaluate.py`: MAE/RMSE evaluation and metrics persistence

## Outputs

- Processed datasets: `data/processed/`
- Trained model artifacts (if saved): `models/`
- Metrics CSVs: `results/metrics/`

## Notes

- If XGBoost is unavailable, baseline notebook will still run with remaining models.
- If `china.arff` fails to load, verify `scipy` is installed in the active environment.

---

## Web Application

A production-ready estimator is available in `backend/` and `frontend/`.

### Quick start

```powershell
# Terminal 1 – backend
cd backend
..\venv\Scripts\Activate.ps1
python main.py

# Terminal 2 – frontend
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000` for the estimation app and `http://localhost:3000/admin` for the admin dashboard.

See [PROJECT_SETUP.md](PROJECT_SETUP.md) for full configuration instructions.

### Two-step adaptive flow

1. **Stage 1** — Fill in a universal project brief (screens, entities, duration, team, complexity, reliability).
2. **Stage 2** — Answer a short set of follow-up questions selected by the backend based on your project profile.
3. **Result** — Receive effort estimate (person-months), INR base cost, and your chosen display currency breakdown.

No dataset names are exposed. Routing and model selection are fully internal.

### Admin controls

Navigate to `/admin` and enter your `ADMIN_API_KEY` to manage at runtime:

- Switch between **ML model mode** and **AI provider mode** without redeploying.
- Change AI provider (OpenAI / Gemini / Groq) and prompt profile.
- Update the monthly blended rate used for cost derivation.
- View system diagnostics (model service loaded, active mode).

### Running backend tests

```powershell
cd backend
..\venv\Scripts\Activate.ps1
python -m pytest tests/ -v
```

### Running frontend smoke test

Keep the backend running, then execute:

```powershell
cd frontend
npm run smoke:two-step
```

This script exercises the public two-step flow (`/predict/intake` then `/predict/final`) and prints the resulting effort, cost, and mode.