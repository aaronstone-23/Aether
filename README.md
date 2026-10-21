# Aether

Aether is a scam awareness app with a React/Vite frontend and a Flask API. During local development, Vite forwards `/api/*` requests to Flask so both sides work from the same browser origin.

## Run the app locally

Use two terminals from this directory.

**Terminal 1 — backend** (Python 3.10+):

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python run.py
```

Flask listens on `http://127.0.0.1:5000`. Its health endpoint is `http://127.0.0.1:5000/api/health`.

**Terminal 2 — frontend** (Node.js):

```powershell
cd Frontend
npm ci
npm run dev
```

Open the Vite URL printed in the terminal, usually `http://localhost:5173`. The app's connection indicator should show **connected**. The frontend sends API requests to `/api`; Vite proxies those requests to Flask.

If Flask runs on a different address, set `AETHER_BACKEND_URL` in `Frontend/.env.local`, for example `AETHER_BACKEND_URL=http://127.0.0.1:8000`, then restart Vite. `VITE_API_BASE_URL` can be set to a full API base URL when a deployment does not use the Vite proxy. For direct cross-origin requests, set backend `FRONTEND_URL` to the frontend origin (comma-separated origins are supported).

## Optional services

Create `backend/.env` for integrations that need credentials. The app can run without these, with the related live features unavailable or using their built-in fallback behavior.

```dotenv
OPENROUTER_API_KEY=
SUPABASE_URL=
SUPABASE_SERVICE_KEY=
SAFE_BROWSING_API_KEY=
FRONTEND_URL=http://localhost:5173,http://127.0.0.1:5173
```

The backend reads this file at startup. Never commit real credentials.
