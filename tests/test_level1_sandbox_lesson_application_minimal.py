import unittest

from ashl_core.level1_explicit_lesson_application_approval_minimal import (
    APPROVED,
    NEEDS_MORE,
    REJECTED,
    build_level1_explicit_lesson_application_approval,
)
from ashl_core.level1_sandbox_lesson_application_minimal import (
    build_level1_sandbox_lesson_application,
    run_level1_sandbox_lesson_application_minimal_check,
    validate_level1_sandbox_lesson_application,
)
from ashl_core.reviewed_lesson_sandbox_application_readiness_minimal import (
    build_reviewed_lesson_sandbox_application_readiness,
)


class Level1SandboxLessonApplicationMinimalTests(unittest.TestCase):
    def _record(self):
        return build_level1_sandbox_lesson_application()

    def test_valid_level1_sandbox_lesson_application_is_created(self):
        record = self._record()

        self.assertTrue(validate_level1_sandbox_lesson_application(record)["valid"])
        self.assertEqual(record["application_status"], "applied_in_phase0_level1_sandbox_only")

    def test_reuses_readiness_and_explicit_approval(self):
        record = self._record()

        self.assertIn("readiness_record", record)
        self.assertIn("approval_record", record)
        self.assertEqual(record["approval_source"], "explicit_user_statement")
        self.assertEqual(record["approval_actor"], "user")
        self.assertEqual(record["approver_role"], "project_owner")
        self.assertTrue(record["approval_text"].strip())

    def test_application_scope_is_phase0_level1_sandbox_only(self):
        record = self._record()

        self.assertEqual(record["target_scope"], "phase0_level1_sandbox_only")
        self.assertFalse(record["blocked_boundaries"]["production_behavior_change"])
        self.assertFalse(record["blocked_boundaries"]["runtime_lesson_application"])

    def test_sandbox_effect_is_check_before_retry_for_danger_symbol(self):
        record = self._record()

        self.assertEqual(record["front_symbol"], "d")
        self.assertEqual(record["preferred_sandbox_action"], "check_before_retry")
        self.assertTrue(record["blocks_retry_same_action_until_check"])

    def test_audit_and_rollback_are_required(self):
        record = self._record()

        self.assertTrue(all(record["audit"].values()))
        self.assertTrue(record["rollback"]["rollback_available"])
        self.assertEqual(record["rollback"]["rollback_scope"], "phase0_level1_sandbox_application_record_only")

    def test_missing_readiness_blocks(self):
        record = self._record()
        record.pop("readiness_record")

        self.assertFalse(validate_level1_sandbox_lesson_application(record)["valid"])

    def test_not_ready_readiness_blocks(self):
        record = build_level1_sandbox_lesson_application(
            readiness_record=build_reviewed_lesson_sandbox_application_readiness()
        )

        self.assertFalse(validate_level1_sandbox_lesson_application(record)["valid"])

    def test_missing_approval_blocks(self):
        record = self._record()
        record.pop("approval_record")

        self.assertFalse(validate_level1_sandbox_lesson_application(record)["valid"])

    def test_rejected_approval_blocks(self):
        approval = build_level1_explicit_lesson_application_approval(approval_decision=REJECTED)
        record = build_level1_sandbox_lesson_application(approval_record=approval)

        self.assertFalse(validate_level1_sandbox_lesson_application(record)["valid"])

    def test_needs_more_evidence_approval_blocks(self):
        approval = build_level1_explicit_lesson_application_approval(approval_decision=NEEDS_MORE)
        record = build_level1_sandbox_lesson_application(approval_record=approval)

        self.assertFalse(validate_level1_sandbox_lesson_application(record)["valid"])

    def test_non_explicit_approval_source_blocks(self):
        record = self._record()
        record["approval_record"]["human_application_approval"]["approval_source"] = "implicit_chat_command"

        self.assertFalse(validate_level1_sandbox_lesson_application(record)["valid"])

    def test_codex_and_ai_self_approval_blocks(self):
        for actor in ("codex", "ai"):
            with self.subTest(actor=actor):
                record = self._record()
                record["approval_record"]["human_application_approval"]["approval_actor"] = actor

                self.assertFalse(validate_level1_sandbox_lesson_application(record)["valid"])

    def test_demo_fixture_as_real_approval_blocks(self):
        record = self._record()
        record["approval_record"]["human_application_approval"]["demo_fixture_is_real_approval"] = True

        self.assertFalse(validate_level1_sandbox_lesson_application(record)["valid"])

    def test_wrong_scope_blocks(self):
        record = self._record()
        record["target_scope"] = "production"

        self.assertFalse(validate_level1_sandbox_lesson_application(record)["valid"])

    def test_wrong_symbol_or_action_blocks(self):
        for path, value in (("front_symbol", "."), ("preferred_sandbox_action", "retry_same_action")):
            with self.subTest(path=path):
                record = self._record()
                record[path] = value

                self.assertFalse(validate_level1_sandbox_lesson_application(record)["valid"])

    def test_retry_block_false_blocks(self):
        record = self._record()
        record["blocks_retry_same_action_until_check"] = False

        self.assertFalse(validate_level1_sandbox_lesson_application(record)["valid"])

    def test_audit_missing_or_false_blocks(self):
        record = self._record()
        record["audit"]["source_readiness_checked"] = False
        self.assertFalse(validate_level1_sandbox_lesson_application(record)["valid"])

        record = self._record()
        record.pop("audit")
        self.assertFalse(validate_level1_sandbox_lesson_application(record)["valid"])

    def test_rollback_missing_or_false_blocks(self):
        record = self._record()
        record["rollback"]["rollback_available"] = False
        self.assertFalse(validate_level1_sandbox_lesson_application(record)["valid"])

        record = self._record()
        record.pop("rollback")
        self.assertFalse(validate_level1_sandbox_lesson_application(record)["valid"])

    def test_blocked_boundaries_true_block(self):
        for field in (
            "memory_write",
            "retention_write",
            "predictor_modified",
            "runtime_behavior_changed",
            "production_behavior_change",
            "selected_action_created",
            "final_action_created",
            "direct_action_command_created",
            "proof_of_learning_claimed",
        ):
            with self.subTest(field=field):
                record = self._record()
                record["blocked_boundaries"][field] = True

                self.assertFalse(validate_level1_sandbox_lesson_application(record)["valid"])

    def test_default_approval_builder_without_explicit_source_is_not_enough(self):
        approval = build_level1_explicit_lesson_application_approval(approval_decision=APPROVED)
        record = build_level1_sandbox_lesson_application(approval_record=approval)

        self.assertFalse(validate_level1_sandbox_lesson_application(record)["valid"])

    def test_demo_summary_counts_are_deterministic(self):
        result = run_level1_sandbox_lesson_application_minimal_check()
        summary = result["summary"]

        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["valid_level1_sandbox_application_count"], 1)
        self.assertEqual(summary["invalid_level1_sandbox_application_count"], 53)
        self.assertEqual(summary["sandbox_effect_applied_count"], 1)
        self.assertEqual(summary["readiness_checked_count"], 1)
        self.assertEqual(summary["approval_checked_count"], 1)
        self.assertEqual(summary["audit_recorded_count"], 1)
        self.assertEqual(summary["rollback_available_count"], 1)


if __name__ == "__main__":
    unittest.main()
