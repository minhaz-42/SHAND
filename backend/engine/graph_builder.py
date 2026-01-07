"""Build a simple dependency graph between assumptions.

Approach (explainable):
- Compare assumptions by token overlap (content words)
- If assumption A mentions a key noun present in B, treat A -> B as dependency
- Return adjacency list mapping ids (as strings) to lists of ids

This is intentionally simple and deterministic for review and later extension.
"""
import re


def tokenize_content_words(s):
    # Lowercase, remove punctuation, keep words >2 chars
    tokens = re.findall(r"\b[a-zA-Z]{3,}\b", s.lower())
    # Remove common stop-like words conservatively
    stop = set(["the", "and", "for", "with", "that", "this", "will", "should", "given"])
    return [t for t in tokens if t not in stop]


def build_graph(structured_assumptions):
    """structured_assumptions: list of dicts with 'id' and 'text'

    Returns adjacency list like {"1": [2,3], "2": []}
    """
    id_to_tokens = {}
    for a in structured_assumptions:
        id_to_tokens[a["id"]] = set(tokenize_content_words(a["text"]))

    graph = {str(a["id"]): [] for a in structured_assumptions}

    for a in structured_assumptions:
        for b in structured_assumptions:
            if a["id"] == b["id"]:
                continue
            # if A's tokens contain a meaningful overlap with B's tokens, A may depend on B
            overlap = id_to_tokens[a["id"]].intersection(id_to_tokens[b["id"]])
            if len(overlap) >= 2:
                graph[str(a["id"])].append(b["id"])
    return graph
