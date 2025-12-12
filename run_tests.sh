#!/bin/bash

# Quick start script to run unit tests with comprehensive reporting
# Usage: ./run_tests.sh [options]
# Options:
#   (no args)       Run all tests with coverage and reports
#   -v              Verbose output
#   -q              Quiet output
#   --file FILE     Run specific test file (e.g., test_auth.py)
#   --test TEST     Run specific test (e.g., TestPasswordHashing::test_hash_password)
#   --no-cov        Run without coverage report
#   --html          Generate HTML coverage report (default: always generated)
#   --ci            CI mode - generates JUnit XML and coverage reports
#   --help          Show this message

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Default options
VERBOSE="-v"
COVERAGE="--cov=. --cov-report=term-missing --cov-report=html:htmlcov"
PYTEST_ARGS=""
CI_MODE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE="-vv"
            shift
            ;;
        -q|--quiet)
            VERBOSE="-q"
            shift
            ;;
        --file)
            PYTEST_ARGS="tests/$2"
            shift 2
            ;;
        --test)
            PYTEST_ARGS="tests/ -k $2"
            shift 2
            ;;
        --no-cov)
            COVERAGE=""
            shift
            ;;
        --html)
            COVERAGE="$COVERAGE --cov-report=html"
            shift
            ;;
        --ci)
            CI_MODE=true
            COVERAGE="$COVERAGE --cov-report=xml:coverage.xml"
            shift
            ;;
        --help)
            grep "^#" "$0" | grep -v "^#!/bin/bash" | sed 's/# //'
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Check if we're in the right directory
if [ ! -d "$BACKEND_DIR/tests" ]; then
    echo -e "${RED}❌ Error: backend/tests directory not found${NC}"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Navigate to backend directory
cd "$BACKEND_DIR"

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}🧪 Running Unit Tests${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Activate virtual environment if it exists
if [ -f "../.venv/bin/activate" ]; then
    source "../.venv/bin/activate"
    echo -e "${GREEN}✅ Virtual environment activated${NC}"
    echo ""
fi

# Install test dependencies
echo -e "${YELLOW}Installing test dependencies...${NC}"
pip install -q pytest pytest-cov pytest-mock pytest-asyncio pytest-html 2>/dev/null || true

echo ""
echo -e "${BLUE}Running pytest...${NC}"
echo ""

# Build pytest command with reports
PYTEST_CMD="python -m pytest tests/ $VERBOSE $COVERAGE"

# Add JUnit XML report in CI mode or always for reports
if [ "$CI_MODE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --junit-xml=test-results.xml --html=report.html --self-contained-html"
else
    # Always generate HTML report
    PYTEST_CMD="$PYTEST_CMD --html=report.html --self-contained-html"
fi

# Add specific test args if provided
if [ -n "$PYTEST_ARGS" ]; then
    PYTEST_CMD="python -m pytest $PYTEST_ARGS $VERBOSE $COVERAGE --html=report.html --self-contained-html"
fi

# Run pytest
eval "$PYTEST_CMD"

TEST_RESULT=$?

echo ""
echo -e "${BLUE}========================================${NC}"
if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ Tests completed successfully!${NC}"
else
    echo -e "${RED}❌ Tests completed with errors${NC}"
fi
echo -e "${BLUE}========================================${NC}"
echo ""

# Display report locations
echo -e "${GREEN}📊 Reports Generated:${NC}"
echo "   📋 HTML Test Report:     report.html"
echo "   📈 HTML Coverage Report: htmlcov/index.html"

if [ "$CI_MODE" = true ] && [ -f "test-results.xml" ]; then
    echo "   📑 JUnit XML Report:     test-results.xml"
    echo "   📊 Coverage XML Report:  coverage.xml"
fi

echo ""

# Print summary if in CI mode
if [ "$CI_MODE" = true ] && [ -f "test-results.xml" ]; then
    echo -e "${BLUE}Test Summary:${NC}"
    python3 << 'PYTHON_EOF'
import xml.etree.ElementTree as ET
try:
    tree = ET.parse('test-results.xml')
    root = tree.getroot()
    
    total = int(root.get('tests', 0))
    failures = int(root.get('failures', 0))
    errors = int(root.get('errors', 0))
    skipped = int(root.get('skipped', 0))
    passed = total - failures - errors - skipped
    
    print(f"  Total Tests:  {total}")
    print(f"  ✅ Passed:    {passed}")
    print(f"  ❌ Failed:    {failures}")
    print(f"  ⚠️  Errors:    {errors}")
    print(f"  ⏭️  Skipped:   {skipped}")
    
except Exception as e:
    pass
PYTHON_EOF
    echo ""
fi

exit $TEST_RESULT
