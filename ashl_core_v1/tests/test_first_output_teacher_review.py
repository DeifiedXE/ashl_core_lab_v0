import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.output.first_output_candidate import (
    build_first_output_candidate_from_replay,
    load_last_first_output_candidate,
    save_first_output_candidate,
)
from ashl_core_v1.output.first_output_review import (
    build_first_output_review_record,
    list_first_output_reviews,
    load_last_first_output_review,
    review_first_output_candidate,
    review_last_first_output_candidate,
)


ROOT = Path(__file__).resolve().parents[2]
CLI_MODULE = "ashl_core_v1.output.first_output_review_cli"


class FirstOutputTeacherReviewTests(unittest.TestCase):
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

    def seed_candidate(self, data_dir: Path) -> dict:
        candidate = build_first_output_candidate_from_replay(
            {
                "session_id": "session_001",
                "case_sequence": ["blocked_front_obstacle"],
                "case_count": 1,
            }
        )
        return save_first_output_candidate(candidate, data_dir)

    def test_review_last_candidate_works_after_candidate_exists(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            candidate = self.seed_candidate(data_dir)

            review = review_last_first_output_candidate("approved", "ok", data_dir)

            self.assertEqual(candidate["candidate_id"], review["source_candidate_id"])
            self.assertEqual("approved", review["review_status"])

    def test_review_candidate_works_by_candidate_id(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            candidate = self.seed_candidate(data_dir)

            review = review_first_output_candidate(candidate["candidate_id"], "rejected", "no", data_dir)

            self.assertEqual(candidate["candidate_id"], review["source_candidate_id"])
            self.assertEqual("rejected", review["review_status"])

    def test_approved_review_creates_approved_scope(self):
        candidate = build_first_output_candidate_from_replay({"session_id": "session_001"})

        review = build_first_output_review_record(candidate, "approved", "ok")

        self.assertEqual("traceable_status_output_only", review["approved_scope"])

    def test_non_approved_reviews_have_null_approved_scope(self):
        candidate = build_first_output_candidate_from_replay({"session_id": "session_001"})
        for status in ("rejected", "deferred", "needs_more_evidence", "conflict_detected"):
            with self.subTest(status=status):
                review = build_first_output_review_record(candidate, status, "hold")
                self.assertIsNone(review["approved_scope"])

    def test_show_last_review_returns_latest_review(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.seed_candidate(data_dir)
            review = review_last_first_output_candidate("deferred", "later", data_dir)

            self.assertEqual(review, load_last_first_output_review(data_dir))

    def test_list_reviews_returns_records(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.seed_candidate(data_dir)
            review_last_first_output_candidate("needs_more_evidence", "more", data_dir)

            records = list_first_output_reviews(data_dir)

            self.assertEqual(1, records["review_count"])
            self.assertEqual("needs_more_evidence", records["reviews"][0]["review_status"])

    def test_missing_candidate_returns_readable_not_found(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_cli(
                Path(temp_dir),
                "review-candidate",
                "--candidate-id",
                "missing",
                "--status",
                "approved",
                "--note",
                "missing",
                check=False,
            )

            self.assertEqual(1, result.returncode)
            self.assertIn("not_found", result.stdout)

    def test_review_does_not_modify_original_candidate(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            candidate = self.seed_candidate(data_dir)
            before = copy.deepcopy(load_last_first_output_candidate(data_dir))

            review_last_first_output_candidate("approved", "ok", data_dir)

            self.assertEqual(before, load_last_first_output_candidate(data_dir))
            self.assertEqual(candidate["candidate_id"], before["candidate_id"])

    def test_cli_review_last_candidate_outputs_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.seed_candidate(data_dir)

            result = self.run_cli(
                data_dir,
                "review-last-candidate",
                "--status",
                "approved",
                "--note",
                "ok",
            )
            review = json.loads(result.stdout)

            self.assertEqual("approved", review["review_status"])

    def test_repo_data_directory_is_not_polluted_during_tests(self):
        self.assertFalse((ROOT / "ashl_core_v1" / "data").exists())


if __name__ == "__main__":
    unittest.main()
