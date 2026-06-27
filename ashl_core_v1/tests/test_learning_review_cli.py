import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.lesson.review_store import (
    list_learning_review_records,
    list_pending_learning_digests,
    list_reviewed_learning_digests,
    seed_blocked_sample,
)


ROOT = Path(__file__).resolve().parents[2]
CLI_MODULE = "ashl_core_v1.lesson.review_cli"


class LearningReviewCliTests(unittest.TestCase):
    def run_cli(self, data_dir: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", CLI_MODULE, "--data-dir", str(data_dir), *args],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

    def test_seed_blocked_sample_creates_pending_digest(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)

            result = self.run_cli(data_dir, "seed-blocked-sample")
            pending = list_pending_learning_digests(data_dir)

            self.assertIn("seeded digest_id=learning_digest_front_obstacle_001", result.stdout)
            self.assertEqual(1, len(pending))
            self.assertEqual("learning_digest_front_obstacle_001", pending[0].learning_digest_id)

    def test_list_pending_shows_pending_digest(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            seed_blocked_sample(data_dir)

            result = self.run_cli(data_dir, "list-pending")

            self.assertIn("digest_id=learning_digest_front_obstacle_001", result.stdout)
            self.assertIn("digest_type=obstruction_event", result.stdout)
            self.assertIn("generalization_scope=same_context_only", result.stdout)
            self.assertIn("source_perception_refs=perception_front_obstacle_tick0", result.stdout)

    def test_approved_review_creates_review_record(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            seed_blocked_sample(data_dir)

            result = self.run_cli(
                data_dir,
                "review",
                "--digest-id",
                "learning_digest_front_obstacle_001",
                "--status",
                "approved",
                "--note",
                "approved from test",
            )
            records = list_learning_review_records(data_dir)

            self.assertIn("status=approved", result.stdout)
            self.assertEqual(1, len(records))
            self.assertEqual("approved", records[0].review_status)
            self.assertEqual("approved from test", records[0].teacher_note)

    def test_approved_review_creates_reviewed_digest_with_memory_entry_allowed_true(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            seed_blocked_sample(data_dir)

            self.run_cli(
                data_dir,
                "review",
                "--digest-id",
                "learning_digest_front_obstacle_001",
                "--status",
                "approved",
                "--note",
                "approved from test",
            )
            reviewed = list_reviewed_learning_digests(data_dir)

            self.assertEqual(1, len(reviewed))
            self.assertTrue(reviewed[0].memory_entry_allowed)
            self.assertEqual("learning_digest_front_obstacle_001", reviewed[0].source_learning_digest_id)

    def test_rejected_review_creates_reviewed_digest_with_memory_entry_allowed_false(self):
        reviewed = self.review_blocked_sample_with_status("rejected")

        self.assertFalse(reviewed.memory_entry_allowed)
        self.assertEqual("rejected", reviewed.review_status)

    def test_deferred_review_creates_reviewed_digest_with_memory_entry_allowed_false(self):
        reviewed = self.review_blocked_sample_with_status("deferred")

        self.assertFalse(reviewed.memory_entry_allowed)
        self.assertEqual("deferred", reviewed.review_status)

    def test_needs_more_evidence_review_creates_reviewed_digest_with_memory_entry_allowed_false(self):
        reviewed = self.review_blocked_sample_with_status("needs_more_evidence")

        self.assertFalse(reviewed.memory_entry_allowed)
        self.assertEqual("needs_more_evidence", reviewed.review_status)

    def test_conflict_detected_review_creates_reviewed_digest_with_memory_entry_allowed_false(self):
        reviewed = self.review_blocked_sample_with_status("conflict_detected")

        self.assertFalse(reviewed.memory_entry_allowed)
        self.assertEqual("conflict_detected", reviewed.review_status)

    def test_reviewed_output_preserves_source_digest_id(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            seed_blocked_sample(data_dir)
            self.run_cli(
                data_dir,
                "review",
                "--digest-id",
                "learning_digest_front_obstacle_001",
                "--status",
                "approved",
                "--note",
                "approved from test",
            )

            result = self.run_cli(data_dir, "show-reviewed")

            self.assertIn("reviewed_digest_id=reviewed_learning_digest_front_obstacle_001_approved", result.stdout)
            self.assertIn("source_learning_digest_id=learning_digest_front_obstacle_001", result.stdout)
            self.assertIn("memory_entry_allowed=true", result.stdout)

    def test_review_missing_digest_returns_readable_not_found_result(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    CLI_MODULE,
                    "--data-dir",
                    str(data_dir),
                    "review",
                    "--digest-id",
                    "missing",
                    "--status",
                    "approved",
                    "--note",
                    "cannot find",
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(2, result.returncode)
            self.assertIn("not_found:", result.stderr)

    def review_blocked_sample_with_status(self, status: str):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            seed_blocked_sample(data_dir)
            self.run_cli(
                data_dir,
                "review",
                "--digest-id",
                "learning_digest_front_obstacle_001",
                "--status",
                status,
                "--note",
                f"{status} from test",
            )
            reviewed = list_reviewed_learning_digests(data_dir)
            self.assertEqual(1, len(reviewed))
            return reviewed[0]


if __name__ == "__main__":
    unittest.main()
