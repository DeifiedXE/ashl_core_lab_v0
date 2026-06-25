import copy
import unittest

from ashl_core.teaching_cli import run_command
from ashl_core.thought_memory_action_parallel_mini_loop_consistency_evaluation_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_thought_memory_action_parallel_mini_loop_consistency_evaluation_record,
    run_thought_memory_action_parallel_mini_loop_consistency_evaluation_minimal_check,
    validate_thought_memory_action_parallel_mini_loop_consistency_evaluation_record,
)
from ashl_core.thought_memory_action_parallel_mini_loop_minimal import (
    run_thought_memory_action_parallel_mini_loop_minimal_check,
)


class ThoughtMemoryActionParallelMiniLoopConsistencyEvaluationMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_thought_memory_action_parallel_mini_loop_minimal_check()["valid_records"]
        cls.result = run_thought_memory_action_parallel_mini_loop_consistency_evaluation_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.reach = cls.records[0]
        cls.wait = cls.records[1]
        cls.probe = cls.records[2]

    def test_valid_consistency_evaluation_records_are_created(self):
        for record in self.records:
            result = validate_thought_memory_action_parallel_mini_loop_consistency_evaluation_record(
                record
            )

            self.assertTrue(result["valid"], result["error_codes"])
            self.assertEqual(
                record["record_type"],
                "thought_memory_action_parallel_mini_loop_consistency_evaluation_minimal",
            )
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)
            self.assertTrue(record["consistency_evaluation"]["consistency_evaluation_created"])

    def test_evaluation_checks_thought_action_memory_alignment(self):
        record = build_thought_memory_action_parallel_mini_loop_consistency_evaluation_record(
            self.sources[0]
        )
        evaluation = record["consistency_evaluation"]
        result = validate_thought_memory_action_parallel_mini_loop_consistency_evaluation_record(record)

        self.assertTrue(result["valid"], result["error_codes"])
        self.assertTrue(evaluation["preview_candidate_matches_action_observation"])
        self.assertTrue(evaluation["working_memory_links_preview_and_observation"])
        self.assertTrue(evaluation["preview_not_treated_as_reality"])
        self.assertEqual(evaluation["alignment_label"], "thought_action_memory_aligned")

    def test_reach_wait_and_probe_are_evaluated(self):
        self.assertEqual(self.reach["source_parallel_mini_loop"]["previewed_candidate"], "reach_front_item")
        self.assertEqual(self.wait["source_parallel_mini_loop"]["previewed_candidate"], "wait_or_observe")
        self.assertEqual(
            self.probe["source_parallel_mini_loop"]["previewed_candidate"],
            "observe_or_alternative_probe",
        )

    def test_evaluation_does_not_create_signal_hint_or_next_cycle_read(self):
        for record in self.records:
            evaluation = record["consistency_evaluation"]
            result = record["evaluation_result"]

            self.assertFalse(evaluation["mismatch_signal_created"])
            self.assertFalse(evaluation["temporary_learning_signal_created"])
            self.assertFalse(evaluation["candidate_hint_created"])
            self.assertFalse(evaluation["next_cycle_read_enabled"])
            self.assertFalse(result["temporary_signal_created_in_this_package"])
            self.assertFalse(result["candidate_hint_created_in_this_package"])
            self.assertFalse(result["next_cycle_read_created_in_this_package"])

    def test_evaluation_does_not_create_action_or_memory_behavior(self):
        for record in self.records:
            result = record["evaluation_result"]
            blocked = record["blocked_flags"]

            self.assertFalse(result["behavior_change_created_in_this_package"])
            self.assertFalse(result["memory_write_created_in_this_package"])
            self.assertFalse(blocked["selected_action_created"])
            self.assertFalse(blocked["direct_command_created"])
            self.assertFalse(blocked["execution_created"])
            self.assertFalse(blocked["memory_write"])
            self.assertFalse(blocked["retention_write"])
            self.assertFalse(blocked["predictor_read_enabled"])
            self.assertFalse(blocked["proof_of_learning_claim"])

    def test_boundary_audit_is_present(self):
        for record in self.records:
            audit = record["boundary_audit"]
            result = validate_thought_memory_action_parallel_mini_loop_consistency_evaluation_record(
                record
            )

            self.assertTrue(result["boundary_audit_passed"])
            self.assertTrue(audit["triggered"])
            self.assertEqual(audit["boundary_number"], 171)
            self.assertFalse(audit["production_behavior_created"])
            self.assertFalse(audit["memory_write_created"])
            self.assertFalse(audit["predictor_read_enabled"])

    def test_bad_source_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["source_parallel_mini_loop"]["source_validated"] = False

        result = validate_thought_memory_action_parallel_mini_loop_consistency_evaluation_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_source_validated_not_expected", result["error_codes"])

    def test_source_candidate_mismatch_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["source_parallel_mini_loop"]["observed_candidate"] = "wait_or_observe"

        result = validate_thought_memory_action_parallel_mini_loop_consistency_evaluation_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_previewed_candidate_does_not_match_observed_candidate", result["error_codes"])

    def test_preview_as_reality_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["source_parallel_mini_loop"]["preview_result_treated_as_observed_outcome"] = True

        result = validate_thought_memory_action_parallel_mini_loop_consistency_evaluation_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn(
            "source_preview_result_treated_as_observed_outcome_not_expected",
            result["error_codes"],
        )

    def test_evaluation_false_alignment_blocks(self):
        for field in (
            "preview_candidate_matches_action_observation",
            "working_memory_links_preview_and_observation",
            "preview_not_treated_as_reality",
            "action_evidence_source_checked",
            "temporary_memory_scope_checked",
            "cycle_budget_respected",
        ):
            bad = copy.deepcopy(self.wait)
            bad["consistency_evaluation"][field] = False

            result = validate_thought_memory_action_parallel_mini_loop_consistency_evaluation_record(bad)

            self.assertFalse(result["valid"])
            self.assertIn(f"consistency_evaluation_{field}_not_expected", result["error_codes"])

    def test_signal_hint_or_next_cycle_read_blocks(self):
        cases = (
            ("consistency_evaluation", "mismatch_signal_created"),
            ("consistency_evaluation", "temporary_learning_signal_created"),
            ("consistency_evaluation", "candidate_hint_created"),
            ("consistency_evaluation", "next_cycle_read_enabled"),
            ("evaluation_result", "temporary_signal_created_in_this_package"),
            ("evaluation_result", "candidate_hint_created_in_this_package"),
            ("evaluation_result", "next_cycle_read_created_in_this_package"),
        )
        for section, field in cases:
            bad = copy.deepcopy(self.probe)
            bad[section][field] = True

            result = validate_thought_memory_action_parallel_mini_loop_consistency_evaluation_record(bad)

            self.assertFalse(result["valid"])
            self.assertIn(f"{section}_{field}_not_expected", result["error_codes"])

    def test_action_memory_predictor_and_proof_blocks(self):
        cases = (
            ("blocked_flags", "selected_action_created"),
            ("blocked_flags", "direct_command_created"),
            ("blocked_flags", "execution_created"),
            ("evaluation_result", "memory_write_created_in_this_package"),
            ("blocked_flags", "retention_write"),
            ("boundary_audit", "predictor_read_enabled"),
            ("boundary_audit", "predictor_influence_enabled"),
            ("boundary_audit", "direct_endocrine_feed"),
            ("boundary_audit", "direct_tendency_feed"),
            ("boundary_audit", "production_behavior_created"),
            ("evaluation_result", "proof_of_learning_claim"),
        )
        for section, field in cases:
            bad = copy.deepcopy(self.reach)
            bad[section][field] = True

            result = validate_thought_memory_action_parallel_mini_loop_consistency_evaluation_record(bad)

            self.assertFalse(result["valid"])

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(summary["consistency_evaluation_result_count"], 46)
        self.assertEqual(summary["valid_consistency_evaluation_count"], 3)
        self.assertEqual(summary["invalid_consistency_evaluation_count"], 43)
        self.assertEqual(summary["consistency_evaluation_created_count"], 3)
        self.assertEqual(summary["aligned_evaluation_count"], 3)
        self.assertEqual(summary["preview_action_match_count"], 3)
        self.assertEqual(summary["working_memory_alignment_checked_count"], 3)
        self.assertEqual(summary["reach_evaluation_count"], 1)
        self.assertEqual(summary["wait_evaluation_count"], 1)
        self.assertEqual(summary["probe_evaluation_count"], 1)
        self.assertEqual(summary["temporary_signal_blocked_count"], 3)
        self.assertEqual(summary["candidate_hint_blocked_count"], 3)
        self.assertEqual(summary["next_cycle_read_blocked_count"], 3)
        self.assertEqual(summary["action_creation_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_use_blocked_count"], 3)
        self.assertEqual(summary["production_behavior_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)
        self.assertEqual(summary["boundary_audit_passed_count"], 3)

    def test_cli_command(self):
        result = run_command(
            "run-thought-memory-action-parallel-mini-loop-consistency-evaluation-minimal-check"
        )

        self.assertEqual(
            result["command"],
            "run-thought-memory-action-parallel-mini-loop-consistency-evaluation-minimal-check",
        )
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
