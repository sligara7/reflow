#!/usr/bin/env python3
"""
Configuration Consistency Validation Tool

Validates that code defaults match docker-compose.yml deployment configuration.
Prevents configuration drift issues (DATABASE_URL mismatches, port conflicts, etc.).

Usage:
    python3 validate_configuration_consistency.py --system-root /path/to/system

Part of Reflow v3.6.0 - Early Testing Integration feature (D-06.5-A03)
Prevents Category 5 issues: Code-configuration mismatch (2 issues from operational testing)
"""

import argparse
import ast
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
import yaml


class ConfigurationConsistencyValidator:
    """Validates configuration consistency between code and deployment config."""

    def __init__(self, system_root: Path):
        self.system_root = Path(system_root)
        self.services_dir = self.system_root / "services"
        self.docker_compose_file = self._find_docker_compose()

    def _find_docker_compose(self) -> Optional[Path]:
        """Find docker-compose.yml file."""
        candidates = [
            self.system_root / "docker-compose.yml",
            self.system_root / "docker-compose.yaml",
            self.services_dir / "docker-compose.yml",
            self.services_dir / "docker-compose.yaml"
        ]

        for candidate in candidates:
            if candidate.exists():
                return candidate

        return None

    def validate(self) -> Dict:
        """Validate configuration consistency across all services."""
        print("\nValidating configuration consistency...")

        if not self.docker_compose_file:
            return {
                "status": "warning",
                "message": "No docker-compose.yml found - skipping deployment config validation"
            }

        print(f"  Using docker-compose file: {self.docker_compose_file}")

        # Parse docker-compose.yml
        try:
            docker_config = self._parse_docker_compose()
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to parse docker-compose.yml: {e}"
            }

        # Find all services
        services = self._find_services()
        if not services:
            return {
                "status": "error",
                "error": "No services found"
            }

        print(f"  Found {len(services)} services: {', '.join(services)}")

        issues = []

        # Validate each service
        for service in services:
            service_issues = self._validate_service(service, docker_config)
            issues.extend(service_issues)

        # System-wide checks
        system_issues = self._validate_system_wide(docker_config)
        issues.extend(system_issues)

        # Build result
        result = {
            "status": "fail" if issues else "pass",
            "docker_compose_file": str(self.docker_compose_file),
            "services_validated": len(services),
            "total_issues": len(issues),
            "issues": issues
        }

        return result

    def _parse_docker_compose(self) -> Dict:
        """Parse docker-compose.yml file."""
        with open(self.docker_compose_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _find_services(self) -> List[str]:
        """Find all service directories."""
        if not self.services_dir.exists():
            return []

        services = [
            d.name for d in self.services_dir.iterdir()
            if d.is_dir() and not d.name.startswith('.')
            and (d / "src").exists()
        ]

        return services

    def _validate_service(
        self,
        service_name: str,
        docker_config: Dict
    ) -> List[Dict]:
        """Validate configuration for a single service."""
        issues = []
        service_dir = self.services_dir / service_name

        # Extract code configuration
        code_config = self._extract_code_config(service_dir)

        # Extract docker-compose configuration for this service
        docker_service_config = docker_config.get('services', {}).get(service_name, {})

        if not docker_service_config:
            issues.append({
                "type": "missing_docker_service",
                "severity": "warning",
                "service": service_name,
                "message": f"Service '{service_name}' not found in docker-compose.yml",
                "fix": f"Add service '{service_name}' to docker-compose.yml"
            })
            return issues

        # Check 1: DATABASE_URL consistency
        db_issues = self._check_database_url(
            service_name,
            code_config.get('database_url'),
            docker_service_config.get('environment', {})
        )
        issues.extend(db_issues)

        # Check 2: Port consistency
        port_issues = self._check_ports(
            service_name,
            code_config.get('port'),
            docker_service_config.get('ports', [])
        )
        issues.extend(port_issues)

        # Check 3: Environment variables
        env_issues = self._check_environment_variables(
            service_name,
            code_config.get('env_vars', set()),
            docker_service_config.get('environment', {})
        )
        issues.extend(env_issues)

        # Check 4: Hardcoded localhost
        localhost_issues = self._check_hardcoded_localhost(service_name, service_dir)
        issues.extend(localhost_issues)

        return issues

    def _extract_code_config(self, service_dir: Path) -> Dict:
        """Extract configuration defaults from service code."""
        config = {
            'database_url': None,
            'port': None,
            'env_vars': set()
        }

        src_dir = service_dir / "src"
        if not src_dir.exists():
            return config

        # Scan Python files for configuration patterns
        for py_file in src_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract DATABASE_URL
                db_url_match = re.search(
                    r'DATABASE_URL\s*=\s*os\.getenv\(["\']DATABASE_URL["\']\s*,\s*["\']([^"\']+)["\']',
                    content
                )
                if db_url_match:
                    config['database_url'] = db_url_match.group(1)

                # Extract PORT
                port_match = re.search(
                    r'PORT\s*=\s*(?:int\()?os\.getenv\(["\']PORT["\']\s*,\s*["\']?(\d+)["\']?\)',
                    content
                )
                if port_match:
                    config['port'] = int(port_match.group(1))

                # Extract all environment variable references
                env_var_matches = re.findall(
                    r'os\.getenv\(["\']([A-Z_]+)["\']',
                    content
                )
                config['env_vars'].update(env_var_matches)

            except Exception:
                continue

        return config

    def _check_database_url(
        self,
        service_name: str,
        code_db_url: Optional[str],
        docker_env: Dict
    ) -> List[Dict]:
        """Check DATABASE_URL consistency."""
        issues = []

        if not code_db_url:
            return issues  # No DATABASE_URL in code

        # Get DATABASE_URL from docker-compose
        docker_db_url = docker_env.get('DATABASE_URL')

        if not docker_db_url:
            issues.append({
                "type": "missing_database_url",
                "severity": "warning",
                "service": service_name,
                "message": f"Service code references DATABASE_URL but not set in docker-compose.yml",
                "code_default": code_db_url,
                "fix": "Add DATABASE_URL to docker-compose.yml environment section"
            })
            return issues

        # Check for common mismatches
        # Issue 1: postgresql:// vs postgresql+psycopg2://
        if 'postgresql://' in code_db_url and 'postgresql+psycopg2://' not in code_db_url:
            if 'postgresql+psycopg2://' in docker_db_url or 'postgresql://' in docker_db_url:
                issues.append({
                    "type": "database_url_driver_mismatch",
                    "severity": "error",
                    "service": service_name,
                    "message": "DATABASE_URL driver mismatch between code and docker-compose",
                    "code_default": code_db_url,
                    "docker_value": docker_db_url,
                    "fix": "Ensure both use 'postgresql+psycopg2://' for SQLAlchemy or 'postgresql://' for psycopg2"
                })

        # Issue 2: Extract user/database from both and compare
        code_parts = self._parse_database_url(code_db_url)
        docker_parts = self._parse_database_url(docker_db_url)

        if code_parts and docker_parts:
            if code_parts.get('user') != docker_parts.get('user'):
                issues.append({
                    "type": "database_user_mismatch",
                    "severity": "warning",
                    "service": service_name,
                    "message": "Database user differs between code and docker-compose",
                    "code_user": code_parts.get('user'),
                    "docker_user": docker_parts.get('user'),
                    "fix": "Ensure database user is consistent"
                })

            if code_parts.get('database') != docker_parts.get('database'):
                issues.append({
                    "type": "database_name_mismatch",
                    "severity": "warning",
                    "service": service_name,
                    "message": "Database name differs between code and docker-compose",
                    "code_database": code_parts.get('database'),
                    "docker_database": docker_parts.get('database'),
                    "fix": "Ensure database name is consistent"
                })

        return issues

    def _parse_database_url(self, db_url: str) -> Optional[Dict]:
        """Parse DATABASE_URL into components."""
        # Pattern: postgresql://user:password@host:port/database
        match = re.match(
            r'postgresql(?:\+\w+)?://([^:]+):?([^@]*)@([^:]+):?(\d+)?/(.+)',
            db_url
        )

        if match:
            return {
                'user': match.group(1),
                'password': match.group(2),
                'host': match.group(3),
                'port': match.group(4),
                'database': match.group(5)
            }

        return None

    def _check_ports(
        self,
        service_name: str,
        code_port: Optional[int],
        docker_ports: List
    ) -> List[Dict]:
        """Check port consistency."""
        issues = []

        if not code_port:
            return issues  # No port in code

        if not docker_ports:
            issues.append({
                "type": "missing_port_mapping",
                "severity": "warning",
                "service": service_name,
                "message": f"Service code uses port {code_port} but no port mapping in docker-compose.yml",
                "code_port": code_port,
                "fix": f"Add port mapping to docker-compose.yml (e.g., '{code_port}:{code_port}')"
            })
            return issues

        # Parse docker port mappings (format: "host:container" or "container")
        container_ports = []
        for port_mapping in docker_ports:
            port_str = str(port_mapping)
            if ':' in port_str:
                _, container_port = port_str.split(':')
                container_ports.append(int(container_port))
            else:
                container_ports.append(int(port_str))

        if code_port not in container_ports:
            issues.append({
                "type": "port_mismatch",
                "severity": "error",
                "service": service_name,
                "message": f"Service code uses port {code_port} but docker-compose uses {container_ports}",
                "code_port": code_port,
                "docker_ports": container_ports,
                "fix": f"Update docker-compose port mapping to include container port {code_port}"
            })

        return issues

    def _check_environment_variables(
        self,
        service_name: str,
        code_env_vars: Set[str],
        docker_env: Dict
    ) -> List[Dict]:
        """Check that environment variables referenced in code are defined in docker-compose."""
        issues = []

        # Filter out common env vars that might have defaults
        ignore_vars = {'PATH', 'HOME', 'USER', 'PYTHONPATH'}
        required_vars = code_env_vars - ignore_vars

        missing_vars = []
        for var in required_vars:
            if var not in docker_env:
                missing_vars.append(var)

        if missing_vars:
            issues.append({
                "type": "missing_environment_variables",
                "severity": "warning",
                "service": service_name,
                "message": f"Service code references environment variables not set in docker-compose.yml",
                "missing_variables": missing_vars,
                "fix": "Add missing environment variables to docker-compose.yml or ensure they have defaults in code"
            })

        return issues

    def _check_hardcoded_localhost(
        self,
        service_name: str,
        service_dir: Path
    ) -> List[Dict]:
        """Check for hardcoded localhost references (should use service names in Docker)."""
        issues = []

        src_dir = service_dir / "src"
        if not src_dir.exists():
            return issues

        localhost_files = []

        for py_file in src_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Check for localhost or 127.0.0.1 in URLs
                if re.search(r'(localhost|127\.0\.0\.1)(?!.*example)', content):
                    localhost_files.append(str(py_file.relative_to(service_dir)))

            except Exception:
                continue

        if localhost_files:
            issues.append({
                "type": "hardcoded_localhost",
                "severity": "warning",
                "service": service_name,
                "message": "Hardcoded 'localhost' or '127.0.0.1' found in code",
                "files": localhost_files[:5],  # Limit to 5 examples
                "fix": "Use service names from docker-compose.yml instead of localhost (e.g., 'http://character_service:8000')"
            })

        return issues

    def _validate_system_wide(self, docker_config: Dict) -> List[Dict]:
        """Perform system-wide validation checks."""
        issues = []

        # Check for port conflicts between services
        port_conflicts = self._check_port_conflicts(docker_config)
        issues.extend(port_conflicts)

        return issues

    def _check_port_conflicts(self, docker_config: Dict) -> List[Dict]:
        """Check for port conflicts between services."""
        issues = []
        port_to_services = {}

        for service_name, service_config in docker_config.get('services', {}).items():
            ports = service_config.get('ports', [])

            for port_mapping in ports:
                port_str = str(port_mapping)

                # Extract host port
                if ':' in port_str:
                    host_port, _ = port_str.split(':')
                else:
                    host_port = port_str

                try:
                    host_port = int(host_port)
                except ValueError:
                    continue

                if host_port in port_to_services:
                    port_to_services[host_port].append(service_name)
                else:
                    port_to_services[host_port] = [service_name]

        # Find conflicts (multiple services using same host port)
        for port, services in port_to_services.items():
            if len(services) > 1:
                issues.append({
                    "type": "port_conflict",
                    "severity": "error",
                    "port": port,
                    "services": services,
                    "message": f"Port {port} is used by multiple services: {', '.join(services)}",
                    "fix": "Assign unique host ports to each service"
                })

        return issues


def main():
    parser = argparse.ArgumentParser(
        description="Validate configuration consistency between code and docker-compose.yml"
    )
    parser.add_argument(
        '--system-root',
        required=True,
        help='Path to system root directory'
    )
    parser.add_argument(
        '--output',
        help='Output JSON report to file'
    )

    args = parser.parse_args()

    validator = ConfigurationConsistencyValidator(args.system_root)
    result = validator.validate()

    # Output result
    if args.output:
        output_file = Path(args.output)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\nValidation report written to: {output_file}")

    # Print summary
    print("\n" + "="*60)
    print("CONFIGURATION CONSISTENCY VALIDATION SUMMARY")
    print("="*60)

    if result['status'] == 'pass':
        print("✅ PASS: Configuration is consistent")
        sys.exit(0)
    elif result['status'] == 'fail':
        print("❌ FAIL: Configuration inconsistencies found")
        print("\nCommon issues:")
        print("  - DATABASE_URL driver mismatch (postgresql:// vs postgresql+psycopg2://)")
        print("  - Port mismatches between code and docker-compose")
        print("  - Missing environment variables in docker-compose")
        print("  - Hardcoded localhost (should use service names)")
        print("  - Port conflicts between services")
        sys.exit(1)
    elif result['status'] == 'warning':
        print(f"⚠️  WARNING: {result.get('message', 'Unknown warning')}")
        sys.exit(0)
    else:
        print(f"⚠️  ERROR: {result.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == '__main__':
    main()
