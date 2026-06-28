import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.output.first_output_candidate import (
    build_first_output_candidate_from_replay,
    list_first_output_candidates,
    save_first_output_candidate,
)
from ashl_core_v1.output.first_output_promotion import (
    build_first_output_record,
    list_first_output_records,
    load_last_first_output_record,
    promote_first_output_review,
    promote_last_approved_first_output,
)
from ashl_core_v1.output.first_output_review import (
    build_first_output_review_record,
    list_first_output_reviews,
    review_last_first_output_candidate,
)


ROOT = Path(__file__).resolve().parents[2]
CLI_MODULE = "ashl_core_v1.output.first_output_promotion_cli"


class FirstOutputPromotionTests(unittest.TestCase):
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

    def seed_candidate_and_review(self, data_dir: Path, status: str = "approved") -> tuple[dict, dict]:
        candidate = save_first_output_candidate(
            build_first_output_candidate_from_replay(
                {
                    "session_id": "session_001",
                    "case_sequence": ["blocked_front_obstacle"],
                    "case_count": 1,
                }
            ),
            data_dir,
        )
        review = review_last_first_output_candidate(status, f"{status} note", data_dir)
        return candidate, review

    def test_approved_review_can_be_promoted(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            candidate, review = self.seed_candidate_and_review(data_dir)

            record = promote_first_output_review(review["review_id"], data_dir)

            self.assertEqual("promoted", record["promotion_status"])
            self.assertEqual(candidate["candidate_id"], record["source_candidate_id"])

    def test_promoted_record_includes_source_review_id_and_payload(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            candidate, review = self.seed_candidate_and_review(data_dir)

            record = promote_first_output_review(review["review_id"], data_dir)

            self.assertEqual(review["review_id"], record["source_review_id"])
            self.assertEqual(candidate["output_payload"], record["output_payload"])

    def test_promote_last_approved_works(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.seed_candidate_and_review(data_dir)

            record = promote_last_approved_first_output(data_dir)

            self.assertEqual("promoted", record["promotion_status"])

    def test_show_last_first_output_works(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            _, review = self.seed_candidate_and_review(data_dir)
            record = promote_first_output_review(review["review_id"], data_dir)

            self.assertEqual(record, load_last_first_output_record(data_dir))

    def test_list_first_outputs_returns_records(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            _, review = self.seed_candidate_and_review(data_dir)
            promote_first_output_review(review["review_id"], data_dir)

            records = list_first_output_records(data_dir)

            self.assertEqual(1, records["record_count"])

    def test_rejected_review_cannot_promote(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            _, review = self.seed_candidate_and_review(data_dir, "rejected")

            record = promote_first_output_review(review["review_id"], data_dir)

            self.assertEqual("blocked", record["promotion_status"])
            self.assertIn("review_status_not_approved", record["promotion_reason"])

    def test_missing_review_cannot_promote(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            record = promote_first_output_review("missing", Path(temp_dir))

            self.assertEqual("blocked", record["promotion_status"])
            self.assertEqual("review_not_found", record["promotion_reason"])

    def test_candidate_review_mismatch_cannot_promote(self):
        candidate = build_first_output_candidate_from_replay({"session_id": "session_001"})
        other_candidate = build_first_output_candidate_from_replay({"session_id": "session_002"})
        review = build_first_output_review_record(other_candidate, "approved", "ok")

        record = build_first_output_record(candidate, review)

        self.assertEqual("blocked", record["promotion_status"])
        self.assertEqual("candidate_review_mismatch", record["promotion_reason"])

    def test_promotion_does_not_delete_candidate_or_review(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            _, review = self.seed_candidate_and_review(data_dir)
            candidates_before = copy.deepcopy(list_first_output_candidates(data_dir))
            reviews_before = copy.deepcopy(list_first_output_reviews(data_dir))

            promote_first_output_review(review["review_id"], data_dir)

            self.assertEqual(candidates_before, list_first_output_candidates(data_dir))
            self.assertEqual(reviews_before, list_first_output_reviews(data_dir))

    def test_cli_promote_last_approved_outputs_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.seed_candidate_and_review(data_dir)

            result = self.run_cli(data_dir, "promote-last-approved")
            record = json.loads(result.stdout)

            self.assertEqual("promoted", record["promotion_status"])

    def test_repo_data_directory_is_not_polluted_during_tests(self):
        self.assertFalse((ROOT / "ashl_core_v1" / "data").exists())


if __name__ == "__main__":
    unittest.main()
