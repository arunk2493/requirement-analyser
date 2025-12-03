#!/bin/bash

# Frontend startup script for requirement-analyser

echo "Starting Requirement Analyzer Frontend..."
echo "=========================================="

cd "$(dirname "$0")/frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Dependencies not found. Installing..."
    npm install
fi

# Start the development server
echo "Starting Vite development server on http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

npm run dev
