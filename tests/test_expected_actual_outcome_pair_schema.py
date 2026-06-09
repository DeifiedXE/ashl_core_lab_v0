import json
import subprocess
import sys
import unittest

from ashl_core.expected_actual_outcome_pair_schema import (
    build_valid_mismatch_pair_record,
    build_valid_no_mismatch_pair_record,
    run_expected_actual_outcome_pair_schema_check,
    validate_expected_actual_outcome_pair,
)
from ashl_core.teaching_cli import run_command


class ExpectedActualOutcomePairSchemaTests(unittest.TestCase):
    def test_valid_mismatch_pair_passes(self):
        validation = validate_expected_actual_outcome_pair(build_valid_mismatch_pair_record())

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertTrue(validation["has_expected_outcome"])
        self.assertTrue(validation["has_actual_outcome"])
        self.assertIs(validation["mismatch"], True)
        self.assertTrue(validation["failure_reason_required"])
        self.assertTrue(validation["failure_reason_valid"])
        self.assertTrue(validation["trace_only"])
        self.assertTrue(validation["review_required"])

    def test_valid_no_mismatch_pair_passes(self):
        validation = validate_expected_actual_outcome_pair(build_valid_no_mismatch_pair_record())

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertIs(validation["mismatch"], False)
        self.assertFalse(validation["failure_reason_required"])
        self.assertFalse(validation["failure_reason_valid"])

    def test_missing_expected_outcome_blocks_pair(self):
        record = build_valid_mismatch_pair_record()
        record.pop("expected_outcome")

        validation = validate_expected_actual_outcome_pair(record)
        self.assertFalse(validation["valid"])
        self.assertIn("missing_required_field:expected_outcome", validation["error_codes"])
        self.assertIn("expected_outcome_missing_or_not_dict", validation["error_codes"])

    def test_missing_actual_outcome_blocks_pair(self):
        record = build_valid_mismatch_pair_record()
        record.pop("actual_outcome")

        validation = validate_expected_actual_outcome_pair(record)
        self.assertFalse(validation["valid"])
        self.assertIn("missing_required_field:actual_outcome", validation["error_codes"])
        self.assertIn("actual_outcome_missing_or_not_dict", validation["error_codes"])

    def test_mismatch_missing_blocks_pair(self):
        record = build_valid_mismatch_pair_record()
        record.pop("mismatch")

        validation = validate_expected_actual_outcome_pair(record)
        self.assertFalse(validation["valid"])
        self.assertIn("missing_required_field:mismatch", validation["error_codes"])
        self.assertIn("mismatch_not_boolean", validation["error_codes"])

    def test_mismatch_non_boolean_blocks_pair(self):
        record = build_valid_mismatch_pair_record()
        record["mismatch"] = "true"

        validation = validate_expected_actual_outcome_pair(record)
        self.assertFalse(validation["valid"])
        self.assertIn("mismatch_not_boolean", validation["error_codes"])

    def test_unknown_expected_and_unknown_actual_blocks_pair(self):
        record = build_valid_mismatch_pair_record()
        record["expected_outcome"]["known"] = False
        record["actual_outcome"]["known"] = False

        validation = validate_expected_actual_outcome_pair(record)
        self.assertFalse(validation["valid"])
        self.assertIn("unknown_vs_unknown_outcome_pair", validation["error_codes"])

    def test_mismatch_true_requires_structured_failure_reason(self):
        record = build_valid_mismatch_pair_record()
        record["failure_reason"] = None

        validation = validate_expected_actual_outcome_pair(record)
        self.assertFalse(validation["valid"])
        self.assertIn("failure_reason_missing_or_not_dict", validation["error_codes"])

    def test_failure_reason_missing_required_fields_blocks_pair(self):
        record = build_valid_mismatch_pair_record()
        record["failure_reason"].pop("category")

        validation = validate_expected_actual_outcome_pair(record)
        self.assertFalse(validation["valid"])
        self.assertIn("failure_reason_missing_field:category", validation["error_codes"])

    def test_outcome_required_fields_block_pair(self):
        for outcome_name, error_code in [
            ("expected_outcome", "expected_outcome_missing_field:known"),
            ("actual_outcome", "actual_outcome_missing_field:known"),
        ]:
            with self.subTest(outcome_name=outcome_name):
                record = build_valid_mismatch_pair_record()
                record[outcome_name].pop("known")
                validation = validate_expected_actual_outcome_pair(record)
                self.assertFalse(validation["valid"])
                self.assertIn(error_code, validation["error_codes"])

    def test_review_boundary_blocks_runtime_permissions(self):
        for flag, error_code in [
            ("review_required", "review_required_not_true"),
            ("lesson_application_allowed", "lesson_application_allowed_enabled"),
            ("persistent_learning_allowed", "persistent_learning_allowed_enabled"),
            ("memory_write_allowed", "memory_write_allowed_enabled"),
            ("predictor_mutation_allowed", "predictor_mutation_allowed_enabled"),
        ]:
            with self.subTest(flag=flag):
                record = build_valid_mismatch_pair_record()
                record["review_boundary"][flag] = False if flag == "review_required" else True
                validation = validate_expected_actual_outcome_pair(record)
                self.assertFalse(validation["valid"])
                self.assertIn(error_code, validation["error_codes"])

    def test_required_blocking_safety_flags_block_pair(self):
        for flag, error_code in [
            ("trace_only", "trace_only_not_true"),
            ("blocked_from_action_selection", "action_selection_not_blocked"),
            ("blocked_from_action_behavior_change", "action_behavior_change_not_blocked"),
            ("blocked_from_lesson_application", "lesson_application_not_blocked"),
            ("blocked_from_memory_write", "memory_write_not_blocked"),
            ("blocked_from_predictor_mutation", "predictor_mutation_not_blocked"),
            ("blocked_from_persistent_rule_write", "persistent_rule_write_not_blocked"),
        ]:
            with self.subTest(flag=flag):
                record = build_valid_mismatch_pair_record()
                record["safety_flags"][flag] = False
                validation = validate_expected_actual_outcome_pair(record)
                self.assertFalse(validation["valid"])
                self.assertIn(error_code, validation["error_codes"])

    def test_runtime_and_mutation_safety_flags_block_pair(self):
        for flag, error_code in [
            ("action_selection_influence", "action_selection_influence_enabled"),
            ("action_behavior_changed", "action_behavior_changed_enabled"),
            ("lesson_application_runtime", "lesson_application_runtime_enabled"),
            ("memory_write", "memory_write_enabled"),
            ("predictor_modified", "predictor_modified_enabled"),
            ("persistent_rule_write", "persistent_rule_write_enabled"),
            ("endocrine_control", "endocrine_control_enabled"),
            ("autonomy_enabled", "autonomy_enabled"),
        ]:
            with self.subTest(flag=flag):
                record = build_valid_mismatch_pair_record()
                record["safety_flags"][flag] = 1
                validation = validate_expected_actual_outcome_pair(record)
                self.assertFalse(validation["valid"])
                self.assertIn(error_code, validation["error_codes"])

    def test_demo_check_summary_has_expected_counts(self):
        result = run_expected_actual_outcome_pair_schema_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-expected-actual-outcome-pair-schema-check")
        self.assertEqual(result["flow"], "expected_actual_outcome_pair_schema_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["pair_record_count"], 12)
        self.assertEqual(summary["valid_pair_count"], 2)
        self.assertEqual(summary["invalid_pair_count"], 10)
        self.assertEqual(summary["mismatch_true_count"], 1)
        self.assertEqual(summary["mismatch_false_count"], 1)
        self.assertGreaterEqual(summary["missing_expected_outcome_blocked_count"], 1)
        self.assertGreaterEqual(summary["missing_actual_outcome_blocked_count"], 1)
        self.assertGreaterEqual(summary["non_boolean_mismatch_blocked_count"], 1)
        self.assertGreaterEqual(summary["unknown_vs_unknown_blocked_count"], 1)
        self.assertGreaterEqual(summary["missing_failure_reason_blocked_count"], 1)
        self.assertGreaterEqual(summary["action_selection_unblocked_blocked_count"], 1)
        self.assertGreaterEqual(summary["lesson_application_unblocked_blocked_count"], 1)
        self.assertGreaterEqual(summary["memory_write_unblocked_blocked_count"], 1)
        self.assertGreaterEqual(summary["predictor_mutation_unblocked_blocked_count"], 1)
        self.assertGreaterEqual(summary["persistent_rule_write_unblocked_blocked_count"], 1)
        self.assertEqual(summary["action_selection_influence_count"], 0)
        self.assertEqual(summary["action_behavior_changed_count"], 0)
        self.assertEqual(summary["lesson_application_runtime_count"], 0)
        self.assertEqual(summary["memory_write_count"], 0)
        self.assertEqual(summary["predictor_modified_count"], 0)
        self.assertEqual(summary["persistent_rule_write_count"], 0)
        self.assertEqual(summary["endocrine_control_count"], 0)
        self.assertEqual(summary["autonomy_enabled_count"], 0)
        self.assertTrue(boundary["schema_check_only"])
        self.assertTrue(boundary["trace_only_pairs"])
        self.assertTrue(boundary["review_gated_pairs"])
        self.assertFalse(boundary["runtime_action_selection_added"])
        self.assertFalse(boundary["action_selection_modified"])
        self.assertFalse(boundary["predictor_mutation_added"])

    def test_run_command_dispatches_schema_check(self):
        result = run_command("run-expected-actual-outcome-pair-schema-check")

        self.assertEqual(result["command"], "run-expected-actual-outcome-pair-schema-check")
        self.assertEqual(result["summary"]["valid_pair_count"], 2)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [sys.executable, "-m", "ashl_core.teaching_cli", "run-expected-actual-outcome-pair-schema-check"],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-expected-actual-outcome-pair-schema-check")
        self.assertEqual(result["summary"]["pair_record_count"], 12)


if __name__ == "__main__":
    unittest.main()
