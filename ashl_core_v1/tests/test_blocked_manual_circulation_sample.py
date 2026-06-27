import json
import unittest

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
from ashl_core_v1.runtime import build_blocked_manual_circulation_sample
from ashl_core_v1.thought import InfluenceTrace, ThoughtReadTrace, ThoughtSignal


REQUIRED_SAMPLE_KEYS = (
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
    "cycle_summary",
)


class BlockedManualCirculationSampleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sample = build_blocked_manual_circulation_sample()

    def test_sample_contains_all_required_records(self):
        for key in REQUIRED_SAMPLE_KEYS:
            with self.subTest(key=key):
                self.assertIn(key, self.sample)

    def test_all_records_can_be_reconstructed_as_data_shapes(self):
        self.assertIsInstance(
            PerceptionReadableData.from_dict(self.sample["perception_readable_data"]),
            PerceptionReadableData,
        )
        self.assertIsInstance(
            EndocrineSignal.from_dict(self.sample["endocrine_signal"]),
            EndocrineSignal,
        )
        self.assertIsInstance(
            LearningDigest.from_dict(self.sample["learning_digest"]),
            LearningDigest,
        )
        self.assertIsInstance(
            LearningReviewRecord.from_dict(self.sample["learning_review_record"]),
            LearningReviewRecord,
        )
        self.assertIsInstance(
            ReviewedLearningDigest.from_dict(self.sample["reviewed_learning_digest"]),
            ReviewedLearningDigest,
        )
        self.assertIsInstance(
            MemoryLearningTrace.from_dict(self.sample["memory_learning_trace"]),
            MemoryLearningTrace,
        )
        self.assertIsInstance(
            MemoryRoutingTrace.from_dict(self.sample["memory_routing_trace"]),
            MemoryRoutingTrace,
        )
        self.assertIsInstance(
            MemoryApplicationData.from_dict(self.sample["memory_application_data"]),
            MemoryApplicationData,
        )
        self.assertIsInstance(
            ThoughtReadTrace.from_dict(self.sample["thought_read_trace"]),
            ThoughtReadTrace,
        )
        self.assertIsInstance(
            InfluenceTrace.from_dict(self.sample["influence_trace"]),
            InfluenceTrace,
        )
        self.assertIsInstance(
            ThoughtSignal.from_dict(self.sample["thought_signal"]),
            ThoughtSignal,
        )
        self.assertIsInstance(
            BodyActionSignal.from_dict(self.sample["body_action_signal"]),
            BodyActionSignal,
        )

    def test_perception_and_learning_semantics_are_blocked_front_obstacle(self):
        perception = self.sample["perception_readable_data"]
        digest = self.sample["learning_digest"]

        self.assertEqual("front_obstacle", perception["readable_type"])
        self.assertEqual("blocked", perception["readable_payload"]["observed"])
        self.assertEqual("front", perception["readable_payload"]["position"])
        self.assertEqual("obstruction_event", digest["digest_type"])
        self.assertEqual("front_action_blocked", digest["digest_payload"]["event"])

    def test_all_source_ids_link_correctly(self):
        perception = self.sample["perception_readable_data"]
        endocrine = self.sample["endocrine_signal"]
        digest = self.sample["learning_digest"]
        review = self.sample["learning_review_record"]
        reviewed = self.sample["reviewed_learning_digest"]
        memory_trace = self.sample["memory_learning_trace"]
        routing = self.sample["memory_routing_trace"]
        application = self.sample["memory_application_data"]
        thought_read = self.sample["thought_read_trace"]
        influence = self.sample["influence_trace"]
        thought = self.sample["thought_signal"]
        body = self.sample["body_action_signal"]

        self.assertEqual([perception["perception_id"]], digest["source_perception_refs"])
        self.assertEqual([endocrine["endocrine_signal_id"]], digest["source_endocrine_refs"])
        self.assertEqual(digest["learning_digest_id"], review["source_learning_digest_id"])
        self.assertEqual(digest["learning_digest_id"], reviewed["source_learning_digest_id"])
        self.assertEqual(review["review_record_id"], reviewed["source_review_record_id"])
        self.assertEqual(reviewed["reviewed_digest_id"], memory_trace["source_reviewed_digest_id"])
        self.assertEqual(digest["learning_digest_id"], memory_trace["source_learning_digest_id"])
        self.assertEqual(review["review_record_id"], memory_trace["source_review_record_id"])
        self.assertEqual([perception["perception_id"]], memory_trace["source_perception_refs"])
        self.assertEqual([endocrine["endocrine_signal_id"]], memory_trace["source_endocrine_refs"])
        self.assertEqual(
            memory_trace["memory_learning_trace_id"],
            routing["source_memory_learning_trace_id"],
        )
        self.assertEqual(
            [memory_trace["memory_learning_trace_id"]],
            application["source_memory_learning_trace_refs"],
        )
        self.assertEqual(
            [routing["memory_routing_trace_id"]],
            application["source_memory_routing_trace_refs"],
        )
        self.assertEqual(
            [application["memory_application_data_id"]],
            thought_read["source_memory_application_data_refs"],
        )
        self.assertEqual(
            thought_read["thought_read_trace_id"],
            influence["source_thought_read_trace_id"],
        )
        self.assertEqual(
            [application["memory_application_data_id"]],
            thought["source_memory_application_data_refs"],
        )
        self.assertEqual(
            [endocrine["endocrine_signal_id"]],
            thought["source_endocrine_signal_refs"],
        )
        self.assertEqual(
            [thought_read["thought_read_trace_id"]],
            thought["source_thought_read_trace_refs"],
        )
        self.assertEqual(thought["thought_signal_id"], influence["affected_signal_ref"])
        self.assertEqual(thought["thought_signal_id"], body["source_thought_signal_id"])

    def test_learning_digest_is_reviewed_before_memory_trace_exists(self):
        order = self.sample["cycle_summary"]["record_order"]

        self.assertLess(order.index("learning_digest"), order.index("learning_review_record"))
        self.assertLess(order.index("learning_review_record"), order.index("reviewed_learning_digest"))
        self.assertLess(order.index("reviewed_learning_digest"), order.index("memory_learning_trace"))
        self.assertTrue(self.sample["cycle_summary"]["learning_digest_reviewed_before_memory_trace"])

    def test_reviewed_learning_digest_memory_entry_allowed_true(self):
        reviewed = self.sample["reviewed_learning_digest"]

        self.assertEqual("approved", reviewed["review_status"])
        self.assertTrue(reviewed["memory_entry_allowed"])

    def test_memory_learning_trace_references_reviewed_digest_and_review_record(self):
        reviewed = self.sample["reviewed_learning_digest"]
        review = self.sample["learning_review_record"]
        memory_trace = self.sample["memory_learning_trace"]

        self.assertEqual(reviewed["reviewed_digest_id"], memory_trace["source_reviewed_digest_id"])
        self.assertEqual(review["review_record_id"], memory_trace["source_review_record_id"])
        self.assertEqual("routed", memory_trace["routing_status"])
        self.assertEqual("working", memory_trace["memory_layer_target"])

    def test_memory_application_data_contains_thought_readable_items(self):
        memory_items = self.sample["memory_application_data"]["memory_items"]
        contents = [item["content"] for item in memory_items]

        self.assertIn("front obstacle was encountered", contents)
        self.assertIn("direct retry should be reduced in same context", contents)

    def test_thought_read_trace_reads_memory_application_data(self):
        application = self.sample["memory_application_data"]
        thought_read = self.sample["thought_read_trace"]

        self.assertEqual(
            [application["memory_application_data_id"]],
            thought_read["source_memory_application_data_refs"],
        )

    def test_influence_trace_marks_visible_influence(self):
        influence = self.sample["influence_trace"]

        self.assertTrue(influence["influence_visible"])
        self.assertIn("observe_or_adjust", influence["after_summary"])

    def test_thought_signal_body_intent_hint_is_observe_or_adjust(self):
        thought = self.sample["thought_signal"]

        self.assertEqual("observe_or_adjust", thought["body_intent_hint"])
        self.assertEqual(
            ["reviewed_blocked_memory_read", "same_context_only"],
            thought["reason_codes"],
        )

    def test_body_action_signal_is_observe_or_adjust(self):
        body = self.sample["body_action_signal"]

        self.assertEqual("observe_or_adjust", body["action_signal_type"])
        self.assertEqual("sandbox_body", body["target_channel"])
        self.assertEqual("next_observation", body["expected_feedback_kind"])

    def test_sample_can_be_serialized_to_dict_and_json(self):
        encoded = json.dumps(self.sample, sort_keys=True)
        decoded = json.loads(encoded)

        self.assertEqual(
            self.sample["cycle_summary"]["case_id"],
            decoded["cycle_summary"]["case_id"],
        )

    def test_manual_sample_does_not_create_runner_or_cli(self):
        self.assertNotIn("runner_command", self.sample)
        self.assertNotIn("cli_command", self.sample)


if __name__ == "__main__":
    unittest.main()
