# Development Setup Guide

## Project Structure Overview

After reorganization, the project is now organized as:

```
requirement-analyser/
├── backend/                 # ← All backend code moved here
│   ├── agents/             # Agentic framework
│   ├── config/             # Configuration files
│   ├── models/             # Database models
│   ├── prompts/            # LLM prompts
│   ├── rag/                # RAG system
│   ├── routes/             # API routes
│   ├── app.py              # FastAPI entry point
│   └── requirements.txt     # Python dependencies
│
├── frontend/               # React + Vite application
│   ├── src/
│   ├── public/
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── run_backend.sh          # Quick backend startup
├── run_frontend.sh         # Quick frontend startup
└── README.md               # Main documentation
```

## Why This Structure?

1. **Clear Separation:** Backend and frontend are completely separated
2. **Scalability:** Easy to deploy backend and frontend independently
3. **Modularity:** Agents are organized logically within the backend
4. **Convention:** Follows standard monorepo patterns (backend/, frontend/)

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+ with npm
- PostgreSQL (or SQLite configured in config/db.py)

### Rapid Setup

```bash
# Option 1: Using startup scripts (easiest)
./run_backend.sh    # Terminal 1
./run_frontend.sh   # Terminal 2
```

### Manual Setup

**Backend:**
```bash
cd backend
python3 -m venv ../.venv
source ../.venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Import Structure Explanation

### Backend Imports (app.py)

The key change is in `backend/app.py`:

```python
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now imports work as if backend/ is the root
from config.db import Base, engine
from routes import upload, generateStories, ...
```

This allows all backend modules to use simple imports:
- `from config.db import ...` (not `from backend.config.db`)
- `from models.file_model import ...`
- `from agents.epic_agent import EpicAgent`

### Frontend API Calls

Frontend makes HTTP calls to `http://localhost:8000/*`:
- These endpoint URLs do NOT change
- CORS is configured to allow frontend origin
- API contract remains the same

## Key Files and Their Purposes

### Backend Configuration
| File | Purpose |
|------|---------|
| `backend/app.py` | FastAPI application entry point |
| `backend/config/db.py` | Database session and Base model |
| `backend/config/gemini.py` | Gemini LLM integration |
| `backend/config/config.py` | Environment and settings |
| `backend/requirements.txt` | Python dependencies |

### Backend Agents
| File | Purpose |
|------|---------|
| `backend/agents/base_agent.py` | Abstract base class for all agents |
| `backend/agents/epic_agent.py` | Generates epics from requirements |
| `backend/agents/story_agent.py` | Generates stories from epics |
| `backend/agents/qa_agent.py` | Generates QA/test cases |
| `backend/agents/rag_agent.py` | Retrieves documents via RAG |
| `backend/agents/agent_coordinator.py` | Orchestrates agent workflows |

### Backend Routes
| File | Purpose |
|------|---------|
| `backend/routes/agents_router.py` | Agentic AI endpoints |
| `backend/routes/upload.py` | File upload endpoint |
| `backend/routes/generateEpics.py` | Epic generation (legacy) |
| `backend/routes/generateStories.py` | Story generation (legacy) |
| `backend/routes/generateQA.py` | QA generation (legacy) |
| `backend/routes/getEpics.py` | List epics with pagination |
| `backend/routes/getStories.py` | List stories with pagination |
| `backend/routes/getQA.py` | List QA with pagination |
| `backend/routes/getTestPlan.py` | List test plans with pagination |

### Backend Models
| File | Purpose |
|------|---------|
| `backend/models/file_model.py` | SQLAlchemy ORM models |

### Frontend Components
| File | Purpose |
|------|---------|
| `frontend/src/App.jsx` | Main router component |
| `frontend/src/components/UploadPage.jsx` | File upload interface |
| `frontend/src/components/EpicsPage.jsx` | Browse epics |
| `frontend/src/components/StoriesPage.jsx` | Browse stories |
| `frontend/src/components/QAPage.jsx` | Browse QA |
| `frontend/src/components/AgenticAIPage.jsx` | Agentic AI control panel |
| `frontend/src/api/api.js` | HTTP client helpers |

