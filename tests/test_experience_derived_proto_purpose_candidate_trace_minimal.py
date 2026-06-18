import copy
import unittest

from ashl_core.experience_derived_proto_purpose_candidate_trace_minimal import (
    run_experience_derived_proto_purpose_candidate_trace_minimal_check,
    validate_experience_derived_proto_purpose_candidate_trace,
)
from ashl_core.teaching_cli import run_command


class ExperienceDerivedProtoPurposeCandidateTraceMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = run_experience_derived_proto_purpose_candidate_trace_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.reward = cls.records[0]
        cls.mismatch = cls.records[1]
        cls.comfort = cls.records[2]

    def test_valid_proto_purpose_candidate_traces_are_created(self):
        for record in self.records:
            result = validate_experience_derived_proto_purpose_candidate_trace(record)

            self.assertTrue(result["valid"])
            self.assertEqual(record["trace_type"], "experience_derived_proto_purpose_candidate_trace")
            self.assertEqual(record["trace_mode"], "proto_purpose_trace_only")

    def test_reward_experience_creates_approach_or_reach_item_proto_purpose(self):
        result = validate_experience_derived_proto_purpose_candidate_trace(self.reward)

        self.assertTrue(result["valid"])
        self.assertEqual(result["experience_type"], "reward_experience")
        self.assertEqual(result["proto_purpose"], "approach_or_reach_item")
        self.assertEqual(
            result["ideal_expected_state"],
            "reachable_positive_item_contact_under_approved_purpose",
        )

    def test_prediction_error_resolution_creates_resolve_mismatch_proto_purpose(self):
        result = validate_experience_derived_proto_purpose_candidate_trace(self.mismatch)

        self.assertTrue(result["valid"])
        self.assertEqual(result["experience_type"], "prediction_error_resolution_experience")
        self.assertEqual(result["proto_purpose"], "resolve_mismatch")
        self.assertEqual(result["ideal_expected_state"], "uncertainty_is_lower")

    def test_comfort_settling_creates_support_user_comfort_proto_purpose(self):
        result = validate_experience_derived_proto_purpose_candidate_trace(self.comfort)

        self.assertTrue(result["valid"])
        self.assertEqual(result["experience_type"], "comfort_settling_experience")
        self.assertEqual(result["proto_purpose"], "support_user_comfort")
        self.assertEqual(result["ideal_expected_state"], "user_or_system_state_more_settled")

    def test_requires_purpose_approval_and_blocks_action_authority(self):
        for record in self.records:
            approval = record["approval_boundary"]
            candidate = record["proto_purpose_candidate"]

            self.assertTrue(approval["requires_purpose_approval"])
            self.assertFalse(approval["approved_purpose_created"])
            self.assertFalse(approval["action_authority_granted"])
            self.assertFalse(approval["candidate_ordering_allowed"])
            self.assertFalse(candidate["action_authority"])

    def test_approved_purpose_created_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["approval_boundary"]["approved_purpose_created"] = True

        result = validate_experience_derived_proto_purpose_candidate_trace(bad)

        self.assertFalse(result["valid"])
        self.assertIn("approved_purpose_created_not_false", result["error_codes"])

    def test_experience_directly_creates_purpose_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["experience_source"]["experience_directly_creates_purpose"] = True

        result = validate_experience_derived_proto_purpose_candidate_trace(bad)

        self.assertFalse(result["valid"])
        self.assertIn("experience_directly_creates_purpose_not_false", result["error_codes"])

    def test_gap_missing_blocks(self):
        bad = copy.deepcopy(self.mismatch)
        bad["gap_assessment"]["gap_detected"] = False

        result = validate_experience_derived_proto_purpose_candidate_trace(bad)

        self.assertFalse(result["valid"])
        self.assertIn("gap_detected_not_true", result["error_codes"])
        self.assertIn("proto_purpose_requires_gap", result["error_codes"])

    def test_wrong_case_pairing_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["proto_purpose_candidate"]["proto_purpose"] = "support_user_comfort"

        result = validate_experience_derived_proto_purpose_candidate_trace(bad)

        self.assertFalse(result["valid"])
        self.assertIn("case_proto_purpose_mismatch", result["error_codes"])

    def test_candidate_ordering_allowed_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["approval_boundary"]["candidate_ordering_allowed"] = True

        result = validate_experience_derived_proto_purpose_candidate_trace(bad)

        self.assertFalse(result["valid"])
        self.assertIn("candidate_ordering_allowed_not_false", result["error_codes"])

    def test_selected_action_created_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["blocked_flags"]["selected_action_created"] = True

        result = validate_experience_derived_proto_purpose_candidate_trace(bad)

        self.assertFalse(result["valid"])
        self.assertIn("blocked_flags_selected_action_created_not_false", result["error_codes"])

    def test_memory_write_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["blocked_flags"]["memory_write"] = True

        result = validate_experience_derived_proto_purpose_candidate_trace(bad)

        self.assertFalse(result["valid"])
        self.assertIn("blocked_flags_memory_write_not_false", result["error_codes"])

    def test_predictor_modified_blocks(self):
        bad = copy.deepcopy(self.mismatch)
        bad["blocked_flags"]["predictor_modified"] = True

        result = validate_experience_derived_proto_purpose_candidate_trace(bad)

        self.assertFalse(result["valid"])
        self.assertIn("blocked_flags_predictor_modified_not_false", result["error_codes"])

    def test_user_happiness_claim_blocks(self):
        bad = copy.deepcopy(self.comfort)
        bad["blocked_flags"]["user_happiness_claim"] = True

        result = validate_experience_derived_proto_purpose_candidate_trace(bad)

        self.assertFalse(result["valid"])
        self.assertIn("blocked_flags_user_happiness_claim_not_false", result["error_codes"])

    def test_emotional_manipulation_blocks(self):
        bad = copy.deepcopy(self.comfort)
        bad["blocked_flags"]["emotional_manipulation"] = True

        result = validate_experience_derived_proto_purpose_candidate_trace(bad)

        self.assertFalse(result["valid"])
        self.assertIn("blocked_flags_emotional_manipulation_not_false", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(summary["proto_purpose_candidate_trace_result_count"], 29)
        self.assertEqual(summary["valid_proto_purpose_candidate_trace_count"], 3)
        self.assertEqual(summary["invalid_proto_purpose_candidate_trace_count"], 26)
        self.assertEqual(summary["reward_experience_trace_count"], 1)
        self.assertEqual(summary["prediction_error_resolution_trace_count"], 1)
        self.assertEqual(summary["comfort_settling_trace_count"], 1)
        self.assertEqual(summary["approach_or_reach_item_proto_purpose_count"], 1)
        self.assertEqual(summary["resolve_mismatch_proto_purpose_count"], 1)
        self.assertEqual(summary["support_user_comfort_proto_purpose_count"], 1)
        self.assertEqual(summary["requires_purpose_approval_count"], 3)
        self.assertEqual(summary["approved_purpose_blocked_count"], 3)
        self.assertEqual(summary["action_authority_blocked_count"], 3)
        self.assertEqual(summary["action_creation_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_mutation_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)

    def test_cli_command(self):
        result = run_command("run-experience-derived-proto-purpose-candidate-trace-minimal-check")

        self.assertEqual(
            result["command"],
            "run-experience-derived-proto-purpose-candidate-trace-minimal-check",
        )
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()

