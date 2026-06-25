import copy
import unittest

from ashl_core.teaching_cli import run_command
from ashl_core.thought_memory_action_parallel_mini_loop_candidate_hint_into_ordering_minimal import (
    run_thought_memory_action_parallel_mini_loop_candidate_hint_into_ordering_minimal_check,
)
from ashl_core.thought_memory_action_parallel_mini_loop_ordering_to_next_sandbox_action_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_thought_memory_action_parallel_mini_loop_ordering_to_next_sandbox_action_record,
    run_thought_memory_action_parallel_mini_loop_ordering_to_next_sandbox_action_minimal_check,
    validate_thought_memory_action_parallel_mini_loop_ordering_to_next_sandbox_action_record,
)


class ThoughtMemoryActionParallelMiniLoopOrderingToNextSandboxActionMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_thought_memory_action_parallel_mini_loop_candidate_hint_into_ordering_minimal_check()[
            "valid_records"
        ]
        cls.result = run_thought_memory_action_parallel_mini_loop_ordering_to_next_sandbox_action_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.reach = cls.records[0]
        cls.wait = cls.records[1]
        cls.probe = cls.records[2]

    def test_valid_compact_sandbox_action_paths_are_created(self):
        for record in self.records:
            result = validate_thought_memory_action_parallel_mini_loop_ordering_to_next_sandbox_action_record(
                record
            )

            self.assertTrue(result["valid"], result["error_codes"])
            self.assertEqual(
                record["record_type"],
                "thought_memory_action_parallel_mini_loop_ordering_to_next_sandbox_action_minimal",
            )
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)
            self.assertTrue(record["compact_sandbox_action_path"]["compact_action_path_created"])

    def test_b174_top_hint_becomes_selected_action(self):
        record = build_thought_memory_action_parallel_mini_loop_ordering_to_next_sandbox_action_record(
            self.sources[0]
        )
        source = record["source_candidate_hint_ordering"]
        path = record["compact_sandbox_action_path"]
        result = validate_thought_memory_action_parallel_mini_loop_ordering_to_next_sandbox_action_record(
            record
        )

        self.assertTrue(result["valid"], result["error_codes"])
        self.assertEqual(source["primary_ranked_action"], "reach_front_item")
        self.assertEqual(path["selected_action"], source["primary_ranked_action"])
        self.assertEqual(path["selected_action_source"], "b174_hint_influenced_advisory_ordering")

    def test_reach_wait_and_probe_each_run_one_sandbox_action_path(self):
        expected = [
            ("reach_front_item", "sandbox.arbitration.reach_front_item", "front_item_reached"),
            ("wait_or_observe", "sandbox.arbitration.wait_or_observe", "local_context_observed"),
            (
                "observe_or_alternative_probe",
                "sandbox.arbitration.observe_or_alternative_probe",
                "local_context_observed",
            ),
        ]
        for record, (action, command, observed_outcome) in zip(self.records, expected):
            path = record["compact_sandbox_action_path"]

            self.assertEqual(path["selected_action"], action)
            self.assertEqual(path["final_action"], action)
            self.assertEqual(path["direct_command"], command)
            self.assertEqual(path["execution_count"], 1)
            self.assertEqual(path["observed_outcome"], observed_outcome)

    def test_trace_links_preserve_source_ordering_hint_and_working_memory_refs(self):
        for record in self.records:
            source = record["source_candidate_hint_ordering"]
            links = record["compact_sandbox_action_path"]["trace_links"]

            self.assertEqual(links["source_ordering_record_id"], source["source_ordering_record_id"])
            self.assertEqual(links["source_candidate_hint_record_id"], source["source_candidate_hint_record_id"])
            self.assertEqual(links["source_working_memory_update_id"], source["source_working_memory_update_id"])
            self.assertEqual(links["source_boundary_index"], "2026-06-09-b174")
            self.assertEqual(links["source_primary_ranked_action"], source["primary_ranked_action"])

    def test_action_path_creates_selection_command_execution_and_observation_once(self):
        for record in self.records:
            path = record["compact_sandbox_action_path"]
            containment = record["action_path_containment"]
            result = validate_thought_memory_action_parallel_mini_loop_ordering_to_next_sandbox_action_record(
                record
            )

            self.assertTrue(path["selected_action_created"])
            self.assertTrue(path["final_action_created"])
            self.assertTrue(path["direct_command_created"])
            self.assertTrue(path["execution_created"])
            self.assertTrue(path["sandbox_action_executed"])
            self.assertTrue(path["outcome_observation_created"])
            self.assertEqual(path["execution_count"], 1)
            self.assertTrue(containment["execution_count_limited_to_one"])
            self.assertTrue(result["selected_action_created"])
            self.assertTrue(result["outcome_observation_created"])

    def test_does_not_update_memory_feedback_reordering_scores_or_runtime_ordering(self):
        for record in self.records:
            path = record["compact_sandbox_action_path"]
            containment = record["action_path_containment"]
            result = validate_thought_memory_action_parallel_mini_loop_ordering_to_next_sandbox_action_record(
                record
            )

            self.assertFalse(path["working_memory_update_created"])
            self.assertFalse(path["feedback_evaluation_created"])
            self.assertFalse(path["feedback_application_created"])
            self.assertFalse(path["candidate_reordering_created"])
            self.assertFalse(path["candidate_scores_changed"])
            self.assertFalse(containment["runtime_next_cycle_candidate_ordering_changed_in_this_package"])
            self.assertTrue(result["working_memory_update_blocked"])
            self.assertTrue(result["feedback_blocked"])
            self.assertTrue(result["candidate_reordering_blocked"])

    def test_does_not_write_memory_use_predictor_feed_or_claim_proof(self):
        for record in self.records:
            path = record["compact_sandbox_action_path"]
            audit = record["boundary_audit"]
            result = validate_thought_memory_action_parallel_mini_loop_ordering_to_next_sandbox_action_record(
                record
            )

            self.assertFalse(path["memory_write_created"])
            self.assertFalse(path["retention_write_created"])
            self.assertFalse(path["predictor_read_enabled"])
            self.assertFalse(path["predictor_influence_enabled"])
            self.assertFalse(path["direct_endocrine_feed"])
            self.assertFalse(path["direct_tendency_feed"])
            self.assertFalse(path["proof_of_learning_claim"])
            self.assertFalse(audit["production_behavior_created"])
            self.assertTrue(result["memory_write_blocked"])
            self.assertTrue(result["predictor_use_blocked"])
            self.assertTrue(result["direct_feed_blocked"])
            self.assertTrue(result["production_behavior_blocked"])
            self.assertTrue(result["proof_claim_blocked"])

    def test_bad_source_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["source_candidate_hint_ordering"]["source_validated"] = False

        result = validate_thought_memory_action_parallel_mini_loop_ordering_to_next_sandbox_action_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_source_validated_not_expected", result["error_codes"])

    def test_wrong_selected_command_or_outcome_blocks(self):
        cases = (
            ("selected_action", "wait_or_observe", "compact_sandbox_action_path_selected_action_not_expected"),
            ("direct_command", "sandbox.production.reach_front_item", "compact_sandbox_action_path_direct_command_not_expected"),
            ("observed_outcome", "blocked", "compact_sandbox_action_path_observed_outcome_not_expected"),
        )
        for field, value, error in cases:
            bad = copy.deepcopy(self.reach)
            bad["compact_sandbox_action_path"][field] = value

            result = validate_thought_memory_action_parallel_mini_loop_ordering_to_next_sandbox_action_record(
                bad
            )

            self.assertFalse(result["valid"])
            self.assertIn(error, result["error_codes"])

    def test_working_memory_feedback_and_reordering_flags_block(self):
        cases = (
            ("working_memory_update_created", "working_memory_update_blocked"),
            ("feedback_evaluation_created", "feedback_blocked"),
            ("feedback_application_created", "feedback_blocked"),
            ("candidate_reordering_created", "candidate_reordering_blocked"),
            ("candidate_scores_changed", "candidate_reordering_blocked"),
        )
        for field, result_field in cases:
            bad = copy.deepcopy(self.probe)
            bad["compact_sandbox_action_path"][field] = True

            result = validate_thought_memory_action_parallel_mini_loop_ordering_to_next_sandbox_action_record(
                bad
            )

            self.assertFalse(result["valid"])
            self.assertFalse(result[result_field])

    def test_memory_predictor_direct_feed_production_and_proof_flags_block(self):
        cases = (
            ("memory_write_created", "memory_write_blocked"),
            ("predictor_read_enabled", "predictor_use_blocked"),
            ("direct_endocrine_feed", "direct_feed_blocked"),
            ("production_behavior_created", "production_behavior_blocked"),
            ("proof_of_learning_claim", "proof_claim_blocked"),
            ("consciousness_claim", "consciousness_claim_blocked"),
        )
        for field, result_field in cases:
            bad = copy.deepcopy(self.wait)
            bad["compact_sandbox_action_path"][field] = True

            result = validate_thought_memory_action_parallel_mini_loop_ordering_to_next_sandbox_action_record(
                bad
            )

            self.assertFalse(result["valid"])
            self.assertFalse(result[result_field])

    def test_hallucination_self_check_is_present_and_blocks_bad_claims(self):
        for record in self.records:
            result = validate_thought_memory_action_parallel_mini_loop_ordering_to_next_sandbox_action_record(
                record
            )
            self.assertTrue(record["hallucination_self_check"]["triggered"])
            self.assertTrue(result["hallucination_self_check_passed"])

        bad = copy.deepcopy(self.reach)
        bad["hallucination_self_check"]["sandbox_only_not_production"] = False
        result = validate_thought_memory_action_parallel_mini_loop_ordering_to_next_sandbox_action_record(bad)

        self.assertFalse(result["valid"])
        self.assertFalse(result["hallucination_self_check_passed"])

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(summary["compact_sandbox_action_path_result_count"], 114)
        self.assertEqual(summary["valid_compact_sandbox_action_path_count"], 3)
        self.assertEqual(summary["invalid_compact_sandbox_action_path_count"], 111)
        self.assertEqual(summary["compact_action_path_created_count"], 3)
        self.assertEqual(summary["selected_action_created_count"], 3)
        self.assertEqual(summary["final_action_created_count"], 3)
        self.assertEqual(summary["direct_command_created_count"], 3)
        self.assertEqual(summary["execution_created_count"], 3)
        self.assertEqual(summary["sandbox_action_executed_count"], 3)
        self.assertEqual(summary["outcome_observation_created_count"], 3)
        self.assertEqual(summary["reach_action_path_count"], 1)
        self.assertEqual(summary["wait_action_path_count"], 1)
        self.assertEqual(summary["probe_action_path_count"], 1)
        self.assertEqual(summary["working_memory_update_blocked_count"], 3)
        self.assertEqual(summary["feedback_blocked_count"], 3)
        self.assertEqual(summary["candidate_reordering_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_use_blocked_count"], 3)
        self.assertEqual(summary["direct_feed_blocked_count"], 3)
        self.assertEqual(summary["production_behavior_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)
        self.assertEqual(summary["consciousness_claim_blocked_count"], 3)
        self.assertEqual(summary["boundary_audit_passed_count"], 3)
        self.assertEqual(summary["hallucination_self_check_passed_count"], 3)

    def test_cli_command(self):
        result = run_command(
            "run-thought-memory-action-parallel-mini-loop-ordering-to-next-sandbox-action-minimal-check"
        )

        self.assertEqual(
            result["command"],
            "run-thought-memory-action-parallel-mini-loop-ordering-to-next-sandbox-action-minimal-check",
        )
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
