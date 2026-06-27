import unittest

from ashl_core_v1.runtime.cradle_cases import (
    build_all_cradle_case_samples,
    build_cradle_case_sample,
    list_cradle_case_ids,
)


EXPECTED_CASES = (
    "blocked_front_obstacle",
    "success_front_step",
    "unknown_feedback",
    "teacher_rejected",
    "teacher_deferred",
    "conflict_detected",
    "stale_learning",
    "superseded_learning",
)

REQUIRED_RECORDS = (
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


class MultiCaseCradleCirculationSamplesTests(unittest.TestCase):
    def test_list_cradle_case_ids_returns_all_expected_cases(self):
        self.assertEqual(EXPECTED_CASES, list_cradle_case_ids())

    def test_each_case_can_be_built(self):
        for case_id in EXPECTED_CASES:
            with self.subTest(case_id=case_id):
                self.assertEqual(case_id, build_cradle_case_sample(case_id)["cycle_summary"]["case_id"])

    def test_each_case_has_all_required_records(self):
        for case_id in EXPECTED_CASES:
            sample = build_cradle_case_sample(case_id)
            for key in REQUIRED_RECORDS:
                with self.subTest(case_id=case_id, key=key):
                    self.assertIn(key, sample)

    def test_each_case_has_cycle_summary(self):
        for case_id in EXPECTED_CASES:
            summary = build_cradle_case_sample(case_id)["cycle_summary"]
            for key in (
                "case_id",
                "review_status",
                "memory_entry_allowed",
                "routing_status",
                "memory_layer_target",
                "influence_visible",
                "body_action_signal_type",
                "expected_next_feedback_kind",
            ):
                with self.subTest(case_id=case_id, key=key):
                    self.assertIn(key, summary)

    def test_approved_cases_may_allow_memory_entry(self):
        for case_id in (
            "blocked_front_obstacle",
            "success_front_step",
            "stale_learning",
            "superseded_learning",
        ):
            summary = build_cradle_case_sample(case_id)["cycle_summary"]
            with self.subTest(case_id=case_id):
                self.assertEqual("approved", summary["review_status"])
                self.assertTrue(summary["memory_entry_allowed"])

    def test_blocked_review_statuses_cannot_allow_memory_entry(self):
        for case_id in (
            "unknown_feedback",
            "teacher_rejected",
            "teacher_deferred",
            "conflict_detected",
        ):
            summary = build_cradle_case_sample(case_id)["cycle_summary"]
            with self.subTest(case_id=case_id):
                self.assertFalse(summary["memory_entry_allowed"])

    def test_stale_and_superseded_approve_but_route_to_none(self):
        for case_id, routing_status in (
            ("stale_learning", "stale"),
            ("superseded_learning", "superseded"),
        ):
            summary = build_cradle_case_sample(case_id)["cycle_summary"]
            with self.subTest(case_id=case_id):
                self.assertEqual("approved", summary["review_status"])
                self.assertTrue(summary["memory_entry_allowed"])
                self.assertEqual(routing_status, summary["routing_status"])
                self.assertEqual("none", summary["memory_layer_target"])

    def test_each_case_preserves_source_id_links(self):
        for case_id in EXPECTED_CASES:
            sample = build_cradle_case_sample(case_id)
            perception = sample["perception_readable_data"]
            endocrine = sample["endocrine_signal"]
            digest = sample["learning_digest"]
            review = sample["learning_review_record"]
            reviewed = sample["reviewed_learning_digest"]
            memory_trace = sample["memory_learning_trace"]
            routing = sample["memory_routing_trace"]
            application = sample["memory_application_data"]
            thought_read = sample["thought_read_trace"]
            influence = sample["influence_trace"]
            thought = sample["thought_signal"]
            body = sample["body_action_signal"]
            with self.subTest(case_id=case_id):
                self.assertEqual([perception["perception_id"]], digest["source_perception_refs"])
                self.assertEqual([endocrine["endocrine_signal_id"]], digest["source_endocrine_refs"])
                self.assertEqual(digest["learning_digest_id"], review["source_learning_digest_id"])
                self.assertEqual(review["review_record_id"], reviewed["source_review_record_id"])
                self.assertEqual(reviewed["reviewed_digest_id"], memory_trace["source_reviewed_digest_id"])
                self.assertEqual(review["review_record_id"], memory_trace["source_review_record_id"])
                self.assertEqual(memory_trace["memory_learning_trace_id"], routing["source_memory_learning_trace_id"])
                self.assertEqual([memory_trace["memory_learning_trace_id"]], application["source_memory_learning_trace_refs"])
                self.assertEqual([application["memory_application_data_id"]], thought_read["source_memory_application_data_refs"])
                self.assertEqual(thought_read["thought_read_trace_id"], influence["source_thought_read_trace_id"])
                self.assertEqual(thought["thought_signal_id"], body["source_thought_signal_id"])

    def test_build_all_cradle_case_samples_returns_all_cases(self):
        samples = build_all_cradle_case_samples()

        self.assertEqual(set(EXPECTED_CASES), set(samples))

    def test_unknown_case_id_raises(self):
        with self.assertRaises(ValueError):
            build_cradle_case_sample("missing_case")


if __name__ == "__main__":
    unittest.main()
