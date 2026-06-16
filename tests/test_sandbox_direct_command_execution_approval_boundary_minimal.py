import unittest
from copy import deepcopy

from ashl_core.sandbox_direct_command_execution_approval_boundary_minimal import (
    BOUNDARY_INDEX_AFTER,
    BOUNDARY_INDEX_BEFORE,
    COMMAND,
    DIRECT_COMMAND,
    build_sandbox_direct_command_execution_approval_boundary_record,
    run_sandbox_direct_command_execution_approval_boundary_minimal_check,
    validate_sandbox_direct_command_execution_approval_boundary_record,
)


class SandboxDirectCommandExecutionApprovalBoundaryMinimalTests(unittest.TestCase):
    def setUp(self):
        self.record = build_sandbox_direct_command_execution_approval_boundary_record()

    def assertInvalid(self, field, value, expected_error):
        record = deepcopy(self.record)
        record[field] = value
        result = validate_sandbox_direct_command_execution_approval_boundary_record(record)
        self.assertFalse(result["valid"])
        self.assertIn(expected_error, result["error_codes"])

    def test_valid_execution_approval_boundary_is_created(self):
        result = validate_sandbox_direct_command_execution_approval_boundary_record(self.record)
        self.assertTrue(result["valid"], result["error_codes"])
        self.assertEqual("sandbox_direct_command_execution_approval_boundary", self.record["record_type"])
        self.assertEqual(DIRECT_COMMAND, self.record["direct_command"])
        self.assertEqual(BOUNDARY_INDEX_BEFORE, self.record["source_boundary_index"])
        self.assertEqual(BOUNDARY_INDEX_AFTER, self.record["target_boundary_index"])

    def test_reuses_b101_direct_command_source(self):
        result = validate_sandbox_direct_command_execution_approval_boundary_record(self.record)
        self.assertTrue(result["source_direct_command_checked"])
        self.assertEqual("sandbox_direct_command_b101", self.record["source_sandbox_direct_command"])
        self.assertTrue(self.record["source_direct_command_required"])
        self.assertTrue(self.record["source_direct_command_validated"])

    def test_future_execution_boundary_opened_without_execution(self):
        result = validate_sandbox_direct_command_execution_approval_boundary_record(self.record)
        self.assertTrue(result["future_execution_boundary_opened"])
        self.assertTrue(self.record["direct_command_execution_allowed_in_future_package"])
        self.assertFalse(self.record["execution_allowed_in_this_package"])
        self.assertFalse(self.record["direct_command_executed"])
        self.assertFalse(self.record["execution_result_created"])

    def test_scope_and_safeguards_are_required(self):
        result = validate_sandbox_direct_command_execution_approval_boundary_record(self.record)
        self.assertTrue(result["sandbox_scope_checked"])
        self.assertTrue(result["execution_safeguards_checked"])
        self.assertEqual("sandbox_only", self.record["allowed_future_execution_scope"])
        self.assertEqual(1, self.record["max_future_execution_count"])
        self.assertTrue(self.record["audit_required"])
        self.assertTrue(self.record["rollback_required"])
        self.assertTrue(self.record["mentor_override_required"])

    def test_invalid_missing_source_blocks(self):
        self.assertInvalid(
            "source_sandbox_direct_command_record",
            {},
            "missing_or_invalid_b101_direct_command_source",
        )

    def test_invalid_non_sandbox_scope_blocks(self):
        self.assertInvalid("direct_command_scope", "production", "direct_command_scope_not_expected")
        self.assertInvalid(
            "allowed_future_execution_scope",
            "production",
            "allowed_future_execution_scope_not_expected",
        )

    def test_invalid_execution_in_this_package_blocks(self):
        self.assertInvalid(
            "execution_allowed_in_this_package",
            True,
            "execution_allowed_in_this_package_not_false",
        )
        self.assertInvalid("direct_command_executed", True, "direct_command_executed_not_false")
        self.assertInvalid("execution_result_created", True, "execution_result_created_not_false")

    def test_invalid_execution_safeguards_block(self):
        for field in (
            "execution_scope_must_remain_sandbox_only",
            "execution_budget_required",
            "audit_required",
            "rollback_required",
            "mentor_override_required",
        ):
            with self.subTest(field=field):
                self.assertInvalid(field, False, f"{field}_not_true")
        self.assertInvalid("max_future_execution_count", 2, "max_future_execution_count_not_expected")

    def test_production_memory_retention_predictor_and_proof_block(self):
        for field in (
            "production_behavior_changed",
            "memory_write_performed",
            "retained_jsonl_write_performed",
            "retention_write_performed",
            "predictor_mutation_performed",
            "real_navigation_changed",
            "ui_behavior_changed",
            "proof_of_learning_claim_allowed",
        ):
            with self.subTest(field=field):
                self.assertInvalid(field, True, f"{field}_not_false")

    def test_demo_summary_counts_are_deterministic(self):
        result = run_sandbox_direct_command_execution_approval_boundary_minimal_check()
        summary = result["summary"]
        boundary = result["boundary"]
        self.assertEqual(COMMAND, result["command"])
        self.assertEqual("ok", result["status"])
        self.assertEqual(1, summary["valid_approval_boundary_count"])
        self.assertEqual(36, summary["invalid_approval_boundary_count"])
        self.assertEqual(1, summary["source_direct_command_checked_count"])
        self.assertEqual(1, summary["future_execution_boundary_opened_count"])
        self.assertEqual(1, summary["sandbox_scope_checked_count"])
        self.assertEqual(1, summary["execution_safeguards_checked_count"])
        self.assertEqual(1, summary["production_behavior_blocked_count"])
        self.assertEqual(1, summary["memory_write_blocked_count"])
        self.assertEqual(1, summary["retention_blocked_count"])
        self.assertEqual(1, summary["predictor_mutation_blocked_count"])
        self.assertEqual(1, summary["proof_claim_blocked_count"])
        self.assertTrue(
            summary["all_sandbox_direct_command_execution_approval_boundary_checks_passed"]
        )
        self.assertTrue(boundary["boundary_change_required"])
        self.assertEqual(BOUNDARY_INDEX_BEFORE, boundary["boundary_index_version_before"])
        self.assertEqual(BOUNDARY_INDEX_AFTER, boundary["boundary_index_version_after"])


if __name__ == "__main__":
    unittest.main()
