import unittest

from ashl_core.mentor_feedback_runtime import (
    ALLOWED_MENTOR_FEEDBACK_LABELS,
    build_minimal_mentor_feedback_trace,
)


SOURCE_TRACE_ID = "first_output_trace:final_check:1"


class MinimalMentorFeedbackRuntimeTests(unittest.TestCase):
    def build_trace(self, label="observed"):
        return build_minimal_mentor_feedback_trace(
            source_first_output_trace_id=SOURCE_TRACE_ID,
            session_id="final_check",
            tick=1,
            mentor_feedback_label=label,
        )

    def test_builds_mentor_feedback_trace(self):
        trace = self.build_trace()

        self.assertIsInstance(trace, dict)
        self.assertEqual(trace["trace_type"], "mentor_feedback_trace")
        self.assertEqual(trace["feedback_trace_id"], "mentor_feedback_trace:final_check:1")

    def test_references_source_first_output_trace_id(self):
        trace = self.build_trace()

        self.assertEqual(trace["source_first_output_trace_id"], SOURCE_TRACE_ID)

    def test_accepts_all_minimal_feedback_labels(self):
        for label in sorted(ALLOWED_MENTOR_FEEDBACK_LABELS):
            with self.subTest(label=label):
                trace = self.build_trace(label)
                self.assertEqual(trace["mentor_feedback_label"], label)

    def test_rejects_invalid_feedback_label(self):
        with self.assertRaises(ValueError):
            self.build_trace("good")

    def test_does_not_create_lesson_candidate(self):
        trace = self.build_trace()

        self.assertIs(trace["creates_lesson_candidate"], False)
        self.assertNotIn("lesson_candidate", trace)

    def test_does_not_write_lesson_store_or_memory_layer(self):
        trace = self.build_trace()

        self.assertIs(trace["writes_lesson_store"], False)
        self.assertIs(trace["writes_memory_layer"], False)

    def test_uses_feedback_only_effect(self):
        trace = self.build_trace()

        self.assertEqual(trace["effect"], "feedback_only")

    def test_uses_test_object_stage(self):
        trace = self.build_trace()

        self.assertEqual(trace["engineering_stage"], "test_object")

    def test_rejects_empty_source_first_output_trace_id(self):
        with self.assertRaises(ValueError):
            build_minimal_mentor_feedback_trace(
                source_first_output_trace_id="",
                session_id="final_check",
                tick=1,
                mentor_feedback_label="observed",
            )

    def test_keeps_feedback_note_as_optional_trace_data(self):
        trace = build_minimal_mentor_feedback_trace(
            source_first_output_trace_id=SOURCE_TRACE_ID,
            session_id="final_check",
            tick=1,
            mentor_feedback_label="acceptable",
            mentor_source="mentor",
            mentor_feedback_note="noted during engineering supervision",
        )

        self.assertEqual(trace["mentor_feedback_note"], "noted during engineering supervision")
        self.assertEqual(trace["mentor_source"], "mentor")

    def test_does_not_include_review_selection_or_activation_outputs(self):
        trace = self.build_trace()
        forbidden_keys = {
            "failure_event",
            "review",
            "selection",
            "activation",
            "lesson_store_write",
            "memory_layer_write",
        }

        self.assertTrue(forbidden_keys.isdisjoint(trace))


if __name__ == "__main__":
    unittest.main()
