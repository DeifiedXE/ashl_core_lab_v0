"""Evidence-bounded D-Laplace mechanism portability classification."""

from __future__ import annotations

from dataclasses import dataclass

from ashl_core_v1.migration_audit.d_laplace_qm0_types import (
    DLaplaceMigrationCandidateRecord,
    DLaplaceModuleInventoryRecord,
    DLaplaceQM1AllowlistRecord,
    MigrationContaminationFinding,
    stable_id,
)


@dataclass(frozen=True)
class _MechanismSpec:
    kind: str
    keywords: tuple[str, ...]
    source_status: str
    proposed_q_stage: str
    synthetic_dependencies: tuple[str, ...] = ()
    authority_dependencies: tuple[str, ...] = ()
    analysis_tag_dependencies: tuple[str, ...] = ()
    primitive_dependencies: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()


MECHANISM_SPECS = (
    _MechanismSpec(
        "active_cost_accounting",
        ("cost", "budgetvector"),
        "portable_after_semantic_extraction",
        "Q-M1-candidate-only",
        synthetic_dependencies=("synthetic_score_mapping",),
        constraints=("separate_score_from_cost", "no_existence_value_from_performance_only"),
    ),
    _MechanismSpec(
        "storage_quota",
        ("quota", "budget", "memory_peak"),
        "portable_after_semantic_extraction",
        "Q-M1-candidate-only",
        synthetic_dependencies=("research_budget_profile",),
        constraints=("external_authorization", "bounded_accounting_only"),
    ),
    _MechanismSpec(
        "anonymous_organ_registry",
        ("registry", "idallocator", "anonymous"),
        "portable_mechanism_candidate",
        "Q-M1-candidate-only",
        constraints=("anonymous_identity", "append_only_registration"),
    ),
    _MechanismSpec(
        "lineage",
        ("lineage", "parent_id", "ancestor"),
        "portable_mechanism_candidate",
        "Q-M1-candidate-only",
        constraints=("identity_continuity", "history_not_deletable"),
    ),
    _MechanismSpec(
        "candidate_generation_protocol",
        ("proposer", "generate", "candidate"),
        "portable_after_semantic_extraction",
        "Q-M2-or-later",
        synthetic_dependencies=("synthetic_world_tokens",),
        primitive_dependencies=("primitive_manifest",),
        constraints=("shadow_only", "no_runtime_replacement"),
    ),
    _MechanismSpec(
        "candidate_validation_protocol",
        ("evaluator", "validate", "locked_test"),
        "portable_after_semantic_extraction",
        "Q-M2-or-later",
        synthetic_dependencies=("synthetic_task_score",),
        constraints=("teacher_review_preserved", "source_evidence_preserved"),
    ),
    _MechanismSpec(
        "snapshot",
        ("snapshot", "create_snapshot"),
        "portable_after_authority_removal",
        "Q-M1-candidate-only",
        authority_dependencies=("filesystem_snapshot_authority",),
        constraints=("append_only_attempt_history", "rollback_event_required"),
    ),
    _MechanismSpec(
        "rollback",
        ("rollback", "restore"),
        "unresolved",
        "Q-M1-candidate-only",
        authority_dependencies=("history_overwrite_authority",),
        constraints=("attempt_history_must_survive", "no_wholesale_history_restore"),
    ),
    _MechanismSpec(
        "organ_lifecycle_protocol",
        ("birth", "sleep", "wake", "prune", "replace", "merge", "split", "rewire"),
        "portable_after_authority_removal",
        "Q-M3-or-later",
        authority_dependencies=("organ_lifecycle_mutation",),
        constraints=("human_approval", "continuity_cost", "rollback"),
    ),
    _MechanismSpec(
        "lesion_regeneration_protocol",
        ("lesion", "regener"),
        "portable_after_authority_removal",
        "Q-M3-or-later",
        authority_dependencies=("organ_replacement_authority",),
        constraints=("identity_continuity", "supervised_only"),
    ),
    _MechanismSpec(
        "active_passive_organ_coexistence",
        ("active_organs", "passive", "shadow"),
        "portable_after_authority_removal",
        "Q-M2-or-later",
        constraints=("shadow_first", "no_core_replacement"),
    ),
    _MechanismSpec(
        "ACTION_BID",
        ("action_bid", "bid"),
        "portable_after_semantic_extraction",
        "Q-M4-or-later",
        synthetic_dependencies=("synthetic_action_world",),
        primitive_dependencies=("ACTION_BID",),
        constraints=("closed_sandbox", "external_permission_gates"),
    ),
    _MechanismSpec(
        "ABSTAIN",
        ("abstain",),
        "portable_after_semantic_extraction",
        "Q-M4-or-later",
        synthetic_dependencies=("synthetic_action_world",),
        primitive_dependencies=("ABSTAIN",),
        constraints=("closed_sandbox",),
    ),
    _MechanismSpec(
        "bid_cost_and_stake_limit",
        ("stake", "bid_cost"),
        "portable_after_semantic_extraction",
        "Q-M4-or-later",
        synthetic_dependencies=("synthetic_action_score",),
        constraints=("hard_stake_limit", "no_external_action_authority"),
    ),
    _MechanismSpec(
        "counterfactual_consequence_credit",
        ("counterfactual",),
        "portable_after_semantic_extraction",
        "Q-M4-or-later",
        synthetic_dependencies=("synthetic_world_consequence",),
        constraints=("grounded_consequence_source",),
    ),
    _MechanismSpec(
        "upstream_support_credit",
        ("upstream", "credit"),
        "portable_after_semantic_extraction",
        "Q-M4-or-later",
        synthetic_dependencies=("synthetic_credit_mapping",),
        constraints=("credit_conservation",),
    ),
    _MechanismSpec(
        "ecological_limit_snapshotting",
        ("ecological", "snapshot"),
        "portable_after_semantic_extraction",
        "DLM-1-or-later",
        synthetic_dependencies=("synthetic_ecology_threshold",),
        constraints=("sealed_thresholds", "append_only_snapshot"),
    ),
    _MechanismSpec(
        "teacher_input_isolation",
        ("teacher", "bandwidth", "ledger"),
        "portable_after_semantic_extraction",
        "DLM-1-or-later",
        synthetic_dependencies=("synthetic_teacher_packets",),
        constraints=("teacher_cannot_create_organs", "teacher_review_preserved"),
    ),
    _MechanismSpec(
        "analysis_tag_one_way_isolation",
        ("analysis_non_interference", "analysis_tags"),
        "portable_mechanism_candidate",
        "DLM-1-or-later",
        analysis_tag_dependencies=("offline_analysis_tags",),
        constraints=("one_way_dataflow_test",),
    ),
    _MechanismSpec(
        "self_audit_gate_framework",
        ("audit", "validation", "proof"),
        "portable_mechanism_candidate",
        "DLM-1-or-later",
        constraints=("never_replace_sensor_or_archive_specific_audits",),
    ),
    _MechanismSpec(
        "synthetic_task_score_adapter",
        ("syn_", "synthetic", "score", "world"),
        "forbidden_direct_migration",
        "never",
        synthetic_dependencies=("fixed_world", "fixed_score_mapping"),
    ),
    _MechanismSpec(
        "direct_organ_templates",
        ("graph_for_family", "template"),
        "forbidden_direct_migration",
        "never",
        synthetic_dependencies=("human_family_label",),
        primitive_dependencies=("direct_solution_template",),
    ),
    _MechanismSpec(
        "research_reset_fork_history_authority",
        ("reset", "fork", "rollback", "restore"),
        "forbidden_direct_migration",
        "never",
        authority_dependencies=("reset_fork_overwrite",),
    ),
)


