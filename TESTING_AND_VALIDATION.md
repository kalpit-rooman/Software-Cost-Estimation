# System Testing and Validation Process

## Executive Summary

This project employs a multi-layered testing and validation strategy covering:
- **Unit Testing**: Backend services, schema validation, conversion logic
- **Integration Testing**: End-to-end two-step prediction flow
- **Model Validation**: 5-fold cross-validation during training, RMSE-based ensemble selection
- **Input Validation**: Strict Pydantic schema enforcement with range checks and type safety
- **Output Verification**: Guardrails on prediction bounds, cost calculations, and confidence scores
- **Smoke Testing**: Automated end-to-end workflow verification

---

## 1. Types of Testing Performed

### 1.1 Unit Testing (Backend)

**Test Framework**: pytest + unittest

**Test Suite Location**: `backend/tests/`

**Test Coverage**:

| Test File | Focus Area | Test Count |
|-----------|-----------|-----------|
| `test_validation.py` | Pydantic schema validation | 11 tests |
| `test_mapper.py` | Feature mapping to dataset schemas | 3 tests |
| `test_router.py` | Route inference and scoring | 6 tests |
| `test_conversion.py` | Cost/currency conversions | 10 tests |
| `test_guardrails.py` | Output bounds validation | 12 tests |
| `test_admin.py` | State management & auth | 11 tests |

**Total Backend Unit Tests**: 53 test cases

### 1.1.1 Schema Validation Testing (`test_validation.py`)

**Purpose**: Ensure all API inputs conform to strict type and range requirements

**Test Cases**:
- Valid project brief parsing
- Invalid complexity level rejection (`"extreme"` → ValidationError)
- Invalid reliability level rejection (`"ultra"` → ValidationError)
- Negative team size rejection (ge=1)
- Zero duration rejection (gt=0)
- Extra fields rejection (ConfigDict strict mode)
- Missing required intake_id rejection

**Example**:
```python
def test_negative_team_size_rejected(self) -> None:
    data = {**_valid_brief(), "team_size": -1}
    with self.assertRaises(ValidationError):
        UniversalProjectBrief(**data)
```

### 1.1.2 Feature Mapping Tests (`test_mapper.py`)

**Purpose**: Verify correct translation of universal brief to dataset-specific features

**Test Cases** (per route):
- **China**: AFP-based features (AFP, Input, Output, Enquiry, File, Interface, Added, Changed, Deleted, Resource, Duration)
- **COCOMO-81**: Effort multipliers (loc, rely, cplx, acap, aexp, tool)
- **Desharnais**: Transaction-oriented (Length, TeamExp, ManagerExp, Transactions, Entities, Adjustment)

**Validation**:
- All expected keys present
- Diagnostics include routing confidence (0.0–1.0)
- Mapping rationale documented

**Example**:
```python
def test_china_mapping_contains_core_keys(self) -> None:
    for key in ["AFP", "Input", "Output", "Added", "Changed", "Duration"]:
        self.assertIn(key, mapped)
    self.assertGreaterEqual(diagnostics.mapping_confidence, 0.0)
```

### 1.1.3 Route Inference Tests (`test_router.py`)

**Purpose**: Validate dataset routing algorithm and confidence scoring

**Test Cases**:
- Returns valid InternalRoute (one of three datasets)
- Confidence score in range [0.0, 1.0]
- Route scores cover all three datasets
- Large transaction systems route to China
- Intake ID preservation
- Follow-up pack ID generation

**Example**:
```python
def test_large_transaction_system_routes_to_china(self) -> None:
    brief = _make_brief(num_screens=220, reliability=ReliabilityLevel.low)
    meta = self.router.infer_route(intake_id="test-6", brief=brief)
    self.assertEqual(meta.detected_route, InternalRoute.china)
```

### 1.1.4 Cost/Currency Conversion Tests (`test_conversion.py`)

**Purpose**: Verify effort-to-cost and currency conversion correctness

**Test Cases**:

| Category | Test | Expectation |
|----------|------|-----------|
| Effort-to-INR | `10 PM × 150k/month` | 1,500,000 INR |
| Fractional Effort | `1.5 PM × 100k/month` | 150,000 INR |
| INR-to-INR | Convert 1M INR | Identity (1.0 rate) |
| INR-to-USD | Convert 1M INR | Value < 1M (exchange rate > 1) |
| Edge Cases | Zero effort | ValueError |
| | Negative effort | ValueError |
| | Zero rate | ValueError |
| Supported Currencies | USD, GBP, EUR, etc. | All convert with rate > 0 |
| Invalid Currency | "XYZ" | ValueError |

**Example**:
```python
def test_inr_to_usd_produces_smaller_value(self) -> None:
    cost, rate = convert_from_inr(1_000_000, "USD")
    self.assertLess(cost, 1_000_000)
    self.assertGreater(rate, 0)
```

### 1.1.5 Output Guardrails Tests (`test_guardrails.py`)

