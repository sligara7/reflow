#!/usr/bin/env python3
"""Analyze source code abstraction level to determine translation strategy.

This tool analyzes a codebase and determines its abstraction level on a 1-4 scale:
- Level 1: Machine Code (binary, CPU-specific)
- Level 2: Assembly (mnemonics, hardware-aware, registers, flags)
- Level 3: Middle-level (C/C++ with memory addresses, pointers, bit manipulation)
- Level 4: High-level (Python, Java, C# - abstracts hardware entirely)

The abstraction GAP between source and target determines translation strategy:
- Gap = 0: LITERAL translation (syntax changes only)
- Gap = 1: DIRECT translation (idiom mapping)
- Gap >= 2: SEMANTIC translation (translate behavior, not implementation)

Usage:
    python3 analyze_abstraction_level.py <codebase_path> [--output <output.json>] [--target <language>]

Example:
    python3 analyze_abstraction_level.py ./legacy_source --target python --output abstraction_analysis.json
"""

import argparse
import json
import os
import re
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional


# Language to abstraction level mapping
LANGUAGE_LEVELS = {
    # Level 1 - Machine Code
    "binary": 1,
    "hex": 1,

    # Level 2 - Assembly
    "asm": 2,
    "assembly": 2,
    "s": 2,  # .s files
    "nasm": 2,
    "masm": 2,
    "6502": 2,
    "x86": 2,
    "arm": 2,

    # Level 3 - Middle-level
    "c": 3,
    "cpp": 3,
    "c++": 3,
    "h": 3,
    "hpp": 3,
    "objective-c": 3,
    "objc": 3,
    "d": 3,

    # Level 4 - High-level
    "python": 4,
    "py": 4,
    "java": 4,
    "kotlin": 4,
    "scala": 4,
    "csharp": 4,
    "cs": 4,
    "javascript": 4,
    "js": 4,
    "typescript": 4,
    "ts": 4,
    "ruby": 4,
    "rb": 4,
    "go": 4,
    "rust": 4,  # Rust is high-level despite low-level capabilities
    "swift": 4,
    "php": 4,
    "perl": 4,
    "lua": 4,
    "r": 4,
    "julia": 4,
    "haskell": 4,
    "hs": 4,
    "elixir": 4,
    "erlang": 4,
    "clojure": 4,
    "f#": 4,
    "fsharp": 4,
    "fortran": 3,  # Fortran is middle-level (close to hardware)
    "f90": 3,
    "f95": 3,
    "cobol": 3,  # COBOL is middle-level
    "cob": 3,
}


# Patterns that indicate lower abstraction levels
LOW_LEVEL_INDICATORS = {
    # Assembly-like patterns (Level 2)
    "registers": [
        r'\b(eax|ebx|ecx|edx|esi|edi|esp|ebp)\b',  # x86 registers
        r'\b(rax|rbx|rcx|rdx|rsi|rdi|rsp|rbp|r[89]|r1[0-5])\b',  # x86-64
        r'\b[aA]\s*=\s*[MmWw]\(',  # 6502-style M() or W() memory access
        r'\bJSR\s*\(',  # Jump to subroutine
        r'\bgoto\s+\w+\s*;',  # goto statements
    ],
    "flags": [
        r'\bif\s*\(\s*[zcnv]\s*\)',  # CPU flags (z=zero, c=carry, n=negative, v=overflow)
        r'\bif\s*\(\s*![zcnv]\s*\)',
        r'\b(carry|zero|negative|overflow)\s*flag',
    ],
    "memory_direct": [
        r'\bM\s*\(\s*0x[0-9a-fA-F]+\s*\)',  # Direct memory access M(0x1234)
        r'\bwriteData\s*\(\s*0x',  # Hardware register writes
        r'\breadData\s*\(\s*0x',
    ],

    # Middle-level patterns (Level 3)
    "pointers": [
        r'\*\s*\(',  # Pointer dereference
        r'\&\s*\w+',  # Address-of operator
        r'\w+\s*\*\s*\w+',  # Pointer declaration
        r'->',  # Pointer member access
        r'malloc\s*\(',
        r'free\s*\(',
        r'sizeof\s*\(',
    ],
    "bit_manipulation": [
        r'\b\w+\s*&\s*0x[0-9a-fA-F]+',  # Bit masking
        r'\b\w+\s*\|\s*0x[0-9a-fA-F]+',  # Bit setting
        r'\b\w+\s*\^\s*0x[0-9a-fA-F]+',  # Bit XOR
        r'<<\s*\d+',  # Left shift
        r'>>\s*\d+',  # Right shift
        r'BOOST_BINARY\s*\(',  # Binary literals
    ],
    "memory_layout": [
        r'#define\s+\w+\s+0x[0-9a-fA-F]+',  # Memory address constants
        r'\[\s*\d+\s*\]',  # Array with numeric index
        r'struct\s+\w+\s*\{',  # Struct definitions
        r'union\s+\w+\s*\{',  # Union definitions
    ],
}

