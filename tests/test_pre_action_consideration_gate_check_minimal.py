import json
import subprocess
import sys
import unittest

from ashl_core.pre_action_consideration_candidate_minimal import build_pre_action_consideration_candidates
from ashl_core.pre_action_consideration_gate_check_minimal import (
    build_pre_action_consideration_gate_result,
    run_pre_action_consideration_gate_check_minimal_check,
    validate_pre_action_consideration_gate_result,
)
from ashl_core.runtime_tendency_memory_influence_safety_envelope_minimal import (
    build_runtime_tendency_memory_influence_safety_envelope,
)
from ashl_core.teaching_cli import run_command


class PreActionConsiderationGateCheckMinimalTests(unittest.TestCase):
    def _valid_result(self):
        return build_pre_action_consideration_gate_result()

    def _candidate(self, scenario_id):
        for candidate in self._valid_result()["gated_candidates"]:
            if candidate["scenario_id"] == scenario_id:
                return candidate
        self.fail(f"missing candidate {scenario_id}")

    def _assert_invalid(self, record, error_code):
        validation = validate_pre_action_consideration_gate_result(record)

        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])

    def test_valid_pre_action_gate_result_is_created(self):
        record = self._valid_result()
        validation = validate_pre_action_consideration_gate_result(record)

        self.assertTrue(validation["valid"])
        self.assertEqual(record["gate_status"], "passed_for_action_selection_adjacent_review")
        self.assertEqual(len(record["gated_candidates"]), 3)

    def test_valid_gate_reuses_candidate_result_and_safety_envelope(self):
        candidate_result = build_pre_action_consideration_candidates()
        safety_envelope = build_runtime_tendency_memory_influence_safety_envelope()
        record = build_pre_action_consideration_gate_result(candidate_result, safety_envelope)

        self.assertEqual(record["source_pre_action_candidate_result_id"], candidate_result["pre_action_candidate_result_id"])
        self.assertEqual(record["source_safety_envelope_id"], safety_envelope["safety_envelope_id"])
        self.assertTrue(record["gate_checks"]["candidate_result_valid"])
        self.assertTrue(record["gate_checks"]["safety_envelope_valid"])

    def test_expected_candidate_mappings_pass_gate(self):
        self.assertEqual(
            self._candidate("obstacle_retry_failed_same_state")["considered_action"],
            "check_before_retry",
        )
        self.assertEqual(
            self._candidate("costly_retry_same_state")["considered_action"],
            "slow_down_or_reduce_cost",
        )
        self.assertEqual(
            self._candidate("unclear_failure_same_state")["considered_action"],
            "ask_for_help",
        )

    def test_gated_candidates_allowed_only_for_adjacent_review(self):
        for candidate in self._valid_result()["gated_candidates"]:
            with self.subTest(candidate=candidate["scenario_id"]):
                self.assertTrue(candidate["gate_passed"])
                self.assertTrue(candidate["allowed_for_action_selection_adjacent_review"])
                self.assertFalse(candidate["allowed_for_runtime_action_selection"])
                self.assertFalse(candidate["allowed_for_final_action"])
                self.assertFalse(candidate["allowed_for_action_execution"])

    def test_all_gate_checks_true(self):
        for field, value in self._valid_result()["gate_checks"].items():
            with self.subTest(field=field):
                self.assertTrue(value)

    def test_allowed_next_layer_blocks_runtime_paths(self):
        allowed = self._valid_result()["allowed_next_layer"]

        self.assertTrue(allowed["may_enter_action_selection_adjacent_review"])
        self.assertFalse(allowed["may_enter_runtime_action_selection"])
        self.assertFalse(allowed["may_create_final_action"])
        self.assertFalse(allowed["may_execute_action"])
        self.assertFalse(allowed["may_create_direct_command"])
        self.assertFalse(allowed["may_write_persistent_policy"])

    def test_bad_gate_status_blocks(self):
        record = self._valid_result()
        record["gate_status"] = "runtime_action_selection_ready"
        self._assert_invalid(record, "gate_status_not_passed_for_action_selection_adjacent_review")

    def test_wrong_mapping_blocks(self):
        record = self._valid_result()
        record["gated_candidates"][0]["considered_action"] = "ask_for_help"
        self._assert_invalid(record, "obstacle_retry_failed_same_state_wrong_considered_action")

    def test_gate_passed_false_blocks(self):
        record = self._valid_result()
        record["gated_candidates"][0]["gate_passed"] = False
        self._assert_invalid(record, "gate_passed_not_true")

    def test_gated_candidate_runtime_permissions_block(self):
        cases = {
            "allowed_for_runtime_action_selection": "allowed_for_runtime_action_selection_not_false",
            "allowed_for_final_action": "allowed_for_final_action_not_false",
            "allowed_for_action_execution": "allowed_for_action_execution_not_false",
        }
        for field, error_code in cases.items():
            with self.subTest(field=field):
                record = self._valid_result()
                record["gated_candidates"][0][field] = True
                self._assert_invalid(record, error_code)

    def test_gate_check_false_blocks(self):
        cases = [
            "candidate_result_valid",
            "safety_envelope_valid",
            "rollback_verified",
            "mentor_override_available",
            "exploration_allowed",
            "audit_trace_required",
            "no_final_action_gate",
            "no_action_execution_gate",
        ]
        for field in cases:
            with self.subTest(field=field):
                record = self._valid_result()
                record["gate_checks"][field] = False
                self._assert_invalid(record, f"{field}_not_true")

    def test_allowed_next_layer_true_runtime_paths_block(self):
        cases = {
            "may_enter_runtime_action_selection": "may_enter_runtime_action_selection_not_false",
            "may_create_final_action": "may_create_final_action_not_false",
            "may_execute_action": "may_execute_action_not_false",
            "may_create_direct_command": "may_create_direct_command_not_false",
            "may_write_persistent_policy": "may_write_persistent_policy_not_false",
        }
        for field, error_code in cases.items():
            with self.subTest(field=field):
                record = self._valid_result()
                record["allowed_next_layer"][field] = True
                self._assert_invalid(record, error_code)

    def test_empty_human_summary_fields_block(self):
        cases = {
            "why_it_passed": "why_it_passed_empty_or_not_string",
            "plain_result": "plain_result_empty_or_not_string",
        }
        for field, error_code in cases.items():
            with self.subTest(field=field):
                record = self._valid_result()
                record["human_summary"][field] = ""
                self._assert_invalid(record, error_code)

    def test_blocked_flags_true_block(self):
        cases = {
            "production_action_selection": "production_action_selection_enabled",
            "runtime_action_selection": "runtime_action_selection_enabled",
            "final_action_created": "final_action_created_enabled",
            "action_selected": "action_selected_enabled",
            "action_executed": "action_executed_enabled",
            "direct_action_command": "direct_action_command_enabled",
            "real_navigation_changed": "real_navigation_changed_enabled",
            "ui_behavior_changed": "ui_behavior_changed_enabled",
            "persistent_policy_written": "persistent_policy_written_enabled",
            "general_behavior_changed": "general_behavior_changed_enabled",
            "semantic_or_fuzzy_match_used": "semantic_or_fuzzy_match_used_enabled",
            "exploration_blocked": "exploration_blocked_enabled",
            "curiosity_overridden": "curiosity_overridden_enabled",
            "mentor_override_blocked": "mentor_override_blocked_enabled",
            "lesson_applied": "lesson_applied_enabled",
            "memory_write": "memory_write_enabled",
            "new_retention_written": "new_retention_written_enabled",
            "predictor_modified": "predictor_modified_enabled",
            "proof_of_learning_claim": "proof_of_learning_claim_enabled",
        }
        for flag, error_code in cases.items():
            with self.subTest(flag=flag):
                record = self._valid_result()
                record["blocked_flags"][flag] = True
                self._assert_invalid(record, error_code)

    def test_demo_summary_counts_are_deterministic(self):
        result = run_pre_action_consideration_gate_check_minimal_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-pre-action-consideration-gate-check-minimal-check")
        self.assertEqual(result["flow"], "pre_action_consideration_gate_check_minimal_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["pre_action_gate_result_count"], 53)
        self.assertEqual(summary["valid_pre_action_gate_result_count"], 1)
        self.assertEqual(summary["invalid_pre_action_gate_result_count"], 52)
        self.assertEqual(summary["gated_candidate_count"], 3)
        self.assertEqual(summary["gate_passed_candidate_count"], 3)
        self.assertEqual(summary["allowed_for_action_selection_adjacent_review_count"], 3)
        self.assertEqual(summary["runtime_action_selection_blocked_count"], 1)
        self.assertEqual(summary["final_action_blocked_count"], 1)
        self.assertEqual(summary["action_execution_blocked_count"], 1)
        self.assertEqual(summary["direct_command_blocked_count"], 1)
        self.assertEqual(summary["persistent_policy_blocked_count"], 1)
        self.assertEqual(summary["candidate_result_valid_count"], 1)
        self.assertEqual(summary["safety_envelope_valid_count"], 1)
        self.assertEqual(summary["rollback_verified_count"], 1)
        self.assertEqual(summary["mentor_override_available_count"], 1)
        self.assertEqual(summary["exploration_allowed_count"], 1)
        self.assertEqual(summary["audit_trace_required_count"], 1)
        self.assertEqual(summary["bad_gate_status_blocked_count"], 1)
        self.assertEqual(summary["wrong_mapping_blocked_count"], 3)
        self.assertEqual(summary["gate_passed_false_blocked_count"], 1)
        self.assertEqual(summary["runtime_action_selection_allowed_blocked_count"], 1)
        self.assertEqual(summary["final_action_allowed_blocked_count"], 1)
        self.assertEqual(summary["action_execution_allowed_blocked_count"], 1)
        self.assertEqual(summary["production_action_selection_blocked_count"], 1)
        self.assertEqual(summary["runtime_action_selection_flag_blocked_count"], 1)
        self.assertEqual(summary["final_action_created_blocked_count"], 1)
        self.assertEqual(summary["action_selected_blocked_count"], 1)
        self.assertEqual(summary["action_executed_blocked_count"], 1)
        self.assertEqual(summary["direct_action_command_blocked_count"], 1)
        self.assertEqual(summary["persistent_policy_written_blocked_count"], 1)
        self.assertEqual(summary["proof_of_learning_claim_blocked_count"], 1)
        self.assertEqual(boundary["gated_candidate_count"], 3)
        self.assertFalse(boundary["runtime_action_selection_added"])
        self.assertFalse(boundary["final_action_creation_added"])
        self.assertFalse(boundary["action_selection_added"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-pre-action-consideration-gate-check-minimal-check")

        self.assertEqual(result["command"], "run-pre-action-consideration-gate-check-minimal-check")
        self.assertEqual(result["summary"]["valid_pre_action_gate_result_count"], 1)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-pre-action-consideration-gate-check-minimal-check",
            ],
            check=True,
            capture_output=True,
            encoding="utf-8",
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-pre-action-consideration-gate-check-minimal-check")
        self.assertEqual(result["summary"]["gated_candidate_count"], 3)


if __name__ == "__main__":
    unittest.main()
