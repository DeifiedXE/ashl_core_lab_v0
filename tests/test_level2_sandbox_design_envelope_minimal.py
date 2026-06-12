import unittest

from ashl_core.level2_sandbox_design_envelope_minimal import (
    ALLOWED_FUTURE_LEVEL2_CAPABILITIES,
    FORBIDDEN_CAPABILITIES,
    REQUIRED_FUTURE_INPUTS,
    STOP_CONDITIONS,
    build_level2_sandbox_design_envelope,
    run_level2_sandbox_design_envelope_minimal_check,
    validate_level2_sandbox_design_envelope,
)
from ashl_core.teaching_cli import run_command


class Level2SandboxDesignEnvelopeMinimalTests(unittest.TestCase):
    def setUp(self):
        self.record = build_level2_sandbox_design_envelope()

    def test_valid_design_envelope(self):
        result = validate_level2_sandbox_design_envelope(self.record)

        self.assertTrue(result["valid"])
        self.assertEqual("level2_sandbox_design_envelope", self.record["record_type"])
        self.assertEqual("phase0_level2_sandbox_design_only", self.record["target_scope"])

    def test_requires_valid_level1_review_conclusion(self):
        record = build_level2_sandbox_design_envelope()
        record["source_level1_review_conclusion"]["valid_level1_review_conclusion"] = False

        self.assertIn("valid_level1_review_conclusion_not_true", self._errors(record))

    def test_requires_valid_level2_readiness_precheck(self):
        record = build_level2_sandbox_design_envelope()
        record["source_level2_readiness_precheck"]["valid_level2_readiness_precheck"] = False

        self.assertIn("valid_level2_readiness_precheck_not_true", self._errors(record))

    def test_wrong_target_scope_blocks(self):
        record = build_level2_sandbox_design_envelope()
        record["target_scope"] = "production"

        self.assertIn("target_scope_not_phase0_level2_sandbox_design_only", self._errors(record))

    def test_level2_execution_attempt_blocks(self):
        self.assert_field_true_blocks("level2_execution_allowed")

    def test_level2_application_attempt_blocks(self):
        self.assert_field_true_blocks("level2_application_allowed")

    def test_memory_write_attempt_blocks(self):
        self.assert_field_true_blocks("memory_write_created")

    def test_retained_jsonl_write_attempt_blocks(self):
        self.assert_field_true_blocks("retained_jsonl_write_created")

    def test_retention_write_attempt_blocks(self):
        self.assert_field_true_blocks("retention_write_created")

    def test_predictor_mutation_attempt_blocks(self):
        self.assert_field_true_blocks("predictor_mutation_created")

    def test_runtime_behavior_change_attempt_blocks(self):
        self.assert_field_true_blocks("runtime_behavior_change_allowed")

    def test_production_promotion_attempt_blocks(self):
        self.assert_field_true_blocks("production_behavior_change_allowed")

    def test_selected_action_attempt_blocks(self):
        self.assert_field_true_blocks("selected_action_created")

    def test_final_action_attempt_blocks(self):
        self.assert_field_true_blocks("final_action_created")

    def test_direct_action_command_attempt_blocks(self):
        self.assert_field_true_blocks("direct_action_command_created")

    def test_proof_of_learning_claim_attempt_blocks(self):
        self.assert_field_true_blocks("proof_of_learning_claim_created")

    def test_allowed_future_capabilities_are_explicit(self):
        self.assertEqual(set(ALLOWED_FUTURE_LEVEL2_CAPABILITIES), set(self.record["allowed_future_level2_capabilities"]))

    def test_forbidden_capabilities_are_explicit(self):
        self.assertEqual(set(FORBIDDEN_CAPABILITIES), set(self.record["forbidden_capabilities"]))

    def test_required_future_inputs_are_explicit(self):
        self.assertEqual(set(REQUIRED_FUTURE_INPUTS), set(self.record["required_future_inputs"]))

    def test_missing_stop_conditions_blocks(self):
        record = build_level2_sandbox_design_envelope()
        record["stop_conditions"] = []

        self.assertIn("stop_conditions_not_explicit", self._errors(record))
        self.assertEqual(set(STOP_CONDITIONS), set(self.record["stop_conditions"]))

    def test_missing_audit_requirement_blocks(self):
        record = build_level2_sandbox_design_envelope()
        record["audit_required"] = False

        self.assertIn("audit_required_not_true", self._errors(record))

    def test_missing_rollback_requirement_blocks(self):
        record = build_level2_sandbox_design_envelope()
        record["rollback_required"] = False

        self.assertIn("rollback_required_not_true", self._errors(record))

    def test_missing_human_review_requirement_blocks(self):
        record = build_level2_sandbox_design_envelope()
        record["human_review_required_before_future_level2_application"] = False

        self.assertIn("human_review_required_before_future_level2_application_not_true", self._errors(record))

    def test_task_queue_completed_status_is_not_approval(self):
        self.assert_field_true_blocks("task_queue_completed_status_is_approval")

    def test_passing_tests_are_not_approval(self):
        self.assert_field_true_blocks("passing_tests_are_approval")

    def test_codex_status_is_not_approval(self):
        self.assert_field_true_blocks("codex_generated_status_is_approval")

    def test_cli_returns_status_ok(self):
        result = run_command("run-level2-sandbox-design-envelope-minimal-check")

        self.assertEqual("ok", result["status"])

    def test_demo_summary_counts_are_deterministic(self):
        summary = run_level2_sandbox_design_envelope_minimal_check()["summary"]

        self.assertEqual(1, summary["valid_level2_sandbox_design_envelope_count"])
        self.assertGreaterEqual(summary["invalid_level2_sandbox_design_envelope_count"], 1)
        self.assertEqual(0, summary["level2_execution_allowed_count"])
        self.assertEqual(0, summary["level2_application_allowed_count"])
        self.assertEqual(1, summary["forbidden_capability_blocked_count"])
        self.assertEqual(1, summary["audit_required_count"])
        self.assertEqual(1, summary["rollback_required_count"])
        self.assertEqual(1, summary["human_review_required_count"])

    def assert_field_true_blocks(self, field):
        record = build_level2_sandbox_design_envelope()
        record[field] = True

        self.assertIn(f"{field}_not_false", self._errors(record))

    def _errors(self, record):
        return validate_level2_sandbox_design_envelope(record)["error_codes"]


if __name__ == "__main__":
    unittest.main()
