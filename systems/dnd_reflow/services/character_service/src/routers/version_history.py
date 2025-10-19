from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from ..db import get_db
from ..models.versioning import Character, CharacterVersion, CharacterBranch
from ..security import require_auth

router = APIRouter()


@router.get("/{character_id}/history", summary="Get git-like version history for character")
def get_version_history(character_id: str, db: Session = Depends(get_db), auth=Depends(require_auth)):
    """
    Returns a git-like version tree showing all versions across all branches.
    
    Response format:
    {
      "character": {...},
      "branches": {
        "main": [...versions...],
        "theme/cyberpunk": [...versions...]
      },
      "tree": "text representation",
      "stats": {...}
    }
    """
    # Get character
    char = db.query(Character).filter(Character.id == character_id).first()
    if not char:
        raise HTTPException(status_code=404, detail="character not found")
    
    # Get all versions
    versions = db.query(CharacterVersion).filter(
        CharacterVersion.character_id == character_id
    ).order_by(CharacterVersion.created_at.asc()).all()
    
    if not versions:
        return {
            "character_id": character_id,
            "character": {
                "name": char.name,
                "concept": char.concept,
                "type": char.type
            },
            "branches": {},
            "tree": "No versions found",
            "stats": {
                "total_versions": 0,
                "total_branches": 0
            }
        }
    
    # Organize by branch
    branches: Dict[str, List[Dict[str, Any]]] = {}
    for v in versions:
        branch_name = v.branch_name
        if branch_name not in branches:
            branches[branch_name] = []
        
        version_data = {
            "version_id": str(v.id),
            "version_number": v.version_number,
            "branch_name": v.branch_name,
            "is_head": v.is_head,
            "parent_version_id": str(v.parent_version_id) if v.parent_version_id else None,
            "change_type": v.change_type,
            "change_description": v.change_description,
            "level": v.level,
            "experience_points": v.experience_points,
            "species": v.species,
            "subspecies": v.subspecies,
            "custom_species_traits": v.custom_species_traits,
            "classes": v.classes,
            "ability_scores": v.ability_scores,
            "proficiency_bonus": v.proficiency_bonus,
            "created_at": str(v.created_at)
        }
        branches[branch_name].append(version_data)
    
    # Build text tree
    tree_lines = []
    tree_lines.append("=" * 80)
    tree_lines.append(f"CHARACTER: {char.name}")
    tree_lines.append(f"Concept: {char.concept}")
    tree_lines.append("=" * 80)
    tree_lines.append("")
    tree_lines.append(f"📊 Total Versions: {len(versions)}")
    tree_lines.append(f"🌿 Branches: {', '.join(branches.keys())}")
    tree_lines.append("")
    tree_lines.append("=" * 80)
    tree_lines.append("VERSION TREE")
    tree_lines.append("=" * 80)
    tree_lines.append("")
    
    # Display each branch
    for branch_name, branch_versions in branches.items():
        tree_lines.append(f"🌿 Branch: {branch_name}")
        tree_lines.append("")
        
        for idx, v in enumerate(branch_versions):
            is_last = (idx == len(branch_versions) - 1)
            connector = "└──" if is_last else "├──"
            head_marker = "⭐" if v["is_head"] else "●"
            
            # Format classes
            classes_dict = v.get("classes", {})
            if isinstance(classes_dict, dict):
                classes_str = ", ".join([
                    f"{k} L{c.get('level', '?')}" 
                    for k, c in classes_dict.items()
                ])
            else:
                classes_str = str(classes_dict)
            
            tree_lines.append(f"{connector} {head_marker} v{v['version_number']} [{v['change_type'] or 'unknown'}]")
            tree_lines.append(f"    📅 {v['created_at']}")
            tree_lines.append(f"    👤 Species: {v['species']}")
            tree_lines.append(f"    ⚔️  Classes: {classes_str if classes_str else 'None'}")
            tree_lines.append(f"    📊 Level: {v['level']} | XP: {v['experience_points']}")
            
            if v.get('change_description'):
                tree_lines.append(f"    💬 {v['change_description']}")
            
            # Show custom traits
            custom_traits = v.get('custom_species_traits', {})
            if custom_traits and isinstance(custom_traits, dict):
                traits_str = ", ".join(custom_traits.keys())
                if traits_str:
                    tree_lines.append(f"    ✨ Custom Traits: {traits_str}")
            
            tree_lines.append("")
        
        tree_lines.append("")
    
    # Build progression analysis
    main_versions = branches.get('main', [])
    progression = []
    if len(main_versions) > 1:
        for i in range(len(main_versions)):
            v = main_versions[i]
            changes = []
            
            if i > 0:
                prev = main_versions[i-1]
                level_diff = v['level'] - prev['level']
                if level_diff > 0:
                    changes.append(f"⬆️ Leveled up +{level_diff}")
                
                prev_classes = set(prev.get('classes', {}).keys())
                curr_classes = set(v.get('classes', {}).keys())
                new_classes = curr_classes - prev_classes
                if new_classes:
                    changes.append(f"➕ Added classes: {', '.join(new_classes)}")
            
            progression.append({
                "version_number": v['version_number'],
                "level": v['level'],
                "changes": changes
            })
    
    # Get branch metadata
    branch_metadata = []
    for branch_name in branches.keys():
        if branch_name != 'main':
            branch_versions = branches[branch_name]
            if branch_versions:
                first_v = branch_versions[0]
                parent_id = first_v.get('parent_version_id')
                if parent_id:
                    parent = db.query(CharacterVersion).filter(
                        CharacterVersion.id == parent_id
                    ).first()
                    if parent:
                        branch_metadata.append({
                            "branch_name": branch_name,
                            "branched_from": f"{parent.branch_name} v{parent.version_number}",
                            "version_count": len(branch_versions)
                        })
    
    return {
        "character_id": character_id,
        "character": {
            "name": char.name,
            "concept": char.concept,
            "type": char.type,
            "current_version_id": str(char.current_version_id) if char.current_version_id else None
        },
        "branches": branches,
        "tree": "\n".join(tree_lines),
        "progression": progression,
        "alternate_timelines": branch_metadata,
        "stats": {
            "total_versions": len(versions),
            "total_branches": len(branches),
            "branch_names": list(branches.keys())
        }
    }


