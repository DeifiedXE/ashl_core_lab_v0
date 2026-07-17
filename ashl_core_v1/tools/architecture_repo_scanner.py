"""Repo-grounded architecture scanner for Package 122A.

The scanner is deliberately source-code oriented.  It reads Python source,
tests, and documents, then emits deterministic records that other Package 122A
tools classify.  It does not import runtime modules, open devices, create
sessions, or inspect live runtime databases.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
from dataclasses import asdict, dataclass, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


BASELINE_SCHEMA_VERSION = "ashl_architecture_repo_scan_baseline_v0"
SCAN_RESULT_SCHEMA_VERSION = "ashl_architecture_reconciliation_scan_result_v0"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def plain(value: Any) -> Any:
    if is_dataclass(value):
        return plain(asdict(value))
    if hasattr(value, "to_dict"):
        return plain(value.to_dict())
    if isinstance(value, dict):
        return {str(key): plain(item) for key, item in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [plain(item) for item in value]
    if isinstance(value, Path):
        return value.as_posix()
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(plain(value), ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def sha256_payload(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def stable_id(prefix: str, payload: Any) -> str:
    return f"{prefix}:{sha256_payload(payload)[:16]}"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def safe_parse_python(path: Path) -> ast.Module | None:
    try:
        return ast.parse(read_text(path), filename=str(path))
    except SyntaxError:
        return None


def relpath(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def module_path_from_file(path: Path, repo_root: Path) -> str:
    relative = relpath(path, repo_root)
    if relative.endswith(".py"):
        relative = relative[:-3]
    return relative.replace("/", ".").replace("\\", ".")


def source_line_from_module(module_path: str) -> str:
    parts = module_path.split(".")
    if len(parts) >= 2 and parts[0] == "ashl_core_v1":
        return parts[1]
    return "repo"


def iter_project_files(repo_root: str | Path, suffixes: tuple[str, ...]) -> tuple[Path, ...]:
    root = Path(repo_root)
    ignored_parts = {".git", "__pycache__", ".uv-cache", ".uv-python"}
    paths: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in ignored_parts for part in path.parts):
            continue
        if path.suffix.lower() in suffixes:
            paths.append(path)
    return tuple(sorted(paths, key=lambda item: item.as_posix()))


def iter_python_files(repo_root: str | Path) -> tuple[Path, ...]:
    return iter_project_files(repo_root, (".py",))


def iter_document_files(repo_root: str | Path) -> tuple[Path, ...]:
    return iter_project_files(repo_root, (".md", ".txt", ".rst"))


def parse_sqlite_tables(text: str) -> tuple[str, ...]:
    tables = {
        match.group(1)
        for match in re.finditer(
            r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([A-Za-z_][A-Za-z0-9_]*)",
            text,
            flags=re.IGNORECASE,
        )
    }
    return tuple(sorted(tables))


def parse_argparse_commands(text: str) -> tuple[str, ...]:
    commands = {
        match.group(1)
        for match in re.finditer(r"\.add_parser\(\s*[\"']([^\"']+)[\"']", text)
    }
    return tuple(sorted(commands))


def get_git_commit_without_subprocess(repo_root: str | Path) -> str | None:
    root = Path(repo_root)
    git_dir = root / ".git"
    if not git_dir.exists():
        return None
    try:
        head = read_text(git_dir / "HEAD").strip()
        if head.startswith("ref:"):
            ref_path = git_dir / head.split(":", 1)[1].strip().replace("/", "\\")
            if ref_path.exists():
                return read_text(ref_path).strip()[:7]
            packed_refs = git_dir / "packed-refs"
            if packed_refs.exists():
                ref_name = head.split(":", 1)[1].strip()
                for line in read_text(packed_refs).splitlines():
                    if line and not line.startswith("#") and line.endswith(ref_name):
                        return line.split()[0][:7]
            return None
        return head[:7] if head else None
    except OSError:
        return None


@dataclass(frozen=True)
class ArchitectureRepoScanBaselineRecord:
    scan_id: str
    schema_version: str
    created_at: str
    repo_root: str
    scanned_commit: str | None
    python_file_count: int
    runtime_module_count: int
    perception_module_count: int
    test_file_count: int
    document_file_count: int
    dataclass_count: int
    enum_count: int
    validator_count: int
    cli_command_count: int
    sqlite_table_count: int
    scan_config_sha256: str
    scan_result_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return plain(self)


def _count_ast_items(python_files: Iterable[Path]) -> tuple[int, int, int, int, int]:
    dataclass_count = 0
    enum_count = 0
    validator_count = 0
    cli_command_count = 0
    sqlite_tables: set[str] = set()
    for path in python_files:
        text = read_text(path)
        cli_command_count += len(parse_argparse_commands(text))
        sqlite_tables.update(parse_sqlite_tables(text))
        tree = safe_parse_python(path)
        if tree is None:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                decorator_names = {_node_name(item) for item in node.decorator_list}
                base_names = {_node_name(item) for item in node.bases}
                if "dataclass" in decorator_names:
                    dataclass_count += 1
                if "Enum" in base_names:
                    enum_count += 1
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if "validate" in node.name:
                    validator_count += 1
    return dataclass_count, enum_count, validator_count, cli_command_count, len(sqlite_tables)


def _node_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Call):
        return _node_name(node.func)
    if isinstance(node, ast.Subscript):
        return _node_name(node.value)
    return ""


def scan_repo_baseline(repo_root: str | Path) -> ArchitectureRepoScanBaselineRecord:
    root = Path(repo_root).resolve()
    python_files = iter_python_files(root)
    document_files = iter_document_files(root)
    dataclass_count, enum_count, validator_count, cli_command_count, sqlite_table_count = _count_ast_items(python_files)
    runtime_modules = [
        path for path in python_files if relpath(path, root).startswith("ashl_core_v1/runtime/")
    ]
    perception_modules = [
        path for path in python_files if relpath(path, root).startswith("ashl_core_v1/perception/")
    ]
    test_files = [
        path
        for path in python_files
        if "/tests/" in relpath(path, root) or relpath(path, root).startswith("tests/")
    ]
    scan_config = {
        "scanner": "architecture_repo_scanner_v0",
        "repo_root": root.as_posix(),
        "included_suffixes": (".py", ".md", ".txt", ".rst"),
    }
    result_without_hash = {
        "repo_root": root.as_posix(),
        "python_file_count": len(python_files),
        "runtime_module_count": len(runtime_modules),
        "perception_module_count": len(perception_modules),
        "test_file_count": len(test_files),
        "document_file_count": len(document_files),
        "dataclass_count": dataclass_count,
        "enum_count": enum_count,
        "validator_count": validator_count,
        "cli_command_count": cli_command_count,
        "sqlite_table_count": sqlite_table_count,
    }
    return ArchitectureRepoScanBaselineRecord(
        scan_id=stable_id("architecture_repo_scan", result_without_hash),
        schema_version=BASELINE_SCHEMA_VERSION,
        created_at=utc_now(),
        repo_root=root.as_posix(),
        scanned_commit=get_git_commit_without_subprocess(root),
        python_file_count=len(python_files),
        runtime_module_count=len(runtime_modules),
        perception_module_count=len(perception_modules),
        test_file_count=len(test_files),
        document_file_count=len(document_files),
        dataclass_count=dataclass_count,
        enum_count=enum_count,
        validator_count=validator_count,
        cli_command_count=cli_command_count,
        sqlite_table_count=sqlite_table_count,
        scan_config_sha256=sha256_payload(scan_config),
        scan_result_sha256=sha256_payload(result_without_hash),
    )


def run_architecture_scan(repo_root: str | Path) -> dict[str, Any]:
    """Run the full Package 122A scan and return machine-readable records."""
    from ashl_core_v1.tools.architecture_gap_analyzer import analyze_architecture_gaps
    from ashl_core_v1.tools.architecture_interface_graph import build_interface_connections
    from ashl_core_v1.tools.architecture_module_classifier import classify_runtime_modules
    from ashl_core_v1.tools.architecture_operational_surface_inventory import build_operational_surface_inventory
    from ashl_core_v1.tools.architecture_roadmap_reconciler import reconcile_roadmap
    from ashl_core_v1.tools.architecture_store_inventory import build_store_surface_inventory
    from ashl_core_v1.tools.architecture_test_mapper import build_test_coverage_map

    root = Path(repo_root).resolve()
    baseline = scan_repo_baseline(root)
    tests = build_test_coverage_map(root)
    stores = build_store_surface_inventory(root)
    surfaces = build_operational_surface_inventory(root)
    modules = classify_runtime_modules(root, test_records=tests, store_records=stores, surface_records=surfaces)
    interfaces = build_interface_connections(root, module_records=modules, test_records=tests)
    roadmap = reconcile_roadmap(root)
    analysis = analyze_architecture_gaps(
        repo_root=root,
        baseline=baseline,
        module_records=modules,
        interface_records=interfaces,
        store_records=stores,
        surface_records=surfaces,
        test_records=tests,
        roadmap_records=roadmap,
    )
    scan = {
        "schema_version": SCAN_RESULT_SCHEMA_VERSION,
        "created_at": utc_now(),
        "baseline": baseline.to_dict(),
        "modules": [record.to_dict() for record in modules],
        "interfaces": [record.to_dict() for record in interfaces],
        "stores": [record.to_dict() for record in stores],
        "operational_surfaces": [record.to_dict() for record in surfaces],
        "tests": [record.to_dict() for record in tests],
        "roadmap": roadmap,
        "analysis": analysis,
    }
    scan["scan_sha256"] = sha256_payload({key: value for key, value in scan.items() if key != "scan_sha256"})
    return scan


def write_scan_result(scan: dict[str, Any], output_dir: str | Path) -> Path:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    result_path = output / "architecture_scan_result_v0.json"
    result_path.write_text(canonical_json(scan) + "\n", encoding="utf-8")
    baseline_path = output / "architecture_scan_baseline_v0.json"
    baseline_path.write_text(canonical_json(scan["baseline"]) + "\n", encoding="utf-8")
    return result_path


def load_scan_result(scan_dir: str | Path) -> dict[str, Any]:
    scan_path = Path(scan_dir) / "architecture_scan_result_v0.json"
    if not scan_path.exists():
        baseline_path = Path(scan_dir) / "architecture_scan_baseline_v0.json"
        if baseline_path.exists():
            return {"baseline": json.loads(read_text(baseline_path))}
        raise FileNotFoundError(f"missing architecture scan result: {scan_path}")
    return json.loads(read_text(scan_path))
