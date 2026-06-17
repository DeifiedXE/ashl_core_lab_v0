import copy
import unittest

from ashl_core.teaching_cli import run_command
from ashl_core.temporal_candy_loop_sandbox_minimal import (
    ACTION_PLAN,
    MAX_ACTION_STEPS,
    MIN_IDLE_TICKS_BETWEEN_ACTIONS,
    build_temporal_candy_loop_sandbox_record,
    run_temporal_candy_loop_sandbox_minimal_check,
    validate_temporal_candy_loop_sandbox_record,
)


class TemporalCandyLoopSandboxMinimalTests(unittest.TestCase):
    def test_valid_temporal_candy_loop_is_created(self):
        record = build_temporal_candy_loop_sandbox_record()
        result = validate_temporal_candy_loop_sandbox_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual(record["record_type"], "temporal_candy_loop_sandbox")
        self.assertEqual(record["boundary_index_after"], "2026-06-09-b106")

    def test_uses_time_envelope(self):
        record = build_temporal_candy_loop_sandbox_record()
        context = record["sandbox_context"]
        time_summary = record["time_summary"]

        self.assertEqual(context["time_model"], "OFFLINE_IDLE_ACTIVE_trace")
        self.assertTrue(context["idle_tick_enabled"])
        self.assertTrue(context["action_tick_enabled"])
        self.assertTrue(context["runtime_tick_enabled"])
        self.assertEqual(time_summary["idle_tick_total"], MAX_ACTION_STEPS * MIN_IDLE_TICKS_BETWEEN_ACTIONS)
        self.assertEqual(time_summary["action_tick_total"], MAX_ACTION_STEPS)

    def test_actions_are_slowed_by_idle_ticks(self):
        record = build_temporal_candy_loop_sandbox_record()

        for step in record["steps"]:
            self.assertEqual(step["mode_before_action"], "IDLE")
            self.assertEqual(step["mode_during_action"], "ACTIVE")
            self.assertEqual(step["idle_ticks_before_action"], MIN_IDLE_TICKS_BETWEEN_ACTIONS)
            self.assertTrue(step["cooldown_satisfied"])
            self.assertTrue(step["too_fast_blocked"])

    def test_sandbox_runs_six_manual_steps(self):
        record = build_temporal_candy_loop_sandbox_record()

        self.assertEqual(record["action_plan"], list(ACTION_PLAN))
        self.assertEqual(len(record["steps"]), MAX_ACTION_STEPS)
        self.assertEqual(record["time_summary"]["active_step_count"], MAX_ACTION_STEPS)
        self.assertTrue(record["time_summary"]["loop_stopped_by_budget"])

    def test_candy_contact_and_non_subjective_reward_trace(self):
        record = build_temporal_candy_loop_sandbox_record()
        first_step = record["steps"][0]

        self.assertTrue(first_step["candy_contact"])
        self.assertEqual(first_step["result"], "item_contact")
        self.assertTrue(first_step["candy_event_created"])
        self.assertEqual(record["candy_summary"]["candy_contact_count"], 1)
        self.assertEqual(record["candy_summary"]["candy_event_count"], 1)
        self.assertEqual(record["candy_summary"]["non_subjective_reward_event_count"], 1)
        self.assertFalse(record["candy_summary"]["candy_collection_enabled"])
        self.assertFalse(record["candy_summary"]["inventory_enabled"])

    def test_idle_ticks_do_not_create_evidence_memory_or_commands(self):
        record = build_temporal_candy_loop_sandbox_record()

        for step in record["steps"]:
            for idle_trace in step["idle_traces_before_action"]:
                self.assertFalse(idle_trace["formal_evidence_created"])
                self.assertFalse(idle_trace["memory_write"])
                self.assertFalse(idle_trace["retention_write"])
                self.assertFalse(idle_trace["world_model_updated"])
                self.assertFalse(idle_trace["prediction_error_changed"])
                self.assertFalse(idle_trace["direct_command_created"])
                self.assertFalse(idle_trace["action_executed"])

    def test_pathfinding_and_open_ended_loop_are_blocked(self):
        record = build_temporal_candy_loop_sandbox_record()
        context = record["sandbox_context"]

        self.assertFalse(context["pathfinding_used"])
        self.assertFalse(context["open_ended_loop"])
        self.assertTrue(context["manual_action_plan"])

    def test_boundary_flags_block_persistent_and_production_effects(self):
        record = build_temporal_candy_loop_sandbox_record()
        flags = record["blocked_flags"]

        for field in (
            "production_behavior_changed",
            "real_navigation_changed",
            "ui_behavior_changed",
            "memory_write_performed",
            "retained_jsonl_write_performed",
            "retention_write_performed",
            "predictor_mutation_performed",
            "endocrine_runtime_used",
            "proof_of_learning_claim_allowed",
        ):
            self.assertFalse(flags[field])

    def test_too_fast_action_blocks(self):
        record = build_temporal_candy_loop_sandbox_record()
        bad = copy.deepcopy(record)
        bad["steps"][0]["idle_ticks_before_action"] = 1

        result = validate_temporal_candy_loop_sandbox_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("step_1_idle_ticks_too_low", result["error_codes"])

    def test_cooldown_false_blocks(self):
        record = build_temporal_candy_loop_sandbox_record()
        bad = copy.deepcopy(record)
        bad["steps"][0]["cooldown_satisfied"] = False

        result = validate_temporal_candy_loop_sandbox_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("step_1_cooldown_not_satisfied", result["error_codes"])

    def test_idle_evidence_blocks(self):
        record = build_temporal_candy_loop_sandbox_record()
        bad = copy.deepcopy(record)
        bad["steps"][0]["idle_traces_before_action"][0]["formal_evidence_created"] = True

        result = validate_temporal_candy_loop_sandbox_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("step_1_idle_trace_created_evidence", result["error_codes"])

    def test_open_ended_loop_blocks(self):
        record = build_temporal_candy_loop_sandbox_record()
        bad = copy.deepcopy(record)
        bad["sandbox_context"]["open_ended_loop"] = True

        result = validate_temporal_candy_loop_sandbox_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("sandbox_context_open_ended_loop_not_expected", result["error_codes"])

    def test_proof_claim_blocks(self):
        record = build_temporal_candy_loop_sandbox_record()
        bad = copy.deepcopy(record)
        bad["blocked_flags"]["proof_of_learning_claim_allowed"] = True

        result = validate_temporal_candy_loop_sandbox_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("blocked_flags_proof_of_learning_claim_allowed_not_false", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        result = run_temporal_candy_loop_sandbox_minimal_check()
        summary = result["summary"]

        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["valid_temporal_candy_loop_count"], 1)
        self.assertEqual(summary["invalid_temporal_candy_loop_count"], 38)
        self.assertEqual(summary["time_envelope_checked_count"], 1)
        self.assertEqual(summary["slowdown_checked_count"], 1)
        self.assertEqual(summary["candy_contact_total"], 1)
        self.assertEqual(summary["active_step_total"], 6)
        self.assertEqual(summary["idle_trace_total"], 12)
        self.assertTrue(summary["all_temporal_candy_loop_checks_passed"])

    def test_cli_command(self):
        result = run_command("run-temporal-candy-loop-sandbox-minimal-check")

        self.assertEqual(result["command"], "run-temporal-candy-loop-sandbox-minimal-check")
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()

