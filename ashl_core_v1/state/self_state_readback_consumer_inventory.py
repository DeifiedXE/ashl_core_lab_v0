"""Source-grounded consumer inventory for Package 138."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import sha256_bytes, sha256_payload, utc_now
from ashl_core_v1.state.self_state_readback_types import (
    AUDIT_ONLY_CONSUMER_ID,
    INVENTORY_SCHEMA_VERSION,
    SelfStateReadbackConsumerInventoryRecord,
)


@dataclass(frozen=True)
class _ConsumerDefinition:
    surface_id: str
    paths: tuple[str, ...]
    markers: tuple[str, ...]
    owner: str
    role: str
    classification: str
    rejection_reasons: tuple[str, ...]
    audit_only: bool = False


_DEFINITIONS = (
    _ConsumerDefinition(
        "package_134_session_identity_binding",
        ("ashl_core_v1/state/persistent_session_recovery_types.py",),
        ("class PersistentSessionIdentityBindingRecord", "working_readback_restored"),
        "package_134_recovery_authority",
        "structural_identity_binding_without_payload_readback",
        "authority_source_not_a_readback_consumer",
        ("active_head_authority_preserved", "recovery_cannot_restore_readback"),
    ),
    _ConsumerDefinition(
        "teacher_gated_session_working_readback",
        ("ashl_core_v1/runtime/teacher_gated_session_store.py",),
        ("working_readback", "teacher_decisions"),
        "memory_learning_runtime",
        "teacher_reviewed_concept_working_readback",
        "forbidden_memory_learning_consumer",
        ("memory_content_boundary", "teacher_scope_mismatch"),
    ),
    _ConsumerDefinition(
        "feedback_reviewed_concept_readback",
        (
            "ashl_core_v1/learning/feedback_refined_concept_reviewed_readback_integration.py",
        ),
        ("WorkingReadbackIntegrationRecord", "ReviewedConcept"),
        "learning_system",
        "reviewed_concept_memory_readback",
        "forbidden_semantic_memory_consumer",
        ("semantic_content_boundary", "learning_authority_preserved"),
    ),
    _ConsumerDefinition(
        "active_perception_readback_influence",
        ("ashl_core_v1/runtime/active_perception_readback_influence.py",),
        ("score_extension_candidate_with_working_readback", "ACTIVE_PERCEPTION_SIGNAL_THEME"),
        "frozen_perception_line",
        "legacy_active_perception_readback_influence",
        "forbidden_perception_attention_consumer",
        ("perception_line_frozen", "attention_influence_forbidden"),
    ),
    _ConsumerDefinition(
        "teacher_gated_candidate_ordering",
        ("ashl_core_v1/task/advisory_readback_candidate_ordering_application.py",),
        ("compute_advisory_readback_ordering", "approved_for_candidate_ordering_change"),
        "teacher_gated_task_engine",
        "candidate_ordering_authority",
        "forbidden_candidate_ordering_consumer",
        ("behavior_authority_forbidden", "separate_teacher_scope"),
    ),
    _ConsumerDefinition(
        "package_136_drive_modulation_surface",
        ("ashl_core_v1/endocrine/drive_modulation_types.py",),
        ("AUDIT_ONLY_CONSUMER_ID", "DriveModulationCounterfactualComparison"),
        "package_136_modulation_boundary",
        "same_session_drive_modulation_audit_surface",
        "forbidden_drive_consumer",
        ("drive_authority_separate", "cross_package_consumer_reuse_forbidden"),
    ),
    _ConsumerDefinition(
        "operator_total_state_snapshot",
        (
            "ashl_core_v1/runtime/operator_console_types.py",
            "ashl_core_v1/runtime/operator_console_state_reader.py",
        ),
        ("QingyinTotalStateSnapshot", "build_total_state_snapshot"),
        "local_operator_console",
        "derived_operator_status_view",
        "operator_view_not_a_runtime_consumer",
        ("operator_translation_only", "no_qingyin_output"),
    ),
    _ConsumerDefinition(
        AUDIT_ONLY_CONSUMER_ID,
        ("ashl_core_v1/state/self_state_readback_types.py",),
        ("AUDIT_ONLY_CONSUMER_ID", "SelfStateReadbackCounterfactualSnapshot"),
        "package_138_audit_harness",
        "opaque_structural_read_only_counterfactual_surface",
        "audit_only_structural_consumer",
        ("not_a_production_runtime_consumer",),
        audit_only=True,
    ),
)


def build_self_state_readback_consumer_inventory(
    ashl_root: str | Path,
) -> tuple[SelfStateReadbackConsumerInventoryRecord, ...]:
    root = Path(ashl_root).resolve()
    records: list[SelfStateReadbackConsumerInventoryRecord] = []
    for definition in _DEFINITIONS:
        paths = tuple(root / item for item in definition.paths)
        if not all(path.is_file() for path in paths):
            missing = tuple(
                definition.paths[index]
                for index, path in enumerate(paths)
                if not path.is_file()
            )
            raise FileNotFoundError(f"Package 138 consumer inventory missing source: {missing}")
        texts = tuple(path.read_text(encoding="utf-8") for path in paths)
        combined = "\n".join(texts)
        if not all(marker in combined for marker in definition.markers):
            raise RuntimeError(
                f"Package 138 consumer inventory marker missing: {definition.surface_id}"
            )
        hashes = tuple(sha256_bytes(path.read_bytes()) for path in paths)
        payload: dict[str, Any] = {
            "inventory_record_id": "",
            "inventory_sha256": "",
            "schema_version": INVENTORY_SCHEMA_VERSION,
            "created_at": utc_now(),
            "consumer_surface_id": definition.surface_id,
            "module_paths": definition.paths,
            "source_file_sha256s": hashes,
            "detected_symbols": definition.markers,
            "current_authority_owner": definition.owner,
            "current_runtime_role": definition.role,
            "classification": definition.classification,
            "production_eligible": False,
            "audit_only_eligible": definition.audit_only,
            "rejection_reasons": definition.rejection_reasons,
            "source_scan_verified": True,
            "source_record_refs": tuple(f"source_file:{item}" for item in hashes),
        }
        identity = dict(payload)
        identity.pop("inventory_record_id")
        identity.pop("inventory_sha256")
        identity.pop("created_at")
        digest = sha256_payload(identity)
        payload["inventory_record_id"] = f"self_state_readback_consumer_inventory:{digest[:16]}"
        payload["inventory_sha256"] = digest
        records.append(SelfStateReadbackConsumerInventoryRecord(**payload))
    return tuple(records)


def consumer_inventory_sha256(
    records: tuple[SelfStateReadbackConsumerInventoryRecord, ...],
) -> str:
    return sha256_payload(
        tuple(
            (item.consumer_surface_id, item.inventory_sha256)
            for item in sorted(records, key=lambda record: record.consumer_surface_id)
        )
    )
