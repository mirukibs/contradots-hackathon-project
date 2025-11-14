"""
Comprehensive API Usage Examples and Testing Guide

This module provides practical examples for using the Social Scoring System API,
including complete workflows, cURL commands, and integration testing patterns.
"""

# =======================
# COMPLETE WORKFLOW EXAMPLES
# =======================

class APIWorkflowExamples:
    """
    Complete API workflow demonstrations showing realistic usage patterns
    for the Social Scoring System.
    """
    
    @staticmethod
    def complete_system_workflow():
        """
        Demonstrates the complete system workflow from user registration
        to action validation and leaderboard checking.
        """
        return {
            "title": "Complete System Workflow",
            "description": "End-to-end example showing all major system functions",
            "steps": [
                {
                    "step_number": 1,
                    "title": "Register Activity Lead",
                    "description": "Create a user with LEAD privileges to manage activities",
                    "endpoint": {
                        "method": "POST",
                        "url": "http://localhost:5000/api/v1/person/register",
                        "headers": {
                            "Content-Type": "application/json"
                        },
                        "body": {
                            "name": "Sarah Environmental",
                            "email": "sarah@greeninitiative.org",
                            "role": "LEAD"
                        }
                    },
                    "expected_response": {
                        "status": 201,
                        "body": {
                            "personId": "550e8400-e29b-41d4-a716-446655440000",
                            "message": "User registered successfully"
                        }
                    },
                    "curl_command": '''curl -X POST "http://localhost:5000/api/v1/person/register" \\
  -H "Content-Type: application/json" \\
  -d '{
    "name": "Sarah Environmental",
    "email": "sarah@greeninitiative.org", 
    "role": "LEAD"
  }' '''
                },
                
                {
                    "step_number": 2,
                    "title": "Authenticate Lead User",
                    "description": "Get JWT token for the lead user to access protected endpoints",
                    "endpoint": {
                        "method": "POST",
                        "url": "http://localhost:5000/api/v1/person/authenticate",
                        "headers": {
                            "Content-Type": "application/json"
                        },
                        "body": {
                            "email": "sarah@greeninitiative.org",
                            "password": "SecurePassword123!"
                        }
                    },
                    "expected_response": {
                        "status": 200,
                        "body": {
                            "accessToken": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                            "refreshToken": "refresh_token_example...",
                            "personId": "550e8400-e29b-41d4-a716-446655440000",
                            "email": "sarah@greeninitiative.org",
                            "roles": ["LEAD"],
                            "expiresAt": "2024-01-01T13:00:00Z"
                        }
                    },
                    "curl_command": '''curl -X POST "http://localhost:5000/api/v1/person/authenticate" \\
  -H "Content-Type: application/json" \\
  -d '{
    "email": "sarah@greeninitiative.org",
    "password": "SecurePassword123!"
  }' ''',
                    "note": "Save the accessToken for subsequent requests requiring authentication"
                },
                
                {
                    "step_number": 3,
                    "title": "Create Environmental Activity",
                    "description": "Lead user creates a new activity for community participation",
                    "endpoint": {
                        "method": "POST",
                        "url": "http://localhost:5000/api/v1/activity",
                        "headers": {
                            "Content-Type": "application/json",
                            "Authorization": "Bearer <LEAD_JWT_TOKEN>"
                        },
                        "body": {
                            "name": "Coastal Cleanup Initiative",
                            "description": "Community-driven cleanup of plastic waste from coastal areas. Participants collect and sort recyclable materials while documenting environmental impact through blockchain-verified proof of work.",
                            "points": 75
                        }
                    },
                    "expected_response": {
                        "status": 201,
                        "body": {
                            "activityId": "a1b2c3d4-e5f6-7890-abcd-123456789abc",
                            "message": "Activity created successfully"
                        }
                    },
                    "curl_command": '''curl -X POST "http://localhost:5000/api/v1/activity" \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer <LEAD_JWT_TOKEN>" \\
  -d '{
    "name": "Coastal Cleanup Initiative",
    "description": "Community-driven cleanup of plastic waste from coastal areas...",
    "points": 75
  }' '''
                },
                
                {
                    "step_number": 4,
                    "title": "Register Community Members",
                    "description": "Register multiple users who will participate in activities",
                    "endpoints": [
                        {
                            "member": "Alex Community",
                            "endpoint": {
                                "method": "POST",
                                "url": "http://localhost:5000/api/v1/person/register",
                                "body": {
                                    "name": "Alex Community",
                                    "email": "alex@community.org",
                                    "role": "MEMBER"
                                }
                            }
                        },
                        {
                            "member": "Maria Volunteer", 
                            "endpoint": {
                                "method": "POST",
                                "url": "http://localhost:5000/api/v1/person/register",
                                "body": {
                                    "name": "Maria Volunteer",
                                    "email": "maria@volunteers.net",
                                    "role": "MEMBER"
                                }
                            }
                        }
                    ],
                    "bulk_curl_example": '''# Register multiple members
for member in "alex@community.org" "maria@volunteers.net"; do
  name=$(echo $member | cut -d'@' -f1 | sed 's/[^a-zA-Z]/ /g' | sed 's/.*/\\u&/')
  curl -X POST "http://localhost:5000/api/v1/person/register" \\
    -H "Content-Type: application/json" \\
    -d "{\"name\": \"$name\", \"email\": \"$member\", \"role\": \"MEMBER\"}"
done'''
                },
                
                {
                    "step_number": 5,
                    "title": "Members Authenticate and View Activities",
                    "description": "Community members authenticate and view available activities",
                    "sequence": [
                        {
                            "action": "Authenticate Alex",
                            "endpoint": {
                                "method": "POST",
                                "url": "http://localhost:5000/api/v1/person/authenticate",
                                "body": {
                                    "email": "alex@community.org",
                                    "password": "password123"
                                }
                            }
                        },
                        {
                            "action": "View Available Activities",
                            "endpoint": {
                                "method": "GET",
                                "url": "http://localhost:5000/api/v1/activity",
                                "headers": {
                                    "Authorization": "Bearer <ALEX_JWT_TOKEN>"
                                }
                            },
                            "expected_response": {
                                "status": 200,
                                "body": {
                                    "activities": [
                                        {
                                            "activityId": "a1b2c3d4-e5f6-7890-abcd-123456789abc",
                                            "name": "Coastal Cleanup Initiative",
                                            "description": "Community-driven cleanup...",
                                            "points": 75,
                                            "leadName": "Sarah Environmental",
                                            "isActive": True,
                                            "participantCount": 0
                                        }
                                    ],
                                    "totalCount": 1
                                }
                            }
                        }
                    ]
                },
                
                {
                    "step_number": 6,
                    "title": "Submit Environmental Actions",
                    "description": "Community members submit completed environmental actions with blockchain proof",
                    "submissions": [
                        {
                            "member": "Alex",
                            "endpoint": {
                                "method": "POST",
                                "url": "http://localhost:5000/api/v1/action",
                                "headers": {
                                    "Authorization": "Bearer <ALEX_JWT_TOKEN>",
                                    "Content-Type": "application/json"
                                },
                                "body": {
                                    "activityId": "a1b2c3d4-e5f6-7890-abcd-123456789abc",
                                    "description": "Collected 12kg of plastic waste from Bondi Beach section A, sorted into recyclables and non-recyclables. Documented GPS coordinates and before/after photos.",
                                    "proofHash": "0x1a2b3c4d5e6f789012345678901234567890abcdef1234567890abcdef123456"
                                }
                            }
                        },
                        {
                            "member": "Maria",
                            "endpoint": {
                                "method": "POST",
                                "url": "http://localhost:5000/api/v1/action",
                                "headers": {
                                    "Authorization": "Bearer <MARIA_JWT_TOKEN>",
                                    "Content-Type": "application/json"
                                },
                                "body": {
                                    "activityId": "a1b2c3d4-e5f6-7890-abcd-123456789abc",
                                    "description": "Organized community group of 8 volunteers for beach cleanup, collected 25kg total waste including microplastics filtering. Team coordination and environmental education provided.",
                                    "proofHash": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
                                }
                            }
                        }
                    ],
                    "expected_responses": {
                        "status": 201,
                        "body": {
                            "actionId": "action_uuid_here",
                            "message": "Action submitted for verification",
                            "status": "SUBMITTED"
                        }
                    }
                },
                
                {
                    "step_number": 7,
                    "title": "Lead Reviews Pending Actions",
                    "description": "Activity lead reviews and validates submitted actions",
                    "sequence": [
                        {
                            "action": "Get Pending Validations",
                            "endpoint": {
                                "method": "GET", 
                                "url": "http://localhost:5000/api/v1/action/pending",
                                "headers": {
                                    "Authorization": "Bearer <LEAD_JWT_TOKEN>"
                                }
                            },
                            "expected_response": {
                                "body": {
                                    "pendingActions": [
                                        {
                                            "actionId": "alex_action_id",
                                            "personName": "Alex Community",
                                            "activityName": "Coastal Cleanup Initiative",
                                            "description": "Collected 12kg of plastic waste...",
                                            "status": "SUBMITTED",
                                            "submittedAt": "2024-01-01T10:30:00Z"
                                        },
                                        {
                                            "actionId": "maria_action_id",
                                            "personName": "Maria Volunteer",
                                            "activityName": "Coastal Cleanup Initiative", 
                                            "description": "Organized community group...",
                                            "status": "SUBMITTED",
                                            "submittedAt": "2024-01-01T11:15:00Z"
                                        }
                                    ],
                                    "totalCount": 2
                                }
                            }
                        },
                        {
                            "action": "Validate Alex's Action",
                            "endpoint": {
                                "method": "POST",
                                "url": "http://localhost:5000/api/v1/action/<alex_action_id>/validate",
                                "headers": {
                                    "Authorization": "Bearer <LEAD_JWT_TOKEN>",
                                    "Content-Type": "application/json"
                                },
                                "body": {
                                    "isValid": True,
                                    "notes": "Excellent documentation and proof verification confirmed on blockchain. Good environmental impact."
                                }
                            }
                        },
                        {
                            "action": "Validate Maria's Action",
                            "endpoint": {
                                "method": "POST", 
                                "url": "http://localhost:5000/api/v1/action/<maria_action_id>/validate",
                                "headers": {
                                    "Authorization": "Bearer <LEAD_JWT_TOKEN>",
                                    "Content-Type": "application/json"
                                },
                                "body": {
                                    "isValid": True,
                                    "notes": "Outstanding team leadership and coordination. Exceptional environmental impact with community engagement."
                                }
                            }
                        }
                    ]
                },
                
                {
                    "step_number": 8,
                    "title": "Check Updated Leaderboard",
                    "description": "View the updated leaderboard showing reputation scores after action validation",
                    "endpoint": {
                        "method": "GET",
                        "url": "http://localhost:5000/api/v1/person/leaderboard",
                        "headers": {}  # Public endpoint
                    },
                    "expected_response": {
                        "status": 200,
                        "body": {
                            "leaderboard": [
                                {
                                    "personId": "maria_person_id",
                                    "name": "Maria Volunteer",
                                    "reputationScore": 75,
                                    "rank": 1,
                                    "activityCount": 1
                                },
                                {
                                    "personId": "alex_person_id",
                                    "name": "Alex Community",
                                    "reputationScore": 75,
                                    "rank": 2,
                                    "activityCount": 1
                                },
                                {
                                    "personId": "550e8400-e29b-41d4-a716-446655440000",
                                    "name": "Sarah Environmental",
                                    "reputationScore": 0,
                                    "rank": 3,
                                    "activityCount": 0
                                }
                            ],
                            "totalCount": 3
                        }
                    },
                    "curl_command": '''curl -X GET "http://localhost:5000/api/v1/person/leaderboard"'''
                }
            ],
            
            "summary": {
                "workflow_description": "Complete system demonstration showing user registration, activity creation, action submission, validation, and leaderboard updates",
                "participants": 3,
                "activities_created": 1,
                "actions_submitted": 2,
                "actions_validated": 2,
                "total_points_awarded": 150
            }
        }
    
    @staticmethod
    def error_handling_scenarios():
        """
        Examples of error scenarios and proper error handling patterns.
        """
        return {
            "title": "Error Handling Scenarios",
            "description": "Common error situations and expected API responses",
            "scenarios": [
                {
                    "scenario": "Authentication Required",
                    "description": "Accessing protected endpoint without authentication",
                    "request": {
                        "method": "GET",
                        "url": "http://localhost:5000/api/v1/person/profile",
                        "headers": {}  # No Authorization header
                    },
                    "expected_response": {
                        "status": 401,
                        "body": {
                            "error": {
                                "message": "Authentication required. Please provide a valid JWT token.",
                                "code": "AUTH_TOKEN_MISSING"
                            }
                        }
                    },
                    "curl_command": '''curl -X GET "http://localhost:5000/api/v1/person/profile"'''
                },
                
                {
                    "scenario": "Invalid JWT Token",
                    "description": "Using expired or invalid JWT token",
                    "request": {
                        "method": "GET",
                        "url": "http://localhost:5000/api/v1/person/profile",
                        "headers": {
                            "Authorization": "Bearer invalid.jwt.token"
                        }
                    },
                    "expected_response": {
                        "status": 401,
                        "body": {
                            "error": {
                                "message": "Invalid authentication token",
                                "code": "AUTH_TOKEN_INVALID"
                            }
                        }
                    }
                },
                
                {
                    "scenario": "Insufficient Permissions",
                    "description": "MEMBER trying to create activity (LEAD only)",
                    "request": {
                        "method": "POST",
                        "url": "http://localhost:5000/api/v1/activity",
                        "headers": {
                            "Authorization": "Bearer <MEMBER_JWT_TOKEN>",
                            "Content-Type": "application/json"
                        },
                        "body": {
                            "name": "New Activity",
                            "description": "Test activity",
                            "points": 50
                        }
                    },
                    "expected_response": {
                        "status": 403,
                        "body": {
                            "error": {
                                "message": "LEAD role required for this operation",
                                "code": "AUTH_INSUFFICIENT_PERMISSIONS"
                            }
                        }
                    }
                },
                
                {
                    "scenario": "Validation Error",
                    "description": "Invalid data in request body",
                    "request": {
                        "method": "POST",
                        "url": "http://localhost:5000/api/v1/person/register",
                        "headers": {
                            "Content-Type": "application/json"
                        },
                        "body": {
                            "name": "",  # Empty name
                            "email": "invalid-email",  # Invalid email format
                            "role": "INVALID_ROLE"  # Invalid role
                        }
                    },
                    "expected_response": {
                        "status": 400,
                        "body": {
                            "error": {
                                "message": "Validation error in request data",
                                "code": "VALIDATION_ERROR",
                                "validationErrors": [
                                    {
                                        "field": "name",
                                        "message": "Name must be at least 2 characters long",
                                        "code": "VALIDATION_LENGTH_INSUFFICIENT"
                                    },
                                    {
                                        "field": "email",
                                        "message": "Invalid email format",
                                        "code": "VALIDATION_INVALID_FORMAT"
                                    },
                                    {
                                        "field": "role",
                                        "message": "Role must be either MEMBER or LEAD",
                                        "code": "VALIDATION_INVALID_VALUE"
                                    }
                                ]
                            }
                        }
                    }
                },
                
                {
                    "scenario": "Resource Not Found",
                    "description": "Accessing non-existent resource",
                    "request": {
                        "method": "GET",
                        "url": "http://localhost:5000/api/v1/activity/non-existent-uuid",
                        "headers": {
                            "Authorization": "Bearer <VALID_JWT_TOKEN>"
                        }
                    },
                    "expected_response": {
                        "status": 404,
                        "body": {
                            "error": {
                                "message": "Activity not found",
                                "code": "ACTIVITY_NOT_FOUND"
                            }
                        }
                    }
                },
                
                {
                    "scenario": "Duplicate Email Registration",
                    "description": "Attempting to register with existing email",
                    "request": {
                        "method": "POST",
                        "url": "http://localhost:5000/api/v1/person/register",
                        "headers": {
                            "Content-Type": "application/json"
                        },
                        "body": {
                            "name": "Another User",
                            "email": "alex@community.org",  # Already registered
                            "role": "MEMBER"
                        }
                    },
                    "expected_response": {
                        "status": 409,
                        "body": {
                            "error": {
                                "message": "Email address is already registered",
                                "code": "PERSON_EMAIL_ALREADY_EXISTS"
                            }
                        }
                    }
                }
            ]
        }

