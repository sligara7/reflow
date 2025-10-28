# Human Documentation Workflow - Analysis & Recommendations

**Created**: 2025-10-28
**Issue**: Human documentation/visualization step treated as optional, missing bidirectional workflow
**Impact**: Critical - Users can't easily review/edit architecture, no human→machine translation

## Executive Summary

The current Reflow workflow has **4 critical gaps** preventing effective human-system collaboration:

1. **Visualizations are Mermaid (.mmd) only** - No PNG/SVG rendering for stakeholder review
2. **Human documentation workflow appears optional** - LLMs skip AV-01 through AV-04
3. **No bidirectional translation** - Can't update human docs and propagate to machine specs
4. **No component swap workflow** - Can't easily replace services (e.g., Apache → HAProxy)

**User's Vision**: Human-readable docs as "sister documents" to machine-readable specs, with bidirectional translation and version control enabling architecture evolution tracking.

---

## Current State Analysis

### What Exists

**Workflow**: `02-artifacts_visualization.json` (CONDITIONAL)
- ✅ Step AV-01: Interface Contract Documents (ICDs)
- ✅ Step AV-02: Mermaid Diagrams (.mmd files only)
- ✅ Step AV-03: System README
- ✅ Step AV-04: Architecture handoff documentation
- ❌ **Problem**: Marked `"conditional": true` - LLMs treat as optional

**Machine-Readable Artifacts**:
- ✅ `specs/machine/service_arch/{service}/service_architecture_v*.json`
- ✅ `specs/machine/interface_registry.json`
- ✅ `specs/machine/graphs/system_of_systems_graph.json`
- ✅ Version control via symlinks + version manifest

**Human-Readable Artifacts**:
- ⚠️ `specs/human/documentation/{interface_name}_interface.md` (limited)
- ⚠️ `specs/human/visualizations/*.mmd` (Mermaid source, no renders)
- ❌ **Missing**: Comprehensive human-readable service documentation
- ❌ **Missing**: PNG/SVG diagram renders

**Tools**:
- ✅ `system_of_systems_graph_v2.py` - JSON graph generation
- ✅ `generate_interface_contracts.py` - ICD generation
- ❌ **Missing**: Mermaid→PNG/SVG renderer
- ❌ **Missing**: Machine→Human documentation generator
- ❌ **Missing**: Human→Machine documentation parser
- ❌ **Missing**: Component swap validator

### What's Missing

#### 1. Visual Diagram Rendering (PNG/SVG)

**Current**: Mermaid source files (.mmd) only
```
specs/human/visualizations/
├── system_architecture.mmd          ✅ Exists
├── deployment_architecture.mmd      ✅ Exists
├── {service}_components.mmd         ✅ Exists
└── {scenario}_sequence.mmd          ✅ Exists
```

**Needed**: Rendered images
```
specs/human/visualizations/
├── system_architecture.mmd          ← Source
├── system_architecture.png          ← MISSING
├── system_architecture.svg          ← MISSING
├── deployment_architecture.mmd      ← Source
├── deployment_architecture.png      ← MISSING
└── ...
```

**Why PNG/SVG**:
- Stakeholders can't render .mmd files (need Mermaid CLI or web tool)
- PNG for presentations, reports, wikis
- SVG for scalable, interactive diagrams
- Both formats standard in technical documentation

**Solution**: Add Mermaid CLI rendering step to AV-02

#### 2. Human-Readable Service Documentation

**Current**: Only machine-readable `service_architecture.json`

**Needed**: Human-readable "sister documents"
```
specs/human/documentation/services/
├── apache_proxy_service.md          ← MISSING
│   ├── Overview (purpose, responsibilities)
│   ├── Interfaces (provides/requires in prose)
│   ├── Dependencies (what it needs, why)
│   ├── Deployment (how to run, ports, health checks)
│   ├── Configuration (env vars, config files)
│   └── Version History (changelog)
├── character_service.md             ← MISSING
└── ...
```

