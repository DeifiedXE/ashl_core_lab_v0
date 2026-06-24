import unittest
from copy import deepcopy

from ashl_core.sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_approval_boundary_minimal import (
    run_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_approval_boundary_minimal_check,
)
from ashl_core.sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_record,
    run_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_minimal_check,
    validate_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_record,
)
from ashl_core.teaching_cli import run_command


class SandboxCandidateOrderingArbitrationReorderedCandidateDirectCommandMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = (
            run_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_approval_boundary_minimal_check()[
                "valid_records"
            ]
        )
        cls.result = run_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.reach = cls.records[0]
        cls.wait = cls.records[1]
        cls.probe = cls.records[2]

    def assert_invalid(self, record: dict) -> list[str]:
        result = validate_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_record(record)
        self.assertFalse(result["valid"])
        self.assertTrue(result["error_codes"])
        return result["error_codes"]

    def test_valid_direct_command_records_are_created(self):
        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(len(self.records), 3)
        for record in self.records:
            result = validate_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_record(record)
            self.assertTrue(result["valid"], result["error_codes"])
            self.assertEqual(
                record["record_type"],
                "sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_minimal",
            )
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)
            self.assertTrue(record["sandbox_direct_command"]["direct_command_created"])

    def test_boundary_versions_are_b159_to_b160(self):
        boundary = self.result["boundary"]

        self.assertEqual(boundary["boundary_index_version_before"], "2026-06-09-b159")
        self.assertEqual(boundary["boundary_index_version_after"], "2026-06-09-b160")

    def test_default_builder_uses_reordered_direct_command_approval_boundary_source(self):
        record = build_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_record()
        source = record["source_direct_command_approval_boundary"]
        command = record["sandbox_direct_command"]

        self.assertEqual(source["source_boundary_index"], "2026-06-09-b159")
        self.assertTrue(source["future_direct_command_allowed"])
        self.assertEqual(command["direct_command"], source["candidate_for_future_direct_command"])
        self.assertEqual(command["direct_command_scope"], "same_session_sandbox_only")

    def test_direct_commands_match_reordered_final_actions(self):
        self.assertEqual(
            self.reach["sandbox_direct_command"]["direct_command"],
            "sandbox.arbitration.reach_front_item",
        )
        self.assertEqual(
            self.wait["sandbox_direct_command"]["direct_command"],
            "sandbox.arbitration.wait_or_observe",
        )
        self.assertEqual(
            self.probe["sandbox_direct_command"]["direct_command"],
            "sandbox.arbitration.observe_or_alternative_probe",
        )

    def test_source_approval_boundary_is_preserved(self):
        for record in self.records:
            source = record["source_direct_command_approval_boundary"]

            self.assertTrue(source["source_validated"])
            self.assertEqual(source["source_boundary_index"], "2026-06-09-b159")
            self.assertTrue(source["future_direct_command_allowed"])
            self.assertEqual(source["direct_command_scope"], "same_session_sandbox_only")
            self.assertFalse(source["source_direct_command_created_in_source_package"])
            self.assertTrue(source["source_reordering_preserved"])
            self.assertTrue(source["source_arbitration_rules_preserved"])

    def test_direct_command_does_not_execute_or_observe_outcome(self):
        for record in self.records:
            command = record["sandbox_direct_command"]

            self.assertTrue(command["direct_command_created"])
            self.assertFalse(command["sandbox_execution_created"])
            self.assertEqual(command["execution_count"], 0)
            self.assertFalse(command["execution_allowed_in_this_package"])
            self.assertFalse(command["new_outcome_observation_created"])
            self.assertTrue(command["future_execution_requires_separate_boundary"])
            self.assertTrue(command["future_outcome_observation_requires_separate_boundary"])

    def test_direct_command_does_not_change_scores_ordering_or_feedback(self):
        for record in self.records:
            command = record["sandbox_direct_command"]

            self.assertFalse(command["candidate_scores_changed"])
            self.assertFalse(command["runtime_next_cycle_candidate_ordering_changed"])
            self.assertFalse(command["feedback_loop_created"])

    def test_rollback_removes_direct_command_without_dirty_state(self):
        rollback = self.reach["rollback_preview"]
        result = validate_sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_record(self.reach)

        self.assertTrue(result["rollback_available"])
        self.assertTrue(rollback["rollback_available"])
        self.assertTrue(rollback["direct_command_removed_on_rollback"])
        self.assertFalse(rollback["execution_state_created"])
        self.assertFalse(rollback["dirty_state_after_rollback"])
        self.assertFalse(rollback["persistent_update_performed"])

    def test_bad_source_blocks(self):
        bad = deepcopy(self.reach)
        bad["source_direct_command_approval_boundary"]["source_validated"] = False

        errors = self.assert_invalid(bad)

        self.assertIn("source_validated_not_true", errors)

    def test_source_future_direct_command_not_allowed_blocks(self):
        bad = deepcopy(self.reach)
        bad["source_direct_command_approval_boundary"]["future_direct_command_allowed"] = False

        errors = self.assert_invalid(bad)

        self.assertIn("source_future_direct_command_allowed_not_expected", errors)

    def test_source_wrong_future_command_blocks(self):
        bad = deepcopy(self.reach)
        bad["source_direct_command_approval_boundary"]["candidate_for_future_direct_command"] = "sandbox.bad"

        errors = self.assert_invalid(bad)

        self.assertIn("source_direct_command_not_from_final_action", errors)

    def test_direct_command_created_false_blocks(self):
        bad = deepcopy(self.reach)
        bad["sandbox_direct_command"]["direct_command_created"] = False

        errors = self.assert_invalid(bad)

        self.assertIn("sandbox_direct_command_direct_command_created_not_expected", errors)

    def test_wrong_direct_command_scope_or_source_blocks(self):
        for field, value in (
            ("direct_command", "sandbox.bad"),
            ("direct_command_scope", "production"),
            ("direct_command_source", "unapproved"),
            ("direct_command_reason", "unchecked"),
        ):
            bad = deepcopy(self.reach)
            bad["sandbox_direct_command"][field] = value

            errors = self.assert_invalid(bad)

            self.assertIn(f"sandbox_direct_command_{field}_not_expected", errors)

    def test_execution_and_outcome_blocks(self):
        for field, value in (
            ("sandbox_execution_created", True),
            ("execution_count", 1),
            ("execution_allowed_in_this_package", True),
            ("new_outcome_observation_created", True),
        ):
            bad = deepcopy(self.reach)
            bad["sandbox_direct_command"][field] = value

            errors = self.assert_invalid(bad)

            self.assertIn(f"sandbox_direct_command_{field}_not_expected", errors)

    def test_score_runtime_feedback_blocks(self):
        for field in (
            "candidate_scores_changed",
            "runtime_next_cycle_candidate_ordering_changed",
            "feedback_loop_created",
        ):
            bad = deepcopy(self.wait)
            bad["sandbox_direct_command"][field] = True

            errors = self.assert_invalid(bad)

            self.assertIn(f"sandbox_direct_command_{field}_not_expected", errors)

    def test_future_boundaries_are_required(self):
        for field in (
            "future_execution_requires_separate_boundary",
            "future_outcome_observation_requires_separate_boundary",
            "future_memory_write_requires_separate_boundary",
            "future_retention_requires_separate_boundary",
            "future_predictor_influence_requires_separate_boundary",
            "future_production_promotion_requires_separate_boundary",
        ):
            bad = deepcopy(self.reach)
            bad["sandbox_direct_command"][field] = False

            errors = self.assert_invalid(bad)

            self.assertIn(f"sandbox_direct_command_{field}_not_expected", errors)

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

        self.assertEqual(summary["direct_command_result_count"], 72)
        self.assertEqual(summary["valid_direct_command_count"], 3)
        self.assertEqual(summary["invalid_direct_command_count"], 69)
        self.assertEqual(summary["direct_command_created_count"], 3)
        self.assertEqual(summary["same_session_sandbox_only_direct_command_count"], 3)
        self.assertEqual(summary["source_final_action_preserved_count"], 3)
        self.assertEqual(summary["source_reordering_preserved_count"], 3)
        self.assertEqual(summary["reach_front_item_direct_command_count"], 1)
        self.assertEqual(summary["wait_or_observe_direct_command_count"], 1)
        self.assertEqual(summary["observe_or_alternative_probe_direct_command_count"], 1)
        self.assertEqual(summary["execution_blocked_count"], 3)
        self.assertEqual(summary["outcome_observation_blocked_count"], 3)
        self.assertEqual(summary["candidate_scores_blocked_count"], 3)
        self.assertEqual(summary["runtime_next_cycle_blocked_count"], 3)
        self.assertEqual(summary["feedback_loop_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_use_blocked_count"], 3)
        self.assertEqual(summary["direct_feed_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)
        self.assertEqual(summary["arbitration_rules_preserved_count"], 3)
        self.assertEqual(summary["rollback_available_count"], 3)

    def test_cli_command(self):
        result = run_command(
            "run-sandbox-candidate-ordering-arbitration-reordered-candidate-direct-command-minimal-check"
        )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(
            result["flow"],
            "sandbox_candidate_ordering_arbitration_reordered_candidate_direct_command_minimal_v0",
        )


if __name__ == "__main__":
    unittest.main()
