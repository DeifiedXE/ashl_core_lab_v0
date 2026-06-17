import copy
import unittest

from ashl_core.mimetic_endocrine_sweetness_preference_sandbox_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_mimetic_endocrine_sweetness_preference_sandbox_record,
    run_mimetic_endocrine_sweetness_preference_sandbox_minimal_check,
    validate_mimetic_endocrine_sweetness_preference_sandbox_record,
)
from ashl_core.teaching_cli import run_command


class MimeticEndocrineSweetnessPreferenceSandboxMinimalTests(unittest.TestCase):
    def test_valid_sweetness_preference_record_is_created(self):
        record = build_mimetic_endocrine_sweetness_preference_sandbox_record()
        result = validate_mimetic_endocrine_sweetness_preference_sandbox_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual(record["record_type"], "mimetic_endocrine_sweetness_preference_sandbox")
        self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)

    def test_stage0_calibrates_both_candy_types_once(self):
        record = build_mimetic_endocrine_sweetness_preference_sandbox_record()
        stage0 = record["stage0_candy_calibration"]

        self.assertEqual(stage0["stage_id"], "stage0_candy_calibration")
        self.assertEqual(len(stage0["calibration_trials"]), 2)
        self.assertEqual(stage0["ordinary_candy_eaten_count"], 1)
        self.assertEqual(stage0["sweeter_candy_eaten_count"], 1)
        self.assertTrue(stage0["each_candy_eaten_once"])
        self.assertFalse(stage0["choice_required"])
        self.assertFalse(stage0["action_selection_applied"])

    def test_stage1_uses_candidates_but_consumes_only_chosen_sweeter_path(self):
        record = build_mimetic_endocrine_sweetness_preference_sandbox_record()
        stage1 = record["stage1_two_candy_paths"]
        left, right = stage1["choice_candidates"]
        actual = stage1["actual_consumed_path"]

        self.assertEqual(stage1["preferred_path"], "right_sweeter_candy")
        self.assertTrue(stage1["sweeter_response_higher"])
        self.assertGreater(right["sweetness"], left["sweetness"])
        self.assertGreater(right["expected_dopamine_like_response_value"], left["expected_dopamine_like_response_value"])
        self.assertEqual(actual["path_id"], "right_sweeter_candy")
        self.assertEqual(stage1["actual_consumed_path_count"], 1)
        self.assertFalse(stage1["unchosen_path_consumed"])
        self.assertFalse(stage1["return_after_choice_allowed"])
        self.assertTrue(stage1["irreversible_choice_enforced"])

    def test_stage2_sweeter_path_with_mild_obstacle_still_wins_and_consumes_one_path(self):
        record = build_mimetic_endocrine_sweetness_preference_sandbox_record()
        stage2 = record["stage2_obstacle_sweeter_path"]
        left, right = stage2["choice_candidates"]
        actual = stage2["actual_consumed_path"]

        self.assertEqual(stage2["preferred_path"], "right_mild_obstacle_sweeter_candy")
        self.assertTrue(stage2["obstacle_penalty_applied"])
        self.assertTrue(stage2["sweeter_net_tendency_still_higher"])
        self.assertGreater(right["obstacle_cost"], 0)
        self.assertGreater(right["expected_net_tendency_score"], left["expected_net_tendency_score"])
        self.assertEqual(actual["path_id"], "right_mild_obstacle_sweeter_candy")
        self.assertEqual(stage2["actual_consumed_path_count"], 1)
        self.assertFalse(stage2["unchosen_path_consumed"])
        self.assertFalse(stage2["return_after_choice_allowed"])
        self.assertTrue(stage2["irreversible_choice_enforced"])

    def test_dopamine_like_records_are_valid_response_trace_only(self):
        record = build_mimetic_endocrine_sweetness_preference_sandbox_record()
        traces = [
            *record["stage0_candy_calibration"]["calibration_trials"],
            record["stage1_two_candy_paths"]["actual_consumed_path"],
            record["stage2_obstacle_sweeter_path"]["actual_consumed_path"],
        ]

        for trace in traces:
            signal = trace["dopamine_like_signal_record"]
            self.assertEqual(signal["signal_name"], "dopamine_like")
            self.assertTrue(trace["dopamine_like_signal_valid"])
            self.assertTrue(signal["blocked_from_action_selection"])
            self.assertTrue(signal["blocked_from_memory_write"])
            self.assertTrue(signal["blocked_from_candidate_approval"])
            self.assertFalse(signal["subjective_claim"])
            self.assertFalse(signal["source_trace"]["runtime_event_applied"])
            self.assertFalse(trace["runtime_endocrine_state_persisted"])
            self.assertFalse(trace["subjective_pleasure_claim"])

    def test_choice_candidates_are_preview_only_and_not_consumed(self):
        record = build_mimetic_endocrine_sweetness_preference_sandbox_record()

        for stage_key in ("stage1_two_candy_paths", "stage2_obstacle_sweeter_path"):
            for candidate in record[stage_key]["choice_candidates"]:
                self.assertTrue(candidate["candidate_preview_only"])
                self.assertFalse(candidate["candy_consumed"])

    def test_preference_preview_records_irreversible_one_path_rule(self):
        record = build_mimetic_endocrine_sweetness_preference_sandbox_record()
        preview = record["preference_preview"]

        self.assertTrue(preview["choice_is_irreversible"])
        self.assertFalse(preview["both_paths_consumed_after_choice"])
        self.assertTrue(preview["preference_changed_by_sweetness"])
        self.assertTrue(preview["obstacle_can_be_overcome_by_sweetness_preview"])
        self.assertFalse(preview["action_selection_applied"])
        self.assertFalse(preview["free_choice_applied"])

    def test_context_blocks_free_choice_and_pathfinding(self):
        record = build_mimetic_endocrine_sweetness_preference_sandbox_record()
        context = record["sandbox_context"]

        self.assertEqual(context["sandbox_scope"], "sandbox_only")
        self.assertTrue(context["fixed_choice_fixture"])
        self.assertFalse(context["free_choice_added"])
        self.assertFalse(context["pathfinding_used"])
        self.assertFalse(context["production_behavior_changed"])

    def test_blocked_flags_keep_boundaries_closed(self):
        record = build_mimetic_endocrine_sweetness_preference_sandbox_record()
        flags = record["blocked_flags"]

        for field in (
            "free_choice_added",
            "pathfinding_used",
            "production_behavior_changed",
            "memory_write_performed",
            "retention_write_performed",
            "predictor_mutation_performed",
            "endocrine_runtime_state_persisted",
            "biological_hormone_claim_allowed",
            "subjective_pleasure_claim_allowed",
            "proof_of_learning_claim_allowed",
        ):
            self.assertFalse(flags[field])

    def test_stage0_each_candy_once_false_blocks(self):
        record = build_mimetic_endocrine_sweetness_preference_sandbox_record()
        bad = copy.deepcopy(record)
        bad["stage0_candy_calibration"]["each_candy_eaten_once"] = False

        result = validate_mimetic_endocrine_sweetness_preference_sandbox_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("stage0_each_candy_eaten_once_not_true", result["error_codes"])

    def test_stage1_unchosen_consumed_blocks(self):
        record = build_mimetic_endocrine_sweetness_preference_sandbox_record()
        bad = copy.deepcopy(record)
        bad["stage1_two_candy_paths"]["unchosen_path_consumed"] = True

        result = validate_mimetic_endocrine_sweetness_preference_sandbox_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("stage1_unchosen_path_consumed", result["error_codes"])

    def test_stage1_return_after_choice_blocks(self):
        record = build_mimetic_endocrine_sweetness_preference_sandbox_record()
        bad = copy.deepcopy(record)
        bad["stage1_two_candy_paths"]["return_after_choice_allowed"] = True

        result = validate_mimetic_endocrine_sweetness_preference_sandbox_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("stage1_return_after_choice_allowed", result["error_codes"])

    def test_stage2_two_consumed_paths_blocks(self):
        record = build_mimetic_endocrine_sweetness_preference_sandbox_record()
        bad = copy.deepcopy(record)
        bad["stage2_obstacle_sweeter_path"]["actual_consumed_path_count"] = 2

        result = validate_mimetic_endocrine_sweetness_preference_sandbox_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("stage2_actual_consumed_path_count_not_one", result["error_codes"])

    def test_stage2_sweeter_net_lower_blocks(self):
        record = build_mimetic_endocrine_sweetness_preference_sandbox_record()
        bad = copy.deepcopy(record)
        bad["stage2_obstacle_sweeter_path"]["choice_candidates"][1]["expected_net_tendency_score"] = 0.2

        result = validate_mimetic_endocrine_sweetness_preference_sandbox_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("stage2_sweeter_net_tendency_not_higher", result["error_codes"])

    def test_subjective_claim_blocks(self):
        record = build_mimetic_endocrine_sweetness_preference_sandbox_record()
        bad = copy.deepcopy(record)
        bad["stage1_two_candy_paths"]["actual_consumed_path"]["subjective_pleasure_claim"] = True

        result = validate_mimetic_endocrine_sweetness_preference_sandbox_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("stage1_actual_path_1_subjective_pleasure_claim", result["error_codes"])

    def test_runtime_endocrine_state_blocks(self):
        record = build_mimetic_endocrine_sweetness_preference_sandbox_record()
        bad = copy.deepcopy(record)
        bad["stage1_two_candy_paths"]["actual_consumed_path"]["runtime_endocrine_state_persisted"] = True

        result = validate_mimetic_endocrine_sweetness_preference_sandbox_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("stage1_actual_path_1_runtime_endocrine_state_persisted", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        result = run_mimetic_endocrine_sweetness_preference_sandbox_minimal_check()
        summary = result["summary"]

        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["valid_sweetness_preference_sandbox_count"], 1)
        self.assertEqual(summary["invalid_sweetness_preference_sandbox_count"], 51)
        self.assertEqual(summary["stage0_calibration_completed_count"], 1)
        self.assertEqual(summary["stage0_each_candy_eaten_once_count"], 1)
        self.assertEqual(summary["stage1_sweeter_response_higher_count"], 1)
        self.assertEqual(summary["stage1_irreversible_choice_enforced_count"], 1)
        self.assertEqual(summary["stage2_obstacle_penalty_applied_count"], 1)
        self.assertEqual(summary["stage2_irreversible_choice_enforced_count"], 1)
        self.assertEqual(summary["stage2_sweeter_net_tendency_still_higher_count"], 1)
        self.assertEqual(summary["valid_dopamine_like_response_trace_total"], 4)
        self.assertTrue(summary["all_sweetness_preference_sandbox_checks_passed"])

    def test_cli_command(self):
        result = run_command("run-mimetic-endocrine-sweetness-preference-sandbox-minimal-check")

        self.assertEqual(result["command"], "run-mimetic-endocrine-sweetness-preference-sandbox-minimal-check")
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
