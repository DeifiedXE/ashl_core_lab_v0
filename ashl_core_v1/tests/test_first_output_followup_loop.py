import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.output.first_output_candidate import (
    build_first_output_candidate_from_replay,
    save_first_output_candidate,
)
from ashl_core_v1.output.first_output_followup import (
    ALLOWED_FOLLOWUP_KINDS,
    follow_first_output,
    follow_last_first_output,
    list_first_output_followups,
    load_last_first_output_followup,
)
from ashl_core_v1.output.first_output_promotion import (
    list_first_output_records,
    promote_last_approved_first_output,
)
from ashl_core_v1.output.first_output_review import review_last_first_output_candidate


ROOT = Path(__file__).resolve().parents[2]
CLI_MODULE = "ashl_core_v1.output.first_output_followup_cli"


class FirstOutputFollowUpLoopTests(unittest.TestCase):
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

    def seed_first_output_record(self, data_dir: Path) -> dict:
        save_first_output_candidate(
            build_first_output_candidate_from_replay(
                {
                    "session_id": "session_001",
                    "case_sequence": ["blocked_front_obstacle"],
                    "case_count": 1,
                }
            ),
            data_dir,
        )
        review_last_first_output_candidate("approved", "ok", data_dir)
        return promote_last_approved_first_output(data_dir)

    def test_follow_last_first_output_works_after_record_exists(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            record = self.seed_first_output_record(data_dir)

            followup = follow_last_first_output(
                "teacher_note",
                "noticed first output",
                "check tomorrow",
                data_dir,
            )

            self.assertEqual(record["first_output_id"], followup["source_first_output_id"])
            self.assertEqual("teacher_note", followup["followup_kind"])

    def test_follow_first_output_works_by_id(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            record = self.seed_first_output_record(data_dir)

            followup = follow_first_output(
                record["first_output_id"],
                "next_step_marker",
                "next marker",
                None,
                data_dir,
            )

            self.assertEqual(record["first_output_id"], followup["source_first_output_id"])

    def test_all_supported_followup_kinds_work(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.seed_first_output_record(data_dir)

            kinds = [
                follow_last_first_output(kind, f"{kind} note", None, data_dir)["followup_kind"]
                for kind in ALLOWED_FOLLOWUP_KINDS
            ]

            self.assertEqual(list(ALLOWED_FOLLOWUP_KINDS), kinds)

    def test_missing_first_output_id_returns_readable_not_found(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_cli(
                Path(temp_dir),
                "follow-first-output",
                "--first-output-id",
                "missing",
                "--kind",
                "teacher_note",
                "--note",
                "missing",
                check=False,
            )

            self.assertEqual(1, result.returncode)
            self.assertIn("not_found", result.stdout)

    def test_followup_preserves_source_ids_and_last_followup(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            record = self.seed_first_output_record(data_dir)

            followup = follow_last_first_output("teacher_question", "why this?", None, data_dir)

            self.assertEqual(record["source_candidate_id"], followup["source_candidate_id"])
            self.assertEqual(record["source_review_id"], followup["source_review_id"])
            self.assertEqual(followup, load_last_first_output_followup(data_dir))

    def test_list_followups_returns_records(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.seed_first_output_record(data_dir)
            follow_last_first_output("teacher_note", "one", None, data_dir)
            follow_last_first_output("hold_for_later", "two", None, data_dir)

            result = list_first_output_followups(data_dir)

            self.assertEqual(2, result["followup_count"])

    def test_followup_does_not_modify_first_output_record(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.seed_first_output_record(data_dir)
            before = copy.deepcopy(list_first_output_records(data_dir))

            follow_last_first_output("teacher_note", "ok", None, data_dir)

            self.assertEqual(before, list_first_output_records(data_dir))

    def test_cli_follow_last_and_show_latest(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.seed_first_output_record(data_dir)

            result = self.run_cli(
                data_dir,
                "follow-last-first-output",
                "--kind",
                "needs_observation",
                "--note",
                "needs observation",
            )
            followup = json.loads(result.stdout)
            latest = json.loads(self.run_cli(data_dir, "show-last-followup").stdout)

            self.assertEqual(followup["followup_id"], latest["followup_id"])

    def test_repo_data_directory_is_not_polluted_during_tests(self):
        self.assertFalse((ROOT / "ashl_core_v1" / "data").exists())


if __name__ == "__main__":
    unittest.main()
