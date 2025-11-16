# Social Scoring System - Infrastructure Layer

This directory contains the infrastructure layer implementation for the Social Scoring System, providing technical implementations without presentation concerns.

## 🏗️ Architecture Overview

The infrastructure layer implements:
- **Knox Authentication** - Token-based authentication infrastructure
- **PostgreSQL/SQLite** - Database persistence
- **Repository Pattern** - Domain interface implementations
- **Django ORM** - Database abstraction layer
- **Clean Architecture** - Pure infrastructure concerns only

## 📁 Directory Structure

```
src/infrastructure/
├── django_app/           # Django application core
│   ├── models.py         # Django ORM models
│   ├── settings.py       # Django configuration
│   ├── apps.py           # App configuration
│   └── signals.py        # Django signals
├── auth/                 # Authentication infrastructure
│   └── knox_authentication.py  # Knox auth implementation
└── persistence/          # Data persistence
    └── django_repositories.py  # Repository implementations
```

## 🔧 Infrastructure Components

### Authentication Infrastructure
- **Knox Token Management**: Stateless token authentication
- **User Context**: Integration with domain security
- **Session Management**: Token lifecycle management

### Database Infrastructure  
- **ORM Models**: Django models as persistence layer
- **Repository Implementations**: Bridge between domain and persistence
- **Database Signals**: Event handling for data consistency

### Configuration Infrastructure
- **Django Settings**: Database, authentication, and app configuration
- **Environment Variables**: Runtime configuration management
- **App Registration**: Django application setup

## 🗄️ Database Models

### PersonProfile
Maps domain Person to persistence:
- `person_id`: Domain aggregate ID
- `user`: Django User integration
- `role`: PARTICIPANT/LEAD/VALIDATOR
- `reputation_score`: Calculated score
- `is_active`: Status management

### Activity
Domain Activity persistence:
- `activity_id`: Domain aggregate ID
- `name`, `description`: Activity properties
- `lead`: Creator relationship
- `points`: Scoring configuration
- `is_active`: Lifecycle management

### Action
Domain Action persistence:
- `action_id`: Domain aggregate ID
- `activity`, `person`: Relationship mapping
- `proof_hash`: Cryptographic proof
- `status`: Validation state
- `points_awarded`: Score tracking

## 🔐 Authentication Infrastructure

### Knox Integration
```python
class KnoxAuthentication(BaseAuthentication):
    def authenticate(self, request: HttpRequest) -> Optional[tuple[User, AuthToken]]:
        # Token validation and user context extraction
        
    def get_domain_context(self, user: User) -> PersonSecurityContext:
        # Bridge to domain security model
```

### Token Management
- Stateless authentication
- Configurable token TTL
- Automatic token cleanup
- Domain context integration

## 🔄 Repository Pattern Implementation

### Domain Interface Compliance
```python
class DjangoPersonRepository(IPersonRepository):
    def save(self, person: Person) -> None:
        # Domain-to-ORM mapping
        
    def find_by_id(self, person_id: PersonId) -> Optional[Person]:
        # ORM-to-domain mapping
```

### Data Mapping
- Domain object ↔ ORM model conversion
- Value object serialization
- Aggregate boundary preservation
- Transaction management

## ⚙️ Configuration Management

### Django Settings
- Database configuration
- Authentication backends
- Signal handler registration
- Middleware configuration

### Environment Integration
```python
# settings.py
DATABASES = {
    'default': dj_database_url.parse(
        os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3')
    )
}

KNOX_TOKEN_MODEL = 'knox.AuthToken'
REST_KNOX_TOKEN_TTL = timedelta(hours=int(os.getenv('KNOX_TOKEN_TTL', '24')))
```

## 🔄 Signal Infrastructure

### Domain Event Integration
```python
@receiver(post_save, sender=Action)
def handle_action_save(sender: Any, instance: Action, **kwargs: Any) -> None:
    # Bridge ORM events to domain events
    # Maintain data consistency
    # Trigger reputation updates
```

### Data Consistency
- Automatic PersonProfile creation
- Reputation score maintenance
- Cross-model synchronization
- Event-driven updates

## 🏗️ Technical Foundation

### Database Abstraction
- Django ORM for query abstraction
- Migration management
- Index optimization
- Relationship mapping

### Type Safety
- Comprehensive type stubs for Django
- Static type checking support
- Runtime type validation
- IDE integration

### Performance Infrastructure
- Connection pooling
- Query optimization
- Index management
- Caching strategy

## 🚀 Deployment Infrastructure

### Database Setup
```bash
# Development
python manage.py makemigrations
python manage.py migrate

# Production
python manage.py migrate --run-syncdb
python manage.py collectstatic
```

### Environment Configuration
```env
DATABASE_URL=postgresql://user:pass@localhost/dbname
KNOX_TOKEN_TTL=86400
DEBUG=False
SECRET_KEY=production-secret-key
```

## 🔗 Layer Integration

### Domain Layer Bridge
- Repository pattern implementation
- Value object serialization
- Aggregate persistence
- Domain event handling

### Application Layer Support
- Service dependency injection
- Transaction management
- Configuration provision
- Infrastructure abstraction

### Presentation Layer Separation
- No HTTP concerns
- No URL routing
- No view logic
- Pure infrastructure focus

## 📝 Development Guidelines

### Infrastructure Principles
1. **Separation of Concerns**: Only infrastructure responsibilities
2. **Domain Independence**: No business logic
3. **Technology Isolation**: Framework-specific code isolated
4. **Configuration Management**: Environment-driven setup

### Code Organization
- Type stubs for development flexibility
- Clear domain-infrastructure boundaries
- Minimal external dependencies
- Testable components

### Performance Considerations
- Database query optimization
- Connection management
- Memory usage monitoring
- Scaling preparation

## 🔗 Related Documentation

- [Domain Layer Documentation](../domain/README.md)
- [Application Layer Documentation](../application/README.md)
- [Knox Authentication Docs](https://james1345.github.io/django-rest-knox/)
- [Django ORM Documentation](https://docs.djangoproject.com/en/stable/topics/db/)