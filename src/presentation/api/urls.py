"""
Main API URL configuration for the Social Scoring System.

This module defines the main API URL patterns that route to
different API modules.
"""

from django.urls import path, include

app_name = 'api'

urlpatterns = [
    # Authentication endpoints
    path('auth/', include('src.presentation.api.authentication.urls')),
    
    # Future API modules will be added here
    # path('activities/', include('src.presentation.api.activities.urls')),
    # path('actions/', include('src.presentation.api.actions.urls')),
    # path('leaderboard/', include('src.presentation.api.leaderboard.urls')),
    
    # Health check
    path('health/', lambda request: __import__('django.http').HttpResponse('API OK')),
]