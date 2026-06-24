import copy
import unittest

from ashl_core.sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_approval_boundary_minimal import (
    run_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_approval_boundary_minimal_check,
)
from ashl_core.sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_record,
    run_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_minimal_check,
    validate_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_record,
)
from ashl_core.teaching_cli import run_command


class SandboxCandidateOrderingArbitrationReorderedCandidateDirectCommandExecutionMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = (
            run_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_approval_boundary_minimal_check()[
                "valid_records"
            ]
        )
        cls.result = run_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.reach = cls.records[0]
        cls.wait = cls.records[1]
        cls.probe = cls.records[2]

    def assert_invalid(self, record: dict) -> list[str]:
        result = validate_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_record(
            record
        )
        self.assertFalse(result["valid"])
        self.assertTrue(result["error_codes"])
        return result["error_codes"]

    def test_valid_executions_are_created(self):
        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(len(self.records), 3)
        for record in self.records:
            result = validate_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_record(
                record
            )

            self.assertTrue(result["valid"], result["error_codes"])
            self.assertEqual(
                record["record_type"],
                "sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_minimal",
            )
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)
            self.assertTrue(record["sandbox_execution"]["execution_created"])
            self.assertTrue(record["sandbox_execution"]["direct_command_executed"])
            self.assertTrue(record["sandbox_execution"]["sandbox_action_executed"])

    def test_boundary_versions_are_b161_to_b162(self):
        boundary = self.result["boundary"]

        self.assertEqual(boundary["boundary_index_version_before"], "2026-06-09-b161")
        self.assertEqual(boundary["boundary_index_version_after"], "2026-06-09-b162")

    def test_default_builder_uses_b161_execution_boundary_source(self):
        record = build_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_record()
        source = record["source_execution_approval_boundary"]
        execution = record["sandbox_execution"]

        self.assertEqual(source["source_boundary_index"], "2026-06-09-b161")
        self.assertTrue(source["future_execution_allowed"])
        self.assertEqual(source["execution_scope"], "same_session_sandbox_only")
        self.assertEqual(execution["direct_command"], source["candidate_for_future_execution"])

    def test_reach_front_item_command_executes_once(self):
        record = build_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_record(
            self.sources[0]
        )
        execution = record["sandbox_execution"]
        result = validate_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_record(
            record
        )

        self.assertTrue(result["valid"], result["error_codes"])
        self.assertEqual(result["scenario_id"], "item_reachable_feedback_prioritizes_reach")
        self.assertEqual(execution["direct_command"], "sandbox.arbitration.reach_front_item")
        self.assertEqual(execution["command_payload"]["operation"], "reach_front_item")
        self.assertEqual(execution["execution_count"], 1)
        self.assertEqual(execution["execution_budget"], 1)
        self.assertEqual(execution["budget_remaining"], 0)

    def test_wait_or_observe_command_executes_once(self):
        execution = self.wait["sandbox_execution"]
        result = validate_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_record(
            self.wait
        )

        self.assertTrue(result["valid"], result["error_codes"])
        self.assertEqual(result["scenario_id"], "item_not_afforded_blocks_feedback_priority")
        self.assertEqual(execution["direct_command"], "sandbox.arbitration.wait_or_observe")
        self.assertEqual(execution["command_payload"]["operation"], "wait_or_observe")

    def test_probe_command_executes_once(self):
        execution = self.probe["sandbox_execution"]
        result = validate_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_record(
            self.probe
        )

        self.assertTrue(result["valid"], result["error_codes"])
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

    def test_execution_does_not_change_scores_ordering_or_create_actions(self):
        for record in self.records:
            execution = record["sandbox_execution"]

            self.assertFalse(execution["candidate_scores_changed"])
            self.assertFalse(execution["runtime_next_cycle_candidate_ordering_changed"])
            self.assertFalse(execution["new_selected_action_created"])
            self.assertFalse(execution["new_final_action_created"])
            self.assertFalse(execution["new_direct_command_created"])

    def test_source_execution_boundary_is_preserved(self):
        for record in self.records:
            source = record["source_execution_approval_boundary"]

            self.assertTrue(source["source_validated"])
            self.assertEqual(source["source_boundary_index"], "2026-06-09-b161")
            self.assertTrue(source["future_execution_allowed"])
            self.assertFalse(source["source_sandbox_execution_created_in_source_package"])
            self.assertFalse(source["source_execution_result_created_in_source_package"])
            self.assertFalse(source["source_new_outcome_observation_created_in_source_package"])
            self.assertTrue(source["source_arbitration_rules_preserved"])

    def test_bad_source_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["source_execution_approval_boundary"]["source_validated"] = False

        errors = self.assert_invalid(bad)

        self.assertIn("source_validated_not_true", errors)

    def test_source_already_executed_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["source_execution_approval_boundary"]["source_sandbox_execution_created_in_source_package"] = True

        errors = self.assert_invalid(bad)

        self.assertIn("source_source_sandbox_execution_created_in_source_package_not_expected", errors)

    def test_wrong_execution_scope_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["sandbox_execution"]["execution_scope"] = "production"

        errors = self.assert_invalid(bad)

        self.assertIn("sandbox_execution_execution_scope_not_expected", errors)

    def test_execution_count_must_be_one(self):
        bad = copy.deepcopy(self.reach)
        bad["sandbox_execution"]["execution_count"] = 2

        errors = self.assert_invalid(bad)

        self.assertIn("sandbox_execution_execution_count_not_expected", errors)

    def test_execution_result_required_but_outcome_forbidden(self):
        bad_result = copy.deepcopy(self.reach)
        bad_result["sandbox_execution"]["execution_result_created"] = False
        result_errors = self.assert_invalid(bad_result)

        bad_outcome = copy.deepcopy(self.reach)
        bad_outcome["sandbox_execution"]["outcome_observation_created"] = True
        outcome_errors = self.assert_invalid(bad_outcome)

        self.assertIn("sandbox_execution_execution_result_created_not_expected", result_errors)
        self.assertIn("sandbox_execution_outcome_observation_created_not_expected", outcome_errors)

    def test_feedback_scores_runtime_and_action_creation_block(self):
        for field in (
            "feedback_loop_created",
            "candidate_scores_changed",
            "runtime_next_cycle_candidate_ordering_changed",
            "new_selected_action_created",
            "new_final_action_created",
            "new_direct_command_created",
        ):
            bad = copy.deepcopy(self.wait)
            bad["sandbox_execution"][field] = True

            errors = self.assert_invalid(bad)

            self.assertIn(f"sandbox_execution_{field}_not_expected", errors)

    def test_memory_predictor_direct_feed_and_proof_flags_block(self):
        for field in (
            "memory_write",
            "retention_write",
            "predictor_read_enabled",
            "predictor_influence_enabled",
            "predictor_modified",
            "direct_endocrine_feed",
            "direct_tendency_feed",
            "proof_of_learning_claim",
        ):
            bad = copy.deepcopy(self.probe)
            bad["blocked_flags"][field] = True

            errors = self.assert_invalid(bad)

            self.assertIn(f"blocked_flags_{field}_not_false", errors)

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(summary["execution_result_count"], 88)
        self.assertEqual(summary["valid_execution_count"], 3)
        self.assertEqual(summary["invalid_execution_count"], 85)
        self.assertEqual(summary["sandbox_execution_created_count"], 3)
        self.assertEqual(summary["direct_command_executed_count"], 3)
        self.assertEqual(summary["sandbox_action_executed_count"], 3)
        self.assertEqual(summary["same_session_sandbox_only_execution_count"], 3)
        self.assertEqual(summary["execution_budget_checked_count"], 3)
        self.assertEqual(summary["execution_result_created_count"], 3)
        self.assertEqual(summary["source_execution_boundary_preserved_count"], 3)
        self.assertEqual(summary["source_reordering_preserved_count"], 3)
        self.assertEqual(summary["reach_front_item_execution_count"], 1)
        self.assertEqual(summary["wait_or_observe_execution_count"], 1)
        self.assertEqual(summary["observe_or_alternative_probe_execution_count"], 1)
        self.assertEqual(summary["outcome_observation_blocked_count"], 3)
        self.assertEqual(summary["feedback_loop_blocked_count"], 3)
        self.assertEqual(summary["candidate_scores_blocked_count"], 3)
        self.assertEqual(summary["runtime_next_cycle_blocked_count"], 3)
        self.assertEqual(summary["action_creation_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_use_blocked_count"], 3)
        self.assertEqual(summary["direct_feed_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)

    def test_cli_command(self):
        result = run_command(
            "run-sandbox-candidate-ordering-arbitration-reordered-candidate-direct-command-execution-minimal-check"
        )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(
            result["flow"],
            "sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_execution_minimal_v0",
        )


if __name__ == "__main__":
    unittest.main()
