# Aether

Aether is a fintech safety app focused on scam awareness and financial fraud prevention. It helps users inspect suspicious messages, understand warning signs, practise identifying scams, and find safer next steps when dealing with potential financial threats.

Aether features a React and Vite frontend with a Flask API backend.

## Features

- **Message Checks:** Analyze pasted SMS messages, chats, emails, URLs, phone numbers, and UPI IDs for common scam indicators.
- **Email Forensics:** Paste email headers or upload `.eml` or `.txt` files to inspect sender claims, authentication results, links, and routing information.
- **Scam Practice:** Review fictional scam and legitimate-message scenarios with difficulty and category filters.
- **Bank Watch:** Browse curated incident data and external news coverage for banks and payment providers.
- **Scam Reports Map:** Explore regional reports and submit anonymous scam reports for Indian states and union territories.
- **Recovery Guidance:** Follow recommended steps for situations involving sent money, clicked links, or shared personal information.
- **Safety Assistant:** Ask questions about scams and financial safety.

> **Disclaimer:** Aether provides general safety guidance. Email headers may be incomplete or forged, and neither a risk score nor the absence of warnings proves that a message is safe.

## Tech Stack

- **Frontend:** React, Vite, Tailwind CSS
- **Backend:** Python, Flask
- **Optional Integrations:** OpenRouter, Google Safe Browsing, Supabase

## Requirements

- Python 3.10 or later
- Node.js and npm

## Run Locally

Start the backend and frontend in separate terminals.

### 1. Start the Backend

From the project root, run:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python run.py
```

**macOS / Linux:**

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run.py
```

The Flask backend should be available at:

- **API:** http://127.0.0.1:5000
- **Health Check:** http://127.0.0.1:5000/api/health

Open the health-check URL to verify that the backend is running.

### 2. Start the Frontend

Open a second terminal from the project root:

```bash
cd Frontend
npm ci
npm run dev
```

Open the Vite URL displayed in the terminal, usually http://localhost:5173.

During development, Vite forwards `/api` requests to Flask.

### 3. Configure the Backend URL

If Flask runs at a different address, create or update `Frontend/.env.local`:

```env
AETHER_BACKEND_URL=http://127.0.0.1:8000
```

Restart Vite after changing the configuration.

For a frontend deployment that connects directly to an API, configure `VITE_API_BASE_URL` with the API base URL. Set the backend's `FRONTEND_URL` to the frontend origin to allow cross-origin requests.

## Optional Backend Configuration

Create a `backend/.env` file for integrations that require credentials:

```env
OPENROUTER_API_KEY=
OPENROUTER_MODEL=deepseek/deepseek-v4-flash
OPENROUTER_FALLBACK_MODEL=deepseek/deepseek-chat

SAFE_BROWSING_API_KEY=

SUPABASE_URL=
SUPABASE_SERVICE_KEY=

FRONTEND_URL=http://localhost:5173,http://127.0.0.1:5173
ADMIN_KEY=
```

### Integration Details

- **OpenRouter:** Enables assistant responses, generated explanations, and generated practice scenarios. Built-in fallback behavior may be available when the service is unavailable.
- **Google Safe Browsing:** Enables external URL reputation checks. Without an API key, Aether can still inspect suspicious link patterns but cannot verify reputation through this service.
- **Supabase:** Enables shared storage for verdict metadata and scam reports. Without it, regional reports use a local SQLite database.
- **Admin Key:** Protects the demo email deletion endpoint.

The backend reads `backend/.env` at startup.

**Security note:** Never commit real API keys, service-role credentials, or other secrets to version control.

## API Endpoints

All endpoints are prefixed with `/api`.

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Check backend health |
| `POST` | `/analyse` | Analyze message text |
| `POST` | `/analyze/eml` | Analyze an uploaded `.eml` or `.txt` file |
| `GET` | `/simulation/next` | Retrieve a practice scenario |
| `POST` | `/simulation/score` | Submit a practice answer |
| `GET` | `/bank-watch?bank=<name>` | Retrieve curated incidents and news coverage |
| `GET` | `/map/data` | Retrieve map data and report totals |
| `POST` | `/map/report` | Submit a regional scam report |
| `GET` | `/panic/money_sent` | Retrieve guidance for situations where money was sent |
| `GET` | `/panic/no_money` | Retrieve guidance for situations where no money was sent |
| `POST` | `/chat` | Ask the safety assistant a question |

## Data and Privacy

- **Message Analysis:** Submitted text is analyzed to generate a result. When Supabase is configured, Aether may store verdict metadata and risk indicators, but raw message text is not stored in the verdict record.
- **Recent Checks:** The frontend keeps recent checks within the current app session.
- **Practice Progress:** Stored in session storage.
- **Recovery Checklists:** Progress is stored in local storage.
- **Bank Watch:** External news coverage is not equivalent to a verified fraud report.
- **Regional Reports:** Depending on the configuration, reports may be stored in Supabase or the backend's local SQLite database.

## License

See [`LICENSE`](LICENSE) for license information.
