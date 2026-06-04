import unittest

from ashl_core.fake_sandbox import build_initial_sandbox_state, pick_up
from ashl_core.lesson_store import build_lesson_from_failure, select_lesson_for_failure_reason


def _failure_result(failure_reason):
    return {
        "type": "sandbox_action_result",
        "tool": "pick_up",
        "object_id": "cube_001",
        "result": "failed",
        "failure_reason": failure_reason,
        "state": build_initial_sandbox_state(),
    }


def _lesson_east():
    return build_lesson_from_failure("session_east", pick_up(build_initial_sandbox_state(), "cube_001"))


def _lesson_west():
    return build_lesson_from_failure("session_west", _failure_result("not_facing_west"))


class MultiLessonIsolationTests(unittest.TestCase):
    def test_two_non_conflicting_lessons_do_not_interfere(self):
        lessons = [_lesson_east(), _lesson_west()]

        east = select_lesson_for_failure_reason(lessons, "not_facing_east")
        west = select_lesson_for_failure_reason(lessons, "not_facing_west")

        self.assertEqual(east["selected_lesson_id"], "lesson_001")
        self.assertEqual(east["selected_action"], "turn(east)")
        self.assertNotEqual(east["selected_action"], "turn(west)")
        self.assertFalse(east["conflict_detected"])

        self.assertEqual(west["selected_lesson_id"], "lesson_002")
        self.assertEqual(west["selected_action"], "turn(west)")
        self.assertNotEqual(west["selected_action"], "turn(east)")
        self.assertFalse(west["conflict_detected"])

    def test_east_case_only_triggers_east_lesson(self):
        result = select_lesson_for_failure_reason([_lesson_east(), _lesson_west()], "not_facing_east")

        self.assertEqual(result["active_lesson_ids"], ["lesson_001", "lesson_002"])
        self.assertEqual(result["matched_failure_reason"], "not_facing_east")
        self.assertEqual(result["selected_lesson_id"], "lesson_001")
        self.assertEqual(result["selected_action"], "turn(east)")
        self.assertNotIn("turn(west)", str(result))

    def test_west_case_only_triggers_west_lesson(self):
        result = select_lesson_for_failure_reason([_lesson_east(), _lesson_west()], "not_facing_west")

        self.assertEqual(result["active_lesson_ids"], ["lesson_001", "lesson_002"])
        self.assertEqual(result["matched_failure_reason"], "not_facing_west")
        self.assertEqual(result["selected_lesson_id"], "lesson_002")
        self.assertEqual(result["selected_action"], "turn(west)")
        self.assertNotIn("turn(east)", str(result))

    def test_single_east_lesson_keeps_existing_behavior(self):
        result = select_lesson_for_failure_reason([_lesson_east()], "not_facing_east")

        self.assertEqual(result["selected_lesson_id"], "lesson_001")
        self.assertEqual(result["selected_action"], "turn(east)")

    def test_single_west_lesson_keeps_existing_behavior(self):
        result = select_lesson_for_failure_reason([_lesson_west()], "not_facing_west")

        self.assertEqual(result["selected_lesson_id"], "lesson_002")
        self.assertEqual(result["selected_action"], "turn(west)")

    def test_no_cross_trigger_for_east_with_west_present(self):
        result = select_lesson_for_failure_reason([_lesson_east(), _lesson_west()], "not_facing_east")

        self.assertNotEqual(result["selected_lesson_id"], "lesson_002")
        self.assertEqual(result["selected_lesson_id"], "lesson_001")

    def test_no_cross_trigger_for_west_with_east_present(self):
        result = select_lesson_for_failure_reason([_lesson_east(), _lesson_west()], "not_facing_west")

        self.assertNotEqual(result["selected_lesson_id"], "lesson_001")
        self.assertEqual(result["selected_lesson_id"], "lesson_002")

    def test_no_conflict_detected_in_isolation_case(self):
        east = select_lesson_for_failure_reason([_lesson_east(), _lesson_west()], "not_facing_east")
        west = select_lesson_for_failure_reason([_lesson_east(), _lesson_west()], "not_facing_west")

        self.assertFalse(east["conflict_detected"])
        self.assertFalse(west["conflict_detected"])


if __name__ == "__main__":
    unittest.main()
