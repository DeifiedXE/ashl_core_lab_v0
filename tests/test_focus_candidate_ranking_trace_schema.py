import json
import subprocess
import sys
import unittest
from copy import deepcopy

from ashl_core.focus_candidate_ranking_trace_schema import (
    build_valid_focus_candidate_ranking_trace_record,
    run_focus_candidate_ranking_trace_schema_check,
    validate_focus_candidate_ranking_trace_record,
)
from ashl_core.teaching_cli import run_command


class FocusCandidateRankingTraceSchemaTests(unittest.TestCase):
    def test_valid_ranking_trace_passes(self):
        record = build_valid_focus_candidate_ranking_trace_record()
        validation = validate_focus_candidate_ranking_trace_record(record)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertTrue(validation["active_focus_is_null"])
        self.assertFalse(validation["focus_applied"])
        self.assertFalse(validation["attention_control"])

    def test_rank_position_must_be_positive(self):
        record = build_valid_focus_candidate_ranking_trace_record()
        record["ranking_items"][0]["rank_position"] = 0

        validation = validate_focus_candidate_ranking_trace_record(record)
        self.assertFalse(validation["valid"])
        self.assertIn("rank_position_not_positive_integer", validation["error_codes"])

    def test_rank_position_values_must_be_unique(self):
        record = build_valid_focus_candidate_ranking_trace_record()
        record["ranking_items"][1]["rank_position"] = 1

        validation = validate_focus_candidate_ranking_trace_record(record)
        self.assertFalse(validation["valid"])
        self.assertIn("rank_position_not_unique", validation["error_codes"])

    def test_rank_position_values_must_be_contiguous(self):
        record = build_valid_focus_candidate_ranking_trace_record()
        record["ranking_items"][2]["rank_position"] = 4

        validation = validate_focus_candidate_ranking_trace_record(record)
        self.assertFalse(validation["valid"])
        self.assertIn("rank_position_not_contiguous", validation["error_codes"])

    def test_ranked_candidate_count_mismatch_blocks_trace(self):
        record = build_valid_focus_candidate_ranking_trace_record()
        record["ranked_candidate_count"] = 2

        validation = validate_focus_candidate_ranking_trace_record(record)
        self.assertFalse(validation["valid"])
        self.assertIn("ranked_candidate_count_mismatch", validation["error_codes"])

    def test_score_snapshot_missing_blocks_trace(self):
        record = build_valid_focus_candidate_ranking_trace_record()
        record["ranking_items"][0]["score_snapshot"].pop("total_score")

        validation = validate_focus_candidate_ranking_trace_record(record)
        self.assertFalse(validation["valid"])
        self.assertIn("missing_score_snapshot_field:total_score", validation["error_codes"])

    def test_score_snapshot_non_numeric_blocks_trace(self):
        record = build_valid_focus_candidate_ranking_trace_record()
        record["ranking_items"][0]["score_snapshot"]["change_salience"] = "high"

        validation = validate_focus_candidate_ranking_trace_record(record)
        self.assertFalse(validation["valid"])
        self.assertIn("score_snapshot_field_not_numeric:change_salience", validation["error_codes"])

    def test_score_snapshot_out_of_range_blocks_trace(self):
        record = build_valid_focus_candidate_ranking_trace_record()
        record["ranking_items"][0]["score_snapshot"]["contrast_salience"] = 2.0

        validation = validate_focus_candidate_ranking_trace_record(record)
        self.assertFalse(validation["valid"])
        self.assertIn("score_snapshot_field_out_of_range:contrast_salience", validation["error_codes"])

    def test_unknown_ranking_reason_code_blocks_trace(self):
        record = build_valid_focus_candidate_ranking_trace_record()
        record["ranking_items"][0]["ranking_reason_codes"] = ["object_importance"]

        validation = validate_focus_candidate_ranking_trace_record(record)
        self.assertFalse(validation["valid"])
        self.assertIn("unknown_ranking_reason_code:object_importance", validation["error_codes"])

    def test_tie_breaker_missing_blocks_trace(self):
        record = build_valid_focus_candidate_ranking_trace_record()
        record["ranking_items"][0].pop("tie_breaker")

        validation = validate_focus_candidate_ranking_trace_record(record)
        self.assertFalse(validation["valid"])
        self.assertIn("missing_ranking_item_field:tie_breaker", validation["error_codes"])
        self.assertIn("tie_breaker_not_dict", validation["error_codes"])

    def test_tie_breaker_used_true_requires_method_and_reason(self):
        record = build_valid_focus_candidate_ranking_trace_record()
        record["ranking_items"][0]["tie_breaker"] = {"used": True, "method": None, "reason": None}

        validation = validate_focus_candidate_ranking_trace_record(record)
        self.assertFalse(validation["valid"])
        self.assertIn("tie_breaker_method_required", validation["error_codes"])
        self.assertIn("tie_breaker_reason_required", validation["error_codes"])

    def test_unknown_tie_breaker_method_blocks_trace(self):
        record = build_valid_focus_candidate_ranking_trace_record()
        record["ranking_items"][0]["tie_breaker"] = {
            "used": True,
            "method": "object_importance",
            "reason": "demo",
        }

        validation = validate_focus_candidate_ranking_trace_record(record)
        self.assertFalse(validation["valid"])
        self.assertIn("unknown_tie_breaker_method", validation["error_codes"])

    def test_lock_prevention_missing_blocks_trace(self):
        record = build_valid_focus_candidate_ranking_trace_record()
        record["ranking_items"][0].pop("lock_prevention")

        validation = validate_focus_candidate_ranking_trace_record(record)
        self.assertFalse(validation["valid"])
        self.assertIn("missing_ranking_item_field:lock_prevention", validation["error_codes"])
        self.assertIn("lock_prevention_not_dict", validation["error_codes"])

    def test_lock_prevention_runtime_like_values_block_trace(self):
        for field, value, error_code in [
            ("interruptible", False, "interruptible_not_true"),
            ("external_mentor_interrupt_allowed", False, "external_mentor_interrupt_not_allowed"),
            ("attention_duration_exceeded", True, "attention_duration_exceeded_enabled"),
        ]:
            with self.subTest(field=field):
                record = build_valid_focus_candidate_ranking_trace_record()
                record["ranking_items"][0]["lock_prevention"][field] = value
                validation = validate_focus_candidate_ranking_trace_record(record)
                self.assertFalse(validation["valid"])
                self.assertIn(error_code, validation["error_codes"])

    def test_active_focus_focus_attention_and_semantic_fields_block_trace(self):
        for field, value, error_code in [
            ("active_focus_id", "focus_candidate_from_change_trace:001", "active_focus_id_non_null"),
            ("focus_applied", True, "focus_applied_enabled"),
            ("attention_control", True, "attention_control_enabled"),
            ("semantic_label", "wall", "semantic_label_non_null"),
        ]:
            with self.subTest(field=field):
                record = build_valid_focus_candidate_ranking_trace_record()
                record[field] = value
                validation = validate_focus_candidate_ranking_trace_record(record)
                self.assertFalse(validation["valid"])
                self.assertIn(error_code, validation["error_codes"])

    def test_runtime_semantic_and_tracking_flags_block_trace(self):
        for flag, error_code in [
            ("runtime_ranking", "runtime_ranking_enabled"),
            ("runtime_focus_selector", "runtime_focus_selector_enabled"),
            ("attention_control", "attention_control_flag_enabled"),
            ("focus_applied", "focus_applied_flag_enabled"),
            ("object_recognition", "object_recognition_enabled"),
            ("object_tracking", "object_tracking_enabled"),
            ("semantic_vision", "semantic_vision_enabled"),
        ]:
            with self.subTest(flag=flag):
                record = build_valid_focus_candidate_ranking_trace_record()
                record["safety_flags"][flag] = True
                validation = validate_focus_candidate_ranking_trace_record(record)
                self.assertFalse(validation["valid"])
                self.assertIn(error_code, validation["error_codes"])

    def test_influence_and_write_flags_block_trace(self):
        for flag, error_code in [
            ("action_selection_influence", "action_selection_influence_enabled"),
            ("memory_write", "memory_write_enabled"),
            ("endocrine_control", "endocrine_control_enabled"),
            ("predictor_modified", "predictor_modified_enabled"),
        ]:
            with self.subTest(flag=flag):
                record = build_valid_focus_candidate_ranking_trace_record()
                record["safety_flags"][flag] = 1
                validation = validate_focus_candidate_ranking_trace_record(record)
                self.assertFalse(validation["valid"])
                self.assertIn(error_code, validation["error_codes"])

    def test_downstream_unblocked_flags_block_trace(self):
        for flag, error_code in [
            ("blocked_from_action_selection", "action_selection_not_blocked"),
            ("blocked_from_memory_write", "memory_write_not_blocked"),
            ("blocked_from_endocrine_control", "endocrine_control_not_blocked"),
        ]:
            with self.subTest(flag=flag):
                record = build_valid_focus_candidate_ranking_trace_record()
                record["safety_flags"][flag] = False
                validation = validate_focus_candidate_ranking_trace_record(record)
                self.assertFalse(validation["valid"])
                self.assertIn(error_code, validation["error_codes"])

    def test_demo_check_summary_has_expected_counts(self):
        result = run_focus_candidate_ranking_trace_schema_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-focus-candidate-ranking-trace-schema-check")
        self.assertEqual(result["flow"], "focus_candidate_ranking_trace_schema_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["ranking_trace_count"], 7)
        self.assertEqual(summary["valid_ranking_trace_count"], 1)
        self.assertEqual(summary["invalid_ranking_trace_count"], 6)
        self.assertEqual(summary["ranking_item_count"], 3)
        self.assertEqual(summary["valid_ranking_item_count"], 3)
        self.assertEqual(summary["invalid_ranking_item_count"], 0)
        self.assertGreaterEqual(summary["active_focus_non_null_blocked_count"], 1)
        self.assertGreaterEqual(summary["focus_applied_blocked_count"], 1)
        self.assertGreaterEqual(summary["attention_control_blocked_count"], 1)
        self.assertGreaterEqual(summary["semantic_label_non_null_blocked_count"], 1)
        self.assertGreaterEqual(summary["unknown_ranking_reason_code_blocked_count"], 1)
        self.assertGreaterEqual(summary["runtime_ranking_blocked_count"], 1)
        self.assertEqual(summary["runtime_focus_selector_count"], 0)
        self.assertEqual(summary["object_recognition_count"], 0)
        self.assertEqual(summary["object_tracking_count"], 0)
        self.assertEqual(summary["semantic_vision_count"], 0)
        self.assertEqual(summary["action_selection_influence_count"], 0)
        self.assertEqual(summary["memory_write_count"], 0)
        self.assertEqual(summary["endocrine_control_count"], 0)
        self.assertEqual(summary["predictor_modified_count"], 0)
        self.assertTrue(boundary["schema_check_only"])
        self.assertTrue(boundary["total_score_is_reference_not_winner_condition"])
        self.assertFalse(boundary["runtime_ranking_added"])
        self.assertFalse(boundary["active_focus_selection_added"])
        self.assertFalse(boundary["attention_control_added"])
        self.assertFalse(boundary["action_selection_modified"])
        self.assertFalse(boundary["visual_memory_write"])

    def test_run_command_dispatches_schema_check(self):
        result = run_command("run-focus-candidate-ranking-trace-schema-check")

        self.assertEqual(result["command"], "run-focus-candidate-ranking-trace-schema-check")
        self.assertEqual(result["summary"]["valid_ranking_trace_count"], 1)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [sys.executable, "-m", "ashl_core.teaching_cli", "run-focus-candidate-ranking-trace-schema-check"],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-focus-candidate-ranking-trace-schema-check")
        self.assertEqual(result["summary"]["runtime_ranking_blocked_count"], 1)


if __name__ == "__main__":
    unittest.main()
