import unittest
from copy import deepcopy

from ashl_core.visual_prediction_error_attention_priority_preview_minimal import (
    build_attention_priority_preview_from_visual_prediction_error,
    build_visual_prediction_error_preview,
    run_visual_prediction_error_attention_priority_preview_minimal_check,
    validate_attention_priority_preview,
    validate_visual_prediction_error_preview,
)


EXPECTED_PREDICTION_FIELDS = {
    "prediction_error_preview_id",
    "expected_trace_id",
    "actual_trace_id",
    "error_type",
    "read_only",
    "human_summary",
    "safe_claims",
    "blocked_flags",
}

EXPECTED_ATTENTION_FIELDS = {
    "attention_priority_preview_id",
    "source_prediction_error_preview_id",
    "source_retained_link_preview_id",
    "priority_level",
    "read_only",
    "human_summary",
    "safe_claims",
    "blocked_flags",
}

PREDICTION_BLOCKED_FLAGS = {
    "active_focus_applied",
    "attention_control",
    "action_selection_influence",
    "action_behavior_changed",
    "memory_write",
    "new_retention_written",
    "lesson_applied",
    "object_recognition",
    "predictor_modified",
    "proof_of_learning_claim",
    "semantic_vision",
}

ATTENTION_BLOCKED_FLAGS = {
    "active_focus_applied",
    "attention_control",
    "action_selection_influence",
    "action_behavior_changed",
    "memory_write",
    "new_retention_written",
    "lesson_applied",
    "predictor_modified",
    "proof_of_learning_claim",
}


def expected_trace():
    return {
        "visual_trace_id": "expected_visual_trace_demo_001",
        "trace_type": "controlled_symbolic_visual_trace",
        "observation": "stable frame",
        "human_summary": "The visual trace was expected to remain stable.",
    }


def actual_changed_trace():
    return {
        "visual_trace_id": "actual_visual_trace_demo_001",
        "trace_type": "controlled_symbolic_visual_trace",
        "observation": "one visible frame-level change",
        "human_summary": "One frame-level element changed.",
    }


def actual_stable_trace():
    return {
        "visual_trace_id": "actual_visual_trace_stable_demo_001",
        "trace_type": "controlled_symbolic_visual_trace",
        "observation": "stable frame",
        "human_summary": "The visual trace remained stable.",
    }


