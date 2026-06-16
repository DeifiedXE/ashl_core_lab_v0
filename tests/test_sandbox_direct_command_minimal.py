import unittest
from copy import deepcopy

from ashl_core.sandbox_direct_command_minimal import (
    BOUNDARY_INDEX_AFTER,
    BOUNDARY_INDEX_BEFORE,
    DIRECT_COMMAND,
    build_sandbox_direct_command_record,
    build_sandbox_direct_command_summary,
    run_sandbox_direct_command_minimal_check,
    validate_sandbox_direct_command_record,
    validate_sandbox_direct_command_summary,
)


class SandboxDirectCommandMinimalTests(unittest.TestCase):
    def setUp(self):
        self.record = build_sandbox_direct_command_record()

    def test_valid_sandbox_direct_command_is_created(self):
        result = validate_sandbox_direct_command_record(self.record)
        self.assertTrue(result["valid"], result["error_codes"])
        self.assertEqual("sandbox_direct_command", self.record["record_type"])
        self.assertEqual(DIRECT_COMMAND, self.record["direct_command"])
        self.assertTrue(self.record["direct_command_created"])

    def test_direct_command_is_sandbox_only(self):
        result = validate_sandbox_direct_command_record(self.record)
        self.assertTrue(result["sandbox_scope_checked"])
        self.assertEqual("phase0_level3_sandbox_only", self.record["sandbox_scope"])
        self.assertEqual("sandbox_only", self.record["direct_command_scope"])
        self.assertTrue(self.record["command_is_sandbox_only"])

    def test_sources_are_reused_and_checked(self):
        result = validate_sandbox_direct_command_record(self.record)
        self.assertTrue(result["direct_command_source_checked"])
        self.assertEqual(
            "sandbox_direct_command_approval_boundary_b100",
            self.record["source_direct_command_approval_boundary"],
        )
        self.assertEqual("sandbox_final_action_b99", self.record["source_final_action"])

    def test_direct_command_execution_is_blocked(self):
        result = validate_sandbox_direct_command_record(self.record)
        self.assertTrue(result["direct_command_execution_blocked"])
        self.assertFalse(self.record["direct_command_executed"])
        self.assertFalse(self.record["execution_allowed_in_this_package"])
        self.assertTrue(self.record["future_direct_command_execution_requires_separate_boundary"])

    def test_valid_summary_records_boundary_update(self):
        summary = build_sandbox_direct_command_summary(self.record)
        result = validate_sandbox_direct_command_summary(summary)
        self.assertTrue(result["valid"], result["error_codes"])
        self.assertEqual(BOUNDARY_INDEX_BEFORE, summary["boundary_index_before"])
        self.assertEqual(BOUNDARY_INDEX_AFTER, summary["boundary_index_after"])
        self.assertTrue(result["boundary_update_checked"])

    def test_invalid_missing_approval_source_blocks(self):
        record = deepcopy(self.record)
        record["source_direct_command_approval_record"] = {}
        result = validate_sandbox_direct_command_record(record)
        self.assertFalse(result["valid"])
        self.assertIn("missing_or_invalid_b100_direct_command_approval_source", result["error_codes"])

    def test_invalid_missing_final_action_source_blocks(self):
        record = deepcopy(self.record)
        record["source_sandbox_final_action_record"] = {}
        result = validate_sandbox_direct_command_record(record)
        self.assertFalse(result["valid"])
        self.assertIn("missing_or_invalid_b99_final_action_source", result["error_codes"])

    def test_invalid_missing_final_action_audit_source_blocks(self):
        record = deepcopy(self.record)
        record["source_b99_final_action_audit_record"] = {}
        result = validate_sandbox_direct_command_record(record)
        self.assertFalse(result["valid"])
        self.assertIn("missing_or_invalid_b99_final_action_audit_source", result["error_codes"])

    def test_invalid_non_sandbox_scope_blocks(self):
        record = deepcopy(self.record)
        record["direct_command_scope"] = "production"
        result = validate_sandbox_direct_command_record(record)
        self.assertFalse(result["valid"])
        self.assertIn("direct_command_scope_not_expected", result["error_codes"])

    def test_invalid_command_execution_blocks(self):
        record = deepcopy(self.record)
        record["direct_command_executed"] = True
        result = validate_sandbox_direct_command_record(record)
        self.assertFalse(result["valid"])
        self.assertIn("direct_command_executed_not_false", result["error_codes"])

    def test_invalid_execution_allowed_blocks(self):
        record = deepcopy(self.record)
        record["execution_allowed_in_this_package"] = True
        result = validate_sandbox_direct_command_record(record)
        self.assertFalse(result["valid"])
        self.assertIn("execution_allowed_in_this_package_not_false", result["error_codes"])

    def test_invalid_command_payload_blocks(self):
        record = deepcopy(self.record)
        record["command_payload"]["operation"] = "retry_same_action"
        result = validate_sandbox_direct_command_record(record)
        self.assertFalse(result["valid"])
        self.assertIn("command_payload_operation_not_expected", result["error_codes"])

    def test_production_memory_retention_predictor_and_proof_block(self):
        fields = (
            "production_behavior_changed",
            "memory_write_performed",
            "retained_jsonl_write_performed",
            "retention_write_performed",
            "predictor_mutation_performed",
            "proof_of_learning_claim_allowed",
        )
        for field in fields:
            with self.subTest(field=field):
                record = deepcopy(self.record)
                record[field] = True
                result = validate_sandbox_direct_command_record(record)
                self.assertFalse(result["valid"])
                self.assertIn(f"{field}_not_false", result["error_codes"])

    def test_real_navigation_and_ui_behavior_block(self):
        for field in ("real_navigation_changed", "ui_behavior_changed"):
            with self.subTest(field=field):
                record = deepcopy(self.record)
                record[field] = True
                result = validate_sandbox_direct_command_record(record)
                self.assertFalse(result["valid"])
                self.assertIn(f"{field}_not_false", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        result = run_sandbox_direct_command_minimal_check()
        summary = result["summary"]
        self.assertEqual("ok", result["status"])
        self.assertEqual(1, summary["valid_direct_command_count"])
        self.assertEqual(28, summary["invalid_direct_command_count"])
        self.assertEqual(1, summary["valid_summary_count"])
        self.assertEqual(14, summary["invalid_summary_count"])
        self.assertEqual(1, summary["direct_command_source_checked_count"])
        self.assertEqual(1, summary["direct_command_created_checked_count"])
        self.assertEqual(1, summary["direct_command_execution_blocked_count"])
        self.assertEqual(1, summary["boundary_update_checked_count"])
        self.assertTrue(summary["all_sandbox_direct_command_checks_passed"])


if __name__ == "__main__":
    unittest.main()
