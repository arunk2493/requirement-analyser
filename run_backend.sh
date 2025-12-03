#!/bin/bash

# Backend startup script for requirement-analyser

echo "Starting Requirement Analyzer Backend..."
echo "========================================"

cd "$(dirname "$0")/backend"

# Check if virtual environment exists
if [ ! -d "../.venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv ../.venv
fi

# Activate virtual environment
source ../.venv/bin/activate

# Install requirements if needed
if [ ! -z "$1" ] && [ "$1" == "--install" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Start the server
echo "Starting FastAPI server on http://localhost:8000"
echo "API docs available at http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn app:app --reload --host 0.0.0.0 --port 8000
