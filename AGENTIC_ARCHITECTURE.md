# Agentic AI Architecture - Requirement Analyzer

## Overview

The system has been converted to an **agentic AI architecture** where specialized agents handle different responsibilities in the requirement analysis workflow. Each agent is independent, focused, and communicates through standardized interfaces.

## Architecture Components

### Backend Structure

```
/agents/
├── __init__.py              # Agent module exports
├── base_agent.py            # BaseAgent abstract class
├── epic_agent.py            # EpicAgent - Generates epics from requirements
├── story_agent.py           # StoryAgent - Generates stories from epics
├── qa_agent.py              # QAAgent - Generates QA test cases from stories
├── rag_agent.py             # RAGAgent - Retrieves documents from RAG system
└── agent_coordinator.py     # AgentCoordinator - Orchestrates agents

/routes/
├── agents_router.py         # REST endpoints for agents
├── ... (existing routes)

/config/
├── gemini.py                # LLM integration (Gemini)
├── db.py                    # Database configuration

/models/
├── file_model.py            # SQLAlchemy models (Upload, Epic, Story, QA)

/rag/
├── embedder.py              # Embedding generation
├── vectorstore.py           # Vector database operations
```

### Frontend Structure

```
/frontend/src/
├── components/
│   ├── AgenticAIPage.jsx    # Main agentic interface (NEW)
│   ├── UploadPage.jsx
│   ├── EpicsPage.jsx
│   ├── StoriesPage.jsx
│   ├── QAPage.jsx
│   ├── TestPlansPage.jsx
│   ├── Dashboard.jsx
│   ├── GenerateConfluence.jsx
│   └── Sidebar.jsx          # Updated with agentic AI link

├── api/
│   └── api.js               # API helpers

└── App.jsx                  # Updated with new route
```

## Agent Details

### 1. **BaseAgent** (Abstract Base Class)
- Provides standard interface for all agents
- Handles logging and response formatting
- Returns `AgentResponse` objects with standardized format

**Response Format:**
```python
{
    "success": bool,
    "data": Any,
    "message": str,
    "agent_name": str,
    "timestamp": str,
    "error": Optional[str]
}
```

### 2. **EpicAgent**
- **Responsibility:** Generate epics from uploaded requirements
- **Input:** `upload_id` (int)
- **Output:** List of epics with Confluence page URLs
- **Process:**
  1. Retrieves uploaded requirement text from database
  2. Uses Gemini to generate structured epics (JSON format)
  3. Creates Confluence pages for upload folder and each epic
  4. Stores epic data in database with Confluence page IDs
  5. Returns epic list with generated IDs and Confluence links

### 3. **StoryAgent**
- **Responsibility:** Generate user stories from an epic
- **Input:** `epic_id` (int)
- **Output:** List of stories with content and IDs
- **Process:**
  1. Retrieves epic content from database
  2. Uses Gemini to break down epic into user stories
  3. Parses response (handles dict/list formats)
  4. Stores stories in database
  5. Returns story list

### 4. **QAAgent**
- **Responsibility:** Generate QA/test cases from a story
- **Input:** `story_id` (int)
- **Output:** List of QA test cases with details
- **Process:**
  1. Retrieves story content from database
  2. Uses Gemini to generate structured QA test cases
  3. Parses JSON response with safety mechanisms
  4. Stores QA tests in database
  5. Returns QA test list

### 5. **RAGAgent**
- **Responsibility:** Retrieve relevant documents from RAG system
- **Input:** 
  - `query` (str): Search query
  - `upload_id` (Optional[int]): Filter by specific upload
  - `top_k` (int): Number of results (default: 5)
- **Output:** List of relevant documents with similarity scores
- **Process:**
  1. Generates embedding for the search query
  2. Searches vectorstore for similar documents
  3. Optionally filters by upload_id
  4. Returns formatted results with similarity scores

### 6. **AgentCoordinator**
- **Responsibility:** Orchestrate multiple agents in a workflow
- **Methods:**
  - `generate_epics(upload_id)` - Trigger EpicAgent
  - `generate_stories(epic_id)` - Trigger StoryAgent
  - `generate_qa(story_id)` - Trigger QAAgent
  - `retrieve_documents(query, upload_id, top_k)` - Trigger RAGAgent
  - `execute_workflow(upload_id)` - Execute full workflow:
    - Generate epics for upload
    - Generate stories for all epics
    - Generate QA for first 5 stories

