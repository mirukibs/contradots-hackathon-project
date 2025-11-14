"""
Response schema definitions for the Social Scoring System API.

This module defines the JSON schema structures for API responses,
ensuring consistency and type safety across all endpoints.
"""

from typing import TypedDict, List, Optional, Union
from datetime import datetime

# =======================
# BASE RESPONSE SCHEMAS
# =======================

class ErrorResponse(TypedDict):
    """Standard error response format across all endpoints."""
    error: "ErrorDetail"

class ErrorDetail(TypedDict):
    """Error detail structure."""
    message: str
    code: str
    details: Optional[dict]

class SuccessResponse(TypedDict):
    """Basic success response with message."""
    message: str

# =======================
# AUTHENTICATION SCHEMAS
# =======================

class AuthenticationResponse(TypedDict):
    """JWT authentication response."""
    accessToken: str
    refreshToken: str
    personId: str
    email: str
    roles: List[str]
    expiresAt: str

class AuthenticationContext(TypedDict):
    """Authentication context passed to controllers."""
    personId: str
    email: str
    roles: List[str]
    isAuthenticated: bool

# =======================
# PERSON SCHEMAS
# =======================

class PersonProfile(TypedDict):
    """Complete person profile information."""
    personId: str
    name: str
    email: str
    role: str
    reputationScore: int
    isActive: bool
    registeredAt: str
    lastActiveAt: Optional[str]

class LeaderboardEntry(TypedDict):
    """Individual entry in the leaderboard."""
    personId: str
    name: str
    reputationScore: int
    rank: int
    activityCount: int

class LeaderboardResponse(TypedDict):
    """Full leaderboard response."""
    leaderboard: List[LeaderboardEntry]
    totalCount: int
    currentUserRank: Optional[int]

class RegisterPersonRequest(TypedDict):
    """Request schema for person registration."""
    name: str
    email: str
    role: Optional[str]  # Default: "MEMBER"

class RegisterPersonResponse(TypedDict):
    """Response schema for person registration."""
    personId: str
    message: str

class AuthenticateUserRequest(TypedDict):
    """Request schema for user authentication."""
    email: str
    password: str

# =======================
# ACTIVITY SCHEMAS
# =======================

class ActivitySummary(TypedDict):
    """Summary information for an activity."""
    activityId: str
    name: str
    description: str
    points: int
    leadName: str
    leadId: str
    isActive: bool
    createdAt: str
    participantCount: int

class ActivityDetails(TypedDict):
    """Detailed information for an activity."""
    activityId: str
    name: str
    description: str
    points: int
    leadName: str
    leadId: str
    isActive: bool
    createdAt: str
    participantCount: int
    totalActionsSubmitted: int
    validatedActionsCount: int
    pendingActionsCount: int
    totalPointsAwarded: int

class ActivitiesResponse(TypedDict):
    """Response for listing activities."""
    activities: List[ActivitySummary]
    totalCount: int
    page: int
    totalPages: int

class CreateActivityRequest(TypedDict):
    """Request schema for activity creation."""
    name: str
    description: str
    points: int

class CreateActivityResponse(TypedDict):
    """Response schema for activity creation."""
    activityId: str
    message: str

class DeactivateActivityResponse(TypedDict):
    """Response schema for activity deactivation."""
    message: str
    activityId: str

# =======================
# ACTION SCHEMAS
# =======================

class ActionSummary(TypedDict):
    """Summary information for an action."""
    actionId: str
    personId: str
    personName: str
    activityId: str
    activityName: str
    description: str
    status: str  # SUBMITTED, VALIDATED, REJECTED
    submittedAt: str
    validatedAt: Optional[str]
    pointsAwarded: Optional[int]

class ActionDetails(TypedDict):
    """Detailed information for an action."""
    actionId: str
    personId: str
    personName: str
    activityId: str
    activityName: str
    description: str
    proofHash: str
    status: str
    submittedAt: str
    validatedAt: Optional[str]
    validatedBy: Optional[str]
    pointsAwarded: Optional[int]
    validationNotes: Optional[str]

class MyActionsResponse(TypedDict):
    """Response for user's own actions."""
    actions: List[ActionSummary]
    totalCount: int
    statusCounts: "ActionStatusCounts"

class ActionStatusCounts(TypedDict):
    """Count of actions by status."""
    submitted: int
    validated: int
    rejected: int

class PendingValidationsResponse(TypedDict):
    """Response for pending validations."""
    pendingActions: List[ActionSummary]
    totalCount: int

class PersonActionsResponse(TypedDict):
    """Response for specific person's actions."""
    actions: List[ActionSummary]
    totalCount: int
    personName: str

class SubmitActionRequest(TypedDict):
    """Request schema for action submission."""
    activityId: str
    description: str
    proofHash: str

class SubmitActionResponse(TypedDict):
    """Response schema for action submission."""
    actionId: str
    message: str
    status: str

class ValidateProofRequest(TypedDict):
    """Request schema for proof validation."""
    isValid: bool
    notes: Optional[str]

