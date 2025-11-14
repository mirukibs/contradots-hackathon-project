"""
Comprehensive API Specification for Social Scoring System

This document provides detailed specifications for all REST API endpoints
based on the domain and application layer designs.
"""

# =======================
# API SPECIFICATION OVERVIEW
# =======================

API_SPECIFICATION = {
    "openapi": "3.0.0",
    "info": {
        "title": "Social Scoring System API",
        "version": "1.0.0",
        "description": "RESTful API for blockchain-based social impact tracking and scoring system",
        "contact": {
            "name": "Development Team",
            "url": "https://github.com/mirukibs/contradots-hackathon-project"
        },
        "license": {
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT"
        }
    },
    "servers": [
        {
            "url": "http://localhost:5000/api/v1",
            "description": "Development server"
        },
        {
            "url": "https://api.socialscoring.example.com/api/v1", 
            "description": "Production server"
        }
    ],
    "security": [
        {
            "bearerAuth": []
        }
    ]
}

# =======================
# AUTHENTICATION & SECURITY
# =======================

AUTHENTICATION_DESIGN = {
    "scheme": "JWT Bearer Token",
    "token_lifetime": "1 hour",
    "refresh_strategy": "Refresh tokens (future implementation)",
    "role_based_access": {
        "MEMBER": [
            "submit_action",
            "view_activities", 
            "view_leaderboard",
            "view_profile"
        ],
        "LEAD": [
            "create_activity",
            "manage_activity", 
            "validate_proof",
            "deactivate_activity",
            "view_pending_validations"
        ]
    },
    "permission_inheritance": "LEAD inherits all MEMBER permissions",
    "ownership_rules": {
        "activity_management": "Only creator can deactivate",
        "action_submission": "Users can only submit for themselves",
        "profile_access": "Users can view their own profile and others (if authenticated)"
    }
}

# =======================
# PERSON MANAGEMENT API
# =======================

