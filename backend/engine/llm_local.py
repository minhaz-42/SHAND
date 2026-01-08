"""
Local LLM Inference Module using Ollama
Provides assumption analysis using local models like Mistral, Llama2, etc.
No API keys needed, runs completely offline after model download.
"""

import json
import requests
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Ollama API endpoint (runs locally)
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODELS_URL = "http://localhost:11434/api/tags"

# Model to use (default: neural-chat:7b which is lightweight and effective)
# Other available models: devstral, qwen2.5-coder, mathstral, etc.
DEFAULT_MODEL = "neural-chat:7b"


def is_ollama_available() -> bool:
    """Check if Ollama service is running."""
    try:
        response = requests.get(OLLAMA_MODELS_URL, timeout=2)
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False


def get_available_models() -> List[str]:
    """Get list of downloaded models in Ollama."""
    try:
        response = requests.get(OLLAMA_MODELS_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return [model['name'].split(':')[0] for model in data.get('models', [])]
    except Exception as e:
        logger.warning(f"Could not get available models: {str(e)}")
    return []


def analyze_assumptions_with_llm(
    text: str,
    model: str = DEFAULT_MODEL,
    detailed: bool = False
) -> Dict[str, Any]:
    """
    Analyze assumptions using local LLM model.
    
    Args:
        text: Input text to analyze
        model: Model name (mistral, llama2, neural-chat, etc.)
        detailed: If True, request deeper analysis
    
    Returns:
        Dictionary with assumptions, categories, risks, and explanations
    """
    
    if not is_ollama_available():
        return {
            "error": "Ollama not running. Start with: ollama serve",
            "assumptions": []
        }
    
    # Construct prompt for LLM reasoning
    prompt = f"""Analyze this text and identify key assumptions. Return valid JSON only.

TEXT:
{text}

Return ONLY this JSON format (no markdown or extra text):
{{
    "assumptions": [
        {{
            "text": "assumption statement",
            "reasoning": "why this is an assumption",
            "category": "Technical",
            "confidence": 0.8,
            "risk_level": "MEDIUM",
            "what_breaks": "consequence if false",
            "source_evidence": "quote"
        }}
    ],
    "analysis_quality": "high",
    "total_text_length": 0
}}"""

    try:
        # Call local Ollama API
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.5,
                "num_ctx": 1024,
                "top_p": 0.9,
                "top_k": 40,
            },
            timeout=600  # 10 minutes for very large texts
        )
        
        if response.status_code != 200:
            return {
                "error": f"Ollama error: {response.status_code}",
                "assumptions": []
            }
        
        # Extract response
        result = response.json()
        response_text = result.get("response", "").strip()
        
        # Parse JSON from response
        try:
            # Find JSON in response (sometimes LLM adds text before/after)
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                parsed = json.loads(json_str)
                
                # Map LLM output to our format
                assumptions = []
                for idx, assumption in enumerate(parsed.get('assumptions', []), 1):
                    assumptions.append({
                        "id": idx,
                        "text": assumption.get("text", ""),
                        "reason": assumption.get("reasoning", ""),
                        "type": assumption.get("category", "Unknown"),
                        "confidence": assumption.get("confidence", 0.5),
                        "risk": assumption.get("risk_level", "MEDIUM"),
                        "what_breaks": assumption.get("what_breaks", ""),
                        "source_evidence": assumption.get("source_evidence", ""),
                        "llm_generated": True,
                        "model": model
                    })
                
                return {
                    "assumptions": assumptions,
                    "analysis_quality": parsed.get("analysis_quality", "medium"),
                    "total_assumptions": len(assumptions),
                    "model_used": model,
                    "method": "local_llm"
                }
            else:
                # Fallback: try to parse entire response
                parsed = json.loads(response_text)
                assumptions = [
                    {
                        "id": idx + 1,
                        "text": a.get("text", ""),
                        "reason": a.get("reasoning", ""),
                        "type": a.get("category", "Unknown"),
                        "confidence": a.get("confidence", 0.5),
                        "risk": a.get("risk_level", "MEDIUM"),
                        "what_breaks": a.get("what_breaks", ""),
                        "source_evidence": a.get("source_evidence", ""),
                        "llm_generated": True,
                        "model": model
                    }
                    for idx, a in enumerate(parsed.get('assumptions', []))
                ]
                return {
                    "assumptions": assumptions,
                    "analysis_quality": parsed.get("analysis_quality", "medium"),
                    "total_assumptions": len(assumptions),
                    "model_used": model,
                    "method": "local_llm"
                }
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {str(e)}")
            return {
                "error": f"Could not parse LLM response as JSON",
                "raw_response": response_text[:500],
                "assumptions": []
            }
    
    except requests.exceptions.Timeout:
        return {
            "error": "LLM analysis timed out. Try a shorter text or simpler model.",
            "assumptions": []
        }
    except requests.exceptions.ConnectionError:
        return {
            "error": "Could not connect to Ollama. Make sure 'ollama serve' is running.",
            "assumptions": []
        }
    except Exception as e:
        logger.error(f"LLM analysis error: {str(e)}")
        return {
            "error": str(e),
            "assumptions": []
        }


