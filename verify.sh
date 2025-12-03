#!/bin/bash

# Verification script for reorganization
# Checks that all components are in place and working

echo "======================================"
echo "Requirement Analyzer - Verification"
echo "======================================"
echo ""

PROJECT_ROOT="/Users/arunkumaraswamy/Documents/Study/requirement-analyser"
ISSUES=0

echo "📁 Checking Directory Structure..."
echo "---"

# Check backend folders
BACKEND_FOLDERS=(
    "backend"
    "backend/agents"
    "backend/config"
    "backend/models"
    "backend/prompts"
    "backend/rag"
    "backend/routes"
)

for folder in "${BACKEND_FOLDERS[@]}"; do
    if [ -d "$PROJECT_ROOT/$folder" ]; then
        echo "✓ $folder"
    else
        echo "✗ $folder - MISSING"
        ISSUES=$((ISSUES + 1))
    fi
done

echo ""
echo "📄 Checking Key Files..."
echo "---"

KEY_FILES=(
    "backend/app.py"
    "backend/requirements.txt"
    "backend/config/db.py"
    "backend/models/file_model.py"
    "backend/agents/base_agent.py"
    "backend/agents/epic_agent.py"
    "backend/agents/story_agent.py"
    "backend/agents/qa_agent.py"
    "backend/agents/rag_agent.py"
    "backend/agents/agent_coordinator.py"
    "backend/rag/embedder.py"
    "backend/rag/vectorstore.py"
    "backend/routes/agents_router.py"
    "frontend/src/App.jsx"
    "frontend/src/components/AgenticAIPage.jsx"
    "run_backend.sh"
    "run_frontend.sh"
    "README.md"
    "DEVELOPMENT.md"
    "AGENTIC_ARCHITECTURE.md"
)

for file in "${KEY_FILES[@]}"; do
    if [ -f "$PROJECT_ROOT/$file" ]; then
        echo "✓ $file"
    else
        echo "✗ $file - MISSING"
        ISSUES=$((ISSUES + 1))
    fi
done

echo ""
echo "🔗 Checking Startup Scripts..."
echo "---"

if [ -x "$PROJECT_ROOT/run_backend.sh" ]; then
    echo "✓ run_backend.sh is executable"
else
    echo "✗ run_backend.sh is not executable"
    ISSUES=$((ISSUES + 1))
fi

if [ -x "$PROJECT_ROOT/run_frontend.sh" ]; then
    echo "✓ run_frontend.sh is executable"
else
    echo "✗ run_frontend.sh is not executable"
    ISSUES=$((ISSUES + 1))
fi

echo ""
echo "🐍 Checking Python Imports..."
echo "---"

cd "$PROJECT_ROOT/backend" || exit

python3 << 'EOF'
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

test_imports = [
    ("config.db", ["Base", "engine"]),
    ("models.file_model", ["Upload", "Epic"]),
    ("agents.base_agent", ["BaseAgent"]),
    ("agents.epic_agent", ["EpicAgent"]),
    ("agents.agent_coordinator", ["AgentCoordinator"]),
    ("rag.embedder", ["EmbeddingManager"]),
    ("rag.vectorstore", ["VectorStore"]),
    ("routes.agents_router", ["router"]),
]

all_passed = True
for module_name, items in test_imports:
    try:
        module = __import__(module_name, fromlist=items)
        for item in items:
            if hasattr(module, item):
                print(f"✓ {module_name}.{item}")
            else:
                print(f"✗ {module_name}.{item} - NOT FOUND")
                all_passed = False
    except Exception as e:
        print(f"✗ {module_name} - {str(e)[:50]}")
        all_passed = False

sys.exit(0 if all_passed else 1)
EOF

IMPORT_RESULT=$?
if [ $IMPORT_RESULT -ne 0 ]; then
    ISSUES=$((ISSUES + 1))
fi

echo ""
echo "📋 Checking Documentation..."
echo "---"

DOCS=(
    "README.md"
    "DEVELOPMENT.md"
    "AGENTIC_ARCHITECTURE.md"
    "REORGANIZATION.md"
)

for doc in "${DOCS[@]}"; do
    if [ -f "$PROJECT_ROOT/$doc" ]; then
        LINES=$(wc -l < "$PROJECT_ROOT/$doc")
        echo "✓ $doc ($LINES lines)"
    else
        echo "✗ $doc - MISSING"
        ISSUES=$((ISSUES + 1))
    fi
done

echo ""
echo "======================================"
echo "Summary"
echo "======================================"

if [ $ISSUES -eq 0 ]; then
    echo "✓ All checks passed!"
    echo ""
    echo "Next steps:"
    echo "  1. ./run_backend.sh    (Terminal 1)"
    echo "  2. ./run_frontend.sh   (Terminal 2)"
    echo ""
    echo "Then visit:"
    echo "  - Frontend: http://localhost:5173"
    echo "  - API Docs: http://localhost:8000/docs"
else
    echo "✗ Found $ISSUES issue(s)"
    echo ""
    echo "Please review the errors above and fix them."
fi

echo ""
