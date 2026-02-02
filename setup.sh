#!/bin/bash

# Usage vs Revenue Analyzer - Setup Script

echo "================================"
echo "Usage vs Revenue Analyzer Setup"
echo "================================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo ""
    echo "⚠️  Please edit .env file and add your API keys:"
    echo "   - OPENAI_API_KEY"
    echo "   - STRIPE_API_KEY"
    echo ""
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the application:"
echo "  1. Activate the virtual environment: source venv/bin/activate"
echo "  2. Configure your API keys in .env file"
echo "  3. Run: python -m uvicorn app.main:app --reload"
echo "  4. Open http://localhost:8000 in your browser"
echo ""
