#!/bin/bash

echo "🚀 Starting Document QA API..."

# Always run from the script's directory so relative paths work after renames
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Ensure virtual environment Python exists
if [ ! -x "venv/bin/python" ]; then
    echo "❌ Error: virtual environment Python not found at $SCRIPT_DIR/venv/bin/python"
    echo "Run ./setup.sh first to create it."
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create a .env file with your OpenAI API key."
    exit 1
fi

# Run the application using venv Python explicitly
exec "$SCRIPT_DIR/venv/bin/python" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload