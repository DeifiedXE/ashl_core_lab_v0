import copy
import unittest

from ashl_core.phase1_closure_audit_minimal import (
    BOUNDARY_INDEX_AFTER,
    BOUNDARY_INDEX_BEFORE,
    build_phase1_closure_audit_record,
    run_phase1_closure_audit_minimal_check,
    validate_phase1_closure_audit_record,
)
from ashl_core.phase1_runtime_session_trace_spine_minimal import (
    run_phase1_runtime_session_trace_spine_minimal_check,
)
from ashl_core.phase1_session_frame_runtime_tick_handoff_minimal import (
    run_phase1_session_frame_runtime_tick_handoff_minimal_check,
)
from ashl_core.phase1_tick1_frame_three_line_substrate_index_minimal import (
    run_phase1_tick1_frame_three_line_substrate_index_minimal_check,
)
from ashl_core.teaching_cli import run_command


class Phase1ClosureAuditMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.trace_records = run_phase1_runtime_session_trace_spine_minimal_check()["valid_records"]
        cls.handoff_records = run_phase1_session_frame_runtime_tick_handoff_minimal_check()["valid_records"]
        cls.index_records = run_phase1_tick1_frame_three_line_substrate_index_minimal_check()["valid_records"]
        cls.result = run_phase1_closure_audit_minimal_check()
        cls.records = cls.result["valid_records"]
        cls.reach = cls.records[0]
        cls.wait = cls.records[1]
        cls.probe = cls.records[2]

    def test_valid_phase1_closure_audits_are_created(self):
        for record in self.records:
            result = validate_phase1_closure_audit_record(record)
            closure = record["phase1_closure_audit"]

            self.assertTrue(result["valid"], result["error_codes"])
            self.assertEqual(record["record_type"], "phase1_closure_audit_minimal")
            self.assertEqual(record["boundary_index_before"], BOUNDARY_INDEX_BEFORE)
            self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)
            self.assertTrue(closure["phase1_session_trace_spine_present"])
            self.assertTrue(closure["tick_handoff_present"])
            self.assertTrue(closure["three_line_index_present"])
            self.assertTrue(closure["no_live_runtime"])
            self.assertTrue(closure["no_action_selection"])
            self.assertTrue(closure["no_memory_write"])
            self.assertTrue(closure["phase1_closure_ready"])

    def test_phase1_sources_are_validated_and_matched(self):
        record = build_phase1_closure_audit_record(
            self.trace_records[0],
            self.handoff_records[0],
            self.index_records[0],
        )
        source = record["source_phase1_substrates"]
        result = validate_phase1_closure_audit_record(record)

        self.assertTrue(result["valid"], result["error_codes"])
        self.assertTrue(source["trace_spine_validated"])
        self.assertEqual(source["trace_spine_boundary_index"], "2026-06-09-b179")
        self.assertTrue(source["tick_handoff_validated"])
        self.assertEqual(source["tick_handoff_boundary_index"], "2026-06-09-b181")
        self.assertTrue(source["three_line_index_validated"])
        self.assertEqual(source["three_line_index_boundary_index"], "2026-06-09-b182")
        self.assertTrue(source["all_source_scenarios_match"])
        self.assertTrue(source["all_source_sessions_match"])
        self.assertTrue(source["all_source_purposes_match"])

    def test_phase1_closure_ready_does_not_create_runtime_action_or_memory(self):
        for record in self.records:
            result = validate_phase1_closure_audit_record(record)

            self.assertTrue(result["phase1_closure_ready"])
            self.assertTrue(result["no_live_runtime"])
            self.assertTrue(result["no_action_selection"])
            self.assertTrue(result["no_memory_write"])
            self.assertTrue(result["candidate_input_blocked"])
            self.assertTrue(result["production_behavior_blocked"])
            self.assertTrue(result["proof_claim_blocked"])
            self.assertTrue(result["consciousness_claim_blocked"])

    def test_duplicate_phase1_packages_are_blocked(self):
        for record in self.records:
            guard = record["duplicate_package_guard"]
            result = validate_phase1_closure_audit_record(record)

            self.assertTrue(guard["phase1_duplicate_packages_blocked"])
            self.assertFalse(guard["duplicate_session_trace_spine_package_allowed"])
            self.assertFalse(guard["duplicate_session_frame_package_allowed"])
            self.assertFalse(guard["duplicate_tick_handoff_package_allowed"])
            self.assertFalse(guard["duplicate_three_line_index_package_allowed"])
            self.assertFalse(guard["duplicate_phase1_closure_audit_package_allowed"])
            self.assertEqual(guard["next_phase_required"], "Phase2")
            self.assertTrue(result["duplicate_phase1_packages_blocked"])

    def test_bad_source_blocks_builder(self):
        bad_index = copy.deepcopy(self.index_records[0])
        bad_index["thought_line_index"]["candidate_input_created"] = True

        with self.assertRaises(ValueError):
            build_phase1_closure_audit_record(self.trace_records[0], self.handoff_records[0], bad_index)

    def test_missing_source_presence_blocks_validator(self):
        cases = (
            ("phase1_session_trace_spine_present", False),
            ("tick_handoff_present", False),
            ("three_line_index_present", False),
            ("phase1_closure_ready", False),
        )
        for field, value in cases:
            bad = copy.deepcopy(self.reach)
            bad["phase1_closure_audit"][field] = value

            result = validate_phase1_closure_audit_record(bad)

            self.assertFalse(result["valid"])
            self.assertFalse(result["phase1_closure_ready"])

    def test_live_runtime_action_or_memory_pollution_blocks(self):
        cases = (
            (("phase1_closure_audit", "no_live_runtime"), False, "no_live_runtime"),
            (("phase1_closure_audit", "no_action_selection"), False, "no_action_selection"),
            (("phase1_closure_audit", "no_memory_write"), False, "no_memory_write"),
            (("closure_containment", "live_runtime_session_started_in_this_package"), True, "no_live_runtime"),
            (("closure_containment", "selected_action_created_in_this_package"), True, "no_action_selection"),
            (("closure_containment", "persistent_memory_write_created_in_this_package"), True, "no_memory_write"),
        )
        for path, value, result_field in cases:
            bad = copy.deepcopy(self.wait)
            self._set_path(bad, path, value)

            result = validate_phase1_closure_audit_record(bad)

            self.assertFalse(result["valid"])
            self.assertFalse(result[result_field])

    def test_duplicate_guard_pollution_blocks(self):
        cases = (
            ("phase1_duplicate_packages_blocked", False),
            ("duplicate_session_trace_spine_package_allowed", True),
            ("duplicate_session_frame_package_allowed", True),
            ("duplicate_tick_handoff_package_allowed", True),
            ("duplicate_three_line_index_package_allowed", True),
            ("duplicate_phase1_closure_audit_package_allowed", True),
            ("next_phase_required", "Phase1"),
        )
        for field, value in cases:
            bad = copy.deepcopy(self.probe)
            bad["duplicate_package_guard"][field] = value

            result = validate_phase1_closure_audit_record(bad)

            self.assertFalse(result["valid"])
            self.assertFalse(result["duplicate_phase1_packages_blocked"])

    def test_external_predictor_feed_production_and_claim_pollution_blocks(self):
        cases = (
            (("closure_containment", "candidate_input_created_in_this_package"), True, "candidate_input_blocked"),
            (("closure_containment", "external_tool_called_in_this_package"), True, "external_tools_blocked"),
            (("closure_containment", "predictor_modified_in_this_package"), True, "predictor_use_blocked"),
            (("closure_containment", "direct_tendency_feed_in_this_package"), True, "direct_feed_blocked"),
            (("boundary_audit", "production_behavior_created"), True, "production_behavior_blocked"),
            (("boundary_audit", "proof_of_learning_claim"), True, "proof_claim_blocked"),
            (("boundary_audit", "consciousness_claim"), True, "consciousness_claim_blocked"),
            (("boundary_audit", "llm_runtime_used"), True, "llm_runtime_blocked"),
        )
        for path, value, result_field in cases:
            bad = copy.deepcopy(self.reach)
            self._set_path(bad, path, value)

            result = validate_phase1_closure_audit_record(bad)

            self.assertFalse(result["valid"])
            self.assertFalse(result[result_field])

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]

        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(summary["phase1_closure_audit_result_count"], 35)
        self.assertEqual(summary["valid_phase1_closure_audit_count"], 3)
        self.assertEqual(summary["invalid_phase1_closure_audit_count"], 32)
        self.assertEqual(summary["phase1_session_trace_spine_present_count"], 3)
        self.assertEqual(summary["tick_handoff_present_count"], 3)
        self.assertEqual(summary["three_line_index_present_count"], 3)
        self.assertEqual(summary["no_live_runtime_count"], 3)
        self.assertEqual(summary["no_action_selection_count"], 3)
        self.assertEqual(summary["no_memory_write_count"], 3)
        self.assertEqual(summary["phase1_closure_ready_count"], 3)
        self.assertEqual(summary["duplicate_phase1_packages_blocked_count"], 3)
        self.assertEqual(summary["candidate_input_blocked_count"], 3)
        self.assertEqual(summary["external_tools_blocked_count"], 3)
        self.assertEqual(summary["predictor_use_blocked_count"], 3)
        self.assertEqual(summary["direct_feed_blocked_count"], 3)
        self.assertEqual(summary["production_behavior_blocked_count"], 3)
        self.assertEqual(summary["proof_claim_blocked_count"], 3)
        self.assertEqual(summary["consciousness_claim_blocked_count"], 3)
        self.assertEqual(summary["llm_runtime_blocked_count"], 3)
        self.assertEqual(summary["boundary_audit_passed_count"], 3)

    def test_cli_command(self):
        result = run_command("run-phase1-closure-audit-minimal-check")

        self.assertEqual(result["command"], "run-phase1-closure-audit-minimal-check")
        self.assertEqual(result["status"], "ok")

    @staticmethod
    def _set_path(record, path, value):
        target = record
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value


if __name__ == "__main__":
    unittest.main()
