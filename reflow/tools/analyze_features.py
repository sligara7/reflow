#!/usr/bin/env python3

import sys
import json
from pathlib import Path
import re
from typing import Dict, List, Set

class FeatureAnalyzer:
    def __init__(self, feature_summary_path: Path):
        self.feature_summary_path = Path(feature_summary_path)
        self.required_systems = {}
        self.system_features = {}

    def parse_feature_summary(self) -> dict:
        """Parse feature summary markdown for system requirements"""
        try:
            with open(self.feature_summary_path) as f:
                content = f.read()

            # Find all major section headers (e.g., "### 1. Character Creation & Management")
            sections = re.findall(r'### \d+\. ([^\n]+)', content)
            
            for section in sections:
                # Extract section content
                section_pattern = f"### \\d+\\. {re.escape(section)}([^#]*)"
                match = re.search(section_pattern, content)
                if not match:
                    continue
                
                section_content = match.group(1)
                
                # Determine required system
                system_id = self._get_system_id(section)
                
                # Extract features
                features = self._extract_features(section_content)
                
                # Store mapping
                if features:
                    self.required_systems[system_id] = {
                        "section": section,
                        "features": features
                    }
                    self.system_features[system_id] = features

        except Exception as e:
            print(f"Error parsing feature summary: {str(e)}")
            return None

        return {
            "required_systems": self.required_systems,
            "system_features": self.system_features
        }

    def _get_system_id(self, section: str) -> str:
        """Convert section title to system ID"""
        # Remove numbers and special characters
        clean = re.sub(r'^\d+\.\s*', '', section)
        # Convert to lowercase and replace spaces/special chars
        system_id = clean.lower().replace(" & ", "_").replace(" ", "_") + "_system"
        return system_id

    def _extract_features(self, content: str) -> List[str]:
        """Extract feature descriptions from section content"""
        features = []
        
        # Look for subsections (####) or bullet points
        subsections = re.findall(r'####\s+([^\n]+)', content)
        bullets = re.findall(r'[-*]\s+([^\n]+)', content)
        
        features.extend(subsections)
        features.extend(bullets)
        
        return features

    def update_working_memory(self, working_memory_path: Path):
        """Update working memory with required systems"""
        try:
            # Load existing working memory
            if working_memory_path.exists():
                with open(working_memory_path) as f:
                    memory = json.load(f)
            else:
                memory = {}

            # Update required systems
            memory["required_systems"] = [
                {
                    "system_id": system_id,
                    "section": data["section"],
                    "feature_count": len(data["features"]),
                    "status": "identified",
                    "created_at": None
                }
                for system_id, data in self.required_systems.items()
            ]

            # Save updated working memory
            with open(working_memory_path, "w") as f:
                json.dump(memory, f, indent=2)

        except Exception as e:
            print(f"Error updating working memory: {str(e)}")

    def generate_report(self) -> dict:
        """Generate analysis report"""
        return {
            "timestamp": "2025-10-05T00:30:00Z",
            "feature_summary_path": str(self.feature_summary_path),
            "analysis": {
                "required_systems": len(self.required_systems),
                "total_features": sum(len(features) for features in self.system_features.values()),
                "systems": [
                    {
                        "system_id": system_id,
                        "section": data["section"],
                        "feature_count": len(data["features"])
                    }
                    for system_id, data in self.required_systems.items()
                ]
            }
        }

def main():
    if len(sys.argv) != 2:
        print("Usage: analyze_features.py <feature_summary_path>")
        sys.exit(1)

    feature_summary_path = Path(sys.argv[1])
    if not feature_summary_path.exists():
        print(f"Error: Feature summary {feature_summary_path} does not exist")
        sys.exit(1)

    analyzer = FeatureAnalyzer(feature_summary_path)
    
    # Parse features
    analysis = analyzer.parse_feature_summary()
    if not analysis:
        print("Error analyzing feature summary")
        sys.exit(1)

    # Update working memory
    working_memory_path = feature_summary_path.parent / "working_memory.json"
    analyzer.update_working_memory(working_memory_path)

    # Generate and print report
    report = analyzer.generate_report()
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()