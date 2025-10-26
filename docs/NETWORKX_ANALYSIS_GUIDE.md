# NetworkX Analysis Guide

**Purpose**: Understand which NetworkX analyses are available for each framework and what insights they reveal.

**Critical Insight**: Framework choice determines which analyses you can run. Choose your framework based on which analyses you need.

---

## Analysis Availability Matrix

| Framework | Flow | Cycles | DAG | SCC | Centrality | Community | Edge Weights? |
|-----------|------|--------|-----|-----|------------|-----------|---------------|
| **UAF** | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ No |
| **Decision Flow** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ Probability |
| **Systems Biology** | ⚠️ | ✅ | ⚠️ | ✅ | ✅ | ✅ | ⚠️ Optional |
| **Social Network** | ⚠️ | ✅ | ⚠️ | ✅ | ✅ | ✅ | ⚠️ Optional |
| **Ecological** | ✅ | ✅ | ⚠️ | ✅ | ✅ | ✅ | ✅ Energy flow |
| **CAS** | ⚠️ | ✅ | ⚠️ | ✅ | ✅ | ✅ | ⚠️ Optional |
| **Custom** | ? | ? | ? | ? | ? | ? | ? User-defined |

**Legend**:
- ✅ = Available
- ❌ = Blocked (missing requirements)
- ⚠️ = Available if edge weights added
- ? = Depends on custom framework definition

---

## Analysis Requirements & Insights

### Flow Analysis (`--flow`)

**Requires**: Edge weights (capacity, probability, or flow rate)

**What it reveals**:
- Critical paths (most common routes through system)
- Bottlenecks (where flow gets constrained)
- Maximum throughput capacity
- Load distribution across paths

**Frameworks supporting**:
- ✅ **Decision Flow**: Uses transition probabilities (0.0-1.0)
  - Example: "70% of users skip git automation (critical path)"
- ✅ **Ecological**: Uses energy transfer rates (kcal/m²/year)
  - Example: "Energy bottleneck at decomposer level"
- ⚠️ **UAF**: Not supported (no edge weights in standard UAF)
- ⚠️ **Systems Biology**: If you add reaction rates
- ⚠️ **Social Network**: If you add interaction frequencies

**When to choose framework with flow**:
- Need to find bottlenecks in workflows, pipelines, or processes
- Need to identify most common paths (where users actually go)
- Need to optimize throughput or capacity

---

### Cycle Detection (`--cycles`)

**Requires**: None (all frameworks support)

**What it reveals** (SEMANTIC DIFFERENCES):

**UAF**:
- Cycles = **CIRCULAR DEPENDENCIES** (BAD)
- Example: "Service A depends on B, B depends on A → deadlock"
- Goal: Eliminate all cycles (want DAG)

**Decision Flow**:
- Cycles = **REWORK LOOPS** (EXPECTED)
- Example: "SE-03 validation fails 40% → loop back to SE-02"
- Goal: Understand failure rates, not eliminate

**Systems Biology**:
- Cycles = **FEEDBACK LOOPS** (ESSENTIAL)
- Example: "Gene X inhibits Gene Y which activates Gene X → homeostasis"
- Goal: Identify regulatory circuits

**Ecological**:
- Cycles = **NUTRIENT CYCLES** (EXPECTED)
- Example: "Decomposers return nutrients to producers"
- Goal: Understand energy recycling

**When to use**:
- UAF: Verify no circular service dependencies
- Decision Flow: Find rework/retry patterns
- Biology/Ecological: Identify feedback mechanisms

---

### DAG Analysis (`--dag`)

**Requires**: Acyclic graph (no cycles) OR directed edges

**What it reveals**:
- Topological ordering (valid execution sequence)
- Longest path (critical path for project planning)
- Dependency levels (which nodes can run in parallel)

**Best for**:
- ✅ **UAF**: Service dependency ordering for deployment
- ✅ **Decision Flow**: Workflow step sequencing (if no rework loops)
- ⚠️ **Systems Biology**: If modeling metabolic pathways (often have cycles)
- ⚠️ **Ecological**: If modeling hierarchical food chains (not webs)

**When to use**:
- Need deployment order (which services to start first)
- Need build order (which components to compile first)
- Need task scheduling (PERT/CPM charts)

---

### Strongly Connected Components (SCC) (`--scc`)

**Requires**: Directed graph

**What it reveals**:
- Groups of nodes that are mutually reachable
- Condensation graph (system high-level structure)

**UAF**:
- Large SCCs = **COUPLING PROBLEM**
- Services within SCC must be deployed together
- Goal: Small SCCs (loose coupling)

**Decision Flow**:
- SCCs = **REWORK CLUSTERS**
- Steps that loop back to each other
- Example: SE-02, SE-03, SE-04 form SCC (validation loop)

**Systems Biology**:
- SCCs = **REGULATORY MODULES**
- Genes that mutually regulate each other
- Example: Cell cycle checkpoint proteins

**When to use**: Find tightly coupled groups requiring coordinated changes

---

### Centrality Analysis (`--centrality`)

**Requires**: None (all frameworks support)

**What it reveals**:
- **Degree centrality**: Most connected nodes
- **Betweenness centrality**: Nodes on many paths (bridges)
- **Closeness centrality**: Nodes with shortest paths to all others
- **Eigenvector centrality**: Nodes connected to other important nodes
- **PageRank**: Importance based on incoming connections

