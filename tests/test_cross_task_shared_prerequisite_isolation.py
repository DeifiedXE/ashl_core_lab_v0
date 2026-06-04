import unittest

from ashl_core.fake_sandbox import build_initial_sandbox_state, pick_up
from ashl_core.lesson_store import build_lesson_from_failure, select_lesson_for_context, select_lesson_for_decision_point


DECISION_POINT = "before_retry_pick_up_cube"


def _lesson_001():
    lesson = build_lesson_from_failure("session_cube_001", pick_up(build_initial_sandbox_state(), "cube_001"))
    lesson["object_id"] = "cube_001"
    return lesson


def _lesson_003():
    return {
        "lesson_id": "lesson_003",
        "source_session": "session_cube_002",
        "source_failure_reason": "not_facing_east_for_cube_002",
        "trigger": {"action": "pick_up", "target_type": "cube"},
        "decision_point": DECISION_POINT,
        "object_id": "cube_002",
        "condition": {"avatar_facing": "east"},
        "suggested_action_before_retry": "turn(east)",
        "status": "active",
        "confidence": "tested_once",
    }


class CrossTaskSharedPrerequisiteIsolationTests(unittest.TestCase):
    def test_shared_prerequisite_selects_cube_001_lesson_only(self):
        result = select_lesson_for_context(
            [_lesson_001(), _lesson_003()],
            {"task": "pick_up", "object_id": "cube_001", "decision_point": DECISION_POINT},
        )

        self.assertEqual(result["selected_lesson_id"], "lesson_001")
        self.assertEqual(result["selected_action"], "turn(east)")
        self.assertNotIn("lesson_003", result["matched_lesson_ids"])
        self.assertFalse(result["conflict_detected"])

    def test_shared_prerequisite_selects_cube_002_lesson_only(self):
        result = select_lesson_for_context(
            [_lesson_001(), _lesson_003()],
            {"task": "pick_up", "object_id": "cube_002", "decision_point": DECISION_POINT},
        )

        self.assertEqual(result["selected_lesson_id"], "lesson_003")
        self.assertEqual(result["selected_action"], "turn(east)")
        self.assertNotIn("lesson_001", result["matched_lesson_ids"])
        self.assertFalse(result["conflict_detected"])

    def test_shared_prerequisite_does_not_create_false_conflict(self):
        cube_001 = select_lesson_for_context(
            [_lesson_001(), _lesson_003()],
            {"task": "pick_up", "object_id": "cube_001", "decision_point": DECISION_POINT},
        )
        cube_002 = select_lesson_for_context(
            [_lesson_001(), _lesson_003()],
            {"task": "pick_up", "object_id": "cube_002", "decision_point": DECISION_POINT},
        )

        self.assertEqual(cube_001["active_lesson_ids"], ["lesson_001", "lesson_003"])
        self.assertEqual(cube_002["active_lesson_ids"], ["lesson_001", "lesson_003"])
        self.assertFalse(cube_001["conflict_detected"])
        self.assertFalse(cube_002["conflict_detected"])

    def test_incompatible_decision_point_conflict_still_detects(self):
        lesson_east = _lesson_001()
        lesson_west = build_lesson_from_failure(
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
        result = select_lesson_for_decision_point([lesson_east, lesson_west], DECISION_POINT)

        self.assertTrue(result["conflict_detected"])
        self.assertEqual(result["conflict_resolution"], "require_review")


if __name__ == "__main__":
    unittest.main()
