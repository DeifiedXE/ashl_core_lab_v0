import json
import subprocess
import sys
import unittest

from ashl_core.phase0_level0_obstacle_memory_flip_test_minimal import (
    build_phase0_level0_obstacle_memory_flip_result,
    run_phase0_level0_obstacle_memory_flip_test_minimal_check,
    validate_phase0_level0_obstacle_memory_flip_result,
)
from ashl_core.teaching_cli import run_command


class Phase0Level0ObstacleMemoryFlipTestMinimalTests(unittest.TestCase):
    def _result(self):
        return build_phase0_level0_obstacle_memory_flip_result()

    def _case(self, result, memory_case):
        return {item["memory_case"]: item for item in result["memory_case_results"]}[memory_case]

    def _assert_invalid(self, record, error_code):
        validation = validate_phase0_level0_obstacle_memory_flip_result(record)
        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])

    def test_valid_level0_flip_result_is_created(self):
        result = self._result()
        validation = validate_phase0_level0_obstacle_memory_flip_result(result)

        self.assertTrue(validation["valid"])
        self.assertEqual(result["level_info"]["level_id"], "phase0_level0_obstacle_memory_flip_test")

    def test_same_state_is_used_for_all_cases(self):
        state = self._result()["shared_state"]

        self.assertEqual(state["scenario_id"], "obstacle_memory_flip_same_state")
        self.assertEqual(state["front_symbol"], "w")
        self.assertTrue(state["symbol_fixture_only"])
        self.assertEqual(state["agent_position"], [0, 0])
        self.assertEqual(state["facing"], "east")
        self.assertEqual(state["front_cell_position"], [1, 0])
        self.assertTrue(state["same_state_for_all_cases"])

    def test_same_candidate_actions_are_used(self):
        self.assertEqual(
            self._result()["candidate_actions"],
            ["retry_same_action", "check_before_retry", "ask_for_help", "slow_down_or_reduce_cost"],
        )

    def test_only_memory_content_changes(self):
        flip = self._result()["flip_check"]

        self.assertTrue(flip["same_runner_used"])
        self.assertTrue(flip["same_state_used"])
        self.assertTrue(flip["same_candidate_actions_used"])
        self.assertTrue(flip["only_memory_content_changed"])

    def test_baseline_scores_are_correct(self):
        scores = self._result()["baseline_result"]["scores"]

        self.assertEqual(scores["retry_same_action"], 0.50)
        self.assertEqual(scores["check_before_retry"], 0.50)
        self.assertEqual(scores["ask_for_help"], 0.20)
        self.assertEqual(scores["slow_down_or_reduce_cost"], 0.30)

    def test_retry_failed_memory_makes_check_stronger_than_retry(self):
        case = self._case(self._result(), "retry_failed")

        self.assertEqual(case["exact_key"], "obstacle_retry_failed")
        self.assertEqual(case["scores"]["check_before_retry"], 0.60)
        self.assertEqual(case["scores"]["retry_same_action"], 0.45)
        self.assertGreater(case["scores"]["check_before_retry"], case["scores"]["retry_same_action"])
        self.assertEqual(case["expected_stronger_action"], "check_before_retry")
        self.assertTrue(case["flip_side_passed"])

    def test_retry_succeeded_memory_makes_retry_stronger_than_check(self):
        case = self._case(self._result(), "retry_succeeded")

        self.assertEqual(case["exact_key"], "obstacle_retry_succeeded")
        self.assertEqual(case["scores"]["retry_same_action"], 0.60)
        self.assertEqual(case["scores"]["check_before_retry"], 0.45)
        self.assertGreater(case["scores"]["retry_same_action"], case["scores"]["check_before_retry"])
        self.assertEqual(case["expected_stronger_action"], "retry_same_action")
        self.assertTrue(case["flip_side_passed"])

    def test_flip_flags_are_true(self):
        flip = self._result()["flip_check"]

        self.assertTrue(flip["bidirectional_flip_passed"])
        self.assertTrue(flip["one_way_caution_bias_rejected"])
        self.assertTrue(flip["safe_to_continue_to_level1_danger"])

    def test_max_absolute_delta_within_limit(self):
        for case in self._result()["memory_case_results"]:
            for delta in case["score_deltas"].values():
                self.assertLessEqual(abs(delta), 0.10)

    def test_runtime_only_level_info_blocks_execution_and_danger(self):
        info = self._result()["level_info"]

        self.assertFalse(info["danger_cell_used"])
        self.assertFalse(info["execution_required"])
        self.assertFalse(info["pathfinding_required"])

    def test_wrong_front_symbol_blocks(self):
        result = self._result()
        result["shared_state"]["front_symbol"] = "d"
        self._assert_invalid(result, "front_symbol_not_w")

    def test_missing_memory_case_blocks(self):
        result = self._result()
        result["memory_case_results"] = [self._case(result, "retry_failed")]
        self._assert_invalid(result, "missing_retry_succeeded_case")

    def test_one_way_caution_bias_blocks(self):
        result = self._result()
        succeeded = self._case(result, "retry_succeeded")
        succeeded["scores"]["retry_same_action"] = 0.45
        succeeded["scores"]["check_before_retry"] = 0.60
        succeeded["score_deltas"]["retry_same_action"] = -0.05
        succeeded["score_deltas"]["check_before_retry"] = 0.10
        result["flip_check"]["one_way_caution_bias_rejected"] = False
        self._assert_invalid(result, "retry_succeeded_does_not_prefer_retry")
        self._assert_invalid(result, "one_way_caution_bias_rejected_not_true")

    def test_wrong_delta_blocks(self):
        result = self._result()
        self._case(result, "retry_failed")["score_deltas"]["check_before_retry"] = 0.09
        self._assert_invalid(result, "retry_failed_check_before_retry_delta_wrong")

    def test_delta_too_high_blocks(self):
        result = self._result()
        self._case(result, "retry_failed")["score_deltas"]["check_before_retry"] = 0.20
        self._assert_invalid(result, "retry_failed_check_before_retry_delta_too_high")

    def test_same_runner_state_candidates_and_memory_flags_block(self):
        cases = {
            "same_runner_used": "same_runner_used_not_true",
            "same_state_used": "same_state_used_not_true",
            "same_candidate_actions_used": "same_candidate_actions_used_not_true",
            "only_memory_content_changed": "only_memory_content_changed_not_true",
        }
        for field, error_code in cases.items():
            with self.subTest(field=field):
                result = self._result()
                result["flip_check"][field] = False
                self._assert_invalid(result, error_code)

    def test_safe_to_continue_false_blocks(self):
        result = self._result()
        result["flip_check"]["safe_to_continue_to_level1_danger"] = False
        self._assert_invalid(result, "safe_to_continue_to_level1_danger_not_true")

    def test_blocked_flags_true_block(self):
        cases = {
            "danger_cell_used": "danger_cell_used_enabled",
            "pathfinding_performed": "pathfinding_performed_enabled",
            "action_executed": "action_executed_enabled",
            "production_action_selection": "production_action_selection_enabled",
            "runtime_action_selection": "runtime_action_selection_enabled",
            "selected_action_created": "selected_action_created_enabled",
            "final_action_created": "final_action_created_enabled",
            "direct_action_command": "direct_action_command_enabled",
            "semantic_or_fuzzy_match_used": "semantic_or_fuzzy_match_used_enabled",
            "lesson_applied": "lesson_applied_enabled",
            "memory_write": "memory_write_enabled",
            "retention_write": "retention_write_enabled",
            "predictor_modified": "predictor_modified_enabled",
            "proof_of_learning_claim": "proof_of_learning_claim_enabled",
        }
        for flag, error_code in cases.items():
            with self.subTest(flag=flag):
                result = self._result()
                result["blocked_flags"][flag] = True
                self._assert_invalid(result, error_code)

    def test_demo_summary_counts_are_deterministic(self):
        result = run_phase0_level0_obstacle_memory_flip_test_minimal_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-phase0-level0-obstacle-memory-flip-test-minimal-check")
        self.assertEqual(result["flow"], "phase0_level0_obstacle_memory_flip_test_minimal_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["level0_flip_result_count"], 49)
        self.assertEqual(summary["valid_level0_flip_result_count"], 1)
        self.assertEqual(summary["invalid_level0_flip_result_count"], 48)
        self.assertEqual(summary["retry_failed_case_count"], 1)
        self.assertEqual(summary["retry_succeeded_case_count"], 1)
        self.assertEqual(summary["failed_memory_prefers_check_count"], 1)
        self.assertEqual(summary["success_memory_prefers_retry_count"], 1)
        self.assertEqual(summary["bidirectional_flip_passed_count"], 1)
        self.assertEqual(summary["one_way_caution_bias_rejected_count"], 1)
        self.assertEqual(summary["safe_to_continue_to_level1_danger_count"], 1)
        self.assertFalse(boundary["danger_cell_used"])
        self.assertFalse(boundary["action_execution_added"])
        self.assertFalse(boundary["pathfinding_added"])
        self.assertFalse(boundary["proof_of_learning_claimed"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-phase0-level0-obstacle-memory-flip-test-minimal-check")

        self.assertEqual(result["command"], "run-phase0-level0-obstacle-memory-flip-test-minimal-check")
        self.assertEqual(result["summary"]["valid_level0_flip_result_count"], 1)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-phase0-level0-obstacle-memory-flip-test-minimal-check",
            ],
            check=True,
            capture_output=True,
            encoding="utf-8",
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-phase0-level0-obstacle-memory-flip-test-minimal-check")
        self.assertEqual(result["summary"]["bidirectional_flip_passed_count"], 1)


if __name__ == "__main__":
    unittest.main()
