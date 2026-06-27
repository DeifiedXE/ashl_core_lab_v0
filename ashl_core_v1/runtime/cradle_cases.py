"""Fixed multi-case cradle circulation samples for ASHL Core v1."""

from __future__ import annotations

from typing import Any

from ashl_core_v1.body import BodyActionSignal
from ashl_core_v1.endocrine import EndocrineSignal
from ashl_core_v1.lesson import (
    LearningDigest,
    LearningReviewRecord,
    ReviewedLearningDigest,
)
from ashl_core_v1.memory import (
    MemoryApplicationData,
    MemoryLearningTrace,
    MemoryRoutingTrace,
)
from ashl_core_v1.perception import PerceptionReadableData
from ashl_core_v1.runtime.manual_samples import build_blocked_manual_circulation_sample
from ashl_core_v1.thought import InfluenceTrace, ThoughtReadTrace, ThoughtSignal


CRADLE_CASE_IDS = (
    "blocked_front_obstacle",
    "success_front_step",
    "unknown_feedback",
    "teacher_rejected",
    "teacher_deferred",
    "conflict_detected",
    "stale_learning",
    "superseded_learning",
)

_CASE_SPECS: dict[str, dict[str, object]] = {
    "success_front_step": {
        "readable_type": "action_success",
        "readable_payload": {"observed": "success", "position": "front"},
        "review_status": "approved",
        "memory_entry_allowed": True,
        "routing_status": "routed",
        "memory_layer_target": "working",
        "body_action_signal_type": "continue_or_observe",
        "expected_next_feedback_kind": "next_observation",
        "influence_visible": True,
        "digest_type": "success_event",
        "digest_payload": {
            "event": "front_step_succeeded",
            "suggested_learning": "front_step_can_continue_in_same_context",
        },
        "memory_items": (
            "front step succeeded",
            "continuation can remain available in same context",
        ),
    },
    "unknown_feedback": {
        "readable_type": "unknown_feedback",
        "readable_payload": {"observed": "unknown", "position": "front"},
        "review_status": "needs_more_evidence",
        "memory_entry_allowed": False,
        "routing_status": "held_for_review",
        "memory_layer_target": "none",
        "body_action_signal_type": "observe",
        "expected_next_feedback_kind": "more_evidence",
        "influence_visible": False,
        "digest_type": "unknown_feedback_event",
        "digest_payload": {
            "event": "feedback_insufficient",
            "suggested_learning": "more_evidence_required_before_memory_entry",
        },
        "memory_items": (
            "feedback was insufficient",
            "keep observation pending until more evidence exists",
        ),
    },
    "teacher_rejected": {
        "readable_type": "teacher_rejected_learning",
        "readable_payload": {"observed": "rejected", "position": "front"},
        "review_status": "rejected",
        "memory_entry_allowed": False,
        "routing_status": "rejected",
        "memory_layer_target": "none",
        "body_action_signal_type": "wait",
        "expected_next_feedback_kind": "teacher_followup",
        "influence_visible": False,
        "digest_type": "rejected_learning_event",
        "digest_payload": {
            "event": "teacher_rejected_learning",
            "suggested_learning": "do_not_apply_this_learning",
        },
        "memory_items": (
            "learning was rejected by teacher",
            "do not use rejected learning for memory application",
        ),
    },
    "teacher_deferred": {
        "readable_type": "teacher_deferred_learning",
        "readable_payload": {"observed": "deferred", "position": "front"},
        "review_status": "deferred",
        "memory_entry_allowed": False,
        "routing_status": "deferred",
        "memory_layer_target": "none",
        "body_action_signal_type": "wait",
        "expected_next_feedback_kind": "teacher_followup",
        "influence_visible": False,
        "digest_type": "deferred_learning_event",
        "digest_payload": {
            "event": "teacher_deferred_learning",
            "suggested_learning": "wait_for_later_teacher_decision",
        },
        "memory_items": (
            "teacher deferred the learning decision",
            "hold learning outside active memory application",
        ),
    },
    "conflict_detected": {
        "readable_type": "conflicting_feedback",
        "readable_payload": {"observed": "conflict", "position": "front"},
        "review_status": "conflict_detected",
        "memory_entry_allowed": False,
        "routing_status": "conflict_detected",
        "memory_layer_target": "none",
        "body_action_signal_type": "observe_or_adjust",
        "expected_next_feedback_kind": "clarifying_observation",
        "influence_visible": False,
        "digest_type": "conflict_event",
        "digest_payload": {
            "event": "conflicting_feedback_detected",
            "suggested_learning": "resolve_conflict_before_memory_entry",
        },
        "memory_items": (
            "feedback conflict was detected",
            "observe or adjust before trusting this learning",
        ),
    },
    "stale_learning": {
        "readable_type": "stale_learning_signal",
        "readable_payload": {"observed": "stale", "position": "front"},
        "review_status": "approved",
        "memory_entry_allowed": True,
        "routing_status": "stale",
        "memory_layer_target": "none",
        "body_action_signal_type": "observe",
        "expected_next_feedback_kind": "fresh_observation",
        "influence_visible": False,
        "digest_type": "stale_learning_event",
        "digest_payload": {
            "event": "learning_marked_stale",
            "suggested_learning": "approved_but_do_not_route_to_active_layer",
        },
        "memory_items": (
            "learning was approved but stale",
            "keep trace visible without active routing",
        ),
    },
    "superseded_learning": {
        "readable_type": "superseded_learning_signal",
        "readable_payload": {"observed": "superseded", "position": "front"},
        "review_status": "approved",
        "memory_entry_allowed": True,
        "routing_status": "superseded",
        "memory_layer_target": "none",
        "body_action_signal_type": "observe",
        "expected_next_feedback_kind": "fresh_observation",
        "influence_visible": False,
        "digest_type": "superseded_learning_event",
        "digest_payload": {
            "event": "learning_superseded",
            "suggested_learning": "approved_but_replaced_by_later_learning",
        },
        "memory_items": (
            "learning was approved but superseded",
            "later learning replaces active use",
        ),
    },
}


