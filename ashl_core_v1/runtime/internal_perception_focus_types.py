"""Immutable records for Package 127 bounded internal visual focus."""

from __future__ import annotations

import math
from dataclasses import dataclass, fields
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import plain


BASELINE_COMMIT = "65b3f4fd5ee73011d8fe8be061b8aa3b78079d43"
PACKAGE_127_PASS_STATUS = "passed_internal_perception_focus_shift_v0"
PACKAGE_127_BLOCKED_STATUS = "blocked_internal_perception_focus_shift_v0"
FOCUS_ACTION_KIND = "shift_internal_perception_focus"
FOCUS_SELECTION_RULE = (
    "highest_difference_strength_then_grid_y_then_grid_x"
)
FOCUS_SCOPE = "screen_visual_grid_region"
MAXIMUM_FOCUS_CANDIDATES = 16
DEFAULT_DIFFERENCE_STRENGTH_FLOOR = 0.08


def _record_dict(record: Any) -> dict[str, object]:
    return {
        field.name: plain(getattr(record, field.name))
        for field in fields(record)
    }


def _tuple_of_str(value: Any) -> tuple[str, ...]:
    return tuple(str(item) for item in (value or ()))


def _normalize_refs(record: Any, *names: str) -> None:
    for name in names:
        object.__setattr__(
            record,
            name,
            _tuple_of_str(getattr(record, name)),
        )


