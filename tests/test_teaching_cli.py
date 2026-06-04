import json
import subprocess
import sys
import unittest

from ashl_core.teaching_cli import run_disable_reenable_flow, run_known_flow, run_unknown_flow


class TeachingCliTests(unittest.TestCase):
    def test_teaching_cli_known_flow_succeeds(self):
        result = run_known_flow()

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["failure_reason"], "not_facing_east")
        self.assertIsNotNone(result["lesson"])
        self.assertEqual(result["generation_status"], "supported_failure_reason")
        self.assertEqual(result["behavior_before"], "failed")
        self.assertEqual(result["behavior_after"], "success")
        self.assertEqual(result["conflict_check"], "not_implemented")
        self.assertIn("Conflict check is not implemented", result["notes"][0])

    def test_teaching_cli_unknown_flow_matches_boundary_behavior(self):
        result = run_unknown_flow()

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["failure_reason"], "unmapped_obstacle_shadow")
        self.assertEqual(result["generation_status"], "unknown_failure_reason")
        self.assertIsNone(result["executable_action"])
        self.assertIsNone(result["lesson"])
        self.assertFalse(result["behavior_changed"])
        self.assertNotIn("turn(east)", str(result))

    def test_teaching_cli_disable_reenable_preserves_causal_control(self):
        result = run_disable_reenable_flow()

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["enabled_result"], "success")
        self.assertEqual(result["disabled_result"], "failed")
        self.assertEqual(result["reenabled_result"], "success")
        self.assertTrue(result["causality"]["summary"]["causal_control_passed"])

    def test_teaching_cli_does_not_add_new_generation_path(self):
        result = run_unknown_flow()

        self.assertIsNone(result["lesson"])
        self.assertIsNone(result["executable_action"])
        self.assertNotEqual(result["trace"]["source_failure_reason"], "not_facing_east")
        self.assertNotIn("turn(east)", str(result))

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


if __name__ == "__main__":
    unittest.main()
