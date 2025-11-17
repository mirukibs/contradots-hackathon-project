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
    
    # Activity and Action endpoints
    path('activity_action/', include('src.presentation.api.activity_action.urls')),
    
    # Future API modules will be added here
    # path('leaderboard/', include('src.presentation.api.leaderboard.urls')),
    
    # Health check
    path('health/', lambda request: __import__('django.http').HttpResponse('API OK')),
]