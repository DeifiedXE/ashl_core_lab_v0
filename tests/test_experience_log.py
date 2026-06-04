import tempfile
import unittest
from pathlib import Path

from ashl_core.action_sandbox import apply_action
from ashl_core.body_state import build_body_state
from ashl_core.experience_log import (
    append_experience_event,
    append_lesson_candidate,
    build_experience_event,
    build_lesson_candidate_from_standing_trace,
    list_experience_events,
    list_lesson_candidates,
)
from ashl_core.standing_task import run_standing_task


class ExperienceLogTests(unittest.TestCase):
    def test_build_experience_event_from_action_result(self):
        action_result = apply_action(build_body_state("lying"), "sit_up")
        event = build_experience_event(action_result)

        self.assertIsNotNone(event)
        self.assertEqual(event["type"], "experience_event")
        self.assertEqual(event["source"], "standing_task")
        self.assertEqual(event["action"], "sit_up")
        self.assertTrue(event["success"])

    def test_failure_reason_is_preserved(self):
        action_result = apply_action(build_body_state("lying"), "stand_up")
        event = build_experience_event(action_result)

        self.assertEqual(event["failure_reason"], "cannot_stand_directly_from_lying")

    def test_missing_required_fields_returns_none(self):
        self.assertIsNone(build_experience_event({"action": "stand_up"}))

    def test_build_lesson_candidate_from_successful_standing_trace(self):
        lesson = build_lesson_candidate_from_standing_trace(run_standing_task())

        self.assertIsNotNone(lesson)
        self.assertEqual(lesson["type"], "lesson_candidate")
        self.assertEqual(lesson["lesson_kind"], "body_transition")
        self.assertIn("cannot_stand_directly_from_lying", lesson["evidence"])

    def test_unsuccessful_trace_does_not_create_lesson_candidate(self):
        trace = {"type": "standing_task_trace", "success": False, "final_state": "fallen"}

        self.assertIsNone(build_lesson_candidate_from_standing_trace(trace))

    def test_lesson_candidate_is_candidate(self):
        lesson = build_lesson_candidate_from_standing_trace(run_standing_task())

        self.assertEqual(lesson["status"], "candidate")
        self.assertTrue(lesson["audit_required"])

    def test_append_and_list_experience_events(self):
        with tempfile.TemporaryDirectory() as tmp:
            event = build_experience_event(apply_action(build_body_state("lying"), "stand_up"))
            append_experience_event(tmp, event)

            self.assertEqual(list_experience_events(tmp), [event])

    def test_append_and_list_lesson_candidates(self):
        with tempfile.TemporaryDirectory() as tmp:
            lesson = build_lesson_candidate_from_standing_trace(run_standing_task())
            append_lesson_candidate(tmp, lesson)

            self.assertEqual(list_lesson_candidates(tmp), [lesson])

    def test_missing_files_return_empty_lists(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(list_experience_events(tmp), [])
            self.assertEqual(list_lesson_candidates(tmp), [])

    def test_tests_use_tmp_path_without_repo_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            lesson = build_lesson_candidate_from_standing_trace(run_standing_task())
            append_lesson_candidate(tmp, lesson)

            self.assertTrue((Path(tmp) / "lesson_candidates.jsonl").exists())


if __name__ == "__main__":
    unittest.main()
