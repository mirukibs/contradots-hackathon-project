# Activity and Action API Documentation

This module provides RESTful API endpoints for managing activities and actions in the Social Scoring System.

## Overview

The Activity and Action API allows:
- **Leads** to create and manage activities
- **Participants** to submit actions for activities
- **Leads** to validate action proofs
- All authenticated users to view activities and their own actions

## Base URL

All endpoints are prefixed with: `/api/v1/`

## Authentication

All endpoints require authentication via JWT token. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## API Endpoints

### Activity Endpoints

#### 1. Create Activity
**POST** `/api/v1/activities/create/`

Create a new activity (Lead only).

**Request Body:**
```json
{
  "name": "Beach Cleanup",
  "description": "Clean up the local beach and collect plastic waste",
  "points": 50
}
```

**Response (201 Created):**
```json
{
  "message": "Activity created successfully",
  "activityId": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Validation Rules:**
- `name`: 3-200 characters, must contain at least one letter
- `description`: 10-1000 characters, cannot be empty
- `points`: 1-1000 (integer)

**Errors:**
- `400`: Invalid request data
- `401`: Authentication required
- `403`: Insufficient permissions (not a lead)

---

#### 2. Get Active Activities
**GET** `/api/v1/activities/`

Get all currently active activities.

**Response (200 OK):**
```json
{
  "activities": [
    {
      "activityId": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Beach Cleanup",
      "description": "Clean up the local beach and collect plastic waste",
      "points": 50,
      "leadName": "John Doe",
      "isActive": true
    },
    {
      "activityId": "650e8400-e29b-41d4-a716-446655440001",
      "name": "Tree Planting",
      "description": "Plant trees in the community park",
      "points": 30,
      "leadName": "Jane Smith",
      "isActive": true
    }
  ]
}
```

**Errors:**
- `401`: Authentication required

---

#### 3. Get Activity Details
**GET** `/api/v1/activities/<activity_id>/`

Get detailed information about a specific activity.

**Response (200 OK):**
```json
{
  "activityId": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Beach Cleanup",
  "description": "Clean up the local beach and collect plastic waste",
  "points": 50,
  "leadName": "John Doe",
  "isActive": true,
  "totalActions": 15,
  "validatedActions": 12
}
```

**Errors:**
- `401`: Authentication required
- `404`: Activity not found

---

#### 4. Deactivate Activity
**POST** `/api/v1/activities/deactivate/`

Deactivate an activity (Lead only).

**Request Body:**
```json
{
  "activityId": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response (200 OK):**
```json
{
  "message": "Activity deactivated successfully"
}
```

**Errors:**
- `400`: Invalid request data
- `401`: Authentication required
- `403`: Insufficient permissions
- `404`: Activity not found

---

### Action Endpoints

#### 5. Submit Action
**POST** `/api/v1/actions/submit/`

Submit a new action for an activity.

**Request Body:**
```json
{
  "activityId": "550e8400-e29b-41d4-a716-446655440000",
  "description": "Collected 5 bags of plastic waste from the beach",
  "proofHash": "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456"
}
```

**Response (201 Created):**
```json
{
  "message": "Action submitted successfully",
  "actionId": "750e8400-e29b-41d4-a716-446655440002"
}
```

**Validation Rules:**
- `activityId`: Valid UUID
- `description`: 10-500 characters
- `proofHash`: 32-128 hexadecimal characters

**Errors:**
- `400`: Invalid request data
- `401`: Authentication required
- `404`: Activity not found

---

#### 6. Get Pending Validations
**GET** `/api/v1/actions/pending/`

Get all actions pending validation (Lead only).

**Response (200 OK):**
```json
{
  "actions": [
    {
      "actionId": "750e8400-e29b-41d4-a716-446655440002",
      "personName": "Alice Johnson",
      "activityName": "Beach Cleanup",
      "description": "Collected 5 bags of plastic waste from the beach",
      "status": "pending",
      "submittedAt": "2025-11-17T14:30:00Z"
    },
    {
      "actionId": "850e8400-e29b-41d4-a716-446655440003",
      "personName": "Bob Williams",
      "activityName": "Tree Planting",
      "description": "Planted 10 saplings in the park",
      "status": "pending",
      "submittedAt": "2025-11-17T15:45:00Z"
    }
  ]
}
```

**Errors:**
- `401`: Authentication required
- `403`: Insufficient permissions (not a lead)

---

#### 7. Get My Actions
**GET** `/api/v1/actions/my-actions/`

Get all actions submitted by the current user.

**Response (200 OK):**
```json
{
  "actions": [
    {
      "actionId": "750e8400-e29b-41d4-a716-446655440002",
      "personName": "Alice Johnson",
      "activityName": "Beach Cleanup",
      "description": "Collected 5 bags of plastic waste from the beach",
      "status": "validated",
      "submittedAt": "2025-11-17T14:30:00Z"
    },
    {
      "actionId": "950e8400-e29b-41d4-a716-446655440004",
      "personName": "Alice Johnson",
      "activityName": "Tree Planting",
      "description": "Planted 5 saplings",
      "status": "pending",
      "submittedAt": "2025-11-17T16:00:00Z"
    }
  ]
}
```

**Errors:**
- `401`: Authentication required

---

#### 8. Validate Proof
**POST** `/api/v1/actions/validate/`

Validate or reject an action's proof (Lead only).

**Request Body:**
```json
{
  "actionId": "750e8400-e29b-41d4-a716-446655440002",
  "isValid": true,
  "validatorComment": "Great work! Clear evidence of beach cleanup."
}
```

**Response (200 OK):**
```json
{
  "message": "Proof validated successfully"
}
```

Or for rejection:

**Request Body:**
```json
{
  "actionId": "750e8400-e29b-41d4-a716-446655440002",
  "isValid": false,
  "validatorComment": "Proof image is unclear, please resubmit."
}
```

**Response (200 OK):**
```json
{
  "message": "Proof rejected"
}
```

**Validation Rules:**
- `actionId`: Valid UUID
- `isValid`: Boolean (required)
- `validatorComment`: 0-500 characters (optional)

**Errors:**
- `400`: Invalid request data
- `401`: Authentication required
- `403`: Insufficient permissions (not a lead)
- `404`: Action not found

---

## Error Response Format

All error responses follow this format:

```json
{
  "error": "ERROR_CODE",
  "message": "Human-readable error message",
  "details": {} // Optional, contains validation errors
}
```

### Common Error Codes

- `VALIDATION_ERROR`: Request data failed validation
- `AUTHORIZATION_ERROR`: User lacks required permissions
- `INTERNAL_ERROR`: Unexpected server error

---

## Status Codes

- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Unexpected server error

---

## Role-Based Access Control

### Lead Permissions
- Create activities
- Deactivate activities
- View all activities
- Validate action proofs
- View pending validations
- View their own actions

### Participant Permissions
- View all active activities
- Submit actions
- View their own actions

---

## Example Usage with cURL

### Create an Activity (as Lead)
```bash
curl -X POST http://localhost:8000/api/v1/activities/create/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Beach Cleanup",
    "description": "Clean up the local beach and collect plastic waste",
    "points": 50
  }'
```

### Submit an Action
```bash
curl -X POST http://localhost:8000/api/v1/actions/submit/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "activityId": "550e8400-e29b-41d4-a716-446655440000",
    "description": "Collected 5 bags of plastic waste from the beach",
    "proofHash": "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456"
  }'
```

### Get Active Activities
```bash
curl -X GET http://localhost:8000/api/v1/activities/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Validate Proof (as Lead)
```bash
curl -X POST http://localhost:8000/api/v1/actions/validate/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "actionId": "750e8400-e29b-41d4-a716-446655440002",
    "isValid": true,
    "validatorComment": "Great work! Clear evidence of beach cleanup."
  }'
```

---

## Integration Notes

### Application Layer Integration
The API integrates with the application layer services:
- `ActivityApplicationService` for activity operations
- `ActionApplicationService` for action operations

### Authentication Context
Each request extracts the user's authentication context to enforce:
- Role-based permissions (Lead vs Participant)
- User identity verification
- Authorization checks

### Domain Model
The API respects domain model boundaries:
- Commands are validated before execution
- Domain events are published for state changes
- Repository pattern is used for persistence

---

## Testing

The API can be tested using:
- **Postman**: Import the endpoints and test with different roles
- **cURL**: Use command-line examples provided above
- **Automated Tests**: Integration tests in `tests/presentation/api/`

---

## Future Enhancements

Planned improvements:
- Pagination for list endpoints
- Filtering and sorting capabilities
- File upload for proof attachments
- Real-time notifications via WebSockets
- Bulk action validation
- Activity categories and tags
