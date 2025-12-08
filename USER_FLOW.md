# User Flow Documentation

## Overview
This document describes the complete user journey through the Requirement Analyzer application, including all major features and workflows.

---

## 1. Authentication Flow

### 1.1 Initial Access
```
User visits application
         ↓
Is user logged in? (Check localStorage token)
         ↓
    No → Show Login Page
    Yes → Show Dashboard
```

### 1.2 Login Process
```
User enters email and password
         ↓
Click "Login" button
         ↓
Validate credentials with backend
         ↓
Success? 
    Yes → Store token & email in localStorage → Redirect to Dashboard
    No → Show error message → Remain on login page
```

### 1.3 Logout Process
```
User clicks "Logout" button (in sidebar)
         ↓
Clear authentication tokens from localStorage
         ↓
Reset application state
         ↓
Redirect to Login Page
```

---

## 2. Main Application Flow

### 2.1 Sidebar Navigation
```
Collapsed State (w-20):
  - Only icons visible
  - Hover shows tooltips on right side
  - All navigation items available
  
Expanded State (w-72):
  - Icons + Labels visible
  - Sidebar title and subtitle visible
  - Full user information display
  - Collapse button toggles between states
```

### 2.2 Navigation Menu
```
Dashboard
├── Home page with overview
└── Quick access to recent items

Upload
├── Select file to upload
├── Upload to server
└── Create upload record

Agentic AI
├── Select upload
├── Generate Epics
├── Generate Stories
├── Generate QA
└── Generate Test Plans

Epics
├── View all epics for selected upload
└── Display epic details

Stories
├── View all stories for selected upload
└── Display story details

QA
├── View all QA items for selected upload
└── Display QA details

Test Plans
├── View all test plans for selected upload
└── Display test plan details

Search Documents ⭐ (NEW)
├── Enter search query
├── Search across vectorstore + database
└── View results with metadata

History
└── View confluence export history
```

---

## 3. Upload & Generation Workflow

### 3.1 File Upload Process
```
User navigates to "/upload"
         ↓
Select file from local system
         ↓
Click "Upload" button
         ↓
File sent to backend
         ↓
Backend processes file:
  - Create Upload record in database
  - Extract text from document
  - Generate embeddings using SentenceTransformer
  - Store vectors in vectorstore JSON files
         ↓
Success response
         ↓
Upload ID returned & stored
         ↓
User can now generate Epics/Stories/QA/Test Plans from this upload
```

### 3.2 Epic Generation Workflow
```
User navigates to "/agentic-ai"
         ↓
Select upload from dropdown
         ↓
Click "Generate Epics"
         ↓
Backend Flow:
  1. Retrieve upload document from storage
  2. Call EpicAgent with document content
  3. EpicAgent:
     - Uses Gemini LLM for analysis
     - Extracts epics from requirements
     - Structures with name, description, confluence_page_id
  4. Store generated epics in Epic table
         ↓
Frontend displays generated epics in table
         ↓
User can view epic details
```

### 3.3 Story Generation Workflow
```
User selects epic from Epics page
         ↓
System retrieves epic ID
         ↓
User clicks "Generate Stories for this Epic"
         ↓
Backend Flow:
  1. Retrieve epic content from database
  2. Call StoryAgent with epic data
  3. StoryAgent:
     - Uses Gemini LLM for story generation
     - Creates user stories from epic
     - Structures with title, description, acceptance criteria
  4. Store generated stories linked to epic_id
         ↓
Frontend displays stories in table
         ↓
User can view story details
```

### 3.4 QA/Test Plan Generation Workflow
```
User selects story/epic
         ↓
Click "Generate QA" or "Generate Test Plans"
         ↓
Backend Flow:
  1. Retrieve story/epic content
  2. Call QAAgent or TestPlanAgent
  3. Agent:
     - Uses Gemini LLM for generation
     - Creates test cases or test plans
     - Structures with test cases, objectives, etc.
  4. Store in QA table (type = 'qa' or 'test_plan')
         ↓
Frontend displays results in table
         ↓
User can view details and export
```

---

## 3.5 Agent Coordinator Architecture & Usage

### Overview
The **AgentCoordinator** is a centralized orchestrator that manages all agent operations and workflows. It coordinates between multiple specialized agents (EpicAgent, StoryAgent, QAAgent, TestPlanAgent, RAGAgent) to execute comprehensive requirement analysis pipelines.

