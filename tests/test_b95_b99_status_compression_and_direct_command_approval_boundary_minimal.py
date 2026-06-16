import unittest
from copy import deepcopy

from ashl_core.b95_b99_status_compression_and_direct_command_approval_boundary_minimal import (
    BOUNDARY_INDEX_AFTER,
    BOUNDARY_INDEX_BEFORE,
    build_b95_b99_status_compression_record,
    build_sandbox_direct_command_approval_boundary_record,
    build_status_compression_and_direct_command_approval_summary,
    run_b95_b99_status_compression_and_direct_command_approval_boundary_minimal_check,
    validate_b95_b99_status_compression_record,
    validate_sandbox_direct_command_approval_boundary_record,
    validate_status_compression_and_direct_command_approval_summary,
)


class B95B99StatusCompressionAndDirectCommandApprovalBoundaryMinimalTests(unittest.TestCase):
    def test_valid_status_compression(self):
        record = build_b95_b99_status_compression_record()
        result = validate_b95_b99_status_compression_record(record)
        self.assertTrue(result["valid"], result["error_codes"])
        self.assertEqual("b95_b99_status_compression", record["record_type"])
        self.assertEqual(BOUNDARY_INDEX_BEFORE, record["boundary_index_before"])
        self.assertEqual(BOUNDARY_INDEX_BEFORE, record["boundary_index_after_for_compression_only"])
        self.assertFalse(record["compression_boundary_change_required"])
        self.assertTrue(record["sandbox_only"])
        self.assertEqual("sandbox_only", record["final_action_scope"])
        self.assertFalse(record["direct_command_created"])

    def test_valid_direct_command_approval_boundary(self):
        record = build_sandbox_direct_command_approval_boundary_record()
        result = validate_sandbox_direct_command_approval_boundary_record(record)
        self.assertTrue(result["valid"], result["error_codes"])
        self.assertEqual("sandbox_direct_command_approval_boundary", record["record_type"])
        self.assertEqual(
            "approved_for_future_sandbox_direct_command_package_only",
            record["approval_status"],
        )
        self.assertEqual(
            "future_sandbox_only_direct_command_from_sandbox_final_action",
            record["approval_scope"],
        )
        self.assertTrue(record["direct_command_allowed_in_future_package"])
        self.assertFalse(record["implementation_in_this_package"])
        self.assertFalse(record["direct_command_created"])
        self.assertTrue(result["future_direct_command_approval_checked"])

    def test_valid_combined_summary(self):
        record = build_status_compression_and_direct_command_approval_summary()
        result = validate_status_compression_and_direct_command_approval_summary(record)
        self.assertTrue(result["valid"], result["error_codes"])
        self.assertEqual(BOUNDARY_INDEX_BEFORE, record["boundary_index_before"])
        self.assertEqual(BOUNDARY_INDEX_AFTER, record["boundary_index_after"])
        self.assertTrue(record["boundary_change_required"])
        self.assertTrue(record["boundary_index_update_required"])
        self.assertTrue(record["status_compression_completed"])
        self.assertTrue(record["direct_command_approval_boundary_created"])
        self.assertFalse(record["direct_command_created"])

    def test_invalid_status_compression_changes_boundary_by_itself(self):
        record = build_b95_b99_status_compression_record()
        record["compression_boundary_change_required"] = True
        result = validate_b95_b99_status_compression_record(record)
        self.assertFalse(result["valid"])
        self.assertIn("compression_boundary_change_required_not_false", result["error_codes"])

    def test_invalid_missing_b99_audit_source_blocks_status_compression(self):
        record = build_b95_b99_status_compression_record()
        record["source_b99_audit_record"] = {}
        result = validate_b95_b99_status_compression_record(record)
        self.assertFalse(result["valid"])
        self.assertIn("missing_or_invalid_b99_audit_source", result["error_codes"])

    def test_invalid_missing_b99_audit_source_blocks_approval(self):
        record = build_sandbox_direct_command_approval_boundary_record()
        record["source_b99_audit_record"] = {}
        result = validate_sandbox_direct_command_approval_boundary_record(record)
        self.assertFalse(result["valid"])
        self.assertIn("missing_or_invalid_b99_audit_source", result["error_codes"])

    def test_invalid_source_final_action_not_sandbox_only(self):
        record = build_sandbox_direct_command_approval_boundary_record()
        record["required_source_final_action_scope"] = "production"
        result = validate_sandbox_direct_command_approval_boundary_record(record)
        self.assertFalse(result["valid"])
        self.assertIn("required_source_final_action_scope_not_expected", result["error_codes"])

    def test_invalid_direct_command_created_blocks_approval(self):
        record = build_sandbox_direct_command_approval_boundary_record()
        record["direct_command_created"] = True
        result = validate_sandbox_direct_command_approval_boundary_record(record)
        self.assertFalse(result["valid"])
        self.assertIn("direct_command_created_not_false", result["error_codes"])

    def test_invalid_implementation_in_this_package_blocks_approval(self):
        record = build_sandbox_direct_command_approval_boundary_record()
        record["implementation_in_this_package"] = True
        result = validate_sandbox_direct_command_approval_boundary_record(record)
        self.assertFalse(result["valid"])
        self.assertIn("implementation_in_this_package_not_false", result["error_codes"])

    def test_invalid_production_behavior_blocks_approval(self):
        record = build_sandbox_direct_command_approval_boundary_record()
        record["production_behavior_changed"] = True
        result = validate_sandbox_direct_command_approval_boundary_record(record)
        self.assertFalse(result["valid"])
        self.assertIn("production_behavior_changed_not_false", result["error_codes"])

    def test_invalid_persistent_update_blocks_approval(self):
        record = build_sandbox_direct_command_approval_boundary_record()
        record["persistent_rule_created"] = True
        result = validate_sandbox_direct_command_approval_boundary_record(record)
        self.assertFalse(result["valid"])
        self.assertIn("persistent_rule_created_not_false", result["error_codes"])

    def test_invalid_persistent_trust_doubt_update_blocks_approval(self):
        record = build_sandbox_direct_command_approval_boundary_record()
        record["persistent_trust_doubt_update_performed"] = True
        result = validate_sandbox_direct_command_approval_boundary_record(record)
        self.assertFalse(result["valid"])
        self.assertIn("persistent_trust_doubt_update_performed_not_false", result["error_codes"])

    def test_invalid_cross_session_feedback_persistence_blocks_approval(self):
        record = build_sandbox_direct_command_approval_boundary_record()
        record["cross_session_feedback_persistence"] = True
        result = validate_sandbox_direct_command_approval_boundary_record(record)
        self.assertFalse(result["valid"])
        self.assertIn("cross_session_feedback_persistence_not_false", result["error_codes"])

    def test_invalid_memory_and_retained_jsonl_write_block_approval(self):
        for field in ("memory_write_performed", "retained_jsonl_write_performed"):
            with self.subTest(field=field):
                record = build_sandbox_direct_command_approval_boundary_record()
                record[field] = True
                result = validate_sandbox_direct_command_approval_boundary_record(record)
                self.assertFalse(result["valid"])
                self.assertIn(f"{field}_not_false", result["error_codes"])

    def test_invalid_retention_write_blocks_approval(self):
        record = build_sandbox_direct_command_approval_boundary_record()
        record["retention_write_performed"] = True
        result = validate_sandbox_direct_command_approval_boundary_record(record)
        self.assertFalse(result["valid"])
        self.assertIn("retention_write_performed_not_false", result["error_codes"])

    def test_invalid_predictor_read_influence_mutation_blocks_approval(self):
        for field in ("predictor_read_enabled", "predictor_influence_enabled", "predictor_mutation_performed"):
            with self.subTest(field=field):
                record = build_sandbox_direct_command_approval_boundary_record()
                record[field] = True
                result = validate_sandbox_direct_command_approval_boundary_record(record)
                self.assertFalse(result["valid"])
                self.assertIn(f"{field}_not_false", result["error_codes"])

    def test_invalid_proof_claim_blocks_approval(self):
        record = build_sandbox_direct_command_approval_boundary_record()
        record["proof_of_learning_claim_allowed"] = True
        result = validate_sandbox_direct_command_approval_boundary_record(record)
        self.assertFalse(result["valid"])
        self.assertIn("proof_of_learning_claim_allowed_not_false", result["error_codes"])

    def test_invalid_autonomous_claims_block_approval(self):
        for field in ("autonomous_learning_claim_allowed", "autonomous_action_claim_allowed"):
            with self.subTest(field=field):
                record = build_sandbox_direct_command_approval_boundary_record()
                record[field] = True
                result = validate_sandbox_direct_command_approval_boundary_record(record)
                self.assertFalse(result["valid"])
                self.assertIn(f"{field}_not_false", result["error_codes"])

    def test_invalid_future_production_without_separate_boundary_blocks(self):
        record = build_sandbox_direct_command_approval_boundary_record()
        record["future_production_promotion_requires_separate_boundary"] = False
        result = validate_sandbox_direct_command_approval_boundary_record(record)
        self.assertFalse(result["valid"])
        self.assertIn("future_production_promotion_requires_separate_boundary_not_true", result["error_codes"])

    def test_invalid_test_tier_policy_runtime_capability_blocks_status_source(self):
        record = build_b95_b99_status_compression_record()
        source = deepcopy(record["source_b99_audit_record"])
        source["test_tier_policy_runtime_capability"] = True
        record["source_b99_audit_record"] = source
        result = validate_b95_b99_status_compression_record(record)
        self.assertFalse(result["valid"])
        self.assertIn("missing_or_invalid_b99_audit_source", result["error_codes"])

    def test_invalid_summary_without_boundary_update_blocks(self):
        record = build_status_compression_and_direct_command_approval_summary()
        record["boundary_index_after"] = BOUNDARY_INDEX_BEFORE
        result = validate_status_compression_and_direct_command_approval_summary(record)
        self.assertFalse(result["valid"])
        self.assertIn("boundary_index_after_not_expected", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        result = run_b95_b99_status_compression_and_direct_command_approval_boundary_minimal_check()
        summary = result["summary"]
        self.assertEqual("ok", result["status"])
        self.assertEqual(1, summary["valid_status_compression_count"])
        self.assertEqual(10, summary["invalid_status_compression_count"])
        self.assertEqual(1, summary["valid_direct_command_approval_count"])
        self.assertEqual(21, summary["invalid_direct_command_approval_count"])
        self.assertEqual(1, summary["valid_summary_count"])
        self.assertEqual(15, summary["invalid_summary_count"])
        self.assertEqual(1, summary["future_direct_command_approval_checked_count"])
        self.assertEqual(1, summary["direct_command_blocked_count"])
        self.assertTrue(summary["all_status_compression_and_direct_command_approval_checks_passed"])


if __name__ == "__main__":
    unittest.main()