# Patterns that indicate higher abstraction levels
HIGH_LEVEL_INDICATORS = {
    "classes": [
        r'\bclass\s+\w+',
        r'\binterface\s+\w+',
        r'\bprotocol\s+\w+',
        r'@dataclass',
        r'@interface',
    ],
    "modern_types": [
        r'\bOptional\[',
        r'\bList\[',
        r'\bDict\[',
        r'\bSet\[',
        r'\bTuple\[',
        r'\benum\s+\w+',
        r'\bEnum\)',
    ],
    "abstractions": [
        r'\bdef\s+\w+\s*\(',  # Python functions
        r'\basync\s+def',
        r'\bawait\s+',
        r'\blambda\s+',
        r'\bfor\s+\w+\s+in\s+',  # For-in loops
        r'\bwith\s+\w+',  # Context managers
    ],
    "frameworks": [
        r'\bimport\s+pygame',
        r'\bimport\s+numpy',
        r'\bimport\s+pandas',
        r'\bfrom\s+fastapi',
        r'\bfrom\s+django',
        r'\bfrom\s+flask',
    ],
}


@dataclass
class AbstractionAnalysis:
    """Result of abstraction level analysis."""
    source_language: str
    detected_level: int
    level_name: str
    target_language: Optional[str]
    target_level: Optional[int]
    abstraction_gap: Optional[int]
    recommended_strategy: str
    indicators: dict
    file_count: int
    total_lines: int
    confidence: float
    warnings: list
    recommendations: list


def detect_file_language(filepath: Path) -> Optional[str]:
    """Detect language from file extension."""
    ext = filepath.suffix.lower().lstrip('.')
    if ext in LANGUAGE_LEVELS:
        return ext

    # Special cases
    if ext in ('h', 'hpp', 'hxx'):
        return 'cpp'
    if ext == 'cc':
        return 'cpp'

    return None


def count_pattern_matches(content: str, patterns: list[str]) -> int:
    """Count how many times patterns match in content."""
    count = 0
    for pattern in patterns:
        count += len(re.findall(pattern, content, re.IGNORECASE))
    return count


def analyze_file_content(content: str) -> dict:
    """Analyze file content for abstraction level indicators."""
    indicators = {
        "low_level": {},
        "high_level": {},
    }

    # Check low-level indicators
    for category, patterns in LOW_LEVEL_INDICATORS.items():
        count = count_pattern_matches(content, patterns)
        if count > 0:
            indicators["low_level"][category] = count

    # Check high-level indicators
    for category, patterns in HIGH_LEVEL_INDICATORS.items():
        count = count_pattern_matches(content, patterns)
        if count > 0:
            indicators["high_level"][category] = count

    return indicators


