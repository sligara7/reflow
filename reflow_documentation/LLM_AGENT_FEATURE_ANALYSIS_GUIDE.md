# LLM Agent Guide: Feature Analysis Tool

## Overview
The `analyze_features.py` tool parses feature requirement documents to identify system boundaries and responsibilities, enabling structured architecture decomposition from high-level requirements.

## Purpose & Integration

### **Previously: Orphaned Tool**
❌ **No integration**: Listed in documentation but never used in workflow
❌ **Unclear purpose**: Vague "system analysis" description
❌ **No LLM guidance**: No instructions for using output

### **Now: Integrated Requirements Analysis** 
✅ **Entry point integration**: Available as option in new_concept_or_system workflow
✅ **Clear purpose**: Requirements parsing → system identification → architecture input
✅ **LLM workflow**: Structured guidance for using analysis results

## How It Works

### 1. Tool Execution
```bash
python3 ./tools/analyze_features.py <feature_summary_path>
```

**Input**: Markdown file with structured feature sections
**Output**: JSON analysis report + updated working_memory.json

### 2. Expected Input Format
The tool expects a markdown file with numbered sections:

```markdown
# System Feature Summary

### 1. User Authentication & Management
- User registration and login
- Password reset functionality  
- Multi-factor authentication
- Role-based access control

### 2. Content Creation & Publishing
- Article creation and editing
- Media upload and management
- Content scheduling and publishing
- Version control and drafts

### 3. Payment Processing & Billing
- Subscription management
- Payment gateway integration
- Invoice generation
- Billing history and reports
```

### 3. Analysis Output
```json
{
  "timestamp": "2025-10-14T...",
  "feature_summary_path": "/path/to/feature_summary.md",
  "analysis": {
    "required_systems": 3,
    "total_features": 12,
    "systems": [
      {
        "system_id": "user_authentication_management_system",
        "section": "User Authentication & Management",
        "feature_count": 4,
        "features": [
          "User registration and login",
          "Password reset functionality",
          "Multi-factor authentication", 
          "Role-based access control"
        ]
      },
      {
        "system_id": "content_creation_publishing_system",
        "section": "Content Creation & Publishing", 
        "feature_count": 4,
        "features": [
          "Article creation and editing",
          "Media upload and management",
          "Content scheduling and publishing",
          "Version control and drafts"
        ]
      },
      {
        "system_id": "payment_processing_billing_system",
        "section": "Payment Processing & Billing",
        "feature_count": 4,
        "features": [
          "Subscription management",
          "Payment gateway integration", 
          "Invoice generation",
          "Billing history and reports"
        ]
      }
    ]
  },
  "llm_architectural_guidance": {
    "purpose": "Use identified systems as basis for service architecture decomposition",
    "next_steps": [
      "1. Review each identified system and its feature responsibilities",
      "2. Use system_id values as candidate service names in architecture design",
      "3. Map features to service capabilities in service_architecture.json files",
      "4. Ensure complete feature coverage across all identified systems",
      "5. Consider system interactions and interface requirements"
    ],
    "system_design_considerations": [
      "Each system represents a distinct domain boundary with 4 average features",
      "Systems with high feature counts may need further decomposition",
      "Systems with related features should consider shared interfaces",
      "Use feature descriptions to derive service capabilities and interfaces"
    ],
    "working_memory_updated": "required_systems list populated for architecture workflow"
  }
}
```

### 4. Working Memory Update
The tool also updates `working_memory.json`:

```json
{
  "required_systems": [
    {
      "system_id": "user_authentication_management_system",
      "section": "User Authentication & Management",
      "feature_count": 4,
      "status": "identified",
      "created_at": null
    },
    {
      "system_id": "content_creation_publishing_system", 
      "section": "Content Creation & Publishing",
      "feature_count": 4,
      "status": "identified",
      "created_at": null
    },
    {
      "system_id": "payment_processing_billing_system",
      "section": "Payment Processing & Billing", 
      "feature_count": 4,
      "status": "identified",
      "created_at": null
    }
  ]
}
```

## LLM Agent Workflow

