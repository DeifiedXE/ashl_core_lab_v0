import copy
import unittest

from ashl_core.teaching_cli import run_command
from ashl_core.thought_memory_action_parallel_mini_loop_consistency_evaluation_minimal import (
    run_thought_memory_action_parallel_mini_loop_consistency_evaluation_minimal_check,
)
from ashl_core.thought_memory_action_parallel_mini_loop_temporary_alignment_signal_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_thought_memory_action_parallel_mini_loop_temporary_alignment_signal_record,
    run_thought_memory_action_parallel_mini_loop_temporary_alignment_signal_minimal_check,
    validate_thought_memory_action_parallel_mini_loop_temporary_alignment_signal_record,
)


class ThoughtMemoryActionParallelMiniLoopTemporaryAlignmentSignalMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_thought_memory_action_parallel_mini_loop_consistency_evaluation_minimal_check()[
            "valid_records"
        ]
        cls.result = run_thought_memory_action_parallel_mini_loop_temporary_alignment_signal_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.reach = cls.records[0]
        cls.wait = cls.records[1]
        cls.probe = cls.records[2]

    def test_valid_temporary_alignment_signals_are_created(self):
        for record in self.records:
            result = validate_thought_memory_action_parallel_mini_loop_temporary_alignment_signal_record(
                record
            )

            self.assertTrue(result["valid"], result["error_codes"])
            self.assertEqual(
                record["record_type"],
                "thought_memory_action_parallel_mini_loop_temporary_alignment_signal_minimal",
            )
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)
            self.assertTrue(record["temporary_alignment_signal"]["temporary_alignment_signal_created"])

    def test_b171_consistency_evaluation_becomes_temporary_signal(self):
        record = build_thought_memory_action_parallel_mini_loop_temporary_alignment_signal_record(
            self.sources[0]
        )
        source = record["source_consistency_evaluation"]
        signal = record["temporary_alignment_signal"]
        result = validate_thought_memory_action_parallel_mini_loop_temporary_alignment_signal_record(
            record
        )

        self.assertTrue(result["valid"], result["error_codes"])
        self.assertTrue(source["consistency_evaluation_created"])
        self.assertTrue(source["preview_candidate_matches_action_observation"])
        self.assertTrue(source["working_memory_links_preview_and_observation"])
        self.assertEqual(signal["signal_label"], "temporary_thought_action_memory_alignment_signal")
        self.assertEqual(signal["signal_value"], "thought_action_memory_aligned")

    def test_reach_wait_and_probe_signals_are_created(self):
        self.assertEqual(self.reach["source_consistency_evaluation"]["previewed_candidate"], "reach_front_item")
        self.assertEqual(self.wait["source_consistency_evaluation"]["previewed_candidate"], "wait_or_observe")
        self.assertEqual(
            self.probe["source_consistency_evaluation"]["previewed_candidate"],
            "observe_or_alternative_probe",
        )

    def test_signal_is_temporary_same_session_sandbox_only(self):
        for record in self.records:
            signal = record["temporary_alignment_signal"]
            containment = record["signal_containment"]

            self.assertEqual(signal["signal_scope"], "same_session_sandbox_only")
            self.assertEqual(signal["signal_lifetime"], "same_session_temporary_only")
            self.assertEqual(signal["signal_authority"], "record_only_context_marker")
            self.assertTrue(containment["same_session_only"])
            self.assertTrue(containment["sandbox_only"])
            self.assertFalse(containment["persistent_signal_written"])

    def test_signal_does_not_enable_readback_hint_or_reordering(self):
        for record in self.records:
            signal = record["temporary_alignment_signal"]
            containment = record["signal_containment"]
            result = validate_thought_memory_action_parallel_mini_loop_temporary_alignment_signal_record(
                record
            )

            self.assertFalse(signal["readback_enabled"])
            self.assertFalse(signal["candidate_hint_created"])
            self.assertFalse(signal["candidate_reordering_created"])
            self.assertFalse(containment["next_cycle_read_enabled"])
            self.assertFalse(containment["candidate_hint_created_in_this_package"])
            self.assertFalse(containment["candidate_reordering_created_in_this_package"])
            self.assertTrue(result["readback_blocked"])
            self.assertTrue(result["candidate_hint_blocked"])
            self.assertTrue(result["candidate_reordering_blocked"])

    def test_signal_does_not_create_action_memory_predictor_or_proof(self):
        for record in self.records:
            signal = record["temporary_alignment_signal"]
            containment = record["signal_containment"]
            audit = record["boundary_audit"]

            self.assertFalse(signal["action_selection_enabled"])
            self.assertFalse(signal["memory_write_enabled"])
            self.assertFalse(signal["predictor_influence_enabled"])
            self.assertFalse(containment["selected_action_created_in_this_package"])
            self.assertFalse(containment["direct_command_created_in_this_package"])
            self.assertFalse(containment["execution_created_in_this_package"])
            self.assertFalse(containment["memory_write_created_in_this_package"])
            self.assertFalse(containment["proof_of_learning_claim"])
            self.assertFalse(audit["production_behavior_created"])

    def test_bad_source_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["source_consistency_evaluation"]["source_validated"] = False

        result = validate_thought_memory_action_parallel_mini_loop_temporary_alignment_signal_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_source_validated_not_expected", result["error_codes"])

    def test_source_already_has_signal_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["source_consistency_evaluation"]["source_temporary_signal_created_in_source"] = True

        result = validate_thought_memory_action_parallel_mini_loop_temporary_alignment_signal_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn(
            "source_source_temporary_signal_created_in_source_not_expected",
            result["error_codes"],
        )

    def test_wrong_signal_label_or_scope_blocks(self):
        cases = (
            ("signal_label", "candidate_hint"),
            ("signal_scope", "production"),
            ("signal_lifetime", "persistent"),
            ("signal_authority", "candidate_ordering_authority"),
        )
        for field, value in cases:
            bad = copy.deepcopy(self.wait)
            bad["temporary_alignment_signal"][field] = value

            result = validate_thought_memory_action_parallel_mini_loop_temporary_alignment_signal_record(bad)

            self.assertFalse(result["valid"])
            self.assertIn(f"temporary_alignment_signal_{field}_not_expected", result["error_codes"])

    def test_readback_hint_or_reordering_true_blocks(self):
        cases = (
            ("temporary_alignment_signal", "readback_enabled"),
            ("temporary_alignment_signal", "candidate_hint_created"),
            ("temporary_alignment_signal", "candidate_reordering_created"),
            ("signal_containment", "next_cycle_read_enabled"),
            ("signal_containment", "candidate_hint_created_in_this_package"),
            ("signal_containment", "candidate_reordering_created_in_this_package"),
        )
        for section, field in cases:
            bad = copy.deepcopy(self.probe)
            bad[section][field] = True

            result = validate_thought_memory_action_parallel_mini_loop_temporary_alignment_signal_record(bad)

            self.assertFalse(result["valid"])
            self.assertIn(f"{section}_{field}_not_expected", result["error_codes"])

    def test_new_action_or_execution_true_blocks(self):
        cases = (
            ("temporary_alignment_signal", "action_selection_enabled"),
            ("signal_containment", "selected_action_created_in_this_package"),
            ("signal_containment", "final_action_created_in_this_package"),
            ("signal_containment", "direct_command_created_in_this_package"),
            ("signal_containment", "execution_created_in_this_package"),
            ("signal_containment", "new_outcome_observation_created_in_this_package"),
        )
        for section, field in cases:
            bad = copy.deepcopy(self.reach)
            bad[section][field] = True

            result = validate_thought_memory_action_parallel_mini_loop_temporary_alignment_signal_record(bad)

            self.assertFalse(result["valid"])

    def test_memory_predictor_production_and_proof_flags_block(self):
        cases = (
            ("temporary_alignment_signal", "memory_write_enabled"),
            ("temporary_alignment_signal", "predictor_influence_enabled"),
            ("signal_containment", "memory_write_created_in_this_package"),
            ("signal_containment", "retention_write_created_in_this_package"),
            ("signal_containment", "predictor_read_enabled_in_this_package"),
            ("signal_containment", "predictor_influence_enabled_in_this_package"),
            ("signal_containment", "predictor_modified_in_this_package"),
            ("signal_containment", "production_behavior_created_in_this_package"),
            ("signal_containment", "proof_of_learning_claim"),
            ("boundary_audit", "direct_endocrine_feed"),
            ("boundary_audit", "direct_tendency_feed"),
        )
        for section, field in cases:
            bad = copy.deepcopy(self.wait)
            bad[section][field] = True

            result = validate_thought_memory_action_parallel_mini_loop_temporary_alignment_signal_record(bad)

            self.assertFalse(result["valid"])

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(summary["temporary_alignment_signal_result_count"], 51)
        self.assertEqual(summary["valid_temporary_alignment_signal_count"], 3)
        self.assertEqual(summary["invalid_temporary_alignment_signal_count"], 48)
        self.assertEqual(summary["temporary_alignment_signal_created_count"], 3)
        self.assertEqual(summary["reach_signal_count"], 1)
        self.assertEqual(summary["wait_signal_count"], 1)
        self.assertEqual(summary["probe_signal_count"], 1)
        self.assertEqual(summary["readback_blocked_count"], 3)
        self.assertEqual(summary["candidate_hint_blocked_count"], 3)
        self.assertEqual(summary["candidate_reordering_blocked_count"], 3)
        self.assertEqual(summary["action_creation_blocked_count"], 3)
        self.assertEqual(summary["signal_persistence_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_use_blocked_count"], 3)
        self.assertEqual(summary["production_behavior_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)
        self.assertEqual(summary["boundary_audit_passed_count"], 3)

    def test_cli_command(self):
        result = run_command(
            "run-thought-memory-action-parallel-mini-loop-temporary-alignment-signal-minimal-check"
        )

        self.assertEqual(
            result["command"],
            "run-thought-memory-action-parallel-mini-loop-temporary-alignment-signal-minimal-check",
        )
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