**Format Example** (`apache_proxy_service.md`):
```markdown
# Apache Proxy Service

## Overview
Front-end reverse proxy handling all external requests.

## Provides
- **External API** (IFC-PROXY-001): REST/HTTP on port 8000
  - Routes requests to backend services
  - Handles SSL termination
  - Rate limiting: 1000 req/sec

## Requires
- **User Service API** (IFC-USER-001): User authentication
- **Character Service API** (IFC-CHAR-001): Character data

## Deployment
- Container: `apache_proxy:latest`
- Port: 8000 (external), 8443 (SSL)
- Health check: GET /health → 200 OK
- Start command: `docker-compose up -d apache_proxy`

## Configuration
- `BACKEND_USER_SERVICE`: http://user_service:8001
- `BACKEND_CHAR_SERVICE`: http://character_service:8002
- `SSL_CERT_PATH`: /etc/ssl/certs/proxy.crt

## Version History
- v1.0.0 (2025-10-20): Initial architecture
```

**Benefit**: Non-technical stakeholders can review, suggest changes

#### 3. Bidirectional Translation Workflow

**Current**: One-way (Human design → Machine specs via workflow)

**Needed**: Two-way (Human edits → Machine specs → Re-validation)

**Workflow**:
```
┌─────────────────────────────────────────────────────────┐
│ Initial Architecture (SE workflow)                       │
│ ─────────────────────────────────────────────────────── │
│ service_architecture.json ──┐                           │
│                              ├──> generate_human_docs.py │
│ interface_registry.json ────┘         ↓                 │
│                              human_docs/*.md             │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Human Reviews & Edits                                    │
│ ─────────────────────────────────────────────────────── │
│ User edits: apache_proxy_service.md                      │
│   - Changes port 8000 → 8080                            │
│   - Adds new interface to session_service               │
│   - Updates SSL configuration                           │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Back-Translation & Validation                            │
│ ─────────────────────────────────────────────────────── │
│ parse_human_docs.py                                      │
│   ↓                                                      │
│ Updated service_architecture.json (new version)          │
│   ↓                                                      │
│ Re-run SE-06 (system_of_systems_graph_v2.py)            │
│   ↓                                                      │
│ Validate: No circular deps, interfaces match, etc.      │
│   ↓                                                      │
│ Success → Commit new version                            │
│ Failure → Report conflicts to user                      │
└─────────────────────────────────────────────────────────┘
```

**Key Requirements**:
- Parse human docs with structured format (YAML frontmatter + Markdown)
- Detect changes (diff old vs new human docs)
- Generate updated `service_architecture_v*.json`
- Re-run validation (SE-06)
- Commit both human + machine versions

#### 4. Component Swap Workflow

**User's Example**: Replace Apache with HAProxy

**Current Process**: Manual, error-prone
1. Create new `service_architecture_haproxy.json`
2. Update `index.json` to reference haproxy instead of apache
3. Manually verify interfaces match
4. Re-run system_of_systems_graph_v2.py
5. Hope nothing breaks

**Needed Process**: Automated, validated
```bash
# Step 1: User specifies swap
python3 tools/component_swap.py \
  --old apache_proxy_service \
  --new haproxy_service \
  --index specs/machine/index.json

# Tool does:
# 1. Validate: haproxy provides SAME interfaces as apache (or compatible)
# 2. Validate: haproxy has SAME/compatible dependencies
# 3. Update: index.json (haproxy replaces apache)
# 4. Update: interface_registry.json (if needed)
# 5. Generate: New system graph
# 6. Validate: No broken dependencies, interfaces match
# 7. Report: Changes made, compatibility issues (if any)

# Step 2: Review changes
git diff specs/machine/index.json
cat context/component_swap_report.md

# Step 3: Commit if acceptable
git add specs/machine/index.json
git commit -m "feat: Swap Apache for HAProxy"
```

**Tool Requirements**:
- Interface compatibility checking (structural + semantic)
- Dependency validation
- Index.json update with version preservation
- Rollback support (undo swap)
- Component swap report generation

---

## Proposed Enhancements

### Enhancement 1: Make Human Documentation MANDATORY

**Change**: `02-artifacts_visualization.json`

