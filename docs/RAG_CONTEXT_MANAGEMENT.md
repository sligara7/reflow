# RAG-Enhanced Context Management for Reflow

## Overview

The RAG (Retrieval-Augmented Generation) enhanced context management system addresses two critical challenges in reflow workflows:

1. **LLM agents generating unwanted reports** after completing steps
2. **LLM agents forgetting or ignoring decision_flow.json instructions** 

By using vector embeddings and semantic retrieval, the system automatically injects the most relevant context at the right time, making workflow adherence systematic rather than relying on LLM discipline.

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                    RAG Context Management                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Knowledge Bases (Vector Embeddings)                     │
│     ├── decision_flow_kb (CRITICAL_BEHAVIORAL_RULES, etc)   │
│     ├── workflow_steps_kb (Architecture, Dev, Feature)      │
│     ├── tool_reference_kb (Tool documentation)              │
│     ├── architectural_definitions_kb (UAF terms)            │
│     └── system_context_kb (Runtime state)                   │
│                                                              │
│  2. Retrieval Strategies                                    │
│     ├── on_step_start (Load workflow instructions)          │
│     ├── on_degradation_detected (Corrective context)        │
│     ├── on_tool_execution (Tool usage docs)                 │
│     ├── on_user_query (Semantic search)                     │
│     └── periodic_refresh (Context continuity)               │
│                                                              │
│  3. Context Prioritization                                  │
│     ├── CRITICAL (always injected, 2000 tokens)             │
│     ├── HIGH (inject on relevance, 3000 tokens)             │
│     ├── MEDIUM (inject on query, 2000 tokens)               │
│     └── LOW (explicit need only, 1000 tokens)               │
│                                                              │
│  4. Degradation Detection                                   │
│     ├── Report generation attempts                          │
│     ├── Workflow violations                                 │
│     ├── System isolation breaches                           │
│     └── Context confusion signals                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Setup

### 1. Install Dependencies

```bash
pip install sentence-transformers faiss-cpu numpy
```

### 2. Initialize RAG Configuration

```bash
# Copy template to your system
cp templates/rag_context_config_template.json systems/my_system/context/rag_context_config.json

# Edit config and update system_name
nano systems/my_system/context/rag_context_config.json
```

### 3. Generate Embeddings

```bash
# Generate embeddings for all knowledge bases
python3 tools/generate_rag_embeddings.py systems/my_system

# Force rebuild if files changed
python3 tools/generate_rag_embeddings.py systems/my_system --force-rebuild
```

This creates:
- `systems/my_system/context/embeddings/decision_flow_embeddings.pkl`
- `systems/my_system/context/embeddings/workflow_steps_embeddings.pkl`
- `systems/my_system/context/embeddings/tool_reference_embeddings.pkl`
- And metadata files for each

### 4. Enable RAG Mode

Edit `decision_flow.json`:
```json
"rag_enhanced_mode": {
  "enabled": true
}
```

## Usage

### Wrap User Queries

Automatically retrieve and inject relevant context:

```bash
# Basic usage
python3 tools/rag_agent_wrapper.py systems/my_system wrap \
  --query "How do I validate the architecture?" \
  --output prompt.txt

# With explicit strategy
python3 tools/rag_agent_wrapper.py systems/my_system wrap \
  --query "Start the next step" \
  --strategy on_step_start \
  --output prompt.txt
```

**Output Example:**
```
MANDATORY CONTEXT:

**CRITICAL:** CRITICAL_BEHAVIORAL_RULES (similarity: 1.00)
```json
{
  "NEVER_GENERATE_REPORTS": [
    "NEVER generate a report after completing a step or substep",
    ...
  ]
}
```

RELEVANT WORKFLOW:

workflow_instructions for Arch-01-SetupAndContext (similarity: 0.85)
```json
{
  "step_id": "Arch-01",
  "description": "Setup system isolation and load context",
  ...
}
```

---

USER QUERY: How do I validate the architecture?

**REMINDER**: Follow the workflow instructions and behavioral rules specified in the MANDATORY CONTEXT above.
```

### Analyze Agent Responses

Detect degradation and get corrective recommendations:

