import copy
import unittest

from ashl_core.sandbox_body_motor_command_execution_loop_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_sandbox_body_motor_command_execution_loop_record,
    run_sandbox_body_motor_command_execution_loop_minimal_check,
    validate_sandbox_body_motor_command_execution_loop_record,
)
from ashl_core.sandbox_body_motor_final_action_minimal import (
    run_sandbox_body_motor_final_action_minimal_check,
)
from ashl_core.teaching_cli import run_command


class SandboxBodyMotorCommandExecutionLoopMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_sandbox_body_motor_final_action_minimal_check()["valid_records"]

    def test_valid_command_execution_loop_record_is_created(self):
        record = build_sandbox_body_motor_command_execution_loop_record(self.sources[0])
        result = validate_sandbox_body_motor_command_execution_loop_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual(record["record_type"], "sandbox_body_motor_command_execution_loop_minimal")
        self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)

    def test_step_forward_final_action_creates_command_execution_and_outcome(self):
        record = build_sandbox_body_motor_command_execution_loop_record(self.sources[0])

        self.assertEqual(record["direct_command_result"]["direct_command"], "sandbox.body.step_forward")
        self.assertTrue(record["direct_command_result"]["direct_command_created"])
        self.assertTrue(record["motor_execution_result"]["motor_action_executed"])
        self.assertEqual(record["motor_execution_result"]["execution_result"], "moved_forward_one_cell")
        self.assertTrue(record["outcome_observation"]["outcome_observed"])
        self.assertTrue(record["outcome_observation"]["movement_observed"])
        self.assertFalse(record["outcome_observation"]["reach_observed"])

    def test_reach_front_final_action_creates_command_execution_and_outcome(self):
        record = build_sandbox_body_motor_command_execution_loop_record(self.sources[2])

        self.assertEqual(record["direct_command_result"]["direct_command"], "sandbox.body.reach_front")
        self.assertTrue(record["direct_command_result"]["direct_command_created"])
        self.assertTrue(record["motor_execution_result"]["motor_action_executed"])
        self.assertEqual(record["motor_execution_result"]["execution_result"], "front_item_reached")
        self.assertTrue(record["outcome_observation"]["outcome_observed"])
        self.assertFalse(record["outcome_observation"]["movement_observed"])
        self.assertTrue(record["outcome_observation"]["reach_observed"])

    def test_wall_case_blocks_command_execution_and_outcome(self):
        record = build_sandbox_body_motor_command_execution_loop_record(self.sources[1])

        self.assertFalse(record["direct_command_result"]["direct_command_created"])
        self.assertIsNone(record["direct_command_result"]["direct_command"])
        self.assertEqual(record["direct_command_result"]["blocked_reason"], "final_action_not_available_for_command")
        self.assertFalse(record["motor_execution_result"]["motor_action_executed"])
        self.assertFalse(record["outcome_observation"]["outcome_observed"])

    def test_execution_is_once_and_sandbox_only(self):
        record = build_sandbox_body_motor_command_execution_loop_record(self.sources[0])
        execution = record["motor_execution_result"]

        self.assertEqual(execution["execution_scope"], "sandbox_only")
        self.assertEqual(execution["execution_count"], 1)
        self.assertEqual(execution["execution_budget"], 1)
        self.assertEqual(execution["budget_remaining"], 0)
        self.assertTrue(execution["stop_condition_met"])

    def test_wrong_direct_command_blocks(self):
        record = build_sandbox_body_motor_command_execution_loop_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["direct_command_result"]["direct_command"] = "sandbox.body.jump"

        result = validate_sandbox_body_motor_command_execution_loop_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("direct_command_result_direct_command_not_expected", result["error_codes"])

    def test_command_not_created_blocks(self):
        record = build_sandbox_body_motor_command_execution_loop_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["direct_command_result"]["direct_command_created"] = False

        result = validate_sandbox_body_motor_command_execution_loop_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("direct_command_result_direct_command_created_not_expected", result["error_codes"])

    def test_motor_not_executed_blocks(self):
        record = build_sandbox_body_motor_command_execution_loop_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["motor_execution_result"]["motor_action_executed"] = False

        result = validate_sandbox_body_motor_command_execution_loop_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("motor_execution_result_motor_action_executed_not_expected", result["error_codes"])

    def test_wrong_execution_result_blocks(self):
        record = build_sandbox_body_motor_command_execution_loop_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["motor_execution_result"]["execution_result"] = "wrong"

        result = validate_sandbox_body_motor_command_execution_loop_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("motor_execution_result_execution_result_not_expected", result["error_codes"])

    def test_outcome_mismatch_blocks(self):
        record = build_sandbox_body_motor_command_execution_loop_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["outcome_observation"]["outcome_match"] = False

        result = validate_sandbox_body_motor_command_execution_loop_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("outcome_observation_outcome_match_not_expected", result["error_codes"])

    def test_production_behavior_blocks(self):
        record = build_sandbox_body_motor_command_execution_loop_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["motor_execution_result"]["production_behavior_changed"] = True

        result = validate_sandbox_body_motor_command_execution_loop_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("motor_execution_result_production_behavior_changed_not_expected", result["error_codes"])

    def test_memory_write_blocks(self):
        record = build_sandbox_body_motor_command_execution_loop_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["outcome_observation"]["memory_write_performed"] = True

        result = validate_sandbox_body_motor_command_execution_loop_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("outcome_observation_memory_write_performed_not_expected", result["error_codes"])

    def test_predictor_mutation_blocks(self):
        record = build_sandbox_body_motor_command_execution_loop_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["outcome_observation"]["predictor_mutation_performed"] = True

        result = validate_sandbox_body_motor_command_execution_loop_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("outcome_observation_predictor_mutation_performed_not_expected", result["error_codes"])

    def test_blocked_flags_true_block(self):
        record = build_sandbox_body_motor_command_execution_loop_record(self.sources[0])
        bad = copy.deepcopy(record)
        bad["blocked_flags"]["pathfinding_used"] = True

        result = validate_sandbox_body_motor_command_execution_loop_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("blocked_flags_pathfinding_used_not_false", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        result = run_sandbox_body_motor_command_execution_loop_minimal_check()
        summary = result["summary"]

        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["command_execution_loop_result_count"], 31)
        self.assertEqual(summary["valid_command_execution_loop_count"], 3)
        self.assertEqual(summary["invalid_command_execution_loop_count"], 28)
        self.assertEqual(summary["direct_command_created_count"], 2)
        self.assertEqual(summary["direct_command_blocked_count"], 1)
        self.assertEqual(summary["motor_action_executed_count"], 2)
        self.assertEqual(summary["outcome_observed_count"], 2)
        self.assertEqual(summary["movement_observed_count"], 1)
        self.assertEqual(summary["reach_observed_count"], 1)

    def test_cli_command(self):
        result = run_command("run-sandbox-body-motor-command-execution-loop-minimal-check")

        self.assertEqual(result["command"], "run-sandbox-body-motor-command-execution-loop-minimal-check")
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