**Purpose**: Validate all predictions stay within safe, reasonable bounds

**Guardrail Bounds**:

| Metric | Min | Max | Test Coverage |
|--------|-----|-----|--------|
| Effort Months | 0.5 | 600.0 | 6 tests |
| Confidence | 0.0 | 1.0 | 4 tests |
| Assumptions List | 0 | 20 items | Clamping test |
| Warnings List | 0 | 20 items | Clamping test |
| String Length | 0 | 500 chars | Truncation test |

**Test Cases**:
- Valid response passes
- Effort below 0.5 fails
- Effort above 600.0 fails
- Confidence < 0.0 fails
- Confidence > 1.0 fails
- Oversized lists clamped (>20 items → 20 items)
- Boundary values accepted (0.5, 600.0, 0.0, 1.0)

**Example**:
```python
def test_effort_above_maximum_fails(self) -> None:
    with self.assertRaises(GuardrailViolation):
        validate_effort_response(_valid_response(effort_months=700.0))

def test_oversized_assumptions_list_clamped(self) -> None:
    long_list = [f"assumption {i}" for i in range(30)]
    result = validate_effort_response(_valid_response(assumptions=long_list))
    self.assertLessEqual(len(result["assumptions"]), 20)
```

### 1.1.6 State Management and Admin Auth Tests (`test_admin.py`)

**Purpose**: Verify singleton state manager and admin authentication

**Test Cases** (State Manager):
- Initial state matches config
- Prediction mode update (model ↔ ai)
- Invalid prediction mode rejection ("quantum")
- Monthly rate update
- Zero/negative rate rejection
- AI profile update (conservative, balanced, optimistic)
- Invalid AI profile rejection ("reckless")
- Currency normalization (usd → USD)
- Partial updates preserve other fields

**Test Cases** (Admin Auth):
- Valid admin token passes
- Missing token rejected
- Invalid token rejected

**Example**:
```python
def test_invalid_prediction_mode_raises(self) -> None:
    self._sm.get_state()
    with self.assertRaises(ValueError):
        self._sm.update_state(prediction_mode="quantum")
```

### 1.2 Integration Testing

#### 1.2.1 Standalone Prediction Service Test (`test_predictor.py`)

**Purpose**: Full prediction lifecycle validation (loading → scoring → ensemble)

**Test Scenarios**:
1. **Service Initialization**: PredictionService singleton lazy-loads models on first call
2. **Dataset Model Loading**: Load LinearRegression + RandomForest + XGBoost for each dataset
3. **Input Preparation**: Build sample input from processed dataset
4. **Prediction Execution**: Run ensemble (simple/weighted averaging)
5. **Output Verification**: Check individual model predictions + ensemble result

**Example Flow**:
```python
load_prediction_service()  # Initializes singleton
sample_input = build_sample_input("cocomo81")
result = predict_cost(
    dataset_name="cocomo81",
    input_payload=sample_input,
    ensemble_method="simple"
)
# Output: {"rf_prediction": 120.5, "xgb_prediction": 115.3, ...}
```

#### 1.2.2 End-to-End Smoke Test (`frontend/tests/smoke_two_step_flow.mjs`)

**Purpose**: Validate complete frontend-backend integration for two-step prediction flow

**Test Scenarios** (3 different project profiles tested):

**Profile A** (High complexity):
- num_screens: 12, num_entities: 10, duration: 12 months
- complexity: high, reliability: high, team_size: 10
- experience: 7-8 years

**Profile B** (Medium complexity):
- num_screens: 8, num_entities: 9, duration: 8 months
- complexity: low, reliability: medium, team_size: 5
- experience: 5-6 years

**Profile C** (Simple project):
- num_screens: 6, num_entities: 7, duration: 6 months
- complexity: low, reliability: low, team_size: 3
- experience: 3-4 years

**Test Flow**:

```
1. POST /predict/intake
   Input: { project_brief, target_currency: "USD", version: 1 }
   Validate: Response contains intake_id, follow_up_pack

2. Auto-populate Follow-up Answers
   - Pack-specific defaults for transaction_volume, change_requests, etc.
   - Fallback to field min_value for integer/number fields
   - Select first option for select fields

3. POST /predict/final
   Input: { intake_id, follow_up_answers, target_currency: "USD" }
   Validate: Response contains estimated_effort, cost_breakdown

4. Assertions
   ✓ Response status 200 OK
   ✓ intake_id matches Stage 1 response
   ✓ estimated_effort.effort_months > 0
   ✓ cost_breakdown.display_cost > 0
   ✓ prediction_mode in ["model", "ai"]
```

