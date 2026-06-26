import copy
import unittest

from ashl_core.phase2_to_phase10_completed_capability_cross_check_minimal import (
    BOUNDARY_INDEX_AFTER,
    BOUNDARY_INDEX_BEFORE,
    COMMAND,
    build_phase2_to_phase10_completed_capability_cross_check_record,
    run_phase2_to_phase10_completed_capability_cross_check_minimal_check,
    validate_phase2_to_phase10_completed_capability_cross_check_record,
)
from ashl_core.teaching_cli import run_command


class Phase2ToPhase10CompletedCapabilityCrossCheckMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = run_phase2_to_phase10_completed_capability_cross_check_minimal_check()
        cls.record = cls.result["valid_records"][0]

    def test_valid_cross_check_report_is_created(self):
        validation = validate_phase2_to_phase10_completed_capability_cross_check_record(self.record)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(self.record["record_type"], "phase2_to_phase10_completed_capability_cross_check_minimal")
        self.assertEqual(self.record["boundary_index_before"], BOUNDARY_INDEX_BEFORE)
        self.assertEqual(self.record["boundary_index_after"], BOUNDARY_INDEX_AFTER)
        self.assertEqual(self.result["status"], "ok")

    def test_reads_required_docs(self):
        validation = validate_phase2_to_phase10_completed_capability_cross_check_record(self.record)
        readback = self.record["source_document_readback"]
        source_ids = {source["source_id"] for source in readback["source_documents"]}

        self.assertTrue(validation["reads_capability_inventory"])
        self.assertTrue(validation["reads_capability_matrix"])
        self.assertTrue(validation["reads_status"])
        self.assertTrue(validation["reads_line_index"])
        self.assertIn("capability_inventory", source_ids)
        self.assertIn("capability_matrix", source_ids)
        self.assertIn("status", source_ids)
        self.assertIn("line_index", source_ids)

    def test_completed_items_are_marked_do_not_repeat(self):
        completed = self.record["completed_do_not_repeat"]
        ids = {item["capability_id"] for item in completed}
        validation = validate_phase2_to_phase10_completed_capability_cross_check_record(self.record)

        self.assertTrue(validation["phase2_completed_items_present"])
        self.assertIn("phase2_grounding_entry_report", ids)
        self.assertIn("phase2_evidence_source_link_report", ids)
        self.assertIn("phase2_unknown_classification_correction", ids)
        for item in completed:
            self.assertEqual(item["classification"], "completed_do_not_repeat")
            self.assertTrue(item["reuse_rule"])
            self.assertTrue(item["blocked_duplicate"])

    def test_partial_items_can_only_extend_existing_spines(self):
        partial = self.record["partial_only_extend"]
        ids = {item["capability_id"] for item in partial}
        validation = validate_phase2_to_phase10_completed_capability_cross_check_record(self.record)

        self.assertTrue(validation["phase3_to_phase5_partial_or_unfinished_present"])
        self.assertIn("phase2_perception_capability_grounding", ids)
        self.assertIn("phase3_memory_admission_and_retention", ids)
        self.assertIn("phase4_layered_thought_and_state_settling", ids)
        self.assertIn("phase5_nine_line_growth_substrate", ids)
        for item in partial:
            self.assertEqual(item["classification"], "partial_only_extend")
            self.assertTrue(item["only_valid_next_connection"])
            self.assertTrue(item["must_not_restart_from"])

    def test_unfinished_items_can_enter_roadmap(self):
        unfinished = self.record["unfinished_roadmap_candidates"]
        ids = {item["capability_id"] for item in unfinished}
        validation = validate_phase2_to_phase10_completed_capability_cross_check_record(self.record)

        self.assertIn("phase2_grounding_source_availability_readback", ids)
        self.assertIn("phase3_reviewed_session_trace_memory_candidate", ids)
        self.assertIn("phase4_record_only_settling_signal", ids)
        self.assertIn("phase5_nine_line_integration_audit", ids)
        self.assertIn("phase6_to_phase10_authoritative_plan", ids)
        self.assertTrue(validation["phase6_to_phase10_not_authorized_as_runtime"])

    def test_design_only_items_are_not_runtime(self):
        design_only = self.record["design_only_not_runtime"]
        documents = {item["document"] for item in design_only}
        validation = validate_phase2_to_phase10_completed_capability_cross_check_record(self.record)

        self.assertTrue(validation["design_only_runtime_confusion_blocked"])
        self.assertIn("docs/qingyin_thought_system_layering_design_v0.md", documents)
        self.assertIn("docs/qingyin_bridge_dual_eye_capability_perception_design_v0.md", documents)
        for item in design_only:
            self.assertEqual(item["classification"], "design_only_not_runtime")
            self.assertTrue(item["reason"])

    def test_duplicate_prevention_is_visible(self):
        duplicate = self.record["duplicate_prevention"]
        validation = validate_phase2_to_phase10_completed_capability_cross_check_record(self.record)

        self.assertTrue(validation["duplicate_reimplementation_blocked"])
        self.assertTrue(validation["roadmap_uncertainty_reduced"])
        self.assertTrue(duplicate["phase1_duplicate_substrate_blocked"])
        self.assertTrue(duplicate["phase2_entry_duplicate_blocked"])
        self.assertTrue(duplicate["phase2_source_link_duplicate_blocked"])
        self.assertTrue(duplicate["phase2_wait_probe_capability_mistake_blocked"])

    def test_no_runtime_authority_is_created(self):
        authority = self.record["authority_containment"]
        validation = validate_phase2_to_phase10_completed_capability_cross_check_record(self.record)

        self.assertFalse(validation["new_runtime_authority_created"])
        self.assertTrue(validation["no_candidate_input"])
        self.assertTrue(validation["no_action_selection"])
        self.assertTrue(validation["no_memory_write"])
        self.assertTrue(validation["no_production_behavior"])
        self.assertTrue(validation["no_learning_or_consciousness_claim"])
        self.assertFalse(authority["new_runtime_authority_created"])
        self.assertFalse(authority["candidate_input_created_in_this_package"])
        self.assertFalse(authority["selected_action_created_in_this_package"])
        self.assertFalse(authority["memory_write_created_in_this_package"])
        self.assertFalse(authority["production_behavior_created_in_this_package"])

    def test_bad_source_docs_block_builder(self):
        source_texts = {
            "capability_inventory": "",
            "capability_matrix": "phase2 closed phase1 substrate perception capability grounding entry minimal",
            "status": "Current version: `Boundary Index Version: 2026-06-09-b186`",
            "line_index": "# ASHL Core Phase0 Line Document Index",
            "boundary_index": "Boundary Index Version: 2026-06-09-b186",
            "growth_plan": "## Phase 2: Perception And Capability Grounding",
        }

        with self.assertRaises(ValueError):
            build_phase2_to_phase10_completed_capability_cross_check_record(source_texts)

    def test_invalid_cases_are_rejected(self):
        cases = (
            (("record_type",), "bad_record"),
            (("boundary_index_after",), "2026-06-09-b186"),
            (("source_document_readback", "reads_capability_inventory"), False),
            (("completed_do_not_repeat", 2, "classification"), "partial_only_extend"),
            (("partial_only_extend", 1, "only_valid_next_connection"), ""),
            (("unfinished_roadmap_candidates", 5, "why_allowed"), ""),
            (("design_only_not_runtime", 0, "classification"), "runtime_ready"),
            (("duplicate_prevention", "completed_items_must_not_be_reimplemented"), False),
            (("duplicate_prevention", "phase6_to_phase10_runtime_claim_blocked_without_plan"), False),
            (("authority_containment", "new_runtime_authority_created"), True),
            (("authority_containment", "candidate_input_created_in_this_package"), True),
            (("authority_containment", "selected_action_created_in_this_package"), True),
            (("authority_containment", "memory_write_created_in_this_package"), True),
            (("authority_containment", "production_behavior_created_in_this_package"), True),
            (("authority_containment", "proof_of_learning_claim"), True),
            (("human_summary", "what_error_it_prevents"), ""),
        )
        for path, value in cases:
            bad = copy.deepcopy(self.record)
            self._set_path(bad, path, value)

            validation = validate_phase2_to_phase10_completed_capability_cross_check_record(bad)

            self.assertFalse(validation["valid"], path)

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(summary["cross_check_result_count"], 25)
        self.assertEqual(summary["valid_cross_check_count"], 1)
        self.assertEqual(summary["invalid_cross_check_count"], 24)
        self.assertEqual(summary["reads_capability_inventory_count"], 1)
        self.assertEqual(summary["reads_capability_matrix_count"], 1)
        self.assertEqual(summary["reads_status_count"], 1)
        self.assertEqual(summary["reads_line_index_count"], 1)
        self.assertEqual(summary["completed_do_not_repeat_count"], 5)
        self.assertEqual(summary["partial_only_extend_count"], 4)
        self.assertEqual(summary["unfinished_roadmap_candidate_count"], 6)
        self.assertEqual(summary["design_only_not_runtime_count"], 5)
        self.assertEqual(summary["phase6_to_phase10_not_authorized_as_runtime_count"], 1)
        self.assertEqual(summary["new_runtime_authority_created_count"], 0)

    def test_cli_command(self):
        result = run_command(COMMAND)

        self.assertEqual(result["command"], COMMAND)
        self.assertEqual(result["status"], "ok")

    @staticmethod
    def _set_path(record, path, value):
        target = record
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value


if __name__ == "__main__":
    unittest.main()
