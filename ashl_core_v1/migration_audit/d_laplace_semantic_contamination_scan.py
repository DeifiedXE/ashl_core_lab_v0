"""AST-backed synthetic semantics, teacher, family, and analysis-tag scan."""

from __future__ import annotations

import ast
from pathlib import PurePosixPath

from ashl_core_v1.migration_audit.d_laplace_qm0_types import (
    DLaplaceModuleInventoryRecord,
    MigrationContaminationFinding,
    sha256_payload,
    stable_id,
)
from ashl_core_v1.migration_audit.d_laplace_source_reader import (
    ReadOnlyDLaplaceSource,
)


SENSITIVE_RUNTIME_TERMS = (
    "propos",
    "candidate",
    "select",
    "cost",
    "mutat",
    "regen",
    "arbit",
    "credit",
    "prune",
    "replace",
    "birth",
)


def _tokens(node: ast.AST) -> set[str]:
    result: set[str] = set()
    for item in ast.walk(node):
        if isinstance(item, ast.Name):
            result.add(item.id.casefold())
        elif isinstance(item, ast.Attribute):
            result.add(item.attr.casefold())
        elif isinstance(item, ast.Constant) and isinstance(item.value, str):
            result.add(item.value.casefold())
    return result


def _call_names(node: ast.AST) -> tuple[str, ...]:
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
        result.append(".".join(reversed(parts)).casefold())
    return tuple(result)


def _assignment_names(node: ast.Assign | ast.AnnAssign) -> tuple[str, ...]:
    targets = node.targets if isinstance(node, ast.Assign) else [node.target]
    result: list[str] = []
    for target in targets:
        for item in ast.walk(target):
            if isinstance(item, ast.Name):
                result.append(item.id.casefold())
            elif isinstance(item, ast.Attribute):
                result.append(item.attr.casefold())
    return tuple(result)


def _finding(
    *,
    module: DLaplaceModuleInventoryRecord,
    node: ast.AST,
    source_text: str,
    category: str,
    severity: str,
    status: str,
    migration_effect: str,
    explanation: str,
    symbol_name: str | None = None,
) -> MigrationContaminationFinding:
    excerpt = ast.get_source_segment(source_text, node) or ast.dump(node)
    line_range = (
        f"L{getattr(node, 'lineno', 0)}-"
        f"L{getattr(node, 'end_lineno', getattr(node, 'lineno', 0))}"
    )
    payload = {
        "path": module.relative_path,
        "symbol": symbol_name,
        "category": category,
        "line_range": line_range,
        "excerpt_hash": sha256_payload(excerpt),
    }
    return MigrationContaminationFinding(
        finding_id=stable_id("d_laplace_contamination_finding", payload),
        category=category,
        severity=severity,
        relative_path=module.relative_path,
        symbol_name=symbol_name,
        line_range=line_range,
        evidence_excerpt_hash=sha256_payload(excerpt),
        finding_status=status,
        migration_effect=migration_effect,
        explanation=explanation,
        source_trace_refs=(module.module_record_id,),
    )


