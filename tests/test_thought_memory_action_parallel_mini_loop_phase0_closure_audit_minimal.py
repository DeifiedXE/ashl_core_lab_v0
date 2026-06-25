import copy
import unittest

from ashl_core.teaching_cli import run_command
from ashl_core.thought_memory_action_parallel_mini_loop_phase0_closure_audit_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_thought_memory_action_parallel_mini_loop_phase0_closure_audit_record,
    run_thought_memory_action_parallel_mini_loop_phase0_closure_audit_minimal_check,
    validate_thought_memory_action_parallel_mini_loop_phase0_closure_audit_record,
)
from ashl_core.thought_memory_action_parallel_mini_loop_two_cycle_influence_check_minimal import (
    run_thought_memory_action_parallel_mini_loop_two_cycle_influence_check_minimal_check,
)


class ThoughtMemoryActionParallelMiniLoopPhase0ClosureAuditMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_thought_memory_action_parallel_mini_loop_two_cycle_influence_check_minimal_check()[
            "valid_records"
        ]
        cls.result = run_thought_memory_action_parallel_mini_loop_phase0_closure_audit_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.reach = cls.records[0]
        cls.wait = cls.records[1]
        cls.probe = cls.records[2]

    def test_valid_phase0_closure_audits_are_created(self):
        for record in self.records:
            result = validate_thought_memory_action_parallel_mini_loop_phase0_closure_audit_record(record)

            self.assertTrue(result["valid"], result["error_codes"])
            self.assertEqual(
                record["record_type"],
                "thought_memory_action_parallel_mini_loop_phase0_closure_audit_minimal",
            )
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)
            self.assertTrue(record["phase0_closure_evidence"]["closure_audit_created"])
            self.assertTrue(record["closure_criteria_audit"]["phase0_minimal_loop_complete"])

    def test_b177_two_cycle_influence_source_enters_closure_audit(self):
        record = build_thought_memory_action_parallel_mini_loop_phase0_closure_audit_record(self.sources[0])
        source = record["source_two_cycle_influence_check"]
        evidence = record["phase0_closure_evidence"]
        result = validate_thought_memory_action_parallel_mini_loop_phase0_closure_audit_record(record)

        self.assertTrue(result["valid"], result["error_codes"])
        self.assertEqual(source["source_boundary_index"], "2026-06-09-b177")
        self.assertEqual(source["cycle_count_checked"], 2)
        self.assertTrue(source["influence_visible"])
        self.assertTrue(evidence["two_cycle_influence_visible"])
        self.assertTrue(result["phase0_minimal_loop_complete"])

    def test_closure_evidence_links_all_prior_trace_ids(self):
        for record in self.records:
            source = record["source_two_cycle_influence_check"]
            evidence = record["phase0_closure_evidence"]

            self.assertEqual(
                evidence["first_cycle_working_memory_update_id"],
                source["first_cycle_working_memory_update_id"],
            )
            self.assertEqual(evidence["candidate_hint_record_id"], source["candidate_hint_record_id"])
            self.assertEqual(evidence["ordering_record_id"], source["ordering_record_id"])
            self.assertEqual(evidence["sandbox_action_path_record_id"], source["sandbox_action_path_record_id"])
            self.assertEqual(
                evidence["second_cycle_working_memory_update_id"],
                source["second_cycle_working_memory_update_id"],
            )
            self.assertEqual(
                evidence["source_two_cycle_influence_check_record_id"],
                source["source_two_cycle_influence_check_record_id"],
            )

    def test_closure_criteria_are_all_met(self):
        for record in self.records:
            criteria = record["closure_criteria_audit"]
            result = validate_thought_memory_action_parallel_mini_loop_phase0_closure_audit_record(record)

            self.assertTrue(criteria["phase0_minimal_loop_complete"])
            self.assertEqual(criteria["closure_status"], "complete_as_same_session_sandbox_record_evidence")
            self.assertEqual(criteria["criteria_met_count"], 13)
            self.assertEqual(criteria["criteria_total_count"], 13)
            self.assertTrue(all(criteria["criteria"].values()))
            self.assertTrue(result["all_closure_criteria_met"])

    def test_closure_is_record_only(self):
        for record in self.records:
            evidence = record["phase0_closure_evidence"]
            containment = record["closure_containment"]
            result = validate_thought_memory_action_parallel_mini_loop_phase0_closure_audit_record(record)

            self.assertEqual(evidence["closure_scope"], "same_session_sandbox_record_only")
            self.assertEqual(evidence["closure_evidence_authority"], "audit_only")
            self.assertTrue(evidence["record_only_audit"])
            self.assertTrue(containment["uses_existing_trace_records_only"])
            self.assertTrue(containment["no_new_source_trace_record_created"])
            self.assertTrue(result["closure_record_only"])

    def test_no_feedback_reordering_action_memory_predictor_feed_production_or_claim_is_created(self):
        for record in self.records:
            evidence = record["phase0_closure_evidence"]
            containment = record["closure_containment"]
            audit = record["boundary_audit"]
            result = validate_thought_memory_action_parallel_mini_loop_phase0_closure_audit_record(record)

            self.assertFalse(evidence["feedback_evaluation_created"])
            self.assertFalse(evidence["feedback_application_created"])
            self.assertFalse(evidence["candidate_reordering_created"])
            self.assertFalse(evidence["new_selected_action_created"])
            self.assertFalse(evidence["new_execution_created"])
            self.assertFalse(evidence["working_memory_update_created"])
            self.assertFalse(evidence["memory_write"])
            self.assertFalse(evidence["retention_write"])
            self.assertFalse(evidence["predictor_read_enabled"])
            self.assertFalse(evidence["direct_endocrine_feed"])
            self.assertFalse(evidence["production_behavior_created"])
            self.assertFalse(evidence["proof_of_learning_claim"])
            self.assertFalse(evidence["consciousness_claim"])
            self.assertFalse(containment["working_memory_update_created_in_this_package"])
            self.assertEqual(audit["boundary_number"], 178)
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
        bad_source["influence_comparison"]["influence_visible"] = False

        with self.assertRaises(ValueError):
            build_thought_memory_action_parallel_mini_loop_phase0_closure_audit_record(bad_source)

    def test_bad_source_summary_blocks_validator(self):
        bad = copy.deepcopy(self.reach)
        bad["source_two_cycle_influence_check"]["source_validated"] = False

        result = validate_thought_memory_action_parallel_mini_loop_phase0_closure_audit_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_source_validated_not_expected", result["error_codes"])

    def test_missing_or_broken_evidence_blocks(self):
        cases = (
            ("closure_audit_created", False),
            ("cycle_count_verified", 1),
            ("temporary_same_session_memory_used", False),
            ("candidate_hint_created_in_source_line", False),
            ("candidate_ordering_changed_in_source_line", False),
            ("second_cycle_action_uses_hint_path", False),
            ("second_cycle_action_observed", False),
            ("second_cycle_working_memory_updated", False),
            ("two_cycle_influence_visible", False),
            ("sandbox_only", False),
            ("record_only_audit", False),
        )
        for field, value in cases:
            bad = copy.deepcopy(self.wait)
            bad["phase0_closure_evidence"][field] = value

            result = validate_thought_memory_action_parallel_mini_loop_phase0_closure_audit_record(bad)

            self.assertFalse(result["valid"])
            if field == "closure_audit_created":
                self.assertFalse(result["phase0_closure_audit_created"])
            if field == "record_only_audit":
                self.assertFalse(result["closure_record_only"])

    def test_criteria_false_blocks_closure(self):
        cases = (
            "cycle_count_is_two",
            "temporary_same_session_memory_used",
            "candidate_hint_created",
            "next_cycle_candidate_ordering_changed",
            "second_cycle_action_uses_hint_path",
            "outcome_observed",
            "working_memory_updated_after_second_cycle",
            "two_cycle_influence_visible",
            "sandbox_only",
            "record_only_evidence",
            "long_term_memory_written_false",
            "production_behavior_created_false",
            "proof_of_learning_claim_false",
        )
        for field in cases:
            bad = copy.deepcopy(self.probe)
            bad["closure_criteria_audit"]["criteria"][field] = False
            bad["closure_criteria_audit"]["criteria_met_count"] = 12
            bad["closure_criteria_audit"]["phase0_minimal_loop_complete"] = False

            result = validate_thought_memory_action_parallel_mini_loop_phase0_closure_audit_record(bad)

            self.assertFalse(result["valid"])
            self.assertFalse(result["all_closure_criteria_met"])

    def test_forbidden_evidence_flags_block(self):
        cases = (
            ("feedback_evaluation_created", "feedback_blocked"),
            ("feedback_application_created", "feedback_blocked"),
            ("feedback_loop_created", "feedback_blocked"),
            ("candidate_reordering_created", "candidate_reordering_blocked"),
            ("candidate_scores_changed", "candidate_reordering_blocked"),
            ("runtime_next_cycle_candidate_ordering_changed", "candidate_reordering_blocked"),
            ("new_selected_action_created", "action_creation_blocked"),
            ("new_final_action_created", "action_creation_blocked"),
            ("new_direct_command_created", "action_creation_blocked"),
            ("new_execution_created", "action_creation_blocked"),
            ("new_outcome_observation_created", "action_creation_blocked"),
            ("working_memory_update_created", "memory_persistence_blocked"),
            ("long_term_memory_write", "memory_persistence_blocked"),
            ("core_memory_write", "memory_persistence_blocked"),
            ("archive_memory_write", "memory_persistence_blocked"),
            ("memory_write", "memory_persistence_blocked"),
            ("retention_write", "memory_persistence_blocked"),
            ("persistent_working_memory_written", "memory_persistence_blocked"),
            ("memory_admission_created", "memory_persistence_blocked"),
            ("predictor_read_enabled", "predictor_use_blocked"),
            ("predictor_influence_enabled", "predictor_use_blocked"),
            ("predictor_modified", "predictor_use_blocked"),
            ("direct_endocrine_feed", "direct_feed_blocked"),
            ("direct_tendency_feed", "direct_feed_blocked"),
            ("production_behavior_created", "production_behavior_blocked"),
            ("runtime_behavior_changed", "production_behavior_blocked"),
            ("production_readiness_claim", "production_behavior_blocked"),
            ("proof_of_learning_claim", "proof_claim_blocked"),
            ("long_term_learning_claim", "proof_claim_blocked"),
            ("consciousness_claim", "consciousness_claim_blocked"),
        )
        for field, result_field in cases:
            bad = copy.deepcopy(self.reach)
            bad["phase0_closure_evidence"][field] = True

            result = validate_thought_memory_action_parallel_mini_loop_phase0_closure_audit_record(bad)

            self.assertFalse(result["valid"])
            self.assertFalse(result[result_field])

    def test_containment_audit_and_blocked_flags_block(self):
        cases = (
            (("closure_containment", "feedback_evaluation_created_in_this_package"), True, "feedback_blocked"),
            (("closure_containment", "candidate_reordering_created_in_this_package"), True, "candidate_reordering_blocked"),
            (("closure_containment", "new_selected_action_created_in_this_package"), True, "action_creation_blocked"),
            (("closure_containment", "working_memory_update_created_in_this_package"), True, "memory_persistence_blocked"),
            (("closure_containment", "predictor_read_enabled_in_this_package"), True, "predictor_use_blocked"),
            (("closure_containment", "direct_endocrine_feed_in_this_package"), True, "direct_feed_blocked"),
            (("closure_containment", "production_behavior_created_in_this_package"), True, "production_behavior_blocked"),
            (("closure_containment", "proof_of_learning_claim"), True, "proof_claim_blocked"),
            (("closure_containment", "consciousness_claim"), True, "consciousness_claim_blocked"),
            (("boundary_audit", "production_behavior_created"), True, "production_behavior_blocked"),
            (("boundary_audit", "predictor_read_enabled"), True, "predictor_use_blocked"),
            (("boundary_audit", "next_layer_precreated"), True, "boundary_audit_passed"),
            (("blocked_flags", "memory_write"), True, "memory_persistence_blocked"),
            (("blocked_flags", "predictor_read_enabled"), True, "predictor_use_blocked"),
            (("blocked_flags", "proof_of_learning_claim"), True, "proof_claim_blocked"),
        )
        for path, value, result_field in cases:
            bad = copy.deepcopy(self.wait)
            target = bad
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value

            result = validate_thought_memory_action_parallel_mini_loop_phase0_closure_audit_record(bad)

            self.assertFalse(result["valid"])
            self.assertFalse(result[result_field])

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(summary["phase0_closure_audit_result_count"], 78)
        self.assertEqual(summary["valid_phase0_closure_audit_count"], 3)
        self.assertEqual(summary["invalid_phase0_closure_audit_count"], 75)
        self.assertEqual(summary["closure_audit_created_count"], 3)
        self.assertEqual(summary["phase0_minimal_loop_complete_count"], 3)
        self.assertEqual(summary["all_closure_criteria_met_count"], 3)
        self.assertEqual(summary["closure_record_only_count"], 3)
        self.assertEqual(summary["reach_closure_audit_count"], 1)
        self.assertEqual(summary["wait_closure_audit_count"], 1)
        self.assertEqual(summary["probe_closure_audit_count"], 1)
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
        result = run_command("run-thought-memory-action-parallel-mini-loop-phase0-closure-audit-minimal-check")

        self.assertEqual(
            result["command"],
            "run-thought-memory-action-parallel-mini-loop-phase0-closure-audit-minimal-check",
        )
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
