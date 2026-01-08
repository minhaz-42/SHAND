from django.urls import path
from .views import AnalyzeAPIView, AnalyzeLLMEnhancedAPIView, AnalyzeDeepDiveAPIView
from .views_llm_local import AnalyzeLLMLocalAPIView, StatusAPIView

urlpatterns = [
    path("", AnalyzeAPIView.as_view(), name="analyze"),
    path("llm/", AnalyzeLLMEnhancedAPIView.as_view(), name="analyze-llm"),
    path("llm-local/", AnalyzeLLMLocalAPIView.as_view(), name="analyze-llm-local"),
    path("deepdive/", AnalyzeDeepDiveAPIView.as_view(), name="analyze-deepdive"),
    path("status/", StatusAPIView.as_view(), name="status"),
]