## API Endpoints

### Agent Endpoints (NEW)

```
POST /agents/epic/generate
{
  "upload_id": int
}
Response: { message, data: { epics: [...] } }

POST /agents/story/generate
{
  "epic_id": int
}
Response: { message, data: { stories: [...] } }

POST /agents/qa/generate
{
  "story_id": int
}
Response: { message, data: { qa_tests: [...] } }

POST /agents/rag/search
{
  "query": str,
  "upload_id": Optional[int],
  "top_k": int
}
Response: { message, data: { documents: [...] } }

POST /agents/workflow/execute
{
  "upload_id": int
}
Response: { message, data: { success, epics, stories, qa, errors } }
```

## Frontend Interface (AgenticAIPage)

Built with **PrimeReact** components, organized in tabs:

### Tabs:
1. **Generate Epics**
   - Input: Upload ID (InputNumber)
   - Action: Generate Epics button
   - Output: DataTable with generated epics

2. **Generate Stories**
   - Input: Epic ID (InputNumber)
   - Action: Generate Stories button
   - Output: DataTable with generated stories

3. **Generate QA**
   - Input: Story ID (InputNumber)
   - Action: Generate QA Tests button
   - Output: DataTable with QA tests

4. **RAG Search**
   - Input: Search query (InputText) + Upload ID (optional)
   - Action: Search Documents button
   - Output: List of retrieved documents with similarity scores

5. **Full Workflow**
   - Input: Upload ID (InputNumber)
   - Action: Execute Full Workflow button
   - Output: Combined results from all agents

### UI Features:
- Toast notifications for success/error feedback
- Loading states with progress spinner
- DataTable for structured results
- Card-based layout for organization
- PrimeReact components for consistency
- Dark mode support

## Workflow Execution

### Standard Workflow (Agent Coordinator):
1. **Upload File** → triggers file upload endpoint
2. **Generate Epics** → EpicAgent processes requirements
3. **Generate Stories** → StoryAgent breaks down epics
4. **Generate QA** → QAAgent creates test cases
5. **Retrieve Context** → RAGAgent searches for related documents

### Full Automation Workflow:
```
POST /agents/workflow/execute
↓
EpicAgent generates epics from upload
↓
For each epic: StoryAgent generates stories
↓
For first 5 stories: QAAgent generates QA tests
↓
Return combined results
```

## Data Flow

```
User Upload
    ↓
EpicAgent → generates structured epics, creates Confluence pages
    ↓
  [Epic IDs]
    ↓
StoryAgent → breaks epics into user stories
    ↓
  [Story IDs]
    ↓
QAAgent → generates test cases
    ↓
RAGAgent → retrieves supporting documents
    ↓
Frontend displays all results
```

## Database Models

All agents interact with these models:

- **Upload:** Original requirement files
- **Epic:** Generated epics with Confluence page IDs
- **Story:** Generated user stories linked to epics
- **QA:** Test cases and QA tests linked to stories

## Error Handling

Each agent implements:
- Try-catch error handling
- Logging at info/error levels
- Standardized error responses
- Graceful failure modes

## CORS Configuration

Already enabled globally in `app.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", ...],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Getting Started

### Prerequisites:
- Python 3.8+
- Node.js 16+
- Gemini API key
- Confluence credentials
- PostgreSQL or SQLite

### Setup:

**Backend:**
```bash
cd /path/to/requirement-analyser
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py  # Runs on http://localhost:8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev  # Runs on http://localhost:5173 or 5174
```

### Usage:

1. Upload a requirements document via the Upload page
2. Navigate to "Agentic AI" section
3. Use individual agents or full workflow to generate artifacts
4. View results in organized DataTables and cards
5. Access Confluence links directly from results

## Configuration

All agent configurations (prompts, LLM models, RAG settings) can be customized in:
- `/config/gemini.py` - LLM settings
- `/prompts/` - Prompt templates
- `/agents/` - Agent-specific settings
- `/rag/` - Vector store configuration

## Future Enhancements

- [ ] Agent feedback loops and refinement
- [ ] Multi-turn conversation agents
- [ ] Custom agent creation interface
- [ ] Agent performance metrics and monitoring
- [ ] Distributed agent execution
- [ ] Agent communication and collaboration
- [ ] Advanced RAG with multi-modal retrieval
- [ ] Custom prompt templates per agent