# =======================
# TESTING STRATEGIES
# =======================

class APITestingGuide:
    """
    Comprehensive testing strategies and patterns for the Social Scoring System API.
    """
    
    @staticmethod
    def automated_testing_examples():
        """
        Examples for automated API testing using various tools and frameworks.
        """
        return {
            "title": "Automated API Testing Examples",
            
            "pytest_examples": {
                "description": "Python pytest examples for comprehensive API testing",
                "setup": '''
# requirements-test.txt
pytest==7.4.3
requests==2.31.0
python-jose==3.3.0

# conftest.py
import pytest
import requests
from typing import Dict, Any

@pytest.fixture
def api_base_url():
    return "http://localhost:5000/api/v1"

@pytest.fixture
def test_lead_user():
    return {
        "name": "Test Lead",
        "email": "test.lead@example.com",
        "role": "LEAD",
        "password": "TestPassword123!"
    }

@pytest.fixture
def test_member_user():
    return {
        "name": "Test Member", 
        "email": "test.member@example.com",
        "role": "MEMBER",
        "password": "TestPassword123!"
    }

@pytest.fixture
def authenticated_lead_headers(api_base_url, test_lead_user):
    # Register and authenticate lead user
    auth_response = requests.post(
        f"{api_base_url}/person/authenticate",
        json={
            "email": test_lead_user["email"],
            "password": test_lead_user["password"]
        }
    )
    token = auth_response.json()["accessToken"]
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
                ''',
                
                "test_examples": '''
# test_person_api.py
import pytest
import requests

def test_register_person_success(api_base_url):
    """Test successful person registration."""
    response = requests.post(f"{api_base_url}/person/register", json={
        "name": "John Test",
        "email": "john.test@example.com",
        "role": "MEMBER"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert "personId" in data
    assert data["message"] == "User registered successfully"

def test_register_person_duplicate_email(api_base_url):
    """Test registration with duplicate email."""
    user_data = {
        "name": "Jane Test",
        "email": "duplicate@example.com", 
        "role": "MEMBER"
    }
    
    # First registration should succeed
    response1 = requests.post(f"{api_base_url}/person/register", json=user_data)
    assert response1.status_code == 201
    
    # Second registration with same email should fail
    response2 = requests.post(f"{api_base_url}/person/register", json=user_data)
    assert response2.status_code == 409
    assert response2.json()["error"]["code"] == "PERSON_EMAIL_ALREADY_EXISTS"

def test_authenticate_user_success(api_base_url, test_lead_user):
    """Test successful user authentication."""
    response = requests.post(f"{api_base_url}/person/authenticate", json={
        "email": test_lead_user["email"],
        "password": test_lead_user["password"]
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "accessToken" in data
    assert "refreshToken" in data
    assert data["email"] == test_lead_user["email"]
    assert "LEAD" in data["roles"]

def test_get_current_profile(api_base_url, authenticated_lead_headers):
    """Test getting current user profile."""
    response = requests.get(
        f"{api_base_url}/person/profile",
        headers=authenticated_lead_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "personId" in data
    assert "name" in data
    assert "email" in data
    assert data["role"] == "LEAD"

# test_activity_api.py
def test_create_activity_success(api_base_url, authenticated_lead_headers):
    """Test successful activity creation by LEAD."""
    response = requests.post(
        f"{api_base_url}/activity",
        headers=authenticated_lead_headers,
        json={
            "name": "Test Activity",
            "description": "This is a test activity for automated testing",
            "points": 50
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "activityId" in data
    assert data["message"] == "Activity created successfully"

def test_create_activity_insufficient_permissions(api_base_url, authenticated_member_headers):
    """Test activity creation fails for MEMBER role."""
    response = requests.post(
        f"{api_base_url}/activity",
        headers=authenticated_member_headers,
        json={
            "name": "Test Activity",
            "description": "This should fail",
            "points": 50
        }
    )
    
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "AUTH_INSUFFICIENT_PERMISSIONS"

def test_get_activities_success(api_base_url, authenticated_lead_headers):
    """Test retrieving activities list."""
    response = requests.get(
        f"{api_base_url}/activity",
        headers=authenticated_lead_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "activities" in data
    assert "totalCount" in data
    assert isinstance(data["activities"], list)

# test_action_api.py  
def test_submit_action_success(api_base_url, authenticated_member_headers, test_activity_id):
    """Test successful action submission."""
    response = requests.post(
        f"{api_base_url}/action",
        headers=authenticated_member_headers,
        json={
            "activityId": test_activity_id,
            "description": "Completed test activity with proper documentation",
            "proofHash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "actionId" in data
    assert data["status"] == "SUBMITTED"

def test_validate_proof_success(api_base_url, authenticated_lead_headers, test_action_id):
    """Test successful proof validation by LEAD."""
    response = requests.post(
        f"{api_base_url}/action/{test_action_id}/validate",
        headers=authenticated_lead_headers,
        json={
            "isValid": True,
            "notes": "Proof verified successfully in automated test"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "actionStatus" in data
    assert data["actionStatus"] in ["VALIDATED", "REJECTED"]
                '''
            },
            
            "postman_collection": {
                "description": "Postman collection for manual and automated testing",
                "collection_structure": '''
{
  "info": {
    "name": "Social Scoring System API",
    "description": "Complete API test collection for the Social Scoring System",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:5000/api/v1"
    },
    {
      "key": "lead_jwt_token",
      "value": "",
      "type": "string"
    },
    {
      "key": "member_jwt_token", 
      "value": "",
      "type": "string"
    },
    {
      "key": "activity_id",
      "value": "",
      "type": "string"
    }
  ],
  "item": [
    {
      "name": "Authentication Flow",
      "item": [
        {
          "name": "Register Lead User",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": {
                "name": "Test Lead",
                "email": "test.lead@postman.com",
                "role": "LEAD"
              }
            },
            "url": {
              "raw": "{{base_url}}/person/register",
              "host": ["{{base_url}}"],
              "path": ["person", "register"]
            }
          },
          "test": [
            "pm.test('Status code is 201', function () {",
            "    pm.response.to.have.status(201);",
            "});",
            "",
            "pm.test('Response contains personId', function () {",
            "    var jsonData = pm.response.json();",
            "    pm.expect(jsonData).to.have.property('personId');",
            "});"
          ]
        },
        {
          "name": "Authenticate Lead User",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": {
                "email": "test.lead@postman.com",
                "password": "password123"
              }
            },
            "url": {
              "raw": "{{base_url}}/person/authenticate",
              "host": ["{{base_url}}"],
              "path": ["person", "authenticate"]
            }
          },
          "test": [
            "pm.test('Authentication successful', function () {",
            "    pm.response.to.have.status(200);",
            "    var jsonData = pm.response.json();",
            "    pm.expect(jsonData).to.have.property('accessToken');",
            "    pm.collectionVariables.set('lead_jwt_token', jsonData.accessToken);",
            "});"
          ]
        }
      ]
    },
    {
      "name": "Activity Management",
      "item": [
        {
          "name": "Create Activity",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{lead_jwt_token}}"
              },
              {
                "key": "Content-Type", 
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": {
                "name": "Postman Test Activity",
                "description": "Activity created via Postman for testing purposes",
                "points": 100
              }
            },
            "url": {
              "raw": "{{base_url}}/activity",
              "host": ["{{base_url}}"],
              "path": ["activity"]
            }
          },
          "test": [
            "pm.test('Activity created successfully', function () {",
            "    pm.response.to.have.status(201);",
            "    var jsonData = pm.response.json();",
            "    pm.expect(jsonData).to.have.property('activityId');",
            "    pm.collectionVariables.set('activity_id', jsonData.activityId);",
            "});"
          ]
        }
      ]
    }
  ]
}
                '''
            },
            
            "load_testing": {
                "description": "Load testing examples using Artillery.js",
                "artillery_config": '''
# artillery-config.yml
config:
  target: "http://localhost:5000"
  phases:
    - duration: 60
      arrivalRate: 10
      name: "Warm up"
    - duration: 120  
      arrivalRate: 20
      name: "Ramp up load"
    - duration: 180
      arrivalRate: 30
      name: "Sustained load"
  defaults:
    headers:
      Content-Type: "application/json"

scenarios:
  - name: "User Registration and Authentication"
    weight: 30
    flow:
      - post:
          url: "/api/v1/person/register"
          json:
            name: "Load Test User {{ $uuid() }}"
            email: "loadtest.{{ $uuid() }}@example.com"
            role: "MEMBER"
          capture:
            - json: "$.personId"
              as: "personId"
      - post:
          url: "/api/v1/person/authenticate" 
          json:
            email: "loadtest.{{ personId }}@example.com"
            password: "password123"
          capture:
            - json: "$.accessToken"
              as: "authToken"

  - name: "Activity Browsing"
    weight: 50
    flow:
      - get:
          url: "/api/v1/activity"
          headers:
            Authorization: "Bearer {{ authToken }}"
      - get:
          url: "/api/v1/person/leaderboard"

  - name: "Action Submission"
    weight: 20
    flow:
      - post:
          url: "/api/v1/action"
          headers:
            Authorization: "Bearer {{ authToken }}"
          json:
            activityId: "{{ activityId }}"
            description: "Load test action submission {{ $uuid() }}"
            proofHash: "0x{{ $uuid() }}{{ $uuid() }}"
                '''
            }
        }
    
    @staticmethod
    def performance_testing_guidelines():
        """
        Guidelines for performance testing the Social Scoring System API.
        """
        return {
            "title": "Performance Testing Guidelines",
            
            "key_metrics": {
                "response_time_targets": {
                    "authentication": "< 200ms",
                    "profile_retrieval": "< 150ms", 
                    "activity_listing": "< 300ms",
                    "action_submission": "< 500ms",
                    "leaderboard": "< 400ms"
                },
                "throughput_targets": {
                    "concurrent_users": "100+ simultaneous users",
                    "requests_per_second": "500+ RPS sustained",
                    "authentication_rate": "50+ auth/sec"
                },
                "reliability_targets": {
                    "uptime": "99.9%",
                    "error_rate": "< 0.1%",
                    "timeout_rate": "< 0.01%"
                }
            },
            
            "testing_scenarios": [
                {
                    "name": "Normal Load",
                    "description": "Typical daily usage patterns",
                    "concurrent_users": 50,
                    "test_duration": "30 minutes",
                    "user_actions": [
                        "Register (5%)",
                        "Authenticate (15%)", 
                        "Browse activities (40%)",
                        "Submit actions (25%)",
                        "Check leaderboard (15%)"
                    ]
                },
                {
                    "name": "Peak Load",
                    "description": "High activity periods (events, campaigns)",
                    "concurrent_users": 200,
                    "test_duration": "60 minutes", 
                    "user_actions": [
                        "Register (10%)",
                        "Authenticate (20%)",
                        "Browse activities (30%)",
                        "Submit actions (35%)",
                        "Check leaderboard (5%)"
                    ]
                },
                {
                    "name": "Stress Test",
                    "description": "Beyond normal capacity testing",
                    "concurrent_users": 500,
                    "test_duration": "15 minutes",
                    "expected_degradation": "Graceful degradation acceptable"
                }
            ],
            
            "monitoring_checklist": [
                "Response time percentiles (50th, 95th, 99th)",
                "Error rates by endpoint",
                "Database query performance", 
                "Memory and CPU utilization",
                "JWT token validation overhead",
                "Network I/O and bandwidth usage"
            ]
        }

