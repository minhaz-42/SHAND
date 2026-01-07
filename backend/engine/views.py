from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .assumption_detector import detect_assumptions
from .assumption_classifier import classify_assumption
from .risk_engine import assess_risk
from .graph_builder import build_graph


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
