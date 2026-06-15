import unittest
from copy import deepcopy

from ashl_core.b85_b93_documentation_compression_status_sync_minimal import (
    BOUNDARY_INDEX_VERSION,
    DOCS_UPDATED,
    build_b85_b93_status_sync_record,
    run_b85_b93_documentation_compression_status_sync_minimal_check,
    validate_b85_b93_status_sync_record,
)
from ashl_core.teaching_cli import run_command


class B85B93DocumentationCompressionStatusSyncMinimalTests(unittest.TestCase):
    def test_valid_status_sync(self):
        record = build_b85_b93_status_sync_record()
        result = validate_b85_b93_status_sync_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual("b85_b93_documentation_compression_status_sync", record["record_type"])
        self.assertEqual("completed_documentation_compression_status_sync", record["sync_status"])

    def test_boundary_index_remains_unchanged(self):
        record = build_b85_b93_status_sync_record()

        self.assertEqual("2026-06-09-b93", BOUNDARY_INDEX_VERSION)
        self.assertEqual("2026-06-09-b93", record["boundary_index_before"])
        self.assertEqual("2026-06-09-b93", record["boundary_index_after"])
        self.assertFalse(record["boundary_change_required"])
        self.assertFalse(record["boundary_index_update_required"])
        self.assertFalse(record["current_boundary_index_updated"])

    def test_docs_updated_are_expected_minimal_docs(self):
        record = build_b85_b93_status_sync_record()
        result = validate_b85_b93_status_sync_record(record)

        self.assertEqual(DOCS_UPDATED, record["docs_updated"])
        self.assertEqual(5, result["docs_updated_count"])
        self.assertEqual(0, result["missing_docs_count"])

    def test_loop_scope_is_sandbox_same_session_and_rollback_verified(self):
        record = build_b85_b93_status_sync_record()

        self.assertTrue(record["same_session_only"])
        self.assertTrue(record["sandbox_only"])
        self.assertTrue(record["rollback_required"])
        self.assertTrue(record["rollback_verified"])
        self.assertIn("rollback", record["compressed_loop_summary"])

    def test_boundaries_remain_blocked(self):
        record = build_b85_b93_status_sync_record()

        for field in (
            "selected_action_created",
            "final_action_created",
            "direct_command_created",
            "persistent_rule_created",
            "persistent_trust_doubt_update_performed",
            "cross_session_feedback_persistence",
            "memory_write_performed",
            "retained_jsonl_write_performed",
            "retention_write_performed",
            "predictor_mutation_performed",
            "production_behavior_changed",
            "verification_execution_is_production_behavior",
            "same_session_loop_proves_learning",
            "proof_of_learning_claim_allowed",
            "qingyin_autonomous_action_claim_allowed",
        ):
            with self.subTest(field=field):
                self.assertFalse(record[field])

    def test_cli_command_returns_ok(self):
        result = run_command("run-b85-b93-documentation-compression-status-sync-minimal-check")

        self.assertEqual("ok", result["status"])
        self.assertEqual(1, result["summary"]["valid_sync_count"])

    def test_invalid_boundary_index_changed(self):
        self.assertInvalid("boundary_index_after", "2026-06-09-b94")
        self.assertInvalid("boundary_change_required", True)
        self.assertInvalid("boundary_index_update_required", True)

    def test_invalid_selected_action_claim(self):
        self.assertInvalid("selected_action_created", True)

    def test_invalid_final_action_claim(self):
        self.assertInvalid("final_action_created", True)

    def test_invalid_autonomous_action_claim(self):
        self.assertInvalid("qingyin_autonomous_action_claim_allowed", True)

    def test_invalid_persistent_trust_doubt_update(self):
        self.assertInvalid("persistent_trust_doubt_update_performed", True)
        self.assertInvalid("persistent_rule_created", True)

    def test_invalid_cross_session_persistence(self):
        self.assertInvalid("cross_session_feedback_persistence", True)

    def test_invalid_memory_write(self):
        self.assertInvalid("memory_write_performed", True)
        self.assertInvalid("retained_jsonl_write_performed", True)

    def test_invalid_retention_write(self):
        self.assertInvalid("retention_write_performed", True)

    def test_invalid_predictor_mutation(self):
        self.assertInvalid("predictor_mutation_performed", True)

    def test_invalid_production_behavior(self):
        self.assertInvalid("production_behavior_changed", True)
        self.assertInvalid("verification_execution_is_production_behavior", True)

    def test_invalid_proof_of_learning_claim(self):
        self.assertInvalid("same_session_loop_proves_learning", True)
        self.assertInvalid("proof_of_learning_claim_allowed", True)

    def test_invalid_line_count_over_150_when_current_boundary_index_is_touched(self):
        record = deepcopy(build_b85_b93_status_sync_record())
        record["current_boundary_index_updated"] = True
        record["current_boundary_index_line_count"] = 151

        self.assertFalse(validate_b85_b93_status_sync_record(record)["valid"])

    def test_invalid_rollback_missing(self):
        self.assertInvalid("rollback_required", False)
        self.assertInvalid("rollback_verified", False)

    def test_summary_counts_are_deterministic(self):
        result = run_b85_b93_documentation_compression_status_sync_minimal_check()
        summary = result["summary"]

        self.assertEqual("ok", result["status"])
        self.assertEqual(1, summary["valid_sync_count"])
        self.assertGreaterEqual(summary["invalid_sync_count"], 20)
        self.assertEqual(1, summary["boundary_unchanged_checked_count"])
        self.assertEqual(5, summary["docs_updated_count"])
        self.assertEqual(1, summary["line_count_checked_count"])
        self.assertEqual(1, summary["overclaim_blocked_count"])
        self.assertEqual(1, summary["selected_action_blocked_count"])
        self.assertEqual(1, summary["final_action_blocked_count"])
        self.assertEqual(1, summary["persistent_update_blocked_count"])
        self.assertEqual(1, summary["cross_session_blocked_count"])
        self.assertEqual(1, summary["memory_write_blocked_count"])
        self.assertEqual(1, summary["retention_blocked_count"])
        self.assertEqual(1, summary["predictor_mutation_blocked_count"])
        self.assertEqual(1, summary["production_behavior_blocked_count"])
        self.assertEqual(1, summary["proof_claim_blocked_count"])
        self.assertTrue(summary["all_b85_b93_documentation_compression_status_sync_checks_passed"])

    def assertInvalid(self, field, value):
        record = deepcopy(build_b85_b93_status_sync_record())
        record[field] = value

        self.assertFalse(validate_b85_b93_status_sync_record(record)["valid"])


if __name__ == "__main__":
    unittest.main()
