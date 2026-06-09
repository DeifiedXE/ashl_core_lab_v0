import json
import subprocess
import sys
import unittest

from ashl_core.failure_reason_classifier import classify_experience_reason
from ashl_core.similar_context_key import build_similar_context_key, run_similar_context_key_check
from ashl_core.teaching_cli import run_command


class SimilarContextKeyTests(unittest.TestCase):
    def test_default_output_shape(self):
        result = run_similar_context_key_check()

        self.assertEqual(result["command"], "run-similar-context-key-check")
        self.assertEqual(result["flow"], "similar_context_key_v0")
        self.assertEqual(result["status"], "ok")
        self.assertIn("key_results", result)
        self.assertIn("comparison_results", result)
        self.assertIn("summary", result)
        self.assertIn("boundary_check", result)

    def test_same_structure_different_position_produces_same_key(self):
        result = run_similar_context_key_check()
        keys = {item["case_name"]: item["similar_context_key"] for item in result["key_results"]}

        self.assertEqual(keys["wall_position_a"], keys["wall_position_b"])
        self.assertEqual(
            keys["wall_position_a"],
            "front_symbol=w|action=move_forward|primary_reason=front_cell_wall",
        )
        self.assertTrue(result["comparison_results"]["same_structure_different_position_match"])

    def test_different_front_symbol_and_reason_differ(self):
        result = run_similar_context_key_check()
        keys = {item["case_name"]: item["similar_context_key"] for item in result["key_results"]}

        self.assertNotEqual(keys["wall_position_a"], keys["empty_moved"])
        self.assertNotEqual(keys["item_contact"], keys["unknown"])
        self.assertTrue(result["comparison_results"]["different_front_symbol_differs"])
        self.assertTrue(result["comparison_results"]["different_reason_differs"])

    def test_turn_look_and_unknown_keys_are_stable(self):
        result = run_similar_context_key_check()
        keys = {item["case_name"]: item["similar_context_key"] for item in result["key_results"]}
        unknown = next(item for item in result["key_results"] if item["case_name"] == "unknown")

        self.assertEqual(
            keys["turn_right"],
            "front_symbol=null|action=turn_right|primary_reason=turn_action_orientation_change",
        )
        self.assertEqual(
            keys["look"],
            "front_symbol=null|action=look|primary_reason=look_action_observation_only",
        )
        self.assertEqual(
            keys["unknown"],
            "front_symbol=null|action=move_forward|primary_reason=unknown_outcome_reason",
        )
        self.assertTrue(unknown["unknown_key"])
        self.assertTrue(result["comparison_results"]["turn_key_stable"])
        self.assertTrue(result["comparison_results"]["look_key_stable"])
        self.assertTrue(result["comparison_results"]["unknown_key_stable"])

    def test_key_fields_do_not_include_position_by_default(self):
        result = run_similar_context_key_check()

        for item in result["key_results"]:
            self.assertNotIn("pos_before", item["key_fields"])
            self.assertNotIn("pos_after", item["key_fields"])

    def test_build_key_from_classifier_output(self):
        record = {
            "level_id": "simulated_vision_larger_sandbox_v0",
            "pos_before": [99, 99],
            "front_symbol_before": "i",
            "action": "move_forward",
            "outcome_type": "item_contact",
            "failure_reasons": [],
            "effect_tags": ["item_contact"],
            "position_changed": True,
        }
        classification = classify_experience_reason(record)
        key = build_similar_context_key(record, classification)

        self.assertEqual(
            key["similar_context_key"],
            "front_symbol=i|action=move_forward|primary_reason=front_cell_item_contact",
        )
        self.assertFalse(key["unknown_key"])
        self.assertTrue(key["position_independent_by_default"])

    def test_summary(self):
        summary = run_similar_context_key_check()["summary"]

        self.assertEqual(summary["case_count"], 9)
        self.assertEqual(summary["passed_count"], 9)
        self.assertEqual(summary["failed_count"], 0)
        self.assertEqual(summary["position_independent_match_count"], 1)
        self.assertEqual(summary["different_context_diff_count"], 2)
        self.assertEqual(summary["unknown_key_count"], 1)
        self.assertTrue(summary["all_similar_context_key_checks_passed"])

    def test_boundary_check(self):
        boundary = run_similar_context_key_check()["boundary_check"]

        self.assertTrue(boundary["similar_context_key_enabled"])
        self.assertTrue(boundary["experience_abstraction_layer_continued"])
        self.assertTrue(boundary["position_independent_by_default"])
        self.assertTrue(boundary["deterministic_rules_only"])
        self.assertTrue(boundary["failure_reason_classifier_required"])
        self.assertFalse(boundary["prediction_enabled"])
        self.assertFalse(boundary["rule_learning_enabled"])
        self.assertFalse(boundary["rule_revision_enabled"])
        self.assertFalse(boundary["action_selection_modified"])
        self.assertFalse(boundary["pathfinding_used"])
        self.assertFalse(boundary["llm_reasoning_used"])
        self.assertFalse(boundary["long_term_memory_write"])
        self.assertFalse(boundary["general_learning_claimed"])

    def test_run_command_uses_default(self):
        result = run_command("run-similar-context-key-check")

        self.assertEqual(result["command"], "run-similar-context-key-check")
        self.assertTrue(result["summary"]["all_similar_context_key_checks_passed"])

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-similar-context-key-check",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-similar-context-key-check")
        self.assertEqual(result["summary"]["case_count"], 9)
        self.assertTrue(result["summary"]["all_similar_context_key_checks_passed"])


if __name__ == "__main__":
    unittest.main()
