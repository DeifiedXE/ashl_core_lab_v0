import unittest

from ashl_core.fake_sandbox import build_initial_sandbox_state, pick_up
from ashl_core.lesson_store import (
    build_lesson_from_failure,
    link_lesson_supersede,
    mark_lesson_stale,
    select_lesson_for_context,
    select_lesson_for_decision_point,
)


DECISION_POINT = "before_retry_pick_up_cube"
CONTEXT = {"task": "pick_up", "object_id": "cube_001", "decision_point": DECISION_POINT}


def _lesson_001():
    lesson = build_lesson_from_failure("session_east", pick_up(build_initial_sandbox_state(), "cube_001"))
    lesson["object_id"] = "cube_001"
    lesson["stale"] = False
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


def _lesson_004():
    return {
        "lesson_id": "lesson_004",
        "source_session": "manual_fixture",
        "source_failure_reason": "not_facing_east_refined",
        "trigger": {"action": "pick_up", "target_type": "cube"},
        "decision_point": DECISION_POINT,
        "object_id": "cube_001",
        "condition": {"avatar_facing": "east"},
        "suggested_action_before_retry": "turn(east)",
        "status": "inactive",
        "stale": False,
        "confidence": "manual_fixture",
    }


class SupersedeLinkTests(unittest.TestCase):
    def test_supersede_link_records_bidirectional_relation(self):
        result = link_lesson_supersede(_lesson_001(), _lesson_004())

        self.assertTrue(result["trace"]["supersede_linked"])
        self.assertEqual(result["old_lesson"]["superseded_by"], "lesson_004")
        self.assertEqual(result["new_lesson"]["supersedes"], "lesson_001")
        self.assertEqual(result["trace"]["old_superseded_by"], "lesson_004")
        self.assertEqual(result["trace"]["new_supersedes"], "lesson_001")

    def test_supersede_link_does_not_change_status(self):
        old_lesson = _lesson_001()
        new_lesson = _lesson_004()
        result = link_lesson_supersede(old_lesson, new_lesson)

        self.assertEqual(result["old_lesson"]["status"], old_lesson["status"])
        self.assertEqual(result["new_lesson"]["status"], new_lesson["status"])
        self.assertFalse(result["trace"]["old_status_changed"])
        self.assertFalse(result["trace"]["new_status_changed"])
        self.assertFalse(result["trace"]["status_changed"])

    def test_supersede_link_does_not_change_selection_behavior(self):
        before = select_lesson_for_context([_lesson_001(), _lesson_004()], CONTEXT)
        link = link_lesson_supersede(_lesson_001(), _lesson_004())
        after = select_lesson_for_context([link["old_lesson"], link["new_lesson"]], CONTEXT)

        self.assertEqual(before["selected_lesson_id"], "lesson_001")
        self.assertEqual(after["selected_lesson_id"], "lesson_001")
        self.assertEqual(after["selected_action"], "turn(east)")
        self.assertFalse(link["trace"]["selection_behavior_changed"])

    def test_supersede_link_does_not_override_stale_behavior(self):
        stale_old = mark_lesson_stale(_lesson_001())
        link = link_lesson_supersede(stale_old, _lesson_004())
        result = select_lesson_for_context([link["old_lesson"], link["new_lesson"]], CONTEXT)

        self.assertIsNone(result["selected_lesson_id"])
        self.assertIsNone(result["selected_action"])
        self.assertEqual(result["skipped_lessons"], [{"lesson_id": "lesson_001", "skipped_reason": "stale"}])
        self.assertNotEqual(result["selected_lesson_id"], "lesson_004")

    def test_stale_lesson_with_supersede_link_does_not_participate_in_conflict(self):
        stale_old = mark_lesson_stale(_lesson_001())
        link = link_lesson_supersede(stale_old, _lesson_004())
        west = _lesson_002()
        result = select_lesson_for_decision_point([link["old_lesson"], link["new_lesson"], west], DECISION_POINT)

        self.assertEqual(result["skipped_lessons"], [{"lesson_id": "lesson_001", "skipped_reason": "stale"}])
        self.assertFalse(result["conflict_detected"])
        self.assertEqual(result["selected_lesson_id"], "lesson_002")
        self.assertEqual(result["selected_action"], "turn(west)")


if __name__ == "__main__":
    unittest.main()