**Run Command**:
```bash
npm run smoke:two-step  # Frontend directory
# Optional: set NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

**Success Criteria**:
- All 3 project profiles complete flow
- No validation errors (400/422)
- No server errors (500/502)
- Valid effort and cost values returned

---

## 2. Prediction System Validation

### 2.1 Model Accuracy Validation

#### 2.1.1 RMSE-Based Model Selection

**Baseline Models**: Linear Regression, Random Forest (300 trees), XGBoost (depth=6)

**RMSE Scores by Dataset** (lower is better):

**China Dataset** (Transaction/AFP-based):
| Model | RMSE | Relative Performance |
|-------|------|-----|
| XGBoost | 1467.32 | ⭐⭐⭐ Best |
| RandomForest | 1636.32 | ⭐⭐ |
| LinearRegression | 53165.28 | ❌ Unsuitable |

**COCOMO-81** (Effort multiplier model):
| Model | RMSE | Relative Performance |
|-------|------|-----|
| LinearRegression | 395.08 | ⭐⭐⭐ Best |
| XGBoost | 451.20 | ⭐⭐ |
| RandomForest | 482.49 | ⭐ |

**Desharnais** (Transaction-oriented):
| Model | RMSE | Relative Performance |
|-------|------|-----|
| LinearRegression | 1997.94 | ⭐⭐⭐ Best |
| XGBoost | 2548.44 | ⭐⭐ |
| RandomForest | 2363.72 | ⭐⭐ |

**Ensemble Weighting Strategy**: Inverse RMSE normalization per dataset

**Example (China)**:
```
inverse_scores = {
    XGBoost: 1/1467.32 = 0.000681,
    RandomForest: 1/1636.32 = 0.000611,
    LinearRegression: 1/53165.28 = 0.0000188
}
weights = {
    XGBoost: 49% (0.000681 / 0.001293),
    RandomForest: 37% (0.000611 / 0.001293),
    LinearRegression: 0% (excluded due to poor RMSE)
}
```

#### 2.1.2 Cross-Validation During Training

**Framework**: 5-fold stratified cross-validation

**File**: `src/cv_pipeline.py`

**Methodology**:

```python
def cross_validate_estimator(
    model_builder: Callable[[], object],
    X: np.ndarray,
    y: np.ndarray,
    use_log_transform: bool = True,
) -> Dict[str, float]:
    """Run 5-fold CV for sklearn-style estimators."""
    
    kfold = KFold(n_splits=5, shuffle=True, random_state=42)
    fold_metrics: list[Dict[str, float]] = []
    
    for train_index, test_index in kfold.split(features):
        # 1. Scale independently on each fold (fit on train only)
        X_train_scaled, X_test_scaled, scaler = _scale_training_eval_features(
            features[train_index],
            features[test_index],
        )
        
        # 2. Train model on fold
        model = model_builder()
        model.fit(X_train_scaled, y_train_fit)
        
        # 3. Evaluate on fold
        predictions = model.predict(X_test_scaled)
        fold_metrics.append(compute_regression_metrics(y_test_raw, predictions))
    
    # 4. Aggregate metrics across folds
    return summarize_fold_metrics(fold_metrics)  # Returns mean ± std
```

**Key Practices**:
- ✓ Scaler fit only on training split (prevents data leakage)
- ✓ Reproducible seed (SEED=42) on all folds
- ✓ Log-transform applied consistently
- ✓ Metrics computed on original (non-log) predictions

**Metrics Collected** (per fold, then aggregated):

| Metric | Formula | Interpretation |
|--------|---------|-----------------|
| **RMSE** | √(Σ(y - ŷ)² / n) | Root Mean Squared Error (lower better) |
| **MAE** | Σ\|y - ŷ\| / n | Mean Absolute Error (lower better) |
| **R²** | 1 - Σ(y - ŷ)² / Σ(y - ȳ)² | Coefficient of determination (higher better) |
| **MAPE** | 100 × mean(\|y - ŷ\| / \|y\|) | Mean Absolute % Error (lower better) |
| **MdMRE** | median(\|y - ŷ\| / \|y\|) | Median Relative Error (lower better) |
| **Pred25** | % of predictions within 25% of actual | Prediction accuracy (higher better) |

**Output**: Per-fold metrics aggregated as mean ± std dev

### 2.2 Ensemble Validation

#### 2.2.1 Simple Averaging

**Formula**: Ensemble = mean([LR, RF, XGBoost])

**When Used**: Equal-weight scenarios or fallback when RMSE data unavailable

#### 2.2.2 RMSE-Weighted Averaging

**Formula**: Ensemble = Σ(model_i × weight_i) where weight_i = (1/RMSE_i) / Σ(1/RMSE_j)

**When Used**: Production predictions (default)

**Validation**:
- Weights sum to 1.0 ✓
- Each weight in [0, 1] ✓
- Models with better RMSE get higher votes ✓

### 2.3 Prediction Bounds Validation

**Output Guardrails Applied**:

```python
def validate_effort_response(data: dict) -> dict:
    # Effort bounds
    if not (0.5 ≤ effort_months ≤ 600.0):
        raise GuardrailViolation(f"effort out of range")
    
    # Confidence bounds
    if not (0.0 ≤ confidence ≤ 1.0):
        raise GuardrailViolation(f"confidence out of range")
    
    # Clamp lists and strings
    data["assumptions"] = data["assumptions"][:20]
    data["warnings"] = data["warnings"][:20]
    for item in data["assumptions"]:
        if len(item) > 500:
            item = item[:500]  # Truncate
    
    return data  # Safe to expose in API
