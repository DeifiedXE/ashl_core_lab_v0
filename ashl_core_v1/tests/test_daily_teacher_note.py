import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.output.first_output_candidate import (
    build_first_output_candidate_from_last_daily,
    save_first_output_candidate,
)
from ashl_core_v1.output.first_output_followup import follow_last_first_output
from ashl_core_v1.output.first_output_promotion import promote_last_approved_first_output
from ashl_core_v1.output.first_output_review import review_last_first_output_candidate
from ashl_core_v1.runtime.daily_run import load_last_daily_run, run_cradle_daily
from ashl_core_v1.teacher_console.daily_teacher_note import (
    list_daily_teacher_notes,
    load_last_daily_teacher_note,
    write_daily_teacher_note,
)


ROOT = Path(__file__).resolve().parents[2]
CLI_MODULE = "ashl_core_v1.teacher_console.daily_teacher_note_cli"


class DailyTeacherNoteTests(unittest.TestCase):
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

    def seed_daily_with_followup(self, data_dir: Path) -> dict:
        daily_run = run_cradle_daily("basic", data_dir)
        save_first_output_candidate(build_first_output_candidate_from_last_daily(data_dir), data_dir)
        review_last_first_output_candidate("approved", "ok", data_dir)
        promote_last_approved_first_output(data_dir)
        follow_last_first_output("teacher_note", "follow this", None, data_dir)
        return daily_run

    def test_write_note_works_after_daily_run_exists(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            daily_run = run_cradle_daily("basic", data_dir)

            note = write_daily_teacher_note("daily note", (), None, data_dir)

            self.assertEqual(daily_run["daily_run_id"], note["source_daily_run_id"])
            self.assertEqual(daily_run["session_id"], note["source_session_id"])

    def test_write_note_can_link_first_output_followup(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.seed_daily_with_followup(data_dir)

            note = write_daily_teacher_note("daily note", ("watch blocked",), "tomorrow", data_dir)

            self.assertTrue(note["source_first_output_followup_id"])
            self.assertEqual(["watch blocked"], note["attention_items"])
            self.assertEqual("tomorrow", note["tomorrow_hint"])

    def test_show_last_and_list_notes_work(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            run_cradle_daily("basic", data_dir)
            note = write_daily_teacher_note("daily note", (), None, data_dir)

            self.assertEqual(note, load_last_daily_teacher_note(data_dir))
            self.assertEqual(1, list_daily_teacher_notes(data_dir)["note_count"])

    def test_missing_daily_run_returns_readable_not_found(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_cli(
                Path(temp_dir),
                "write-note",
                "--note",
                "no daily",
                check=False,
            )

            self.assertEqual(1, result.returncode)
            self.assertIn("not_found", result.stdout)

    def test_note_does_not_modify_daily_run(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            daily_run = run_cradle_daily("basic", data_dir)

            write_daily_teacher_note("daily note", (), None, data_dir)

            self.assertEqual(daily_run, load_last_daily_run(data_dir))

    def test_cli_write_note_outputs_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            run_cradle_daily("basic", data_dir)

            result = self.run_cli(
                data_dir,
                "write-note",
                "--note",
                "cli note",
                "--attention-item",
                "blocked",
                "--tomorrow-hint",
                "inspect",
            )
            payload = json.loads(result.stdout)

            self.assertEqual("cli note", payload["note_text"])
            self.assertEqual(["blocked"], payload["attention_items"])

    def test_repo_data_directory_is_not_polluted_during_tests(self):
        self.assertFalse((ROOT / "ashl_core_v1" / "data").exists())


if __name__ == "__main__":
    unittest.main()
