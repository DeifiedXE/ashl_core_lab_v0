import unittest
from copy import deepcopy

from ashl_core.sandbox_final_action_minimal import (
    BOUNDARY_INDEX_AFTER,
    BOUNDARY_INDEX_BEFORE,
    build_sandbox_final_action_record,
    build_sandbox_final_action_result_summary,
    build_test_tier_policy_and_sandbox_final_action_summary,
    run_test_tier_policy_and_sandbox_final_action_minimal_check,
    validate_sandbox_final_action_record,
    validate_sandbox_final_action_result_summary,
    validate_test_tier_policy_and_sandbox_final_action_summary,
)
from ashl_core.test_tier_policy_minimal import (
    build_test_tier_policy_record,
    validate_test_tier_policy_record,
)


class TestTierPolicyAndSandboxFinalActionMinimalTests(unittest.TestCase):
    def setUp(self):
        self.policy = build_test_tier_policy_record()
        self.final_action = build_sandbox_final_action_record()
        self.combined_summary = build_test_tier_policy_and_sandbox_final_action_summary(
            self.policy, self.final_action
        )

    def test_valid_test_tier_policy(self):
        result = validate_test_tier_policy_record(self.policy)
        self.assertTrue(result["valid"], result["error_codes"])
        self.assertEqual("targeted", self.policy["default_package_test_tier"])
        self.assertFalse(self.policy["full_unittest_discover_default"])
        self.assertTrue(self.policy["full_unittest_discover_conditional"])
        self.assertTrue(self.policy["full_unittest_skip_requires_reason"])
        self.assertFalse(self.policy["boundary_index_change_required_by_policy_only"])

    def test_valid_sandbox_final_action(self):
        result = validate_sandbox_final_action_record(self.final_action)
        self.assertTrue(result["valid"], result["error_codes"])
        self.assertEqual("observe_or_alternative_probe", self.final_action["selected_action"])
        self.assertEqual(self.final_action["selected_action"], self.final_action["final_action"])
        self.assertTrue(self.final_action["final_action_created"])
        self.assertEqual("sandbox_only", self.final_action["final_action_scope"])
        self.assertTrue(result["final_action_source_checked"])
        self.assertTrue(result["sandbox_scope_checked"])

    def test_valid_result_summary(self):
        summary = build_sandbox_final_action_result_summary(self.final_action)
        result = validate_sandbox_final_action_result_summary(summary)
        self.assertTrue(result["valid"], result["error_codes"])
        self.assertTrue(summary["final_action_created"])
        self.assertFalse(summary["direct_command_created"])

    def test_valid_combined_summary(self):
        result = validate_test_tier_policy_and_sandbox_final_action_summary(self.combined_summary)
        self.assertTrue(result["valid"], result["error_codes"])
        self.assertEqual(BOUNDARY_INDEX_BEFORE, self.combined_summary["boundary_index_before"])
        self.assertEqual(BOUNDARY_INDEX_AFTER, self.combined_summary["boundary_index_after"])
        self.assertTrue(self.combined_summary["boundary_change_required"])
        self.assertFalse(self.combined_summary["test_tier_policy_boundary_change_required"])

    def test_invalid_policy_requires_full_unittest_for_every_package(self):
        policy = deepcopy(self.policy)
        policy["full_unittest_discover_default"] = True
        self.assertIn("full_unittest_discover_default_not_false", validate_test_tier_policy_record(policy)["error_codes"])

    def test_invalid_full_regression_skipped_without_reason(self):
        policy = deepcopy(self.policy)
        policy["full_unittest_discover_skipped"] = True
        policy["full_unittest_skip_reason"] = ""
        self.assertIn("full_unittest_skipped_without_reason", validate_test_tier_policy_record(policy)["error_codes"])

    def test_invalid_policy_changes_boundary_index_by_itself(self):
        policy = deepcopy(self.policy)
        policy["boundary_index_change_required_by_policy_only"] = True
        self.assertIn(
            "boundary_index_change_required_by_policy_only_not_false",
            validate_test_tier_policy_record(policy)["error_codes"],
        )

    def test_invalid_missing_b98_approval_source(self):
        record = deepcopy(self.final_action)
        record["source_final_action_approval_boundary_record"] = {}
        self.assertIn(
            "missing_or_invalid_b98_final_action_approval_source",
            validate_sandbox_final_action_record(record)["error_codes"],
        )

    def test_invalid_final_action_differs_from_selected_action(self):
        record = deepcopy(self.final_action)
        record["final_action"] = "retry_same_action_without_check"
        self.assertIn("final_action_not_selected_action", validate_sandbox_final_action_record(record)["error_codes"])

    def test_invalid_final_action_outside_sandbox_scope(self):
        record = deepcopy(self.final_action)
        record["final_action_scope"] = "production"
        self.assertIn("final_action_scope_not_expected", validate_sandbox_final_action_record(record)["error_codes"])

    def test_invalid_direct_command(self):
        self._assert_final_action_false_field_blocks("direct_command_created")
        self._assert_final_action_false_field_blocks("direct_command_allowed")

    def test_invalid_production_behavior(self):
        self._assert_final_action_false_field_blocks("production_behavior_changed")

    def test_invalid_persistent_rule(self):
        self._assert_final_action_false_field_blocks("persistent_rule_created")

    def test_invalid_persistent_trust_doubt_update(self):
        self._assert_final_action_false_field_blocks("persistent_trust_doubt_update_performed")

    def test_invalid_cross_session_persistence(self):
        self._assert_final_action_false_field_blocks("cross_session_feedback_persistence")

    def test_invalid_memory_write(self):
        self._assert_final_action_false_field_blocks("memory_write_performed")
        self._assert_final_action_false_field_blocks("retained_jsonl_write_performed")

    def test_invalid_retention_write(self):
        self._assert_final_action_false_field_blocks("retention_write_performed")

    def test_invalid_predictor_read_influence_mutation(self):
        self._assert_final_action_false_field_blocks("predictor_read_enabled")
        self._assert_final_action_false_field_blocks("predictor_influence_enabled")
        self._assert_final_action_false_field_blocks("predictor_mutation_performed")

    def test_invalid_proof_claim(self):
        self._assert_final_action_false_field_blocks("proof_of_learning_claim_allowed")

    def test_invalid_autonomous_learning_action_claim(self):
        self._assert_final_action_false_field_blocks("autonomous_learning_claim_allowed")
        self._assert_final_action_false_field_blocks("autonomous_action_claim_allowed")

    def test_invalid_llm_used_true(self):
        self._assert_final_action_false_field_blocks("llm_used")

    def test_demo_summary_counts_are_deterministic(self):
        result = run_test_tier_policy_and_sandbox_final_action_minimal_check()
        summary = result["summary"]
        self.assertEqual("ok", result["status"])
        self.assertEqual(1, summary["valid_test_policy_count"])
        self.assertEqual(4, summary["invalid_test_policy_count"])
        self.assertEqual(1, summary["valid_final_action_count"])
        self.assertEqual(19, summary["invalid_final_action_count"])
        self.assertEqual(1, summary["valid_summary_count"])
        self.assertEqual(9, summary["invalid_summary_count"])
        self.assertEqual(1, summary["final_action_source_checked_count"])
        self.assertEqual(1, summary["sandbox_scope_checked_count"])
        self.assertEqual(1, summary["direct_command_blocked_count"])
        self.assertEqual(1, summary["persistent_update_blocked_count"])
        self.assertEqual(1, summary["memory_write_blocked_count"])
        self.assertEqual(1, summary["retention_blocked_count"])
        self.assertEqual(1, summary["predictor_mutation_blocked_count"])
        self.assertEqual(1, summary["production_behavior_blocked_count"])
        self.assertEqual(1, summary["proof_claim_blocked_count"])
        self.assertTrue(summary["all_test_tier_policy_and_sandbox_final_action_checks_passed"])

    def _assert_final_action_false_field_blocks(self, field):
        record = deepcopy(self.final_action)
        record[field] = True
        self.assertIn(f"{field}_not_false", validate_sandbox_final_action_record(record)["error_codes"])


if __name__ == "__main__":
    unittest.main()
