import copy
import unittest

from ashl_core.teaching_cli import run_command
from ashl_core.thought_memory_action_parallel_mini_loop_signal_readback_candidate_hint_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_thought_memory_action_parallel_mini_loop_signal_readback_candidate_hint_record,
    run_thought_memory_action_parallel_mini_loop_signal_readback_candidate_hint_minimal_check,
    validate_thought_memory_action_parallel_mini_loop_signal_readback_candidate_hint_record,
)
from ashl_core.thought_memory_action_parallel_mini_loop_temporary_alignment_signal_minimal import (
    run_thought_memory_action_parallel_mini_loop_temporary_alignment_signal_minimal_check,
)


class ThoughtMemoryActionParallelMiniLoopSignalReadbackCandidateHintMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_thought_memory_action_parallel_mini_loop_temporary_alignment_signal_minimal_check()[
            "valid_records"
        ]
        cls.result = run_thought_memory_action_parallel_mini_loop_signal_readback_candidate_hint_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.reach = cls.records[0]
        cls.wait = cls.records[1]
        cls.probe = cls.records[2]

    def test_valid_signal_readbacks_and_candidate_hints_are_created(self):
        for record in self.records:
            result = validate_thought_memory_action_parallel_mini_loop_signal_readback_candidate_hint_record(
                record
            )

            self.assertTrue(result["valid"], result["error_codes"])
            self.assertEqual(
                record["record_type"],
                "thought_memory_action_parallel_mini_loop_signal_readback_candidate_hint_minimal",
            )
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)
            self.assertTrue(record["signal_readback"]["signal_readback_created"])
            self.assertTrue(record["candidate_hint"]["candidate_hint_created"])

    def test_b172_temporary_signal_becomes_weak_hint(self):
        record = build_thought_memory_action_parallel_mini_loop_signal_readback_candidate_hint_record(
            self.sources[0]
        )
        source = record["source_temporary_alignment_signal"]
        readback = record["signal_readback"]
        hint = record["candidate_hint"]
        result = validate_thought_memory_action_parallel_mini_loop_signal_readback_candidate_hint_record(
            record
        )

        self.assertTrue(result["valid"], result["error_codes"])
        self.assertTrue(source["temporary_alignment_signal_created"])
        self.assertEqual(source["signal_label"], "temporary_thought_action_memory_alignment_signal")
        self.assertTrue(readback["signal_readback_created"])
        self.assertEqual(readback["readback_result"], "temporary_alignment_signal_read")
        self.assertTrue(readback["readback_used_for_candidate_hint"])
        self.assertTrue(hint["candidate_hint_created"])
        self.assertEqual(hint["hint_strength"], "weak")
        self.assertEqual(hint["candidate_for_hint"], "reach_front_item")

    def test_reach_wait_and_probe_hints_are_created(self):
        self.assertEqual(self.reach["candidate_hint"]["candidate_for_hint"], "reach_front_item")
        self.assertEqual(self.wait["candidate_hint"]["candidate_for_hint"], "wait_or_observe")
        self.assertEqual(
            self.probe["candidate_hint"]["candidate_for_hint"],
            "observe_or_alternative_probe",
        )

    def test_hint_is_temporary_same_session_candidate_input_only(self):
        for record in self.records:
            readback = record["signal_readback"]
            hint = record["candidate_hint"]
            containment = record["hint_containment"]

            self.assertEqual(readback["readback_scope"], "same_session_sandbox_only")
            self.assertEqual(readback["readback_authority"], "context_read_only")
            self.assertEqual(hint["hint_scope"], "same_session_sandbox_only")
            self.assertEqual(hint["hint_lifetime"], "same_session_temporary_only")
            self.assertEqual(hint["hint_authority"], "candidate_input_only")
            self.assertTrue(containment["same_session_only"])
            self.assertTrue(containment["sandbox_only"])

    def test_hint_does_not_reorder_or_select_action(self):
        for record in self.records:
            readback = record["signal_readback"]
            hint = record["candidate_hint"]
            containment = record["hint_containment"]
            result = validate_thought_memory_action_parallel_mini_loop_signal_readback_candidate_hint_record(
                record
            )

            self.assertFalse(readback["candidate_reordering_created"])
            self.assertFalse(hint["candidate_reordering_created"])
            self.assertFalse(containment["candidate_hint_applied_to_ordering"])
            self.assertFalse(containment["candidate_reordering_created_in_this_package"])
            self.assertFalse(containment["candidate_scores_changed_in_this_package"])
            self.assertFalse(hint["selected_action_created"])
            self.assertTrue(result["candidate_ordering_blocked"])
            self.assertTrue(result["action_creation_blocked"])

    def test_hint_does_not_write_memory_use_predictor_or_claim_learning(self):
        for record in self.records:
            readback = record["signal_readback"]
            hint = record["candidate_hint"]
            containment = record["hint_containment"]
            audit = record["boundary_audit"]

            self.assertFalse(readback["readback_persisted"])
            self.assertFalse(hint["memory_write_enabled"])
            self.assertFalse(hint["predictor_influence_enabled"])
            self.assertFalse(containment["memory_write_created_in_this_package"])
            self.assertFalse(containment["retention_write_created_in_this_package"])
            self.assertFalse(containment["production_behavior_created_in_this_package"])
            self.assertFalse(hint["proof_of_learning_claim"])
            self.assertFalse(audit["production_behavior_created"])

    def test_bad_source_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["source_temporary_alignment_signal"]["source_validated"] = False

        result = validate_thought_memory_action_parallel_mini_loop_signal_readback_candidate_hint_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_source_validated_not_expected", result["error_codes"])

    def test_source_already_has_readback_or_hint_blocks(self):
        cases = (
            ("source_readback_enabled_in_source", True),
            ("source_candidate_hint_created_in_source", True),
            ("source_candidate_reordering_created_in_source", True),
        )
        for field, value in cases:
            bad = copy.deepcopy(self.reach)
            bad["source_temporary_alignment_signal"][field] = value

            result = validate_thought_memory_action_parallel_mini_loop_signal_readback_candidate_hint_record(bad)

            self.assertFalse(result["valid"])
            self.assertIn(f"source_{field}_not_expected", result["error_codes"])

    def test_bad_source_candidate_blocks(self):
        bad = copy.deepcopy(self.wait)
        bad["source_temporary_alignment_signal"]["previewed_candidate"] = "retry_same_action"

        result = validate_thought_memory_action_parallel_mini_loop_signal_readback_candidate_hint_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_previewed_candidate_does_not_match_observed_candidate", result["error_codes"])
        self.assertIn("source_previewed_candidate_not_hintable", result["error_codes"])

    def test_readback_shape_blocks_invalid_cases(self):
        cases = (
            ("signal_readback_created", False),
            ("readback_scope", "production"),
            ("readback_lifetime", "persistent"),
            ("readback_authority", "candidate_ordering_authority"),
            ("readback_used_for_candidate_hint", False),
            ("readback_persisted", True),
        )
        for field, value in cases:
            bad = copy.deepcopy(self.wait)
            bad["signal_readback"][field] = value

            result = validate_thought_memory_action_parallel_mini_loop_signal_readback_candidate_hint_record(bad)

            self.assertFalse(result["valid"])
            self.assertIn(f"signal_readback_{field}_not_expected", result["error_codes"])

    def test_candidate_hint_shape_blocks_invalid_cases(self):
        cases = (
            ("candidate_hint_created", False),
            ("hint_scope", "production"),
            ("hint_lifetime", "persistent"),
            ("hint_authority", "selected_action_authority"),
            ("hint_strength", "strong"),
            ("candidate_for_hint", "retry_same_action"),
        )
        for field, value in cases:
            bad = copy.deepcopy(self.probe)
            bad["candidate_hint"][field] = value

            result = validate_thought_memory_action_parallel_mini_loop_signal_readback_candidate_hint_record(bad)

            self.assertFalse(result["valid"])
            self.assertIn(f"candidate_hint_{field}_not_expected", result["error_codes"])

    def test_reordering_action_memory_predictor_and_proof_flags_block(self):
        cases = (
            ("signal_readback", "candidate_reordering_created"),
            ("signal_readback", "action_selection_enabled"),
            ("candidate_hint", "candidate_reordering_created"),
            ("candidate_hint", "selected_action_created"),
            ("candidate_hint", "direct_command_created"),
            ("candidate_hint", "execution_created"),
            ("candidate_hint", "memory_write_enabled"),
            ("candidate_hint", "predictor_influence_enabled"),
            ("candidate_hint", "production_behavior_created"),
            ("candidate_hint", "proof_of_learning_claim"),
        )
        for section, field in cases:
            bad = copy.deepcopy(self.reach)
            bad[section][field] = True

            result = validate_thought_memory_action_parallel_mini_loop_signal_readback_candidate_hint_record(bad)

            self.assertFalse(result["valid"])

    def test_containment_blocks_next_layer_effects(self):
        cases = (
            "candidate_hint_persisted",
            "candidate_hint_applied_to_ordering",
            "candidate_reordering_created_in_this_package",
            "candidate_scores_changed_in_this_package",
            "runtime_next_cycle_candidate_ordering_changed_in_this_package",
            "selected_action_created_in_this_package",
            "direct_command_created_in_this_package",
            "execution_created_in_this_package",
            "memory_write_created_in_this_package",
            "retention_write_created_in_this_package",
            "predictor_read_enabled_in_this_package",
            "production_behavior_created_in_this_package",
            "proof_of_learning_claim",
        )
        for field in cases:
            bad = copy.deepcopy(self.wait)
            bad["hint_containment"][field] = True

            result = validate_thought_memory_action_parallel_mini_loop_signal_readback_candidate_hint_record(bad)

            self.assertFalse(result["valid"])
            self.assertIn(f"hint_containment_{field}_not_expected", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(summary["candidate_hint_result_count"], 56)
        self.assertEqual(summary["valid_candidate_hint_count"], 3)
        self.assertEqual(summary["invalid_candidate_hint_count"], 53)
        self.assertEqual(summary["signal_readback_created_count"], 3)
        self.assertEqual(summary["candidate_hint_created_count"], 3)
        self.assertEqual(summary["reach_hint_count"], 1)
        self.assertEqual(summary["wait_hint_count"], 1)
        self.assertEqual(summary["probe_hint_count"], 1)
        self.assertEqual(summary["candidate_ordering_blocked_count"], 3)
        self.assertEqual(summary["action_creation_blocked_count"], 3)
        self.assertEqual(summary["hint_persistence_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_use_blocked_count"], 3)
        self.assertEqual(summary["production_behavior_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)
        self.assertEqual(summary["boundary_audit_passed_count"], 3)

    def test_cli_command(self):
        result = run_command(
            "run-thought-memory-action-parallel-mini-loop-signal-readback-candidate-hint-minimal-check"
        )

        self.assertEqual(
            result["command"],
            "run-thought-memory-action-parallel-mini-loop-signal-readback-candidate-hint-minimal-check",
        )
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
