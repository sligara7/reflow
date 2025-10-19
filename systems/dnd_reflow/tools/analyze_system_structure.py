#!/usr/bin/env python3
"""
Tool for analyzing the internal structure of a system to identify integration points.

This tool examines a system's codebase to understand its components, interfaces,
and potential integration points for system-of-systems scenarios.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

def analyze_repository_structure(repo_path: str) -> Dict[str, Any]:
    """
    Analyze a repository's structure to identify potential services and components.
    
    Args:
        repo_path: Path to the repository to analyze
        
    Returns:
        Dictionary containing structural analysis results
    """
    if not os.path.exists(repo_path):
        return {"error": f"Repository path {repo_path} does not exist"}
    
    structure = {
        "repository_path": repo_path,
        "identified_services": [],
        "potential_interfaces": [],
        "technology_stack": [],
        "architectural_patterns": []
    }
    
    # Basic directory structure analysis
    for root, dirs, files in os.walk(repo_path):
        # Skip hidden directories and common build/cache directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'target', 'build']]
        
        rel_path = os.path.relpath(root, repo_path)
        
        # Identify potential services based on directory structure
        if any(indicator in rel_path.lower() for indicator in ['service', 'api', 'server', 'app']):
            structure["identified_services"].append({
                "name": os.path.basename(root),
                "path": rel_path,
                "type": "potential_service"
            })
        
        # Identify technology stack
        for file in files:
            if file == "package.json":
                structure["technology_stack"].append("Node.js")
            elif file == "requirements.txt" or file == "pyproject.toml":
                structure["technology_stack"].append("Python")
            elif file == "pom.xml" or file == "build.gradle":
                structure["technology_stack"].append("Java")
            elif file == "Cargo.toml":
                structure["technology_stack"].append("Rust")
            elif file == "go.mod":
                structure["technology_stack"].append("Go")
            elif file.endswith(".dockerfile") or file == "Dockerfile":
                structure["architectural_patterns"].append("Containerized")
    
    # Remove duplicates
    structure["technology_stack"] = list(set(structure["technology_stack"]))
    structure["architectural_patterns"] = list(set(structure["architectural_patterns"]))
    
    return structure

def analyze_interfaces_from_code(repo_path: str) -> List[Dict[str, Any]]:
    """
    Analyze code files to identify potential interfaces (REST endpoints, etc.)
    
    Args:
        repo_path: Path to the repository to analyze
        
    Returns:
        List of identified interfaces
    """
    interfaces = []
    
    # This is a simplified analysis - would be expanded based on specific needs
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'target', 'build']]
        
        for file in files:
            if file.endswith(('.py', '.js', '.ts', '.java', '.go', '.rs')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                        # Look for common API patterns
                        if any(pattern in content for pattern in ['@app.route', '@RequestMapping', 'app.get', 'app.post']):
                            interfaces.append({
                                "file": os.path.relpath(file_path, repo_path),
                                "type": "http_endpoint",
                                "confidence": "medium"
                            })
                except Exception as e:
                    # Skip files that can't be read
                    continue
    
    return interfaces

def main():
    parser = argparse.ArgumentParser(description="Analyze system structure for integration planning")
    parser.add_argument("system_path", help="Path to the system repository or directory")
    parser.add_argument("--output", "-o", help="Output file for analysis results (JSON format)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.system_path):
        print(f"Error: System path {args.system_path} does not exist", file=sys.stderr)
        sys.exit(1)
    
    print(f"Analyzing system structure: {args.system_path}")
    
    # Perform analysis
    structure_analysis = analyze_repository_structure(args.system_path)
    interface_analysis = analyze_interfaces_from_code(args.system_path)
    
    # Combine results
    results = {
        "system_path": args.system_path,
        "analysis_timestamp": "2024-10-16",  # Would use actual timestamp
        "structure": structure_analysis,
        "interfaces": interface_analysis,
        "recommendations": {
            "integration_strategy": "manual_review_required",
            "next_steps": [
                "Review identified services for accuracy",
                "Validate detected interfaces",
                "Map interfaces to business capabilities",
                "Define integration requirements"
            ]
        }
    }
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Analysis results written to: {args.output}")
    else:
        print(json.dumps(results, indent=2))
    
    if args.verbose:
        print(f"\nSummary:")
        print(f"- Identified {len(structure_analysis.get('identified_services', []))} potential services")
        print(f"- Found {len(interface_analysis)} potential interfaces")
        print(f"- Detected technologies: {', '.join(structure_analysis.get('technology_stack', []))}")

if __name__ == "__main__":
    main()