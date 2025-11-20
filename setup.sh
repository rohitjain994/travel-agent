#!/bin/bash

# Setup script for Travel Agent Chatbot

echo "🚀 Setting up Travel Agent Chatbot..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating template..."
    echo "GEMINI_API_KEY=your_gemini_api_key_here" > .env
    echo "📝 Please edit .env and add your Gemini API key"
    echo "   Get your API key from: https://makersuite.google.com/app/apikey"
else
    echo "✅ .env file found"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run the application:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Add your GEMINI_API_KEY to .env file"
echo "  3. Run: streamlit run app.py"
echo ""

