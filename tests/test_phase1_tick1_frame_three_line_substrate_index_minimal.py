import copy
import unittest

from ashl_core.phase1_session_frame_runtime_tick_handoff_minimal import (
    run_phase1_session_frame_runtime_tick_handoff_minimal_check,
)
from ashl_core.phase1_tick1_frame_three_line_substrate_index_minimal import (
    BOUNDARY_INDEX_AFTER,
    BOUNDARY_INDEX_BEFORE,
    EXPECTED_LINE_COUNT,
    build_phase1_tick1_frame_three_line_substrate_index_record,
    run_phase1_tick1_frame_three_line_substrate_index_minimal_check,
    validate_phase1_tick1_frame_three_line_substrate_index_record,
)
from ashl_core.teaching_cli import run_command


class Phase1Tick1FrameThreeLineSubstrateIndexMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = run_phase1_session_frame_runtime_tick_handoff_minimal_check()["valid_records"]
        cls.result = run_phase1_tick1_frame_three_line_substrate_index_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.reach = cls.records[0]
        cls.wait = cls.records[1]
        cls.probe = cls.records[2]

    def test_valid_tick1_three_line_indexes_are_created(self):
        for record in self.records:
            result = validate_phase1_tick1_frame_three_line_substrate_index_record(record)

            self.assertTrue(result["valid"], result["error_codes"])
            self.assertEqual(record["record_type"], "phase1_tick1_frame_three_line_substrate_index_minimal")
            self.assertEqual(record["boundary_index_before"], BOUNDARY_INDEX_BEFORE)
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)
            self.assertTrue(record["tick1_frame_reference"]["tick1_frame_reference_created"])
            self.assertTrue(record["thought_line_index"]["thought_line_index_created"])
            self.assertTrue(record["action_line_index"]["action_line_index_created"])
            self.assertTrue(record["memory_line_index"]["memory_line_index_created"])
            self.assertTrue(record["cross_line_continuity_index"]["tick1_frame_indexed"])

    def test_b181_tick1_frame_is_the_source(self):
        record = build_phase1_tick1_frame_three_line_substrate_index_record(self.sources[0])
        source = record["source_runtime_tick_handoff"]
        frame = record["tick1_frame_reference"]
        result = validate_phase1_tick1_frame_three_line_substrate_index_record(record)

        self.assertTrue(result["valid"], result["error_codes"])
        self.assertTrue(source["source_validated"])
        self.assertEqual(source["source_boundary_index"], "2026-06-09-b181")
        self.assertTrue(source["source_tick1_context_created"])
        self.assertTrue(source["source_appended_frame_created"])
        self.assertTrue(source["source_continuity_passed"])
        self.assertEqual(frame["tick1_context_id"], source["source_tick1_context_id"])
        self.assertEqual(frame["appended_frame_id"], source["source_appended_session_frame_id"])
        self.assertTrue(frame["record_reference_only"])

    def test_thought_line_indexes_context_without_runtime_thought(self):
        thought = self.reach["thought_line_index"]
        source = self.reach["source_runtime_tick_handoff"]
        result = validate_phase1_tick1_frame_three_line_substrate_index_record(self.reach)

        self.assertEqual(thought["line_name"], "thought")
        self.assertEqual(thought["approved_purpose_context"], source["approved_purpose"])
        self.assertEqual(thought["handoff_reason_context"], source["source_handoff_reason"])
        self.assertEqual(thought["observed_outcome_context"], source["observed_outcome_context"])
        self.assertFalse(thought["candidate_input_created"])
        self.assertFalse(thought["thought_runtime_started"])
        self.assertFalse(thought["llm_runtime_used"])
        self.assertTrue(result["candidate_input_blocked"])
        self.assertTrue(result["llm_runtime_blocked"])

    def test_action_line_indexes_history_without_selection_or_execution(self):
        for record in self.records:
            action = record["action_line_index"]
            source = record["source_runtime_tick_handoff"]
            result = validate_phase1_tick1_frame_three_line_substrate_index_record(record)

            self.assertEqual(action["line_name"], "action")
            self.assertEqual(action["selected_action_context"], source["selected_action_context"])
            self.assertTrue(action["selected_action_context_only"])
            self.assertFalse(action["selected_action_created"])
            self.assertFalse(action["final_action_created"])
            self.assertFalse(action["direct_command_created"])
            self.assertFalse(action["execution_created"])
            self.assertFalse(action["outcome_observation_created"])
            self.assertTrue(result["action_creation_blocked"])

    def test_memory_line_indexes_references_without_memory_write(self):
        for record in self.records:
            memory = record["memory_line_index"]
            source = record["source_runtime_tick_handoff"]
            result = validate_phase1_tick1_frame_three_line_substrate_index_record(record)

            self.assertEqual(memory["line_name"], "memory")
            self.assertEqual(memory["working_memory_slot_set_id"], source["source_working_memory_slot_set_id"])
            self.assertEqual(memory["evidence_source_set_id"], source["source_evidence_source_set_id"])
            self.assertTrue(memory["working_memory_reference_only"])
            self.assertTrue(memory["evidence_reference_only"])
            self.assertFalse(memory["working_memory_update_created"])
            self.assertFalse(memory["persistent_memory_write"])
            self.assertFalse(memory["retention_write"])
            self.assertTrue(result["memory_write_blocked"])

    def test_cross_line_index_preserves_three_record_only_lanes(self):
        cross = self.wait["cross_line_continuity_index"]
        result = validate_phase1_tick1_frame_three_line_substrate_index_record(self.wait)

        self.assertEqual(cross["lane_count"], EXPECTED_LINE_COUNT)
        self.assertTrue(cross["thought_line_record_only"])
        self.assertTrue(cross["action_line_record_only"])
        self.assertTrue(cross["memory_line_record_only"])
        self.assertTrue(cross["all_lanes_record_only"])
        self.assertTrue(cross["continuity_passed"])
        self.assertTrue(cross["session_id_preserved"])
        self.assertTrue(cross["approved_purpose_preserved"])
        self.assertFalse(cross["candidate_input_created"])
        self.assertFalse(cross["action_authority_created"])
        self.assertFalse(cross["memory_authority_created"])
        self.assertTrue(result["three_line_index_record_only"])

    def test_bad_source_blocks_builder(self):
        bad_source = copy.deepcopy(self.sources[0])
        bad_source["tick1_context"]["next_tick_context_created"] = False

        with self.assertRaises(ValueError):
            build_phase1_tick1_frame_three_line_substrate_index_record(bad_source)

    def test_bad_source_summary_blocks_validator(self):
        cases = (
            (("source_runtime_tick_handoff", "source_validated"), False),
            (("source_runtime_tick_handoff", "source_boundary_index"), "2026-06-09-b180"),
            (("source_runtime_tick_handoff", "source_tick1_context_created"), False),
            (("source_runtime_tick_handoff", "source_appended_frame_created"), False),
            (("source_runtime_tick_handoff", "source_continuity_passed"), False),
        )
        for path, value in cases:
            bad = copy.deepcopy(self.reach)
            self._set_path(bad, path, value)

            result = validate_phase1_tick1_frame_three_line_substrate_index_record(bad)

            self.assertFalse(result["valid"])

    def test_candidate_input_or_line_count_pollution_blocks(self):
        cases = (
            (("thought_line_index", "candidate_input_created"), True),
            (("cross_line_continuity_index", "candidate_input_created"), True),
            (("cross_line_continuity_index", "lane_count"), 2),
            (("cross_line_continuity_index", "all_lanes_record_only"), False),
            (("authority_containment", "candidate_input_created_in_this_package"), True),
        )
        for path, value in cases:
            bad = copy.deepcopy(self.wait)
            self._set_path(bad, path, value)

            result = validate_phase1_tick1_frame_three_line_substrate_index_record(bad)

            self.assertFalse(result["valid"])
            self.assertFalse(result["candidate_input_blocked"] if "candidate_input" in path else result["valid"])

    def test_action_creation_pollution_blocks(self):
        cases = (
            (("action_line_index", "selected_action_created"), True),
            (("action_line_index", "final_action_created"), True),
            (("action_line_index", "direct_command_created"), True),
            (("action_line_index", "execution_created"), True),
            (("action_line_index", "outcome_observation_created"), True),
            (("authority_containment", "selected_action_created_in_this_package"), True),
        )
        for path, value in cases:
            bad = copy.deepcopy(self.probe)
            self._set_path(bad, path, value)

            result = validate_phase1_tick1_frame_three_line_substrate_index_record(bad)

            self.assertFalse(result["valid"])
            self.assertFalse(result["action_creation_blocked"])

    def test_memory_external_predictor_feed_and_claim_pollution_blocks(self):
        cases = (
            (("memory_line_index", "working_memory_update_created"), True, "memory_write_blocked"),
            (("memory_line_index", "persistent_memory_write"), True, "memory_write_blocked"),
            (("memory_line_index", "retention_write"), True, "memory_write_blocked"),
            (("tick1_frame_reference", "external_tool_called"), True, "external_tools_blocked"),
            (("authority_containment", "predictor_read_enabled_in_this_package"), True, "predictor_use_blocked"),
            (("authority_containment", "direct_tendency_feed_in_this_package"), True, "direct_feed_blocked"),
            (("boundary_audit", "production_behavior_created"), True, "production_behavior_blocked"),
            (("thought_line_index", "proof_of_learning_claim"), True, "proof_claim_blocked"),
            (("thought_line_index", "consciousness_claim"), True, "consciousness_claim_blocked"),
            (("thought_line_index", "llm_runtime_used"), True, "llm_runtime_blocked"),
        )
        for path, value, result_field in cases:
            bad = copy.deepcopy(self.reach)
            self._set_path(bad, path, value)

            result = validate_phase1_tick1_frame_three_line_substrate_index_record(bad)

            self.assertFalse(result["valid"])
            self.assertFalse(result[result_field])

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(summary["tick1_three_line_substrate_index_result_count"], 39)
        self.assertEqual(summary["valid_tick1_three_line_substrate_index_count"], 3)
        self.assertEqual(summary["invalid_tick1_three_line_substrate_index_count"], 36)
        self.assertEqual(summary["tick1_frame_reference_created_count"], 3)
        self.assertEqual(summary["thought_line_index_created_count"], 3)
        self.assertEqual(summary["action_line_index_created_count"], 3)
        self.assertEqual(summary["memory_line_index_created_count"], 3)
        self.assertEqual(summary["cross_line_continuity_index_created_count"], 3)
        self.assertEqual(summary["lane_count_valid_count"], 3)
        self.assertEqual(summary["all_lanes_record_only_count"], 3)
        self.assertEqual(summary["three_line_index_record_only_count"], 3)
        self.assertEqual(summary["reach_three_line_index_count"], 1)
        self.assertEqual(summary["wait_three_line_index_count"], 1)
        self.assertEqual(summary["probe_three_line_index_count"], 1)
        self.assertEqual(summary["live_runtime_blocked_count"], 3)
        self.assertEqual(summary["candidate_input_blocked_count"], 3)
        self.assertEqual(summary["action_creation_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["external_tools_blocked_count"], 3)
        self.assertEqual(summary["predictor_use_blocked_count"], 3)
        self.assertEqual(summary["direct_feed_blocked_count"], 3)
        self.assertEqual(summary["production_behavior_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)
        self.assertEqual(summary["consciousness_claim_blocked_count"], 3)
        self.assertEqual(summary["llm_runtime_blocked_count"], 3)
        self.assertEqual(summary["boundary_audit_passed_count"], 3)

    def test_cli_command(self):
        result = run_command("run-phase1-tick1-frame-three-line-substrate-index-minimal-check")

        self.assertEqual(result["command"], "run-phase1-tick1-frame-three-line-substrate-index-minimal-check")
        self.assertEqual(result["status"], "ok")

    @staticmethod
    def _set_path(record, path, value):
        target = record
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value


if __name__ == "__main__":
    unittest.main()
