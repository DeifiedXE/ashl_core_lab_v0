import copy
import unittest

from ashl_core.sandbox_candidate_ordering_arbitration_reordered_candidate_selected_action_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_sandbox_candidate_ordering_arbitration_reordered_candidate_selected_action_record,
    run_sandbox_candidate_ordering_arbitration_reordered_candidate_selected_action_minimal_check,
    validate_sandbox_candidate_ordering_arbitration_reordered_candidate_selected_action_record,
)
from ashl_core.sandbox_candidate_ordering_arbitration_reordered_candidate_to_selected_action_approval_boundary_minimal import (
    run_sandbox_candidate_ordering_arbitration_reordered_candidate_to_selected_action_approval_boundary_minimal_check,
)
from ashl_core.teaching_cli import run_command


class SandboxCandidateOrderingArbitrationReorderedCandidateSelectedActionMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = (
            run_sandbox_candidate_ordering_arbitration_reordered_candidate_to_selected_action_approval_boundary_minimal_check()[
                "valid_records"
            ]
        )
        cls.result = run_sandbox_candidate_ordering_arbitration_reordered_candidate_selected_action_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.reach = cls.records[0]
        cls.wait = cls.records[1]
        cls.probe = cls.records[2]

    def test_valid_selected_action_records_are_created(self):
        for record in self.records:
            result = validate_sandbox_candidate_ordering_arbitration_reordered_candidate_selected_action_record(
                record
            )

            self.assertTrue(result["valid"], result["error_codes"])
            self.assertEqual(
                record["record_type"],
                "sandbox_candidate_ordering_arbitration_reordered_candidate_selected_action_minimal",
            )
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)
            self.assertTrue(record["sandbox_selected_action"]["selected_action_created"])
            self.assertEqual(record["sandbox_selected_action"]["selected_action_scope"], "same_session_sandbox_only")

    def test_reach_reordered_candidate_becomes_selected_action(self):
        record = build_sandbox_candidate_ordering_arbitration_reordered_candidate_selected_action_record(
            self.sources[0]
        )
        selected = record["sandbox_selected_action"]
        result = validate_sandbox_candidate_ordering_arbitration_reordered_candidate_selected_action_record(record)

        self.assertTrue(result["valid"], result["error_codes"])
        self.assertEqual(result["scenario_id"], "item_reachable_feedback_prioritizes_reach")
        self.assertEqual(selected["selected_action"], "reach_front_item")

    def test_wait_reordered_candidate_becomes_selected_action(self):
        selected = self.wait["sandbox_selected_action"]
        result = validate_sandbox_candidate_ordering_arbitration_reordered_candidate_selected_action_record(
            self.wait
        )

        self.assertTrue(result["valid"], result["error_codes"])
        self.assertEqual(result["scenario_id"], "item_not_afforded_blocks_feedback_priority")
        self.assertEqual(selected["selected_action"], "wait_or_observe")

    def test_probe_reordered_candidate_becomes_selected_action(self):
        selected = self.probe["sandbox_selected_action"]
        result = validate_sandbox_candidate_ordering_arbitration_reordered_candidate_selected_action_record(
            self.probe
        )

        self.assertTrue(result["valid"], result["error_codes"])
        self.assertEqual(result["scenario_id"], "mismatch_feedback_outranks_retry_tendency")
        self.assertEqual(selected["selected_action"], "observe_or_alternative_probe")

    def test_selected_action_does_not_create_later_action_layers(self):
        for record in self.records:
            selected = record["sandbox_selected_action"]

            self.assertFalse(selected["final_action_created"])
            self.assertFalse(selected["direct_command_created"])
            self.assertFalse(selected["sandbox_execution_created"])
            self.assertFalse(selected["new_outcome_observation_created"])
            self.assertFalse(selected["execution_allowed_in_this_package"])

    def test_selected_action_does_not_change_scores_or_runtime_ordering(self):
        for record in self.records:
            selected = record["sandbox_selected_action"]

            self.assertFalse(selected["candidate_scores_changed"])
            self.assertFalse(selected["runtime_next_cycle_candidate_ordering_changed"])

    def test_source_approval_must_be_valid(self):
        bad = copy.deepcopy(self.reach)
        bad["source_selected_action_approval_boundary"]["source_validated"] = False

        result = validate_sandbox_candidate_ordering_arbitration_reordered_candidate_selected_action_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_validated_not_true", result["error_codes"])

    def test_source_must_allow_future_selected_action(self):
        bad = copy.deepcopy(self.reach)
        bad["source_selected_action_approval_boundary"]["future_selected_action_allowed"] = False

        result = validate_sandbox_candidate_ordering_arbitration_reordered_candidate_selected_action_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_future_selected_action_allowed_not_expected", result["error_codes"])

    def test_source_must_not_already_create_selected_action(self):
        bad = copy.deepcopy(self.reach)
        bad["source_selected_action_approval_boundary"]["source_selected_action_created_in_source_package"] = True

        result = validate_sandbox_candidate_ordering_arbitration_reordered_candidate_selected_action_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_source_selected_action_created_in_source_package_not_expected", result["error_codes"])

    def test_wrong_selected_action_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["sandbox_selected_action"]["selected_action"] = "wait_or_observe"

        result = validate_sandbox_candidate_ordering_arbitration_reordered_candidate_selected_action_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("sandbox_selected_action_selected_action_not_expected", result["error_codes"])

    def test_selected_action_not_created_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["sandbox_selected_action"]["selected_action_created"] = False

        result = validate_sandbox_candidate_ordering_arbitration_reordered_candidate_selected_action_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("sandbox_selected_action_selected_action_created_not_expected", result["error_codes"])

    def test_final_direct_execution_or_observation_true_blocks(self):
        for field in (
            "final_action_created",
            "direct_command_created",
            "sandbox_execution_created",
            "new_outcome_observation_created",
            "execution_allowed_in_this_package",
        ):
            bad = copy.deepcopy(self.reach)
            bad["sandbox_selected_action"][field] = True

            result = validate_sandbox_candidate_ordering_arbitration_reordered_candidate_selected_action_record(
                bad
            )

            self.assertFalse(result["valid"])
            self.assertIn(f"sandbox_selected_action_{field}_not_expected", result["error_codes"])

    def test_future_boundaries_remain_required(self):
        for field in (
            "future_final_action_requires_separate_boundary",
            "future_direct_command_requires_separate_boundary",
            "future_execution_requires_separate_boundary",
            "future_outcome_observation_requires_separate_boundary",
        ):
            bad = copy.deepcopy(self.reach)
            bad["sandbox_selected_action"][field] = False

            result = validate_sandbox_candidate_ordering_arbitration_reordered_candidate_selected_action_record(
                bad
            )

            self.assertFalse(result["valid"])
            self.assertIn(f"sandbox_selected_action_{field}_not_expected", result["error_codes"])

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

            result = validate_sandbox_candidate_ordering_arbitration_reordered_candidate_selected_action_record(
                bad
            )

            self.assertFalse(result["valid"])
            self.assertIn(f"blocked_flags_{field}_not_false", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(summary["selected_action_result_count"], 49)
        self.assertEqual(summary["valid_selected_action_count"], 3)
        self.assertEqual(summary["invalid_selected_action_count"], 46)
        self.assertEqual(summary["selected_action_created_count"], 3)
        self.assertEqual(summary["same_session_sandbox_only_count"], 3)
        self.assertEqual(summary["source_approval_preserved_count"], 3)
        self.assertEqual(summary["source_reordering_preserved_count"], 3)
        self.assertEqual(summary["reach_front_item_selected_count"], 1)
        self.assertEqual(summary["wait_or_observe_selected_count"], 1)
        self.assertEqual(summary["observe_or_alternative_probe_selected_count"], 1)
        self.assertEqual(summary["final_action_blocked_count"], 3)
        self.assertEqual(summary["direct_command_blocked_count"], 3)
        self.assertEqual(summary["execution_blocked_count"], 3)
        self.assertEqual(summary["outcome_observation_blocked_count"], 3)
        self.assertEqual(summary["candidate_scores_blocked_count"], 3)
        self.assertEqual(summary["runtime_next_cycle_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_use_blocked_count"], 3)
        self.assertEqual(summary["direct_feed_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)

    def test_cli_command(self):
        result = run_command(
            "run-sandbox-candidate-ordering-arbitration-reordered-candidate-selected-action-minimal-check"
        )

        self.assertEqual(
            result["command"],
            "run-sandbox-candidate-ordering-arbitration-reordered-candidate-selected-action-minimal-check",
        )
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