**Before**:
```json
{
  "workflow_metadata": {
    "conditional": true,
    "conditional_description": "User can choose architecture-only or full development"
  }
}
```

**After**:
```json
{
  "workflow_metadata": {
    "conditional": false,
    "note": "Human documentation is ALWAYS generated for architecture review"
  },
  "entry_points": {
    "from_systems_engineering": {
      "first_step": "AV-01",
      "skip_decision_step": true
    }
  }
}
```

**Rationale**: Human documentation is NOT optional - it's essential for:
- Architecture review by non-technical stakeholders
- Change proposals
- Onboarding new team members
- Compliance documentation

### Enhancement 2: Add PNG/SVG Rendering to AV-02

**New Action**: AV-02-A05 (Render Mermaid to PNG/SVG)

**Tool**: Use Mermaid CLI or `mmdc` command

**Implementation**:
```json
{
  "action_id": "AV-02-A05",
  "action_name": "Render Mermaid Diagrams to PNG/SVG",
  "description": "Convert all .mmd files to PNG and SVG for stakeholder distribution",
  "command_pattern": "for f in specs/human/visualizations/*.mmd; do mmdc -i $f -o ${f%.mmd}.png && mmdc -i $f -o ${f%.mmd}.svg; done",
  "requires": ["@mermaid-js/mermaid-cli (npm install -g @mermaid-js/mermaid-cli)"],
  "outputs": [
    "specs/human/visualizations/*.png",
    "specs/human/visualizations/*.svg"
  ],
  "validation": ["PNG files > 0 bytes", "SVG files valid XML"]
}
```

**Fallback** (if mmdc not available):
- Use Mermaid web API: `https://mermaid.ink/img/{base64_encoded_mmd}`
- Use Python library: `mermaid-py` or `cairosvg`
- Generate markdown with embedded Mermaid (rendered by GitHub/GitLab)

### Enhancement 3: Create Human Documentation Generation Tool

**New Tool**: `generate_human_documentation.py`

**Purpose**: Convert machine-readable service architectures to human-readable markdown

**Usage**:
```bash
python3 tools/generate_human_documentation.py \
  --system-root /path/to/system \
  --output-dir specs/human/documentation/services \
  --format markdown

# Generates:
# specs/human/documentation/services/
# ├── apache_proxy_service.md
# ├── character_service.md
# ├── user_service.md
# └── ...
```

**Input**: `service_architecture_v*.json`

**Output**: Structured markdown with:
- YAML frontmatter (service_id, version, last_updated)
- Overview section (description, responsibilities)
- Interfaces section (provides, requires in prose)
- Dependencies section (what, why, criticality)
- Deployment section (container, ports, health checks, commands)
- Configuration section (env vars, config files)
- Version history section (changelog from version_manifest.json)

**Template**: `templates/human_documentation/service_documentation_template.md`

### Enhancement 4: Create Human→Machine Translation Tool

**New Tool**: `parse_human_documentation.py`

**Purpose**: Parse human-edited markdown and generate updated machine-readable specs

**Usage**:
```bash
python3 tools/parse_human_documentation.py \
  --human-docs specs/human/documentation/services/*.md \
  --machine-specs specs/machine/service_arch/ \
  --validate \
  --commit-message "feat: Update architecture per stakeholder review"

# Tool workflow:
# 1. Parse YAML frontmatter + markdown sections
# 2. Detect changes vs current machine specs
# 3. Generate new service_architecture_v*.json files
# 4. Update symlinks
# 5. Re-run system_of_systems_graph_v2.py validation
# 6. Report validation results
# 7. If valid: Commit changes
# 8. If invalid: Report conflicts, prompt for resolution
```

**Change Detection**:
```markdown
# Diff report
specs/human/documentation/services/apache_proxy_service.md

CHANGED: Port 8000 → 8080
  Before: - Port: 8000 (external)
  After:  - Port: 8080 (external)

ADDED: New dependency on session_service
  - **Session Service API** (IFC-SESSION-001): Session management

REMOVED: SSL configuration section
```