def build_graph_from_llm_assumptions(
    assumptions: List[Dict[str, Any]]
) -> Dict[str, List[int]]:
    """
    Build dependency graph from LLM-identified assumptions.
    
    Args:
        assumptions: List of assumptions from analyze_assumptions_with_llm
    
    Returns:
        Adjacency list of assumption dependencies
    """
    if not assumptions:
        return {}
    
    # Simple graph: if assumptions share key terms, they're related
    graph = {str(a['id']): [] for a in assumptions}
    
    assumption_texts = [a['text'].lower().split() for a in assumptions]
    
    for i, text1 in enumerate(assumption_texts):
        for j, text2 in enumerate(assumption_texts):
            if i != j:
                # Count shared words (simple overlap)
                shared = len(set(text1) & set(text2))
                if shared >= 3:  # At least 3 shared words
                    graph[str(i + 1)].append(j + 1)
    
    return graph


def explain_assumption_with_llm(
    assumption_text: str,
    original_text: str,
    model: str = DEFAULT_MODEL
) -> Dict[str, Any]:
    """
    Get detailed LLM explanation for a specific assumption.
    
    Args:
        assumption_text: The assumption to explain
        original_text: Original context
        model: Model to use
    
    Returns:
        Detailed explanation with evidence and mitigation
    """
    
    if not is_ollama_available():
        return {"error": "Ollama not running"}
    
    prompt = f"""Analyze this assumption deeply:

ASSUMPTION: "{assumption_text}"

ORIGINAL CONTEXT:
{original_text[:1000]}...

Provide:
1. Evidence in text supporting this assumption
2. Evidence contradicting this assumption
3. Worst-case scenario if false
4. Likelihood it's true (1-10)
5. How to validate or mitigate this risk

Return valid JSON:
{{
    "evidence_for": "...",
    "evidence_against": "...",
    "worst_case": "...",
    "likelihood": 7,
    "validation_strategy": "..."
}}"""
    
    try:
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.3,
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get("response", "").strip()
            
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                return json.loads(response_text[json_start:json_end])
    
    except Exception as e:
        logger.error(f"Explanation error: {str(e)}")
    
    return {"error": "Could not generate explanation"}


def generate_report_with_llm(
    text: str,
    assumptions: List[Dict[str, Any]],
    model: str = DEFAULT_MODEL
) -> str:
    """
    Generate executive summary/report using LLM.
    
    Args:
        text: Original input text
        assumptions: Identified assumptions
        model: Model to use
    
    Returns:
        Executive summary string
    """
    
    if not is_ollama_available():
        return "Analysis unavailable"
    
    assumption_list = "\n".join([
        f"- {a['text']} (Risk: {a['risk']})"
        for a in assumptions[:5]
    ])
    
    prompt = f"""Based on this text and assumptions, create a brief executive summary:

TEXT:
{text[:500]}...

KEY ASSUMPTIONS:
{assumption_list}

Provide 2-3 sentences highlighting:
1. Main risks
2. Top priority
3. Recommended next step

Be concise and actionable."""
    
    try:
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.5,
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "").strip()
    
    except Exception as e:
        logger.error(f"Report generation error: {str(e)}")
    
    return "Summary unavailable"
