import copy
import unittest

from ashl_core.phase1_session_frame_materialization_minimal import (
    run_phase1_session_frame_materialization_minimal_check,
)
from ashl_core.phase1_session_frame_runtime_tick_handoff_minimal import (
    BOUNDARY_INDEX_AFTER,
    BOUNDARY_INDEX_BEFORE,
    EXPECTED_APPENDED_TICK_COUNT,
    EXPECTED_SOURCE_TICK_COUNT,
    build_phase1_session_frame_runtime_tick_handoff_record,
    run_phase1_session_frame_runtime_tick_handoff_minimal_check,
    validate_phase1_session_frame_runtime_tick_handoff_record,
)
from ashl_core.teaching_cli import run_command


class Phase1SessionFrameRuntimeTickHandoffMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_phase1_session_frame_materialization_minimal_check()["valid_records"]
        cls.result = run_phase1_session_frame_runtime_tick_handoff_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.reach = cls.records[0]
        cls.wait = cls.records[1]
        cls.probe = cls.records[2]

    def test_valid_runtime_tick_handoffs_are_created(self):
        for record in self.records:
            result = validate_phase1_session_frame_runtime_tick_handoff_record(record)

            self.assertTrue(result["valid"], result["error_codes"])
            self.assertEqual(record["record_type"], "phase1_session_frame_runtime_tick_handoff_minimal")
            self.assertEqual(record["boundary_index_before"], BOUNDARY_INDEX_BEFORE)
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)
            self.assertTrue(record["tick1_context"]["next_tick_context_created"])
            self.assertTrue(record["appended_session_frame"]["frame_appended"])
            self.assertTrue(record["continuity_comparison"]["continuity_passed"])

    def test_b180_frame_is_read_as_tick0_input(self):
        record = build_phase1_session_frame_runtime_tick_handoff_record(self.sources[0])
        source = record["source_session_frame"]
        tick0 = record["tick0_context"]
        result = validate_phase1_session_frame_runtime_tick_handoff_record(record)

        self.assertTrue(result["valid"], result["error_codes"])
        self.assertTrue(source["source_validated"])
        self.assertEqual(source["source_boundary_index"], "2026-06-09-b180")
        self.assertEqual(source["source_frame_tick_count"], EXPECTED_SOURCE_TICK_COUNT)
        self.assertEqual(tick0["source_frame_id"], source["source_session_frame_id"])
        self.assertEqual(tick0["source_tick_index"], source["source_current_tick_index"])
        self.assertTrue(tick0["read_b180_frame_as_next_tick_input"])
        self.assertFalse(tick0["mutates_source_frame"])

    def test_tick1_context_advances_one_same_session_tick(self):
        source = self.reach["source_session_frame"]
        tick0 = self.reach["tick0_context"]
        tick1 = self.reach["tick1_context"]

        self.assertEqual(tick1["session_id"], tick0["session_id"])
        self.assertEqual(tick1["scenario_id"], tick0["scenario_id"])
        self.assertEqual(tick1["previous_tick_index"], source["source_current_tick_index"])
        self.assertEqual(tick1["next_tick_index"], source["source_current_tick_index"] + 1)
        self.assertEqual(tick1["source_tick0_context_id"], tick0["tick0_context_id"])
        self.assertEqual(tick1["input_frame_id"], source["source_session_frame_id"])
        self.assertTrue(tick1["same_session_sandbox_only"])

    def test_appended_frame_preserves_existing_references(self):
        source = self.reach["source_session_frame"]
        tick1 = self.reach["tick1_context"]
        frame = self.reach["appended_session_frame"]

        self.assertEqual(frame["previous_frame_id"], source["source_session_frame_id"])
        self.assertEqual(frame["source_tick1_context_id"], tick1["tick1_context_id"])
        self.assertEqual(frame["previous_frame_tick_count"], EXPECTED_SOURCE_TICK_COUNT)
        self.assertEqual(frame["frame_tick_count"], EXPECTED_APPENDED_TICK_COUNT)
        self.assertEqual(frame["inherits_trace_snapshot_id"], source["source_trace_snapshot_id"])
        self.assertEqual(frame["inherits_working_memory_slot_set_id"], source["source_working_memory_slot_set_id"])
        self.assertEqual(frame["inherits_evidence_source_set_id"], source["source_evidence_source_set_id"])
        self.assertTrue(frame["working_memory_reference_only"])
        self.assertTrue(frame["evidence_reference_only"])

    def test_continuity_comparison_checks_tick0_to_tick1(self):
        continuity = self.reach["continuity_comparison"]
        result = validate_phase1_session_frame_runtime_tick_handoff_record(self.reach)

        self.assertTrue(continuity["continuity_compared"])
        self.assertTrue(continuity["session_id_preserved"])
        self.assertTrue(continuity["scenario_id_preserved"])
        self.assertTrue(continuity["approved_purpose_preserved"])
        self.assertTrue(continuity["tick_index_advances_by_one"])
        self.assertTrue(continuity["frame_count_advances_by_one"])
        self.assertTrue(continuity["working_memory_refs_preserved"])
        self.assertTrue(continuity["evidence_refs_preserved"])
        self.assertTrue(result["continuity_passed"])
        self.assertTrue(result["tick_index_advanced"])
        self.assertTrue(result["frame_count_advanced"])

    def test_handoff_does_not_create_action_execution_or_observation(self):
        for record in self.records:
            tick1 = record["tick1_context"]
            containment = record["authority_containment"]
            result = validate_phase1_session_frame_runtime_tick_handoff_record(record)

            self.assertFalse(tick1["selected_action_created"])
            self.assertFalse(tick1["final_action_created"])
            self.assertFalse(tick1["direct_command_created"])
            self.assertFalse(tick1["execution_created"])
            self.assertFalse(tick1["outcome_observation_created"])
            self.assertFalse(containment["selected_action_created_in_this_package"])
            self.assertTrue(result["action_creation_blocked"])

    def test_handoff_does_not_write_memory_or_call_external_tools(self):
        for record in self.records:
            tick0 = record["tick0_context"]
            tick1 = record["tick1_context"]
            frame = record["appended_session_frame"]
            result = validate_phase1_session_frame_runtime_tick_handoff_record(record)

            self.assertFalse(tick0["external_tool_called"])
            self.assertFalse(tick1["external_tool_called"])
            self.assertFalse(tick1["working_memory_update_created"])
            self.assertFalse(tick1["persistent_memory_write"])
            self.assertFalse(frame["persistent_memory_write"])
            self.assertTrue(result["memory_write_blocked"])
            self.assertTrue(result["external_tools_blocked"])

    def test_handoff_blocks_predictor_production_proof_and_consciousness_claims(self):
        for record in self.records:
            result = validate_phase1_session_frame_runtime_tick_handoff_record(record)

            self.assertTrue(result["predictor_use_blocked"])
            self.assertTrue(result["production_behavior_blocked"])
            self.assertTrue(result["proof_claim_blocked"])
            self.assertTrue(result["consciousness_claim_blocked"])

    def test_bad_source_blocks_builder(self):
        bad_source = copy.deepcopy(self.sources[0])
        bad_source["session_frame"]["session_frame_materialized"] = False

        with self.assertRaises(ValueError):
            build_phase1_session_frame_runtime_tick_handoff_record(bad_source)

    def test_bad_handoff_parts_block_validator(self):
        cases = (
            (("source_session_frame", "source_validated"), False),
            (("tick0_context", "read_b180_frame_as_next_tick_input"), False),
            (("tick1_context", "next_tick_context_created"), False),
            (("tick1_context", "next_tick_index"), 12),
            (("appended_session_frame", "frame_appended"), False),
            (("appended_session_frame", "frame_tick_count"), 12),
            (("continuity_comparison", "continuity_passed"), False),
            (("continuity_comparison", "tick_index_advances_by_one"), False),
        )
        for path, value in cases:
            bad = copy.deepcopy(self.wait)
            target = bad
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value

            result = validate_phase1_session_frame_runtime_tick_handoff_record(bad)

            self.assertFalse(result["valid"])

    def test_authority_and_blocked_flags_block_forbidden_authority(self):
        cases = (
            (("authority_containment", "runtime_tick_scheduler_created_in_this_package"), True, "live_runtime_blocked"),
            (("authority_containment", "external_tool_called_in_this_package"), True, "external_tools_blocked"),
            (("authority_containment", "persistent_memory_write_created_in_this_package"), True, "memory_write_blocked"),
            (("authority_containment", "predictor_modified_in_this_package"), True, "predictor_use_blocked"),
            (("authority_containment", "production_behavior_created_in_this_package"), True, "production_behavior_blocked"),
            (("authority_containment", "consciousness_claim"), True, "consciousness_claim_blocked"),
            (("blocked_flags", "external_tool_called"), True, "external_tools_blocked"),
            (("blocked_flags", "persistent_memory_write"), True, "memory_write_blocked"),
            (("blocked_flags", "predictor_modified"), True, "predictor_use_blocked"),
            (("blocked_flags", "proof_of_learning_claim"), True, "proof_claim_blocked"),
        )
        for path, value, result_field in cases:
            bad = copy.deepcopy(self.probe)
            target = bad
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value

            result = validate_phase1_session_frame_runtime_tick_handoff_record(bad)

            self.assertFalse(result["valid"])
            self.assertFalse(result[result_field])

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(summary["runtime_tick_handoff_result_count"], 36)
        self.assertEqual(summary["valid_runtime_tick_handoff_count"], 3)
        self.assertEqual(summary["invalid_runtime_tick_handoff_count"], 33)
        self.assertEqual(summary["tick0_context_created_count"], 3)
        self.assertEqual(summary["tick1_context_created_count"], 3)
        self.assertEqual(summary["appended_frame_created_count"], 3)
        self.assertEqual(summary["continuity_compared_count"], 3)
        self.assertEqual(summary["continuity_passed_count"], 3)
        self.assertEqual(summary["tick_index_advanced_count"], 3)
        self.assertEqual(summary["frame_count_advanced_count"], 3)
        self.assertEqual(summary["runtime_handoff_record_only_count"], 3)
        self.assertEqual(summary["reach_tick_handoff_count"], 1)
        self.assertEqual(summary["wait_tick_handoff_count"], 1)
        self.assertEqual(summary["probe_tick_handoff_count"], 1)
        self.assertEqual(summary["live_runtime_blocked_count"], 3)
        self.assertEqual(summary["action_creation_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["external_tools_blocked_count"], 3)
        self.assertEqual(summary["predictor_use_blocked_count"], 3)
        self.assertEqual(summary["production_behavior_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)
        self.assertEqual(summary["consciousness_claim_blocked_count"], 3)
        self.assertEqual(summary["boundary_audit_passed_count"], 3)

    def test_cli_command(self):
        result = run_command("run-phase1-session-frame-runtime-tick-handoff-minimal-check")

        self.assertEqual(result["command"], "run-phase1-session-frame-runtime-tick-handoff-minimal-check")
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
