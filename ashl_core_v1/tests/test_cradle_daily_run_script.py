import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.runtime.daily_run import (
    DAILY_RUN_HISTORY_FILE,
    LAST_DAILY_RUN_FILE,
    load_last_daily_run,
    run_cradle_daily,
)


ROOT = Path(__file__).resolve().parents[2]
CLI_MODULE = "ashl_core_v1.runtime.daily_run_cli"


class CradleDailyRunScriptTests(unittest.TestCase):
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

    def test_run_daily_basic_runs_basic_case_set(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            daily_run = run_cradle_daily("basic", Path(temp_dir))

            self.assertEqual("basic", daily_run["case_set"])
            self.assertEqual(4, daily_run["case_count"])
            self.assertEqual(
                [
                    "blocked_front_obstacle",
                    "success_front_step",
                    "unknown_feedback",
                    "teacher_rejected",
                ],
                daily_run["case_ids"],
            )

    def test_run_daily_all_runs_all_case_set(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            daily_run = run_cradle_daily("all", Path(temp_dir))

            self.assertEqual("all", daily_run["case_set"])
            self.assertEqual(8, daily_run["case_count"])
            self.assertEqual(8, daily_run["turn_count"])

    def test_run_daily_creates_and_closes_session(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            daily_run = run_cradle_daily("basic", Path(temp_dir))

            self.assertEqual(4, daily_run["turn_count"])
            self.assertTrue(daily_run["session_id"])
            self.assertTrue(daily_run["closed_at"])

    def test_run_daily_writes_last_daily_run_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            daily_run = run_cradle_daily("basic", data_dir)

            self.assertTrue((data_dir / LAST_DAILY_RUN_FILE).is_file())
            self.assertEqual(daily_run, load_last_daily_run(data_dir))

    def test_run_daily_appends_daily_run_history_jsonl(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            run_cradle_daily("basic", data_dir)
            run_cradle_daily("basic", data_dir)

            lines = (data_dir / DAILY_RUN_HISTORY_FILE).read_text(encoding="utf-8").splitlines()
            self.assertEqual(2, len(lines))

    def test_run_daily_writes_daily_report(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            daily_run = run_cradle_daily("basic", Path(temp_dir))

            self.assertTrue(Path(daily_run["report_path"]).is_file())
            self.assertIn(
                "Daily cradle run completed",
                Path(daily_run["report_path"]).read_text(encoding="utf-8"),
            )

    def test_show_last_daily_returns_latest_run(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            daily_run = run_cradle_daily("basic", data_dir)

            result = self.run_cli(data_dir, "show-last-daily")
            payload = json.loads(result.stdout)

            self.assertEqual(daily_run["daily_run_id"], payload["daily_run_id"])

    def test_cli_run_daily_all_outputs_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_cli(Path(temp_dir), "run-daily", "--case-set", "all")
            payload = json.loads(result.stdout)

            self.assertEqual("all", payload["case_set"])
            self.assertEqual(8, payload["case_count"])

    def test_show_last_daily_missing_returns_readable_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_cli(Path(temp_dir), "show-last-daily", check=False)

            self.assertEqual(1, result.returncode)
            self.assertIn("not_found", result.stdout)

    def test_repo_data_directory_is_not_polluted_during_tests(self):
        self.assertFalse((ROOT / "ashl_core_v1" / "data").exists())


if __name__ == "__main__":
    unittest.main()
