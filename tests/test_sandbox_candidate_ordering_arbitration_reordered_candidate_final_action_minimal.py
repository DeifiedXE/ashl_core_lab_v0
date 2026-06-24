import unittest
from copy import deepcopy

from ashl_core.sandbox_candidate_ordering_arbitration_reordered_candidate_final_action_approval_boundary_minimal import (
    run_sandbox_candidate_ordering_arbitration_reordered_candidate_final_action_approval_boundary_minimal_check,
)
from ashl_core.sandbox_candidate_ordering_arbitration_reordered_candidate_final_action_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_sandbox_candidate_ordering_arbitration_reordered_candidate_final_action_record,
    run_sandbox_candidate_ordering_arbitration_reordered_candidate_final_action_minimal_check,
    validate_sandbox_candidate_ordering_arbitration_reordered_candidate_final_action_record,
)
from ashl_core.teaching_cli import run_command


class SandboxCandidateOrderingArbitrationReorderedCandidateFinalActionMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = (
            run_sandbox_candidate_ordering_arbitration_reordered_candidate_final_action_approval_boundary_minimal_check()[
                "valid_records"
            ]
        )
        cls.result = run_sandbox_candidate_ordering_arbitration_reordered_candidate_final_action_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.reach = cls.records[0]
        cls.wait = cls.records[1]
        cls.probe = cls.records[2]

    def assert_invalid(self, record: dict) -> list[str]:
        result = validate_sandbox_candidate_ordering_arbitration_reordered_candidate_final_action_record(record)
        self.assertFalse(result["valid"])
        self.assertTrue(result["error_codes"])
        return result["error_codes"]

    def test_valid_final_actions_are_created(self):
        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(len(self.records), 3)
        for record in self.records:
            result = validate_sandbox_candidate_ordering_arbitration_reordered_candidate_final_action_record(record)
            self.assertTrue(result["valid"], result["error_codes"])
            self.assertEqual(
                record["record_type"],
                "sandbox_candidate_ordering_arbitration_reordered_candidate_final_action_minimal",
            )
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)

    def test_boundary_versions_are_b157_to_b158(self):
        boundary = self.result["boundary"]
        self.assertEqual(boundary["boundary_index_version_before"], "2026-06-09-b157")
        self.assertEqual(boundary["boundary_index_version_after"], "2026-06-09-b158")

    def test_default_builder_uses_reordered_final_action_approval_boundary_source(self):
        record = build_sandbox_candidate_ordering_arbitration_reordered_candidate_final_action_record()
        source = record["source_final_action_approval_boundary"]
        final = record["sandbox_final_action"]

        self.assertEqual(source["source_boundary_index"], "2026-06-09-b157")
        self.assertTrue(source["future_final_action_allowed"])
        self.assertEqual(final["final_action"], source["candidate_for_future_final_action"])
        self.assertEqual(final["final_action_source"], "reordered_candidate_final_action_approval_boundary")

    def test_reach_wait_and_probe_become_final_actions(self):
        self.assertEqual(self.reach["sandbox_final_action"]["final_action"], "reach_front_item")
        self.assertEqual(self.wait["sandbox_final_action"]["final_action"], "wait_or_observe")
        self.assertEqual(self.probe["sandbox_final_action"]["final_action"], "observe_or_alternative_probe")

    def test_source_approval_is_required(self):
        for record in self.records:
            source = record["source_final_action_approval_boundary"]

            self.assertTrue(source["source_validated"])
            self.assertEqual(source["source_boundary_index"], "2026-06-09-b157")
            self.assertTrue(source["future_final_action_allowed"])
            self.assertEqual(source["final_action_scope"], "same_session_sandbox_only")
            self.assertEqual(source["candidate_for_future_final_action"], source["selected_action"])
            self.assertFalse(source["source_final_action_created_in_source_package"])
            self.assertTrue(source["source_reordering_preserved"])
            self.assertTrue(source["same_purpose_only"])
            self.assertTrue(source["arbitration_rules_preserved"])

    def test_final_action_does_not_create_command_execution_or_observation(self):
        for record in self.records:
            final = record["sandbox_final_action"]

            self.assertTrue(final["final_action_created"])
            self.assertFalse(final["direct_command_created"])
            self.assertFalse(final["sandbox_execution_created"])
            self.assertFalse(final["new_outcome_observation_created"])
            self.assertFalse(final["execution_allowed_in_this_package"])
            self.assertTrue(final["future_direct_command_requires_separate_boundary"])
            self.assertTrue(final["future_execution_requires_separate_boundary"])
            self.assertTrue(final["future_outcome_observation_requires_separate_boundary"])

    def test_final_action_does_not_change_scores_runtime_ordering_or_feedback(self):
        for record in self.records:
            final = record["sandbox_final_action"]

            self.assertFalse(final["candidate_scores_changed"])
            self.assertFalse(final["runtime_next_cycle_candidate_ordering_changed"])
            self.assertFalse(final["feedback_loop_created"])

    def test_bad_source_blocks(self):
        bad = deepcopy(self.reach)
        bad["source_final_action_approval_boundary"]["source_validated"] = False

        errors = self.assert_invalid(bad)

        self.assertIn("source_validated_not_true", errors)

    def test_source_final_action_already_created_blocks(self):
        bad = deepcopy(self.reach)
        bad["source_final_action_approval_boundary"]["source_final_action_created_in_source_package"] = True

        errors = self.assert_invalid(bad)

        self.assertIn("source_source_final_action_created_in_source_package_not_expected", errors)

    def test_source_wrong_candidate_blocks(self):
        bad = deepcopy(self.reach)
        bad["source_final_action_approval_boundary"]["candidate_for_future_final_action"] = "wait_or_observe"

        errors = self.assert_invalid(bad)

        self.assertIn("source_candidate_for_future_final_action_not_from_selected_action", errors)

    def test_final_action_created_false_blocks(self):
        bad = deepcopy(self.reach)
        bad["sandbox_final_action"]["final_action_created"] = False

        errors = self.assert_invalid(bad)

        self.assertIn("sandbox_final_action_final_action_created_not_expected", errors)

    def test_wrong_final_action_blocks(self):
        bad = deepcopy(self.reach)
        bad["sandbox_final_action"]["final_action"] = "wait_or_observe"

        errors = self.assert_invalid(bad)

        self.assertIn("sandbox_final_action_final_action_not_expected", errors)

    def test_direct_command_execution_or_observation_true_blocks(self):
        for field in (
            "direct_command_created",
            "sandbox_execution_created",
            "new_outcome_observation_created",
            "execution_allowed_in_this_package",
        ):
            bad = deepcopy(self.reach)
            bad["sandbox_final_action"][field] = True

            errors = self.assert_invalid(bad)

            self.assertIn(f"sandbox_final_action_{field}_not_expected", errors)

    def test_score_runtime_feedback_true_blocks(self):
        for field in (
            "candidate_scores_changed",
            "runtime_next_cycle_candidate_ordering_changed",
            "feedback_loop_created",
        ):
            bad = deepcopy(self.wait)
            bad["sandbox_final_action"][field] = True

            errors = self.assert_invalid(bad)

            self.assertIn(f"sandbox_final_action_{field}_not_expected", errors)

    def test_memory_predictor_direct_feed_and_proof_flags_block(self):
        for flag in (
            "memory_write",
            "retention_write",
            "predictor_read_enabled",
            "predictor_influence_enabled",
            "predictor_modified",
            "direct_endocrine_feed",
            "direct_tendency_feed",
            "proof_of_learning_claim",
        ):
            bad = deepcopy(self.probe)
            bad["blocked_flags"][flag] = True

            errors = self.assert_invalid(bad)

            self.assertIn(f"blocked_flags_{flag}_not_false", errors)

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(summary["final_action_result_count"], 71)
        self.assertEqual(summary["valid_final_action_count"], 3)
        self.assertEqual(summary["invalid_final_action_count"], 68)
        self.assertEqual(summary["final_action_created_count"], 3)
        self.assertEqual(summary["same_session_sandbox_only_count"], 3)
        self.assertEqual(summary["source_approval_preserved_count"], 3)
        self.assertEqual(summary["source_reordering_preserved_count"], 3)
        self.assertEqual(summary["reach_front_item_final_action_count"], 1)
        self.assertEqual(summary["wait_or_observe_final_action_count"], 1)
        self.assertEqual(summary["observe_or_alternative_probe_final_action_count"], 1)
        self.assertEqual(summary["direct_command_blocked_count"], 3)
        self.assertEqual(summary["execution_blocked_count"], 3)
        self.assertEqual(summary["outcome_observation_blocked_count"], 3)
        self.assertEqual(summary["candidate_scores_blocked_count"], 3)
        self.assertEqual(summary["runtime_next_cycle_blocked_count"], 3)
        self.assertEqual(summary["feedback_loop_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_use_blocked_count"], 3)
        self.assertEqual(summary["direct_feed_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)
        self.assertEqual(summary["rollback_available_count"], 3)

    def test_cli_command(self):
        result = run_command(
            "run-sandbox-candidate-ordering-arbitration-reordered-candidate-final-action-minimal-check"
        )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(
            result["flow"],
            "sandbox_candidate_ordering_arbitration_reordered_candidate_final_action_minimal_v0",
        )


if __name__ == "__main__":
    unittest.main()