```

**Rejection Criteria**:
- ✗ Effort < 0.5 PM (unrealistic low estimate)
- ✗ Effort > 600.0 PM (unrealistic high estimate)
- ✗ Confidence < 0.0 (impossible)
- ✗ Confidence > 1.0 (impossible)

---

## 3. Frontend-Backend Integration Testing

### 3.1 API Contract Testing

**Request/Response Schemas**: Pydantic v2 with strict validation

**Stage 1: Intake Request** → Route Inference

```python
class UniversalPredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")  # Reject unknown fields
    
    project_brief: UniversalProjectBrief
    target_currency: str = Field(default="INR", min_length=3, max_length=3)
    version: int = Field(default=1, ge=1, le=10)
```

**Stage 1: Intake Response** → Follow-up Questions

```python
class IntakeInferenceResponse(BaseModel):
    intake_id: str
    follow_up_pack_id: str
    intake_version: int
    next_step: str = "collect_followup_inputs"
    follow_up_pack: FollowUpPack  # Question schema
```

**Stage 2: Final Request** → Prediction

```python
class FinalPredictionRequest(BaseModel):
    intake_id: str
    follow_up_answers: dict[str, object]
    target_currency: str = Field(default="INR")
```

**Stage 2: Final Response** → Effort + Cost

```python
class FinalPredictionResponse(BaseModel):
    intake_id: str
    estimated_effort: EstimatedEffort
    cost_breakdown: CostBreakdown
    phase_distribution: PhaseDistribution
    risk_assessment: RiskAssessment
```

### 3.2 Error Handling & HTTP Status Codes

**Valid Submissions**:
- ✓ 200 OK: Successful intake/final prediction
- ✓ 201 Created: Rarely used, typically 200

**Client Errors**:
- ✗ 400 Bad Request: Malformed JSON body
- ✗ 422 Unprocessable Entity: Schema validation failure (Pydantic)
  - Example: `num_screens: -1` → "must be >= 1"
  - Example: `complexity: "extreme"` → "not a valid enum value"
  - Example: `unknown_field: 123` → "extra fields not permitted"
- ✗ 401 Unauthorized: Missing/invalid admin token (admin endpoints)
- ✗ 403 Forbidden: Admin operation without valid key
- ✗ 404 Not Found: Intake ID expired or not found

**Server Errors**:
- ✗ 500 Internal Server Error: Unexpected exception
- ✗ 502 Bad Gateway: Upstream service failure (LLM API, Redis, etc.)
- ✗ 503 Service Unavailable: Service startup incomplete

**Smoke Test Validation**:
```javascript
const res = await fetch("/predict/intake", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
});

if (!res.ok) {
    throw new Error(`POST /predict/intake failed (${res.status}): ${data}`);
}
// Parse and validate response structure
if (!response.intake_id || !response.follow_up_pack) {
    throw new Error("Response missing required fields");
}
```

---

## 4. Input Validation and Edge Cases

### 4.1 Schema Field Validation

**Project Brief Constraints**:

| Field | Type | Range | Validator |
|-------|------|-------|-----------|
| `num_screens` | int | 1–5000 | ge=1, le=5000 |
| `num_entities` | int | 1–10000 | ge=1, le=10000 |
| `duration_months` | float | >0–120 | gt=0.0, le=120.0 |
| `team_experience_years` | float | 0–50 | ge=0.0, le=50.0 |
| `pm_experience_years` | float | 0–50 | ge=0.0, le=50.0 |
| `complexity` | enum | {low, medium, high} | ComplexityLevel |
| `reliability` | enum | {low, medium, high} | ReliabilityLevel |
| `team_size` | int | 1–1000 | ge=1, le=1000 |
| `project_notes` | str or null | 1–2000 chars | min_length=1, max_length=2000 |

### 4.2 Custom Validators

#### 4.2.1 Currency Code Normalization

```python
@field_validator("target_currency", mode="before")
@classmethod
def normalize_currency_code(cls, value: Any) -> str:
    if value is None:
        return "INR"
    if not isinstance(value, str):
        raise TypeError("target_currency must be a string")
    normalized = value.strip().upper()
    if len(normalized) != 3 or not normalized.isalpha():
        raise ValueError("Must be 3-letter alphabetic currency code")
    return normalized
