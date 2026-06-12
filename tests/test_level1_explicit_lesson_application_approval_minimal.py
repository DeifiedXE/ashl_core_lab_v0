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
    def test_valid_approved_explicit_application_approval_is_created(self):
        record = build_level1_explicit_lesson_application_approval(approval_decision=APPROVED)

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
        record = build_level1_explicit_lesson_application_approval(approval_decision=APPROVED)

        self.assertTrue(record["allowed_next_layer"]["may_enter_level1_sandbox_lesson_application_package"])

    def test_approved_decision_does_not_apply_lesson_now(self):
        record = build_level1_explicit_lesson_application_approval(approval_decision=APPROVED)

        self.assertFalse(record["human_application_approval"]["approval_applies_lesson_now"])
        self.assertFalse(record["approval_result"]["lesson_applied"])
        self.assertFalse(record["approval_result"]["sandbox_lesson_applied"])

    def test_approved_decision_is_sandbox_only(self):
        record = build_level1_explicit_lesson_application_approval(approval_decision=APPROVED)

        self.assertTrue(record["approval_scope"]["sandbox_only"])
        self.assertFalse(record["approval_scope"]["production_scope"])
        self.assertFalse(record["approval_scope"]["runtime_global_scope"])

    def test_approved_decision_is_future_package_only(self):
        record = build_level1_explicit_lesson_application_approval(approval_decision=APPROVED)

        self.assertTrue(record["human_application_approval"]["approval_is_for_future_package_only"])

    def test_approved_decision_cannot_write_memory(self):
        record = build_level1_explicit_lesson_application_approval(approval_decision=APPROVED)

        self.assertFalse(record["allowed_next_layer"]["may_write_memory"])
        self.assertFalse(record["approval_result"]["memory_write"])

    def test_approved_decision_cannot_write_retention(self):
        record = build_level1_explicit_lesson_application_approval(approval_decision=APPROVED)

        self.assertFalse(record["allowed_next_layer"]["may_write_retention"])
        self.assertFalse(record["approval_result"]["retention_write"])

    def test_approved_decision_cannot_mutate_predictor(self):
        record = build_level1_explicit_lesson_application_approval(approval_decision=APPROVED)

        self.assertFalse(record["allowed_next_layer"]["may_mutate_predictor"])
        self.assertFalse(record["approval_result"]["predictor_modified"])

    def test_approved_decision_cannot_change_runtime_behavior(self):
        record = build_level1_explicit_lesson_application_approval(approval_decision=APPROVED)

        self.assertFalse(record["allowed_next_layer"]["may_change_runtime_behavior"])
        self.assertFalse(record["approval_result"]["runtime_behavior_changed"])

    def test_approved_decision_cannot_create_final_action(self):
        record = build_level1_explicit_lesson_application_approval(approval_decision=APPROVED)

        self.assertFalse(record["allowed_next_layer"]["may_create_final_action"])

    def test_rejected_decision_allows_no_next_layer(self):
        record = build_level1_explicit_lesson_application_approval(approval_decision=REJECTED)

        self.assertTrue(all(value is False for value in record["allowed_next_layer"].values()))

    def test_needs_more_evidence_decision_allows_no_next_layer(self):
        record = build_level1_explicit_lesson_application_approval(approval_decision=NEEDS_MORE)

        self.assertTrue(all(value is False for value in record["allowed_next_layer"].values()))

    def test_wrong_source_readiness_status_blocks(self):
        record = build_level1_explicit_lesson_application_approval(approval_decision=APPROVED)

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
                record = build_level1_explicit_lesson_application_approval(approval_decision=APPROVED)
                record["approval_scope"][field] = True

                self.assertFalse(validate_level1_explicit_lesson_application_approval(record)["valid"])

    def test_unknown_approval_decision_blocks(self):
        record = build_level1_explicit_lesson_application_approval(approval_decision=APPROVED)

        record["human_application_approval"]["approval_decision"] = "apply_now"

        self.assertFalse(validate_level1_explicit_lesson_application_approval(record)["valid"])

    def test_approval_applies_lesson_now_true_blocks(self):
        record = build_level1_explicit_lesson_application_approval(approval_decision=APPROVED)

        record["human_application_approval"]["approval_applies_lesson_now"] = True

        self.assertFalse(validate_level1_explicit_lesson_application_approval(record)["valid"])

    def test_may_apply_lesson_in_this_package_true_blocks(self):
        record = build_level1_explicit_lesson_application_approval(approval_decision=APPROVED)

        record["allowed_next_layer"]["may_apply_lesson_in_this_package"] = True

        self.assertFalse(validate_level1_explicit_lesson_application_approval(record)["valid"])

    def test_memory_write_true_blocks(self):
        record = build_level1_explicit_lesson_application_approval(approval_decision=APPROVED)

        record["approval_result"]["memory_write"] = True

        self.assertFalse(validate_level1_explicit_lesson_application_approval(record)["valid"])

    def test_retention_write_true_blocks(self):
        record = build_level1_explicit_lesson_application_approval(approval_decision=APPROVED)

        record["approval_result"]["retention_write"] = True

        self.assertFalse(validate_level1_explicit_lesson_application_approval(record)["valid"])

    def test_predictor_modified_true_blocks(self):
        record = build_level1_explicit_lesson_application_approval(approval_decision=APPROVED)

        record["approval_result"]["predictor_modified"] = True

        self.assertFalse(validate_level1_explicit_lesson_application_approval(record)["valid"])

    def test_runtime_behavior_changed_true_blocks(self):
        record = build_level1_explicit_lesson_application_approval(approval_decision=APPROVED)

        record["approval_result"]["runtime_behavior_changed"] = True

        self.assertFalse(validate_level1_explicit_lesson_application_approval(record)["valid"])

    def test_final_action_created_true_blocks(self):
        record = build_level1_explicit_lesson_application_approval(approval_decision=APPROVED)

        record["blocked_flags"]["final_action_created"] = True

        self.assertFalse(validate_level1_explicit_lesson_application_approval(record)["valid"])

    def test_proof_of_learning_claim_true_blocks(self):
        record = build_level1_explicit_lesson_application_approval(approval_decision=APPROVED)

        record["blocked_flags"]["proof_of_learning_claim"] = True

        self.assertFalse(validate_level1_explicit_lesson_application_approval(record)["valid"])

    def test_demo_summary_counts_are_deterministic(self):
        result = run_level1_explicit_lesson_application_approval_minimal_check()
        summary = result["summary"]

        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["explicit_approval_result_count"], 51)
        self.assertEqual(summary["valid_explicit_approval_result_count"], 3)
        self.assertEqual(summary["invalid_explicit_approval_result_count"], 48)
        self.assertEqual(summary["approved_for_future_package_count"], 1)
        self.assertEqual(summary["rejected_for_application_count"], 1)
        self.assertEqual(summary["needs_more_evidence_before_application_count"], 1)
        self.assertEqual(summary["explicit_human_application_approval_present_count"], 1)
        self.assertEqual(summary["may_enter_level1_sandbox_lesson_application_package_count"], 1)
        self.assertEqual(summary["lesson_application_blocked_count"], 3)


if __name__ == "__main__":
    unittest.main()
