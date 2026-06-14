import unittest

from ashl_core.memory_influence_preview_minimal import (
    BOUNDARY_INDEX_VERSION_AFTER,
    BOUNDARY_INDEX_VERSION_BEFORE,
    build_memory_influence_preview_record,
    run_memory_influence_preview_minimal_check,
    validate_memory_influence_preview_record,
)
from ashl_core.memory_write_and_read_minimal import build_controlled_memory_read_record


class MemoryInfluencePreviewMinimalTests(unittest.TestCase):
    def test_valid_memory_influence_preview_from_controlled_memory_read(self):
        record = build_memory_influence_preview_record()
        result = validate_memory_influence_preview_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual("memory_influence_preview", record["record_type"])
        self.assertEqual("generated_no_runtime_effect", record["preview_status"])
        self.assertEqual("controlled_preview_only", record["preview_scope"])
        self.assertEqual("controlled_memory_read", record["preview_source"])
        self.assertEqual("check_before_retry", record["preferred_future_tendency"])
        self.assertEqual("retry_same_action_without_check", record["discouraged_future_tendency"])
        self.assertIn("check_relevant_state", record["safe_alternatives"])
        self.assertFalse(record["preview_is_runtime_influence"])
        self.assertFalse(record["preview_is_predictor_input"])
        self.assertFalse(record["preview_is_action_selection"])

    def test_invalid_when_controlled_memory_read_is_missing(self):
        record = build_memory_influence_preview_record()
        record.pop("source_controlled_memory_read")

        result = validate_memory_influence_preview_record(record)

        self.assertFalse(result["valid"])
        self.assertIn("source_controlled_memory_read_missing", result["error_codes"])

    def test_invalid_when_memory_read_failed(self):
        source = build_controlled_memory_read_record()
        source["read_status"] = "read_failed"

        with self.assertRaises(ValueError):
            build_memory_influence_preview_record(source)

        record = build_memory_influence_preview_record()
        record["source_controlled_memory_read"] = source

        self.assertIn(
            "source_controlled_memory_read_invalid",
            validate_memory_influence_preview_record(record)["error_codes"],
        )

    def test_invalid_when_retrieved_memory_text_missing(self):
        record = build_memory_influence_preview_record()
        record["retrieved_memory_text"] = ""

        result = validate_memory_influence_preview_record(record)

        self.assertFalse(result["valid"])
        self.assertIn("retrieved_memory_text_empty", result["error_codes"])

    def test_invalid_when_preview_is_runtime_influence(self):
        self.assert_false_field_blocks("preview_is_runtime_influence")

    def test_invalid_when_preview_is_predictor_input(self):
        self.assert_false_field_blocks("preview_is_predictor_input")

    def test_invalid_when_predictor_read_enabled(self):
        self.assert_false_field_blocks("predictor_read_enabled")

    def test_invalid_when_predictor_influence_enabled(self):
        self.assert_false_field_blocks("predictor_influence_enabled")

    def test_invalid_when_predictor_mutation_occurs(self):
        self.assert_false_field_blocks("predictor_mutation_performed")

    def test_invalid_when_selected_action_is_created(self):
        self.assert_false_field_blocks("selected_action_created")

    def test_invalid_when_final_action_is_created(self):
        self.assert_false_field_blocks("final_action_created")

    def test_invalid_when_direct_command_is_created(self):
        self.assert_false_field_blocks("direct_command_created")

    def test_invalid_when_production_behavior_changes(self):
        self.assert_false_field_blocks("production_behavior_changed")

    def test_invalid_when_retained_jsonl_write_is_performed(self):
        self.assert_false_field_blocks("retained_jsonl_write_performed")

    def test_invalid_when_retention_write_is_performed(self):
        self.assert_false_field_blocks("retention_write_performed")

    def test_invalid_when_proof_of_learning_is_claimed(self):
        self.assert_false_field_blocks("proof_of_learning_claim_allowed")

    def test_invalid_when_qingyin_autonomous_learning_is_claimed(self):
        self.assert_false_field_blocks("autonomous_learning_claim_allowed")

    def test_invalid_when_qingyin_autonomous_action_is_claimed(self):
        self.assert_false_field_blocks("autonomous_action_claim_allowed")

    def test_invalid_when_preferred_tendency_is_not_check_before_retry(self):
        record = build_memory_influence_preview_record()
        record["preferred_future_tendency"] = "retry_same_action"

        self.assertIn(
            "preferred_future_tendency_not_expected",
            validate_memory_influence_preview_record(record)["error_codes"],
        )

    def test_invalid_when_discouraged_tendency_is_not_retry_same_action_without_check(self):
        record = build_memory_influence_preview_record()
        record["discouraged_future_tendency"] = "check_before_retry"

        self.assertIn(
            "discouraged_future_tendency_not_expected",
            validate_memory_influence_preview_record(record)["error_codes"],
        )

    def test_invalid_when_future_runtime_boundary_is_not_required(self):
        self.assert_true_field_required("future_runtime_influence_requires_separate_boundary")

    def test_invalid_when_future_predictor_boundary_is_not_required(self):
        self.assert_true_field_required("future_predictor_influence_requires_separate_boundary")

    def test_invalid_when_future_action_selection_boundary_is_not_required(self):
        self.assert_true_field_required("future_action_selection_requires_separate_boundary")

    def test_invalid_when_future_retention_boundary_is_not_required(self):
        self.assert_true_field_required("future_retention_requires_separate_boundary")

    def test_invalid_when_rollback_unavailable(self):
        self.assert_true_field_required("rollback_available")

    def test_invalid_when_source_memory_record_enables_influence(self):
        for field in ("runtime_influence_enabled", "predictor_read_enabled", "predictor_influence_enabled", "writes_jsonl"):
            with self.subTest(field=field):
                source = build_controlled_memory_read_record()
                source["source_minimal_memory_record"][field] = True
                with self.assertRaises(ValueError):
                    build_memory_influence_preview_record(source)

                record = build_memory_influence_preview_record()
                record["source_controlled_memory_read"] = source
                self.assertIn(
                    "source_controlled_memory_read_invalid",
                    validate_memory_influence_preview_record(record)["error_codes"],
                )

    def test_demo_summary_counts_are_deterministic(self):
        result = run_memory_influence_preview_minimal_check()
        summary = result["summary"]

        self.assertEqual("ok", result["status"])
        self.assertEqual(1, summary["valid_preview_count"])
        self.assertGreaterEqual(summary["invalid_preview_count"], 1)
        self.assertEqual(1, summary["controlled_memory_read_checked_count"])
        self.assertEqual(1, summary["retrieved_memory_text_checked_count"])
        self.assertEqual(1, summary["preview_generated_count"])
        self.assertEqual(1, summary["preferred_tendency_checked_count"])
        self.assertEqual(1, summary["runtime_influence_blocked_count"])
        self.assertEqual(1, summary["predictor_read_blocked_count"])
        self.assertEqual(1, summary["predictor_mutation_blocked_count"])
        self.assertEqual(1, summary["selected_action_blocked_count"])
        self.assertEqual(1, summary["final_action_blocked_count"])
        self.assertEqual(1, summary["retained_jsonl_write_blocked_count"])
        self.assertEqual(1, summary["retention_write_blocked_count"])
        self.assertEqual(1, summary["proof_claim_blocked_count"])
        self.assertEqual(1, summary["rollback_available_count"])

    def test_boundary_index_updates_for_preview_validation_boundary(self):
        boundary = run_memory_influence_preview_minimal_check()["boundary"]

        self.assertTrue(boundary["boundary_change_required"])
        self.assertTrue(boundary["boundary_index_update_required"])
        self.assertEqual("2026-06-09-b78", BOUNDARY_INDEX_VERSION_BEFORE)
        self.assertEqual("2026-06-09-b79", BOUNDARY_INDEX_VERSION_AFTER)
        self.assertEqual("2026-06-09-b78", boundary["boundary_index_version_before"])
        self.assertEqual("2026-06-09-b79", boundary["boundary_index_version_after"])

    def assert_false_field_blocks(self, field):
        record = build_memory_influence_preview_record()
        record[field] = True

        self.assertIn(f"{field}_not_false", validate_memory_influence_preview_record(record)["error_codes"])

    def assert_true_field_required(self, field):
        record = build_memory_influence_preview_record()
        record[field] = False

        self.assertIn(f"{field}_not_true", validate_memory_influence_preview_record(record)["error_codes"])


if __name__ == "__main__":
    unittest.main()
