#!/bin/bash

echo "🚀 Setting up Tally Bridge Component"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install Python dependencies
echo "Installing Python dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd tally_bridge/frontend
npm install
cd ../..

echo "✅ Setup complete!"
echo ""
echo "To run in development mode (use 2 terminals):"
echo ""
echo "Terminal 1 (Frontend):"
echo "cd tally_bridge/frontend && npm run dev"
echo ""
echo "Terminal 2 (Streamlit):"
echo "source venv/bin/activate && streamlit run demo_app.py"
echo ""
echo "Then open http://localhost:8501 in your browser"