import unittest

from ashl_core.reviewed_lesson_sandbox_application_readiness_minimal import (
    build_reviewed_lesson_sandbox_application_readiness,
    run_reviewed_lesson_sandbox_application_readiness_minimal_check,
    validate_reviewed_lesson_sandbox_application_readiness,
)


class ReviewedLessonSandboxApplicationReadinessMinimalTests(unittest.TestCase):
    def test_valid_sandbox_application_readiness_record_is_created(self):
        record = build_reviewed_lesson_sandbox_application_readiness()

        self.assertTrue(validate_reviewed_lesson_sandbox_application_readiness(record)["valid"])
        self.assertEqual(record["readiness_mode"], "sandbox_application_readiness_only")

    def test_readiness_reuses_generic_lesson_evidence_pipeline_completion_bridge(self):
        record = build_reviewed_lesson_sandbox_application_readiness()

        self.assertEqual(
            record["source_evidence"]["source_bridge_id"],
            "generic_lesson_evidence_pipeline_completion_bridge_demo_001",
        )
        self.assertEqual(record["source_evidence"]["source_type"], "generic_lesson_effect_evidence_trace")

    def test_lesson_effect_evidence_trace_is_present(self):
        record = build_reviewed_lesson_sandbox_application_readiness()

        self.assertTrue(record["source_evidence"]["lesson_effect_evidence_trace_created"])

    def test_evidence_only_true_required(self):
        record = build_reviewed_lesson_sandbox_application_readiness()

        record["source_evidence"]["evidence_only"] = False

        self.assertFalse(validate_reviewed_lesson_sandbox_application_readiness(record)["valid"])

    def test_target_scope_is_phase0_level1_sandbox_only(self):
        record = build_reviewed_lesson_sandbox_application_readiness()

        self.assertEqual(record["application_scope"]["target_scope"], "phase0_level1_sandbox_only")
        self.assertEqual(record["application_scope"]["target_level_id"], "phase0_level1_first_contact_danger")

    def test_production_scope_false_required(self):
        record = build_reviewed_lesson_sandbox_application_readiness()

        record["application_scope"]["production_scope"] = True

        self.assertFalse(validate_reviewed_lesson_sandbox_application_readiness(record)["valid"])

    def test_all_satisfied_requirements_true_required(self):
        record = build_reviewed_lesson_sandbox_application_readiness()

        self.assertTrue(all(record["satisfied_requirements"].values()))

        record["satisfied_requirements"]["rollback_path_defined"] = False

        self.assertFalse(validate_reviewed_lesson_sandbox_application_readiness(record)["valid"])

    def test_explicit_human_application_approval_missing_required(self):
        record = build_reviewed_lesson_sandbox_application_readiness()

        self.assertTrue(record["missing_requirements"]["explicit_human_application_approval"])

        record["missing_requirements"]["explicit_human_application_approval"] = False

        self.assertFalse(validate_reviewed_lesson_sandbox_application_readiness(record)["valid"])

    def test_readiness_status_is_not_ready_missing_explicit_human_application_approval(self):
        record = build_reviewed_lesson_sandbox_application_readiness()

        self.assertEqual(
            record["readiness_result"]["readiness_status"],
            "not_ready_missing_explicit_human_application_approval",
        )

    def test_ready_for_application_false_required(self):
        record = build_reviewed_lesson_sandbox_application_readiness()

        record["readiness_result"]["ready_for_application"] = True

        self.assertFalse(validate_reviewed_lesson_sandbox_application_readiness(record)["valid"])

    def test_allowed_to_apply_lesson_false_required(self):
        record = build_reviewed_lesson_sandbox_application_readiness()

        record["readiness_result"]["allowed_to_apply_lesson"] = True

        self.assertFalse(validate_reviewed_lesson_sandbox_application_readiness(record)["valid"])

    def test_allowed_write_and_mutation_flags_false_required(self):
        for field in (
            "allowed_to_write_memory",
            "allowed_to_write_retention",
            "allowed_to_mutate_predictor",
            "allowed_to_change_runtime_behavior",
            "allowed_to_create_final_action",
        ):
            with self.subTest(field=field):
                record = build_reviewed_lesson_sandbox_application_readiness()
                record["readiness_result"][field] = True

                self.assertFalse(validate_reviewed_lesson_sandbox_application_readiness(record)["valid"])

    def test_wrong_scope_blocks(self):
        record = build_reviewed_lesson_sandbox_application_readiness()

        record["application_scope"]["target_scope"] = "runtime_global"

        self.assertFalse(validate_reviewed_lesson_sandbox_application_readiness(record)["valid"])

    def test_false_satisfied_requirement_blocks(self):
        record = build_reviewed_lesson_sandbox_application_readiness()

        record["satisfied_requirements"]["mentor_override_preserved"] = False

        self.assertFalse(validate_reviewed_lesson_sandbox_application_readiness(record)["valid"])

    def test_human_approval_not_missing_blocks(self):
        record = build_reviewed_lesson_sandbox_application_readiness()

        record["missing_requirements"]["explicit_human_application_approval"] = False

        self.assertFalse(validate_reviewed_lesson_sandbox_application_readiness(record)["valid"])

    def test_memory_write_true_blocks(self):
        record = build_reviewed_lesson_sandbox_application_readiness()

        record["source_evidence"]["memory_write"] = True

        self.assertFalse(validate_reviewed_lesson_sandbox_application_readiness(record)["valid"])

    def test_retention_write_true_blocks(self):
        record = build_reviewed_lesson_sandbox_application_readiness()

        record["source_evidence"]["retention_write"] = True

        self.assertFalse(validate_reviewed_lesson_sandbox_application_readiness(record)["valid"])

    def test_predictor_modified_true_blocks(self):
        record = build_reviewed_lesson_sandbox_application_readiness()

        record["source_evidence"]["predictor_modified"] = True

        self.assertFalse(validate_reviewed_lesson_sandbox_application_readiness(record)["valid"])

    def test_runtime_behavior_changed_true_blocks(self):
        record = build_reviewed_lesson_sandbox_application_readiness()

        record["source_evidence"]["runtime_behavior_changed"] = True

        self.assertFalse(validate_reviewed_lesson_sandbox_application_readiness(record)["valid"])

    def test_proof_of_learning_claim_true_blocks(self):
        record = build_reviewed_lesson_sandbox_application_readiness()

        record["blocked_flags"]["proof_of_learning_claim"] = True

        self.assertFalse(validate_reviewed_lesson_sandbox_application_readiness(record)["valid"])

    def test_demo_summary_counts_are_deterministic(self):
        result = run_reviewed_lesson_sandbox_application_readiness_minimal_check()
        summary = result["summary"]

        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["sandbox_application_readiness_result_count"], 60)
        self.assertEqual(summary["valid_sandbox_application_readiness_count"], 1)
        self.assertEqual(summary["invalid_sandbox_application_readiness_count"], 59)
        self.assertEqual(summary["evidence_trace_ready_count"], 1)
        self.assertEqual(summary["application_scope_defined_count"], 1)
        self.assertEqual(summary["rollback_path_defined_count"], 1)
        self.assertEqual(summary["audit_trace_required_count"], 1)
        self.assertEqual(summary["mentor_override_preserved_count"], 1)
        self.assertEqual(summary["missing_explicit_human_application_approval_count"], 1)
        self.assertEqual(summary["not_ready_status_count"], 1)
        self.assertEqual(summary["ready_for_application_blocked_count"], 1)
        self.assertEqual(summary["lesson_application_blocked_count"], 1)


if __name__ == "__main__":
    unittest.main()