**Validation** (re-run SE-06):
- Check for circular dependencies
- Verify interface consistency
- Validate port conflicts
- Check dependency availability

**Output**:
- Updated `service_architecture_v*.json` (new version)
- Updated `version_manifest.json`
- Updated symlinks
- New `system_of_systems_graph.json`
- Change report: `context/human_to_machine_changes_{date}.md`

### Enhancement 5: Create Component Swap Tool

**New Tool**: `component_swap.py`

**Purpose**: Safely swap one component for another (e.g., Apache → HAProxy)

**Usage**:
```bash
python3 tools/component_swap.py \
  --index specs/machine/index.json \
  --remove apache_proxy_service \
  --add haproxy_service \
  --validate \
  --report context/component_swap_report.md

# Tool workflow:
# 1. Load index.json
# 2. Load apache_proxy_service_architecture.json
# 3. Load haproxy_service_architecture.json
# 4. Compare interfaces (structural + semantic)
# 5. Check: Does haproxy provide SAME/compatible interfaces?
# 6. Check: Does haproxy have SAME/compatible dependencies?
# 7. Update: index.json (swap reference)
# 8. Re-run: system_of_systems_graph_v2.py
# 9. Validate: No broken dependencies
# 10. Generate: Swap compatibility report
# 11. If compatible: Success, user can commit
# 12. If incompatible: Report issues, suggest fixes
```

**Interface Compatibility Check**:
```
Comparing: apache_proxy_service vs haproxy_service

PROVIDED INTERFACES:
  ✅ IFC-PROXY-001 (External API):
     - Apache: REST/HTTP, port 8000
     - HAProxy: REST/HTTP, port 8000 (COMPATIBLE)

REQUIRED INTERFACES:
  ✅ IFC-USER-001 (User Service API):
     - Both require same interface (COMPATIBLE)
  ✅ IFC-CHAR-001 (Character Service API):
     - Both require same interface (COMPATIBLE)

DEPLOYMENT:
  ⚠️  Port change: Apache uses 8000, HAProxy uses 8080
      → Recommend: Update port_registry.json

VERDICT: ✅ COMPATIBLE (with minor adjustments)
```

**Report Output** (`context/component_swap_report.md`):
```markdown
# Component Swap Report

**Old**: apache_proxy_service
**New**: haproxy_service
**Date**: 2025-10-28

## Compatibility Summary

✅ Interface compatibility: PASS
✅ Dependency compatibility: PASS
⚠️ Port configuration: WARNING (8000 → 8080)
✅ System graph validation: PASS

## Changes Made

1. Updated `specs/machine/index.json`:
   - Removed: `apache_proxy_service_architecture.json`
   - Added: `haproxy_service_architecture.json`

2. Updated `specs/machine/port_registry.json`:
   - Changed proxy service port: 8000 → 8080

3. Re-generated `system_of_systems_graph.json`:
   - 29 nodes (apache_proxy replaced with haproxy)
   - 0 broken dependencies
   - 0 circular dependencies

## Action Items

- [ ] Update downstream services to use port 8080
- [ ] Update firewall rules (allow 8080)
- [ ] Update load balancer configuration
- [ ] Test health checks on new port

## Rollback Instructions

To revert this swap:
```bash
git revert HEAD
python3 tools/system_of_systems_graph_v2.py specs/machine/index.json --detect-gaps
```
```

---

## Implementation Roadmap

### Phase 1: Critical Fixes (Week 1)

**Goal**: Make human documentation mandatory, add PNG/SVG rendering

1. **Update `02-artifacts_visualization.json`**
   - Change `"conditional": false`
   - Make AV-01 through AV-04 always execute
   - Add AV-02-A05 (PNG/SVG rendering)

2. **Add Mermaid CLI Dependency**
   - Document installation: `npm install -g @mermaid-js/mermaid-cli`
   - Add fallback: Use mermaid.ink web API if CLI unavailable

3. **Update CLAUDE.md**
   - Section: "Human Documentation is Mandatory"
   - Emphasize: Always generate visualizations + human docs

**Deliverables**:
- Updated workflow file
- Mermaid rendering action
- Updated LLM agent guide