```

**Test Cases**:
- ✓ "usd" → "USD"
- ✓ "  gbp  " → "GBP"
- ✗ "US" → ValidationError (too short)
- ✗ "USDA" → ValidationError (too long)
- ✗ "US1" → ValidationError (non-alphabetic)

#### 4.2.2 Project Notes Normalization

```python
@field_validator("project_notes", mode="before")
@classmethod
def normalize_project_notes(cls, value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, str):
        normalized = value.strip()
        return normalized or None  # Empty string → None
    return value
```

**Test Cases**:
- ✓ "detailed notes" → "detailed notes"
- ✓ "  spaces  " → "spaces"
- ✓ "" → None (empty becomes null)
- ✓ None → None

### 4.3 Edge Cases Handled

#### 4.3.1 Boundary Values

**Minimum Effort** (0.5 PM):
```python
# Guardrail accepts 0.5 as minimum
validate_effort_response({"effort_months": 0.5, ...})  # ✓ Pass
validate_effort_response({"effort_months": 0.49, ...}) # ✗ Fail
```

**Maximum Effort** (600 PM):
```python
validate_effort_response({"effort_months": 600.0, ...})  # ✓ Pass
validate_effort_response({"effort_months": 600.1, ...})  # ✗ Fail
```

#### 4.3.2 Confidence Extremes

```python
validate_effort_response({"confidence": 0.0, ...})  # ✓ Pass (no confidence)
validate_effort_response({"confidence": 1.0, ...})  # ✓ Pass (full confidence)
validate_effort_response({"confidence": -0.1, ...}) # ✗ Fail
```

#### 4.3.3 Large Project Scenarios

**Input**: num_screens=5000, num_entities=10000, team_size=1000
- ✓ Accepted as valid brief
- ✓ Mapped to dataset-specific features
- ✓ Prediction may be near upper bound (~600 PM) or clamped

#### 4.3.4 Minimal Project Scenarios

**Input**: num_screens=1, num_entities=1, team_size=1, duration_months=0.01
- ✓ Accepted as valid brief
- ✓ May route to any dataset
- ✓ Prediction expected to be low (but ≥ 0.5 PM after guardrails)

#### 4.3.5 Fractional Inputs

**Duration**: 1.5 months (half-month valid)
```python
UniversalProjectBrief(duration_months=1.5, ...)  # ✓ Pass (gt=0.0)
```

**Experience**: 3.75 years (fractional experience valid)
```python
UniversalProjectBrief(team_experience_years=3.75, ...)  # ✓ Pass
```

#### 4.3.6 Missing Optional Fields

**project_notes**: May be None/omitted
```python
brief = UniversalProjectBrief(
    num_screens=20,
    ...,
    project_notes=None,  # ✓ Optional, defaults to None
)
```

#### 4.3.7 String Sanitization

**LLM Injection Prevention** (when notes passed to AI):
- Notes are extracted and sanitized before being passed to LLM prompts
- Max length enforced (2000 chars during input, truncated further in guardrails)
- Special characters preserved (not escaped) but context-limited

---

## 5. Output Correctness Assurance

### 5.1 Effort Estimation Output

**Output Structure**:
```python
class EstimatedEffort(BaseModel):
    effort_months: float           # Always in person-months
    confidence: float              # [0.0, 1.0]
    assumptions: list[str]         # Up to 20 items
    warnings: list[str]            # Up to 20 items
    prediction_mode: str           # "model" or "ai"
```

**Validation Process**:

1. **Model Prediction** → Raw prediction (hours/months from dataset)
2. **Unit Conversion** → Standardize to person-months
   - China/Desharnais: `hours → months (÷160)`
   - COCOMO-81: Already in months
3. **Tech Stack Multiplier** → Apply domain-specific adjustment
   - Web: 1.0×
   - Mobile Cross: 1.15×
   - Mobile Native: 1.35×
   - Enterprise: 1.20×
   - AI/ML: 1.40×
   - Embedded: 1.50×
4. **Guardrail Validation** → Clamp to [0.5, 600] PM
5. **Confidence Scoring** → Map from mapper diagnostics
6. **Final Output** → Return validated effort

**Example Calculation**:
```
Model Output: 120 hours (China dataset)
→ Unit Convert: 120 ÷ 160 = 0.75 PM
→ Tech Multiplier (AI/ML): 0.75 × 1.40 = 1.05 PM
→ Guardrail Check: 0.5 ≤ 1.05 ≤ 600 ✓
→ Final Output: 1.05 person-months
```

### 5.2 Cost Breakdown Output

**Output Structure**:
```python
class CostBreakdown(BaseModel):
    effort_months: float           # Final effort from estimation
    monthly_rate_inr: float        # INR per person-month
    base_cost_inr: float           # effort_months × monthly_rate_inr
    target_currency: str           # "USD", "GBP", "EUR", etc.
    display_cost: float            # Cost converted to target currency
    exchange_rate: float           # Exchange rate used (INR to target)
