import json
import subprocess
import sys
import unittest

from ashl_core.action_selection_adjacent_review_minimal import (
    build_action_selection_adjacent_review,
    run_action_selection_adjacent_review_minimal_check,
    validate_action_selection_adjacent_review,
)
from ashl_core.pre_action_consideration_gate_check_minimal import build_pre_action_consideration_gate_result
from ashl_core.teaching_cli import run_command


class ActionSelectionAdjacentReviewMinimalTests(unittest.TestCase):
    def _valid_review(self):
        return build_action_selection_adjacent_review()

    def _item(self, scenario_id):
        for item in self._valid_review()["review_items"]:
            if item["scenario_id"] == scenario_id:
                return item
        self.fail(f"missing review item {scenario_id}")

    def _assert_invalid(self, record, error_code):
        validation = validate_action_selection_adjacent_review(record)

        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])

    def test_valid_review_is_created(self):
        record = self._valid_review()
        validation = validate_action_selection_adjacent_review(record)

        self.assertTrue(validation["valid"])
        self.assertEqual(record["review_mode"], "action_selection_adjacent_review_only")
        self.assertEqual(len(record["review_items"]), 3)

    def test_valid_review_reuses_pre_action_gate_result(self):
        gate_result = build_pre_action_consideration_gate_result()
        record = build_action_selection_adjacent_review(gate_result)

        self.assertEqual(record["source_pre_action_gate_result_id"], gate_result["pre_action_gate_result_id"])

    def test_review_item_mappings(self):
        self.assertEqual(
            self._item("obstacle_retry_failed_same_state")["reviewed_action"],
            "check_before_retry",
        )
        self.assertEqual(
            self._item("costly_retry_same_state")["reviewed_action"],
            "slow_down_or_reduce_cost",
        )
        self.assertEqual(
            self._item("unclear_failure_same_state")["reviewed_action"],
            "ask_for_help",
        )

    def test_review_items_are_review_only_and_not_actions(self):
        for item in self._valid_review()["review_items"]:
            with self.subTest(item=item["scenario_id"]):
                self.assertTrue(item["review_only"])
                self.assertFalse(item["selected_action"])
                self.assertFalse(item["final_action"])
                self.assertFalse(item["action_execution"])

    def test_most_review_worthy_candidate_is_check_before_retry(self):
        summary = self._valid_review()["review_summary"]

        self.assertEqual(summary["most_review_worthy_candidate"], "check_before_retry")
        self.assertFalse(summary["selection_made"])
        self.assertFalse(summary["final_action_created"])

    def test_allowed_next_layer_allows_only_non_executing_choice_candidate(self):
        allowed = self._valid_review()["allowed_next_layer"]

        self.assertTrue(allowed["may_enter_non_executing_action_choice_candidate"])
        self.assertFalse(allowed["may_enter_runtime_action_selection"])
        self.assertFalse(allowed["may_create_final_action"])
        self.assertFalse(allowed["may_execute_action"])
        self.assertFalse(allowed["may_create_direct_command"])
        self.assertFalse(allowed["may_write_persistent_policy"])

    def test_bad_review_mode_blocks(self):
        record = self._valid_review()
        record["review_mode"] = "runtime_action_selection_review"
        self._assert_invalid(record, "review_mode_not_action_selection_adjacent_review_only")

    def test_wrong_mapping_blocks(self):
        record = self._valid_review()
        record["review_items"][0]["reviewed_action"] = "ask_for_help"
        self._assert_invalid(record, "obstacle_retry_failed_same_state_wrong_reviewed_action")

    def test_selected_action_true_blocks(self):
        record = self._valid_review()
        record["review_items"][0]["selected_action"] = True
        self._assert_invalid(record, "selected_action_not_false")

    def test_final_action_true_blocks(self):
        record = self._valid_review()
        record["review_items"][0]["final_action"] = True
        self._assert_invalid(record, "final_action_not_false")

    def test_action_execution_true_blocks(self):
        record = self._valid_review()
        record["review_items"][0]["action_execution"] = True
        self._assert_invalid(record, "action_execution_not_false")

    def test_selection_made_true_blocks(self):
        record = self._valid_review()
        record["review_summary"]["selection_made"] = True
        self._assert_invalid(record, "selection_made_not_false")

    def test_allowed_next_layer_runtime_paths_block(self):
        cases = {
            "may_enter_runtime_action_selection": "may_enter_runtime_action_selection_not_false",
            "may_create_final_action": "may_create_final_action_not_false",
            "may_execute_action": "may_execute_action_not_false",
            "may_create_direct_command": "may_create_direct_command_not_false",
            "may_write_persistent_policy": "may_write_persistent_policy_not_false",
        }
        for field, error_code in cases.items():
            with self.subTest(field=field):
                record = self._valid_review()
                record["allowed_next_layer"][field] = True
                self._assert_invalid(record, error_code)

    def test_blocked_flags_true_block(self):
        cases = {
            "production_action_selection": "production_action_selection_enabled",
            "runtime_action_selection": "runtime_action_selection_enabled",
            "selected_action_created": "selected_action_created_enabled",
            "final_action_created": "final_action_created_enabled",
            "action_executed": "action_executed_enabled",
            "direct_action_command": "direct_action_command_enabled",
            "real_navigation_changed": "real_navigation_changed_enabled",
            "ui_behavior_changed": "ui_behavior_changed_enabled",
            "persistent_policy_written": "persistent_policy_written_enabled",
            "general_behavior_changed": "general_behavior_changed_enabled",
            "semantic_or_fuzzy_match_used": "semantic_or_fuzzy_match_used_enabled",
            "exploration_blocked": "exploration_blocked_enabled",
            "curiosity_overridden": "curiosity_overridden_enabled",
            "mentor_override_blocked": "mentor_override_blocked_enabled",
            "lesson_applied": "lesson_applied_enabled",
            "memory_write": "memory_write_enabled",
            "new_retention_written": "new_retention_written_enabled",
            "predictor_modified": "predictor_modified_enabled",
            "proof_of_learning_claim": "proof_of_learning_claim_enabled",
        }
        for flag, error_code in cases.items():
            with self.subTest(flag=flag):
                record = self._valid_review()
                record["blocked_flags"][flag] = True
                self._assert_invalid(record, error_code)

    def test_demo_summary_counts_are_deterministic(self):
        result = run_action_selection_adjacent_review_minimal_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-action-selection-adjacent-review-minimal-check")
        self.assertEqual(result["flow"], "action_selection_adjacent_review_minimal_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["action_selection_adjacent_review_count"], 41)
        self.assertEqual(summary["valid_action_selection_adjacent_review_count"], 1)
        self.assertEqual(summary["invalid_action_selection_adjacent_review_count"], 40)
        self.assertEqual(summary["review_item_count"], 3)
        self.assertEqual(summary["review_only_item_count"], 3)
        self.assertEqual(summary["not_selected_action_item_count"], 3)
        self.assertEqual(summary["not_final_action_item_count"], 3)
        self.assertEqual(summary["not_action_execution_item_count"], 3)
        self.assertEqual(summary["most_review_worthy_candidate_count"], 1)
        self.assertEqual(summary["may_enter_non_executing_action_choice_candidate_count"], 1)
        self.assertEqual(summary["runtime_action_selection_blocked_count"], 1)
        self.assertEqual(summary["final_action_blocked_count"], 1)
        self.assertEqual(summary["action_execution_blocked_count"], 1)
        self.assertEqual(summary["direct_command_blocked_count"], 1)
        self.assertEqual(summary["persistent_policy_blocked_count"], 1)
        self.assertEqual(summary["wrong_mapping_blocked_count"], 1)
        self.assertEqual(summary["selected_action_blocked_count"], 1)
        self.assertEqual(summary["proof_of_learning_claim_blocked_count"], 1)
        self.assertEqual(boundary["review_item_count"], 3)
        self.assertEqual(boundary["most_review_worthy_candidate"], "check_before_retry")
        self.assertFalse(boundary["review_is_selection"])
        self.assertFalse(boundary["selected_action_added"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-action-selection-adjacent-review-minimal-check")

        self.assertEqual(result["command"], "run-action-selection-adjacent-review-minimal-check")
        self.assertEqual(result["summary"]["valid_action_selection_adjacent_review_count"], 1)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-action-selection-adjacent-review-minimal-check",
            ],
            check=True,
            capture_output=True,
            encoding="utf-8",
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-action-selection-adjacent-review-minimal-check")
        self.assertEqual(result["summary"]["most_review_worthy_candidate_count"], 1)


if __name__ == "__main__":
    unittest.main()
