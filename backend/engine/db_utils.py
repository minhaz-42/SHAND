# --- Hallucination Signal Detection ---
# This system operationalizes hallucination as confidence without sufficient support, not factual incorrectness.
# Signals are detected from LLM output structure, following support-based taxonomy.
from .models import AnalysisSession, HallucinationEvent
import uuid

def process_claims_and_hallucinations(session: AnalysisSession, llm_response: dict, user_text: str):
    """
    Parses claims from LLM output, detects hallucination signals, logs events, and computes hallucination rate.
    Args:
        session: AnalysisSession instance
        llm_response: dict with 'claims' and 'summary' from LLM
        user_text: original input text
    """
    claims = llm_response.get('claims', [])
    total_claims = len(claims)
    hallucination_count = 0
    signal_types = ['unsupported', 'assumption_leak', 'contradiction', 'schema']

    for claim in claims:
        claim_id = claim.get('claim_id') or str(uuid.uuid4())
        text = claim.get('text', '')
        confidence = claim.get('confidence', 'medium')
        support = claim.get('support', {})
        signals = claim.get('signals', {})

        # --- Signal Detection ---
        # Unsupported Claim: Assertive, no citation/derivation, not in user text
        if signals.get('unsupported', False):
            HallucinationEvent.objects.create(
                session=session,
                claim_id=claim_id,
                event_type='unsupported',
                claim_text=text,
                confidence_level=confidence
            )
            hallucination_count += 1

        # Assumption Leakage: Hidden assumptions as facts, not marked
        if signals.get('assumption_leak', False):
            HallucinationEvent.objects.create(
                session=session,
                claim_id=claim_id,
                event_type='assumption',
                claim_text=text,
                confidence_level=confidence
            )
            hallucination_count += 1

        # Internal Contradiction: Conflicting claims in session
        if signals.get('contradiction', False):
            HallucinationEvent.objects.create(
                session=session,
                claim_id=claim_id,
                event_type='contradiction',
                claim_text=text,
                confidence_level=confidence
            )
            hallucination_count += 1

        # Schema/Validation Failure: Missing required fields, invalid output
        if signals.get('schema', False):
            HallucinationEvent.objects.create(
                session=session,
                claim_id=claim_id,
                event_type='schema',
                claim_text=text,
                confidence_level=confidence
            )
            hallucination_count += 1

    # Compute hallucination rate (do not penalize user_flag)
    hallucination_rate = (hallucination_count / total_claims) if total_claims > 0 else 0.0
    session.total_claims = total_claims
    session.hallucination_count = hallucination_count
    session.hallucination_rate = hallucination_rate
    session.save()
    return {
        'total_claims': total_claims,
        'hallucination_count': hallucination_count,
        'hallucination_rate': hallucination_rate
    }
"""
Database utility functions for saving analysis results.
"""
from django.utils import timezone
from .models import (
    AnalysisSession,
    Assumption,
    AssumptionDependency,
    RiskAssessment,
)
import logging

logger = logging.getLogger(__name__)


def save_analysis_session(
    input_text: str,
    assumptions: list,
    analysis_type: str = 'llm_local',
    model_used: str = 'neural-chat:7b',
    executive_summary: str = '',
    processing_time: float = 0,
    error_message: str | None = None,
):
    """
    Save a complete analysis session to the database.
    
    Args:
        input_text: Original text analyzed
        assumptions: List of detected assumptions (dicts)
        analysis_type: Type of analysis performed
        model_used: Model/method used
        executive_summary: Generated summary
        processing_time: Time taken in seconds
        error_message: Error message if analysis failed
    
    Returns:
        AnalysisSession instance
    """
    try:
        # Create session
        session = AnalysisSession.objects.create(
            input_text=input_text,
            input_text_length=len(input_text.split()),
            status='completed' if not error_message else 'failed',
            analysis_type=analysis_type,
            model_used=model_used,
            executive_summary=executive_summary,
            processing_time_seconds=processing_time,
            error_message=error_message,
            completed_at=timezone.now()
        )
        
        # Count risks
        high_risk = 0
        medium_risk = 0
        low_risk = 0
        
        # Save assumptions
        assumption_objects = []
        for idx, assumption in enumerate(assumptions, 1):
            risk = assumption.get('risk', 'medium').lower()
            
            if risk == 'high':
                high_risk += 1
            elif risk == 'medium':
                medium_risk += 1
            else:
                low_risk += 1
            
            assumption_obj = Assumption.objects.create(
                session=session,
                assumption_text=assumption.get('text', ''),
                reasoning=assumption.get('reason', ''),
                category=assumption.get('type', 'other').lower(),
                risk_level=risk,
                confidence=assumption.get('confidence', 0.5),
                what_breaks=assumption.get('what_breaks', ''),
                source_evidence=assumption.get('source_evidence', ''),
                position_in_analysis=idx,
                llm_generated=assumption.get('llm_generated', True),
            )
            assumption_objects.append(assumption_obj)
            
            # Create risk assessment
            RiskAssessment.objects.create(
                assumption=assumption_obj,
                likelihood=assumption.get('likelihood', 0.5),
                impact_if_false=assumption.get('impact_if_false', 0.5),
                overall_risk_score=assumption.get('risk_score', 0.5),
                mitigation_strategy=assumption.get('mitigation', ''),
            )
        
        # Update session counts
        # Removed unknown attributes total_assumptions and high_risk_count
        session.medium_risk_count = medium_risk
        session.low_risk_count = low_risk
        session.save()
        
        # Create dependencies if provided
        graph = {}  # Can be passed in assumptions or built separately
        if assumptions and isinstance(assumptions[0], dict) and 'dependencies' in assumptions[0]:
            for assumption in assumptions:
                if 'dependencies' in assumption:
                    for dep in assumption['dependencies']:
                        source_idx = assumption.get('id', 0)
                        target_idx = dep
                        if source_idx < len(assumption_objects) and target_idx < len(assumption_objects):
                            try:
                                AssumptionDependency.objects.create(
                                    session=session,
                                    source_assumption=assumption_objects[source_idx - 1],
                                    target_assumption=assumption_objects[target_idx - 1],
                                    dependency_type='depends_on'
                                )
                            except Exception as e:
                                logger.warning(f"Could not create dependency: {str(e)}")
        
        logger.info(f"Saved analysis session {session.id} with {len(assumptions)} assumptions")
        return session
    
    except Exception as e:
        logger.error(f"Error saving analysis session: {str(e)}")
        raise