def list_cradle_case_ids() -> tuple[str, ...]:
    return CRADLE_CASE_IDS


def build_cradle_case_sample(case_id: str) -> dict[str, Any]:
    if case_id == "blocked_front_obstacle":
        return _normalize_blocked_sample()
    if case_id not in _CASE_SPECS:
        raise ValueError(f"unknown cradle case id: {case_id}")
    return _build_case_from_spec(case_id, _CASE_SPECS[case_id])


def build_all_cradle_case_samples() -> dict[str, dict[str, Any]]:
    return {case_id: build_cradle_case_sample(case_id) for case_id in CRADLE_CASE_IDS}


def _normalize_blocked_sample() -> dict[str, Any]:
    sample = build_blocked_manual_circulation_sample()
    summary = sample["cycle_summary"]
    sample["cycle_summary"] = {
        "case_id": "blocked_front_obstacle",
        "review_status": sample["reviewed_learning_digest"]["review_status"],
        "memory_entry_allowed": sample["reviewed_learning_digest"]["memory_entry_allowed"],
        "routing_status": sample["memory_learning_trace"]["routing_status"],
        "memory_layer_target": sample["memory_learning_trace"]["memory_layer_target"],
        "influence_visible": sample["influence_trace"]["influence_visible"],
        "body_action_signal_type": sample["body_action_signal"]["action_signal_type"],
        "expected_next_feedback_kind": sample["body_action_signal"]["expected_feedback_kind"],
        "record_order": summary["record_order"],
    }
    return sample


