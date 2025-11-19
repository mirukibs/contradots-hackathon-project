"""
Django repository implementations for the Social Scoring System.

This module provides concrete repository implementations using Django ORM
that implement the repository interfaces defined in the domain layer.
"""

from typing import List, TYPE_CHECKING, Optional
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.contrib.auth.models import User

from ...domain.person.person_repository import PersonRepository
from ...domain.person.person import Person
from ...domain.person.role import Role
from ...domain.shared.value_objects.person_id import PersonId
from ...domain.activity.activity_repository import ActivityRepository
from ...domain.activity.activity import Activity
from ...domain.shared.value_objects.activity_id import ActivityId
from ...domain.action.action_repository import ActionRepository
from ...domain.action.action import Action as DomainAction
from ...domain.action.action_status import ActionStatus
from ...domain.shared.value_objects.action_id import ActionId

from ..django_app.models import PersonProfile, Activity as ActivityModel, Action as ActionModel

if TYPE_CHECKING:
    pass


class DjangoPersonRepository(PersonRepository):
    """
    Django ORM implementation of PersonRepository.
    
    Provides persistence for Person aggregate roots using Django models
    while maintaining domain layer interfaces.
    """
    
    def find_by_id(self, person_id: PersonId) -> Person:
        """
        Find person by their unique ID.
        
        Args:
            person_id: Unique identifier for the person
            
        Returns:
            Person domain object
            
        Raises:
            ValueError: If person is not found
        """
        try:
            profile = PersonProfile.objects.get(person_id=person_id.value)
            return self._to_domain_person(profile)
        except ObjectDoesNotExist:
            raise ValueError(f"Person with ID {person_id.value} not found")
    
    def find_by_email(self, email: str) -> Person:
        """
        Find person by their email address.
        
        Args:
            email: Email address to search for
            
        Returns:
            Person domain object
            
        Raises:
            ValueError: If person is not found
        """
        try:
            profile = PersonProfile.objects.get(user__email=email.lower().strip())
            return self._to_domain_person(profile)
        except ObjectDoesNotExist:
            raise ValueError(f"Person with email {email} not found")
    
    def save(self, person: Person) -> None:
        """
        Save person to the database.
        
        Args:
            person: Person domain object to save
        """
        with transaction.atomic():
            try:
                # Try to find existing profile
                profile = PersonProfile.objects.get(person_id=person.person_id.value)
                # Update existing
                self._update_profile_from_person(profile, person)
            except ObjectDoesNotExist:
                # Create new
                profile = self._create_profile_from_person(person)
            
            profile.save()
    
    def delete(self, person_id: PersonId) -> None:
        """
        Delete person from the database.
        
        Args:
            person_id: ID of person to delete
        """
        try:
            profile = PersonProfile.objects.get(person_id=person_id.value)
            # Delete the Django user as well (cascade will handle profile)
            profile.user.delete()
        except ObjectDoesNotExist:
            # Already deleted or never existed
            pass
    
    def find_all(self) -> List[Person]:
        """
        Find all Person aggregates.
        
        Returns:
            List of all Person aggregates
        """
        profiles = PersonProfile.objects.filter(is_active=True).order_by('created_at')
        return [self._to_domain_person(profile) for profile in profiles]
    
    def get_leaderboard(self, limit: int = 50) -> List[Person]:
        """
        Get leaderboard of people ordered by reputation score.
        
        Args:
            limit: Maximum number of people to return
            
        Returns:
            List of Person objects ordered by reputation score (descending)
        """
        profiles = PersonProfile.objects.filter(
            is_active=True
        ).order_by(
            '-reputation_score', 'created_at'
        )[:limit]
        
        return [self._to_domain_person(profile) for profile in profiles]
    
    def _to_domain_person(self, profile: PersonProfile) -> Person:
        """Convert Django PersonProfile to domain Person."""
        return Person(
            person_id=PersonId(profile.person_id),
            name=profile.full_name,
            email=profile.user.email,
            role=Role(profile.role),
            reputation_score=profile.reputation_score
        )
    
    def _create_profile_from_person(self, person: Person) -> PersonProfile:
        """Create Django PersonProfile from domain Person."""
        # Find existing Django user (should exist from authentication system)
        try:
            user = User.objects.get(email=person.email)
            # Check if this user already has a profile
            try:
                existing_profile = PersonProfile.objects.get(user=user)
                # User already has a profile, update it instead of creating new
                existing_profile.person_id = person.person_id.value
                existing_profile.role = person.role.value
                existing_profile.full_name = person.name
                existing_profile.reputation_score = person.reputation_score
                existing_profile.is_active = True
                return existing_profile
            except ObjectDoesNotExist:
                # User exists but no profile yet, this is the expected case for registration
                pass
        except ObjectDoesNotExist:
            # This shouldn't happen - authentication should create Django User first
            raise ValueError(f"Django user for email {person.email} does not exist. Authentication must be completed first.")
        
        # Create profile for existing user
        profile = PersonProfile(
            user=user,
            person_id=person.person_id.value,
            role=person.role.value,
            full_name=person.name,
            reputation_score=person.reputation_score,
            is_active=True
        )
        
        return profile
    
    def _update_profile_from_person(self, profile: PersonProfile, person: Person) -> None:
        """Update Django PersonProfile from domain Person."""
        profile.full_name = person.name
        profile.role = person.role.value
        profile.reputation_score = person.reputation_score
        
        # Update Django user as well
        profile.user.email = person.email
        profile.user.username = person.email
        profile.user.first_name = person.name
        profile.user.save()


