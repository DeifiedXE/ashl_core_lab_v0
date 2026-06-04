import json
import subprocess
import sys
import unittest

from ashl_core.teaching_cli import (
    run_conflict_check_flow,
    run_disable_reenable_flow,
    run_known_flow,
    run_unknown_flow,
)


class TeachingCliTests(unittest.TestCase):
    def test_teaching_cli_known_flow_succeeds(self):
        result = run_known_flow()

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["failure_reason"], "not_facing_east")
        self.assertIsNotNone(result["lesson"])
        self.assertEqual(result["generation_status"], "supported_failure_reason")
        self.assertEqual(result["behavior_before"], "failed")
        self.assertEqual(result["behavior_after"], "success")
        self.assertTrue(result["conflict_check"]["implemented"])
        self.assertFalse(result["conflict_check"]["conflict_detected"])

    def test_teaching_cli_unknown_flow_matches_boundary_behavior(self):
        result = run_unknown_flow()

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["failure_reason"], "unmapped_obstacle_shadow")
        self.assertEqual(result["generation_status"], "unknown_failure_reason")
        self.assertIsNone(result["executable_action"])
        self.assertIsNone(result["lesson"])
        self.assertFalse(result["behavior_changed"])
        self.assertNotIn("turn(east)", str(result))
        self.assertTrue(result["conflict_check"]["implemented"])

    def test_teaching_cli_disable_reenable_preserves_causal_control(self):
        result = run_disable_reenable_flow()

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["enabled_result"], "success")
        self.assertEqual(result["disabled_result"], "failed")
        self.assertEqual(result["reenabled_result"], "success")
        self.assertTrue(result["causality"]["summary"]["causal_control_passed"])
        self.assertTrue(result["conflict_check"]["implemented"])

    def test_teaching_cli_does_not_add_new_generation_path(self):
        result = run_unknown_flow()

        self.assertIsNone(result["lesson"])
        self.assertIsNone(result["executable_action"])
        self.assertNotEqual(result["trace"]["source_failure_reason"], "not_facing_east")
        self.assertNotIn("turn(east)", str(result))

    def test_teaching_cli_conflict_check_reports_real_conflict(self):
        result = run_conflict_check_flow()
        conflict = result["conflict_check"]

        self.assertTrue(conflict["implemented"])
        self.assertTrue(conflict["conflict_detected"])
        self.assertEqual(conflict["conflict_resolution"], "require_review")
        self.assertTrue(conflict["review_required"])
        self.assertEqual(conflict["review_status"], "pending_human_review")
        self.assertEqual(conflict["conflicting_lesson_ids"], ["lesson_001", "lesson_002"])
        self.assertEqual(conflict["conflicting_actions"], ["turn(east)", "turn(west)"])
        self.assertIsNone(conflict["selected_action"])
        self.assertFalse(conflict["behavior_changed"])

    def test_module_cli_outputs_json(self):
        process = subprocess.run(
            [sys.executable, "-m", "ashl_core.teaching_cli", "run-unknown-flow"],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(process.stdout)

        self.assertEqual(result["command"], "run-unknown-flow")
        self.assertEqual(result["generation_status"], "unknown_failure_reason")

    def test_module_cli_conflict_flow_outputs_json(self):
        process = subprocess.run(
            [sys.executable, "-m", "ashl_core.teaching_cli", "run-conflict-check-flow"],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(process.stdout)

        self.assertEqual(result["command"], "run-conflict-check-flow")
        self.assertTrue(result["conflict_check"]["implemented"])
        self.assertTrue(result["conflict_check"]["conflict_detected"])


if __name__ == "__main__":
    unittest.main()
