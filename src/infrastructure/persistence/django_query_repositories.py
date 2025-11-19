"""
Django query repository implementations for the Social Scoring System.

This module provides concrete query repository implementations using Django ORM
that implement the query repository interfaces defined in the application layer.
Following CQRS pattern for optimized read operations.

NOTE: This infrastructure layer only uses DTOs and primitive types,
avoiding direct dependencies on domain objects per clean architecture.
"""

from typing import List
from django.db.models import QuerySet
from django.core.exceptions import ObjectDoesNotExist

from ...application.repositories.activity_query_repository import ActivityQueryRepository
from ...application.repositories.action_query_repository import ActionQueryRepository
from ...application.repositories.leaderboard_query_repository import LeaderboardQueryRepository

from ...application.dtos.activity_dto import ActivityDto
from ...application.dtos.activity_details_dto import ActivityDetailsDto
from ...application.dtos.action_dto import ActionDto
from ...application.dtos.leaderboard_dto import LeaderboardDto

from ..django_app.models import Activity, Action, PersonProfile


class DjangoActivityQueryRepository(ActivityQueryRepository):
    """
    Django ORM implementation of ActivityQueryRepository.
    
    Provides optimized read operations for activity data using Django ORM
    with proper filtering and joins for performance.
    """
    
    def get_active_activities(self) -> List[ActivityDto]:
        """
        Get all currently active activities.
        
        Returns:
            List of ActivityDto objects for all active activities
        """
        activities = Activity.objects.filter(
            is_active=True
        ).select_related('lead_person__user').order_by('-created_at')
        
        return [self._to_activity_dto(activity) for activity in activities]
    
    def get_activity_details(self, activity_id) -> ActivityDetailsDto:
        """
        Get detailed information for a specific activity including statistics.
        
        Args:
            activity_id: The ID of the activity to get details for (ActivityId or string)
            
        Returns:
            ActivityDetailsDto with comprehensive activity information
            
        Raises:
            ValueError: If activity not found
        """
        # Convert ActivityId to string if needed
        activity_id_str = str(activity_id)
        
        try:
            activity = Activity.objects.select_related(
                'lead_person__user'
            ).get(activity_id=activity_id_str)
            
            # Get action statistics using direct query
            from ..django_app.models import Action
            actions = Action.objects.filter(activity=activity)
            total_actions = actions.count()
            participant_count = actions.values('person').distinct().count()
            
            return ActivityDetailsDto(
                activityId=str(activity.activity_id),
                name=activity.name,
                description=activity.description,
                points=activity.points,
                leadName=activity.lead_person.full_name,
                isActive=activity.is_active,
                participantCount=participant_count,
                totalActionsSubmitted=total_actions
            )
            
        except ObjectDoesNotExist:
            raise ValueError(f"Activity with ID {activity_id} not found")
    
    def _to_activity_dto(self, activity: Activity) -> ActivityDto:
        """Convert Django Activity model to ActivityDto."""
        return ActivityDto(
            activityId=str(activity.activity_id),
            name=activity.name,
            description=activity.description,
            points=activity.points,
            leadName=activity.lead_person.full_name,
            isActive=activity.is_active
        )


class DjangoActionQueryRepository(ActionQueryRepository):
    """
    Django ORM implementation of ActionQueryRepository.
    
    Provides optimized read operations for action data using Django ORM
    with proper filtering and joins for performance.
    """
    
    def get_pending_validations(self) -> List[ActionDto]:
        """
        Get all actions that are pending validation.
        
        Returns:
            List of ActionDto objects for actions awaiting validation
        """
        actions = Action.objects.filter(
            status=Action.SUBMITTED
        ).select_related(
            'person__user', 'activity'
        ).order_by('submitted_at')
        
        return [self._to_action_dto(action) for action in actions]
    
    def get_person_actions(self, person_id: str) -> List[ActionDto]:
        """
        Get all actions submitted by a specific person.
        
        Args:
            person_id: The ID of the person to get actions for (as string)
            
        Returns:
            List of ActionDto objects for the person's actions
        """
        actions = Action.objects.filter(
            person__person_id=person_id
        ).select_related(
            'person__user', 'activity'
        ).order_by('-submitted_at')
        
        return [self._to_action_dto(action) for action in actions]
    
    def get_activity_actions(self, activity_id: str) -> List[ActionDto]:
        """
        Get all actions submitted for a specific activity.
        
        Args:
            activity_id: The ID of the activity to get actions for (as string)
            
        Returns:
            List of ActionDto objects for the activity's actions
        """
        actions = Action.objects.filter(
            activity__activity_id=activity_id
        ).select_related(
            'person__user', 'activity'
        ).order_by('-submitted_at')
        
        return [self._to_action_dto(action) for action in actions]
    
    def _to_action_dto(self, action: Action) -> ActionDto:
        """Convert Django Action model to ActionDto."""
        return ActionDto(
            actionId=str(action.action_id),
            personName=action.person.full_name,
            activityName=action.activity.name,
            description=action.description,
            status=action.status,
            submittedAt=action.submitted_at.isoformat(),
            blockchainActionId=action.blockchain_action_id
        )


class DjangoLeaderboardQueryRepository(LeaderboardQueryRepository):
    """
    Django ORM implementation of LeaderboardQueryRepository.
    
    Provides optimized read operations for leaderboard data using Django ORM
    with proper ranking calculations.
    """
    
    def get_leaderboard(self) -> List[LeaderboardDto]:
        """
        Get the current leaderboard with all participants ranked by reputation score.
        
        Returns:
            List of LeaderboardDto objects ordered by rank (highest score first)
        """
        profiles = PersonProfile.objects.filter(
            is_active=True
        ).select_related('user').order_by(
            '-reputation_score', 'created_at'
        )
        
        leaderboard = []
        for rank, profile in enumerate(profiles, 1):
            leaderboard.append(
                LeaderboardDto(
                    personId=str(profile.person_id),
                    name=profile.full_name,
                    reputationScore=profile.reputation_score,
                    rank=rank
                )
            )
        
        return leaderboard
    
    def get_person_rank(self, person_id: str) -> int:
        """
        Get the current rank of a specific person in the leaderboard.
        
        Args:
            person_id: The ID of the person to get rank for (as string)
            
        Returns:
            The person's current rank (1-based, 1 = highest score)
            
        Raises:
            ValueError: If person not found
        """
        try:
            target_profile = PersonProfile.objects.get(person_id=person_id)
        except ObjectDoesNotExist:
            raise ValueError(f"Person with ID {person_id} not found")
        
        # Count how many people have higher reputation scores
        higher_ranked_count = PersonProfile.objects.filter(
            is_active=True,
            reputation_score__gt=target_profile.reputation_score
        ).count()
        
        # Rank is 1-based, so add 1
        return higher_ranked_count + 1