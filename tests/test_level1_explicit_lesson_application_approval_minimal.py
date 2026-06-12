import unittest

from ashl_core.level1_explicit_lesson_application_approval_minimal import (
    build_level1_explicit_lesson_application_approval,
    run_level1_explicit_lesson_application_approval_minimal_check,
    validate_level1_explicit_lesson_application_approval,
)


APPROVED = "approved_for_future_level1_sandbox_application_package"
REJECTED = "rejected_for_application"
NEEDS_MORE = "needs_more_evidence_before_application"


class Level1ExplicitLessonApplicationApprovalMinimalTests(unittest.TestCase):
    def _approved_record(self):
        return build_level1_explicit_lesson_application_approval(
            approval_decision=APPROVED,
            approval_source="explicit_user_statement",
            approval_text="I explicitly approve a future Phase0 Level 1 sandbox-only lesson application package.",
        )

    def test_valid_approved_explicit_application_approval_is_created(self):
        record = self._approved_record()

        self.assertTrue(validate_level1_explicit_lesson_application_approval(record)["valid"])
        self.assertEqual(record["human_application_approval"]["approval_decision"], APPROVED)

    def test_valid_rejected_application_decision_is_created(self):
        record = build_level1_explicit_lesson_application_approval(approval_decision=REJECTED)

        self.assertTrue(validate_level1_explicit_lesson_application_approval(record)["valid"])
        self.assertTrue(record["approval_result"]["rejected_for_application"])

    def test_valid_needs_more_evidence_application_decision_is_created(self):
        record = build_level1_explicit_lesson_application_approval(approval_decision=NEEDS_MORE)

        self.assertTrue(validate_level1_explicit_lesson_application_approval(record)["valid"])
        self.assertTrue(record["approval_result"]["needs_more_evidence_before_application"])

    def test_approved_decision_may_enter_future_level1_sandbox_application_package(self):
        record = self._approved_record()

        self.assertTrue(record["allowed_next_layer"]["may_enter_level1_sandbox_lesson_application_package"])

    def test_approved_record_requires_approval_source_explicit_user_statement(self):
        record = self._approved_record()
        record["human_application_approval"]["approval_source"] = "test_fixture"

        self.assertFalse(validate_level1_explicit_lesson_application_approval(record)["valid"])

    def test_approved_record_requires_non_empty_approval_text(self):
        record = self._approved_record()
        record["human_application_approval"]["approval_text"] = ""

        self.assertFalse(validate_level1_explicit_lesson_application_approval(record)["valid"])

    def test_approved_record_requires_approval_actor_user(self):
        record = self._approved_record()
        record["human_application_approval"]["approval_actor"] = "codex"

        self.assertFalse(validate_level1_explicit_lesson_application_approval(record)["valid"])

    def test_approved_record_requires_approver_role_project_owner(self):
        record = self._approved_record()
        record["human_application_approval"]["approver_role"] = "assistant"

        self.assertFalse(validate_level1_explicit_lesson_application_approval(record)["valid"])

    def test_codex_self_approval_is_blocked(self):
        record = self._approved_record()
        record["human_application_approval"]["codex_self_approval_allowed"] = True

        self.assertFalse(validate_level1_explicit_lesson_application_approval(record)["valid"])

    def test_ai_self_approval_is_blocked(self):
        record = self._approved_record()
        record["human_application_approval"]["ai_self_approval_allowed"] = True

        self.assertFalse(validate_level1_explicit_lesson_application_approval(record)["valid"])

    def test_demo_fixture_is_not_real_approval(self):
        record = self._approved_record()
        record["human_application_approval"]["demo_fixture_is_real_approval"] = True

        self.assertFalse(validate_level1_explicit_lesson_application_approval(record)["valid"])

    def test_implicit_approval_is_blocked(self):
        record = self._approved_record()
        record["human_application_approval"]["implicit_approval_allowed"] = True

        self.assertFalse(validate_level1_explicit_lesson_application_approval(record)["valid"])

    def test_implicit_chat_command_alone_is_not_approval(self):
        record = self._approved_record()
        record["human_application_approval"]["approval_source"] = "implicit_chat_command"
        record["human_application_approval"]["approval_inferred_from_marker_text"] = True

        self.assertFalse(validate_level1_explicit_lesson_application_approval(record)["valid"])

    def test_completed_readiness_is_not_approval(self):
        record = self._approved_record()
        record["human_application_approval"]["approval_inferred_from_readiness"] = True

        self.assertFalse(validate_level1_explicit_lesson_application_approval(record)["valid"])

    def test_completed_tests_are_not_approval(self):
        record = self._approved_record()
        record["human_application_approval"]["approval_inferred_from_completed_tests"] = True

        self.assertFalse(validate_level1_explicit_lesson_application_approval(record)["valid"])

    def test_may_enter_false_without_explicit_user_statement(self):
        record = build_level1_explicit_lesson_application_approval(approval_decision=APPROVED)

        self.assertFalse(record["allowed_next_layer"]["may_enter_level1_sandbox_lesson_application_package"])
        self.assertFalse(validate_level1_explicit_lesson_application_approval(record)["valid"])

    def test_valid_explicit_user_approval_can_enter_future_application_package(self):
        record = self._approved_record()

        self.assertTrue(record["approval_result"]["explicit_user_statement_present"])
        self.assertTrue(record["approval_result"]["approval_source_valid"])
        self.assertTrue(record["approval_result"]["approval_actor_valid"])
        self.assertTrue(record["allowed_next_layer"]["may_enter_level1_sandbox_lesson_application_package"])

    def test_approved_decision_does_not_apply_lesson_now(self):
        record = self._approved_record()

        self.assertFalse(record["human_application_approval"]["approval_applies_lesson_now"])
        self.assertFalse(record["approval_result"]["lesson_applied"])
        self.assertFalse(record["approval_result"]["sandbox_lesson_applied"])

    def test_approved_decision_is_sandbox_only(self):
        record = self._approved_record()

        self.assertTrue(record["approval_scope"]["sandbox_only"])
        self.assertFalse(record["approval_scope"]["production_scope"])
        self.assertFalse(record["approval_scope"]["runtime_global_scope"])

    def test_approved_decision_is_future_package_only(self):
        record = self._approved_record()

        self.assertTrue(record["human_application_approval"]["approval_is_for_future_package_only"])

    def test_approved_decision_cannot_write_memory(self):
        record = self._approved_record()

        self.assertFalse(record["allowed_next_layer"]["may_write_memory"])
        self.assertFalse(record["approval_result"]["memory_write"])

    def test_approved_decision_cannot_write_retention(self):
        record = self._approved_record()

        self.assertFalse(record["allowed_next_layer"]["may_write_retention"])
        self.assertFalse(record["approval_result"]["retention_write"])

    def test_approved_decision_cannot_mutate_predictor(self):
        record = self._approved_record()

        self.assertFalse(record["allowed_next_layer"]["may_mutate_predictor"])
        self.assertFalse(record["approval_result"]["predictor_modified"])

    def test_approved_decision_cannot_change_runtime_behavior(self):
        record = self._approved_record()

        self.assertFalse(record["allowed_next_layer"]["may_change_runtime_behavior"])
        self.assertFalse(record["approval_result"]["runtime_behavior_changed"])

    def test_approved_decision_cannot_create_final_action(self):
        record = self._approved_record()

        self.assertFalse(record["allowed_next_layer"]["may_create_final_action"])

    def test_rejected_decision_allows_no_next_layer(self):
        record = build_level1_explicit_lesson_application_approval(approval_decision=REJECTED)

        self.assertTrue(all(value is False for value in record["allowed_next_layer"].values()))

    def test_needs_more_evidence_decision_allows_no_next_layer(self):
        record = build_level1_explicit_lesson_application_approval(approval_decision=NEEDS_MORE)

        self.assertTrue(all(value is False for value in record["allowed_next_layer"].values()))

    def test_wrong_source_readiness_status_blocks(self):
        record = self._approved_record()

        record["source_readiness"]["readiness_status"] = "ready"

        self.assertFalse(validate_level1_explicit_lesson_application_approval(record)["valid"])

    def test_scope_violations_block(self):
        for field in (
            "production_scope",
            "runtime_global_scope",
            "persistent_policy_scope",
            "memory_write_scope",
            "retention_write_scope",
            "predictor_mutation_scope",
        ):
            with self.subTest(field=field):
                record = self._approved_record()
                record["approval_scope"][field] = True

                self.assertFalse(validate_level1_explicit_lesson_application_approval(record)["valid"])

    def test_unknown_approval_decision_blocks(self):
        record = self._approved_record()

        record["human_application_approval"]["approval_decision"] = "apply_now"

        self.assertFalse(validate_level1_explicit_lesson_application_approval(record)["valid"])

    def test_approval_applies_lesson_now_true_blocks(self):
        record = self._approved_record()

        record["human_application_approval"]["approval_applies_lesson_now"] = True

        self.assertFalse(validate_level1_explicit_lesson_application_approval(record)["valid"])

    def test_may_apply_lesson_in_this_package_true_blocks(self):
        record = self._approved_record()

        record["allowed_next_layer"]["may_apply_lesson_in_this_package"] = True

        self.assertFalse(validate_level1_explicit_lesson_application_approval(record)["valid"])

    def test_memory_write_true_blocks(self):
        record = self._approved_record()

        record["approval_result"]["memory_write"] = True

        self.assertFalse(validate_level1_explicit_lesson_application_approval(record)["valid"])

    def test_retention_write_true_blocks(self):
        record = self._approved_record()

        record["approval_result"]["retention_write"] = True

        self.assertFalse(validate_level1_explicit_lesson_application_approval(record)["valid"])

    def test_predictor_modified_true_blocks(self):
        record = self._approved_record()

        record["approval_result"]["predictor_modified"] = True

        self.assertFalse(validate_level1_explicit_lesson_application_approval(record)["valid"])

    def test_runtime_behavior_changed_true_blocks(self):
        record = self._approved_record()

        record["approval_result"]["runtime_behavior_changed"] = True

        self.assertFalse(validate_level1_explicit_lesson_application_approval(record)["valid"])

    def test_final_action_created_true_blocks(self):
        record = self._approved_record()

        record["blocked_flags"]["final_action_created"] = True

        self.assertFalse(validate_level1_explicit_lesson_application_approval(record)["valid"])

    def test_proof_of_learning_claim_true_blocks(self):
        record = self._approved_record()

        record["blocked_flags"]["proof_of_learning_claim"] = True

        self.assertFalse(validate_level1_explicit_lesson_application_approval(record)["valid"])

    def test_demo_summary_counts_are_deterministic(self):
        result = run_level1_explicit_lesson_application_approval_minimal_check()
        summary = result["summary"]

        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["explicit_approval_result_count"], 62)
        self.assertEqual(summary["valid_explicit_approval_result_count"], 3)
        self.assertEqual(summary["invalid_explicit_approval_result_count"], 59)
        self.assertEqual(summary["approved_for_future_package_count"], 1)
        self.assertEqual(summary["rejected_for_application_count"], 1)
        self.assertEqual(summary["needs_more_evidence_before_application_count"], 1)
        self.assertEqual(summary["explicit_human_application_approval_present_count"], 1)
        self.assertEqual(summary["explicit_user_statement_present_count"], 1)
        self.assertEqual(summary["approval_source_valid_count"], 1)
        self.assertEqual(summary["approval_actor_valid_count"], 1)
        self.assertEqual(summary["demo_fixture_rejected_as_real_approval_count"], 3)
        self.assertEqual(summary["codex_self_approval_rejected_count"], 3)
        self.assertEqual(summary["ai_self_approval_rejected_count"], 3)
        self.assertEqual(summary["implicit_approval_rejected_count"], 3)
        self.assertEqual(summary["may_enter_level1_sandbox_lesson_application_package_count"], 1)
        self.assertEqual(summary["lesson_application_blocked_count"], 3)


if __name__ == "__main__":
    unittest.main()
