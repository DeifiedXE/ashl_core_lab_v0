import unittest
from copy import deepcopy

from ashl_core.sandbox_multi_cycle_action_loop_minimal import (
    BOUNDARY_INDEX_AFTER,
    BOUNDARY_INDEX_BEFORE,
    DIRECT_COMMAND,
    FINAL_ACTION,
    MAX_CYCLES,
    build_sandbox_multi_cycle_action_loop_record,
    run_sandbox_multi_cycle_action_loop_minimal_check,
    validate_sandbox_multi_cycle_action_loop_record,
)


class SandboxMultiCycleActionLoopMinimalTests(unittest.TestCase):
    def setUp(self):
        self.record = build_sandbox_multi_cycle_action_loop_record()

    def test_valid_multi_cycle_loop_is_created(self):
        result = validate_sandbox_multi_cycle_action_loop_record(self.record)
        self.assertTrue(result["valid"], result["error_codes"])
        self.assertEqual("sandbox_multi_cycle_action_loop", self.record["record_type"])
        self.assertEqual("completed_bounded_sandbox_multi_cycle_action_loop", self.record["loop_status"])
        self.assertEqual(BOUNDARY_INDEX_BEFORE, self.record["boundary_index_before"])
        self.assertEqual(BOUNDARY_INDEX_AFTER, self.record["boundary_index_after"])
        self.assertTrue(self.record["boundary_change_required"])

    def test_loop_has_two_cycles_and_stops_by_budget(self):
        result = validate_sandbox_multi_cycle_action_loop_record(self.record)
        loop_result = self.record["loop_result"]
        self.assertEqual(MAX_CYCLES, self.record["loop_config"]["max_cycles"])
        self.assertEqual(MAX_CYCLES, len(self.record["cycles"]))
        self.assertTrue(result["cycles_completed"])
        self.assertTrue(result["loop_stopped_by_budget"])
        self.assertTrue(loop_result["loop_stopped_by_budget"])
        self.assertEqual("max_cycles_reached", loop_result["stop_reason"])
        self.assertFalse(loop_result["next_cycle_execution_authorized"])

    def test_each_cycle_contains_full_sandbox_action_stack(self):
        result = validate_sandbox_multi_cycle_action_loop_record(self.record)
        self.assertEqual(MAX_CYCLES, result["selected_action_created_count"])
        self.assertEqual(MAX_CYCLES, result["final_action_created_count"])
        self.assertEqual(MAX_CYCLES, result["direct_command_created_count"])
        self.assertEqual(MAX_CYCLES, result["direct_command_executed_count"])
        self.assertEqual(MAX_CYCLES, result["outcome_evaluation_passed_count"])
        for cycle in self.record["cycles"]:
            self.assertEqual(FINAL_ACTION, cycle["selected_action"])
            self.assertEqual(FINAL_ACTION, cycle["final_action"])
            self.assertEqual(DIRECT_COMMAND, cycle["direct_command"])
            self.assertTrue(cycle["selected_action_created"])
            self.assertTrue(cycle["sandbox_action_executed"])
            self.assertTrue(cycle["final_action_created"])
            self.assertTrue(cycle["direct_command_created"])
            self.assertTrue(cycle["direct_command_executed"])
            self.assertTrue(cycle["outcome_evaluation_passed"])

    def test_second_cycle_consumes_previous_outcome_context(self):
        self.assertEqual("initial_loop_context", self.record["cycles"][0]["input_context_source"])
        self.assertTrue(self.record["cycles"][0]["next_cycle_context_created"])
        self.assertTrue(self.record["cycles"][0]["feeds_next_cycle"])
        self.assertEqual("previous_cycle_outcome", self.record["cycles"][1]["input_context_source"])
        self.assertFalse(self.record["cycles"][1]["next_cycle_context_created"])
        self.assertFalse(self.record["cycles"][1]["feeds_next_cycle"])

    def test_source_chain_is_validated(self):
        result = validate_sandbox_multi_cycle_action_loop_record(self.record)
        self.assertTrue(result["source_chain_checked"])
        for field in (
            "source_selected_action_record",
            "source_sandbox_action_execution_record",
            "source_final_action_record",
            "source_direct_command_record",
            "source_direct_command_execution_record",
            "source_outcome_evaluation_record",
        ):
            bad = deepcopy(self.record)
            bad["cycles"][0][field] = {}
            self.assertFalse(validate_sandbox_multi_cycle_action_loop_record(bad)["valid"], field)

    def test_sandbox_only_and_forbidden_boundaries_hold(self):
        result = validate_sandbox_multi_cycle_action_loop_record(self.record)
        self.assertTrue(result["sandbox_only_checked"])
        self.assertTrue(result["open_ended_loop_blocked"])
        self.assertTrue(result["next_cycle_execution_blocked"])
        self.assertTrue(result["production_behavior_blocked"])
        self.assertTrue(result["memory_write_blocked"])
        self.assertTrue(result["retention_blocked"])
        self.assertTrue(result["predictor_mutation_blocked"])
        self.assertTrue(result["endocrine_runtime_blocked"])
        self.assertTrue(result["runtime_behavior_change_blocked"])
        self.assertTrue(result["proof_claim_blocked"])

    def test_open_ended_loop_blocks(self):
        bad = deepcopy(self.record)
        bad["loop_config"]["open_ended_loop"] = True
        bad["blocked_flags"]["open_ended_loop_created"] = True
        result = validate_sandbox_multi_cycle_action_loop_record(bad)
        self.assertFalse(result["valid"])
        self.assertIn("loop_config_open_ended_loop_not_expected", result["error_codes"])
        self.assertIn("blocked_flags_open_ended_loop_created_not_false", result["error_codes"])

    def test_third_cycle_blocks(self):
        bad = deepcopy(self.record)
        bad["cycles"].append(deepcopy(self.record["cycles"][0]))
        bad["loop_result"]["cycle_count"] = 3
        result = validate_sandbox_multi_cycle_action_loop_record(bad)
        self.assertFalse(result["valid"])
        self.assertIn("cycle_count_not_expected", result["error_codes"])
        self.assertIn("loop_result_cycle_count_not_expected", result["error_codes"])

    def test_source_selected_action_invalid_blocks(self):
        bad = deepcopy(self.record)
        bad["cycles"][0]["source_selected_action_record"]["selected_action_created"] = False
        result = validate_sandbox_multi_cycle_action_loop_record(bad)
        self.assertFalse(result["valid"])
        self.assertIn("cycle_1_selected_action_source_invalid", result["error_codes"])

    def test_direct_command_execution_false_blocks(self):
        bad = deepcopy(self.record)
        bad["cycles"][0]["direct_command_executed"] = False
        result = validate_sandbox_multi_cycle_action_loop_record(bad)
        self.assertFalse(result["valid"])
        self.assertIn("cycle_1_direct_command_executed_not_expected", result["error_codes"])

    def test_outcome_evaluation_false_blocks(self):
        bad = deepcopy(self.record)
        bad["cycles"][0]["outcome_evaluation_passed"] = False
        result = validate_sandbox_multi_cycle_action_loop_record(bad)
        self.assertFalse(result["valid"])
        self.assertIn("cycle_1_outcome_evaluation_passed_not_expected", result["error_codes"])

    def test_blocked_flags_true_block(self):
        for field in self.record["blocked_flags"]:
            bad = deepcopy(self.record)
            bad["blocked_flags"][field] = True
            result = validate_sandbox_multi_cycle_action_loop_record(bad)
            self.assertFalse(result["valid"], field)
            self.assertIn(f"blocked_flags_{field}_not_false", result["error_codes"])

    def test_human_summary_fields_required(self):
        for field in self.record["human_summary"]:
            bad = deepcopy(self.record)
            bad["human_summary"][field] = ""
            result = validate_sandbox_multi_cycle_action_loop_record(bad)
            self.assertFalse(result["valid"], field)
            self.assertIn(f"human_summary_{field}_empty", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        result = run_sandbox_multi_cycle_action_loop_minimal_check()
        summary = result["summary"]
        self.assertEqual("ok", result["status"])
        self.assertEqual(1, summary["valid_multi_cycle_loop_count"])
        self.assertEqual(57, summary["invalid_multi_cycle_loop_count"])
        self.assertEqual(1, summary["source_chain_checked_count"])
        self.assertEqual(1, summary["cycles_completed_count"])
        self.assertEqual(1, summary["sandbox_only_checked_count"])
        self.assertEqual(2, summary["selected_action_created_total"])
        self.assertEqual(2, summary["final_action_created_total"])
        self.assertEqual(2, summary["direct_command_created_total"])
        self.assertEqual(2, summary["direct_command_executed_total"])
        self.assertEqual(2, summary["outcome_evaluation_passed_total"])
        self.assertEqual(1, summary["next_cycle_context_created_total"])
        self.assertEqual(1, summary["loop_stopped_by_budget_count"])
        self.assertEqual(1, summary["open_ended_loop_blocked_count"])
        self.assertEqual(1, summary["next_cycle_execution_blocked_count"])
        self.assertEqual(1, summary["production_behavior_blocked_count"])
        self.assertEqual(1, summary["memory_write_blocked_count"])
        self.assertEqual(1, summary["retention_blocked_count"])
        self.assertEqual(1, summary["predictor_mutation_blocked_count"])
        self.assertEqual(1, summary["proof_claim_blocked_count"])
        self.assertTrue(summary["all_sandbox_multi_cycle_action_loop_checks_passed"])


if __name__ == "__main__":
    unittest.main()
