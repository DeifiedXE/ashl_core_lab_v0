import copy
import unittest

from ashl_core.teaching_cli import run_command
from ashl_core.thought_memory_action_parallel_mini_loop_candidate_hint_into_ordering_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_thought_memory_action_parallel_mini_loop_candidate_hint_into_ordering_record,
    run_thought_memory_action_parallel_mini_loop_candidate_hint_into_ordering_minimal_check,
    validate_thought_memory_action_parallel_mini_loop_candidate_hint_into_ordering_record,
)
from ashl_core.thought_memory_action_parallel_mini_loop_signal_readback_candidate_hint_minimal import (
    run_thought_memory_action_parallel_mini_loop_signal_readback_candidate_hint_minimal_check,
)


class ThoughtMemoryActionParallelMiniLoopCandidateHintIntoOrderingMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_thought_memory_action_parallel_mini_loop_signal_readback_candidate_hint_minimal_check()[
            "valid_records"
        ]
        cls.result = run_thought_memory_action_parallel_mini_loop_candidate_hint_into_ordering_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.reach = cls.records[0]
        cls.wait = cls.records[1]
        cls.probe = cls.records[2]

    def test_valid_candidate_hint_orderings_are_created(self):
        for record in self.records:
            result = validate_thought_memory_action_parallel_mini_loop_candidate_hint_into_ordering_record(
                record
            )

            self.assertTrue(result["valid"], result["error_codes"])
            self.assertEqual(
                record["record_type"],
                "thought_memory_action_parallel_mini_loop_candidate_hint_into_ordering_minimal",
            )
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)
            self.assertTrue(record["candidate_hint_ordering"]["candidate_ordering_created"])
            self.assertTrue(record["candidate_hint_ordering"]["candidate_order_changed"])

    def test_b173_weak_hint_changes_sandbox_advisory_ordering(self):
        record = build_thought_memory_action_parallel_mini_loop_candidate_hint_into_ordering_record(
            self.sources[0]
        )
        source = record["source_candidate_hint"]
        ordering = record["candidate_hint_ordering"]
        result = validate_thought_memory_action_parallel_mini_loop_candidate_hint_into_ordering_record(
            record
        )

        self.assertTrue(result["valid"], result["error_codes"])
        self.assertTrue(source["candidate_hint_created"])
        self.assertEqual(source["hint_strength"], "weak")
        self.assertTrue(ordering["hint_used_for_ordering"])
        self.assertEqual(ordering["primary_ranked_action"], "reach_front_item")
        self.assertNotEqual(
            ordering["candidate_actions_before_ordering"],
            ordering["candidate_actions_after_ordering"],
        )

    def test_reach_wait_and_probe_hints_each_become_first_candidate(self):
        self.assertEqual(self.reach["candidate_hint_ordering"]["primary_ranked_action"], "reach_front_item")
        self.assertEqual(self.wait["candidate_hint_ordering"]["primary_ranked_action"], "wait_or_observe")
        self.assertEqual(
            self.probe["candidate_hint_ordering"]["primary_ranked_action"],
            "observe_or_alternative_probe",
        )

    def test_candidate_set_is_preserved_while_order_changes(self):
        for record in self.records:
            ordering = record["candidate_hint_ordering"]

            self.assertTrue(ordering["candidate_set_preserved"])
            self.assertEqual(
                sorted(ordering["candidate_actions_before_ordering"]),
                sorted(ordering["candidate_actions_after_ordering"]),
            )
            self.assertNotEqual(
                ordering["candidate_actions_before_ordering"],
                ordering["candidate_actions_after_ordering"],
            )

    def test_ordering_is_same_session_sandbox_advisory_only(self):
        for record in self.records:
            ordering = record["candidate_hint_ordering"]
            containment = record["ordering_containment"]

            self.assertEqual(ordering["ordering_scope"], "same_session_sandbox_only")
            self.assertEqual(ordering["ordering_lifetime"], "same_session_temporary_only")
            self.assertEqual(ordering["ordering_authority"], "sandbox_advisory_candidate_ordering_only")
            self.assertEqual(ordering["ordering_effect_scope"], "same_session_sandbox_advisory_record_only")
            self.assertTrue(containment["same_session_only"])
            self.assertTrue(containment["sandbox_only"])

    def test_ordering_does_not_select_or_execute_action(self):
        for record in self.records:
            ordering = record["candidate_hint_ordering"]
            containment = record["ordering_containment"]
            result = validate_thought_memory_action_parallel_mini_loop_candidate_hint_into_ordering_record(
                record
            )

            self.assertFalse(ordering["selected_action_created"])
            self.assertFalse(ordering["final_action_created"])
            self.assertFalse(ordering["direct_command_created"])
            self.assertFalse(ordering["execution_created"])
            self.assertFalse(ordering["new_outcome_observation_created"])
            self.assertFalse(containment["selected_action_created_in_this_package"])
            self.assertTrue(result["action_creation_blocked"])

    def test_ordering_does_not_mutate_scores_runtime_memory_predictor_or_proof(self):
        for record in self.records:
            ordering = record["candidate_hint_ordering"]
            containment = record["ordering_containment"]
            audit = record["boundary_audit"]
            result = validate_thought_memory_action_parallel_mini_loop_candidate_hint_into_ordering_record(
                record
            )

            self.assertFalse(ordering["candidate_scores_changed"])
            self.assertFalse(ordering["runtime_next_cycle_candidate_ordering_changed"])
            self.assertFalse(containment["memory_write_created_in_this_package"])
            self.assertFalse(containment["predictor_read_enabled_in_this_package"])
            self.assertFalse(audit["production_behavior_created"])
            self.assertTrue(result["score_mutation_blocked"])
            self.assertTrue(result["runtime_ordering_blocked"])
            self.assertTrue(result["memory_write_blocked"])
            self.assertTrue(result["predictor_use_blocked"])
            self.assertTrue(result["proof_claim_blocked"])

    def test_bad_source_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["source_candidate_hint"]["source_validated"] = False

        result = validate_thought_memory_action_parallel_mini_loop_candidate_hint_into_ordering_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_source_validated_not_expected", result["error_codes"])

    def test_bad_source_candidate_blocks(self):
        bad = copy.deepcopy(self.wait)
        bad["source_candidate_hint"]["candidate_for_hint"] = "retry_same_action"

        result = validate_thought_memory_action_parallel_mini_loop_candidate_hint_into_ordering_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_candidate_for_hint_not_orderable", result["error_codes"])
        self.assertIn("source_previewed_candidate_does_not_match_hint", result["error_codes"])

    def test_ordering_shape_blocks_invalid_cases(self):
        cases = (
            ("candidate_ordering_created", False),
            ("ordering_scope", "production"),
            ("ordering_lifetime", "persistent"),
            ("ordering_authority", "selected_action_authority"),
            ("hint_used_for_ordering", False),
            ("candidate_set_preserved", False),
            ("candidate_order_changed", False),
        )
        for field, value in cases:
            bad = copy.deepcopy(self.probe)
            bad["candidate_hint_ordering"][field] = value

            result = validate_thought_memory_action_parallel_mini_loop_candidate_hint_into_ordering_record(bad)

            self.assertFalse(result["valid"])
            self.assertIn(f"candidate_hint_ordering_{field}_not_expected", result["error_codes"])

    def test_action_creation_flags_block(self):
        cases = (
            "selected_action_created",
            "final_action_created",
            "direct_command_created",
            "execution_created",
            "new_outcome_observation_created",
        )
        for field in cases:
            bad = copy.deepcopy(self.reach)
            bad["candidate_hint_ordering"][field] = True

            result = validate_thought_memory_action_parallel_mini_loop_candidate_hint_into_ordering_record(bad)

            self.assertFalse(result["valid"])
            self.assertFalse(result["action_creation_blocked"])

    def test_containment_blocks_next_layer_effects(self):
        cases = (
            "candidate_scores_changed_in_this_package",
            "runtime_next_cycle_candidate_ordering_changed_in_this_package",
            "selected_action_created_in_this_package",
            "final_action_created_in_this_package",
            "direct_command_created_in_this_package",
            "execution_created_in_this_package",
            "new_outcome_observation_created_in_this_package",
            "memory_write_created_in_this_package",
            "retention_write_created_in_this_package",
            "predictor_read_enabled_in_this_package",
            "production_behavior_created_in_this_package",
            "proof_of_learning_claim",
        )
        for field in cases:
            bad = copy.deepcopy(self.wait)
            bad["ordering_containment"][field] = True

            result = validate_thought_memory_action_parallel_mini_loop_candidate_hint_into_ordering_record(bad)

            self.assertFalse(result["valid"])
            self.assertIn(f"ordering_containment_{field}_not_expected", result["error_codes"])

    def test_rollback_and_audit_block_invalid_cases(self):
        bad = copy.deepcopy(self.reach)
        bad["rollback_preview"]["dirty_state_after_rollback"] = True
        rollback_result = validate_thought_memory_action_parallel_mini_loop_candidate_hint_into_ordering_record(
            bad
        )

        bad = copy.deepcopy(self.reach)
        bad["boundary_audit"]["next_layer_precreated"] = True
        audit_result = validate_thought_memory_action_parallel_mini_loop_candidate_hint_into_ordering_record(
            bad
        )

        self.assertFalse(rollback_result["valid"])
        self.assertFalse(rollback_result["rollback_available"])
        self.assertFalse(audit_result["valid"])
        self.assertFalse(audit_result["boundary_audit_passed"])

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(summary["candidate_hint_ordering_result_count"], 64)
        self.assertEqual(summary["valid_candidate_hint_ordering_count"], 3)
        self.assertEqual(summary["invalid_candidate_hint_ordering_count"], 61)
        self.assertEqual(summary["candidate_ordering_created_count"], 3)
        self.assertEqual(summary["candidate_order_changed_count"], 3)
        self.assertEqual(summary["candidate_set_preserved_count"], 3)
        self.assertEqual(summary["hint_used_for_ordering_count"], 3)
        self.assertEqual(summary["reach_first_count"], 1)
        self.assertEqual(summary["wait_first_count"], 1)
        self.assertEqual(summary["probe_first_count"], 1)
        self.assertEqual(summary["score_mutation_blocked_count"], 3)
        self.assertEqual(summary["runtime_ordering_blocked_count"], 3)
        self.assertEqual(summary["action_creation_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_use_blocked_count"], 3)
        self.assertEqual(summary["direct_feed_blocked_count"], 3)
        self.assertEqual(summary["production_behavior_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)
        self.assertEqual(summary["rollback_available_count"], 3)
        self.assertEqual(summary["boundary_audit_passed_count"], 3)

    def test_cli_command(self):
        result = run_command(
            "run-thought-memory-action-parallel-mini-loop-candidate-hint-into-ordering-minimal-check"
        )

        self.assertEqual(
            result["command"],
            "run-thought-memory-action-parallel-mini-loop-candidate-hint-into-ordering-minimal-check",
        )
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