class ValidateProofResponse(TypedDict):
    """Response schema for proof validation."""
    message: str
    actionStatus: str
    pointsAwarded: Optional[int]

# =======================
# SYSTEM SCHEMAS
# =======================

class HealthCheckResponse(TypedDict):
    """Health check endpoint response."""
    status: str
    service: str
    version: str
    timestamp: str

class ApiInfoResponse(TypedDict):
    """API information endpoint response."""
    name: str
    version: str
    description: str
    endpoints: "EndpointInfo"
    authentication: "AuthInfo"

class EndpointInfo(TypedDict):
    """Endpoint information structure."""
    person: str
    activity: str
    action: str

class AuthInfo(TypedDict):
    """Authentication information structure."""
    type: str
    header: str

# =======================
# PAGINATION SCHEMAS
# =======================

class PaginationParams(TypedDict):
    """Standard pagination parameters."""
    page: int
    limit: int
    offset: int

class PaginatedResponse(TypedDict):
    """Base structure for paginated responses."""
    totalCount: int
    page: int
    totalPages: int
    hasNextPage: bool
    hasPreviousPage: bool

# =======================
# VALIDATION SCHEMAS
# =======================

class ValidationError(TypedDict):
    """Individual field validation error."""
    field: str
    message: str
    code: str
    value: Optional[Union[str, int, bool]]

class ValidationErrorResponse(TypedDict):
    """Response for validation errors."""
    error: "ValidationErrorDetail"

class ValidationErrorDetail(TypedDict):
    """Validation error detail structure."""
    message: str
    code: str
    validationErrors: List[ValidationError]

# =======================
# FILTER SCHEMAS  
# =======================

class ActivityFilters(TypedDict, total=False):
    """Available filters for activity endpoints."""
    isActive: Optional[bool]
    leadId: Optional[str]
    minPoints: Optional[int]
    maxPoints: Optional[int]

class ActionFilters(TypedDict, total=False):
    """Available filters for action endpoints."""
    status: Optional[str]
    activityId: Optional[str]
    personId: Optional[str]
    dateFrom: Optional[str]
    dateTo: Optional[str]

class PersonFilters(TypedDict, total=False):
    """Available filters for person endpoints."""
    role: Optional[str]
    isActive: Optional[bool]
    minReputationScore: Optional[int]

# =======================
# OPENAPI SCHEMA COMPONENTS
# =======================

OPENAPI_COMPONENTS = {
    "schemas": {
        "ErrorResponse": {
            "type": "object",
            "properties": {
                "error": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string"},
                        "code": {"type": "string"},
                        "details": {"type": "object"}
                    },
                    "required": ["message", "code"]
                }
            },
            "required": ["error"]
        },
        
        "PersonProfile": {
            "type": "object",
            "properties": {
                "personId": {"type": "string", "format": "uuid"},
                "name": {"type": "string"},
                "email": {"type": "string", "format": "email"},
                "role": {"type": "string", "enum": ["MEMBER", "LEAD"]},
                "reputationScore": {"type": "integer", "minimum": 0},
                "isActive": {"type": "boolean"},
                "registeredAt": {"type": "string", "format": "date-time"},
                "lastActiveAt": {"type": "string", "format": "date-time"}
            },
            "required": ["personId", "name", "email", "role", "reputationScore", "isActive", "registeredAt"]
        },
        
        "LeaderboardEntry": {
            "type": "object",
            "properties": {
                "personId": {"type": "string", "format": "uuid"},
                "name": {"type": "string"},
                "reputationScore": {"type": "integer", "minimum": 0},
                "rank": {"type": "integer", "minimum": 1},
                "activityCount": {"type": "integer", "minimum": 0}
            },
            "required": ["personId", "name", "reputationScore", "rank", "activityCount"]
        },
        
        "ActivitySummary": {
            "type": "object",
            "properties": {
                "activityId": {"type": "string", "format": "uuid"},
                "name": {"type": "string"},
                "description": {"type": "string"},
                "points": {"type": "integer", "minimum": 1},
                "leadName": {"type": "string"},
                "leadId": {"type": "string", "format": "uuid"},
                "isActive": {"type": "boolean"},
                "createdAt": {"type": "string", "format": "date-time"},
                "participantCount": {"type": "integer", "minimum": 0}
            },
            "required": ["activityId", "name", "description", "points", "leadName", "leadId", "isActive", "createdAt", "participantCount"]
        },
        
        "ActivityDetails": {
            "allOf": [
                {"$ref": "#/components/schemas/ActivitySummary"},
                {
                    "type": "object",
                    "properties": {
                        "totalActionsSubmitted": {"type": "integer", "minimum": 0},
                        "validatedActionsCount": {"type": "integer", "minimum": 0},
                        "pendingActionsCount": {"type": "integer", "minimum": 0},
                        "totalPointsAwarded": {"type": "integer", "minimum": 0}
                    },
                    "required": ["totalActionsSubmitted", "validatedActionsCount", "pendingActionsCount", "totalPointsAwarded"]
                }
            ]
        },
        
        "ActionSummary": {
            "type": "object",
            "properties": {
                "actionId": {"type": "string", "format": "uuid"},
                "personId": {"type": "string", "format": "uuid"},
                "personName": {"type": "string"},
                "activityId": {"type": "string", "format": "uuid"},
                "activityName": {"type": "string"},
                "description": {"type": "string"},
                "status": {"type": "string", "enum": ["SUBMITTED", "VALIDATED", "REJECTED"]},
                "submittedAt": {"type": "string", "format": "date-time"},
                "validatedAt": {"type": "string", "format": "date-time"},
                "pointsAwarded": {"type": "integer", "minimum": 0}
            },
            "required": ["actionId", "personId", "personName", "activityId", "activityName", "description", "status", "submittedAt"]
        }
    },
    
    "securitySchemes": {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT authorization header using the Bearer scheme"
        }
    }
}

