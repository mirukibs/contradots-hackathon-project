"""
URL patterns for Activity and Action API endpoints.

This module defines URL routes for activity and action-related API endpoints
following RESTful conventions.
"""

from django.urls import path
from . import views

app_name = 'activity_action'

urlpatterns = [
    # ==================== Activity Endpoints ====================
    
    # Create new activity
    path(
        'activities/create/',
        views.create_activity,
        name='create_activity'
    ),

    # Get all active activities
    path(
        'activities/',
        views.get_active_activities,
        name='get_active_activities'
    ),

    # Deactivate activity (must come before <str:activity_id>)
    path(
        'activities/deactivate/',
        views.deactivate_activity,
        name='deactivate_activity'
    ),

    # Reactivate activity (must come before <str:activity_id>)
    path(
        'activities/reactivate/',
        views.reactivate_activity,
        name='reactivate_activity'
    ),

    # Get specific activity details (should be last among 'activities/' routes)
    path(
        'activities/<str:activity_id>/',
        views.get_activity_details,
        name='get_activity_details'
    ),
    
    # ==================== Action Endpoints ====================
    
    # Submit new action
    path(
        'actions/submit/',
        views.submit_action,
        name='submit_action'
    ),
    
    # Get pending validations (Lead only)
    path(
        'actions/pending/',
        views.get_pending_validations,
        name='get_pending_validations'
    ),
    
    # Get current user's actions
    path(
        'actions/my-actions/',
        views.get_my_actions,
        name='get_my_actions'
    ),
    
    # Validate action proof
    path(
        'actions/validate/',
        views.validate_proof,
        name='validate_proof'
    ),
]
