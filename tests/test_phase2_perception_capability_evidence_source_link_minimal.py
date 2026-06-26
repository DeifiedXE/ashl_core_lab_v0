import copy
import unittest

from ashl_core.phase2_closed_phase1_substrate_perception_capability_grounding_entry_minimal import (
    run_phase2_closed_phase1_substrate_perception_capability_grounding_entry_minimal_check,
)
from ashl_core.phase2_perception_capability_evidence_source_link_minimal import (
    BOUNDARY_INDEX_AFTER,
    BOUNDARY_INDEX_BEFORE,
    COMMAND,
    build_phase2_perception_capability_evidence_source_link_record,
    run_phase2_perception_capability_evidence_source_link_minimal_check,
    validate_phase2_perception_capability_evidence_source_link_record,
)
from ashl_core.teaching_cli import run_command


class Phase2PerceptionCapabilityEvidenceSourceLinkMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_records = run_phase2_closed_phase1_substrate_perception_capability_grounding_entry_minimal_check()[
            "valid_records"
        ]
        cls.result = run_phase2_perception_capability_evidence_source_link_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.by_scenario = {record["source_phase2_entry_report"]["scenario_id"]: record for record in cls.records}
        cls.reach = cls.by_scenario["item_reachable_feedback_prioritizes_reach"]
        cls.wait = cls.by_scenario["item_not_afforded_blocks_feedback_priority"]
        cls.probe = cls.by_scenario["mismatch_feedback_outranks_retry_tendency"]

    def test_valid_source_link_reports_are_created(self):
        for record in self.records:
            result = validate_phase2_perception_capability_evidence_source_link_record(record)
            report = record["source_link_report"]

            self.assertTrue(result["valid"], result["error_codes"])
            self.assertEqual(record["record_type"], "phase2_perception_capability_evidence_source_link_minimal")
            self.assertEqual(record["boundary_index_before"], BOUNDARY_INDEX_BEFORE)
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)
            self.assertTrue(report["phase2_source_link_report_created"])
            self.assertEqual(report["phase2_purpose"], "perception_and_capability_grounding")
            self.assertTrue(report["record_only_report"])
            self.assertTrue(report["source_reference_link_only"])

    def test_reads_b184_entry_report_as_source(self):
        record = build_phase2_perception_capability_evidence_source_link_record(self.source_records[0])
        source = record["source_phase2_entry_report"]
        result = validate_phase2_perception_capability_evidence_source_link_record(record)

        self.assertTrue(result["valid"], result["error_codes"])
        self.assertTrue(source["source_validated"])
        self.assertEqual(source["source_boundary_index"], "2026-06-09-b184")
        self.assertTrue(source["phase2_entry_report_created"])
        self.assertTrue(source["source_record_only"])
        self.assertFalse(source["source_candidate_input_created"])
        self.assertFalse(source["source_memory_write_created"])

    def test_perception_candidates_link_to_visual_spatial_source_reference(self):
        for record in self.records:
            result = validate_phase2_perception_capability_evidence_source_link_record(record)
            catalog = record["existing_evidence_source_catalog"]
            links = record["perception_evidence_source_links"]
            kinds = {link["evidence_kind"] for link in links}

            self.assertTrue(result["visual_spatial_source_reference_available"])
            self.assertEqual(catalog["visual_spatial_source"]["source_family"], "visual_spatial_grounding_minimal")
            self.assertEqual(kinds, {"observed_outcome_context", "phase1_evidence_source_reference"})
            self.assertTrue(all(link["linked_to_existing_source_reference"] for link in links))
            self.assertTrue(all(link["target_source_family"] == "visual_spatial_grounding_minimal" for link in links))
            self.assertTrue(all(link["resolved_grounding_created"] is False for link in links))
            self.assertTrue(result["semantic_vision_blocked"])

    def test_reach_front_capability_candidate_links_to_existing_capability_map_reference(self):
        result = validate_phase2_perception_capability_evidence_source_link_record(self.reach)
        closed_operation_link = self._link_by_kind(self.reach["capability_evidence_source_links"], "closed_operation_context")

        self.assertTrue(result["valid"], result["error_codes"])
        self.assertTrue(result["reach_front_capability_reference_linked"])
        self.assertEqual(closed_operation_link["source_value"], "reach_front_item")
        self.assertEqual(closed_operation_link["linked_capability_id"], "sandbox.body.reach_front")
        self.assertTrue(closed_operation_link["linked_capability_available"])
        self.assertTrue(closed_operation_link["capability_reference_resolved"])
        self.assertFalse(closed_operation_link["grounded_capability_binding_created"])

    def test_wait_and_probe_capability_links_preserve_unknown(self):
        for record in (self.wait, self.probe):
            result = validate_phase2_perception_capability_evidence_source_link_record(record)
            closed_operation_link = self._link_by_kind(
                record["capability_evidence_source_links"],
                "closed_operation_context",
            )

            self.assertTrue(result["valid"], result["error_codes"])
            self.assertFalse(closed_operation_link["resolved_source_reference"])
            self.assertIsNone(closed_operation_link["linked_capability_id"])
            self.assertIsNotNone(closed_operation_link["unresolved_unknown_reason"])
            self.assertTrue(closed_operation_link["unknown_preserved"])

    def test_unresolved_unknowns_are_preserved_without_invention(self):
        self.assertEqual(self.wait["unresolved_unknown_preservation"]["unresolved_link_count"], 2)
        self.assertEqual(self.reach["unresolved_unknown_preservation"]["unresolved_link_count"], 1)
        self.assertEqual(self.probe["unresolved_unknown_preservation"]["unresolved_link_count"], 2)
        for record in self.records:
            unknown = record["unresolved_unknown_preservation"]
            result = validate_phase2_perception_capability_evidence_source_link_record(record)

            self.assertTrue(result["unresolved_unknowns_preserved"])
            self.assertTrue(unknown["unresolved_unknowns_preserved"])
            self.assertFalse(unknown["unknown_values_invented"])
            self.assertFalse(unknown["semantic_vision_created"])
            self.assertFalse(unknown["grounded_capability_binding_created"])

    def test_does_not_create_semantic_vision_capability_map_action_or_memory(self):
        for record in self.records:
            report = record["source_link_report"]
            containment = record["authority_containment"]
            result = validate_phase2_perception_capability_evidence_source_link_record(record)

            self.assertFalse(report["semantic_vision_created"])
            self.assertFalse(report["object_recognition_created"])
            self.assertFalse(report["active_focus_created"])
            self.assertFalse(report["capability_map_created"])
            self.assertFalse(report["capability_map_mutated"])
            self.assertFalse(report["candidate_input_created"])
            self.assertFalse(report["action_selection_created"])
            self.assertFalse(report["direct_command_created"])
            self.assertFalse(report["execution_created"])
            self.assertFalse(report["outcome_observation_created"])
            self.assertFalse(report["memory_write_created"])
            self.assertFalse(containment["predictor_read_enabled_in_this_package"])
            self.assertTrue(result["candidate_input_blocked"])
            self.assertTrue(result["capability_map_mutation_blocked"])
            self.assertTrue(result["memory_write_blocked"])

    def test_bad_source_blocks_builder(self):
        bad_source = copy.deepcopy(self.source_records[0])
        bad_source["phase2_entry_report"]["candidate_input_created"] = True

        with self.assertRaises(ValueError):
            build_phase2_perception_capability_evidence_source_link_record(bad_source)

    def test_bad_source_summary_blocks_validator(self):
        cases = (
            (("source_phase2_entry_report", "source_validated"), False),
            (("source_phase2_entry_report", "source_boundary_index"), "2026-06-09-b183"),
            (("source_phase2_entry_report", "phase2_entry_report_created"), False),
            (("source_phase2_entry_report", "source_candidate_input_created"), True),
            (("source_phase2_entry_report", "source_semantic_vision_created"), True),
        )
        for path, value in cases:
            bad = copy.deepcopy(self.reach)
            self._set_path(bad, path, value)

            result = validate_phase2_perception_capability_evidence_source_link_record(bad)

            self.assertFalse(result["valid"])

    def test_visual_source_pollution_blocks(self):
        cases = (
            (("existing_evidence_source_catalog", "visual_spatial_source", "source_available"), False),
            (("existing_evidence_source_catalog", "visual_spatial_source", "boundary_index"), "2026-06-09-b110"),
            (("existing_evidence_source_catalog", "visual_spatial_source", "semantic_vision_created"), True),
            (("perception_evidence_source_links", 0, "target_source_family"), "semantic_vision"),
            (("perception_evidence_source_links", 0, "semantic_vision_created"), True),
            (("perception_evidence_source_links", 0, "object_recognition_created"), True),
            (("perception_evidence_source_links", 0, "active_focus_created"), True),
            (("perception_evidence_source_links", 0, "new_visual_record_created"), True),
        )
        for path, value in cases:
            bad = copy.deepcopy(self.wait)
            self._set_path(bad, path, value)

            result = validate_phase2_perception_capability_evidence_source_link_record(bad)

            self.assertFalse(result["valid"])
            if "semantic" in path or "object" in path or "focus" in path or "new_visual" in path:
                self.assertFalse(result["semantic_vision_blocked"])

    def test_capability_source_pollution_blocks(self):
        cases = (
            (("existing_evidence_source_catalog", "qingyin_bridge_capability_map_sources", 0, "source_available"), False),
            (("existing_evidence_source_catalog", "qingyin_bridge_capability_map_sources", 0, "boundary_index"), "2026-06-09-b134"),
            (("existing_evidence_source_catalog", "capability_map_created_in_this_package"), True),
            (("existing_evidence_source_catalog", "capability_map_mutated_in_this_package"), True),
            (("existing_evidence_source_catalog", "raw_tool_access_created_in_this_package"), True),
            (("capability_evidence_source_links", 0, "grounded_capability_binding_created"), True),
            (("capability_evidence_source_links", 0, "capability_map_created"), True),
            (("capability_evidence_source_links", 0, "capability_map_mutated"), True),
            (("capability_evidence_source_links", 0, "raw_tool_access_created"), True),
        )
        for path, value in cases:
            bad = copy.deepcopy(self.probe)
            self._set_path(bad, path, value)

            result = validate_phase2_perception_capability_evidence_source_link_record(bad)

            self.assertFalse(result["valid"])

    def test_capability_wrong_reach_reference_blocks(self):
        bad = copy.deepcopy(self.reach)
        bad["capability_evidence_source_links"][0]["linked_capability_id"] = "sandbox.body.step_forward"

        result = validate_phase2_perception_capability_evidence_source_link_record(bad)

        self.assertFalse(result["valid"])
        self.assertFalse(result["reach_front_capability_reference_linked"])

    def test_candidate_action_execution_and_outcome_pollution_blocks(self):
        cases = (
            (("source_link_report", "candidate_input_created"), True, "candidate_input_blocked"),
            (("source_link_report", "candidate_ordering_created"), True, "candidate_ordering_blocked"),
            (("authority_containment", "selected_action_created_in_this_package"), True, "action_selection_blocked"),
            (("source_link_report", "direct_command_created"), True, "direct_command_blocked"),
            (("source_link_report", "execution_created"), True, "execution_blocked"),
            (("source_link_report", "outcome_observation_created"), True, "outcome_observation_blocked"),
        )
        for path, value, result_field in cases:
            bad = copy.deepcopy(self.wait)
            self._set_path(bad, path, value)

            result = validate_phase2_perception_capability_evidence_source_link_record(bad)

            self.assertFalse(result["valid"])
            self.assertFalse(result[result_field])

    def test_memory_predictor_feed_production_and_claim_pollution_blocks(self):
        cases = (
            (("source_link_report", "memory_write_created"), True, "memory_write_blocked"),
            (("authority_containment", "predictor_read_enabled_in_this_package"), True, "predictor_use_blocked"),
            (("authority_containment", "direct_endocrine_feed_in_this_package"), True, "direct_feed_blocked"),
            (("source_link_report", "production_behavior_created"), True, "production_behavior_blocked"),
            (("source_link_report", "learning_claim_created"), True, "learning_claim_blocked"),
            (("source_link_report", "consciousness_claim_created"), True, "consciousness_claim_blocked"),
        )
        for path, value, result_field in cases:
            bad = copy.deepcopy(self.probe)
            self._set_path(bad, path, value)

            result = validate_phase2_perception_capability_evidence_source_link_record(bad)

            self.assertFalse(result["valid"])
            self.assertFalse(result[result_field])

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(summary["source_link_result_count"], 52)
        self.assertEqual(summary["valid_source_link_count"], 3)
        self.assertEqual(summary["invalid_source_link_count"], 49)
        self.assertEqual(summary["source_link_report_created_count"], 3)
        self.assertEqual(summary["perception_source_links_created_count"], 3)
        self.assertEqual(summary["capability_source_links_created_count"], 3)
        self.assertEqual(summary["visual_spatial_source_reference_available_count"], 3)
        self.assertEqual(summary["capability_map_source_reference_available_count"], 3)
        self.assertEqual(summary["unresolved_unknowns_preserved_count"], 3)
        self.assertEqual(summary["reach_front_capability_reference_linked_count"], 1)
        self.assertEqual(summary["wait_unknown_source_link_count"], 1)
        self.assertEqual(summary["probe_unknown_source_link_count"], 1)
        self.assertEqual(summary["candidate_input_blocked_count"], 3)
        self.assertEqual(summary["candidate_ordering_blocked_count"], 3)
        self.assertEqual(summary["action_selection_blocked_count"], 3)
        self.assertEqual(summary["direct_command_blocked_count"], 3)
        self.assertEqual(summary["execution_blocked_count"], 3)
        self.assertEqual(summary["outcome_observation_blocked_count"], 3)
        self.assertEqual(summary["memory_write_blocked_count"], 3)
        self.assertEqual(summary["semantic_vision_blocked_count"], 3)
        self.assertEqual(summary["capability_map_mutation_blocked_count"], 3)
        self.assertEqual(summary["raw_tool_access_blocked_count"], 3)
        self.assertEqual(summary["predictor_use_blocked_count"], 3)
        self.assertEqual(summary["direct_feed_blocked_count"], 3)
        self.assertEqual(summary["production_behavior_blocked_count"], 3)
        self.assertEqual(summary["learning_claim_blocked_count"], 3)
        self.assertEqual(summary["consciousness_claim_blocked_count"], 3)
        self.assertEqual(summary["boundary_audit_passed_count"], 3)

    def test_cli_command(self):
        result = run_command(COMMAND)

        self.assertEqual(result["command"], COMMAND)
        self.assertEqual(result["status"], "ok")

    @staticmethod
    def _link_by_kind(links, kind):
        for link in links:
            if link["evidence_kind"] == kind:
                return link
        raise AssertionError(f"missing link kind {kind}")

    @staticmethod
    def _set_path(record, path, value):
        target = record
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value


if __name__ == "__main__":
    unittest.main()
