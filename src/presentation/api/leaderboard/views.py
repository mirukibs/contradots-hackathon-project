"""
Leaderboard API views for the Social Scoring System.

This module provides Django REST Framework views for leaderboard endpoints,
integrating with the application layer query repositories.
"""

import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from typing import Dict, Any

from .serializers import (
    LeaderboardResponseSerializer,
    PersonProfileSerializer
)

from ....infrastructure.persistence.django_query_repositories import (
    DjangoLeaderboardQueryRepository
)
from ....infrastructure.security.django_authorization_service import (
    get_authorization_service
)
from ....application.security.authentication_context import AuthenticationContext
from ....application.security.authorization_exception import AuthorizationException

logger = logging.getLogger(__name__)


def _get_auth_context(request: Request) -> AuthenticationContext:
    """
    Extract authentication context from the request.
    
    Args:
        request: Django REST framework request
        
    Returns:
        AuthenticationContext with current user information
        
    Raises:
        AuthorizationException: If user is not authenticated
    """
    if not request.user or not request.user.is_authenticated:
        raise AuthorizationException("Authentication required")
    
    # Get PersonProfile from Django User
    try:
        from ....infrastructure.django_app.models import PersonProfile
        person_profile = PersonProfile.objects.get(user=request.user)
        
        # Create PersonId from the profile
        from ....domain.shared.value_objects.person_id import PersonId
        person_id = PersonId(person_profile.person_id)
        
        # Map role from profile
        from ....domain.person.role import Role
        role_mapping = {
            PersonProfile.MEMBER: Role.MEMBER,
            PersonProfile.LEAD: Role.LEAD
        }
        domain_role = role_mapping.get(person_profile.role, Role.MEMBER)
        
        return AuthenticationContext(
            current_user_id=person_id,
            email=request.user.email,
            roles=[domain_role],
            is_authenticated=True
        )
        
    except PersonProfile.DoesNotExist:
        raise AuthorizationException("Person profile not found for authenticated user")
    except Exception as e:
        raise AuthorizationException(f"Invalid authentication state: {str(e)}")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_leaderboard(request: Request) -> Response:
    """
    Get the current leaderboard rankings.
    
    Query Parameters:
        - limit: int (optional) - Number of entries to return (default: 50, max: 100)
        - offset: int (optional) - Number of entries to skip (default: 0)
    
    Returns:
        200: Leaderboard data with rankings
        401: Authentication required
    """
    try:
        # Get authentication context
        auth_context = _get_auth_context(request)
        
        # Parse query parameters
        limit = min(int(request.GET.get('limit', 50)), 100)  # Max 100 entries
        offset = max(int(request.GET.get('offset', 0)), 0)  # Non-negative offset
        
        # Get leaderboard data
        leaderboard_repo = DjangoLeaderboardQueryRepository()
        leaderboard_entries = leaderboard_repo.get_leaderboard()
        
        # Apply pagination manually since the repository doesn't support it
        total_entries = len(leaderboard_entries)
        paginated_entries = leaderboard_entries[offset:offset + limit]
        
        # Get current user's rank
        current_user_rank = None
        try:
            current_user_rank = leaderboard_repo.get_person_rank(str(auth_context.current_user_id))
        except Exception:
            # User might not be ranked yet
            pass
        
        # Convert to response data
        leaderboard_data = [entry.to_dict() for entry in paginated_entries]
        
        response_data = {
            'leaderboard': leaderboard_data,
            'total': total_entries,
            'currentUserRank': current_user_rank
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except AuthorizationException as e:
        return Response({
            'error': 'AUTHORIZATION_ERROR',
            'message': str(e)
        }, status=status.HTTP_403_FORBIDDEN)
    except ValueError as e:
        return Response({
            'error': 'VALIDATION_ERROR',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': 'INTERNAL_ERROR',
            'message': f'An unexpected error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_profile(request: Request) -> Response:
    """
    Get the current user's profile information.
    
    Returns:
        200: User profile data
        401: Authentication required
        404: User profile not found
    """
    try:
        # Get authentication context
        auth_context = _get_auth_context(request)
        
        # Get user's profile through repository
        from ....infrastructure.persistence.django_repositories import DjangoPersonRepository
        person_repo = DjangoPersonRepository()
        
        try:
            person = person_repo.find_by_id(auth_context.current_user_id)
            
            # Convert to DTO format
            profile_data = {
                'personId': str(person.person_id),
                'name': person.name,
                'email': person.email,
                'role': person.role.value,
                'reputationScore': person.reputation_score
            }
            
            return Response(profile_data, status=status.HTTP_200_OK)
            
        except Exception:
            return Response({
                'error': 'NOT_FOUND',
                'message': 'User profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
    except AuthorizationException as e:
        return Response({
            'error': 'AUTHORIZATION_ERROR',
            'message': str(e)
        }, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return Response({
            'error': 'INTERNAL_ERROR',
            'message': f'An unexpected error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_rank(request: Request) -> Response:
    """
    Get the current user's rank in the leaderboard.
    
    Returns:
        200: User's current rank
        401: Authentication required
        404: User not ranked yet
    """
    try:
        # Get authentication context
        auth_context = _get_auth_context(request)
        
        # Get user's rank
        leaderboard_repo = DjangoLeaderboardQueryRepository()
        try:
            rank = leaderboard_repo.get_person_rank(str(auth_context.current_user_id))
            
            return Response({
                'rank': rank,
                'personId': str(auth_context.current_user_id)
            }, status=status.HTTP_200_OK)
            
        except ValueError:
            return Response({
                'error': 'NOT_FOUND',
                'message': 'User not ranked yet (no actions completed)'
            }, status=status.HTTP_404_NOT_FOUND)
        
    except AuthorizationException as e:
        return Response({
            'error': 'AUTHORIZATION_ERROR',
            'message': str(e)
        }, status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return Response({
            'error': 'INTERNAL_ERROR',
            'message': f'An unexpected error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)