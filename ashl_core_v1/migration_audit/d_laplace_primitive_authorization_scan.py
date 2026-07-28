"""Static primitive/interface authorization audit with unresolved preservation."""

from __future__ import annotations

import ast

from ashl_core_v1.migration_audit.d_laplace_qm0_types import (
    DLaplaceModuleInventoryRecord,
    PrimitiveAuthorizationFinding,
    stable_id,
)
from ashl_core_v1.migration_audit.d_laplace_source_reader import (
    ReadOnlyDLaplaceSource,
)


HIGH_LEVEL_TERMS = {
    "ACTION_BID",
    "ANOMALY",
    "CLASSIFY",
    "DETECT",
    "FRAME_DIFF",
    "OBJECT",
    "SEMANTIC",
    "SMOOTH",
    "SOLUTION",
    "SPEECH",
}


def _target_names(node: ast.Assign | ast.AnnAssign) -> tuple[str, ...]:
    targets = node.targets if isinstance(node, ast.Assign) else [node.target]
    result: list[str] = []
    for target in targets:
        if isinstance(target, ast.Name):
            result.append(target.id)
        elif isinstance(target, ast.Attribute):
            result.append(target.attr)
    return tuple(result)


def _string_constants(node: ast.AST) -> tuple[str, ...]:
    return tuple(
        sorted(
            {
                item.value
                for item in ast.walk(node)
                if isinstance(item, ast.Constant)
                and isinstance(item.value, str)
                and item.value
            }
        )
    )


