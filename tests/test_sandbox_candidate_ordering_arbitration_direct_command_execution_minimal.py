import copy
import unittest

from ashl_core.sandbox_candidate_ordering_arbitration_direct_command_execution_approval_boundary_minimal import (
    run_sandbox_candidate_ordering_arbitration_direct_command_execution_approval_boundary_minimal_check,
)
from ashl_core.sandbox_candidate_ordering_arbitration_direct_command_execution_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_sandbox_candidate_ordering_arbitration_direct_command_execution_record,
    run_sandbox_candidate_ordering_arbitration_direct_command_execution_minimal_check,
    validate_sandbox_candidate_ordering_arbitration_direct_command_execution_record,
)
from ashl_core.teaching_cli import run_command


class SandboxCandidateOrderingArbitrationDirectCommandExecutionMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_sandbox_candidate_ordering_arbitration_direct_command_execution_approval_boundary_minimal_check()[
            "valid_records"
        ]
        cls.result = run_sandbox_candidate_ordering_arbitration_direct_command_execution_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.reach = cls.records[0]
        cls.wait = cls.records[1]
        cls.probe = cls.records[2]

    def test_valid_executions_are_created(self):
        for record in self.records:
            result = validate_sandbox_candidate_ordering_arbitration_direct_command_execution_record(record)

            self.assertTrue(result["valid"])
            self.assertEqual(
                record["record_type"],
                "sandbox_candidate_ordering_arbitration_direct_command_execution_minimal",
            )
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)
            self.assertTrue(record["sandbox_execution"]["execution_created"])
            self.assertTrue(record["sandbox_execution"]["direct_command_executed"])
            self.assertTrue(record["sandbox_execution"]["sandbox_action_executed"])

    def test_reach_front_item_command_executes_once(self):
        record = build_sandbox_candidate_ordering_arbitration_direct_command_execution_record(self.sources[0])
        execution = record["sandbox_execution"]
        result = validate_sandbox_candidate_ordering_arbitration_direct_command_execution_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual(result["scenario_id"], "item_reachable_feedback_prioritizes_reach")
        self.assertEqual(execution["direct_command"], "sandbox.arbitration.reach_front_item")
        self.assertEqual(execution["command_payload"]["operation"], "reach_front_item")
        self.assertEqual(execution["execution_count"], 1)
        self.assertEqual(execution["execution_budget"], 1)
        self.assertEqual(execution["budget_remaining"], 0)

    def test_wait_or_observe_command_executes_once(self):
        execution = self.wait["sandbox_execution"]
        result = validate_sandbox_candidate_ordering_arbitration_direct_command_execution_record(self.wait)

        self.assertTrue(result["valid"])
        self.assertEqual(result["scenario_id"], "item_not_afforded_blocks_feedback_priority")
        self.assertEqual(execution["direct_command"], "sandbox.arbitration.wait_or_observe")
        self.assertEqual(execution["command_payload"]["operation"], "wait_or_observe")

    def test_probe_command_executes_once(self):
        execution = self.probe["sandbox_execution"]
        result = validate_sandbox_candidate_ordering_arbitration_direct_command_execution_record(self.probe)

        self.assertTrue(result["valid"])
        self.assertEqual(result["scenario_id"], "mismatch_feedback_outranks_retry_tendency")
        self.assertEqual(execution["direct_command"], "sandbox.arbitration.observe_or_alternative_probe")
        self.assertEqual(execution["command_payload"]["operation"], "observe_or_alternative_probe")

    def test_execution_does_not_observe_outcome_or_create_feedback(self):
        for record in self.records:
            execution = record["sandbox_execution"]

            self.assertTrue(execution["execution_result_created"])
            self.assertFalse(execution["outcome_observation_created"])
            self.assertFalse(execution["feedback_loop_created"])
            self.assertTrue(execution["future_outcome_observation_requires_separate_boundary"])
            self.assertTrue(execution["future_feedback_requires_separate_boundary"])
            self.assertFalse(record["blocked_flags"]["feedback_loop_created"])

    def test_bad_source_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["source_execution_approval_boundary"]["source_validated"] = False

        result = validate_sandbox_candidate_ordering_arbitration_direct_command_execution_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_validated_not_true", result["error_codes"])

    def test_wrong_scope_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["sandbox_execution"]["execution_scope"] = "production"

        result = validate_sandbox_candidate_ordering_arbitration_direct_command_execution_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("sandbox_execution_execution_scope_not_expected", result["error_codes"])

    def test_execution_count_must_be_one(self):
        bad = copy.deepcopy(self.reach)
        bad["sandbox_execution"]["execution_count"] = 2

        result = validate_sandbox_candidate_ordering_arbitration_direct_command_execution_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("sandbox_execution_execution_count_not_expected", result["error_codes"])

    def test_outcome_observation_true_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["sandbox_execution"]["outcome_observation_created"] = True

        result = validate_sandbox_candidate_ordering_arbitration_direct_command_execution_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("sandbox_execution_outcome_observation_created_not_expected", result["error_codes"])

    def test_feedback_memory_predictor_direct_feed_and_proof_flags_block(self):
        for field in (
            "feedback_loop_created",
            "memory_write",
            "predictor_modified",
            "direct_endocrine_feed",
            "direct_tendency_feed",
            "proof_of_learning_claim",
        ):
            bad = copy.deepcopy(self.probe)
            bad["blocked_flags"][field] = True

            result = validate_sandbox_candidate_ordering_arbitration_direct_command_execution_record(bad)

            self.assertFalse(result["valid"])
            self.assertIn(f"blocked_flags_{field}_not_false", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(summary["execution_result_count"], 38)
        self.assertEqual(summary["valid_execution_count"], 3)
        self.assertEqual(summary["invalid_execution_count"], 35)
        self.assertEqual(summary["sandbox_execution_created_count"], 3)
        self.assertEqual(summary["direct_command_executed_count"], 3)
        self.assertEqual(summary["sandbox_action_executed_count"], 3)
        self.assertEqual(summary["execution_result_created_count"], 3)
        self.assertEqual(summary["reach_front_item_execution_count"], 1)
        self.assertEqual(summary["wait_or_observe_execution_count"], 1)
        self.assertEqual(summary["observe_or_alternative_probe_execution_count"], 1)
        self.assertEqual(summary["outcome_observation_blocked_count"], 3)
        self.assertEqual(summary["feedback_loop_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_use_blocked_count"], 3)
        self.assertEqual(summary["direct_feed_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)

    def test_cli_command(self):
        result = run_command("run-sandbox-candidate-ordering-arbitration-direct-command-execution-minimal-check")

        self.assertEqual(
            result["command"],
            "run-sandbox-candidate-ordering-arbitration-direct-command-execution-minimal-check",
        )
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
