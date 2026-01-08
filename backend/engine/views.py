from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import os

from .assumption_detector import detect_assumptions
from .assumption_classifier import classify_assumption
from .risk_engine import assess_risk
from .graph_builder import build_graph
from .llm_enhancer import (
    validate_and_enhance_assumptions,
    deep_analyze_assumption,
    generate_executive_summary
)
from .llm_local import (
    analyze_assumptions_with_llm,
    is_ollama_available,
    get_available_models,
    build_graph_from_llm_assumptions,
    generate_report_with_llm
)


class AnalyzeAPIView(APIView):
    """POST /analyze/ endpoint.

    Expects JSON: {"text": "..."}
    Returns structured assumptions and a simple adjacency list graph.
    """

    def post(self, request):
        data = request.data
        text = data.get("text", "")
        if not isinstance(text, str) or not text.strip():
            return Response({"detail": "`text` must be a non-empty string."}, status=status.HTTP_400_BAD_REQUEST)

        word_count = len(text.split())
        if word_count > getattr(settings, "MAX_INPUT_WORDS", 800):
            return Response({"detail": f"Input exceeds word limit ({word_count} words). Max is {settings.MAX_INPUT_WORDS}."}, status=status.HTTP_400_BAD_REQUEST)

        # Detector returns raw assumption candidates
        candidates = detect_assumptions(text)

        # Classify and assess risk

        def what_breaks(type_, risk):
            # Deterministic, explainable mapping
            if risk == "HIGH":
                if type_ == "Behavioral":
                    return "If this assumption fails, user or stakeholder behavior may undermine the entire plan."
                if type_ == "Technical":
                    return "If this fails, technical implementation or system reliability is at risk."
                if type_ == "Economic":
                    return "If this fails, financial losses or missed targets are likely."
                if type_ == "Temporal":
                    return "If this fails, deadlines or schedules will be missed."
                if type_ == "Factual":
                    return "If this fails, the foundation of the argument is invalid."
                if type_ == "Ethical":
                    return "If this fails, ethical or legal violations may occur."
                return "If this fails, the context or environment may not support the plan."
            if risk == "MEDIUM":
                return "If this fails, moderate disruption or rework may be needed."
            return "If this fails, minor adjustments or clarifications may be required."

        structured = []
        for idx, cand in enumerate(candidates, start=1):
            cls = classify_assumption(cand["assumption_text"])
            risk = assess_risk(cand["assumption_text"])
            type_ = cls["type"]
            risk_level = risk["level"]
            structured.append({
                "id": idx,
                "text": cand["assumption_text"],
                "source_sentence": cand.get("source_sentence"),
                "type": type_,
                "confidence": cls["confidence"],
                "risk": risk_level,
                "risk_justification": risk["justification"],
                "reason": cand.get("why_a_assumption"),
                "what_breaks": what_breaks(type_, risk_level),
            })

        graph = build_graph(structured)

        return Response({"assumptions": structured, "graph": graph})

