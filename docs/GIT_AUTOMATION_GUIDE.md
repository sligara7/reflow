# Git Automation Guide for Reflow Workflows

**Version**: 1.0.0
**Date**: 2025-10-24
**Purpose**: Enable automatic git commits at key workflow milestones

---

## Overview

Git automation provides **hands-free version control** during Reflow workflow execution. When enabled, the system automatically creates meaningful commits at logical checkpoints, pushing your architecture and code to a remote repository.

### Benefits

✅ **Automatic backup** - Never lose work, all progress saved to remote
✅ **Version history** - See exactly when each milestone completed
✅ **Collaboration** - Team members track progress in real-time
✅ **Recovery** - Roll back to any workflow stage
✅ **Audit trail** - Complete record of system evolution
✅ **Meaningful commits** - Descriptive messages at logical points

---

## Setup (One-Time Configuration)

### Step 1: Enable During Setup Workflow

When running `00-setup` workflow, you'll be asked:

> **Would you like to enable automatic git commits during workflow execution?**
>
> - Yes - Enable automatic git commits and pushes (recommended)
> - No - I'll manage git manually

Choose **Yes** to enable automation.

### Step 2: Provide Git Configuration

You'll be prompted for:

1. **Git remote URL**:
   - GitHub: `https://github.com/username/repo.git`
   - GitLab: `https://gitlab.com/username/repo.git`
   - SSH: `git@github.com:username/repo.git`

2. **Branch name** (default: `main`):
   - `main` - Standard main branch
   - `develop` - Development branch
   - `architecture` - Architecture-only branch
   - Custom: Any branch name

3. **Commit author** (default: `Claude Code <noreply@anthropic.com>`):
   - Keep default for Claude Code attribution
   - Or use your own: `Your Name <your@email.com>`

### Step 3: Authentication Setup

**For HTTPS:**
```bash
git config --global credential.helper store
# Or
git config --global credential.helper manager
```

**For SSH:**
```bash
# Generate key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Add to agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Add public key to GitHub/GitLab
cat ~/.ssh/id_ed25519.pub
```

---

## Automatic Commit Points

Below are ALL automatic commit points across all workflows, with exact git commands used.

### 00-setup: Initial Setup

**Milestone**: S-03-A06 - After setup complete

**What's committed**:
- Directory structure (`context/`, `specs/`, `docs/`, `services/`)
- Foundational documents (`SYSTEM_MISSION_STATEMENT.md`, `USER_SCENARIOS.md`, `SUCCESS_CRITERIA.md`)
- Workflow tracking (`working_memory.json`, `step_progress_tracker.json`)
- Git configuration (`.gitignore`, `git_config.json`)

**Git commands**:
```bash
cd {system_root}
git add .
git commit -m "$(cat <<'EOF'
Initial setup: Directory structure and foundational documents

- Created directory structure (context/, specs/, docs/, services/)
- Added foundational documents (SYSTEM_MISSION_STATEMENT.md, USER_SCENARIOS.md, SUCCESS_CRITERIA.md)
- Initialized working_memory.json and workflow tracking
- Configured automatic git commits

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
git branch -M {git_branch}
git push -u origin {git_branch}
```

---

### 01-systems-engineering: Architecture Design

**Milestone 1**: SE-02 - After each service architecture completed

**What's committed** (per service):
- `specs/machine/service_arch/{service}/service_architecture_v{version}-{date}.json`
- `specs/machine/service_arch/{service}/service_architecture.json` (symlink)

**Git commands** (example for character_service):
```bash
cd {system_root}
git add specs/machine/service_arch/character_service/
git commit -m "$(cat <<'EOF'
Architecture: Completed character_service service architecture

- Defined character_service architecture (v1.0.0)
- Specified interfaces, data models, and deployment
- Documented dependencies and constraints
- Created versioned architecture file

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
git push origin {git_branch}
```

**Frequency**: Once per service (10 commits for dnd_reflow with 10 services)

---

**Milestone 2**: SE-06 - After system graph generated and validated

**What's committed**:
- `specs/machine/index.json`
- `specs/machine/graphs/system_of_systems_graph.json`
- `specs/machine/architecture_issues.json`

**Git commands**:
```bash
cd {system_root}
git add specs/machine/index.json specs/machine/graphs/ specs/machine/architecture_issues.json
git commit -m "$(cat <<'EOF'
Architecture: System graph and validation complete

- Generated system-of-systems graph (10 services, {N} interfaces)
- Validated architectural consistency (0 critical issues)
- Created service index with versioning
- Documented architectural issues and recommendations

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
git push origin {git_branch}
```

**Frequency**: Once per workflow run

---

### 02-artifacts-visualization: Documentation & Diagrams

**Milestone 1**: AV-03 - After human documentation generated

**What's committed**:
- `specs/human/service_arch/{service}/system_description_v{version}-{date}.md` (all services)
- `specs/human/service_arch/{service}/system_description.md` (symlinks)