### Step 1: Requirements Analysis
```python
# When starting a new system architecture:
1. If feature summary document available, run analyze_features.py first
2. Review analysis output to understand system boundaries
3. Identify which features belong to which systems
4. Use system_id values as starting point for service names
```

### Step 2: System Decomposition Planning
```python
# Use analysis results for architecture design:
1. Each identified system becomes a candidate service or service group
2. Map features to service capabilities in service_architecture.json
3. Consider system interactions - features that cross system boundaries indicate interfaces
4. Plan service responsibilities based on feature groupings
```

### Step 3: Architecture Design Integration
```python
# In architecture phase (Arch-01-SetupAndContext):
1. Load working_memory.json to see required_systems
2. Use system_id values as basis for service naming
3. Ensure all features are covered in service decomposition
4. Design interfaces between systems based on feature interactions
```

## Integration Points

### **Decision Flow Integration**
The tool is now integrated as an **optional first step** in the `new_concept_or_system` entry point:

```json
{
  "options": {
    "with_feature_analysis": {
      "description": "Analyze feature requirements document first to identify system boundaries",
      "requirements_analysis": {
        "tool": "./tools/analyze_features.py",
        "command": "python3 ./tools/analyze_features.py <feature_summary_path>",
        "success_criteria": "Required systems identified and working memory populated"
      },
      "route_to": "architecture/Arch-01-SetupAndContext.json"
    },
    "direct_architecture": {
      "description": "Start architecture design directly without feature analysis"
    }
  }
}
```

### **Architecture Phase Connection**
- **Input to architecture**: Working memory populated with required_systems
- **Used in Arch-01**: System identification and decomposition planning
- **Service naming**: system_id values become candidate service names
- **Feature mapping**: Features mapped to service capabilities

## Benefits for LLM Agents

### ✅ **Structured Requirements Processing**
- Converts unstructured feature descriptions into system boundaries
- Provides clear mapping from features to system responsibilities
- Eliminates guesswork in system decomposition

### ✅ **Consistent System Identification**
- Generates standardized system_id naming (e.g., "user_authentication_management_system")
- Ensures complete feature coverage across identified systems
- Provides feature count metrics for complexity assessment

### ✅ **Architecture Design Foundation**
- Populates working memory with required systems before architecture design
- Gives LLM agents clear starting point for service decomposition
- Ensures feature requirements drive architectural decisions

### ✅ **Quality Assurance**
- Validates that all features are mapped to systems
- Identifies systems with high feature counts that may need decomposition
- Provides traceability from requirements to architecture

## Example LLM Agent Usage

```
Starting new system architecture with feature analysis...

📊 Feature Analysis Results:
- Parsed feature_summary.md with 3 major sections
- Identified 3 required systems with 12 total features
- Updated working_memory.json with system requirements

🏗️ Identified Systems:
1. user_authentication_management_system (4 features)
   - User registration and login
   - Password reset functionality
   - Multi-factor authentication
   - Role-based access control

2. content_creation_publishing_system (4 features)
   - Article creation and editing
   - Media upload and management
   - Content scheduling and publishing
   - Version control and drafts

3. payment_processing_billing_system (4 features)
   - Subscription management
   - Payment gateway integration
   - Invoice generation
   - Billing history and reports

🤖 Next Steps for Architecture Design:
✅ Use system_id values as candidate service names
✅ Map features to service capabilities in service_architecture.json files
✅ Design interfaces between systems where features interact
✅ Ensure complete feature coverage in service decomposition

Proceeding to architecture phase with structured system requirements...
```

## Success Criteria

### ✅ **Complete Requirements Coverage**
- All feature sections parsed and mapped to systems
- Every feature assigned to appropriate system boundary
- No orphaned or unmapped requirements

### ✅ **Architecture Ready**
- Working memory populated with required_systems list
- System boundaries clearly defined with feature responsibilities
- LLM agents have structured input for architecture design

### ✅ **Traceability Maintained**
- Clear mapping from feature summary to system identification
- Feature-to-system relationships preserved for architecture validation
- Requirements traceability through architecture phases

The `analyze_features.py` tool now serves as a crucial **requirements-to-architecture bridge**, transforming unstructured feature descriptions into structured system boundaries that drive architectural design decisions.