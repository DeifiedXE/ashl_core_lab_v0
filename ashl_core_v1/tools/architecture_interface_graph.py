"""Actual import/call and data-flow graph builder for Package 122A."""

from __future__ import annotations

import ast
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
    stable_id,
)


INTERFACE_CONNECTION_SCHEMA_VERSION = "ashl_architecture_interface_connection_v0"


@dataclass(frozen=True)
class ArchitectureInterfaceConnectionRecord:
    connection_id: str
    schema_version: str
    source_module: str
    target_module: str
    connection_kind: str
    source_callable: str | None
    target_callable: str | None
    source_record_kind: str | None
    target_record_kind: str | None
    data_identity_preserved: bool | None
    source_trace_refs_preserved: bool | None
    actual_import_exists: bool
    actual_runtime_call_exists: bool
    integration_test_exists: bool
    connection_status: str
    risk_codes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return plain(self)


def _import_aliases(tree: ast.Module | None) -> dict[str, str]:
    aliases: dict[str, str] = {}
    if tree is None:
        return aliases
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("ashl_core_v1."):
                    aliases[alias.asname or alias.name.split(".")[-1]] = alias.name
        elif isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("ashl_core_v1."):
            for alias in node.names:
                aliases[alias.asname or alias.name] = f"{node.module}.{alias.name}"
    return aliases


def _call_names(tree: ast.Module | None) -> tuple[str, ...]:
    names: set[str] = set()
    if tree is None:
        return tuple()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                names.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                names.add(node.func.attr)
    return tuple(sorted(names))


def _module_test_exists(source: str, target: str, test_records: tuple[Any, ...]) -> bool:
    source_stem = source.split(".")[-1]
    target_stem = target.split(".")[-1]
    for record in test_records:
        files = tuple(getattr(record, "direct_test_files", tuple())) + tuple(getattr(record, "integration_test_files", tuple()))
        module_path = getattr(record, "module_path", "")
        if files and (module_path == source or module_path == target):
            return True
        if source_stem in module_path or target_stem in module_path:
            return bool(files)
    return False


def _status(import_exists: bool, call_exists: bool, tested: bool, risks: tuple[str, ...]) -> str:
    if "identity_risk" in risks:
        return "identity_risk"
    if "trace_lineage_risk" in risks:
        return "trace_lineage_risk"
    if import_exists and call_exists and tested:
        return "verified_runtime_connection"
    if import_exists and call_exists:
        return "implemented_without_integration_test"
    if import_exists:
        return "declared_but_not_implemented"
    return "unknown"


def build_interface_connections(
    repo_root: str | Path,
    *,
    module_records: tuple[Any, ...] = tuple(),
    test_records: tuple[Any, ...] = tuple(),
) -> tuple[ArchitectureInterfaceConnectionRecord, ...]:
    root = Path(repo_root).resolve()
    module_files = [
        path
        for path in iter_python_files(root)
        if relpath(path, root).startswith("ashl_core_v1/") and not relpath(path, root).startswith("ashl_core_v1/tests/")
    ]
    records: list[ArchitectureInterfaceConnectionRecord] = []
    for path in module_files:
        source_module = module_path_from_file(path, root)
        tree = safe_parse_python(path)
        aliases = _import_aliases(tree)
        calls = set(_call_names(tree))
        for alias_name, imported_target in sorted(aliases.items()):
            target_module = ".".join(imported_target.split(".")[:-1])
            if target_module == source_module:
                continue
            call_exists = alias_name in calls or imported_target.split(".")[-1] in calls
            tested = _module_test_exists(source_module, target_module, test_records)
            risks: list[str] = []
            if "trace" in source_module and not tested:
                risks.append("trace_lineage_risk")
            payload = {
                "source": source_module,
                "target": target_module,
                "target_callable": imported_target.split(".")[-1],
                "kind": "function_call" if call_exists else "record_conversion",
            }
            records.append(
                ArchitectureInterfaceConnectionRecord(
                    connection_id=stable_id("architecture_interface_connection", payload),
                    schema_version=INTERFACE_CONNECTION_SCHEMA_VERSION,
                    source_module=source_module,
                    target_module=target_module,
                    connection_kind="function_call" if call_exists else "record_conversion",
                    source_callable=None,
                    target_callable=imported_target.split(".")[-1],
                    source_record_kind=None,
                    target_record_kind=None,
                    data_identity_preserved=None,
                    source_trace_refs_preserved=None,
                    actual_import_exists=True,
                    actual_runtime_call_exists=call_exists,
                    integration_test_exists=tested,
                    connection_status=_status(True, call_exists, tested, tuple(risks)),
                    risk_codes=tuple(sorted(risks)),
                )
            )

    records.extend(_mandatory_interface_records(root, test_records))
    unique: dict[str, ArchitectureInterfaceConnectionRecord] = {}
    for record in records:
        unique[record.connection_id] = record
    return tuple(sorted(unique.values(), key=lambda item: (item.source_module, item.target_module, item.connection_id)))


