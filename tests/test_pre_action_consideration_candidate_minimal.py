import json
import subprocess
import sys
import unittest

from ashl_core.pre_action_consideration_candidate_minimal import (
    build_pre_action_consideration_candidates,
    run_pre_action_consideration_candidate_minimal_check,
    validate_pre_action_consideration_candidate_result,
)
from ashl_core.teaching_cli import run_command


class PreActionConsiderationCandidateMinimalTests(unittest.TestCase):
    def _valid_result(self):
        return build_pre_action_consideration_candidates()

    def _candidate(self, scenario_id):
        for candidate in self._valid_result()["candidates"]:
            if candidate["scenario_id"] == scenario_id:
                return candidate
        self.fail(f"missing candidate {scenario_id}")

    def _assert_invalid(self, record, error_code):
        validation = validate_pre_action_consideration_candidate_result(record)

        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])

    def test_valid_pre_action_candidate_result_is_created(self):
        record = self._valid_result()
        validation = validate_pre_action_consideration_candidate_result(record)

        self.assertTrue(validation["valid"])
        self.assertEqual(record["candidate_count"], 3)
        self.assertEqual(len(record["candidates"]), 3)

    def test_candidates_derive_from_largest_positive_deltas(self):
        record = self._valid_result()

        for candidate in record["candidates"]:
            with self.subTest(candidate=candidate["candidate_id"]):
                self.assertGreater(candidate["delta"], 0.0)
                self.assertLessEqual(candidate["delta"], 0.10)
                self.assertEqual(candidate["consideration_source"], "largest_positive_runtime_tendency_delta")

    def test_expected_candidate_mappings(self):
        self.assertEqual(
            self._candidate("obstacle_retry_failed_same_state")["considered_action"],
            "check_before_retry",
        )
        self.assertEqual(
            self._candidate("costly_retry_same_state")["considered_action"],
            "slow_down_or_reduce_cost",
        )
        self.assertEqual(
            self._candidate("unclear_failure_same_state")["considered_action"],
            "ask_for_help",
        )

    def test_all_candidates_are_pre_action_only_and_not_final_action(self):
        for candidate in self._valid_result()["candidates"]:
            with self.subTest(candidate=candidate["candidate_id"]):
                self.assertTrue(candidate["pre_action_only"])
                self.assertFalse(candidate["selected_as_final_action"])
                self.assertIn(candidate["exact_key"], {
                    "obstacle_retry_failed",
                    "costly_retry_failed",
                    "unclear_failure_repeated",
                })

    def test_unknown_scenario_blocks(self):
        record = self._valid_result()
        record["candidates"][0]["scenario_id"] = "unknown_scenario"
        self._assert_invalid(record, "unknown_scenario_id")

    def test_unknown_exact_key_blocks(self):
        record = self._valid_result()
        record["candidates"][0]["exact_key"] = "semantic_guess"
        self._assert_invalid(record, "unknown_exact_key")

    def test_wrong_mapping_blocks(self):
        record = self._valid_result()
        record["candidates"][0]["considered_action"] = "ask_for_help"
        self._assert_invalid(record, "obstacle_retry_failed_same_state_wrong_considered_action")

    def test_delta_boundaries_block(self):
        cases = [
            ("negative", -0.01, 0.49, "delta_not_positive"),
            ("zero", 0.00, 0.50, "delta_not_positive"),
            ("too_high", 0.11, 0.61, "delta_too_high"),
        ]
        for name, delta, memory_score, error_code in cases:
            with self.subTest(name=name):
                record = self._valid_result()
                record["candidates"][0]["delta"] = delta
                record["candidates"][0]["memory_influenced_score"] = memory_score
                self._assert_invalid(record, error_code)

    def test_wrong_consideration_source_blocks(self):
        record = self._valid_result()
        record["candidates"][0]["consideration_source"] = "manual_selection"
        self._assert_invalid(record, "consideration_source_not_largest_positive_runtime_tendency_delta")

    def test_pre_action_only_false_blocks(self):
        record = self._valid_result()
        record["candidates"][0]["pre_action_only"] = False
        self._assert_invalid(record, "pre_action_only_not_true")

    def test_selected_as_final_action_true_blocks(self):
        record = self._valid_result()
        record["candidates"][0]["selected_as_final_action"] = True
        self._assert_invalid(record, "selected_as_final_action_not_false")

    def test_aggregate_false_fields_block(self):
        cases = [
            "all_candidates_from_exact_key_scenarios",
            "all_candidates_from_positive_delta",
            "all_candidates_pre_action_only",
            "all_candidates_not_final_action",
            "safe_to_continue_to_pre_action_gate_check",
        ]
        for field in cases:
            with self.subTest(field=field):
                record = self._valid_result()
                record["aggregate_result"][field] = False
                self._assert_invalid(record, f"{field}_not_true")

    def test_empty_human_summary_fields_block(self):
        cases = {
            "what_candidates_mean": "what_candidates_mean_empty_or_not_string",
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
            "action_selected": "action_selected_enabled",
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
        result = run_pre_action_consideration_candidate_minimal_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-pre-action-consideration-candidate-minimal-check")
        self.assertEqual(result["flow"], "pre_action_consideration_candidate_minimal_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["pre_action_candidate_result_count"], 40)
        self.assertEqual(summary["valid_pre_action_candidate_result_count"], 1)
        self.assertEqual(summary["invalid_pre_action_candidate_result_count"], 39)
        self.assertEqual(summary["candidate_count"], 3)
        self.assertEqual(summary["positive_delta_candidate_count"], 3)
        self.assertEqual(summary["pre_action_only_candidate_count"], 3)
        self.assertEqual(summary["not_final_action_candidate_count"], 3)
        self.assertEqual(summary["exact_key_candidate_count"], 3)
        self.assertEqual(summary["obstacle_candidate_pass_count"], 1)
        self.assertEqual(summary["costly_retry_candidate_pass_count"], 1)
        self.assertEqual(summary["unclear_failure_candidate_pass_count"], 1)
        self.assertEqual(summary["candidate_count_violation_blocked_count"], 2)
        self.assertEqual(summary["unknown_scenario_blocked_count"], 1)
        self.assertEqual(summary["unknown_exact_key_blocked_count"], 1)
        self.assertEqual(summary["wrong_mapping_blocked_count"], 3)
        self.assertEqual(summary["non_positive_delta_blocked_count"], 2)
        self.assertEqual(summary["delta_too_high_blocked_count"], 1)
        self.assertEqual(summary["pre_action_only_false_blocked_count"], 1)
        self.assertEqual(summary["selected_as_final_action_blocked_count"], 1)
        self.assertEqual(summary["production_action_selection_blocked_count"], 1)
        self.assertEqual(summary["final_action_created_blocked_count"], 1)
        self.assertEqual(summary["action_selected_blocked_count"], 1)
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
        self.assertEqual(boundary["candidate_count"], 3)
        self.assertFalse(boundary["production_action_selection_added"])
        self.assertFalse(boundary["final_action_creation_added"])
        self.assertFalse(boundary["action_selection_added"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-pre-action-consideration-candidate-minimal-check")

        self.assertEqual(result["command"], "run-pre-action-consideration-candidate-minimal-check")
        self.assertEqual(result["summary"]["valid_pre_action_candidate_result_count"], 1)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-pre-action-consideration-candidate-minimal-check",
            ],
            check=True,
            capture_output=True,
            encoding="utf-8",
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-pre-action-consideration-candidate-minimal-check")
        self.assertEqual(result["summary"]["candidate_count"], 3)


if __name__ == "__main__":
    unittest.main()
