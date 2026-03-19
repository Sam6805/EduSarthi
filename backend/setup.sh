#!/bin/bash
# Quick start script for Education Tutor Backend

set -e

echo "======================================"
echo "📚 Education Tutor Backend Setup"
echo "======================================"
echo ""

# Check Python
echo "✓ Checking Python..."
python --version || { echo "Python 3.8+ required"; exit 1; }

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "✓ Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "✓ Activating virtual environment..."
if [ -f "venv/Scripts/activate" ]; then
    # Windows
    source venv/Scripts/activate
else
    # Linux/Mac
    source venv/bin/activate
fi

# Install dependencies
echo "✓ Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "======================================"
echo "✅ Setup Complete!"
echo "======================================"
echo ""
echo "To start the server, run:"
echo "  python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "API will be available at:"
echo "  http://localhost:8000"
echo ""
echo "Documentation:"
echo "  http://localhost:8000/docs"
echo ""
echo "To run tests:"
echo "  python tests/test_api.py"
echo ""
echo "To run evaluation:"
echo "  python experiments/baseline_vs_pruned.py"
echo ""
