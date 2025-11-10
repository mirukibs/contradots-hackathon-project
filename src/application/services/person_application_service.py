"""PersonApplicationService - Application service for person-related use cases"""

from typing import List

from src.application.commands.register_person_command import RegisterPersonCommand
from src.application.dtos.person_profile_dto import PersonProfileDto
from src.application.dtos.leaderboard_dto import LeaderboardDto
from src.application.repositories.leaderboard_query_repository import LeaderboardQueryRepository
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
    
    It coordinates between command/query repositories but contains no business logic.
    """
    
    def __init__(
        self,
        person_repo: PersonRepository,
        leaderboard_query_repo: LeaderboardQueryRepository
    ) -> None:
        self._person_repo = person_repo
        self._leaderboard_query_repo = leaderboard_query_repo
    
    def register_person(self, command: RegisterPersonCommand) -> PersonId:
        """
        Register a new person in the system.
        
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
    
    def get_person_profile(self, person_id: PersonId) -> PersonProfileDto:
        """
        Get a person's profile information.
        
        Args:
            person_id: The ID of the person to retrieve
            
        Returns:
            PersonProfileDto: The person's profile data
            
        Raises:
            ValueError: If person not found
        """
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
    
    def get_leaderboard(self) -> List[LeaderboardDto]:
        """
        Get the current leaderboard rankings.
        
        Returns:
            List[LeaderboardDto]: List of leaderboard entries sorted by rank
        """
        # Delegate to query repository for optimized read
        return self._leaderboard_query_repo.get_leaderboard()