def audit_primitive_authorization(
    source: ReadOnlyDLaplaceSource,
    modules: tuple[DLaplaceModuleInventoryRecord, ...],
    *,
    authoritative_document_refs: tuple[str, ...],
) -> tuple[PrimitiveAuthorizationFinding, ...]:
    allowed: dict[str, set[str]] = {}
    forbidden: dict[str, set[str]] = {}
    direct_templates: list[tuple[str, str]] = []
    interface_refs: dict[str, set[str]] = {"ACTION_BID": set(), "ABSTAIN": set()}
    for module in modules:
        if module.evidence_status != "source_code_ast_parsed":
            continue
        source_text = source.read_text(module.relative_path)
        tree = ast.parse(source_text, filename=module.relative_path)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                names = _target_names(node)
                value = node.value
                for name in names:
                    folded = name.casefold()
                    if "primitive" not in folded:
                        continue
                    target = forbidden if "forbidden" in folded else allowed
                    for primitive in _string_constants(value):
                        target.setdefault(primitive, set()).add(module.module_record_id)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                folded = node.name.casefold()
                if "graph_for_family" in folded or "solution_template" in folded:
                    direct_templates.append((node.name, module.module_record_id))
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                if node.value in interface_refs:
                    interface_refs[node.value].add(module.module_record_id)
    findings: list[PrimitiveAuthorizationFinding] = []
    for primitive, refs in sorted(allowed.items()):
        suspicious = any(term in primitive.upper() for term in HIGH_LEVEL_TERMS)
        counter_refs = tuple(sorted(forbidden.get(primitive, set())))
        status = (
            "suspicious_high_level_authorization"
            if suspicious
            else "bounded_low_level_primitive"
        )
        findings.append(
            PrimitiveAuthorizationFinding(
                primitive_finding_id=stable_id(
                    "d_laplace_primitive_finding",
                    {"primitive": primitive, "status": status},
                ),
                primitive_or_interface_id=primitive,
                declared_capability="declared_primitive",
                reachable_high_level_behavior=(
                    ("organ_candidate_behavior",) if suspicious else ()
                ),
                authorization_source="source_code_primitive_manifest",
                authorization_depth_status=status,
                supporting_evidence_refs=tuple(sorted(refs)),
                counter_evidence_refs=counter_refs,
                claim_effect=(
                    "novelty_claim_downgraded_due_to_suspicious_primitive"
                    if suspicious
                    else "bounded_static_evidence_only"
                ),
                source_trace_refs=tuple(sorted(refs | forbidden.get(primitive, set()))),
            )
        )
    for interface, refs in sorted(interface_refs.items()):
        if not refs:
            continue
        findings.append(
            PrimitiveAuthorizationFinding(
                primitive_finding_id=stable_id(
                    "d_laplace_primitive_finding",
                    {"interface": interface, "status": "suspicious"},
                ),
                primitive_or_interface_id=interface,
                declared_capability="active_action_interface",
                reachable_high_level_behavior=("action_arbitration",),
                authorization_source="source_code_interface_literal",
                authorization_depth_status="suspicious_high_level_authorization",
                supporting_evidence_refs=tuple(sorted(refs)),
                counter_evidence_refs=(),
                claim_effect="novelty_claim_downgraded_due_to_unresolved_primitive_authorization",
                source_trace_refs=tuple(sorted(refs)),
            )
        )
    for symbol, module_ref in sorted(direct_templates):
        findings.append(
            PrimitiveAuthorizationFinding(
                primitive_finding_id=stable_id(
                    "d_laplace_primitive_finding",
                    {"direct_template": symbol, "module": module_ref},
                ),
                primitive_or_interface_id=symbol,
                declared_capability="family_to_organ_graph_construction",
                reachable_high_level_behavior=("direct_solution_template",),
                authorization_source="source_code_function",
                authorization_depth_status="direct_answer_template",
                supporting_evidence_refs=(module_ref,),
                counter_evidence_refs=(),
                claim_effect="blocking_direct_migration_and_novelty_claim_downgrade",
                source_trace_refs=(module_ref,),
            )
        )
    manifest_refs = tuple(
        sorted({ref for refs in allowed.values() for ref in refs})
    )
    if not manifest_refs:
        findings.append(
            PrimitiveAuthorizationFinding(
                primitive_finding_id=stable_id(
                    "d_laplace_primitive_finding",
                    {"primitive_manifest": "missing"},
                ),
                primitive_or_interface_id="primitive_manifest",
                declared_capability="unknown",
                reachable_high_level_behavior=(),
                authorization_source="source_scope_scan",
                authorization_depth_status="unresolved",
                supporting_evidence_refs=(),
                counter_evidence_refs=(),
                claim_effect="clean_primitive_authorization_claim_blocked",
                source_trace_refs=(),
            )
        )
    findings.append(
        PrimitiveAuthorizationFinding(
            primitive_finding_id=stable_id(
                "d_laplace_primitive_finding",
                {"authorization_depth": "unresolved"},
            ),
            primitive_or_interface_id="primitive_authorization_depth",
            declared_capability="D-Laplace organ novelty",
            reachable_high_level_behavior=("organ_formation", "active_action"),
            authorization_source="authoritative_closeout_documents",
            authorization_depth_status="unresolved",
            supporting_evidence_refs=tuple(authoritative_document_refs),
            counter_evidence_refs=manifest_refs,
            claim_effect="downgraded_due_to_unresolved_primitive_authorization",
            source_trace_refs=tuple(authoritative_document_refs),
        )
    )
    findings.append(
        PrimitiveAuthorizationFinding(
            primitive_finding_id=stable_id(
                "d_laplace_primitive_finding",
                {"reachability_experiment": "not_run_qm0"},
            ),
            primitive_or_interface_id="capability_to_primitive_dynamic_reachability",
            declared_capability="dynamic authorization depth experiment",
            reachable_high_level_behavior=(),
            authorization_source="qm0_read_only_scope",
            authorization_depth_status="not_run",
            supporting_evidence_refs=(),
            counter_evidence_refs=(),
            claim_effect="NOT_RUN_not_zero; authorization_depth_remains_unresolved",
            source_trace_refs=(),
        )
    )
    unique = {finding.primitive_finding_id: finding for finding in findings}
    return tuple(
        sorted(unique.values(), key=lambda item: item.primitive_finding_id)
    )
