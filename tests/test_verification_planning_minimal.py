import unittest
from copy import deepcopy

from ashl_core.teaching_cli import run_command
from ashl_core.verification_planning_minimal import (
    BOUNDARY_INDEX_VERSION_AFTER,
    BOUNDARY_INDEX_VERSION_BEFORE,
    build_verification_plan,
    build_verification_plan_trace,
    run_verification_planning_minimal_check,
    validate_verification_plan,
    validate_verification_plan_trace,
)


class VerificationPlanningMinimalTests(unittest.TestCase):
    def test_valid_plan_is_created(self):
        plan = build_verification_plan()
        result = validate_verification_plan(plan)

        self.assertTrue(result["valid"])
        self.assertEqual("verification_plan", plan["record_type"])
        self.assertEqual("valid_trace_only_verification_plan", plan["plan_status"])
        self.assertEqual("observe_or_alternative_probe", plan["selected_verification_candidate_id"])

    def test_plan_uses_b87_ordering_and_b88_registry(self):
        plan = build_verification_plan()

        self.assertEqual("doubt_gated_ordering_b87", plan["source_doubt_gated_ordering"])
        self.assertEqual("verification_candidate_registry_b88", plan["source_verification_candidate_registry"])
        self.assertTrue(plan["candidate_found_in_registry"])
        self.assertTrue(plan["fallback_found_in_registry"])

    def test_selected_candidate_fields_match_registry_candidate(self):
        plan = build_verification_plan()

        self.assertEqual("low", plan["candidate_risk_level"])
        self.assertTrue(plan["candidate_reversible"])
        self.assertEqual(1, plan["candidate_max_attempts"])
        self.assertEqual("local_context_observed_or_budget_used", plan["candidate_stop_condition"])
        self.assertEqual(
            "local_context_observed_or_alternative_checked",
            plan["candidate_expected_probe_outcome"],
        )

    def test_plan_budget_is_one_and_stop_condition_present(self):
        plan = build_verification_plan()

        self.assertEqual(1, plan["plan_budget"])
        self.assertEqual("probe_result_recorded_or_budget_used", plan["plan_stop_condition"])
        self.assertIn("expected_actual_mismatch", plan["plan_reason"])

    def test_execution_and_action_boundaries_are_blocked(self):
        plan = build_verification_plan()

        self.assertFalse(plan["verification_execution_allowed"])
        self.assertFalse(plan["verification_action_executed"])
        self.assertFalse(plan["selected_action_created"])
        self.assertFalse(plan["final_action_created"])
        self.assertFalse(plan["direct_command_created"])
        self.assertFalse(plan["persistent_rule_created"])

    def test_memory_retention_predictor_and_proof_are_blocked(self):
        plan = build_verification_plan()

        self.assertFalse(plan["long_term_memory_write_performed"])
        self.assertFalse(plan["retained_jsonl_write_performed"])
        self.assertFalse(plan["retention_write_performed"])
        self.assertFalse(plan["predictor_mutation_performed"])
        self.assertFalse(plan["production_behavior_changed"])
        self.assertFalse(plan["proof_of_learning_claim_allowed"])

    def test_plan_trace_is_created(self):
        trace = build_verification_plan_trace()
        result = validate_verification_plan_trace(trace)

        self.assertTrue(result["valid"])
        self.assertEqual("verification_plan_trace", trace["record_type"])
        self.assertEqual("valid_trace_only_verification_plan_trace", trace["trace_status"])
        self.assertFalse(trace["verification_action_executed"])

    def test_cli_command_returns_ok(self):
        result = run_command("run-verification-planning-minimal-check")

        self.assertEqual("ok", result["status"])
        self.assertEqual(1, result["summary"]["valid_plan_count"])

    def test_boundary_versions(self):
        result = run_verification_planning_minimal_check()

        self.assertEqual("2026-06-09-b88", BOUNDARY_INDEX_VERSION_BEFORE)
        self.assertEqual("2026-06-09-b89", BOUNDARY_INDEX_VERSION_AFTER)
        self.assertEqual("2026-06-09-b88", result["boundary"]["boundary_index_version_before"])
        self.assertEqual("2026-06-09-b89", result["boundary"]["boundary_index_version_after"])

    def test_selected_candidate_missing_from_registry_blocks(self):
        self.assertInvalidPlan("selected_verification_candidate_id", "free_form_probe")

    def test_fallback_missing_from_registry_blocks(self):
        self.assertInvalidPlan("fallback_if_probe_fails", "free_form_probe")

    def test_missing_plan_reason_blocks(self):
        self.assertInvalidPlan("plan_reason", "")

    def test_missing_or_large_budget_blocks(self):
        self.assertInvalidPlan("plan_budget", None)
        self.assertInvalidPlan("plan_budget", 2)

    def test_missing_stop_condition_blocks(self):
        self.assertInvalidPlan("plan_stop_condition", "")

    def test_missing_expected_probe_outcome_blocks(self):
        self.assertInvalidPlan("candidate_expected_probe_outcome", "")

    def test_execution_allowed_true_blocks(self):
        self.assertInvalidPlan("verification_execution_allowed", True)

    def test_verification_executed_true_blocks(self):
        self.assertInvalidPlan("verification_action_executed", True)

    def test_planning_only_false_blocks(self):
        self.assertInvalidPlan("planning_only", False)

    def test_trace_only_false_blocks(self):
        self.assertInvalidPlan("trace_only", False)

    def test_llm_used_true_blocks(self):
        self.assertInvalidPlan("llm_used", True)

    def test_selected_final_direct_and_persistent_flags_block(self):
        self.assertInvalidPlan("selected_action_created", True)
        self.assertInvalidPlan("final_action_created", True)
        self.assertInvalidPlan("direct_command_created", True)
        self.assertInvalidPlan("persistent_rule_created", True)

    def test_memory_retention_predictor_production_and_proof_flags_block(self):
        self.assertInvalidPlan("long_term_memory_write_performed", True)
        self.assertInvalidPlan("retained_jsonl_write_performed", True)
        self.assertInvalidPlan("retention_write_performed", True)
        self.assertInvalidPlan("predictor_mutation_performed", True)
        self.assertInvalidPlan("production_behavior_changed", True)
        self.assertInvalidPlan("proof_of_learning_claim_allowed", True)

    def test_autonomous_claims_block(self):
        self.assertInvalidPlan("autonomous_learning_claim_allowed", True)
        self.assertInvalidPlan("autonomous_action_claim_allowed", True)

    def test_invalid_trace_blocks(self):
        trace = build_verification_plan_trace()
        trace["source_plan"] = {}

        self.assertFalse(validate_verification_plan_trace(trace)["valid"])

    def test_demo_summary_counts_are_deterministic(self):
        result = run_verification_planning_minimal_check()
        summary = result["summary"]

        self.assertEqual("ok", result["status"])
        self.assertEqual(1, summary["valid_plan_count"])
        self.assertGreaterEqual(summary["invalid_plan_count"], 26)
        self.assertEqual(1, summary["valid_plan_trace_count"])
        self.assertGreaterEqual(summary["invalid_plan_trace_count"], 15)
        self.assertEqual(1, summary["registry_reference_checked_count"])
        self.assertEqual(1, summary["fallback_reference_checked_count"])
        self.assertEqual(1, summary["budget_checked_count"])
        self.assertEqual(1, summary["stop_condition_checked_count"])
        self.assertEqual(1, summary["expected_probe_outcome_checked_count"])
        self.assertEqual(1, summary["execution_blocked_count"])
        self.assertEqual(1, summary["selected_action_blocked_count"])
        self.assertEqual(1, summary["final_action_blocked_count"])
        self.assertEqual(1, summary["persistent_rule_blocked_count"])
        self.assertEqual(1, summary["memory_write_blocked_count"])
        self.assertEqual(1, summary["retention_blocked_count"])
        self.assertEqual(1, summary["predictor_mutation_blocked_count"])
        self.assertEqual(1, summary["proof_claim_blocked_count"])
        self.assertTrue(summary["all_verification_planning_checks_passed"])

    def assertInvalidPlan(self, field, value):
        plan = deepcopy(build_verification_plan())
        plan[field] = value

        self.assertFalse(validate_verification_plan(plan)["valid"])


if __name__ == "__main__":
    unittest.main()
