# Project Setup

This repository now includes a frontend package in `frontend/` and a FastAPI backend in `backend/`.

## Start the backend

Open a PowerShell terminal at the repository root and run:

```powershell
cd backend
..\venv\Scripts\Activate.ps1
pip install -r ..\requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.

## Start the frontend

Open a second PowerShell terminal at the repository root and run:

```powershell
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:3000`.

## Optional environment override

The frontend defaults to `http://localhost:8000` for API requests. If you need a different backend URL, create a `.env.local` file inside `frontend/` with:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Runtime expectation

- Backend API: `POST /predict`, `GET /health`, `GET /datasets`
- Frontend UI: single-page Next.js app with the demo connected to the backend prediction service