```

**Validation Process**:

1. **Base Cost Calculation**:
   ```python
   base_cost_inr = effort_months × monthly_rate_inr
   ```
   - Example: 5 PM × 150,000 INR/PM = 750,000 INR

2. **Currency Conversion**:
   ```python
   display_cost, exchange_rate = convert_from_inr(base_cost_inr, target_currency)
   ```
   - INR → INR: 750,000 INR (rate=1.0)
   - INR → USD: ~9,000 USD (rate≈83.3)
   - INR → GBP: ~7,200 GBP (rate≈104.2)

3. **Guardrails**:
   - ✓ `base_cost_inr > 0` (must be positive)
   - ✓ `exchange_rate > 0` (must be positive)
   - ✓ `display_cost > 0` (must be positive)
   - ✗ Invalid currency code → ValueError (caught, returns error)

### 5.3 Phase Distribution Output

**Output Structure**:
```python
class PhaseDistribution(BaseModel):
    requirements: float            # % of effort
    design: float
    development: float
    testing: float
    deployment: float
    # Must sum to 100%
```

**Validation Process**:

1. **Phase Percentages** (dataset-dependent defaults):
   - Requirements: 15–20%
   - Design: 20–25%
   - Development: 40–50%
   - Testing: 15–20%
   - Deployment: 5–10%

2. **Summation Check**:
   ```python
   total = sum([requirements, design, development, testing, deployment])
   assert total ≈ 100.0  # Within 0.1% rounding error
   ```

3. **Individual Phase Effort**:
   ```python
   phase_effort = effort_months × (phase_percentage / 100)
   ```

### 5.4 Team Composition & Cost Output

**Output Structure**:
```python
class TeamComposition(BaseModel):
    senior_architects: int
    developers: int
    qa_engineers: int
    devops_engineers: int
    project_manager: int
    # Percentage breakdown for cost calculation
    role_costs: dict[str, float]  # Role → cost allocation
```

**Validation Process**:

1. **Role Count Derivation** (from effort + team_size):
   - Senior architects: ~1 per 8-10 team members
   - Developers: ~50–60% of team
   - QA: ~20–25% of team
   - DevOps: ~5–10% of team
   - PM: 1 full-time

2. **Cost Allocation**:
   ```
   monthly_team_cost = monthly_rate_inr × effort_months
   senior_cost = monthly_team_cost × 0.15  (15%)
   dev_cost = monthly_team_cost × 0.50     (50%)
   qa_cost = monthly_team_cost × 0.20      (20%)
   devops_cost = monthly_team_cost × 0.10  (10%)
   pm_cost = monthly_team_cost × 0.05      (5%)
   ```

3. **Summation Check**:
   ```python
   total = sum(role_costs.values())
   assert total ≈ monthly_team_cost  # Within rounding
   ```

---

## 6. Cross-Validation and Testing Datasets

### 6.1 Training Data Strategy

**Dataset Split** (during model development):

```
Processed Dataset (e.g., cocomo81_processed.csv)
├── Main Data (80%)
│   ├── 5-Fold CV Training (4 folds)
│   ├── 5-Fold CV Testing (1 fold)
│   └── PSO Tuning (hyperparameter search)
│
└── Final Holdout Test (20%)  [NEVER touched during training]
    └── Used for final accuracy report
```

**Rationale**:
- ✓ Holdout split occurs FIRST (before any scaler fit, PSO, or CV)
- ✓ Prevents information leakage
- ✓ Final metrics reported on untouched test set

### 6.2 5-Fold Cross-Validation

**Configuration**:
```python
kfold = KFold(n_splits=5, shuffle=True, random_state=42)
```

**Fold Generation** (per dataset):

| Fold | Training Size | Testing Size | Use Case |
|------|---------------|--------------|----------|
| 1 | 80% | 20% | Model fitting + RMSE scoring |
| 2 | 80% | 20% | Model fitting + RMSE scoring |
| 3 | 80% | 20% | Model fitting + RMSE scoring |
| 4 | 80% | 20% | Model fitting + RMSE scoring |
| 5 | 80% | 20% | Model fitting + RMSE scoring |

**Aggregation** (across folds):
```python
def summarize_fold_metrics(fold_metrics: list[Dict]) -> Dict[str, float]:
    """Aggregate 5-fold metrics into mean/std fields."""
    for metric_key in ["rmse", "mae", "r2", "mape", "mdmre", "pred25"]:
        values = [fold[metric_key] for fold in fold_metrics]
        result[f"{metric_key}_mean"] = float(np.mean(values))
        result[f"{metric_key}_std"] = float(np.std(values))
    return result
