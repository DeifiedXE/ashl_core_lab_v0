import json
import subprocess
import sys
import unittest

from ashl_core.phase0_level1_first_contact_danger_minimal import (
    build_phase0_level1_first_contact_danger_result,
    run_phase0_level1_first_contact_danger_minimal_check,
    validate_phase0_level1_first_contact_danger_result,
)
from ashl_core.teaching_cli import run_command


class Phase0Level1FirstContactDangerMinimalTests(unittest.TestCase):
    def _result(self):
        return build_phase0_level1_first_contact_danger_result()

    def _assert_invalid(self, record, error_code):
        validation = validate_phase0_level1_first_contact_danger_result(record)
        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])

    def test_valid_level1_result_is_created(self):
        result = self._result()
        validation = validate_phase0_level1_first_contact_danger_result(result)

        self.assertTrue(validation["valid"])
        self.assertEqual(result["level_info"]["level_id"], "phase0_level1_first_contact_danger")

    def test_level_id_and_fixture_are_correct(self):
        result = self._result()
        info = result["level_info"]
        fixture = result["map_fixture"]

        self.assertEqual(info["level_id"], "phase0_level1_first_contact_danger")
        self.assertEqual(info["level_mode"], "one_step_symbolic_sandbox_level")
        self.assertFalse(info["pathfinding_required"])
        self.assertFalse(info["goal_reach_required"])
        self.assertEqual(fixture["map_size"], [5, 5])
        self.assertEqual(fixture["agent_position"], [0, 0])
        self.assertEqual(fixture["facing"], "east")
        self.assertEqual(fixture["front_cell_position"], [1, 0])
        self.assertEqual(fixture["front_symbol"], "d")
        self.assertFalse(fixture["goal_used_in_v0"])

    def test_symbol_detection_is_fixture_only(self):
        detection = self._result()["symbol_detection"]

        self.assertTrue(detection["front_symbol_checked"])
        self.assertEqual(detection["front_symbol"], "d")
        self.assertTrue(detection["danger_ahead"])
        self.assertTrue(detection["symbol_fixture_only"])
        self.assertFalse(detection["object_recognition"])
        self.assertFalse(detection["semantic_vision"])

    def test_action_path_executes_check_before_retry_once(self):
        action_path = self._result()["action_path"]

        self.assertEqual(action_path["candidate_action"], "check_before_retry")
        self.assertTrue(action_path["choice_candidate_used"])
        self.assertTrue(action_path["sandbox_intent_created"])
        self.assertTrue(action_path["sandbox_action_executed"])
        self.assertEqual(action_path["executed_sandbox_action"], "check_before_retry")
        self.assertFalse(action_path["production_action_selection"])
        self.assertFalse(action_path["final_action_created"])

    def test_sandbox_outcome_is_successful_danger_check(self):
        outcome = self._result()["sandbox_outcome"]

        self.assertTrue(outcome["checked_before_retry"])
        self.assertTrue(outcome["danger_detected"])
        self.assertTrue(outcome["obstacle_detected"])
        self.assertFalse(outcome["retry_same_action_executed"])
        self.assertFalse(outcome["movement_executed"])
        self.assertTrue(outcome["outcome_match"])
        self.assertTrue(outcome["sandbox_check_success"])
        self.assertEqual(outcome["state_mutation_scope"], "sandbox_record_only")

    def test_lesson_review_status_requires_human_review_without_writes(self):
        status = self._result()["lesson_review_status"]

        self.assertTrue(status["lesson_review_candidate_ready"])
        self.assertTrue(status["requires_human_review"])
        self.assertFalse(status["lesson_applied"])
        self.assertFalse(status["memory_write"])
        self.assertFalse(status["retention_write"])
        self.assertFalse(status["predictor_modified"])
        self.assertIn("check_before_retry", status["candidate_statement"])

    def test_wrong_symbol_blocks(self):
        result = self._result()
        result["map_fixture"]["front_symbol"] = "."
        self._assert_invalid(result, "front_symbol_not_d")

    def test_object_recognition_true_blocks(self):
        result = self._result()
        result["symbol_detection"]["object_recognition"] = True
        self._assert_invalid(result, "object_recognition_not_false")

    def test_semantic_vision_true_blocks(self):
        result = self._result()
        result["symbol_detection"]["semantic_vision"] = True
        self._assert_invalid(result, "semantic_vision_not_false")

    def test_pathfinding_true_blocks(self):
        result = self._result()
        result["level_info"]["pathfinding_required"] = True
        self._assert_invalid(result, "pathfinding_required_not_false")

    def test_goal_reach_claim_blocks(self):
        result = self._result()
        result["blocked_flags"]["goal_reached_claim"] = True
        self._assert_invalid(result, "goal_reached_claim_enabled")

    def test_movement_executed_true_blocks(self):
        result = self._result()
        result["sandbox_outcome"]["movement_executed"] = True
        self._assert_invalid(result, "movement_executed_not_false")

    def test_lesson_memory_retention_predictor_blocks(self):
        cases = {
            "lesson_applied": "lesson_applied_not_false",
            "memory_write": "memory_write_not_false",
            "retention_write": "retention_write_not_false",
            "predictor_modified": "predictor_modified_not_false",
        }
        for field, error_code in cases.items():
            with self.subTest(field=field):
                result = self._result()
                result["lesson_review_status"][field] = True
                self._assert_invalid(result, error_code)

    def test_blocked_flags_true_block(self):
        cases = {
            "pathfinding_performed": "pathfinding_performed_enabled",
            "goal_reached_claim": "goal_reached_claim_enabled",
            "object_recognition": "object_recognition_enabled",
            "semantic_vision": "semantic_vision_enabled",
            "production_action_selection": "production_action_selection_enabled",
            "runtime_action_selection": "runtime_action_selection_enabled",
            "selected_action_created": "selected_action_created_enabled",
            "final_action_created": "final_action_created_enabled",
            "direct_action_command": "direct_action_command_enabled",
            "real_navigation_changed": "real_navigation_changed_enabled",
            "ui_behavior_changed": "ui_behavior_changed_enabled",
            "persistent_policy_written": "persistent_policy_written_enabled",
            "general_behavior_changed": "general_behavior_changed_enabled",
            "lesson_applied": "lesson_applied_enabled",
            "memory_write": "memory_write_enabled",
            "retention_write": "retention_write_enabled",
            "new_retention_written": "new_retention_written_enabled",
            "predictor_modified": "predictor_modified_enabled",
            "proof_of_learning_claim": "proof_of_learning_claim_enabled",
        }
        for flag, error_code in cases.items():
            with self.subTest(flag=flag):
                result = self._result()
                result["blocked_flags"][flag] = True
                self._assert_invalid(result, error_code)

    def test_demo_summary_counts_are_deterministic(self):
        result = run_phase0_level1_first_contact_danger_minimal_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-phase0-level1-first-contact-danger-minimal-check")
        self.assertEqual(result["flow"], "phase0_level1_first_contact_danger_minimal_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["level1_result_count"], 63)
        self.assertEqual(summary["valid_level1_result_count"], 1)
        self.assertEqual(summary["invalid_level1_result_count"], 62)
        self.assertEqual(summary["danger_symbol_detected_count"], 1)
        self.assertEqual(summary["sandbox_action_executed_count"], 1)
        self.assertEqual(summary["check_before_retry_executed_count"], 1)
        self.assertEqual(summary["danger_detected_count"], 1)
        self.assertEqual(summary["movement_blocked_count"], 1)
        self.assertEqual(summary["outcome_match_count"], 1)
        self.assertEqual(summary["sandbox_check_success_count"], 1)
        self.assertEqual(summary["lesson_review_candidate_ready_count"], 1)
        self.assertEqual(summary["requires_human_review_count"], 1)
        self.assertFalse(boundary["pathfinding_added"])
        self.assertFalse(boundary["object_recognition_added"])
        self.assertFalse(boundary["lesson_application_added"])
        self.assertFalse(boundary["proof_of_learning_claimed"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-phase0-level1-first-contact-danger-minimal-check")

        self.assertEqual(result["command"], "run-phase0-level1-first-contact-danger-minimal-check")
        self.assertEqual(result["summary"]["valid_level1_result_count"], 1)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-phase0-level1-first-contact-danger-minimal-check",
            ],
            check=True,
            capture_output=True,
            encoding="utf-8",
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-phase0-level1-first-contact-danger-minimal-check")
        self.assertEqual(result["summary"]["danger_symbol_detected_count"], 1)


if __name__ == "__main__":
    unittest.main()