def get_analysis_summary(session_id: int):
    """
    Get a summary of an analysis session.
    
    Args:
        session_id: ID of the AnalysisSession
    
    Returns:
        Dictionary with summary stats
    """
    try:
        session = AnalysisSession.objects.get(id=session_id)
        assumptions = session.assumptions.all()  # type: ignore
        
        return {
            'session_id': session.id,
            'input_length': session.input_text_length,
            'total_claims': session.total_claims,
            'hallucination_count': session.hallucination_count,
            'medium_risk': session.medium_risk_count,
            'low_risk': session.low_risk_count,
            'analysis_type': session.analysis_type,
            'model': session.model_used,
            'processing_time': session.processing_time_seconds,
            'created_at': session.created_at,
            'status': session.status,
            'assumptions': [
                {
                    'id': a.id,
                    'text': a.assumption_text,
                    'category': a.category,
                    'risk': a.risk_level,
                    'confidence': a.confidence,
                }
                for a in assumptions
            ]
        }
    except AnalysisSession.DoesNotExist:
        return None


def get_risk_report(session_id: int):
    """
    Get detailed risk report for a session.
    
    Args:
        session_id: ID of the AnalysisSession
    
    Returns:
        Dictionary with risk analysis
    """
    try:
        session = AnalysisSession.objects.get(id=session_id)
        assumptions = session.assumptions.all().select_related('risk_assessment')  # type: ignore
        
        risk_items = []
        for assumption in assumptions:
            risk_data = {
                'assumption': assumption.assumption_text,
                'risk_level': assumption.risk_level,
                'confidence': assumption.confidence,
            }
            
            if hasattr(assumption, 'risk_assessment'):
                ra = assumption.risk_assessment
                risk_data.update({
                    'likelihood': ra.likelihood,
                    'impact': ra.impact_if_false,
                    'score': ra.overall_risk_score,
                    'mitigation': ra.mitigation_strategy,
                })
            
            risk_items.append(risk_data)
        
        # Sort by risk score
        risk_items.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return {
            'session_id': session.id,
            'created_at': session.created_at,
            'total_risk_items': len(risk_items),
            # Removed unknown attribute high_risk_count
            'items': risk_items
        }
    except AnalysisSession.DoesNotExist:
        return None


def get_analysis_history(limit: int = 100, offset: int = 0, analysis_type: str | None = None):
    """
    Get analysis history with optional filtering.
    
    Args:
        limit: Number of results to return
        offset: Number of results to skip
        analysis_type: Filter by analysis type
    
    Returns:
        List of analysis sessions
    """
    query = AnalysisSession.objects.all()
    
    if analysis_type:
        query = query.filter(analysis_type=analysis_type)
    
    query = query.order_by('-created_at')[offset:offset + limit]
    
    return [
        {
            'id': s.id,
            'created_at': s.created_at,
            'status': s.status,
            'total_claims': s.total_claims,
            'analysis_type': s.analysis_type,
            'model': s.model_used,
            'text_preview': s.input_text[:100] + '...',
        }
        for s in query
    ]