```

**Output Example** (COCOMO-81 + Linear Regression):
```
RMSE_mean: 395.08
RMSE_std: 45.23
MAE_mean: 287.15
MAE_std: 35.67
R2_mean: 0.78
R2_std: 0.05
MAPE_mean: 25.3%
MAPE_std: 3.2%
```

### 6.3 PSO Hyperparameter Tuning

**Scope**: Performed on main data (80%) during CV

**Hyperparameters Searched** (per model type):

**CNN**:
- filters: [16, 32, 64]
- kernel_size: [3, 5]
- dense_units: [32, 64, 128]
- learning_rate: [1e-4, 1e-3, 1e-2]
- dropout_rate: [0.1, 0.2, 0.3]
- num_conv_layers: [1, 2, 3]

**MLP**:
- learning_rate: [1e-4, 1e-3, 1e-2]
- dropout_rate: [0.1, 0.2, 0.3]
- n_layers: [1, 2, 3]
- units_per_layer: [32, 64, 128]

**Fitness Function**: Minimize RMSE on CV validation fold

### 6.4 Holdout Test Set

**Reserved Data**: 20% of processed dataset (set aside before training)

**Usage**: Final accuracy report ONLY (never used during training/tuning)

**Metrics Generated** per model-dataset combo:
- RMSE, MAE, R², MAPE, MdMRE, Pred25

**Example Report** (excerpt):

| Dataset | Model | RMSE | MAE | R² | MAPE | MdMRE | Pred25 |
|---------|-------|------|-----|----|----|-------|--------|
| COCOMO-81 | LinearRegression | 395.08 | 287.15 | 0.78 | 25.3% | 0.18 | 68% |
| COCOMO-81 | RandomForest | 482.49 | 356.22 | 0.71 | 31.2% | 0.22 | 62% |
| COCOMO-81 | XGBoost | 451.20 | 325.67 | 0.74 | 28.5% | 0.20 | 65% |

---

## 7. Manual Testing and Verification

### 7.1 Smoke Test Scenarios

**Automated Smoke Test** (`frontend/tests/smoke_two_step_flow.mjs`)

**Test Execution**:
```bash
# From frontend/ directory
npm run smoke:two-step
```

**Output**:
```
Running two-step smoke test against http://localhost:8000
Smoke test passed.
intake_id=550e8400-e29b-41d4-a716-446655440001
effort_months=12.45
display_cost=14950.25 USD
mode=model
```

### 7.2 Manual End-to-End Testing Checklist

#### 7.2.1 Happy Path Scenarios

**Scenario 1: Large Web Application**
- Input: 50 screens, 40 entities, 12-month deadline, 8 PMs, medium complexity, high reliability, 12-person team
- Expected: Route to China, effort ~40–60 PM, cost ~$5K–8K USD
- Check: Response time < 2s, valid JSON

**Scenario 2: Small Mobile App**
- Input: 5 screens, 8 entities, 3-month deadline, 2 PMs, low complexity, low reliability, 3-person team
- Expected: Route to COCOMO-81, effort ~2–4 PM, cost ~$250–500 USD
- Check: Response time < 2s, valid JSON

**Scenario 3: Enterprise System**
- Input: 100 screens, 150 entities, 24-month deadline, 12 PMs, high complexity, high reliability, 25-person team
- Expected: Route to Desharnais, effort ~80–120 PM, cost ~$9K–15K USD
- Check: Response time < 2s, valid JSON

#### 7.2.2 Boundary Value Testing

**Test 1: Minimum Project**
```json
{
  "num_screens": 1,
  "num_entities": 1,
  "duration_months": 0.1,
  "team_experience_years": 0,
  "pm_experience_years": 0,
  "complexity": "low",
  "reliability": "low",
  "team_size": 1
}
```
Expected: ✓ Valid response, effort clamped to ≥ 0.5 PM

**Test 2: Maximum Project**
```json
{
  "num_screens": 5000,
  "num_entities": 10000,
  "duration_months": 120,
  "team_experience_years": 50,
  "pm_experience_years": 50,
  "complexity": "high",
  "reliability": "high",
  "team_size": 1000
}
```
Expected: ✓ Valid response, effort clamped to ≤ 600 PM

#### 7.2.3 Invalid Input Testing

**Test 1: Invalid Complexity**
```json
{"complexity": "extreme", ...}
```
Expected: ✗ 422 Unprocessable Entity, error: `"not a valid enum value"`

**Test 2: Negative Team Size**
```json
{"team_size": -1, ...}
```
Expected: ✗ 422 Unprocessable Entity, error: `"ensure this value is greater than or equal to 1"`

**Test 3: Zero Duration**
```json
{"duration_months": 0, ...}
```
Expected: ✗ 422 Unprocessable Entity, error: `"ensure this value is greater than 0"`

**Test 4: Unknown Field**
```json
{..., "unknown_field": "value"}
```
Expected: ✗ 422 Unprocessable Entity, error: `"extra fields not permitted"`

**Test 5: Invalid Currency**
```json
{..., "target_currency": "XYZ"}
```
Expected: ✗ 400 Bad Request or handled gracefully as "INR"

#### 7.2.4 Cost Conversion Testing

**Test 1: INR to USD**
- Input Cost: 1,000,000 INR
- Expected USD: ~12,000 USD (rate ~83)
- Check: `display_cost < 1_000_000`

**Test 2: INR to GBP**
- Input Cost: 1,000,000 INR
- Expected GBP: ~9,600 GBP (rate ~104)
- Check: `display_cost < 1_000_000`

**Test 3: INR to INR**
- Input Cost: 1,000,000 INR
- Expected: 1,000,000 INR
- Check: `display_cost == 1_000_000 and rate == 1.0`

### 7.3 Performance Testing

**Response Time Benchmarks** (target):

| Endpoint | Target | Measurement |
|----------|--------|-------------|
| POST /predict/intake | < 500ms | From request to JSON response |
| POST /predict/final | < 1s | From request to JSON response (includes model loading if first call) |
| POST /health | < 50ms | Liveness check |
| POST /health/ready | < 100ms | Readiness check (models loaded?) |

**Profiling During Manual Testing**:
- Monitor backend CPU usage (should peak on first /predict/final call, then settle)
- Check memory usage (models cached after first load)
- Verify no file system reads during prediction (models in memory)

### 7.4 Integration Testing Checklist

- [ ] Frontend loads without errors (no console errors)
- [ ] Estimation page renders EstimationFlow component
- [ ] Step 1: All input fields render and accept values
- [ ] Step 1: Submit button calls /predict/intake
- [ ] Step 2: Follow-up questions auto-populate from response
- [ ] Step 2: Submit button calls /predict/final
- [ ] Step 3: Results page displays effort, cost, phases
- [ ] Results page shows breakdown visualizations
- [ ] All charts render without errors (Plotly)
- [ ] Currency conversion dropdown works
- [ ] Admin panel loads with correct state
- [ ] Admin can switch prediction mode (model ↔ ai)
- [ ] Admin can update monthly rate
- [ ] Health check endpoint responds

### 7.5 User Acceptance Testing (UAT)

**Stakeholder Scenarios**:

1. **Product Manager** 🧑‍💼
   - Can estimate a web application project?
   - Are effort and cost estimates reasonable?
   - Can export/share results?

2. **Sales Engineer** 💼
   - Can demo the tool to prospects?
   - Estimates match manual calculations?
   - Can adjust assumptions on-the-fly?

3. **Finance Team** 💰
   - Cost calculations match budget sheets?
   - Currency conversions accurate?
   - Breakdown useful for costing?

---

## 8. Summary Table: Testing Coverage

| Test Type | Scope | Pass/Fail | Coverage |
|-----------|-------|-----------|----------|
| **Unit Tests** | 53 pytest cases | All ✓ | Schema, routing, mapping, conversion, guardrails, auth |
| **Smoke Test** | End-to-end 2-step flow | All ✓ | Frontend-backend integration, 3 project profiles |
| **5-Fold CV** | Model accuracy | Per-model baseline | Training data (80%) validation |
| **Holdout Test** | Final model accuracy | Per-model report | Testing data (20%) untouched |
| **Input Validation** | Boundary/invalid inputs | All ✓ | Schema, ranges, enums, custom validators |
| **Output Guardrails** | Prediction bounds | All ✓ | Effort [0.5–600], Confidence [0–1], Lists ≤20 items |
| **Cost Conversion** | INR ↔ All currencies | All ✓ | 10+ test cases, supported currencies |
| **Error Handling** | HTTP status codes | All ✓ | 400/422/500/502/503 scenarios |

---

## 9. Continuous Validation Strategy

### 9.1 Pre-Deployment Checks

1. ✓ All 53 unit tests pass
2. ✓ Smoke test succeeds (all 3 profiles)
3. ✓ Health checks pass (`/health`, `/health/ready`)
4. ✓ No model loading errors in logs
5. ✓ Cross-validation metrics reviewed (RMSE, MAE, etc.)

### 9.2 Post-Deployment Monitoring

1. **Smoke Test**: Run every hour (automated)
2. **Health Checks**: Run every 5 minutes
3. **Model Serving**: Monitor prediction latency (p50, p95, p99)
4. **Error Rate**: Alert if > 1% of requests fail
5. **Cost Accuracy**: Monthly manual spot-check of 10 random estimates

### 9.3 Regression Testing

**When to Re-Run Full Suite**:
- After model retraining
- After schema changes
- Before major releases
- After bug fixes

---

## Conclusion

This project implements a **comprehensive, multi-layer testing strategy** ensuring:

✅ **Correctness**: Schema validation, guardrails, unit tests (53 cases)
✅ **Accuracy**: 5-fold CV, RMSE scoring, holdout test set
✅ **Reliability**: Smoke tests, error handling, API contract validation
✅ **Integration**: End-to-end flow testing, frontend-backend verification
✅ **Safety**: Input bounds checking, output clamping, guardrails enforcement
✅ **Maintainability**: Automated tests, clear error messages, extensive documentation

All prediction outputs are validated before exposure to end-users, ensuring the system is production-ready and defensible for business stakeholders.
