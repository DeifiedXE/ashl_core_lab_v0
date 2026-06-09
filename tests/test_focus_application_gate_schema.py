import json
import subprocess
import sys
import unittest
from copy import deepcopy

from ashl_core.focus_application_gate_schema import (
    build_valid_focus_application_gate_record,
    run_focus_application_gate_schema_check,
    validate_focus_application_gate_record,
)
from ashl_core.teaching_cli import run_command


class FocusApplicationGateSchemaTests(unittest.TestCase):
    def test_valid_review_only_gate_record_passes(self):
        record = build_valid_focus_application_gate_record()
        validation = validate_focus_application_gate_record(record)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(validation["gate_count"], 6)
        self.assertTrue(validation["all_required_gates_present"])
        self.assertFalse(validation["all_gates_passed"])

    def test_all_required_gates_must_be_present(self):
        record = build_valid_focus_application_gate_record()
        record["gates"] = []

        validation = validate_focus_application_gate_record(record)
        self.assertFalse(validation["valid"])
        for gate_name in [
            "focus_application_candidate_gate",
            "focus_lock_prevention_gate",
            "mentor_interrupt_gate",
            "endocrine_boundary_gate",
            "perception_to_action_boundary_gate",
            "runtime_permission_gate",
        ]:
            self.assertIn(f"missing_required_gate:{gate_name}", validation["error_codes"])

    def test_each_required_gate_missing_blocks_record(self):
        for gate_name in [
            "focus_application_candidate_gate",
            "focus_lock_prevention_gate",
            "mentor_interrupt_gate",
            "endocrine_boundary_gate",
            "perception_to_action_boundary_gate",
            "runtime_permission_gate",
        ]:
            with self.subTest(gate_name=gate_name):
                record = build_valid_focus_application_gate_record()
                record["gates"] = [gate for gate in record["gates"] if gate["gate_name"] != gate_name]
                validation = validate_focus_application_gate_record(record)
                self.assertFalse(validation["valid"])
                self.assertIn(f"missing_required_gate:{gate_name}", validation["error_codes"])

    def test_unknown_and_runtime_like_gate_status_blocks_record(self):
        for status in ["unknown", "runtime_enabled", "active", "applied"]:
            with self.subTest(status=status):
                record = build_valid_focus_application_gate_record()
                record["gates"][0]["status"] = status
                validation = validate_focus_application_gate_record(record)
                self.assertFalse(validation["valid"])
                self.assertIn(f"unknown_gate_status:{status}", validation["error_codes"])

    def test_gate_passed_true_blocks_record_in_v0(self):
        record = build_valid_focus_application_gate_record()
        record["gates"][0]["passed"] = True

        validation = validate_focus_application_gate_record(record)
        self.assertFalse(validation["valid"])
        self.assertIn("gate_passed_true", validation["error_codes"])

    def test_required_reason_code_missing_blocks_record(self):
        record = build_valid_focus_application_gate_record()
        record["gates"][0]["reason_codes"] = ["ranking_trace_is_not_active_focus"]

        validation = validate_focus_application_gate_record(record)
        self.assertFalse(validation["valid"])
        self.assertIn("missing_gate_reason_code:rank_position_1_not_selected_focus", validation["error_codes"])
        self.assertIn("missing_gate_reason_code:highest_total_score_not_selected_focus", validation["error_codes"])

    def test_unknown_reason_code_blocks_record(self):
        record = build_valid_focus_application_gate_record()
        record["gates"][0]["reason_codes"].append("select_active_focus")

        validation = validate_focus_application_gate_record(record)
        self.assertFalse(validation["valid"])
        self.assertIn("unknown_gate_reason_code:select_active_focus", validation["error_codes"])

    def test_active_focus_focus_applied_and_attention_control_block_record(self):
        for field, value, error_code in [
            ("active_focus_id", "focus_candidate_from_change_trace:001", "active_focus_id_non_null"),
            ("focus_applied", True, "focus_applied_enabled"),
            ("attention_control", True, "attention_control_enabled"),
        ]:
            with self.subTest(field=field):
                record = build_valid_focus_application_gate_record()
                record[field] = value
                validation = validate_focus_application_gate_record(record)
                self.assertFalse(validation["valid"])
                self.assertIn(error_code, validation["error_codes"])

    def test_runtime_and_bridge_flags_block_record(self):
        for flag, error_code in [
            ("runtime_focus_selector", "runtime_focus_selector_enabled"),
            ("runtime_ranking", "runtime_ranking_enabled"),
            ("active_focus_enabled", "active_focus_enabled"),
            ("focus_applied", "focus_applied_flag_enabled"),
            ("attention_control", "attention_control_flag_enabled"),
            ("focus_to_action_bridge", "focus_to_action_bridge_enabled"),
            ("perception_to_action_bridge", "perception_to_action_bridge_enabled"),
            ("endocrine_runtime", "endocrine_runtime_enabled"),
            ("object_recognition", "object_recognition_enabled"),
            ("object_tracking", "object_tracking_enabled"),
            ("semantic_vision", "semantic_vision_enabled"),
        ]:
            with self.subTest(flag=flag):
                record = build_valid_focus_application_gate_record()
                record["safety_flags"][flag] = True
                validation = validate_focus_application_gate_record(record)
                self.assertFalse(validation["valid"])
                self.assertIn(error_code, validation["error_codes"])

    def test_influence_write_and_predictor_flags_block_record(self):
        for flag, error_code in [
            ("action_selection_influence", "action_selection_influence_enabled"),
            ("memory_write", "memory_write_enabled"),
            ("endocrine_control", "endocrine_control_enabled"),
            ("predictor_modified", "predictor_modified_enabled"),
        ]:
            with self.subTest(flag=flag):
                record = build_valid_focus_application_gate_record()
                record["safety_flags"][flag] = 1
                validation = validate_focus_application_gate_record(record)
                self.assertFalse(validation["valid"])
                self.assertIn(error_code, validation["error_codes"])

    def test_downstream_unblocked_flags_block_record(self):
        for flag, error_code in [
            ("blocked_from_action_selection", "action_selection_not_blocked"),
            ("blocked_from_memory_write", "memory_write_not_blocked"),
            ("blocked_from_endocrine_control", "endocrine_control_not_blocked"),
        ]:
            with self.subTest(flag=flag):
                record = build_valid_focus_application_gate_record()
                record["safety_flags"][flag] = False
                validation = validate_focus_application_gate_record(record)
                self.assertFalse(validation["valid"])
                self.assertIn(error_code, validation["error_codes"])

    def test_source_trace_missing_blocks_record(self):
        record = build_valid_focus_application_gate_record()
        record.pop("source_trace")

        validation = validate_focus_application_gate_record(record)
        self.assertFalse(validation["valid"])
        self.assertIn("missing_required_field:source_trace", validation["error_codes"])
        self.assertIn("missing_source_trace", validation["error_codes"])

    def test_demo_check_summary_has_expected_counts(self):
        result = run_focus_application_gate_schema_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-focus-application-gate-schema-check")
        self.assertEqual(result["flow"], "focus_application_gate_schema_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["gate_record_count"], 6)
        self.assertEqual(summary["valid_gate_record_count"], 1)
        self.assertEqual(summary["invalid_gate_record_count"], 5)
        self.assertEqual(summary["gate_count"], 6)
        self.assertEqual(summary["required_gate_count"], 6)
        self.assertGreaterEqual(summary["missing_required_gate_blocked_count"], 1)
        self.assertGreaterEqual(summary["active_focus_non_null_blocked_count"], 1)
        self.assertGreaterEqual(summary["focus_applied_blocked_count"], 1)
        self.assertGreaterEqual(summary["attention_control_blocked_count"], 1)
        self.assertGreaterEqual(summary["runtime_permission_enabled_blocked_count"], 1)
        self.assertEqual(summary["runtime_focus_selector_count"], 0)
        self.assertEqual(summary["runtime_ranking_count"], 0)
        self.assertEqual(summary["active_focus_enabled_count"], 0)
        self.assertEqual(summary["focus_to_action_bridge_count"], 0)
        self.assertEqual(summary["perception_to_action_bridge_count"], 0)
        self.assertEqual(summary["endocrine_runtime_count"], 0)
        self.assertEqual(summary["action_selection_influence_count"], 0)
        self.assertEqual(summary["memory_write_count"], 0)
        self.assertEqual(summary["endocrine_control_count"], 0)
        self.assertEqual(summary["predictor_modified_count"], 0)
        self.assertEqual(summary["object_recognition_count"], 0)
        self.assertEqual(summary["object_tracking_count"], 0)
        self.assertEqual(summary["semantic_vision_count"], 0)
        self.assertTrue(boundary["schema_check_only"])
        self.assertTrue(boundary["review_only_gates"])
        self.assertFalse(boundary["runtime_focus_selector_added"])
        self.assertFalse(boundary["active_focus_selection_added"])
        self.assertFalse(boundary["focus_to_action_bridge_added"])

    def test_run_command_dispatches_schema_check(self):
        result = run_command("run-focus-application-gate-schema-check")

        self.assertEqual(result["command"], "run-focus-application-gate-schema-check")
        self.assertEqual(result["summary"]["valid_gate_record_count"], 1)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [sys.executable, "-m", "ashl_core.teaching_cli", "run-focus-application-gate-schema-check"],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-focus-application-gate-schema-check")
        self.assertEqual(result["summary"]["runtime_permission_enabled_blocked_count"], 1)


if __name__ == "__main__":
    unittest.main()
