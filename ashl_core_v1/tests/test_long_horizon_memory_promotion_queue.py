import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.memory.promotion_queue import (
    build_memory_promotion_candidate,
    enqueue_last_first_output_followup,
    enqueue_last_teacher_note,
    enqueue_manual_promotion_candidate,
    enqueue_memory_promotion_candidate,
    list_memory_promotion_queue,
    load_last_memory_promotion_candidate,
)
from ashl_core_v1.output.first_output_candidate import (
    build_first_output_candidate_from_last_daily,
    save_first_output_candidate,
)
from ashl_core_v1.output.first_output_followup import follow_last_first_output
from ashl_core_v1.output.first_output_promotion import promote_last_approved_first_output
from ashl_core_v1.output.first_output_review import review_last_first_output_candidate
from ashl_core_v1.runtime.daily_run import run_cradle_daily
from ashl_core_v1.teacher_console.daily_teacher_note import write_daily_teacher_note


ROOT = Path(__file__).resolve().parents[2]
CLI_MODULE = "ashl_core_v1.memory.promotion_queue_cli"


class LongHorizonMemoryPromotionQueueTests(unittest.TestCase):
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

    def seed_daily_note(self, data_dir: Path) -> dict:
        run_cradle_daily("basic", data_dir)
        return write_daily_teacher_note("teacher note", ("watch",), "tomorrow", data_dir)

    def seed_followup(self, data_dir: Path) -> dict:
        run_cradle_daily("basic", data_dir)
        save_first_output_candidate(build_first_output_candidate_from_last_daily(data_dir), data_dir)
        review_last_first_output_candidate("approved", "ok", data_dir)
        promote_last_approved_first_output(data_dir)
        return follow_last_first_output("teacher_note", "followup", None, data_dir)

    def test_manual_promotion_candidate_can_be_enqueued(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            candidate = enqueue_manual_promotion_candidate(
                "manual observation",
                "review later",
                "high",
                Path(temp_dir),
            )

            self.assertEqual("manual_note", candidate["source_kind"])
            self.assertEqual("queued", candidate["status"])
            self.assertEqual("high", candidate["priority"])

    def test_last_teacher_note_can_be_enqueued(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            note = self.seed_daily_note(data_dir)

            candidate = enqueue_last_teacher_note("promote teacher note", "normal", data_dir)

            self.assertEqual("daily_teacher_note", candidate["source_kind"])
            self.assertEqual(note["note_id"], candidate["source_id"])

    def test_last_first_output_followup_can_be_enqueued(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            followup = self.seed_followup(data_dir)

            candidate = enqueue_last_first_output_followup("promote followup", "low", data_dir)

            self.assertEqual("first_output_followup", candidate["source_kind"])
            self.assertEqual(followup["followup_id"], candidate["source_id"])

    def test_list_queue_and_show_last_work(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            first = enqueue_manual_promotion_candidate("one", "reason", "normal", data_dir)
            second = enqueue_manual_promotion_candidate("two", "reason", "normal", data_dir)

            self.assertNotEqual(first["promotion_candidate_id"], second["promotion_candidate_id"])
            self.assertEqual(second, load_last_memory_promotion_candidate(data_dir))
            self.assertEqual(2, list_memory_promotion_queue(data_dir)["candidate_count"])

    def test_missing_teacher_note_returns_readable_not_found(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_cli(
                Path(temp_dir),
                "enqueue-last-teacher-note",
                "--reason",
                "missing",
                check=False,
            )

            self.assertEqual(1, result.returncode)
            self.assertIn("not_found", result.stdout)

    def test_missing_followup_returns_readable_not_found(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_cli(
                Path(temp_dir),
                "enqueue-last-followup",
                "--reason",
                "missing",
                check=False,
            )

            self.assertEqual(1, result.returncode)
            self.assertIn("not_found", result.stdout)

    def test_invalid_source_kind_and_priority_are_rejected(self):
        with self.assertRaises(ValueError):
            build_memory_promotion_candidate("bad", "id", "summary", "reason")
        with self.assertRaises(ValueError):
            build_memory_promotion_candidate("manual_note", "id", "summary", "reason", "urgent")

    def test_enqueue_validates_candidate(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            candidate = build_memory_promotion_candidate(
                "daily_operation_audit",
                "audit_001",
                "audit summary",
                "review audit",
                "normal",
                ("audit:audit_001",),
            )

            saved = enqueue_memory_promotion_candidate(candidate, Path(temp_dir))

            self.assertEqual(candidate, saved)

    def test_cli_enqueue_manual_outputs_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_cli(
                Path(temp_dir),
                "enqueue-manual",
                "--summary",
                "manual",
                "--reason",
                "future review",
            )
            payload = json.loads(result.stdout)

            self.assertEqual("manual_note", payload["source_kind"])

    def test_queue_does_not_write_long_term_memory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            enqueue_manual_promotion_candidate("manual", "future review", "normal", data_dir)

            self.assertFalse((data_dir / "long_term_memory.json").exists())

    def test_repo_data_directory_is_not_polluted_during_tests(self):
        self.assertFalse((ROOT / "ashl_core_v1" / "data").exists())


if __name__ == "__main__":
    unittest.main()