### Phase 2: Human Documentation Generator (Week 2)

**Goal**: Auto-generate human-readable docs from machine specs

1. **Create `generate_human_documentation.py`**
   - Input: service_architecture_v*.json
   - Output: service_name.md (structured markdown)
   - Template: service_documentation_template.md

2. **Create Template** (`templates/human_documentation/service_documentation_template.md`)
   - YAML frontmatter for metadata
   - Standard sections (Overview, Interfaces, Dependencies, Deployment, Config, Changelog)

3. **Add to Workflow** (AV-01-A04)
   - Run after ICD generation
   - Output to specs/human/documentation/services/

**Deliverables**:
- Human documentation generator tool
- Markdown template
- Updated AV-01 workflow step

### Phase 3: Bidirectional Translation (Week 3-4)

**Goal**: Parse human docs back to machine specs with validation

1. **Create `parse_human_documentation.py`**
   - Parse YAML frontmatter + markdown sections
   - Detect changes vs current machine specs
   - Generate updated service_architecture_v*.json
   - Re-run SE-06 validation

2. **Create Workflow** (new workflow: `human_edit_workflow.json`)
   - Step 1: Detect modified human docs (git diff)
   - Step 2: Parse and generate machine specs
   - Step 3: Run validation (SE-06)
   - Step 4: Report results (success/conflicts)
   - Step 5: Commit if valid, prompt user if conflicts

3. **Create Change Detection Tool**
   - Compare old vs new human docs (semantic diff)
   - Generate change report
   - Highlight breaking changes

**Deliverables**:
- Human→Machine parser tool
- New workflow for human edits
- Change detection and reporting

### Phase 4: Component Swap Tool (Week 5)

**Goal**: Enable safe component swapping with validation

1. **Create `component_swap.py`**
   - Interface compatibility checker
   - Dependency validator
   - Index.json updater
   - System graph re-generator
   - Compatibility report generator

2. **Interface Compatibility Algorithm**
   - Structural check (fields, types)
   - Semantic check (protocols, data formats)
   - Deployment check (ports, resources)

3. **Create Workflow** (new workflow: `component_swap_workflow.json`)
   - Step 1: Validate old component exists
   - Step 2: Validate new component exists
   - Step 3: Check compatibility
   - Step 4: Update index.json (if compatible)
   - Step 5: Re-run SE-06 validation
   - Step 6: Generate swap report

**Deliverables**:
- Component swap tool
- Compatibility checker algorithm
- Swap workflow
- Documentation in CLAUDE.md

### Phase 5: Version Control & Evolution Tracking (Week 6)

**Goal**: Track architecture evolution over time

1. **Enhance Version Manifest**
   - Add human documentation versions
   - Track human→machine translation history
   - Link human doc versions to machine spec versions

2. **Create Architecture Timeline Tool**
   - Show evolution: v1.0.0 → v1.1.0 → v2.0.0
   - Highlight: What changed in each version
   - Show: Component swaps, interface changes, new services

3. **Create Mixed-Version Validation**
   - Allow: index.json with different service versions
   - Validate: Cross-version interface compatibility
   - Report: Version conflicts

**Deliverables**:
- Enhanced version manifest schema
- Architecture timeline visualization
- Mixed-version validation tool

---

## Benefits

### For Users

1. **Easy Architecture Review**
   - PNG/SVG diagrams for stakeholders
   - Human-readable docs for non-technical reviewers
   - Change proposals via markdown edits

2. **Component Flexibility**
   - Swap components (Apache → HAProxy)
   - Mix component versions
   - Validate compatibility automatically

3. **Architecture Evolution Tracking**
   - See how system changed over time
   - Compare versions
   - Rollback if needed

### For LLM Agents

1. **Clear Workflow**
   - Human documentation is MANDATORY
   - Always generate visualizations
   - Always validate bidirectional translation

2. **Better Validation**
   - Component swap tool prevents broken dependencies
   - Interface compatibility checking prevents runtime errors
   - Version tracking enables rollback

