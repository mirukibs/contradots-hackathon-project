"""PersonApplicationService - Application service for person-related use cases"""

from typing import List

from src.application.commands.register_person_command import RegisterPersonCommand
from src.application.commands.authentication_commands import AuthenticateUserCommand
from src.application.dtos.person_profile_dto import PersonProfileDto
from src.application.dtos.leaderboard_dto import LeaderboardDto
from src.application.dtos.authentication_dtos import AuthenticationResultDto
from src.application.repositories.leaderboard_query_repository import LeaderboardQueryRepository
from src.application.security.authentication_context import AuthenticationContext
from src.application.security.authorization_service import AuthorizationService
from src.domain.person.person_repository import PersonRepository
from src.domain.person.person import Person, PersonId
from src.domain.person.role import Role


class PersonApplicationService:
    """
    Application service that orchestrates person-related use cases.
    
    This service handles:
    - User registration
    - Profile queries  
    - Leaderboard generation
    
    It coordinates between repositories and enforces authorization.
    """
    
    def __init__(
        self,
        person_repo: PersonRepository,
        leaderboard_query_repo: LeaderboardQueryRepository,
        authorization_service: AuthorizationService
    ) -> None:
        self._person_repo = person_repo
        self._leaderboard_query_repo = leaderboard_query_repo
        self._authorization_service = authorization_service
    
    def register_person(self, command: RegisterPersonCommand) -> PersonId:
        """
        Register a new person in the system.
        
        Note: Registration is typically public and doesn't require authentication.
        
        Args:
            command: The registration command containing person details
            
        Returns:
            PersonId: The ID of the newly created person
            
        Raises:
            ValueError: If command validation fails or person already exists
        """
        # Validate command
        command.validate()
        
        # Check if person with this email already exists
        existing_people = self._person_repo.find_all()
        for person in existing_people:
            if person.email == command.email:
                raise ValueError(f"Person with email {command.email} already exists")
        
        # Create new person using domain factory
        # Map application layer role to domain role
        role_mapping = {
            'participant': Role.MEMBER,
            'lead': Role.LEAD
        }
        role = role_mapping[command.role.lower()]
        person = Person.create(
            name=command.name,
            email=command.email,
            role=role
        )
        
        # Save the person
        self._person_repo.save(person)
        
        return person.person_id
    
    def authenticate_user(self, command: AuthenticateUserCommand) -> AuthenticationResultDto:
        """
        Authenticate a user with their credentials (as specified in Application Layer design).
        
        Args:
            command: The authentication command with user credentials
            
        Returns:
            AuthenticationResultDto: Result of the authentication attempt
        """
        try:
            # Find person by email
            person = self._person_repo.find_by_email(command.email)
            
            # Verify authentication credentials
            if not person.can_authenticate_with_email(command.email):
                return AuthenticationResultDto.failed("Invalid email credentials")
            
            # In a real implementation, password verification would happen here
            # For now, we assume password is valid if email is found
            
            return AuthenticationResultDto.successful(person.person_id, person.email)
            
        except Exception as e:
            return AuthenticationResultDto.failed(f"Authentication failed: {str(e)}")
    
    def get_current_user_profile(self, auth_context: AuthenticationContext) -> PersonProfileDto:
        """
        Get the current authenticated user's profile (as specified in Application Layer design).
        
        Args:
            auth_context: Authentication context of the current user
            
        Returns:
            PersonProfileDto: The current user's profile data
            
        Raises:
            ValueError: If person not found
            AuthorizationException: If user is not authenticated
        """
        # Require authentication
        self._authorization_service.require_authentication(auth_context)
        
        # Get current user's profile directly without additional auth check
        person = self._person_repo.find_by_id(auth_context.current_user_id)
        if not person:
            raise ValueError(f"Person not found: {auth_context.current_user_id}")
        
        # Map domain object to DTO
        return PersonProfileDto(
            personId=str(person.person_id),
            name=person.name,
            email=person.email,
            role=str(person.role),
            reputationScore=person.reputation_score
        )
    
    def get_person_profile(self, person_id: PersonId, context: AuthenticationContext) -> PersonProfileDto:
        """
        Get a person's profile information.
        
        Args:
            person_id: The ID of the person to retrieve
            context: Authentication context of the requesting user
            
        Returns:
            PersonProfileDto: The person's profile data
            
        Raises:
            ValueError: If person not found
            AuthorizationException: If user is not authenticated or accessing other's profile without permission
        """
        # Users can view their own profile, LEADs can view any profile
        self._authorization_service.require_authentication(context)
        
        if person_id != context.current_user_id:
            # Allow LEADs to view any profile
            self._authorization_service.validate_role_permission(context, "view_profile")
        
        person = self._person_repo.find_by_id(person_id)
        if not person:
            raise ValueError(f"Person not found: {person_id}")
        
        # Map domain object to DTO
        return PersonProfileDto(
            personId=str(person.person_id),
            name=person.name,
            email=person.email,
            role=str(person.role),
            reputationScore=person.reputation_score
        )
    
    def get_leaderboard(self, context: AuthenticationContext) -> List[LeaderboardDto]:
        """
        Get the current leaderboard rankings.
        
        Args:
            context: Authentication context of the requesting user
            
        Returns:
            List[LeaderboardDto]: List of leaderboard entries sorted by rank
            
        Raises:
            AuthorizationException: If user is not authenticated
        """
        # Require authentication to view leaderboard
        self._authorization_service.validate_role_permission(context, "view_leaderboard")
        
        # Delegate to query repository for optimized read
        return self._leaderboard_query_repo.get_leaderboard()