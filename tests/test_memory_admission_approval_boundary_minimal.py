import unittest

from ashl_core.memory_admission_approval_boundary_minimal import (
    ALLOWED_DECISIONS,
    APPROVED_DECISION,
    BLOCKED_DECISIONS,
    BOUNDARY_INDEX_VERSION_AFTER,
    BOUNDARY_INDEX_VERSION_BEFORE,
    build_memory_admission_approval_record,
    run_memory_admission_approval_boundary_minimal_check,
    validate_memory_admission_approval_record,
)
from ashl_core.memory_admission_package_design_minimal import build_memory_admission_package_design


class MemoryAdmissionApprovalBoundaryMinimalTests(unittest.TestCase):
    def test_valid_approved_for_future_memory_admission_package_approval(self):
        record = build_memory_admission_approval_record()
        result = validate_memory_admission_approval_record(record)
        self.assertTrue(result["valid"])
        self.assertEqual(record["record_type"], "memory_admission_approval")
        self.assertEqual(record["source_design_record_type"], "memory_admission_package_design")
        self.assertEqual(record["source_design_status"], "future_memory_admission_package_design_recorded")
        self.assertEqual(record["approval_decision"], APPROVED_DECISION)
        self.assertTrue(record["future_memory_admission_package_may_proceed"])
        self.assertFalse(record["memory_admission_performed"])
        self.assertFalse(record["memory_write_allowed"])
        self.assertFalse(record["retained_jsonl_write_allowed"])
        self.assertFalse(record["runtime_influence_allowed"])
        self.assertFalse(record["predictor_mutation_allowed"])
        self.assertFalse(record["proof_of_learning_claim_allowed"])

    def test_valid_blocked_decisions_do_not_proceed(self):
        for decision in BLOCKED_DECISIONS:
            with self.subTest(decision=decision):
                record = build_memory_admission_approval_record(approval_decision=decision)
                result = validate_memory_admission_approval_record(record)
                self.assertTrue(result["valid"])
                self.assertFalse(record["future_memory_admission_package_may_proceed"])

    def test_valid_decisions_are_supported(self):
        for decision in ALLOWED_DECISIONS:
            with self.subTest(decision=decision):
                record = build_memory_admission_approval_record(approval_decision=decision)
                self.assertTrue(validate_memory_admission_approval_record(record)["valid"])

    def test_invalid_approval_source_actor_role_and_text_block(self):
        cases = [
            ("approval_source", "task_queue", "approval_source_not_expected"),
            ("approval_actor", "codex", "approval_actor_not_expected"),
            ("approver_role", "assistant", "approver_role_not_expected"),
            ("approval_text", "", "approval_text_empty"),
        ]
        for field, value, error in cases:
            with self.subTest(field=field):
                record = build_memory_admission_approval_record()
                record[field] = value
                result = validate_memory_admission_approval_record(record)
                self.assertFalse(result["valid"])
                self.assertIn(error, result["error_codes"])

    def test_invalid_self_or_indirect_approval_sources_block(self):
        for field in (
            "codex_self_approval_allowed",
            "ai_self_approval_allowed",
            "fixture_approval_is_real_approval",
            "task_queue_status_is_approval",
            "passing_tests_are_approval",
            "implicit_chat_command_is_approval",
        ):
            with self.subTest(field=field):
                record = build_memory_admission_approval_record()
                record[field] = True
                result = validate_memory_admission_approval_record(record)
                self.assertFalse(result["valid"])
                self.assertIn(f"{field}_not_false", result["error_codes"])

    def test_invalid_missing_or_invalid_source_design_blocks(self):
        record = build_memory_admission_approval_record()
        record.pop("source_memory_admission_package_design")
        result = validate_memory_admission_approval_record(record)
        self.assertFalse(result["valid"])
        self.assertIn("source_memory_admission_package_design_missing", result["error_codes"])

        record = build_memory_admission_approval_record()
        record["source_memory_admission_package_design"]["memory_write_allowed"] = True
        result = validate_memory_admission_approval_record(record)
        self.assertFalse(result["valid"])
        self.assertIn("source_memory_admission_package_design_invalid", result["error_codes"])

        source = build_memory_admission_package_design()
        source["memory_write_allowed"] = True
        with self.assertRaises(ValueError):
            build_memory_admission_approval_record(source)

    def test_invalid_wrong_candidate_source_and_decision_logic_blocks(self):
        record = build_memory_admission_approval_record()
        record["target_candidate_source"] = "other"
        result = validate_memory_admission_approval_record(record)
        self.assertFalse(result["valid"])
        self.assertIn("target_candidate_source_not_expected", result["error_codes"])

        record = build_memory_admission_approval_record()
        record["approval_decision"] = "write_memory"
        result = validate_memory_admission_approval_record(record)
        self.assertFalse(result["valid"])
        self.assertIn("approval_decision_not_allowed", result["error_codes"])

        record = build_memory_admission_approval_record()
        record["future_memory_admission_package_may_proceed"] = False
        result = validate_memory_admission_approval_record(record)
        self.assertFalse(result["valid"])
        self.assertIn("approved_decision_may_proceed_not_true", result["error_codes"])

        record = build_memory_admission_approval_record(approval_decision="rejected_for_memory_admission")
        record["future_memory_admission_package_may_proceed"] = True
        result = validate_memory_admission_approval_record(record)
        self.assertFalse(result["valid"])
        self.assertIn("blocked_decision_may_proceed_not_false", result["error_codes"])

    def test_invalid_memory_and_runtime_permissions_block(self):
        for field in (
            "memory_admission_performed",
            "memory_write_allowed",
            "retained_jsonl_write_allowed",
            "retention_write_allowed",
            "runtime_influence_allowed",
            "predictor_influence_allowed",
            "predictor_mutation_allowed",
            "production_behavior_change_allowed",
            "selected_action_allowed",
            "final_action_allowed",
            "proof_of_learning_claim_allowed",
        ):
            with self.subTest(field=field):
                record = build_memory_admission_approval_record()
                record[field] = True
                result = validate_memory_admission_approval_record(record)
                self.assertFalse(result["valid"])
                self.assertIn(f"{field}_not_false", result["error_codes"])

    def test_invalid_boundary_bypass_blocks(self):
        for field in (
            "requires_separate_future_memory_admission_package",
            "requires_separate_future_memory_write_boundary",
            "requires_separate_runtime_influence_boundary",
            "requires_separate_predictor_influence_boundary",
        ):
            with self.subTest(field=field):
                record = build_memory_admission_approval_record()
                record[field] = False
                result = validate_memory_admission_approval_record(record)
                self.assertFalse(result["valid"])
                self.assertIn(f"{field}_not_true", result["error_codes"])

    def test_invalid_qingyin_claims_and_audit_block(self):
        cases = [
            ("repo_audit_acknowledged", False, "repo_audit_acknowledged_not_true"),
            ("qingyin_self_authored_lesson_text", True, "qingyin_self_authored_lesson_text_not_false"),
            ("autonomous_learning_claim_allowed", True, "autonomous_learning_claim_allowed_not_false"),
            ("audit_recorded", False, "audit_recorded_not_true"),
            ("rollback_available", False, "rollback_available_not_true"),
        ]
        for field, value, error in cases:
            with self.subTest(field=field):
                record = build_memory_admission_approval_record()
                record[field] = value
                result = validate_memory_admission_approval_record(record)
                self.assertFalse(result["valid"])
                self.assertIn(error, result["error_codes"])

    def test_summary_counts_are_deterministic(self):
        result = run_memory_admission_approval_boundary_minimal_check()
        summary = result["summary"]
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["valid_approval_count"], 4)
        self.assertGreaterEqual(summary["invalid_approval_count"], 1)
        self.assertEqual(summary["approved_decision_checked_count"], 1)
        self.assertEqual(summary["blocked_decision_checked_count"], 3)
        self.assertEqual(summary["explicit_user_statement_checked_count"], 4)
        self.assertEqual(summary["project_owner_checked_count"], 4)
        self.assertEqual(summary["codex_self_approval_blocked_count"], 4)
        self.assertEqual(summary["ai_self_approval_blocked_count"], 4)
        self.assertEqual(summary["fixture_approval_blocked_count"], 4)
        self.assertEqual(summary["task_queue_approval_blocked_count"], 4)
        self.assertEqual(summary["passing_tests_approval_blocked_count"], 4)
        self.assertEqual(summary["memory_admission_performed_blocked_count"], 4)
        self.assertEqual(summary["memory_write_blocked_count"], 4)
        self.assertEqual(summary["retained_jsonl_write_blocked_count"], 4)
        self.assertEqual(summary["runtime_influence_blocked_count"], 4)
        self.assertEqual(summary["predictor_mutation_blocked_count"], 4)
        self.assertEqual(summary["proof_claim_blocked_count"], 4)

    def test_boundary_index_updates_for_approval_validation_boundary(self):
        result = run_memory_admission_approval_boundary_minimal_check()
        boundary = result["boundary"]
        self.assertTrue(boundary["boundary_change_required"])
        self.assertTrue(boundary["boundary_index_update_required"])
        self.assertEqual(boundary["boundary_index_version_before"], BOUNDARY_INDEX_VERSION_BEFORE)
        self.assertEqual(boundary["boundary_index_version_after"], BOUNDARY_INDEX_VERSION_AFTER)


if __name__ == "__main__":
    unittest.main()
