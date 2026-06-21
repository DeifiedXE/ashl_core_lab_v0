import copy
import unittest

from ashl_core.approved_purpose_sandbox_direct_command_execution_approval_boundary_minimal import (
    run_approved_purpose_sandbox_direct_command_execution_approval_boundary_minimal_check,
)
from ashl_core.approved_purpose_sandbox_direct_command_execution_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_approved_purpose_sandbox_direct_command_execution_record,
    run_approved_purpose_sandbox_direct_command_execution_minimal_check,
    validate_approved_purpose_sandbox_direct_command_execution_record,
)
from ashl_core.teaching_cli import run_command


class ApprovedPurposeSandboxDirectCommandExecutionMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_approved_purpose_sandbox_direct_command_execution_approval_boundary_minimal_check()[
            "valid_records"
        ]
        cls.result = run_approved_purpose_sandbox_direct_command_execution_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.reward = cls.records[0]
        cls.mismatch = cls.records[1]
        cls.comfort = cls.records[2]

    def test_valid_executions_are_created(self):
        for record in self.records:
            result = validate_approved_purpose_sandbox_direct_command_execution_record(record)

            self.assertTrue(result["valid"])
            self.assertEqual(record["record_type"], "approved_purpose_sandbox_direct_command_execution_minimal")
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)
            self.assertTrue(record["sandbox_execution"]["execution_created"])
            self.assertTrue(record["sandbox_execution"]["direct_command_executed"])

    def test_reach_front_command_executes_once(self):
        record = build_approved_purpose_sandbox_direct_command_execution_record(self.sources[0])
        execution = record["sandbox_execution"]
        result = validate_approved_purpose_sandbox_direct_command_execution_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual(result["approved_purpose"], "approach_or_reach_item")
        self.assertEqual(execution["direct_command"], "sandbox.approved_purpose.reach_front_item")
        self.assertEqual(execution["command_payload"]["operation"], "reach_front_item")
        self.assertEqual(execution["execution_count"], 1)
        self.assertEqual(execution["execution_budget"], 1)
        self.assertEqual(execution["budget_remaining"], 0)

    def test_probe_command_executes_once(self):
        execution = self.mismatch["sandbox_execution"]
        result = validate_approved_purpose_sandbox_direct_command_execution_record(self.mismatch)

        self.assertTrue(result["valid"])
        self.assertEqual(result["approved_purpose"], "resolve_mismatch")
        self.assertEqual(execution["direct_command"], "sandbox.approved_purpose.observe_or_alternative_probe")
        self.assertEqual(execution["command_payload"]["operation"], "observe_or_alternative_probe")

    def test_support_command_executes_once(self):
        execution = self.comfort["sandbox_execution"]
        result = validate_approved_purpose_sandbox_direct_command_execution_record(self.comfort)

        self.assertTrue(result["valid"])
        self.assertEqual(result["approved_purpose"], "support_user_comfort")
        self.assertEqual(execution["direct_command"], "sandbox.approved_purpose.offer_low_pressure_support")
        self.assertEqual(execution["command_payload"]["operation"], "offer_low_pressure_support")

    def test_execution_does_not_observe_outcome_or_create_feedback(self):
        for record in self.records:
            execution = record["sandbox_execution"]

            self.assertTrue(execution["execution_result_created"])
            self.assertFalse(execution["outcome_observation_created"])
            self.assertTrue(execution["future_outcome_observation_requires_separate_boundary"])
            self.assertTrue(execution["future_feedback_requires_separate_boundary"])
            self.assertFalse(record["blocked_flags"]["feedback_loop_created"])

    def test_bad_source_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["source_execution_approval_boundary"]["source_validated"] = False

        result = validate_approved_purpose_sandbox_direct_command_execution_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_validated_not_true", result["error_codes"])

    def test_wrong_scope_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["sandbox_execution"]["execution_scope"] = "production"

        result = validate_approved_purpose_sandbox_direct_command_execution_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("sandbox_execution_execution_scope_not_expected", result["error_codes"])

    def test_execution_count_must_be_one(self):
        bad = copy.deepcopy(self.reward)
        bad["sandbox_execution"]["execution_count"] = 2

        result = validate_approved_purpose_sandbox_direct_command_execution_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("sandbox_execution_execution_count_not_expected", result["error_codes"])

    def test_outcome_observation_true_blocks(self):
        bad = copy.deepcopy(self.reward)
        bad["sandbox_execution"]["outcome_observation_created"] = True

        result = validate_approved_purpose_sandbox_direct_command_execution_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("sandbox_execution_outcome_observation_created_not_expected", result["error_codes"])

    def test_memory_predictor_manipulation_and_proof_flags_block(self):
        for field in (
            "memory_write",
            "predictor_modified",
            "emotional_manipulation",
            "proof_of_learning_claim",
        ):
            bad = copy.deepcopy(self.comfort)
            bad["blocked_flags"][field] = True

            result = validate_approved_purpose_sandbox_direct_command_execution_record(bad)

            self.assertFalse(result["valid"])
            self.assertIn(f"blocked_flags_{field}_not_false", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(summary["execution_result_count"], 34)
        self.assertEqual(summary["valid_execution_count"], 3)
        self.assertEqual(summary["invalid_execution_count"], 31)
        self.assertEqual(summary["sandbox_execution_created_count"], 3)
        self.assertEqual(summary["direct_command_executed_count"], 3)
        self.assertEqual(summary["execution_result_created_count"], 3)
        self.assertEqual(summary["approach_or_reach_item_execution_count"], 1)
        self.assertEqual(summary["resolve_mismatch_execution_count"], 1)
        self.assertEqual(summary["support_user_comfort_execution_count"], 1)
        self.assertEqual(summary["outcome_observation_blocked_count"], 3)
        self.assertEqual(summary["feedback_loop_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_mutation_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)

    def test_cli_command(self):
        result = run_command("run-approved-purpose-sandbox-direct-command-execution-minimal-check")

        self.assertEqual(
            result["command"],
            "run-approved-purpose-sandbox-direct-command-execution-minimal-check",
        )
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
