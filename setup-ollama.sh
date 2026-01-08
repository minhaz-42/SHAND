#!/bin/bash

# SHAND LLM Setup Script
# Sets up local LLM model support using Ollama

echo "🚀 SHAND LLM Setup"
echo "=================="
echo ""

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not found!"
    echo ""
    echo "Install Ollama from: https://ollama.ai"
    echo ""
    echo "Or on macOS:"
    echo "  brew install ollama"
    exit 1
fi

echo "✅ Ollama found: $(ollama --version)"
echo ""

# Check if model exists
echo "📦 Checking for Mistral model..."
if ! ollama list 2>/dev/null | grep -q "mistral"; then
    echo "⬇️  Downloading Mistral 7B (4.1GB)..."
    echo "   This may take a few minutes..."
    ollama pull mistral
    if [ $? -eq 0 ]; then
        echo "✅ Mistral downloaded successfully"
    else
        echo "❌ Failed to download Mistral"
        exit 1
    fi
else
    echo "✅ Mistral already installed"
fi

echo ""
echo "📦 Installing Python dependencies..."
cd /Users/tanvir/Desktop/SHAND/backend
pip install requests --quiet

echo "✅ Dependencies installed"
echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Start Ollama (in a new terminal):"
echo "   ollama serve"
echo ""
echo "2. Start Django server (in another terminal):"
echo "   cd /Users/tanvir/Desktop/SHAND && ./runserver.sh"
echo ""
echo "3. Test the LLM endpoint:"
echo "   curl -X POST http://127.0.0.1:8000/analyze-llm-local/ \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"text\": \"We assume users will adopt this immediately.\"}'"
echo ""
echo "📚 Documentation: /Users/tanvir/Desktop/SHAND/MODEL_SETUP_GUIDE.md"
