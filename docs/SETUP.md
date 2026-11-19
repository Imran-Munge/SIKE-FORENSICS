# Local setup

## Backend
Python 3.11+.
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

## Frontend
Node 20+.
cd frontend
npm install
npm run dev

Set NEXT_PUBLIC_API_URL=http://localhost:8000 in frontend/.env.local.

## Production
Use object storage for originals, a queue/worker for expensive video/audio models, PostgreSQL for cases and evidence, and isolated analysis workers. Never overwrite original evidence.