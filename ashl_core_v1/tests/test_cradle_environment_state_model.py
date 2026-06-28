import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.environment.cradle_environment_state import (
    build_cradle_environment_state_from_case,
    build_cradle_environment_state_from_last_session,
    list_cradle_environment_states,
    load_last_cradle_environment_state,
    save_cradle_environment_state,
)
from ashl_core_v1.runtime.cradle_cases import list_cradle_case_ids
from ashl_core_v1.runtime.cradle_session import run_case_in_cradle_session, start_cradle_session


ROOT = Path(__file__).resolve().parents[2]
CLI_MODULE = "ashl_core_v1.environment.cradle_environment_state_cli"


class CradleEnvironmentStateModelTests(unittest.TestCase):
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

    def test_environment_state_can_be_built_for_every_cradle_case(self):
        for case_id in list_cradle_case_ids():
            with self.subTest(case_id=case_id):
                state = build_cradle_environment_state_from_case(case_id)
                self.assertEqual(case_id, state["case_id"])
                self.assertTrue(state["available_operations"])

    def test_blocked_front_obstacle_maps_to_blocked_obstacle(self):
        state = build_cradle_environment_state_from_case("blocked_front_obstacle")

        self.assertEqual("obstacle", state["front_state"]["kind"])
        self.assertTrue(state["front_state"]["blocked"])
        self.assertIn("observe", state["available_operations"])
        self.assertIn("wait", state["available_operations"])
        self.assertIn("adjust", state["available_operations"])

    def test_success_front_step_maps_to_open_front_state(self):
        state = build_cradle_environment_state_from_case("success_front_step")

        self.assertEqual("open", state["front_state"]["kind"])
        self.assertFalse(state["front_state"]["blocked"])
        self.assertIn("step_forward", state["available_operations"])

    def test_unknown_feedback_maps_to_unknown_front_state(self):
        state = build_cradle_environment_state_from_case("unknown_feedback")

        self.assertEqual("unknown", state["front_state"]["kind"])
        self.assertTrue(state["front_state"]["unknown"])
        self.assertIn("inspect", state["available_operations"])

    def test_review_limited_cases_map_to_review_limited_front_state(self):
        for case_id in ("teacher_rejected", "teacher_deferred", "conflict_detected"):
            with self.subTest(case_id=case_id):
                state = build_cradle_environment_state_from_case(case_id)
                self.assertEqual("review_limited", state["front_state"]["kind"])
                self.assertIn("wait", state["available_operations"])

    def test_stale_and_superseded_map_to_outdated_trace_front_state(self):
        for case_id in ("stale_learning", "superseded_learning"):
            with self.subTest(case_id=case_id):
                state = build_cradle_environment_state_from_case(case_id)
                self.assertEqual("outdated_trace", state["front_state"]["kind"])
                self.assertIn("inspect", state["available_operations"])

    def test_save_load_and_list_states_work(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            state = build_cradle_environment_state_from_case("blocked_front_obstacle")

            saved = save_cradle_environment_state(state, data_dir)

            self.assertEqual(saved, load_last_cradle_environment_state(data_dir))
            self.assertEqual(1, list_cradle_environment_states(data_dir)["state_count"])

    def test_build_from_last_session_uses_last_case(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            session = start_cradle_session(data_dir)
            run_case_in_cradle_session("success_front_step", data_dir)

            state = build_cradle_environment_state_from_last_session(data_dir)

            self.assertEqual("success_front_step", state["case_id"])
            self.assertEqual(session["session_id"], state["session_id"])
            self.assertEqual(1, state["turn"])

    def test_missing_case_id_returns_readable_not_found(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_cli(
                Path(temp_dir),
                "build-from-case",
                "--case-id",
                "missing",
                check=False,
            )

            self.assertEqual(1, result.returncode)
            self.assertIn("not_found", result.stdout)

    def test_cli_build_from_case_and_show_last_state(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            result = self.run_cli(data_dir, "build-from-case", "--case-id", "unknown_feedback")
            payload = json.loads(result.stdout)
            latest = json.loads(self.run_cli(data_dir, "show-last-state").stdout)

            self.assertEqual("unknown_feedback", payload["case_id"])
            self.assertEqual(payload["environment_state_id"], latest["environment_state_id"])

    def test_repo_data_directory_is_not_polluted_during_tests(self):
        self.assertFalse((ROOT / "ashl_core_v1" / "data").exists())


if __name__ == "__main__":
    unittest.main()