### 3.5.1 Agent Coordinator Components

```
AgentCoordinator (Central Orchestrator)
├── Initialization
│   ├── Initialize all agents on startup
│   ├── Set up database connections
│   ├── Configure logging
│   └── Setup error handling
│
├── Agent Management
│   ├── EpicAgent - Generates epics from documents
│   ├── StoryAgent - Generates stories from epics
│   ├── QAAgent - Generates QA items from stories
│   ├── TestPlanAgent - Generates test plans from stories
│   ├── RAGAgent - Retrieves relevant documents via semantic search
│   └── BaseAgent - Provides common functionality to all agents
│
├── Workflow Execution
│   ├── Single agent workflow (one agent at a time)
│   ├── Sequential workflow (one after another)
│   └── Parallel workflow (multiple agents)
│
├── Error Handling & Logging
│   ├── Execution error tracking
│   ├── Retry mechanisms
│   ├── Detailed logging for debugging
│   └── Graceful degradation on failures
│
└── Response Management
    ├── Structured response formatting
    ├── Result aggregation
    ├── Status tracking
    └── Metadata enrichment
```

### 3.5.2 Agent Workflow Execution

#### Single Agent Execution
```
Frontend Request (e.g., Generate Epics)
         ↓
AgentCoordinator receives request
         ↓
Identify required agent (EpicAgent)
         ↓
Set up execution context:
  - Load upload document
  - Prepare input data
  - Initialize agent with context
         ↓
EpicAgent.execute()
  ├── Log execution start
  ├── Call Gemini LLM with prompt
  ├── Parse LLM response
  ├── Validate output structure
  ├── Create database records
  └── Log execution end
         ↓
AgentCoordinator formats response
         ↓
Return structured result to frontend
         ↓
Frontend displays generated epics
```

#### Sequential Workflow (Optional Multi-Step)
```
User initiates workflow: Upload → Epics → Stories → QA
         ↓
AgentCoordinator.execute_workflow(upload_id)
         ↓
Step 1: Generate Epics
  └── EpicAgent generates epics from document
         ↓
Step 2: Generate Stories
  └── StoryAgent generates stories for each epic
         ↓
Step 3: Generate QA
  └── QAAgent generates QA items for each story
         ↓
Step 4: Generate Test Plans
  └── TestPlanAgent generates test plans for each story
         ↓
Collect results from all steps
         ↓
Return aggregated results to frontend
         ↓
Frontend displays complete workflow results
```

### 3.5.3 Agent Coordinator API Methods

```
1. generate_epics(upload_id)
   └── Coordinates EpicAgent to generate epics
   
2. generate_stories(epic_id, upload_id)
   └── Coordinates StoryAgent to generate stories
   
3. generate_qa(epic_id, story_id, upload_id)
   └── Coordinates QAAgent to generate QA items
   
4. generate_test_plans(epic_id, story_id, upload_id)
   └── Coordinates TestPlanAgent to generate test plans
   
5. retrieve_documents(query, upload_id, top_k)
   └── Coordinates RAGAgent for semantic search
   
6. execute_workflow(upload_id)
   └── Executes complete pipeline: Epics → Stories → QA → Test Plans
   
7. get_epics(upload_id, user_id)
   └── Retrieves generated epics for an upload
   
8. get_stories(epic_id, user_id)
   └── Retrieves generated stories for an epic
   
9. get_qa(upload_id, user_id)
   └── Retrieves generated QA items
   
10. get_test_plans(upload_id, user_id)
    └── Retrieves generated test plans
```

### 3.5.4 Agent Coordinator in Agentic AI Page

```
User opens "/agentic-ai"
         ↓
Page initializes AgentCoordinator via API
         ↓
User selects upload from dropdown
         ↓
Available actions:
  ├── Generate Epics → coordinator.generate_epics(upload_id)
  ├── Generate Stories → coordinator.generate_stories(epic_id, upload_id)
  ├── Generate QA → coordinator.generate_qa(epic_id, story_id, upload_id)
  ├── Generate Test Plans → coordinator.generate_test_plans(epic_id, story_id, upload_id)
  └── Execute Full Workflow → coordinator.execute_workflow(upload_id)
         ↓
User clicks action button
         ↓
Request sent to AgentCoordinator endpoint
         ↓
Coordinator orchestrates agent execution
         ↓
Backend processes with selected agent
         ↓
Results stored in database
         ↓
Response returned to frontend
         ↓
Frontend displays results
         ↓
User can now:
  ├── View generated content in respective pages
  ├── Generate next level artifacts
  └── Search across generated content
```

