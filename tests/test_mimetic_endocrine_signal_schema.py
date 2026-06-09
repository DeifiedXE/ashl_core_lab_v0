import json
import subprocess
import sys
import unittest

from ashl_core.mimetic_endocrine_signal_schema import (
    build_demo_signal_records,
    build_invalid_demo_cases,
    run_mimetic_endocrine_signal_schema_check,
    validate_signal_record,
)
from ashl_core.teaching_cli import run_command


class MimeticEndocrineSignalSchemaTests(unittest.TestCase):
    def test_check_runner_returns_pass_status(self):
        result = run_mimetic_endocrine_signal_schema_check()

        self.assertEqual(result["command"], "run-mimetic-endocrine-signal-schema-check")
        self.assertEqual(result["flow"], "mimetic_endocrine_signal_schema_v0")
        self.assertEqual(result["status"], "ok")

    def test_four_canonical_signal_records_exist(self):
        result = run_mimetic_endocrine_signal_schema_check()
        names = {record["signal_name"] for record in result["signal_records"]}

        self.assertEqual(
            names,
            {"dopamine_like", "norepinephrine_like", "oxytocin_like", "cortisol_like"},
        )

    def test_all_canonical_records_validate_and_are_bounded(self):
        for record in build_demo_signal_records():
            validation = validate_signal_record(record)

            self.assertTrue(validation["valid"], validation["validation_errors"])
            self.assertGreaterEqual(record["value"], 0.0)
            self.assertLessEqual(record["value"], 1.0)
            self.assertGreaterEqual(record["baseline"], 0.0)
            self.assertLessEqual(record["baseline"], 1.0)
            self.assertGreaterEqual(record["decay_rate"], 0.0)
            self.assertLessEqual(record["decay_rate"], 1.0)
            self.assertGreaterEqual(record["confidence"], 0.0)
            self.assertLessEqual(record["confidence"], 1.0)

    def test_all_canonical_records_are_traceable_and_blocked(self):
        for record in build_demo_signal_records():
            self.assertIsInstance(record["source_event_ids"], list)
            self.assertTrue(record["source_event_ids"])
            self.assertTrue(record["source_trace"])
            self.assertTrue(record["blocked_from_action_selection"])
            self.assertTrue(record["blocked_from_memory_write"])
            self.assertTrue(record["blocked_from_candidate_approval"])
            self.assertFalse(record["subjective_claim"])

    def test_required_axis_and_source_event_types(self):
        records = {record["signal_name"]: record for record in build_demo_signal_records()}

        self.assertEqual(records["dopamine_like"]["axis"], "approach_reward")
        self.assertEqual(
            records["dopamine_like"]["source_event_types"],
            ["reward_event", "goal_progress", "prediction_error_decrease"],
        )
        self.assertEqual(records["norepinephrine_like"]["axis"], "attention_salience")
        self.assertIn("change_detected", records["norepinephrine_like"]["source_event_types"])
        self.assertEqual(records["oxytocin_like"]["axis"], "source_trust")
        self.assertIn("human_review", records["oxytocin_like"]["source_event_types"])
        self.assertEqual(records["cortisol_like"]["axis"], "pressure_load")
        self.assertIn("failure_accumulation", records["cortisol_like"]["source_event_types"])

    def test_invalid_demo_cases_fail_safely(self):
        cases = {
            case["case_name"]: validate_signal_record(case["record"])
            for case in build_invalid_demo_cases()
        }

        self.assertFalse(cases["invalid_value_out_of_range"]["valid"])
        self.assertIn("value_out_of_range", cases["invalid_value_out_of_range"]["validation_errors"])
        self.assertFalse(cases["invalid_subjective_claim_true"]["valid"])
        self.assertIn("subjective_claim_not_allowed", cases["invalid_subjective_claim_true"]["validation_errors"])
        self.assertFalse(cases["invalid_action_selection_unblocked"]["valid"])
        self.assertIn("action_selection_not_blocked", cases["invalid_action_selection_unblocked"]["validation_errors"])
        self.assertFalse(cases["invalid_missing_source_trace"]["valid"])
        self.assertIn("missing_source_trace", cases["invalid_missing_source_trace"]["validation_errors"])
        self.assertFalse(cases["unknown_signal_name"]["valid"])
        self.assertIn("unknown_signal_name", cases["unknown_signal_name"]["validation_errors"])

    def test_summary_counts_and_boundary_flags(self):
        result = run_mimetic_endocrine_signal_schema_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(summary["signal_count"], 4)
        self.assertEqual(summary["valid_signal_count"], 4)
        self.assertEqual(summary["invalid_signal_count"], 0)
        self.assertEqual(summary["blocked_from_action_selection_count"], 4)
        self.assertEqual(summary["blocked_from_memory_write_count"], 4)
        self.assertEqual(summary["blocked_from_candidate_approval_count"], 4)
        self.assertEqual(summary["subjective_claim_count"], 0)
        self.assertEqual(summary["runtime_formula_count"], 0)
        self.assertEqual(summary["action_selection_influence_count"], 0)
        self.assertEqual(summary["memory_write_count"], 0)
        self.assertEqual(summary["candidate_approval_influence_count"], 0)

        self.assertTrue(boundary["schema_check_only"])
        self.assertFalse(boundary["runtime_formula_added"])
        self.assertFalse(boundary["signal_interaction_runtime_added"])
        self.assertFalse(boundary["endocrine_state_runtime_added"])
        self.assertFalse(boundary["subjective_emotion_claimed"])
        self.assertFalse(boundary["subjective_possibility_denied"])
        self.assertFalse(boundary["action_selection_modified"])
        self.assertFalse(boundary["endocrine_signal_used_for_action_selection"])
        self.assertFalse(boundary["predictor_modified"])
        self.assertFalse(boundary["memory_layer_write"])
        self.assertFalse(boundary["personality_drift_enabled"])

    def test_run_command_uses_default(self):
        result = run_command("run-mimetic-endocrine-signal-schema-check")

        self.assertEqual(result["command"], "run-mimetic-endocrine-signal-schema-check")
        self.assertEqual(result["summary"]["signal_count"], 4)
        self.assertEqual(result["summary"]["runtime_formula_count"], 0)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-mimetic-endocrine-signal-schema-check",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-mimetic-endocrine-signal-schema-check")
        self.assertEqual(result["summary"]["valid_signal_count"], 4)
        self.assertEqual(result["summary"]["action_selection_influence_count"], 0)


if __name__ == "__main__":
    unittest.main()
