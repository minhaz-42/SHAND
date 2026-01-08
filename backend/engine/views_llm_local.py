"""
Additional views for LLM-local analysis.
Import these into your main views.py
"""

import logging
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .llm_local import (
    analyze_assumptions_with_llm,
    is_ollama_available,
    get_available_models,
    build_graph_from_llm_assumptions,
    generate_report_with_llm
)

logger = logging.getLogger(__name__)


class AnalyzeLLMLocalAPIView(APIView):
    """POST /analyze-llm-local/ endpoint using Ollama.
    
    Uses local LLM model (Mistral, Llama2, etc.) to analyze assumptions.
    No API keys needed, runs completely offline.
    Requires: ollama serve running in background
    
    Example:
        curl -X POST http://127.0.0.1:8000/analyze-llm-local/ \\
             -H "Content-Type: application/json" \\
             -d '{"text": "...", "model": "mistral"}'
    """

    def post(self, request):
        # Check if Ollama is running
        if not is_ollama_available():
            return Response({
                "detail": "Ollama service not running. Start with: 'ollama serve'",
                "instructions": "https://ollama.ai for installation",
                "available_models": []
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        data = request.data
        text = data.get("text", "").strip()
        model = data.get("model", "neural-chat:7b")  # Default to neural-chat:7b
        
        # Validate input
        if not text:
            return Response(
                {"detail": "`text` must be a non-empty string."},
                status=status.HTTP_400_BAD_REQUEST
            )

        word_count = len(text.split())
        max_words = getattr(settings, "MAX_INPUT_WORDS", 5000)
        
        if word_count > max_words:
            return Response({
                "detail": f"Input exceeds word limit ({word_count} words). Max is {max_words}."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Use LLM to analyze assumptions
            llm_result = analyze_assumptions_with_llm(text, model=model)
            
            logger.info(f"LLM result: {llm_result}")
            
            if "error" in llm_result and not llm_result.get("assumptions"):
                logger.error(f"LLM error: {llm_result.get('error')}")
                return Response(llm_result, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            assumptions = llm_result.get("assumptions", [])
            
            # Build dependency graph
            graph = build_graph_from_llm_assumptions(assumptions)
            
            # Generate executive summary
            summary = generate_report_with_llm(text, assumptions, model=model)
            
            return Response({
                "assumptions": assumptions,
                "graph": graph,
                "executive_summary": summary,
                "analysis_type": "llm_local",
                "model_used": model,
                "analysis_quality": llm_result.get("analysis_quality", "medium"),
                "total_assumptions": llm_result.get("total_assumptions", len(assumptions))
            })
        
        except Exception as e:
            logger.exception(f"Unexpected error in LLM analysis")
            return Response({
                "error": f"Analysis failed: {str(e)}",
                "analysis_type": "llm_local"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StatusAPIView(APIView):
    """GET /status/ endpoint - Check LLM availability and models."""

    def get(self, request):
        ollama_available = is_ollama_available()
        available_models = get_available_models() if ollama_available else []
        
        return Response({
            "ollama_status": "running" if ollama_available else "not_running",
            "ollama_url": "http://localhost:11434",
            "available_models": available_models,
            "recommended_model": "mistral",
            "endpoints": {
                "rule_based": "/analyze/",
                "llm_local": "/analyze-llm-local/",
                "llm_claude": "/analyze-llm/",
                "deepdive": "/analyze-deepdive/",
                "status": "/status/"
            },
            "instructions": {
                "ollama_not_running": "Run: ollama serve",
                "no_models": "Download model: ollama pull mistral",
                "setup": "https://ollama.ai"
            }
        })
