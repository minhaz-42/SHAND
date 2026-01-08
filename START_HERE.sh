#!/bin/bash

# SHAND LLM Integration - COMPLETE SETUP GUIDE
# =============================================

cat << 'EOF'

🚀 SHAND LLM Integration - Setup Instructions
==============================================

Your project now has ML/LLM-powered assumption analysis!

WHAT WAS ADDED:
✅ Local LLM support (Ollama + Mistral)
✅ Three analysis methods: Rule-based, LLM Local, Claude API
✅ New endpoints: /analyze-llm-local/, /status/
✅ Automatic model detection and management
✅ Zero-cost local inference

QUICK START (Choose one):
========================

OPTION A: LOCAL LLM (RECOMMENDED - Free, Smart, Offline)
─────────────────────────────────────────────────────────

1. Install Ollama:
   $ brew install ollama
   
   Or download from: https://ollama.ai

2. Download model (one-time, 4.1GB):
   $ ollama pull mistral

3. Start Ollama service (Terminal 1):
   $ ollama serve
   
   Keep this running in background!

4. Start Django (Terminal 2):
   $ cd /Users/tanvir/Desktop/SHAND
   $ ./runserver.sh

5. Test it (Terminal 3):
   $ ./test-llm.sh
   
   Or manually:
   $ curl -X POST http://127.0.0.1:8000/analyze-llm-local/ \
     -H "Content-Type: application/json" \
     -d '{"text": "We assume users will adopt this."}'

6. Open browser:
   http://127.0.0.1:8000


OPTION B: CLAUDE API (Fastest, Smartest)
──────────────────────────────────────────

1. Get API key:
   https://console.anthropic.com/

2. Set environment variable:
   $ export ANTHROPIC_API_KEY="sk-..."

3. Install dependencies:
   $ cd backend && pip install anthropic

4. Start Django:
   $ ./runserver.sh

5. Use endpoint:
   curl -X POST http://127.0.0.1:8000/analyze-llm/ ...


OPTION C: BOTH (Hybrid - Best of both worlds)
──────────────────────────────────────────────

Just do Option A setup, and optionally Option B.

All endpoints work simultaneously:
- /analyze/           (Rule-based, instant, free)
- /analyze-llm-local/ (LLM local, 30-60s, free)
- /analyze-llm/       (Claude API)


FILE STRUCTURE:
═══════════════

New Python Modules:
  ✅ backend/engine/llm_local.py          (Local inference)
  ✅ backend/engine/views_llm_local.py    (API views)

New Scripts:
  ✅ setup-ollama.sh    (Automated setup)
  ✅ test-llm.sh        (Test all endpoints)

Documentation:
  ✅ LLM_READY.md            (This guide!)
  ✅ MODEL_SETUP_GUIDE.md    (Detailed setup)
  ✅ ARCHITECTURE.md         (Technical details)


COMPARING MODELS:
═════════════════

Model             | Speed    | Reasoning | Size   | RAM  | Best For
─────────────────┼──────────┼───────────┼────────┼──────┼──────────
Mistral 7B ⭐    | 40s      | ⭐⭐⭐⭐⭐ | 4.1GB  | 6GB  | Most cases
Llama 2 7B       | 45s      | ⭐⭐⭐⭐   | 3.8GB  | 5GB  | Fallback
Neural-Chat 7B   | 20s      | ⭐⭐⭐     | 4.7GB  | 6GB  | Speed
Dolphin-Mixtral  | 90s      | ⭐⭐⭐⭐⭐ | 26GB   | 40GB | Best (needs power)


API ENDPOINTS:
══════════════

GET /status/
  → Check system health, available models

POST /analyze/
  → Rule-based analysis (original)
  → Input: {"text": "..."}
  → Instant, free, offline

POST /analyze-llm-local/
  → LLM analysis (NEW!)
  → Input: {"text": "...", "model": "mistral"}
  → 30-60 seconds, free, offline

POST /analyze-llm/
  → Claude API analysis
  → Input: {"text": "..."}
  → 1-3 seconds, ~$0.003, requires API key


TESTING YOUR SETUP:
═══════════════════

1. Check if Ollama is running:
   $ curl http://localhost:11434/api/tags
   
   Should return: {"models": [...]}

