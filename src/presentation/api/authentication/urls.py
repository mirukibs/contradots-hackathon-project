"""
URL patterns for authentication API endpoints.

This module defines URL routes for authentication-related API endpoints
following RESTful conventions.
"""

from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    # User registration
    path(
        'register/',
        views.register_user,
        name='register'
    ),
    
    # User login
    path(
        'login/',
        views.login_user,
        name='login'
    ),
    
    # User logout
    path(
        'logout/',
        views.logout_user,
        name='logout'
    ),
    
    # Token validation
    path(
        'validate/',
        views.validate_token,
        name='validate_token'
    ),
    
    # Current user context
    path(
        'me/',
        views.get_current_user,
        name='current_user'
    ),
]