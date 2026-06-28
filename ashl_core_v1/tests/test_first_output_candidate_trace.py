import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.output.first_output_candidate import (
    FIRST_OUTPUT_CANDIDATE_RECORDS_FILE,
    LAST_FIRST_OUTPUT_CANDIDATE_FILE,
    build_first_output_candidate_from_last_daily,
    build_first_output_candidate_from_replay,
    list_first_output_candidates,
    load_last_first_output_candidate,
    save_first_output_candidate,
)
from ashl_core_v1.runtime.daily_run import run_cradle_daily


ROOT = Path(__file__).resolve().parents[2]
CLI_MODULE = "ashl_core_v1.output.first_output_candidate_cli"


class FirstOutputCandidateTraceTests(unittest.TestCase):
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

    def replay_summary(self) -> dict:
        return {
            "session_id": "session_001",
            "case_count": 2,
            "case_sequence": ["blocked_front_obstacle", "success_front_step"],
            "influence_visible_count": 2,
        }

    def test_candidate_can_be_built_from_replay_summary(self):
        candidate = build_first_output_candidate_from_replay(self.replay_summary())

        self.assertEqual("session_replay", candidate["source_kind"])
        self.assertEqual("session_001", candidate["source_session_id"])
        self.assertTrue(candidate["candidate_id"])

    def test_candidate_includes_source_refs(self):
        candidate = build_first_output_candidate_from_replay(self.replay_summary())

        self.assertIn("session:session_001", candidate["trace_refs"])
        self.assertIn("case:blocked_front_obstacle", candidate["trace_refs"])

    def test_candidate_review_status_defaults_pending_teacher_review(self):
        candidate = build_first_output_candidate_from_replay(self.replay_summary())

        self.assertEqual("pending_teacher_review", candidate["review_status"])

    def test_candidate_output_kind_is_supported(self):
        candidate = build_first_output_candidate_from_replay(self.replay_summary())

        self.assertEqual("short_status_text", candidate["output_kind"])

    def test_candidate_output_payload_is_non_empty(self):
        candidate = build_first_output_candidate_from_replay(self.replay_summary())

        self.assertEqual("cradle_day_complete", candidate["output_payload"]["symbol"])
        self.assertTrue(candidate["output_payload"]["text"])

    def test_save_candidate_appends_jsonl_and_writes_last_candidate(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            candidate = build_first_output_candidate_from_replay(self.replay_summary())

            save_first_output_candidate(candidate, data_dir)

            self.assertTrue((data_dir / FIRST_OUTPUT_CANDIDATE_RECORDS_FILE).is_file())
            self.assertTrue((data_dir / LAST_FIRST_OUTPUT_CANDIDATE_FILE).is_file())
            self.assertEqual(1, len(list_first_output_candidates(data_dir)))

    def test_show_last_candidate_returns_latest(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            candidate = build_first_output_candidate_from_replay(self.replay_summary())
            save_first_output_candidate(candidate, data_dir)

            self.assertEqual(candidate, load_last_first_output_candidate(data_dir))

    def test_list_candidates_returns_records(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            save_first_output_candidate(build_first_output_candidate_from_replay(self.replay_summary()), data_dir)

            result = self.run_cli(data_dir, "list-candidates")
            payload = json.loads(result.stdout)

            self.assertEqual(1, len(payload["candidates"]))

    def test_build_from_last_daily_works_after_daily_run(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            daily_run = run_cradle_daily("basic", data_dir)

            candidate = build_first_output_candidate_from_last_daily(data_dir)

            self.assertEqual(daily_run["daily_run_id"], candidate["source_daily_run_id"])
            self.assertIn("daily_run_available", candidate["reason_codes"])

    def test_missing_daily_run_returns_readable_not_found(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_cli(Path(temp_dir), "build-from-last-daily", check=False)

            self.assertEqual(1, result.returncode)
            self.assertIn("not_found", result.stdout)

    def test_cli_build_from_last_daily_saves_candidate(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            run_cradle_daily("basic", data_dir)

            result = self.run_cli(data_dir, "build-from-last-daily")
            candidate = json.loads(result.stdout)

            self.assertEqual("pending_teacher_review", candidate["review_status"])
            self.assertIsNotNone(load_last_first_output_candidate(data_dir))

    def test_repo_data_directory_is_not_polluted_during_tests(self):
        self.assertFalse((ROOT / "ashl_core_v1" / "data").exists())


if __name__ == "__main__":
    unittest.main()
