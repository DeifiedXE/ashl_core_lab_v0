"""Static state-like inventory and authoritative Package 133 contract loader."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import sha256_bytes, sha256_payload, utc_now
from ashl_core_v1.state.persistent_self_state_schema import (
    BOUNDARY_SCHEMA_VERSION,
    CONTRACT_SCHEMA_VERSION,
    PersistentSelfStateRepresentationContract,
    StateLikeStructureBoundaryRecord,
)


CONTRACT_RELATIVE_PATH = Path(
    "ashl_core_v1/docs/reference/persistent_self_state_representation_contract_v0.json"
)

STATE_LIKE_STRUCTURE_SPECS: tuple[dict[str, Any], ...] = (
    {
        "structure_kind": "legacy_session_state_snapshot",
        "modules": ("ashl_core_v1/runtime/session_persistence.py",),
        "symbols": ("build_state_snapshot", "save_state_snapshot"),
        "authority_owner": "legacy_runtime_session_persistence",
        "persistence_shape": "overwrite_json_with_arbitrary_state_values",
        "actual_role": "single-session convenience snapshot and summaries",
        "classification": "legacy_persistence_not_self_state",
        "reuse": ("none",),
        "forbidden": ("arbitrary_state_values", "overwrite_file_semantics", "repo_default_data_path"),
        "risks": ("world_fact", "memory_content", "semantic_history"),
    },
    {
        "structure_kind": "state_engine_cradle_handoff",
        "modules": ("ashl_core_v1/state/cradle_state_persistence_handoff.py",),
        "symbols": ("CradleStateHandoffRecord", "write_cradle_state_handoff_bundle"),
        "authority_owner": "state_engine",
        "persistence_shape": "explicit_state_dir_overwrite_handoff_bundle",
        "actual_role": "teacher-visible session continuity handoff and bookmarks",
        "classification": "continuity_authority_reused_boundary_only",
        "reuse": ("state_engine_authority_owner", "explicit_state_dir", "validation_first_boundary"),
        "forbidden": ("working_memory_summary_payload", "task_summary_payload", "bookmark_payload", "overwrite_storage"),
        "risks": ("memory_content", "semantic_history"),
    },
    {
        "structure_kind": "state_engine_resume_chain",
        "modules": (
            "ashl_core_v1/state/state_engine_resume_continuity_audit.py",
            "ashl_core_v1/state/cradle_state_restore_preview_resume_handoff.py",
        ),
        "symbols": ("StateEngineResumeContinuityAuditRecord", "TeacherGatedResumeHandoffRecord"),
        "authority_owner": "state_engine",
        "persistence_shape": "teacher_gated_resume_handoff_documents",
        "actual_role": "manual future-scoped resume selection and handoff",
        "classification": "session_scoped_not_self_state",
        "reuse": ("no_automatic_resume_boundary", "teacher_visible_provenance_convention"),
        "forbidden": ("resume_selection_payload", "target_engine_entry", "manual_command", "recovery_execution"),
        "risks": ("semantic_history",),
    },
    {
        "structure_kind": "teacher_gated_session_checkpoint",
        "modules": ("ashl_core_v1/runtime/teacher_gated_session_store.py",),
        "symbols": ("PersistedCheckpoint", "TeacherGatedSessionStore"),
        "authority_owner": "bounded_session_runtime",
        "persistence_shape": "sqlite_checkpoint_with_mutable_session_head",
        "actual_role": "bounded session pause/review checkpoint and runtime records",
        "classification": "session_scoped_not_self_state",
        "reuse": ("session_id_provenance_only", "sqlite_transaction_pattern"),
        "forbidden": ("session_state_payload", "working_readback_snapshot", "runtime_records", "mutable_session_head"),
        "risks": ("memory_content", "semantic_history"),
    },
    {
        "structure_kind": "task_working_memory",
        "modules": ("ashl_core_v1/memory/task_working_memory_lifecycle.py",),
        "symbols": ("ActiveTaskFrame", "TaskWorkingMemoryTickUpdate"),
        "authority_owner": "memory_engine_working_layer",
        "persistence_shape": "task_local_frame_and_demo_history",
        "actual_role": "ephemeral task execution context",
        "classification": "session_scoped_not_self_state",
        "reuse": ("none",),
        "forbidden": ("active_task_payload", "tick_updates", "suspended_task_content"),
        "risks": ("memory_content", "world_fact"),
    },
    {
        "structure_kind": "working_readback",
        "modules": (
            "ashl_core_v1/memory/reviewed_concept_working_readback_preview.py",
            "ashl_core_v1/host_body/host_body_working_readback_integration.py",
        ),
        "symbols": ("ReviewedConceptWorkingReadbackPreview", "HostBodyWorkingReadbackVisibilityRecord"),
        "authority_owner": "memory_and_host_body_advisory_path",
        "persistence_shape": "bounded_interpreted_read_only_context",
        "actual_role": "reviewed concept advisory context for one bounded runtime path",
        "classification": "content_system_not_self_state",
        "reuse": ("read_only_context_boundary_only",),
        "forbidden": ("hint_labels", "task_notes", "concept_content", "behavior_influence"),
        "risks": ("memory_content", "semantic_history"),
    },
    {
        "structure_kind": "governed_memory_records",
        "modules": (
            "ashl_core_v1/memory/types.py",
            "ashl_core_v1/memory/trace_store.py",
        ),
        "symbols": ("MemoryLearningTrace", "MemoryApplicationData", "list_memory_learning_traces"),
        "authority_owner": "memory_engine",
        "persistence_shape": "reviewed_memory_traces_and_content_records",
        "actual_role": "teacher-governed interpreted memory and routing",
        "classification": "content_system_not_self_state",
        "reuse": ("opaque_record_reference_convention_only",),
        "forbidden": ("memory_items", "reviewed_concept_content", "routing_notes", "trace_notes"),
        "risks": ("memory_content", "semantic_history", "world_fact"),
    },
    {
        "structure_kind": "perception_and_temporal_history",
        "modules": (
            "ashl_core_v1/runtime/package_124a_temporal_store.py",
            "ashl_core_v1/runtime/trace_envelope.py",
        ),
        "symbols": ("Package124ATemporalStore", "TraceEnvelope"),
        "authority_owner": "perception_trace_and_temporal_foundation",
        "persistence_shape": "append_only_evidence_and_per_session_trace_history",
        "actual_role": "grounded evidence history and temporal provenance",
        "classification": "evidence_history_not_self_state",
        "reuse": ("canonical_sha256_integrity_pattern", "append_only_record_pattern", "source_record_refs"),
        "forbidden": ("raw_or_derived_perception_payload", "temporal_event_content", "cross_session_trace_ref_reclassification"),
        "risks": ("raw_perception", "world_fact", "semantic_history"),
    },
    {
        "structure_kind": "operator_runtime_status",
        "modules": (
            "ashl_core_v1/runtime/operator_console_state_reader.py",
            "ashl_core_v1/runtime/operator_console_types.py",
        ),
        "symbols": ("build_total_state_snapshot", "QingyinTotalStateSnapshot"),
        "authority_owner": "local_operator_console",
        "persistence_shape": "derived_current_runtime_view",
        "actual_role": "operator-facing process, sensor and teacher-gate status",
        "classification": "operational_view_not_self_state",
        "reuse": ("none",),
        "forbidden": ("running_sleeping_stopped_status", "sensor_status", "teacher_gate_status"),
        "risks": ("world_fact",),
    },
)


def build_state_like_structure_inventory(
    ashl_root: str | Path,
) -> tuple[StateLikeStructureBoundaryRecord, ...]:
    root = Path(ashl_root).resolve()
    created_at = utc_now()
    records: list[StateLikeStructureBoundaryRecord] = []
    for spec in STATE_LIKE_STRUCTURE_SPECS:
        modules = tuple(str(item) for item in spec["modules"])
        required_symbols = tuple(str(item) for item in spec["symbols"])
        hashes: list[str] = []
        discovered_symbols: set[str] = set()
        files_present = True
        for module in modules:
            path = root / module
            if not path.is_file() or path.is_symlink():
                files_present = False
                hashes.append("0" * 64)
                continue
            data = path.read_bytes()
            hashes.append(sha256_bytes(data))
            tree = ast.parse(data.decode("utf-8"), filename=module)
            discovered_symbols.update(
                node.name
                for node in tree.body
                if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
            )
        scan_verified = files_present and set(required_symbols).issubset(discovered_symbols)
        identity_payload = {
            "structure_kind": spec["structure_kind"],
            "modules": modules,
            "hashes": hashes,
            "symbols": required_symbols,
            "classification": spec["classification"],
        }
        records.append(
            StateLikeStructureBoundaryRecord(
                boundary_record_id=(
                    f"state_like_boundary:{sha256_payload(identity_payload)[:16]}"
                ),
                schema_version=BOUNDARY_SCHEMA_VERSION,
                created_at=created_at,
                structure_kind=str(spec["structure_kind"]),
                source_module_refs=modules,
                required_symbol_refs=required_symbols,
                source_file_sha256s=tuple(hashes),
                authority_owner=str(spec["authority_owner"]),
                persistence_shape=str(spec["persistence_shape"]),
                actual_role=str(spec["actual_role"]),
                self_state_classification=str(spec["classification"]),
                reusable_elements=tuple(spec["reuse"]),
                forbidden_direct_reuse=tuple(spec["forbidden"]),
                content_risk_categories=tuple(spec["risks"]),
                source_scan_verified=scan_verified,
                source_record_refs=tuple(f"source_file:{item}" for item in hashes),
            )
        )
    return tuple(records)


def load_authoritative_self_state_contract(
    ashl_root: str | Path,
) -> PersistentSelfStateRepresentationContract:
    path = Path(ashl_root).resolve() / CONTRACT_RELATIVE_PATH
    payload = json.loads(path.read_text(encoding="utf-8"))
    return PersistentSelfStateRepresentationContract(
        contract_id=str(payload["contract_id"]),
        contract_sha256=str(payload["contract_sha256"]),
        schema_version=str(payload["schema_version"]),
        created_at=str(payload["created_at"]),
        baseline_commit=str(payload["baseline_commit"]),
        authority_owner=str(payload["authority_owner"]),
        representation_kind=str(payload["representation_kind"]),
        allowed_persistent_fields=tuple(payload["allowed_persistent_fields"]),
        forbidden_content_categories=tuple(payload["forbidden_content_categories"]),
        forbidden_authorities=tuple(payload["forbidden_authorities"]),
        parent_child_lineage_required=bool(payload["parent_child_lineage_required"]),
        monotonic_version_required=bool(payload["monotonic_version_required"]),
        distinct_session_provenance_required=bool(payload["distinct_session_provenance_required"]),
        canonical_hash_chain_required=bool(payload["canonical_hash_chain_required"]),
        append_only_persistence_required=bool(payload["append_only_persistence_required"]),
        state_engine_continuity_authority_reused=bool(payload["state_engine_continuity_authority_reused"]),
        legacy_state_payload_reused=bool(payload["legacy_state_payload_reused"]),
        legacy_store_directly_reused=bool(payload["legacy_store_directly_reused"]),
        active_head_created=bool(payload["active_head_created"]),
        cross_session_recovery_enabled=bool(payload["cross_session_recovery_enabled"]),
        runtime_behavior_influence_enabled=bool(payload["runtime_behavior_influence_enabled"]),
        drive_signal_enabled=bool(payload["drive_signal_enabled"]),
        memory_write_enabled=bool(payload["memory_write_enabled"]),
        output_enabled=bool(payload["output_enabled"]),
        persistent_self_claim_authorized=bool(payload["persistent_self_claim_authorized"]),
        next_package=str(payload["next_package"]),
    )


def path_fingerprint(path: str | Path) -> str:
    normalized = str(Path(path).resolve()).replace("\\", "/").lower()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