@dataclass(frozen=True)
class InternalPerceptionFocusCandidate:
    focus_candidate_id: str
    schema_version: str
    created_at: str
    parent_runtime_session_id: str
    parent_perception_session_id: str
    parent_observation_window_id: str
    source_visual_change_primitive_id: str
    source_visual_frame_primitive_id: str
    source_grid_width: int
    source_grid_height: int
    grid_x: int
    grid_y: int
    difference_strength: float
    reason_codes: tuple[str, ...]
    semantic_label: None
    object_identity: None
    object_class: None
    memory_used: bool
    endocrine_signal_used: bool
    thought_engine_used: bool
    uncertainty_signal_used: bool
    novelty_signal_used: bool
    candidate_status: str
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.reason_codes != ("changed_grid_cell_present",):
            raise ValueError("Package 127 candidate reason is fixed")
        if any(
            value is not None
            for value in (
                self.semantic_label,
                self.object_identity,
                self.object_class,
            )
        ):
            raise ValueError("focus candidate semantic fields must remain null")
        if any(
            (
                self.memory_used,
                self.endocrine_signal_used,
                self.thought_engine_used,
                self.uncertainty_signal_used,
                self.novelty_signal_used,
            )
        ):
            raise ValueError("focus candidate may use only changed-grid evidence")
        if self.source_grid_width <= 0 or self.source_grid_height <= 0:
            raise ValueError("focus candidate requires positive grid geometry")
        if not 0 <= self.grid_x < self.source_grid_width:
            raise ValueError("focus candidate grid_x is outside source geometry")
        if not 0 <= self.grid_y < self.source_grid_height:
            raise ValueError("focus candidate grid_y is outside source geometry")
        if not math.isfinite(float(self.difference_strength)):
            raise ValueError("focus candidate difference must be finite")
        if self.candidate_status != "eligible":
            raise ValueError("stored focus candidates must be eligible")
        if not (
            self.source_visual_change_primitive_id
            and self.source_visual_frame_primitive_id
            and self.parent_runtime_session_id
            and self.parent_perception_session_id
            and self.parent_observation_window_id
            and self.source_record_refs
        ):
            raise ValueError("focus candidate source lineage is incomplete")
        _normalize_refs(
            self,
            "reason_codes",
            "source_record_refs",
            "source_trace_refs",
        )

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class InternalPerceptionFocusCandidateBatch:
    focus_candidate_batch_id: str
    schema_version: str
    created_at: str
    parent_observation_window_id: str
    source_visual_change_primitive_id: str
    difference_strength_floor: float
    changed_grid_cell_count: int
    eligible_cell_count: int
    candidate_ids: tuple[str, ...]
    omitted_candidate_count: int
    maximum_candidate_count: int
    candidate_count: int
    stable_frame: bool
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not math.isfinite(float(self.difference_strength_floor)):
            raise ValueError("focus candidate floor must be finite")
        if self.maximum_candidate_count != MAXIMUM_FOCUS_CANDIDATES:
            raise ValueError("Package 127 candidate limit must remain 16")
        if self.candidate_count != len(self.candidate_ids):
            raise ValueError("focus candidate batch count mismatch")
        if self.candidate_count > self.maximum_candidate_count:
            raise ValueError("focus candidate limit exceeded")
        if any(
            value < 0
            for value in (
                self.changed_grid_cell_count,
                self.eligible_cell_count,
                self.omitted_candidate_count,
                self.candidate_count,
            )
        ):
            raise ValueError("focus candidate counts cannot be negative")
        if self.stable_frame != (self.changed_grid_cell_count == 0):
            raise ValueError("stable-frame status must reflect source evidence")
        _normalize_refs(
            self,
            "candidate_ids",
            "source_record_refs",
            "source_trace_refs",
        )

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class InternalPerceptionFocusSelection:
    focus_selection_id: str
    schema_version: str
    created_at: str
    parent_observation_window_id: str
    candidate_ids: tuple[str, ...]
    selected_candidate_id: str | None
    selection_rule: str
    selected_grid_x: int | None
    selected_grid_y: int | None
    selected_difference_strength: float | None
    candidate_set_preserved: bool
    deterministic_tie_break_used: bool
    selection_status: str
    failure_reasons: tuple[str, ...]
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.selection_rule != FOCUS_SELECTION_RULE:
            raise ValueError("invalid Package 127 selection rule")
        if not self.candidate_set_preserved:
            raise ValueError("focus candidate set must remain preserved")
        if self.selection_status not in {
            "selected",
            "no_candidate",
            "blocked",
            "cancelled",
        }:
            raise ValueError("invalid focus selection status")
        if self.selection_status == "selected":
            if (
                self.selected_candidate_id not in self.candidate_ids
                or self.selected_grid_x is None
                or self.selected_grid_y is None
                or self.selected_difference_strength is None
            ):
                raise ValueError("selected focus candidate is incomplete")
        elif any(
            value is not None
            for value in (
                self.selected_candidate_id,
                self.selected_grid_x,
                self.selected_grid_y,
                self.selected_difference_strength,
            )
        ):
            raise ValueError("unselected focus result cannot name a region")
        _normalize_refs(
            self,
            "candidate_ids",
            "failure_reasons",
            "source_record_refs",
            "source_trace_refs",
        )

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class InternalPerceptionFocusAuthorization:
    authorization_id: str
    schema_version: str
    created_at: str
    parent_runtime_session_id: str
    parent_perception_session_id: str
    parent_observation_window_id: str
    authorization_source: str
    authorized_by: str
    allowed_focus_scope: str
    maximum_focus_shift_count: int
    maximum_focused_child_windows: int
    same_raw_capture_target_required: bool
    full_frame_capture_required: bool
    expires_at_chain_end: bool
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if (
            self.authorization_source != "explicit_session_configuration"
            or self.authorized_by != "local_operator"
            or self.allowed_focus_scope
            != "screen_visual_grid_region_only"
        ):
            raise ValueError("invalid Package 127 focus authorization")
        if (
            self.maximum_focus_shift_count != 1
            or self.maximum_focused_child_windows != 1
        ):
            raise ValueError("Package 127 permits one focused child only")
        if not (
            self.same_raw_capture_target_required
            and self.full_frame_capture_required
            and self.expires_at_chain_end
        ):
            raise ValueError("focus authorization must preserve capture bounds")
        _normalize_refs(self, "source_record_refs", "source_trace_refs")

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class InternalPerceptionFocusPolicyDecision:
    policy_decision_id: str
    schema_version: str
    created_at: str
    focus_selection_id: str
    authorization_id: str
    decision: str
    authorization_valid: bool
    selected_candidate_valid: bool
    source_lineage_valid: bool
    grid_coordinate_valid: bool
    focus_budget_available: bool
    parent_window_completed_clean: bool
    transport_integrity_valid: bool
    operator_stop_absent: bool
    failure_reasons: tuple[str, ...]
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.decision not in {"allow", "block", "cancelled", "expired"}:
            raise ValueError("invalid focus policy decision")
        gates = (
            self.authorization_valid,
            self.selected_candidate_valid,
            self.source_lineage_valid,
            self.grid_coordinate_valid,
            self.focus_budget_available,
            self.parent_window_completed_clean,
            self.transport_integrity_valid,
            self.operator_stop_absent,
        )
        if self.decision == "allow" and (
            not all(gates) or self.failure_reasons
        ):
            raise ValueError("allowed focus decision requires every gate")
        if self.decision != "allow" and not self.failure_reasons:
            raise ValueError("blocked focus decision requires a reason")
        _normalize_refs(
            self,
            "failure_reasons",
            "source_record_refs",
            "source_trace_refs",
        )

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class InternalPerceptionFocusPlan:
    focus_plan_id: str
    schema_version: str
    created_at: str
    policy_decision_id: str
    parent_observation_window_id: str
    selected_candidate_id: str
    focus_scope: str
    grid_x: int
    grid_y: int
    grid_width: int
    grid_height: int
    normalized_left: float
    normalized_top: float
    normalized_right: float
    normalized_bottom: float
    maximum_child_window_count: int
    raw_capture_region_changed: bool
    raw_capture_target_changed: bool
    full_frame_capture_preserved: bool
    semantic_label: None
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.focus_scope != FOCUS_SCOPE:
            raise ValueError("Package 127 focus scope is visual grid only")
        if self.grid_width <= 0 or self.grid_height <= 0:
            raise ValueError("focus plan requires positive grid geometry")
        if not 0 <= self.grid_x < self.grid_width:
            raise ValueError("focus plan grid_x is invalid")
        if not 0 <= self.grid_y < self.grid_height:
            raise ValueError("focus plan grid_y is invalid")
        bounds = (
            self.normalized_left,
            self.normalized_top,
            self.normalized_right,
            self.normalized_bottom,
        )
        if not all(math.isfinite(value) and 0.0 <= value <= 1.0 for value in bounds):
            raise ValueError("focus plan normalized bounds are invalid")
        if not (
            self.normalized_left < self.normalized_right
            and self.normalized_top < self.normalized_bottom
        ):
            raise ValueError("focus plan normalized bounds are empty")
        expected = (
            self.grid_x / self.grid_width,
            self.grid_y / self.grid_height,
            (self.grid_x + 1) / self.grid_width,
            (self.grid_y + 1) / self.grid_height,
        )
        if any(abs(actual - target) > 1e-12 for actual, target in zip(bounds, expected)):
            raise ValueError("focus bounds must derive from source grid geometry")
        if (
            self.maximum_child_window_count != 1
            or self.raw_capture_region_changed
            or self.raw_capture_target_changed
            or not self.full_frame_capture_preserved
            or self.semantic_label is not None
        ):
            raise ValueError("focus plan cannot alter or semantically label capture")
        _normalize_refs(self, "source_record_refs", "source_trace_refs")

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class InternalPerceptionFocusShiftAction:
    internal_action_id: str
    schema_version: str
    created_at: str
    action_kind: str
    focus_plan_id: str
    parent_observation_window_id: str
    internal_only: bool
    external_side_effect: bool
    sensor_target_changed: bool
    sensor_configuration_changed: bool
    screen_region_changed: bool
    selected_action_created: bool
    final_action_created: bool
    direct_command_created: bool
    action_source: str
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if (
            self.action_kind != FOCUS_ACTION_KIND
            or self.action_source != "bounded_low_level_visual_change_policy"
            or not self.internal_only
        ):
            raise ValueError("invalid Package 127 internal action")
        if any(
            (
                self.external_side_effect,
                self.sensor_target_changed,
                self.sensor_configuration_changed,
                self.screen_region_changed,
                self.selected_action_created,
                self.final_action_created,
                self.direct_command_created,
            )
        ):
            raise ValueError("focus shift cannot create external action effects")
        _normalize_refs(self, "source_record_refs", "source_trace_refs")

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class FocusedVisualRegionView:
    focused_region_view_id: str
    schema_version: str
    created_at: str
    focus_plan_id: str
    child_runtime_session_id: str
    child_perception_session_id: str
    child_observation_window_id: str
    source_visual_frame_primitive_id: str
    source_perception_readable_data_id: str
    grid_x: int
    grid_y: int
    luminance_mean: float
    contrast_value: float
    edge_density_value: float
    source_cell_change_present: bool
    raw_pixel_payload_present: bool
    image_crop_persisted: bool
    semantic_label: None
    object_identity: None
    read_only_context: bool
    action_selection_authority: bool
    memory_write_authority: bool
    scoring_authority: bool
    output_authority: bool
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.grid_x < 0 or self.grid_y < 0:
            raise ValueError("focused region coordinates cannot be negative")
        if not all(
            math.isfinite(float(value))
            for value in (
                self.luminance_mean,
                self.contrast_value,
                self.edge_density_value,
            )
        ):
            raise ValueError("focused region values must be finite")
        if any(
            (
                self.raw_pixel_payload_present,
                self.image_crop_persisted,
                self.action_selection_authority,
                self.memory_write_authority,
                self.scoring_authority,
                self.output_authority,
            )
        ):
            raise ValueError("focused region view must remain read-only")
        if (
            self.semantic_label is not None
            or self.object_identity is not None
            or not self.read_only_context
        ):
            raise ValueError("focused region cannot contain semantics")
        _normalize_refs(self, "source_record_refs", "source_trace_refs")

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class InternalPerceptionFocusContextSidecar:
    focus_context_id: str
    schema_version: str
    created_at: str
    child_perception_session_id: str
    child_observation_window_id: str
    focus_plan_id: str
    focused_region_view_id: str
    full_frame_perception_readable_data_id: str
    focus_state: str
    active_from_event_time_ns: int
    active_until_event_time_ns: int
    automatically_released: bool
    read_only_context: bool
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.focus_state not in {"focused", "released", "interrupted"}:
            raise ValueError("invalid focus sidecar state")
        if self.active_until_event_time_ns < self.active_from_event_time_ns:
            raise ValueError("focus sidecar interval is inverted")
        if not self.full_frame_perception_readable_data_id:
            raise ValueError("full-frame readable data must remain attached")
        if not self.read_only_context:
            raise ValueError("focus sidecar must remain read-only")
        if self.focus_state == "released" and not self.automatically_released:
            raise ValueError("completed focus must release automatically")
        _normalize_refs(self, "source_record_refs", "source_trace_refs")

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class InternalPerceptionFocusReleaseRecord:
    focus_release_record_id: str
    schema_version: str
    created_at: str
    focus_context_id: str
    child_observation_window_id: str
    previous_focus_state: str
    new_focus_state: str
    release_reason: str
    child_window_count: int
    history_preserved: bool
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.previous_focus_state not in {"focused", "interrupted"}:
            raise ValueError("focus release requires an active prior state")
        if (
            self.new_focus_state != "released"
            or self.child_window_count != 1
            or not self.history_preserved
        ):
            raise ValueError("Package 127 focus must release after one child")
        _normalize_refs(self, "source_record_refs", "source_trace_refs")

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package127ScoreEquivalenceRecord:
    score_equivalence_record_id: str
    schema_version: str
    created_at: str
    parent_observation_window_id: str
    authoritative_score_before: int
    authoritative_score_after: int
    package_127_score_contribution: int
    package_112_score_changed: bool
    focus_context_read_only: bool
    source_record_refs: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if (
            self.package_127_score_contribution != 0
            or self.package_112_score_changed
            or self.authoritative_score_before != self.authoritative_score_after
            or not self.focus_context_read_only
        ):
            raise ValueError("Package 127 must not affect Package 112 scoring")
        _normalize_refs(self, "source_record_refs", "source_trace_refs")

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)


