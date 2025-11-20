# User Scenarios

**System Name**: TODO API Service
**Version**: 1.0.0
**Date**: 2025-11-19

---

## User Personas

### Persona 1: Individual User
- **Name**: Sarah, Software Developer
- **Goals**: Track daily tasks, organize work items
- **Technical Level**: High
- **Usage Pattern**: Multiple times daily via API client or custom application

### Persona 2: Application Developer
- **Name**: Mike, Frontend Developer
- **Goals**: Integrate TODO functionality into a web application
- **Technical Level**: High
- **Usage Pattern**: API integration for end-user applications

---

## Use Cases

### UC-1: Create a New TODO
**Actor**: Individual User (Sarah)
**Goal**: Add a new task to track
**Preconditions**: None
**Steps**:
1. User sends POST request with title="Fix login bug" and description="Investigate SSO timeout issue"
2. System creates TODO with unique ID and timestamp
3. System returns TODO object with ID and creation time
4. User confirms task was added

**Success Criteria**: TODO appears in list with correct details

---

### UC-2: View All TODOs
**Actor**: Individual User (Sarah)
**Goal**: See all current tasks
**Preconditions**: At least one TODO exists
**Steps**:
1. User sends GET request to list endpoint
2. System retrieves all TODOs from database
3. System returns array of TODO objects
4. User reviews task list

**Success Criteria**: All TODOs displayed with accurate information

---

### UC-3: Update TODO Details
**Actor**: Individual User (Sarah)
**Goal**: Modify task information
**Preconditions**: TODO exists
**Steps**:
1. User sends PUT request with updated title, description, or priority
2. System validates TODO exists
3. System updates fields
4. System returns updated TODO object
5. User confirms changes saved

**Success Criteria**: Modified TODO reflects new information

---

### UC-4: Mark TODO as Complete
**Actor**: Individual User (Sarah)
**Goal**: Mark task as finished
**Preconditions**: TODO exists with status="pending"
**Steps**:
1. User sends PATCH request to mark TODO complete
2. System updates status to "completed"
3. System returns updated TODO
4. User confirms task marked done

**Success Criteria**: TODO status changed to completed

---

### UC-5: Search TODOs
**Actor**: Individual User (Sarah)
**Goal**: Find specific tasks by keyword
**Preconditions**: Multiple TODOs exist
**Steps**:
1. User sends GET request with search query="login"
2. System searches title and description fields
3. System returns matching TODOs
4. User finds relevant task

**Success Criteria**: Search returns TODOs containing search term

---

### UC-6: Delete Completed TODO
**Actor**: Individual User (Sarah)
**Goal**: Remove finished task
**Preconditions**: TODO exists
**Steps**:
1. User sends DELETE request with TODO ID
2. System removes TODO from database
3. System returns confirmation
4. User confirms deletion

**Success Criteria**: TODO no longer appears in list

---

### UC-7: Filter TODOs by Priority
**Actor**: Individual User (Sarah)
**Goal**: View high-priority tasks only
**Preconditions**: TODOs exist with different priorities
**Steps**:
1. User sends GET request with filter priority="high"
2. System filters TODOs by priority level
3. System returns filtered list
4. User reviews high-priority tasks

**Success Criteria**: Only high-priority TODOs returned

---

## User Journey Maps

### Journey 1: Daily Task Management
1. **Morning**: User lists all pending TODOs to plan day
2. **Midday**: User adds new TODO for urgent issue
3. **Afternoon**: User marks completed TODO as done
4. **Evening**: User reviews remaining tasks, updates priorities

### Journey 2: Application Integration
1. **Development**: Developer reviews API documentation
2. **Implementation**: Developer integrates TODO endpoints into web app
3. **Testing**: Developer verifies CRUD operations work correctly
4. **Deployment**: Developer launches application with TODO features

---

## Scenarios

### Scenario 1: High Workload Day
- Sarah has 15 active TODOs
- Creates 5 new TODOs during the day
- Marks 8 as complete
- Updates priorities on 3 items
- Searches for "urgent" to find critical tasks
- **System must handle all operations smoothly under 100ms**

### Scenario 2: Fresh Start
- Sarah completes all TODOs
- Deletes completed items
- Starts new week with empty list
- Adds new set of TODOs
- **System must support batch operations efficiently**