**Git commands**:
```bash
cd {system_root}
git add specs/human/service_arch/
git commit -m "$(cat <<'EOF'
Documentation: Human-readable docs for all services

- Generated system descriptions for 10 services
- Documented architecture decisions and rationale
- Created versioned documentation with symlinks
- Included API overview, integration points, and design patterns

Services documented:
- character_service, session_service, campaign_service
- dice_service, condition_service, game_rules_service
- llm_service, cr_service, api_gateway, coordinator

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
git push origin {git_branch}
```

**Frequency**: Once (all services documented together)

---

**Milestone 2**: AV-04 - After visualizations created

**What's committed**:
- `specs/human/visualizations/*.mmd` (Mermaid diagrams)
- `specs/human/visualizations/README.md`

**Git commands**:
```bash
cd {system_root}
git add specs/human/visualizations/
git commit -m "$(cat <<'EOF'
Visualization: Architecture diagrams generated

- Created Mermaid diagrams for all services
- Generated system-of-systems visualization
- Documented interface contracts visually
- Added diagram rendering instructions

Diagrams:
- System overview diagram
- Service dependency graph
- Interface contract diagrams
- Deployment architecture

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
git push origin {git_branch}
```

**Frequency**: Once per workflow run

---

### 03-development: Service Implementation

**Milestone 1**: D-03 - After each service foundation code completed

**What's committed** (per service):
- `services/{service}/src/__init__.py`
- `services/{service}/src/models/`
- `services/{service}/src/api/`
- `services/{service}/pyproject.toml` or `requirements.txt`
- `services/{service}/Dockerfile`
- `services/{service}/README.md`

**Git commands** (example for character_service):
```bash
cd {system_root}
git add services/character_service/
git commit -m "$(cat <<'EOF'
Development: character_service foundation code complete

- Initialized project structure with poetry/hatchling
- Created data models (Character, CharacterVersion, CharacterBranch)
- Set up API endpoint stubs (FastAPI)
- Configured async database (asyncpg)
- Added Dockerfile and docker-compose integration

Ready for: Core implementation and testing

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
git push origin {git_branch}
```

**Frequency**: Once per service (10 commits for dnd_reflow)

---

**Milestone 2**: D-03 - After service implementation and tests pass

**What's committed** (per service):
- `services/{service}/src/` (full implementation)
- `services/{service}/tests/` (all tests)
- `services/{service}/.coverage` report (optional)

**Git commands** (example for character_service):
```bash
cd {system_root}
git add services/character_service/
git commit -m "$(cat <<'EOF'
Development: character_service implementation complete with passing tests

- Implemented all endpoints (15 routes)
- Added business logic (character CRUD, versioning, validation)
- Integrated with game_rules_service, llm_service, cr_service
- Wrote unit tests (85% coverage)
- All tests passing (42 tests, 0 failures)

Test results:
✅ 42 tests passed
✅ 85% code coverage
✅ All quality gates passed

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
git push origin {git_branch}
```

**Frequency**: Once per service after implementation complete

---

### 04-testing-operations: CI/CD & Deployment

**Milestone 1**: TO-02 - After CI/CD pipeline configured

**What's committed**:
- `.github/workflows/ci.yml` (or GitLab CI, etc.)
- `docker-compose.yml`
- `Dockerfile` (updated if needed)
- `.dockerignore`

**Git commands**:
```bash
cd {system_root}
git add .github/workflows/ docker-compose.yml Dockerfile .dockerignore
git commit -m "$(cat <<'EOF'
Operations: CI/CD pipeline configured

- Created GitHub Actions workflow
- Configured automated testing on push
- Set up Docker Compose for local development
- Added multi-stage Dockerfile for production
- Configured linting and security scanning

Pipeline stages:
- Lint (ruff, mypy)
- Test (pytest, 80% coverage requirement)
- Build (Docker image)
- Security scan (safety, bandit)
- Deploy (staging on successful main branch)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
git push origin {git_branch}
```

**Frequency**: Once per workflow run

---

**Milestone 2**: TO-04 - After successful deployment

**What's committed**:
- `deploy/` directory (Kubernetes manifests, Terraform, etc.)
- `deploy/README.md`
- Environment-specific configs

**Git commands**:
```bash
cd {system_root}
git add deploy/
git commit -m "$(cat <<'EOF'
Operations: Deployment configuration complete

- Created Kubernetes manifests for all services
- Configured service discovery and networking
- Set up persistent volumes for databases
- Added environment-specific configurations (dev, staging, prod)
- Documented deployment procedures

Deployment targets:
- Development: docker-compose (local)
- Staging: Kubernetes cluster (staging.example.com)
- Production: Kubernetes cluster (production.example.com)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
git push origin {git_branch}
```

**Frequency**: Once per workflow run

---

## Commit Message Guidelines

All automatic commits follow this structure:

