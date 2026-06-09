import json
import subprocess
import sys
import unittest
from copy import deepcopy

from ashl_core.expected_actual_outcome_pair_schema import validate_expected_actual_outcome_pair
from ashl_core.outcome_pair_from_action_trial_trace import (
    build_expected_actual_outcome_pair_from_trial_trace,
    build_valid_mismatch_trial_trace,
    build_valid_no_mismatch_trial_trace,
    run_outcome_pair_from_action_trial_trace_check,
)
from ashl_core.teaching_cli import run_command


class OutcomePairFromActionTrialTraceTests(unittest.TestCase):
    def test_valid_mismatch_trial_produces_valid_outcome_pair(self):
        pair = build_expected_actual_outcome_pair_from_trial_trace(build_valid_mismatch_trial_trace())
        validation = validate_expected_actual_outcome_pair(pair)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertIs(pair["mismatch"], True)

    def test_valid_no_mismatch_trial_produces_valid_outcome_pair(self):
        pair = build_expected_actual_outcome_pair_from_trial_trace(build_valid_no_mismatch_trial_trace())
        validation = validate_expected_actual_outcome_pair(pair)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertIs(pair["mismatch"], False)

    def test_generated_pair_passes_expected_actual_outcome_pair_schema(self):
        for trace in [build_valid_mismatch_trial_trace(), build_valid_no_mismatch_trial_trace()]:
            with self.subTest(case_name=trace["case_name"]):
                pair = build_expected_actual_outcome_pair_from_trial_trace(trace)
                validation = validate_expected_actual_outcome_pair(pair)
                self.assertTrue(validation["valid"], validation["error_codes"])

    def test_mismatch_true_creates_structured_failure_reason(self):
        pair = build_expected_actual_outcome_pair_from_trial_trace(build_valid_mismatch_trial_trace())
        reason = pair["failure_reason"]

        self.assertIs(pair["mismatch"], True)
        self.assertIsInstance(reason, dict)
        self.assertEqual(reason["category"], "actual_outcome_did_not_match_expected_outcome")
        self.assertEqual(reason["evidence"]["comparison_rule"], "structured_state_equality")
        self.assertTrue(reason["known"])

    def test_mismatch_false_has_no_failure_reason(self):
        pair = build_expected_actual_outcome_pair_from_trial_trace(build_valid_no_mismatch_trial_trace())

        self.assertIs(pair["mismatch"], False)
        self.assertIsNone(pair["failure_reason"])

    def test_missing_expected_outcome_blocks_pair_generation(self):
        trace = build_valid_mismatch_trial_trace()
        trace.pop("expected_outcome")

        with self.assertRaisesRegex(ValueError, "missing_expected_outcome"):
            build_expected_actual_outcome_pair_from_trial_trace(trace)

    def test_missing_actual_outcome_blocks_pair_generation(self):
        trace = build_valid_mismatch_trial_trace()
        trace["trial_result"].pop("actual_outcome")

        with self.assertRaisesRegex(ValueError, "missing_actual_outcome"):
            build_expected_actual_outcome_pair_from_trial_trace(trace)

    def test_unknown_vs_unknown_trace_blocks_valid_pair(self):
        trace = build_valid_mismatch_trial_trace()
        trace["expected_outcome"]["known"] = False
        trace["trial_result"]["actual_outcome"]["known"] = False

        pair = build_expected_actual_outcome_pair_from_trial_trace(trace)
        validation = validate_expected_actual_outcome_pair(pair)

        self.assertFalse(validation["valid"])
        self.assertIn("unknown_vs_unknown_outcome_pair", validation["error_codes"])

    def test_schema_boundary_violation_blocks_valid_pair(self):
        trace = build_valid_mismatch_trial_trace()
        trace["unsafe_pair_overrides"] = {
            "safety_flags": {"blocked_from_action_selection": False}
        }

        pair = build_expected_actual_outcome_pair_from_trial_trace(trace)
        validation = validate_expected_actual_outcome_pair(pair)

        self.assertFalse(validation["valid"])
        self.assertIn("action_selection_not_blocked", validation["error_codes"])

    def test_generated_pairs_remain_trace_only_and_review_gated(self):
        pair = build_expected_actual_outcome_pair_from_trial_trace(build_valid_mismatch_trial_trace())

        self.assertTrue(pair["safety_flags"]["trace_only"])
        self.assertTrue(pair["review_boundary"]["review_required"])
        self.assertTrue(pair["review_boundary"]["lesson_candidate_allowed"])
        self.assertFalse(pair["review_boundary"]["lesson_application_allowed"])
        self.assertFalse(pair["review_boundary"]["persistent_learning_allowed"])
        self.assertFalse(pair["review_boundary"]["memory_write_allowed"])
        self.assertFalse(pair["review_boundary"]["predictor_mutation_allowed"])

    def test_generated_pairs_remain_blocked_from_runtime_effects(self):
        pair = build_expected_actual_outcome_pair_from_trial_trace(build_valid_mismatch_trial_trace())
        for flag in [
            "blocked_from_action_selection",
            "blocked_from_action_behavior_change",
            "blocked_from_lesson_application",
            "blocked_from_memory_write",
            "blocked_from_predictor_mutation",
            "blocked_from_persistent_rule_write",
        ]:
            with self.subTest(flag=flag):
                self.assertTrue(pair["safety_flags"][flag])

    def test_generated_pairs_create_no_runtime_or_mutation_flags(self):
        pair = build_expected_actual_outcome_pair_from_trial_trace(build_valid_mismatch_trial_trace())
        for flag in [
            "action_selection_influence",
            "action_behavior_changed",
            "lesson_application_runtime",
            "memory_write",
            "predictor_modified",
            "persistent_rule_write",
            "endocrine_control",
            "autonomy_enabled",
        ]:
            with self.subTest(flag=flag):
                self.assertFalse(pair["safety_flags"][flag])

    def test_build_does_not_mutate_trial_trace(self):
        trace = build_valid_mismatch_trial_trace()
        original = deepcopy(trace)

        build_expected_actual_outcome_pair_from_trial_trace(trace)

        self.assertEqual(trace, original)

    def test_demo_check_summary_has_expected_counts(self):
        result = run_outcome_pair_from_action_trial_trace_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-outcome-pair-from-action-trial-trace-check")
        self.assertEqual(result["flow"], "outcome_pair_from_action_trial_trace_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["trial_trace_count"], 6)
        self.assertEqual(summary["valid_trial_trace_count"], 2)
        self.assertEqual(summary["invalid_trial_trace_count"], 4)
        self.assertEqual(summary["generated_pair_count"], 4)
        self.assertEqual(summary["valid_pair_count"], 2)
        self.assertEqual(summary["invalid_pair_count"], 2)
        self.assertEqual(summary["mismatch_true_count"], 1)
        self.assertEqual(summary["mismatch_false_count"], 1)
        self.assertEqual(summary["failure_reason_created_count"], 1)
        self.assertEqual(summary["missing_expected_outcome_blocked_count"], 1)
        self.assertEqual(summary["missing_actual_outcome_blocked_count"], 1)
        self.assertEqual(summary["unknown_vs_unknown_blocked_count"], 1)
        self.assertEqual(summary["schema_validation_failed_count"], 2)
        self.assertEqual(summary["action_selection_influence_count"], 0)
        self.assertEqual(summary["action_behavior_changed_count"], 0)
        self.assertEqual(summary["lesson_application_runtime_count"], 0)
        self.assertEqual(summary["memory_write_count"], 0)
        self.assertEqual(summary["predictor_modified_count"], 0)
        self.assertEqual(summary["persistent_rule_write_count"], 0)
        self.assertEqual(summary["endocrine_control_count"], 0)
        self.assertEqual(summary["autonomy_enabled_count"], 0)
        self.assertTrue(boundary["trace_check_only"])
        self.assertTrue(boundary["uses_expected_actual_outcome_pair_schema"])
        self.assertTrue(boundary["structured_state_equality_only"])
        self.assertFalse(boundary["free_form_outcome_comparison_used"])
        self.assertFalse(boundary["llm_semantic_comparison_used"])
        self.assertFalse(boundary["runtime_action_selection_added"])
        self.assertFalse(boundary["action_selection_modified"])
        self.assertFalse(boundary["predictor_mutation_added"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-outcome-pair-from-action-trial-trace-check")

        self.assertEqual(result["command"], "run-outcome-pair-from-action-trial-trace-check")
        self.assertEqual(result["summary"]["valid_pair_count"], 2)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [sys.executable, "-m", "ashl_core.teaching_cli", "run-outcome-pair-from-action-trial-trace-check"],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-outcome-pair-from-action-trial-trace-check")
        self.assertEqual(result["summary"]["generated_pair_count"], 4)


if __name__ == "__main__":
    unittest.main()