def calculate_abstraction_level(indicators: dict, base_level: int) -> tuple[int, float]:
    """Calculate abstraction level based on indicators.

    Returns (level, confidence).
    """
    low_level_score = sum(indicators.get("low_level", {}).values())
    high_level_score = sum(indicators.get("high_level", {}).values())

    # Strong assembly indicators drop to level 2
    assembly_indicators = (
        indicators.get("low_level", {}).get("registers", 0) +
        indicators.get("low_level", {}).get("flags", 0) +
        indicators.get("low_level", {}).get("memory_direct", 0)
    )

    # Adjust level based on indicators
    adjusted_level = base_level

    if assembly_indicators > 50:
        # Heavy assembly-like code
        adjusted_level = min(adjusted_level, 2)
    elif assembly_indicators > 10:
        # Some assembly patterns
        adjusted_level = min(adjusted_level, 3)

    # High-level indicators can raise the level
    if high_level_score > low_level_score * 2 and base_level >= 3:
        adjusted_level = max(adjusted_level, 4)

    # Calculate confidence
    total_indicators = low_level_score + high_level_score
    if total_indicators == 0:
        confidence = 0.5  # No strong signals
    else:
        # Higher confidence when indicators clearly point one direction
        ratio = abs(low_level_score - high_level_score) / total_indicators
        confidence = 0.5 + (ratio * 0.5)

    return adjusted_level, confidence


def get_level_name(level: int) -> str:
    """Get human-readable name for abstraction level."""
    names = {
        1: "Machine Code",
        2: "Assembly",
        3: "Middle-level (C/C++)",
        4: "High-level",
    }
    return names.get(level, "Unknown")


def get_strategy_recommendation(gap: int) -> str:
    """Get translation strategy based on abstraction gap."""
    if gap == 0:
        return "LITERAL"
    elif gap == 1:
        return "DIRECT"
    else:
        return "SEMANTIC"


def generate_recommendations(analysis: AbstractionAnalysis) -> list[str]:
    """Generate specific recommendations based on analysis."""
    recommendations = []

    if analysis.recommended_strategy == "SEMANTIC":
        recommendations.append(
            "Use SEMANTIC translation: Identify what code DOES, not HOW it does it"
        )
        recommendations.append(
            "Group low-level operations into semantic clusters before translating"
        )
        recommendations.append(
            "Replace memory operations with object properties"
        )
        recommendations.append(
            "Replace bit flags with enums and booleans"
        )
        recommendations.append(
            "Replace goto/labels with methods and match statements"
        )
        recommendations.append(
            "See docs/TRANSLATION_LEARNINGS.md for detailed examples"
        )
    elif analysis.recommended_strategy == "DIRECT":
        recommendations.append(
            "Use DIRECT translation: Map idioms from source to target language"
        )
        recommendations.append(
            "Preserve algorithm structure, adapt syntax to target language"
        )
    else:
        recommendations.append(
            "Use LITERAL translation: Direct syntax conversion"
        )
        recommendations.append(
            "Focus on syntax differences between versions"
        )

    # Add warnings about specific patterns
    low_level = analysis.indicators.get("low_level", {})
    if low_level.get("registers", 0) > 0:
        recommendations.append(
            "WARNING: Register operations detected - these should become state variables"
        )
    if low_level.get("flags", 0) > 0:
        recommendations.append(
            "WARNING: CPU flags detected - these should become explicit boolean conditions"
        )
    if low_level.get("memory_direct", 0) > 0:
        recommendations.append(
            "WARNING: Direct memory access detected - these should become object properties"
        )

    return recommendations


