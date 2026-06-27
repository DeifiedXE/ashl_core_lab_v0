import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.lesson.correction_store import (
    create_teacher_correction,
    create_teacher_revoke,
    list_teacher_corrections,
    list_teacher_revokes,
)
from ashl_core_v1.lesson.review_store import (
    list_reviewed_learning_digests,
    seed_blocked_sample,
    review_learning_digest,
)
from ashl_core_v1.memory.trace_store import (
    list_memory_learning_traces,
    seed_blocked_sample_trace,
)


ROOT = Path(__file__).resolve().parents[2]
CLI_MODULE = "ashl_core_v1.lesson.correction_cli"


class TeacherCorrectionAndRevokeTests(unittest.TestCase):
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

    def seed_reviewed_digest(self, data_dir: Path) -> str:
        seed_blocked_sample(data_dir)
        review_learning_digest(
            digest_id="learning_digest_front_obstacle_001",
            status="approved",
            note="approved before correction",
            data_dir=data_dir,
        )
        return list_reviewed_learning_digests(data_dir)[0].reviewed_digest_id

    def test_correct_reviewed_creates_correction_record(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            reviewed_digest_id = self.seed_reviewed_digest(data_dir)

            record = create_teacher_correction(
                reviewed_digest_id,
                "correct_note",
                "note correction",
                data_dir,
            )

            self.assertEqual(reviewed_digest_id, record["source_reviewed_digest_id"])
            self.assertEqual("correct_note", record["correction_type"])
            self.assertEqual(1, len(list_teacher_corrections(data_dir)))

    def test_change_to_rejected_correction_can_be_recorded(self):
        self.assert_correction_type("change_to_rejected", "rejected_requested")

    def test_change_to_deferred_correction_can_be_recorded(self):
        self.assert_correction_type("change_to_deferred", "deferred_requested")

    def test_mark_wrong_correction_can_be_recorded(self):
        self.assert_correction_type("mark_wrong", "marked_wrong")

    def test_revoke_memory_trace_creates_revoke_record(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            seed_blocked_sample_trace(data_dir)

            record = create_teacher_revoke(
                "memory_learning_front_obstacle_001",
                "wrong_learning",
                "trace should not be trusted",
                data_dir,
            )

            self.assertEqual("memory_learning_front_obstacle_001", record["source_memory_learning_trace_id"])
            self.assertEqual("reviewed_learning_front_obstacle_001", record["source_reviewed_digest_id"])
            self.assertEqual(1, len(list_teacher_revokes(data_dir)))

    def test_list_corrections_returns_records(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            reviewed_digest_id = self.seed_reviewed_digest(data_dir)
            create_teacher_correction(reviewed_digest_id, "mark_wrong", "wrong", data_dir)

            result = self.run_cli(data_dir, "list-corrections")
            records = json.loads(result.stdout)

            self.assertEqual(1, len(records))
            self.assertEqual("mark_wrong", records[0]["correction_type"])

    def test_list_revokes_returns_records(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            seed_blocked_sample_trace(data_dir)
            create_teacher_revoke("memory_learning_front_obstacle_001", "wrong_learning", "wrong", data_dir)

            result = self.run_cli(data_dir, "list-revokes")
            records = json.loads(result.stdout)

            self.assertEqual(1, len(records))
            self.assertEqual("wrong_learning", records[0]["revoke_reason"])

    def test_missing_reviewed_digest_returns_not_found(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_cli(
                Path(temp_dir),
                "correct-reviewed",
                "--reviewed-digest-id",
                "missing",
                "--type",
                "mark_wrong",
                "--note",
                "missing",
                check=False,
            )

            self.assertEqual(1, result.returncode)
            self.assertIn("not_found", result.stdout)

    def test_missing_memory_trace_returns_not_found(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_cli(
                Path(temp_dir),
                "revoke-memory-trace",
                "--trace-id",
                "missing",
                "--reason",
                "wrong_learning",
                "--note",
                "missing",
                check=False,
            )

            self.assertEqual(1, result.returncode)
            self.assertIn("not_found", result.stdout)

    def test_correction_does_not_delete_original_reviewed_digest(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            reviewed_digest_id = self.seed_reviewed_digest(data_dir)

            create_teacher_correction(reviewed_digest_id, "mark_wrong", "wrong", data_dir)

            self.assertEqual(1, len(list_reviewed_learning_digests(data_dir)))

    def test_revoke_does_not_delete_original_memory_trace(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            seed_blocked_sample_trace(data_dir)

            create_teacher_revoke("memory_learning_front_obstacle_001", "wrong_learning", "wrong", data_dir)

            self.assertEqual(1, len(list_memory_learning_traces(data_dir)))

    def test_cli_correct_reviewed_creates_record(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            reviewed_digest_id = self.seed_reviewed_digest(data_dir)

            result = self.run_cli(
                data_dir,
                "correct-reviewed",
                "--reviewed-digest-id",
                reviewed_digest_id,
                "--type",
                "mark_wrong",
                "--note",
                "wrong",
            )
            record = json.loads(result.stdout)

            self.assertEqual("mark_wrong", record["correction_type"])

    def test_repo_data_directory_is_not_polluted_during_tests(self):
        self.assertFalse((ROOT / "ashl_core_v1" / "data").exists())

    def assert_correction_type(self, correction_type: str, replacement_status: str):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            reviewed_digest_id = self.seed_reviewed_digest(data_dir)

            record = create_teacher_correction(reviewed_digest_id, correction_type, "note", data_dir)

            self.assertEqual(correction_type, record["correction_type"])
            self.assertEqual(replacement_status, record["replacement_status"])


if __name__ == "__main__":
    unittest.main()