PERSON_API_ENDPOINTS = {
    
    "register_person": {
        "method": "POST",
        "path": "/person/register",
        "summary": "Register a new user in the system",
        "description": "Creates a new person account. Public endpoint that doesn't require authentication.",
        "security": [],  # Public endpoint
        "request_body": {
            "content_type": "application/json",
            "schema": {
                "type": "object",
                "required": ["name", "email"],
                "properties": {
                    "name": {
                        "type": "string",
                        "minLength": 2,
                        "maxLength": 100,
                        "description": "Full name of the person",
                        "example": "John Doe"
                    },
                    "email": {
                        "type": "string",
                        "format": "email",
                        "description": "Valid email address for authentication",
                        "example": "john.doe@example.com"
                    },
                    "role": {
                        "type": "string",
                        "enum": ["MEMBER", "LEAD"],
                        "default": "MEMBER",
                        "description": "User role in the system",
                        "example": "MEMBER"
                    }
                }
            }
        },
        "responses": {
            "201": {
                "description": "User registered successfully",
                "schema": {
                    "type": "object",
                    "properties": {
                        "personId": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for the created person"
                        },
                        "message": {
                            "type": "string",
                            "example": "User registered successfully"
                        }
                    }
                }
            },
            "400": {
                "description": "Validation error",
                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
            },
            "409": {
                "description": "Email already exists",
                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
            }
        },
        "application_service_mapping": {
            "service": "PersonApplicationService",
            "method": "registerPerson",
            "command": "RegisterPersonCommand"
        }
    },
    
    "authenticate_user": {
        "method": "POST", 
        "path": "/person/authenticate",
        "summary": "Authenticate user and get JWT token",
        "description": "Validates user credentials and returns JWT token for subsequent requests.",
        "security": [],  # Public endpoint
        "request_body": {
            "content_type": "application/json",
            "schema": {
                "type": "object",
                "required": ["email", "password"],
                "properties": {
                    "email": {
                        "type": "string",
                        "format": "email", 
                        "description": "Registered email address",
                        "example": "john.doe@example.com"
                    },
                    "password": {
                        "type": "string",
                        "minLength": 8,
                        "description": "User password",
                        "example": "password123"
                    }
                }
            }
        },
        "responses": {
            "200": {
                "description": "Authentication successful",
                "schema": {
                    "type": "object",
                    "properties": {
                        "accessToken": {
                            "type": "string",
                            "description": "JWT access token"
                        },
                        "refreshToken": {
                            "type": "string",
                            "description": "Refresh token for token renewal"
                        },
                        "personId": {
                            "type": "string",
                            "format": "uuid",
                            "description": "User's unique identifier"
                        },
                        "email": {
                            "type": "string",
                            "description": "User's email address"
                        },
                        "roles": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "User's roles in the system"
                        },
                        "expiresAt": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Token expiration time"
                        }
                    }
                }
            },
            "401": {
                "description": "Invalid credentials",
                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
            }
        },
        "application_service_mapping": {
            "service": "PersonApplicationService",
            "method": "authenticateUser", 
            "command": "AuthenticateUserCommand"
        }
    },
    
    "get_current_user_profile": {
        "method": "GET",
        "path": "/person/profile",
        "summary": "Get current authenticated user's profile",
        "description": "Returns the profile information for the currently authenticated user.",
        "security": [{"bearerAuth": []}],
        "responses": {
            "200": {
                "description": "User profile retrieved successfully",
                "schema": {
                    "$ref": "#/components/schemas/PersonProfile"
                }
            },
            "401": {
                "description": "Authentication required",
                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
            }
        },
        "application_service_mapping": {
            "service": "PersonApplicationService",
            "method": "getCurrentUserProfile",
            "requires_auth": True
        }
    },
    
    "get_person_profile": {
        "method": "GET",
        "path": "/person/profile/{personId}",
        "summary": "Get profile of a specific user",
        "description": "Returns the profile information for a specific user by their ID.",
        "security": [{"bearerAuth": []}],
        "parameters": [
            {
                "name": "personId",
                "in": "path",
                "required": True,
                "schema": {
                    "type": "string",
                    "format": "uuid"
                },
                "description": "Unique identifier of the person"
            }
        ],
        "responses": {
            "200": {
                "description": "User profile retrieved successfully",
                "schema": {"$ref": "#/components/schemas/PersonProfile"}
            },
            "401": {
                "description": "Authentication required",
                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
            },
            "404": {
                "description": "Person not found", 
                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
            }
        },
        "application_service_mapping": {
            "service": "PersonApplicationService",
            "method": "getPersonProfile",
            "requires_auth": True
        }
    },
    
    "get_leaderboard": {
        "method": "GET",
        "path": "/person/leaderboard",
        "summary": "Get system leaderboard",
        "description": "Returns the reputation-based leaderboard. Public endpoint with optional authentication for personalized data.",
        "security": [],  # Optional authentication
        "parameters": [
            {
                "name": "limit",
                "in": "query",
                "required": False,
                "schema": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 50
                },
                "description": "Maximum number of entries to return"
            }
        ],
        "responses": {
            "200": {
                "description": "Leaderboard retrieved successfully",
                "schema": {
                    "type": "object",
                    "properties": {
                        "leaderboard": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/LeaderboardEntry"}
                        },
                        "totalCount": {
                            "type": "integer",
                            "description": "Total number of participants"
                        },
                        "currentUserRank": {
                            "type": "integer",
                            "description": "Current user's rank (if authenticated)"
                        }
                    }
                }
            }
        },
        "application_service_mapping": {
            "service": "PersonApplicationService", 
            "method": "getLeaderboard",
            "requires_auth": False
        }
    }
}

# =======================
# ACTIVITY MANAGEMENT API
# =======================

