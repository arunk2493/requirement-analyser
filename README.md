# Requirement Analyzer - Agentic AI System

**Purpose:**
An intelligent requirement analysis tool using an agentic AI architecture. Converts uploaded requirements into epics, stories, and QA test cases using specialized agents (EpicAgent, StoryAgent, QAAgent, RAGAgent). Integrates with Confluence for document management.

**Architecture:**
- **Backend:** FastAPI with agentic framework (agents/, config/, models/, routes/)
- **Frontend:** React 18 + Vite + PrimeReact for UI components
- **Database:** PostgreSQL (configured via POSTGRES_URL env variable)
- **LLM:** Google Gemini for text generation
- **RAG:** Vector-based document retrieval for context-aware generation
- **Collaboration:** Confluence integration for page creation and documentation

**Prerequisites**
- Python 3.10+ installed and available as `python3`
- Node.js 18+ and `npm` for the frontend
- PostgreSQL database (or configure SQLite in config/db.py)
- Google Gemini API key
- Confluence instance credentials (optional, for document creation)
- Git (optional) to clone the repository

**Repository Layout**
```
requirement-analyser/
├── backend/                 # Backend code
│   ├── agents/             # Agentic framework (EpicAgent, StoryAgent, QAAgent, RAGAgent)
│   ├── routes/             # FastAPI route handlers
│   ├── models/             # SQLAlchemy ORM models
│   ├── config/             # Configuration (database, LLM, Confluence)
│   ├── prompts/            # LLM prompt templates
│   ├── rag/                # RAG system (embeddings, vectorstore)
│   ├── app.py              # FastAPI application entry point
│   └── requirements.txt     # Python dependencies
│
├── frontend/               # React + Vite frontend
│   ├── src/
│   │   ├── components/     # React components (pages, UI)
│   │   ├── api/            # API client helpers
│   │   └── App.jsx         # Main app component
│   ├── package.json        # Node dependencies
│   └── vite.config.js      # Vite configuration
│
├── run_backend.sh          # Backend startup script
├── run_frontend.sh         # Frontend startup script
├── AGENTIC_ARCHITECTURE.md # Detailed agent system documentation
└── README.md               # This file
```

**Quick Start**

### Option 1: Use startup scripts (Recommended)

```bash
# Terminal 1 - Start Backend
cd /path/to/requirement-analyser
./run_backend.sh

# Terminal 2 - Start Frontend
cd /path/to/requirement-analyser
./run_frontend.sh
```

### Option 2: Manual startup

**Backend Setup:**
```bash
cd /path/to/requirement-analyser/backend
python3 -m venv ../.venv
source ../.venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

**Frontend Setup:**
```bash
cd /path/to/requirement-analyser/frontend
npm install
npm run dev
```

**Environment Variables:**
Create a `.env` file in the project root:
```
POSTGRES_URL=postgresql://user:password@localhost/db_name
GEMINI_API_KEY=your_gemini_api_key
CONFLUENCE_URL=https://yourinstance.atlassian.net/wiki
CONFLUENCE_USERNAME=your_email@example.com
CONFLUENCE_PASSWORD=your_api_token
CONFLUENCE_SPACE_KEY=your_space_key
CONFLUENCE_ROOT_FOLDER_ID=your_folder_id
```

**Access the Application:**
- Frontend: http://localhost:5173 (or 5174 if 5173 is taken)
- API Docs: http://localhost:8000/docs
- Backend Health: http://localhost:8000/

**Core Features**

1. **Upload Requirements** - Upload PDF/DOCX files containing requirements
2. **Generate Epics** - AI-generated epics from uploaded requirements
3. **Generate Stories** - User stories derived from epics
4. **Generate QA** - Test cases and QA scenarios from stories
5. **RAG Retrieval** - Intelligent document search and context retrieval
6. **Confluence Integration** - Automatic page creation and linking
7. **Pagination & Sorting** - Browse large datasets efficiently
8. **Agentic Interface** - Control agents via intuitive web UI (AgenticAIPage)

**Agent System**

Each agent handles a specific task:
- **EpicAgent**: Generates epics from requirements, creates Confluence pages
- **StoryAgent**: Breaks epics into user stories
- **QAAgent**: Generates test cases from stories
- **RAGAgent**: Retrieves relevant documents via semantic search
- **AgentCoordinator**: Orchestrates agent workflows

See `AGENTIC_ARCHITECTURE.md` for detailed agent documentation.

**API Endpoints**

### Agentic Endpoints (NEW)
- `POST /agents/epic/generate` - Generate epics from upload
- `POST /agents/story/generate` - Generate stories from epic
- `POST /agents/qa/generate` - Generate QA from story
- `POST /agents/rag/search` - Retrieve documents via RAG
- `POST /agents/workflow/execute` - Execute full workflow

### Data Endpoints (with pagination & sorting)
- `GET /epics?page=1&page_size=10&sort_by=created_at&sort_order=desc`
- `GET /stories?page=1&page_size=10&sort_by=created_at&sort_order=desc`
- `GET /qa?page=1&page_size=10&sort_by=created_at&sort_order=desc`
- `GET /testplans?page=1&page_size=10&sort_by=created_at&sort_order=desc`
- `POST /upload` - Upload a requirements document

### Legacy Endpoints
- `POST /generate-epics/{upload_id}` - Traditional epic generation
- `POST /generate-stories/{epic_id}` - Traditional story generation
- `POST /generate-qa/{story_id}` - Traditional QA generation

**Testing**

Run tests after startup:
```bash
# Test backend health
curl http://localhost:8000/

# Test epic generation
curl -X POST http://localhost:8000/agents/epic/generate \
  -H "Content-Type: application/json" \
  -d '{"upload_id": 1}'

# Test RAG search
curl "http://localhost:8000/agents/rag/search?query=authentication&upload_id=1"
```

**Troubleshooting**

- **Backend won't start:** Check Python version (3.10+), virtual environment activation, and requirements installation
- **Frontend won't compile:** Ensure Node.js 18+, npm installed, and run `npm install` in frontend/
- **Database connection error:** Verify POSTGRES_URL in .env and database is running
- **Gemini API errors:** Check GEMINI_API_KEY is set correctly
- **Port conflicts:** Change port numbers in startup scripts or FastAPI calls

**Development**

For development with hot reload:
- Backend: uvicorn with `--reload` flag (auto-restarts on file changes)
- Frontend: Vite dev server (hot module replacement)

See `AGENTIC_ARCHITECTURE.md` for extending agents with new capabilities.