### 3.5.5 Agent Coordinator with RAGAgent

```
User navigates to "/search-documents"
         ↓
User enters search query and clicks search
         ↓
Frontend calls ragVectorStoreSearch API
         ↓
Backend routes to AgentCoordinator.retrieve_documents()
         ↓
AgentCoordinator initializes RAGAgent
         ↓
RAGAgent.execute(query):
  ├── Encode query using SentenceTransformer
  ├── Search vectorstore JSON files:
  │   ├── Load all vectorstore files
  │   ├── Calculate similarity for each document
  │   └── Collect results
  ├── Search database:
  │   ├── Query Epic table
  │   ├── Query QA table (type='test_plan')
  │   ├── Calculate similarity for each record
  │   └── Collect results
  ├── Combine all results
  ├── Filter by 30% relevance threshold
  ├── Remove acceptanceCriteria text
  ├── Sort by similarity score
  └── Return top 10 results
         ↓
AgentCoordinator formats response with:
  ├── Search results array
  ├── Metadata for each result
  ├── Source attribution
  ├── Similarity scores
  └── Confluence links (if available)
         ↓
Response returned to frontend
         ↓
Frontend displays results with:
  ├── Source badges (Retrieval: Vectorstore/Database)
  ├── Horizontal metadata layout
  ├── Color-coded similarity
  └── Clickable Confluence links
         ↓
User can:
  ├── Modify query and search again
  ├── Click links to view source documents
  ├── Click "Clear" to reset
  └── Download or export results
```

### 3.5.6 Error Handling in Agent Coordinator

```
Error occurs during agent execution:
         ↓
Agent catches exception
         ↓
Log error with context:
  ├── Agent name
  ├── Operation type
  ├── Input parameters
  ├── Error message
  ├── Stack trace
  └── Timestamp
         ↓
Coordinator evaluates error type:
  ├── Retryable error → Attempt retry (max 3 times)
  ├── Validation error → Return user-friendly message
  ├── LLM error → Try alternative prompt or fail gracefully
  └── System error → Log and return generic error response
         ↓
If retry exhausted or non-retryable:
  ├── Format error response
  ├── Return to frontend with error details
  └── Log for debugging
         ↓
Frontend displays error message:
  ├── User-friendly message
  ├── Suggestion to retry
  └── Contact support if persistent
```

### 3.5.7 Agent Coordinator State Management

```
AgentCoordinator maintains:
  ├── Execution history (for logging)
  ├── Agent instances (initialized once)
  ├── Database connections (reused)
  ├── Configuration settings
  ├── Error tracking
  └── Performance metrics
         ↓
Per-request context:
  ├── Upload ID
  ├── User ID (for authorization)
  ├── Agent being executed
  ├── Start time
  ├── Status (pending/executing/completed/failed)
  └── Results (once completed)
```

---

## 4. Search Documents Workflow ⭐ (NEW)

### 4.1 Search Initiation
```
User navigates to "/search-documents"
         ↓
Sees search card with input field
         ↓
Enters search query (e.g., "camera requirements")
         ↓
Presses Enter or clicks "Search Documents"
         ↓
Button becomes disabled with loading spinner
```

### 4.2 Dual-Source Search Execution
```
Backend receives query
         ↓
┌─────────────────────────────────────────┐
│ Parallel Search (Two Sources)           │
├─────────────────────────────────────────┤
│ 1. Vectorstore Search:                  │
│    - Load vectorstore*.json files       │
│    - Encode query with SentenceTransformer
│    - Calculate cosine similarity        │
│    - Return top results                 │
│                                         │
│ 2. Database Search:                     │
│    - Query Epic table                   │
│    - Query QA table (type='test_plan')  │
│    - Encode content with embeddings     │
│    - Calculate cosine similarity        │
│    - Return top results                 │
└─────────────────────────────────────────┘
         ↓
Combine results from both sources
         ↓
Filter by relevance threshold (≥30%)
         ↓
Remove acceptanceCriteria text
         ↓
Filter empty results after cleaning
         ↓
Sort by similarity_percentage (descending)
         ↓
Limit to top 10 results
```

