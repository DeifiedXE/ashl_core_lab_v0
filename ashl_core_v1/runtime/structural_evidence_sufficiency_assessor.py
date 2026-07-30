"""Deterministic structural contract, checkpoint, and assessment builders."""

from __future__ import annotations

from ashl_core_v1.runtime.host_sensor_types import (
    monotonic_ns,
    stable_id,
    utc_now,
)
from ashl_core_v1.runtime.structural_evidence_sufficiency_types import (
    CHECKPOINT_INTERVAL_NS,
    CONTRACT_KIND,
    MAXIMUM_CHECKPOINT_COUNT,
    MINIMUM_COMPLETE_ALIGNMENT_WINDOWS,
    MINIMUM_ELAPSED_NS,
    MINIMUM_POST_EVENT_COVERAGE_NS,
    REQUIRED_LANES,
    StructuralEvidenceCheckpoint,
    StructuralEvidenceSufficiencyAssessment,
    StructuralEvidenceSufficiencyContract,
)


CONTRACT_SCHEMA_VERSION = (
    "ashl_package_128_structural_evidence_sufficiency_contract_v0"
)
CHECKPOINT_SCHEMA_VERSION = (
    "ashl_package_128_structural_evidence_checkpoint_v0"
)
ASSESSMENT_SCHEMA_VERSION = (
    "ashl_package_128_structural_evidence_sufficiency_assessment_v0"
)


def validate_runtime_provenance(
    refs: tuple[str, ...] | list[str],
) -> None:
    forbidden = (
        "stimulus",
        "fixture",
        "schedule",
        "expected_stop",
        "expected_focus",
    )
    for ref in refs:
        lowered = str(ref).lower()
        if any(token in lowered for token in forbidden):
            raise ValueError(
                "stimulus ground truth is forbidden from runtime provenance"
            )


def create_structural_sufficiency_contract(
    *,
    runtime_session_id: str,
    perception_session_id: str,
    observation_window_id: str,
    focus_context_id: str,
    hard_deadline_event_time_ns: int,
    source_record_refs: tuple[str, ...],
    source_trace_refs: tuple[str, ...] = tuple(),
) -> StructuralEvidenceSufficiencyContract:
    validate_runtime_provenance(
        source_record_refs + source_trace_refs
    )
    return StructuralEvidenceSufficiencyContract(
        contract_id=stable_id("structural_sufficiency_contract"),
        schema_version=CONTRACT_SCHEMA_VERSION,
        created_at=utc_now(),
        runtime_session_id=runtime_session_id,
        perception_session_id=perception_session_id,
        observation_window_id=observation_window_id,
        contract_kind=CONTRACT_KIND,
        authorization_source="explicit_session_configuration",
        authorized_by="local_operator",
        required_lanes=REQUIRED_LANES,
        required_focus_context_id=focus_context_id,
        minimum_elapsed_ns=MINIMUM_ELAPSED_NS,
        minimum_complete_alignment_windows=(
            MINIMUM_COMPLETE_ALIGNMENT_WINDOWS
        ),
        minimum_post_event_coverage_ns=MINIMUM_POST_EVENT_COVERAGE_NS,
        require_focused_region_evidence=True,
        require_closed_visual_regions=True,
        require_no_open_visual_regions=True,
        require_full_frame_preserved=True,
        checkpoint_interval_ns=CHECKPOINT_INTERVAL_NS,
        maximum_checkpoint_count=MAXIMUM_CHECKPOINT_COUNT,
        hard_deadline_event_time_ns=int(hard_deadline_event_time_ns),
        contract_expires_at_window_end=True,
        semantic_goal=None,
        expected_object=None,
        expected_label=None,
        source_record_refs=source_record_refs,
        source_trace_refs=source_trace_refs,
    )


