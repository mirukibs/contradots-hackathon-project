"""Comprehensive tests for PersonApplicationService"""

from typing import List, Any
from unittest.mock import Mock
from src.application.services.person_application_service import PersonApplicationService
from src.application.commands.register_person_command import RegisterPersonCommand
from src.application.dtos.person_profile_dto import PersonProfileDto
from src.application.dtos.leaderboard_dto import LeaderboardDto
from src.application.security.authentication_context import AuthenticationContext
from src.domain.shared.value_objects.person_id import PersonId
from src.domain.person.person import Person
from src.domain.person.role import Role


class TestPersonApplicationService:
    """Test suite for PersonApplicationService covering all methods and edge cases"""

    def setup_method(self):
        """Set up test fixtures and mocks"""
        # Create mock repositories
        self.mock_person_repo = Mock()
        self.mock_leaderboard_query_repo = Mock()
        self.mock_authorization_service = Mock()
        
        # Create service instance
        self.service = PersonApplicationService(
            person_repo=self.mock_person_repo,
            leaderboard_query_repo=self.mock_leaderboard_query_repo,
            authorization_service=self.mock_authorization_service
        )
        
        # Create mock authentication context
        self.mock_auth_context = Mock(spec=AuthenticationContext)
        self.mock_auth_context.is_authenticated = True
        self.mock_auth_context.current_user_id = PersonId.generate()
        self.mock_auth_context.email = "test@example.com"
        
        # Test data
        self.valid_person_id = PersonId.generate()
        self.valid_command = RegisterPersonCommand(
            name="John Doe",
            email="john.doe@example.com", 
            role="member"
        )
        
        # Create test person
        self.test_person = Person.create(
            name="John Doe",
            email="john.doe@example.com",
            role=Role.MEMBER
        )

    def test_register_person_success(self):
        """Test successful person registration"""
        # Arrange
        self.mock_person_repo.find_all.return_value = []  # No existing people
        
        # Act
        result = self.service.register_person(self.valid_command)
        
        # Assert
        assert isinstance(result, PersonId)
        self.mock_person_repo.find_all.assert_called_once()
        self.mock_person_repo.save.assert_called_once()
        
        # Verify the person passed to save has correct attributes
        saved_person = self.mock_person_repo.save.call_args[0][0]
        assert saved_person.name == "John Doe"
        assert saved_person.email == "john.doe@example.com"
        assert str(saved_person.role) == "MEMBER"

    def test_register_person_invalid_command(self):
        """Test registration with invalid command"""
        # Arrange
        invalid_command = RegisterPersonCommand(
            name="",  # Invalid empty name
            email="john.doe@example.com",
            role="member"
        )
        
        # Act & Assert
        try:
            self.service.register_person(invalid_command)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Name is required and cannot be empty" in str(e)
        
        # Verify repositories weren't called
        self.mock_person_repo.find_all.assert_not_called()
        self.mock_person_repo.save.assert_not_called()

    def test_register_person_email_already_exists(self):
        """Test registration with existing email"""
        # Arrange
        existing_person = Person.create(
            name="Jane Smith",
            email="john.doe@example.com",  # Same email as command
            role=Role.LEAD
        )
        self.mock_person_repo.find_all.return_value = [existing_person]
        
        # Act & Assert
        try:
            self.service.register_person(self.valid_command)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Person with email john.doe@example.com already exists" in str(e)
        
        # Verify find_all was called but save was not
        self.mock_person_repo.find_all.assert_called_once()
        self.mock_person_repo.save.assert_not_called()

    def test_register_person_with_lead_role(self):
        """Test registration with lead role"""
        # Arrange
        lead_command = RegisterPersonCommand(
            name="Jane Smith",
            email="jane.smith@example.com",
            role="lead"
        )
        self.mock_person_repo.find_all.return_value = []
        
        # Act
        result = self.service.register_person(lead_command)
        
        # Assert
        assert isinstance(result, PersonId)
        
        # Verify the person has correct role
        saved_person = self.mock_person_repo.save.call_args[0][0]
        assert str(saved_person.role) == "LEAD"

    def test_register_person_case_insensitive_role(self):
        """Test registration with different case roles (member/lead)"""
        test_cases = ["member", "lead", "MEMBER", "LEAD"]

        for role_input in test_cases:
            # Reset mocks
            self.mock_person_repo.reset_mock()
            self.mock_person_repo.find_all.return_value = []

            command = RegisterPersonCommand(
                name=f"Test User {role_input}",
                email=f"test_{role_input.lower()}@example.com",
                role=role_input
            )

            # Act
            result = self.service.register_person(command)

            # Assert
            assert isinstance(result, PersonId)
            self.mock_person_repo.save.assert_called_once()
            saved_person = self.mock_person_repo.save.call_args[0][0]
            expected_role = "MEMBER" if role_input.lower() == "member" else "LEAD"
            assert str(saved_person.role) == expected_role

    def test_get_person_profile_success(self):
        """Test successful person profile retrieval"""
        # Arrange
        test_person = Person.create(
            name="John Doe",
            email="john.doe@example.com",
            role=Role.MEMBER
        )
        # Set reputation score for testing using public method
        # Note: In real implementation, reputation would be updated through domain events
        # For testing purposes, we'll use reflection to access the internal field
        test_person.__dict__['_reputation_score'] = 75
        
        self.mock_person_repo.find_by_id.return_value = test_person
        
        # Act
        result = self.service.get_person_profile(self.valid_person_id, self.mock_auth_context)
        
        # Assert
        assert isinstance(result, PersonProfileDto)
        assert result.personId == str(test_person.person_id)
        assert result.name == "John Doe"
        assert result.email == "john.doe@example.com"
        assert result.role == "MEMBER"
        assert result.reputationScore == 75
        
        self.mock_person_repo.find_by_id.assert_called_once_with(self.valid_person_id)

    def test_get_person_profile_not_found(self):
        """Test person profile retrieval when person doesn't exist"""
        # Arrange
        self.mock_person_repo.find_by_id.return_value = None
        
        # Act & Assert
        try:
            self.service.get_person_profile(self.valid_person_id, self.mock_auth_context)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert f"Person not found: {self.valid_person_id}" in str(e)
        
        self.mock_person_repo.find_by_id.assert_called_once_with(self.valid_person_id)

    def test_get_person_profile_with_zero_reputation(self):
        """Test person profile with zero reputation score"""
        # Arrange
        test_person = Person.create(
            name="New User",
            email="new.user@example.com",
            role=Role.MEMBER
        )
        # New users start with 0 reputation
        assert test_person.reputation_score == 0
        
        self.mock_person_repo.find_by_id.return_value = test_person
        
        # Act
        result = self.service.get_person_profile(self.valid_person_id, self.mock_auth_context)
        
        # Assert
        assert result.reputationScore == 0

    def test_get_person_profile_with_negative_reputation(self):
        """Test person profile with negative reputation score"""
        # Arrange
        test_person = Person.create(
            name="Problematic User",
            email="problem.user@example.com",
            role=Role.MEMBER
        )
        # Manually set negative reputation for testing using reflection
        test_person.__dict__['_reputation_score'] = -25
        
        self.mock_person_repo.find_by_id.return_value = test_person
        
        # Act
        result = self.service.get_person_profile(self.valid_person_id, self.mock_auth_context)
        
        # Assert
        assert result.reputationScore == -25

    def test_get_leaderboard_success(self):
        """Test successful leaderboard retrieval"""
        # Arrange
        expected_leaderboard = [
            LeaderboardDto(
                personId="person1",
                name="Top Player",
                reputationScore=1000,
                rank=1
            ),
            LeaderboardDto(
                personId="person2", 
                name="Second Place",
                reputationScore=750,
                rank=2
            ),
            LeaderboardDto(
                personId="person3",
                name="Third Place",
                reputationScore=500,
                rank=3
            )
        ]
        
        self.mock_leaderboard_query_repo.get_leaderboard.return_value = expected_leaderboard
        
        # Act
        result = self.service.get_leaderboard(self.mock_auth_context)
        
        # Assert
        assert result == expected_leaderboard
        assert len(result) == 3
        assert result[0].rank < result[1].rank < result[2].rank
        assert result[0].reputationScore > result[1].reputationScore > result[2].reputationScore
        
        self.mock_leaderboard_query_repo.get_leaderboard.assert_called_once()

    def test_get_leaderboard_empty(self):
        """Test leaderboard retrieval when no users exist"""
        # Arrange
        self.mock_leaderboard_query_repo.get_leaderboard.return_value = []
        
        # Act
        result = self.service.get_leaderboard(self.mock_auth_context)
        
        # Assert
        assert result == []
        assert len(result) == 0
        
        self.mock_leaderboard_query_repo.get_leaderboard.assert_called_once()

    def test_get_leaderboard_single_user(self):
        """Test leaderboard with single user"""
        # Arrange
        single_user_leaderboard = [
            LeaderboardDto(
                personId="only_user",
                name="Only User",
                reputationScore=100,
                rank=1
            )
        ]
        
        self.mock_leaderboard_query_repo.get_leaderboard.return_value = single_user_leaderboard
        
        # Act
        result = self.service.get_leaderboard(self.mock_auth_context)
        
        # Assert
        assert len(result) == 1
        assert result[0].rank == 1
        assert result[0].name == "Only User"

    def test_register_multiple_people_different_emails(self):
        """Test registering multiple people with different emails"""
        # Arrange
        commands = [
            RegisterPersonCommand(name="User 1", email="user1@example.com", role="member"),
            RegisterPersonCommand(name="User 2", email="user2@example.com", role="lead"),
            RegisterPersonCommand(name="User 3", email="user3@example.com", role="member")
        ]
        
        # Start with empty repository, then add people as they're registered
        existing_people: List[Any] = []
        
        def mock_find_all() -> List[Any]:
            return existing_people.copy()
        
        def mock_save(person: Any) -> None:
            existing_people.append(person)
        
        self.mock_person_repo.find_all.side_effect = mock_find_all
        self.mock_person_repo.save.side_effect = mock_save
        
        # Act & Assert
        results: List[PersonId] = []
        for command in commands:
            result = self.service.register_person(command)
            results.append(result)
            assert isinstance(result, PersonId)
        
        # Verify all different
        assert len(set(str(r) for r in results)) == 3
        
        # Verify save was called for each
        assert self.mock_person_repo.save.call_count == 3

    def test_service_constructor_with_dependencies(self):
        """Test service constructor properly stores dependencies"""
        # Create new service instance
        service = PersonApplicationService(
            person_repo=self.mock_person_repo,
            leaderboard_query_repo=self.mock_leaderboard_query_repo,
            authorization_service=self.mock_authorization_service
        )
        
        # Verify dependencies are stored (using reflection for testing)
        assert service.__dict__.get('_person_repo') is self.mock_person_repo
        assert service.__dict__.get('_leaderboard_query_repo') is self.mock_leaderboard_query_repo
        assert service.__dict__.get('_authorization_service') is self.mock_authorization_service

    def test_register_person_repository_exception_handling(self):
        """Test handling of repository exceptions during registration"""
        # Arrange
        self.mock_person_repo.find_all.return_value = []
        self.mock_person_repo.save.side_effect = Exception("Database connection error")
        
        # Act & Assert
        try:
            self.service.register_person(self.valid_command)
            assert False, "Should have raised Exception"
        except Exception as e:
            assert "Database connection error" in str(e)

    def test_get_person_profile_repository_exception_handling(self):
        """Test handling of repository exceptions during profile retrieval"""
        # Arrange
        self.mock_person_repo.find_by_id.side_effect = Exception("Database connection error")
        
        # Act & Assert
        try:
            self.service.get_person_profile(self.valid_person_id, self.mock_auth_context)
            assert False, "Should have raised Exception"
        except Exception as e:
            assert "Database connection error" in str(e)

    def test_get_leaderboard_repository_exception_handling(self):
        """Test handling of repository exceptions during leaderboard retrieval"""
        # Arrange
        self.mock_leaderboard_query_repo.get_leaderboard.side_effect = Exception("Query service unavailable")
        
        # Act & Assert
        try:
            self.service.get_leaderboard(self.mock_auth_context)
            assert False, "Should have raised Exception"
        except Exception as e:
            assert "Query service unavailable" in str(e)

    def test_register_person_with_special_characters(self):
        """Test registration with special characters in name"""
        # Arrange
        special_command = RegisterPersonCommand(
            name="José María O'Connor-Smith",
            email="jose.maria@example.com",
            role="member"
        )
        self.mock_person_repo.find_all.return_value = []
        
        # Act
        result = self.service.register_person(special_command)
        
        # Assert
        assert isinstance(result, PersonId)
        saved_person = self.mock_person_repo.save.call_args[0][0]
        assert saved_person.name == "José María O'Connor-Smith"

    def test_case_sensitivity_email_duplicate_check(self):
        """Test that email duplicate check is case sensitive"""
        # Arrange
        existing_person = Person.create(
            name="Existing User",
            email="USER@EXAMPLE.COM",  # Uppercase email
            role=Role.MEMBER
        )
        self.mock_person_repo.find_all.return_value = [existing_person]
        
        command = RegisterPersonCommand(
            name="New User",
            email="user@example.com",  # Lowercase email
            role="member"
        )
        
        # Act - Should succeed because emails are different case
        result = self.service.register_person(command)
        
        # Assert
        assert isinstance(result, PersonId)
        self.mock_person_repo.save.assert_called_once()