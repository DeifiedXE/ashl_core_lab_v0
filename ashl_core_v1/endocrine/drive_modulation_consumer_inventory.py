"""Source-grounded consumer inventory for Package 136."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ashl_core_v1.endocrine.drive_modulation_types import (
    AUDIT_ONLY_CONSUMER_ID,
    INVENTORY_SCHEMA_VERSION,
    DriveModulationConsumerInventoryRecord,
)
from ashl_core_v1.runtime.host_sensor_types import sha256_bytes, sha256_payload, utc_now


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
        "legacy_endocrine_signal_shape",
        ("ashl_core_v1/endocrine/types.py",),
        ("class EndocrineSignal",),
        "legacy_first_stage_fixture",
        "four_axis_fixture_value_shape",
        "legacy_endocrine_not_package_136_authority",
        ("legacy_authority_conflict", "free_form_modulation_notes"),
    ),
    _ConsumerDefinition(
        "legacy_fixed_circulation_endocrine_flow",
        ("ashl_core_v1/runtime/fixed_circulation_runner.py",),
        ("endocrine_signal_id", "thought_signal_id"),
        "legacy_fixed_circulation_demo",
        "deterministic_demo_dataflow",
        "legacy_endocrine_runtime_flow_forbidden",
        ("thought_path_influence", "body_intent_path_influence"),
    ),
    _ConsumerDefinition(
        "thought_signal_endocrine_reference_surface",
        ("ashl_core_v1/thought/types.py",),
        ("source_endocrine_signal_refs",),
        "thought_schema",
        "legacy_reference_field",
        "forbidden_thought_engine_surface",
        ("thought_engine_capability_forbidden",),
    ),
    _ConsumerDefinition(
        "bounded_capture_deadline",
        ("ashl_core_v1/runtime/bounded_capture_deadline_controller.py",),
        ("class BoundedCaptureDeadlineController", "request_stop"),
        "package_125_and_package_128_perception_lifecycle",
        "sensor_window_deadline_and_stop_authority",
        "forbidden_perception_lifecycle_surface",
        ("observation_extension_forbidden", "observation_stop_authority_preserved"),
    ),
    _ConsumerDefinition(
        "internal_visual_focus_policy",
        ("ashl_core_v1/runtime/internal_perception_focus_policy.py",),
        ("InternalPerceptionFocusPolicyDecision",),
        "package_127_focus_authority",
        "bounded_visual_focus_selection",
        "forbidden_attention_surface",
        ("attention_capability_frozen", "focus_change_forbidden"),
    ),
    _ConsumerDefinition(
        "structural_sufficiency_stop_policy",
        ("ashl_core_v1/runtime/observation_stop_policy.py",),
        ("ObservationStopPolicyDecision",),
        "package_128_stop_policy",
        "structural_evidence_stop_decision",
        "forbidden_perception_policy_surface",
        ("perception_capability_frozen", "stop_policy_authority_preserved"),
    ),
    _ConsumerDefinition(
        "teacher_gated_candidate_ordering",
        ("ashl_core_v1/task/advisory_readback_candidate_ordering_application.py",),
        ("compute_advisory_readback_ordering", "approved_for_candidate_ordering_change"),
        "teacher_gated_task_engine",
        "candidate_ordering_authority",
        "forbidden_candidate_ordering_surface",
        ("candidate_ordering_forbidden", "teacher_authority_preserved"),
    ),
    _ConsumerDefinition(
        "teacher_gated_selected_action",
        ("ashl_core_v1/task/teacher_gated_selected_action_application.py",),
        ("apply_teacher_gated_selected_action",),
        "teacher_gated_task_engine",
        "selected_action_authority",
        "forbidden_action_surface",
        ("action_preference_forbidden", "selected_action_forbidden"),
    ),
    _ConsumerDefinition(
        "memory_trace_store",
        ("ashl_core_v1/memory/trace_store.py",),
        ("list_memory_learning_traces", "list_memory_application_data"),
        "memory_system",
        "memory_trace_read_write_authority",
        "forbidden_memory_surface",
        ("memory_read_influence_forbidden", "memory_write_forbidden"),
    ),
    _ConsumerDefinition(
        "persistent_self_state_and_recovery",
        (
            "ashl_core_v1/state/persistent_self_state_schema.py",
            "ashl_core_v1/state/persistent_session_recovery_types.py",
        ),
        ("PersistentSelfStateRecord", "ActiveSelfStateHeadRecord"),
        "package_133_and_package_134_state_authorities",
        "opaque_identity_representation_and_structural_recovery",
        "forbidden_self_state_surface",
        ("self_state_content_forbidden", "cross_session_carry_forbidden"),
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
        "derived_status_not_a_modulation_consumer",
        ("runtime_status_relabel_forbidden", "operator_view_is_read_only"),
    ),
    _ConsumerDefinition(
        "raw_output_token_registry",
        ("ashl_core_v1/runtime/raw_output_token_registry.py",),
        ("build_raw_output_token_registry",),
        "package_122b_output_surface",
        "neutral_operator_output_token_registry",
        "forbidden_output_surface",
        ("output_content_forbidden", "output_timing_forbidden"),
    ),
    _ConsumerDefinition(
        "continuous_event_loop_budgets",
        ("ashl_core_v1/runtime/continuous_event_loop.py",),
        ("DEFAULT_MAX_DEPTH", "DEFAULT_MAX_FRAME_COUNT"),
        "bounded_runtime_continuity_demo",
        "event_depth_and_frame_budget",
        "forbidden_runtime_scheduler_surface",
        ("event_capability_expansion_forbidden", "scheduler_modulation_forbidden"),
    ),
    _ConsumerDefinition(
        AUDIT_ONLY_CONSUMER_ID,
        ("ashl_core_v1/endocrine/drive_modulation_types.py",),
        ("AUDIT_ONLY_CONSUMER_ID", "DriveModulationBoundarySnapshot"),
        "package_136_audit_harness",
        "nonproduction_scalar_counterfactual_surface",
        "audit_only_counterfactual_surface",
        ("not_a_production_runtime_consumer",),
        audit_only=True,
    ),
)


def build_drive_modulation_consumer_inventory(
    ashl_root: str | Path,
) -> tuple[DriveModulationConsumerInventoryRecord, ...]:
    root = Path(ashl_root).resolve()
    records: list[DriveModulationConsumerInventoryRecord] = []
    for definition in _DEFINITIONS:
        paths = tuple(root / item for item in definition.paths)
        if not all(path.is_file() for path in paths):
            missing = tuple(
                definition.paths[index]
                for index, path in enumerate(paths)
                if not path.is_file()
            )
            raise FileNotFoundError(f"Package 136 consumer inventory missing source: {missing}")
        texts = tuple(path.read_text(encoding="utf-8") for path in paths)
        combined = "\n".join(texts)
        if not all(marker in combined for marker in definition.markers):
            raise RuntimeError(
                f"Package 136 consumer inventory marker missing: {definition.surface_id}"
            )
        hashes = tuple(sha256_bytes(path.read_bytes()) for path in paths)
        payload: dict[str, Any] = {
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
            "source_record_refs": definition.paths,
        }
        digest = sha256_payload(
            {"schema_version": INVENTORY_SCHEMA_VERSION, **payload}
        )
        records.append(
            DriveModulationConsumerInventoryRecord(
                inventory_record_id=f"drive_modulation_consumer_inventory:{digest[:16]}",
                inventory_sha256=digest,
                schema_version=INVENTORY_SCHEMA_VERSION,
                created_at=utc_now(),
                **payload,
            )
        )
    return tuple(records)


def consumer_inventory_sha256(
    records: tuple[DriveModulationConsumerInventoryRecord, ...],
) -> str:
    return sha256_payload(
        tuple(
            (item.consumer_surface_id, item.inventory_sha256)
            for item in sorted(records, key=lambda record: record.consumer_surface_id)
        )
    )