def scan_semantic_contamination(
    source: ReadOnlyDLaplaceSource,
    modules: tuple[DLaplaceModuleInventoryRecord, ...],
) -> tuple[MigrationContaminationFinding, ...]:
    findings: list[MigrationContaminationFinding] = []
    for module in modules:
        if module.evidence_status != "source_code_ast_parsed":
            continue
        source_text = source.read_text(module.relative_path)
        tree = ast.parse(source_text, filename=module.relative_path)
        path_name = PurePosixPath(module.relative_path).name.casefold()
        if path_name.startswith(("syn_", "synthetic", "iteration1", "iteration2")):
            findings.append(
                _finding(
                    module=module,
                    node=tree,
                    source_text=source_text,
                    category="synthetic_world_semantics",
                    severity="blocking_for_direct_migration",
                    status="confirmed_dataflow_or_authority_finding",
                    migration_effect="synthetic_adapter_not_portable_core",
                    explanation=(
                        "Module path and AST contain experiment-world construction "
                        "or synthetic run orchestration."
                    ),
                )
            )
        for node in ast.walk(tree):
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                names = _assignment_names(node)
                value = node.value
                if (
                    any(
                        "score" in name
                        or "affinity" in name
                        or "reward" in name
                        for name in names
                    )
                    and isinstance(value, (ast.Dict, ast.List, ast.Tuple))
                ):
                    findings.append(
                        _finding(
                            module=module,
                            node=node,
                            source_text=source_text,
                            category="synthetic_task_score_semantics",
                            severity="blocking_for_direct_migration",
                            status="confirmed_dataflow_or_authority_finding",
                            migration_effect="synthetic_score_adapter_forbidden",
                            explanation=(
                                "A fixed mapping is bound to score, reward, or affinity "
                                "state and cannot be treated as generic Cost arithmetic."
                            ),
                        )
                    )
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            name = node.name.casefold()
            tokens = _tokens(node)
            calls = _call_names(node)
            sensitive = any(term in name for term in SENSITIVE_RUNTIME_TERMS)
            if sensitive and "family" in tokens and not any(
                term in name
                for term in ("audit", "report", "non_interference", "offline_analysis")
            ):
                findings.append(
                    _finding(
                        module=module,
                        node=node,
                        source_text=source_text,
                        category="family_semantic_leakage",
                        severity="blocking_for_direct_migration",
                        status="confirmed_dataflow_or_authority_finding",
                        migration_effect="semantic_extraction_required",
                        explanation=(
                            "Family data is consumed by a proposer, selector, Cost, "
                            "mutation, regeneration, or lifecycle-sensitive function."
                        ),
                        symbol_name=node.name,
                    )
                )
            if "teacher" in name:
                direct_creation = any(
                    any(
                        token in call
                        for token in (
                            "organ",
                            "candidate",
                            "propos",
                            "registry.add",
                            "append",
                        )
                    )
                    for call in calls
                ) or bool(
                    {"organ", "organs", "candidate", "candidates"} & tokens
                )
                if direct_creation:
                    findings.append(
                        _finding(
                            module=module,
                            node=node,
                            source_text=source_text,
                            category="teacher_rule_leakage",
                            severity="blocking_for_direct_migration",
                            status="confirmed_dataflow_or_authority_finding",
                            migration_effect="teacher_rule_isolation_required",
                            explanation=(
                                "Teacher-labelled flow reaches candidate or organ-bearing "
                                "state; direct Qingyin migration is blocked."
                            ),
                            symbol_name=node.name,
                        )
                    )
            if "graph_for_family" in name or (
                "family" in name
                and any(token in tokens for token in ("node", "nodes", "organ"))
            ):
                findings.append(
                    _finding(
                        module=module,
                        node=node,
                        source_text=source_text,
                        category="direct_organ_template",
                        severity="blocking_for_qm1",
                        status="confirmed_dataflow_or_authority_finding",
                        migration_effect="forbidden_direct_migration",
                        explanation=(
                            "Function constructs organ structure from a human family "
                            "identifier and therefore acts as a direct template."
                        ),
                        symbol_name=node.name,
                    )
                )
                findings.append(
                    _finding(
                        module=module,
                        node=node,
                        source_text=source_text,
                        category="primitive_answer_leakage",
                        severity="blocking_for_qm1",
                        status="confirmed_dataflow_or_authority_finding",
                        migration_effect="novelty_claim_downgraded",
                        explanation=(
                            "Family-to-graph construction can pre-authorize the claimed "
                            "high-level capability."
                        ),
                        symbol_name=node.name,
                    )
                )
            if "analysis_non_interference_proof" in name:
                findings.append(
                    _finding(
                        module=module,
                        node=node,
                        source_text=source_text,
                        category="human_analysis_tag_runtime_leakage",
                        severity="informational",
                        status="bounded_counter_evidence",
                        migration_effect="supporting_analysis_only_one_way_isolation_candidate",
                        explanation=(
                            "Source computes selector, Cost, and regeneration digests with "
                            "and without offline tags; test evidence is still required."
                        ),
                        symbol_name=node.name,
                    )
                )
            if sensitive and (
                "analysis_tag" in tokens or "analysis_tags" in tokens
            ) and "non_interference" not in name:
                findings.append(
                    _finding(
                        module=module,
                        node=node,
                        source_text=source_text,
                        category="human_analysis_tag_runtime_leakage",
                        severity="blocking_for_direct_migration",
                        status="confirmed_dataflow_or_authority_finding",
                        migration_effect="reverse_flow_must_be_removed",
                        explanation=(
                            "Human analysis tags are consumed by a runtime-sensitive "
                            "function, creating a forbidden reverse edge."
                        ),
                        symbol_name=node.name,
                    )
                )
    unique = {finding.finding_id: finding for finding in findings}
    return tuple(sorted(unique.values(), key=lambda item: item.finding_id))
