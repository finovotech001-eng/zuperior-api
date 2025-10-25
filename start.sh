#!/bin/bash

echo "Starting CRM API Server..."
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Change to app directory
cd app

# Start the server
echo "Starting FastAPI server on http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo ""
python main.py

