# Technical Design: As-Fielded Architecture Tracking

**Feature**: As-Fielded Architecture Tracking
**Design Date**: 2025-10-26
**Version**: 1.0.0
**Addresses**: GitHub Issue #6

## Design Overview

This feature introduces a three-tier architecture lifecycle tracking system: **as-designed** → **as-built** → **as-fielded**.

**Key Insight**: The systems engineering graph represents an idealized architecture. Reality inevitably differs due to implementation and operational constraints. Tracking these differences provides:
1. Accountability (how close is implementation to design?)
2. Feedback loop (are designs realistic and implementable?)
3. Documentation compliance (as-built docs required in many industries)
4. Continuous improvement (feed operational insights back to design)

## Architecture Lifecycle Phases

```
SE-06: Systems Engineering Complete
  ↓ generates
system_of_systems_graph.json (AS-DESIGNED)
  ↓
D-06: Development Complete
  ↓ generates
system_of_systems_graph_as_built.json (AS-BUILT)
  ↓ + delta report (designed → built)
  ↓
TO-06: Operational Testing Complete
  ↓ generates
system_of_systems_graph_as_fielded.json (AS-FIELDED)
  ↓ + delta report (designed → fielded, built → fielded)
```

## File Naming Convention

| Phase | Filename | Location |
|-------|----------|----------|
| As-Designed | `system_of_systems_graph.json` | `specs/machine/graphs/` |
| As-Built | `system_of_systems_graph_as_built.json` | `specs/machine/graphs/` |
| As-Fielded | `system_of_systems_graph_as_fielded.json` | `specs/machine/graphs/` |
| Delta Report (Designed→Built) | `architecture_delta_designed_to_built_{date}.json` | `specs/machine/graphs/` |
| Delta Report (Designed→Fielded) | `architecture_delta_designed_to_fielded_{date}.json` | `specs/machine/graphs/` |
| Delta Report (Built→Fielded) | `architecture_delta_built_to_fielded_{date}.json` | `specs/machine/graphs/` |

## Tool 1: `generate_as_built_architecture.py`

### Purpose
Reverse-engineer architecture from implemented source code.

### Algorithm

```python
1. Scan services/ directory for implemented services
2. For each service directory:
   a. Parse service_architecture.json (if exists) to get expected structure
   b. Scan src/ for actual code
   c. Extract REST endpoints (Flask @app.route, FastAPI @app.get, etc.)
   d. Extract function signatures (Python def statements)
   e. Parse requirements.txt for dependencies
   f. Parse config files for database connections, message queues
3. Build nodes array (services/components)
4. Build edges array (interfaces/dependencies)
5. Add metadata: architecture_type="as_built", generation_method="static_code_analysis"
6. Write system_of_systems_graph_as_built.json
7. Run compare_architectures.py (designed vs built)
8. Generate delta report
```

### Code Structure

```python
class AsBuiltArchitectureGenerator:
    def __init__(self, system_root: Path):
        self.system_root = system_root
        self.services_dir = system_root / "services"
        self.designed_graph_path = system_root / "specs/machine/graphs/system_of_systems_graph.json"

    def scan_services(self) -> List[ServiceInfo]:
        """Scan services/ directory and extract service information"""

    def extract_rest_endpoints(self, service_path: Path) -> List[Endpoint]:
        """Parse Python code using AST to find REST endpoints"""
        # Use ast.parse to find decorators like @app.route, @app.get

    def extract_function_signatures(self, service_path: Path) -> List[Function]:
        """Parse Python code to find function definitions"""

    def extract_dependencies(self, service_path: Path) -> List[Dependency]:
        """Parse requirements.txt, pyproject.toml"""

    def extract_database_connections(self, service_path: Path) -> List[Database]:
        """Look for SQLAlchemy, psycopg2, motor, etc."""

    def build_graph(self, services: List[ServiceInfo]) -> Dict:
        """Construct system_of_systems_graph format"""

    def generate(self) -> Path:
        """Main entry point - generate as-built graph"""
```

### Command-Line Interface

```bash
python3 tools/generate_as_built_architecture.py \
  --system-root <path_to_system> \
  --output <path_to_output_graph> \
  --compare-to-designed  # Optional: generate delta report immediately
```

### Dependencies
- Python 3.8+ standard library: `ast`, `pathlib`, `json`, `argparse`
- No external dependencies

### Estimated Complexity
- **Lines of Code**: 600-800
- **Effort**: 8-12 hours
- **Difficulty**: MEDIUM (AST parsing, graph construction)