### 4.3 Results Display & Filtering
```
Results returned with:
  - Source badge:
    • "Retrieval: Vectorstore" (blue)
    • "Retrieval: Database" (purple)
  - Display name based on type
  - Similarity percentage color-coded:
    • Green (>70%) = High match
    • Yellow (50-70%) = Medium match
    • Red (<50%) = Low match
  - Preview text (first 400 chars)
  - Metadata in horizontal layout:
    • For Vectorstore: File, Upload ID, Type
    • For Epics: Epic ID, Upload ID, Confluence Link
    • For Test Plans: Test Plan ID, Epic ID, Confluence Link
         ↓
User can:
  ├── Scroll through results
  ├── Click Confluence links (if available)
  ├── Modify search query
  └── Click "Clear" to reset everything
```

### 4.4 No Results Scenarios
```
Scenario 1: Irrelevant Query
  - User searches for query with <30% relevance
  - Shows: "No matching documents found. Try a different search query."
  
Scenario 2: Before Search Clicked
  - User types query but hasn't clicked search
  - Shows: Only search card, no empty state message
  
Scenario 3: After Clear Button
  - User clicks "Clear" button
  - State resets: query cleared, results removed, messages cleared
  - UI returns to initial state
```

---

## 5. Data Flow Architecture

### 5.1 Upload & Embedding Storage
```
User File
    ↓
Backend Upload Handler
    ├── Create Upload record in DB
    ├── Extract text
    └── Generate embeddings (SentenceTransformer: all-MiniLM-L6-v2)
    ↓
Store embeddings in vectorstore JSON:
    storage/vectorstore_upload_{ID}.json
    {
      "doc_key": {
        "text": "...",
        "embedding": [...],
        "metadata": {...}
      }
    }
```

### 5.2 Database Schema
```
Uploads Table:
  - id (PK)
  - user_id (FK)
  - filename
  - upload_date
  - created_at

Epics Table:
  - id (PK)
  - upload_id (FK)
  - name
  - content (JSON)
  - confluence_page_id
  - created_at

QA Table:
  - id (PK)
  - epic_id (FK)
  - type (epic|story|qa|test_plan)
  - content (JSON)
  - confluence_page_id
  - created_at
```

### 5.3 Search Data Sources
```
Vectorstore JSON Files
├── Documents uploaded by users
├── Text + Embeddings stored
└── Queried via semantic similarity

Database Records
├── Generated Epics
├── Generated Test Plans (QA with type='test_plan')
└── Queried via semantic similarity
```

---

## 6. User Interface Sections

### 6.1 Sidebar Components
```
Header (Expanded):
  - Logo: 🚀 Analyzer
  - Subtitle: Requirement Analysis Tool
  - Collapse button (left arrow)

Header (Collapsed):
  - Just collapse button
  - Shows tooltip on hover

Navigation:
  - 9 menu items with icons
  - Active state: Blue gradient background
  - Tooltips on hover (collapsed mode)

User Section:
  - User profile card (expanded)
    • User circle icon
    • "Logged in as" label
    • Email address (bold white)
  - Logout button (always visible)
    • Red background, hover darker red
    • Shows tooltip when collapsed

Transitions:
  - 300ms smooth width animation
  - Opacity-based tooltip fading
  - Responsive padding adjustments
```

### 6.2 Search Documents Page
```
Header:
  - Title: 🔍 Search Documents
  - Subtitle: Description

Messages (Conditional):
  - Error: Red background, red text, visible 4 seconds
  - Success: Green background, green text, visible 4 seconds

Search Card:
  - Input field with placeholder
  - Two buttons:
    • Search Documents (orange, flex-1)
    • Clear (gray, min-width)
  - Help text with info icon

Results Section (if found):
  - Heading: "Top {count} Search Results"
  - Result cards:
    • Result number and display name
    • Source badge (blue/purple)
    • Similarity percentage (color-coded)
    • Preview text (first 400 chars)
    • Metadata in horizontal single-row layout

Empty State (after search, no results):
  - Message: "No results found for '{query}'"
  - Encourages trying different query
```

