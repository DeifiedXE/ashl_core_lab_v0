"""Manual first-stage circulation samples for ASHL Core v1.

These builders create fixed records only. They do not run a loop, select actions,
or execute anything.
"""

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
from ashl_core_v1.thought import InfluenceTrace, ThoughtReadTrace, ThoughtSignal


def build_blocked_manual_circulation_sample() -> dict[str, Any]:
    """Build the fixed front-obstacle manual circulation sample."""

    case_id = "blocked_front_obstacle"
    base_trace_ref = "trace:blocked_front_obstacle:tick0"

    perception = PerceptionReadableData(
        perception_id="perception_front_obstacle_tick0",
        source_kind="sandbox_event",
        source_ref="event_front_action_blocked",
        readable_type="front_obstacle",
        readable_payload={
            "observed": "blocked",
            "position": "front",
        },
        uncertainty=0.1,
        source_trace_refs=(base_trace_ref,),
        created_at_tick=0,
    )

    endocrine = EndocrineSignal(
        endocrine_signal_id="endocrine_blocked_tick0",
        dopamine_like=0.0,
        norepinephrine_like=0.2,
        oxytocin_like=0.0,
        cortisol_like=0.2,
        modulation_notes=(
            "small_alertness_from_blocked_front",
            "small_pressure_from_obstruction",
        ),
        source_trace_refs=(base_trace_ref, perception.perception_id),
    )

    learning_digest = LearningDigest(
        learning_digest_id="learning_digest_front_obstacle_001",
        source_perception_refs=(perception.perception_id,),
        source_endocrine_refs=(endocrine.endocrine_signal_id,),
        before_state_ref="state_before_front_attempt_001",
        event_or_action_ref="body_action_attempt_forward_000",
        after_state_ref="state_after_front_blocked_001",
        digest_type="obstruction_event",
        digest_payload={
            "event": "front_action_blocked",
            "suggested_learning": "direct_forward_attempt_was_blocked",
        },
        generalization_scope="same_context_only",
        uncertainty=0.15,
        source_trace_refs=(base_trace_ref, perception.perception_id, endocrine.endocrine_signal_id),
    )

    review_record = LearningReviewRecord(
        review_record_id="learning_review_front_obstacle_approved_001",
        source_learning_digest_id=learning_digest.learning_digest_id,
        review_status="approved",
        teacher_note="approved as same-context blocked learning sample",
        reviewer_ref="teacher:fixture",
        approved_scope="same_context_only",
        created_at_tick=1,
    )

    reviewed_digest = ReviewedLearningDigest(
        reviewed_digest_id="reviewed_learning_front_obstacle_001",
        source_learning_digest_id=learning_digest.learning_digest_id,
        source_review_record_id=review_record.review_record_id,
        review_status=review_record.review_status,
        approved_scope=review_record.approved_scope,
        reviewed_payload={
            "event": "front_action_blocked",
            "reviewed_learning": "direct_forward_attempt_was_blocked",
            "scope": "same_context_only",
        },
        source_trace_refs=(
            learning_digest.learning_digest_id,
            review_record.review_record_id,
        ),
        memory_entry_allowed=True,
    )

    memory_learning_trace = MemoryLearningTrace(
        memory_learning_trace_id="memory_learning_front_obstacle_001",
        source_reviewed_digest_id=reviewed_digest.reviewed_digest_id,
        source_learning_digest_id=learning_digest.learning_digest_id,
        source_review_record_id=review_record.review_record_id,
        source_perception_refs=learning_digest.source_perception_refs,
        source_endocrine_refs=learning_digest.source_endocrine_refs,
        state_snapshot_ref="state_snapshot_front_obstacle_001",
        session_summary_ref="session_summary_manual_sample_001",
        last_trace_summary_ref="last_trace_summary_front_obstacle_001",
        routing_status="routed",
        memory_layer_target="working",
        trace_notes=(
            "teacher_approved_same_context_learning",
            "manual_sample_not_runtime_runner",
        ),
    )

    memory_routing_trace = MemoryRoutingTrace(
        memory_routing_trace_id="memory_routing_front_obstacle_001",
        source_memory_learning_trace_id=memory_learning_trace.memory_learning_trace_id,
        route_decision="route_to_working_memory",
        target_layer="working",
        route_reason_codes=(
            "approved",
            "same_context_only",
            "manual_blocked_sample",
        ),
        confidence=0.9,
    )

    memory_application_data = MemoryApplicationData(
        memory_application_data_id="memory_application_front_obstacle_001",
        source_memory_learning_trace_refs=(memory_learning_trace.memory_learning_trace_id,),
        source_memory_routing_trace_refs=(memory_routing_trace.memory_routing_trace_id,),
        memory_items=(
            {
                "item_id": "memory_item_front_obstacle_observed_001",
                "kind": "observation",
                "content": "front obstacle was encountered",
            },
            {
                "item_id": "memory_item_reduce_direct_retry_001",
                "kind": "same_context_guidance",
                "content": "direct retry should be reduced in same context",
            },
        ),
        read_scope="same_context_only",
        routing_notes=("working_memory_for_next_thought",),
    )

    thought_read_trace = ThoughtReadTrace(
        thought_read_trace_id="thought_read_front_obstacle_001",
        source_memory_application_data_refs=(
            memory_application_data.memory_application_data_id,
        ),
        read_reason="prepare_next_body_signal",
        read_result_summary=(
            "same-context blocked learning suggests observing or adjusting "
            "instead of direct retry"
        ),
        uncertainty=0.2,
    )

    thought_signal_id = "thought_signal_observe_or_adjust_001"
    influence_trace = InfluenceTrace(
        influence_trace_id="influence_front_obstacle_001",
        source_thought_read_trace_id=thought_read_trace.thought_read_trace_id,
        affected_signal_ref=thought_signal_id,
        influence_kind="same_context_retry_reduction",
        before_summary="direct retry remained plausible",
        after_summary="observe_or_adjust became the body intent hint",
        influence_visible=True,
    )

    thought_signal = ThoughtSignal(
        thought_signal_id=thought_signal_id,
        source_memory_application_data_refs=(
            memory_application_data.memory_application_data_id,
        ),
        source_endocrine_signal_refs=(endocrine.endocrine_signal_id,),
        source_thought_read_trace_refs=(thought_read_trace.thought_read_trace_id,),
        body_intent_hint="observe_or_adjust",
        reason_codes=(
            "reviewed_blocked_memory_read",
            "same_context_only",
        ),
        uncertainty=0.2,
    )

    body_action_signal = BodyActionSignal(
        body_action_signal_id="body_action_observe_or_adjust_001",
        source_thought_signal_id=thought_signal.thought_signal_id,
        action_signal_type="observe_or_adjust",
        target_channel="sandbox_body",
        arguments={
            "preferred_next": "observe_front",
            "avoid_direct_retry": True,
        },
        expected_feedback_kind="next_observation",
        source_trace_refs=(
            thought_signal.thought_signal_id,
            influence_trace.influence_trace_id,
        ),
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
            "event": "front_action_blocked",
            "record_order": list(record_order),
            "learning_digest_reviewed_before_memory_trace": True,
            "memory_entry_allowed": reviewed_digest.memory_entry_allowed,
            "influence_visible": influence_trace.influence_visible,
            "body_intent_hint": thought_signal.body_intent_hint,
            "body_action_signal_type": body_action_signal.action_signal_type,
            "next_expected_feedback_kind": body_action_signal.expected_feedback_kind,
        },
    }
