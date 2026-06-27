import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.runtime.cradle_session import (
    CURRENT_SESSION_FILE,
    SESSION_HISTORY_FILE,
    close_cradle_session,
    list_cradle_session_history,
    load_current_cradle_session,
    run_case_in_cradle_session,
    start_cradle_session,
)
from ashl_core_v1.runtime.session_persistence import (
    LAST_TRACE_SUMMARY_FILE,
    SESSION_SUMMARY_FILE,
    STATE_SNAPSHOT_FILE,
)


ROOT = Path(__file__).resolve().parents[2]
CLI_MODULE = "ashl_core_v1.runtime.cradle_session_cli"


class CradleSessionStartCloseTests(unittest.TestCase):
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

    def test_start_creates_active_session(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)

            session = start_cradle_session(data_dir)

            self.assertEqual("active", session["status"])
            self.assertEqual(0, session["turn_count"])
            self.assertEqual([], session["case_history"])
            self.assertTrue((data_dir / CURRENT_SESSION_FILE).is_file())

    def test_show_session_returns_active_session(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            start_cradle_session(data_dir)

            result = self.run_cli(data_dir, "show-session")
            session = json.loads(result.stdout)

            self.assertEqual("active", session["status"])

    def test_run_case_requires_active_session(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_cli(
                Path(temp_dir),
                "run-case",
                "--case-id",
                "blocked_front_obstacle",
                check=False,
            )

            self.assertEqual(1, result.returncode)
            self.assertIn("not_found", result.stdout)

    def test_run_case_increments_turn_count_and_appends_history(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            start_cradle_session(data_dir)

            session = run_case_in_cradle_session("blocked_front_obstacle", data_dir)

            self.assertEqual(1, session["turn_count"])
            self.assertEqual(1, len(session["case_history"]))
            self.assertEqual("blocked_front_obstacle", session["last_case_id"])
            self.assertEqual("routed", session["last_cycle_summary"]["routing_status"])

    def test_run_case_updates_persistence_summaries(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            start_cradle_session(data_dir)

            run_case_in_cradle_session("blocked_front_obstacle", data_dir)
            persistence_dir = data_dir / "session_persistence"

            self.assertTrue((persistence_dir / STATE_SNAPSHOT_FILE).is_file())
            self.assertTrue((persistence_dir / SESSION_SUMMARY_FILE).is_file())
            self.assertTrue((persistence_dir / LAST_TRACE_SUMMARY_FILE).is_file())

    def test_close_session_closes_active_session_and_appends_history(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            start_cradle_session(data_dir)
            run_case_in_cradle_session("blocked_front_obstacle", data_dir)

            session = close_cradle_session(data_dir)
            history = list_cradle_session_history(data_dir)

            self.assertEqual("closed", session["status"])
            self.assertTrue(session["closed_at"])
            self.assertEqual(1, len(history))
            self.assertEqual(session["session_id"], history[0]["session_id"])
            self.assertTrue((data_dir / SESSION_HISTORY_FILE).is_file())

    def test_run_case_after_close_is_rejected_with_readable_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            start_cradle_session(data_dir)
            close_cradle_session(data_dir)

            result = self.run_cli(
                data_dir,
                "run-case",
                "--case-id",
                "blocked_front_obstacle",
                check=False,
            )

            self.assertEqual(1, result.returncode)
            self.assertIn("active cradle session not found", result.stdout)

    def test_cli_start_run_close_round_trip(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)

            self.run_cli(data_dir, "start-session")
            run_result = self.run_cli(data_dir, "run-case", "--case-id", "success_front_step")
            close_result = self.run_cli(data_dir, "close-session")

            self.assertEqual(1, json.loads(run_result.stdout)["turn_count"])
            self.assertEqual("closed", json.loads(close_result.stdout)["status"])

    def test_load_current_cradle_session_returns_none_when_missing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.assertIsNone(load_current_cradle_session(Path(temp_dir)))

    def test_repo_data_directory_is_not_polluted_during_tests(self):
        self.assertFalse((ROOT / "ashl_core_v1" / "data").exists())


if __name__ == "__main__":
    unittest.main()