def create_structural_evidence_checkpoint(
    *,
    contract: StructuralEvidenceSufficiencyContract,
    checkpoint_index: int,
    evaluated_at_event_time_ns: int,
    elapsed_observation_ns: int,
    complete_alignment_window_count: int,
    partial_alignment_window_count: int,
    focused_region_view_id: str,
    full_frame_perception_readable_data_refs: tuple[str, ...],
    focused_region_evidence_record_count: int,
    observed_visual_region_refs: tuple[str, ...],
    open_visual_region_refs: tuple[str, ...],
    closed_visual_span_refs: tuple[str, ...],
    latest_visual_closure_event_time_ns: int | None,
    latest_complete_source_coverage_event_time_ns: int,
    screen_source_coverage_present: bool,
    host_state_source_coverage_present: bool,
    required_lane_drop_count: int = 0,
    backpressure_fault_count: int = 0,
    capture_failure_count: int = 0,
    compile_failure_count: int = 0,
    source_record_refs: tuple[str, ...] = tuple(),
    source_trace_refs: tuple[str, ...] = tuple(),
    runtime_session_id: str | None = None,
    perception_session_id: str | None = None,
    observation_window_id: str | None = None,
    evaluated_at_processing_time_ns: int | None = None,
) -> StructuralEvidenceCheckpoint:
    validate_runtime_provenance(
        source_record_refs + source_trace_refs
    )
    event_time = int(evaluated_at_event_time_ns)
    coverage_boundary = int(
        latest_complete_source_coverage_event_time_ns
    )
    if coverage_boundary > event_time:
        raise ValueError(
            "source coverage boundary cannot exceed checkpoint event time"
        )
    closure = latest_visual_closure_event_time_ns
    post_event_coverage_ns = (
        max(
            0,
            coverage_boundary - int(closure),
        )
        if closure is not None
        else 0
    )
    return StructuralEvidenceCheckpoint(
        checkpoint_id=stable_id("structural_evidence_checkpoint"),
        schema_version=CHECKPOINT_SCHEMA_VERSION,
        created_at=utc_now(),
        contract_id=contract.contract_id,
        runtime_session_id=(
            runtime_session_id or contract.runtime_session_id
        ),
        perception_session_id=(
            perception_session_id or contract.perception_session_id
        ),
        observation_window_id=(
            observation_window_id or contract.observation_window_id
        ),
        checkpoint_index=int(checkpoint_index),
        evaluated_at_event_time_ns=event_time,
        evaluated_at_processing_time_ns=(
            int(evaluated_at_processing_time_ns)
            if evaluated_at_processing_time_ns is not None
            else monotonic_ns()
        ),
        elapsed_observation_ns=int(elapsed_observation_ns),
        remaining_to_hard_deadline_ns=max(
            0,
            contract.hard_deadline_event_time_ns - event_time,
        ),
        complete_alignment_window_count=int(
            complete_alignment_window_count
        ),
        partial_alignment_window_count=int(
            partial_alignment_window_count
        ),
        focused_region_view_id=focused_region_view_id,
        full_frame_perception_readable_data_refs=(
            full_frame_perception_readable_data_refs
        ),
        focused_region_evidence_record_count=int(
            focused_region_evidence_record_count
        ),
        observed_visual_region_refs=observed_visual_region_refs,
        open_visual_region_refs=open_visual_region_refs,
        closed_visual_span_refs=closed_visual_span_refs,
        latest_visual_closure_event_time_ns=closure,
        post_event_coverage_ns=post_event_coverage_ns,
        screen_source_coverage_present=bool(
            screen_source_coverage_present
        ),
        host_state_source_coverage_present=bool(
            host_state_source_coverage_present
        ),
        required_lane_drop_count=int(required_lane_drop_count),
        backpressure_fault_count=int(backpressure_fault_count),
        capture_failure_count=int(capture_failure_count),
        compile_failure_count=int(compile_failure_count),
        semantic_label=None,
        uncertainty_score=None,
        confidence_score=None,
        source_record_refs=source_record_refs,
        source_trace_refs=source_trace_refs,
    )