ACTIVITY_API_ENDPOINTS = {
    
    "create_activity": {
        "method": "POST",
        "path": "/activity",
        "summary": "Create a new activity (LEAD only)",
        "description": "Creates a new activity that members can participate in. Only users with LEAD role can create activities.",
        "security": [{"bearerAuth": []}],
        "required_roles": ["LEAD"],
        "request_body": {
            "content_type": "application/json",
            "schema": {
                "type": "object",
                "required": ["name", "description", "points"],
                "properties": {
                    "name": {
                        "type": "string",
                        "minLength": 3,
                        "maxLength": 200,
                        "description": "Activity name",
                        "example": "Beach Cleanup Drive"
                    },
                    "description": {
                        "type": "string",
                        "minLength": 10,
                        "maxLength": 2000,
                        "description": "Detailed description of the activity",
                        "example": "Community-led initiative to clean plastic waste from local beaches"
                    },
                    "points": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 1000,
                        "description": "Points awarded for completing this activity",
                        "example": 50
                    }
                }
            }
        },
        "responses": {
            "201": {
                "description": "Activity created successfully",
                "schema": {
                    "type": "object",
                    "properties": {
                        "activityId": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for the created activity"
                        },
                        "message": {
                            "type": "string",
                            "example": "Activity created successfully"
                        }
                    }
                }
            },
            "401": {
                "description": "Authentication required",
                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
            },
            "403": {
                "description": "LEAD role required",
                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
            }
        },
        "application_service_mapping": {
            "service": "ActivityApplicationService",
            "method": "createActivity",
            "command": "CreateActivityCommand"
        }
    },
    
    "get_active_activities": {
        "method": "GET",
        "path": "/activity",
        "summary": "Get all active activities",
        "description": "Returns a list of all currently active activities that users can participate in.",
        "security": [{"bearerAuth": []}],
        "parameters": [
            {
                "name": "page", 
                "in": "query",
                "required": False,
                "schema": {
                    "type": "integer",
                    "minimum": 1,
                    "default": 1
                },
                "description": "Page number for pagination"
            },
            {
                "name": "limit",
                "in": "query",
                "required": False,
                "schema": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 20
                },
                "description": "Number of activities per page"
            }
        ],
        "responses": {
            "200": {
                "description": "Activities retrieved successfully",
                "schema": {
                    "type": "object",
                    "properties": {
                        "activities": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/ActivitySummary"}
                        },
                        "totalCount": {
                            "type": "integer",
                            "description": "Total number of active activities"
                        },
                        "page": {
                            "type": "integer",
                            "description": "Current page number"
                        },
                        "totalPages": {
                            "type": "integer", 
                            "description": "Total number of pages"
                        }
                    }
                }
            },
            "401": {
                "description": "Authentication required",
                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
            }
        },
        "application_service_mapping": {
            "service": "ActivityApplicationService",
            "method": "getActiveActivities",
            "requires_auth": True
        }
    },
    
    "get_activity_details": {
        "method": "GET",
        "path": "/activity/{activityId}",
        "summary": "Get detailed information about a specific activity",
        "description": "Returns comprehensive details about an activity including statistics and participation data.",
        "security": [{"bearerAuth": []}],
        "parameters": [
            {
                "name": "activityId",
                "in": "path",
                "required": True,
                "schema": {
                    "type": "string",
                    "format": "uuid"
                },
                "description": "Unique identifier of the activity"
            }
        ],
        "responses": {
            "200": {
                "description": "Activity details retrieved successfully",
                "schema": {"$ref": "#/components/schemas/ActivityDetails"}
            },
            "401": {
                "description": "Authentication required",
                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
            },
            "404": {
                "description": "Activity not found",
                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
            }
        },
        "application_service_mapping": {
            "service": "ActivityApplicationService",
            "method": "getActivityDetails",
            "requires_auth": True
        }
    },
    
    "deactivate_activity": {
        "method": "POST",
        "path": "/activity/{activityId}/deactivate", 
        "summary": "Deactivate an activity (creator only)",
        "description": "Deactivates an activity, preventing new participation. Only the activity creator can perform this action.",
        "security": [{"bearerAuth": []}],
        "required_ownership": "activity_creator",
        "parameters": [
            {
                "name": "activityId",
                "in": "path",
                "required": True,
                "schema": {
                    "type": "string",
                    "format": "uuid"
                },
                "description": "Unique identifier of the activity to deactivate"
            }
        ],
        "responses": {
            "200": {
                "description": "Activity deactivated successfully",
                "schema": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "example": "Activity deactivated successfully"
                        },
                        "activityId": {
                            "type": "string",
                            "format": "uuid"
                        }
                    }
                }
            },
            "401": {
                "description": "Authentication required",
                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
            },
            "403": {
                "description": "Only activity creator can deactivate",
                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
            },
            "404": {
                "description": "Activity not found",
                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
            }
        },
        "application_service_mapping": {
            "service": "ActivityApplicationService",
            "method": "deactivateActivity",
            "command": "DeactivateActivityCommand"
        }
    }
}

# =======================
# ACTION MANAGEMENT API
# =======================

