import unittest

from ashl_core.memory_admission_minimal import (
    build_memory_admission_record,
    build_reviewed_lesson_memory_candidate_record,
)
from ashl_core.memory_write_approval_boundary_minimal import (
    ALLOWED_DECISIONS,
    APPROVED_DECISION,
    BLOCKED_DECISIONS,
    BOUNDARY_INDEX_VERSION_AFTER,
    BOUNDARY_INDEX_VERSION_BEFORE,
    build_memory_write_approval_record,
    run_memory_write_approval_boundary_minimal_check,
    validate_memory_write_approval_record,
)


class MemoryWriteApprovalBoundaryMinimalTests(unittest.TestCase):
    def test_valid_approved_for_future_memory_write_package_approval(self):
        record = build_memory_write_approval_record()
        result = validate_memory_write_approval_record(record)
        self.assertTrue(result["valid"])
        self.assertEqual(record["record_type"], "memory_write_approval")
        self.assertEqual(record["approval_decision"], APPROVED_DECISION)
        self.assertTrue(record["future_memory_write_package_may_proceed"])
        self.assertEqual(record["source_admission_record_type"], "memory_admission")
        self.assertEqual(record["source_candidate_record_type"], "reviewed_lesson_memory_candidate")
        self.assertFalse(record["memory_write_performed"])
        self.assertFalse(record["long_term_memory_write_performed"])
        self.assertFalse(record["retained_jsonl_write_performed"])
        self.assertFalse(record["retention_write_performed"])
        self.assertFalse(record["runtime_influence_allowed"])
        self.assertFalse(record["predictor_mutation_allowed"])

    def test_valid_blocked_decisions_do_not_proceed(self):
        for decision in BLOCKED_DECISIONS:
            with self.subTest(decision=decision):
                record = build_memory_write_approval_record(approval_decision=decision)
                result = validate_memory_write_approval_record(record)
                self.assertTrue(result["valid"])
                self.assertFalse(record["future_memory_write_package_may_proceed"])

    def test_valid_decisions_are_supported(self):
        for decision in ALLOWED_DECISIONS:
            with self.subTest(decision=decision):
                record = build_memory_write_approval_record(approval_decision=decision)
                self.assertTrue(validate_memory_write_approval_record(record)["valid"])

    def test_invalid_approval_source_actor_role_and_text_block(self):
        cases = [
            ("approval_source", "task_queue", "approval_source_not_expected"),
            ("approval_actor", "codex", "approval_actor_not_expected"),
            ("approver_role", "assistant", "approver_role_not_expected"),
            ("approval_text", "", "approval_text_empty"),
        ]
        for field, value, error in cases:
            with self.subTest(field=field):
                record = build_memory_write_approval_record()
                record[field] = value
                result = validate_memory_write_approval_record(record)
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
                record = build_memory_write_approval_record()
                record[field] = True
                result = validate_memory_write_approval_record(record)
                self.assertFalse(result["valid"])
                self.assertIn(f"{field}_not_false", result["error_codes"])

    def test_invalid_missing_or_invalid_source_admission_blocks(self):
        record = build_memory_write_approval_record()
        record.pop("source_memory_admission")
        result = validate_memory_write_approval_record(record)
        self.assertFalse(result["valid"])
        self.assertIn("source_memory_admission_missing", result["error_codes"])

        admission = build_memory_admission_record()
        admission["long_term_memory_write_performed"] = True
        with self.assertRaises(ValueError):
            build_memory_write_approval_record(source_admission=admission)

        record = build_memory_write_approval_record()
        record["source_memory_admission"]["long_term_memory_write_performed"] = True
        result = validate_memory_write_approval_record(record)
        self.assertFalse(result["valid"])
        self.assertIn("source_memory_admission_invalid", result["error_codes"])

    def test_invalid_missing_or_invalid_reviewed_lesson_memory_candidate_blocks(self):
        record = build_memory_write_approval_record()
        record.pop("source_reviewed_lesson_memory_candidate")
        result = validate_memory_write_approval_record(record)
        self.assertFalse(result["valid"])
        self.assertIn("source_reviewed_lesson_memory_candidate_missing", result["error_codes"])

        admission = build_memory_admission_record()
        candidate = build_reviewed_lesson_memory_candidate_record(admission)
        candidate["writes_jsonl"] = True
        with self.assertRaises(ValueError):
            build_memory_write_approval_record(source_admission=admission, source_candidate=candidate)

        record = build_memory_write_approval_record()
        record["source_reviewed_lesson_memory_candidate"]["writes_jsonl"] = True
        result = validate_memory_write_approval_record(record)
        self.assertFalse(result["valid"])
        self.assertIn("source_reviewed_lesson_memory_candidate_invalid", result["error_codes"])

    def test_invalid_decision_logic_blocks(self):
        record = build_memory_write_approval_record()
        record["approval_decision"] = "write_memory_now"
        result = validate_memory_write_approval_record(record)
        self.assertFalse(result["valid"])
        self.assertIn("approval_decision_not_allowed", result["error_codes"])

        record = build_memory_write_approval_record()
        record["future_memory_write_package_may_proceed"] = False
        result = validate_memory_write_approval_record(record)
        self.assertFalse(result["valid"])
        self.assertIn("approved_decision_may_proceed_not_true", result["error_codes"])

        record = build_memory_write_approval_record(approval_decision="rejected_for_memory_write")
        record["future_memory_write_package_may_proceed"] = True
        result = validate_memory_write_approval_record(record)
        self.assertFalse(result["valid"])
        self.assertIn("blocked_decision_may_proceed_not_false", result["error_codes"])

    def test_invalid_write_runtime_predictor_action_and_proof_claims_block(self):
        for field in (
            "memory_write_performed",
            "long_term_memory_write_performed",
            "retained_jsonl_write_performed",
            "retention_write_performed",
            "runtime_influence_allowed",
            "predictor_influence_allowed",
            "predictor_mutation_allowed",
            "production_behavior_change_allowed",
            "selected_action_allowed",
            "final_action_allowed",
            "proof_of_learning_claim_allowed",
        ):
            with self.subTest(field=field):
                record = build_memory_write_approval_record()
                record[field] = True
                result = validate_memory_write_approval_record(record)
                self.assertFalse(result["valid"])
                self.assertIn(f"{field}_not_false", result["error_codes"])

    def test_invalid_required_future_boundaries_block(self):
        for field in (
            "requires_separate_future_memory_write_package",
            "requires_explicit_target_layer_selection",
            "requires_retention_rule",
            "requires_rollback_rule",
            "requires_cross_session_influence_rule",
            "requires_separate_runtime_influence_boundary",
            "requires_separate_predictor_influence_boundary",
        ):
            with self.subTest(field=field):
                record = build_memory_write_approval_record()
                record[field] = False
                result = validate_memory_write_approval_record(record)
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
                record = build_memory_write_approval_record()
                record[field] = value
                result = validate_memory_write_approval_record(record)
                self.assertFalse(result["valid"])
                self.assertIn(error, result["error_codes"])

    def test_summary_counts_are_deterministic(self):
        result = run_memory_write_approval_boundary_minimal_check()
        summary = result["summary"]
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["valid_approval_count"], 6)
        self.assertGreaterEqual(summary["invalid_approval_count"], 1)
        self.assertEqual(summary["approved_decision_checked_count"], 1)
        self.assertEqual(summary["blocked_decision_checked_count"], 5)
        self.assertEqual(summary["explicit_user_statement_checked_count"], 6)
        self.assertEqual(summary["project_owner_checked_count"], 6)
        self.assertEqual(summary["source_admission_checked_count"], 6)
        self.assertEqual(summary["source_candidate_checked_count"], 6)
        self.assertEqual(summary["codex_self_approval_blocked_count"], 6)
        self.assertEqual(summary["ai_self_approval_blocked_count"], 6)
        self.assertEqual(summary["fixture_approval_blocked_count"], 6)
        self.assertEqual(summary["task_queue_approval_blocked_count"], 6)
        self.assertEqual(summary["passing_tests_approval_blocked_count"], 6)
        self.assertEqual(summary["memory_write_performed_blocked_count"], 6)
        self.assertEqual(summary["long_term_memory_write_blocked_count"], 6)
        self.assertEqual(summary["retained_jsonl_write_blocked_count"], 6)
        self.assertEqual(summary["retention_write_blocked_count"], 6)
        self.assertEqual(summary["runtime_influence_blocked_count"], 6)
        self.assertEqual(summary["predictor_mutation_blocked_count"], 6)
        self.assertEqual(summary["proof_claim_blocked_count"], 6)

    def test_boundary_index_updates_for_memory_write_approval_boundary(self):
        result = run_memory_write_approval_boundary_minimal_check()
        boundary = result["boundary"]
        self.assertTrue(boundary["boundary_change_required"])
        self.assertTrue(boundary["boundary_index_update_required"])
        self.assertEqual(boundary["boundary_index_version_before"], BOUNDARY_INDEX_VERSION_BEFORE)
        self.assertEqual(boundary["boundary_index_version_after"], BOUNDARY_INDEX_VERSION_AFTER)


if __name__ == "__main__":
    unittest.main()