# =======================
# INTEGRATION EXAMPLES
# =======================

class APIIntegrationExamples:
    """
    Examples showing how to integrate the Social Scoring System API 
    with various platforms and applications.
    """
    
    @staticmethod
    def frontend_integration_examples():
        """
        Frontend integration examples for web and mobile applications.
        """
        return {
            "title": "Frontend Integration Examples",
            
            "react_typescript_example": '''
// types/api.ts
export interface PersonProfile {
  personId: string;
  name: string;
  email: string;
  role: 'MEMBER' | 'LEAD';
  reputationScore: number;
  isActive: boolean;
}

export interface Activity {
  activityId: string;
  name: string;
  description: string;
  points: number;
  leadName: string;
  isActive: boolean;
  participantCount: number;
}

export interface ApiError {
  error: {
    message: string;
    code: string;
    details?: any;
  };
}

// services/apiService.ts
import axios from 'axios';

class ApiService {
  private baseURL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000/api/v1';
  private authToken: string | null = null;

  constructor() {
    // Load saved auth token
    this.authToken = localStorage.getItem('authToken');
    this.setupInterceptors();
  }

  private setupInterceptors() {
    axios.interceptors.request.use(
      (config) => {
        if (this.authToken) {
          config.headers.Authorization = `Bearer ${this.authToken}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    axios.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          this.logout();
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  async authenticate(email: string, password: string): Promise<PersonProfile> {
    try {
      const response = await axios.post(`${this.baseURL}/person/authenticate`, {
        email,
        password
      });
      
      this.authToken = response.data.accessToken;
      localStorage.setItem('authToken', this.authToken);
      
      return await this.getCurrentProfile();
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getCurrentProfile(): Promise<PersonProfile> {
    try {
      const response = await axios.get(`${this.baseURL}/person/profile`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getActivities(): Promise<Activity[]> {
    try {
      const response = await axios.get(`${this.baseURL}/activity`);
      return response.data.activities;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async submitAction(activityId: string, description: string, proofHash: string) {
    try {
      const response = await axios.post(`${this.baseURL}/action`, {
        activityId,
        description, 
        proofHash
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  logout() {
    this.authToken = null;
    localStorage.removeItem('authToken');
  }

  private handleError(error: any): ApiError {
    if (error.response?.data?.error) {
      return error.response.data;
    }
    return {
      error: {
        message: 'An unexpected error occurred',
        code: 'UNKNOWN_ERROR'
      }
    };
  }
}

export const apiService = new ApiService();

// components/ActivityList.tsx
import React, { useEffect, useState } from 'react';
import { Activity } from '../types/api';
import { apiService } from '../services/apiService';

export const ActivityList: React.FC = () => {
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadActivities = async () => {
      try {
        setLoading(true);
        const data = await apiService.getActivities();
        setActivities(data);
      } catch (err: any) {
        setError(err.error?.message || 'Failed to load activities');
      } finally {
        setLoading(false);
      }
    };

    loadActivities();
  }, []);

  if (loading) return <div>Loading activities...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="activity-list">
      <h2>Available Activities</h2>
      {activities.map((activity) => (
        <div key={activity.activityId} className="activity-card">
          <h3>{activity.name}</h3>
          <p>{activity.description}</p>
          <div className="activity-meta">
            <span>Points: {activity.points}</span>
            <span>Lead: {activity.leadName}</span>
            <span>Participants: {activity.participantCount}</span>
          </div>
        </div>
      ))}
    </div>
  );
};
            ''',
            
            "mobile_integration_flutter": '''
// lib/models/api_models.dart
class PersonProfile {
  final String personId;
  final String name; 
  final String email;
  final String role;
  final int reputationScore;
  final bool isActive;

  PersonProfile({
    required this.personId,
    required this.name,
    required this.email, 
    required this.role,
    required this.reputationScore,
    required this.isActive,
  });

  factory PersonProfile.fromJson(Map<String, dynamic> json) {
    return PersonProfile(
      personId: json['personId'],
      name: json['name'],
      email: json['email'],
      role: json['role'],
      reputationScore: json['reputationScore'],
      isActive: json['isActive'],
    );
  }
}

// lib/services/api_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  static const String baseUrl = 'http://localhost:5000/api/v1';
  static String? _authToken;

  static Future<void> initialize() async {
    final prefs = await SharedPreferences.getInstance();
    _authToken = prefs.getString('auth_token');
  }

  static Map<String, String> get headers {
    final Map<String, String> headers = {
      'Content-Type': 'application/json',
    };
    
    if (_authToken != null) {
      headers['Authorization'] = 'Bearer $_authToken';
    }
    
    return headers;
  }

  static Future<PersonProfile> authenticate(String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/person/authenticate'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'email': email,
        'password': password,
      }),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      _authToken = data['accessToken'];
      
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('auth_token', _authToken!);
      
      return getCurrentProfile();
    } else {
      throw Exception('Authentication failed');
    }
  }

  static Future<PersonProfile> getCurrentProfile() async {
    final response = await http.get(
      Uri.parse('$baseUrl/person/profile'),
      headers: headers,
    );

    if (response.statusCode == 200) {
      return PersonProfile.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Failed to load profile');
    }
  }

  static Future<void> logout() async {
    _authToken = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('auth_token');
  }
}

// lib/screens/activity_list_screen.dart
import 'package:flutter/material.dart';

class ActivityListScreen extends StatefulWidget {
  @override
  _ActivityListScreenState createState() => _ActivityListScreenState();
}

class _ActivityListScreenState extends State<ActivityListScreen> {
  List<Activity> activities = [];
  bool isLoading = true;
  String? error;

  @override
  void initState() {
    super.initState();
    loadActivities();
  }

  Future<void> loadActivities() async {
    try {
      setState(() {
        isLoading = true;
        error = null;
      });
      
      final loadedActivities = await ApiService.getActivities();
      
      setState(() {
        activities = loadedActivities;
        isLoading = false;
      });
    } catch (e) {
      setState(() {
        error = e.toString();
        isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Activities'),
        actions: [
          IconButton(
            icon: Icon(Icons.refresh),
            onPressed: loadActivities,
          ),
        ],
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (isLoading) {
      return Center(child: CircularProgressIndicator());
    }
    
    if (error != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text('Error: $error'),
            ElevatedButton(
              onPressed: loadActivities,
              child: Text('Retry'),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: loadActivities,
      child: ListView.builder(
        itemCount: activities.length,
        itemBuilder: (context, index) {
          final activity = activities[index];
          return ActivityCard(activity: activity);
        },
      ),
    );
  }
}
            '''
        }

