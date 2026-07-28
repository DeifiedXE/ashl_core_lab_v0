"""Future ASHL substitution candidates without runtime modification."""

from __future__ import annotations

from ashl_core_v1.migration_audit.d_laplace_qm0_types import (
    ASHLSubstitutionCandidateRecord,
    DLaplaceMigrationCandidateRecord,
    stable_id,
)


def _candidate_refs(
    candidates: tuple[DLaplaceMigrationCandidateRecord, ...],
    mechanism_kind: str,
) -> tuple[str, ...]:
    return tuple(
        candidate.migration_candidate_id
        for candidate in candidates
        if candidate.mechanism_kind == mechanism_kind
    )


def _record(
    *,
    role: str,
    mechanism: str,
    scope: str,
    status: str,
    stage: str,
    preserve: tuple[str, ...],
    forbid: tuple[str, ...],
    tests: tuple[str, ...],
    candidates: tuple[DLaplaceMigrationCandidateRecord, ...],
) -> ASHLSubstitutionCandidateRecord:
    payload = {
        "role": role,
        "mechanism": mechanism,
        "scope": scope,
        "status": status,
    }
    return ASHLSubstitutionCandidateRecord(
        substitution_candidate_id=stable_id(
            "ashl_d_laplace_substitution_candidate",
            payload,
        ),
        ashl_module_or_future_role=role,
        d_laplace_mechanism_kind=mechanism,
        substitution_scope=scope,
        substitution_status=status,
        earliest_allowed_stage=stage,
        preserved_ashl_responsibilities=preserve,
        forbidden_replacements=forbid,
        required_future_tests=tests,
        source_trace_refs=_candidate_refs(candidates, mechanism),
    )


def build_ashl_substitution_map(
    candidates: tuple[DLaplaceMigrationCandidateRecord, ...],
) -> tuple[ASHLSubstitutionCandidateRecord, ...]:
    records = [
        _record(
            role="fixed_resource_budget_accounting",
            mechanism="active_cost_accounting",
            scope="resource arithmetic and bounded quota only",
            status="full_substitution_candidate",
            stage="DLM-1-after-Package-132",
            preserve=("approved purpose", "hard safety gates"),
            forbid=("performance_as_existence_value",),
            tests=("score_cost_separation", "quota_hard_bound"),
            candidates=candidates,
        ),
        _record(
            role="hand_maintained_generic_organ_registry",
            mechanism="anonymous_organ_registry",
            scope="anonymous identity and lineage bookkeeping",
            status="full_substitution_candidate",
            stage="DLM-1-after-Package-132",
            preserve=("individual identity continuity", "raw history"),
            forbid=("organ_template_import", "lineage_deletion"),
            tests=("anonymous_identity", "append_only_lineage"),
            candidates=candidates,
        ),
        _record(
            role="static_enable_disable_lifecycle_bookkeeping",
            mechanism="organ_lifecycle_protocol",
            scope="supervised sleep and wake bookkeeping only",
            status="full_substitution_candidate",
            stage="Q-M3-or-later",
            preserve=("human approval", "continuity constraints"),
            forbid=("automatic_birth", "automatic_death", "automatic_prune"),
            tests=("supervised_lifecycle_only", "rollback_history_preserved"),
            candidates=candidates,
        ),
        _record(
            role="generic_ecological_limit_accounting",
            mechanism="ecological_limit_snapshotting",
            scope="Cost ecology and append-only snapshot records",
            status="full_substitution_candidate",
            stage="DLM-1-after-Package-132",
            preserve=("sealed_thresholds", "raw_history"),
            forbid=("history_overwrite",),
            tests=("threshold_seal", "snapshot_append_only"),
            candidates=candidates,
        ),
        _record(
            role="fixed_Thought_layer_router",
            mechanism="ACTION_BID",
            scope="resource arbitration only",
            status="partial_substitution_candidate",
            stage="Q-M4-or-later",
            preserve=(
                "hypothesis_generation",
                "evidence_comparison",
                "prediction_construction",
                "safety_validation",
            ),
            forbid=("thought_generation_replacement", "external_action_authority"),
            tests=("abstain_available", "hard_safety_gate_precedence"),
            candidates=candidates,
        ),
        _record(
            role="direct_drive_to_action_score_wiring",
            mechanism="bid_cost_and_stake_limit",
            scope="bounded bid-context modulation",
            status="partial_substitution_candidate",
            stage="Q-M4-or-later",
            preserve=("endocrine_state_sources", "approved_purpose", "hard_safety_gates"),
            forbid=("drive_source_replacement", "permission_bypass"),
            tests=("stake_limit", "permission_gate_precedence"),
            candidates=candidates,
        ),
        _record(
            role="manually_created_specialty_anchors",
            mechanism="active_passive_organ_coexistence",
            scope="future low-Cost specialized passive organs",
            status="partial_substitution_candidate",
            stage="DLM-2-after-Package-132",
            preserve=("source_memory", "memory_admission", "teacher_review", "concept_truth"),
            forbid=("memory_truth_replacement",),
            tests=("shadow_only", "memory_boundary_preserved"),
            candidates=candidates,
        ),
        _record(
            role="fixed_perception_verification_candidate_ranking",
            mechanism="ACTION_BID",
            scope="future bid and abstain arbitration",
            status="partial_substitution_candidate",
            stage="Q-M4-or-later",
            preserve=(
                "source_perception",
                "temporal_evidence",
                "candidate_semantics",
                "external_permission_gates",
            ),
            forbid=("sensor_priority_selection", "semantic_source_replacement"),
            tests=("perception_provenance_preserved", "permission_gate_precedence"),
            candidates=candidates,
        ),
        _record(
            role="general_research_trust_audit_support",
            mechanism="self_audit_gate_framework",
            scope="supporting mechanism only",
            status="supporting_mechanism_only",
            stage="DLM-1-after-Package-132",
            preserve=(
                "Package_123_transport_integrity_audit",
                "Package_124_archive_integrity_audit",
                "Package_125_capture_session_identity_audit",
                "sensor_specific_audits",
                "teacher_identity_approval_checks",
                "raw_trace_integrity",
            ),
            forbid=("domain_audit_replacement",),
            tests=("domain_audits_remain_authoritative",),
            candidates=candidates,
        ),
    ]
    never_substitute = (
        "Package_120_sensor_ingress",
        "Package_121_perception_primitive_compiler",
        "Package_122_multimodal_runtime",
        "Package_124_archive",
        "Package_124A_temporal_foundation",
        "raw_append_only_history",
        "TraceEnvelope_authority",
        "teacher_review",
        "memory_admission",
        "Core_Memory",
        "individual_self_state",
        "identity_continuity",
        "relationship_continuity",
        "ethical_and_permission_gates",
        "Qingyin_Home",
        "output_provenance",
        "GCMC_truth_formation",
        "Package_125_capture_session_identity_audit",
    )
    for role in never_substitute:
        records.append(
            _record(
                role=role,
                mechanism="none",
                scope="ASHL responsibility remains authoritative",
                status="never_substitute",
                stage="never",
                preserve=(role,),
                forbid=("D_Laplace_replacement",),
                tests=("responsibility_remains_ASHL_authoritative",),
                candidates=candidates,
            )
        )
    return tuple(records)
