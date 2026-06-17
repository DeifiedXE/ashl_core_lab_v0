import copy
import unittest

from ashl_core.teaching_cli import run_command
from ashl_core.time_paced_locomotion_action_completion_minimal import (
    BOUNDARY_INDEX_AFTER,
    MAX_ACTION_STEPS,
    build_time_paced_locomotion_action_completion_record,
    run_time_paced_locomotion_action_completion_minimal_check,
    validate_time_paced_locomotion_action_completion_record,
)


class TimePacedLocomotionActionCompletionMinimalTests(unittest.TestCase):
    def test_valid_completion_is_created(self):
        record = build_time_paced_locomotion_action_completion_record()
        result = validate_time_paced_locomotion_action_completion_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual(record["record_type"], "time_paced_locomotion_action_completion")
        self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)

    def test_source_temporal_loop_is_checked(self):
        record = build_time_paced_locomotion_action_completion_record()
        source = record["source_temporal_loop"]

        self.assertTrue(source["source_validated"])
        self.assertEqual(source["source_boundary_index"], "2026-06-09-b106")
        self.assertEqual(source["source_active_step_count"], 6)
        self.assertEqual(source["source_idle_tick_total"], 12)

    def test_each_active_step_has_complete_action_line(self):
        record = build_time_paced_locomotion_action_completion_record()

        self.assertEqual(len(record["action_lines"]), MAX_ACTION_STEPS)
        for line in record["action_lines"]:
            self.assertTrue(line["selected_action"]["selected_action_created"])
            self.assertTrue(line["final_action"]["final_action_created"])
            self.assertTrue(line["direct_command"]["direct_command_created"])
            self.assertTrue(line["execution"]["direct_command_executed"])
            self.assertTrue(line["outcome_evaluation"]["outcome_evaluation_created"])
            self.assertEqual(line["outcome_evaluation"]["evaluation_result"], "passed")

    def test_locomotion_direct_commands_are_sandbox_only(self):
        record = build_time_paced_locomotion_action_completion_record()

        commands = [line["direct_command"]["direct_command"] for line in record["action_lines"]]
        self.assertEqual(commands, [
            "sandbox.move_forward",
            "sandbox.move_forward",
            "sandbox.turn_right",
            "sandbox.turn_right",
            "sandbox.move_forward",
            "sandbox.move_forward",
        ])
        for line in record["action_lines"]:
            self.assertEqual(line["direct_command"]["direct_command_scope"], "sandbox_only")
            self.assertEqual(line["execution"]["execution_scope"], "sandbox_only")

    def test_cooldown_is_preserved_from_temporal_loop(self):
        record = build_time_paced_locomotion_action_completion_record()

        for line in record["action_lines"]:
            self.assertTrue(line["cooldown_satisfied"])
            self.assertEqual(line["source_idle_ticks_before_action"], 2)

    def test_candy_contact_action_line_is_preserved(self):
        record = build_time_paced_locomotion_action_completion_record()

        self.assertTrue(record["action_lines"][0]["outcome_evaluation"]["candy_contact"])
        self.assertEqual(record["completion_summary"]["candy_contact_action_line_count"], 1)
        for line in record["action_lines"][1:]:
            self.assertFalse(line["outcome_evaluation"]["candy_contact"])

    def test_manual_plan_not_free_choice(self):
        record = build_time_paced_locomotion_action_completion_record()
        config = record["completion_config"]

        self.assertTrue(config["manual_action_plan_reused"])
        self.assertFalse(config["free_choice_added"])
        self.assertFalse(config["background_autonomy_started"])
        self.assertFalse(config["pathfinding_used"])

    def test_completion_summary_counts(self):
        record = build_time_paced_locomotion_action_completion_record()
        summary = record["completion_summary"]

        self.assertEqual(summary["selected_action_created_count"], 6)
        self.assertEqual(summary["final_action_created_count"], 6)
        self.assertEqual(summary["direct_command_created_count"], 6)
        self.assertEqual(summary["direct_command_executed_count"], 6)
        self.assertEqual(summary["outcome_evaluation_created_count"], 6)
        self.assertTrue(summary["loop_stopped_by_budget"])
        self.assertFalse(summary["next_action_authorized_after_budget"])

    def test_blocked_flags(self):
        record = build_time_paced_locomotion_action_completion_record()
        flags = record["blocked_flags"]

        for field in (
            "background_autonomy_started",
            "free_choice_added",
            "pathfinding_used",
            "open_ended_loop_created",
            "too_fast_action_allowed",
            "production_behavior_changed",
            "memory_write_performed",
            "retention_write_performed",
            "predictor_mutation_performed",
            "endocrine_runtime_used",
            "proof_of_learning_claim_allowed",
        ):
            self.assertFalse(flags[field])

    def test_wrong_source_blocks(self):
        record = build_time_paced_locomotion_action_completion_record()
        bad = copy.deepcopy(record)
        bad["source_temporal_loop"]["source_validated"] = False

        result = validate_time_paced_locomotion_action_completion_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_temporal_loop_source_validated_not_expected", result["error_codes"])

    def test_missing_action_line_blocks(self):
        record = build_time_paced_locomotion_action_completion_record()
        bad = copy.deepcopy(record)
        bad["action_lines"] = bad["action_lines"][:-1]

        result = validate_time_paced_locomotion_action_completion_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("action_line_count_not_expected", result["error_codes"])

    def test_direct_command_not_executed_blocks(self):
        record = build_time_paced_locomotion_action_completion_record()
        bad = copy.deepcopy(record)
        bad["action_lines"][0]["execution"]["direct_command_executed"] = False

        result = validate_time_paced_locomotion_action_completion_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("action_line_1_direct_command_not_executed", result["error_codes"])

    def test_free_choice_blocks(self):
        record = build_time_paced_locomotion_action_completion_record()
        bad = copy.deepcopy(record)
        bad["completion_config"]["free_choice_added"] = True

        result = validate_time_paced_locomotion_action_completion_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("completion_config_free_choice_added_not_expected", result["error_codes"])

    def test_proof_claim_blocks(self):
        record = build_time_paced_locomotion_action_completion_record()
        bad = copy.deepcopy(record)
        bad["blocked_flags"]["proof_of_learning_claim_allowed"] = True

        result = validate_time_paced_locomotion_action_completion_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("blocked_flags_proof_of_learning_claim_allowed_not_false", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        result = run_time_paced_locomotion_action_completion_minimal_check()
        summary = result["summary"]

        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["valid_time_paced_locomotion_completion_count"], 1)
        self.assertEqual(summary["invalid_time_paced_locomotion_completion_count"], 39)
        self.assertEqual(summary["source_temporal_loop_checked_count"], 1)
        self.assertEqual(summary["action_line_completed_count"], 1)
        self.assertEqual(summary["cooldown_checked_count"], 1)
        self.assertEqual(summary["selected_action_created_total"], 6)
        self.assertEqual(summary["direct_command_executed_total"], 6)
        self.assertEqual(summary["candy_contact_action_line_total"], 1)
        self.assertTrue(summary["all_time_paced_locomotion_action_completion_checks_passed"])

    def test_cli_command(self):
        result = run_command("run-time-paced-locomotion-action-completion-minimal-check")

        self.assertEqual(result["command"], "run-time-paced-locomotion-action-completion-minimal-check")
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()

