import unittest

from ashl_core.fake_sandbox import build_initial_sandbox_state, pick_up, turn
from ashl_core.lesson_store import (
    build_lesson_from_failure,
    disable_lesson,
    enable_lesson,
    select_lesson_for_decision_point,
)


DECISION_POINT = "before_retry_pick_up_cube"


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


def _run_behavior_from_selection(selection):
    state = build_initial_sandbox_state()
    actions = ["observe()"]
    if selection["selected_action"] == "turn(east)":
        state = turn(state, "east")["state"]
        actions.append("turn(east)")
    elif selection["selected_action"] == "turn(west)":
        state = turn(state, "west")["state"]
        actions.append("turn(west)")
    result = pick_up(state, "cube_001")
    actions.append("pick_up(cube_001)")
    return {"result": result["result"], "actions": actions}


class ConflictDetectionRequireReviewTests(unittest.TestCase):
    def test_conflict_detection_requires_review_when_incompatible_lessons_match_same_decision_point(self):
        result = select_lesson_for_decision_point([_lesson_east(), _lesson_west()], DECISION_POINT)

        self.assertTrue(result["conflict_detected"])
        self.assertEqual(result["conflict_resolution"], "require_review")
        self.assertTrue(result["review_required"])
        self.assertEqual(result["review_status"], "pending_human_review")
        self.assertEqual(result["conflicting_lesson_ids"], ["lesson_001", "lesson_002"])
        self.assertEqual(result["conflicting_actions"], ["turn(east)", "turn(west)"])
        self.assertIsNone(result["selected_lesson_id"])
        self.assertIsNone(result["selected_action"])
        self.assertFalse(result["behavior_changed"])

    def test_conflict_does_not_apply_any_lesson_action(self):
        selection = select_lesson_for_decision_point([_lesson_east(), _lesson_west()], DECISION_POINT)
        behavior = _run_behavior_from_selection(selection)

        self.assertNotIn("turn(east)", behavior["actions"])
        self.assertNotIn("turn(west)", behavior["actions"])
        self.assertIsNone(selection["selected_action"])
        self.assertEqual(behavior["result"], "failed")

    def test_disabling_one_conflicting_lesson_restores_single_lesson_causal_control(self):
        lesson_east = _lesson_east()
        lesson_west = _lesson_west()
        conflict = select_lesson_for_decision_point([lesson_east, lesson_west], DECISION_POINT)
        disabled = select_lesson_for_decision_point([lesson_east, disable_lesson(lesson_west)], DECISION_POINT)
        behavior = _run_behavior_from_selection(disabled)

        self.assertTrue(conflict["conflict_detected"])
        self.assertFalse(disabled["conflict_detected"])
        self.assertEqual(disabled["selected_lesson_id"], "lesson_001")
        self.assertEqual(disabled["selected_action"], "turn(east)")
        self.assertEqual(behavior["result"], "success")

    def test_reenabling_conflicting_lesson_restores_require_review(self):
        lesson_east = _lesson_east()
        lesson_west = _lesson_west()
        disabled_west = disable_lesson(lesson_west)
        reenabled_west = enable_lesson(disabled_west)
        result = select_lesson_for_decision_point([lesson_east, reenabled_west], DECISION_POINT)

        self.assertTrue(result["conflict_detected"])
        self.assertEqual(result["conflict_resolution"], "require_review")
        self.assertIsNone(result["selected_action"])
        self.assertFalse(result["behavior_changed"])


if __name__ == "__main__":
    unittest.main()
