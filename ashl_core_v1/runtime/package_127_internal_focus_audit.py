"""Evidence-scoped final audit for Package 127."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ashl_core_v1.host_body.host_body_internal_action_choice import (
    ALLOWED_INTERNAL_ACTION_KINDS,
)
from ashl_core_v1.perception.perception_primitive_store import (
    PerceptionPrimitiveStore,
)
from ashl_core_v1.runtime.host_sensor_types import stable_id, utc_now
from ashl_core_v1.runtime.internal_perception_focus_types import (
    BASELINE_COMMIT,
    FOCUS_ACTION_KIND,
    PACKAGE_127_BLOCKED_STATUS,
    PACKAGE_127_PASS_STATUS,
    Package127InternalPerceptionFocusShiftAudit,
)
from ashl_core_v1.runtime.package_126_reacquisition_store import (
    Package126ReacquisitionStore,
)
from ashl_core_v1.runtime.package_127_internal_focus_store import (
    Package127InternalFocusStore,
)
from ashl_core_v1.runtime.perception_reacquisition_types import (
    BASELINE_COMMIT as PACKAGE_126_BASELINE_COMMIT,
)


PACKAGE_127_AUDIT_SCHEMA_VERSION = (
    "ashl_package_127_internal_perception_focus_shift_audit_v0"
)


def audit_package_127_internal_focus(
    *,
    state_dir: str | Path,
    append: bool = True,
) -> Package127InternalPerceptionFocusShiftAudit:
    path = Path(state_dir)
    store = Package127InternalFocusStore(path)
    reacquisition_store = Package126ReacquisitionStore(path)
    primitive_store = PerceptionPrimitiveStore(path)
    run = _latest_passed_run(
        store.list_payloads("package_127_real_run_records")
    )
    candidates = store.list_payloads("internal_focus_candidates")
    controls = store.latest_payload("package_127_control_results") or {}
    scores = store.list_payloads(
        "package_127_score_equivalence_records"
    )
    event_failures = (
        store.list_payloads("operator_event_delivery_failures")
        + reacquisition_store.list_payloads(
            "operator_event_delivery_failures"
        )
    )
    failures: list[str] = []

    def require(flag: bool, reason: str) -> bool:
        if not flag:
            failures.append(reason)
        return flag

    package_126_verified = require(
        PACKAGE_126_BASELINE_COMMIT
        == "acb543ed79a9d56bbf4a1660628200f8916497d2"
        and "capture_again" in ALLOWED_INTERNAL_ACTION_KINDS
        and "listen_again" in ALLOWED_INTERNAL_ACTION_KINDS,
        "package_126_baseline_not_verified",
    )
    package_125_verified = require(
        "extend_observation_window" in ALLOWED_INTERNAL_ACTION_KINDS,
        "package_125_baseline_not_verified",
    )
    qm0_verified = require(
        BASELINE_COMMIT
        == "65b3f4fd5ee73011d8fe8be061b8aa3b78079d43",
        "qm0_baseline_not_verified",
    )
    parent = dict(run.get("parent") or {})
    child = dict(run.get("child") or {})
    real_parent = require(
        bool(
            run
            and parent.get("screen_capture_session_id")
            and parent.get("host_state_capture_session_id")
            and parent.get("observation_window_id")
            and int(parent.get("required_windows_expected", 0)) > 0
            and int(parent.get("required_windows_complete", -1))
            == int(parent.get("required_windows_expected", 0))
        ),
        "real_parent_capture_not_verified",
    )
    visual_change: dict[str, Any] = {}
    try:
        if run.get("parent_visual_change_primitive_id"):
            visual_change = primitive_store.get_primitive(
                str(run["parent_visual_change_primitive_id"])
            )
    except KeyError:
        visual_change = {}
    changed_cells = tuple(
        visual_change.get("changed_grid_cells") or ()
    )
    actual_change = require(
        bool(
            visual_change.get("source_kind") == "screen"
            and len(changed_cells) >= 2
        ),
        "actual_visual_change_evidence_not_verified",
    )
    run_candidate_ids = set(run.get("focus_candidate_ids") or ())
    run_candidates = tuple(
        item
        for item in candidates
        if item.get("focus_candidate_id") in run_candidate_ids
    )
    candidate_count = len(run_candidates)
    candidate_lineage = require(
        bool(
            candidate_count >= 2
            and all(
                item.get("source_visual_change_primitive_id")
                == visual_change.get("visual_change_id")
                and item.get("reason_codes")
                == ["changed_grid_cell_present"]
                and item.get("semantic_label") is None
                and item.get("object_identity") is None
                and item.get("object_class") is None
                for item in run_candidates
            )
            and {
                (
                    int(item["grid_x"]),
                    int(item["grid_y"]),
                    float(item["difference_strength"]),
                )
                for item in run_candidates
            }.issubset(
                {
                    (
                        int(item["grid_x"]),
                        int(item["grid_y"]),
                        float(item["difference_strength"]),
                    )
                    for item in changed_cells
                }
            )
        ),
        "focus_candidates_not_grounded_in_changed_grid",
    )
    expected_top = (
        sorted(
            run_candidates,
            key=lambda item: (
                -float(item["difference_strength"]),
                int(item["grid_y"]),
                int(item["grid_x"]),
            ),
        )[0]
        if run_candidates
        else {}
    )
    deterministic = require(
        run.get("selection_rule")
        == "highest_difference_strength_then_grid_y_then_grid_x",
        "deterministic_selection_not_verified",
    )
    selected_highest = require(
        bool(
            expected_top
            and run.get("selected_candidate_id")
            == expected_top.get("focus_candidate_id")
            and int(run.get("selected_grid_x", -1))
            == int(expected_top.get("grid_x", -2))
            and int(run.get("selected_grid_y", -1))
            == int(expected_top.get("grid_y", -2))
        ),
        "selected_candidate_is_not_highest_difference",
    )
    authorization = require(
        bool(run.get("focus_authorization_id")),
        "focus_authorization_not_verified",
    )
    policy = require(
        run.get("focus_policy_decision") == "allow",
        "focus_policy_gate_not_verified",
    )
    action = require(
        bool(
            run.get("focus_internal_action_id")
            and run.get("focus_action_kind") == FOCUS_ACTION_KIND
            and FOCUS_ACTION_KIND in ALLOWED_INTERNAL_ACTION_KINDS
        ),
        "internal_focus_action_not_verified",
    )
    package_126_child = require(
        bool(
            run.get("package_126_child_window_used") is True
            and run.get("package_126_reacquisition_execution_id")
            and child.get("observation_window_id")
            and child.get("observation_window_id")
            != parent.get("observation_window_id")
            and reacquisition_store.get_payload(
                "reacquisition_capture_executions",
                str(run["package_126_reacquisition_execution_id"]),
            )
        )
        if run.get("package_126_reacquisition_execution_id")
        else False,
        "package_126_child_window_not_verified",
    )
    target_unchanged = require(
        run.get("raw_capture_target_unchanged") is True,
        "raw_capture_target_changed",
    )
    region_unchanged = require(
        run.get("raw_capture_region_unchanged") is True,
        "raw_capture_region_changed",
    )
    full_frame = require(
        bool(
            run.get("full_frame_capture_preserved") is True
            and run.get("full_frame_visual_primitive_id")
            and run.get("full_frame_perception_readable_data_id")
            and child.get("visual_primitive_refs")
            and child.get("visual_readable_data_refs")
        ),
        "full_frame_capture_not_preserved",
    )
    view_payload = {}
    try:
        if run.get("focused_region_view_id"):
            view_payload = store.get_payload(
                "focused_visual_region_views",
                str(run["focused_region_view_id"]),
            )
    except KeyError:
        view_payload = {}
    view_created = require(
        bool(
            view_payload
            and view_payload.get("raw_pixel_payload_present") is False
            and view_payload.get("image_crop_persisted") is False
            and view_payload.get("read_only_context") is True
        ),
        "focused_region_view_not_verified",
    )
    view_matches = require(
        bool(
            view_payload
            and int(view_payload.get("grid_x", -1))
            == int(run.get("selected_grid_x", -2))
            and int(view_payload.get("grid_y", -1))
            == int(run.get("selected_grid_y", -2))
            and view_payload.get("source_perception_readable_data_id")
            == run.get("full_frame_perception_readable_data_id")
        ),
        "focused_region_does_not_match_selection",
    )
    focused_evidence = require(
        bool(
            run.get("focused_region_new_evidence_present") is True
            and view_payload.get("source_cell_change_present") is True
        ),
        "focused_region_new_evidence_missing",
    )
    focus_child_count = int(run.get("focus_child_window_count", 0) or 0)
    require(
        focus_child_count == 1,
        "focus_child_window_count_not_one",
    )
    released = require(
        bool(
            run.get("focus_automatically_released") is True
            and run.get("focus_state") == "released"
            and run.get("focus_release_record_id")
        ),
        "focus_not_automatically_released",
    )
    counts = {
        name: int(child.get(name, -1))
        for name in (
            "required_lane_drop_count",
            "backpressure_fault_count",
            "capture_failure_count",
            "compile_failure_count",
            "flush_remaining_count",
        )
    }
    for name, value in counts.items():
        require(value == 0, f"child_{name}_nonzero")

    control_names = (
        "stable_control_passed",
        "authorization_off_control_passed",
        "tie_control_passed",
        "invalid_coordinate_control_passed",
        "wrong_session_control_passed",
        "transport_fault_control_passed",
        "second_shift_control_passed",
        "operator_stop_control_passed",
        "raw_crop_control_passed",
        "semantic_injection_control_passed",
    )
    for name in control_names:
        require(controls.get(name) is True, f"{name}_missing_or_failed")
    score_changed = bool(
        not scores
        or any(
            item.get("package_112_score_changed")
            or int(item.get("package_127_score_contribution", -1)) != 0
            or int(item.get("authoritative_score_before", -1))
            != int(item.get("authoritative_score_after", -2))
            for item in scores
        )
    )
    require(not score_changed, "package_112_score_equivalence_failed")
    require(not event_failures, "operator_event_delivery_failure")
    boundary_true_fields = (
        "memory_write_created",
        "working_readback_created",
        "evidence_sufficiency_runtime_created",
        "novelty_signal_created",
        "uncertainty_signal_created",
        "thought_engine_used",
        "endocrine_signal_used",
        "audio_focus_created",
        "camera_focus_created",
        "sensor_priority_runtime_created",
        "selected_action_created",
        "final_action_created",
        "direct_command_created",
        "external_control_created",
        "output_created",
        "object_recognition_created",
        "semantic_vision_created",
        "package_128_implemented",
        "package_129_implemented",
        "d_laplace_component_used",
        "dlm_1_implemented",
    )
    for name in boundary_true_fields:
        require(
            run.get(name) is False,
            f"forbidden_boundary_crossed:{name}",
        )
    require(
        all(
            int(run.get(name, -1)) == 0
            for name in (
                "llm_runtime_calls",
                "codex_runtime_calls",
                "network_runtime_calls",
            )
        ),
        "runtime_model_or_network_call_detected",
    )

    audit = Package127InternalPerceptionFocusShiftAudit(
        audit_id=stable_id("package_127_audit"),
        schema_version=PACKAGE_127_AUDIT_SCHEMA_VERSION,
        created_at=utc_now(),
        baseline_commit=BASELINE_COMMIT,
        package_126_baseline_verified=package_126_verified,
        package_125_baseline_verified=package_125_verified,
        qm0_baseline_verified=qm0_verified,
        real_parent_capture_verified=real_parent,
        actual_visual_change_evidence_verified=actual_change,
        focus_candidate_count=candidate_count,
        candidates_from_changed_grid_cells=candidate_lineage,
        deterministic_selection_verified=deterministic,
        selected_candidate_is_highest_difference=selected_highest,
        authorization_verified=authorization,
        policy_gate_verified=policy,
        internal_focus_action_created=action,
        action_kind_verified=action,
        package_126_child_window_used=package_126_child,
        raw_capture_target_unchanged=target_unchanged,
        raw_capture_region_unchanged=region_unchanged,
        full_frame_capture_preserved=full_frame,
        focused_region_view_created=view_created,
        focused_region_matches_selection=view_matches,
        focused_region_new_evidence_present=focused_evidence,
        focus_child_window_count=focus_child_count,
        focus_automatically_released=released,
        required_lane_drop_count=counts["required_lane_drop_count"],
        backpressure_fault_count=counts["backpressure_fault_count"],
        capture_failure_count=counts["capture_failure_count"],
        compile_failure_count=counts["compile_failure_count"],
        flush_remaining_count=counts["flush_remaining_count"],
        stable_control_passed=bool(
            controls.get("stable_control_passed")
        ),
        authorization_off_control_passed=bool(
            controls.get("authorization_off_control_passed")
        ),
        tie_control_passed=bool(controls.get("tie_control_passed")),
        invalid_coordinate_control_passed=bool(
            controls.get("invalid_coordinate_control_passed")
        ),
        wrong_session_control_passed=bool(
            controls.get("wrong_session_control_passed")
        ),
        transport_fault_control_passed=bool(
            controls.get("transport_fault_control_passed")
        ),
        second_shift_control_passed=bool(
            controls.get("second_shift_control_passed")
        ),
        operator_stop_control_passed=bool(
            controls.get("operator_stop_control_passed")
        ),
        raw_crop_control_passed=bool(
            controls.get("raw_crop_control_passed")
        ),
        semantic_injection_control_passed=bool(
            controls.get("semantic_injection_control_passed")
        ),
        package_112_score_changed=score_changed,
        memory_write_created=False,
        working_readback_created=False,
        evidence_sufficiency_runtime_created=False,
        novelty_signal_created=False,
        uncertainty_signal_created=False,
        thought_engine_used=False,
        endocrine_signal_used=False,
        audio_focus_created=False,
        camera_focus_created=False,
        sensor_priority_runtime_created=False,
        selected_action_created=False,
        final_action_created=False,
        direct_command_created=False,
        external_control_created=False,
        output_created=False,
        object_recognition_created=False,
        semantic_vision_created=False,
        package_128_implemented=False,
        package_129_implemented=False,
        d_laplace_component_used=False,
        dlm_1_implemented=False,
        llm_runtime_calls=0,
        codex_runtime_calls=0,
        network_runtime_calls=0,
        audit_status=(
            PACKAGE_127_PASS_STATUS
            if not failures
            else PACKAGE_127_BLOCKED_STATUS
        ),
        failure_reasons=tuple(dict.fromkeys(failures)),
        source_trace_refs=tuple(),
    )
    if append:
        store.append_record("package_127_audits", audit)
    return audit


def _latest_passed_run(
    runs: tuple[dict[str, Any], ...],
) -> dict[str, Any]:
    matches = tuple(
        item
        for item in runs
        if item.get("run_status")
        == "passed_real_internal_focus_shift"
    )
    return dict(matches[-1]) if matches else {}