# =======================
# PRODUCTION DEPLOYMENT
# =======================

PRODUCTION_DEPLOYMENT_GUIDE = {
    "title": "Production Deployment Guide",
    "description": "Best practices for deploying the Social Scoring System API in production environments",
    
    "environment_configuration": {
        "environment_variables": [
            "DATABASE_URL - Production database connection string",
            "JWT_SECRET_KEY - Strong secret key for JWT signing",
            "CORS_ORIGINS - Allowed frontend origins",
            "LOG_LEVEL - Logging level (INFO, WARNING, ERROR)",
            "RATE_LIMIT_PER_MINUTE - API rate limiting configuration",
            "BLOCKCHAIN_NODE_URL - Blockchain network endpoint",
            "SMTP_CONFIG - Email service configuration for notifications"
        ],
        
        "security_considerations": [
            "Use HTTPS only in production",
            "Implement proper CORS policies",
            "Set secure JWT token expiration times",
            "Enable API rate limiting",
            "Use environment-specific database credentials",
            "Implement proper logging and monitoring",
            "Regular security audits and updates"
        ]
    },
    
    "monitoring_and_observability": {
        "key_metrics": [
            "Request latency percentiles",
            "Error rates by endpoint",
            "Authentication success/failure rates",
            "Database connection pool status",
            "Memory and CPU utilization",
            "JWT token validation performance"
        ],
        
        "alerting_rules": [
            "API response time > 1 second",
            "Error rate > 1%",
            "Database connection failures",
            "High memory usage (> 80%)",
            "Authentication failures spike"
        ]
    }
}