```bash
python3 tools/rag_agent_wrapper.py systems/my_system analyze \
  --response response.txt \
  --output analysis.json
```

**Output Example:**
```json
{
  "response_valid": false,
  "degradation_signals": ["report_generation_attempt"],
  "timestamp": "2025-10-18T02:30:00Z",
  "recommendation": "INJECT_CORRECTIVE_CONTEXT",
  "severity": "CRITICAL",
  "corrective_context": {
    "always_included": [
      {
        "id": "CRITICAL_BEHAVIORAL_RULES.NEVER_GENERATE_REPORTS",
        "text": "[rules prohibiting report generation]",
        "priority": "CRITICAL"
      }
    ]
  }
}
```

### Pre-Operation Validation

Validate context state before operations:

```bash
python3 tools/rag_agent_wrapper.py systems/my_system validate
```

**Output Example:**
```json
{
  "validation_time": "2025-10-18T02:30:00Z",
  "system_name": "my_system",
  "working_directory": "/path/to/systems/my_system",
  "current_step": "Arch-03",
  "operations_since_refresh": 2,
  "checks_passed": [
    "working_directory_verification",
    "operation_count",
    "context_file_working_memory.json"
  ],
  "checks_failed": [],
  "overall_status": "PASS"
}
```

### Force Context Refresh

Manually trigger a full context refresh:

```bash
python3 tools/rag_agent_wrapper.py systems/my_system refresh \
  --output refresh_summary.json
```

## How It Solves the Problems

### Problem 1: LLM Agents Generating Unwanted Reports

**Before RAG:**
- LLM reads NEVER_GENERATE_REPORTS once at start
- After 4+ operations, context drifts
- LLM forgets the prohibition
- Generates report anyway

**With RAG:**
1. **Degradation Detection**: Pattern matching detects "generating report", "status update", etc.
2. **Automatic Retrieval**: Immediately retrieves `CRITICAL_BEHAVIORAL_RULES.NEVER_GENERATE_REPORTS`
3. **Context Injection**: Injects prohibition directly before LLM response
4. **Severity Assessment**: Flags as CRITICAL, requires correction

**Result:** LLM cannot forget the rule because it's semantically retrieved and injected whenever needed.

### Problem 2: Forgetting decision_flow.json Instructions

**Before RAG:**
- LLM must remember to read decision_flow.json
- No systematic enforcement
- Instructions treated as "optional"
- Context refresh is manual and error-prone

**With RAG:**
1. **Always-Included Context**: `CRITICAL_BEHAVIORAL_RULES` always injected (2000 token budget)
2. **Step-Based Retrieval**: Workflow instructions for current step automatically retrieved
3. **Periodic Refresh**: Auto-triggers after 4 operations or 12 minutes
4. **Validation Checks**: Pre-operation validation ensures alignment with decision_flow

**Result:** decision_flow.json instructions are systematically enforced, not optionally followed.

## Retrieval Strategies

### on_step_start
**Trigger:** Step transitions (user says "next step", "proceed", etc.)  
**Retrieves:**
- Workflow instructions for current step (workflow_steps_kb)
- CRITICAL_BEHAVIORAL_RULES (decision_flow_kb)
- System isolation requirements (decision_flow_kb)

### on_degradation_detected
**Trigger:** Degradation pattern detected in output  
**Retrieves:**
- Targeted sections based on signal type
- Always includes CRITICAL_BEHAVIORAL_RULES
- Forces immediate context refresh

### on_tool_execution
**Trigger:** User requests tool execution  
**Retrieves:**
- Tool usage documentation (tool_reference_kb)
- Validation requirements (decision_flow_kb)
- System isolation checks

### on_user_query
**Trigger:** General user questions  
**Retrieves:**
- Semantic search across all knowledge bases
- Relevance-ranked results (top-5)
- Always includes CRITICAL_BEHAVIORAL_RULES

### periodic_refresh
**Trigger:** Every 4 operations OR 12 minutes  
**Retrieves:**
- Current step requirements
- CRITICAL_BEHAVIORAL_RULES
- Full reload of working_memory.json

## Context Prioritization

### Token Budget Management

Total context budget: **8000 tokens**

