# Separate Repositories: Reflow and Systems

## Overview

**RECOMMENDED APPROACH**: Keep reflow and systems as **completely separate repositories** in different filesystem locations. This ensures:
- **Reflow repository**: Workflow tooling (tools, templates, workflows) - one location
- **System repositories**: Individual system deliverables (specs, services, docs) - separate locations

## Why Separate Locations?

### Problems with Nested Repositories
- **Nested .git directories cause conflicts** (git within git)
- Accidental commits of system files to reflow repo
- Confusion about which repo you're working in (`git remote -v` shows wrong origin)
- Complex `.gitignore` rules and submodule management
- Files from one repo appearing in another

### Benefits of Complete Separation
- ✅ **No nested repository conflicts whatsoever**
- ✅ Clean separation between tooling and deliverables
- ✅ Each system has independent version control
- ✅ Systems can be stored anywhere on filesystem
- ✅ Zero risk of accidental file mixing
- ✅ Supports independent CI/CD per system
- ✅ Simple, straightforward git workflow for each repo

## Repository Structure

### Option A: Completely Separate (RECOMMENDED)

```
/home/user/dev/
├── reflow/                      # Reflow tooling repository
│   ├── .git/
│   ├── tools/
│   ├── templates/
│   ├── decision_flow.json
│   └── systems/                 # Empty (or for reference only)
│       └── .gitkeep
│
/home/user/projects/
├── dnd_reflow/                  # System repository (separate location)
│   ├── .git/
│   ├── specs/
│   ├── services/
│   └── docs/
│
├── another_system/              # Another system (separate location)
│   ├── .git/
│   ├── specs/
│   └── services/
```

### Option B: Colocated but Ignored

```
/home/user/dev/reflow/           # Reflow repository
├── .git/                        # Reflow repo
├── .gitignore                   # Contains: systems/*
├── tools/
├── templates/
└── systems/
    ├── dnd_reflow/              # Separate repo (ignored by reflow)
    │   ├── .git/                # Its own repo
    │   ├── specs/
    │   └── services/
    └── another_system/          # Another separate repo (ignored)
        ├── .git/
        └── specs/
```

**Note**: Option A is strongly recommended to avoid any possibility of confusion.

## Setup: Creating a New System

### 1. Create System in Separate Location

```bash
# Create system directory (anywhere you want)
mkdir -p ~/projects/my_system
cd ~/projects/my_system

# Initialize system structure
mkdir -p context specs/{machine/{service_arch,interfaces},human} services docs

# Create initial documents
echo "# My System Mission" > docs/SYSTEM_MISSION_STATEMENT.md

# Initialize as git repository
git init

# Create system-specific .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
.venv/
venv/
.env

# Editor
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
EOF

git add .
git commit -m "Initial system setup"

# Create GitHub repo and push
git remote add origin https://github.com/user/my_system.git
git branch -M main
git push -u origin main
```

### 2. Link System as Submodule in Reflow

```bash
cd /path/to/reflow

# Remove system from direct tracking (if it was tracked)
git rm -r --cached systems/<system_name> 2>/dev/null || true
git commit -m "Remove <system_name> from direct tracking" 2>/dev/null || true

# Remove local directory
rm -rf systems/<system_name>

# Add as submodule
git submodule add https://github.com/user/<system_name>.git systems/<system_name>

# Commit submodule configuration
git add .gitmodules systems/<system_name>
git commit -m "Add <system_name> as Git submodule"
git push
```

### 3. Verify Submodule Setup

```bash
# Check .gitmodules file
cat .gitmodules

# Should show:
# [submodule "systems/<system_name>"]
#     path = systems/<system_name>
#     url = https://github.com/user/<system_name>.git

# Verify submodule status
git submodule status

# Check that systems/<system_name>/.git is a FILE (not directory)
ls -la systems/<system_name>/.git
```

## Working with Submodules

### Work on Reflow Tooling

```bash
cd /path/to/reflow

# Make changes to tools, templates, workflows
vim tools/some_tool.py

# Commit to reflow repo
git add .
git commit -m "Update reflow tooling"
git push
```

### Work on a System

```bash
cd /path/to/reflow/systems/<system_name>

# You're now in the system's repository
# Make changes to specs, services, docs
vim services/api/main.py

# Commit to system repo
git add .
git commit -m "Update system implementation"
git push origin main

# Update parent repo to track new submodule commit
cd ../..  # Back to reflow root
git add systems/<system_name>
git commit -m "Update <system_name> submodule reference"
git push
```

### Clone Reflow with Submodules

```bash
# Clone reflow repository
git clone https://github.com/user/reflow.git
cd reflow

# Initialize and fetch submodules
git submodule init
git submodule update

# Or clone with submodules in one command
git clone --recurse-submodules https://github.com/user/reflow.git
```

### Update Submodules

```bash
cd /path/to/reflow

# Update specific submodule
git submodule update --remote systems/<system_name>

# Update all submodules
git submodule update --remote --merge

# Commit the updated references
git add systems/
git commit -m "Update submodule references"
git push
```

## Convert Existing System to Submodule

If a system was incorrectly tracked directly in the reflow repo:

```bash
# 1. Ensure system is already exported to its own GitHub repo
#    (follow "Export System to Separate Repository" steps above if needed)

# 2. In reflow repo, remove from tracking
cd /path/to/reflow
git rm -r --cached systems/<system_name>
git commit -m "Remove <system_name> - converting to submodule"
git push

# 3. Remove local copy
rm -rf systems/<system_name>

# 4. Add as submodule
git submodule add https://github.com/user/<system_name>.git systems/<system_name>
git add .gitmodules systems/<system_name>
git commit -m "Add <system_name> as submodule"
git push
```

## Troubleshooting

### Detached HEAD in Submodule

Submodules checkout specific commits (detached HEAD state). To work on the latest:

```bash
cd systems/<system_name>
git checkout main
git pull origin main
```

### Submodule Shows Uncommitted Changes

The parent repo tracks a specific commit. After committing in the submodule:

```bash
cd /path/to/reflow
git add systems/<system_name>
git commit -m "Update <system_name> submodule reference"
git push
```

### Accidentally Committed System Files to Reflow

```bash
# Remove from tracking
git rm -r --cached systems/<system_name>
git commit -m "Remove system files"
git push

# Convert to submodule (see above)
```

### `.gitignore` Still Ignoring Systems

The reflow `.gitignore` should NOT contain `systems/*`. It should look like:

```gitignore
# Systems are managed as Git submodules
# Each system in systems/ is its own repository

# Bytecode / cache
__pycache__/
*.py[cod]
...
```

## Best Practices

1. **Never mix reflow and system files**: Each has its own repository
2. **System .gitignore**: Create system-specific ignores, don't copy reflow's
3. **Commit submodule references**: After updating a submodule, commit the reference in the parent repo
4. **Use branches in submodules**: Check out appropriate branches, not detached HEAD
5. **Document exports**: Log system exports in `context/process_log.md`

## References

- Git Submodules Documentation: https://git-scm.com/book/en/v2/Git-Tools-Submodules
- decision_flow.json: `entry_points.github_system_export.repository_structure`
