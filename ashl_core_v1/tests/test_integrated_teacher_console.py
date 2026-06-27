import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.runtime.cradle_cases import list_cradle_case_ids
from ashl_core_v1.teacher_console.console import (
    build_teacher_console_status,
    teacher_console_close_session,
    teacher_console_list_cases,
    teacher_console_readiness,
    teacher_console_replay_current,
    teacher_console_replay_last_closed,
    teacher_console_run_all_cases,
    teacher_console_run_case,
    teacher_console_start_session,
)


ROOT = Path(__file__).resolve().parents[2]
CLI_MODULE = "ashl_core_v1.teacher_console.console_cli"


class IntegratedTeacherConsoleTests(unittest.TestCase):
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

    def test_status_works_with_no_session(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            status = build_teacher_console_status(Path(temp_dir))

            self.assertFalse(status["has_active_session"])
            self.assertIsNone(status["current_session_id"])
            self.assertEqual(0, status["turn_count"])
            self.assertIn("No current cradle session", status["human_readable_status"])

    def test_list_cases_returns_all_cradle_cases(self):
        result = teacher_console_list_cases()

        self.assertEqual(list(list_cradle_case_ids()), result["case_ids"])
        self.assertEqual(len(list_cradle_case_ids()), result["case_count"])

    def test_start_session_creates_active_session(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            session = teacher_console_start_session(Path(temp_dir))

            self.assertEqual("active", session["status"])
            self.assertEqual(0, session["turn_count"])

    def test_run_case_works_through_console(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            teacher_console_start_session(data_dir)

            session = teacher_console_run_case("blocked_front_obstacle", data_dir)

            self.assertEqual(1, session["turn_count"])
            self.assertEqual("blocked_front_obstacle", session["last_case_id"])

    def test_run_all_cases_works_through_console(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            teacher_console_start_session(data_dir)

            result = teacher_console_run_all_cases(data_dir)

            self.assertEqual(len(list_cradle_case_ids()), result["case_count"])
            self.assertEqual(list(list_cradle_case_ids()), result["case_ids"])
            self.assertEqual(len(list_cradle_case_ids()), result["current_session"]["turn_count"])

    def test_replay_current_works_through_console(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            teacher_console_start_session(data_dir)
            teacher_console_run_case("success_front_step", data_dir)

            replay = teacher_console_replay_current(data_dir)

            self.assertEqual(["success_front_step"], replay["case_sequence"])
            self.assertEqual(1, replay["case_count"])

    def test_close_session_works_through_console(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            teacher_console_start_session(data_dir)

            session = teacher_console_close_session(data_dir)

            self.assertEqual("closed", session["status"])

    def test_replay_last_closed_works_after_close(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            teacher_console_start_session(data_dir)
            teacher_console_run_case("unknown_feedback", data_dir)
            teacher_console_close_session(data_dir)

            replay = teacher_console_replay_last_closed(data_dir)

            self.assertEqual("closed", replay["status"])
            self.assertEqual(["unknown_feedback"], replay["case_sequence"])

    def test_readiness_works_through_console(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            readiness = teacher_console_readiness(Path(temp_dir))

            self.assertTrue(readiness["checked_capabilities"]["controlled_growth_minimum_ready"])
            self.assertFalse(readiness["checked_capabilities"]["daily_no_codex_ready"])

    def test_unknown_case_id_returns_readable_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.run_cli(data_dir, "start-session")

            result = self.run_cli(
                data_dir,
                "run-case",
                "--case-id",
                "missing_case",
                check=False,
            )
            payload = json.loads(result.stdout)

            self.assertEqual(1, result.returncode)
            self.assertEqual("not_found", payload["status"])
            self.assertIn("missing_case", payload["error"])

    def test_cli_status_outputs_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_cli(Path(temp_dir), "status")
            status = json.loads(result.stdout)

            self.assertIn("human_readable_status", status)
            self.assertEqual(len(list_cradle_case_ids()), status["case_count_available"])

    def test_optional_empty_store_commands_return_readable_results(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)

            for command, key in (
                ("list-pending", "pending_count"),
                ("show-reviewed", "reviewed_count"),
                ("list-corrections", "correction_count"),
                ("list-revokes", "revoke_count"),
            ):
                with self.subTest(command=command):
                    result = self.run_cli(data_dir, command)
                    payload = json.loads(result.stdout)
                    self.assertEqual(0, payload[key])

    def test_repo_data_directory_is_not_polluted_during_tests(self):
        self.assertFalse((ROOT / "ashl_core_v1" / "data").exists())


if __name__ == "__main__":
    unittest.main()
