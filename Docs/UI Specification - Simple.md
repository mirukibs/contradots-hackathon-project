# 🎨 Social Scoring System - UI Specification

**Simplified Frontend Requirements**  
*Based on Domain Model | Version: 1.0*

---

## 🏗️ **System Architecture**

### **Frontend Structure**
```
Mobile App (React Native or Flutter)
├── Authentication Layer
├── Role-based Navigation (Member/Lead)
├── Real-time Event Handling
└── Offline Data Caching
```

### **Core Dependencies**
- **State Management**: Redux/Zustand for app state
- **Real-time**: WebSocket for live updates
- **Navigation**: React Navigation (RN) or Flutter Navigator
- **Forms**: React Hook Form or Flutter Forms

---

## 📱 **Core Components**

### **1. User Components**
- `UserProfile` - Display person info & reputation
- `Leaderboard` - Ranked list of users
- `RoleIndicator` - Show MEMBER/LEAD badge

### **2. Activity Components**
- `ActivityCard` - Activity preview with points
- `ActivityList` - Scrollable activity feed
- `CreateActivityForm` - Lead-only creation form

### **3. Action Components**
- `ActionCard` - Action with status badge
- `ActionSubmitForm` - Submit action with proof
- `ActionStatus` - Timeline showing validation progress

### **4. Shared Components**
- `Dashboard` - Role-specific home screen
- `Notification` - Real-time event alerts
- `LoadingSpinner` - Loading states

---

## 🔄 **User Flows & Screens**

### **Authentication Flow**
```
1. Welcome Screen
2. Register/Login
3. Role Selection (Member/Lead)
4. → Dashboard
```

### **Member Flow**
```
Dashboard → Activities List → Activity Details → Submit Action → Status
     ↓
  Profile ← → Leaderboard ← → My Actions
```

### **Lead Flow**
```
Dashboard → Create Activity → Activity Management
     ↓
  Pending Validations → Validate Actions
     ↓
  + All Member flows
```

---

## 📊 **Required Data Models**

### **Person Data**
```typescript
interface Person {
  personId: string;
  name: string;
  email: string;
  role: "MEMBER" | "LEAD";
  reputationScore: number;
}
```

### **Activity Data**
```typescript
interface Activity {
  activityId: string;
  title: string;
  description: string;
  creatorId: string;
  points: number;
  isActive: boolean;
  createdAt: string;
}
```

### **Action Data**
```typescript
interface Action {
  actionId: string;
  personId: string;
  activityId: string;
  description: string;
  proofHash: string;
  status: "SUBMITTED" | "VALIDATED" | "REJECTED";
  submittedAt: string;
  verifiedAt?: string;
}
```

### **Real-time Events**
```typescript
interface ActionSubmittedEvent {
  type: "ActionSubmitted";
  actionId: string;
  personName: string;
  activityName: string;
}

interface ProofValidatedEvent {
  type: "ProofValidated";
  personId: string;
  isValid: boolean;
  reputationChange: number;
}
```

---

## 📱 **Screen Breakdown**

### **1. Welcome Screen**
- App logo/branding
- Login button
- Register button

### **2. Registration Screen**
- Name input
- Email input
- Role selector (Member/Lead)
- Submit button

### **3. Dashboard (Member)**
- Personal reputation score
- Recent activities (3-5 items)
- Quick action: "Submit Action"
- Navigation: Profile, Activities, Leaderboard

### **4. Dashboard (Lead)**
- Personal reputation score
- Created activities count
- Pending validations count
- Quick actions: "Create Activity", "Validate Actions"

### **5. Activities List**
- Search/filter bar
- Activity cards with:
  - Title, points, creator
  - "Join" button for members

### **6. Activity Details**
- Full description
- Points reward
- Creator info
- Participant count
- "Submit Action" button (members only)

### **7. Submit Action**
- Activity selector dropdown
- Description text area
- Proof upload/input
- Submit button

### **8. Profile Screen**
- User info display
- Reputation score (large)
- Action history list
- Settings/logout

### **9. Leaderboard**
- Ranked user list
- Current user highlighted
- Reputation scores

### **10. My Actions (Member)**
- Action list with status badges
- Filter by status
- Tap for details

### **11. Pending Validations (Lead)**
- Submitted actions list
- Proof review
- Approve/Reject buttons

---

## 🔄 **Data Flow Requirements**

### **Screen → Data Mapping**

| Screen | Data Needed | Real-time Updates |
|--------|------------|------------------|
| Dashboard | User profile, recent activities | Reputation changes |
| Activities List | All active activities | New activities |
| Activity Details | Activity info, participants | Participant count |
| Leaderboard | All users ranked | Rank changes |
| My Actions | User's actions | Status changes |
| Profile | User info | Reputation updates |

### **Form Data Requirements**

#### **Registration Form**
```typescript
interface RegisterForm {
  name: string;        // Required, min 2 chars
  email: string;       // Required, valid email
  role: "MEMBER" | "LEAD";  // Required
}
```

#### **Create Activity Form**
```typescript
interface CreateActivityForm {
  title: string;       // Required, max 100 chars
  description: string; // Required, max 500 chars  
  points: number;      // Required, 1-1000
}
```

#### **Submit Action Form**
```typescript
interface SubmitActionForm {
  activityId: string;  // Selected from dropdown
  description: string; // Required, max 300 chars
  proofHash: string;   // Required, hex format
}
```

---

## ⚡ **Real-time Updates**

### **Event Handling**
- **ActionSubmitted**: Update activity participant count
- **ProofValidated**: Update user reputation, refresh leaderboard
- **LeaderboardUpdated**: Update user rankings

### **UI Feedback Patterns**
- **Optimistic Updates**: Show immediate feedback
- **Loading States**: During API calls
- **Error Handling**: Retry mechanisms
- **Success Notifications**: Confirm actions

---

## 🔧 **Technical Notes**

### **State Management**
- Global state for user profile
- Local state for form data
- Real-time state for live updates

### **Navigation**
- Tab navigation for main sections
- Stack navigation for detail screens
- Role-based conditional rendering

### **Validation**
- Client-side form validation
- Server response error handling
- Real-time field validation

This simplified specification provides the essential screens and data flows needed to build the MVP, focusing on the core domain model requirements without over-engineering.