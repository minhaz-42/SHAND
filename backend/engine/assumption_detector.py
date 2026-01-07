"""Rule-based assumption detector.

Primary responsibilities:
- Identify sentences that contain explicit or implicit assumptions
- Extract a concise assumption candidate and explain why it's an assumption

Heuristics used (deterministic, explainable):
- Sentence splitting by punctuation
- Linguistic markers: will, assumes, assuming, expected to, should, likely, may, might
- Modal verb patterns ("we will" -> implies future outcome assumed)
- "If"/"unless" constructions may reveal missing premises

Each candidate is returned as a dict with:
- assumption_text
- source_sentence
- why_a_assumption

This module intentionally avoids ML and relies on simple, traceable rules.
"""
import re

SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
ASSUMPTION_MARKERS = [
    r"\bassume(?:s|d|ing)?\b",
    r"\bwill\b",
    r"\bexpected to\b",
    r"\bshould\b",
    r"\blikely\b",
    r"\bmay\b",
    r"\bmight\b",
    r"\bis assumed\b",
    r"\bassuming\b",
]


def split_sentences(text):
    sentences = SENTENCE_SPLIT_RE.split(text.strip())
    return [s.strip() for s in sentences if s.strip()]


def extract_assumption_from_sentence(sentence):
    """Return a candidate assumption dict if heuristics find one."""
    lower = sentence.lower()
    for marker in ASSUMPTION_MARKERS:
        if re.search(marker, lower):
            # Create a concise assumption text: attempt simple extraction
            # If phrase contains 'assuming' or 'assume', capture the clause following it
            m = re.search(r"\bassuming\b\s+(.+)$", lower)
            if m:
                assumption = m.group(1).strip(". ")
                reason = "Contains 'assuming' clause which names a premise."
                return {
                    "assumption_text": assumption,
                    "source_sentence": sentence,
                    "why_a_assumption": reason,
                }

            m = re.search(r"\bassume(?:s|d)?\b( that)?\s*(.+)$", lower)
            if m:
                assumption = m.group(2).strip(". ")
                reason = "Uses explicit 'assume' verb indicating a premise."
                return {
                    "assumption_text": assumption,
                    "source_sentence": sentence,
                    "why_a_assumption": reason,
                }

            # For modal verbs like 'will', take the clause containing will
            m = re.search(r"([A-Za-z0-9 ,'-]+\bwill\b.+?$)", sentence)
            if m:
                assumption = m.group(1).strip(". ")
                reason = "Predictive/modal language ('will') implies expectation that may be an assumption."
                return {
                    "assumption_text": assumption,
                    "source_sentence": sentence,
                    "why_a_assumption": reason,
                }

            # Fallback: return the whole sentence as a candidate
            return {
                "assumption_text": sentence.strip(". "),
                "source_sentence": sentence,
                "why_a_assumption": "Contains linguistic marker indicating an assumption.",
            }
    return None


def detect_assumptions(text):
    """Detect assumption candidates in the text and return a list of dicts.

    Deterministic, rule-based approach suitable for review.
    """
    sentences = split_sentences(text)
    candidates = []
    for s in sentences:
        cand = extract_assumption_from_sentence(s)
        if cand:
            # Avoid duplicates
            if not any(cand["assumption_text"].lower() == existing["assumption_text"].lower() for existing in candidates):
                candidates.append(cand)

    # Additional heuristic: find conditional sentences that imply missing premises
    for s in sentences:
        lower = s.lower()
        if "if" in lower or "unless" in lower:
            # Extract condition and outcome
            m = re.search(r"if\s+([^,.:;]+),?\s*(.+)", lower)
            if m:
                condition = m.group(1).strip()
                outcome = m.group(2).strip().strip(". ")
                assumption_text = f"{outcome} given {condition}"
                reason = "Conditional sentence implies an unstated link between condition and outcome."
                if not any(assumption_text.lower() == c["assumption_text"].lower() for c in candidates):
                    candidates.append({
                        "assumption_text": assumption_text,
                        "source_sentence": s,
                        "why_a_assumption": reason,
                    })
    return candidates
