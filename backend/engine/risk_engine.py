"""Risk engine assigns LOW/MEDIUM/HIGH with short justification.

Risk factors considered:
- Evidence presence (reduces risk)
- Scope words ("all", "every", "systemic") increase risk
- Temporal fragility words increase risk ("soon", "within")
- Human dependency ("users", "people") increases risk

The logic is deterministic and returns an explainable justification string.
"""
import re

EVIDENCE_WORDS = r"data|evidence|study|studies|analysis|test|measured"
SCOPE_WORDS = r"all|every|entire|systemic|company-wide|global"
TEMPORAL_WORDS = r"soon|within|by the end|next|in "+"[0-9]"
HUMAN_DEPENDENCY = r"user|customer|people|operator|human"


def assess_risk(assumption_text):
    txt = assumption_text.lower()
    score = 0
    reasons = []

    # Evidence reduces risk
    if re.search(EVIDENCE_WORDS, txt):
        score -= 1
        reasons.append("Evidence mentioned, lowering risk.")

    # Scope increases risk
    if re.search(SCOPE_WORDS, txt):
        score += 2
        reasons.append("Broad scope language (e.g., 'all') increases potential impact.")

    # Temporal fragility
    if re.search(r"soon|within|next|by the end|quarter|year", txt):
        score += 1
        reasons.append("Time-sensitive claim can be fragile over time.")

    # Human dependency
    if re.search(HUMAN_DEPENDENCY, txt):
        score += 1
        reasons.append("Depends on human behavior which can be variable.")

    # Weak/hedged language reduces risk a bit
    if re.search(r"likely|may|might|could|possible", txt):
        score -= 0.5
        reasons.append("Hedging language present, signalling lower asserted certainty.")

    # Compute level
    if score <= -0.5:
        level = "LOW"
    elif score <= 1.5:
        level = "MEDIUM"
    else:
        level = "HIGH"

    justification = " ".join(reasons) or "No explicit indicators; defaulting to MEDIUM risk."
    return {"level": level, "justification": justification}