ACTION_API_ENDPOINTS = {
    
    "submit_action": {
        "method": "POST",
        "path": "/action",
        "summary": "Submit an action for verification",
        "description": "Submits a completed action with blockchain proof for verification and scoring.",
        "security": [{"bearerAuth": []}],
        "request_body": {
            "content_type": "application/json",
            "schema": {
                "type": "object",
                "required": ["activityId", "description", "proofHash"],
                "properties": {
                    "activityId": {
                        "type": "string",
                        "format": "uuid",
                        "description": "ID of the activity this action relates to",
                        "example": "123e4567-e89b-12d3-a456-426614174000"
                    },
                    "description": {
                        "type": "string",
                        "minLength": 10,
                        "maxLength": 1000,
                        "description": "Detailed description of the action performed",
                        "example": "Collected 5kg of plastic waste from Bondi Beach section A"
                    },
                    "proofHash": {
                        "type": "string",
                        "pattern": "^0x[a-fA-F0-9]{64}$",
                        "description": "Blockchain hash proving the action was completed",
                        "example": "0x1a2b3c4d5e6f7890abcdef1234567890abcdef1234567890abcdef1234567890"
                    }
                }
            }
        },
        "responses": {
            "201": {
                "description": "Action submitted successfully",
                "schema": {
                    "type": "object",
                    "properties": {
                        "actionId": {
                            "type": "string",
                            "format": "uuid",
                            "description": "Unique identifier for the submitted action"
                        },
                        "message": {
                            "type": "string",
                            "example": "Action submitted for verification"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["SUBMITTED"],
                            "description": "Current status of the action"
                        }
                    }
                }
            },
            "400": {
                "description": "Invalid request data",
                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
            },
            "401": {
                "description": "Authentication required", 
                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
            },
            "404": {
                "description": "Activity not found or inactive",
                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
            }
        },
        "application_service_mapping": {
            "service": "ActionApplicationService",
            "method": "submitAction",
            "command": "SubmitActionCommand"
        }
    },
    
    "get_pending_validations": {
        "method": "GET",
        "path": "/action/pending",
        "summary": "Get actions pending validation (LEAD only)",
        "description": "Returns a list of actions that are pending proof validation. Only accessible by users with LEAD role.",
        "security": [{"bearerAuth": []}],
        "required_roles": ["LEAD"],
        "parameters": [
            {
                "name": "activityId",
                "in": "query", 
                "required": False,
                "schema": {
                    "type": "string",
                    "format": "uuid"
                },
                "description": "Filter by specific activity ID"
            },
            {
                "name": "limit",
                "in": "query",
                "required": False,
                "schema": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "default": 20
                },
                "description": "Maximum number of pending actions to return"
            }
        ],
        "responses": {
            "200": {
                "description": "Pending validations retrieved successfully",
                "schema": {
                    "type": "object",
                    "properties": {
                        "pendingActions": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/ActionSummary"}
                        },
                        "totalCount": {
                            "type": "integer",
                            "description": "Total number of pending validations"
                        }
                    }
                }
            },
            "401": {
                "description": "Authentication required",
                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
            },
            "403": {
                "description": "LEAD role required",
                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
            }
        },
        "application_service_mapping": {
            "service": "ActionApplicationService",
            "method": "getPendingValidations",
            "requires_auth": True
        }
    },
    
    "get_my_actions": {
        "method": "GET",
        "path": "/action/my-actions",
        "summary": "Get current user's actions",
        "description": "Returns a list of all actions submitted by the currently authenticated user.",
        "security": [{"bearerAuth": []}],
        "parameters": [
            {
                "name": "status",
                "in": "query",
                "required": False,
                "schema": {
                    "type": "string",
                    "enum": ["SUBMITTED", "VALIDATED", "REJECTED"]
                },
                "description": "Filter by action status"
            },
            {
                "name": "activityId",
                "in": "query",
                "required": False,
                "schema": {
                    "type": "string",
                    "format": "uuid"
                },
                "description": "Filter by specific activity"
            }
        ],
        "responses": {
            "200": {
                "description": "User's actions retrieved successfully",
                "schema": {
                    "type": "object",
                    "properties": {
                        "actions": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/ActionSummary"}
                        },
                        "totalCount": {
                            "type": "integer"
                        },
                        "statusCounts": {
                            "type": "object",
                            "properties": {
                                "submitted": {"type": "integer"},
                                "validated": {"type": "integer"},
                                "rejected": {"type": "integer"}
                            }
                        }
                    }
                }
            },
            "401": {
                "description": "Authentication required",
                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
            }
        },
        "application_service_mapping": {
            "service": "ActionApplicationService",
            "method": "getMyActions",
            "requires_auth": True
        }
    },
    
    "get_person_actions": {
        "method": "GET",
        "path": "/action/person/{personId}",
        "summary": "Get actions for a specific person",
        "description": "Returns actions submitted by a specific person. Accessible to authenticated users.",
        "security": [{"bearerAuth": []}],
        "parameters": [
            {
                "name": "personId",
                "in": "path",
                "required": True,
                "schema": {
                    "type": "string",
                    "format": "uuid"
                },
                "description": "Unique identifier of the person"
            }
        ],
        "responses": {
            "200": {
                "description": "Person's actions retrieved successfully",
                "schema": {
                    "type": "object",
                    "properties": {
                        "actions": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/ActionSummary"}
                        },
                        "totalCount": {"type": "integer"},
                        "personName": {"type": "string"}
                    }
                }
            },
            "401": {
                "description": "Authentication required",
                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
            },
            "404": {
                "description": "Person not found",
                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
            }
        },
        "application_service_mapping": {
            "service": "ActionApplicationService",
            "method": "getPersonActions",
            "requires_auth": True
        }
    },
    
    "validate_proof": {
        "method": "POST",
        "path": "/action/{actionId}/validate",
        "summary": "Validate proof for an action (LEAD only)",
        "description": "Validates the blockchain proof for a submitted action. Only accessible by users with LEAD role.",
        "security": [{"bearerAuth": []}],
        "required_roles": ["LEAD"],
        "parameters": [
            {
                "name": "actionId",
                "in": "path",
                "required": True,
                "schema": {
                    "type": "string",
                    "format": "uuid"
                },
                "description": "Unique identifier of the action to validate"
            }
        ],
        "request_body": {
            "content_type": "application/json",
            "schema": {
                "type": "object",
                "required": ["isValid"],
                "properties": {
                    "isValid": {
                        "type": "boolean",
                        "description": "Whether the proof is valid",
                        "example": True
                    },
                    "notes": {
                        "type": "string",
                        "maxLength": 500,
                        "description": "Optional validation notes",
                        "example": "Proof verified on blockchain, action confirmed"
                    }
                }
            }
        },
        "responses": {
            "200": {
                "description": "Proof validation completed",
                "schema": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "example": "Proof validation completed"
                        },
                        "actionStatus": {
                            "type": "string",
                            "enum": ["VALIDATED", "REJECTED"],
                            "description": "New status of the action"
                        },
                        "pointsAwarded": {
                            "type": "integer",
                            "description": "Points awarded if validation successful"
                        }
                    }
                }
            },
            "401": {
                "description": "Authentication required",
                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
            },
            "403": {
                "description": "LEAD role required",
                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
            },
            "404": {
                "description": "Action not found",
                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
            }
        },
        "application_service_mapping": {
            "service": "ActionApplicationService",
            "method": "simulateProofValidation",
            "command": "ValidateProofCommand"
        }
    }
}

