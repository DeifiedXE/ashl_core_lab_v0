import copy
import unittest

from ashl_core.teaching_cli import run_command
from ashl_core.thought_memory_action_parallel_mini_loop_outcome_to_same_session_working_memory_minimal import (
    run_thought_memory_action_parallel_mini_loop_outcome_to_same_session_working_memory_minimal_check,
)
from ashl_core.thought_memory_action_parallel_mini_loop_two_cycle_influence_check_minimal import (
    BASELINE_CANDIDATE_ORDERS,
    BOUNDARY_INDEX_AFTER,
    HINT_INFLUENCED_CANDIDATE_ORDERS,
    build_thought_memory_action_parallel_mini_loop_two_cycle_influence_check_record,
    run_thought_memory_action_parallel_mini_loop_two_cycle_influence_check_minimal_check,
    validate_thought_memory_action_parallel_mini_loop_two_cycle_influence_check_record,
)


class ThoughtMemoryActionParallelMiniLoopTwoCycleInfluenceCheckMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_thought_memory_action_parallel_mini_loop_outcome_to_same_session_working_memory_minimal_check()[
            "valid_records"
        ]
        cls.result = run_thought_memory_action_parallel_mini_loop_two_cycle_influence_check_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.reach = cls.records[0]
        cls.wait = cls.records[1]
        cls.probe = cls.records[2]

    def test_valid_two_cycle_influence_checks_are_created(self):
        for record in self.records:
            result = validate_thought_memory_action_parallel_mini_loop_two_cycle_influence_check_record(record)

            self.assertTrue(result["valid"], result["error_codes"])
            self.assertEqual(
                record["record_type"],
                "thought_memory_action_parallel_mini_loop_two_cycle_influence_check_minimal",
            )
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)
            self.assertTrue(record["influence_comparison"]["influence_check_created"])

    def test_b176_working_memory_source_enters_two_cycle_check(self):
        record = build_thought_memory_action_parallel_mini_loop_two_cycle_influence_check_record(self.sources[0])
        source = record["source_same_session_working_memory"]
        evidence = record["two_cycle_evidence"]
        comparison = record["influence_comparison"]
        result = validate_thought_memory_action_parallel_mini_loop_two_cycle_influence_check_record(record)

        self.assertTrue(result["valid"], result["error_codes"])
        self.assertEqual(source["source_boundary_index"], "2026-06-09-b176")
        self.assertEqual(evidence["cycle_count_checked"], 2)
        self.assertTrue(comparison["influence_visible"])
        self.assertTrue(result["two_cycle_checked"])

    def test_reach_wait_and_probe_each_show_hint_influence(self):
        for record in self.records:
            source = record["source_same_session_working_memory"]
            comparison = record["influence_comparison"]
            action = source["selected_action"]

            self.assertEqual(comparison["baseline_candidate_order"], BASELINE_CANDIDATE_ORDERS[action])
            self.assertEqual(comparison["hint_influenced_candidate_order"], HINT_INFLUENCED_CANDIDATE_ORDERS[action])
            self.assertGreater(comparison["hinted_candidate_baseline_rank"], 1)
            self.assertEqual(comparison["hinted_candidate_after_rank"], 1)
            self.assertTrue(comparison["hint_moved_candidate_to_front"])

    def test_influence_path_links_memory_hint_ordering_action_and_second_memory(self):
        for record in self.records:
            source = record["source_same_session_working_memory"]
            evidence = record["two_cycle_evidence"]
            comparison = record["influence_comparison"]
            result = validate_thought_memory_action_parallel_mini_loop_two_cycle_influence_check_record(record)

            self.assertEqual(evidence["first_cycle_working_memory_update_id"], source["first_cycle_working_memory_update_id"])
            self.assertEqual(evidence["candidate_hint_record_id"], source["source_candidate_hint_record_id"])
            self.assertEqual(evidence["ordering_record_id"], source["source_ordering_record_id"])
            self.assertEqual(evidence["sandbox_action_path_record_id"], source["source_sandbox_action_path_record_id"])
            self.assertEqual(evidence["second_cycle_working_memory_update_id"], source["second_cycle_working_memory_update_id"])
            self.assertTrue(comparison["first_cycle_memory_to_hint_linked"])
            self.assertTrue(comparison["hint_to_ordering_linked"])
            self.assertTrue(comparison["ordering_to_action_path_linked"])
            self.assertTrue(comparison["action_path_to_second_memory_linked"])
            self.assertTrue(result["second_cycle_action_matches_hint"])
            self.assertTrue(result["outcome_memory_linked"])

    def test_comparison_is_record_only(self):
        for record in self.records:
            comparison = record["influence_comparison"]
            containment = record["comparison_containment"]
            result = validate_thought_memory_action_parallel_mini_loop_two_cycle_influence_check_record(record)

            self.assertEqual(comparison["comparison_scope"], "same_session_sandbox_record_only")
            self.assertEqual(comparison["comparison_authority"], "evidence_check_only")
            self.assertTrue(containment["uses_existing_trace_records_only"])
            self.assertTrue(containment["no_new_source_trace_record_created"])
            self.assertTrue(result["comparison_record_only"])

    def test_no_feedback_reordering_action_memory_or_production_is_created(self):
        for record in self.records:
            comparison = record["influence_comparison"]
            audit = record["boundary_audit"]
            result = validate_thought_memory_action_parallel_mini_loop_two_cycle_influence_check_record(record)

            self.assertFalse(comparison["feedback_evaluation_created"])
            self.assertFalse(comparison["candidate_reordering_created"])
            self.assertFalse(comparison["new_selected_action_created"])
            self.assertFalse(comparison["new_execution_created"])
            self.assertFalse(comparison["working_memory_update_created"])
            self.assertFalse(comparison["memory_write"])
            self.assertFalse(comparison["retention_write"])
            self.assertFalse(comparison["predictor_read_enabled"])
            self.assertFalse(comparison["direct_endocrine_feed"])
            self.assertFalse(comparison["production_behavior_created"])
            self.assertFalse(comparison["proof_of_learning_claim"])
            self.assertFalse(comparison["consciousness_claim"])
            self.assertEqual(audit["boundary_number"], 177)
            self.assertTrue(result["feedback_blocked"])
            self.assertTrue(result["candidate_reordering_blocked"])
            self.assertTrue(result["action_creation_blocked"])
            self.assertTrue(result["memory_persistence_blocked"])
            self.assertTrue(result["predictor_use_blocked"])
            self.assertTrue(result["direct_feed_blocked"])
            self.assertTrue(result["production_behavior_blocked"])
            self.assertTrue(result["proof_claim_blocked"])
            self.assertTrue(result["consciousness_claim_blocked"])

    def test_bad_source_blocks_builder(self):
        bad_source = copy.deepcopy(self.sources[0])
        bad_source["same_session_working_memory_update"]["available_for_future_two_cycle_comparison"] = False

        with self.assertRaises(ValueError):
            build_thought_memory_action_parallel_mini_loop_two_cycle_influence_check_record(bad_source)

    def test_bad_source_summary_blocks_validator(self):
        bad = copy.deepcopy(self.reach)
        bad["source_same_session_working_memory"]["source_validated"] = False

        result = validate_thought_memory_action_parallel_mini_loop_two_cycle_influence_check_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_source_validated_not_expected", result["error_codes"])

    def test_broken_evidence_links_block(self):
        cases = (
            ("first_cycle_memory_trace_link_present", False, "two_cycle_checked"),
            ("candidate_hint_trace_link_present", False, "two_cycle_checked"),
            ("hint_influenced_ordering_trace_link_present", False, "two_cycle_checked"),
            ("second_cycle_action_path_trace_link_present", False, "two_cycle_checked"),
            ("second_cycle_working_memory_trace_link_present", False, "two_cycle_checked"),
            ("second_cycle_action", "retry_same_action", "second_cycle_action_matches_hint"),
            ("second_cycle_outcome", "blocked", "outcome_memory_linked"),
        )
        for field, value, _result_field in cases:
            bad = copy.deepcopy(self.probe)
            bad["two_cycle_evidence"][field] = value

            result = validate_thought_memory_action_parallel_mini_loop_two_cycle_influence_check_record(bad)

            self.assertFalse(result["valid"])

    def test_wrong_ordering_comparison_blocks(self):
        cases = (
            ("baseline_candidate_order", ["reach_front_item"]),
            ("hint_influenced_candidate_order", ["wait_or_observe", "reach_front_item", "fallback_stop_and_report"]),
            ("candidate_set_preserved", False),
            ("candidate_order_changed", False),
            ("hinted_candidate_baseline_rank", 1),
            ("hinted_candidate_after_rank", 2),
            ("hint_moved_candidate_to_front", False),
        )
        for field, value in cases:
            bad = copy.deepcopy(self.reach)
            bad["influence_comparison"][field] = value

            result = validate_thought_memory_action_parallel_mini_loop_two_cycle_influence_check_record(bad)

            self.assertFalse(result["valid"])

    def test_influence_visibility_or_path_break_blocks(self):
        cases = (
            ("first_cycle_memory_to_hint_linked", "influence_visible"),
            ("hint_to_ordering_linked", "influence_visible"),
            ("ordering_to_action_path_linked", "influence_visible"),
            ("action_path_to_second_memory_linked", "influence_visible"),
            ("second_cycle_action_matches_top_hint", "second_cycle_action_matches_hint"),
            ("second_cycle_memory_matches_observed_outcome", "outcome_memory_linked"),
            ("influence_path_complete", "influence_visible"),
            ("influence_visible", "influence_visible"),
        )
        for field, result_field in cases:
            bad = copy.deepcopy(self.wait)
            bad["influence_comparison"][field] = False

            result = validate_thought_memory_action_parallel_mini_loop_two_cycle_influence_check_record(bad)

            self.assertFalse(result["valid"])
            self.assertFalse(result[result_field])

    def test_forbidden_comparison_flags_block(self):
        cases = (
            ("feedback_evaluation_created", "feedback_blocked"),
            ("candidate_reordering_created", "candidate_reordering_blocked"),
            ("candidate_scores_changed", "candidate_reordering_blocked"),
            ("new_selected_action_created", "action_creation_blocked"),
            ("new_execution_created", "action_creation_blocked"),
            ("working_memory_update_created", "memory_persistence_blocked"),
            ("memory_write", "memory_persistence_blocked"),
            ("predictor_read_enabled", "predictor_use_blocked"),
            ("direct_endocrine_feed", "direct_feed_blocked"),
            ("production_behavior_created", "production_behavior_blocked"),
            ("proof_of_learning_claim", "proof_claim_blocked"),
            ("consciousness_claim", "consciousness_claim_blocked"),
        )
        for field, result_field in cases:
            bad = copy.deepcopy(self.probe)
            bad["influence_comparison"][field] = True

            result = validate_thought_memory_action_parallel_mini_loop_two_cycle_influence_check_record(bad)

            self.assertFalse(result["valid"])
            self.assertFalse(result[result_field])

    def test_containment_and_audit_block_next_layer_or_production(self):
        cases = (
            (("comparison_containment", "candidate_ordering_created_in_this_package"), True, "comparison_record_only"),
            (("comparison_containment", "working_memory_update_created_in_this_package"), True, "memory_persistence_blocked"),
            (("comparison_containment", "predictor_read_enabled_in_this_package"), True, "predictor_use_blocked"),
            (("boundary_audit", "production_behavior_created"), True, "production_behavior_blocked"),
            (("boundary_audit", "next_layer_precreated"), True, "boundary_audit_passed"),
        )
        for path, value, result_field in cases:
            bad = copy.deepcopy(self.reach)
            target = bad
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value

            result = validate_thought_memory_action_parallel_mini_loop_two_cycle_influence_check_record(bad)

            self.assertFalse(result["valid"])
            self.assertFalse(result[result_field])

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(summary["two_cycle_influence_check_result_count"], 79)
        self.assertEqual(summary["valid_two_cycle_influence_check_count"], 3)
        self.assertEqual(summary["invalid_two_cycle_influence_check_count"], 76)
        self.assertEqual(summary["influence_check_created_count"], 3)
        self.assertEqual(summary["two_cycle_checked_count"], 3)
        self.assertEqual(summary["influence_visible_count"], 3)
        self.assertEqual(summary["hint_moved_candidate_to_front_count"], 3)
        self.assertEqual(summary["second_cycle_action_matches_hint_count"], 3)
        self.assertEqual(summary["outcome_memory_linked_count"], 3)
        self.assertEqual(summary["comparison_record_only_count"], 3)
        self.assertEqual(summary["reach_influence_check_count"], 1)
        self.assertEqual(summary["wait_influence_check_count"], 1)
        self.assertEqual(summary["probe_influence_check_count"], 1)
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
        result = run_command("run-thought-memory-action-parallel-mini-loop-two-cycle-influence-check-minimal-check")

        self.assertEqual(
            result["command"],
            "run-thought-memory-action-parallel-mini-loop-two-cycle-influence-check-minimal-check",
        )
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
