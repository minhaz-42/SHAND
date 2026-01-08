from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('', lambda request: redirect('/landing.html')),
    path("analyze/", include("engine.urls")),
    path("api/", include("engine.urls")),
]

# Serve static frontend files at root in development
from django.conf import settings
from django.conf.urls.static import static
urlpatterns += static('/', document_root=settings.STATICFILES_DIRS[0])
