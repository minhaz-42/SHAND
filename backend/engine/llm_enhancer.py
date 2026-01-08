"""
LLM-based enhancement module for assumption analysis.
Uses Claude API to validate, improve, and provide deeper insights on assumptions.
"""

import os
import json
from typing import Dict, List, Any, Union
import anthropic
from anthropic.types import TextBlock


def get_claude_client():
    """Initialize Claude client from API key."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set in environment variables")
    return anthropic.Anthropic(api_key=api_key)


def validate_and_enhance_assumptions(
    text: str, 
    rule_based_assumptions: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Use Claude to validate rule-based assumptions and find additional ones.
    
    Args:
        text: Original input text
        rule_based_assumptions: List of assumptions found by rule-based detector
    
    Returns:
        Dictionary with validation and additional assumptions
    """
    client = get_claude_client()
    
    # Format rule-based findings for Claude
    rule_text = json.dumps([
        {
            "id": a["id"],
            "text": a["text"],
            "type": a["type"],
            "confidence": a["confidence"]
        }
        for a in rule_based_assumptions
    ], indent=2)
    
    prompt = f"""Analyze this text for implicit and explicit assumptions:

TEXT:
{text}

RULE-BASED DETECTOR FINDINGS (already identified):
{rule_text}

TASK: 
1. Review the rule-based findings - are they valid assumptions? Rate each as CONFIRMED or QUESTIONABLE
2. Find 2-3 additional assumptions the rule detector missed
3. For each assumption, provide:
   - Text of assumption
   - Why it's an assumption (brief reasoning)
   - Category (Behavioral, Factual, Technical, Economic, Temporal, Contextual, or Ethical)
   - Confidence (0.0-1.0)
   - Severity if false (LOW, MEDIUM, HIGH)

Return ONLY valid JSON (no markdown, no explanation):
{{
    "validation": [
        {{"id": 1, "status": "CONFIRMED" or "QUESTIONABLE", "feedback": "reason if questionable"}}
    ],
    "additional_assumptions": [
        {{
            "text": "assumption text",
            "reasoning": "why this is an assumption",
            "category": "category",
            "confidence": 0.8,
            "severity_if_false": "MEDIUM"
        }}
    ]
}}"""
    
    try:
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1500,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = message.content[0].text.strip() if isinstance(message.content[0], TextBlock) else ""
        
        # Parse JSON response
        result = json.loads(response_text)
        return result
    
    except anthropic.APIError as e:
        return {
            "error": str(e),
            "validation": [],
            "additional_assumptions": []
        }
    except json.JSONDecodeError as e:
        return {
            "error": f"Invalid JSON from LLM: {str(e)}",
            "validation": [],
            "additional_assumptions": []
        }


def deep_analyze_assumption(
    assumption_text: str,
    context_text: str,
    current_analysis: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Use Claude for deeper analysis of a single assumption.
    
    Args:
        assumption_text: The assumption statement
        context_text: Original input text for context
        current_analysis: Current rule-based analysis (type, risk, etc.)
    
    Returns:
        Deep analysis including nuances and counterarguments
    """
    client = get_claude_client()
    
    prompt = f"""Analyze this assumption in depth:

ASSUMPTION: "{assumption_text}"

ORIGINAL TEXT CONTEXT:
{context_text[:500]}...

CURRENT ANALYSIS:
- Type: {current_analysis.get('type', 'Unknown')}
- Risk Level: {current_analysis.get('risk', 'Unknown')}
- Confidence: {current_analysis.get('confidence', 'N/A')}

PROVIDE:
1. Evidence in text that supports or contradicts this assumption
2. What would happen if this assumption is false (worst case)
3. How likely is this to be true in reality (1-10 scale)
4. Recommended mitigation/validation strategy
5. Related assumptions (if any)

Return ONLY valid JSON:
{{
    "evidence_for": "supporting evidence",
    "evidence_against": "contradicting evidence",
    "worst_case_scenario": "what breaks",
    "real_world_likelihood": 7,
    "likelihood_reasoning": "why 7 out of 10",
    "mitigation_strategy": "how to validate or mitigate",
    "related_assumptions": ["assumption 1", "assumption 2"]
}}"""
    
    try:
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = message.content[0].text.strip() if isinstance(message.content[0], TextBlock) else ""
        result = json.loads(response_text)
        result["llm_enhanced"] = True
        return result
    
    except Exception as e:
        return {
            "error": str(e),
            "llm_enhanced": False
        }


def generate_executive_summary(
    text: str,
    assumptions: List[Dict[str, Any]]
) -> str:
    """
    Generate an executive summary of key risks and recommendations.
    
    Args:
        text: Original input text
        assumptions: List of identified assumptions
    
    Returns:
        Executive summary string
    """
    client = get_claude_client()
    
    # Format assumptions for summary
    assumption_summary = "\n".join([
        f"- {a['text']} (Risk: {a['risk']}, Type: {a['type']})"
        for a in assumptions[:5]  # Top 5 assumptions
    ])
    
    prompt = f"""Based on this text and identified assumptions, provide a brief executive summary:

TEXT:
{text[:1000]}...

KEY ASSUMPTIONS IDENTIFIED:
{assumption_summary}

PROVIDE: 2-3 sentence summary highlighting:
1. Main risk areas
2. Top priority to address
3. Recommended next steps

Be concise and actionable."""
    
    try:
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=300,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text.strip() if isinstance(message.content[0], TextBlock) else "[LLM Summary unavailable]"
    except Exception as e:
        return f"[LLM Summary unavailable: {str(e)}]"
