import unittest

from ashl_core_v1.body import BodyActionSignal
from ashl_core_v1.endocrine import EndocrineSignal
from ashl_core_v1.lesson import (
    LearningDigest,
    LearningReviewRecord,
    ReviewedLearningDigest,
)
from ashl_core_v1.memory import (
    LastTraceSummaryRef,
    MemoryApplicationData,
    MemoryLearningTrace,
    MemoryRoutingTrace,
    SessionSummaryRef,
    StateSnapshotRef,
)
from ashl_core_v1.perception import PerceptionReadableData
from ashl_core_v1.thought import InfluenceTrace, ThoughtReadTrace, ThoughtSignal


class FirstStageDataShapesTests(unittest.TestCase):
    def assert_round_trip(self, value):
        restored = type(value).from_dict(value.to_dict())

        self.assertEqual(value, restored)

    def test_perception_readable_data_can_round_trip_dict(self):
        perception = PerceptionReadableData(
            perception_id="perception_blocked_001",
            source_kind="sandbox_event",
            source_ref="event_front_blocked",
            readable_type="front_obstacle",
            readable_payload={"result": "blocked", "front": "obstacle"},
            uncertainty=0.2,
            source_trace_refs=("trace_tick_0",),
            created_at_tick=0,
        )

        as_dict = perception.to_dict()

        self.assertEqual("perception_blocked_001", as_dict["perception_id"])
        self.assertEqual(["trace_tick_0"], as_dict["source_trace_refs"])
        self.assert_round_trip(perception)

    def test_endocrine_signal_rejects_invalid_range(self):
        signal = EndocrineSignal(
            endocrine_signal_id="endocrine_001",
            dopamine_like=0.1,
            norepinephrine_like=0.2,
            oxytocin_like=0.3,
            cortisol_like=0.4,
            modulation_notes=("slight_blocked_response",),
            source_trace_refs=("trace_tick_0",),
        )

        self.assert_round_trip(signal)
        with self.assertRaises(ValueError):
            EndocrineSignal(endocrine_signal_id="bad", cortisol_like=1.2)

    def test_learning_digest_review_required_defaults_true(self):
        digest = self._learning_digest()

        self.assertTrue(digest.review_required)
        self.assert_round_trip(digest)

    def test_learning_digest_cannot_be_treated_as_reviewed_data(self):
        digest = self._learning_digest()

        self.assertFalse(hasattr(digest, "memory_entry_allowed"))
        with self.assertRaises(TypeError):
            ReviewedLearningDigest.from_dict(digest.to_dict())

    def test_learning_review_record_supports_allowed_statuses(self):
        for status in (
            "approved",
            "rejected",
            "deferred",
            "needs_more_evidence",
            "conflict_detected",
        ):
            with self.subTest(status=status):
                record = LearningReviewRecord(
                    review_record_id=f"review_{status}",
                    source_learning_digest_id="learning_digest_001",
                    review_status=status,
                    teacher_note="checked by teacher",
                    reviewer_ref="teacher:local",
                    approved_scope="same_context" if status == "approved" else None,
                    created_at_tick=1,
                )
                self.assertEqual(status, record.review_status)
                self.assert_round_trip(record)

        with self.assertRaises(ValueError):
            LearningReviewRecord(
                review_record_id="review_bad",
                source_learning_digest_id="learning_digest_001",
                review_status="auto_approved",
                teacher_note="bad",
                reviewer_ref="teacher:local",
                approved_scope=None,
            )

    def test_reviewed_learning_digest_approved_can_allow_memory_entry(self):
        reviewed = ReviewedLearningDigest(
            reviewed_digest_id="reviewed_digest_001",
            source_learning_digest_id="learning_digest_001",
            source_review_record_id="review_approved",
            review_status="approved",
            approved_scope="same_context",
            reviewed_payload={"lesson": "front action blocked"},
            source_trace_refs=("trace_tick_0", "review_approved"),
            memory_entry_allowed=True,
        )

        self.assertTrue(reviewed.memory_entry_allowed)
        self.assert_round_trip(reviewed)

    def test_reviewed_learning_digest_rejected_cannot_allow_memory_entry(self):
        with self.assertRaises(ValueError):
            ReviewedLearningDigest(
                reviewed_digest_id="reviewed_digest_rejected",
                source_learning_digest_id="learning_digest_001",
                source_review_record_id="review_rejected",
                review_status="rejected",
                approved_scope=None,
                reviewed_payload={"lesson": "not accepted"},
                source_trace_refs=("trace_tick_0", "review_rejected"),
                memory_entry_allowed=True,
            )

        rejected = ReviewedLearningDigest(
            reviewed_digest_id="reviewed_digest_rejected",
            source_learning_digest_id="learning_digest_001",
            source_review_record_id="review_rejected",
            review_status="rejected",
            approved_scope=None,
            reviewed_payload={"lesson": "not accepted"},
            source_trace_refs=("trace_tick_0", "review_rejected"),
            memory_entry_allowed=False,
        )
        self.assert_round_trip(rejected)

    def test_memory_learning_trace_keeps_review_and_source_refs(self):
        trace = MemoryLearningTrace(
            memory_learning_trace_id="memory_learning_001",
            source_reviewed_digest_id="reviewed_digest_001",
            source_learning_digest_id="learning_digest_001",
            source_review_record_id="review_approved",
            source_perception_refs=("perception_blocked_001",),
            source_endocrine_refs=("endocrine_001",),
            state_snapshot_ref="state_snapshot_001",
            session_summary_ref="session_summary_001",
            last_trace_summary_ref="last_trace_summary_001",
            routing_status="routed",
            memory_layer_target="working",
            trace_notes=("teacher approved",),
        )

        self.assertEqual("review_approved", trace.source_review_record_id)
        self.assertEqual(("perception_blocked_001",), trace.source_perception_refs)
        self.assert_round_trip(trace)

    def test_memory_routing_trace_keeps_route_decision_and_target_layer(self):
        routing = MemoryRoutingTrace(
            memory_routing_trace_id="memory_routing_001",
            source_memory_learning_trace_id="memory_learning_001",
            route_decision="route_to_working_memory",
            target_layer="working",
            route_reason_codes=("same_context",),
            confidence=0.8,
        )

        self.assertEqual("working", routing.target_layer)
        self.assert_round_trip(routing)
        with self.assertRaises(ValueError):
            MemoryRoutingTrace(
                memory_routing_trace_id="bad",
                source_memory_learning_trace_id="memory_learning_001",
                route_decision="bad",
                target_layer="unbounded",
                route_reason_codes=(),
                confidence=0.5,
            )
        with self.assertRaises(ValueError):
            MemoryRoutingTrace(
                memory_routing_trace_id="bad_confidence",
                source_memory_learning_trace_id="memory_learning_001",
                route_decision="bad",
                target_layer="working",
                route_reason_codes=(),
                confidence=1.5,
            )

    def test_memory_application_data_keeps_memory_trace_refs(self):
        data = MemoryApplicationData(
            memory_application_data_id="memory_application_001",
            source_memory_learning_trace_refs=("memory_learning_001",),
            source_memory_routing_trace_refs=("memory_routing_001",),
            memory_items=({"kind": "blocked_pattern", "value": "front_obstacle"},),
            read_scope="same_context",
            routing_notes=("working memory read",),
        )

        self.assertEqual(("memory_learning_001",), data.source_memory_learning_trace_refs)
        self.assert_round_trip(data)

    def test_thought_read_trace_records_memory_read_refs(self):
        trace = ThoughtReadTrace(
            thought_read_trace_id="thought_read_001",
            source_memory_application_data_refs=("memory_application_001",),
            read_reason="prepare body signal",
            read_result_summary="front obstacle was teacher-approved",
            uncertainty=0.25,
        )

        self.assertEqual(("memory_application_001",), trace.source_memory_application_data_refs)
        self.assert_round_trip(trace)

    def test_influence_trace_records_visible_influence(self):
        trace = InfluenceTrace(
            influence_trace_id="influence_001",
            source_thought_read_trace_id="thought_read_001",
            affected_signal_ref="thought_signal_001",
            influence_kind="reduced_repeat",
            before_summary="repeat forward action",
            after_summary="observe or adjust",
            influence_visible=True,
        )

        self.assertTrue(trace.influence_visible)
        self.assert_round_trip(trace)

    def test_thought_signal_links_memory_and_endocrine_refs(self):
        signal = ThoughtSignal(
            thought_signal_id="thought_signal_001",
            source_memory_application_data_refs=("memory_application_001",),
            source_endocrine_signal_refs=("endocrine_001",),
            source_thought_read_trace_refs=("thought_read_001",),
            body_intent_hint="observe_or_adjust",
            reason_codes=("front_obstacle", "teacher_reviewed"),
            uncertainty=0.3,
        )

        self.assertEqual(("endocrine_001",), signal.source_endocrine_signal_refs)
        self.assert_round_trip(signal)

    def test_body_action_signal_links_source_thought_signal(self):
        signal = BodyActionSignal(
            body_action_signal_id="body_action_001",
            source_thought_signal_id="thought_signal_001",
            action_signal_type="observe_or_adjust",
            target_channel="sandbox_body",
            arguments={"direction": "front"},
            expected_feedback_kind="perception_update",
            source_trace_refs=("thought_signal_001",),
        )

        self.assertEqual("thought_signal_001", signal.source_thought_signal_id)
        self.assert_round_trip(signal)

    def test_continuity_refs_can_be_created(self):
        state = StateSnapshotRef(
            state_snapshot_ref_id="state_snapshot_001",
            state_snapshot_path=None,
            state_summary={"position": [0, 0], "facing": "north"},
        )
        session = SessionSummaryRef(
            session_summary_ref_id="session_summary_001",
            session_id="session_001",
            turn_count=1,
            summary="one blocked event",
        )
        last_trace = LastTraceSummaryRef(
            last_trace_summary_ref_id="last_trace_summary_001",
            trace_id="trace_tick_0",
            summary="blocked front obstacle observed",
        )

        self.assert_round_trip(state)
        self.assert_round_trip(session)
        self.assert_round_trip(last_trace)

    def test_data_shapes_do_not_create_runtime_loop(self):
        body_signal = BodyActionSignal(
            body_action_signal_id="body_action_001",
            source_thought_signal_id="thought_signal_001",
            action_signal_type="observe_or_adjust",
            target_channel="sandbox_body",
            arguments={},
            expected_feedback_kind=None,
            source_trace_refs=(),
        )

        self.assertFalse(hasattr(body_signal, "run"))
        self.assertFalse(hasattr(body_signal, "execute"))

    def _learning_digest(self) -> LearningDigest:
        return LearningDigest(
            learning_digest_id="learning_digest_001",
            source_perception_refs=("perception_blocked_001",),
            source_endocrine_refs=("endocrine_001",),
            before_state_ref="state_before_001",
            event_or_action_ref="body_action_forward_001",
            after_state_ref="state_after_001",
            digest_type="blocked_event",
            digest_payload={"readable_type": "front_obstacle"},
            generalization_scope="same_context",
            uncertainty=0.2,
            source_trace_refs=("trace_tick_0",),
        )


if __name__ == "__main__":
    unittest.main()
