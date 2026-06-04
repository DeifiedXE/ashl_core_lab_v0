import tempfile
import unittest
from pathlib import Path

from ashl_core.experience_log import list_experience_events, list_lesson_candidates
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

    def test_persist_experience_false_does_not_create_jsonl_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace = run_standing_task(persist_experience=False, data_dir=tmp)

            self.assertTrue(trace["success"])
            self.assertIsNone(trace["experience_persistence"])
            self.assertFalse((Path(tmp) / "experience_events.jsonl").exists())
            self.assertFalse((Path(tmp) / "lesson_candidates.jsonl").exists())

    def test_persist_experience_true_creates_experience_events(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace = run_standing_task(persist_experience=True, data_dir=tmp)
            events = list_experience_events(tmp)

            self.assertTrue(trace["success"])
            self.assertTrue((Path(tmp) / "experience_events.jsonl").exists())
            self.assertEqual(len(events), len(trace["actions"]))

    def test_persist_experience_true_creates_lesson_candidates(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_standing_task(persist_experience=True, data_dir=tmp)
            lessons = list_lesson_candidates(tmp)

            self.assertTrue((Path(tmp) / "lesson_candidates.jsonl").exists())
            self.assertEqual(len(lessons), 1)
            self.assertEqual(lessons[0]["lesson_kind"], "body_transition")
            self.assertEqual(lessons[0]["status"], "candidate")

    def test_experience_events_include_failed_stand_up(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_standing_task(persist_experience=True, data_dir=tmp)
            events = list_experience_events(tmp)

            self.assertTrue(
                any(
                    event["action"] == "stand_up"
                    and event["success"] is False
                    and event["failure_reason"] == "cannot_stand_directly_from_lying"
                    for event in events
                )
            )


if __name__ == "__main__":
    unittest.main()
