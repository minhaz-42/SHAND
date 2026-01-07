"""Simple deterministic classifier for assumption types.

It scans for keywords associated with predefined categories and returns a best
match plus a confidence score. This is transparent and reviewable logic.

Return format:
{
  "assumption": "...",
  "type": "Factual|Behavioral|Technical|Economic|Temporal|Contextual|Ethical",
  "confidence": 0.0-1.0
}
"""

import re

CATEGORIES = {
    "Factual": [r"data|evidence|facts|statistics|studies"],
    "Behavioral": [r"users|customers|people|behavior|will do|tend to|prefer"],
    "Technical": [r"system|server|tech|infrastructure|API|implementation|rely on"],
    "Economic": [r"cost|price|budget|econom(y|ic)|market|revenue|profit"],
    "Temporal": [r"soon|next|later|within|by the end|quarter|year|delay"],
    "Contextual": [r"in the context|context|environment|market conditions|scenario"],
    "Ethical": [r"fair|bias|ethical|rights|consent|privacy|harm"],
}


def classify_assumption(text):
    text_l = text.lower()
    scores = {cat: 0 for cat in CATEGORIES}

    for cat, patterns in CATEGORIES.items():
        for pat in patterns:
            if re.search(pat, text_l):
                scores[cat] += 1

    # Choose best category
    best = max(scores.items(), key=lambda kv: kv[1])
    cat, score = best
    # Confidence: normalized score, add a base confidence for any non-zero
    if score == 0:
        # fallback: contextual if nothing matches; low confidence
        return {"assumption": text, "type": "Contextual", "confidence": 0.35}
    else:
        # Confidence between 0.6 and 0.95 depending on score (saturates)
        confidence = min(0.95, 0.6 + 0.15 * (score - 1))
        return {"assumption": text, "type": cat, "confidence": round(confidence, 2)}
