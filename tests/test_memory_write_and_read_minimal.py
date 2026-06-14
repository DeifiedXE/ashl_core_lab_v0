import unittest
from copy import deepcopy

from ashl_core.memory_admission_minimal import (
    build_memory_admission_record,
    build_reviewed_lesson_memory_candidate_record,
)
from ashl_core.memory_write_and_read_minimal import (
    BOUNDARY_INDEX_VERSION_AFTER,
    BOUNDARY_INDEX_VERSION_BEFORE,
    build_controlled_memory_read_record,
    build_minimal_memory_write_record,
    build_minimal_reviewed_lesson_memory_record,
    run_memory_write_and_read_minimal_check,
    validate_controlled_memory_read_record,
    validate_minimal_memory_write_record,
    validate_minimal_reviewed_lesson_memory_record,
)
from ashl_core.memory_write_approval_boundary_minimal import (
    build_memory_write_approval_record,
)


class MemoryWriteAndReadMinimalTests(unittest.TestCase):
    def test_valid_memory_write_record(self):
        record = build_minimal_memory_write_record()
        result = validate_minimal_memory_write_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual("memory_write", record["record_type"])
        self.assertTrue(record["memory_write_performed"])
        self.assertTrue(record["minimal_memory_read_enabled"])
        self.assertTrue(record["controlled_memory_read_path_enabled"])
        self.assertFalse(record["retained_jsonl_write_performed"])
        self.assertFalse(record["runtime_influence_enabled"])
        self.assertFalse(record["predictor_read_enabled"])
        self.assertFalse(record["selected_action_allowed"])
        self.assertEqual(
            "invalidate_minimal_memory_record_and_block_controlled_read",
            record["rollback_action"],
        )

    def test_valid_minimal_reviewed_lesson_memory_record(self):
        record = build_minimal_reviewed_lesson_memory_record()
        result = validate_minimal_reviewed_lesson_memory_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual("minimal_reviewed_lesson_memory_record", record["record_type"])
        self.assertEqual("written_and_readable_by_controlled_memory_read_path", record["memory_status"])
        self.assertTrue(record["controlled_memory_read_enabled"])
        self.assertTrue(record["human_approved_for_memory_write"])
        self.assertTrue(record["human_approved_for_controlled_memory_read"])
        self.assertFalse(record["writes_jsonl"])
        self.assertFalse(record["runtime_influence_enabled"])
        self.assertFalse(record["predictor_read_enabled"])

    def test_valid_controlled_memory_read_record(self):
        record = build_controlled_memory_read_record()
        result = validate_controlled_memory_read_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual("controlled_memory_read", record["record_type"])
        self.assertEqual("read_successful", record["read_status"])
        self.assertEqual("controlled_memory_read_path_only", record["read_scope"])
        self.assertTrue(record["read_visible_to_qingyin_controlled_path"])
        self.assertIn("do not retry the same action immediately", record["retrieved_memory_text"])
        self.assertFalse(record["read_is_runtime_influence"])
        self.assertFalse(record["read_is_predictor_input"])
        self.assertFalse(record["read_is_action_selection_input"])
        self.assertFalse(record["selected_action_created"])
        self.assertFalse(record["final_action_created"])

    def test_invalid_when_memory_write_approval_is_missing(self):
        record = build_minimal_memory_write_record()
        record.pop("source_memory_write_approval")

        result = validate_minimal_memory_write_record(record)

        self.assertFalse(result["valid"])
        self.assertIn("source_memory_write_approval_missing", result["error_codes"])

    def test_invalid_when_approval_decision_is_blocked(self):
        for decision in (
            "rejected_for_memory_write",
            "needs_more_evidence_before_memory_write",
            "needs_retention_rule_before_memory_write",
            "needs_rollback_rule_before_memory_write",
            "needs_rewrite_before_memory_write",
        ):
            with self.subTest(decision=decision):
                admission = build_memory_admission_record()
                candidate = build_reviewed_lesson_memory_candidate_record(admission)
                approval = build_memory_write_approval_record(admission, candidate, approval_decision=decision)
                with self.assertRaises(ValueError):
                    build_minimal_memory_write_record(admission, candidate, approval)

                record = build_minimal_memory_write_record()
                record["source_memory_write_approval"] = approval
                record["source_approval_decision"] = decision
                result = validate_minimal_memory_write_record(record)
                self.assertFalse(result["valid"])
                self.assertIn("source_approval_decision_not_expected", result["error_codes"])
                self.assertIn("source_memory_write_approval_not_approved", result["error_codes"])

    def test_invalid_when_memory_admission_source_missing(self):
        with self.assertRaises(ValueError):
            build_minimal_memory_write_record(memory_admission={})

        record = build_minimal_memory_write_record()
        record.pop("source_memory_admission")

        self.assertIn(
            "source_memory_admission_missing",
            validate_minimal_memory_write_record(record)["error_codes"],
        )

    def test_invalid_when_reviewed_lesson_memory_candidate_source_missing(self):
        admission = build_memory_admission_record()
        with self.assertRaises(ValueError):
            build_minimal_memory_write_record(admission, reviewed_lesson_memory_candidate={})

        record = build_minimal_memory_write_record()
        record.pop("source_reviewed_lesson_memory_candidate")

        self.assertIn(
            "source_reviewed_lesson_memory_candidate_missing",
            validate_minimal_memory_write_record(record)["error_codes"],
        )

    def test_invalid_memory_write_target_boundaries(self):
        cases = {
            "core_memory": "memory_record_layer_not_expected",
            "archive_memory": "memory_record_layer_not_expected",
            "production_long_term_memory_runtime": "memory_record_layer_not_expected",
        }
        for value, error in cases.items():
            with self.subTest(value=value):
                record = build_minimal_memory_write_record()
                record["memory_record_layer"] = value

                self.assertIn(error, validate_minimal_memory_write_record(record)["error_codes"])

    def test_invalid_when_retained_jsonl_or_retention_write_is_performed(self):
        for field in ("retained_jsonl_write_performed", "retention_write_performed"):
            with self.subTest(field=field):
                record = build_minimal_memory_write_record()
                record[field] = True

                self.assertIn(f"{field}_not_false", validate_minimal_memory_write_record(record)["error_codes"])

    def test_invalid_when_controlled_memory_read_disabled_after_write(self):
        write = build_minimal_memory_write_record()
        write["controlled_memory_read_path_enabled"] = False

        self.assertIn(
            "controlled_memory_read_path_enabled_not_true",
            validate_minimal_memory_write_record(write)["error_codes"],
        )

        memory_record = build_minimal_reviewed_lesson_memory_record()
        memory_record["controlled_memory_read_enabled"] = False

        self.assertIn(
            "controlled_memory_read_enabled_not_true",
            validate_minimal_reviewed_lesson_memory_record(memory_record)["error_codes"],
        )

    def test_invalid_when_controlled_read_becomes_runtime_predictor_or_action_input(self):
        for field in (
            "read_is_runtime_influence",
            "read_is_predictor_input",
            "read_is_action_selection_input",
            "runtime_influence_enabled",
            "predictor_influence_enabled",
        ):
            with self.subTest(field=field):
                read = build_controlled_memory_read_record()
                read[field] = True

                self.assertIn(f"{field}_not_false", validate_controlled_memory_read_record(read)["error_codes"])

    def test_invalid_when_runtime_or_predictor_mutation_is_enabled(self):
        for validator, builder, field in (
            (validate_minimal_memory_write_record, build_minimal_memory_write_record, "runtime_influence_enabled"),
            (validate_minimal_memory_write_record, build_minimal_memory_write_record, "predictor_mutation_performed"),
            (validate_controlled_memory_read_record, build_controlled_memory_read_record, "runtime_influence_enabled"),
            (validate_controlled_memory_read_record, build_controlled_memory_read_record, "predictor_mutation_performed"),
        ):
            with self.subTest(field=field, validator=validator.__name__):
                record = builder()
                record[field] = True

                self.assertIn(f"{field}_not_false", validator(record)["error_codes"])

    def test_invalid_when_selected_action_or_final_action_is_created(self):
        for field in ("selected_action_created", "final_action_created"):
            with self.subTest(field=field):
                read = build_controlled_memory_read_record()
                read[field] = True

                self.assertIn(f"{field}_not_false", validate_controlled_memory_read_record(read)["error_codes"])

        for field in ("selected_action_allowed", "final_action_allowed"):
            with self.subTest(field=field):
                write = build_minimal_memory_write_record()
                write[field] = True

                self.assertIn(f"{field}_not_false", validate_minimal_memory_write_record(write)["error_codes"])

    def test_invalid_when_production_or_proof_is_claimed(self):
        for field in ("production_behavior_change_allowed", "proof_of_learning_claim_allowed"):
            with self.subTest(field=field):
                write = build_minimal_memory_write_record()
                write[field] = True

                self.assertIn(f"{field}_not_false", validate_minimal_memory_write_record(write)["error_codes"])

        read = build_controlled_memory_read_record()
        read["production_behavior_changed"] = True
        self.assertIn("production_behavior_changed_not_false", validate_controlled_memory_read_record(read)["error_codes"])

    def test_invalid_when_qingyin_self_authorship_or_autonomy_is_claimed(self):
        for field in (
            "qingyin_self_authored_text",
            "autonomous_learning_claim_allowed",
            "autonomous_action_claim_allowed",
        ):
            with self.subTest(field=field):
                write = build_minimal_memory_write_record()
                write[field] = True

                self.assertIn(f"{field}_not_false", validate_minimal_memory_write_record(write)["error_codes"])

    def test_invalid_when_rollback_missing_or_does_not_block_read(self):
        write = build_minimal_memory_write_record()
        write["rollback_available"] = False
        self.assertIn("rollback_available_not_true", validate_minimal_memory_write_record(write)["error_codes"])

        write = build_minimal_memory_write_record()
        write["rollback_action"] = "invalidate_record_only"
        self.assertIn("rollback_action_not_expected", validate_minimal_memory_write_record(write)["error_codes"])

        read = build_controlled_memory_read_record()
        read["rollback_available"] = False
        self.assertIn("rollback_available_not_true", validate_controlled_memory_read_record(read)["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        result = run_memory_write_and_read_minimal_check()
        summary = result["summary"]

        self.assertEqual("ok", result["status"])
        self.assertEqual(1, summary["valid_memory_write_count"])
        self.assertGreaterEqual(summary["invalid_memory_write_count"], 1)
        self.assertEqual(1, summary["valid_minimal_memory_record_count"])
        self.assertGreaterEqual(summary["invalid_minimal_memory_record_count"], 1)
        self.assertEqual(1, summary["valid_controlled_memory_read_count"])
        self.assertGreaterEqual(summary["invalid_controlled_memory_read_count"], 1)
        self.assertEqual(1, summary["approval_checked_count"])
        self.assertEqual(1, summary["memory_write_performed_count"])
        self.assertEqual(1, summary["controlled_memory_read_performed_count"])
        self.assertEqual(1, summary["retrieved_memory_text_visible_count"])
        self.assertEqual(3, summary["retained_jsonl_write_blocked_count"])
        self.assertEqual(3, summary["runtime_influence_blocked_count"])
        self.assertEqual(3, summary["predictor_read_blocked_count"])
        self.assertEqual(3, summary["predictor_mutation_blocked_count"])

    def test_boundary_index_updates_for_memory_write_and_read(self):
        boundary = run_memory_write_and_read_minimal_check()["boundary"]

        self.assertTrue(boundary["boundary_change_required"])
        self.assertTrue(boundary["boundary_index_update_required"])
        self.assertEqual("2026-06-09-b77", BOUNDARY_INDEX_VERSION_BEFORE)
        self.assertEqual("2026-06-09-b78", BOUNDARY_INDEX_VERSION_AFTER)
        self.assertEqual("2026-06-09-b77", boundary["boundary_index_version_before"])
        self.assertEqual("2026-06-09-b78", boundary["boundary_index_version_after"])


if __name__ == "__main__":
    unittest.main()