@dataclass(frozen=True)
class Package127InternalPerceptionFocusShiftAudit:
    audit_id: str
    schema_version: str
    created_at: str
    baseline_commit: str
    package_126_baseline_verified: bool
    package_125_baseline_verified: bool
    qm0_baseline_verified: bool
    real_parent_capture_verified: bool
    actual_visual_change_evidence_verified: bool
    focus_candidate_count: int
    candidates_from_changed_grid_cells: bool
    deterministic_selection_verified: bool
    selected_candidate_is_highest_difference: bool
    authorization_verified: bool
    policy_gate_verified: bool
    internal_focus_action_created: bool
    action_kind_verified: bool
    package_126_child_window_used: bool
    raw_capture_target_unchanged: bool
    raw_capture_region_unchanged: bool
    full_frame_capture_preserved: bool
    focused_region_view_created: bool
    focused_region_matches_selection: bool
    focused_region_new_evidence_present: bool
    focus_child_window_count: int
    focus_automatically_released: bool
    required_lane_drop_count: int
    backpressure_fault_count: int
    capture_failure_count: int
    compile_failure_count: int
    flush_remaining_count: int
    stable_control_passed: bool
    authorization_off_control_passed: bool
    tie_control_passed: bool
    invalid_coordinate_control_passed: bool
    wrong_session_control_passed: bool
    transport_fault_control_passed: bool
    second_shift_control_passed: bool
    operator_stop_control_passed: bool
    raw_crop_control_passed: bool
    semantic_injection_control_passed: bool
    package_112_score_changed: bool
    memory_write_created: bool
    working_readback_created: bool
    evidence_sufficiency_runtime_created: bool
    novelty_signal_created: bool
    uncertainty_signal_created: bool
    thought_engine_used: bool
    endocrine_signal_used: bool
    audio_focus_created: bool
    camera_focus_created: bool
    sensor_priority_runtime_created: bool
    selected_action_created: bool
    final_action_created: bool
    direct_command_created: bool
    external_control_created: bool
    output_created: bool
    object_recognition_created: bool
    semantic_vision_created: bool
    package_128_implemented: bool
    package_129_implemented: bool
    d_laplace_component_used: bool
    dlm_1_implemented: bool
    llm_runtime_calls: int
    codex_runtime_calls: int
    network_runtime_calls: int
    audit_status: str
    failure_reasons: tuple[str, ...]
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.baseline_commit != BASELINE_COMMIT:
            raise ValueError("Package 127 baseline commit mismatch")
        if self.audit_status not in {
            PACKAGE_127_PASS_STATUS,
            PACKAGE_127_BLOCKED_STATUS,
        }:
            raise ValueError("invalid Package 127 audit status")
        if self.audit_status == PACKAGE_127_PASS_STATUS and self.failure_reasons:
            raise ValueError("passing Package 127 audit cannot contain failures")
        _normalize_refs(self, "failure_reasons", "source_trace_refs")

    def to_dict(self) -> dict[str, object]:
        return _record_dict(self)
