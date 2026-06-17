import copy
import unittest

from ashl_core.mimetic_endocrine_cost_sensitive_choice_sandbox_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_mimetic_endocrine_cost_sensitive_choice_sandbox_record,
    run_mimetic_endocrine_cost_sensitive_choice_sandbox_minimal_check,
    validate_mimetic_endocrine_cost_sensitive_choice_sandbox_record,
)
from ashl_core.teaching_cli import run_command


class MimeticEndocrineCostSensitiveChoiceSandboxMinimalTests(unittest.TestCase):
    def test_valid_cost_sensitive_choice_record_is_created(self):
        record = build_mimetic_endocrine_cost_sensitive_choice_sandbox_record()
        result = validate_mimetic_endocrine_cost_sensitive_choice_sandbox_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual(record["record_type"], "mimetic_endocrine_cost_sensitive_choice_sandbox")
        self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)

    def test_reuses_stage0_sweetness_calibration_source(self):
        record = build_mimetic_endocrine_cost_sensitive_choice_sandbox_record()
        source = record["source_calibration"]

        self.assertEqual(source["source_record_type"], "mimetic_endocrine_sweetness_preference_sandbox")
        self.assertEqual(source["source_boundary_index"], "2026-06-09-b108")
        self.assertTrue(source["source_stage0_each_candy_eaten_once"])
        self.assertTrue(source["source_valid"])

    def test_raw_sweeter_response_is_higher_but_net_tendency_is_lower(self):
        record = build_mimetic_endocrine_cost_sensitive_choice_sandbox_record()
        scenario = record["high_difficulty_choice_scenario"]
        ordinary, sweeter = scenario["choice_candidates"]

        self.assertTrue(scenario["raw_sweeter_response_higher"])
        self.assertGreater(sweeter["expected_dopamine_like_response_value"], ordinary["expected_dopamine_like_response_value"])
        self.assertTrue(scenario["difficulty_cost_applied"])
        self.assertTrue(scenario["sweeter_net_tendency_lower"])
        self.assertLess(sweeter["expected_net_tendency_score"], ordinary["expected_net_tendency_score"])

    def test_return_path_available_without_consuming_both_candies(self):
        record = build_mimetic_endocrine_cost_sensitive_choice_sandbox_record()
        policy = record["high_difficulty_choice_scenario"]["return_policy"]

        self.assertTrue(policy["return_after_probe_allowed"])
        self.assertTrue(policy["return_before_candy_consumption_only"])
        self.assertTrue(policy["return_path_available"])
        self.assertFalse(policy["return_consumes_candy"])
        self.assertFalse(policy["both_paths_can_be_consumed"])

    def test_easy_ordinary_path_is_preferred_and_sweeter_path_not_forced(self):
        record = build_mimetic_endocrine_cost_sensitive_choice_sandbox_record()
        scenario = record["high_difficulty_choice_scenario"]
        actual = scenario["actual_consumed_path"]
        summary = record["choice_result_summary"]

        self.assertEqual(scenario["preferred_path"], "left_easy_ordinary_candy")
        self.assertTrue(scenario["hard_sweeter_path_not_forced"])
        self.assertEqual(actual["path_id"], "left_easy_ordinary_candy")
        self.assertEqual(scenario["actual_consumed_path_count"], 1)
        self.assertFalse(scenario["unchosen_sweeter_path_consumed"])
        self.assertFalse(scenario["both_paths_consumed"])
        self.assertTrue(summary["ordinary_easy_path_preferred"])
        self.assertTrue(summary["hard_sweeter_path_not_forced"])

    def test_actual_response_is_valid_trace_only(self):
        record = build_mimetic_endocrine_cost_sensitive_choice_sandbox_record()
        actual = record["high_difficulty_choice_scenario"]["actual_consumed_path"]
        signal = actual["dopamine_like_signal_record"]

        self.assertEqual(signal["signal_name"], "dopamine_like")
        self.assertTrue(actual["dopamine_like_signal_valid"])
        self.assertTrue(signal["blocked_from_action_selection"])
        self.assertTrue(signal["blocked_from_memory_write"])
        self.assertTrue(signal["blocked_from_candidate_approval"])
        self.assertFalse(signal["subjective_claim"])
        self.assertFalse(signal["source_trace"]["runtime_event_applied"])
        self.assertFalse(actual["runtime_endocrine_state_persisted"])
        self.assertFalse(actual["subjective_pleasure_claim"])

    def test_context_keeps_sandbox_symbolic_numeric_not_visual(self):
        record = build_mimetic_endocrine_cost_sensitive_choice_sandbox_record()
        context = record["sandbox_context"]

        self.assertEqual(context["sandbox_scope"], "sandbox_only")
        self.assertTrue(context["fixed_choice_fixture"])
        self.assertTrue(context["uses_symbolic_numeric_fixture"])
        self.assertFalse(context["visual_detection_claimed"])
        self.assertFalse(context["free_choice_added"])
        self.assertFalse(context["pathfinding_used"])

    def test_blocked_flags_keep_boundaries_closed(self):
        record = build_mimetic_endocrine_cost_sensitive_choice_sandbox_record()
        flags = record["blocked_flags"]

        for field in (
            "visual_detection_claimed",
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

    def test_wrong_preferred_path_blocks(self):
        record = build_mimetic_endocrine_cost_sensitive_choice_sandbox_record()
        bad = copy.deepcopy(record)
        bad["high_difficulty_choice_scenario"]["preferred_path"] = "right_high_difficulty_sweeter_candy"

        result = validate_mimetic_endocrine_cost_sensitive_choice_sandbox_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("preferred_path_not_easy_ordinary", result["error_codes"])

    def test_sweeter_net_not_lower_blocks(self):
        record = build_mimetic_endocrine_cost_sensitive_choice_sandbox_record()
        bad = copy.deepcopy(record)
        bad["high_difficulty_choice_scenario"]["choice_candidates"][1]["expected_net_tendency_score"] = 0.9

        result = validate_mimetic_endocrine_cost_sensitive_choice_sandbox_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("sweeter_net_tendency_not_lower", result["error_codes"])

    def test_return_unavailable_blocks(self):
        record = build_mimetic_endocrine_cost_sensitive_choice_sandbox_record()
        bad = copy.deepcopy(record)
        bad["high_difficulty_choice_scenario"]["return_policy"]["return_path_available"] = False

        result = validate_mimetic_endocrine_cost_sensitive_choice_sandbox_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("return_policy_return_path_available_not_expected", result["error_codes"])

    def test_both_paths_consumed_blocks(self):
        record = build_mimetic_endocrine_cost_sensitive_choice_sandbox_record()
        bad = copy.deepcopy(record)
        bad["high_difficulty_choice_scenario"]["both_paths_consumed"] = True

        result = validate_mimetic_endocrine_cost_sensitive_choice_sandbox_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("both_paths_consumed", result["error_codes"])

    def test_subjective_claim_blocks(self):
        record = build_mimetic_endocrine_cost_sensitive_choice_sandbox_record()
        bad = copy.deepcopy(record)
        bad["high_difficulty_choice_scenario"]["actual_consumed_path"]["subjective_pleasure_claim"] = True

        result = validate_mimetic_endocrine_cost_sensitive_choice_sandbox_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("actual_response_subjective_pleasure_claim", result["error_codes"])

    def test_runtime_endocrine_state_blocks(self):
        record = build_mimetic_endocrine_cost_sensitive_choice_sandbox_record()
        bad = copy.deepcopy(record)
        bad["high_difficulty_choice_scenario"]["actual_consumed_path"]["runtime_endocrine_state_persisted"] = True

        result = validate_mimetic_endocrine_cost_sensitive_choice_sandbox_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("actual_response_runtime_endocrine_state_persisted", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        result = run_mimetic_endocrine_cost_sensitive_choice_sandbox_minimal_check()
        summary = result["summary"]

        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["valid_cost_sensitive_choice_sandbox_count"], 1)
        self.assertEqual(summary["invalid_cost_sensitive_choice_sandbox_count"], 39)
        self.assertEqual(summary["source_calibration_valid_count"], 1)
        self.assertEqual(summary["raw_sweeter_response_higher_count"], 1)
        self.assertEqual(summary["sweeter_net_tendency_lower_count"], 1)
        self.assertEqual(summary["ordinary_easy_path_preferred_count"], 1)
        self.assertEqual(summary["hard_sweeter_path_not_forced_count"], 1)
        self.assertEqual(summary["valid_dopamine_like_response_trace_total"], 1)
        self.assertTrue(summary["all_cost_sensitive_choice_sandbox_checks_passed"])

    def test_cli_command(self):
        result = run_command("run-mimetic-endocrine-cost-sensitive-choice-sandbox-minimal-check")

        self.assertEqual(result["command"], "run-mimetic-endocrine-cost-sensitive-choice-sandbox-minimal-check")
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