class VisualPredictionErrorAttentionPriorityPreviewMinimalTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = run_visual_prediction_error_attention_priority_preview_minimal_check()
        cls.valid_prediction = next(
            preview
            for preview in cls.result["visual_prediction_error_previews"]
            if validate_visual_prediction_error_preview(preview)["valid"]
            and preview["error_type"] == "visual_change_detected"
        )
        cls.valid_no_error = next(
            preview
            for preview in cls.result["visual_prediction_error_previews"]
            if validate_visual_prediction_error_preview(preview)["valid"]
            and preview["error_type"] == "no_visual_prediction_error"
        )
        cls.valid_notice = next(
            preview
            for preview in cls.result["attention_priority_previews"]
            if validate_attention_priority_preview(preview)["valid"]
            and preview["priority_level"] == "notice"
        )
        cls.valid_ignore = next(
            preview
            for preview in cls.result["attention_priority_previews"]
            if validate_attention_priority_preview(preview)["valid"]
            and preview["priority_level"] == "ignore"
        )

    def test_valid_visual_prediction_error_preview_is_created(self):
        preview = build_visual_prediction_error_preview(expected_trace(), actual_changed_trace())
        validation = validate_visual_prediction_error_preview(preview)
        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(preview["error_type"], "visual_change_detected")

    def test_valid_no_error_preview_is_created(self):
        preview = build_visual_prediction_error_preview(expected_trace(), actual_stable_trace())
        validation = validate_visual_prediction_error_preview(preview)
        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(preview["error_type"], "no_visual_prediction_error")

    def test_visual_change_detected_creates_notice_priority(self):
        priority = build_attention_priority_preview_from_visual_prediction_error(self.valid_prediction)
        validation = validate_attention_priority_preview(priority)
        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(priority["priority_level"], "notice")

    def test_no_visual_prediction_error_creates_ignore_priority(self):
        priority = build_attention_priority_preview_from_visual_prediction_error(self.valid_no_error)
        validation = validate_attention_priority_preview(priority)
        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(priority["priority_level"], "ignore")

    def test_records_have_only_expected_top_level_fields(self):
        self.assertEqual(set(self.valid_prediction), EXPECTED_PREDICTION_FIELDS)
        self.assertEqual(set(self.valid_notice), EXPECTED_ATTENTION_FIELDS)

    def test_human_summaries_include_required_fields(self):
        prediction_summary = self.valid_prediction["human_summary"]
        attention_summary = self.valid_notice["human_summary"]
        for field in ("expected", "actual", "difference", "plain_result"):
            self.assertIsInstance(prediction_summary[field], str)
            self.assertTrue(prediction_summary[field])
        for field in ("why_prioritized", "retained_context", "plain_result"):
            self.assertIsInstance(attention_summary[field], str)
            self.assertTrue(attention_summary[field])

    def test_read_only_false_blocks(self):
        prediction = deepcopy(self.valid_prediction)
        prediction["read_only"] = False
        attention = deepcopy(self.valid_notice)
        attention["read_only"] = False
        self.assertIn("read_only_not_true", validate_visual_prediction_error_preview(prediction)["error_codes"])
        self.assertIn("read_only_not_true", validate_attention_priority_preview(attention)["error_codes"])

    def test_unknown_error_type_blocks(self):
        preview = deepcopy(self.valid_prediction)
        preview["error_type"] = "semantic_scene_mismatch"
        self.assertIn("error_type_not_allowed", validate_visual_prediction_error_preview(preview)["error_codes"])

    def test_unknown_priority_level_blocks(self):
        preview = deepcopy(self.valid_notice)
        preview["priority_level"] = "select_action"
        self.assertIn("priority_level_not_allowed", validate_attention_priority_preview(preview)["error_codes"])

    def test_empty_difference_blocks(self):
        preview = deepcopy(self.valid_prediction)
        preview["human_summary"]["difference"] = ""
        self.assertIn("difference_empty_or_not_string", validate_visual_prediction_error_preview(preview)["error_codes"])

    def test_empty_why_prioritized_blocks(self):
        preview = deepcopy(self.valid_notice)
        preview["human_summary"]["why_prioritized"] = ""
        self.assertIn("why_prioritized_empty_or_not_string", validate_attention_priority_preview(preview)["error_codes"])

    def test_prediction_blocked_flags_true_block(self):
        for flag in sorted(PREDICTION_BLOCKED_FLAGS):
            with self.subTest(flag=flag):
                preview = deepcopy(self.valid_prediction)
                preview["blocked_flags"][flag] = True
                self.assertIn(f"{flag}_enabled", validate_visual_prediction_error_preview(preview)["error_codes"])

    def test_attention_blocked_flags_true_block(self):
        for flag in sorted(ATTENTION_BLOCKED_FLAGS):
            with self.subTest(flag=flag):
                preview = deepcopy(self.valid_notice)
                preview["blocked_flags"][flag] = True
                self.assertIn(f"{flag}_enabled", validate_attention_priority_preview(preview)["error_codes"])

    def test_focus_applied_true_blocks_attention_priority(self):
        preview = deepcopy(self.valid_notice)
        preview["blocked_flags"]["focus_applied"] = True
        self.assertIn("focus_applied_enabled", validate_attention_priority_preview(preview)["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]
        self.assertEqual(self.result["flow"], "visual_prediction_error_attention_priority_preview_minimal_v0")
        self.assertEqual(summary["prediction_error_preview_count"], 16)
        self.assertEqual(summary["valid_prediction_error_preview_count"], 2)
        self.assertEqual(summary["attention_priority_preview_count"], 14)
        self.assertEqual(summary["valid_attention_priority_preview_count"], 2)
        self.assertEqual(summary["visual_change_detected_count"], 1)
        self.assertEqual(summary["no_visual_prediction_error_count"], 1)
        self.assertEqual(summary["notice_priority_count"], 1)
        self.assertEqual(summary["ignore_priority_count"], 1)
        self.assertEqual(summary["invalid_preview_count"], 26)
        self.assertEqual(summary["read_only_false_blocked_count"], 1)
        self.assertEqual(summary["error_type_blocked_count"], 1)
        self.assertEqual(summary["priority_level_blocked_count"], 1)
        self.assertEqual(summary["empty_difference_blocked_count"], 1)
        self.assertEqual(summary["empty_why_prioritized_blocked_count"], 1)
        self.assertEqual(summary["active_focus_applied_blocked_count"], 2)
        self.assertEqual(summary["attention_control_blocked_count"], 2)
        self.assertEqual(summary["action_selection_influence_blocked_count"], 2)
        self.assertEqual(summary["action_behavior_changed_blocked_count"], 2)
        self.assertEqual(summary["memory_write_blocked_count"], 2)
        self.assertEqual(summary["new_retention_written_blocked_count"], 2)
        self.assertEqual(summary["lesson_applied_blocked_count"], 2)
        self.assertEqual(summary["predictor_modified_blocked_count"], 2)
        self.assertEqual(summary["proof_of_learning_claim_blocked_count"], 2)
        self.assertEqual(summary["active_focus_applied_count"], 0)
        self.assertEqual(summary["attention_control_count"], 0)
        self.assertEqual(summary["action_selection_influence_count"], 0)
        self.assertEqual(summary["action_behavior_changed_count"], 0)
        self.assertEqual(summary["memory_write_count"], 0)
        self.assertEqual(summary["new_retention_written_count"], 0)
        self.assertEqual(summary["lesson_applied_count"], 0)
        self.assertEqual(summary["predictor_modified_count"], 0)
        self.assertEqual(summary["proof_of_learning_claim_count"], 0)


if __name__ == "__main__":
    unittest.main()
