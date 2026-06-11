import json
import subprocess
import sys
import unittest

from ashl_core.runtime_tendency_memory_influence_rollback_check_minimal import (
    build_runtime_tendency_memory_influence_rollback_result,
)
from ashl_core.runtime_tendency_memory_influence_safety_envelope_minimal import (
    build_runtime_tendency_memory_influence_safety_envelope,
    run_runtime_tendency_memory_influence_safety_envelope_minimal_check,
    validate_runtime_tendency_memory_influence_safety_envelope,
)
from ashl_core.teaching_cli import run_command


class RuntimeTendencyMemoryInfluenceSafetyEnvelopeMinimalTests(unittest.TestCase):
    def _valid_envelope(self):
        return build_runtime_tendency_memory_influence_safety_envelope()

    def _assert_invalid(self, record, error_code):
        validation = validate_runtime_tendency_memory_influence_safety_envelope(record)

        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])

    def test_valid_safety_envelope_is_created(self):
        record = self._valid_envelope()
        validation = validate_runtime_tendency_memory_influence_safety_envelope(record)

        self.assertTrue(validation["valid"])
        self.assertEqual(
            set(record),
            {
                "safety_envelope_id",
                "source_rollback_result_id",
                "scope",
                "limits",
                "required_guards",
                "allowed_future_use",
                "human_summary",
                "blocked_flags",
            },
        )

    def test_valid_safety_envelope_reuses_rollback_result(self):
        rollback = build_runtime_tendency_memory_influence_rollback_result()
        record = build_runtime_tendency_memory_influence_safety_envelope(rollback)

        self.assertEqual(record["source_rollback_result_id"], rollback["rollback_result_id"])
        self.assertTrue(record["required_guards"]["rollback_verified"])
        self.assertTrue(record["required_guards"]["dirty_state_absent"])
        self.assertTrue(record["required_guards"]["persistent_influence_absent"])

    def test_scope_requirements_are_enforced(self):
        cases = {
            "runtime_tendency_only": "runtime_tendency_only_not_true",
            "controlled_runner_only": "controlled_runner_only_not_true",
            "same_state_same_candidates_required": "same_state_same_candidates_required_not_true",
            "exact_key_memory_signal_only": "exact_key_memory_signal_only_not_true",
        }
        for field, error_code in cases.items():
            with self.subTest(field=field):
                record = self._valid_envelope()
                record["scope"][field] = False
                self._assert_invalid(record, error_code)

    def test_production_action_selection_allowed_false_required(self):
        record = self._valid_envelope()
        record["scope"]["production_action_selection_allowed"] = True
        self._assert_invalid(record, "production_action_selection_allowed_not_false")

    def test_limit_requirements_are_enforced(self):
        cases = {
            "one_step_evaluation_only": "one_step_evaluation_only_not_true",
            "no_persistent_influence": "no_persistent_influence_not_true",
            "rollback_required": "rollback_required_not_true",
        }
        for field, error_code in cases.items():
            with self.subTest(field=field):
                record = self._valid_envelope()
                record["limits"][field] = False
                self._assert_invalid(record, error_code)

    def test_max_absolute_delta_limit_required(self):
        record = self._valid_envelope()
        record["limits"]["max_absolute_delta"] = 0.11
        self._assert_invalid(record, "max_absolute_delta_too_high")

    def test_required_guards_are_enforced(self):
        cases = {
            "rollback_verified": "rollback_verified_not_true",
            "dirty_state_absent": "dirty_state_absent_not_true",
            "persistent_influence_absent": "persistent_influence_absent_not_true",
            "mentor_override_available": "mentor_override_available_not_true",
            "exploration_allowed": "exploration_allowed_not_true",
            "audit_trace_required": "audit_trace_required_not_true",
            "no_final_action_gate": "no_final_action_gate_not_true",
            "no_action_execution_gate": "no_action_execution_gate_not_true",
        }
        for field, error_code in cases.items():
            with self.subTest(field=field):
                record = self._valid_envelope()
                record["required_guards"][field] = False
                self._assert_invalid(record, error_code)

    def test_allowed_future_use_requirements_are_enforced(self):
        record = self._valid_envelope()
        record["allowed_future_use"]["may_feed_pre_action_consideration_design"] = False
        self._assert_invalid(record, "may_feed_pre_action_consideration_design_not_true")

        false_required = {
            "may_feed_runtime_action_selection": "may_feed_runtime_action_selection_not_false",
            "may_create_final_action": "may_create_final_action_not_false",
            "may_execute_action": "may_execute_action_not_false",
            "may_write_policy": "may_write_policy_not_false",
        }
        for field, error_code in false_required.items():
            with self.subTest(field=field):
                record = self._valid_envelope()
                record["allowed_future_use"][field] = True
                self._assert_invalid(record, error_code)

    def test_empty_human_summary_fields_block(self):
        cases = {
            "what_is_allowed": "what_is_allowed_empty_or_not_string",
            "what_is_required": "what_is_required_empty_or_not_string",
            "what_is_blocked": "what_is_blocked_empty_or_not_string",
            "plain_result": "plain_result_empty_or_not_string",
        }
        for field, error_code in cases.items():
            with self.subTest(field=field):
                record = self._valid_envelope()
                record["human_summary"][field] = ""
                self._assert_invalid(record, error_code)

    def test_blocked_flags_true_block(self):
        cases = {
            "production_action_selection": "production_action_selection_enabled",
            "final_action_created": "final_action_created_enabled",
            "action_executed": "action_executed_enabled",
            "direct_action_command": "direct_action_command_enabled",
            "real_navigation_changed": "real_navigation_changed_enabled",
            "ui_behavior_changed": "ui_behavior_changed_enabled",
            "persistent_policy_written": "persistent_policy_written_enabled",
            "general_behavior_changed": "general_behavior_changed_enabled",
            "dirty_state_allowed": "dirty_state_allowed_enabled",
            "persistent_influence_allowed": "persistent_influence_allowed_enabled",
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
                record = self._valid_envelope()
                record["blocked_flags"][flag] = True
                self._assert_invalid(record, error_code)

    def test_demo_summary_counts_are_deterministic(self):
        result = run_runtime_tendency_memory_influence_safety_envelope_minimal_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-runtime-tendency-memory-influence-safety-envelope-minimal-check")
        self.assertEqual(result["flow"], "runtime_tendency_memory_influence_safety_envelope_minimal_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["safety_envelope_count"], 44)
        self.assertEqual(summary["valid_safety_envelope_count"], 1)
        self.assertEqual(summary["invalid_safety_envelope_count"], 43)
        self.assertEqual(summary["rollback_verified_count"], 1)
        self.assertEqual(summary["dirty_state_absent_count"], 1)
        self.assertEqual(summary["persistent_influence_absent_count"], 1)
        self.assertEqual(summary["mentor_override_available_count"], 1)
        self.assertEqual(summary["exploration_allowed_count"], 1)
        self.assertEqual(summary["runtime_selection_blocked_count"], 1)
        self.assertEqual(summary["final_action_blocked_count"], 1)
        self.assertEqual(summary["action_execution_blocked_count"], 1)
        self.assertEqual(summary["policy_write_blocked_count"], 1)
        self.assertEqual(summary["max_absolute_delta_violation_blocked_count"], 1)
        self.assertEqual(summary["production_action_selection_blocked_count"], 1)
        self.assertEqual(summary["final_action_created_blocked_count"], 1)
        self.assertEqual(summary["action_executed_blocked_count"], 1)
        self.assertEqual(summary["direct_action_command_blocked_count"], 1)
        self.assertEqual(summary["real_navigation_changed_blocked_count"], 1)
        self.assertEqual(summary["ui_behavior_changed_blocked_count"], 1)
        self.assertEqual(summary["persistent_policy_written_blocked_count"], 1)
        self.assertEqual(summary["general_behavior_changed_blocked_count"], 1)
        self.assertEqual(summary["dirty_state_allowed_blocked_count"], 1)
        self.assertEqual(summary["persistent_influence_allowed_blocked_count"], 1)
        self.assertEqual(summary["exploration_blocked_count"], 1)
        self.assertEqual(summary["curiosity_overridden_blocked_count"], 1)
        self.assertEqual(summary["mentor_override_blocked_count"], 1)
        self.assertEqual(summary["lesson_applied_blocked_count"], 1)
        self.assertEqual(summary["memory_write_blocked_count"], 1)
        self.assertEqual(summary["new_retention_written_blocked_count"], 1)
        self.assertEqual(summary["predictor_modified_blocked_count"], 1)
        self.assertEqual(summary["proof_of_learning_claim_blocked_count"], 1)
        self.assertTrue(boundary["controlled_runner_scope_required"])
        self.assertTrue(boundary["same_state_same_candidates_required"])
        self.assertTrue(boundary["exact_key_memory_signal_only"])
        self.assertEqual(boundary["max_absolute_delta"], 0.10)
        self.assertTrue(boundary["rollback_verified"])
        self.assertTrue(boundary["dirty_state_absent"])
        self.assertTrue(boundary["persistent_influence_absent"])
        self.assertTrue(boundary["mentor_override_available"])
        self.assertTrue(boundary["exploration_allowed"])
        self.assertTrue(boundary["audit_trace_required"])
        self.assertTrue(boundary["no_final_action_gate"])
        self.assertTrue(boundary["no_action_execution_gate"])
        self.assertFalse(boundary["runtime_action_selection_added"])
        self.assertFalse(boundary["final_action_creation_added"])
        self.assertFalse(boundary["action_execution_added"])
        self.assertFalse(boundary["direct_action_command_added"])
        self.assertFalse(boundary["persistent_policy_write_added"])
        self.assertFalse(boundary["general_behavior_change_added"])
        self.assertFalse(boundary["proof_of_learning_claimed"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-runtime-tendency-memory-influence-safety-envelope-minimal-check")

        self.assertEqual(result["command"], "run-runtime-tendency-memory-influence-safety-envelope-minimal-check")
        self.assertEqual(result["summary"]["valid_safety_envelope_count"], 1)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-runtime-tendency-memory-influence-safety-envelope-minimal-check",
            ],
            check=True,
            capture_output=True,
            encoding="utf-8",
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-runtime-tendency-memory-influence-safety-envelope-minimal-check")
        self.assertEqual(result["summary"]["rollback_verified_count"], 1)


if __name__ == "__main__":
    unittest.main()