@router.get("/{character_id}/versions", summary="List all versions for character")
def list_versions(character_id: str, db: Session = Depends(get_db), auth=Depends(require_auth)):
    """
    Simple list of all versions without tree structure.
    """
    char = db.query(Character).filter(Character.id == character_id).first()
    if not char:
        raise HTTPException(status_code=404, detail="character not found")
    
    versions = db.query(CharacterVersion).filter(
        CharacterVersion.character_id == character_id
    ).order_by(CharacterVersion.created_at.asc()).all()
    
    return {
        "character_id": character_id,
        "versions": [
            {
                "version_id": str(v.id),
                "version_number": v.version_number,
                "branch_name": v.branch_name,
                "is_head": v.is_head,
                "change_type": v.change_type,
                "level": v.level,
                "species": v.species,
                "classes": v.classes,
                "created_at": str(v.created_at)
            }
            for v in versions
        ]
    }


@router.get("/{character_id}/version/{version_id}", summary="Get specific version details")
def get_version(character_id: str, version_id: str, db: Session = Depends(get_db), auth=Depends(require_auth)):
    """
    Get full details of a specific version.
    """
    version = db.query(CharacterVersion).filter(
        CharacterVersion.id == version_id,
        CharacterVersion.character_id == character_id
    ).first()
    
    if not version:
        raise HTTPException(status_code=404, detail="version not found")
    
    return {
        "version_id": str(version.id),
        "character_id": character_id,
        "version_number": version.version_number,
        "branch_name": version.branch_name,
        "is_head": version.is_head,
        "parent_version_id": str(version.parent_version_id) if version.parent_version_id else None,
        "change_type": version.change_type,
        "change_description": version.change_description,
        "level": version.level,
        "experience_points": version.experience_points,
        "species": version.species,
        "subspecies": version.subspecies,
        "custom_species_traits": version.custom_species_traits,
        "classes": version.classes,
        "ability_scores": version.ability_scores,
        "proficiency_bonus": version.proficiency_bonus,
        "sheet_snapshot": version.sheet_snapshot,
        "backstory": version.backstory,
        "personality_traits": version.personality_traits,
        "ideals": version.ideals,
        "bonds": version.bonds,
        "flaws": version.flaws,
        "created_at": str(version.created_at)
    }
