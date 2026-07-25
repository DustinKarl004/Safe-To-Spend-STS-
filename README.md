# Safe-To-Spend (STS)

## Run locally

**Quickest way — one script, both services:**
```bash
./dev.sh
```
Handles venv creation, `pip install`, `npm install`, and `.env` setup automatically on first run. Ctrl+C stops both. Backend: http://localhost:8000, frontend: http://localhost:5173.

**Or run each manually, in two terminals:**

**Backend** (FastAPI, port 8000):
```bash
cd safe-to-spend-api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

**Frontend** (Vue 3 + Vite, port 5173):
```bash
cd safe-to-spend-web
npm install
npm run dev
```

Open http://localhost:5173 — register, set your payday and wallets, and the dashboard shows your live safe-to-spend number.