| Priority  | Max Tokens | When Injected | Example Sections |
|-----------|------------|---------------|------------------|
| CRITICAL  | 2000       | Always        | CRITICAL_BEHAVIORAL_RULES, system_name, current_step |
| HIGH      | 3000       | On relevance  | validation_before_every_operation, workflow instructions |
| MEDIUM    | 2000       | On query      | tool_reference, quality_gates |
| LOW       | 1000       | Explicit need | process_log history, completed steps |

**Dynamic Allocation:** If CRITICAL only uses 1500 tokens, remaining 500 can be allocated to HIGH priority.

## Degradation Detection Patterns

| Signal | Detection Patterns | Target Sections | Alert Level |
|--------|-------------------|-----------------|-------------|
| report_generation_attempt | `creating.*report`, `generating.*summary`, `status update` | NEVER_GENERATE_REPORTS | CRITICAL |
| workflow_violation | `skipping step`, `proceeding without`, `ignoring workflow` | MANDATORY_WORKFLOW_ADHERENCE | CRITICAL |
| system_isolation_breach | `accessing.*other system`, `wrong system directory` | system_isolation_recovery | CRITICAL |
| context_confusion | `what system am I working on`, `what step are we at` | working_memory.json, step_progress_tracker.json | HIGH |

## Integration with Existing Workflows

### Manual Mode (Current)
```bash
# LLM agent manually reads files
cat systems/my_system/context/working_memory.json
cat systems/my_system/context/current_focus.md
```

### RAG-Enhanced Mode (New)
```bash
# Automatic retrieval and injection
enhanced_prompt=$(python3 tools/rag_agent_wrapper.py systems/my_system wrap \
  --query "$user_query" \
  --format-for-injection)

# Pass to LLM agent
llm_agent "$enhanced_prompt"
```

## Metrics & Monitoring

RAG system tracks:
- `query_latency_ms` - Time to retrieve context
- `retrieval_success_rate` - % of successful retrievals
- `average_relevance_score` - Quality of semantic matches
- `degradation_detection_count` - How often issues caught
- `auto_correction_success_rate` - Effectiveness of corrections
- `token_budget_utilization` - Context efficiency
- `cache_hit_rate` - Performance optimization

View metrics:
```bash
cat systems/my_system/context/rag_metrics.json
```

## Advantages Over Manual Context Management

| Aspect | Manual | RAG-Enhanced |
|--------|--------|--------------|
| **Context Retention** | Relies on LLM memory | Systematic retrieval |
| **Relevance** | Entire files loaded | Semantic top-k matching |
| **Token Efficiency** | 5000-10000 tokens | 2000-8000 tokens (targeted) |
| **Degradation Response** | Manual detection | Automatic detection + correction |
| **Workflow Adherence** | Optional discipline | Systematically enforced |
| **Refresh Triggers** | Manual or fixed | Intelligent (semantic + time) |

## Future Enhancements

1. **Hybrid Search**: Combine semantic search with keyword matching
2. **Contextual Reranking**: Rerank results based on current workflow state
3. **Multi-System RAG**: Share knowledge bases across related systems
4. **Adaptive Chunking**: Dynamic chunk sizes based on content type
5. **Continuous Learning**: Update embeddings based on usage patterns

## Troubleshooting

### Embeddings Out of Date
```bash
# Check generation summary
cat systems/my_system/context/embeddings/generation_summary.json

# Rebuild if source files changed
python3 tools/generate_rag_embeddings.py systems/my_system --force-rebuild
```

### Low Relevance Scores
- Adjust `min_similarity` thresholds in config
- Check if queries match knowledge base content
- Verify embeddings model is appropriate

### High Token Usage
- Reduce `max_token_budget` for lower priorities
- Increase `min_similarity` to filter more results
- Chunk decision_flow.json into smaller sections

### Degradation Not Detected
- Review detection patterns in config
- Add new patterns for specific issues
- Check `monitoring_enabled` is true

## References

- Configuration Template: `templates/rag_context_config_template.json`
- Embedding Tool: `tools/generate_rag_embeddings.py`
- Retrieval Tool: `tools/retrieve_rag_context.py`
- Integration Wrapper: `tools/rag_agent_wrapper.py`
- decision_flow.json: `rag_enhanced_mode` section
