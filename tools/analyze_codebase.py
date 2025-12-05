#!/usr/bin/env python3
"""
analyze_codebase.py - Codebase Discovery and Inventory Tool

Part of Reflow v4.1.0 System Overhaul Feature
Workflow: 01e-reverse_engineering
Step: RE-01 Codebase Discovery & Inventory

Scans a codebase directory and generates a comprehensive inventory including:
- Programming languages and versions detected
- Frameworks and libraries
- Entry points (main functions, API endpoints, CLI handlers)
- Dependencies from manifest files
- Configuration files and environment variables
- Code metrics (LOC, file count, etc.)

Usage:
    python3 analyze_codebase.py <codebase_path> --output <output_path>

Example:
    python3 analyze_codebase.py /path/to/legacy/code --output specs/reverse/codebase_inventory.json
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


# File extension to language mapping
EXTENSION_TO_LANGUAGE = {
    '.py': 'python',
    '.pyw': 'python',
    '.pyx': 'python',
    '.js': 'javascript',
    '.jsx': 'javascript',
    '.ts': 'typescript',
    '.tsx': 'typescript',
    '.java': 'java',
    '.kt': 'kotlin',
    '.kts': 'kotlin',
    '.go': 'go',
    '.rs': 'rust',
    '.rb': 'ruby',
    '.php': 'php',
    '.c': 'c',
    '.h': 'c',
    '.cpp': 'cpp',
    '.cc': 'cpp',
    '.cxx': 'cpp',
    '.hpp': 'cpp',
    '.cs': 'csharp',
    '.swift': 'swift',
    '.scala': 'scala',
    '.clj': 'clojure',
    '.ex': 'elixir',
    '.exs': 'elixir',
    '.erl': 'erlang',
    '.hs': 'haskell',
    '.lua': 'lua',
    '.pl': 'perl',
    '.pm': 'perl',
    '.r': 'r',
    '.R': 'r',
    '.sql': 'sql',
    '.sh': 'shell',
    '.bash': 'shell',
    '.zsh': 'shell',
    '.cbl': 'cobol',
    '.cob': 'cobol',
    '.f': 'fortran',
    '.f90': 'fortran',
    '.f95': 'fortran',
    '.for': 'fortran',
}

# Default exclude patterns
DEFAULT_EXCLUDES = [
    '**/node_modules/**',
    '**/.git/**',
    '**/venv/**',
    '**/.venv/**',
    '**/env/**',
    '**/__pycache__/**',
    '**/.tox/**',
    '**/dist/**',
    '**/build/**',
    '**/*.egg-info/**',
    '**/target/**',
    '**/.idea/**',
    '**/.vscode/**',
    '**/vendor/**',
]

# Framework detection patterns
FRAMEWORK_PATTERNS = {
    'python': {
        'django': [
            ('file', 'manage.py'),
            ('file', 'settings.py'),
            ('import', r'from django'),
            ('import', r'import django'),
        ],
        'flask': [
            ('import', r'from flask'),
            ('import', r'import flask'),
        ],
        'fastapi': [
            ('import', r'from fastapi'),
            ('import', r'import fastapi'),
        ],
        'celery': [
            ('import', r'from celery'),
            ('import', r'import celery'),
        ],
        'sqlalchemy': [
            ('import', r'from sqlalchemy'),
            ('import', r'import sqlalchemy'),
        ],
        'pytest': [
            ('import', r'import pytest'),
            ('file', 'pytest.ini'),
            ('file', 'conftest.py'),
        ],
        'pandas': [
            ('import', r'import pandas'),
            ('import', r'from pandas'),
        ],
        'numpy': [
            ('import', r'import numpy'),
            ('import', r'from numpy'),
        ],
    },
    'javascript': {
        'react': [
            ('import', r'from [\'"]react[\'"]'),
            ('import', r'require\([\'"]react[\'"]\)'),
        ],
        'vue': [
            ('import', r'from [\'"]vue[\'"]'),
            ('file', 'vue.config.js'),
        ],
        'angular': [
            ('import', r'@angular/core'),
            ('file', 'angular.json'),
        ],
        'express': [
            ('import', r'require\([\'"]express[\'"]\)'),
            ('import', r'from [\'"]express[\'"]'),
        ],
        'next': [
            ('file', 'next.config.js'),
            ('import', r'from [\'"]next'),
        ],
    },
    'java': {
        'spring': [
            ('import', r'org\.springframework'),
            ('annotation', r'@SpringBootApplication'),
            ('file', 'application.properties'),
            ('file', 'application.yml'),
        ],
        'hibernate': [
            ('import', r'org\.hibernate'),
            ('import', r'javax\.persistence'),
        ],
    },
    'go': {
        'gin': [
            ('import', r'github\.com/gin-gonic/gin'),
        ],
        'echo': [
            ('import', r'github\.com/labstack/echo'),
        ],
        'fiber': [
            ('import', r'github\.com/gofiber/fiber'),
        ],
    },
}


def should_exclude(path: Path, exclude_patterns: List[str]) -> bool:
    """Check if path matches any exclude pattern."""
    path_str = str(path)
    for pattern in exclude_patterns:
        # Simple glob matching
        if '**' in pattern:
            regex_pattern = pattern.replace('**', '.*').replace('*', '[^/]*')
            if re.search(regex_pattern, path_str):
                return True
        elif '*' in pattern:
            regex_pattern = pattern.replace('*', '.*')
            if re.match(regex_pattern, path_str):
                return True
        elif pattern in path_str:
            return True
    return False


def count_lines(file_path: Path) -> Tuple[int, int, int]:
    """Count total, blank, and comment lines in a file."""
    total = 0
    blank = 0
    comment = 0

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            in_multiline_comment = False
            ext = file_path.suffix.lower()

            for line in f:
                total += 1
                stripped = line.strip()

                if not stripped:
                    blank += 1
                    continue

                # Python comments
                if ext in ['.py', '.pyw']:
                    if stripped.startswith('#'):
                        comment += 1
                    elif '"""' in stripped or "'''" in stripped:
                        if stripped.count('"""') == 1 or stripped.count("'''") == 1:
                            in_multiline_comment = not in_multiline_comment
                        comment += 1
                    elif in_multiline_comment:
                        comment += 1

                # C-style comments
                elif ext in ['.js', '.jsx', '.ts', '.tsx', '.java', '.c', '.cpp', '.h', '.hpp', '.cs', '.go', '.rs', '.swift', '.kt']:
                    if stripped.startswith('//'):
                        comment += 1
                    elif '/*' in stripped:
                        in_multiline_comment = True
                        comment += 1
                    elif '*/' in stripped:
                        in_multiline_comment = False
                        comment += 1
                    elif in_multiline_comment:
                        comment += 1

                # Shell comments
                elif ext in ['.sh', '.bash', '.zsh']:
                    if stripped.startswith('#'):
                        comment += 1

    except Exception:
        pass

    return total, blank, comment