## Development Workflow

### Running the Full Stack

**Terminal 1 - Backend:**
```bash
cd requirement-analyser
./run_backend.sh

# Or manually:
cd backend
source ../.venv/bin/activate
uvicorn app:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd requirement-analyser
./run_frontend.sh

# Or manually:
cd frontend
npm run dev
```

**Terminal 3 - Optional: Monitor logs**
```bash
# Watch backend logs for errors
tail -f /path/to/log/file

# Or use curl to test endpoints
curl http://localhost:8000/docs  # OpenAPI docs
```

### Making Changes

#### Backend Changes
1. Edit files in `backend/agents/`, `backend/routes/`, or `backend/config/`
2. Server auto-reloads with `--reload` flag
3. Check `http://localhost:8000/docs` for API changes

#### Frontend Changes
1. Edit files in `frontend/src/`
2. Browser auto-refreshes via Vite HMR
3. Check browser console for errors

#### Agent Development
1. Create new agent by extending `BaseAgent` in `backend/agents/`
2. Implement `execute(context)` method
3. Register in `AgentCoordinator`
4. Add endpoint in `backend/routes/agents_router.py`
5. Add API helper in `frontend/src/api/api.js`

## Environment Configuration

Create `.env` file in project root:

```env
# Database
POSTGRES_URL=postgresql://user:password@localhost:5432/requirement_db

# LLM
GEMINI_API_KEY=your_gemini_key_here

# Confluence (optional)
CONFLUENCE_URL=https://yourinstance.atlassian.net/wiki
CONFLUENCE_USERNAME=your_email@example.com
CONFLUENCE_PASSWORD=your_api_token
CONFLUENCE_SPACE_KEY=~personal_space_key
CONFLUENCE_ROOT_FOLDER_ID=12345678

# Application
DEBUG=true
LOG_LEVEL=INFO
```

## Common Tasks

### Installing New Python Package
```bash
cd backend
source ../.venv/bin/activate
pip install package_name
pip freeze > requirements.txt  # Update requirements
```

### Installing New NPM Package
```bash
cd frontend
npm install package_name
npm run build  # Test build before deploying
```

### Testing an Endpoint
```bash
# Test health
curl http://localhost:8000/

# Test epic generation
curl -X POST http://localhost:8000/agents/epic/generate \
  -H "Content-Type: application/json" \
  -d '{"upload_id": 1}'

# Test with jq for pretty output
curl -s http://localhost:8000/epics | jq '.data.epics'
```

### Database Migrations
If using Alembic:
```bash
cd backend
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## Troubleshooting

### Backend Won't Start
```bash
# Check Python version
python3 --version  # Should be 3.10+

# Check virtual environment is activated
which python  # Should show .venv path

# Reinstall dependencies
pip install -r requirements.txt

# Check syntax
python3 -m py_compile app.py
```

### Frontend Won't Start
```bash
# Check Node version
node --version  # Should be 18+
npm --version   # Should be 9+

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Port Already in Use
```bash
# Backend on different port
uvicorn app:app --port 8001

# Frontend on different port
npm run dev -- --port 3000
```

### Database Connection Error
```bash
# Check if PostgreSQL is running
psql -h localhost -U user -d requirement_db -c "SELECT 1"

# Check POSTGRES_URL in .env
echo $POSTGRES_URL
```

## Next Steps

1. **Review AGENTIC_ARCHITECTURE.md** for detailed agent documentation
2. **Explore agent implementations** in `backend/agents/`
3. **Test endpoints** using the interactive API docs at http://localhost:8000/docs
4. **Add new agents** following the BaseAgent pattern
5. **Extend RAG system** for better document retrieval

## Support

For issues or questions:
1. Check `README.md` for general info
2. Review `AGENTIC_ARCHITECTURE.md` for agent details
3. Examine existing agents as examples
4. Check backend logs for error details