# =======================
# HTTP STATUS CODES
# =======================

HTTP_STATUS_CODES = {
    # Success responses
    "OK": 200,
    "CREATED": 201,
    "NO_CONTENT": 204,
    
    # Client error responses
    "BAD_REQUEST": 400,
    "UNAUTHORIZED": 401,
    "FORBIDDEN": 403,
    "NOT_FOUND": 404,
    "METHOD_NOT_ALLOWED": 405,
    "CONFLICT": 409,
    "UNPROCESSABLE_ENTITY": 422,
    
    # Server error responses
    "INTERNAL_SERVER_ERROR": 500,
    "NOT_IMPLEMENTED": 501,
    "SERVICE_UNAVAILABLE": 503
}

# =======================
# ERROR CODES
# =======================

ERROR_CODES = {
    # Authentication/Authorization errors
    "AUTH_TOKEN_MISSING": "Authentication token is required",
    "AUTH_TOKEN_INVALID": "Invalid authentication token",
    "AUTH_TOKEN_EXPIRED": "Authentication token has expired",
    "AUTH_INSUFFICIENT_PERMISSIONS": "Insufficient permissions for this operation",
    "AUTH_INVALID_CREDENTIALS": "Invalid email or password",
    
    # Validation errors
    "VALIDATION_REQUIRED_FIELD": "Required field is missing",
    "VALIDATION_INVALID_FORMAT": "Field has invalid format",
    "VALIDATION_INVALID_VALUE": "Field has invalid value",
    "VALIDATION_LENGTH_EXCEEDED": "Field exceeds maximum length",
    "VALIDATION_LENGTH_INSUFFICIENT": "Field is too short",
    
    # Business logic errors
    "PERSON_EMAIL_ALREADY_EXISTS": "Email address is already registered",
    "PERSON_NOT_FOUND": "Person not found",
    "ACTIVITY_NOT_FOUND": "Activity not found",
    "ACTIVITY_INACTIVE": "Activity is no longer active",
    "ACTION_NOT_FOUND": "Action not found",
    "ACTION_ALREADY_VALIDATED": "Action has already been validated",
    "ACTION_INVALID_PROOF": "Invalid blockchain proof provided",
    
    # Resource access errors
    "RESOURCE_NOT_FOUND": "Requested resource not found",
    "RESOURCE_ACCESS_DENIED": "Access to resource is denied",
    "RESOURCE_MODIFICATION_DENIED": "Modification of resource is denied",
    
    # System errors
    "SYSTEM_INTERNAL_ERROR": "An internal system error occurred",
    "SYSTEM_SERVICE_UNAVAILABLE": "Service is temporarily unavailable",
    "SYSTEM_DATABASE_ERROR": "Database operation failed"
}

# =======================
# REQUEST VALIDATION RULES
# =======================

VALIDATION_RULES = {
    "person": {
        "name": {
            "required": True,
            "min_length": 2,
            "max_length": 100,
            "pattern": r"^[a-zA-Z\s'-]+$"
        },
        "email": {
            "required": True,
            "format": "email",
            "max_length": 254
        },
        "role": {
            "required": False,
            "enum": ["MEMBER", "LEAD"],
            "default": "MEMBER"
        }
    },
    
    "activity": {
        "name": {
            "required": True,
            "min_length": 3,
            "max_length": 200
        },
        "description": {
            "required": True,
            "min_length": 10,
            "max_length": 2000
        },
        "points": {
            "required": True,
            "type": "integer",
            "minimum": 1,
            "maximum": 1000
        }
    },
    
    "action": {
        "activityId": {
            "required": True,
            "format": "uuid"
        },
        "description": {
            "required": True,
            "min_length": 10,
            "max_length": 1000
        },
        "proofHash": {
            "required": True,
            "pattern": r"^0x[a-fA-F0-9]{64}$"
        }
    },
    
    "validation": {
        "isValid": {
            "required": True,
            "type": "boolean"
        },
        "notes": {
            "required": False,
            "max_length": 500
        }
    }
}