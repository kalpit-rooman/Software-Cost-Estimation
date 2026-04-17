---
name: cnn-pso-training
description: "Train and optimize CNN models with PSO for software cost estimation. Use when: improving CNN architecture, adding layers (BatchNorm, Dropout), expanding PSO search space, tuning hyperparameters, adding training callbacks (EarlyStopping, ReduceLROnPlateau), feature engineering for effort prediction, or debugging model performance issues."
---

# CNN+PSO Training & Optimization

## When to Use

- Modifying CNN architecture in `src/cnn_model.py`
- Expanding PSO search space in `src/pso_optimizer.py`
- Creating feature engineering in `src/feature_engineering.py`
- Re-running training notebooks (04_cnn.ipynb, 05_pso.ipynb)
- Debugging poor model performance

## Current Architecture

- File: `src/cnn_model.py` → `build_cnn_regressor()`
- 1D CNN: Conv1D → Flatten → Dense → Dense(1)
- Hyperparams: filters(32), kernel_size(3), dense_units(64), lr(1e-3)

## Improvement Procedure

1. Add BatchNormalization after each Conv1D layer
2. Add Dropout(rate) after Dense layers — rate is PSO-tunable
3. Add second Conv1D layer with MaxPooling1D between them
4. Add EarlyStopping(patience=10, restore_best_weights=True) and ReduceLROnPlateau callbacks in `train_cnn_model()`
5. Increase max epochs to 100 (callbacks regulate actual training)

## PSO Expansion

- File: `src/pso_optimizer.py`
- Current: 4D search [filters, kernel_size, dense_units, learning_rate]
- Target: 6D search — add [dropout_rate (0.1-0.5), num_conv_layers (1-3)]
- Update `decode_cnn_hyperparameters()` for new dimensions
- Increase: n_particles=15, iters=25

## Feature Engineering

- File: `src/feature_engineering.py` (new)
- Log-transform effort target: `np.log1p(y)` — inverse with `np.expm1(pred)` at eval
- This is the single biggest accuracy boost for skewed effort data
- Optional: polynomial features for top correlated features

## Key Constraints

- Always use random_state=42
- Save best model to `models/` as .h5 after training
- Save best PSO hyperparams as JSON to `models/best_hyperparams.json`
- Reshape input with `reshape_for_cnn()` before any CNN training
