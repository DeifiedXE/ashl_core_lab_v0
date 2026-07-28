"""Contextual reset, fork, overwrite, and lifecycle authority scan."""

from __future__ import annotations

import ast

from ashl_core_v1.migration_audit.d_laplace_qm0_types import (
    DLaplaceModuleInventoryRecord,
    MigrationContaminationFinding,
    sha256_payload,
    stable_id,
)
from ashl_core_v1.migration_audit.d_laplace_source_reader import (
    ReadOnlyDLaplaceSource,
)


def _node_calls(node: ast.AST) -> tuple[str, ...]:
    result: list[str] = []
    for item in ast.walk(node):
        if not isinstance(item, ast.Call):
            continue
        value: ast.AST = item.func
        parts: list[str] = []
        while isinstance(value, ast.Attribute):
            parts.append(value.attr)
            value = value.value
        if isinstance(value, ast.Name):
            parts.append(value.id)
        result.append(".".join(reversed(parts)))
    return tuple(result)


def _finding(
    *,
    module: DLaplaceModuleInventoryRecord,
    node: ast.AST,
    source_text: str,
    category: str,
    severity: str,
    migration_effect: str,
    explanation: str,
) -> MigrationContaminationFinding:
    excerpt = ast.get_source_segment(source_text, node) or ast.dump(node)
    line_range = (
        f"L{getattr(node, 'lineno', 0)}-"
        f"L{getattr(node, 'end_lineno', getattr(node, 'lineno', 0))}"
    )
    payload = {
        "path": module.relative_path,
        "symbol": getattr(node, "name", None),
        "category": category,
        "line_range": line_range,
        "excerpt_hash": sha256_payload(excerpt),
    }
    return MigrationContaminationFinding(
        finding_id=stable_id("d_laplace_contamination_finding", payload),
        category=category,
        severity=severity,
        relative_path=module.relative_path,
        symbol_name=getattr(node, "name", None),
        line_range=line_range,
        evidence_excerpt_hash=sha256_payload(excerpt),
        finding_status="confirmed_dataflow_or_authority_finding",
        migration_effect=migration_effect,
        explanation=explanation,
        source_trace_refs=(module.module_record_id,),
    )


def scan_state_authority(
    source: ReadOnlyDLaplaceSource,
    modules: tuple[DLaplaceModuleInventoryRecord, ...],
) -> tuple[MigrationContaminationFinding, ...]:
    findings: list[MigrationContaminationFinding] = []
    for module in modules:
        if module.evidence_status != "source_code_ast_parsed":
            continue
        source_text = source.read_text(module.relative_path)
        tree = ast.parse(source_text, filename=module.relative_path)
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            name = node.name.casefold()
            calls = _node_calls(node)
            mutates_files = any(
                call.endswith(
                    (
                        "copy",
                        "copy2",
                        "move",
                        "replace",
                        "unlink",
                        "rmtree",
                        "write_text",
                        "write_bytes",
                    )
                )
                for call in calls
            )
            if "fork" in name:
                findings.append(
                    _finding(
                        module=module,
                        node=node,
                        source_text=source_text,
                        category="fork_authority",
                        severity="blocking_for_qm1",
                        migration_effect="forbidden_for_qingyin",
                        explanation="Function declaration exposes individual or state fork authority.",
                    )
                )
            if "reset" in name:
                findings.append(
                    _finding(
                        module=module,
                        node=node,
                        source_text=source_text,
                        category="reset_authority",
                        severity="blocking_for_qm1",
                        migration_effect=(
                            "research_harness_only_and_isolated"
                            if "/tests/" in f"/{module.relative_path.casefold()}/"
                            else "forbidden_for_qingyin"
                        ),
                        explanation="Function declaration exposes reset authority.",
                    )
                )
            if any(term in name for term in ("rollback", "restore")):
                category = (
                    "history_overwrite_authority"
                    if mutates_files
                    else "absolute_mutation_authority"
                )
                findings.append(
                    _finding(
                        module=module,
                        node=node,
                        source_text=source_text,
                        category=category,
                        severity="blocking_for_qm1",
                        migration_effect="forbidden_for_qingyin",
                        explanation=(
                            "Rollback or restore authority is present; append-only preservation "
                            "of the attempted history is not demonstrated."
                        ),
                    )
                )
            if any(
                term in name
                for term in (
                    "prune",
                    "replace",
                    "merge",
                    "split",
                    "rewire",
                    "lesion",
                    "regener",
                    "birth",
                    "sleep",
                    "wake",
                )
            ):
                findings.append(
                    _finding(
                        module=module,
                        node=node,
                        source_text=source_text,
                        category="absolute_mutation_authority",
                        severity="blocking_for_direct_migration",
                        migration_effect="reusable_only_after_authority_removal",
                        explanation=(
                            "Organ lifecycle mutation authority is executable in source and "
                            "requires a future Qingyin permission and continuity layer."
                        ),
                    )
                )
    unique = {finding.finding_id: finding for finding in findings}
    return tuple(sorted(unique.values(), key=lambda item: item.finding_id))