def _module_matches(
    module: DLaplaceModuleInventoryRecord,
    keywords: tuple[str, ...],
) -> bool:
    haystack = " ".join(
        (module.relative_path, *module.declared_symbols)
    ).casefold()
    return any(keyword.casefold() in haystack for keyword in keywords)


def classify_portable_mechanisms(
    modules: tuple[DLaplaceModuleInventoryRecord, ...],
    findings: tuple[MigrationContaminationFinding, ...],
    *,
    migration_document_refs: tuple[str, ...],
) -> tuple[DLaplaceMigrationCandidateRecord, ...]:
    records: list[DLaplaceMigrationCandidateRecord] = []
    for spec in MECHANISM_SPECS:
        source_refs = tuple(
            sorted(
                module.module_record_id
                for module in modules
                if module.evidence_status == "source_code_ast_parsed"
                and "/tests/" not in f"/{module.relative_path.casefold()}/"
                and _module_matches(module, spec.keywords)
            )
        )
        status = spec.source_status if source_refs else "documentation_only_candidate"
        if spec.kind == "rollback" and any(
            finding.category == "history_overwrite_authority"
            for finding in findings
        ):
            status = "unresolved"
        extraction_required = status in {
            "portable_after_semantic_extraction",
            "portable_after_authority_removal",
        }
        payload = {
            "mechanism_kind": spec.kind,
            "source_refs": source_refs,
            "status": status,
        }
        records.append(
            DLaplaceMigrationCandidateRecord(
                migration_candidate_id=stable_id(
                    "d_laplace_migration_candidate",
                    payload,
                ),
                mechanism_kind=spec.kind,
                source_module_refs=source_refs,
                portability_status=status,
                extraction_required=extraction_required,
                synthetic_dependencies=spec.synthetic_dependencies,
                authority_dependencies=spec.authority_dependencies,
                analysis_tag_dependencies=spec.analysis_tag_dependencies,
                primitive_dependencies=spec.primitive_dependencies,
                proposed_q_stage=spec.proposed_q_stage,
                qingyin_constraints_required=spec.constraints,
                forbidden_direct_import=True,
                source_trace_refs=tuple(
                    dict.fromkeys((*source_refs, *migration_document_refs))
                ),
            )
        )
    return tuple(records)


