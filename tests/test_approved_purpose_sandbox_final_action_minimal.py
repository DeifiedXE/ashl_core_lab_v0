import copy
import unittest

from ashl_core.approved_purpose_sandbox_final_action_approval_boundary_minimal import (
    run_approved_purpose_sandbox_final_action_approval_boundary_minimal_check,
)
from ashl_core.approved_purpose_sandbox_final_action_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_approved_purpose_sandbox_final_action_record,
    run_approved_purpose_sandbox_final_action_minimal_check,
    validate_approved_purpose_sandbox_final_action_record,
)
from ashl_core.teaching_cli import run_command


class ApprovedPurposeSandboxFinalActionMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_approved_purpose_sandbox_final_action_approval_boundary_minimal_check()[
            "valid_records"
        ]
        cls.result = run_approved_purpose_sandbox_final_action_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.reward = cls.records[0]
        cls.mismatch = cls.records[1]
        cls.comfort = cls.records[2]

    def test_valid_final_action_records_are_created(self):
        for record in self.records:
            result = validate_approved_purpose_sandbox_final_action_record(record)

            self.assertTrue(result["valid"])
            self.assertEqual(record["record_type"], "approved_purpose_sandbox_final_action_minimal")
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)
            self.assertTrue(record["sandbox_final_action"]["final_action_created"])

    def test_approach_or_reach_item_finalizes_reach_front_item(self):
        record = build_approved_purpose_sandbox_final_action_record(self.sources[0])
        final = record["sandbox_final_action"]
        result = validate_approved_purpose_sandbox_final_action_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual(result["approved_purpose"], "approach_or_reach_item")
        self.assertEqual(final["final_action"], "reach_front_item")
        self.assertEqual(final["final_action_scope"], "sandbox_only")

    def test_resolve_mismatch_finalizes_probe(self):
        final = self.mismatch["sandbox_final_action"]
        result = validate_approved_purpose_sandbox_final_action_record(self.mismatch)

        self.assertTrue(result["valid"])
        self.assertEqual(result["approved_purpose"], "resolve_mismatch")
        self.assertEqual(final["final_action"], "observe_or_alternative_probe")

    def test_support_user_comfort_finalizes_low_pressure_support(self):
        final = self.comfort["sandbox_final_action"]
        result = validate_approved_purpose_sandbox_final_action_record(self.comfort)

        self.assertTrue(result["valid"])
        self.assertEqual(result["approved_purpose"], "support_user_comfort")
        self.assertEqual(final["final_action"], "offer_low_pressure_support")

    def test_final_action_does_not_command_or_execute(self):
        for record in self.records:
            final = record["sandbox_final_action"]

            self.assertTrue(final["final_action_created"])
            self.assertFalse(final["direct_command_created"])
            self.assertFalse(final["sandbox_action_executed"])
            self.assertFalse(final["execution_allowed_in_this_package"])
            self.assertTrue(final["future_direct_command_requires_separate_boundary"])
            self.assertTrue(final["future_execution_requires_separate_boundary"])

    def test_source_approval_boundary_is_preserved(self):
        source = self.reward["source_final_action_approval_boundary"]

        self.assertTrue(source["source_validated"])
        self.assertTrue(source["future_final_action_allowed"])
        self.assertFalse(source["source_final_action_created_in_source_package"])
        self.assertEqual(source["candidate_for_future_final_action"], "reach_front_item")

    def test_rollback_removes_final_action_without_dirty_state(self):
        rollback = self.reward["rollback_preview"]
        result = validate_approved_purpose_sandbox_final_action_record(self.reward)

        self.assertTrue(result["rollback_available"])
        self.assertTrue(rollback["rollback_available"])
        self.assertTrue(rollback["final_action_removed_on_rollback"])
        self.assertFalse(rollback["dirty_state_after_rollback"])
        self.assertFalse(rollback["persistent_update_performed"])

    def test_bad_source_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["source_final_action_approval_boundary"]["source_validated"] = False

        result = validate_approved_purpose_sandbox_final_action_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_validated_not_true", result["error_codes"])

    def test_final_action_created_false_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["sandbox_final_action"]["final_action_created"] = False

        result = validate_approved_purpose_sandbox_final_action_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("sandbox_final_action_final_action_created_not_expected", result["error_codes"])

    def test_wrong_final_action_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["sandbox_final_action"]["final_action"] = "wait_or_observe"

        result = validate_approved_purpose_sandbox_final_action_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("sandbox_final_action_final_action_not_expected", result["error_codes"])

    def test_direct_command_and_execution_block(self):
        for field, error in (
            ("direct_command_created", "sandbox_final_action_direct_command_created_not_expected"),
            ("sandbox_action_executed", "sandbox_final_action_sandbox_action_executed_not_expected"),
            ("execution_allowed_in_this_package", "sandbox_final_action_execution_allowed_in_this_package_not_expected"),
        ):
            bad = copy.deepcopy(self.reward)
            bad["sandbox_final_action"][field] = True

            result = validate_approved_purpose_sandbox_final_action_record(bad)

            self.assertFalse(result["valid"])
            self.assertIn(error, result["error_codes"])

    def test_memory_predictor_manipulation_and_proof_flags_block(self):
        for field in (
            "memory_write",
            "predictor_modified",
            "emotional_manipulation",
            "proof_of_learning_claim",
        ):
            bad = copy.deepcopy(self.comfort)
            bad["blocked_flags"][field] = True

            result = validate_approved_purpose_sandbox_final_action_record(bad)

            self.assertFalse(result["valid"])
            self.assertIn(f"blocked_flags_{field}_not_false", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(summary["final_action_result_count"], 30)
        self.assertEqual(summary["valid_final_action_count"], 3)
        self.assertEqual(summary["invalid_final_action_count"], 27)
        self.assertEqual(summary["final_action_created_count"], 3)
        self.assertEqual(summary["approach_or_reach_item_final_action_count"], 1)
        self.assertEqual(summary["resolve_mismatch_final_action_count"], 1)
        self.assertEqual(summary["support_user_comfort_final_action_count"], 1)
        self.assertEqual(summary["sandbox_only_final_action_count"], 3)
        self.assertEqual(summary["direct_command_blocked_count"], 3)
        self.assertEqual(summary["execution_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_mutation_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)
        self.assertEqual(summary["rollback_available_count"], 3)

    def test_cli_command(self):
        result = run_command("run-approved-purpose-sandbox-final-action-minimal-check")

        self.assertEqual(result["command"], "run-approved-purpose-sandbox-final-action-minimal-check")
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
