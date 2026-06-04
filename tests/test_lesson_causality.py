import unittest

from ashl_core.fake_sandbox import build_initial_sandbox_state, pick_up
from ashl_core.lesson_runner import run_lesson_causality_test
from ashl_core.lesson_store import (
    build_lesson_from_failure,
    disable_lesson,
    enable_lesson,
    find_applicable_lesson,
    remove_lesson,
    set_lesson_status,
)


class LessonCausalityTests(unittest.TestCase):
    def _lesson(self):
        failure = pick_up(build_initial_sandbox_state(), "cube_001")
        return build_lesson_from_failure("session_1", failure)

    def _actions(self, result_section):
        return [action["action"] for action in result_section["actions"]]

    def test_set_lesson_status_can_disable_active_lesson(self):
        disabled = set_lesson_status(self._lesson(), "disabled")

        self.assertEqual(disabled["status"], "disabled")

    def test_disable_lesson_makes_it_inapplicable(self):
        lesson = disable_lesson(self._lesson())

        self.assertIsNone(find_applicable_lesson([lesson], {"action": "pick_up", "object_id": "cube_001"}))

    def test_enable_lesson_makes_it_applicable(self):
        lesson = enable_lesson(disable_lesson(self._lesson()))

        self.assertEqual(
            find_applicable_lesson([lesson], {"action": "pick_up", "object_id": "cube_001"})["lesson_id"],
            "lesson_001",
        )

    def test_remove_lesson_removes_lesson_001(self):
        lessons = remove_lesson([self._lesson()], "lesson_001")

        self.assertEqual(lessons, [])

    def test_run_lesson_causality_test_passed(self):
        self.assertTrue(run_lesson_causality_test()["passed"])

    def test_active_group_success(self):
        result = run_lesson_causality_test()

        self.assertEqual(result["active"]["result"], "success")

    def test_active_group_uses_lesson_001(self):
        result = run_lesson_causality_test()

        self.assertEqual(result["active"]["used_lesson_ids"], ["lesson_001"])

    def test_disabled_group_failed(self):
        result = run_lesson_causality_test()

        self.assertEqual(result["disabled"]["result"], "failed")

    def test_disabled_group_uses_no_lesson(self):
        result = run_lesson_causality_test()

        self.assertEqual(result["disabled"]["used_lesson_ids"], [])

    def test_re_enabled_group_success(self):
        result = run_lesson_causality_test()

        self.assertEqual(result["re_enabled"]["result"], "success")

    def test_re_enabled_group_uses_lesson_001(self):
        result = run_lesson_causality_test()

        self.assertEqual(result["re_enabled"]["used_lesson_ids"], ["lesson_001"])

    def test_removed_group_failed(self):
        result = run_lesson_causality_test()

        self.assertEqual(result["removed"]["result"], "failed")

    def test_removed_group_uses_no_lesson(self):
        result = run_lesson_causality_test()

        self.assertEqual(result["removed"]["used_lesson_ids"], [])

    def test_disabled_group_actions_do_not_include_turn_east(self):
        result = run_lesson_causality_test()

        self.assertNotIn("turn(east)", self._actions(result["disabled"]))

    def test_removed_group_actions_do_not_include_turn_east(self):
        result = run_lesson_causality_test()

        self.assertNotIn("turn(east)", self._actions(result["removed"]))

    def test_summary_causal_control_passed(self):
        result = run_lesson_causality_test()

        self.assertTrue(result["summary"]["causal_control_passed"])

    def test_unknown_status_returns_none(self):
        self.assertIsNone(set_lesson_status(self._lesson(), "archived"))


if __name__ == "__main__":
    unittest.main()