def _build_case_from_spec(case_id: str, spec: dict[str, object]) -> dict[str, Any]:
    base_trace_ref = f"trace:{case_id}:tick0"
    review_status = str(spec["review_status"])
    memory_layer_target = str(spec["memory_layer_target"])
    influence_visible = bool(spec["influence_visible"])
    memory_entry_allowed = bool(spec["memory_entry_allowed"])
    body_action_signal_type = str(spec["body_action_signal_type"])

    perception = PerceptionReadableData(
        perception_id=f"perception_{case_id}_tick0",
        source_kind="cradle_case_event",
        source_ref=f"event_{case_id}",
        readable_type=str(spec["readable_type"]),
        readable_payload=dict(spec["readable_payload"]),
        uncertainty=0.1 if review_status == "approved" else 0.45,
        source_trace_refs=(base_trace_ref,),
        created_at_tick=0,
    )
    endocrine = EndocrineSignal(
        endocrine_signal_id=f"endocrine_{case_id}_tick0",
        dopamine_like=0.2 if case_id == "success_front_step" else 0.0,
        norepinephrine_like=0.2 if case_id in {"unknown_feedback", "conflict_detected"} else 0.1,
        oxytocin_like=0.0,
        cortisol_like=0.2 if review_status != "approved" else 0.1,
        modulation_notes=(f"{case_id}_state_modulation",),
        source_trace_refs=(base_trace_ref, perception.perception_id),
    )
    learning_digest = LearningDigest(
        learning_digest_id=f"learning_digest_{case_id}_001",
        source_perception_refs=(perception.perception_id,),
        source_endocrine_refs=(endocrine.endocrine_signal_id,),
        before_state_ref=f"state_before_{case_id}_001",
        event_or_action_ref=f"body_action_source_{case_id}_000",
        after_state_ref=f"state_after_{case_id}_001",
        digest_type=str(spec["digest_type"]),
        digest_payload=dict(spec["digest_payload"]),
        generalization_scope="same_context_only",
        uncertainty=0.1 if review_status == "approved" else 0.5,
        source_trace_refs=(base_trace_ref, perception.perception_id, endocrine.endocrine_signal_id),
    )
    review_record = LearningReviewRecord(
        review_record_id=f"learning_review_{case_id}_{review_status}_001",
        source_learning_digest_id=learning_digest.learning_digest_id,
        review_status=review_status,
        teacher_note=f"{review_status} cradle case fixture for {case_id}",
        reviewer_ref="teacher:fixture",
        approved_scope="same_context_only" if review_status == "approved" else None,
        created_at_tick=1,
    )
    reviewed_digest = ReviewedLearningDigest(
        reviewed_digest_id=f"reviewed_learning_{case_id}_001",
        source_learning_digest_id=learning_digest.learning_digest_id,
        source_review_record_id=review_record.review_record_id,
        review_status=review_status,
        approved_scope=review_record.approved_scope,
        reviewed_payload={
            "case_id": case_id,
            "digest_type": learning_digest.digest_type,
            "review_status": review_status,
        },
        source_trace_refs=(learning_digest.learning_digest_id, review_record.review_record_id),
        memory_entry_allowed=memory_entry_allowed,
    )
    memory_learning_trace = MemoryLearningTrace(
        memory_learning_trace_id=f"memory_learning_{case_id}_001",
        source_reviewed_digest_id=reviewed_digest.reviewed_digest_id,
        source_learning_digest_id=learning_digest.learning_digest_id,
        source_review_record_id=review_record.review_record_id,
        source_perception_refs=learning_digest.source_perception_refs,
        source_endocrine_refs=learning_digest.source_endocrine_refs,
        state_snapshot_ref=f"state_snapshot_{case_id}_001",
        session_summary_ref="session_summary_cradle_cases_001",
        last_trace_summary_ref=f"last_trace_summary_{case_id}_001",
        routing_status=str(spec["routing_status"]),
        memory_layer_target=memory_layer_target,
        trace_notes=(f"{case_id}_cradle_fixture",),
    )
    memory_routing_trace = MemoryRoutingTrace(
        memory_routing_trace_id=f"memory_routing_{case_id}_001",
        source_memory_learning_trace_id=memory_learning_trace.memory_learning_trace_id,
        route_decision=f"route_{memory_learning_trace.routing_status}",
        target_layer=memory_layer_target,
        route_reason_codes=(review_status, memory_learning_trace.routing_status),
        confidence=0.9 if memory_layer_target == "working" else 0.4,
    )
    memory_items = tuple(
        {
            "item_id": f"memory_item_{case_id}_{index}",
            "kind": "cradle_case_note",
            "content": item,
        }
        for index, item in enumerate(spec["memory_items"], start=1)
    )
    memory_application_data = MemoryApplicationData(
        memory_application_data_id=f"memory_application_{case_id}_001",
        source_memory_learning_trace_refs=(memory_learning_trace.memory_learning_trace_id,),
        source_memory_routing_trace_refs=(memory_routing_trace.memory_routing_trace_id,),
        memory_items=memory_items,
        read_scope="same_context_only",
        routing_notes=(f"{case_id}_routing_{memory_learning_trace.routing_status}",),
    )
    thought_read_trace = ThoughtReadTrace(
        thought_read_trace_id=f"thought_read_{case_id}_001",
        source_memory_application_data_refs=(memory_application_data.memory_application_data_id,),
        read_reason=f"prepare_{case_id}_body_signal",
        read_result_summary=f"{case_id} produced {body_action_signal_type}",
        uncertainty=0.2 if influence_visible else 0.6,
    )
    thought_signal_id = f"thought_signal_{case_id}_001"
    influence_trace = InfluenceTrace(
        influence_trace_id=f"influence_{case_id}_001",
        source_thought_read_trace_id=thought_read_trace.thought_read_trace_id,
        affected_signal_ref=thought_signal_id,
        influence_kind=f"{case_id}_influence",
        before_summary=f"{case_id} before readback",
        after_summary=f"{case_id} after readback",
        influence_visible=influence_visible,
    )
    thought_signal = ThoughtSignal(
        thought_signal_id=thought_signal_id,
        source_memory_application_data_refs=(memory_application_data.memory_application_data_id,),
        source_endocrine_signal_refs=(endocrine.endocrine_signal_id,),
        source_thought_read_trace_refs=(thought_read_trace.thought_read_trace_id,),
        body_intent_hint=body_action_signal_type,
        reason_codes=(review_status, memory_learning_trace.routing_status),
        uncertainty=0.2 if influence_visible else 0.6,
    )
    body_action_signal = BodyActionSignal(
        body_action_signal_id=f"body_action_{case_id}_001",
        source_thought_signal_id=thought_signal.thought_signal_id,
        action_signal_type=body_action_signal_type,
        target_channel="sandbox_body",
        arguments={"case_id": case_id},
        expected_feedback_kind=str(spec["expected_next_feedback_kind"]),
        source_trace_refs=(thought_signal.thought_signal_id, influence_trace.influence_trace_id),
    )
    record_order = (
        "perception_readable_data",
        "endocrine_signal",
        "learning_digest",
        "learning_review_record",
        "reviewed_learning_digest",
        "memory_learning_trace",
        "memory_routing_trace",
        "memory_application_data",
        "thought_read_trace",
        "influence_trace",
        "thought_signal",
        "body_action_signal",
    )
    return {
        "perception_readable_data": perception.to_dict(),
        "endocrine_signal": endocrine.to_dict(),
        "learning_digest": learning_digest.to_dict(),
        "learning_review_record": review_record.to_dict(),
        "reviewed_learning_digest": reviewed_digest.to_dict(),
        "memory_learning_trace": memory_learning_trace.to_dict(),
        "memory_routing_trace": memory_routing_trace.to_dict(),
        "memory_application_data": memory_application_data.to_dict(),
        "thought_read_trace": thought_read_trace.to_dict(),
        "influence_trace": influence_trace.to_dict(),
        "thought_signal": thought_signal.to_dict(),
        "body_action_signal": body_action_signal.to_dict(),
        "cycle_summary": {
            "case_id": case_id,
            "review_status": review_status,
            "memory_entry_allowed": memory_entry_allowed,
            "routing_status": memory_learning_trace.routing_status,
            "memory_layer_target": memory_layer_target,
            "influence_visible": influence_visible,
            "body_action_signal_type": body_action_signal_type,
            "expected_next_feedback_kind": body_action_signal.expected_feedback_kind,
            "record_order": list(record_order),
        },
    }