# =======================
# SYSTEM ENDPOINTS
# =======================

SYSTEM_API_ENDPOINTS = {
    "health_check": {
        "method": "GET",
        "path": "/health",
        "summary": "Health check endpoint",
        "description": "Returns the health status of the API service.",
        "security": [],
        "responses": {
            "200": {
                "description": "Service is healthy",
                "schema": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "example": "healthy"
                        },
                        "service": {
                            "type": "string", 
                            "example": "social-scoring-system"
                        },
                        "version": {
                            "type": "string",
                            "example": "1.0.0"
                        },
                        "timestamp": {
                            "type": "string",
                            "format": "date-time"
                        }
                    }
                }
            }
        }
    },
    "api_info": {
        "method": "GET",
        "path": "/info",
        "summary": "API information endpoint",
        "description": "Returns information about the API and available endpoints.",
        "security": [],
        "responses": {
            "200": {
                "description": "API information retrieved successfully",
                "schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "version": {"type": "string"},
                        "description": {"type": "string"},
                        "endpoints": {
                            "type": "object",
                            "properties": {
                                "person": {"type": "string"},
                                "activity": {"type": "string"},
                                "action": {"type": "string"}
                            }
                        },
                        "authentication": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string"},
                                "header": {"type": "string"}
                            }
                        }
                    }
                }
            }
        }
    }
}