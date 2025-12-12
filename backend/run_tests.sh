#!/bin/bash
# Script to run tests with coverage report

cd "$(dirname "$0")" || exit 1

echo "=========================================="
echo "Running Backend Unit Tests with Coverage"
echo "=========================================="

# Install test dependencies if not already installed
echo "Installing test dependencies..."
pip install pytest pytest-cov pytest-mock -q

echo ""
echo "Running tests with coverage..."
echo ""

# Run pytest with coverage
python -m pytest \
    --cov=backend \
    --cov-report=html \
    --cov-report=term-missing \
    --cov-report=json \
    -v \
    tests/

echo ""
echo "=========================================="
echo "Test run completed!"
echo "=========================================="
echo ""
echo "Coverage reports generated:"
echo "  - HTML Report: backend/htmlcov/index.html"
echo "  - JSON Report: backend/.coverage"
echo "  - Terminal: Above"
echo ""
