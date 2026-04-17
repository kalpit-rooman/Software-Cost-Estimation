---
name: streamlit-app
description: "Build the Streamlit web application for software cost estimation. Use when: creating app pages, prediction interface, model comparison dashboard, loading saved models, Plotly visualizations, app styling, or Streamlit deployment configuration."
---

# Streamlit Web Application

## When to Use

- Creating or modifying files in `app/`
- Building prediction interface
- Creating model comparison dashboard
- Styling the application

## App Structure

```
app/
├── app.py                 # Main entry — st.set_page_config, sidebar nav
├── predict.py             # Model loading from models/, prediction functions
├── pages/
│   ├── 1_Home.py          # Project overview, dataset cards
│   ├── 2_Predict.py       # Effort prediction form
│   ├── 3_Dashboard.py     # Model comparison charts
│   └── 4_About.py         # Methodology explanation
└── assets/
    └── style.css          # Custom dark/obsidian theme
```

## Prediction Logic (`predict.py`)

- Load models from `models/` directory (`.h5` for CNN, `.pkl` for sklearn)
- Load scaler from `models/scaler.pkl` for input preprocessing
- NEVER retrain models at runtime — always load saved weights
- For CNN: reshape input with `reshape_for_cnn()` before prediction
- If log-transform was used: apply `np.expm1()` to CNN predictions

## Page: Predict Effort

- Dropdown: select dataset type (COCOMO/Desharnais/China)
- Dynamic form: show input fields matching selected dataset's features
- Model selector: checkboxes for each model (default: all selected)
- "Predict" button → display results in columns/cards
- Show side-by-side comparison table of all selected models' predictions

## Page: Dashboard

- Use Plotly for interactive charts (not matplotlib)
- Load metrics from `results/metrics/` CSVs
- Load figures from `results/figures/` for static plots
- Dropdowns to filter by dataset, metric type
- Highlight best model per dataset+metric combination

## Styling

- Dark/obsidian theme matching user's brand preference
- Custom CSS via `st.markdown(unsafe_allow_html=True)`
- Use st.columns for layout, st.metric for KPI cards
- Color scheme: dark backgrounds (#1a1a2e, #16213e), red accents (#e94560)

## Launch Command

```bash
streamlit run app/app.py
```

## Key Constraints

- Add `streamlit` and `plotly` to `requirements.txt`
- All model paths relative to project root using pathlib
- Handle missing model files gracefully (show "Model not trained yet" message)
