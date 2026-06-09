import json
import subprocess
import sys
import unittest
from copy import deepcopy

from ashl_core.focus_candidate_from_change_trace import run_focus_candidate_from_change_trace_check
from ashl_core.focus_candidate_ranking_trace import (
    generate_focus_candidate_ranking_trace,
    run_focus_candidate_ranking_trace_check,
)
from ashl_core.focus_candidate_ranking_trace_schema import validate_focus_candidate_ranking_trace_record
from ashl_core.teaching_cli import run_command


class FocusCandidateRankingTraceTests(unittest.TestCase):
    def test_valid_focus_candidates_produce_valid_ranking_trace(self):
        result = run_focus_candidate_ranking_trace_check()

        self.assertEqual(result["command"], "run-focus-candidate-ranking-trace-check")
        self.assertEqual(result["flow"], "focus_candidate_ranking_trace_v0")
        self.assertEqual(result["status"], "ok")
        self.assertTrue(result["ranking_trace_validation"]["valid"], result["ranking_trace_validation"]["error_codes"])

    def test_generated_ranking_trace_passes_schema(self):
        result = run_focus_candidate_ranking_trace_check()
        validation = validate_focus_candidate_ranking_trace_record(result["ranking_trace"])

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(validation["valid_ranking_item_count"], 3)

    def test_summary_counts_are_deterministic(self):
        summary = run_focus_candidate_ranking_trace_check()["summary"]

        self.assertEqual(summary["focus_candidate_count"], 3)
        self.assertEqual(summary["valid_focus_candidate_count"], 3)
        self.assertEqual(summary["invalid_focus_candidate_count"], 0)
        self.assertEqual(summary["ranking_trace_count"], 1)
        self.assertEqual(summary["valid_ranking_trace_count"], 1)
        self.assertEqual(summary["invalid_ranking_trace_count"], 0)
        self.assertEqual(summary["ranking_item_count"], 3)
        self.assertEqual(summary["valid_ranking_item_count"], 3)
        self.assertEqual(summary["invalid_ranking_item_count"], 0)

    def test_rank_position_values_are_contiguous(self):
        ranking_items = run_focus_candidate_ranking_trace_check()["ranking_trace"]["ranking_items"]

        self.assertEqual([item["rank_position"] for item in ranking_items], [1, 2, 3])

    def test_ranking_items_preserve_score_snapshot(self):
        result = run_focus_candidate_ranking_trace_check()
        candidates_by_id = {
            candidate["focus_candidate_id"]: candidate
            for candidate in result["focus_candidates"]
        }

        for item in result["ranking_trace"]["ranking_items"]:
            self.assertEqual(
                item["score_snapshot"],
                candidates_by_id[item["focus_candidate_id"]]["score_fields"],
            )

    def test_total_score_ordering_is_trace_only(self):
        result = run_focus_candidate_ranking_trace_check()
        ranking_trace = result["ranking_trace"]
        total_scores = [item["score_snapshot"]["total_score"] for item in ranking_trace["ranking_items"]]

        self.assertEqual(total_scores, sorted(total_scores, reverse=True))
        self.assertIsNone(ranking_trace["active_focus_id"])
        self.assertFalse(ranking_trace["focus_applied"])
        self.assertFalse(ranking_trace["attention_control"])
        self.assertFalse(ranking_trace["safety_flags"]["runtime_ranking"])

    def test_active_focus_and_runtime_boundaries_remain_false(self):
        result = run_focus_candidate_ranking_trace_check()
        summary = result["summary"]

        for key in [
            "active_focus_id_non_null_count",
            "focus_applied_count",
            "attention_control_count",
            "runtime_ranking_count",
            "runtime_focus_selector_count",
            "semantic_label_non_null_count",
            "object_recognition_count",
            "object_tracking_count",
            "semantic_vision_count",
            "action_selection_influence_count",
            "memory_write_count",
            "endocrine_control_count",
            "predictor_modified_count",
        ]:
            with self.subTest(key=key):
                self.assertEqual(summary[key], 0)

    def test_lock_prevention_fields_are_present_and_safe(self):
        ranking_items = run_focus_candidate_ranking_trace_check()["ranking_trace"]["ranking_items"]

        for item in ranking_items:
            lock_prevention = item["lock_prevention"]
            self.assertEqual(lock_prevention["cooldown_state"], "not_applied")
            self.assertEqual(lock_prevention["decay_state"], "not_applied")
            self.assertTrue(lock_prevention["interruptible"])
            self.assertIsNone(lock_prevention["forced_interrupt_reason"])
            self.assertFalse(lock_prevention["attention_duration_exceeded"])
            self.assertTrue(lock_prevention["external_mentor_interrupt_allowed"])

    def test_no_focus_action_memory_or_endocrine_effects_are_created(self):
        boundary = run_focus_candidate_ranking_trace_check()["boundary_check"]

        self.assertFalse(boundary["runtime_ranking_added"])
        self.assertFalse(boundary["active_focus_selection_added"])
        self.assertFalse(boundary["focus_application_added"])
        self.assertFalse(boundary["attention_control_added"])
        self.assertFalse(boundary["action_selection_modified"])
        self.assertFalse(boundary["visual_memory_write"])
        self.assertFalse(boundary["endocrine_runtime_added"])
        self.assertFalse(boundary["predictor_modified"])

    def test_invalid_focus_candidate_blocks_valid_ranking_trace_generation(self):
        focus_candidates = deepcopy(run_focus_candidate_from_change_trace_check()["focus_candidates"])
        focus_candidates[0]["semantic_label"] = "wall"

        self.assertEqual(generate_focus_candidate_ranking_trace(focus_candidates), {})

    def test_generated_trace_with_active_focus_id_non_null_is_invalid(self):
        trace = deepcopy(run_focus_candidate_ranking_trace_check()["ranking_trace"])
        trace["active_focus_id"] = trace["ranking_items"][0]["focus_candidate_id"]

        validation = validate_focus_candidate_ranking_trace_record(trace)
        self.assertFalse(validation["valid"])
        self.assertIn("active_focus_id_non_null", validation["error_codes"])

    def test_generated_trace_runtime_flags_are_invalid(self):
        for flag, error_code in [
            ("runtime_ranking", "runtime_ranking_enabled"),
            ("runtime_focus_selector", "runtime_focus_selector_enabled"),
            ("attention_control", "attention_control_flag_enabled"),
            ("focus_applied", "focus_applied_flag_enabled"),
            ("object_tracking", "object_tracking_enabled"),
            ("semantic_vision", "semantic_vision_enabled"),
            ("action_selection_influence", "action_selection_influence_enabled"),
            ("memory_write", "memory_write_enabled"),
            ("endocrine_control", "endocrine_control_enabled"),
            ("predictor_modified", "predictor_modified_enabled"),
        ]:
            with self.subTest(flag=flag):
                trace = deepcopy(run_focus_candidate_ranking_trace_check()["ranking_trace"])
                trace["safety_flags"][flag] = True
                validation = validate_focus_candidate_ranking_trace_record(trace)
                self.assertFalse(validation["valid"])
                self.assertIn(error_code, validation["error_codes"])

    def test_generated_trace_top_level_focus_fields_are_invalid(self):
        for field, value, error_code in [
            ("focus_applied", True, "focus_applied_enabled"),
            ("attention_control", True, "attention_control_enabled"),
            ("semantic_label", "wall", "semantic_label_non_null"),
        ]:
            with self.subTest(field=field):
                trace = deepcopy(run_focus_candidate_ranking_trace_check()["ranking_trace"])
                trace[field] = value
                validation = validate_focus_candidate_ranking_trace_record(trace)
                self.assertFalse(validation["valid"])
                self.assertIn(error_code, validation["error_codes"])

    def test_generated_trace_item_errors_are_invalid(self):
        for mutate, error_code in [
            (lambda trace: trace["ranking_items"][0].__setitem__("ranking_reason_codes", ["object_importance"]), "unknown_ranking_reason_code:object_importance"),
            (lambda trace: trace["ranking_items"][0].__setitem__("rank_position", 0), "rank_position_not_positive_integer"),
            (lambda trace: trace["ranking_items"][0].pop("score_snapshot"), "missing_ranking_item_field:score_snapshot"),
            (lambda trace: trace["ranking_items"][0]["lock_prevention"].__setitem__("interruptible", False), "interruptible_not_true"),
            (
                lambda trace: trace["ranking_items"][0]["lock_prevention"].__setitem__(
                    "external_mentor_interrupt_allowed",
                    False,
                ),
                "external_mentor_interrupt_not_allowed",
            ),
        ]:
            with self.subTest(error_code=error_code):
                trace = deepcopy(run_focus_candidate_ranking_trace_check()["ranking_trace"])
                mutate(trace)
                validation = validate_focus_candidate_ranking_trace_record(trace)
                self.assertFalse(validation["valid"])
                self.assertIn(error_code, validation["error_codes"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-focus-candidate-ranking-trace-check")

        self.assertEqual(result["command"], "run-focus-candidate-ranking-trace-check")
        self.assertEqual(result["summary"]["valid_ranking_trace_count"], 1)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [sys.executable, "-m", "ashl_core.teaching_cli", "run-focus-candidate-ranking-trace-check"],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-focus-candidate-ranking-trace-check")
        self.assertEqual(result["summary"]["ranking_item_count"], 3)


if __name__ == "__main__":
    unittest.main()
