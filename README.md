# SHAND — Structured Human Assumption & Narrative Detector

## Recent Updates (2026)
- **LLM Integration:** Local LLM (Ollama) and enhanced analysis endpoints added. See `views_llm_local.py`, `llm_local.py`, and `FRONTEND_LLM_INTEGRATION.html` for details.
- **Hallucination Dashboard:** New dashboard and API endpoints for hallucination signal analysis. See `hallucination-dashboard.html` and `api_views.py`.
- **Analysis History:** View all past analyses in `all-analysis.html`.
- **Expanded API:** New endpoints for session stats, hallucination events, and model selection.

## Philosophy
SHAND is a thinking tool, not a chatbot or landing page. It is designed for calm, readable, academic analysis of assumptions in text. The UI is minimal, neutral, and card-based. All logic is deterministic and explainable—no machine learning, no black boxes, no hallucinations.

## How It Works

SHAND analyzes text through a four-stage pipeline:

1. **Detector** — Rule-based heuristics identify explicit and implicit assumptions using linguistic markers (will, assume, expected, should, etc.)
2. **Classifier** — Lexical patterns map each assumption to a category with a confidence score (Factual, Behavioral, Technical, Economic, Temporal, Contextual, Ethical)
3. **Risk Engine** — Deterministic scoring considers evidence presence, scope breadth, temporal fragility, and human dependency
4. **Graph Builder** — Token-overlap analysis identifies dependencies between assumptions

### Input
- Plain English text (max 800 words)
- No authentication, no examples, no guided input

### Output
```json
{
  "assumptions": [
    {
      "id": 1,
      "text": "...",
      "type": "Behavioral|Factual|Technical|Economic|Temporal|Contextual|Ethical",
      "confidence": 0.75,
      "risk": "LOW|MEDIUM|HIGH",
      "reason": "Why this is an assumption",
      "risk_justification": "Why this risk level",
      "what_breaks": "If this assumption fails, ..."
    }
  ],
  "graph": { "1": [2, 3], "2": [] }
}
```

## Architecture

### Frontend
- **`index.html`** — Input page with textarea, word counter, LLM toggle, neutral button
- **`landing.html`** — Landing page with hero section, features, research context
- **`analysis.html`** — Results page with summary bar and vertically stacked assumption cards
- **`assumption.html`** — Deep view of single assumption with full explanation and dependencies
- **`about.html`** — Philosophy, methodology, and research relevance explanation
- **`result.html`** — Redirect page shown during processing
- **`all-analysis.html`** — View all past analyses
- **`hallucination-dashboard.html`** — Visualize hallucination signals and model stats
- **`FRONTEND_LLM_INTEGRATION.html`** — Optional UI for LLM mode selection

All styling is inline; no external CSS frameworks. Uses system fonts and academic color palette.

### Backend
- **Django 4.x** — Lightweight REST API server
- **Django REST Framework** — JSON request/response handling
- **SQLite** — Optional persistence (MVP uses localStorage)

#### Core Modules
- **`assumption_detector.py`** — Sentence splitting and linguistic pattern matching
- **`assumption_classifier.py`** — Pattern-based type classification with confidence
- **`risk_engine.py`** — Deterministic risk assessment with explainable factors
- **`graph_builder.py`** — Token-overlap dependency detection
- **`views.py`** — API endpoint handling validation and orchestration
- **`views_llm_local.py`** — LLM-based analysis endpoints (Ollama, local models)
- **`llm_local.py`** — Local LLM inference and model management
- **`api_views.py`** — Hallucination API endpoints and stats
- **`db_utils.py`** — Claim and hallucination processing utilities
- **`models.py`** — Analysis session, claim, and hallucination models

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip

### Quick Start

1. **Clone/navigate to project:**
   ```bash
   cd /path/to/SHAND
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   # or
   .venv\Scripts\activate  # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install django djangorestframework
   ```

4. **Run migrations (optional for MVP):**
   ```bash
   cd backend
   python manage.py migrate
   ```

5. **Start development server:**
   ```bash
   python manage.py runserver
   ```
   Server will run at `http://127.0.0.1:8000`

6. **Open in browser:**
   - Landing page: http://127.0.0.1:8000/landing.html
   - Input page: http://127.0.0.1:8000/index.html

## API Reference


### Key API Endpoints

