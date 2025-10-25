# Basic Operational Test (BOT) - Decision Flow

## Test Scenario: Personal Task Management System

### Objective
Build a complete working task management web application using only reflow workflows to verify the decision flow actually works for real system development.

### System Requirements
Create a task management system with these capabilities:
- **User Service**: User authentication and profiles
- **Task Service**: CRUD operations for tasks  
- **Notification Service**: Email/SMS notifications for task deadlines
- **Web Interface**: Simple web UI for task management
- **Database**: Persistent storage for users and tasks
- **API Gateway**: Single entry point for all requests

### Success Criteria
✅ **Architecture Phase Complete**: 
- All 6 services architecturally defined
- Service interfaces documented
- Architecture passes all reflow validations

✅ **Development Phase Complete**:
- All services have working code  
- Services communicate via defined interfaces
- Basic web interface functional

✅ **Deployment Phase Complete**:
- System deployable (Docker/containers)
- All services start and communicate
- Web interface accessible and functional
- Can create user, add task, get notification

✅ **User Experience**:
- Process completed using only reflow documentation
- No external help required beyond reflow workflows
- Clear path from requirements to working system

### Failure Criteria
❌ **Process Failures**:
- User gets stuck and cannot proceed with reflow workflow
- Workflow instructions unclear or contradictory
- Required tools missing or non-functional

❌ **Technical Failures**:
- Generated architecture has critical flaws
- Service interfaces incompatible
- Generated code doesn't compile/run
- System fails to deploy or function

❌ **Operational Failures**:
- End-to-end system doesn't work
- User cannot complete basic task management workflow
- System crashes or has critical bugs

### Test Execution Steps

#### Phase 1: Architecture (2-3 hours expected)
1. **Start**: Use reflow decision_flow.json to architect the task management system
2. **Define Services**: Create architecture for all 6 services
3. **Define Interfaces**: Document how services communicate  
4. **Validate**: Run all reflow architecture validation tools
5. **Output**: build_ready_index.json and complete architecture docs

**Expected Evidence**:
- `specs/machine/index.json` with all 6 services
- Service architecture files for each service
- Interface contract documents (ICDs)
- Architecture validation reports (all pass)

#### Phase 2: Development (1-2 days expected)  
1. **Bootstrap**: Initialize development environment using reflow
2. **Implement Services**: Build working code for all services
3. **Integration**: Connect services via defined interfaces
4. **Testing**: Verify service-to-service communication
5. **Web Interface**: Build basic task management UI

**Expected Evidence**:
- Working source code in `services/` directories
- Services can start independently
- Inter-service communication functional
- Basic web interface serves pages

#### Phase 3: Deployment (4-6 hours expected)
1. **Package**: Create deployment artifacts (Docker containers)
2. **Deploy**: Start all services in coordinated fashion
3. **Integration Test**: Verify end-to-end functionality
4. **User Acceptance**: Complete actual task management workflow

**Expected Evidence**:
- All services running and healthy
- Web interface accessible
- Can create user account
- Can create/view/complete tasks  
- Can receive notifications (email/mock)

### Documentation Requirements

Document every step, including:
- **Time spent** on each phase
- **Pain points** and confusion encountered
- **Workflow adherence** - what worked, what didn't
- **External help needed** (failures if required)
- **Final system functionality** (screenshot/demo)

### Pass/Fail Decision

**PASS**: Complete working task management system deployed and functional, built using only reflow workflows within reasonable time (2-3 days total).

**FAIL**: Unable to complete system, system doesn't work, or external help required beyond reflow documentation.

### Current System Assessment

**dnd_reflow Status**: Claims to be "ready for production" but you (the user) have never actually used it to build and deploy a working system. This BOT will verify if that claim is accurate.

**Test Date**: TBD
**Tester**: User (ajs7)  
**Status**: Ready to execute

This BOT will provide definitive evidence of whether the decision flow workflow actually enables users to build working systems or needs further development.