import copy
import unittest

from ashl_core.approved_purpose_sandbox_direct_command_approval_boundary_minimal import (
    run_approved_purpose_sandbox_direct_command_approval_boundary_minimal_check,
)
from ashl_core.approved_purpose_sandbox_direct_command_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_approved_purpose_sandbox_direct_command_record,
    run_approved_purpose_sandbox_direct_command_minimal_check,
    validate_approved_purpose_sandbox_direct_command_record,
)
from ashl_core.teaching_cli import run_command


class ApprovedPurposeSandboxDirectCommandMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_approved_purpose_sandbox_direct_command_approval_boundary_minimal_check()[
            "valid_records"
        ]
        cls.result = run_approved_purpose_sandbox_direct_command_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.reward = cls.records[0]
        cls.mismatch = cls.records[1]
        cls.comfort = cls.records[2]

    def test_valid_direct_command_records_are_created(self):
        for record in self.records:
            result = validate_approved_purpose_sandbox_direct_command_record(record)

            self.assertTrue(result["valid"])
            self.assertEqual(record["record_type"], "approved_purpose_sandbox_direct_command_minimal")
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)
            self.assertTrue(record["sandbox_direct_command"]["direct_command_created"])

    def test_approach_or_reach_item_creates_reach_front_command(self):
        record = build_approved_purpose_sandbox_direct_command_record(self.sources[0])
        command = record["sandbox_direct_command"]
        result = validate_approved_purpose_sandbox_direct_command_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual(result["approved_purpose"], "approach_or_reach_item")
        self.assertEqual(command["direct_command"], "sandbox.approved_purpose.reach_front_item")
        self.assertEqual(command["direct_command_scope"], "sandbox_only")

    def test_resolve_mismatch_creates_probe_command(self):
        command = self.mismatch["sandbox_direct_command"]
        result = validate_approved_purpose_sandbox_direct_command_record(self.mismatch)

        self.assertTrue(result["valid"])
        self.assertEqual(result["approved_purpose"], "resolve_mismatch")
        self.assertEqual(command["direct_command"], "sandbox.approved_purpose.observe_or_alternative_probe")

    def test_support_user_comfort_creates_low_pressure_support_command(self):
        command = self.comfort["sandbox_direct_command"]
        result = validate_approved_purpose_sandbox_direct_command_record(self.comfort)

        self.assertTrue(result["valid"])
        self.assertEqual(result["approved_purpose"], "support_user_comfort")
        self.assertEqual(command["direct_command"], "sandbox.approved_purpose.offer_low_pressure_support")

    def test_direct_command_does_not_execute(self):
        for record in self.records:
            command = record["sandbox_direct_command"]

            self.assertTrue(command["direct_command_created"])
            self.assertFalse(command["sandbox_action_executed"])
            self.assertFalse(command["execution_allowed_in_this_package"])
            self.assertTrue(command["future_execution_requires_separate_boundary"])

    def test_source_approval_boundary_is_preserved(self):
        source = self.reward["source_direct_command_approval_boundary"]

        self.assertTrue(source["source_validated"])
        self.assertTrue(source["future_direct_command_allowed"])
        self.assertFalse(source["source_direct_command_created_in_source_package"])
        self.assertEqual(
            source["candidate_for_future_direct_command"],
            "sandbox.approved_purpose.reach_front_item",
        )

    def test_rollback_removes_direct_command_without_dirty_state(self):
        rollback = self.reward["rollback_preview"]
        result = validate_approved_purpose_sandbox_direct_command_record(self.reward)

        self.assertTrue(result["rollback_available"])
        self.assertTrue(rollback["rollback_available"])
        self.assertTrue(rollback["direct_command_removed_on_rollback"])
        self.assertFalse(rollback["dirty_state_after_rollback"])
        self.assertFalse(rollback["persistent_update_performed"])

    def test_bad_source_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["source_direct_command_approval_boundary"]["source_validated"] = False

        result = validate_approved_purpose_sandbox_direct_command_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_validated_not_true", result["error_codes"])

    def test_direct_command_created_false_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["sandbox_direct_command"]["direct_command_created"] = False

        result = validate_approved_purpose_sandbox_direct_command_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("sandbox_direct_command_direct_command_created_not_expected", result["error_codes"])

    def test_wrong_direct_command_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["sandbox_direct_command"]["direct_command"] = "sandbox.approved_purpose.wait"

        result = validate_approved_purpose_sandbox_direct_command_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("sandbox_direct_command_direct_command_not_expected", result["error_codes"])

    def test_execution_blocks(self):
        for field, error in (
            ("sandbox_action_executed", "sandbox_direct_command_sandbox_action_executed_not_expected"),
            ("execution_allowed_in_this_package", "sandbox_direct_command_execution_allowed_in_this_package_not_expected"),
        ):
            bad = copy.deepcopy(self.reward)
            bad["sandbox_direct_command"][field] = True

            result = validate_approved_purpose_sandbox_direct_command_record(bad)

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

            result = validate_approved_purpose_sandbox_direct_command_record(bad)

            self.assertFalse(result["valid"])
            self.assertIn(f"blocked_flags_{field}_not_false", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(summary["direct_command_result_count"], 29)
        self.assertEqual(summary["valid_direct_command_count"], 3)
        self.assertEqual(summary["invalid_direct_command_count"], 26)
        self.assertEqual(summary["direct_command_created_count"], 3)
        self.assertEqual(summary["approach_or_reach_item_direct_command_count"], 1)
        self.assertEqual(summary["resolve_mismatch_direct_command_count"], 1)
        self.assertEqual(summary["support_user_comfort_direct_command_count"], 1)
        self.assertEqual(summary["sandbox_only_direct_command_count"], 3)
        self.assertEqual(summary["execution_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_mutation_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)
        self.assertEqual(summary["rollback_available_count"], 3)

    def test_cli_command(self):
        result = run_command("run-approved-purpose-sandbox-direct-command-minimal-check")

        self.assertEqual(result["command"], "run-approved-purpose-sandbox-direct-command-minimal-check")
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
