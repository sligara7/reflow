# Reflow Meta-Analysis Guide (Self-Sharpening Knife)

## Quick Start

**What**: Use Reflow's functional architecture workflows to analyze Reflow itself, then FIX the implementation
**Why**: Detect AND fix context bottlenecks, gaps, and inefficiencies - making Reflow continuously self-improving
**When**: After workflow updates, before major releases, or quarterly health checks
**Key Feature**: META-05B step fixes actual implementation files (workflows, tools, schemas), not just specs

**Two Ways to Run Meta-Analysis**:
1. **Automatic** (Recommended): Use `98-reflow_feature_update.json` when updating Reflow features - meta-analysis runs automatically after implementation
2. **Manual**: Use `99-meta_analysis.json` for comprehensive quarterly health checks or before major releases

## 🚀 Quick Check (5 minutes)

If functional_architecture.json already exists, run quick analysis:

```bash
cd /path/to/reflow
python3 tools/analyze_functional_architecture.py specs/functional/functional_architecture.json
```

**Output**:
- Console summary of context paths, gaps, cycles
- `specs/functional/functional_architecture_analysis.json` with detailed results

**Success Criteria**:
- ✅ No bottleneck paths (all < 160k tokens)
- ✅ No orphaned critical functions
- ✅ Max path < 80% of context window (< 160k tokens)

---

## ⚡ Automatic Meta-Analysis (Recommended for Feature Updates)

**Workflow**: `98-reflow_feature_update.json`
**When**: Adding/updating a specific Reflow feature (workflow, tool, schema, template)
**Time**: 2-8 hours (feature implementation + targeted meta-analysis)
**Advantage**: Automatically runs meta-analysis after feature implementation - no need to remember

**Trigger Command**:
```
"Implement workflow in /path/to/reflow/workflows/98-reflow_feature_update.json on system /path/to/reflow with feature: <description>"
```

**Steps**:
1. RFU-01: Setup Reflow feature update mode
2. RFU-02: Execute standard feature_update workflow (FU-01 through FU-05)
3. **RFU-03: AUTO-TRIGGER meta-analysis** - Run functional architecture analysis
4. **RFU-04: AUTO-TRIGGER refinement** - Fix functional architecture spec if issues found
5. **RFU-05: AUTO-TRIGGER self-sharpening** - Optimize implementation (META-05B)
6. RFU-06: Commit & document (feature + optimizations)

**Key Benefit**: Every Reflow feature update automatically triggers self-sharpening - creates continuous improvement loop without manual intervention.

---

## 📋 Manual Full Meta-Analysis with Self-Sharpening (6-10 hours)

### Trigger Command

```
"Implement workflow in /path/to/reflow/workflows/99-meta_analysis.json on system /path/to/reflow"
```

### Workflow Steps

#### META-01: Setup (5 min)
- Update `context/working_memory.json` for meta-analysis
- Set framework to "functional_flow"
- Create `specs/functional/` directory

#### META-02: Functional Requirements (30-60 min)
- Read foundational docs (SYSTEM_MISSION_STATEMENT.md, USER_SCENARIOS.md)
- Extract functional requirements (FR-001, FR-002, etc.)
- Create `specs/functional/functional_requirements.json`
- **Gate**: All user scenarios covered by requirements

#### META-03: Functional Architecture (2-3 hours)
- Identify major functional flows (Workflow Execution, Context Management, etc.)
- Decompose flows into atomic functions (F-001, F-002, etc.)
- **CRITICAL**: Estimate context consumption for each function
- Define function dependencies with context weights
- Create `specs/functional/functional_architecture.json`
- **Gate**: All functions have context estimates, dependencies complete

#### META-04: Analysis (5-10 min)
- Run: `python3 tools/analyze_functional_architecture.py specs/functional/functional_architecture.json`
- Review console output and `functional_architecture_analysis.json`
- Categorize issues: CRITICAL, WARNING, INFO
- **Gate**: Analysis completed without errors

#### META-05: Refinement (30-60 min per iteration)
- Address CRITICAL issues in functional architecture spec:
  - Context bottlenecks → Break into sessions, lazy load, summarize
  - Orphaned functions → Add connections or remove
  - Unintentional cycles → Redesign flow