class DjangoActivityRepository(ActivityRepository):
    """
    Django ORM implementation of ActivityRepository.
    
    Provides persistence for Activity aggregate roots using Django models.
    """
    
    def find_by_id(self, activity_id: ActivityId) -> Optional[Activity]:
        """
        Find activity by its unique ID.
        
        Args:
            activity_id: Unique identifier for the activity
            
        Returns:
            Activity domain object if found, None otherwise
        """
        try:
            model = ActivityModel.objects.get(activity_id=activity_id.value)
            return self._to_domain_activity(model)
        except ObjectDoesNotExist:
            return None
    
    def save(self, activity: Activity) -> None:
        """
        Save activity to the database.
        
        Args:
            activity: Activity domain object to save
        """
        with transaction.atomic():
            try:
                # Try to find existing activity
                model = ActivityModel.objects.get(activity_id=activity.activity_id.value)
                # Update existing
                self._update_model_from_activity(model, activity)
            except ObjectDoesNotExist:
                # Create new
                model = self._create_model_from_activity(activity)
            
            model.save()
    
    def delete(self, activity_id: ActivityId) -> None:
        """
        Delete activity from the database.
        
        Args:
            activity_id: ID of activity to delete
        """
        try:
            model = ActivityModel.objects.get(activity_id=activity_id.value)
            model.delete()
        except ObjectDoesNotExist:
            # Already deleted or never existed
            pass
    
    def find_by_creator_id(self, creator_id: PersonId) -> List[Activity]:
        """
        Find activities created by a specific person.
        
        Args:
            creator_id: ID of the creator person
            
        Returns:
            List of Activity domain objects created by the person
        """
        models = ActivityModel.objects.filter(
            lead_person__person_id=creator_id.value
        ).order_by('-created_at')
        
        return [self._to_domain_activity(model) for model in models]
    
    def find_all_active(self) -> List[Activity]:
        """
        Find all active activities.
        
        Returns:
            List of active Activity domain objects
        """
        models = ActivityModel.objects.filter(is_active=True).order_by('-created_at')
        return [self._to_domain_activity(model) for model in models]
    
    def _to_domain_activity(self, model: ActivityModel) -> Activity:
        """Convert Django ActivityModel to domain Activity."""
        from ...domain.activity.activity import Activity
        
        return Activity(
            activity_id=ActivityId(model.activity_id),
            title=model.name,  # Map name to title
            description=model.description,
            creator_id=PersonId(model.lead_person.person_id),
            points=model.points,
            created_at=model.created_at
        )
    
    def _create_model_from_activity(self, activity: Activity) -> ActivityModel:
        """Create Django ActivityModel from domain Activity."""
        lead_profile = PersonProfile.objects.get(person_id=activity.creator_id.value)
        model = ActivityModel(
            activity_id=activity.activity_id.value,
            name=activity.title,
            description=activity.description,
            points=activity.points,
            lead_person=lead_profile,
            is_active=activity.is_active
        )
        return model
    
    def _update_model_from_activity(self, model: ActivityModel, activity: Activity) -> None:
        """Update Django ActivityModel from domain Activity."""
        model.name = activity.title
        model.description = activity.description
        model.is_active = activity.is_active

    def reactivate_activity(self, activity_id: ActivityId) -> None:
        """
        Reactivate a deactivated activity.
        
        Args:
            activity_id: The unique identifier of the activity to reactivate
        """
        try:
            model = ActivityModel.objects.get(activity_id=activity_id.value)
            model.is_active = True
            model.save()
        except ObjectDoesNotExist:
            raise ValueError(f"Activity with ID {activity_id.value} not found")


