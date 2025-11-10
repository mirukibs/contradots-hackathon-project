# 🎯 Social Scoring System - Developer Package

## 📋 **System Overview**

This is a **blockchain-verified reputation system** for communities to incentivize member participation through gamified scoring. Members earn reputation points by participating in activities, with all actions verified through blockchain proof to prevent gaming.

## 🏗️ **Architecture Overview**

The system follows **Domain-Driven Design (DDD)** with **CQRS (Command Query Responsibility Segregation)** and **Event Sourcing** patterns:

- **Domain Layer**: Core business logic and rules
- **Application Layer**: Orchestrates domain operations via CQRS
- **Event-Driven**: Cross-aggregate communication via domain events
- **Blockchain Integration**: Proof validation via external blockchain infrastructure

## 📊 **Domain Model**

### **Core Aggregates**
1. **Person Aggregate**: User management and reputation tracking
2. **Activity Aggregate**: Community activities that award reputation  
3. **Action Aggregate**: Member participation with blockchain proof

### **Key Business Rules**
- **Members** can participate in activities and submit proof
- **Leads** can create and manage activities  
- **Reputation points** are immediately reserved but only confirmed after blockchain proof validation
- **Invalid proofs** result in point reversal to maintain system integrity

## 🔄 **Event-Driven Flow**

```
1. Member submits action → ActionSubmittedEvent
   ├── Reputation points reserved (immediate feedback)
   └── Blockchain validation initiated

2. Blockchain validates proof → ProofValidatedEvent  
   ├── Valid: Points confirmed
   └── Invalid: Points reverted
```

## 🎯 **Core Use Cases**

1. **Register User** (Member/Lead role assignment)
2. **Create Activity** (Lead only - defines point rewards)
3. **Submit Action** (Member participation with proof)
4. **Validate Proof** (Blockchain callback integration)
5. **View Leaderboard** (Real-time reputation rankings)
6. **Browse Activities** (Available participation opportunities)

## 📁 **Project Structure**

```
/src/domain/           # Core business logic
  ├── aggregates/      # Person, Activity, Action
  ├── events/          # ActionSubmittedEvent, ProofValidatedEvent  
  ├── services/        # ReputationService
  └── repositories/    # Domain repository interfaces

/src/application/      # Application services (CQRS)
  ├── commands/        # Input validation objects
  ├── queries/         # Read-optimized DTOs
  ├── services/        # PersonApp, ActivityApp, ActionApp services
  └── handlers/        # Event handlers for projections

/src/infrastructure/   # External integrations
  ├── repositories/    # Database implementations
  ├── events/          # Event store and publishing
  └── blockchain/      # Proof validation integration
```

## 🚀 **Implementation Priority**

### **Phase 1 - Core MVP**
- [ ] Domain entities and repositories
- [ ] Basic application services
- [ ] In-memory event publishing
- [ ] Manual proof validation (for demo)

### **Phase 2 - Blockchain Integration**  
- [ ] Event store implementation
- [ ] Blockchain proof validation
- [ ] Automated proof callbacks

### **Phase 3 - Optimization**
- [ ] CQRS read projections
- [ ] Performance optimizations
- [ ] Advanced blockchain features

## 📚 **Developer Resources**

- **Domain Model Diagram**: `Docs/Simplified Core Domain Model.puml`
- **Application Architecture**: `Docs/Unified Application Layer.puml`
- **Implementation Guide**: `Docs/Application Layer Guide.md`
- **CQRS Details**: `Docs/CQRS Implementation Guide.md`

## 🔧 **Technology Stack**

- **Backend**: Python/Django (already initialized)
- **Database**: PostgreSQL (command + query stores)
- **Events**: Custom event publishing (Phase 1) → Apache Kafka (Phase 2)  
- **Blockchain**: External API integration for proof validation
- **Frontend**: React/Next.js (future)

## 💡 **Key Design Decisions**

### **Why CQRS?**
- **Performance**: Optimized read queries for leaderboards and activity lists
- **Scalability**: Separate read/write scaling
- **Complexity**: Kept simple for hackathon MVP

### **Why Event-Driven?**
- **Blockchain Integration**: Perfect for async proof validation callbacks
- **Loose Coupling**: Aggregates communicate without direct dependencies
- **Audit Trail**: Complete history of reputation changes

### **Why Domain-Driven Design?**
- **Business Focus**: Code directly reflects business rules and language
- **Maintainability**: Clear boundaries and responsibilities
- **Collaboration**: Non-technical stakeholders can understand the model

## ⚠️ **Important Notes**

- **Hackathon Scope**: Focus on core features, avoid over-engineering
- **Event Consistency**: Start with in-process events, add durability later
- **Proof Validation**: Mock blockchain integration initially
- **Performance**: Optimize reads with CQRS projections as needed

## 🎯 **Success Criteria**

✅ Users can register and be assigned roles  
✅ Leads can create activities with point values  
✅ Members can submit actions with proof hashes  
✅ System reserves points immediately (good UX)  
✅ Blockchain validation confirms or reverts points (integrity)  
✅ Leaderboard shows real-time reputation rankings  
✅ Event-driven architecture ready for production scaling  

This architecture provides a solid foundation for rapid hackathon development while being production-ready for future scaling and blockchain integration.