QM1_ALLOWED_KINDS = {
    "active_cost_accounting",
    "storage_quota",
    "anonymous_organ_registry",
    "lineage",
    "snapshot",
    "rollback",
}
QM1_FORBIDDEN_TERMS = {
    "birth",
    "death",
    "prune",
    "replace",
    "merge",
    "split",
    "rewire",
    "lesion",
    "regeneration",
    "ACTION_BID",
    "arbitration",
    "teacher_created",
    "runtime_influence",
}


def build_qm1_candidate_allowlist(
    candidates: tuple[DLaplaceMigrationCandidateRecord, ...],
) -> DLaplaceQM1AllowlistRecord:
    allowed: list[str] = []
    blocked: list[str] = []
    unresolved: list[str] = []
    for candidate in candidates:
        if candidate.mechanism_kind not in QM1_ALLOWED_KINDS:
            blocked.append(candidate.migration_candidate_id)
            continue
        if any(
            term.casefold() in candidate.mechanism_kind.casefold()
            for term in QM1_FORBIDDEN_TERMS
        ):
            blocked.append(candidate.migration_candidate_id)
            continue
        if candidate.portability_status in {
            "unresolved",
            "documentation_only_candidate",
        }:
            unresolved.append(candidate.migration_candidate_id)
            continue
        if candidate.portability_status == "forbidden_direct_migration":
            blocked.append(candidate.migration_candidate_id)
            continue
        allowed.append(candidate.migration_candidate_id)
    payload = {
        "allowed": sorted(allowed),
        "blocked": sorted(blocked),
        "unresolved": sorted(unresolved),
        "execution": False,
    }
    return DLaplaceQM1AllowlistRecord(
        allowlist_id=stable_id("d_laplace_qm1_candidate_allowlist", payload),
        mechanism_candidate_refs=tuple(sorted(allowed)),
        blocked_mechanism_refs=tuple(sorted(blocked)),
        unresolved_mechanism_refs=tuple(sorted(unresolved)),
        q_m1_execution_authorized=False,
        source_trace_refs=tuple(
            sorted({candidate.migration_candidate_id for candidate in candidates})
        ),
    )