def analyze_codebase(codebase_path: str, target_language: Optional[str] = None) -> AbstractionAnalysis:
    """Analyze a codebase and determine its abstraction level."""
    path = Path(codebase_path)

    if not path.exists():
        raise ValueError(f"Path does not exist: {codebase_path}")

    # Collect all source files
    source_files = []
    for ext in LANGUAGE_LEVELS.keys():
        source_files.extend(path.rglob(f"*.{ext}"))

    if not source_files:
        # Try common extensions
        for ext in ['cpp', 'c', 'h', 'py', 'java', 'js', 'ts', 'go', 'rs']:
            source_files.extend(path.rglob(f"*.{ext}"))

    if not source_files:
        raise ValueError(f"No source files found in: {codebase_path}")

    # Analyze files
    all_indicators = {"low_level": {}, "high_level": {}}
    total_lines = 0
    detected_languages = {}

    for filepath in source_files:
        try:
            content = filepath.read_text(errors='ignore')
            total_lines += len(content.splitlines())

            # Track language
            lang = detect_file_language(filepath)
            if lang:
                detected_languages[lang] = detected_languages.get(lang, 0) + 1

            # Analyze content
            file_indicators = analyze_file_content(content)

            # Merge indicators
            for category, count in file_indicators.get("low_level", {}).items():
                all_indicators["low_level"][category] = all_indicators["low_level"].get(category, 0) + count
            for category, count in file_indicators.get("high_level", {}).items():
                all_indicators["high_level"][category] = all_indicators["high_level"].get(category, 0) + count

        except Exception as e:
            print(f"Warning: Could not analyze {filepath}: {e}")

    # Determine primary language
    if detected_languages:
        primary_language = max(detected_languages.keys(), key=lambda k: detected_languages[k])
    else:
        primary_language = "unknown"

    # Get base level from language
    base_level = LANGUAGE_LEVELS.get(primary_language, 3)

    # Adjust based on indicators
    detected_level, confidence = calculate_abstraction_level(all_indicators, base_level)

    # Calculate gap if target specified
    target_level = None
    abstraction_gap = None
    if target_language:
        target_level = LANGUAGE_LEVELS.get(target_language.lower(), 4)
        abstraction_gap = abs(detected_level - target_level)

    # Determine strategy
    if abstraction_gap is not None:
        strategy = get_strategy_recommendation(abstraction_gap)
    else:
        strategy = "UNKNOWN (specify target language)"

    # Build warnings
    warnings = []
    if confidence < 0.7:
        warnings.append("Low confidence in abstraction level detection")
    if detected_level <= 2:
        warnings.append("Assembly-like code detected - semantic translation strongly recommended")
    if all_indicators["low_level"].get("registers", 0) > 100:
        warnings.append("Heavy register usage - this is likely decompiled/emulated code")

    # Create analysis result
    analysis = AbstractionAnalysis(
        source_language=primary_language,
        detected_level=detected_level,
        level_name=get_level_name(detected_level),
        target_language=target_language,
        target_level=target_level,
        abstraction_gap=abstraction_gap,
        recommended_strategy=strategy,
        indicators=all_indicators,
        file_count=len(source_files),
        total_lines=total_lines,
        confidence=confidence,
        warnings=warnings,
        recommendations=[],
    )

    # Generate recommendations
    analysis.recommendations = generate_recommendations(analysis)

    return analysis


def main():
    parser = argparse.ArgumentParser(
        description="Analyze source code abstraction level for migration strategy"
    )
    parser.add_argument("codebase_path", help="Path to source codebase")
    parser.add_argument("--output", "-o", help="Output JSON file path")
    parser.add_argument("--target", "-t", help="Target language for migration")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    try:
        analysis = analyze_codebase(args.codebase_path, args.target)

        # Print summary
        print(f"\n{'='*60}")
        print(f"ABSTRACTION LEVEL ANALYSIS")
        print(f"{'='*60}")
        print(f"Source Language: {analysis.source_language}")
        print(f"Detected Level: {analysis.detected_level} ({analysis.level_name})")
        print(f"Confidence: {analysis.confidence:.1%}")
        print(f"Files Analyzed: {analysis.file_count}")
        print(f"Total Lines: {analysis.total_lines:,}")

        if analysis.target_language:
            print(f"\nTarget Language: {analysis.target_language}")
            print(f"Target Level: {analysis.target_level} ({get_level_name(analysis.target_level)})")
            print(f"Abstraction Gap: {analysis.abstraction_gap}")

        print(f"\n{'='*60}")
        print(f"RECOMMENDED STRATEGY: {analysis.recommended_strategy}")
        print(f"{'='*60}")

        if analysis.warnings:
            print("\nWarnings:")
            for warning in analysis.warnings:
                print(f"  ⚠️  {warning}")

        print("\nRecommendations:")
        for rec in analysis.recommendations:
            print(f"  • {rec}")

        if args.verbose:
            print("\nIndicators:")
            print("  Low-level:", dict(analysis.indicators.get("low_level", {})))
            print("  High-level:", dict(analysis.indicators.get("high_level", {})))

        # Write output
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(asdict(analysis), f, indent=2)
            print(f"\nAnalysis written to: {args.output}")

    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
