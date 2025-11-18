"""RegisterPersonCommand - Command object for person registration"""

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class RegisterPersonCommand:
    """
    Command for registering a new person in the system.
    
    Attributes:
        name: Full name of the person
        email: Email address (must be valid format)
        role: Role in the system ('member' or 'lead')
    """
    name: str
    email: str
    role: str
    
    def validate(self) -> None:
        """
        Validates the command fields according to business rules.
        
        Raises:
            ValueError: If any validation fails
        """
        if not self.name or not self.name.strip():
            raise ValueError("Name is required and cannot be empty")
        
        if not self.email or not self.email.strip():
            raise ValueError("Email is required and cannot be empty")
        
        # Email format validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, self.email):
            raise ValueError("Email must be in valid format")
        
        if not self.role or not self.role.strip():
            raise ValueError("Role is required and cannot be empty")
        # Normalize role for validation
        role = self.role.lower().strip()
        valid_roles = ['member', 'lead']
        if role not in valid_roles:
            raise ValueError(f"Role must be one of: {', '.join(valid_roles)}")