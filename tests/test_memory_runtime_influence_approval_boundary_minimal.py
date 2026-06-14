import unittest

from ashl_core.memory_influence_preview_minimal import build_memory_influence_preview_record
from ashl_core.memory_runtime_influence_approval_boundary_minimal import (
    APPROVED_DECISION,
    BLOCKED_DECISIONS,
    BOUNDARY_INDEX_VERSION_AFTER,
    BOUNDARY_INDEX_VERSION_BEFORE,
    build_memory_runtime_influence_approval_record,
    run_memory_runtime_influence_approval_boundary_minimal_check,
    validate_memory_runtime_influence_approval_record,
)


class MemoryRuntimeInfluenceApprovalBoundaryMinimalTests(unittest.TestCase):
    def test_valid_approval(self):
        record = build_memory_runtime_influence_approval_record()
        result = validate_memory_runtime_influence_approval_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual("memory_runtime_influence_approval", record["record_type"])
        self.assertEqual(APPROVED_DECISION, record["approval_decision"])
        self.assertTrue(record["future_memory_runtime_influence_package_may_proceed"])
        self.assertEqual("explicit_user_statement", record["approval_source"])
        self.assertEqual("user", record["approval_actor"])
        self.assertEqual("project_owner", record["approver_role"])
        self.assertFalse(record["runtime_influence_performed"])
        self.assertFalse(record["selected_action_allowed"])
        self.assertFalse(record["final_action_allowed"])
        self.assertFalse(record["proof_of_learning_claim_allowed"])

    def test_blocked_decisions_are_valid_but_cannot_proceed(self):
        for decision in BLOCKED_DECISIONS:
            with self.subTest(decision=decision):
                record = build_memory_runtime_influence_approval_record(approval_decision=decision)
                result = validate_memory_runtime_influence_approval_record(record)

                self.assertTrue(result["valid"])
                self.assertFalse(record["future_memory_runtime_influence_package_may_proceed"])
                self.assertTrue(result["blocked_decision_checked"])

    def test_all_allowed_decisions_supported(self):
        for decision in (APPROVED_DECISION,) + BLOCKED_DECISIONS:
            with self.subTest(decision=decision):
                record = build_memory_runtime_influence_approval_record(approval_decision=decision)

                self.assertTrue(validate_memory_runtime_influence_approval_record(record)["valid"])

    def test_invalid_approval_source_actor_role_or_text(self):
        cases = (
            ("approval_source", "codex_report", "approval_source_not_expected"),
            ("approval_actor", "codex", "approval_actor_not_expected"),
            ("approver_role", "assistant", "approver_role_not_expected"),
            ("approval_text", "", "approval_text_empty"),
        )
        for field, value, error in cases:
            with self.subTest(field=field):
                record = build_memory_runtime_influence_approval_record()
                record[field] = value

                self.assertIn(error, validate_memory_runtime_influence_approval_record(record)["error_codes"])

    def test_invalid_source_preview_blocks(self):
        source = build_memory_influence_preview_record()
        source["preview_is_runtime_influence"] = True
        with self.assertRaises(ValueError):
            build_memory_runtime_influence_approval_record(source)

        record = build_memory_runtime_influence_approval_record()
        record["source_memory_influence_preview"] = source
        result = validate_memory_runtime_influence_approval_record(record)

        self.assertFalse(result["valid"])
        self.assertIn("source_memory_influence_preview_invalid", result["error_codes"])

    def test_codex_ai_fixture_task_queue_passing_tests_are_not_approval(self):
        for field in (
            "codex_self_approval_allowed",
            "ai_self_approval_allowed",
            "fixture_approval_is_real_approval",
            "task_queue_status_is_approval",
            "passing_tests_are_approval",
            "implicit_chat_command_is_approval",
        ):
            with self.subTest(field=field):
                record = build_memory_runtime_influence_approval_record()
                record[field] = True

                self.assertIn(f"{field}_not_false", validate_memory_runtime_influence_approval_record(record)["error_codes"])

    def test_runtime_influence_performed_blocks(self):
        self.assert_false_field_blocks("runtime_influence_performed")

    def test_predictor_mutation_allowed_blocks(self):
        self.assert_false_field_blocks("predictor_mutation_allowed")

    def test_selected_action_allowed_blocks(self):
        self.assert_false_field_blocks("selected_action_allowed")

    def test_final_action_allowed_blocks(self):
        self.assert_false_field_blocks("final_action_allowed")

    def test_production_behavior_allowed_blocks(self):
        self.assert_false_field_blocks("production_behavior_change_allowed")

    def test_retained_jsonl_and_retention_write_allowed_blocks(self):
        self.assert_false_field_blocks("retained_jsonl_write_allowed")
        self.assert_false_field_blocks("retention_write_allowed")

    def test_proof_claim_blocks(self):
        self.assert_false_field_blocks("proof_of_learning_claim_allowed")

    def test_autonomous_learning_or_action_claim_blocks(self):
        self.assert_false_field_blocks("autonomous_learning_claim_allowed")
        self.assert_false_field_blocks("autonomous_action_claim_allowed")

    def test_required_future_safety_requirements(self):
        for field in (
            "requires_bounded_safety_envelope",
            "requires_rollback_to_baseline",
            "requires_no_selected_action",
            "requires_no_final_action",
            "requires_no_predictor_mutation",
            "requires_no_production_behavior",
            "repo_audit_acknowledged",
            "audit_recorded",
            "rollback_available",
        ):
            with self.subTest(field=field):
                record = build_memory_runtime_influence_approval_record()
                record[field] = False

                self.assertIn(f"{field}_not_true", validate_memory_runtime_influence_approval_record(record)["error_codes"])

    def test_decision_consistency_required(self):
        approved = build_memory_runtime_influence_approval_record()
        approved["future_memory_runtime_influence_package_may_proceed"] = False
        self.assertIn(
            "approved_decision_may_proceed_not_true",
            validate_memory_runtime_influence_approval_record(approved)["error_codes"],
        )

        blocked = build_memory_runtime_influence_approval_record(approval_decision="rejected_for_runtime_influence")
        blocked["future_memory_runtime_influence_package_may_proceed"] = True
        self.assertIn(
            "blocked_decision_may_proceed_not_false",
            validate_memory_runtime_influence_approval_record(blocked)["error_codes"],
        )

    def test_demo_summary_counts_are_deterministic(self):
        result = run_memory_runtime_influence_approval_boundary_minimal_check()
        summary = result["summary"]

        self.assertEqual("ok", result["status"])
        self.assertEqual(5, summary["valid_approval_count"])
        self.assertGreaterEqual(summary["invalid_approval_count"], 1)
        self.assertEqual(1, summary["approved_decision_checked_count"])
        self.assertEqual(4, summary["blocked_decision_checked_count"])
        self.assertEqual(5, summary["source_preview_checked_count"])
        self.assertEqual(5, summary["explicit_user_statement_checked_count"])
        self.assertEqual(5, summary["project_owner_checked_count"])
        self.assertEqual(5, summary["runtime_influence_blocked_count"])
        self.assertEqual(5, summary["predictor_mutation_blocked_count"])
        self.assertEqual(5, summary["selected_action_blocked_count"])
        self.assertEqual(5, summary["final_action_blocked_count"])
        self.assertEqual(5, summary["production_behavior_blocked_count"])
        self.assertEqual(5, summary["proof_claim_blocked_count"])

    def test_boundary_index_updates_for_approval_boundary(self):
        boundary = run_memory_runtime_influence_approval_boundary_minimal_check()["boundary"]

        self.assertTrue(boundary["boundary_change_required"])
        self.assertTrue(boundary["boundary_index_update_required"])
        self.assertEqual("2026-06-09-b79", BOUNDARY_INDEX_VERSION_BEFORE)
        self.assertEqual("2026-06-09-b80", BOUNDARY_INDEX_VERSION_AFTER)
        self.assertEqual("2026-06-09-b79", boundary["boundary_index_version_before"])
        self.assertEqual("2026-06-09-b80", boundary["boundary_index_version_after"])

    def assert_false_field_blocks(self, field):
        record = build_memory_runtime_influence_approval_record()
        record[field] = True

        self.assertIn(f"{field}_not_false", validate_memory_runtime_influence_approval_record(record)["error_codes"])


if __name__ == "__main__":
    unittest.main()
