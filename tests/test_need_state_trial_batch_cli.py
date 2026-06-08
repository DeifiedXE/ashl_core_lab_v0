import json
import subprocess
import sys
import unittest

from ashl_core.teaching_cli import run_need_state_trial_batch_cli


class NeedStateTrialBatchCliTests(unittest.TestCase):
    def test_need_state_trial_batch_cli_command_exists(self):
        process = subprocess.run(
            [sys.executable, "-m", "ashl_core.teaching_cli", "--help"],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        self.assertIn("run-need-state-trial-batch", process.stdout)

    def test_need_state_trial_batch_cli_default_returns_ok_summary(self):
        result = run_need_state_trial_batch_cli(random_seed=0)

        self.assertEqual(result["flow"], "need_state_trial_batch_cli_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["trial_count"], 5)
        self.assertEqual(len(result["step_counts"]), 5)
        self.assertEqual(len(result["trials"]), 5)
        self.assertIn("average_step_count", result)
        self.assertIn("min_step_count", result)
        self.assertIn("max_step_count", result)

    def test_need_state_trial_batch_cli_accepts_trial_count(self):
        result = run_need_state_trial_batch_cli(trial_count=3, max_steps=4, random_seed=2)

        self.assertEqual(result["trial_count"], 3)
        self.assertEqual(len(result["step_counts"]), 3)
        self.assertEqual(len(result["trials"]), 3)

    def test_need_state_trial_batch_cli_random_seed_is_reproducible(self):
        first = run_need_state_trial_batch_cli(trial_count=3, max_steps=8, random_seed=17)
        second = run_need_state_trial_batch_cli(trial_count=3, max_steps=8, random_seed=17)

        self.assertEqual(first, second)

    def test_need_state_trial_batch_cli_boundary_flags_are_false(self):
        result = run_need_state_trial_batch_cli()
        boundary = result["boundary"]

        self.assertIs(boundary["llm_used"], False)
        self.assertIs(boundary["creates_lesson_candidate"], False)
        self.assertIs(boundary["writes_lesson_store"], False)
        self.assertIs(boundary["writes_memory_layer"], False)
        self.assertIs(boundary["awakening_claim"], False)

    def test_module_cli_need_state_trial_batch_default_outputs_json(self):
        process = subprocess.run(
            [sys.executable, "-m", "ashl_core.teaching_cli", "run-need-state-trial-batch"],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        result = json.loads(process.stdout)

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["trial_count"], 5)
        self.assertEqual(len(result["step_counts"]), 5)
        self.assertIn("average_step_count", result)

    def test_module_cli_need_state_trial_batch_outputs_json(self):
        process = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-need-state-trial-batch",
                "--trial-count",
                "3",
                "--random-seed",
                "17",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        result = json.loads(process.stdout)

        self.assertEqual(result["command"], "run-need-state-trial-batch")
        self.assertEqual(result["flow"], "need_state_trial_batch_cli_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["trial_count"], 3)
        self.assertEqual(len(result["step_counts"]), 3)
        self.assertIs(result["boundary"]["llm_used"], False)


if __name__ == "__main__":
    unittest.main()
