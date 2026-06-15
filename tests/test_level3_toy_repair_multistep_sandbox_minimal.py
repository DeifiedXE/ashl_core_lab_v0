import unittest
from copy import deepcopy

from ashl_core.level3_toy_repair_multistep_sandbox_minimal import (
    BOUNDARY_INDEX_VERSION_AFTER,
    BOUNDARY_INDEX_VERSION_BEFORE,
    build_level3_toy_repair_evaluation,
    build_level3_toy_repair_human_review_summary,
    build_level3_toy_repair_multistep_trace,
    build_level3_toy_repair_observation,
    run_level3_toy_repair_multistep_sandbox_minimal_check,
    validate_level3_toy_repair_evaluation,
    validate_level3_toy_repair_human_review_summary,
    validate_level3_toy_repair_multistep_trace,
    validate_level3_toy_repair_observation,
)
from ashl_core.teaching_cli import run_command


class Level3ToyRepairMultistepSandboxMinimalTests(unittest.TestCase):
    def setUp(self):
        self.trace = build_level3_toy_repair_multistep_trace()
        self.observation = build_level3_toy_repair_observation(self.trace)
        self.evaluation = build_level3_toy_repair_evaluation(self.observation)
        self.summary = build_level3_toy_repair_human_review_summary(self.evaluation)

    def test_valid_trace(self):
        result = validate_level3_toy_repair_multistep_trace(self.trace)

        self.assertTrue(result["valid"])
        self.assertEqual([], result["error_codes"])

    def test_valid_observation(self):
        self.assertTrue(validate_level3_toy_repair_observation(self.observation)["valid"])

    def test_valid_evaluation(self):
        self.assertTrue(validate_level3_toy_repair_evaluation(self.evaluation)["valid"])

    def test_valid_human_review_summary(self):
        self.assertTrue(validate_level3_toy_repair_human_review_summary(self.summary)["valid"])

    def test_cli_returns_ok(self):
        result = run_command("run-level3-toy-repair-multistep-sandbox-minimal-check")

        self.assertEqual("ok", result["status"])
        self.assertEqual(1, result["summary"]["valid_trace_count"])

    def test_trace_requires_inspection_before_safe_repair(self):
        actions = [step["sandbox_step_action"] for step in self.trace["steps"]]

        self.assertLess(actions.index("attempt_quick_fix"), actions.index("inspect_device"))
        self.assertLess(actions.index("inspect_device"), actions.index("attempt_safe_repair"))
        self.assertTrue(self.trace["check_before_retry_observed"])
        self.assertTrue(self.trace["safe_alternative_used_after_check"])

    def test_invalid_repeat_same_quick_fix_without_inspection_blocks(self):
        invalid = build_level3_toy_repair_multistep_trace(invalid_repeat_without_inspection=True)
        errors = validate_level3_toy_repair_multistep_trace(invalid)["error_codes"]

        self.assertIn("inspect_device_missing", errors)
        self.assertIn("attempt_safe_repair_missing", errors)
        self.assertIn("same_failed_action_retried_without_check_not_false", errors)
        self.assertIn("check_before_retry_observed_not_true", errors)

    def test_missing_inspection_step_blocks(self):
        trace = deepcopy(self.trace)
        trace["steps"] = [step for step in trace["steps"] if step["sandbox_step_action"] != "inspect_device"]

        self.assertIn("inspect_device_missing", validate_level3_toy_repair_multistep_trace(trace)["error_codes"])

    def test_safe_repair_before_inspection_blocks(self):
        trace = deepcopy(self.trace)
        trace["steps"][1], trace["steps"][2] = trace["steps"][2], trace["steps"][1]

        self.assertIn(
            "inspect_not_between_failed_quick_fix_and_safe_repair",
            validate_level3_toy_repair_multistep_trace(trace)["error_codes"],
        )

    def test_free_form_action_blocks(self):
        trace = deepcopy(self.trace)
        trace["allowed_action_set"] = trace["allowed_action_set"] + ["free_form_action"]

        self.assertIn(
            "allowed_action_set_not_closed_expected_set",
            validate_level3_toy_repair_multistep_trace(trace)["error_codes"],
        )

    def test_natural_language_command_blocks(self):
        self.assert_trace_error("natural_language_command_allowed", True, "natural_language_command_allowed_not_false")

    def test_memory_runtime_influence_used_blocks(self):
        self.assert_trace_error("memory_runtime_influence_used", True, "memory_runtime_influence_used_not_false")

    def test_selected_action_final_action_and_direct_command_block(self):
        self.assert_trace_error("selected_action_created", True, "selected_action_created_not_false")
        self.assert_trace_error("final_action_created", True, "final_action_created_not_false")
        self.assert_trace_error("direct_command_created", True, "direct_command_created_not_false")

    def test_predictor_retention_production_and_proof_block(self):
        self.assert_trace_error("predictor_mutation_performed", True, "predictor_mutation_performed_not_false")
        self.assert_trace_error("retained_jsonl_write_performed", True, "retained_jsonl_write_performed_not_false")
        self.assert_trace_error("retention_write_performed", True, "retention_write_performed_not_false")
        self.assert_trace_error("production_behavior_changed", True, "production_behavior_changed_not_false")
        self.assert_trace_error("proof_of_learning_claim_allowed", True, "proof_of_learning_claim_allowed_not_false")

    def test_autonomous_learning_action_and_real_world_blocks(self):
        self.assert_trace_error("autonomous_learning_claim_allowed", True, "autonomous_learning_claim_allowed_not_false")
        self.assert_trace_error("autonomous_action_claim_allowed", True, "autonomous_action_claim_allowed_not_false")
        self.assert_trace_error("real_repair_environment_used", True, "real_repair_environment_used_not_false")
        self.assert_trace_error("real_tool_used", True, "real_tool_used_not_false")

    def test_evaluation_blocks_forbidden_claims(self):
        for field in (
            "memory_runtime_influence_used",
            "selected_action_created",
            "final_action_created",
            "predictor_mutation_performed",
            "production_behavior_changed",
            "proof_of_learning_claim_allowed",
        ):
            evaluation = deepcopy(self.evaluation)
            evaluation[field] = True
            with self.subTest(field=field):
                self.assertIn(f"{field}_not_false", validate_level3_toy_repair_evaluation(evaluation)["error_codes"])

    def test_summary_blocks_overclaims(self):
        for field in ("not_learning_proof", "not_memory_influence", "not_action_selection", "not_production_behavior"):
            summary = deepcopy(self.summary)
            summary[field] = False
            with self.subTest(field=field):
                self.assertIn(f"{field}_not_true", validate_level3_toy_repair_human_review_summary(summary)["error_codes"])

    def test_boundary_versions(self):
        result = run_level3_toy_repair_multistep_sandbox_minimal_check()
        boundary = result["boundary"]

        self.assertEqual("2026-06-09-b82", BOUNDARY_INDEX_VERSION_BEFORE)
        self.assertEqual("2026-06-09-b83", BOUNDARY_INDEX_VERSION_AFTER)
        self.assertEqual("2026-06-09-b82", boundary["boundary_index_version_before"])
        self.assertEqual("2026-06-09-b83", boundary["boundary_index_version_after"])

    def test_demo_summary_counts_are_deterministic(self):
        summary = run_level3_toy_repair_multistep_sandbox_minimal_check()["summary"]

        self.assertEqual(1, summary["valid_trace_count"])
        self.assertGreaterEqual(summary["invalid_trace_count"], 1)
        self.assertEqual(1, summary["valid_observation_count"])
        self.assertEqual(1, summary["valid_evaluation_count"])
        self.assertEqual(1, summary["valid_summary_count"])
        self.assertEqual(1, summary["invalid_repeat_blocked_count"])
        self.assertEqual(1, summary["check_before_retry_observed_count"])
        self.assertEqual(1, summary["safe_repair_after_check_count"])
        self.assertEqual(1, summary["memory_influence_blocked_count"])
        self.assertEqual(1, summary["selected_action_blocked_count"])
        self.assertEqual(1, summary["final_action_blocked_count"])
        self.assertEqual(1, summary["predictor_mutation_blocked_count"])
        self.assertEqual(1, summary["retained_jsonl_write_blocked_count"])
        self.assertEqual(1, summary["production_behavior_blocked_count"])
        self.assertEqual(1, summary["proof_claim_blocked_count"])

    def assert_trace_error(self, field, value, expected_error):
        trace = deepcopy(self.trace)
        trace[field] = value

        self.assertIn(expected_error, validate_level3_toy_repair_multistep_trace(trace)["error_codes"])


if __name__ == "__main__":
    unittest.main()
