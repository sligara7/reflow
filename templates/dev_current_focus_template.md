# Development Current Focus

Updated: <TIMESTAMP>

## IMMEDIATE NEXT ACTION
Set active service and enumerate initial environment bootstrap tasks.

## ACTIVE CONTEXT
- System: <REPLACE_SYSTEM_NAME>
- Stage: D1 (Initialization & Environment Bootstrap)
- Service: <PENDING_SELECTION>
- Dependency Layer: <UNKNOWN>

## WHAT TO DO RIGHT NOW
1. Populate dev_progress_tracker.json with all services from build_ready_index.json
2. Select first service in lowest dependency layer as active_service
3. Create service directory skeleton if missing
4. Verify runtimes & tooling for the service
5. Update dev_working_memory.json (active_service, next_action)

## DO NOT FORGET
- Every code artifact must trace to service_architecture.json or api_contracts.json
- Increment operations_since_refresh after each meaningful change
- Trigger context refresh before stage transition or after 6 operations