3. **Human-in-the-Loop**
   - User reviews/edits human docs
   - LLM translates back to machine specs
   - Validation catches conflicts

---

## File Structure (After Enhancements)

```
<system_root>/
├── specs/
│   ├── machine/                        # Machine-readable (existing)
│   │   ├── service_arch/
│   │   │   ├── apache_proxy/
│   │   │   │   ├── service_architecture_v1.0.0-20251028.json
│   │   │   │   └── service_architecture.json → v1.0.0-20251028
│   │   │   └── ...
│   │   ├── interface_registry.json
│   │   ├── index.json
│   │   └── graphs/
│   │       └── system_of_systems_graph.json
│   └── human/                          # Human-readable (enhanced)
│       ├── documentation/
│       │   ├── services/               # NEW: Human docs for services
│       │   │   ├── apache_proxy_service_v1.0.0-20251028.md
│       │   │   ├── apache_proxy_service.md → v1.0.0-20251028
│       │   │   ├── character_service.md
│       │   │   └── ...
│       │   └── interfaces/             # Existing
│       │       ├── user_api_interface.md
│       │       └── ...
│       └── visualizations/
│           ├── system_architecture.mmd  # Existing (source)
│           ├── system_architecture.png  # NEW (rendered)
│           ├── system_architecture.svg  # NEW (rendered)
│           └── ...
├── context/
│   ├── working_memory.json
│   ├── human_to_machine_changes_2025-10-28.md  # NEW
│   └── component_swap_report.md                # NEW
└── tools/                               # NEW tools
    ├── generate_human_documentation.py     # NEW
    ├── parse_human_documentation.py        # NEW
    └── component_swap.py                   # NEW
```

---

## Risks & Mitigation

### Risk 1: Mermaid CLI Not Available

**Mitigation**:
- Fallback to mermaid.ink web API
- Provide clear installation instructions
- Allow users to skip rendering (keep .mmd files)

### Risk 2: Human→Machine Translation Errors

**Mitigation**:
- Strict validation after parsing (re-run SE-06)
- Show detailed conflict report to user
- Require user approval before committing
- Enable rollback (git revert)

### Risk 3: Component Swap Breaking Dependencies

**Mitigation**:
- Comprehensive compatibility checking
- Show detailed compatibility report
- Require user review before applying swap
- Automatic rollback on validation failure

### Risk 4: Version Control Complexity

**Mitigation**:
- Maintain symlinks to "current" version
- Version manifest tracks history
- Clear documentation on version strategy
- Tools handle version updates automatically

---

## Success Metrics

1. **Documentation Coverage**
   - Target: 100% of services have human-readable docs
   - Measure: Count services with .md files vs .json files

2. **Visualization Availability**
   - Target: 100% of .mmd files have .png and .svg renders
   - Measure: Count .png/.svg files vs .mmd files

3. **Bidirectional Translation Accuracy**
   - Target: 95% of human edits translate without conflicts
   - Measure: Successful translations / total translations

4. **Component Swap Success Rate**
   - Target: 90% of swaps validated as compatible
   - Measure: Compatible swaps / total swaps attempted

5. **User Satisfaction**
   - Target: Users prefer editing human docs vs JSON
   - Measure: Survey, feedback from users

---

## Conclusion

The current Reflow workflow treats human documentation as optional, when it's actually **critical for architecture review, change proposals, and human-in-the-loop validation**.

**Key Enhancements**:
1. ✅ Make human documentation MANDATORY
2. ✅ Add PNG/SVG rendering for visualizations
3. ✅ Create bidirectional human↔machine translation
4. ✅ Enable component swapping with validation
5. ✅ Track architecture evolution over time

**Implementation**: 6-week roadmap with 5 phases

**Impact**: Enables true human-system collaboration, architecture evolution tracking, and flexible component management.

**Next Steps**:
1. Review and approve this analysis
2. Begin Phase 1 implementation (Week 1)
3. Iterate based on user feedback

---

**Author**: Claude (Analysis based on user feedback)
**Review Status**: PENDING USER APPROVAL
**Priority**: HIGH (Critical workflow gap)