class DjangoActionRepository(ActionRepository):
    """
    Django ORM implementation of ActionRepository.
    
    Provides persistence for Action aggregate roots using Django models.
    """
    
    def find_by_id(self, action_id: ActionId) -> Optional[DomainAction]:
        """
        Find action by its unique ID.
        
        Args:
            action_id: Unique identifier for the action
            
        Returns:
            Action domain object if found, None otherwise
        """
        try:
            model = ActionModel.objects.get(action_id=action_id.value)
            return self._to_domain_action(model)
        except ObjectDoesNotExist:
            return None
    
    def save(self, action: DomainAction) -> None:
        """
        Save action to the database.
        
        Args:
            action: Action domain object to save
        """
        with transaction.atomic():
            try:
                # Try to find existing action
                model = ActionModel.objects.get(action_id=action.action_id.value)
                # Update existing
                self._update_model_from_action(model, action)
            except ObjectDoesNotExist:
                # Create new
                model = self._create_model_from_action(action)
            
            model.save()
    
    def delete(self, action_id: ActionId) -> None:
        """
        Delete action from the database.
        
        Args:
            action_id: ID of action to delete
        """
        try:
            model = ActionModel.objects.get(action_id=action_id.value)
            model.delete()
        except ObjectDoesNotExist:
            # Already deleted or never existed
            pass
    
    def find_by_person_id(self, person_id: PersonId) -> List[DomainAction]:
        """
        Find all Actions submitted by a specific Person.
        
        Args:
            person_id: The unique identifier of the person
            
        Returns:
            List of Actions submitted by the person
        """
        return self.find_actions_by_person(person_id)
    
    def find_by_activity_id(self, activity_id: ActivityId) -> List[DomainAction]:
        """
        Find all Actions associated with a specific Activity.
        
        Args:
            activity_id: The unique identifier of the activity
            
        Returns:
            List of Actions associated with the activity
        """
        return self.find_actions_by_activity(activity_id)
    
    def find_verified_by_person_id(self, person_id: PersonId) -> List[DomainAction]:
        """
        Find all verified Actions by a specific Person.
        
        Args:
            person_id: The unique identifier of the person
            
        Returns:
            List of verified Actions by the person
        """
        models = ActionModel.objects.filter(
            person__person_id=person_id.value,
            status=ActionModel.VALIDATED
        ).order_by('-validated_at')
        
        return [self._to_domain_action(model) for model in models]
    
    def find_actions_by_person(self, person_id: PersonId) -> List[DomainAction]:
        """
        Find actions submitted by a specific person.
        
        Args:
            person_id: ID of the person
            
        Returns:
            List of Action domain objects submitted by the person
        """
        models = ActionModel.objects.filter(
            person__person_id=person_id.value
        ).order_by('-submitted_at')
        
        return [self._to_domain_action(model) for model in models]
    
    def find_actions_by_activity(self, activity_id: ActivityId) -> List[DomainAction]:
        """
        Find actions for a specific activity.
        
        Args:
            activity_id: ID of the activity
            
        Returns:
            List of Action domain objects for the activity
        """
        models = ActionModel.objects.filter(
            activity__activity_id=activity_id.value
        ).order_by('-submitted_at')
        
        return [self._to_domain_action(model) for model in models]
    
    def find_pending_actions(self) -> List[DomainAction]:
        """
        Find all actions pending validation.
        
        Returns:
            List of Action domain objects with SUBMITTED status
        """
        models = ActionModel.objects.filter(
            status=ActionModel.SUBMITTED
        ).order_by('submitted_at')
        
        return [self._to_domain_action(model) for model in models]
    
    def _to_domain_action(self, model: ActionModel) -> DomainAction:
        """Convert Django ActionModel to domain Action."""
        from ...domain.action.action import Action
        
        return Action(
            action_id=ActionId(model.action_id),
            person_id=PersonId(model.person.person_id),
            activity_id=ActivityId(model.activity.activity_id),
            proof=model.proof_hash,  # Map proof_hash to proof
            status=ActionStatus(model.status),
            submitted_at=model.submitted_at,
            verified_at=model.validated_at,
            blockchain_action_id=model.blockchain_action_id
        )
    
    def _create_model_from_action(self, action: DomainAction) -> ActionModel:
        """Create Django ActionModel from domain Action."""
        # Find related objects
        person_profile = PersonProfile.objects.get(person_id=action.person_id.value)
        activity_model = ActivityModel.objects.get(activity_id=action.activity_id.value)
        
        import logging
        proof_hash = action.proof.strip() if isinstance(action.proof, str) else action.proof
        logging.warning(f"REPO: creating model with proof_hash: '{proof_hash}', length: {len(proof_hash) if isinstance(proof_hash, str) else 'N/A'}")
        model = ActionModel(
            action_id=action.action_id.value,
            person=person_profile,
            activity=activity_model,
            description=f"Action for {activity_model.name}",  # Default description
            proof_hash=proof_hash,  # Map proof to proof_hash
            status=action.status.value,
            blockchain_action_id=action.blockchain_action_id
        )
        
        return model
    
    def _update_model_from_action(self, model: ActionModel, action: DomainAction) -> None:
        """Update Django ActionModel from domain Action."""
        import logging
        proof_hash = action.proof.strip() if isinstance(action.proof, str) else action.proof
        logging.warning(f"REPO: about to save proof_hash: '{proof_hash}', length: {len(proof_hash) if isinstance(proof_hash, str) else 'N/A'}")
        if not (isinstance(proof_hash, str) and len(proof_hash) == 66 and proof_hash.startswith('0x')):
            raise ValueError(f"Attempted to save malformed proof_hash: '{proof_hash}' (len={len(proof_hash) if isinstance(proof_hash, str) else 'N/A'})")
        model.proof_hash = proof_hash
        model.status = action.status.value.upper()
        model.blockchain_action_id = action.blockchain_action_id
        
        # Update validation fields if action is validated
        if action.status == ActionStatus.VALIDATED and action.verified_at:
            model.validated_at = action.verified_at
            
            # Set points awarded (from activity)
            model.points_awarded = model.activity.points