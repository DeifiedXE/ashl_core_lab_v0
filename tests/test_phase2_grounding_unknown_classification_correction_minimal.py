import copy
import unittest

from ashl_core.phase2_grounding_unknown_classification_correction_minimal import (
    BOUNDARY_INDEX_AFTER,
    BOUNDARY_INDEX_BEFORE,
    COMMAND,
    build_phase2_grounding_unknown_classification_correction_record,
    run_phase2_grounding_unknown_classification_correction_minimal_check,
    validate_phase2_grounding_unknown_classification_correction_record,
)
from ashl_core.phase2_perception_capability_evidence_source_link_minimal import (
    run_phase2_perception_capability_evidence_source_link_minimal_check,
)
from ashl_core.teaching_cli import run_command


class Phase2GroundingUnknownClassificationCorrectionMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_records = run_phase2_perception_capability_evidence_source_link_minimal_check()["valid_records"]
        cls.result = run_phase2_grounding_unknown_classification_correction_minimal_check()
        cls.record = cls.result["valid_records"][0]
        cls.classification = cls.record["deferred_source_classification"]

    def test_valid_correction_report_is_created(self):
        result = validate_phase2_grounding_unknown_classification_correction_record(self.record)

        self.assertTrue(result["valid"], result["error_codes"])
        self.assertEqual(self.record["record_type"], "phase2_grounding_unknown_classification_correction_minimal")
        self.assertEqual(self.record["boundary_index_before"], BOUNDARY_INDEX_BEFORE)
        self.assertEqual(self.record["boundary_index_after"], BOUNDARY_INDEX_AFTER)
        self.assertTrue(self.classification["deferred_source_classification_created"])
        self.assertTrue(self.classification["record_only_correction"])

    def test_reads_b185_source_link_reports(self):
        sources = self.record["source_b185_records"]
        source_values = {source["source_value"] for source in sources}
        result = validate_phase2_grounding_unknown_classification_correction_record(self.record)

        self.assertTrue(result["valid"], result["error_codes"])
        self.assertEqual(source_values, {"wait_or_observe", "observe_or_alternative_probe"})
        for source in sources:
            self.assertTrue(source["source_validated"])
            self.assertEqual(source["source_boundary_index"], "2026-06-09-b185")
            self.assertEqual(source["previous_evidence_lane"], "capability")
            self.assertEqual(source["previous_evidence_kind"], "closed_operation_context")
            self.assertIsNone(source["previous_linked_capability_id"])
            self.assertFalse(source["previous_capability_reference_resolved"])

    def test_wait_or_observe_is_marked_not_capability(self):
        item = self._item("wait_or_observe")
        result = validate_phase2_grounding_unknown_classification_correction_record(self.record)

        self.assertTrue(result["wait_or_observe_marked_not_capability"])
        self.assertEqual(item["previous_classification"], "capability_unknown")
        self.assertEqual(item["corrected_classification"], "not_capability_binding")
        self.assertFalse(item["is_capability_binding"])
        self.assertFalse(item["forced_into_capability"])
        self.assertEqual(item["deferred_to_phase"], "phase4_endocrine_tendency_settling")
        self.assertEqual(item["phase4_deferred_reference"], "phase4_endocrine_tendency_settling:wait_or_observe")

    def test_probe_is_marked_not_capability(self):
        item = self._item("observe_or_alternative_probe")
        result = validate_phase2_grounding_unknown_classification_correction_record(self.record)

        self.assertTrue(result["observe_or_alternative_probe_marked_not_capability"])
        self.assertEqual(item["previous_classification"], "capability_unknown")
        self.assertEqual(item["corrected_classification"], "not_capability_binding")
        self.assertFalse(item["is_capability_binding"])
        self.assertFalse(item["forced_into_capability"])
        self.assertEqual(item["deferred_to_phase"], "phase4_endocrine_tendency_settling")
        self.assertEqual(
            item["phase4_deferred_reference"],
            "phase4_endocrine_tendency_settling:observe_or_alternative_probe",
        )

    def test_phase4_reference_is_deferred_not_feed(self):
        result = validate_phase2_grounding_unknown_classification_correction_record(self.record)

        self.assertTrue(result["phase4_deferred_reference_created"])
        self.assertTrue(result["no_endocrine_feed"])
        for item in self.classification["classification_items"]:
            self.assertTrue(item["is_phase4_state_settling_signal"])
            self.assertFalse(item["endocrine_feed_created"])
            self.assertFalse(item["direct_tendency_feed_created"])

    def test_unknown_items_are_not_forced_into_capability(self):
        result = validate_phase2_grounding_unknown_classification_correction_record(self.record)

        self.assertTrue(result["unknown_items_not_forced_into_capability"])
        self.assertFalse(self.classification["capability_binding_created"])
        self.assertFalse(self.classification["capability_map_created"])
        for item in self.classification["classification_items"]:
            self.assertFalse(item["unknown_for_capability_line_after_correction"])
            self.assertFalse(item["capability_binding_created"])
            self.assertFalse(item["capability_map_created"])

    def test_no_candidate_action_or_memory_is_created(self):
        result = validate_phase2_grounding_unknown_classification_correction_record(self.record)
        containment = self.record["authority_containment"]

        self.assertTrue(result["no_candidate_input"])
        self.assertTrue(result["no_action_selection"])
        self.assertTrue(result["no_memory_write"])
        self.assertFalse(containment["candidate_input_created_in_this_package"])
        self.assertFalse(containment["selected_action_created_in_this_package"])
        self.assertFalse(containment["execution_created_in_this_package"])
        self.assertFalse(containment["persistent_memory_write_created_in_this_package"])

    def test_bad_b185_source_blocks_builder(self):
        bad_sources = copy.deepcopy(self.source_records)
        bad_sources[0]["capability_evidence_source_links"][0]["candidate_input_created"] = True

        with self.assertRaises(ValueError):
            build_phase2_grounding_unknown_classification_correction_record(bad_sources)

    def test_source_pollution_blocks_validator(self):
        cases = (
            (("source_b185_records", 0, "source_validated"), False),
            (("source_b185_records", 0, "source_boundary_index"), "2026-06-09-b184"),
            (("source_b185_records", 0, "previous_evidence_lane"), "perception"),
            (("source_b185_records", 0, "previous_capability_reference_resolved"), True),
        )
        for path, value in cases:
            bad = copy.deepcopy(self.record)
            self._set_path(bad, path, value)

            result = validate_phase2_grounding_unknown_classification_correction_record(bad)

            self.assertFalse(result["valid"])

    def test_classification_pollution_blocks_validator(self):
        cases = (
            (("deferred_source_classification", "deferred_source_classification_created"), False),
            (("deferred_source_classification", "wait_or_observe_marked_not_capability"), False),
            (("deferred_source_classification", "observe_or_alternative_probe_marked_not_capability"), False),
            (("deferred_source_classification", "phase4_deferred_reference_created"), False),
            (("deferred_source_classification", "classification_items", 0, "forced_into_capability"), True),
            (("deferred_source_classification", "classification_items", 0, "corrected_classification"), "capability_unknown"),
            (("deferred_source_classification", "classification_items", 0, "deferred_to_phase"), "phase2_capability_grounding"),
        )
        for path, value in cases:
            bad = copy.deepcopy(self.record)
            self._set_path(bad, path, value)

            result = validate_phase2_grounding_unknown_classification_correction_record(bad)

            self.assertFalse(result["valid"])

    def test_endocrine_candidate_action_memory_and_claim_pollution_blocks(self):
        cases = (
            (("deferred_source_classification", "classification_items", 0, "endocrine_feed_created"), True, "no_endocrine_feed"),
            (("authority_containment", "direct_tendency_feed_in_this_package"), True, "no_endocrine_feed"),
            (("deferred_source_classification", "candidate_input_created"), True, "no_candidate_input"),
            (("authority_containment", "selected_action_created_in_this_package"), True, "no_action_selection"),
            (("deferred_source_classification", "memory_write_created"), True, "no_memory_write"),
            (("authority_containment", "production_behavior_created_in_this_package"), True, "no_production_behavior"),
            (("authority_containment", "proof_of_learning_claim"), True, "no_learning_or_consciousness_claim"),
        )
        for path, value, result_field in cases:
            bad = copy.deepcopy(self.record)
            self._set_path(bad, path, value)

            result = validate_phase2_grounding_unknown_classification_correction_record(bad)

            self.assertFalse(result["valid"])
            self.assertFalse(result[result_field])

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(summary["classification_correction_result_count"], 24)
        self.assertEqual(summary["valid_classification_correction_count"], 1)
        self.assertEqual(summary["invalid_classification_correction_count"], 23)
        self.assertEqual(summary["deferred_source_classification_created_count"], 1)
        self.assertEqual(summary["wait_or_observe_marked_not_capability_count"], 1)
        self.assertEqual(summary["observe_or_alternative_probe_marked_not_capability_count"], 1)
        self.assertEqual(summary["phase4_deferred_reference_created_count"], 1)
        self.assertEqual(summary["unknown_items_not_forced_into_capability_count"], 1)
        self.assertEqual(summary["no_endocrine_feed_count"], 1)
        self.assertEqual(summary["no_candidate_input_count"], 1)
        self.assertEqual(summary["no_action_selection_count"], 1)
        self.assertEqual(summary["no_memory_write_count"], 1)
        self.assertEqual(summary["no_production_behavior_count"], 1)
        self.assertEqual(summary["no_learning_or_consciousness_claim_count"], 1)
        self.assertEqual(summary["boundary_audit_passed_count"], 1)

    def test_cli_command(self):
        result = run_command(COMMAND)

        self.assertEqual(result["command"], COMMAND)
        self.assertEqual(result["status"], "ok")

    def _item(self, source_value):
        for item in self.classification["classification_items"]:
            if item["source_value"] == source_value:
                return item
        raise AssertionError(f"missing item {source_value}")

    @staticmethod
    def _set_path(record, path, value):
        target = record
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value


if __name__ == "__main__":
    unittest.main()
