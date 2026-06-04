import tempfile
import unittest
from pathlib import Path

from ashl_core.standing_task import run_standing_task


class StandingTaskTests(unittest.TestCase):
    def test_run_standing_task_succeeds(self):
        trace = run_standing_task()

        self.assertTrue(trace["success"])

    def test_final_state_is_standing_stable(self):
        trace = run_standing_task()

        self.assertEqual(trace["final_state"], "standing_stable")

    def test_failures_include_cannot_stand_directly_from_lying(self):
        trace = run_standing_task()

        self.assertIn(
            "cannot_stand_directly_from_lying",
            [failure["failure_reason"] for failure in trace["failures"]],
        )

    def test_lesson_candidate_exists(self):
        trace = run_standing_task()

        self.assertIsNotNone(trace["lesson_candidate"])
        self.assertEqual(trace["lesson_candidate"]["type"], "lesson_candidate")
        self.assertEqual(trace["lesson_candidate"]["lesson_kind"], "body_transition")

    def test_lesson_candidate_is_candidate(self):
        trace = run_standing_task()

        self.assertEqual(trace["lesson_candidate"]["status"], "candidate")
        self.assertTrue(trace["lesson_candidate"]["audit_required"])

    def test_run_standing_task_does_not_create_jsonl_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            before = set(Path(tmp).glob("*.jsonl"))
            trace = run_standing_task()
            after = set(Path(tmp).glob("*.jsonl"))

            self.assertTrue(trace["success"])
            self.assertEqual(after, before)


if __name__ == "__main__":
    unittest.main()
