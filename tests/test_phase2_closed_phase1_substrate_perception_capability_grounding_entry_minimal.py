import copy
import unittest

from ashl_core.phase1_closure_audit_minimal import run_phase1_closure_audit_minimal_check
from ashl_core.phase1_tick1_frame_three_line_substrate_index_minimal import (
    run_phase1_tick1_frame_three_line_substrate_index_minimal_check,
)
from ashl_core.phase2_closed_phase1_substrate_perception_capability_grounding_entry_minimal import (
    BOUNDARY_INDEX_AFTER,
    BOUNDARY_INDEX_BEFORE,
    PRESERVED_UNKNOWN_FIELDS,
    build_phase2_closed_phase1_substrate_perception_capability_grounding_entry_record,
    run_phase2_closed_phase1_substrate_perception_capability_grounding_entry_minimal_check,
    validate_phase2_closed_phase1_substrate_perception_capability_grounding_entry_record,
)
from ashl_core.teaching_cli import run_command


class Phase2ClosedPhase1SubstratePerceptionCapabilityGroundingEntryMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.closure_records = run_phase1_closure_audit_minimal_check()["valid_records"]
        cls.index_records = run_phase1_tick1_frame_three_line_substrate_index_minimal_check()["valid_records"]
        cls.result = run_phase2_closed_phase1_substrate_perception_capability_grounding_entry_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.by_scenario = {record["source_closed_phase1_substrate"]["scenario_id"]: record for record in cls.records}
        cls.closure_by_scenario = {
            record["source_phase1_substrates"]["scenario_id"]: record for record in cls.closure_records
        }
        cls.index_by_scenario = {
            record["source_runtime_tick_handoff"]["scenario_id"]: record for record in cls.index_records
        }
        cls.reach = cls.by_scenario["item_reachable_feedback_prioritizes_reach"]
        cls.wait = cls.by_scenario["item_not_afforded_blocks_feedback_priority"]
        cls.probe = cls.by_scenario["mismatch_feedback_outranks_retry_tendency"]

    def test_valid_phase2_entry_reports_are_created(self):
        for record in self.records:
            result = validate_phase2_closed_phase1_substrate_perception_capability_grounding_entry_record(record)
            report = record["phase2_entry_report"]

            self.assertTrue(result["valid"], result["error_codes"])
            self.assertEqual(record["record_type"], "phase2_closed_phase1_substrate_perception_capability_grounding_entry_minimal")
            self.assertEqual(record["boundary_index_before"], BOUNDARY_INDEX_BEFORE)
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)
            self.assertTrue(report["phase2_entry_report_created"])
            self.assertEqual(report["phase2_purpose"], "perception_and_capability_grounding")
            self.assertTrue(report["record_only_report"])

    def test_reads_closed_phase1_substrate_as_source(self):
        record = build_phase2_closed_phase1_substrate_perception_capability_grounding_entry_record(
            self.closure_by_scenario["item_reachable_feedback_prioritizes_reach"],
            self.index_by_scenario["item_reachable_feedback_prioritizes_reach"],
        )
        source = record["source_closed_phase1_substrate"]
        result = validate_phase2_closed_phase1_substrate_perception_capability_grounding_entry_record(record)

        self.assertTrue(result["valid"], result["error_codes"])
        self.assertTrue(source["source_phase1_closure_validated"])
        self.assertEqual(source["source_phase1_closure_boundary_index"], "2026-06-09-b183")
        self.assertTrue(source["source_phase1_closure_ready"])
        self.assertTrue(source["source_three_line_index_validated"])
        self.assertEqual(source["source_three_line_index_boundary_index"], "2026-06-09-b182")
        self.assertTrue(source["source_three_line_index_record_only"])
        self.assertTrue(source["all_source_scenarios_match"])

    def test_perception_evidence_candidates_are_identified_without_semantic_vision(self):
        for record in self.records:
            perception = record["perception_grounding_entry"]
            result = validate_phase2_closed_phase1_substrate_perception_capability_grounding_entry_record(record)
            kinds = {item["evidence_kind"] for item in perception["perception_evidence_candidates"]}

            self.assertTrue(result["perception_evidence_candidates_identified"])
            self.assertEqual(kinds, {"observed_outcome_context", "phase1_evidence_source_reference"})
            self.assertFalse(perception["semantic_vision_created"])
            self.assertFalse(perception["object_recognition_created"])
            self.assertFalse(perception["active_focus_created"])
            self.assertFalse(perception["new_visual_record_created"])
            self.assertTrue(result["semantic_vision_blocked"])

    def test_capability_evidence_candidates_are_identified_without_tool_authority(self):
        for record in self.records:
            capability = record["capability_grounding_entry"]
            result = validate_phase2_closed_phase1_substrate_perception_capability_grounding_entry_record(record)
            kinds = {item["evidence_kind"] for item in capability["capability_evidence_candidates"]}

            self.assertTrue(result["capability_evidence_candidates_identified"])
            self.assertEqual(kinds, {"closed_operation_context", "phase1_evidence_source_reference"})
            self.assertFalse(capability["grounded_capability_binding_created"])
            self.assertFalse(capability["capability_map_created"])
            self.assertFalse(capability["raw_tool_access_created"])
            self.assertFalse(capability["external_tool_called"])
            self.assertTrue(result["capability_authority_blocked"])

    def test_unknown_fields_are_preserved_without_invention(self):
        unknown = self.reach["unknown_field_preservation"]
        result = validate_phase2_closed_phase1_substrate_perception_capability_grounding_entry_record(self.reach)

        self.assertTrue(result["unknown_fields_preserved"])
        self.assertEqual(unknown["preserved_unknown_fields"], PRESERVED_UNKNOWN_FIELDS)
        self.assertFalse(unknown["unknown_fields_resolved_in_this_package"])
        self.assertFalse(unknown["unknown_values_invented"])
        self.assertTrue(unknown["requires_future_perception_record"])
        self.assertTrue(unknown["requires_future_capability_map_read"])

    def test_entry_does_not_create_candidate_input_action_execution_or_memory(self):
        for record in self.records:
            report = record["phase2_entry_report"]
            result = validate_phase2_closed_phase1_substrate_perception_capability_grounding_entry_record(record)

            self.assertFalse(report["candidate_input_created"])
            self.assertFalse(report["candidate_ordering_created"])
            self.assertFalse(report["action_preparation_created"])
            self.assertFalse(report["action_selection_created"])
            self.assertFalse(report["direct_command_created"])
            self.assertFalse(report["execution_created"])
            self.assertFalse(report["outcome_observation_created"])
            self.assertFalse(report["memory_write_created"])
            self.assertTrue(result["candidate_input_blocked"])
            self.assertTrue(result["candidate_ordering_blocked"])
            self.assertTrue(result["action_selection_blocked"])
            self.assertTrue(result["execution_blocked"])
            self.assertTrue(result["memory_write_blocked"])

    def test_bad_source_blocks_builder(self):
        bad_closure = copy.deepcopy(self.closure_records[0])
        bad_closure["phase1_closure_audit"]["phase1_closure_ready"] = False

        with self.assertRaises(ValueError):
            build_phase2_closed_phase1_substrate_perception_capability_grounding_entry_record(
                bad_closure,
                self.index_records[0],
            )

    def test_source_pollution_blocks_validator(self):
        cases = (
            ("source_phase1_closure_validated", False),
            ("source_phase1_closure_boundary_index", "2026-06-09-b182"),
            ("source_phase1_closure_ready", False),
            ("source_three_line_index_validated", False),
            ("source_three_line_index_boundary_index", "2026-06-09-b181"),
            ("source_three_line_index_record_only", False),
            ("all_source_scenarios_match", False),
        )
        for field, value in cases:
            bad = copy.deepcopy(self.reach)
            bad["source_closed_phase1_substrate"][field] = value

            result = validate_phase2_closed_phase1_substrate_perception_capability_grounding_entry_record(bad)

            self.assertFalse(result["valid"])

    def test_perception_pollution_blocks(self):
        cases = (
            (("perception_grounding_entry", "perception_evidence_candidates_identified"), False),
            (("perception_grounding_entry", "perception_evidence_candidate_count"), 1),
            (("perception_grounding_entry", "semantic_vision_created"), True),
            (("perception_grounding_entry", "object_recognition_created"), True),
            (("perception_grounding_entry", "active_focus_created"), True),
            (("perception_grounding_entry", "new_visual_record_created"), True),
            (("perception_grounding_entry", "perception_evidence_candidates", 0, "semantic_vision_claimed"), True),
        )
        for path, value in cases:
            bad = copy.deepcopy(self.wait)
            self._set_path(bad, path, value)

            result = validate_phase2_closed_phase1_substrate_perception_capability_grounding_entry_record(bad)

            self.assertFalse(result["valid"])
            if "semantic" in path or "object" in path or "focus" in path or "visual" in path:
                self.assertFalse(result["semantic_vision_blocked"])

    def test_capability_pollution_blocks(self):
        cases = (
            (("capability_grounding_entry", "capability_evidence_candidates_identified"), False),
            (("capability_grounding_entry", "capability_evidence_candidate_count"), 1),
            (("capability_grounding_entry", "grounded_capability_binding_created"), True),
            (("capability_grounding_entry", "capability_map_created"), True),
            (("capability_grounding_entry", "raw_tool_access_created"), True),
            (("capability_grounding_entry", "external_tool_called"), True),
            (("capability_grounding_entry", "capability_evidence_candidates", 0, "capability_authority_created"), True),
        )
        for path, value in cases:
            bad = copy.deepcopy(self.probe)
            self._set_path(bad, path, value)

            result = validate_phase2_closed_phase1_substrate_perception_capability_grounding_entry_record(bad)

            self.assertFalse(result["valid"])
            if "external_tool_called" in path:
                self.assertFalse(result["external_tools_blocked"])
            elif "capability_evidence_candidates_identified" not in path and "capability_evidence_candidate_count" not in path:
                self.assertFalse(result["capability_authority_blocked"])

    def test_unknown_and_report_pollution_blocks(self):
        cases = (
            (("unknown_field_preservation", "unknown_fields_preserved"), False, "unknown_fields_preserved"),
            (("unknown_field_preservation", "unknown_fields_resolved_in_this_package"), True, "unknown_fields_preserved"),
            (("unknown_field_preservation", "unknown_values_invented"), True, "unknown_fields_preserved"),
            (("phase2_entry_report", "phase2_entry_report_created"), False, "phase2_entry_report_created"),
            (("phase2_entry_report", "phase2_purpose"), "candidate_input", "valid"),
        )
        for path, value, field in cases:
            bad = copy.deepcopy(self.reach)
            self._set_path(bad, path, value)

            result = validate_phase2_closed_phase1_substrate_perception_capability_grounding_entry_record(bad)

            self.assertFalse(result["valid"])
            if field != "valid":
                self.assertFalse(result[field])

    def test_candidate_and_action_pollution_blocks(self):
        cases = (
            (("phase2_entry_report", "candidate_input_created"), True, "candidate_input_blocked"),
            (("phase2_entry_report", "candidate_ordering_created"), True, "candidate_ordering_blocked"),
            (("authority_containment", "candidate_reordering_created_in_this_package"), True, "candidate_ordering_blocked"),
            (("authority_containment", "selected_action_created_in_this_package"), True, "action_selection_blocked"),
            (("authority_containment", "final_action_created_in_this_package"), True, "action_selection_blocked"),
            (("phase2_entry_report", "direct_command_created"), True, "direct_command_blocked"),
            (("phase2_entry_report", "execution_created"), True, "execution_blocked"),
            (("phase2_entry_report", "outcome_observation_created"), True, "outcome_observation_blocked"),
        )
        for path, value, result_field in cases:
            bad = copy.deepcopy(self.wait)
            self._set_path(bad, path, value)

            result = validate_phase2_closed_phase1_substrate_perception_capability_grounding_entry_record(bad)

            self.assertFalse(result["valid"])
            self.assertFalse(result[result_field])

    def test_memory_predictor_feed_production_and_claim_pollution_blocks(self):
        cases = (
            (("phase2_entry_report", "memory_write_created"), True, "memory_write_blocked"),
            (("authority_containment", "predictor_read_enabled_in_this_package"), True, "predictor_use_blocked"),
            (("authority_containment", "predictor_modified_in_this_package"), True, "predictor_use_blocked"),
            (("authority_containment", "direct_tendency_feed_in_this_package"), True, "direct_feed_blocked"),
            (("phase2_entry_report", "production_behavior_created"), True, "production_behavior_blocked"),
            (("phase2_entry_report", "learning_claim_created"), True, "learning_claim_blocked"),
            (("phase2_entry_report", "consciousness_claim_created"), True, "consciousness_claim_blocked"),
            (("authority_containment", "llm_runtime_used"), True, "llm_runtime_blocked"),
        )
        for path, value, result_field in cases:
            bad = copy.deepcopy(self.probe)
            self._set_path(bad, path, value)

            result = validate_phase2_closed_phase1_substrate_perception_capability_grounding_entry_record(bad)

            self.assertFalse(result["valid"])
            self.assertFalse(result[result_field])

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(summary["phase2_entry_result_count"], 44)
        self.assertEqual(summary["valid_phase2_entry_count"], 3)
        self.assertEqual(summary["invalid_phase2_entry_count"], 41)
        self.assertEqual(summary["phase2_entry_report_created_count"], 3)
        self.assertEqual(summary["perception_evidence_candidates_identified_count"], 3)
        self.assertEqual(summary["capability_evidence_candidates_identified_count"], 3)
        self.assertEqual(summary["unknown_fields_preserved_count"], 3)
        self.assertEqual(summary["reach_phase2_entry_count"], 1)
        self.assertEqual(summary["wait_phase2_entry_count"], 1)
        self.assertEqual(summary["probe_phase2_entry_count"], 1)
        self.assertEqual(summary["candidate_input_blocked_count"], 3)
        self.assertEqual(summary["candidate_ordering_blocked_count"], 3)
        self.assertEqual(summary["action_selection_blocked_count"], 3)
        self.assertEqual(summary["direct_command_blocked_count"], 3)
        self.assertEqual(summary["execution_blocked_count"], 3)
        self.assertEqual(summary["outcome_observation_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["semantic_vision_blocked_count"], 3)
        self.assertEqual(summary["capability_authority_blocked_count"], 3)
        self.assertEqual(summary["external_tools_blocked_count"], 3)
        self.assertEqual(summary["predictor_use_blocked_count"], 3)
        self.assertEqual(summary["direct_feed_blocked_count"], 3)
        self.assertEqual(summary["production_behavior_blocked_count"], 3)
        self.assertEqual(summary["learning_claim_blocked_count"], 3)
        self.assertEqual(summary["consciousness_claim_blocked_count"], 3)
        self.assertEqual(summary["llm_runtime_blocked_count"], 3)
        self.assertEqual(summary["boundary_audit_passed_count"], 3)

    def test_cli_command(self):
        result = run_command("run-phase2-closed-phase1-substrate-perception-capability-grounding-entry-minimal-check")

        self.assertEqual(
            result["command"],
            "run-phase2-closed-phase1-substrate-perception-capability-grounding-entry-minimal-check",
        )
        self.assertEqual(result["status"], "ok")

    @staticmethod
    def _set_path(record, path, value):
        target = record
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value


if __name__ == "__main__":
    unittest.main()
