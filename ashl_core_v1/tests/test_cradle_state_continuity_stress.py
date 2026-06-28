import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.runtime.state_continuity_stress import (
    load_last_state_continuity_stress,
    run_state_continuity_stress,
)


ROOT = Path(__file__).resolve().parents[2]
CLI_MODULE = "ashl_core_v1.runtime.state_continuity_stress_cli"


class CradleStateContinuityStressTests(unittest.TestCase):
    def run_cli(
        self,
        data_dir: Path,
        *args: str,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", CLI_MODULE, "--data-dir", str(data_dir), *args],
            cwd=ROOT,
            check=check,
            capture_output=True,
            text=True,
        )

    def test_run_stress_with_3_runs_completes_3_runs(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_state_continuity_stress(3, "basic", Path(temp_dir))

            self.assertEqual(3, result["runs_completed"])

    def test_daily_run_ids_and_session_ids_count_match_runs(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_state_continuity_stress(3, "basic", Path(temp_dir))

            self.assertEqual(3, len(result["daily_run_ids"]))
            self.assertEqual(3, len(result["session_ids"]))

    def test_turn_counts_are_all_positive(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_state_continuity_stress(3, "basic", Path(temp_dir))

            self.assertTrue(all(turn > 0 for turn in result["turn_counts"]))

    def test_history_counts_grow_and_persistence_present(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_state_continuity_stress(3, "basic", Path(temp_dir))

            self.assertGreaterEqual(result["session_history_count"], 3)
            self.assertGreaterEqual(result["daily_history_count"], 3)
            self.assertTrue(result["state_snapshot_present"])
            self.assertTrue(result["session_summary_present"])
            self.assertTrue(result["last_trace_summary_present"])

    def test_continuity_passed_true_for_normal_case(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_state_continuity_stress(3, "basic", Path(temp_dir))

            self.assertTrue(result["continuity_passed"])
            self.assertEqual([], result["mismatches"])

    def test_invalid_runs_value_returns_readable_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_cli(
                Path(temp_dir),
                "run-stress",
                "--runs",
                "0",
                "--case-set",
                "basic",
                check=False,
            )

            self.assertEqual(1, result.returncode)
            self.assertIn("not_found", result.stdout)

    def test_show_last_stress_returns_latest_result(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            result = run_state_continuity_stress(2, "basic", data_dir)

            self.assertEqual(result, load_last_state_continuity_stress(data_dir))

    def test_cli_run_stress_outputs_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_cli(
                Path(temp_dir),
                "run-stress",
                "--runs",
                "2",
                "--case-set",
                "basic",
            )
            payload = json.loads(result.stdout)

            self.assertEqual(2, payload["runs_completed"])
            self.assertTrue(payload["continuity_passed"])

    def test_repo_data_directory_is_not_polluted_during_tests(self):
        self.assertFalse((ROOT / "ashl_core_v1" / "data").exists())


if __name__ == "__main__":
    unittest.main()
