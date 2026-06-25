import copy
import unittest

from ashl_core.phase1_runtime_session_trace_spine_minimal import (
    BOUNDARY_INDEX_AFTER,
    BOUNDARY_INDEX_BEFORE,
    EXPECTED_TICK_COUNT,
    build_phase1_runtime_session_trace_spine_record,
    run_phase1_runtime_session_trace_spine_minimal_check,
    validate_phase1_runtime_session_trace_spine_record,
)
from ashl_core.teaching_cli import run_command
from ashl_core.thought_memory_action_parallel_mini_loop_phase0_closure_audit_minimal import (
    run_thought_memory_action_parallel_mini_loop_phase0_closure_audit_minimal_check,
)


class Phase1RuntimeSessionTraceSpineMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_thought_memory_action_parallel_mini_loop_phase0_closure_audit_minimal_check()[
            "valid_records"
        ]
        cls.result = run_phase1_runtime_session_trace_spine_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.reach = cls.records[0]
        cls.wait = cls.records[1]
        cls.probe = cls.records[2]

    def test_valid_runtime_session_trace_spines_are_created(self):
        for record in self.records:
            result = validate_phase1_runtime_session_trace_spine_record(record)

            self.assertTrue(result["valid"], result["error_codes"])
            self.assertEqual(record["record_type"], "phase1_runtime_session_trace_spine_minimal")
            self.assertEqual(record["boundary_index_before"], BOUNDARY_INDEX_BEFORE)
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)
            self.assertTrue(record["session_trace_spine"]["session_trace_spine_created"])
            self.assertTrue(record["session_trace_spine"]["runtime_tick_sequence_created"])

    def test_b178_closure_audit_source_enters_trace_spine(self):
        record = build_phase1_runtime_session_trace_spine_record(self.sources[0])
        source = record["source_phase0_closure_audit"]
        spine = record["session_trace_spine"]
        result = validate_phase1_runtime_session_trace_spine_record(record)

        self.assertTrue(result["valid"], result["error_codes"])
        self.assertEqual(source["source_boundary_index"], "2026-06-09-b178")
        self.assertTrue(source["source_validated"])
        self.assertTrue(source["phase0_minimal_loop_complete"])
        self.assertEqual(source["closure_criteria_met_count"], 13)
        self.assertEqual(spine["source_closure_audit_record_id"], source["source_phase0_closure_audit_record_id"])
        self.assertTrue(spine["phase0_closure_link_preserved"])

    def test_session_id_and_tick_order_are_deterministic(self):
        record = self.reach
        spine = record["session_trace_spine"]
        ticks = record["runtime_tick_trace"]["ordered_ticks"]

        self.assertEqual(spine["session_id"], "phase1_session_item_reachable_feedback_prioritizes_reach_001")
        self.assertEqual(spine["tick_count"], EXPECTED_TICK_COUNT)
        self.assertEqual([tick["tick_index"] for tick in ticks], list(range(EXPECTED_TICK_COUNT)))
        self.assertEqual(spine["ordered_tick_ids"], [tick["tick_id"] for tick in ticks])
        self.assertEqual(ticks[0]["tick_label"], "phase0_closure_audit_ingested")
        self.assertEqual(ticks[-1]["tick_label"], "two_cycle_influence_and_closure")

    def test_each_tick_has_state_expected_actual_and_evaluator(self):
        for record in self.records:
            source = record["source_phase0_closure_audit"]
            ticks = record["runtime_tick_trace"]["ordered_ticks"]
            for tick in ticks:
                state = tick["state_snapshot"]

                self.assertEqual(state["state_snapshot_kind"], "trace_state_summary")
                self.assertEqual(state["scenario_id"], source["scenario_id"])
                self.assertEqual(state["approved_purpose"], source["approved_purpose"])
                self.assertEqual(state["selected_action"], source["selected_action"])
                self.assertTrue(tick["expected_outcome"])
                self.assertTrue(tick["actual_outcome"])
                self.assertTrue(tick["evaluator_result"])
                self.assertTrue(tick["trace_linked"])

    def test_trace_spine_is_record_only(self):
        for record in self.records:
            spine = record["session_trace_spine"]
            tick_trace = record["runtime_tick_trace"]
            expected_actual = record["expected_actual_evaluator_trace"]
            containment = record["session_containment"]
            result = validate_phase1_runtime_session_trace_spine_record(record)

            self.assertEqual(spine["session_scope"], "same_session_sandbox_record_only")
            self.assertEqual(spine["trace_spine_authority"], "record_only_trace_index")
            self.assertEqual(tick_trace["tick_trace_authority"], "record_only_ordered_trace")
            self.assertEqual(expected_actual["trace_authority"], "record_only_consistency_summary")
            self.assertTrue(containment["record_only_trace_spine"])
            self.assertTrue(result["trace_spine_record_only"])

    def test_no_live_runtime_state_action_memory_predictor_production_or_claim_is_created(self):
        for record in self.records:
            spine = record["session_trace_spine"]
            tick_trace = record["runtime_tick_trace"]
            expected_actual = record["expected_actual_evaluator_trace"]
            containment = record["session_containment"]
            audit = record["boundary_audit"]
            result = validate_phase1_runtime_session_trace_spine_record(record)

            self.assertFalse(spine["live_runtime_session_started"])
            self.assertFalse(spine["persistent_state_store_created"])
            self.assertFalse(tick_trace["live_runtime_ticks_created"])
            self.assertFalse(expected_actual["runtime_evaluator_created"])
            self.assertFalse(containment["selected_action_created_in_this_package"])
            self.assertFalse(containment["long_term_memory_write_created_in_this_package"])
            self.assertFalse(containment["memory_admission_created_in_this_package"])
            self.assertFalse(containment["predictor_read_enabled_in_this_package"])
            self.assertFalse(containment["production_behavior_created_in_this_package"])
            self.assertFalse(containment["proof_of_learning_claim"])
            self.assertFalse(audit["consciousness_claim"])
            self.assertTrue(result["live_runtime_blocked"])
            self.assertTrue(result["persistent_state_store_blocked"])
            self.assertTrue(result["action_creation_blocked"])
            self.assertTrue(result["memory_write_blocked"])
            self.assertTrue(result["predictor_use_blocked"])
            self.assertTrue(result["production_behavior_blocked"])
            self.assertTrue(result["proof_claim_blocked"])
            self.assertTrue(result["consciousness_claim_blocked"])

    def test_bad_source_blocks_builder(self):
        bad_source = copy.deepcopy(self.sources[0])
        bad_source["closure_criteria_audit"]["phase0_minimal_loop_complete"] = False
        bad_source["closure_criteria_audit"]["criteria_met_count"] = 12

        with self.assertRaises(ValueError):
            build_phase1_runtime_session_trace_spine_record(bad_source)

    def test_bad_source_summary_blocks_validator(self):
        bad = copy.deepcopy(self.reach)
        bad["source_phase0_closure_audit"]["source_validated"] = False

        result = validate_phase1_runtime_session_trace_spine_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_source_validated_not_expected", result["error_codes"])

    def test_broken_spine_fields_block(self):
        cases = (
            ("session_trace_spine_created", False),
            ("session_scope", "runtime"),
            ("tick_count", 7),
            ("tick_index_start", 1),
            ("ordered_tick_ids", []),
            ("expected_actual_trace_created", False),
            ("live_runtime_session_started", True),
            ("persistent_state_store_created", True),
        )
        for field, value in cases:
            bad = copy.deepcopy(self.probe)
            bad["session_trace_spine"][field] = value

            result = validate_phase1_runtime_session_trace_spine_record(bad)

            self.assertFalse(result["valid"])

    def test_broken_tick_fields_block(self):
        cases = (
            ("tick_index", 99),
            ("tick_scope", "runtime"),
            ("source_record_id", ""),
            ("trace_linked", False),
            ("expected_outcome", ""),
            ("actual_outcome", ""),
            ("evaluator_result", ""),
            ("created_live_runtime_tick", True),
            ("created_runtime_behavior", True),
        )
        for field, value in cases:
            bad = copy.deepcopy(self.wait)
            bad["runtime_tick_trace"]["ordered_ticks"][2][field] = value

            result = validate_phase1_runtime_session_trace_spine_record(bad)

            self.assertFalse(result["valid"])

    def test_expected_actual_and_evaluator_runtime_flags_block(self):
        cases = (
            ("expected_actual_trace_created", False),
            ("evaluator_trace_created", False),
            ("expected_actual_pair_count", 7),
            ("runtime_evaluator_created", True),
            ("prediction_error_runtime_created", True),
            ("learning_claim_created", True),
            ("production_readiness_claim_created", True),
        )
        for field, value in cases:
            bad = copy.deepcopy(self.reach)
            bad["expected_actual_evaluator_trace"][field] = value

            result = validate_phase1_runtime_session_trace_spine_record(bad)

            self.assertFalse(result["valid"])

    def test_containment_audit_and_blocked_flags_block(self):
        cases = (
            (("session_containment", "same_session_only"), False, "trace_spine_record_only"),
            (("session_containment", "live_runtime_session_started_in_this_package"), True, "live_runtime_blocked"),
            (("session_containment", "persistent_state_store_created_in_this_package"), True, "persistent_state_store_blocked"),
            (("session_containment", "selected_action_created_in_this_package"), True, "action_creation_blocked"),
            (("session_containment", "long_term_memory_write_created_in_this_package"), True, "memory_write_blocked"),
            (("session_containment", "predictor_read_enabled_in_this_package"), True, "predictor_use_blocked"),
            (("session_containment", "production_behavior_created_in_this_package"), True, "production_behavior_blocked"),
            (("session_containment", "proof_of_learning_claim"), True, "proof_claim_blocked"),
            (("boundary_audit", "next_layer_precreated"), True, "boundary_audit_passed"),
            (("blocked_flags", "memory_write"), True, "memory_write_blocked"),
            (("blocked_flags", "predictor_read_enabled"), True, "predictor_use_blocked"),
            (("blocked_flags", "proof_of_learning_claim"), True, "proof_claim_blocked"),
            (("blocked_flags", "consciousness_claim"), True, "consciousness_claim_blocked"),
        )
        for path, value, result_field in cases:
            bad = copy.deepcopy(self.wait)
            target = bad
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value

            result = validate_phase1_runtime_session_trace_spine_record(bad)

            self.assertFalse(result["valid"])
            self.assertFalse(result[result_field])

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(summary["runtime_session_trace_spine_result_count"], 79)
        self.assertEqual(summary["valid_runtime_session_trace_spine_count"], 3)
        self.assertEqual(summary["invalid_runtime_session_trace_spine_count"], 76)
        self.assertEqual(summary["session_trace_spine_created_count"], 3)
        self.assertEqual(summary["runtime_tick_sequence_created_count"], 3)
        self.assertEqual(summary["trace_spine_record_only_count"], 3)
        self.assertEqual(summary["expected_actual_evaluator_trace_created_count"], 3)
        self.assertEqual(summary["all_ticks_linked_count"], 3)
        self.assertEqual(summary["all_ticks_have_state_snapshot_count"], 3)
        self.assertEqual(summary["reach_session_spine_count"], 1)
        self.assertEqual(summary["wait_session_spine_count"], 1)
        self.assertEqual(summary["probe_session_spine_count"], 1)
        self.assertEqual(summary["live_runtime_blocked_count"], 3)
        self.assertEqual(summary["persistent_state_store_blocked_count"], 3)
        self.assertEqual(summary["action_creation_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_use_blocked_count"], 3)
        self.assertEqual(summary["production_behavior_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)
        self.assertEqual(summary["consciousness_claim_blocked_count"], 3)
        self.assertEqual(summary["boundary_audit_passed_count"], 3)

    def test_cli_command(self):
        result = run_command("run-phase1-runtime-session-trace-spine-minimal-check")

        self.assertEqual(result["command"], "run-phase1-runtime-session-trace-spine-minimal-check")
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
