# requirement-analyser

**Purpose:**
- This repository contains a FastAPI backend and a React + Vite frontend for a requirements analysis tool (generates stories, epics, QA, and test plans from uploaded files).

**Prerequisites**
- Python 3.10+ installed and available as `python3`.
- Node.js 18+ and `npm` for the frontend.
- Git (optional) to clone the repository.

**Repository layout (important paths)**
- Backend entry: `app.py`
- Backend routes: `routes/`
- Frontend app: `frontend/` (Vite + React)
- Requirements: `requirements.txt`

**Quick start (macOS / zsh)**

1) Backend: create virtualenv and install Python dependencies

```bash
cd /path/to/requirement-analyser
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

2) Run the FastAPI backend (development)

```bash
# from the project root
uvicorn app:app --reload
```

After starting, the API will be available at `http://localhost:8000` and the automatic OpenAPI docs at `http://localhost:8000/docs`.

Replace `/your-endpoint` with the actual route names defined in `routes/` (for example, `/list-files` — check the routers in that folder).

3) Frontend: install and run - Dev In progress

```bash
cd frontend
npm install
npm run dev
```

The frontend dev server (Vite) will usually run on `http://localhost:5173` — check the terminal output for the exact URL.