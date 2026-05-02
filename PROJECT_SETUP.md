# Project Setup

This repository contains a FastAPI backend (`backend/`) and a Next.js frontend (`frontend/`).

---

## Prerequisites

- Python 3.10+ with a virtual environment at `venv/`
- Node.js 18+

---

## 1. Clone and create the virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 2. Configure the backend

```powershell
cd backend
Copy-Item .env.example .env
```

Open `backend/.env` and fill in your values. Key settings:

| Variable | Default | Description |
|---|---|---|
| `PREDICTION_MODE` | `model` | `model` uses ML ensemble; `ai` uses an AI provider |
| `OPENAI_API_KEY` | — | Required when `PREDICTION_MODE=ai` and `AI_PROVIDER=openai` |
| `GEMINI_API_KEY` | — | Required when `AI_PROVIDER=gemini` |
| `GROQ_API_KEY` | — | Required when `AI_PROVIDER=groq` |
| `AI_PROFILE` | `balanced` | Prompt profile: `conservative`, `balanced`, or `optimistic` |
| `DEFAULT_MONTHLY_RATE_INR` | `150000` | Blended monthly rate per person used for cost derivation |
| `REDIS_URL` | — | Required for reliable Stage-1 to Stage-2 intake handoff in multi-worker production |
| `INTAKE_CACHE_TTL_SECONDS` | `3600` | Expiry window (seconds) for intake context between `/predict/intake` and `/predict/final` |
| `ADMIN_API_KEY` | — | Set a strong random string to enable the `/admin/*` endpoints |

---

## 3. Start the backend

```powershell
cd backend
..\venv\Scripts\Activate.ps1
python main.py
```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`.

---

## 4. Configure the frontend

```powershell
cd frontend
npm install
```

The frontend defaults to `http://localhost:8000` for all API calls.  
To use a different backend URL, create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

---

## 5. Start the frontend

```powershell
cd frontend
npm run dev
```

The app will be available at `http://localhost:3000`.

---

## 6. Admin dashboard

Navigate to `http://localhost:3000/admin`.  
Enter the `ADMIN_API_KEY` value from `backend/.env` to sign in.

From the dashboard you can change prediction mode, AI provider, prompt profile, monthly rate, and default display currency at runtime without redeploying.

---

## 7. Run backend tests

```powershell
cd backend
..\venv\Scripts\Activate.ps1
python -m pytest tests/ -v
```

---

## 8. Run frontend two-step smoke test

Keep the backend running, then execute:

```powershell
cd frontend
npm run smoke:two-step
```

Expected result includes `Smoke test passed.` plus effort/cost output.

---

## Public API — quick reference

| Method | Path | Description |
|---|---|---|
| `POST` | `/predict/intake` | Stage 1 — submit project brief, receive adaptive follow-up pack |
| `POST` | `/predict/final` | Stage 2 — submit follow-up answers, receive effort + cost estimate |
| `GET` | `/health` | Liveness check |
| `GET` | `/datasets` | List supported dataset identifiers (legacy) |
| `GET` | `/admin/state` | Get current runtime config (requires Bearer token) |
| `PATCH` | `/admin/state` | Update runtime config (requires Bearer token) |
| `GET` | `/admin/diagnostics` | Live diagnostics (requires Bearer token) |