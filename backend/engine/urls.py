from django.urls import path
from .views import AnalyzeAPIView

urlpatterns = [
    path("", AnalyzeAPIView.as_view(), name="analyze"),
]