- **POST /analyze/** — Rule-based analysis (input: `{ "text": "..." }`)
- **POST /llm-local/** — Local LLM analysis (input: `{ "text": "...", "model": "mistral" }`)
- **POST /llm/** — Enhanced LLM analysis (if enabled)
- **GET /api/analyses/** — List all analysis sessions
- **GET /api/analyses/{id}/summary/** — Get summary for a session
- **GET /api/hallucinations/session/{id}/** — Get hallucination events for a session
- **GET /api/hallucinations/stats/** — Get aggregate hallucination stats

See `backend/engine/urls.py` for full list.

## Example Workflow

**Input Text:**
```
We will launch the new feature next quarter and expect minimal support calls. 
Users will quickly prefer the new interface because it is more intuitive. 
All stakeholders assume the market will remain stable through Q4.
```

**Sample Output:**
```json
{
  "assumptions": [
    {
      "id": 1,
      "text": "launch the new feature next quarter",
      "type": "Temporal",
      "risk": "MEDIUM",
      "reason": "Predictive/modal language ('will') implies expectation that may be an assumption.",
      "what_breaks": "If this fails, deadlines or schedules will be missed.",
      "risk_justification": "Time-sensitive claim can be fragile over time."
    },
    {
      "id": 2,
      "text": "users will quickly prefer the new interface",
      "type": "Behavioral",
      "risk": "HIGH",
      "reason": "Contains linguistic marker indicating an assumption.",
      "what_breaks": "If this fails, user or stakeholder behavior may undermine the entire plan.",
      "risk_justification": "Depends on human behavior which can be variable."
    },
    {
      "id": 3,
      "text": "market will remain stable through Q4",
      "type": "Economic",
      "risk": "HIGH",
      "reason": "Predictive/modal language ('will') implies expectation that may be an assumption.",
      "what_breaks": "If this fails, financial losses or missed targets are likely.",
      "risk_justification": "No explicit indicators; defaulting to MEDIUM risk."
    }
  ],
  "graph": {
    "1": [],
    "2": [],
    "3": []
  }
}
```

## Design Principles

### Determinism
- All logic is traceable and reproducible
- No ML, no randomness, no external APIs
- Every output is explainable to a subject matter expert

### Simplicity
- Frontend: ~1000 lines of HTML + inline CSS + vanilla JS
- Backend: ~400 lines of Python logic
- No databases, no caching, no background jobs for MVP

### Neutrality
- No prescriptive language ("best practice", "should")
- No ranking of assumptions as "good" or "bad"
- Focuses on visibility and reasoning support

### Academic Rigor
- Deterministic classification suitable for peer review
- Reproducible results for benchmarking
- Designed for policy, design, and research contexts

## System Constraints

- **Max input:** 800 words
- **Language:** English only
- **Assumption types:** 7 categories (Factual, Behavioral, Technical, Economic, Temporal, Contextual, Ethical)
- **Risk levels:** LOW, MEDIUM, HIGH
- **Browsers:** Modern ES6+ support required (Chrome 60+, Firefox 55+, Safari 12+, Edge 79+)
- **No:** Authentication, multi-user, export, dark mode, visualizations, ML

## Testing

### Manual Testing
```bash
# Test API endpoint
curl -X POST http://127.0.0.1:8000/analyze/ \
  -H "Content-Type: application/json" \
  -d '{"text": "We assume users will adopt this quickly."}'

# Test frontend
# 1. Open http://127.0.0.1:8000/index.html
# 2. Paste sample text in textarea
# 3. Click "Analyze"
# 4. Verify results on analysis.html
# 5. Click on assumption to view details
```


## Project Structure
```
SHAND/
├── README.md
├── frontend/
│   ├── index.html
│   ├── landing.html
│   ├── analysis.html
│   ├── assumption.html
│   ├── about.html
│   ├── result.html
│   ├── all-analysis.html
│   ├── hallucination-dashboard.html
│   └── FRONTEND_LLM_INTEGRATION.html
└── backend/
  ├── manage.py
  ├── db.sqlite3
  ├── shand/
  │   ├── settings.py
  │   ├── urls.py
  │   └── wsgi.py
  └── engine/
    ├── __init__.py
    ├── models.py
    ├── views.py
    ├── views_llm_local.py
    ├── llm_local.py
    ├── api_views.py
    ├── db_utils.py
    ├── urls.py
    ├── assumption_detector.py
    ├── assumption_classifier.py
    ├── risk_engine.py
    ├── graph_builder.py
    └── migrations/
```

## Status & Maintenance

**Last Updated:** January 2026  
**Version:** MVP  
**Status:** Stable and fully functional  
**All Systems:** ✓ Working
