import unittest

from ashl_core.memory_admission_approval_boundary_minimal import build_memory_admission_approval_record
from ashl_core.memory_admission_minimal import (
    BOUNDARY_INDEX_VERSION_AFTER,
    BOUNDARY_INDEX_VERSION_BEFORE,
    build_memory_admission_record,
    build_reviewed_lesson_memory_candidate_record,
    run_memory_admission_minimal_check,
    validate_memory_admission_record,
    validate_reviewed_lesson_memory_candidate_record,
)
from ashl_core.memory_admission_package_design_minimal import build_memory_admission_package_design


class MemoryAdmissionMinimalTests(unittest.TestCase):
    def test_valid_memory_admission_into_reviewed_lesson_memory_candidate(self):
        record = build_memory_admission_record()
        result = validate_memory_admission_record(record)
        self.assertTrue(result["valid"])
        self.assertEqual(record["record_type"], "memory_admission")
        self.assertEqual(record["admission_status"], "admitted_as_reviewed_lesson_memory_candidate")
        self.assertEqual(record["admission_target_form"], "reviewed_lesson_memory_candidate")
        self.assertEqual(record["memory_layer_target"], "candidate_layer_only")
        self.assertTrue(record["memory_admission_performed"])
        self.assertFalse(record["long_term_memory_write_performed"])
        self.assertFalse(record["retained_jsonl_write_performed"])
        self.assertFalse(record["runtime_influence_enabled"])
        self.assertFalse(record["predictor_influence_enabled"])
        self.assertFalse(record["memory_write_allowed"])
        self.assertFalse(record["long_term_memory_write_allowed"])
        self.assertFalse(record["retained_jsonl_write_allowed"])

    def test_valid_reviewed_lesson_memory_candidate_record(self):
        candidate = build_reviewed_lesson_memory_candidate_record()
        result = validate_reviewed_lesson_memory_candidate_record(candidate)
        self.assertTrue(result["valid"])
        self.assertEqual(candidate["record_type"], "reviewed_lesson_memory_candidate")
        self.assertEqual(candidate["candidate_status"], "admitted_candidate_not_long_term_memory")
        self.assertEqual(candidate["memory_layer"], "candidate_layer_only")
        self.assertFalse(candidate["is_long_term_memory"])
        self.assertFalse(candidate["writes_jsonl"])
        self.assertFalse(candidate["runtime_read_enabled"])
        self.assertFalse(candidate["predictor_read_enabled"])
        self.assertTrue(candidate["human_reviewed"])
        self.assertTrue(candidate["human_approved_for_admission"])
        self.assertFalse(candidate["human_approved_for_memory_write"])

    def test_invalid_when_approval_is_missing(self):
        record = build_memory_admission_record()
        record.pop("source_memory_admission_approval")
        result = validate_memory_admission_record(record)
        self.assertFalse(result["valid"])
        self.assertIn("source_memory_admission_approval_missing", result["error_codes"])

    def test_invalid_when_approval_decision_blocks(self):
        for decision in (
            "rejected_for_memory_admission",
            "needs_more_evidence_before_memory_admission",
            "needs_rewrite_before_memory_admission",
        ):
            with self.subTest(decision=decision):
                approval = build_memory_admission_approval_record(approval_decision=decision)
                with self.assertRaises(ValueError):
                    build_memory_admission_record(memory_admission_approval=approval)

                record = build_memory_admission_record()
                record["source_memory_admission_approval"]["approval_decision"] = decision
                result = validate_memory_admission_record(record)
                self.assertFalse(result["valid"])
                self.assertIn("source_memory_admission_approval_invalid", result["error_codes"])
                self.assertIn("source_memory_admission_approval_not_approved", result["error_codes"])

    def test_invalid_when_source_design_is_missing_or_invalid(self):
        record = build_memory_admission_record()
        record.pop("source_memory_admission_package_design")
        result = validate_memory_admission_record(record)
        self.assertFalse(result["valid"])
        self.assertIn("source_memory_admission_package_design_missing", result["error_codes"])

        source = build_memory_admission_package_design()
        source["memory_write_allowed"] = True
        with self.assertRaises(ValueError):
            build_memory_admission_record(memory_admission_package_design=source)

    def test_invalid_target_form_or_layer_blocks(self):
        cases = [
            ("admission_target_form", "long_term_memory", "admission_target_form_not_expected"),
            ("admission_target_form", "core_memory", "admission_target_form_not_expected"),
            ("memory_layer_target", "long_term_memory", "memory_layer_target_not_expected"),
            ("memory_layer_target", "core_memory", "memory_layer_target_not_expected"),
        ]
        for field, value, error in cases:
            with self.subTest(field=field, value=value):
                record = build_memory_admission_record()
                record[field] = value
                result = validate_memory_admission_record(record)
                self.assertFalse(result["valid"])
                self.assertIn(error, result["error_codes"])

    def test_invalid_memory_runtime_predictor_action_and_proof_claims_block(self):
        for field in (
            "long_term_memory_write_performed",
            "retained_jsonl_write_performed",
            "runtime_influence_enabled",
            "predictor_influence_enabled",
            "predictor_mutation_allowed",
            "selected_action_allowed",
            "final_action_allowed",
            "production_behavior_change_allowed",
            "proof_of_learning_claim_allowed",
            "qingyin_self_authored_lesson_text",
            "autonomous_learning_claim_allowed",
        ):
            with self.subTest(field=field):
                record = build_memory_admission_record()
                record[field] = True
                result = validate_memory_admission_record(record)
                self.assertFalse(result["valid"])
                self.assertIn(f"{field}_not_false", result["error_codes"])

    def test_invalid_rollback_missing_or_auto_rebuild_blocks(self):
        record = build_memory_admission_record()
        record["rollback_available"] = False
        result = validate_memory_admission_record(record)
        self.assertFalse(result["valid"])
        self.assertIn("rollback_available_not_true", result["error_codes"])

        record = build_memory_admission_record()
        record["rollback_auto_rebuilds_influence"] = True
        result = validate_memory_admission_record(record)
        self.assertFalse(result["valid"])
        self.assertIn("rollback_auto_rebuilds_influence_not_false", result["error_codes"])

    def test_invalid_candidate_jsonl_runtime_predictor_and_memory_layer_blocks(self):
        for field in (
            "is_long_term_memory",
            "is_core_memory",
            "is_archive_memory",
            "writes_jsonl",
            "runtime_read_enabled",
            "predictor_read_enabled",
            "human_approved_for_memory_write",
            "human_approved_for_runtime_influence",
            "human_approved_for_predictor_influence",
        ):
            with self.subTest(field=field):
                candidate = build_reviewed_lesson_memory_candidate_record()
                candidate[field] = True
                result = validate_reviewed_lesson_memory_candidate_record(candidate)
                self.assertFalse(result["valid"])
                self.assertIn(f"{field}_not_false", result["error_codes"])

    def test_invalid_candidate_source_or_rollback_blocks(self):
        candidate = build_reviewed_lesson_memory_candidate_record()
        candidate.pop("source_memory_admission")
        result = validate_reviewed_lesson_memory_candidate_record(candidate)
        self.assertFalse(result["valid"])
        self.assertIn("source_memory_admission_missing", result["error_codes"])

        candidate = build_reviewed_lesson_memory_candidate_record()
        candidate["source_memory_admission"]["long_term_memory_write_performed"] = True
        result = validate_reviewed_lesson_memory_candidate_record(candidate)
        self.assertFalse(result["valid"])
        self.assertIn("source_memory_admission_invalid", result["error_codes"])

        candidate = build_reviewed_lesson_memory_candidate_record()
        candidate["rollback_available"] = False
        result = validate_reviewed_lesson_memory_candidate_record(candidate)
        self.assertFalse(result["valid"])
        self.assertIn("rollback_available_not_true", result["error_codes"])

    def test_summary_counts_are_deterministic(self):
        result = run_memory_admission_minimal_check()
        summary = result["summary"]
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["valid_memory_admission_count"], 1)
        self.assertGreaterEqual(summary["invalid_memory_admission_count"], 1)
        self.assertEqual(summary["valid_reviewed_lesson_memory_candidate_count"], 1)
        self.assertGreaterEqual(summary["invalid_reviewed_lesson_memory_candidate_count"], 1)
        self.assertEqual(summary["approval_checked_count"], 1)
        self.assertEqual(summary["admission_performed_count"], 1)
        self.assertEqual(summary["candidate_record_created_count"], 1)
        self.assertEqual(summary["long_term_memory_write_blocked_count"], 1)
        self.assertEqual(summary["retained_jsonl_write_blocked_count"], 1)
        self.assertEqual(summary["runtime_influence_blocked_count"], 1)
        self.assertEqual(summary["predictor_mutation_blocked_count"], 1)
        self.assertEqual(summary["proof_claim_blocked_count"], 1)
        self.assertEqual(summary["rollback_available_count"], 1)

    def test_boundary_index_updates_for_memory_admission_boundary(self):
        result = run_memory_admission_minimal_check()
        boundary = result["boundary"]
        self.assertTrue(boundary["boundary_change_required"])
        self.assertTrue(boundary["boundary_index_update_required"])
        self.assertEqual(boundary["boundary_index_version_before"], BOUNDARY_INDEX_VERSION_BEFORE)
        self.assertEqual(boundary["boundary_index_version_after"], BOUNDARY_INDEX_VERSION_AFTER)


if __name__ == "__main__":
    unittest.main()
