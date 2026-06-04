import unittest

from ashl_core.lesson_runner import (
    run_negative_control_unrelated_lesson,
    run_negative_control_wrong_action_inspect,
    run_negative_control_wrong_action_push,
    run_negative_control_wrong_condition,
    run_negative_control_wrong_object,
    run_phase_minus_one_negative_controls,
)


class LessonNegativeControlTests(unittest.TestCase):
    def test_lesson_001_does_not_apply_to_pick_up_cube_002(self):
        result = run_negative_control_wrong_object()

        self.assertTrue(result["passed"])
        self.assertEqual(result["used_lesson_ids"], [])

    def test_pick_up_cube_002_actions_do_not_include_turn_east(self):
        result = run_negative_control_wrong_object()

        self.assertNotIn("turn(east)", [action["action"] for action in result["actions"]])

    def test_pick_up_cube_002_used_lesson_ids_empty(self):
        self.assertEqual(run_negative_control_wrong_object()["used_lesson_ids"], [])

    def test_lesson_001_does_not_apply_to_push_cube_001(self):
        result = run_negative_control_wrong_action_push()

        self.assertTrue(result["passed"])
        self.assertEqual(result["used_lesson_ids"], [])

    def test_push_cube_001_actions_do_not_include_turn_east(self):
        result = run_negative_control_wrong_action_push()

        self.assertNotIn("turn(east)", [action["action"] for action in result["actions"]])

    def test_lesson_001_does_not_apply_to_inspect_cube_001(self):
        result = run_negative_control_wrong_action_inspect()

        self.assertTrue(result["passed"])
        self.assertEqual(result["used_lesson_ids"], [])

    def test_inspect_cube_001_actions_do_not_include_turn_east(self):
        result = run_negative_control_wrong_action_inspect()

        self.assertNotIn("turn(east)", [action["action"] for action in result["actions"]])

    def test_wrong_condition_lesson_does_not_cause_success_attribution(self):
        result = run_negative_control_wrong_condition()

        self.assertTrue(result["passed"])
        self.assertNotIn("lesson_wrong_condition", result["used_lesson_ids"])
        self.assertFalse(result["success"])

    def test_unrelated_lesson_does_not_apply_to_pick_up_cube_001(self):
        result = run_negative_control_unrelated_lesson()

        self.assertTrue(result["passed"])
        self.assertEqual(result["used_lesson_ids"], [])

    def test_run_phase_minus_one_negative_controls_passed(self):
        self.assertTrue(run_phase_minus_one_negative_controls()["passed"])

    def test_summary_no_wrong_object_generalization(self):
        summary = run_phase_minus_one_negative_controls()["summary"]

        self.assertTrue(summary["no_wrong_object_generalization"])

    def test_summary_no_wrong_action_generalization(self):
        summary = run_phase_minus_one_negative_controls()["summary"]

        self.assertTrue(summary["no_wrong_action_generalization"])

    def test_summary_no_wrong_condition_success(self):
        summary = run_phase_minus_one_negative_controls()["summary"]

        self.assertTrue(summary["no_wrong_condition_success"])

    def test_summary_no_unrelated_lesson_trigger(self):
        summary = run_phase_minus_one_negative_controls()["summary"]

        self.assertTrue(summary["no_unrelated_lesson_trigger"])


if __name__ == "__main__":
    unittest.main()
