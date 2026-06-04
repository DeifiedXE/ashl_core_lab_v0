import unittest

from ashl_core.fake_sandbox import build_initial_sandbox_state, pick_up, turn
from ashl_core.lesson_store import (
    build_lesson_from_failure,
    mark_lesson_stale,
    select_lesson_for_context,
    select_lesson_for_decision_point,
    unmark_lesson_stale,
)


DECISION_POINT = "before_retry_pick_up_cube"


def _lesson_001():
    lesson = build_lesson_from_failure("session_east", pick_up(build_initial_sandbox_state(), "cube_001"))
    lesson["object_id"] = "cube_001"
    return lesson


def _lesson_002():
    return build_lesson_from_failure(
        "session_west",
        {
            "type": "sandbox_action_result",
            "tool": "pick_up",
            "object_id": "cube_001",
            "result": "failed",
            "failure_reason": "not_facing_west",
            "state": build_initial_sandbox_state(),
        },
    )


def _run_behavior_from_context_selection(selection):
    state = build_initial_sandbox_state()
    if selection["selected_action"] == "turn(east)":
        state = turn(state, "east")["state"]
    result = pick_up(state, "cube_001")
    return result["result"]


class ManualStaleMarkingTests(unittest.TestCase):
    def test_manual_stale_lesson_is_skipped_by_selection_helper(self):
        stale_lesson = mark_lesson_stale(_lesson_001())
        result = select_lesson_for_context(
            [stale_lesson],
            {"task": "pick_up", "object_id": "cube_001", "decision_point": DECISION_POINT},
        )

        self.assertIsNone(result["selected_lesson_id"])
        self.assertIsNone(result["selected_action"])
        self.assertEqual(result["skipped_lessons"], [{"lesson_id": "lesson_001", "skipped_reason": "stale"}])
        self.assertFalse(result["conflict_detected"])
        self.assertFalse(result["behavior_changed"])
        self.assertNotEqual(result["selected_action"], "turn(east)")

    def test_unstale_restores_single_lesson_causal_control(self):
        stale_lesson = mark_lesson_stale(_lesson_001())
        stale_result = select_lesson_for_context(
            [stale_lesson],
            {"task": "pick_up", "object_id": "cube_001", "decision_point": DECISION_POINT},
        )
        restored_lesson = unmark_lesson_stale(stale_lesson)
        restored_result = select_lesson_for_context(
            [restored_lesson],
            {"task": "pick_up", "object_id": "cube_001", "decision_point": DECISION_POINT},
        )

        self.assertIsNone(stale_result["selected_lesson_id"])
        self.assertEqual(restored_result["selected_lesson_id"], "lesson_001")
        self.assertEqual(restored_result["selected_action"], "turn(east)")
        self.assertEqual(_run_behavior_from_context_selection(restored_result), "success")

    def test_stale_does_not_delete_or_mutate_lesson_identity(self):
        lesson = _lesson_001()
        stale_lesson = mark_lesson_stale(lesson)

        self.assertEqual(stale_lesson["lesson_id"], lesson["lesson_id"])
        self.assertEqual(stale_lesson["source_failure_reason"], lesson["source_failure_reason"])
        self.assertEqual(stale_lesson["suggested_action_before_retry"], lesson["suggested_action_before_retry"])
        self.assertEqual(stale_lesson["decision_point"], lesson["decision_point"])
        self.assertEqual(stale_lesson["object_id"], lesson["object_id"])

    def test_stale_lesson_does_not_create_conflict(self):
        stale_east = mark_lesson_stale(_lesson_001())
        west = _lesson_002()
        result = select_lesson_for_decision_point([stale_east, west], DECISION_POINT)

        self.assertEqual(result["skipped_lessons"], [{"lesson_id": "lesson_001", "skipped_reason": "stale"}])
        self.assertFalse(result["conflict_detected"])
        self.assertEqual(result["selected_lesson_id"], "lesson_002")
        self.assertEqual(result["selected_action"], "turn(west)")


if __name__ == "__main__":
    unittest.main()
