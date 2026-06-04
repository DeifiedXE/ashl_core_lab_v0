import tempfile
import unittest
from pathlib import Path

from ashl_core.candidate_review import (
    append_candidate_review,
    build_candidate_review,
    get_candidate_current_status,
    list_candidate_reviews,
    list_candidates_with_review_status,
)
from ashl_core.rule_candidates import append_rule_candidate


def sample_candidate() -> dict:
    return {
        "id": "rule_cand_test",
        "type": "rule_candidate",
        "status": "candidate",
        "candidate_kind": "concept_counterexample",
        "target_phrase": "睡眠模式",
        "audit_required": True,
        "created_at": "2026-06-04T00:00:00+00:00",
    }


class CandidateReviewTests(unittest.TestCase):
    def test_build_reviewed_review(self):
        review = build_candidate_review(sample_candidate(), "reviewed", note="looks plausible")

        self.assertIsNotNone(review)
        self.assertEqual(review["type"], "candidate_review")
        self.assertEqual(review["decision"], "reviewed")
        self.assertEqual(review["candidate_id"], "rule_cand_test")

    def test_build_rejected_review(self):
        review = build_candidate_review(sample_candidate(), "rejected")

        self.assertIsNotNone(review)
        self.assertEqual(review["decision"], "rejected")

    def test_build_approved_for_trial_review(self):
        review = build_candidate_review(sample_candidate(), "approved_for_trial")

        self.assertIsNotNone(review)
        self.assertEqual(review["decision"], "approved_for_trial")

    def test_unknown_decision_returns_none(self):
        self.assertIsNone(build_candidate_review(sample_candidate(), "active"))

    def test_append_and_list_candidate_reviews(self):
        with tempfile.TemporaryDirectory() as tmp:
            review = build_candidate_review(sample_candidate(), "reviewed")

            append_candidate_review(tmp, review)

            self.assertEqual(list_candidate_reviews(tmp), [review])
            self.assertTrue((Path(tmp) / "candidate_reviews.jsonl").exists())

    def test_status_without_review_uses_candidate_status(self):
        self.assertEqual(get_candidate_current_status(sample_candidate(), []), "candidate")

    def test_status_uses_latest_review_for_same_candidate(self):
        candidate = sample_candidate()
        reviews = [
            build_candidate_review(candidate, "reviewed"),
            build_candidate_review(candidate, "rejected"),
            build_candidate_review(candidate, "approved_for_trial"),
        ]

        self.assertEqual(get_candidate_current_status(candidate, reviews), "approved_for_trial")

    def test_list_candidates_with_review_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            candidate = sample_candidate()
            review = build_candidate_review(candidate, "reviewed")

            append_rule_candidate(tmp, candidate)
            append_candidate_review(tmp, review)
            rows = list_candidates_with_review_status(tmp)

            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["id"], candidate["id"])
            self.assertEqual(rows[0]["candidate_kind"], "concept_counterexample")
            self.assertEqual(rows[0]["target_phrase"], "睡眠模式")
            self.assertEqual(rows[0]["status"], "candidate")
            self.assertEqual(rows[0]["current_status"], "reviewed")
            self.assertTrue(rows[0]["audit_required"])

    def test_missing_candidate_fields_do_not_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            append_rule_candidate(tmp, {"id": "minimal"})

            rows = list_candidates_with_review_status(tmp)

            self.assertEqual(rows[0]["id"], "minimal")
            self.assertIsNone(rows[0]["candidate_kind"])
            self.assertEqual(rows[0]["current_status"], "candidate")

    def test_approved_for_trial_is_review_status_only(self):
        candidate = sample_candidate()
        review = build_candidate_review(candidate, "approved_for_trial")

        self.assertEqual(candidate["status"], "candidate")
        self.assertEqual(get_candidate_current_status(candidate, [review]), "approved_for_trial")
        self.assertNotEqual(candidate["status"], "active")


if __name__ == "__main__":
    unittest.main()
