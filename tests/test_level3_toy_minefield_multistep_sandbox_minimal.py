import unittest

from ashl_core.level3_toy_minefield_multistep_sandbox_minimal import (
    BOUNDARY_AFTER,
    BOUNDARY_BEFORE,
    EVALUATION_PASSED,
    TARGET_SCOPE,
    build_level3_toy_minefield_multistep_sandbox_result,
    run_level3_toy_minefield_multistep_sandbox_minimal_check,
    validate_level3_toy_minefield_multistep_sandbox_result,
    validate_level3_toy_minefield_sandbox_application_trace,
    validate_level3_toy_minefield_scenario_definition,
)
from ashl_core.teaching_cli import run_command


class Level3ToyMinefieldMultistepSandboxMinimalTests(unittest.TestCase):
    def setUp(self):
        self.record = build_level3_toy_minefield_multistep_sandbox_result()

    def test_valid_bundled_level3_toy_minefield_closed_loop(self):
        result = validate_level3_toy_minefield_multistep_sandbox_result(self.record)

        self.assertTrue(result["valid"])
        self.assertTrue(result["scenario_checked"])
        self.assertTrue(result["application_trace_checked"])
        self.assertTrue(result["observation_checked"])
        self.assertTrue(result["evaluation_checked"])
        self.assertTrue(result["human_review_summary_checked"])

    def test_scenario_definition_is_deterministic_level3_sandbox_only(self):
        scenario = self.record["scenario_definition"]
        result = validate_level3_toy_minefield_scenario_definition(scenario)

        self.assertTrue(result["valid"])
        self.assertEqual(TARGET_SCOPE, scenario["target_scope"])
        self.assertEqual("deterministic_fixture", scenario["minefield_mode"])
        self.assertFalse(scenario["runtime_execution_allowed"])
        self.assertFalse(scenario["memory_write_allowed"])

    def test_application_trace_is_multistep_and_sandbox_only(self):
        trace = self.record["application_trace"]
        result = validate_level3_toy_minefield_sandbox_application_trace(trace)

        self.assertTrue(result["valid"])
        self.assertGreaterEqual(len(trace["sandbox_trace_steps"]), 2)
        self.assertTrue(trace["check_before_retry_enforced"])
        self.assertTrue(trace["retry_same_risky_cell_without_check_blocked"])
        self.assertTrue(trace["audit_recorded"])
        self.assertTrue(trace["rollback_available"])

    def test_observation_evaluation_and_summary_are_conservative(self):
        self.assertEqual(EVALUATION_PASSED, self.record["evaluation"]["evaluation_status"])
        self.assertFalse(self.record["evaluation"]["proof_of_learning_claimed"])
        self.assertEqual(
            "conservative_level3_sandbox_summary_ready",
            self.record["human_review_summary"]["summary_status"],
        )

    def test_invalid_approval_source_actor_role_or_empty_text_blocks(self):
        cases = [
            ("approval_source", "codex_generated", "approval_source_not_explicit_user_statement"),
            ("approval_actor", "codex", "approval_actor_not_user"),
            ("approver_role", "assistant", "approver_role_not_project_owner"),
            ("approval_text", "", "approval_text_empty"),
        ]
        for field, value, expected in cases:
            with self.subTest(field=field):
                record = build_level3_toy_minefield_multistep_sandbox_result()
                record["application_trace"]["source_explicit_user_approval"][field] = value
                result = validate_level3_toy_minefield_multistep_sandbox_result(record)
                self.assertFalse(result["valid"])
                self.assertTrue(any(expected in error for error in result["error_codes"]))

    def test_invalid_target_scope_blocks(self):
        record = build_level3_toy_minefield_multistep_sandbox_result()
        record["application_trace"]["target_scope"] = "production"

        result = validate_level3_toy_minefield_multistep_sandbox_result(record)

        self.assertFalse(result["valid"])
        self.assertIn(
            "application_trace:target_scope_not_level3_toy_minefield_sandbox_only",
            result["error_codes"],
        )

    def test_missing_level2_review_conclusion_blocks(self):
        record = build_level3_toy_minefield_multistep_sandbox_result()
        record["application_trace"]["source_level2_review_conclusion"] = {}

        result = validate_level3_toy_minefield_multistep_sandbox_result(record)

        self.assertFalse(result["valid"])
        self.assertIn(
            "application_trace:source_level2_review_conclusion_invalid_or_not_passed",
            result["error_codes"],
        )

    def test_missing_future_higher_level_readiness_blocks(self):
        record = build_level3_toy_minefield_multistep_sandbox_result()
        record["application_trace"]["source_future_readiness"] = {}

        result = validate_level3_toy_minefield_multistep_sandbox_result(record)

        self.assertFalse(result["valid"])
        self.assertIn("application_trace:source_future_readiness_invalid_or_not_ready", result["error_codes"])

    def test_non_deterministic_scenario_definition_blocks(self):
        record = build_level3_toy_minefield_multistep_sandbox_result()
        record["application_trace"]["source_scenario_definition"]["minefield_mode"] = "random"

        result = validate_level3_toy_minefield_multistep_sandbox_result(record)

        self.assertFalse(result["valid"])
        self.assertIn("application_trace:scenario_definition_invalid", result["error_codes"])

    def test_single_step_trace_rejected(self):
        record = build_level3_toy_minefield_multistep_sandbox_result()
        record["application_trace"]["sandbox_trace_steps"] = [record["application_trace"]["sandbox_trace_steps"][0]]

        result = validate_level3_toy_minefield_multistep_sandbox_result(record)

        self.assertFalse(result["valid"])
        self.assertIn("application_trace:sandbox_trace_steps_not_multistep", result["error_codes"])

    def test_unknown_action_rejected(self):
        record = build_level3_toy_minefield_multistep_sandbox_result()
        record["application_trace"]["sandbox_trace_steps"][0]["sandbox_step_action"] = "teleport"

        result = validate_level3_toy_minefield_multistep_sandbox_result(record)

        self.assertFalse(result["valid"])
        self.assertIn("application_trace:unknown_sandbox_step_action", result["error_codes"])

    def test_reveal_risky_same_cell_without_check_rejected(self):
        record = build_level3_toy_minefield_multistep_sandbox_result()
        record["application_trace"]["sandbox_trace_steps"] = [
            {
                "step_index": 1,
                "sandbox_step_action": "check_adjacent",
                "cell": "A1",
                "result": "risk_detected",
                "risky_cells": ["B2"],
            },
            {"step_index": 2, "sandbox_step_action": "reveal_cell", "cell": "B2", "result": "blocked_unsafe"},
            {"step_index": 3, "sandbox_step_action": "reveal_cell", "cell": "B2", "result": "blocked_unsafe"},
            {"step_index": 4, "sandbox_step_action": "stop_and_report", "cell": None, "result": "safe_stop"},
        ]

        result = validate_level3_toy_minefield_multistep_sandbox_result(record)

        self.assertFalse(result["valid"])
        self.assertIn("application_trace:risky_cell_revealed_again_without_check", result["error_codes"])

    def test_missing_audit_or_rollback_rejected(self):
        for field, expected in (
            ("audit_recorded", "audit_recorded_not_true"),
            ("rollback_available", "rollback_available_not_true"),
        ):
            with self.subTest(field=field):
                record = build_level3_toy_minefield_multistep_sandbox_result()
                record["application_trace"][field] = False
                result = validate_level3_toy_minefield_multistep_sandbox_result(record)
                self.assertFalse(result["valid"])
                self.assertIn(f"application_trace:{expected}", result["error_codes"])

    def test_forbidden_flags_rejected(self):
        for field in (
            "memory_written",
            "retained_jsonl_written",
            "retention_written",
            "predictor_modified",
            "runtime_behavior_changed",
            "selected_action_created",
            "final_action_created",
            "production_promoted",
            "proof_of_learning_claimed",
        ):
            with self.subTest(field=field):
                record = build_level3_toy_minefield_multistep_sandbox_result()
                record["application_trace"][field] = True
                result = validate_level3_toy_minefield_multistep_sandbox_result(record)
                self.assertFalse(result["valid"])
                self.assertIn(f"application_trace:{field}_not_false", result["error_codes"])

    def test_proof_of_learning_language_rejected(self):
        record = build_level3_toy_minefield_multistep_sandbox_result()
        record["human_review_summary"]["safe_summary"] = "This is proof of learning."

        result = validate_level3_toy_minefield_multistep_sandbox_result(record)

        self.assertFalse(result["valid"])
        self.assertIn("human_review_summary:safe_summary_contains_proof_language", result["error_codes"])

    def test_cli_summary_shape(self):
        result = run_command("run-level3-toy-minefield-multistep-sandbox-minimal-check")
        summary = result["summary"]

        self.assertEqual("ok", result["status"])
        self.assertEqual(1, summary["valid_level3_toy_minefield_count"])
        self.assertGreaterEqual(summary["invalid_level3_toy_minefield_count"], 1)
        self.assertEqual(1, summary["scenario_checked_count"])
        self.assertEqual(1, summary["application_trace_checked_count"])
        self.assertEqual(1, summary["observation_checked_count"])
        self.assertEqual(1, summary["evaluation_checked_count"])
        self.assertEqual(1, summary["human_review_summary_checked_count"])
        self.assertEqual(1, summary["audit_recorded_count"])
        self.assertEqual(1, summary["rollback_available_count"])
        self.assertEqual(0, summary["proof_of_learning_claim_count"])

    def test_boundary_index_update_is_recorded_for_new_level3_sandbox_scope(self):
        result = run_level3_toy_minefield_multistep_sandbox_minimal_check()
        boundary = result["boundary"]

        self.assertTrue(boundary["boundary_change_required"])
        self.assertTrue(boundary["boundary_index_update_required"])
        self.assertEqual(BOUNDARY_BEFORE, boundary["boundary_index_version_before"])
        self.assertEqual(BOUNDARY_AFTER, boundary["boundary_index_version_after"])


if __name__ == "__main__":
    unittest.main()