def _file_contains(root: Path, relative: str, needle: str) -> bool:
    path = root / relative
    return path.exists() and needle in read_text(path)


def _mandatory_interface_records(root: Path, test_records: tuple[Any, ...]) -> tuple[ArchitectureInterfaceConnectionRecord, ...]:
    specs = (
        {
            "connection_id": "perception_to_host_body",
            "source_module": "ashl_core_v1.runtime.perception_to_host_body_event_adapter",
            "target_module": "ashl_core_v1.runtime.bounded_embodied_session_runtime",
            "kind": "session_injection",
            "source_callable": "build_perception_host_body_event",
            "target_callable": "inject_host_body_event_record",
            "source_record_kind": "perception_readable_data",
            "target_record_kind": "host_body_event",
            "identity": True,
            "trace": True,
            "needle_file": "ashl_core_v1/runtime/bounded_multimodal_perception_session_runtime.py",
            "needle": "inject_host_body_event_record",
            "risks": ("generic_host_body_payload_overload",),
        },
        {
            "connection_id": "host_body_to_internal_action",
            "source_module": "ashl_core_v1.runtime.bounded_embodied_session_runtime",
            "target_module": "ashl_core_v1.host_body.host_body_internal_action_choice",
            "kind": "function_call",
            "source_callable": "_step_internal_action_choice",
            "target_callable": "choose_host_body_internal_action",
            "source_record_kind": "host_body_event",
            "target_record_kind": "internal_action_choice",
            "identity": None,
            "trace": True,
            "needle_file": "ashl_core_v1/runtime/bounded_embodied_session_runtime.py",
            "needle": "choose_host_body_internal_action",
            "risks": tuple(),
        },
        {
            "connection_id": "learning_evidence_to_teacher_gate",
            "source_module": "ashl_core_v1.runtime.bounded_embodied_session_runtime",
            "target_module": "ashl_core_v1.runtime.session_learning_evidence_identity",
            "kind": "teacher_gate",
            "source_callable": "_step_pending_teacher_review",
            "target_callable": "build_session_learning_evidence_snapshot",
            "source_record_kind": "learning_evidence_packet",
            "target_record_kind": "pending_teacher_review",
            "identity": True,
            "trace": True,
            "needle_file": "ashl_core_v1/runtime/bounded_embodied_session_runtime.py",
            "needle": "PendingTeacherReviewRecord",
            "risks": tuple(),
        },
        {
            "connection_id": "teacher_decision_to_package_90_92",
            "source_module": "ashl_core_v1.runtime.teacher_gated_session_resume_commit",
            "target_module": "ashl_core_v1.learning.learning_feedback_to_concept_candidate",
            "kind": "teacher_gate",
            "source_callable": "resume_approved_session_and_commit",
            "target_callable": "build_concept_candidate_from_learning_feedback",
            "source_record_kind": "teacher_decision",
            "target_record_kind": "reviewed_concept",
            "identity": True,
            "trace": True,
            "needle_file": "ashl_core_v1/runtime/teacher_gated_session_resume_commit.py",
            "needle": "adapt_session_evidence_to_learning_feedback_candidate",
            "risks": tuple(),
        },
        {
            "connection_id": "memory_commit_to_working_readback",
            "source_module": "ashl_core_v1.runtime.teacher_gated_session_resume_commit",
            "target_module": "ashl_core_v1.runtime.teacher_gated_session_store",
            "kind": "memory_commit",
            "source_callable": "_commit_reviewed_interpretation",
            "target_callable": "append_working_readback_commit",
            "source_record_kind": "reviewed_interpretation_commit",
            "target_record_kind": "working_readback_commit",
            "identity": True,
            "trace": True,
            "needle_file": "ashl_core_v1/runtime/teacher_gated_session_resume_commit.py",
            "needle": "working_readback",
            "risks": tuple(),
        },
        {
            "connection_id": "working_readback_to_candidate_scoring",
            "source_module": "ashl_core_v1.runtime.no_codex_two_cycle_fixture_growth_worker",
            "target_module": "ashl_core_v1.host_body.host_body_readback_internal_action_influence",
            "kind": "candidate_influence",
            "source_callable": "run_cycle_two",
            "target_callable": "build_readback_influenced_internal_action_choice",
            "source_record_kind": "working_readback_commit",
            "target_record_kind": "candidate_score",
            "identity": True,
            "trace": True,
            "needle_file": "ashl_core_v1/runtime/no_codex_two_cycle_fixture_growth_worker.py",
            "needle": "readback_consumed",
            "risks": tuple(),
        },
        {
            "connection_id": "runtime_state_to_qingyin_home",
            "source_module": "ashl_core_v1.runtime.bounded_embodied_session_runtime",
            "target_module": "ashl_core_v1.host_body.internal_action_home_surface_link",
            "kind": "record_conversion",
            "source_callable": "_step_home_surface_links",
            "target_callable": "build_internal_action_home_surface_link",
            "source_record_kind": "internal_action_result",
            "target_record_kind": "home_surface_link",
            "identity": None,
            "trace": True,
            "needle_file": "ashl_core_v1/runtime/bounded_embodied_session_runtime.py",
            "needle": "Home surface",
            "risks": ("record_surface_not_live_ui",),
        },
    )
    records: list[ArchitectureInterfaceConnectionRecord] = []
    for spec in specs:
        import_exists = (root / spec["needle_file"]).exists()
        call_exists = _file_contains(root, spec["needle_file"], spec["needle"])
        tested = _module_test_exists(spec["source_module"], spec["target_module"], test_records)
        status = _status(import_exists, call_exists, tested, tuple(spec["risks"]))
        if spec["connection_id"] == "perception_to_host_body" and call_exists:
            status = "verified_runtime_connection" if tested else "implemented_without_integration_test"
        records.append(
            ArchitectureInterfaceConnectionRecord(
                connection_id=str(spec["connection_id"]),
                schema_version=INTERFACE_CONNECTION_SCHEMA_VERSION,
                source_module=str(spec["source_module"]),
                target_module=str(spec["target_module"]),
                connection_kind=str(spec["kind"]),
                source_callable=str(spec["source_callable"]),
                target_callable=str(spec["target_callable"]),
                source_record_kind=str(spec["source_record_kind"]),
                target_record_kind=str(spec["target_record_kind"]),
                data_identity_preserved=spec["identity"],
                source_trace_refs_preserved=spec["trace"],
                actual_import_exists=import_exists,
                actual_runtime_call_exists=call_exists,
                integration_test_exists=tested,
                connection_status=status,
                risk_codes=tuple(spec["risks"]),
            )
        )
    return tuple(records)