## Tool 2: `generate_as_fielded_architecture.py`

### Purpose
Capture architecture from deployed/running system.

### Algorithm

```python
1. Check deployment method:
   - If docker-compose.yml exists → parse it
   - If Kubernetes manifests exist → parse them
   - If Docker containers running → query Docker API
2. For each deployed service:
   a. Get service name, image, ports
   b. Query health endpoints (/health, /ready)
   c. Check network connections (netstat/lsof)
   d. Get resource usage (actual CPU/memory vs limits)
3. Discover service dependencies:
   - Observed network traffic (which services talk to which)
   - Environment variables (DATABASE_URL, RABBITMQ_URL, etc.)
4. Build nodes array (deployed services)
5. Build edges array (observed connections)
6. Add metadata: architecture_type="as_fielded", environment="production|staging|dev", deployment_date
7. Write system_of_systems_graph_as_fielded.json
8. Run compare_architectures.py (designed vs fielded, built vs fielded)
9. Generate delta reports
```

### Code Structure

```python
class AsFieldedArchitectureGenerator:
    def __init__(self, system_root: Path, environment: str = "production"):
        self.system_root = system_root
        self.environment = environment
        self.docker_compose_path = system_root / "docker-compose.yml"

    def detect_deployment_method(self) -> str:
        """Detect if docker-compose, k8s, or other"""

    def parse_docker_compose(self) -> List[ServiceInfo]:
        """Parse docker-compose.yml for service definitions"""
        # Use PyYAML to parse

    def query_docker_api(self) -> List[ContainerInfo]:
        """Query Docker API for running containers"""
        # Use docker-py or subprocess + docker CLI

    def check_health_endpoints(self, service: str, port: int) -> HealthStatus:
        """HTTP GET /health, /ready"""

    def discover_network_connections(self) -> List[Connection]:
        """Use netstat/lsof to find active connections"""
        # subprocess.run(['netstat', '-an'])

    def map_environment_dependencies(self, service: str) -> List[Dependency]:
        """Parse env vars for DATABASE_URL, etc."""

    def build_graph(self, services: List[ServiceInfo]) -> Dict:
        """Construct system_of_systems_graph format"""

    def generate(self) -> Path:
        """Main entry point - generate as-fielded graph"""
```

### Command-Line Interface

```bash
python3 tools/generate_as_fielded_architecture.py \
  --system-root <path_to_system> \
  --environment production|staging|dev \
  --output <path_to_output_graph> \
  --compare-to-designed  # Optional: generate delta reports
  --compare-to-built     # Optional: generate delta report vs as-built
```

### Dependencies
- Python 3.8+ standard library: `subprocess`, `pathlib`, `json`, `argparse`
- Optional: `pyyaml` (for docker-compose parsing), `docker` (for Docker API)
  - Fallback: Use subprocess + docker CLI / kubectl

### Estimated Complexity
- **Lines of Code**: 700-900
- **Effort**: 10-14 hours
- **Difficulty**: MEDIUM-HIGH (runtime inspection, multiple deployment methods)

## Tool 3: `compare_architectures.py`

### Purpose
Compare two architecture graphs and generate delta report.

### Algorithm

```python
1. Load graph A (from JSON)
2. Load graph B (to JSON)
3. Extract node sets: nodes_A, nodes_B
4. Compute node deltas:
   - added_nodes = nodes_B - nodes_A
   - removed_nodes = nodes_A - nodes_B
   - common_nodes = nodes_A ∩ nodes_B
   - For common nodes: compare properties (ports, dependencies, capabilities)
5. Extract edge sets: edges_A, edges_B
6. Compute edge deltas:
   - added_edges = edges_B - edges_A
   - removed_edges = edges_A - edges_B
   - common_edges = edges_A ∩ edges_B
   - For common edges: compare properties (protocol, endpoints)
7. Calculate similarity scores:
   - node_similarity = |nodes_A ∩ nodes_B| / |nodes_A ∪ nodes_B|
   - edge_similarity = |edges_A ∩ edges_B| / |edges_A ∪ edges_B|
   - property_similarity = average(property matches for common nodes/edges)
   - overall_similarity = 0.4 × node_similarity + 0.4 × edge_similarity + 0.2 × property_similarity
8. Classify changes:
   - BREAKING: removed nodes, removed edges, incompatible property changes
   - NON_BREAKING: added nodes, added edges, compatible property changes
9. Generate recommendations:
   - If similarity < 70%: "Significant drift - review design or implementation"
   - If removed interfaces: "BREAKING CHANGE - version increment required"
10. Write delta report JSON
```