def assess_structural_evidence(
    *,
    contract: StructuralEvidenceSufficiencyContract,
    checkpoint: StructuralEvidenceCheckpoint,
    active_window: bool = True,
    focus_context_valid: bool = True,
) -> StructuralEvidenceSufficiencyAssessment:
    lineage_integrity = all(
        (
            checkpoint.contract_id == contract.contract_id,
            checkpoint.runtime_session_id == contract.runtime_session_id,
            checkpoint.perception_session_id
            == contract.perception_session_id,
            checkpoint.observation_window_id
            == contract.observation_window_id,
            bool(checkpoint.focused_region_view_id),
            bool(checkpoint.full_frame_perception_readable_data_refs),
            active_window,
            focus_context_valid,
        )
    )
    transport_integrity = not any(
        (
            checkpoint.required_lane_drop_count,
            checkpoint.backpressure_fault_count,
            checkpoint.capture_failure_count,
            checkpoint.compile_failure_count,
        )
    )
    clock_integrity = bool(
        checkpoint.evaluated_at_event_time_ns > 0
        and checkpoint.evaluated_at_processing_time_ns > 0
        and checkpoint.elapsed_observation_ns >= 0
        and checkpoint.evaluated_at_event_time_ns
        <= contract.hard_deadline_event_time_ns
    )
    minimum_elapsed = (
        checkpoint.elapsed_observation_ns
        >= contract.minimum_elapsed_ns
    )
    minimum_windows = (
        checkpoint.complete_alignment_window_count
        >= contract.minimum_complete_alignment_windows
    )
    focused_evidence = (
        checkpoint.focused_region_evidence_record_count > 0
    )
    full_frame = bool(
        checkpoint.full_frame_perception_readable_data_refs
    )
    observed_region = bool(checkpoint.observed_visual_region_refs)
    all_closed = bool(
        observed_region
        and checkpoint.closed_visual_span_refs
        and len(checkpoint.closed_visual_span_refs)
        >= len(checkpoint.observed_visual_region_refs)
        and not checkpoint.open_visual_region_refs
    )
    no_open = not checkpoint.open_visual_region_refs
    post_event = (
        checkpoint.latest_visual_closure_event_time_ns is not None
        and checkpoint.post_event_coverage_ns
        >= contract.minimum_post_event_coverage_ns
    )
    lane_coverage = bool(
        checkpoint.screen_source_coverage_present
        and checkpoint.host_state_source_coverage_present
    )
    gates = (
        minimum_elapsed,
        minimum_windows,
        focused_evidence,
        full_frame,
        observed_region,
        all_closed,
        no_open,
        post_event,
        lane_coverage,
        transport_integrity,
        clock_integrity,
        lineage_integrity,
    )
    satisfied = all(gates)
    hard_deadline = (
        checkpoint.remaining_to_hard_deadline_ns == 0
    )
    failures: list[str] = []
    gate_names = (
        "minimum_elapsed_not_met",
        "minimum_complete_windows_not_met",
        "focused_region_evidence_missing",
        "full_frame_not_preserved",
        "observed_visual_region_missing",
        "visual_regions_not_closed",
        "open_visual_region_remaining",
        "post_event_coverage_not_met",
        "required_lane_coverage_incomplete",
        "transport_integrity_invalid",
        "clock_integrity_invalid",
        "lineage_integrity_invalid",
    )
    failures.extend(
        name for name, gate in zip(gate_names, gates) if not gate
    )
    if not lineage_integrity:
        status = "blocked_invalid_lineage"
    elif not transport_integrity:
        status = "blocked_transport_failure"
    elif satisfied:
        status = "sufficient"
        failures.clear()
    elif hard_deadline:
        status = "inconclusive_at_hard_deadline"
    else:
        status = "insufficient_continue"
    return StructuralEvidenceSufficiencyAssessment(
        assessment_id=stable_id("structural_evidence_assessment"),
        schema_version=ASSESSMENT_SCHEMA_VERSION,
        created_at=utc_now(),
        contract_id=contract.contract_id,
        checkpoint_id=checkpoint.checkpoint_id,
        assessment_status=status,
        minimum_elapsed_met=minimum_elapsed,
        minimum_complete_windows_met=minimum_windows,
        focused_region_evidence_present=focused_evidence,
        full_frame_preserved=full_frame,
        observed_visual_region_present=observed_region,
        all_visual_regions_closed=all_closed,
        no_open_visual_region_remaining=no_open,
        post_event_coverage_met=post_event,
        required_lane_coverage_complete=lane_coverage,
        transport_integrity_valid=transport_integrity,
        clock_integrity_valid=clock_integrity,
        lineage_integrity_valid=lineage_integrity,
        contract_satisfied=satisfied,
        semantic_understanding_claimed=False,
        recognition_claimed=False,
        certainty_claimed=False,
        failure_reasons=tuple(failures),
        source_record_refs=(
            contract.contract_id,
            checkpoint.checkpoint_id,
        ),
        source_trace_refs=tuple(
            dict.fromkeys(
                contract.source_trace_refs
                + checkpoint.source_trace_refs
            )
        ),
    )
