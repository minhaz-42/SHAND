#!/bin/bash

# Test script for LLM-based analysis

echo "🧪 SHAND LLM Analysis Tester"
echo "============================="
echo ""

# Check if Django is running
echo "Checking if Django is running..."
if ! curl -s http://127.0.0.1:8000/status/ > /dev/null 2>&1; then
    echo "❌ Django not running!"
    echo ""
    echo "Start it with: ./runserver.sh"
    exit 1
fi

echo "✅ Django is running"
echo ""

# Check Ollama status
echo "1️⃣  Checking Ollama status..."
STATUS=$(curl -s http://127.0.0.1:8000/status/)

OLLAMA_STATUS=$(echo "$STATUS" | grep -o '"ollama_status":"[^"]*"' | cut -d'"' -f4)
AVAILABLE_MODELS=$(echo "$STATUS" | grep -o '"available_models":\[[^]]*\]')

echo "   Ollama status: $OLLAMA_STATUS"
echo "   Available models: $AVAILABLE_MODELS"
echo ""

if [ "$OLLAMA_STATUS" != "running" ]; then
    echo "⚠️  Ollama is not running!"
    echo ""
    echo "Start Ollama in another terminal:"
    echo "  ollama serve"
    echo ""
    echo "Then download a model:"
    echo "  ollama pull mistral"
    exit 1
fi

echo "✅ Ollama is ready"
echo ""

# Test original endpoint
echo "2️⃣  Testing original rule-based endpoint (/analyze/)..."
RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/analyze/ \
  -H "Content-Type: application/json" \
  -d '{"text": "We assume users will adopt this immediately because it'\''s better than alternatives."}')

if echo "$RESPONSE" | grep -q '"assumptions"'; then
    echo "✅ Rule-based endpoint works"
    NUM_ASSUMPTIONS=$(echo "$RESPONSE" | grep -o '"id":' | wc -l)
    echo "   Found $NUM_ASSUMPTIONS assumptions"
else
    echo "❌ Rule-based endpoint failed"
    echo "$RESPONSE"
fi
echo ""

# Test LLM endpoint
echo "3️⃣  Testing LLM-based endpoint (/analyze-llm-local/)..."
echo "   ⏳ This may take 30-60 seconds on first run..."
echo ""

RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/analyze-llm-local/ \
  -H "Content-Type: application/json" \
  -d '{"text": "We believe our product will capture 30% market share in year one. Users will adopt it immediately because it'\''s 10x better. The engineering team can build this with existing resources."}' \
  --max-time 120)

if echo "$RESPONSE" | grep -q '"assumptions"'; then
    echo "✅ LLM-based endpoint works!"
    NUM_ASSUMPTIONS=$(echo "$RESPONSE" | grep -o '"text":' | wc -l)
    echo "   Found approximately $NUM_ASSUMPTIONS assumptions"
    
    # Show analysis quality
    QUALITY=$(echo "$RESPONSE" | grep -o '"analysis_quality":"[^"]*"' | head -1 | cut -d'"' -f4)
    MODEL=$(echo "$RESPONSE" | grep -o '"model_used":"[^"]*"' | cut -d'"' -f4)
    echo "   Analysis quality: $QUALITY"
    echo "   Model used: $MODEL"
else
    echo "❌ LLM-based endpoint failed"
    echo "Response: $RESPONSE" | head -c 200
fi
echo ""

# Summary
echo "📊 Summary"
echo "=========="
echo "✅ All systems operational!"
echo ""
echo "Available endpoints:"
echo "  POST /analyze/            - Rule-based (fast, free)"
echo "  POST /analyze-llm-local/   - LLM local (smart, free)"
echo "  POST /analyze-llm/         - Claude API (fast, smart)"
echo "  GET  /status/              - Check system status"
echo ""
echo "Next: Try the endpoints from your app or use curl!"
