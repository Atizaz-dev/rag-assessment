#!/bin/bash

echo "🚀 Setting up Document QA API..."

# Check if Python 3.11 is installed
if ! command -v python3.11 &> /dev/null; then
    echo "❌ Python 3.11 not found. Installing..."
    sudo apt update
    sudo apt install python3.11 python3.11-venv python3-pip -y
fi

# Install system dependencies
echo "📦 Installing system dependencies..."
sudo apt install build-essential libpoppler-cpp-dev pkg-config python3-dev -y

# Create virtual environment
echo "🐍 Creating virtual environment..."
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/documents
mkdir -p data/vector_store
mkdir -p app/static

# Create __init__.py files
echo "📄 Creating __init__.py files..."
touch app/__init__.py
touch app/models/__init__.py
touch app/services/__init__.py
touch app/api/__init__.py
touch app/api/routes/__init__.py
touch app/utils/__init__.py
touch tests/__init__.py

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Please create one with your OpenAI API key."
    echo "Example .env file has been created. Please update it with your credentials."
else
    echo "✅ .env file found"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Update .env file with your OpenAI API key"
echo "2. Run the application with: ./run.sh"
echo "   Or manually: source venv/bin/activate && python -m uvicorn app.main:app --reload"
echo ""
echo "🌐 The API will be available at: http://localhost:8000"
echo "📖 API documentation: http://localhost:8000/docs"
echo ""