### Code Structure

```python
class ArchitectureComparator:
    def __init__(self, graph_a_path: Path, graph_b_path: Path):
        self.graph_a = load_json(graph_a_path)
        self.graph_b = load_json(graph_b_path)

    def extract_nodes(self, graph: Dict) -> Set[str]:
        """Extract set of node IDs"""

    def extract_edges(self, graph: Dict) -> Set[Tuple[str, str]]:
        """Extract set of (from_node, to_node) tuples"""

    def compute_node_deltas(self) -> NodeDeltas:
        """Find added/removed/modified nodes"""

    def compute_edge_deltas(self) -> EdgeDeltas:
        """Find added/removed/modified edges"""

    def calculate_similarity(self) -> SimilarityScore:
        """Calculate overall similarity score"""

    def classify_changes(self, deltas: Deltas) -> ChangeClassification:
        """Categorize as BREAKING vs NON_BREAKING"""

    def generate_recommendations(self, similarity: float, classification: ChangeClassification) -> List[str]:
        """Generate actionable recommendations"""

    def compare(self) -> DeltaReport:
        """Main entry point - generate delta report"""
```

### Command-Line Interface

```bash
python3 tools/compare_architectures.py \
  --from <path_to_graph_A> \
  --to <path_to_graph_B> \
  --output <path_to_delta_report> \
  --verbose  # Optional: detailed output
```

### Dependencies
- Python 3.8+ standard library: `json`, `pathlib`, `argparse`, `typing`

### Estimated Complexity
- **Lines of Code**: 500-700
- **Effort**: 6-10 hours
- **Difficulty**: MEDIUM (graph comparison, similarity metrics)

## Workflow Integration

### Workflow 03: Development (`workflows/03-development.json`)

**Modification**: Enhance step D-06 (Release Build)

**Current D-06 Actions**:
- D-06-A01: Final code review
- D-06-A02: Version increment
- D-06-A03: Build artifacts
- D-06-A04: Generate release notes
- D-06-A05: Tag release
- D-06-A06: Publish artifacts

**New Action Added**:
- **D-06-A07: Generate As-Built Architecture**
  - Description: "Reverse-engineer architecture from implemented code and compare to as-designed"
  - Tool: `python3 tools/generate_as_built_architecture.py --system-root {system_root} --compare-to-designed`
  - Outputs:
    - `specs/machine/graphs/system_of_systems_graph_as_built.json`
    - `specs/machine/graphs/architecture_delta_designed_to_built_{date}.json`
  - Success criteria:
    - As-built graph generated
    - Delta report shows similarity score
    - If similarity < 70%, warn user
    - If breaking changes detected, recommend version increment

### Workflow 04: Testing & Operations (`workflows/04-testing_operations.json`)

**Modification**: Enhance step TO-06 (Release Readiness)

**Current TO-06 Actions**:
- TO-06-A01: Final operational test
- TO-06-A02: Performance validation
- TO-06-A03: Security scan
- TO-06-A04: Backup verification
- TO-06-A05: Runbook validation
- TO-06-A06: Release certification
- TO-06-A07: Handoff documentation

**New Actions Added**:
- **TO-06-A08: Generate As-Fielded Architecture**
  - Description: "Capture architecture from deployed system"
  - Tool: `python3 tools/generate_as_fielded_architecture.py --system-root {system_root} --environment production`
  - Outputs: `specs/machine/graphs/system_of_systems_graph_as_fielded.json`

- **TO-06-A09: Compare As-Fielded to As-Designed and As-Built**
  - Description: "Generate delta reports comparing fielded architecture to design and implementation"
  - Tools:
    - `python3 tools/compare_architectures.py --from system_of_systems_graph.json --to system_of_systems_graph_as_fielded.json --output architecture_delta_designed_to_fielded_{date}.json`
    - `python3 tools/compare_architectures.py --from system_of_systems_graph_as_built.json --to system_of_systems_graph_as_fielded.json --output architecture_delta_built_to_fielded_{date}.json`
  - Outputs:
    - `specs/machine/graphs/architecture_delta_designed_to_fielded_{date}.json`
    - `specs/machine/graphs/architecture_delta_built_to_fielded_{date}.json`
  - Success criteria:
    - As-fielded graph generated
    - Both delta reports generated
    - Similarity scores calculated
    - Recommendations provided

## Template Design: `architecture_delta_report_template.json`