def detect_python_version(codebase_path: Path) -> Optional[str]:
    """Detect Python version from various config files."""
    # Check pyproject.toml
    pyproject = codebase_path / 'pyproject.toml'
    if pyproject.exists():
        try:
            content = pyproject.read_text()
            match = re.search(r'requires-python\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)
        except Exception:
            pass

    # Check setup.py
    setup_py = codebase_path / 'setup.py'
    if setup_py.exists():
        try:
            content = setup_py.read_text()
            match = re.search(r'python_requires\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)
        except Exception:
            pass

    # Check .python-version
    python_version = codebase_path / '.python-version'
    if python_version.exists():
        try:
            return python_version.read_text().strip()
        except Exception:
            pass

    # Check runtime.txt (Heroku)
    runtime = codebase_path / 'runtime.txt'
    if runtime.exists():
        try:
            content = runtime.read_text().strip()
            if content.startswith('python-'):
                return content.replace('python-', '')
        except Exception:
            pass

    return None


def detect_node_version(codebase_path: Path) -> Optional[str]:
    """Detect Node.js version from package.json."""
    package_json = codebase_path / 'package.json'
    if package_json.exists():
        try:
            with open(package_json) as f:
                data = json.load(f)
                engines = data.get('engines', {})
                return engines.get('node')
        except Exception:
            pass

    # Check .nvmrc
    nvmrc = codebase_path / '.nvmrc'
    if nvmrc.exists():
        try:
            return nvmrc.read_text().strip()
        except Exception:
            pass

    return None


def parse_requirements(file_path: Path) -> List[Dict[str, str]]:
    """Parse requirements.txt file."""
    deps = []
    try:
        with open(file_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('-'):
                    # Parse package==version or package>=version etc.
                    match = re.match(r'^([a-zA-Z0-9_-]+)([<>=!]+.*)?$', line.split('[')[0])
                    if match:
                        deps.append({
                            'name': match.group(1),
                            'version_constraint': match.group(2) or '*',
                            'source': str(file_path.name)
                        })
    except Exception:
        pass
    return deps


def parse_package_json(file_path: Path) -> Tuple[List[Dict], List[Dict]]:
    """Parse package.json for dependencies."""
    runtime_deps = []
    dev_deps = []

    try:
        with open(file_path) as f:
            data = json.load(f)

            for name, version in data.get('dependencies', {}).items():
                runtime_deps.append({
                    'name': name,
                    'version_constraint': version,
                    'source': 'package.json'
                })

            for name, version in data.get('devDependencies', {}).items():
                dev_deps.append({
                    'name': name,
                    'version_constraint': version,
                    'source': 'package.json'
                })
    except Exception:
        pass

    return runtime_deps, dev_deps


def detect_entry_points(codebase_path: Path, language: str, files: List[Path]) -> List[Dict]:
    """Detect entry points for a language."""
    entry_points = []

    if language == 'python':
        # Check for main blocks
        for f in files:
            if f.suffix == '.py':
                try:
                    content = f.read_text(errors='ignore')
                    if "if __name__ == '__main__':" in content or 'if __name__ == "__main__":' in content:
                        entry_points.append({
                            'type': 'main',
                            'file': str(f.relative_to(codebase_path)),
                            'function': '__main__',
                            'description': 'Main entry point'
                        })
                except Exception:
                    pass

        # Check for manage.py (Django)
        manage_py = codebase_path / 'manage.py'
        if manage_py.exists():
            entry_points.append({
                'type': 'cli',
                'file': 'manage.py',
                'function': 'main',
                'description': 'Django management CLI',
                'commands': ['runserver', 'migrate', 'shell', 'test']
            })

        # Check for wsgi.py
        for f in codebase_path.rglob('wsgi.py'):
            entry_points.append({
                'type': 'wsgi',
                'file': str(f.relative_to(codebase_path)),
                'function': 'application',
                'description': 'WSGI application entry point'
            })

        # Check for asgi.py
        for f in codebase_path.rglob('asgi.py'):
            entry_points.append({
                'type': 'asgi',
                'file': str(f.relative_to(codebase_path)),
                'function': 'application',
                'description': 'ASGI application entry point'
            })

    elif language in ['javascript', 'typescript']:
        # Check package.json for scripts and main
        package_json = codebase_path / 'package.json'
        if package_json.exists():
            try:
                with open(package_json) as f:
                    data = json.load(f)

                    if 'main' in data:
                        entry_points.append({
                            'type': 'main',
                            'file': data['main'],
                            'description': 'Main entry point from package.json'
                        })

                    scripts = data.get('scripts', {})
                    if scripts:
                        entry_points.append({
                            'type': 'scripts',
                            'file': 'package.json',
                            'description': 'NPM scripts',
                            'commands': list(scripts.keys())
                        })
            except Exception:
                pass

        # Check for common server files
        for name in ['server.js', 'server.ts', 'index.js', 'index.ts', 'app.js', 'app.ts']:
            server_file = codebase_path / name
            if server_file.exists():
                entry_points.append({
                    'type': 'server',
                    'file': name,
                    'description': f'Server entry point ({name})'
                })

    elif language == 'java':
        # Look for main methods
        for f in files:
            if f.suffix == '.java':
                try:
                    content = f.read_text(errors='ignore')
                    if 'public static void main(String' in content:
                        entry_points.append({
                            'type': 'main',
                            'file': str(f.relative_to(codebase_path)),
                            'function': 'main',
                            'description': 'Java main class'
                        })
                    if '@SpringBootApplication' in content:
                        entry_points.append({
                            'type': 'spring_boot',
                            'file': str(f.relative_to(codebase_path)),
                            'description': 'Spring Boot application'
                        })
                except Exception:
                    pass

    elif language == 'go':
        # Look for main packages
        for f in files:
            if f.suffix == '.go':
                try:
                    content = f.read_text(errors='ignore')
                    if 'package main' in content and 'func main()' in content:
                        entry_points.append({
                            'type': 'main',
                            'file': str(f.relative_to(codebase_path)),
                            'function': 'main',
                            'description': 'Go main package'
                        })
                except Exception:
                    pass

    return entry_points


def detect_frameworks(codebase_path: Path, language: str, files: List[Path]) -> List[Dict]:
    """Detect frameworks used in the codebase."""
    detected = []

    if language not in FRAMEWORK_PATTERNS:
        return detected

    patterns = FRAMEWORK_PATTERNS[language]

    for framework, checks in patterns.items():
        confidence = 0
        detection_sources = []

        for check_type, pattern in checks:
            if check_type == 'file':
                for f in codebase_path.rglob(pattern):
                    if not should_exclude(f, DEFAULT_EXCLUDES):
                        confidence += 1
                        detection_sources.append(f'file:{pattern}')
                        break

            elif check_type == 'import':
                for f in files[:100]:  # Check first 100 files for performance
                    try:
                        content = f.read_text(errors='ignore')
                        if re.search(pattern, content):
                            confidence += 1
                            detection_sources.append(f'import:{pattern}')
                            break
                    except Exception:
                        pass

            elif check_type == 'annotation':
                for f in files[:100]:
                    try:
                        content = f.read_text(errors='ignore')
                        if re.search(pattern, content):
                            confidence += 1
                            detection_sources.append(f'annotation:{pattern}')
                            break
                    except Exception:
                        pass

        if confidence > 0:
            detected.append({
                'name': framework,
                'version': 'unknown',
                'usage_areas': [],
                'confidence': 'high' if confidence >= 2 else 'medium' if confidence == 1 else 'low',
                'detection_source': ', '.join(detection_sources[:3])
            })

    return detected


def analyze_codebase(codebase_path: str, output_path: str, exclude_patterns: Optional[List[str]] = None) -> Dict[str, Any]:
    """Main function to analyze a codebase."""
    codebase = Path(codebase_path).resolve()

    if not codebase.exists():
        raise ValueError(f"Codebase path does not exist: {codebase_path}")

    if not codebase.is_dir():
        raise ValueError(f"Codebase path is not a directory: {codebase_path}")

    excludes = exclude_patterns or DEFAULT_EXCLUDES

    # Collect all files
    all_files: List[Path] = []
    files_by_language: Dict[str, List[Path]] = defaultdict(list)
    files_by_extension: Dict[str, int] = defaultdict(int)

    for f in codebase.rglob('*'):
        if f.is_file() and not should_exclude(f, excludes):
            all_files.append(f)
            ext = f.suffix.lower()
            files_by_extension[ext] += 1

            if ext in EXTENSION_TO_LANGUAGE:
                lang = EXTENSION_TO_LANGUAGE[ext]
                files_by_language[lang].append(f)

    # Determine primary language
    language_stats = []
    for lang, files in files_by_language.items():
        total_lines = 0
        for f in files[:50]:  # Sample for performance
            lines, _, _ = count_lines(f)
            total_lines += lines

        if len(files) > 50:
            total_lines = int(total_lines * len(files) / 50)

        language_stats.append({
            'language': lang,
            'file_count': len(files),
            'estimated_loc': total_lines,
        })

    language_stats.sort(key=lambda x: x['file_count'], reverse=True)

    # Build languages_detected
    languages_detected = []
    for i, stat in enumerate(language_stats):
        lang = stat['language']
        version = None

        if lang == 'python':
            version = detect_python_version(codebase)
        elif lang in ['javascript', 'typescript']:
            version = detect_node_version(codebase)

        languages_detected.append({
            'language': lang,
            'version_detected': version or 'unknown',
            'file_count': stat['file_count'],
            'lines_of_code': stat['estimated_loc'],
            'primary': i == 0,
            'detection_method': 'file_extension'
        })

    # Detect frameworks for primary language
    frameworks_detected = []
    if languages_detected:
        primary_lang = languages_detected[0]['language']
        primary_files = files_by_language.get(primary_lang, [])
        frameworks_detected = detect_frameworks(codebase, primary_lang, primary_files)

    # Detect entry points
    entry_points = []
    if languages_detected:
        primary_lang = languages_detected[0]['language']
        primary_files = files_by_language.get(primary_lang, [])
        entry_points = detect_entry_points(codebase, primary_lang, primary_files)

    # Parse dependencies
    runtime_deps = []
    dev_deps = []
    system_deps = []

    # Python dependencies
    for req_file in codebase.glob('requirements*.txt'):
        deps = parse_requirements(req_file)
        if 'dev' in req_file.name.lower() or 'test' in req_file.name.lower():
            dev_deps.extend(deps)
        else:
            runtime_deps.extend(deps)

    # Node dependencies
    package_json = codebase / 'package.json'
    if package_json.exists():
        rt, dv = parse_package_json(package_json)
        runtime_deps.extend(rt)
        dev_deps.extend(dv)

    # Find config files
    config_files = []
    env_vars = set()

    config_patterns = ['*.env', '.env*', 'config.json', 'config.yaml', 'config.yml',
                       'settings.py', 'application.properties', 'application.yml']

    for pattern in config_patterns:
        for f in codebase.glob(pattern):
            if not should_exclude(f, excludes):
                config_files.append({
                    'path': str(f.relative_to(codebase)),
                    'type': f.suffix.lstrip('.') or 'env',
                    'purpose': 'Configuration file'
                })

    # Calculate code metrics
    total_lines = 0
    blank_lines = 0
    comment_lines = 0

    sample_files = all_files[:200]  # Sample for performance
    for f in sample_files:
        t, b, c = count_lines(f)
        total_lines += t
        blank_lines += b
        comment_lines += c

    if len(all_files) > 200:
        scale = len(all_files) / 200
        total_lines = int(total_lines * scale)
        blank_lines = int(blank_lines * scale)
        comment_lines = int(comment_lines * scale)

    # Find largest files
    file_sizes = []
    for f in all_files:
        if f.suffix.lower() in EXTENSION_TO_LANGUAGE:
            lines, _, _ = count_lines(f)
            file_sizes.append((f, lines))

    file_sizes.sort(key=lambda x: x[1], reverse=True)
    largest_files = [
        {
            'path': str(f.relative_to(codebase)),
            'lines': lines,
            'note': 'May need refactoring' if lines > 500 else ''
        }
        for f, lines in file_sizes[:10]
    ]

    # Build inventory
    inventory = {
        'schema_version': '1.0.0',
        'inventory_date': datetime.now().isoformat(),
        'source_root': str(codebase),
        'analysis_configuration': {
            'exclude_patterns': excludes,
            'max_file_size_mb': 10,
            'analysis_depth': 'full'
        },
        'languages_detected': languages_detected,
        'frameworks_detected': frameworks_detected,
        'entry_points': entry_points,
        'dependencies': {
            'runtime': runtime_deps[:50],  # Limit for readability
            'development': dev_deps[:30],
            'system': system_deps
        },
        'configuration': {
            'files': config_files,
            'environment_variables': list(env_vars)[:20]
        },
        'directory_structure': {
            'pattern': 'custom',
            'top_level_directories': [
                {
                    'name': d.name,
                    'purpose': 'Unknown',
                    'file_count': sum(1 for _ in d.rglob('*') if _.is_file())
                }
                for d in sorted(codebase.iterdir())[:15]
                if d.is_dir() and not d.name.startswith('.') and not should_exclude(d, excludes)
            ],
            'tests_location': 'tests/' if (codebase / 'tests').exists() else 'test/' if (codebase / 'test').exists() else 'unknown'
        },
        'code_metrics': {
            'total_files': len(all_files),
            'total_lines': total_lines,
            'blank_lines': blank_lines,
            'comment_lines': comment_lines,
            'code_lines': total_lines - blank_lines - comment_lines,
            'test_files': sum(1 for f in all_files if 'test' in f.name.lower()),
            'documentation_detected': 'minimal',
            'files_by_extension': dict(sorted(files_by_extension.items(), key=lambda x: x[1], reverse=True)[:15]),
            'largest_files': largest_files,
            'average_file_size_lines': total_lines // max(len(all_files), 1)
        },
        'potential_issues_detected': [],
        'recommendations': [],
        'analysis_notes': {
            'limitations': ['Some files may have been skipped due to encoding issues'],
            'manual_review_needed': [],
            'assumptions_made': ['File extensions accurately indicate language']
        }
    }

    # Add potential issues
    if total_lines > 100000:
        inventory['potential_issues_detected'].append({
            'issue_type': 'large_codebase',
            'location': 'entire codebase',
            'severity': 'medium',
            'description': f'Large codebase with {total_lines:,} lines - may need modular analysis'
        })

    if not entry_points:
        inventory['potential_issues_detected'].append({
            'issue_type': 'no_entry_points',
            'location': 'entire codebase',
            'severity': 'high',
            'description': 'No entry points detected - may need manual identification'
        })

    # Write output
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with open(output, 'w') as f:
        json.dump(inventory, f, indent=2)

    print(f"Codebase inventory written to: {output}")
    print(f"\nSummary:")
    print(f"  Total files: {len(all_files):,}")
    print(f"  Total lines: {total_lines:,}")
    print(f"  Languages: {', '.join(l['language'] for l in languages_detected[:5])}")
    print(f"  Frameworks: {', '.join(f['name'] for f in frameworks_detected[:5])}")
    print(f"  Entry points: {len(entry_points)}")

    return inventory


def main():
    parser = argparse.ArgumentParser(
        description='Analyze a codebase and generate inventory',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/legacy/code --output specs/reverse/codebase_inventory.json
  %(prog)s /path/to/code --exclude "*.test.*" --exclude "**/docs/**"
        """
    )
    parser.add_argument('codebase_path', help='Path to the codebase to analyze')
    parser.add_argument('--output', '-o', required=True, help='Output path for inventory JSON')
    parser.add_argument('--exclude', action='append', help='Additional exclude patterns')

    args = parser.parse_args()

    exclude_patterns = DEFAULT_EXCLUDES.copy()
    if args.exclude:
        exclude_patterns.extend(args.exclude)

    try:
        analyze_codebase(args.codebase_path, args.output, exclude_patterns)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
