import copy
import unittest

from ashl_core.sandbox_candidate_ordering_arbitration_reordered_candidate_feedback_gated_candidate_reordering_minimal import (
    run_sandbox_candidate_ordering_arbitration_reordered_candidate_feedback_gated_candidate_reordering_minimal_check,
)
from ashl_core.teaching_cli import run_command
from ashl_core.thought_memory_action_parallel_mini_loop_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_thought_memory_action_parallel_mini_loop_record,
    run_thought_memory_action_parallel_mini_loop_minimal_check,
    validate_thought_memory_action_parallel_mini_loop_record,
)


class ThoughtMemoryActionParallelMiniLoopMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_sandbox_candidate_ordering_arbitration_reordered_candidate_feedback_gated_candidate_reordering_minimal_check()[
            "valid_records"
        ]
        cls.result = run_thought_memory_action_parallel_mini_loop_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.reach = cls.records[0]
        cls.wait = cls.records[1]
        cls.probe = cls.records[2]

    def test_valid_parallel_loop_records_are_created(self):
        for record in self.records:
            result = validate_thought_memory_action_parallel_mini_loop_record(record)

            self.assertTrue(result["valid"], result["error_codes"])
            self.assertEqual(record["record_type"], "thought_memory_action_parallel_mini_loop_minimal")
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)
            self.assertTrue(record["parallel_synchronization"]["parallel_loop_created"])

    def test_thought_preview_uses_memory_and_is_not_reality(self):
        record = build_thought_memory_action_parallel_mini_loop_record(self.sources[0])
        thought = record["thought_preview"]
        result = validate_thought_memory_action_parallel_mini_loop_record(record)

        self.assertTrue(result["valid"], result["error_codes"])
        self.assertEqual(thought["memory_source"], "working_memory_recent_trace")
        self.assertEqual(thought["source_memory_kind"], "same_session_temporary_trace")
        self.assertTrue(thought["fantasy_or_preview_not_reality"])
        self.assertFalse(thought["preview_result_treated_as_observed_outcome"])
        self.assertEqual(thought["output_authority"], "candidate_input_only")

    def test_action_observation_records_existing_b169_evidence_only(self):
        for record in self.records:
            action = record["action_observation"]

            self.assertTrue(action["action_observation_created"])
            self.assertEqual(action["observed_action_evidence_source"], "b169_advisory_reordering_record")
            self.assertTrue(action["observed_reordering_created"])
            self.assertTrue(action["observed_reordering_applied"])
            self.assertTrue(action["observed_order_changed"])
            self.assertFalse(action["new_selected_action_created"])
            self.assertFalse(action["new_final_action_created"])
            self.assertFalse(action["new_direct_command_created"])
            self.assertFalse(action["new_execution_created"])
            self.assertFalse(action["new_outcome_observation_created"])

    def test_working_memory_update_is_temporary_only(self):
        for record in self.records:
            memory = record["working_memory_update"]

            self.assertTrue(memory["working_memory_update_created"])
            self.assertEqual(memory["memory_scope"], "same_session_temporary_working_memory_only")
            self.assertTrue(memory["stores_thought_action_alignment"])
            self.assertTrue(memory["stores_preview_vs_observation_check"])
            self.assertFalse(memory["long_term_memory_write"])
            self.assertFalse(memory["memory_write"])
            self.assertFalse(memory["retention_write"])
            self.assertFalse(memory["memory_admission_created"])
            self.assertFalse(memory["habit_created"])
            self.assertFalse(memory["skill_anchor_created"])

    def test_thought_and_action_are_parallel_in_one_cycle(self):
        for record in self.records:
            cycle = record["cycle_frame"]
            sync = record["parallel_synchronization"]

            self.assertEqual(cycle["cycle_index"], 1)
            self.assertEqual(cycle["max_cycles"], 1)
            self.assertTrue(sync["thought_and_action_parallel"])
            self.assertTrue(sync["action_result_checks_thought_preview"])
            self.assertTrue(sync["memory_receives_alignment_trace"])
            self.assertFalse(sync["next_cycle_selection_created"])
            self.assertFalse(sync["open_ended_loop_created"])

    def test_b0_self_check_and_boundary_audit_are_present(self):
        for record in self.records:
            self_check = record["b0_10_self_check"]
            audit = record["boundary_audit"]
            result = validate_thought_memory_action_parallel_mini_loop_record(record)

            self.assertTrue(result["b0_10_self_check_passed"])
            self.assertTrue(result["boundary_audit_passed"])
            self.assertTrue(self_check["triggered"])
            self.assertEqual(self_check["boundary_number"], 170)
            self.assertTrue(audit["triggered"])
            self.assertEqual(audit["boundary_number"], 170)

    def test_reach_wait_and_probe_candidates_enter_parallel_loop(self):
        self.assertEqual(self.reach["thought_preview"]["previewed_candidate"], "reach_front_item")
        self.assertEqual(self.wait["thought_preview"]["previewed_candidate"], "wait_or_observe")
        self.assertEqual(self.probe["thought_preview"]["previewed_candidate"], "observe_or_alternative_probe")

    def test_bad_source_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["source_reordered_candidate_reordering"]["source_validated"] = False

        result = validate_thought_memory_action_parallel_mini_loop_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_validated_not_true", result["error_codes"])

    def test_preview_treated_as_observed_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["thought_preview"]["preview_result_treated_as_observed_outcome"] = True

        result = validate_thought_memory_action_parallel_mini_loop_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn(
            "thought_preview_preview_result_treated_as_observed_outcome_not_expected",
            result["error_codes"],
        )

    def test_thought_selected_action_or_memory_write_blocks(self):
        cases = (
            ("selected_action_created", "thought_preview_selected_action_created_not_expected"),
            ("final_action_created", "thought_preview_final_action_created_not_expected"),
            ("direct_command_created", "thought_preview_direct_command_created_not_expected"),
            ("action_executed", "thought_preview_action_executed_not_expected"),
            ("memory_write_created", "thought_preview_memory_write_created_not_expected"),
        )
        for field, error in cases:
            bad = copy.deepcopy(self.reach)
            bad["thought_preview"][field] = True

            result = validate_thought_memory_action_parallel_mini_loop_record(bad)

            self.assertFalse(result["valid"])
            self.assertIn(error, result["error_codes"])

    def test_action_selected_command_execution_or_outcome_blocks(self):
        for field in (
            "new_selected_action_created",
            "new_final_action_created",
            "new_direct_command_created",
            "new_execution_created",
            "new_outcome_observation_created",
        ):
            bad = copy.deepcopy(self.wait)
            bad["action_observation"][field] = True

            result = validate_thought_memory_action_parallel_mini_loop_record(bad)

            self.assertFalse(result["valid"])
            self.assertIn(f"action_observation_{field}_not_expected", result["error_codes"])

    def test_memory_write_retention_and_habit_blocks(self):
        for field in (
            "long_term_memory_write",
            "memory_write",
            "retention_write",
            "memory_admission_created",
            "habit_created",
            "skill_anchor_created",
        ):
            bad = copy.deepcopy(self.probe)
            bad["working_memory_update"][field] = True

            result = validate_thought_memory_action_parallel_mini_loop_record(bad)

            self.assertFalse(result["valid"])
            self.assertIn(f"working_memory_update_{field}_not_expected", result["error_codes"])

    def test_sync_next_cycle_or_open_ended_loop_blocks(self):
        for field in ("next_cycle_selection_created", "open_ended_loop_created"):
            bad = copy.deepcopy(self.reach)
            bad["parallel_synchronization"][field] = True

            result = validate_thought_memory_action_parallel_mini_loop_record(bad)

            self.assertFalse(result["valid"])
            self.assertIn(f"parallel_synchronization_{field}_not_expected", result["error_codes"])

    def test_self_check_false_blocks(self):
        for field in (
            "triggered",
            "docs_status_matches_code",
            "cli_exists",
            "smoke_exists",
            "tests_match_reported_counts",
        ):
            bad = copy.deepcopy(self.wait)
            bad["b0_10_self_check"][field] = False

            result = validate_thought_memory_action_parallel_mini_loop_record(bad)

            self.assertFalse(result["valid"])
            self.assertIn(f"b0_10_self_check_{field}_not_true", result["error_codes"])

    def test_audit_forbidden_flags_block(self):
        for field in (
            "production_behavior_created",
            "runtime_behavior_leak",
            "memory_write_created",
            "retention_write_created",
            "predictor_read_enabled",
            "predictor_influence_enabled",
            "predictor_modified",
            "direct_endocrine_feed",
            "direct_tendency_feed",
            "raw_weighted_sum_used",
            "proof_of_learning_claim",
        ):
            bad = copy.deepcopy(self.probe)
            bad["boundary_audit"][field] = True

            result = validate_thought_memory_action_parallel_mini_loop_record(bad)

            self.assertFalse(result["valid"])
            self.assertIn(f"boundary_audit_{field}_not_false", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(summary["parallel_loop_result_count"], 57)
        self.assertEqual(summary["valid_parallel_loop_count"], 3)
        self.assertEqual(summary["invalid_parallel_loop_count"], 54)
        self.assertEqual(summary["thought_preview_created_count"], 3)
        self.assertEqual(summary["action_observation_created_count"], 3)
        self.assertEqual(summary["working_memory_update_created_count"], 3)
        self.assertEqual(summary["parallel_loop_created_count"], 3)
        self.assertEqual(summary["b0_10_self_check_passed_count"], 3)
        self.assertEqual(summary["boundary_audit_passed_count"], 3)
        self.assertEqual(summary["reach_loop_count"], 1)
        self.assertEqual(summary["wait_loop_count"], 1)
        self.assertEqual(summary["probe_loop_count"], 1)
        self.assertEqual(summary["one_cycle_budget_count"], 3)
        self.assertEqual(summary["action_creation_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_use_blocked_count"], 3)
        self.assertEqual(summary["production_behavior_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)

    def test_cli_command(self):
        result = run_command("run-thought-memory-action-parallel-mini-loop-minimal-check")

        self.assertEqual(result["command"], "run-thought-memory-action-parallel-mini-loop-minimal-check")
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