2. Check if Django is running:
   $ curl http://127.0.0.1:8000/status/
   
   Should return system status

3. Run full test suite:
   $ ./test-llm.sh
   
   Tests all three endpoints

4. Analyze sample text:
   $ curl -X POST http://127.0.0.1:8000/analyze-llm-local/ \
     -H "Content-Type: application/json" \
     -d '{
       "text": "We will build this in 3 months because the team is experienced.",
       "model": "mistral"
     }'


TROUBLESHOOTING:
════════════════

Problem: "Ollama not running"
Solution: 
  $ ollama serve

Problem: "Model not found"
Solution:
  $ ollama pull mistral

Problem: "Connection refused"
Solution:
  1. Check Ollama is running
  2. Check port 11434 not blocked
  3. Check firewall settings

Problem: "Out of memory"
Solution:
  - Close other apps
  - Use lighter model: neural-chat
  - Or use Claude API instead

Problem: "Analysis is slow"
Solution:
  - First run is slowest (warming up)
  - Subsequent runs are faster
  - Try neural-chat for speed
  - Or use Claude API


RUNNING EVERYTHING:
═══════════════════

Terminal 1 - Ollama Service:
$ ollama serve

Terminal 2 - Django Server:
$ cd /Users/tanvir/Desktop/SHAND
$ ./runserver.sh

Terminal 3 - Test/Use:
$ ./test-llm.sh
# or
$ curl -X POST http://127.0.0.1:8000/analyze-llm-local/ ...
# or
Open: http://127.0.0.1:8000 in browser


USING IN YOUR APP:
══════════════════

To use LLM analysis in frontend, update index.html:

```javascript
// Option 1: Always use LLM
fetch('/analyze-llm-local/', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({text: userText})
})

// Option 2: User can choose
const endpoint = useLLM ? '/analyze-llm-local/' : '/analyze/';
fetch(endpoint, ...)
```


NEXT FEATURES:
═══════════════

Phase 1 (Done!):
  ✅ Local LLM support (Ollama)
  ✅ Claude API integration
  ✅ Status monitoring

Phase 2 (Ready to implement):
  ⏳ Frontend toggle for analysis method
  ⏳ Model selection in UI
  ⏳ Result caching

Phase 3 (Future):
  ⏳ GPU acceleration
  ⏳ Fine-tuned models
  ⏳ Custom assumption categories


COST BREAKDOWN:
════════════════

Rule-based:     Free (all logic)
LLM Local:      Free (your computer)
Claude API:     Contact Anthropic for pricing


KEY DOCS:
═════════

LLM_READY.md         ← Start here
MODEL_SETUP_GUIDE.md ← Detailed setup
ARCHITECTURE.md      ← How it works
LLM_SETUP.md         ← Claude setup


VERIFICATION CHECKLIST:
═══════════════════════

- [ ] Ollama installed
- [ ] Model downloaded (mistral)
- [ ] Ollama service running
- [ ] Django server running
- [ ] Status endpoint accessible
- [ ] /analyze-llm-local/ responds
- [ ] Text limits respected
- [ ] Results display correctly
- [ ] All three endpoints work


PERFORMANCE EXPECTATIONS:
═════════════════════════

First analysis:     30-60 seconds (model warming up)
Subsequent:         15-40 seconds (model loaded)
Claude API:         1-3 seconds (cloud)
Rule-based:         Instant (no ML)


SUPPORT:
════════

If something doesn't work:

1. Check logs:
   - Ollama terminal for errors
   - Django terminal for errors
   
2. Run diagnostics:
   $ ./test-llm.sh
   
3. Check documentation:
   - MODEL_SETUP_GUIDE.md
   - ARCHITECTURE.md
   
4. Common issues in LLM_READY.md


YOU'RE READY! 🎉
════════════════

Your SHAND app now has intelligent LLM reasoning!

The models actually THINK through assumptions
instead of just pattern matching.

Start Ollama, start Django, and analyze assumptions!

Questions? Check the docs or re-run: ./setup-ollama.sh

Happy analyzing! 🚀

EOF

echo ""
echo "📚 Read these for detailed info:"
echo "   - LLM_READY.md (Quick start)"
echo "   - MODEL_SETUP_GUIDE.md (Detailed setup)"
echo "   - ARCHITECTURE.md (How it all works)"