**UAF**:
- High centrality = **CRITICAL SERVICES**
- Example: "API gateway has high betweenness → single point of failure"

**Decision Flow**:
- High centrality = **CRITICAL DECISION POINTS**
- Example: "S-04-decision has high betweenness → affects all downstream paths"

**Social Network**:
- High centrality = **INFLUENCERS**
- Example: "Manager has high degree centrality → key communicator"

**When to use**: Identify critical/influential nodes in any system

---

### Community Detection (`--community`)

**Requires**: None (all frameworks support)

**What it reveals**:
- Clusters of densely connected nodes
- Modularity score (how well-defined communities are)
- Community assignments

**UAF**:
- Communities = **SERVICE GROUPS** (bounded contexts in DDD)
- Example: "Auth services form community, separate from data services"

**Decision Flow**:
- Communities = **WORKFLOW PHASES**
- Example: "Setup steps form community, separate from development steps"

**Systems Biology**:
- Communities = **GENE MODULES**
- Example: "Immune response genes cluster together"

**When to use**: Find natural groupings for organization, deployment, or understanding

---

## Decision Guide: Which Analyses Do I Need?

### I need to find bottlenecks in my system
→ **Choose framework with edge weights** (Decision Flow, Ecological)
→ Use `--flow` analysis

### I need to verify no circular dependencies
→ **Use UAF**
→ Use `--cycles` (expect zero) and `--dag` (verify topological order)

### I need to understand feedback loops and regulation
→ **Use Systems Biology or Ecological**
→ Use `--cycles` (cycles are EXPECTED) and `--scc` (find regulatory modules)

### I need to find most important/critical nodes
→ **Any framework**
→ Use `--centrality` (betweenness for bridges, degree for hubs)

### I need to find natural groupings for deployment
→ **UAF or Decision Flow**
→ Use `--community` (service groups) and `--scc` (coupled components)

### I need to understand rework/retry patterns
→ **Decision Flow**
→ Use `--cycles` (rework loops) and `--flow` (failure rates)

---

## Edge Weight Planning

**CRITICAL**: If your chosen framework requires edge weights for flow analysis, you MUST add weights during architecture design (SE-02), not later.

### Edge Weight Semantics by Framework

**Decision Flow**:
- **Field**: `probability` (0.0-1.0)
- **Meaning**: Likelihood of taking this transition
- **Example**: `"probability": 0.7` → 70% of users take this path

**Ecological**:
- **Field**: `energy_transfer_rate` or `biomass_flow`
- **Meaning**: Energy/matter flowing between species
- **Example**: `"energy_transfer_rate": 1200` → 1200 kcal/m²/year

**Systems Biology** (optional):
- **Field**: `reaction_rate` or `binding_affinity`
- **Meaning**: Speed of molecular interaction
- **Example**: `"reaction_rate": 0.05` → k = 0.05 s⁻¹

**Social Network** (optional):
- **Field**: `interaction_frequency` or `relationship_strength`
- **Meaning**: How often/strongly agents interact
- **Example**: `"interaction_frequency": 10` → 10 interactions/week

**UAF** (not supported):
- No standard edge weight field
- Can add `request_rate` or `data_volume` manually if needed
- Will NOT enable flow analysis in standard tools

---

## Common Mistakes

### ❌ Wrong: Choosing UAF then wanting flow analysis
**Problem**: UAF doesn't support edge weights
**Fix**: Choose Decision Flow or add weights to UAF manually (not standard)

### ❌ Wrong: Expecting cycles in UAF systems
**Problem**: Cycles in UAF = circular dependencies (bugs)
**Fix**: Understand cycle semantics vary by framework

### ❌ Wrong: Not adding edge weights when framework requires them
**Problem**: Flow analysis will fail with "No capacity attribute"
**Fix**: Add weights during SE-02 architecture design

### ❌ Wrong: Using DAG analysis on system with expected cycles
**Problem**: DAG analysis requires acyclic graph
**Fix**: Use SCC or cycle detection instead

---

## Quick Reference: Framework → Analyses

**UAF** (Microservices):
```bash
--centrality --dag --scc --community --connectivity
```
Why: Verify no circular deps, find critical services, identify deployment groups

**Decision Flow** (Workflows):
```bash
--flow --cycles --centrality --community --paths
```
Why: Find bottlenecks, rework loops, critical decision points, workflow phases

**Systems Biology** (Gene networks):
```bash
--cycles --centrality --community --scc
```
Why: Feedback loops, hub genes, gene modules, regulatory circuits

**Ecological** (Food webs):
```bash
--flow --centrality --connectivity --community --cycles
```
Why: Energy flow, keystone species, robustness, trophic levels, nutrient cycles

**Social Network** (Organizations):
```bash
--centrality --community --clustering --connectivity
```
Why: Influencers, social groups, cohesion, bridges

---

## See Also

- **Framework Selection**: `CLAUDE.md` section on framework selection
- **Framework Registry**: `definitions/framework_registry.json`
- **Decision Flow Framework**: `docs/DECISION_FLOW_FRAMEWORK.md`
- **System of Systems Graph Tool**: `tools/system_of_systems_graph_v2.py --help`
