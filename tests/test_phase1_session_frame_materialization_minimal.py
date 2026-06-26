import copy
import unittest

from ashl_core.phase1_runtime_session_trace_spine_minimal import (
    run_phase1_runtime_session_trace_spine_minimal_check,
)
from ashl_core.phase1_session_frame_materialization_minimal import (
    B0_10_COUNTER,
    BOUNDARY_INDEX_AFTER,
    BOUNDARY_INDEX_BEFORE,
    EXPECTED_EVIDENCE_SOURCE_COUNT,
    EXPECTED_WORKING_MEMORY_SLOT_COUNT,
    build_phase1_session_frame_materialization_record,
    run_phase1_session_frame_materialization_minimal_check,
    validate_phase1_session_frame_materialization_record,
)
from ashl_core.teaching_cli import run_command


class Phase1SessionFrameMaterializationMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_phase1_runtime_session_trace_spine_minimal_check()["valid_records"]
        cls.result = run_phase1_session_frame_materialization_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.reach = cls.records[0]
        cls.wait = cls.records[1]
        cls.probe = cls.records[2]

    def test_valid_session_frames_are_created(self):
        for record in self.records:
            result = validate_phase1_session_frame_materialization_record(record)

            self.assertTrue(result["valid"], result["error_codes"])
            self.assertEqual(record["record_type"], "phase1_session_frame_materialization_minimal")
            self.assertEqual(record["boundary_index_before"], BOUNDARY_INDEX_BEFORE)
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)
            self.assertTrue(record["session_frame"]["session_frame_materialized"])
            self.assertEqual(record["session_frame"]["b0_10_counter"], B0_10_COUNTER)

    def test_b179_trace_spine_source_enters_frame(self):
        record = build_phase1_session_frame_materialization_record(self.sources[0])
        source = record["source_runtime_session_trace_spine"]
        frame = record["session_frame"]
        result = validate_phase1_session_frame_materialization_record(record)

        self.assertTrue(result["valid"], result["error_codes"])
        self.assertTrue(source["source_validated"])
        self.assertEqual(source["source_boundary_index"], "2026-06-09-b179")
        self.assertTrue(source["source_trace_spine_record_only"])
        self.assertEqual(source["source_tick_count"], 8)
        self.assertEqual(frame["session_id"], source["session_id"])
        self.assertEqual(frame["source_session_trace_spine_id"], source["source_session_trace_spine_id"])

    def test_current_tick_is_last_existing_tick(self):
        source = self.reach["source_runtime_session_trace_spine"]
        frame = self.reach["session_frame"]
        snapshot = self.reach["trace_snapshot"]

        self.assertEqual(frame["current_tick_index"], 7)
        self.assertEqual(frame["current_tick_id"], source["source_ordered_tick_ids"][-1])
        self.assertEqual(frame["current_tick_label"], "two_cycle_influence_and_closure")
        self.assertEqual(snapshot["current_tick_id"], frame["current_tick_id"])
        self.assertEqual(snapshot["current_state_snapshot"]["state_snapshot_kind"], "trace_state_summary")
        self.assertEqual(snapshot["current_state_snapshot"]["selected_action"], "reach_front_item")

    def test_working_memory_slots_reference_existing_same_session_memory(self):
        source = self.reach["source_runtime_session_trace_spine"]
        slots = self.reach["working_memory_slots"]
        slot_by_role = {slot["slot_role"]: slot for slot in slots["slots"]}

        self.assertTrue(slots["slots_materialized"])
        self.assertEqual(slots["slot_count"], EXPECTED_WORKING_MEMORY_SLOT_COUNT)
        self.assertEqual(
            slot_by_role["first_cycle_context"]["source_working_memory_update_id"],
            source["first_cycle_working_memory_update_id"],
        )
        self.assertEqual(
            slot_by_role["second_cycle_outcome_context"]["source_working_memory_update_id"],
            source["second_cycle_working_memory_update_id"],
        )
        for slot in slots["slots"]:
            self.assertTrue(slot["reference_only"])
            self.assertFalse(slot["new_working_memory_update_created"])
            self.assertFalse(slot["persistent_working_memory_written"])
            self.assertFalse(slot["memory_write_created"])

    def test_evidence_sources_are_existing_record_references(self):
        evidence = self.reach["evidence_sources"]
        kinds = {source["source_kind"] for source in evidence["sources"]}

        self.assertTrue(evidence["evidence_sources_materialized"])
        self.assertEqual(evidence["evidence_source_count"], EXPECTED_EVIDENCE_SOURCE_COUNT)
        self.assertEqual(
            kinds,
            {
                "runtime_session_trace_spine",
                "runtime_tick_trace",
                "expected_actual_evaluator_trace",
                "phase0_closure_audit",
                "first_cycle_working_memory_update",
                "candidate_hint",
                "advisory_ordering",
                "sandbox_action_path",
                "second_cycle_working_memory_update",
            },
        )
        for source in evidence["sources"]:
            self.assertTrue(source["record_reference_only"])
            self.assertFalse(source["creates_new_source_record"])

    def test_frame_does_not_create_runtime_action_memory_predictor_or_production(self):
        for record in self.records:
            frame = record["session_frame"]
            snapshot = record["trace_snapshot"]
            slots = record["working_memory_slots"]
            containment = record["authority_containment"]
            result = validate_phase1_session_frame_materialization_record(record)

            self.assertFalse(frame["live_runtime_session_started"])
            self.assertFalse(frame["new_runtime_tick_created"])
            self.assertFalse(snapshot["runtime_evaluator_created"])
            self.assertFalse(slots["memory_write_created"])
            self.assertFalse(containment["selected_action_created_in_this_package"])
            self.assertFalse(containment["predictor_read_enabled_in_this_package"])
            self.assertFalse(containment["production_behavior_created_in_this_package"])
            self.assertTrue(result["live_runtime_blocked"])
            self.assertTrue(result["action_creation_blocked"])
            self.assertTrue(result["memory_write_blocked"])
            self.assertTrue(result["predictor_use_blocked"])
            self.assertTrue(result["production_behavior_blocked"])

    def test_b0_10_hallucination_self_check_is_present(self):
        check = self.reach["hallucination_self_check"]
        result = validate_phase1_session_frame_materialization_record(self.reach)

        self.assertTrue(check["triggered"])
        self.assertEqual(check["boundary_number"], 180)
        self.assertEqual(check["b0_10_counter"], B0_10_COUNTER)
        self.assertTrue(check["docs_claims_backed_by_code"])
        self.assertTrue(check["status_docs_consistent"])
        self.assertTrue(check["cli_expected_for_package"])
        self.assertTrue(check["smoke_expected_for_package"])
        self.assertFalse(check["sandbox_claimed_as_production"])
        self.assertFalse(check["evaluation_claimed_as_learning_proof"])
        self.assertTrue(result["b0_10_self_check_passed"])

    def test_boundary_audit_blocks_next_layer_and_authority_leaks(self):
        audit = self.reach["boundary_audit"]
        result = validate_phase1_session_frame_materialization_record(self.reach)

        self.assertTrue(audit["triggered"])
        self.assertEqual(audit["boundary_number"], 180)
        self.assertFalse(audit["production_behavior_created"])
        self.assertFalse(audit["runtime_behavior_leak"])
        self.assertFalse(audit["memory_write_created"])
        self.assertFalse(audit["predictor_read_enabled"])
        self.assertFalse(audit["direct_endocrine_feed"])
        self.assertFalse(audit["direct_tendency_feed"])
        self.assertFalse(audit["next_layer_precreated"])
        self.assertFalse(audit["proof_of_learning_claim"])
        self.assertTrue(result["boundary_audit_passed"])

    def test_bad_source_blocks_builder(self):
        bad_source = copy.deepcopy(self.sources[0])
        bad_source["session_trace_spine"]["session_trace_spine_created"] = False

        with self.assertRaises(ValueError):
            build_phase1_session_frame_materialization_record(bad_source)

    def test_bad_source_summary_blocks_validator(self):
        bad = copy.deepcopy(self.reach)
        bad["source_runtime_session_trace_spine"]["source_validated"] = False

        result = validate_phase1_session_frame_materialization_record(bad)

        self.assertFalse(result["valid"])

    def test_broken_frame_snapshot_slots_and_evidence_block(self):
        cases = (
            (("session_frame", "session_frame_materialized"), False),
            (("session_frame", "frame_scope"), "runtime"),
            (("trace_snapshot", "trace_snapshot_materialized"), False),
            (("trace_snapshot", "runtime_evaluator_created"), True),
            (("working_memory_slots", "slots_materialized"), False),
            (("working_memory_slots", "slots", 0, "new_working_memory_update_created"), True),
            (("evidence_sources", "evidence_sources_materialized"), False),
            (("evidence_sources", "new_evidence_record_created"), True),
        )
        for path, value in cases:
            bad = copy.deepcopy(self.wait)
            target = bad
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value

            result = validate_phase1_session_frame_materialization_record(bad)

            self.assertFalse(result["valid"])

    def test_containment_self_check_audit_and_blocked_flags_block(self):
        cases = (
            (("authority_containment", "live_runtime_session_started_in_this_package"), True, "live_runtime_blocked"),
            (("authority_containment", "selected_action_created_in_this_package"), True, "action_creation_blocked"),
            (("authority_containment", "memory_write_created_in_this_package"), True, "memory_write_blocked"),
            (("authority_containment", "predictor_read_enabled_in_this_package"), True, "predictor_use_blocked"),
            (("authority_containment", "direct_endocrine_feed_in_this_package"), True, "direct_feed_blocked"),
            (("authority_containment", "production_behavior_created_in_this_package"), True, "production_behavior_blocked"),
            (("hallucination_self_check", "sandbox_claimed_as_production"), True, "b0_10_self_check_passed"),
            (("boundary_audit", "runtime_behavior_leak"), True, "boundary_audit_passed"),
            (("blocked_flags", "memory_write"), True, "memory_write_blocked"),
            (("blocked_flags", "proof_of_learning_claim"), True, "proof_claim_blocked"),
        )
        for path, value, result_field in cases:
            bad = copy.deepcopy(self.probe)
            target = bad
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value

            result = validate_phase1_session_frame_materialization_record(bad)

            self.assertFalse(result["valid"])
            self.assertFalse(result[result_field])

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(summary["session_frame_materialization_result_count"], 49)
        self.assertEqual(summary["valid_session_frame_count"], 3)
        self.assertEqual(summary["invalid_session_frame_count"], 46)
        self.assertEqual(summary["session_frame_materialized_count"], 3)
        self.assertEqual(summary["trace_snapshot_materialized_count"], 3)
        self.assertEqual(summary["working_memory_slots_materialized_count"], 3)
        self.assertEqual(summary["evidence_sources_materialized_count"], 3)
        self.assertEqual(summary["frame_record_only_count"], 3)
        self.assertEqual(summary["b0_10_self_check_passed_count"], 3)
        self.assertEqual(summary["boundary_audit_passed_count"], 3)
        self.assertEqual(summary["reach_session_frame_count"], 1)
        self.assertEqual(summary["wait_session_frame_count"], 1)
        self.assertEqual(summary["probe_session_frame_count"], 1)
        self.assertEqual(summary["live_runtime_blocked_count"], 3)
        self.assertEqual(summary["action_creation_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["predictor_use_blocked_count"], 3)
        self.assertEqual(summary["direct_feed_blocked_count"], 3)
        self.assertEqual(summary["production_behavior_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)
        self.assertEqual(summary["consciousness_claim_blocked_count"], 3)

    def test_cli_command(self):
        result = run_command("run-phase1-session-frame-materialization-minimal-check")

        self.assertEqual(result["command"], "run-phase1-session-frame-materialization-minimal-check")
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()

