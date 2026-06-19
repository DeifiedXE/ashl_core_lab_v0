import copy
import unittest

from ashl_core.approved_purpose_candidate_ordering_boundary_minimal import (
    run_approved_purpose_candidate_ordering_boundary_minimal_check,
)
from ashl_core.approved_purpose_candidate_ordering_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_approved_purpose_candidate_ordering_record,
    run_approved_purpose_candidate_ordering_minimal_check,
    validate_approved_purpose_candidate_ordering_record,
)
from ashl_core.teaching_cli import run_command


class ApprovedPurposeCandidateOrderingMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_approved_purpose_candidate_ordering_boundary_minimal_check()["valid_records"]
        cls.result = run_approved_purpose_candidate_ordering_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.reward = cls.records[0]
        cls.mismatch = cls.records[1]
        cls.comfort = cls.records[2]

    def test_valid_ordering_records_are_created(self):
        for record in self.records:
            result = validate_approved_purpose_candidate_ordering_record(record)

            self.assertTrue(result["valid"])
            self.assertEqual(record["record_type"], "approved_purpose_candidate_ordering_minimal")
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)

    def test_approach_or_reach_item_orders_positive_item_candidates(self):
        record = build_approved_purpose_candidate_ordering_record(self.sources[0])
        ordering = record["approved_purpose_ordering"]
        result = validate_approved_purpose_candidate_ordering_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual(result["approved_purpose"], "approach_or_reach_item")
        self.assertEqual(ordering["candidate_family"], "positive_item_interaction_candidates")
        self.assertEqual(ordering["candidate_actions_after_ordering"][0], "reach_front_item")
        self.assertEqual(ordering["primary_ranked_action"], "reach_front_item")

    def test_resolve_mismatch_orders_verification_before_retry(self):
        ordering = self.mismatch["approved_purpose_ordering"]
        result = validate_approved_purpose_candidate_ordering_record(self.mismatch)

        self.assertTrue(result["valid"])
        self.assertEqual(result["approved_purpose"], "resolve_mismatch")
        self.assertEqual(ordering["candidate_actions_after_ordering"][0], "observe_or_alternative_probe")
        self.assertLess(
            ordering["candidate_actions_after_ordering"].index("check_before_retry"),
            ordering["candidate_actions_after_ordering"].index("retry_same_action_without_check"),
        )

    def test_support_user_comfort_orders_bounded_low_pressure_support(self):
        ordering = self.comfort["approved_purpose_ordering"]
        result = validate_approved_purpose_candidate_ordering_record(self.comfort)

        self.assertTrue(result["valid"])
        self.assertEqual(result["approved_purpose"], "support_user_comfort")
        self.assertEqual(ordering["candidate_actions_after_ordering"][0], "offer_low_pressure_support")
        self.assertNotIn("force_user_happiness", ordering["candidate_actions_after_ordering"])

    def test_ordering_is_advisory_and_sandbox_only(self):
        for record in self.records:
            ordering = record["approved_purpose_ordering"]

            self.assertTrue(ordering["candidate_ordering_applied"])
            self.assertTrue(ordering["candidate_order_changed"])
            self.assertTrue(ordering["ordering_is_sandbox_only"])
            self.assertTrue(ordering["ordering_is_advisory"])
            self.assertFalse(ordering["selected_action_created"])
            self.assertFalse(ordering["final_action_created"])
            self.assertFalse(ordering["direct_command_created"])
            self.assertFalse(ordering["sandbox_action_executed"])

    def test_rollback_preview_restores_before_order(self):
        for record in self.records:
            self.assertTrue(record["rollback_preview"]["rollback_available"])
            self.assertEqual(
                record["rollback_preview"]["candidate_actions_restored"],
                record["approved_purpose_ordering"]["candidate_actions_before_ordering"],
            )
            self.assertFalse(record["rollback_preview"]["dirty_state_after_rollback"])

    def test_unknown_purpose_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["source_ordering_boundary"]["approved_purpose"] = "make_user_happy"

        result = validate_approved_purpose_candidate_ordering_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("approved_purpose_not_allowed", result["error_codes"])

    def test_ordering_not_applied_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["approved_purpose_ordering"]["candidate_ordering_applied"] = False

        result = validate_approved_purpose_candidate_ordering_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("approved_purpose_ordering_candidate_ordering_applied_not_expected", result["error_codes"])

    def test_primary_not_first_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["approved_purpose_ordering"]["candidate_actions_after_ordering"] = [
            "wait_or_observe",
            "reach_front_item",
            "step_toward_item",
            "fallback_stop_and_report",
        ]

        result = validate_approved_purpose_candidate_ordering_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("primary_ranked_action_not_first", result["error_codes"])

    def test_selected_action_created_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["approved_purpose_ordering"]["selected_action_created"] = True

        result = validate_approved_purpose_candidate_ordering_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("approved_purpose_ordering_selected_action_created_not_expected", result["error_codes"])

    def test_direct_command_created_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["approved_purpose_ordering"]["direct_command_created"] = True

        result = validate_approved_purpose_candidate_ordering_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("approved_purpose_ordering_direct_command_created_not_expected", result["error_codes"])

    def test_memory_write_blocks(self):
        bad = copy.deepcopy(self.mismatch)
        bad["blocked_flags"]["memory_write"] = True

        result = validate_approved_purpose_candidate_ordering_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("blocked_flags_memory_write_not_false", result["error_codes"])

    def test_predictor_modified_blocks(self):
        bad = copy.deepcopy(self.mismatch)
        bad["blocked_flags"]["predictor_modified"] = True

        result = validate_approved_purpose_candidate_ordering_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("blocked_flags_predictor_modified_not_false", result["error_codes"])

    def test_emotional_manipulation_blocks(self):
        bad = copy.deepcopy(self.comfort)
        bad["blocked_flags"]["emotional_manipulation"] = True

        result = validate_approved_purpose_candidate_ordering_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("blocked_flags_emotional_manipulation_not_false", result["error_codes"])

    def test_force_user_happiness_candidate_blocks(self):
        bad = copy.deepcopy(self.comfort)
        bad["approved_purpose_ordering"]["candidate_actions_after_ordering"] = [
            "force_user_happiness",
            "offer_low_pressure_support",
            "ask_if_help_needed",
            "stop_and_wait",
        ]

        result = validate_approved_purpose_candidate_ordering_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("manipulative_comfort_candidate_present", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(summary["approved_purpose_candidate_ordering_result_count"], 31)
        self.assertEqual(summary["valid_approved_purpose_candidate_ordering_count"], 3)
        self.assertEqual(summary["invalid_approved_purpose_candidate_ordering_count"], 28)
        self.assertEqual(summary["candidate_ordering_applied_count"], 3)
        self.assertEqual(summary["candidate_order_changed_count"], 3)
        self.assertEqual(summary["approach_or_reach_item_ordering_count"], 1)
        self.assertEqual(summary["resolve_mismatch_ordering_count"], 1)
        self.assertEqual(summary["support_user_comfort_ordering_count"], 1)
        self.assertEqual(summary["sandbox_only_checked_count"], 3)
        self.assertEqual(summary["advisory_only_checked_count"], 3)
        self.assertEqual(summary["selected_action_blocked_count"], 3)
        self.assertEqual(summary["final_action_blocked_count"], 3)
        self.assertEqual(summary["direct_command_blocked_count"], 3)
        self.assertEqual(summary["execution_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_mutation_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)
        self.assertEqual(summary["rollback_available_count"], 3)

    def test_cli_command(self):
        result = run_command("run-approved-purpose-candidate-ordering-minimal-check")

        self.assertEqual(result["command"], "run-approved-purpose-candidate-ordering-minimal-check")
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