class AnalyzeLLMEnhancedAPIView(APIView):
    """POST /analyze-llm/ endpoint with LLM validation and enhancement.
    
    Combines rule-based detection with Claude API validation and enhancement.
    Requires ANTHROPIC_API_KEY environment variable.
    """

    def post(self, request):
        if not os.environ.get("ANTHROPIC_API_KEY"):
            return Response(
                {"detail": "LLM feature requires ANTHROPIC_API_KEY environment variable"},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = request.data
        text = data.get("text", "")
        if not isinstance(text, str) or not text.strip():
            return Response(
                {"detail": "`text` must be a non-empty string."},
                status=status.HTTP_400_BAD_REQUEST
            )

        word_count = len(text.split())
        if word_count > getattr(settings, "MAX_INPUT_WORDS", 800):
            return Response(
                {"detail": f"Input exceeds word limit ({word_count} words). Max is {settings.MAX_INPUT_WORDS}."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Step 1: Run rule-based detection
        candidates = detect_assumptions(text)

        def what_breaks(type_, risk):
            if risk == "HIGH":
                if type_ == "Behavioral":
                    return "If this assumption fails, user or stakeholder behavior may undermine the entire plan."
                if type_ == "Technical":
                    return "If this fails, technical implementation or system reliability is at risk."
                if type_ == "Economic":
                    return "If this fails, financial losses or missed targets are likely."
                if type_ == "Temporal":
                    return "If this fails, deadlines or schedules will be missed."
                if type_ == "Factual":
                    return "If this fails, the foundation of the argument is invalid."
                if type_ == "Ethical":
                    return "If this fails, ethical or legal violations may occur."
                return "If this fails, the context or environment may not support the plan."
            if risk == "MEDIUM":
                return "If this fails, moderate disruption or rework may be needed."
            return "If this fails, minor adjustments or clarifications may be required."

        structured = []
        for idx, cand in enumerate(candidates, start=1):
            cls = classify_assumption(cand["assumption_text"])
            risk = assess_risk(cand["assumption_text"])
            type_ = cls["type"]
            risk_level = risk["level"]
            structured.append({
                "id": idx,
                "text": cand["assumption_text"],
                "source_sentence": cand.get("source_sentence"),
                "type": type_,
                "confidence": cls["confidence"],
                "risk": risk_level,
                "risk_justification": risk["justification"],
                "reason": cand.get("why_a_assumption"),
                "what_breaks": what_breaks(type_, risk_level),
                "llm_enhanced": False,
            })

        # Step 2: Get LLM validation and enhancement
        llm_result = validate_and_enhance_assumptions(text, structured)
        
        llm_validation = llm_result.get("validation", [])
        llm_suggestions = llm_result.get("additional_assumptions", [])

        # Update structured with LLM feedback
        for validation in llm_validation:
            idx = validation.get("id")
            if idx and idx <= len(structured):
                structured[idx - 1]["llm_feedback"] = {
                    "status": validation.get("status"),
                    "feedback": validation.get("feedback", "")
                }

        # Add LLM-discovered assumptions
        for suggestion in llm_suggestions:
            structured.append({
                "id": len(structured) + 1,
                "text": suggestion.get("text"),
                "type": suggestion.get("category"),
                "confidence": suggestion.get("confidence", 0.7),
                "risk": suggestion.get("severity_if_false", "MEDIUM"),
                "reasoning": suggestion.get("reasoning", ""),
                "source": "llm_discovered",
                "llm_enhanced": True,
            })

        graph = build_graph(structured)
        
        # Step 3: Generate executive summary
        summary = generate_executive_summary(text, structured)

        return Response({
            "assumptions": structured,
            "graph": graph,
            "executive_summary": summary,
            "analysis_type": "llm_enhanced"
        })


class AnalyzeDeepDiveAPIView(APIView):
    """POST /analyze-deepdive/ endpoint with detailed LLM analysis of specific assumptions.
    
    First analyze the text, then provide deep analysis for requested assumptions.
    Body: {"text": "...", "assumption_indices": [0, 1]}
    """

    def post(self, request):
        if not os.environ.get("ANTHROPIC_API_KEY"):
            return Response(
                {"detail": "LLM feature requires ANTHROPIC_API_KEY environment variable"},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = request.data
        text = data.get("text", "")
        indices = data.get("assumption_indices", [])

        if not isinstance(text, str) or not text.strip():
            return Response(
                {"detail": "`text` must be a non-empty string."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Run full analysis
        candidates = detect_assumptions(text)

        def what_breaks(type_, risk):
            if risk == "HIGH":
                if type_ == "Behavioral":
                    return "If this assumption fails, user or stakeholder behavior may undermine the entire plan."
                if type_ == "Technical":
                    return "If this fails, technical implementation or system reliability is at risk."
                if type_ == "Economic":
                    return "If this fails, financial losses or missed targets are likely."
                if type_ == "Temporal":
                    return "If this fails, deadlines or schedules will be missed."
                if type_ == "Factual":
                    return "If this fails, the foundation of the argument is invalid."
                if type_ == "Ethical":
                    return "If this fails, ethical or legal violations may occur."
                return "If this fails, the context or environment may not support the plan."
            if risk == "MEDIUM":
                return "If this fails, moderate disruption or rework may be needed."
            return "If this fails, minor adjustments or clarifications may be required."

        structured = []
        for idx, cand in enumerate(candidates, start=1):
            cls = classify_assumption(cand["assumption_text"])
            risk = assess_risk(cand["assumption_text"])
            type_ = cls["type"]
            risk_level = risk["level"]
            structured.append({
                "id": idx,
                "text": cand["assumption_text"],
                "source_sentence": cand.get("source_sentence"),
                "type": type_,
                "confidence": cls["confidence"],
                "risk": risk_level,
                "risk_justification": risk["justification"],
                "reason": cand.get("why_a_assumption"),
                "what_breaks": what_breaks(type_, risk_level),
            })

        # Perform deep analysis on selected assumptions
        for idx in indices:
            if 0 <= idx < len(structured):
                assumption = structured[idx]
                deep_analysis = deep_analyze_assumption(
                    assumption["text"],
                    text,
                    assumption
                )
                assumption["deep_analysis"] = deep_analysis

        graph = build_graph(structured)

        return Response({
            "assumptions": structured,
            "graph": graph,
            "analysis_type": "deepdive"
        })