```json
{
  "delta_metadata": {
    "report_id": "DELTA-{date}-{from_type}-{to_type}",
    "comparison_date": "YYYY-MM-DD",
    "from_architecture": {
      "file_path": "<path>",
      "architecture_type": "as_designed | as_built | as_fielded",
      "generation_date": "YYYY-MM-DD"
    },
    "to_architecture": {
      "file_path": "<path>",
      "architecture_type": "as_designed | as_built | as_fielded",
      "generation_date": "YYYY-MM-DD"
    },
    "comparison_tool": "compare_architectures.py v1.0.0"
  },
  "similarity_score": {
    "overall": 0.85,
    "breakdown": {
      "nodes": 0.90,
      "edges": 0.80,
      "properties": 0.85
    },
    "interpretation": "HIGH (>0.8) | MEDIUM (0.5-0.8) | LOW (<0.5)"
  },
  "node_deltas": {
    "added": [
      {
        "node_id": "new_service",
        "node_type": "service",
        "rationale": "Why was this added?"
      }
    ],
    "removed": [
      {
        "node_id": "removed_service",
        "node_type": "service",
        "rationale": "Why was this removed?"
      }
    ],
    "modified": [
      {
        "node_id": "modified_service",
        "changed_properties": ["port", "dependencies"],
        "from": {...},
        "to": {...}
      }
    ]
  },
  "edge_deltas": {
    "added": [...],
    "removed": [...],
    "modified": [...]
  },
  "change_classification": {
    "breaking_changes": [
      {
        "change_id": "BC-001",
        "type": "removed_interface",
        "description": "REST API /users endpoint removed",
        "impact": "External clients will fail",
        "recommendation": "Restore interface or increment major version"
      }
    ],
    "non_breaking_changes": [
      {
        "change_id": "NBC-001",
        "type": "added_endpoint",
        "description": "Added /users/search endpoint",
        "impact": "Backward compatible addition"
      }
    ]
  },
  "recommendations": [
    "Similarity score is 85% - good alignment between design and implementation",
    "No breaking changes detected - safe to deploy",
    "Consider incorporating new endpoint /users/search into as-designed architecture"
  ],
  "action_items": [
    {
      "action_id": "AI-001",
      "action": "Update as-designed architecture to include /users/search",
      "assignee": "architect",
      "priority": "low"
    }
  ]
}
```

## File Location Strategy

All architecture graphs and delta reports located in:
```
<system_root>/specs/machine/graphs/
├── system_of_systems_graph.json                      # As-designed (from SE-06)
├── system_of_systems_graph_as_built.json             # As-built (from D-06)
├── system_of_systems_graph_as_fielded.json           # As-fielded (from TO-06)
├── architecture_delta_designed_to_built_20251026.json
├── architecture_delta_designed_to_fielded_20251026.json
└── architecture_delta_built_to_fielded_20251026.json
```

## Error Handling

**Tool 1 (generate_as_built_architecture.py)**:
- No services/ directory → ERROR: "No services directory found. Ensure development workflow completed."
- No code in services/ → WARNING: "Services directory empty or contains only scaffolding"
- AST parsing fails → WARNING: "Could not parse {file}, skipping"
- No as-designed graph found → WARNING: "Cannot compare to as-designed (not found), generating as-built only"

**Tool 2 (generate_as_fielded_architecture.py)**:
- No deployment artifacts found → ERROR: "No docker-compose.yml or running containers found"
- Docker not running → ERROR: "Docker daemon not running"
- No health endpoints responding → WARNING: "Service {name} not responding to health checks"
- No as-designed or as-built found → WARNING: "Cannot generate delta reports (base graphs not found)"

**Tool 3 (compare_architectures.py)**:
- Invalid JSON → ERROR: "Cannot parse {file} as JSON"
- Missing required fields → ERROR: "Architecture graph missing required field {field}"
- Empty graphs → ERROR: "Cannot compare empty graphs"

## Success Metrics

- [ ] As-built graph generated for implemented system
- [ ] As-fielded graph generated for deployed system
- [ ] Delta reports show similarity scores > 70% (good alignment)
- [ ] Breaking changes correctly identified
- [ ] Recommendations are actionable
- [ ] Workflow integration seamless
- [ ] User finds feature valuable (addresses GitHub issue #6)

## Next Steps

1. Proceed to FU-04: Implement the three tools
2. Update workflow files
3. Create template
4. Proceed to FU-05: Update documentation
5. Proceed to FU-06: Validate and close GitHub issue #6
