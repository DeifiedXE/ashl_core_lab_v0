import json
import subprocess
import sys
import unittest
from copy import deepcopy

from ashl_core.expected_actual_outcome_pair_schema import build_valid_mismatch_pair_record
from ashl_core.failure_reason_from_outcome_pair import (
    ALLOWED_CATEGORIES,
    build_failure_reason_from_outcome_pair,
    run_failure_reason_from_outcome_pair_check,
    validate_failure_reason_record,
)
from ashl_core.outcome_pair_from_action_trial_trace import (
    build_expected_actual_outcome_pair_from_trial_trace,
    build_valid_mismatch_trial_trace,
    build_valid_no_mismatch_trial_trace,
)
from ashl_core.teaching_cli import run_command


class FailureReasonFromOutcomePairTests(unittest.TestCase):
    def _valid_reason(self):
        pair = build_expected_actual_outcome_pair_from_trial_trace(build_valid_mismatch_trial_trace())
        return build_failure_reason_from_outcome_pair(pair)

    def test_valid_mismatch_outcome_pair_produces_valid_failure_reason(self):
        reason = self._valid_reason()
        validation = validate_failure_reason_record(reason)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(reason["category"], "actual_outcome_did_not_match_expected_outcome")
        self.assertTrue(reason["known"])

    def test_mismatch_false_produces_no_failure_reason_needed(self):
        pair = build_expected_actual_outcome_pair_from_trial_trace(build_valid_no_mismatch_trial_trace())

        self.assertIsNone(build_failure_reason_from_outcome_pair(pair))

    def test_invalid_outcome_pair_does_not_produce_valid_failure_reason(self):
        pair = build_expected_actual_outcome_pair_from_trial_trace(build_valid_mismatch_trial_trace())
        pair["expected_outcome"]["known"] = False
        pair["actual_outcome"]["known"] = False

        with self.assertRaisesRegex(ValueError, "invalid_outcome_pair"):
            build_failure_reason_from_outcome_pair(pair)

    def test_failure_reason_links_to_source_pair_id(self):
        pair = build_expected_actual_outcome_pair_from_trial_trace(build_valid_mismatch_trial_trace())
        reason = build_failure_reason_from_outcome_pair(pair)

        self.assertEqual(reason["source_pair_id"], pair["pair_id"])
        self.assertEqual(reason["evidence"]["source_pair_id"], pair["pair_id"])
        self.assertEqual(reason["source_trace"]["source_pair_id"], pair["pair_id"])

    def test_failure_reason_includes_expected_and_actual_evidence_ids(self):
        pair = build_expected_actual_outcome_pair_from_trial_trace(build_valid_mismatch_trial_trace())
        reason = build_failure_reason_from_outcome_pair(pair)

        self.assertEqual(reason["evidence"]["expected_outcome_id"], pair["expected_outcome"]["outcome_id"])
        self.assertEqual(reason["evidence"]["actual_outcome_id"], pair["actual_outcome"]["outcome_id"])
        self.assertEqual(reason["evidence"]["comparison_rule"], "structured_state_equality")
        self.assertIs(reason["evidence"]["mismatch"], True)

    def test_failure_reason_category_must_be_allowed(self):
        self.assertIn(self._valid_reason()["category"], ALLOWED_CATEGORIES)

    def test_embedded_allowed_category_is_preserved(self):
        reason = build_failure_reason_from_outcome_pair(build_valid_mismatch_pair_record())

        self.assertEqual(reason["category"], "blocked_or_unmet_expected_outcome")
        self.assertTrue(validate_failure_reason_record(reason)["valid"])

    def test_unknown_embedded_category_falls_back_to_default_category(self):
        pair = build_expected_actual_outcome_pair_from_trial_trace(build_valid_mismatch_trial_trace())
        pair["failure_reason"]["category"] = "free_form_guess"

        reason = build_failure_reason_from_outcome_pair(pair)

        self.assertEqual(reason["category"], "actual_outcome_did_not_match_expected_outcome")
        self.assertTrue(validate_failure_reason_record(reason)["valid"])

    def test_unknown_category_blocks_record(self):
        reason = self._valid_reason()
        reason["category"] = "free_form_unknown"
        validation = validate_failure_reason_record(reason)

        self.assertFalse(validation["valid"])
        self.assertIn("unknown_category", validation["error_codes"])

    def test_missing_evidence_blocks_record(self):
        reason = self._valid_reason()
        reason.pop("evidence")
        validation = validate_failure_reason_record(reason)

        self.assertFalse(validation["valid"])
        self.assertIn("missing_evidence", validation["error_codes"])

    def test_missing_source_pair_id_blocks_record(self):
        reason = self._valid_reason()
        reason.pop("source_pair_id")
        validation = validate_failure_reason_record(reason)

        self.assertFalse(validation["valid"])
        self.assertIn("missing_required_field:source_pair_id", validation["error_codes"])

    def test_review_required_false_blocks_record(self):
        self._assert_review_boundary_error("review_required", False, "review_required_not_true")

    def test_lesson_application_allowed_true_blocks_record(self):
        self._assert_review_boundary_error(
            "lesson_application_allowed",
            True,
            "lesson_application_allowed_enabled",
        )

    def test_persistent_learning_allowed_true_blocks_record(self):
        self._assert_review_boundary_error(
            "persistent_learning_allowed",
            True,
            "persistent_learning_allowed_enabled",
        )

    def test_memory_write_allowed_true_blocks_record(self):
        self._assert_review_boundary_error("memory_write_allowed", True, "memory_write_allowed_enabled")

    def test_predictor_mutation_allowed_true_blocks_record(self):
        self._assert_review_boundary_error(
            "predictor_mutation_allowed",
            True,
            "predictor_mutation_allowed_enabled",
        )

    def test_lesson_candidate_created_true_blocks_record(self):
        self._assert_safety_error("lesson_candidate_created", True, "lesson_candidate_created_enabled")

    def test_blocked_from_action_selection_false_blocks_record(self):
        self._assert_safety_error("blocked_from_action_selection", False, "action_selection_not_blocked")

    def test_blocked_from_action_behavior_change_false_blocks_record(self):
        self._assert_safety_error(
            "blocked_from_action_behavior_change",
            False,
            "action_behavior_change_not_blocked",
        )

    def test_blocked_from_lesson_application_false_blocks_record(self):
        self._assert_safety_error("blocked_from_lesson_application", False, "lesson_application_not_blocked")

    def test_blocked_from_memory_write_false_blocks_record(self):
        self._assert_safety_error("blocked_from_memory_write", False, "memory_write_not_blocked")

    def test_blocked_from_predictor_mutation_false_blocks_record(self):
        self._assert_safety_error("blocked_from_predictor_mutation", False, "predictor_mutation_not_blocked")

    def test_blocked_from_persistent_rule_write_false_blocks_record(self):
        self._assert_safety_error(
            "blocked_from_persistent_rule_write",
            False,
            "persistent_rule_write_not_blocked",
        )

    def test_action_selection_influence_true_blocks_record(self):
        self._assert_safety_error("action_selection_influence", True, "action_selection_influence_enabled")

    def test_action_behavior_changed_nonzero_blocks_record(self):
        self._assert_safety_error("action_behavior_changed", 1, "action_behavior_changed_enabled")

    def test_lesson_application_runtime_true_blocks_record(self):
        self._assert_safety_error("lesson_application_runtime", True, "lesson_application_runtime_enabled")

    def test_memory_write_true_blocks_record(self):
        self._assert_safety_error("memory_write", True, "memory_write_enabled")

    def test_predictor_modified_true_blocks_record(self):
        self._assert_safety_error("predictor_modified", True, "predictor_modified_enabled")

    def test_persistent_rule_write_true_blocks_record(self):
        self._assert_safety_error("persistent_rule_write", True, "persistent_rule_write_enabled")

    def test_endocrine_control_true_blocks_record(self):
        self._assert_safety_error("endocrine_control", True, "endocrine_control_enabled")

    def test_autonomy_enabled_true_blocks_record(self):
        self._assert_safety_error("autonomy_enabled", True, "autonomy_enabled_enabled")

    def test_build_does_not_mutate_outcome_pair(self):
        pair = build_expected_actual_outcome_pair_from_trial_trace(build_valid_mismatch_trial_trace())
        original = deepcopy(pair)

        build_failure_reason_from_outcome_pair(pair)

        self.assertEqual(pair, original)

    def test_demo_check_summary_has_expected_counts(self):
        result = run_failure_reason_from_outcome_pair_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-failure-reason-from-outcome-pair-check")
        self.assertEqual(result["flow"], "failure_reason_from_outcome_pair_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["outcome_pair_count"], 3)
        self.assertEqual(summary["valid_outcome_pair_count"], 2)
        self.assertEqual(summary["invalid_outcome_pair_count"], 1)
        self.assertEqual(summary["mismatch_true_pair_count"], 1)
        self.assertEqual(summary["mismatch_false_pair_count"], 1)
        self.assertEqual(summary["failure_reason_record_count"], 11)
        self.assertEqual(summary["valid_failure_reason_count"], 1)
        self.assertEqual(summary["invalid_failure_reason_count"], 10)
        self.assertEqual(summary["no_failure_reason_needed_count"], 1)
        self.assertEqual(summary["missing_source_pair_blocked_count"], 1)
        self.assertEqual(summary["unknown_category_blocked_count"], 1)
        self.assertEqual(summary["missing_evidence_blocked_count"], 1)
        self.assertEqual(summary["review_boundary_violation_blocked_count"], 1)
        self.assertEqual(summary["lesson_candidate_created_blocked_count"], 1)
        self.assertEqual(summary["action_selection_unblocked_blocked_count"], 1)
        self.assertEqual(summary["lesson_application_unblocked_blocked_count"], 1)
        self.assertEqual(summary["memory_write_unblocked_blocked_count"], 1)
        self.assertEqual(summary["predictor_mutation_unblocked_blocked_count"], 1)
        self.assertEqual(summary["persistent_rule_write_unblocked_blocked_count"], 1)
        for field in [
            "action_selection_influence_count",
            "action_behavior_changed_count",
            "lesson_application_runtime_count",
            "lesson_candidate_created_count",
            "memory_write_count",
            "predictor_modified_count",
            "persistent_rule_write_count",
            "endocrine_control_count",
            "autonomy_enabled_count",
        ]:
            with self.subTest(field=field):
                self.assertEqual(summary[field], 0)
        self.assertTrue(boundary["trace_check_only"])
        self.assertTrue(boundary["uses_outcome_pair_from_action_trial_trace"])
        self.assertTrue(boundary["uses_expected_actual_outcome_pair_schema"])
        self.assertTrue(boundary["v0_local_failure_reason_validator"])
        self.assertFalse(boundary["lesson_candidate_generation_added"])
        self.assertFalse(boundary["runtime_action_selection_added"])
        self.assertFalse(boundary["action_selection_modified"])
        self.assertFalse(boundary["new_action_behavior_added"])
        self.assertFalse(boundary["lesson_application_runtime_added"])
        self.assertFalse(boundary["persistent_learning_added"])
        self.assertFalse(boundary["memory_write_added"])
        self.assertFalse(boundary["predictor_mutation_added"])
        self.assertFalse(boundary["autonomy_added"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-failure-reason-from-outcome-pair-check")

        self.assertEqual(result["command"], "run-failure-reason-from-outcome-pair-check")
        self.assertEqual(result["summary"]["valid_failure_reason_count"], 1)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [sys.executable, "-m", "ashl_core.teaching_cli", "run-failure-reason-from-outcome-pair-check"],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-failure-reason-from-outcome-pair-check")
        self.assertEqual(result["summary"]["failure_reason_record_count"], 11)

    def _assert_review_boundary_error(self, field, value, error_code):
        reason = self._valid_reason()
        reason["review_boundary"][field] = value
        validation = validate_failure_reason_record(reason)

        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])

    def _assert_safety_error(self, field, value, error_code):
        reason = self._valid_reason()
        reason["safety_flags"][field] = value
        validation = validate_failure_reason_record(reason)

        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])


if __name__ == "__main__":
    unittest.main()
