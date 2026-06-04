import unittest

from ashl_core.fake_sandbox import build_initial_sandbox_state, pick_up
from ashl_core.lesson_runner import (
    run_phase_minus_one,
    run_session_1,
    run_session_2a_with_lesson,
    run_session_2b2_without_lesson_with_turn_tool,
    run_session_2b_without_lesson,
)
from ashl_core.lesson_store import build_lesson_from_failure, find_applicable_lesson


class LessonContributionTests(unittest.TestCase):
    def test_session_1_failure_builds_lesson_001(self):
        result = run_session_1()

        self.assertIsNotNone(result["lesson"])
        self.assertEqual(result["lesson"]["lesson_id"], "lesson_001")

    def test_lesson_001_source_failure_reason(self):
        lesson = run_session_1()["lesson"]

        self.assertEqual(lesson["source_failure_reason"], "not_facing_east")

    def test_session_2a_with_lesson_includes_turn_east(self):
        lesson = run_session_1()["lesson"]
        result = run_session_2a_with_lesson(lesson)

        self.assertIn("turn(east)", [action["action"] for action in result["actions"]])

    def test_session_2a_final_pick_up_succeeds(self):
        lesson = run_session_1()["lesson"]
        result = run_session_2a_with_lesson(lesson)

        self.assertTrue(result["success"])
        self.assertEqual(result["final_result"]["result"], "success")
        self.assertEqual(result["final_result"]["state"]["holding"], "cube_001")

    def test_session_2a_used_lesson_ids_contains_lesson_001(self):
        lesson = run_session_1()["lesson"]
        result = run_session_2a_with_lesson(lesson)

        self.assertEqual(result["used_lesson_ids"], ["lesson_001"])

    def test_session_2b_without_lesson_fails(self):
        result = run_session_2b_without_lesson()

        self.assertFalse(result["success"])

    def test_session_2b_failure_reason(self):
        result = run_session_2b_without_lesson()

        self.assertEqual(result["final_result"]["failure_reason"], "not_facing_east")

    def test_session_2b2_turn_tool_visible_without_lesson_does_not_succeed(self):
        result = run_session_2b2_without_lesson_with_turn_tool()

        self.assertIn("turn", result["decision_input_snapshot"]["available_actions"])
        self.assertFalse(result["success"])

    def test_removing_lesson_returns_to_unfixed_behavior(self):
        result = run_session_2b_without_lesson()

        self.assertEqual([action["action"] for action in result["actions"]], ["observe()", "pick_up(cube_001)"])
        self.assertFalse(result["success"])

    def test_lesson_001_does_not_apply_to_unrelated_object_or_action(self):
        failure = pick_up(build_initial_sandbox_state(), "cube_001")
        lesson = build_lesson_from_failure("session_1", failure)

        self.assertIsNone(find_applicable_lesson([lesson], {"action": "push", "object_id": "cube_001"}))
        self.assertIsNone(find_applicable_lesson([lesson], {"action": "pick_up", "object_id": "sphere_001"}))

    def test_run_phase_minus_one_passed(self):
        result = run_phase_minus_one()

        self.assertTrue(result["passed"])
        self.assertTrue(result["summary"]["lesson_caused_behavior_shift"])
        self.assertEqual(result["summary"]["behavior_shift_traceable_to"], ["lesson_001"])

    def test_phase_minus_one_existing_controls_still_hold(self):
        result = run_phase_minus_one()

        self.assertTrue(result["session_2a"]["success"])
        self.assertFalse(result["session_2b"]["success"])
        self.assertFalse(result["session_2b2"]["success"])
        self.assertEqual(result["summary"]["behavior_shift_traceable_to"], ["lesson_001"])


if __name__ == "__main__":
    unittest.main()
