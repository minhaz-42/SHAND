#!/bin/bash
# Quick setup script for LLM integration

echo "🚀 Setting up LLM Integration for SHAND..."

# Check if API key is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  ANTHROPIC_API_KEY not found!"
    echo ""
    echo "Get your API key from: https://console.anthropic.com/"
    echo ""
    echo "To set it (macOS/Linux):"
    echo "  export ANTHROPIC_API_KEY='your-api-key-here'"
    echo ""
    echo "Or add to ~/.zshrc:"
    echo "  echo 'export ANTHROPIC_API_KEY=\"sk-...\"' >> ~/.zshrc && source ~/.zshrc"
    exit 1
fi

# Install dependencies
echo "📦 Installing Anthropic SDK..."
cd backend
pip install anthropic --quiet

echo "✅ LLM setup complete!"
echo ""
echo "Available endpoints:"
echo "  POST /analyze/         - Rule-based analysis (original)"
echo "  POST /analyze-llm/     - LLM-enhanced analysis (NEW)"
echo "  POST /analyze-deepdive/ - Deep LLM analysis (NEW)"
echo ""
echo "Start server:"
echo "  cd /Users/tanvir/Desktop/SHAND && ./runserver.sh"