---

## 7. Feature Highlights

### 7.1 Search Features
- ✅ Dual-source search (vectorstore + database)
- ✅ Semantic similarity using SentenceTransformer
- ✅ 30% relevance threshold filtering
- ✅ acceptanceCriteria text removal
- ✅ Horizontal metadata layout
- ✅ Confluence link integration (clickable)
- ✅ Source attribution (Retrieval: Vectorstore vs Database)
- ✅ Clear button to reset search
- ✅ Responsive design
- ✅ Dark mode support

### 7.2 Sidebar Features
- ✅ Collapse/Expand toggle
- ✅ Smooth animations
- ✅ Tooltips on all icons (collapsed mode)
- ✅ White bold user email display
- ✅ User circle icon for profile
- ✅ Clean, professional design
- ✅ Dark mode support

### 7.3 Generation Features
- ✅ AI-powered epic generation
- ✅ AI-powered story generation
- ✅ AI-powered QA generation
- ✅ AI-powered test plan generation
- ✅ Recent items tracking
- ✅ Confluence export capability

---

## 8. User Journey Examples

### Example 1: Complete Workflow
```
1. Login → Dashboard
2. Upload requirements document
3. Generate Epics from upload
4. Generate Stories from epic
5. Generate Test Plans from story
6. Search for specific requirements using "Search Documents"
7. Export results to Confluence
8. Logout
```

### Example 2: Quick Search
```
1. Login → Dashboard
2. Click "Search Documents" in sidebar
3. Enter search query (e.g., "API authentication")
4. View results from both vectorstore and database
5. Click on Confluence links to view original documents
6. Modify query and search again
7. Click "Clear" to start fresh
```

### Example 3: Explore Generated Content
```
1. Login → Dashboard
2. Navigate to "Epics" to view all generated epics
3. Click on an epic to see details
4. Navigate to "Stories" to view stories for that epic
5. Navigate to "Test Plans" to view test plans
6. Navigate to "Search Documents" to find related content
7. Compare and correlate information across sources
```

---

## 9. Error Handling

### Frontend Error Scenarios
```
1. Network Error:
   - Show error message: "Failed to search documents. Please try again."
   - Message auto-clears after 4 seconds
   
2. Empty Search Query:
   - Show error: "Please enter a search query"
   - Search button remains disabled until text entered
   
3. No Relevant Results:
   - Show error: "No matching documents found. Try a different search query."
   - Only shown after search is performed
   
4. Authentication Expired:
   - Redirect to Login Page
   - Clear stored tokens
```

### Backend Error Handling
```
1. Upload Processing Error:
   - Log error with details
   - Show user-friendly error message
   
2. LLM Generation Error:
   - Retry with exponential backoff
   - Show error if max retries exceeded
   
3. Search Execution Error:
   - Return partial results if one source fails
   - Log errors for debugging
```

---

## 10. Performance Optimizations

### Frontend Optimizations
- ✅ Lazy loading of components
- ✅ Smooth transitions with CSS animations
- ✅ Efficient state management with React hooks
- ✅ Memoization of expensive operations
- ✅ Responsive design for all screen sizes

### Backend Optimizations
- ✅ Parallel search execution (vectorstore + database)
- ✅ Efficient embedding generation
- ✅ Indexed database queries
- ✅ Filtered results before returning
- ✅ Similarity threshold to reduce false positives

---

## 11. Accessibility Features

- ✅ Semantic HTML structure
- ✅ ARIA labels and roles
- ✅ Keyboard navigation (Enter key for search)
- ✅ Color-coded similarity indicators
- ✅ Tooltips for all icons
- ✅ Clear visual hierarchy
- ✅ Dark mode support
- ✅ Responsive design for mobile

---

## Summary

The Requirement Analyzer application provides a comprehensive workflow for:
1. **Managing Requirements** - Upload, organize, and track documents
2. **Generating Artifacts** - Use AI to create epics, stories, QA, and test plans
3. **Searching Intelligently** - Find relevant content across multiple sources using semantic similarity
4. **Exporting & Sharing** - Export to Confluence and collaborate with teams

The dual-source search capability and intuitive UI make it easy for users to discover and correlate information across their entire requirements repository.