```
{Category}: {Brief one-line description}

{Detailed multi-line description}
- Bullet point 1
- Bullet point 2
- Bullet point 3

{Optional: Metrics, test results, or additional context}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: {author}
```

**Categories**:
- `Architecture` - System design, service architectures, interfaces
- `Documentation` - Human-readable docs, guides, README files
- `Visualization` - Diagrams, charts, visual representations
- `Development` - Code implementation, tests, dependencies
- `Operations` - CI/CD, deployment, infrastructure
- `Testing` - Test suites, quality gates, coverage reports

---

## Checking Git Automation Status

### View Configuration

```bash
# See if enabled
cat context/working_memory.json | grep git_automation_enabled

# View full git config
cat context/git_config.json
```

### View Commit History

```bash
# All automatic commits
git log --grep="🤖 Generated with" --oneline

# Commits by category
git log --grep="Architecture:" --oneline
git log --grep="Development:" --oneline

# Detailed view
git log --graph --oneline --all

# See what changed in last commit
git show HEAD
```

---

## Disabling Git Automation

### Option 1: During Setup
When asked "Would you like to enable automatic git commits?", choose **No**.

### Option 2: After Setup
Edit `context/working_memory.json`:
```json
{
  "git_automation_enabled": false
}
```

### Option 3: Delete Configuration
```bash
rm context/git_config.json
```

---

## Troubleshooting

### Problem: Push Fails with Authentication Error

**Solution**:
```bash
# For HTTPS
git config --global credential.helper store
git push origin main  # Will prompt for credentials once

# For SSH
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

### Problem: Branch is Protected

**Error**: `remote: error: GH006: Protected branch update failed`

**Solution**:
- Option A: Change branch to unprotected branch (edit `git_branch` in git_config.json)
- Option B: Disable branch protection temporarily
- Option C: Use pull request workflow instead (not currently automated)

### Problem: Merge Conflicts

**Error**: `! [rejected] main -> main (non-fast-forward)`

**Solution**:
```bash
# Pull and merge manually
git pull origin main
# Resolve conflicts
git add .
git commit -m "Merge remote changes"
git push origin main
# Next auto-commit will work
```

### Problem: Wrong Files Committed

**Solution**:
Edit `.gitignore` to exclude unwanted patterns, then:
```bash
git rm --cached {unwanted_file}
git commit -m "Remove unwanted file from tracking"
git push origin main
```

---

## Commit Schedule Summary

| Workflow | Step | Commits | Frequency |
|----------|------|---------|-----------|
| 00-setup | S-03-A06 | Initial setup | Once |
| 01-systems-engineering | SE-02 | Service architectures | Per service (10x) |
| 01-systems-engineering | SE-06 | System graph | Once |
| 02-artifacts | AV-03 | Human docs | Once (all services) |
| 02-artifacts | AV-04 | Visualizations | Once |
| 03-development | D-03 | Foundation code | Per service (10x) |
| 03-development | D-03 | Implementation | Per service (10x) |
| 04-testing | TO-02 | CI/CD pipeline | Once |
| 04-testing | TO-04 | Deployment config | Once |

**Total for complete workflow**: ~33 commits for dnd_reflow (10 services)

---

## Best Practices

✅ **Use descriptive branch names**: `architecture`, `develop`, `feature/service-name`
✅ **Set up SSH keys**: Faster and more secure than HTTPS passwords
✅ **Monitor commit history**: `git log --oneline --graph`
✅ **Tag major milestones**: `git tag v1.0.0-architecture`
✅ **Push tags**: `git push --tags`
✅ **Review before merging**: Create PRs for main branch if team workflow

---

## Advanced: Customizing Commit Messages

To customize commit messages, LLM agents can:

1. Check `context/git_config.json` for author preference
2. Include relevant metrics (test coverage, service count, etc.)
3. Add links to relevant documentation
4. Include workflow metadata (step ID, timestamp)

Example enhanced commit:
```
Development: character_service implementation complete

- Implemented 15 REST endpoints (see API docs)
- Added versioning with git-like DAG structure
- Integrated 3 dependent services (game_rules, llm, cr)
- Wrote 42 unit tests + 12 integration tests
- Achieved 85% code coverage (target: 80%)

Test Results:
✅ 54 tests passed (0 failures)
✅ 85.3% code coverage
✅ 0 linting errors (ruff)
✅ Type checking passed (mypy --strict)

Performance:
- Character creation: <500ms
- Validation loop: <3 iterations avg
- Database queries: <100ms p95

Next: Deploy to staging environment

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Workflow: 03-development, Step: D-03
Timestamp: 2025-10-24T15:30:00Z
Co-Authored-By: Claude <noreply@anthropic.com>
```

---

**For more information**:
- See `context/GIT_AUTOMATION_README.md` in your system directory
- Reflow documentation: `/home/ajs7/project/reflow/CLAUDE.md`
- Git documentation: https://git-scm.com/doc

**End of Guide**
