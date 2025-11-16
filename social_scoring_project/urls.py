"""
Main Django project URLs configuration.

This is the Django project's main URL router that includes:
- Infrastructure endpoints (minimal)
- Presentation layer API endpoints
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django admin interface
    path('admin/', admin.site.urls),
    
    # API endpoints from presentation layer
    path('api/v1/', include('src.presentation.api.urls')),
    
    # Health check endpoint
    path('health/', lambda request: __import__('django.http').HttpResponse('OK')),
]