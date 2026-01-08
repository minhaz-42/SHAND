from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnalyzeAPIView, AnalyzeLLMEnhancedAPIView, AnalyzeDeepDiveAPIView
from .views_llm_local import AnalyzeLLMLocalAPIView, StatusAPIView
from .api_views import AnalysisSessionViewSet, analysis_summary, risk_report, analysis_statistics, hallucination_stats, hallucinations_for_session, hallucination_flag

router = DefaultRouter()
router.register(r'analyses', AnalysisSessionViewSet, basename='analysis')

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    path('api/analyses/<int:pk>/summary/', analysis_summary, name='analysis-summary'),
    path('api/analyses/<int:pk>/risks/', risk_report, name='analysis-risks'),
    path('api/analyses/statistics/', analysis_statistics, name='analysis-statistics'),

    # Hallucination endpoints at root level for /api/hallucinations/*
    path('hallucinations/stats/', hallucination_stats, name='hallucination-stats'),
    path('hallucinations/session/<int:session_id>/', hallucinations_for_session, name='hallucinations-for-session'),
    path('hallucinations/flag/', hallucination_flag, name='hallucination-flag'),

    # Legacy endpoints
    path("", AnalyzeAPIView.as_view(), name="analyze"),
    path("llm/", AnalyzeLLMEnhancedAPIView.as_view(), name="analyze-llm"),
    path("llm-local/", AnalyzeLLMLocalAPIView.as_view(), name="analyze-llm-local"),
    path("deepdive/", AnalyzeDeepDiveAPIView.as_view(), name="analyze-deepdive"),
    path("status/", StatusAPIView.as_view(), name="status"),
]
