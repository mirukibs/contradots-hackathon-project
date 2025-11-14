# Presentation Layer - HTTP API

This directory contains the HTTP REST API for the Social Scoring System, built with Flask.

## 📁 Structure

```
src/presentation/
├── app.py                    # Main Flask application
├── api_documentation.py      # API documentation and examples
├── controllers/              # HTTP controllers for each domain
│   ├── person_controller.py  # Person/User management endpoints
│   ├── activity_controller.py # Activity management endpoints  
│   └── action_controller.py  # Action submission endpoints
├── middleware/               # HTTP middleware
│   └── authentication.py    # JWT authentication and authorization
└── serializers/              # Request/response serialization
    └── base_serializers.py  # Data transformation utilities
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the API Server
```bash
python run_api.py
```

The API will be available at: `http://localhost:5000`

## 📚 API Endpoints

### 🏠 Health & Info
- `GET /health` - Health check
- `GET /api/v1/info` - API information

### 👤 Person Management
- `POST /api/v1/person/register` - Register new user
- `POST /api/v1/person/authenticate` - Login and get JWT token
- `GET /api/v1/person/profile` - Get current user profile (auth required)
- `GET /api/v1/person/profile/<id>` - Get specific user profile (auth required)
- `GET /api/v1/person/leaderboard` - Get leaderboard (public)

### 🎯 Activity Management
- `POST /api/v1/activity/` - Create activity (LEAD role required)
- `GET /api/v1/activity/` - List active activities (auth required)
- `GET /api/v1/activity/<id>` - Get activity details (auth required)
- `POST /api/v1/activity/<id>/deactivate` - Deactivate activity (creator only)

### ⚡ Action Management
- `POST /api/v1/action/` - Submit action (auth required)
- `GET /api/v1/action/pending` - Get pending validations (LEAD role required)
- `GET /api/v1/action/my-actions` - Get user's actions (auth required)
- `GET /api/v1/action/person/<id>` - Get person's actions (auth required)
- `POST /api/v1/action/<id>/validate` - Validate proof (LEAD role required)

## 🔐 Authentication

Most endpoints require JWT authentication:

```bash
# Include in request headers:
Authorization: Bearer <jwt_token>
```

### Getting a Token
```bash
curl -X POST http://localhost:5000/api/v1/person/authenticate \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

## 🔒 Authorization

Two roles are supported:
- **MEMBER**: Can submit actions, view activities, see profiles
- **LEAD**: All member permissions + create activities, validate proofs

## 📝 Example Usage

### 1. Register as LEAD
```bash
curl -X POST http://localhost:5000/api/v1/person/register \
  -H "Content-Type: application/json" \
  -d '{"name": "Jane Lead", "email": "jane@example.com", "role": "LEAD"}'
```

### 2. Create Activity
```bash
curl -X POST http://localhost:5000/api/v1/activity/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <jwt_token>" \
  -d '{"name": "Beach Cleanup", "description": "Clean the beach", "points": 50}'
```

### 3. Submit Action (as member)
```bash
curl -X POST http://localhost:5000/api/v1/action/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <member_token>" \
  -d '{"activityId": "<activity_uuid>", "description": "Cleaned beach section A", "proofHash": "0x1a2b3c..."}'
```

### 4. Validate Action (as lead)
```bash
curl -X POST http://localhost:5000/api/v1/action/<action_uuid>/validate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <lead_token>" \
  -d '{"isValid": true}'
```

### 5. Check Leaderboard
```bash
curl -X GET http://localhost:5000/api/v1/person/leaderboard
```

## 🏗️ Architecture

The presentation layer follows these principles:

### 🎯 **Separation of Concerns**
- **Controllers**: Handle HTTP concerns (routing, status codes, headers)
- **Serializers**: Transform between HTTP data and application DTOs
- **Middleware**: Handle cross-cutting concerns (auth, CORS, etc.)

### 🔐 **Security-First Design**
- JWT-based authentication
- Role-based authorization
- Input validation and sanitization
- Authorization checks before all operations

### 📊 **Clean Request/Response Flow**
```
HTTP Request → Controller → Serializer → Application Service → Domain
HTTP Response ← Controller ← Serializer ← Application Service ← Domain
```

### 🎨 **RESTful Design**
- Standard HTTP methods (GET, POST, PUT, DELETE)
- Resource-based URLs
- Consistent response formats
- Proper HTTP status codes

## 🔧 Error Handling

All errors return consistent JSON format:

```json
{
  "error": {
    "message": "Human readable error message",
    "code": "MACHINE_READABLE_CODE"
  }
}
```

Common error codes:
- `VALIDATION_ERROR` - Invalid request data
- `AUTHENTICATION_ERROR` - Login required or failed
- `AUTHORIZATION_ERROR` - Insufficient permissions
- `NOT_FOUND` - Resource not found
- `INTERNAL_ERROR` - Server error

## 🔌 Integration Points

The presentation layer integrates with:

1. **Application Services**: For business operations
2. **Authorization Service**: For permission validation
3. **Authentication Context**: For user identity
4. **Domain DTOs**: For data transfer
5. **Infrastructure**: Via dependency injection

## 🎯 Development Notes

### Current Status
✅ **Complete**: HTTP controllers, authentication, serialization
🚧 **Needs Implementation**: Infrastructure layer (repositories, event publishers)

### Next Steps
1. Implement infrastructure layer (in-memory or database)
2. Add comprehensive integration tests
3. Add API versioning
4. Add rate limiting
5. Add comprehensive logging
6. Add metrics and monitoring

### Testing the API
Since the infrastructure layer is not yet implemented, you'll need to either:
1. Create mock implementations of repositories
2. Implement the infrastructure layer
3. Use the provided memory implementations (when created)

The presentation layer is fully functional and ready to integrate with any implementation of the application and infrastructure layers.