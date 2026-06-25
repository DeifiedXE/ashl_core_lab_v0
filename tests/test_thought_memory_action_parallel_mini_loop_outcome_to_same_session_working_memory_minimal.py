import copy
import unittest

from ashl_core.teaching_cli import run_command
from ashl_core.thought_memory_action_parallel_mini_loop_ordering_to_next_sandbox_action_minimal import (
    run_thought_memory_action_parallel_mini_loop_ordering_to_next_sandbox_action_minimal_check,
)
from ashl_core.thought_memory_action_parallel_mini_loop_outcome_to_same_session_working_memory_minimal import (
    BOUNDARY_INDEX_AFTER,
    MEMORY_LABELS,
    build_thought_memory_action_parallel_mini_loop_outcome_to_same_session_working_memory_record,
    run_thought_memory_action_parallel_mini_loop_outcome_to_same_session_working_memory_minimal_check,
    validate_thought_memory_action_parallel_mini_loop_outcome_to_same_session_working_memory_record,
)


class ThoughtMemoryActionParallelMiniLoopOutcomeToSameSessionWorkingMemoryMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_thought_memory_action_parallel_mini_loop_ordering_to_next_sandbox_action_minimal_check()[
            "valid_records"
        ]
        cls.result = run_thought_memory_action_parallel_mini_loop_outcome_to_same_session_working_memory_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.reach = cls.records[0]
        cls.wait = cls.records[1]
        cls.probe = cls.records[2]

    def test_valid_same_session_working_memory_updates_are_created(self):
        for record in self.records:
            result = validate_thought_memory_action_parallel_mini_loop_outcome_to_same_session_working_memory_record(
                record
            )

            self.assertTrue(result["valid"], result["error_codes"])
            self.assertEqual(
                record["record_type"],
                "thought_memory_action_parallel_mini_loop_outcome_to_same_session_working_memory_minimal",
            )
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)
            self.assertTrue(record["same_session_working_memory_update"]["working_memory_update_created"])

    def test_b175_outcome_becomes_same_session_working_memory(self):
        record = build_thought_memory_action_parallel_mini_loop_outcome_to_same_session_working_memory_record(
            self.sources[0]
        )
        source = record["source_sandbox_action_path"]
        memory = record["same_session_working_memory_update"]
        result = validate_thought_memory_action_parallel_mini_loop_outcome_to_same_session_working_memory_record(
            record
        )

        self.assertTrue(result["valid"], result["error_codes"])
        self.assertEqual(memory["stored_observed_outcome"], source["observed_outcome"])
        self.assertEqual(memory["stored_outcome_label"], source["outcome_label"])
        self.assertEqual(memory["stored_selected_action"], source["selected_action"])
        self.assertTrue(result["outcome_written_to_working_memory"])

    def test_reach_wait_and_probe_outcomes_are_stored_with_memory_labels(self):
        expected = [
            ("reach_front_item", "front_item_reached", "mini_loop_reach_front_item_observed"),
            ("wait_or_observe", "local_context_observed", "mini_loop_wait_context_observed"),
            (
                "observe_or_alternative_probe",
                "local_context_observed",
                "mini_loop_mismatch_probe_context_observed",
            ),
        ]
        for record, (action, outcome, label) in zip(self.records, expected):
            memory = record["same_session_working_memory_update"]

            self.assertEqual(memory["stored_selected_action"], action)
            self.assertEqual(memory["stored_observed_outcome"], outcome)
            self.assertEqual(memory["stored_outcome_label"], label)
            self.assertEqual(memory["stored_memory_label"], MEMORY_LABELS[label])

    def test_source_action_path_and_previous_memory_links_are_preserved(self):
        for record in self.records:
            source = record["source_sandbox_action_path"]
            memory = record["same_session_working_memory_update"]
            result = validate_thought_memory_action_parallel_mini_loop_outcome_to_same_session_working_memory_record(
                record
            )

            self.assertEqual(memory["source_sandbox_action_path_record_id"], source["source_sandbox_action_path_record_id"])
            self.assertEqual(memory["source_ordering_record_id"], source["source_ordering_record_id"])
            self.assertEqual(memory["source_candidate_hint_record_id"], source["source_candidate_hint_record_id"])
            self.assertEqual(memory["previous_working_memory_update_id"], source["source_working_memory_update_id"])
            self.assertTrue(memory["links_previous_working_memory_update"])
            self.assertTrue(memory["links_second_cycle_action_path"])
            self.assertTrue(result["previous_memory_linked"])
            self.assertTrue(result["second_cycle_action_linked"])

    def test_update_is_same_session_temporary_only(self):
        for record in self.records:
            memory = record["same_session_working_memory_update"]
            containment = record["working_memory_containment"]
            result = validate_thought_memory_action_parallel_mini_loop_outcome_to_same_session_working_memory_record(
                record
            )

            self.assertEqual(memory["memory_scope"], "same_session_temporary_working_memory_only")
            self.assertEqual(memory["memory_lifetime"], "same_session_temporary_only")
            self.assertEqual(containment["working_memory_scope"], "same_session_temporary_working_memory_only")
            self.assertTrue(containment["same_session_only"])
            self.assertTrue(containment["sandbox_only"])
            self.assertTrue(result["same_session_memory_only"])

    def test_update_does_not_create_feedback_reordering_or_new_action(self):
        for record in self.records:
            memory = record["same_session_working_memory_update"]
            containment = record["working_memory_containment"]
            result = validate_thought_memory_action_parallel_mini_loop_outcome_to_same_session_working_memory_record(
                record
            )

            self.assertFalse(memory["feedback_evaluation_created"])
            self.assertFalse(memory["feedback_application_created"])
            self.assertFalse(memory["candidate_reordering_created"])
            self.assertFalse(memory["candidate_scores_changed"])
            self.assertFalse(memory["new_selected_action_created"])
            self.assertFalse(memory["new_direct_command_created"])
            self.assertFalse(memory["new_execution_created"])
            self.assertFalse(memory["new_outcome_observation_created"])
            self.assertFalse(containment["runtime_next_cycle_candidate_ordering_changed_in_this_package"])
            self.assertTrue(result["feedback_blocked"])
            self.assertTrue(result["candidate_reordering_blocked"])
            self.assertTrue(result["action_creation_blocked"])

    def test_update_does_not_persist_memory_use_predictor_feed_or_claim(self):
        for record in self.records:
            memory = record["same_session_working_memory_update"]
            audit = record["boundary_audit"]
            result = validate_thought_memory_action_parallel_mini_loop_outcome_to_same_session_working_memory_record(
                record
            )

            self.assertFalse(memory["long_term_memory_write"])
            self.assertFalse(memory["core_memory_write"])
            self.assertFalse(memory["archive_memory_write"])
            self.assertFalse(memory["retention_write"])
            self.assertFalse(memory["memory_admission_created"])
            self.assertFalse(memory["predictor_read_enabled"])
            self.assertFalse(memory["predictor_influence_enabled"])
            self.assertFalse(memory["direct_endocrine_feed"])
            self.assertFalse(memory["direct_tendency_feed"])
            self.assertFalse(memory["production_behavior_created"])
            self.assertFalse(memory["proof_of_learning_claim"])
            self.assertFalse(memory["consciousness_claim"])
            self.assertEqual(audit["boundary_number"], 176)
            self.assertTrue(result["memory_persistence_blocked"])
            self.assertTrue(result["predictor_use_blocked"])
            self.assertTrue(result["direct_feed_blocked"])
            self.assertTrue(result["production_behavior_blocked"])
            self.assertTrue(result["proof_claim_blocked"])
            self.assertTrue(result["consciousness_claim_blocked"])

    def test_bad_source_blocks_builder(self):
        bad_source = copy.deepcopy(self.sources[0])
        bad_source["compact_sandbox_action_path"]["execution_count"] = 2

        with self.assertRaises(ValueError):
            build_thought_memory_action_parallel_mini_loop_outcome_to_same_session_working_memory_record(bad_source)

    def test_bad_source_summary_blocks_validator(self):
        bad = copy.deepcopy(self.reach)
        bad["source_sandbox_action_path"]["source_validated"] = False

        result = validate_thought_memory_action_parallel_mini_loop_outcome_to_same_session_working_memory_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_source_validated_not_expected", result["error_codes"])

    def test_wrong_stored_outcome_or_links_block(self):
        cases = (
            (("same_session_working_memory_update", "stored_observed_outcome"), "blocked", "outcome_written_to_working_memory"),
            (("same_session_working_memory_update", "previous_working_memory_update_id"), "wrong", "previous_memory_linked"),
            (("same_session_working_memory_update", "source_sandbox_action_path_record_id"), "wrong", "second_cycle_action_linked"),
            (("same_session_working_memory_update", "available_for_future_two_cycle_comparison"), False, "future_comparison_ready"),
        )
        for path, value, result_field in cases:
            bad = copy.deepcopy(self.probe)
            target = bad
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value

            result = validate_thought_memory_action_parallel_mini_loop_outcome_to_same_session_working_memory_record(
                bad
            )

            self.assertFalse(result["valid"])
            self.assertFalse(result[result_field])

    def test_feedback_reordering_and_action_flags_block(self):
        cases = (
            ("feedback_evaluation_created", "feedback_blocked"),
            ("feedback_application_created", "feedback_blocked"),
            ("candidate_reordering_created", "candidate_reordering_blocked"),
            ("candidate_scores_changed", "candidate_reordering_blocked"),
            ("runtime_next_cycle_candidate_ordering_changed", "candidate_reordering_blocked"),
            ("new_selected_action_created", "action_creation_blocked"),
            ("new_final_action_created", "action_creation_blocked"),
            ("new_direct_command_created", "action_creation_blocked"),
            ("new_execution_created", "action_creation_blocked"),
            ("new_outcome_observation_created", "action_creation_blocked"),
        )
        for field, result_field in cases:
            bad = copy.deepcopy(self.wait)
            bad["same_session_working_memory_update"][field] = True

            result = validate_thought_memory_action_parallel_mini_loop_outcome_to_same_session_working_memory_record(
                bad
            )

            self.assertFalse(result["valid"])
            self.assertFalse(result[result_field])

    def test_memory_predictor_feed_production_proof_and_consciousness_flags_block(self):
        cases = (
            ("memory_write", "memory_persistence_blocked"),
            ("long_term_memory_write", "memory_persistence_blocked"),
            ("retention_write", "memory_persistence_blocked"),
            ("memory_admission_created", "memory_persistence_blocked"),
            ("predictor_read_enabled", "predictor_use_blocked"),
            ("predictor_influence_enabled", "predictor_use_blocked"),
            ("predictor_modified", "predictor_use_blocked"),
            ("direct_endocrine_feed", "direct_feed_blocked"),
            ("direct_tendency_feed", "direct_feed_blocked"),
            ("production_behavior_created", "production_behavior_blocked"),
            ("proof_of_learning_claim", "proof_claim_blocked"),
            ("consciousness_claim", "consciousness_claim_blocked"),
        )
        for field, result_field in cases:
            bad = copy.deepcopy(self.reach)
            bad["same_session_working_memory_update"][field] = True

            result = validate_thought_memory_action_parallel_mini_loop_outcome_to_same_session_working_memory_record(
                bad
            )

            self.assertFalse(result["valid"])
            self.assertFalse(result[result_field])

    def test_boundary_audit_blocks_next_layer_precreation(self):
        bad = copy.deepcopy(self.wait)
        bad["boundary_audit"]["next_layer_precreated"] = True

        result = validate_thought_memory_action_parallel_mini_loop_outcome_to_same_session_working_memory_record(bad)

        self.assertFalse(result["valid"])
        self.assertFalse(result["boundary_audit_passed"])

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(summary["same_session_working_memory_result_count"], 86)
        self.assertEqual(summary["valid_same_session_working_memory_count"], 3)
        self.assertEqual(summary["invalid_same_session_working_memory_count"], 83)
        self.assertEqual(summary["working_memory_update_created_count"], 3)
        self.assertEqual(summary["outcome_written_to_working_memory_count"], 3)
        self.assertEqual(summary["same_session_memory_only_count"], 3)
        self.assertEqual(summary["previous_memory_linked_count"], 3)
        self.assertEqual(summary["second_cycle_action_linked_count"], 3)
        self.assertEqual(summary["future_comparison_ready_count"], 3)
        self.assertEqual(summary["reach_memory_update_count"], 1)
        self.assertEqual(summary["wait_memory_update_count"], 1)
        self.assertEqual(summary["probe_memory_update_count"], 1)
        self.assertEqual(summary["feedback_blocked_count"], 3)
        self.assertEqual(summary["candidate_reordering_blocked_count"], 3)
        self.assertEqual(summary["action_creation_blocked_count"], 3)
        self.assertEqual(summary["memory_persistence_blocked_count"], 3)
        self.assertEqual(summary["predictor_use_blocked_count"], 3)
        self.assertEqual(summary["direct_feed_blocked_count"], 3)
        self.assertEqual(summary["production_behavior_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)
        self.assertEqual(summary["consciousness_claim_blocked_count"], 3)
        self.assertEqual(summary["boundary_audit_passed_count"], 3)

    def test_cli_command(self):
        result = run_command(
            "run-thought-memory-action-parallel-mini-loop-outcome-to-same-session-working-memory-minimal-check"
        )

        self.assertEqual(
            result["command"],
            "run-thought-memory-action-parallel-mini-loop-outcome-to-same-session-working-memory-minimal-check",
        )
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
