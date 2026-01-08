# --- Hallucination REST API ---
# This system operationalizes hallucination as confidence without sufficient support, not factual incorrectness.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import AnalysisSession, HallucinationEvent
from django.db.models import Avg
from .db_utils import process_claims_and_hallucinations
import uuid

@api_view(['POST'])
def analyze_view(request):
    """
    POST /api/analyze/
    Runs analysis, processes claims, logs hallucinations, returns session and stats.
    """
    user_text = request.data.get('input_text', '')
    llm_response = request.data.get('llm_response', {})
    model_name = request.data.get('model_name', 'neural-chat:7b')
    session = AnalysisSession.objects.create(input_text=user_text, model_used=model_name)
    stats = process_claims_and_hallucinations(session, llm_response, user_text)
    return Response({
        'session_id': session.id,
        'model': model_name,
        'stats': stats
    }, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def hallucinations_for_session(request, session_id):
    """
    GET /api/hallucinations/session/<id>/
    Returns all hallucination events for a session.
    """
    events = HallucinationEvent.objects.filter(session_id=session_id)
    return Response([
        {
            'claim_id': e.claim_id,
            'event_type': e.event_type,
            'claim_text': e.claim_text,
            'confidence_level': e.confidence_level,
            'created_at': e.created_at
        } for e in events
    ])

@api_view(['GET'])
def hallucination_stats(request):
    """
    GET /api/hallucinations/stats/
    Returns aggregate stats: average rate, signal breakdown, model comparison.
    """
    sessions = AnalysisSession.objects.all()
    total_sessions = sessions.count()
    avg_rate = sessions.aggregate(avg_rate=Avg('hallucination_rate'))['avg_rate'] or 0.0
    model_stats = {}
    for s in sessions:
        m = s.model_used
        if m not in model_stats:
            model_stats[m] = {'count': 0, 'avg_rate': 0.0}
        model_stats[m]['count'] += 1
        model_stats[m]['avg_rate'] += s.hallucination_rate
    for m in model_stats:
        if model_stats[m]['count'] > 0:
            model_stats[m]['avg_rate'] /= model_stats[m]['count']
    signal_breakdown = {}
    for e in HallucinationEvent.objects.all():
        signal_breakdown[e.event_type] = signal_breakdown.get(e.event_type, 0) + 1
    return Response({
        'total_sessions': total_sessions,
        'average_hallucination_rate': avg_rate,
        'model_stats': model_stats,
        'signal_breakdown': signal_breakdown
    })

@api_view(['POST'])
def hallucination_flag(request):
    """
    POST /api/hallucinations/flag/
    Allows user to flag a claim (tracked separately, not auto-penalized).
    """
    session_id = request.data.get('session_id')
    claim_id = request.data.get('claim_id')
    claim_text = request.data.get('claim_text', '')
    confidence = request.data.get('confidence_level', 'medium')
    HallucinationEvent.objects.create(
        session_id=session_id,
        claim_id=claim_id,
        event_type='user_flag',
        claim_text=claim_text,
        confidence_level=confidence
    )
    return Response({'flagged': True}, status=status.HTTP_201_CREATED)
"""
API views for analysis data exposure.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from . import models
from .models import AnalysisSession, Assumption
from .serializers import AnalysisSessionSerializer, AnalysisSessionDetailSerializer


class AnalysisPagination(PageNumberPagination):
    """Pagination for analysis list."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class AnalysisSessionViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for Analysis Sessions.
    
    GET /api/analyses/ - List all analyses
    GET /api/analyses/{id}/ - Get specific analysis
    """
    queryset = AnalysisSession.objects.all().order_by('-created_at')
    serializer_class = AnalysisSessionSerializer
    pagination_class = AnalysisPagination
    
    def get_serializer_class(self):
        """Use detailed serializer for retrieve action."""
        if self.action == 'retrieve':
            return AnalysisSessionDetailSerializer
        return AnalysisSessionSerializer
    
    def get_queryset(self):
        """Filter and search analyses."""
        queryset = AnalysisSession.objects.all().order_by('-created_at')
        
        # Filter by status
        status_filter = self.request.GET.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by analysis type
        analysis_type = self.request.GET.get('analysis_type', None)
        if analysis_type:
            queryset = queryset.filter(analysis_type=analysis_type)
        
        # Search in input text
        search = self.request.GET.get('search', None)
        if search:
            queryset = queryset.filter(input_text__icontains=search)
        
        return queryset


@api_view(['GET'])
def analysis_summary(request, pk):
    """
    GET /api/analyses/{id}/summary/
    Get summary of a specific analysis.
    """
    session = get_object_or_404(AnalysisSession, pk=pk)
    
    return Response({
        'id': session.id,
        'status': session.status,
            'total_claims': session.total_claims,
            'hallucination_count': session.hallucination_count,
        'medium_risk': session.medium_risk_count,
        'low_risk': session.low_risk_count,
        'analysis_type': session.analysis_type,
        'model': session.model_used,
        'processing_time': session.processing_time_seconds,
        'created_at': session.created_at,
        'executive_summary': session.executive_summary,
    })


@api_view(['GET'])
def risk_report(request, pk):
    """
    GET /api/analyses/{id}/risks/
    Get detailed risk report for an analysis.
    """
    session = get_object_or_404(AnalysisSession, pk=pk)
    assumptions = session.assumptions.all().select_related('risk_assessment').order_by('-confidence')  # type: ignore
    
    risk_items = []
    for assumption in assumptions:
        risk_data = {
            'id': assumption.id,
            'assumption': assumption.assumption_text,
            'category': assumption.category,
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
                'testing_recommendation': ra.testing_recommendation,
            })
        
        risk_items.append(risk_data)
    
    # Sort by risk score
    risk_items.sort(key=lambda x: x.get('score', 0), reverse=True)
    
    return Response({
        'session_id': session.id,
        'created_at': session.created_at,
        'total_risk_items': len(risk_items),
        'medium_risk_count': session.medium_risk_count,
        'low_risk_count': session.low_risk_count,
        'items': risk_items
    })


@api_view(['GET'])
def analysis_statistics(request):
    """
    GET /api/analyses/statistics/
    Get overall statistics for all analyses.
    """
    total_analyses = AnalysisSession.objects.count()
    completed = AnalysisSession.objects.filter(status='completed').count()
    failed = AnalysisSession.objects.filter(status='failed').count()
    
    all_assumptions = Assumption.objects.all()
    high_risk = all_assumptions.filter(risk_level='high').count()
    medium_risk = all_assumptions.filter(risk_level='medium').count()
    low_risk = all_assumptions.filter(risk_level='low').count()
    
    # Average assumptions per analysis
    avg_assumptions = all_assumptions.count() / max(total_analyses, 1)
    
    return Response({
        'total_analyses': total_analyses,
        'completed': completed,
        'failed': failed,
        'success_rate': (completed / total_analyses * 100) if total_analyses > 0 else 0,
        'total_assumptions': all_assumptions.count(),
        'high_risk_assumptions': high_risk,
        'medium_risk_assumptions': medium_risk,
        'low_risk_assumptions': low_risk,
        'avg_assumptions_per_analysis': round(avg_assumptions, 2),
    })
