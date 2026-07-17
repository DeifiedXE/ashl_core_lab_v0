"""Runtime module capability classifier for Package 122A."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ashl_core_v1.tools.architecture_repo_scanner import (
    iter_python_files,
    module_path_from_file,
    plain,
    read_text,
    relpath,
    safe_parse_python,
    sha256_text,
    stable_id,
)


MODULE_CAPABILITY_SCHEMA_VERSION = "ashl_runtime_module_capability_v0"


ROLE_KEYWORDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("session_runtime", ("session", "runtime", "bounded_embodied", "multimodal_perception_session")),
    ("trace_spine", ("trace", "envelope", "spine")),
    ("teacher_review", ("teacher", "review", "pending")),
    ("learning_pipeline", ("learning", "concept_candidate", "reviewed_concept")),
    ("memory_commit", ("memory", "commit", "reviewed_interpretation")),
    ("working_readback", ("readback", "working")),
    ("sensor_ingress", ("sensor", "camera", "screen", "microphone", "host_state")),
    ("raw_artifact_store", ("artifact_store", "content_addressed_sensor_artifact_store")),
    ("ephemeral_audio", ("ephemeral_audio", "audio_artifact_deletion", "evidence_audio_excerpt")),
    ("perception_compiler", ("perception", "compiler", "primitive")),
    ("multimodal_timeline", ("multimodal", "timeline", "alignment_window", "perception_lane")),
    ("perception_to_host_body_bridge", ("perception_to_host_body", "host_body_event_bridge")),
    ("internal_action", ("internal_action", "candidate", "choice")),
    ("home_surface", ("home_surface", "qingyin_home")),
    ("state_continuity", ("state", "continuity", "persistence", "resume")),
    ("self_state", ("self_state", "persistent_self")),
    ("endocrine", ("endocrine",)),
    ("thought", ("thought",)),
    ("active_perception", ("attention", "focus", "recapture", "relisten")),
    ("verification", ("verification", "audit", "validate")),
    ("expression", ("output", "expression", "voice")),
    ("external_bridge", ("bridge", "sandbox", "external")),
    ("governance", ("governance", "policy", "deletion", "consent")),
    ("audit", ("audit", "milestone", "readiness")),
    ("test_harness", ("test_", "worker", "orchestrator")),
    ("documentation", ("docs", "document")),
)


@dataclass(frozen=True)
class RuntimeModuleCapabilityRecord:
    module_record_id: str
    schema_version: str
    module_path: str
    module_line: str
    module_role: tuple[str, ...]
    implementation_status: str
    public_classes: tuple[str, ...]
    public_functions: tuple[str, ...]
    schema_versions: tuple[str, ...]
    record_kinds: tuple[str, ...]
    imported_project_modules: tuple[str, ...]
    importing_project_modules: tuple[str, ...]
    runtime_callers: tuple[str, ...]
    downstream_consumers: tuple[str, ...]
    related_store_tables: tuple[str, ...]
    related_cli_commands: tuple[str, ...]
    related_test_files: tuple[str, ...]
    verified_by_tests: bool
    used_by_current_runtime: bool
    design_only: bool
    audit_only: bool
    capability_summary: str
    blocked_capabilities: tuple[str, ...]
    source_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return plain(self)


def _node_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Call):
        return _node_name(node.func)
    return ""


def _imported_project_modules(tree: ast.Module | None) -> tuple[str, ...]:
    if tree is None:
        return tuple()
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("ashl_core_v1."):
                    imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith("ashl_core_v1."):
                imports.add(node.module)
    return tuple(sorted(imports))


def _public_defs(tree: ast.Module | None) -> tuple[tuple[str, ...], tuple[str, ...]]:
    if tree is None:
        return tuple(), tuple()
    classes: list[str] = []
    functions: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
            classes.append(node.name)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_"):
            functions.append(node.name)
    return tuple(classes), tuple(functions)


def _schema_versions(text: str) -> tuple[str, ...]:
    return tuple(sorted(set(re.findall(r"ashl_[A-Za-z0-9_]+_v[0-9][A-Za-z0-9_]*", text))))


def _record_kinds(public_classes: tuple[str, ...], text: str) -> tuple[str, ...]:
    kinds = {name for name in public_classes if name.endswith("Record")}
    kinds.update(re.findall(r"record_kind\s*=\s*[\"']([^\"']+)[\"']", text))
    return tuple(sorted(kinds))


def _roles(module_path: str, text: str) -> tuple[str, ...]:
    haystack = f"{module_path} {text[:2000]}".lower()
    roles = []
    for role, keywords in ROLE_KEYWORDS:
        if any(keyword in haystack for keyword in keywords):
            roles.append(role)
    return tuple(sorted(set(roles or ["unknown"])))


def _implementation_status(module_path: str, text: str, classes: tuple[str, ...], functions: tuple[str, ...]) -> str:
    path_lower = module_path.lower()
    text_lower = text.lower()
    if module_path.startswith("ashl_core_v1.tests."):
        return "actual_test_harness"
    if path_lower.endswith("_cli"):
        return "actual_cli"
    dataclass_only = bool(classes) and not functions and "runtime" not in path_lower
    if dataclass_only or path_lower.endswith("_types") or path_lower.endswith("_schema"):
        return "schema_only"
    explicit_store_module = path_lower.endswith("_store") or "artifact_store" in path_lower or "primitive_store" in path_lower
    if ("runtime" in path_lower or path_lower.endswith("_run") or path_lower.endswith("_worker")) and not explicit_store_module:
        return "actual_runtime"
    if "sqlite3" in text_lower or "create table" in text_lower or explicit_store_module:
        return "actual_store"
    if "compiler" in path_lower:
        return "actual_compiler"
    if "adapter" in path_lower or "bridge" in path_lower:
        return "actual_adapter"
    if "audit" in path_lower or "milestone" in path_lower:
        return "audit_only"
    if functions and all(("validate" in function or function.startswith("assert_")) for function in functions):
        return "validator_only"
    if "ashl_core_v1.runtime." in module_path or "ashl_core_v1.perception." in module_path:
        return "actual_runtime"
    return "unknown_needs_review"


def classify_runtime_modules(
    repo_root: str | Path,
    *,
    test_records: tuple[Any, ...] = tuple(),
    store_records: tuple[Any, ...] = tuple(),
    surface_records: tuple[Any, ...] = tuple(),
) -> tuple[RuntimeModuleCapabilityRecord, ...]:
    root = Path(repo_root).resolve()
    project_files = [
        path
        for path in iter_python_files(root)
        if relpath(path, root).startswith("ashl_core_v1/")
    ]
    module_imports: dict[str, tuple[str, ...]] = {}
    parsed: dict[str, tuple[Path, str, ast.Module | None]] = {}
    for path in project_files:
        module_path = module_path_from_file(path, root)
        text = read_text(path)
        tree = safe_parse_python(path)
        module_imports[module_path] = _imported_project_modules(tree)
        parsed[module_path] = (path, text, tree)

    reverse_imports: dict[str, list[str]] = {module_path: [] for module_path in parsed}
    for source_module, imported_modules in module_imports.items():
        for imported_module in imported_modules:
            for target_module in parsed:
                if target_module == imported_module or target_module.startswith(imported_module + "."):
                    reverse_imports.setdefault(target_module, []).append(source_module)

    test_map: dict[str, tuple[str, ...]] = {}
    for record in test_records:
        module_path = getattr(record, "module_path", "")
        files = tuple(getattr(record, "direct_test_files", tuple())) + tuple(getattr(record, "integration_test_files", tuple()))
        if files:
            test_map[module_path] = tuple(sorted(set(files)))

    store_table_map: dict[str, tuple[str, ...]] = {}
    for record in store_records:
        store_table_map[getattr(record, "store_module", "")] = tuple(getattr(record, "table_names", tuple()))

    cli_map: dict[str, list[str]] = {}
    for record in surface_records:
        module = getattr(record, "module_path", "")
        cli_map.setdefault(module, []).append(getattr(record, "command_name", ""))

    records: list[RuntimeModuleCapabilityRecord] = []
    for module_path, (path, text, tree) in sorted(parsed.items()):
        public_classes, public_functions = _public_defs(tree)
        imported = module_imports.get(module_path, tuple())
        importing = tuple(sorted(set(reverse_imports.get(module_path, []))))
        status = _implementation_status(module_path, text, public_classes, public_functions)
        related_tests = tuple(sorted(set(test_map.get(module_path, tuple()))))
        related_tables = tuple(sorted(set(store_table_map.get(module_path, tuple()))))
        related_commands = tuple(sorted(set(cli_map.get(module_path, []))))
        roles = _roles(module_path, text)
        verified = bool(related_tests)
        used_by_runtime = (
            status in {"actual_runtime", "actual_store", "actual_compiler", "actual_adapter"}
            or any(".runtime." in module or ".perception." in module for module in importing)
        )
        blocked: list[str] = []
        if not verified and status not in {"schema_only", "actual_cli", "actual_test_harness"}:
            blocked.append("missing_direct_or_integration_test_mapping")
        if status == "schema_only":
            blocked.append("runtime_behavior_not_established_by_schema")
        if "thought" in roles and status != "actual_runtime":
            blocked.append("thought_runtime_not_implemented")
        summary = f"{module_path} classified as {status} with roles {', '.join(roles)}."
        payload = {
            "module_path": module_path,
            "source_sha256": sha256_text(text),
            "status": status,
            "roles": roles,
        }
        records.append(
            RuntimeModuleCapabilityRecord(
                module_record_id=stable_id("runtime_module_capability", payload),
                schema_version=MODULE_CAPABILITY_SCHEMA_VERSION,
                module_path=module_path,
                module_line=module_path.split(".")[1] if module_path.startswith("ashl_core_v1.") else "repo",
                module_role=roles,
                implementation_status=status,
                public_classes=public_classes,
                public_functions=public_functions,
                schema_versions=_schema_versions(text),
                record_kinds=_record_kinds(public_classes, text),
                imported_project_modules=imported,
                importing_project_modules=importing,
                runtime_callers=tuple(sorted(module for module in importing if ".runtime." in module)),
                downstream_consumers=importing,
                related_store_tables=related_tables,
                related_cli_commands=related_commands,
                related_test_files=related_tests,
                verified_by_tests=verified,
                used_by_current_runtime=used_by_runtime,
                design_only=False,
                audit_only=status == "audit_only",
                capability_summary=summary,
                blocked_capabilities=tuple(blocked),
                source_sha256=sha256_text(text),
            )
        )
    return tuple(records)
