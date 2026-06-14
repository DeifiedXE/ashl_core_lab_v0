import unittest

from ashl_core.memory_admission_package_design_minimal import (
    BOUNDARY_VERSION,
    REQUIRED_FUTURE_INPUTS,
    build_memory_admission_package_design,
    run_memory_admission_package_design_minimal_check,
    validate_memory_admission_package_design,
)
from ashl_core.memory_readiness_design_for_approved_bucket_lesson_minimal import (
    build_memory_readiness_design_for_approved_bucket_lesson,
)


class MemoryAdmissionPackageDesignMinimalTests(unittest.TestCase):
    def test_valid_memory_admission_package_design(self):
        record = build_memory_admission_package_design()
        result = validate_memory_admission_package_design(record)
        self.assertTrue(result["valid"])
        self.assertEqual(record["record_type"], "memory_admission_package_design")
        self.assertTrue(record["package_design_only"])
        self.assertFalse(record["memory_admission_performed"])
        self.assertFalse(record["memory_write_performed"])
        self.assertEqual(record["source_record_type"], "memory_readiness_design_for_approved_bucket_lesson")
        self.assertEqual(record["source_review_decision"], "approved_for_future_memory_readiness_design_only")
        self.assertEqual(record["allowed_future_target_forms"], ["reviewed_lesson_memory_candidate"])
        self.assertTrue(set(REQUIRED_FUTURE_INPUTS).issubset(record["required_future_inputs"]))
        self.assertEqual(record["required_future_approval"]["approval_source"], "explicit_user_statement")
        self.assertTrue(record["target_layer_design"]["target_layer_must_be_explicit"])
        self.assertIsNone(record["target_layer_design"]["default_target_layer"])
        self.assertFalse(record["target_layer_design"]["long_term_memory_allowed_now"])
        self.assertFalse(record["target_layer_design"]["core_memory_allowed"])
        self.assertFalse(record["retention_and_rollback_design"]["retained_jsonl_write_allowed_now"])
        self.assertTrue(record["retention_and_rollback_design"]["rollback_rule_required"])
        self.assertTrue(record["retention_and_rollback_design"]["rollback_must_block_auto_influence_rebuild"])
        self.assertFalse(record["cross_session_influence_design"]["cross_session_influence_allowed_now"])
        self.assertFalse(record["cross_session_influence_design"]["session_start_auto_influence_allowed"])
        self.assertFalse(record["runtime_influence_design"]["runtime_influence_allowed_now"])
        self.assertFalse(record["predictor_design"]["predictor_mutation_allowed_now"])
        self.assertTrue(record["audit_and_revocation_design"]["revocation_path_required"])

    def test_builder_rejects_invalid_source(self):
        source = build_memory_readiness_design_for_approved_bucket_lesson()
        source["source_review_decision"] = "rejected"
        with self.assertRaises(ValueError):
            build_memory_admission_package_design(source)

    def test_invalid_source_fields_block(self):
        cases = [
            ("source_record_type", "other", "source_record_type_not_memory_readiness_design"),
            ("source_review_decision", "rejected", "source_review_decision_not_approved"),
        ]
        for field, value, error in cases:
            with self.subTest(field=field):
                record = build_memory_admission_package_design()
                record[field] = value
                result = validate_memory_admission_package_design(record)
                self.assertFalse(result["valid"])
                self.assertIn(error, result["error_codes"])

    def test_invalid_design_status_flags_block(self):
        cases = [
            ("package_design_only", False, "package_design_only_not_true"),
            ("memory_admission_performed", True, "memory_admission_performed_not_false"),
            ("memory_write_performed", True, "memory_write_performed_not_false"),
        ]
        for field, value, error in cases:
            with self.subTest(field=field):
                record = build_memory_admission_package_design()
                record[field] = value
                result = validate_memory_admission_package_design(record)
                self.assertFalse(result["valid"])
                self.assertIn(error, result["error_codes"])

    def test_invalid_future_approval_and_inputs_block(self):
        record = build_memory_admission_package_design()
        record["required_future_approval"]["approval_text_required"] = False
        result = validate_memory_admission_package_design(record)
        self.assertFalse(result["valid"])
        self.assertIn("required_future_approval_approval_text_required_not_expected", result["error_codes"])

        record = build_memory_admission_package_design()
        record["required_future_inputs"] = list(REQUIRED_FUTURE_INPUTS[:-1])
        result = validate_memory_admission_package_design(record)
        self.assertFalse(result["valid"])
        self.assertIn("missing_required_future_input:audit_and_revocation_path_record", result["error_codes"])

    def test_invalid_target_layer_design_blocks(self):
        cases = [
            ("target_layer_must_be_explicit", False, "target_layer_design_target_layer_must_be_explicit_not_expected"),
            ("default_target_layer", "long_term_memory", "default_target_layer_not_none"),
            ("long_term_memory_allowed_now", True, "target_layer_design_long_term_memory_allowed_now_not_expected"),
            ("core_memory_allowed", True, "target_layer_design_core_memory_allowed_not_expected"),
        ]
        for field, value, error in cases:
            with self.subTest(field=field):
                record = build_memory_admission_package_design()
                record["target_layer_design"][field] = value
                result = validate_memory_admission_package_design(record)
                self.assertFalse(result["valid"])
                self.assertIn(error, result["error_codes"])

    def test_invalid_retention_rollback_and_cross_session_blocks(self):
        cases = [
            (
                "retention_and_rollback_design",
                "retained_jsonl_write_allowed_now",
                True,
                "retention_and_rollback_design_retained_jsonl_write_allowed_now_not_expected",
            ),
            (
                "retention_and_rollback_design",
                "rollback_rule_required",
                False,
                "retention_and_rollback_design_rollback_rule_required_not_expected",
            ),
            (
                "retention_and_rollback_design",
                "rollback_must_block_auto_influence_rebuild",
                False,
                "retention_and_rollback_design_rollback_must_block_auto_influence_rebuild_not_expected",
            ),
            (
                "cross_session_influence_design",
                "cross_session_influence_allowed_now",
                True,
                "cross_session_influence_design_cross_session_influence_allowed_now_not_expected",
            ),
            (
                "cross_session_influence_design",
                "session_start_auto_influence_allowed",
                True,
                "cross_session_influence_design_session_start_auto_influence_allowed_not_expected",
            ),
        ]
        for section, field, value, error in cases:
            with self.subTest(section=section, field=field):
                record = build_memory_admission_package_design()
                record[section][field] = value
                result = validate_memory_admission_package_design(record)
                self.assertFalse(result["valid"])
                self.assertIn(error, result["error_codes"])

    def test_invalid_runtime_predictor_and_audit_blocks(self):
        cases = [
            (
                "runtime_influence_design",
                "runtime_influence_allowed_now",
                True,
                "runtime_influence_design_runtime_influence_allowed_now_not_expected",
            ),
            (
                "runtime_influence_design",
                "future_runtime_influence_requires_separate_boundary_package",
                False,
                "runtime_influence_design_future_runtime_influence_requires_separate_boundary_package_not_expected",
            ),
            (
                "predictor_design",
                "predictor_influence_allowed_now",
                True,
                "predictor_design_predictor_influence_allowed_now_not_expected",
            ),
            (
                "predictor_design",
                "predictor_mutation_allowed_now",
                True,
                "predictor_design_predictor_mutation_allowed_now_not_expected",
            ),
            (
                "predictor_design",
                "future_predictor_influence_requires_separate_boundary_package",
                False,
                "predictor_design_future_predictor_influence_requires_separate_boundary_package_not_expected",
            ),
            (
                "audit_and_revocation_design",
                "revocation_path_required",
                False,
                "audit_and_revocation_design_revocation_path_required_not_true",
            ),
        ]
        for section, field, value, error in cases:
            with self.subTest(section=section, field=field):
                record = build_memory_admission_package_design()
                record[section][field] = value
                result = validate_memory_admission_package_design(record)
                self.assertFalse(result["valid"])
                self.assertIn(error, result["error_codes"])

    def test_invalid_forbidden_top_level_flags_block(self):
        for field in (
            "memory_admission_allowed_now",
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
                record = build_memory_admission_package_design()
                record[field] = True
                result = validate_memory_admission_package_design(record)
                self.assertFalse(result["valid"])
                self.assertIn(f"{field}_not_false", result["error_codes"])

    def test_invalid_qingyin_and_repo_audit_claims_block(self):
        cases = [
            ("repo_audit_acknowledged", False, "repo_audit_acknowledged_not_true"),
            ("qingyin_self_authored_lesson_text", True, "qingyin_self_authored_lesson_text_not_false"),
            ("autonomous_learning_claim_allowed", True, "autonomous_learning_claim_allowed_not_false"),
            ("autonomous_action_claim_allowed", True, "autonomous_action_claim_allowed_not_false"),
        ]
        for field, value, error in cases:
            with self.subTest(field=field):
                record = build_memory_admission_package_design()
                record[field] = value
                result = validate_memory_admission_package_design(record)
                self.assertFalse(result["valid"])
                self.assertIn(error, result["error_codes"])

    def test_summary_counts_are_deterministic(self):
        result = run_memory_admission_package_design_minimal_check()
        summary = result["summary"]
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["valid_memory_admission_design_count"], 1)
        self.assertGreaterEqual(summary["invalid_memory_admission_design_count"], 1)
        self.assertEqual(summary["source_readiness_checked_count"], 1)
        self.assertEqual(summary["future_approval_required_count"], 1)
        self.assertEqual(summary["target_layer_selection_required_count"], 1)
        self.assertEqual(summary["rollback_rule_required_count"], 1)
        self.assertEqual(summary["cross_session_rebuild_rule_required_count"], 1)
        self.assertEqual(summary["runtime_boundary_required_count"], 1)
        self.assertEqual(summary["predictor_boundary_required_count"], 1)
        self.assertEqual(summary["memory_admission_blocked_count"], 1)
        self.assertEqual(summary["memory_write_blocked_count"], 1)
        self.assertEqual(summary["retained_jsonl_write_blocked_count"], 1)
        self.assertEqual(summary["runtime_influence_blocked_count"], 1)
        self.assertEqual(summary["predictor_mutation_blocked_count"], 1)
        self.assertEqual(summary["proof_claim_blocked_count"], 1)

    def test_boundary_index_is_unchanged(self):
        result = run_memory_admission_package_design_minimal_check()
        boundary = result["boundary"]
        self.assertFalse(boundary["boundary_change_required"])
        self.assertFalse(boundary["boundary_index_update_required"])
        self.assertEqual(boundary["boundary_index_version_before"], BOUNDARY_VERSION)
        self.assertEqual(boundary["boundary_index_version_after"], BOUNDARY_VERSION)


if __name__ == "__main__":
    unittest.main()
