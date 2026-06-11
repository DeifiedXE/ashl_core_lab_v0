import json
import subprocess
import sys
import unittest

from ashl_core.runtime_tendency_memory_influence_multi_scenario_check_minimal import (
    build_runtime_tendency_multi_scenario_result,
    run_runtime_tendency_memory_influence_multi_scenario_check_minimal_check,
    validate_runtime_tendency_multi_scenario_result,
)
from ashl_core.teaching_cli import run_command


class RuntimeTendencyMemoryInfluenceMultiScenarioCheckMinimalTests(unittest.TestCase):
    def _valid_result(self):
        return build_runtime_tendency_multi_scenario_result()

    def _scenario(self, exact_key):
        for scenario in self._valid_result()["scenario_results"]:
            if scenario["exact_key"] == exact_key:
                return scenario
        self.fail(f"missing scenario {exact_key}")

    def _assert_invalid(self, record, error_code):
        validation = validate_runtime_tendency_multi_scenario_result(record)

        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])

    def test_valid_multi_scenario_result_is_created(self):
        record = self._valid_result()
        validation = validate_runtime_tendency_multi_scenario_result(record)

        self.assertTrue(validation["valid"])
        self.assertEqual(record["scenario_count"], 3)
        self.assertTrue(record["same_candidate_actions_used"])

    def test_obstacle_scenario_changes_expected_deltas(self):
        scenario = self._scenario("obstacle_retry_failed")

        self.assertEqual(scenario["score_deltas"]["check_before_retry"], 0.10)
        self.assertEqual(scenario["score_deltas"]["retry_same_action"], -0.05)

    def test_costly_retry_scenario_changes_expected_deltas(self):
        scenario = self._scenario("costly_retry_failed")

        self.assertEqual(scenario["score_deltas"]["slow_down_or_reduce_cost"], 0.10)
        self.assertEqual(scenario["score_deltas"]["retry_same_action"], -0.05)

    def test_unclear_failure_scenario_changes_expected_deltas(self):
        scenario = self._scenario("unclear_failure_repeated")

        self.assertEqual(scenario["score_deltas"]["ask_for_help"], 0.10)
        self.assertEqual(scenario["score_deltas"]["retry_same_action"], -0.05)

    def test_all_scenarios_remain_within_delta_limit_and_ready(self):
        record = self._valid_result()

        for scenario in record["scenario_results"]:
            with self.subTest(scenario=scenario["scenario_id"]):
                self.assertLessEqual(scenario["max_absolute_delta"], 0.10)
                self.assertTrue(scenario["rollback_ready"])
                self.assertTrue(scenario["mentor_override_ready"])
                self.assertIn(scenario["exact_key"], {
                    "obstacle_retry_failed",
                    "costly_retry_failed",
                    "unclear_failure_repeated",
                })

    def test_unknown_exact_key_blocks(self):
        record = self._valid_result()
        record["scenario_results"][0]["exact_key"] = "semantic_guess"
        self._assert_invalid(record, "unknown_exact_key")

    def test_wrong_delta_blocks(self):
        record = self._valid_result()
        record["scenario_results"][0]["score_deltas"]["check_before_retry"] = 0.09
        self._assert_invalid(record, "obstacle_retry_failed_check_before_retry_delta_unexpected")

    def test_max_absolute_delta_too_high_blocks(self):
        record = self._valid_result()
        record["scenario_results"][0]["max_absolute_delta"] = 0.11
        self._assert_invalid(record, "max_absolute_delta_too_high")

    def test_rollback_ready_false_blocks(self):
        record = self._valid_result()
        record["scenario_results"][0]["rollback_ready"] = False
        self._assert_invalid(record, "rollback_ready_not_true")

    def test_mentor_override_ready_false_blocks(self):
        record = self._valid_result()
        record["scenario_results"][0]["mentor_override_ready"] = False
        self._assert_invalid(record, "mentor_override_ready_not_true")

    def test_aggregate_false_fields_block(self):
        cases = [
            "all_scenarios_changed",
            "all_scenarios_within_delta_limit",
            "all_scenarios_exact_key_only",
            "all_scenarios_rollback_ready",
            "all_scenarios_mentor_override_ready",
            "safe_to_continue_to_pre_action_consideration_design",
        ]
        for field in cases:
            with self.subTest(field=field):
                record = self._valid_result()
                record["aggregate_result"][field] = False
                self._assert_invalid(record, f"{field}_not_true")

    def test_empty_human_summary_blocks(self):
        cases = {
            "what_changed": "what_changed_empty_or_not_string",
            "plain_result": "plain_result_empty_or_not_string",
        }
        for field, error_code in cases.items():
            with self.subTest(field=field):
                record = self._valid_result()
                record["human_summary"][field] = ""
                self._assert_invalid(record, error_code)

    def test_blocked_flags_true_block(self):
        cases = {
            "production_action_selection": "production_action_selection_enabled",
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
                record = self._valid_result()
                record["blocked_flags"][flag] = True
                self._assert_invalid(record, error_code)

    def test_demo_summary_counts_are_deterministic(self):
        result = run_runtime_tendency_memory_influence_multi_scenario_check_minimal_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(
            result["command"],
            "run-runtime-tendency-memory-influence-multi-scenario-check-minimal-check",
        )
        self.assertEqual(result["flow"], "runtime_tendency_memory_influence_multi_scenario_check_minimal_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["multi_scenario_result_count"], 36)
        self.assertEqual(summary["valid_multi_scenario_result_count"], 1)
        self.assertEqual(summary["invalid_multi_scenario_result_count"], 35)
        self.assertEqual(summary["scenario_count"], 3)
        self.assertEqual(summary["changed_scenario_count"], 3)
        self.assertEqual(summary["within_delta_limit_scenario_count"], 3)
        self.assertEqual(summary["rollback_ready_scenario_count"], 3)
        self.assertEqual(summary["mentor_override_ready_scenario_count"], 3)
        self.assertEqual(summary["exact_key_only_scenario_count"], 3)
        self.assertEqual(summary["obstacle_scenario_pass_count"], 1)
        self.assertEqual(summary["costly_retry_scenario_pass_count"], 1)
        self.assertEqual(summary["unclear_failure_scenario_pass_count"], 1)
        self.assertEqual(summary["max_absolute_delta_violation_blocked_count"], 1)
        self.assertEqual(summary["unknown_exact_key_blocked_count"], 1)
        self.assertEqual(summary["wrong_delta_blocked_count"], 3)
        self.assertEqual(summary["rollback_ready_false_blocked_count"], 1)
        self.assertEqual(summary["mentor_override_ready_false_blocked_count"], 1)
        self.assertEqual(summary["aggregate_changed_false_blocked_count"], 1)
        self.assertEqual(summary["aggregate_delta_limit_false_blocked_count"], 1)
        self.assertEqual(summary["aggregate_exact_key_false_blocked_count"], 1)
        self.assertEqual(summary["aggregate_rollback_false_blocked_count"], 1)
        self.assertEqual(summary["aggregate_mentor_override_false_blocked_count"], 1)
        self.assertEqual(summary["safe_to_continue_false_blocked_count"], 1)
        self.assertEqual(summary["production_action_selection_blocked_count"], 1)
        self.assertEqual(summary["final_action_created_blocked_count"], 1)
        self.assertEqual(summary["action_executed_blocked_count"], 1)
        self.assertEqual(summary["direct_action_command_blocked_count"], 1)
        self.assertEqual(summary["real_navigation_changed_blocked_count"], 1)
        self.assertEqual(summary["ui_behavior_changed_blocked_count"], 1)
        self.assertEqual(summary["persistent_policy_written_blocked_count"], 1)
        self.assertEqual(summary["general_behavior_changed_blocked_count"], 1)
        self.assertEqual(summary["semantic_or_fuzzy_match_used_blocked_count"], 1)
        self.assertEqual(summary["exploration_blocked_count"], 1)
        self.assertEqual(summary["curiosity_overridden_blocked_count"], 1)
        self.assertEqual(summary["mentor_override_blocked_count"], 1)
        self.assertEqual(summary["lesson_applied_blocked_count"], 1)
        self.assertEqual(summary["memory_write_blocked_count"], 1)
        self.assertEqual(summary["new_retention_written_blocked_count"], 1)
        self.assertEqual(summary["predictor_modified_blocked_count"], 1)
        self.assertEqual(summary["proof_of_learning_claim_blocked_count"], 1)
        self.assertEqual(boundary["scenario_count"], 3)
        self.assertEqual(boundary["changed_scenario_count"], 3)
        self.assertEqual(boundary["within_delta_limit_scenario_count"], 3)
        self.assertEqual(boundary["rollback_ready_scenario_count"], 3)
        self.assertEqual(boundary["mentor_override_ready_scenario_count"], 3)
        self.assertEqual(boundary["exact_key_only_scenario_count"], 3)
        self.assertFalse(boundary["production_action_selection_added"])
        self.assertFalse(boundary["final_action_creation_added"])
        self.assertFalse(boundary["action_execution_added"])
        self.assertFalse(boundary["direct_action_command_added"])
        self.assertFalse(boundary["semantic_or_fuzzy_matching_added"])
        self.assertFalse(boundary["persistent_policy_write_added"])
        self.assertFalse(boundary["general_behavior_change_added"])
        self.assertFalse(boundary["predictor_mutation_added"])
        self.assertFalse(boundary["proof_of_learning_claimed"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-runtime-tendency-memory-influence-multi-scenario-check-minimal-check")

        self.assertEqual(
            result["command"],
            "run-runtime-tendency-memory-influence-multi-scenario-check-minimal-check",
        )
        self.assertEqual(result["summary"]["valid_multi_scenario_result_count"], 1)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-runtime-tendency-memory-influence-multi-scenario-check-minimal-check",
            ],
            check=True,
            capture_output=True,
            encoding="utf-8",
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(
            result["command"],
            "run-runtime-tendency-memory-influence-multi-scenario-check-minimal-check",
        )
        self.assertEqual(result["summary"]["changed_scenario_count"], 3)


if __name__ == "__main__":
    unittest.main()
