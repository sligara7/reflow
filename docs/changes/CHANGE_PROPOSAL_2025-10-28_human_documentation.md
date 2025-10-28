# Change Proposal: Human Documentation & Visualization Enhancements

**Date**: 2025-10-28
**Proposed By**: User Feedback (session_011CUYUVgvLxFJy3Hmzr7BaZ analysis)
**Type**: Feature Enhancement
**Version Impact**: Minor (v3.7.x → v3.8.0)
**Priority**: HIGH

---

## Feature Description

Add comprehensive human documentation workflow with:
1. **PNG/SVG diagram rendering** - Convert Mermaid .mmd to distributable images
2. **Human-readable documentation generation** - Auto-generate markdown "sister documents" for machine specs
3. **Bidirectional translation** - Parse human-edited docs back to machine specs
4. **Component swap workflow** - Enable safe component replacement with validation
5. **Mandatory human documentation** - Remove "conditional" flag from artifacts workflow

---

## Business Justification

### Current Problem

1. **Stakeholders can't review architecture** - .mmd files require Mermaid CLI, .json files are not human-friendly
2. **LLMs skip human documentation** - Marked as "conditional", treated as optional
3. **No human-in-the-loop editing** - Users can't propose changes via readable docs
4. **Component replacement is manual** - No validation when swapping services (e.g., Apache → HAProxy)

### User Pain Points (from session_011CUYUVgvLxFJy3Hmzr7BaZ)

> "Sometimes it seems optional for the agent to perform this step, particularly for the visualization (using mermaid diagrams)."

> "It is much easier to adjust the human readable versions to say 'I need to change this so that it interfaces with service X instead of service Y' for instance."

> "Say a user had originally had an apache proxy service as the entry into the system, but wanted to swap it for haproxy instead."

### Business Value

- **Faster stakeholder review**: PNG/SVG can be embedded in reports, wikis, presentations
- **Easier change proposals**: Edit markdown docs instead of JSON specs
- **Reduced errors**: Component swap validation prevents broken dependencies
- **Architecture evolution tracking**: Version-controlled human + machine docs show system changes over time

---

## Expected Impact

### Affected Workflows

1. **`02-artifacts_visualization.json`** (MODIFIED)
   - Remove `"conditional": true` flag
   - Add AV-02-A05: Mermaid → PNG/SVG rendering
   - Add AV-01-A04: Human documentation generation

2. **NEW: `human_edit_workflow.json`**
   - Parse human-edited markdown
   - Generate updated machine specs
   - Re-run validation (SE-06)
   - Commit if valid, report conflicts if invalid

3. **NEW: `component_swap_workflow.json`**
   - Interface compatibility checking
   - Index.json updating
   - System graph regeneration
   - Compatibility reporting

### Affected Services/Components

None (internal Reflow enhancement, not end-user system changes)

### Affected Tools (NEW)

1. **`generate_human_documentation.py`** (NEW)
   - Input: service_architecture_v*.json
   - Output: service_name.md (structured markdown)

2. **`parse_human_documentation.py`** (NEW)
   - Input: service_name.md (edited by user)
   - Output: Updated service_architecture_v*.json + validation

3. **`component_swap.py`** (NEW)
   - Input: Old component, new component, index.json
   - Output: Updated index, compatibility report

4. **Mermaid CLI Integration** (DEPENDENCY)
   - Install: `npm install -g @mermaid-js/mermaid-cli`
   - Command: `mmdc -i input.mmd -o output.png`

### Affected Templates (NEW)

1. **`service_documentation_template.md`** (NEW)
   - Human-readable service doc structure
   - YAML frontmatter + markdown sections

2. **`component_swap_report_template.md`** (NEW)
   - Compatibility report structure

### Breaking Changes

**NO BREAKING CHANGES** - All enhancements are additive:
- Existing workflows continue to work
- New tools are optional (fallback if not available)
- Human docs generated alongside machine specs (not replacing)

---

## Implementation Plan

### Phase 1: Critical Fixes (1 week)

1. Update `02-artifacts_visualization.json`:
   - Set `"conditional": false`
   - Add AV-02-A05 (PNG/SVG rendering)

2. Document Mermaid CLI setup
3. Update CLAUDE.md with human documentation guidance

### Phase 2: Human Documentation Generator (1 week)

1. Create `generate_human_documentation.py`
2. Create `service_documentation_template.md`
3. Add AV-01-A04 to workflow

### Phase 3: Bidirectional Translation (2 weeks)

1. Create `parse_human_documentation.py`
2. Create `human_edit_workflow.json`
3. Add change detection logic

### Phase 4: Component Swap Tool (1 week)

1. Create `component_swap.py`
2. Create compatibility checking algorithm
3. Create `component_swap_workflow.json`

### Phase 5: Documentation & Testing (1 week)

1. Update all documentation
2. Test on real systems
3. Create examples

**Total Duration**: 6 weeks

---

## Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Mermaid CLI not available | Medium | Medium | Fallback to mermaid.ink web API |
| Human→Machine parse errors | High | Medium | Strict validation, detailed conflict reports, rollback support |
| Component swap breaks system | High | Low | Comprehensive compatibility checking, dry-run mode, rollback |
| Version control complexity | Medium | Low | Clear documentation, automated version handling |

---

## Success Metrics

1. **100% documentation coverage** - All services have human-readable docs
2. **100% visualization rendering** - All .mmd files have .png and .svg renders
3. **95% translation accuracy** - Human edits translate without conflicts
4. **90% component swap success** - Swaps validated as compatible
5. **User preference** - Users prefer editing human docs vs JSON (survey)

---

## Alignment with System Mission

**Reflow Mission**: "Enable LLM agents to design, architect, and develop complex systems across multiple domains with framework-agnostic workflows"

**How This Aligns**:
- ✅ **Human-in-the-loop**: Bidirectional translation enables human collaboration
- ✅ **Framework-agnostic**: Human documentation works for UAF, Biology, Social, etc.
- ✅ **Quality**: Component swap validation prevents broken architectures
- ✅ **Accessibility**: PNG/SVG makes architecture accessible to non-technical stakeholders

**Key User Scenario Supported**: "Architecture Review by Stakeholders"
- Stakeholders need PNG/SVG diagrams (not .mmd files)
- Stakeholders need human-readable docs (not .json files)
- Stakeholders propose changes via markdown edits (not JSON edits)

---

## Appendix: Detailed Analysis

See: `docs/HUMAN_DOCUMENTATION_WORKFLOW_ANALYSIS.md` (41 KB, comprehensive analysis)

**Key Sections**:
- Current State Analysis
- Identified Gaps
- Proposed Enhancements
- Implementation Roadmap (6 weeks, 5 phases)
- Benefits, Risks, Success Metrics

---

**Status**: PENDING FOUNDATIONAL ALIGNMENT VALIDATION
**Next Step**: Run `validate_foundational_alignment.py` (FU-01-A02)
