"""
Presentation layer URL configuration.

This module defines the main presentation layer URL patterns
that include API endpoints and other presentation routes.
"""

from django.urls import path, include

app_name = 'presentation'

urlpatterns = [
    # API endpoints (already prefixed with api/v1/ in main project URLs)
    path('', include('src.presentation.api.urls')),
    
    # Future presentation endpoints
    # path('docs/', include('src.presentation.docs.urls')),
]