- Re-run analysis (META-04)
- Iterate until no CRITICAL issues
- **Gate**: No context bottlenecks, no orphaned critical functions

#### META-05B: Implementation Refinement - "Self-Sharpening Knife" (1-2 hours per iteration)
**CRITICAL**: This step fixes the actual implementation (workflows, tools, schemas), not just the architectural spec.

- **Map issues to implementation files**:
  - Context bottlenecks → Fix `workflows/*.json` (add refresh points), refactor `tools/*.py` (lazy loading)
  - High-context functions → Refactor `tools/*.py` (F-030, F-053, F-070)
  - Missing error handling → Update `workflows/*.json` and `tools/*.py`
  - Orphaned/unreachable functions → Add workflow steps or remove unused code
- **Fix workflows/*.json**: Add context refresh points, split long workflows, add error handlers
- **Fix tools/*.py**: Implement lazy loading, streaming, summarization, error handling
- **Fix schemas/*.json and templates/*.json**: Update schemas to support workflow changes
- **Test implementation**: Dry-run workflows, validate tool outputs, integration tests
- **Update functional_architecture.json**: Sync spec with actual implementation changes
- **Re-run analysis**: `python3 tools/analyze_functional_architecture.py specs/functional/functional_architecture.json`
- **Loop until validated**: If critical issues remain, iterate from issue mapping
- **Gate**: All workflows executable, tools pass syntax check, analysis shows resolved issues

**Key Insight**: Without META-05B, meta-analysis only updates the spec but doesn't fix the root cause in the implementation. This step makes Reflow self-improving.

#### META-06: Visualizations (Optional, 1-2 hours)
- Generate BPMN process flows
- Generate UML data flow diagrams
- Create context consumption heatmap
- Save to `docs/diagrams/functional/`

#### META-07: Documentation (30-45 min)
- Create `docs/reports/META_ANALYSIS_REPORT_{date}.md`
- Update CHANGELOG.md
- Create GitHub issues for optimizations

#### META-08: Operational Tests (Optional, 2-4 hours)
- Map functional requirements to test scenarios
- Create test suite in `tests/operational/`
- Target 80%+ functional coverage

---

## 🔪 The Self-Sharpening Knife Concept

**Problem Without META-05B**:
```
Analysis → Detect Issues → Update functional_architecture.json → Done
                                    ↑
                          Only updates the SPEC, not the IMPLEMENTATION
```

The issues remain in the actual code (workflows/*.json, tools/*.py, schemas/*.json).

**Solution With META-05B (Self-Sharpening)**:
```
Analysis → Detect Issues → Update spec (META-05)
                          → FIX IMPLEMENTATION (META-05B)
                            - Fix workflows/*.json
                            - Refactor tools/*.py
                            - Update schemas/*.json
                          → Test & Validate
                          → Re-analyze
                          → Loop until fixed
```

**Result**: Reflow continuously improves itself with each meta-analysis run.

**Example Self-Sharpening Cycle**:
1. **Analysis detects**: F-030 (Load All Architecture Files) consumes 15k tokens, path at 154k tokens (96% limit)
2. **META-05**: Update functional_architecture.json to note the issue
3. **META-05B (Self-Sharpening)**:
   - Refactor `tools/system_of_systems_graph_v2.py` to lazy-load files on-demand
   - Reduce F-030 context consumption from 15k → 5k tokens
   - Update functional_architecture.json with new estimate
   - Re-run analysis: Path now 144k tokens (90% limit) ✅
4. **Result**: Reflow just fixed itself and reduced context consumption by 10k tokens

---

## 📊 Key Metrics

### Context Consumption
- **Healthy**: All paths < 160k tokens (< 80% of 200k window)
- **Warning**: Paths 140k-160k tokens (70-80%)
- **Critical**: Paths > 160k tokens (> 80%)

### Function Context Estimates
```
Read small config:      1,000-2,000 tokens
Read workflow file:     5,000-15,000 tokens
Read large architecture: 15,000-30,000 tokens
Generate small file:    2,000-5,000 tokens
Generate architecture:  5,000-15,000 tokens
Generate visualization: 10,000-20,000 tokens
Run analysis:           5,000-10,000 tokens
```

### Common Context Bottlenecks
- Loading all architecture files at once (F-030: 15k tokens)
- Generating multiple visualizations (F-053: 12k tokens)
- Complex graph analysis on large systems (F-032: 8k+ tokens)
- Multiple iterative refinement cycles

---

## 🔧 Interpreting Results

### Analysis Output Structure

```json
{
  "context_analysis": {
    "summary": {
      "bottleneck_paths": 0,        // CRITICAL if > 0
      "warning_paths": 2,            // Monitor
      "safe_paths": 10,              // Good
      "max_context_path": 92000,     // Should be < 160000
      "avg_context_path": 38000      // Lower is better
    },
    "critical_functions": [...]      // Top context consumers
  },
  "gap_analysis": {
    "orphaned_functions": [],        // CRITICAL if critical functions orphaned
    "unreachable_functions": [],     // May be OK if separate contexts
    "dead_end_functions": []         // Review each
  },
  "efficiency_analysis": {
    "cycles": [],                    // Check if intentional
    "high_fan_out": [],              // May indicate "god function"
    "high_fan_in": []                // Critical function, test thoroughly
  },
  "recommendations": [...]           // Actionable fixes
}
```

### Understanding Cycles

**Intentional Cycles** (OK):
- `F-053 → F-054 → F-057 → F-053` - Functional architecture refinement loop
- `F-006 → F-007 → F-001 → ... → F-006` - Workflow step iteration

**Problematic Cycles** (Fix):
- Circular function dependencies with no termination condition
- Mutual recursion without base case

### Understanding Unreachable Functions

**OK**: Functions in separate execution contexts
- Example: Workflow execution flow (F-001 through F-007) operates independently

**Problem**: Critical functions that should be reachable but aren't
- Missing dependencies in functional architecture

---

## 🎯 Common Issues & Fixes

### Issue: Context Bottleneck (Path > 160k tokens)

**Causes**:
- Loading too many large files sequentially
- Generating multiple large visualizations
- Deep iteration without context refresh

**Fixes**:
1. **Break into sessions**: Split long workflows with context refresh points
2. **Lazy loading**: Load files only when needed, not all at once
3. **Summarize outputs**: Return summaries instead of full details
4. **Stream large files**: Read in chunks instead of loading entirely

### Issue: Orphaned Functions

**Causes**:
- Incomplete functional architecture
- Functions added but not integrated
- Functions removed from flows but not deleted

**Fixes**:
1. Add dependencies to integrate function into flows
2. Remove if truly unnecessary
3. Document as standalone utility function

### Issue: High Fan-Out (Function calls too many others)

**Causes**:
- "God function" doing too much
- Orchestrator function (may be intentional)

**Fixes**:
1. Decompose into smaller functions
2. If orchestrator, document clearly and ensure necessary

---

## 📈 Tracking Over Time

### First Meta-Analysis
- Establishes baseline
- Documents current state
- Creates initial `functional_architecture.json`

### Subsequent Meta-Analyses
- Compare with previous results:
  - Has max context path increased?
  - New bottlenecks introduced?
  - New unreachable functions?
- Track metrics over time in CHANGELOG.md
- GitHub issues for regressions

### Recommended Comparison Metrics
```markdown
| Version | Max Path (tokens) | Bottlenecks | Avg Path (tokens) | Issues |
|---------|-------------------|-------------|-------------------|--------|
| v2.0.0  | 92,000            | 0           | 38,000            | 0      |
| v2.1.0  | 95,000            | 0           | 40,000            | 0      |
```

---

## 🔗 Related Documents

- **Workflow (Automatic)**: `workflows/98-reflow_feature_update.json` - Feature update with auto meta-analysis
- **Workflow (Manual)**: `workflows/99-meta_analysis.json` - Full comprehensive meta-analysis
- **Functional Architecture Methodology**: `docs/CLAUDE.md` - v2.1.0 methodology
- **Functional Requirements**: `specs/functional/functional_requirements.json`
- **Functional Architecture**: `specs/functional/functional_architecture.json`
- **Analysis Results**: `specs/functional/functional_architecture_analysis.json`
- **Analysis Tool**: `tools/analyze_functional_architecture.py`

---

## ❓ FAQ

**Q: How often should I run meta-analysis?**
A: After any significant workflow update, before major releases, or quarterly as a health check.

**Q: What if I find a context bottleneck?**
A: CRITICAL issue - must fix before proceeding. See "Common Issues & Fixes" section.

**Q: Are all unreachable functions problems?**
A: No - some functions operate in separate contexts (e.g., standalone utilities). Review each case.

**Q: How long does meta-analysis take?**
A: Quick check: 5 min. Full analysis with self-sharpening: 6-10 hours (includes META-05B implementation fixes).

**Q: What's the difference between META-05 and META-05B?**
A: META-05 refines the functional architecture SPEC (functional_architecture.json). META-05B fixes the actual IMPLEMENTATION (workflows/*.json, tools/*.py, schemas/*.json). META-05B is the "self-sharpening" step that makes Reflow continuously improve itself.

**Q: Can I skip META-05B?**
A: You can, but you'll only get analysis without fixes. The issues will remain in your implementation. META-05B is what makes meta-analysis a "self-sharpening knife" instead of just a diagnostic tool.

**Q: Can I skip the visualization step?**
A: Yes, it's optional. But recommended for major changes to communicate architecture to stakeholders.

**Q: What's the difference between functional architecture and system architecture?**
A: Functional architecture = WHAT the system does (functions). System architecture = HOW it's built (services/components).

**Q: Why track context consumption?**
A: AI agents have limited context windows (e.g., 200k tokens). If a workflow path exceeds this, the AI agent fails or needs expensive context refresh.

**Q: How is this different from the SE workflow's fix loop?**
A: Very similar! SE workflow fixes service_architecture.json files. Meta-analysis (META-05B) fixes Reflow's own workflows/*.json and tools/*.py files. Same principle, applied to Reflow itself.

**Q: When should I use 98-reflow_feature_update vs 99-meta_analysis?**
A:
- **98-reflow_feature_update**: When adding/updating a SPECIFIC Reflow feature. Automatically runs targeted meta-analysis on the new feature impact. Faster (2-8 hours).
- **99-meta_analysis**: For COMPREHENSIVE health checks of ALL of Reflow. Manual trigger. Use quarterly, before major releases, or after multiple feature updates. Longer (6-10 hours).

**Q: Does 98-reflow_feature_update replace 99-meta_analysis?**
A: No, they're complementary. Use 98 for every feature update (automatic self-sharpening). Use 99 periodically for comprehensive health checks. Think: 98 = incremental maintenance, 99 = comprehensive inspection.

---

## 🎓 Example Session

```bash
# 1. Quick check existing functional architecture
$ cd /path/to/reflow
$ python3 tools/analyze_functional_architecture.py specs/functional/functional_architecture.json

# Output shows:
# - Max path: 92k tokens ✅ (under 160k limit)
# - Bottlenecks: 0 ✅
# - Unreachable: 7 (reviewed - separate contexts, OK)
# - Cycles: 2 (both intentional refinement loops, OK)

# 2. Review recommendations
$ cat specs/functional/functional_architecture_analysis.json | grep -A 5 "recommendations"

# 3. If issues found, refine functional_architecture.json (META-05)
$ # Edit specs/functional/functional_architecture.json
$ # Re-run analysis
$ python3 tools/analyze_functional_architecture.py specs/functional/functional_architecture.json

# 4. Fix implementation files (META-05B - Self-Sharpening!)
$ # Map issues: F-030 high context (15k tokens) → lazy load implementation
$ # Edit tools/system_of_systems_graph_v2.py to lazy-load architecture files
$ # Edit workflows/01-systems_engineering.json to add context refresh points
$ # Test changes
$ python3 -m py_compile tools/*.py  # Validate syntax
$ # Update functional_architecture.json with new context estimates
$ python3 tools/analyze_functional_architecture.py specs/functional/functional_architecture.json
$ # Verify: max_context_path reduced from 154k → 144k tokens ✅

# 5. Document results
$ # Create docs/reports/META_ANALYSIS_REPORT_2025-11-04.md
```

---

**Version**: 2.0.0 (Self-Sharpening Knife)
**Last Updated**: 2025-11-04
**Maintainer**: Reflow Development Team
**Key Change**: Added META-05B Implementation Refinement step - makes Reflow self-improving by fixing workflows, tools, and schemas based on analysis results
