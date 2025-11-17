# Social Scoring System API Documentation

## Overview

The Social Scoring System API provides endpoints for managing activities, actions, and user authentication. The system integrates with blockchain (Polkadot testnet) for transparent and immutable record-keeping.

**Base URL**: `http://localhost:8000/api/v1`

**Authentication**: Token-based authentication using custom tokens

**Token Format**: `Bearer <hex-encoded-token>`

---

## Table of Contents

1. [Authentication](#authentication)
2. [Activity Endpoints](#activity-endpoints)
3. [Action Endpoints](#action-endpoints)
4. [Error Responses](#error-responses)
5. [Data Models](#data-models)

---

## Authentication

### Register User

Create a new user account.

**Endpoint**: `POST /auth/register/`

**Authentication**: Not required

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "fullName": "John Doe",
  "role": "lead"  // Optional, defaults to "lead"
}
```

**Response** (201 Created):
```json
{
  "message": "User registered successfully",
  "personId": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "role": "lead"
}
```

**Validation Rules**:
- Email: Valid email format, unique
- Password: Minimum 8 characters
- Full Name: Required, non-empty
- Role: Either "lead" or "member"

---

### Login

Authenticate and receive an access token.

**Endpoint**: `POST /auth/login/`

**Authentication**: Not required

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response** (200 OK):
```json
{
  "token": "7b22757365725f6964223a2022353530653834...",
  "personId": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "role": "lead"
}
```

**Using the Token**:

Include the token in the `Authorization` header for all authenticated requests:

```
Authorization: Token 7b22757365725f6964223a2022353530653834...
```

---

## Activity Endpoints

### Create Activity

Create a new activity (Lead only).

**Endpoint**: `POST /activity_action/create-activity/`

**Authentication**: Required (Lead role)

**Request Body**:
```json
{
  "name": "Community Cleanup",
  "description": "Clean up the local park and surrounding areas",
  "points": 50
}
```

**Field Constraints**:
- `name`: 3-200 characters
- `description`: 10-1000 characters
- `points`: 1-1000

**Response** (201 Created):
```json
{
  "message": "Activity created successfully",
  "activityId": "660e8400-e29b-41d4-a716-446655440001",
  "blockchainActivityId": 123456789,
  "transactionHash": "0x1234567890abcdef..."
}
```

**Important Notes**:
- The activity is **first created on the blockchain**
- The `blockchainActivityId` (integer) is converted to UUID format and used as the `activityId` in the database
- This ensures the database activity ID corresponds to the blockchain activity ID
- If blockchain creation fails, the activity is **not created** in the database

**Error Responses**:
- `400`: Invalid activity data
- `401`: Authentication required
- `403`: Insufficient permissions (not a lead)
- `500`: Blockchain error - activity creation failed

---

### Get Active Activities

Retrieve all currently active activities.

**Endpoint**: `GET /activity_action/activities/`

**Authentication**: Required

**Response** (200 OK):
```json
{
  "activities": [
    {
      "activityId": "660e8400-e29b-41d4-a716-446655440001",
      "name": "Community Cleanup",
      "description": "Clean up the local park and surrounding areas",
      "points": 50,
      "leadName": "John Doe",
      "isActive": true,
      "blockchain": {
        "name": "Community Cleanup",
        "description": "Clean up the local park...",
        "points": 50,
        "isActive": true,
        "leadId": "550e8400-e29b-41d4-a716-446655440000"
      }
    }
  ]
}
```

**Note**: The `blockchain` field contains data from the blockchain and may be omitted if blockchain query fails.

---

### Get Activity Details

Get detailed information about a specific activity.

**Endpoint**: `GET /activity_action/activities/{activityId}/`

**Authentication**: Required

**Path Parameters**:
- `activityId`: UUID of the activity

**Response** (200 OK):
```json
{
  "activityId": "660e8400-e29b-41d4-a716-446655440001",
  "name": "Community Cleanup",
  "description": "Clean up the local park and surrounding areas",
  "points": 50,
  "leadName": "John Doe",
  "isActive": true,
  "participantCount": 15,
  "totalActionsSubmitted": 18,
  "blockchain": {
    "name": "Community Cleanup",
    "description": "Clean up the local park...",
    "points": 50,
    "isActive": true,
    "leadId": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

**Error Responses**:
- `401`: Authentication required
- `404`: Activity not found

---

### Deactivate Activity

Deactivate an activity (Lead only).

**Endpoint**: `POST /activity_action/deactivate-activity/`

**Authentication**: Required (Lead role)

**Request Body**:
```json
{
  "activityId": "660e8400-e29b-41d4-a716-446655440001"
}
```

**Response** (200 OK):
```json
{
  "message": "Activity deactivated successfully",
  "transactionHash": "0x1234567890abcdef..."
}
```

**Error Responses**:
- `400`: Invalid request data
- `401`: Authentication required
- `403`: Insufficient permissions
- `404`: Activity not found

---

## Action Endpoints

### Submit Action

Submit a new action for an activity.

**Endpoint**: `POST /activity_action/submit-action/`

**Authentication**: Required

**Request Body**:
```json
{
  "activityId": "660e8400-e29b-41d4-a716-446655440001",
  "description": "Collected 5 bags of trash from the park",
  "proofHash": "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456"
}
```

**Field Constraints**:
- `activityId`: Valid UUID
- `description`: 10-500 characters
- `proofHash`: 32-128 hex characters (hash of proof image/document)

**Response** (201 Created):
```json
{
  "message": "Action submitted successfully",
  "actionId": "770e8400-e29b-41d4-a716-446655440002",
  "blockchainActionId": 987654321,
  "transactionHash": "0x1234567890abcdef..."
}
```

**Error Responses**:
- `400`: Invalid action data
- `401`: Authentication required
- `404`: Activity not found

---

### Get Pending Validations

Get all actions pending validation (Lead only).

**Endpoint**: `GET /activity_action/pending-validations/`

**Authentication**: Required (Lead role)

**Response** (200 OK):
```json
{
  "actions": [
    {
      "actionId": "770e8400-e29b-41d4-a716-446655440002",
      "activityId": "660e8400-e29b-41d4-a716-446655440001",
      "personId": "880e8400-e29b-41d4-a716-446655440003",
      "description": "Collected 5 bags of trash from the park",
      "proofHash": "a1b2c3d4e5f6...",
      "validationStatus": "pending",
      "submittedAt": "2025-11-17T10:30:00Z",
      "blockchain": {
        "personId": "880e8400-e29b-41d4-a716-446655440003",
        "activityId": "660e8400-e29b-41d4-a716-446655440001",
        "description": "Collected 5 bags...",
        "proofHash": "a1b2c3d4e5f6...",
        "status": "Pending"
      }
    }
  ]
}
```

**Error Responses**:
- `401`: Authentication required
- `403`: Insufficient permissions (not a lead)

---

### Get My Actions

Get all actions submitted by the current user.

**Endpoint**: `GET /activity_action/my-actions/`

**Authentication**: Required

**Response** (200 OK):
```json
{
  "actions": [
    {
      "actionId": "770e8400-e29b-41d4-a716-446655440002",
      "activityId": "660e8400-e29b-41d4-a716-446655440001",
      "personId": "550e8400-e29b-41d4-a716-446655440000",
      "description": "Collected 5 bags of trash from the park",
      "proofHash": "a1b2c3d4e5f6...",
      "validationStatus": "validated",
      "submittedAt": "2025-11-17T10:30:00Z",
      "validatedAt": "2025-11-17T11:45:00Z"
    }
  ]
}
```

**Error Responses**:
- `401`: Authentication required

---

### Validate Proof

Validate or reject an action's proof (Lead only).

**Endpoint**: `POST /activity_action/validate-proof/`

**Authentication**: Required (Lead role)

**Request Body**:
```json
{
  "actionId": "770e8400-e29b-41d4-a716-446655440002",
  "isValid": true,
  "validatorComment": "Proof verified - good work!"  // Optional
}
```

**Response** (200 OK - Valid):
```json
{
  "message": "Proof validated successfully",
  "transactionHash": "0x1234567890abcdef..."
}
```

**Response** (200 OK - Rejected):
```json
{
  "message": "Proof rejected",
  "transactionHash": "0x1234567890abcdef..."
}
```

**Error Responses**:
- `400`: Invalid validation data
- `401`: Authentication required
- `403`: Insufficient permissions (not a lead)
- `404`: Action not found

---

## Error Responses

All error responses follow a consistent format:

```json
{
  "error": "ERROR_CODE",
  "message": "Human-readable error message",
  "details": {}  // Optional, contains validation errors
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid request data or validation failed |
| `AUTHORIZATION_ERROR` | 403 | Insufficient permissions for the operation |
| `NOT_FOUND` | 404 | Requested resource not found |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

### Example Error Response

```json
{
  "error": "VALIDATION_ERROR",
  "message": "Invalid activity data",
  "details": {
    "name": ["This field is required."],
    "points": ["Ensure this value is less than or equal to 1000."]
  }
}
```

---

## Data Models

### User Roles

- **Lead**: Can create activities, deactivate activities, and validate action proofs
- **Member**: Can view activities and submit actions

### Activity Status

- **Active** (`isActive: true`): Activity is accepting action submissions
- **Inactive** (`isActive: false`): Activity is closed, no new actions accepted

### Action Validation Status

- **Pending**: Action submitted, awaiting validation
- **Validated**: Action approved by lead
- **Rejected**: Action rejected by lead

---

## Blockchain Integration

The system integrates with Polkadot testnet for transparent record-keeping:

- **Network**: Polkadot Asset Hub Testnet
- **Contract Address**: `0x7e50f3D523176C696AEe69A1245b12EBAE0a17dd`
- **RPC Endpoint**: `https://testnet-passet-hub-eth-rpc.polkadot.io`

### Blockchain Data

Most responses include a `blockchain` field with on-chain data:

```json
{
  "blockchain": {
    "name": "Activity Name",
    "description": "Activity Description",
    "points": 50,
    "isActive": true,
    "leadId": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

If blockchain query fails, a warning is included instead:

```json
{
  "blockchain_warning": "Blockchain data unavailable: Connection timeout"
}
```

---

## Rate Limiting

Rate limiting is applied per authentication token:

- **Default**: 100 requests per hour
- **Burst**: Up to 10 requests per second

When rate limit is exceeded, the API returns:

```json
{
  "error": "RATE_LIMIT_EXCEEDED",
  "message": "Too many requests. Please try again later.",
  "retryAfter": 3600
}
```

---

## Example Workflows

### Complete Activity Creation and Participation Flow

1. **Register as Lead**:
   ```bash
   POST /auth/register/
   {
     "email": "lead@example.com",
     "password": "LeadPass123!",
     "fullName": "Lead User",
     "role": "lead"
   }
   ```

2. **Login**:
   ```bash
   POST /auth/login/
   {
     "email": "lead@example.com",
     "password": "LeadPass123!"
   }
   # Save the returned token
   ```

3. **Create Activity**:
   ```bash
   POST /activity_action/create-activity/
   Authorization: Token <your-token>
   {
     "name": "Park Cleanup",
     "description": "Help clean our community park",
     "points": 50
   }
   # Save the returned activityId
   ```

4. **Register as Member**:
   ```bash
   POST /auth/register/
   {
     "email": "member@example.com",
     "password": "MemberPass123!",
     "fullName": "Member User",
     "role": "member"
   }
   ```

5. **Member Submits Action**:
   ```bash
   POST /activity_action/submit-action/
   Authorization: Token <member-token>
   {
     "activityId": "<activity-id>",
     "description": "Collected 3 bags of trash",
     "proofHash": "abc123def456..."
   }
   ```

6. **Lead Validates Action**:
   ```bash
   POST /activity_action/validate-proof/
   Authorization: Token <lead-token>
   {
     "actionId": "<action-id>",
     "isValid": true
   }
   ```

---

## Support

For issues or questions:
- GitHub: [mirukibs/contradots-hackathon-project](https://github.com/mirukibs/contradots-hackathon-project)
- Documentation: See `/Docs` folder in repository

---

## Version History

- **v1.0** (November 2025): Initial API release with blockchain integration
