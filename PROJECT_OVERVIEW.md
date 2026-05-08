# Software Cost Estimation System — Project Overview

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Folder Structure](#3-folder-structure)
4. [Machine Learning Pipeline](#4-machine-learning-pipeline)
5. [Backend System](#5-backend-system)
6. [Frontend System](#6-frontend-system)
7. [End-to-End Workflow](#7-end-to-end-workflow)
8. [Key Features](#8-key-features)
9. [Technologies Used](#9-technologies-used)
10. [Strengths](#10-strengths)
11. [Limitations](#11-limitations)
12. [Suggested Improvements](#12-suggested-improvements)

---

## 1. Project Overview

### Problem Statement

Accurately estimating the cost and effort required to develop a software system is one of the most persistent and consequential challenges in software engineering. Underestimates lead to budget overruns, missed deadlines, and project failures. Overestimates result in lost contracts and missed business opportunities. Traditional estimation approaches — such as expert judgement and rule-based algorithmic models like COCOMO — suffer from subjectivity, limited adaptability, and poor calibration when applied to diverse modern software projects.

### Objective

This project addresses the software cost estimation problem by constructing a full-stack, machine-learning-driven estimation platform. The primary research objective is to investigate whether a Convolutional Neural Network (CNN) optimised with Particle Swarm Optimization (PSO) can produce effort predictions that are competitive with or superior to established baseline methods across multiple industry-standard datasets. A secondary objective is to wrap these models in a production-grade web application that any project manager or technical lead can use without machine learning expertise.

### High-Level Functionality

The system accepts a natural-language project brief from the user — including indicators such as the number of screens, data entities, team size, team experience, project complexity, and reliability requirements — and returns a calibrated effort estimate (in person-months), a full cost breakdown in any target currency, an SDLC phase distribution, a risk register, and an AI-powered chatbot that can explain the results in context. The estimation is driven by an ensemble of trained machine learning models, with an optional AI-provider fallback path for projects where model-based estimation may be insufficient.

---

## 2. System Architecture

The system is composed of three tightly-integrated layers: a **Next.js frontend**, a **FastAPI backend**, and a **Python ML pipeline**. These layers are independent subsystems that communicate through a well-defined HTTP API contract, making it possible to develop, test, and deploy each layer separately.

### Component Interaction

```
User Browser (Next.js)
        │
        │  HTTP  POST /predict/intake
        ▼
FastAPI Backend (Python)
        │
        │  Dataset routing → Feature mapping
        ▼
Prediction Service (src/predictor.py)
        │
        │  Dataset-specific models loaded from models/
        ▼
Ensemble ML Engine
  ┌─────┬──────────┬─────────────────┐
  │  LR │    RF    │    XGBoost      │
  └─────┴──────────┴─────────────────┘
        │ Weighted average
        ▼
  Effort (person-months)
        │
        │  Cost conversion, phase distribution, risk scoring
        ▼
  JSON Response → Frontend → Rendered Results Page
```

### Architecture Description

The **frontend** is a statically typed TypeScript application built with Next.js 15 and React 19. It presents a multi-step estimation wizard and a results dashboard. All user inputs are validated client-side before being sent to the backend.

The **backend** is a Python FastAPI application that exposes a RESTful API. On startup, it pre-loads saved machine learning model artefacts from the `models/` directory into memory. Incoming requests are parsed and validated by Pydantic schemas, routed through a dataset selection engine, mapped to feature vectors, run through the ensemble prediction service, and finally enriched with cost conversion, phase distribution, risk assessment, and explainability metadata before the response is returned.

The **ML pipeline** is a collection of Python modules under `src/` that handle data loading, preprocessing, model training, PSO-based hyperparameter optimisation, ensemble logic, and evaluation. These modules are consumed both by the Jupyter notebooks (for research and experimentation) and by the deployed backend service at inference time.

---

## 3. Folder Structure

### `backend/`

The backend is a self-contained FastAPI application. It is organized into four sub-packages following standard separation-of-concerns conventions:

- **`core/`** — Application configuration loaded from environment variables. Defines runtime mode (`ai` vs `model`), API keys for AI providers, default monthly rate in INR, Redis cache settings, and supported dataset names. The `config.py` module serves as the single source of truth for all environment-driven settings.
- **`routes/`** — FastAPI router modules. `predict.py` contains the primary estimation endpoints. `chat.py` handles AI chatbot requests. `health.py` provides a liveness probe. `meta.py` exposes read-only metadata such as supported datasets. `admin.py` exposes bearer-token-protected endpoints for runtime configuration changes.
- **`schemas/`** — Pydantic data models for all request and response shapes. `request_response.py` defines the full public API contract including `UniversalProjectBrief`, `FinalPredictionResponse`, `PhaseBreakdown`, `RiskFactor`, `ExplainabilityStep`, `ModelPredictions`, and all related enumerations.
- **`services/`** — The business logic layer. Each service module has a single responsibility: `router.py` selects the internal dataset route, `mapper.py` translates universal project inputs into dataset-specific feature vectors, `model_orchestrator.py` invokes the ML ensemble, `ai_orchestrator.py` calls the AI provider fallback, `cost_converter.py` converts effort to INR cost, `currency_converter.py` applies live exchange rates, `phase_distributor.py` breaks total effort into SDLC phases, `risk_assessor.py` generates a project risk register, `explainability.py` produces a waterfall decomposition, `chatbot.py` powers the context-aware Q&A assistant, and `guardrails.py` validates AI-generated responses before they reach the client.

**Key files:** `main.py` (application entry point and lifespan management), `services/mapper.py` (feature translation logic), `services/router.py` (intelligent dataset routing).

### `frontend/`

The frontend is a Next.js 15 application written in TypeScript with Tailwind CSS for styling. Its structure follows the Next.js App Router convention:

- **`app/`** — Page routes. `page.tsx` is the landing page. `estimate/page.tsx` hosts the estimation wizard. `estimate/results/` renders the full results dashboard. `admin/` provides a protected admin configuration interface. `contact/` contains a contact form. `features/` describes platform capabilities.
- **`components/`** — Reusable React components. `EstimationFlow.tsx` coordinates the multi-step wizard state. `ResultsPage.tsx` renders the complete estimation output including effort, cost breakdowns, phase distribution, risk register, explainability waterfall, and the AI chatbot panel. `ChatPanel.tsx` manages the conversational interface.
- **`components/estimation/`** — Step-specific wizard components: `Step1ProjectType.tsx` (project category selection), `Step2CoreInputs.tsx` (slider-based core metrics), `Step3AdvancedInputs.tsx` (detailed configuration), `TeamComposition.tsx` (per-role cost configuration).
- **`lib/`** — Client-side utilities. `api.ts` defines all API types and fetch functions. `adminAuth.ts` handles admin authentication state.

**Key files:** `components/EstimationFlow.tsx` (wizard orchestration), `components/ResultsPage.tsx` (output rendering), `lib/api.ts` (API contract).

### `src/`

The `src/` directory contains all reusable Python modules for the ML pipeline. Each module has a single, well-defined responsibility:

- **`data_loader.py`** — Loads raw datasets from `data/raw/`. Supports CSV and ARFF formats. Provides `load_all_raw_datasets()` as the canonical entry point.
- **`preprocess.py`** — Data cleaning, missing value imputation, categorical encoding, feature-target splitting, and feature scaling. Provides both a scikit-learn `ColumnTransformer`-based pipeline and standalone helper functions.
- **`feature_engineering.py`** — Log-transform utilities for the effort target, low-variance feature filtering, and correlation-based feature selection.
- **`baseline_models.py`** — Factory functions for Linear Regression, Random Forest, and XGBoost regressors with standardised hyperparameters and fixed random seeds.
- **`cnn_model.py`** — 1D CNN architecture builder with configurable depth, filters, kernel size, dropout, and learning rate. Includes `GlobalAveragePooling1D` for variable-length feature sequences and `EarlyStopping` / `ReduceLROnPlateau` callbacks.
- **`mlp_model.py`** — Multi-layer Perceptron builder for tabular data as an alternative deep-learning baseline. Uses BatchNormalization and Dropout for regularisation.
- **`pso_optimizer.py`** — PSO-based hyperparameter tuner for the CNN. Defines the 6-dimensional search space (filters, kernel size, learning rate in log space, dropout, number of convolutional layers, batch size), objective function, and hyperparameter decoder.
- **`pso_mlp.py`** — PSO-based hyperparameter tuner for the MLP, following the same design pattern as `pso_optimizer.py`.
- **`ensemble.py`** — Weighted and simple-average ensemble strategies over baseline model predictions. Provides `weighted_average_predictions()` and `simple_average_predictions()`.
- **`evaluate.py`** — Unified metric computation returning MAE, RMSE, R², MAPE, MdMRE, and Pred(25). Provides `save_metrics()` for persisting results.
- **`cv_pipeline.py`** — Complete 5-fold cross-validation pipeline that trains and evaluates all model variants (Linear Regression, Random Forest, XGBoost, CNN baseline, CNN+PSO, MLP baseline, MLP+PSO, and their ensembles) in a reproducible sequence.
- **`predictor.py`** — Runtime prediction service used by the backend. Lazy-loads saved model artefacts on first request, caches them in memory, and exposes `predict()` for feature-to-effort inference.
- **`config.py`** — Path constants and dataset-specific model directories. Also holds the hardcoded RMSE scores used to derive inverse-RMSE ensemble weights.

**Key files:** `predictor.py` (serving layer), `cv_pipeline.py` (training orchestration), `pso_optimizer.py` (optimisation engine).

### `models/`

Contains all saved model artefacts organised in per-dataset subdirectories (`china/`, `cocomo81/`, `desharnais/`). Each subdirectory holds three `.pkl` pipeline files: `lr_model.pkl` (Linear Regression), `rf_model.pkl` (Random Forest), `xgb_model.pkl` (XGBoost). The root `models/` directory also holds `.h5` files for saved CNN and MLP variants, `best_hyperparams.json` (optimal PSO-tuned hyperparameters per dataset), and `training_histories.json` (loss curves from neural network training).

**Key files:** `models/best_hyperparams.json`, per-dataset `.pkl` files.

### `data/`

Maintains a strict separation between raw and processed data:

- **`data/raw/`** — The original, unmodified datasets. `COCOMO-81.csv` (63 projects from Barry Boehm's 1981 constructive cost model study), `Desharnais.csv` (77 business application projects from a Canadian software house), `china.arff` (499 enterprise software projects from a Chinese productivity study in ARFF format). These files are never modified.
- **`data/processed/`** — Cleaned CSV exports produced by the preprocessing notebook. These serve as the canonical input for model training steps.

### `scripts/`

Standalone utility scripts that are executed from the command line rather than from notebooks:

- **`save_baselines.py`** — Trains the three baseline models (Linear Regression, Random Forest, XGBoost) for all configured datasets and saves them as `.pkl` pipelines to `models/<dataset>/`. Accepts `--dataset`, `--reuse-existing`, and `--test-size` CLI arguments.

### `results/`

Output directory for all evaluation artefacts:

- **`results/metrics/`** — CSV files containing metric tables produced by evaluation runs (e.g., `baseline_metrics.csv`, `cnn_metrics.csv`, `cnn_vs_pso_metrics.csv`). These are the primary evidence for quantitative comparison between model variants.
- **`results/figures/`** — Saved plots from notebook visualisations.

### `notebooks/`

Sequential Jupyter notebooks that document the full research workflow:

- **`01_eda.ipynb`** — Exploratory data analysis across all three datasets. Produces shape summaries, descriptive statistics, missing value counts, and effort distribution histograms.
- **`02_preprocessing.ipynb`** — Data cleaning pipeline execution. Outputs the processed CSVs to `data/processed/`.
- **`03_baselines.ipynb`** — Trains and evaluates all three baseline models. Saves metrics.
- **`04_cnn.ipynb`** — Builds, trains, and evaluates the baseline CNN. Compares against baselines.
- **`05_pso.ipynb`** — Runs PSO hyperparameter search on the CNN. Compares baseline CNN with CNN+PSO-tuned variant.

---

## 4. Machine Learning Pipeline

### Datasets

The system is trained and evaluated on three established benchmark datasets from the software effort estimation literature:

**COCOMO-81** is a dataset of 63 projects assembled by Barry Boehm in 1981 to validate his Constructive Cost Model. Each project is described by the source lines of code (KLOC) and a set of cost-driver multipliers including software reliability requirements (RELY), product complexity (CPLX), analyst capability (ACAP), applications experience (AEXP), use of modern programming tools (TOOL), and schedule constraints (SCED). Effort is recorded directly in person-months.

**Desharnais** is a collection of 77 business application projects developed by a Canadian software company between 1983 and 1988. Projects are characterised using function point metrics such as unadjusted function points, adjustment factor, and team and manager experience. Effort is recorded in person-hours and must be converted to person-months for comparison.

**China** is a large dataset of 499 projects from a Chinese productivity study. It uses Adjusted Function Points (AFP) as the primary size measure along with counts of inputs, outputs, enquiries, files, and interfaces. Effort is recorded in person-hours. The significantly larger sample size and richer feature set make it more suitable for deep learning approaches.

### Data Loading

The `src/data_loader.py` module provides a unified interface for all raw data access. CSV files are loaded with pandas; the ARFF file (China dataset) is parsed using scipy's ARFF reader, which handles byte-encoded attribute names produced by Weka-compatible export tools. All datasets are returned under stable string keys (`"cocomo81"`, `"desharnais"`, `"china"`) to ensure consistent downstream handling.

### Preprocessing

The preprocessing pipeline in `src/preprocess.py` applies the following transformations in a reproducible sequence:

1. **Duplicate removal** — Exact duplicate rows are dropped to prevent data leakage between training and test splits.
2. **Missing value imputation** — Numeric columns are imputed with the column median; categorical columns are imputed with the column mode.
3. **Categorical encoding** — Non-numeric columns are transformed with ordinal encoding using scikit-learn's `OrdinalEncoder`. Unseen categories at inference time are handled gracefully with a sentinel value rather than raising an error.
4. **Target identification** — The effort column is identified by matching common naming conventions (e.g., "effort", "actual_effort", "personhours") to support all three datasets without hard-coded column names.
5. **Feature scaling** — For Linear Regression, all numeric features are standardised with `StandardScaler`. Tree-based models (Random Forest, XGBoost) receive unscaled features, as they are invariant to monotonic transformations. CNN and MLP models also receive scaled inputs, which is required for gradient-based optimisation to converge reliably.
6. **Log transformation of the target** — Effort values span multiple orders of magnitude across all three datasets. A `log1p` transformation is applied to the target variable before training neural models. The inverse transformation (`expm1`) is applied to predictions before computing evaluation metrics.

The preprocessing is implemented as a scikit-learn `Pipeline` combining `ColumnTransformer` steps, ensuring that all transformation parameters are fit on training data only and applied consistently at inference time.

### Feature Handling

Feature engineering is handled in `src/feature_engineering.py`. Two optional selection strategies are available: a **variance threshold filter** that removes features with near-zero variance across the training set, and a **correlation-based filter** that retains only features whose absolute Pearson correlation with the effort target exceeds a configurable threshold. In the deployed system, features are passed through without aggressive selection to preserve all available predictive signal, particularly on small datasets where feature selection could introduce bias.

### Model Training

All models are trained using a reproducible random state of 42. A 80/20 train-test split is applied for holdout evaluation, and a 5-fold cross-validation pipeline in `src/cv_pipeline.py` provides the primary performance estimates reported in the final comparison.

#### Linear Regression

A standard Ordinary Least Squares regression with no regularisation. It serves as the simplest possible baseline and is included to characterise the lower bound of predictive performance. Feature scaling is applied for Linear Regression because unnormalised features can cause numerical instability in matrix inversion. Despite its simplicity, Linear Regression often performs competitively on the COCOMO-81 dataset because the effort formula has a near-linear relationship with KLOC when log-transformed.

#### Random Forest

An ensemble of 300 decision trees trained with the `RandomForestRegressor` from scikit-learn with bootstrap sampling and random feature subsets at each split. Random Forest is inherently robust to outliers and non-linear relationships, requires no feature scaling, and handles missing values gracefully through median imputation in the preprocessing pipeline. It is well-suited to the tabular structure of the effort estimation datasets and consistently produces competitive results on both small datasets (COCOMO-81, Desharnais) and the larger China dataset.

#### XGBoost

A gradient-boosted tree ensemble using the `XGBRegressor` with 300 estimators, a learning rate of 0.05, maximum tree depth of 6, and row and column subsampling for regularisation. XGBoost's sequential tree construction is particularly effective at capturing residual patterns missed by earlier trees, making it the highest-performing baseline model on the China dataset (RMSE: 1467). Its regularisation parameters prevent overfitting on small datasets.

#### CNN (Convolutional Neural Network)

The 1D CNN in `src/cnn_model.py` treats each sample's feature vector as a single-channel temporal sequence of length equal to the number of input features. One to three `Conv1D` blocks extract local feature interaction patterns, followed by `GlobalAveragePooling1D` to aggregate the learned representations into a fixed-size vector, a Dense hidden layer with ReLU activation, and a linear output neuron. `BatchNormalization` is applied after each convolutional block to stabilise training and reduce the need for careful learning rate tuning. `Dropout` is applied after the dense layer to regularise the model and reduce overfitting on small datasets.

CNNs are traditionally designed for image or sequence data but can be applied to tabular data by treating features as a pseudo-sequence. The rationale is that the model can learn local interaction patterns between adjacent features — for example, between experience and complexity cost drivers in COCOMO-81 — without requiring the user to manually specify interaction terms. The `EarlyStopping` callback (patience of 15 epochs on validation loss) and `ReduceLROnPlateau` callback (halving the learning rate when validation loss stagnates) are used to avoid premature stopping and to adapt the learning dynamics during training.

#### MLP (Multi-Layer Perceptron)

The MLP in `src/mlp_model.py` is a fully-connected feedforward network that processes the raw feature vector directly without the pseudo-sequence reshaping required by the CNN. It uses the same training callbacks and regularisation strategy (BatchNormalization, Dropout) but differs in that it has no receptive field constraint — every neuron in each layer is connected to every neuron in the previous layer. The MLP serves as an additional deep-learning baseline to isolate the effect of the convolutional inductive bias on performance.

### Ensemble Strategy

The ensemble logic in `src/ensemble.py` and `src/predictor.py` combines the three baseline models (Linear Regression, Random Forest, XGBoost) at inference time. Two strategies are supported:

**Simple average** — All models contribute equally to the final prediction. This is robust when model quality is similar and serves as the default for the deployed application.

**Weighted average (inverse-RMSE weighting)** — Models are assigned weights proportional to the inverse of their RMSE scores computed on the holdout test set. This means models with lower error rates on a given dataset automatically receive higher influence in the ensemble for that dataset. The weights are pre-computed from the RMSE scores stored in `src/config.py` and normalised to sum to one. For the China dataset, XGBoost (RMSE: 1467) receives a higher weight than Random Forest (RMSE: 1636), which in turn outweighs Linear Regression (RMSE: 53165) by a large margin due to Linear Regression's substantially higher error.

The ensemble architecture is dataset-specific: separate model files and separate weight vectors are maintained for each of the three datasets, ensuring that predictions are always drawn from models trained and calibrated on the same data distribution.

### Particle Swarm Optimization (PSO)

PSO is a population-based metaheuristic search algorithm that mimics the social behaviour of a swarm of particles. Each particle in the swarm represents a candidate hyperparameter configuration. Particles iteratively update their positions based on their own best-known position and the global best position discovered by any particle in the swarm. This balance between personal and social exploration allows PSO to efficiently navigate high-dimensional search spaces without gradient information.

In this project, PSO is used to tune the CNN's hyperparameters over a 6-dimensional continuous search space:

| Dimension | Range | Description |
|---|---|---|
| Filters | 8 – 32 | Number of Conv1D filters per layer |
| Kernel size | 2 – 5 | Receptive field of each filter |
| Learning rate | 10⁻³·³ – 10⁻² | Adam learning rate (searched in log space) |
| Dropout rate | 0.1 – 0.4 | Fraction of units dropped for regularisation |
| Num conv layers | 1 – 3 | Depth of the convolutional stack |
| Batch size | {8, 16, 32} | Mini-batch size during gradient descent |

The PSO objective function builds and trains a CNN with the decoded hyperparameters on the training split, evaluates it on the validation split, and returns the RMSE as the cost to minimise. The search uses 6 particles over 6 iterations — a deliberately compact configuration chosen to balance exploration quality against the computational cost of training many neural networks on small datasets.

Learning rate is searched in log10 space (i.e., the PSO searches over the exponent value) because the effective range spans multiple orders of magnitude. This prevents the search from being dominated by linear-scale differences at the boundary.

---

## 5. Backend System

### API Overview

The backend exposes a RESTful API over HTTP using FastAPI. The primary estimation flow uses two sequential endpoints:

| Endpoint | Method | Description |
|---|---|---|
| `/predict/intake` | POST | Accepts a universal project brief and returns follow-up questions |
| `/predict/final` | POST | Accepts follow-up answers and returns the full effort and cost estimate |
| `/predict` | POST | Legacy single-step estimation endpoint (backward compatibility) |
| `/chat` | POST | Context-aware chatbot using Groq's Llama 3.3 70B model |
| `/health` | GET | Liveness and readiness probe |
| `/meta/datasets` | GET | Returns list of supported internal dataset identifiers |
| `/admin/*` | POST/GET | Bearer-token-protected runtime configuration |

### Request Flow

When a request arrives at `POST /predict/intake`:

1. The Pydantic schema `UniversalProjectBrief` validates and normalises all input fields. Enum fields (complexity, reliability) are validated against allowed values; numeric fields are range-checked.
2. The `UniversalRouter` scores the project brief against three internal route profiles (China, COCOMO-81, Desharnais) using weighted feature signals derived from the number of screens, entities, team size, duration, complexity, and reliability. The route with the highest aggregate score is selected, and a routing confidence value is computed based on the margin between the top two scores.
3. A follow-up question pack appropriate to the selected route is returned to the client. Each pack contains fields specifically chosen to elicit the additional project characteristics needed to maximise feature coverage for that dataset's model (e.g., estimated KLOC for COCOMO-81, transaction volume for China, business process count for Desharnais).
4. The intake context (routing metadata and normalised brief) is stored in an in-memory cache keyed by a UUID `intake_id`, with configurable TTL and maximum capacity.

When the client submits `POST /predict/final` with the `intake_id` and follow-up answers:

1. The intake context is retrieved from the cache.
2. The `UniversalMapper` translates the universal project brief and follow-up answers into the dataset-specific feature vector required by the target model. Each route has a dedicated mapping function that derives model features from project characteristics using domain knowledge about each dataset's feature semantics. For example, for the COCOMO-81 route, team experience is translated into an analyst capability (ACAP) cost-driver value using an inverse-linear function; for the China route, the number of screens and entities are used to estimate Adjusted Function Points.
3. The `ModelOrchestrator` (or `AIOrchestrator` in AI mode) runs the ensemble prediction and returns an effort estimate in person-months.
4. Unit conversion is applied: China and Desharnais models return effort in person-hours and are divided by 160 hours/month to obtain person-months. COCOMO-81 returns person-months directly.
5. The effort is converted to INR using the configured blended monthly rate. If the client specified a target currency other than INR, a live exchange rate is fetched (or a cached rate is used) from an external exchange rate API.
6. Phase distribution, risk assessment, explainability waterfall, and team cost breakdown are computed and appended to the response.

### Prediction Pipeline (Detailed)

The `PredictionService` in `src/predictor.py` implements a lazy-loading, per-dataset model cache. On the first prediction request for a given dataset, it loads the three `.pkl` pipeline files from `models/<dataset>/`, validates that all files exist, extracts the feature schema from the saved pipeline's `feature_names_in_` attribute, and caches the bundle. Subsequent requests for the same dataset serve from the in-memory cache without I/O overhead.

At inference time, the input feature dictionary is converted to a pandas DataFrame with the exact column ordering expected by each pipeline. Each model pipeline consists of a scikit-learn `ColumnTransformer` preprocessor (identical to the one used during training) followed by the estimator. This end-to-end pipeline design ensures that all preprocessing transformations are automatically applied at prediction time, preventing preprocessing mismatches.

### Input Transformation Summary

User-facing inputs are deliberately abstracted from dataset-specific feature names. The mapping layer (`backend/services/mapper.py`) bridges this gap:

- **COCOMO-81 mapping** converts project size, complexity, and reliability indicators into KLOC, RELY, CPLX, ACAP, AEXP, TOOL, and SCED values.
- **China mapping** converts screen and entity counts into AFP, Added, Changed, Deleted, Input, Output, Enquiry, File, and Interface function point components.
- **Desharnais mapping** converts project scope, team experience, and process information into function point counts, adjustment factors, team experience scores, and manager experience scores.

---

## 6. Frontend System

### UI Structure

The frontend presents three primary views:

1. **Landing Page** — Introduces the platform, explains the methodology, and directs users to start the estimation flow.
2. **Estimation Wizard** (`/estimate`) — A three-step guided form that collects project information progressively.
3. **Results Dashboard** (`/estimate/results`) — A comprehensive output view displayed after the backend returns a successful prediction.

An **Admin Panel** (`/admin`) is accessible via a bearer token and provides runtime controls for configuration parameters such as the default monthly rate.

### Multi-Step Estimation Wizard

The estimation flow is orchestrated by `EstimationFlow.tsx`, which maintains the complete wizard state (selected project type, core inputs, advanced inputs) and controls step transitions. The wizard is composed of three steps:

**Step 1 — Project Type Selection**: The user selects one of three project categories — *Large Code System* (mapped internally to COCOMO-81), *Business Application* (Desharnais), or *Medium Enterprise System* (China). This selection determines which internal dataset and follow-up question pack will be used. The mapping between project type and dataset is deliberately hidden from the user; the selection is described in business terms rather than technical dataset names.

**Step 2 — Core Inputs**: Three slider controls capture the essential sizing parameters: project size (a generalised scale from 20 to 300), team experience (1 to 10 years), and complexity (1 to 10 scale). These are intentionally high-level to minimise the burden on users who may not know precise function point counts or KLOC.

**Step 3 — Advanced Inputs**: A more detailed form covering reliability requirements, data intensity, team familiarity with the technology, time constraints, tooling maturity, technology stack, and either a flat monthly salary or a per-role team composition with individual rates. These inputs are mapped to dataset-specific features in the frontend before the API call is made (`buildFollowUpAnswers()` in `EstimationFlow.tsx`).

### Input Handling and Dataset Mapping

The frontend performs a client-side mapping step before submitting to the backend. The `buildFollowUpAnswers()` function translates slider values and select inputs into the named fields expected by each dataset's follow-up question pack. For example, for COCOMO-81, it computes an estimated KLOC from the project size slider scaled by data intensity and reliability multipliers. This pre-processing distributes computation between the client and server, reduces the volume of data exchanged, and keeps the API contract stable regardless of future UI changes.

### API Communication

All API calls are centralised in `frontend/lib/api.ts`, which exports typed functions for each backend endpoint. The module uses the native `fetch` API with typed request and response bodies defined as TypeScript interfaces. Error handling is normalised through a helper that extracts the error message from either `Error` objects or raw exception values.

### Result Display

The `ResultsPage.tsx` component renders a multi-panel dashboard that includes:

- **Effort summary** with humanised duration at multiple team sizes
- **Cost breakdown** showing base INR cost and converted display currency
- **Model predictions panel** showing individual model outputs (Linear Regression, Random Forest, XGBoost) alongside the ensemble prediction
- **Cost range** (optimistic, most-likely, pessimistic)
- **SDLC phase distribution** with effort and cost per phase
- **Risk register** listing project-specific risks with impact, probability, and mitigation strategies
- **Role-based cost breakdown** if team composition was specified
- **Explainability waterfall** showing how the base ML estimate was adjusted by tech stack multipliers
- **AI chatbot panel** for natural language Q&A about the estimate

---

## 7. End-to-End Workflow

The following describes the complete journey from user input to displayed results:

**Step 1 — Project Characterisation**
The user opens the web application and navigates to the estimation wizard. They select a project type that best describes their software (e.g., "Business Application"), then move through the three-step form to specify project size, team characteristics, complexity, reliability requirements, technology stack, and cost parameters.

**Step 2 — Intake Submission**
On form submission, the frontend constructs a `UniversalProjectBrief` JSON payload containing all core parameters and sends it to `POST /predict/intake`. The backend validates the payload, scores it against all three internal routes, selects the most appropriate dataset model, and stores the routing context in the intake cache. The response includes the `intake_id` and a pack of follow-up questions generated for the selected route.

**Step 3 — Follow-up Answer Processing**
The frontend pre-computes follow-up answers from the advanced inputs the user already provided (no second round-trip is needed in practice, as answers are derived from the advanced form fields) and immediately submits a `POST /predict/final` request with the `intake_id` and computed answers.

**Step 4 — Feature Mapping**
The backend retrieves the intake context, invokes the `UniversalMapper` to translate universal project parameters and follow-up answers into the feature vector expected by the selected dataset's models, and records mapping diagnostics including a confidence score and any fields that fell back to default values.

**Step 5 — Ensemble Prediction**
The `ModelOrchestrator` calls `predict_cost()` from `src/predictor.py`, which loads the three baseline model pipelines, runs inference in parallel, aggregates predictions using the configured ensemble strategy (weighted by inverse RMSE by default), and returns the ensemble effort estimate alongside individual model predictions.

**Step 6 — Unit Conversion and Cost Derivation**
The raw prediction (in person-hours for China and Desharnais, in person-months for COCOMO-81) is converted to a common person-month unit. The effort is multiplied by the blended monthly rate to produce a base cost in INR. If a non-INR target currency was requested, a live exchange rate is applied.

**Step 7 — Output Enrichment**
The effort and cost are enriched with an SDLC phase distribution, a risk register, an explainability waterfall, and per-role cost breakdowns. A tech stack adjustment multiplier is applied based on the user's technology choice.

**Step 8 — Response and Rendering**
The complete `FinalPredictionResponse` JSON is returned to the frontend. `ResultsPage.tsx` renders all panels, and the AI chatbot is initialised with the full estimation context so it can answer follow-up questions.

---

## 8. Key Features

### Multi-Dataset Estimation

The system uses three distinct industry-standard datasets, each representing a different class of software project. Rather than forcing all projects through a single model trained on mixed data, the routing layer selects the most appropriate dataset based on project characteristics. This specialisation improves calibration: COCOMO-81-trained models are better at estimating large, code-heavy systems; Desharnais models are calibrated for business applications measured in function points; China models provide the best coverage for medium-to-large enterprise systems with rich functional specifications.

### Ensemble Machine Learning

Instead of relying on a single model, the system combines the predictions of three complementary algorithms: Linear Regression (fast, interpretable, linear baseline), Random Forest (non-linear, ensemble of decision trees, robust to noise), and XGBoost (gradient boosted trees, high accuracy on tabular data). The ensemble reduces variance compared to any individual model and is more robust to dataset-specific quirks. Inverse-RMSE weighting ensures that better-calibrated models automatically contribute more to the final prediction.

### PSO-Based Hyperparameter Optimisation

The CNN's architecture and training configuration are determined by PSO rather than manual tuning or grid search. PSO explores the 6-dimensional hyperparameter space efficiently by maintaining a population of candidate configurations and leveraging inter-particle communication to focus the search on promising regions. This automated optimisation removes the need for expert knowledge to configure the neural network and produces hyperparameter settings that are specifically calibrated for each dataset's characteristics.

### AI Chatbot Integration

The platform integrates a conversational AI assistant powered by Groq's Llama 3.3 70B model. The chatbot is initialised with the user's full estimation session context — including effort, confidence, dataset, cost, assumptions, and warnings — plus a preloaded knowledge base covering COCOMO-81 methodology, function point analysis, and general software cost estimation concepts. Users can ask natural-language questions such as "Why is the confidence score only 82%?" or "How can I reduce the estimated cost?" and receive contextually accurate answers. Prompt injection protection is applied to all user-supplied text before it is included in the LLM prompt.

### Web-Based Interface with Currency and Role Support

The platform is fully accessible through a web browser with no installation required. It supports cost output in any currency through live exchange rate conversion. The team composition panel allows project managers to specify the exact role mix (e.g., senior developers, junior developers, QA engineers, project managers) with individual monthly rates, producing a per-role cost breakdown that is more actionable than a single blended figure.

---

## 9. Technologies Used

### Frontend

| Technology | Version | Role |
|---|---|---|
| Next.js | 15.3 | React framework with App Router and SSR |
| React | 19.0 | UI component library |
| TypeScript | 5.8 | Static typing for all frontend code |
| Tailwind CSS | 3.4 | Utility-first CSS framework |
| Phosphor Icons | 2.1 | Icon library |

### Backend

| Technology | Version | Role |
|---|---|---|
| Python | 3.10+ | Primary backend language |
| FastAPI | Latest | HTTP API framework |
| Pydantic | v2 | Schema validation and serialisation |
| Uvicorn | Latest | ASGI server |
| python-dotenv | Latest | Environment variable management |

### Machine Learning

| Technology | Version | Role |
|---|---|---|
| TensorFlow / Keras | 2.x | CNN and MLP model building and training |
| scikit-learn | Latest | Baseline models, preprocessing pipelines, cross-validation |
| XGBoost | Latest | Gradient-boosted tree ensemble |
| PySwarms | Latest | Particle Swarm Optimization implementation |
| NumPy | Latest | Numerical array operations |
| pandas | Latest | Tabular data handling |
| SciPy | Latest | ARFF file loading (China dataset) |
| joblib | Latest | Model serialisation (.pkl pipelines) |

### Data and Storage

| Technology | Role |
|---|---|
| CSV / ARFF files | Raw dataset storage |
| joblib `.pkl` | Saved scikit-learn pipeline artefacts |
| Keras `.h5` | Saved neural network weights |
| JSON | Hyperparameter configs and training histories |

### Development and Infrastructure

| Technology | Role |
|---|---|
| Jupyter Notebooks | Research workflow and reproducible experiments |
| pytest | Automated test suite (backend) |
| Node.js / npm | Frontend package management |
| Git | Version control |

---

## 10. Strengths

### Modular and Maintainable Architecture

The system is cleanly separated into independent layers (frontend, backend, ML pipeline) with well-defined interfaces between them. Within the backend, each service module has a single responsibility, making it straightforward to replace or extend individual components — for example, swapping the XGBoost model for LightGBM or replacing the Groq chatbot with a different LLM provider requires changes to only one module.

### Dataset Specialisation Through Intelligent Routing

Most effort estimation tools apply a single generic model to all project types. The routing layer in this system selects the model trained on the most appropriate dataset based on project characteristics, producing predictions that are better calibrated to the specific class of project being estimated.

### Ensemble Approach Reduces Prediction Variance

By combining three diverse models (linear, tree ensemble, and boosted trees), the system benefits from model diversity. When individual models make different errors on a given input, the ensemble averages out those errors. The inverse-RMSE weighting scheme ensures that the contribution of each model is proportional to its empirical performance on each dataset.

### Automated Hyperparameter Optimisation

The PSO-based tuning loop removes the need for manual CNN configuration, which is particularly valuable for small datasets where the optimal architecture may be quite different from standard defaults. The log-space learning rate search is a well-motivated design choice that allows fine-grained exploration at small learning rates where convergence quality is most sensitive.

### Production-Quality Security Practices

The backend implements prompt injection protection for all user-supplied text before it reaches the LLM, input validation at all API boundaries via Pydantic, bearer-token authentication for administrative endpoints, guardrail validation on AI-generated effort estimates to prevent out-of-range values from reaching clients, and strict CORS configuration. These practices reflect production deployment standards rather than a research prototype.

### Reproducible Research Workflow

All models are trained with a fixed random seed (42). Notebook-based documentation provides a step-by-step audit trail from raw data to final metrics. The separation between `data/raw/` (immutable) and `data/processed/` (derived) ensures that the original datasets are never accidentally modified.

---

## 11. Limitations

### CNN Performance on Small Tabular Datasets

CNNs were originally designed for image and sequence data with rich spatial or temporal structure. When applied to tabular data with small sample sizes (COCOMO-81 has 63 samples, Desharnais has 77), the convolutional inductive bias does not align well with the actual data structure, and the model is prone to overfitting despite regularisation. The baseline models (especially XGBoost and Linear Regression) often match or exceed CNN performance on these small datasets. The CNN demonstrates more competitive performance on the larger China dataset (499 samples) where there is sufficient data to learn meaningful convolutional patterns.

### Dataset Size Constraints

All three datasets are small by modern machine learning standards. The largest (China) has 499 samples, which is marginal for training deep learning models. This limits the expressiveness of the architectures that can be trained without overfitting and makes it difficult to draw statistically significant conclusions from cross-validation experiments due to high fold-to-fold variance.

### Indirect Feature Mapping

The universal mapper translates high-level user inputs (number of screens, entities, complexity score) into dataset-specific features using hand-crafted heuristics. For example, AFP is estimated from screen and entity counts using fixed scaling factors. These approximations introduce systematic bias and cannot substitute for domain expert knowledge of the actual KLOC or function point count of the target project.

### Offline Exchange Rate Fallback

The currency conversion service relies on an external exchange rate API. In production environments without a configured API key, the system falls back to a static exchange rate, which may be significantly out of date for volatile currency pairs.

### No Persistent Session Storage

The intake cache uses an in-memory dictionary with TTL-based expiry. In a multi-instance deployment, requests to `/predict/intake` and `/predict/final` would need to be routed to the same backend instance, or the cache would need to be externalised to Redis (the configuration infrastructure for which is present but optional).

### PSO Convergence Speed

The PSO search uses 6 particles over 6 iterations, which is sufficient for a demonstration but may not find the global optimum on all datasets. A more thorough search would use 20–50 particles over 50–100 iterations, but this would increase training time by an order of magnitude.

---

## 12. Suggested Improvements

### Adopt Tabular-Native Models

For the primary prediction task, gradient boosted tree ensembles (XGBoost, LightGBM, CatBoost) consistently outperform CNNs and MLPs on tabular datasets of this size. Future work should investigate whether replacing the CNN with a more powerful gradient boosting configuration or a Tabular Neural Network architecture (such as TabNet or FT-Transformer) produces measurable improvements in RMSE and Pred(25).

### SHAP-Based Explainability

The current explainability waterfall is heuristic and shows only tech stack adjustments applied on top of the ML estimate. Integrating SHAP (SHapley Additive exPlanations) values would allow the system to quantify exactly how much each input feature contributed to the prediction for a specific project, providing genuinely transparent and auditable estimates rather than post-hoc adjustments.

### Expanded Dataset Coverage

The three datasets date from 1981 to the 1990s and do not capture modern software development practices (agile methodologies, cloud-native architectures, continuous delivery). Augmenting the training data with more recent publicly available effort datasets — such as the ISBSG database or Promise Software Engineering Repository contributions — would improve the relevance and accuracy of predictions for contemporary projects.

### Real-Time Model Retraining

Currently, models are trained offline and loaded as static artefacts. An online learning capability that incorporates actual project outcomes (reported by users after project completion) into the training data would allow the system to continuously improve calibration over time, a property particularly valuable for organisation-specific deployments.

### Improved PSO Search Configuration

Expanding the PSO search to 20+ particles over 30+ iterations, using adaptive inertia weight decay, and applying multi-restart strategies would increase the likelihood of finding near-optimal hyperparameter configurations. Alternative metaheuristics such as Bayesian Optimisation (via Optuna or Hyperopt) may converge faster than PSO for low-dimensional hyperparameter spaces.

### Confidence Interval Reporting

The current confidence score is a scalar derived from mapping completeness rather than from the statistical spread of model predictions. A more rigorous approach would use conformal prediction or quantile regression forests to produce calibrated prediction intervals (e.g., "the effort will fall between 12 and 28 person-months with 90% confidence"), which would be substantially more informative for risk management purposes.

### Progressive Web Application

Converting the frontend to a Progressive Web Application (PWA) would enable offline caching of static assets and allow the estimation wizard to be used in low-connectivity environments — a practical consideration for project managers working on-site.

---

*Document generated: May 2026. Covers the full repository state as of that date.*
