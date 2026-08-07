"""Static reconciliation inventory for legacy drive-adjacent structures."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import sha256_bytes, sha256_payload, utc_now
from ashl_core_v1.endocrine.drive_signal_trace_types import (
    LEGACY_BOUNDARY_SCHEMA_VERSION,
    DriveSignalLegacyBoundaryRecord,
)


LEGACY_STRUCTURE_SPECS: tuple[dict[str, Any], ...] = (
    {
        "structure_kind": "legacy_mimetic_endocrine_value_shape",
        "modules": ("ashl_core_v1/endocrine/types.py",),
        "symbols": ("EndocrineSignal",),
        "actual_role": "first-stage four-axis fixture data shape with free-form modulation notes",
        "owner": "legacy_endocrine_fixture_layer",
        "classification": "legacy_value_shape_not_package_135_authority",
        "reuse": ("bounded_normalized_value", "source_trace_refs", "immutable_record_shape"),
        "forbidden": ("chemical_axis_semantics", "modulation_notes", "promotion_as_authoritative_drive_trace"),
        "risk": True,
    },
    {
        "structure_kind": "legacy_fixed_circulation_endocrine_flow",
        "modules": (
            "ashl_core_v1/runtime/cradle_cases.py",
            "ashl_core_v1/runtime/manual_samples.py",
            "ashl_core_v1/thought/types.py",
        ),
        "symbols": ("build_cradle_case_sample", "build_blocked_manual_circulation_sample", "ThoughtSignal"),
        "actual_role": "historical deterministic cradle/demo circulation that references endocrine IDs from learning and thought records",
        "owner": "legacy_fixed_circulation_fixture",
        "classification": "legacy_fixed_circulation_conflicts_with_trace_only_boundary",
        "reuse": ("source_reference_visibility", "fixture_boundary_tests"),
        "forbidden": ("thought_input", "learning_input", "body_intent_hint", "runtime_modulation"),
        "risk": True,
    },
    {
        "structure_kind": "legacy_endocrine_and_tendency_design_documents",
        "modules": (
            "ashl_core_v1/docs/concept_transfer_sources/06_endocrine_state_modulation/mimetic_endocrine_system_design_v0.md",
            "ashl_core_v1/docs/concept_transfer_sources/05_embodiment_action_sandbox/body_motor_affordance_tendency_endocrine_reconciliation_design_v0.md",
        ),
        "symbols": ("Mimetic Endocrine System Design v0", "tendency may affect candidate ordering only"),
        "actual_role": "design-only historical concepts predating Package 132-134 authority closure",
        "owner": "concept_transfer_documentation",
        "classification": "legacy_design_concepts_partially_reusable",
        "reuse": ("source_provenance", "bounded_values", "time_and_change_trace", "authority_separation"),
        "forbidden": ("reward_semantics", "trust_semantics", "curiosity_semantics", "candidate_priority", "attention_modulation"),
        "risk": True,
    },
    {
        "structure_kind": "thought_endocrine_reference_surface",
        "modules": ("ashl_core_v1/thought/types.py",),
        "symbols": ("ThoughtSignal",),
        "actual_role": "legacy thought signal can cite endocrine signal IDs in fixed demo circulation",
        "owner": "legacy_thought_fixture_layer",
        "classification": "thought_consumer_forbidden_for_package_135",
        "reuse": ("none",),
        "forbidden": ("package_135_trace_import", "thought_engine_influence", "body_intent_hint"),
        "risk": True,
    },
    {
        "structure_kind": "affordance_learning_and_memory_content",
        "modules": ("ashl_core_v1/learning/task_closure_learning_feedback_candidate.py",),
        "symbols": ("LearningFeedbackCandidateRecord", "build_learning_feedback_candidate_from_task_closure"),
        "actual_role": "teacher-governed semantic learning evidence about action feasibility or outcome",
        "owner": "learning_and_memory_authority",
        "classification": "semantic_affordance_learning_not_drive",
        "reuse": ("opaque_source_reference_convention",),
        "forbidden": ("affordance_as_drive", "learning_signal_as_regulatory_trace", "memory_content"),
        "risk": False,
    },
    {
        "structure_kind": "operator_runtime_status_view",
        "modules": (
            "ashl_core_v1/runtime/operator_console_state_reader.py",
            "ashl_core_v1/runtime/operator_console_types.py",
        ),
        "symbols": ("build_total_state_snapshot", "QingyinTotalStateSnapshot"),
        "actual_role": "derived operator-facing process, sensor and teacher-gate status",
        "owner": "local_operator_console",
        "classification": "operator_runtime_status_not_drive",
        "reuse": ("source_record_reference_only_after_future_explicit_authorization",),
        "forbidden": ("running_status_as_drive", "sensor_status_as_desire", "teacher_gate_status_as_reward"),
        "risk": False,
    },
    {
        "structure_kind": "teacher_gated_selected_action_authority",
        "modules": (
            "ashl_core_v1/task/teacher_gated_selected_action_proposal.py",
            "ashl_core_v1/task/teacher_gated_selected_action_application.py",
        ),
        "symbols": ("SelectedActionProposalRecord", "SelectedActionApplicationRecord"),
        "actual_role": "teacher-gated task candidate proposal and selected-action application",
        "owner": "task_engine_teacher_gate",
        "classification": "teacher_gated_selected_action_not_drive",
        "reuse": ("none",),
        "forbidden": ("drive_action_preference", "drive_selected_action", "purpose_expansion"),
        "risk": False,
    },
    {
        "structure_kind": "package_133_persistent_self_state_authority",
        "modules": ("ashl_core_v1/state/persistent_self_state_schema.py",),
        "symbols": ("PersistentSelfStateRecord", "PersistentSelfStateRepresentationContract"),
        "actual_role": "sole immutable structural self-state representation authority",
        "owner": "state_engine_package_133",
        "classification": "package_133_self_state_excludes_drive",
        "reuse": ("opaque_session_provenance_reference", "canonical_hash_lineage_pattern"),
        "forbidden": ("drive_as_self_state_field", "drive_payload", "drive_behavior_authority"),
        "risk": False,
    },
    {
        "structure_kind": "package_134_recovery_authority",
        "modules": ("ashl_core_v1/state/persistent_session_recovery_types.py",),
        "symbols": ("ActiveSelfStateHeadRecord", "PersistentSessionIdentityBindingRecord"),
        "actual_role": "explicit structural identity recovery and separate active-head CAS authority",
        "owner": "state_engine_package_134",
        "classification": "package_134_recovery_excludes_drive",
        "reuse": ("read_only_non_recovery_evidence", "session_and_process_identity"),
        "forbidden": ("drive_restore", "drive_head_field", "cross_session_drive_continuation"),
        "risk": False,
    },
    {
        "structure_kind": "package_132_frozen_perception_attention_line",
        "modules": ("ashl_core_v1/runtime/perception_attention_closure_types.py",),
        "symbols": ("PerceptionAttentionCapabilityBoundaryClosureContract",),
        "actual_role": "authoritative closure of perception capability construction and internal action surface",
        "owner": "package_132_perception_attention_closure",
        "classification": "package_132_frozen_perception_attention_boundary",
        "reuse": ("read_only_boundary_reference",),
        "forbidden": ("perception_modulation", "attention_modulation", "new_internal_action"),
        "risk": False,
    },
)


def build_drive_signal_legacy_inventory(
    ashl_root: str | Path,
) -> tuple[DriveSignalLegacyBoundaryRecord, ...]:
    root = Path(ashl_root).resolve()
    created_at = utc_now()
    records: list[DriveSignalLegacyBoundaryRecord] = []
    for spec in LEGACY_STRUCTURE_SPECS:
        modules = tuple(str(item) for item in spec["modules"])
        required = tuple(str(item) for item in spec["symbols"])
        hashes: list[str] = []
        discovered: set[str] = set()
        files_present = True
        for module in modules:
            path = root / module
            if not path.is_file() or path.is_symlink():
                files_present = False
                hashes.append("0" * 64)
                continue
            data = path.read_bytes()
            hashes.append(sha256_bytes(data))
            text = data.decode("utf-8")
            if path.suffix == ".py":
                tree = ast.parse(text, filename=module)
                discovered.update(
                    node.name
                    for node in tree.body
                    if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
                )
            else:
                discovered.update(marker for marker in required if marker in text)
        scan_verified = files_present and set(required).issubset(discovered)
        payload: dict[str, Any] = {
            "boundary_record_id": "",
            "boundary_sha256": "",
            "schema_version": LEGACY_BOUNDARY_SCHEMA_VERSION,
            "created_at": created_at,
            "structure_kind": str(spec["structure_kind"]),
            "module_paths": modules,
            "required_symbols": required,
            "source_file_sha256s": tuple(hashes),
            "actual_role": str(spec["actual_role"]),
            "authority_owner": str(spec["owner"]),
            "current_classification": str(spec["classification"]),
            "reusable_concepts": tuple(str(item) for item in spec["reuse"]),
            "forbidden_package_135_reuse": tuple(str(item) for item in spec["forbidden"]),
            "direct_runtime_consumer_risk": bool(spec["risk"]),
            "source_scan_verified": scan_verified,
            "source_record_refs": modules,
        }
        digest_payload = dict(payload)
        digest_payload.pop("boundary_record_id", None)
        digest_payload.pop("boundary_sha256", None)
        digest_payload.pop("created_at", None)
        digest = sha256_payload(digest_payload)
        payload["boundary_sha256"] = digest
        payload["boundary_record_id"] = f"drive_legacy_boundary:{digest[:16]}"
        records.append(DriveSignalLegacyBoundaryRecord(**payload))
    return tuple(records)


def drive_signal_inventory_sha256(
    records: tuple[DriveSignalLegacyBoundaryRecord, ...],
) -> str:
    return sha256_payload(
        tuple((record.boundary_record_id, record.boundary_sha256) for record in records)
    )
