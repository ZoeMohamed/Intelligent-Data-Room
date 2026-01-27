#!/bin/bash

# Start Flask API Server
# Usage: ./start_api.sh

echo "🚀 Starting Flask API Server..."
echo "================================"
echo ""
echo "Make sure you have:"
echo "  ✅ Activated virtual environment"
echo "  ✅ Installed dependencies (pip install -r requirements.txt)"
echo "  ✅ Set GEMINI_API_KEY in .env file"
echo ""
echo "================================"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "   Run: cp .env.example .env"
    echo "   Then add your GEMINI_API_KEY"
    exit 1
fi

# Start the API
echo "Starting API on http://localhost:5000"
echo ""
echo "Available endpoints:"
echo "  GET  /health           - Health check"
echo "  GET  /api/models       - List models"
echo "  POST /api/upload       - Upload data file"
echo "  POST /api/query        - Process query"
echo "  POST /api/memory/clear - Clear memory"
echo "  GET  /api/memory       - Get memory"
echo ""
echo "Press Ctrl+C to stop"
echo "================================"
echo ""

# Run with Flask development server (for testing)
if [ "$1" == "--dev" ]; then
    echo "Running in development mode..."
    python api.py
else
    # Run with Gunicorn (production-like)
    echo "Running with Gunicorn (production mode)..."
    gunicorn api:app --bind 0.0.0.0:5000 --workers 2 --timeout 120 --reload
fi
