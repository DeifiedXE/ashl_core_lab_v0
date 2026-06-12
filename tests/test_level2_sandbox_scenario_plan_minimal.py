import unittest

from ashl_core.level2_sandbox_scenario_plan_minimal import (
    PLANNED_STOP_CONDITIONS,
    build_level2_sandbox_scenario_plan,
    run_level2_sandbox_scenario_plan_minimal_check,
    validate_level2_sandbox_scenario_plan,
)
from ashl_core.teaching_cli import run_command


class Level2SandboxScenarioPlanMinimalTests(unittest.TestCase):
    def setUp(self):
        self.record = build_level2_sandbox_scenario_plan()

    def test_valid_scenario_plan_passes(self):
        result = validate_level2_sandbox_scenario_plan(self.record)

        self.assertTrue(result["valid"])
        self.assertEqual("level2_sandbox_scenario_plan_minimal", self.record["record_type"])
        self.assertEqual("phase0_level2_sandbox_design_only", self.record["target_scope"])
        self.assertEqual("planned_for_future_level2_sandbox_package_only", self.record["scenario_plan_status"])

    def test_invalid_scope_fails(self):
        record = build_level2_sandbox_scenario_plan()
        record["target_scope"] = "production"

        self.assertIn("target_scope_not_phase0_level2_sandbox_design_only", self._errors(record))

    def test_missing_valid_level2_design_envelope_dependency_fails(self):
        record = build_level2_sandbox_scenario_plan()
        record["source_level2_design_envelope"]["valid_level2_design_envelope"] = False

        self.assertIn("valid_level2_design_envelope_not_true", self._errors(record))

    def test_level2_execution_remains_blocked(self):
        self.assert_field_true_blocks("level2_execution_allowed")

    def test_level2_application_remains_blocked(self):
        self.assert_field_true_blocks("level2_application_allowed")

    def test_runtime_behavior_remains_blocked(self):
        self.assert_field_true_blocks("runtime_behavior_change_allowed")

    def test_memory_write_remains_blocked(self):
        self.assert_field_true_blocks("memory_write_allowed")

    def test_retained_jsonl_write_remains_blocked(self):
        self.assert_field_true_blocks("retained_jsonl_write_allowed")

    def test_retention_write_remains_blocked(self):
        self.assert_field_true_blocks("retention_write_allowed")

    def test_predictor_mutation_remains_blocked(self):
        self.assert_field_true_blocks("predictor_mutation_allowed")

    def test_selected_action_remains_blocked(self):
        self.assert_field_true_blocks("selected_action_allowed")

    def test_final_action_remains_blocked(self):
        self.assert_field_true_blocks("final_action_allowed")

    def test_direct_command_remains_blocked(self):
        self.assert_field_true_blocks("direct_command_allowed")

    def test_production_promotion_remains_blocked(self):
        self.assert_field_true_blocks("production_promotion_allowed")

    def test_proof_of_learning_claim_remains_blocked(self):
        self.assert_field_true_blocks("proof_of_learning_claim_allowed")

    def test_planned_expected_outcomes_are_checked(self):
        expected = self.record["planned_expected_outcomes"]

        self.assertEqual("d", expected["front_symbol"])
        self.assertEqual("check_before_retry", expected["preferred_sandbox_action"])
        self.assertTrue(expected["retry_same_action_should_be_blocked_until_check"])

    def test_wrong_front_symbol_blocks(self):
        record = build_level2_sandbox_scenario_plan()
        record["planned_expected_outcomes"]["front_symbol"] = "."

        self.assertIn("planned_expected_outcome_front_symbol_not_expected", self._errors(record))

    def test_wrong_preferred_sandbox_action_blocks(self):
        record = build_level2_sandbox_scenario_plan()
        record["planned_expected_outcomes"]["preferred_sandbox_action"] = "retry_same_action"

        self.assertIn("planned_expected_outcome_preferred_sandbox_action_not_expected", self._errors(record))

    def test_retry_block_not_required_blocks(self):
        record = build_level2_sandbox_scenario_plan()
        record["planned_expected_outcomes"]["retry_same_action_should_be_blocked_until_check"] = False

        self.assertIn(
            "planned_expected_outcome_retry_same_action_should_be_blocked_until_check_not_expected",
            self._errors(record),
        )

    def test_missing_planned_expected_outcomes_blocks(self):
        record = build_level2_sandbox_scenario_plan()
        record["planned_expected_outcomes"] = {}

        self.assertIn("planned_expected_outcome_front_symbol_not_expected", self._errors(record))

    def test_planned_stop_conditions_are_present(self):
        self.assertEqual(set(PLANNED_STOP_CONDITIONS), set(self.record["planned_stop_conditions"]))

    def test_missing_stop_conditions_blocks(self):
        record = build_level2_sandbox_scenario_plan()
        record["planned_stop_conditions"] = []

        self.assertIn("planned_stop_conditions_not_explicit", self._errors(record))

    def test_missing_audit_blocks(self):
        record = build_level2_sandbox_scenario_plan()
        record["audit_recorded"] = False

        self.assertIn("audit_recorded_not_true", self._errors(record))

    def test_missing_rollback_requirement_blocks(self):
        record = build_level2_sandbox_scenario_plan()
        record["rollback_required_for_future_execution"] = False

        self.assertIn("rollback_required_for_future_execution_not_true", self._errors(record))

    def test_human_review_required_before_future_level2_application(self):
        self.assertTrue(self.record["human_review_required_before_future_level2_application"])

    def test_missing_human_review_blocks(self):
        record = build_level2_sandbox_scenario_plan()
        record["human_review_required_before_future_level2_application"] = False

        self.assertIn("human_review_required_before_future_level2_application_not_true", self._errors(record))

    def test_cli_path_returns_ok(self):
        result = run_command("run-level2-sandbox-scenario-plan-minimal-check")

        self.assertEqual("ok", result["status"])

    def test_demo_summary_counts_are_deterministic(self):
        summary = run_level2_sandbox_scenario_plan_minimal_check()["summary"]

        self.assertEqual(1, summary["valid_level2_sandbox_scenario_plan_count"])
        self.assertGreaterEqual(summary["invalid_level2_sandbox_scenario_plan_count"], 1)
        self.assertEqual(1, summary["level2_design_envelope_checked_count"])
        self.assertEqual(1, summary["scenario_plan_design_only_count"])
        self.assertEqual(1, summary["level2_execution_blocked_count"])
        self.assertEqual(1, summary["level2_application_blocked_count"])
        self.assertEqual(1, summary["runtime_memory_predictor_blocked_count"])
        self.assertEqual(1, summary["proof_of_learning_blocked_count"])

    def assert_field_true_blocks(self, field):
        record = build_level2_sandbox_scenario_plan()
        record[field] = True

        self.assertIn(f"{field}_not_false", self._errors(record))

    def _errors(self, record):
        return validate_level2_sandbox_scenario_plan(record)["error_codes"]


if __name__ == "__main__":
    unittest.main()
