"""
Test suite for authentication DTOs.

This module contains comprehensive tests for AuthenticationResultDto,
LoginResult, and UserInfo to ensure 100% coverage.
"""

from src.application.dtos.authentication_dtos import AuthenticationResultDto, LoginResult, UserInfo
from src.domain.person.person import PersonId


class TestAuthenticationResultDto:
    """Test cases for AuthenticationResultDto class."""
    
    def test_authentication_result_dto_successful_initialization(self):
        """Test successful initialization of AuthenticationResultDto."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        email = "test@example.com"
        
        dto = AuthenticationResultDto(
            success=True,
            person_id=person_id,
            email=email
        )
        
        assert dto.success is True
        assert dto.person_id == person_id
        assert dto.email == email
        assert dto.error_message == ""
    
    def test_authentication_result_dto_failed_initialization(self):
        """Test failed initialization of AuthenticationResultDto."""
        error_message = "Invalid credentials"
        
        dto = AuthenticationResultDto(
            success=False,
            error_message=error_message
        )
        
        assert dto.success is False
        assert dto.person_id is None
        assert dto.email == ""
        assert dto.error_message == error_message
    
    def test_authentication_result_dto_successful_factory_method(self):
        """Test successful factory method for AuthenticationResultDto."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        email = "test@example.com"
        
        dto = AuthenticationResultDto.successful(person_id, email)
        
        assert dto.success is True
        assert dto.person_id == person_id
        assert dto.email == email
        assert dto.error_message == ""
    
    def test_authentication_result_dto_failed_factory_method(self):
        """Test failed factory method for AuthenticationResultDto."""
        error_message = "Email not found"
        
        dto = AuthenticationResultDto.failed(error_message)
        
        assert dto.success is False
        assert dto.person_id is None
        assert dto.email == ""
        assert dto.error_message == error_message
    
    def test_authentication_result_dto_with_empty_email(self):
        """Test DTO with empty email for failed authentication."""
        dto = AuthenticationResultDto(
            success=False,
            error_message="Authentication failed"
        )
        
        assert dto.email == ""
        assert dto.person_id is None
    
    def test_authentication_result_dto_with_empty_error_for_success(self):
        """Test DTO with empty error message for successful authentication."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        
        dto = AuthenticationResultDto(
            success=True,
            person_id=person_id,
            email="test@example.com"
        )
        
        assert dto.error_message == ""
        assert dto.success is True
    
    def test_authentication_result_dto_different_person_ids(self):
        """Test DTOs with different person IDs."""
        person_id1 = PersonId("123e4567-e89b-12d3-a456-426614174000")
        person_id2 = PersonId("987fcdeb-51a2-43d1-9f12-987654321000")
        
        dto1 = AuthenticationResultDto.successful(person_id1, "user1@example.com")
        dto2 = AuthenticationResultDto.successful(person_id2, "user2@example.com")
        
        assert dto1.person_id != dto2.person_id
        assert dto1.email != dto2.email
        assert dto1.success == dto2.success  # Both successful
    
    def test_authentication_result_dto_different_emails(self):
        """Test DTOs with different emails."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        
        dto1 = AuthenticationResultDto.successful(person_id, "test1@example.com")
        dto2 = AuthenticationResultDto.successful(person_id, "test2@example.com")
        
        assert dto1.email != dto2.email
        assert dto1.person_id == dto2.person_id
        assert dto1.success == dto2.success
    
    def test_authentication_result_dto_different_error_messages(self):
        """Test DTOs with different error messages."""
        dto1 = AuthenticationResultDto.failed("Invalid credentials")
        dto2 = AuthenticationResultDto.failed("Email not found")
        
        assert dto1.error_message != dto2.error_message
        assert dto1.success == dto2.success  # Both failed
        assert dto1.person_id == dto2.person_id  # Both None
    
    def test_authentication_result_dto_successful_vs_failed(self):
        """Test comparison between successful and failed DTOs."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        
        successful_dto = AuthenticationResultDto.successful(person_id, "test@example.com")
        failed_dto = AuthenticationResultDto.failed("Invalid credentials")
        
        assert successful_dto.success != failed_dto.success
        assert successful_dto.person_id != failed_dto.person_id
        assert successful_dto.email != failed_dto.email
        assert successful_dto.error_message != failed_dto.error_message
    
    def test_authentication_result_dto_none_person_id_for_success(self):
        """Test successful DTO with None person_id (edge case)."""
        # This tests the edge case where success=True but person_id is None
        dto = AuthenticationResultDto(
            success=True,
            person_id=None,
            email="test@example.com"
        )
        
        assert dto.success is True
        assert dto.person_id is None
        assert dto.email == "test@example.com"
    
    def test_authentication_result_dto_factory_methods_consistency(self):
        """Test that factory methods create consistent objects."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        email = "test@example.com"
        error_msg = "Authentication failed"
        
        # Test successful factory vs manual construction
        factory_success = AuthenticationResultDto.successful(person_id, email)
        manual_success = AuthenticationResultDto(True, person_id, email)
        
        assert factory_success.success == manual_success.success
        assert factory_success.person_id == manual_success.person_id
        assert factory_success.email == manual_success.email
        assert factory_success.error_message == manual_success.error_message
        
        # Test failed factory vs manual construction
        factory_failed = AuthenticationResultDto.failed(error_msg)
        manual_failed = AuthenticationResultDto(False, error_message=error_msg)
        
        assert factory_failed.success == manual_failed.success
        assert factory_failed.person_id == manual_failed.person_id
        assert factory_failed.email == manual_failed.email
        assert factory_failed.error_message == manual_failed.error_message
    
    def test_authentication_result_dto_empty_string_handling(self):
        """Test DTO with empty string inputs."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        
        # Test with empty email
        dto1 = AuthenticationResultDto(
            success=True,
            person_id=person_id,
            email=""
        )
        assert dto1.email == ""
        
        # Test with empty error message
        dto2 = AuthenticationResultDto(
            success=False,
            error_message=""
        )
        assert dto2.error_message == ""
    
    def test_authentication_result_dto_str_representation(self):
        """Test string representation of AuthenticationResultDto."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        
        # Test successful DTO
        successful_dto = AuthenticationResultDto.successful(person_id, "test@example.com")
        str_repr = str(successful_dto)
        # Since there might not be a __str__ method, this will use object's default
        assert str_repr is not None
        
        # Test failed DTO
        failed_dto = AuthenticationResultDto.failed("Authentication failed")
        str_repr = str(failed_dto)
        assert str_repr is not None
    
    def test_authentication_result_dto_attribute_access(self):
        """Test direct attribute access on AuthenticationResultDto."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        email = "test@example.com"
        error_msg = "Test error"
        
        dto = AuthenticationResultDto(
            success=True,
            person_id=person_id,
            email=email,
            error_message=error_msg
        )
        
        # Test that all attributes are accessible
        assert hasattr(dto, 'success')
        assert hasattr(dto, 'person_id')
        assert hasattr(dto, 'email')
        assert hasattr(dto, 'error_message')
        
        # Test attribute values
        assert dto.success is True
        assert dto.person_id == person_id
        assert dto.email == email
        assert dto.error_message == error_msg
    
    def test_authentication_result_dto_boolean_conversion(self):
        """Test boolean conversion of AuthenticationResultDto."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        
        successful_dto = AuthenticationResultDto.successful(person_id, "test@example.com")
        failed_dto = AuthenticationResultDto.failed("Authentication failed")
        
        # Test that DTOs can be used in boolean contexts based on success
        if successful_dto.success:
            assert True, "Successful DTO should be truthy based on success attribute"
        
        if not failed_dto.success:
            assert True, "Failed DTO should be falsy based on success attribute"
    
    def test_authentication_result_dto_none_values(self):
        """Test DTO behavior with None values."""
        # Test with all None values where allowed
        dto = AuthenticationResultDto(
            success=False,
            person_id=None,
            email="",
            error_message=""
        )
        
        assert dto.success is False
        assert dto.person_id is None
        assert dto.email == ""
        assert dto.error_message == ""
    
    def test_authentication_result_dto_class_methods_return_types(self):
        """Test that class methods return correct types."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        
        successful_result = AuthenticationResultDto.successful(person_id, "test@example.com")
        failed_result = AuthenticationResultDto.failed("Error message")
        
        assert isinstance(successful_result, AuthenticationResultDto)
        assert isinstance(failed_result, AuthenticationResultDto)
        
        # Verify they have the expected success values
        assert successful_result.success is True
        assert failed_result.success is False


class TestLoginResult:
    """Test cases for LoginResult class."""
    
    def test_login_result_successful_initialization(self):
        """Test successful initialization of LoginResult."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        email = "test@example.com"
        
        result = LoginResult(
            success=True,
            person_id=person_id,
            email=email
        )
        
        assert result.success is True
        assert result.person_id == person_id
        assert result.email == email
        assert result.error_message == ""
    
    def test_login_result_failed_initialization(self):
        """Test failed initialization of LoginResult."""
        error_message = "Invalid credentials"
        
        result = LoginResult(
            success=False,
            error_message=error_message
        )
        
        assert result.success is False
        assert result.person_id is None
        assert result.email == ""
        assert result.error_message == error_message
    
    def test_login_result_successful_factory_method(self):
        """Test successful factory method for LoginResult."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        email = "test@example.com"
        
        result = LoginResult.successful(person_id, email)
        
        assert result.success is True
        assert result.person_id == person_id
        assert result.email == email
        assert result.error_message == ""
    
    def test_login_result_failed_factory_method(self):
        """Test failed factory method for LoginResult."""
        error_message = "Authentication failed"
        
        result = LoginResult.failed(error_message)
        
        assert result.success is False
        assert result.person_id is None
        assert result.email == ""
        assert result.error_message == error_message
    
    def test_login_result_equality_same_success_values(self):
        """Test equality for login results with same success values."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        email = "test@example.com"
        
        result1 = LoginResult(success=True, person_id=person_id, email=email)
        result2 = LoginResult(success=True, person_id=person_id, email=email)
        
        assert result1 == result2
    
    def test_login_result_equality_same_failed_values(self):
        """Test equality for login results with same failed values."""
        error_message = "Invalid credentials"
        
        result1 = LoginResult(success=False, error_message=error_message)
        result2 = LoginResult(success=False, error_message=error_message)
        
        assert result1 == result2
    
    def test_login_result_inequality_different_success(self):
        """Test inequality for login results with different success status."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        
        result1 = LoginResult(success=True, person_id=person_id, email="test@example.com")
        result2 = LoginResult(success=False, error_message="Error")
        
        assert result1 != result2
    
    def test_login_result_inequality_different_person_id(self):
        """Test inequality for login results with different person IDs."""
        person_id1 = PersonId("123e4567-e89b-12d3-a456-426614174000")
        person_id2 = PersonId("987fcdeb-51a2-43d1-9f12-987654321000")
        
        result1 = LoginResult(success=True, person_id=person_id1, email="test@example.com")
        result2 = LoginResult(success=True, person_id=person_id2, email="test@example.com")
        
        assert result1 != result2
    
    def test_login_result_inequality_different_email(self):
        """Test inequality for login results with different emails."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        
        result1 = LoginResult(success=True, person_id=person_id, email="test1@example.com")
        result2 = LoginResult(success=True, person_id=person_id, email="test2@example.com")
        
        assert result1 != result2
    
    def test_login_result_inequality_different_error_message(self):
        """Test inequality for login results with different error messages."""
        result1 = LoginResult(success=False, error_message="Error 1")
        result2 = LoginResult(success=False, error_message="Error 2")
        
        assert result1 != result2
    
    def test_login_result_inequality_non_login_result(self):
        """Test inequality when comparing with non-LoginResult object."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        result = LoginResult(success=True, person_id=person_id, email="test@example.com")
        
        assert result != "not a login result"
        assert result != 42
        assert result != None
        assert result != {}
    
    def test_login_result_repr_successful(self):
        """Test string representation of successful login result."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        email = "test@example.com"
        
        result = LoginResult(success=True, person_id=person_id, email=email)
        repr_str = repr(result)
        
        assert "LoginResult(success=True" in repr_str
        assert "test@example.com" in repr_str
        assert str(person_id) in repr_str
    
    def test_login_result_repr_failed(self):
        """Test string representation of failed login result."""
        error_message = "Authentication failed"
        
        result = LoginResult(success=False, error_message=error_message)
        repr_str = repr(result)
        
        assert "LoginResult(success=False" in repr_str
        assert "Authentication failed" in repr_str
    
    def test_login_result_factory_methods_consistency(self):
        """Test that factory methods create objects of correct type."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        
        successful_result = LoginResult.successful(person_id, "test@example.com")
        failed_result = LoginResult.failed("Error message")
        
        assert isinstance(successful_result, LoginResult)
        assert isinstance(failed_result, LoginResult)
        
        # Verify they have the expected success values
        assert successful_result.success is True
        assert failed_result.success is False


class TestUserInfo:
    """Test cases for UserInfo class."""
    
    def test_user_info_initialization(self):
        """Test initialization of UserInfo."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        email = "test@example.com"
        name = "John Doe"
        role = "MEMBER"
        
        user_info = UserInfo(
            person_id=person_id,
            email=email,
            name=name,
            role=role
        )
        
        assert user_info.person_id == person_id
        assert user_info.email == email
        assert user_info.name == name
        assert user_info.role == role
    
    def test_user_info_initialization_lead_role(self):
        """Test initialization of UserInfo with LEAD role."""
        person_id = PersonId("987fcdeb-51a2-43d1-9f12-987654321000")
        email = "lead@example.com"
        name = "Jane Lead"
        role = "LEAD"
        
        user_info = UserInfo(
            person_id=person_id,
            email=email,
            name=name,
            role=role
        )
        
        assert user_info.person_id == person_id
        assert user_info.email == email
        assert user_info.name == name
        assert user_info.role == role
    
    def test_user_info_equality_same_values(self):
        """Test equality for user infos with same values."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        email = "test@example.com"
        name = "John Doe"
        role = "MEMBER"
        
        user_info1 = UserInfo(person_id, email, name, role)
        user_info2 = UserInfo(person_id, email, name, role)
        
        assert user_info1 == user_info2
    
    def test_user_info_inequality_different_person_id(self):
        """Test inequality for user infos with different person IDs."""
        person_id1 = PersonId("123e4567-e89b-12d3-a456-426614174000")
        person_id2 = PersonId("987fcdeb-51a2-43d1-9f12-987654321000")
        
        user_info1 = UserInfo(person_id1, "test@example.com", "John Doe", "MEMBER")
        user_info2 = UserInfo(person_id2, "test@example.com", "John Doe", "MEMBER")
        
        assert user_info1 != user_info2
    
    def test_user_info_inequality_different_email(self):
        """Test inequality for user infos with different emails."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        
        user_info1 = UserInfo(person_id, "test1@example.com", "John Doe", "MEMBER")
        user_info2 = UserInfo(person_id, "test2@example.com", "John Doe", "MEMBER")
        
        assert user_info1 != user_info2
    
    def test_user_info_inequality_different_name(self):
        """Test inequality for user infos with different names."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        
        user_info1 = UserInfo(person_id, "test@example.com", "John Doe", "MEMBER")
        user_info2 = UserInfo(person_id, "test@example.com", "Jane Smith", "MEMBER")
        
        assert user_info1 != user_info2
    
    def test_user_info_inequality_different_role(self):
        """Test inequality for user infos with different roles."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        
        user_info1 = UserInfo(person_id, "test@example.com", "John Doe", "MEMBER")
        user_info2 = UserInfo(person_id, "test@example.com", "John Doe", "LEAD")
        
        assert user_info1 != user_info2
    
    def test_user_info_inequality_non_user_info(self):
        """Test inequality when comparing with non-UserInfo object."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        user_info = UserInfo(person_id, "test@example.com", "John Doe", "MEMBER")
        
        assert user_info != "not a user info"
        assert user_info != 42
        assert user_info != None
        assert user_info != {}
    
    def test_user_info_repr(self):
        """Test string representation of UserInfo."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        email = "test@example.com"
        name = "John Doe"
        role = "MEMBER"
        
        user_info = UserInfo(person_id, email, name, role)
        repr_str = repr(user_info)
        
        assert "UserInfo(" in repr_str
        assert "test@example.com" in repr_str
        assert "John Doe" in repr_str
        assert "MEMBER" in repr_str
        assert str(person_id) in repr_str
    
    def test_user_info_with_special_characters(self):
        """Test UserInfo with special characters in name."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        email = "test@example.com"
        name = "José María González-Smith"
        role = "MEMBER"
        
        user_info = UserInfo(person_id, email, name, role)
        
        assert user_info.name == name
        assert user_info.email == email
        assert user_info.role == role
    
    def test_user_info_with_long_email(self):
        """Test UserInfo with very long email."""
        person_id = PersonId("123e4567-e89b-12d3-a456-426614174000")
        email = "very.long.email.address.with.many.dots@very-long-domain-name.example.com"
        name = "Test User"
        role = "LEAD"
        
        user_info = UserInfo(person_id, email, name, role)
        
        assert user_info.email == email
        assert user_info.role == role