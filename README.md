# Reflow - Systems Engineering Workflow

A comprehensive systems engineering workflow for designing, architecting, and developing complex systems and system-of-systems.

## Quick Start

### 1. Create Your System Folder
Create a new folder anywhere on your system (separate from reflow tooling):
```bash
mkdir ~/projects/my_system
# or anywhere else you prefer: /workspace/my_system, etc.
```

### 2. Describe Your System
Inside your system folder, create a text document describing:
- What system or system-of-systems you want to engineer
- High-level requirements and goals
- Any existing systems that need integration

Example:
```bash
echo "Smart Home Automation System - integrate lighting, security, HVAC, and entertainment systems" > ~/projects/my_system/system_description.txt
```

### 3. Start the Workflow
Tell your LLM agent:
```
Implement workflow in /path/to/reflow/decision_flow.json on system in ~/projects/my_system
```

The workflow will automatically:
- Work with your system at the specified path
- Guide you through systems engineering steps
- Create the proper folder structure
- Generate architecture artifacts
- Optionally proceed to software development

## Key Benefits

### Clean Separation
- **No Repository Conflicts**: Systems are completely separate from reflow tooling
- **Independent Repositories**: Each system can be its own git repository
- **Flexible Locations**: Systems can be anywhere on your filesystem

### System Architecture
- **New Systems**: Complete systems engineering from concept to implementation
- **System-of-Systems**: Integrate multiple existing systems  
- **Feature Updates**: Modify existing architectures safely

### Development Support
- **Multi-language**: Support for Python, Java, TypeScript, Go, Rust, and more
- **Validation**: Automated architecture validation and consistency checking
- **Documentation**: Auto-generated system documentation and interface contracts

## Folder Structure
Each system gets a standardized 4-folder structure:
```
<your_system_path>/
├── context/     # LLM workflow tracking
├── specs/       # Architecture specifications  
├── services/    # Service implementations
└── docs/        # Human documentation
```

## What You Get
- Complete system architecture documentation
- Service specifications with interface definitions
- Development-ready artifacts
- Validation and consistency checking
- Integration planning for complex systems

## Requirements
- Python 3.8+ with dependencies: `networkx`
- LLM agent capable of following structured JSON workflows

---

*Built on UAF 1.2 architecture framework with automated context management*