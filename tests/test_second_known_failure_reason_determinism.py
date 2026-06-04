import unittest

from ashl_core.fake_sandbox import build_initial_sandbox_state
from ashl_core.lesson_store import build_lesson_from_failure, generate_lesson_from_failure


VOLATILE_FIELDS = {"id", "lesson_id", "created_at", "timestamp", "run_id"}


def _west_failure_result():
    return {
        "type": "sandbox_action_result",
        "tool": "pick_up",
        "object_id": "cube_001",
        "result": "failed",
        "failure_reason": "not_facing_west",
        "state": build_initial_sandbox_state(),
    }


def _normalized_lesson(lesson):
    return {key: value for key, value in lesson.items() if key not in VOLATILE_FIELDS}


class SecondKnownFailureReasonDeterminismTests(unittest.TestCase):
    def test_second_known_failure_reason_generates_deterministic_lesson(self):
        lessons = [build_lesson_from_failure("session_1", _west_failure_result()) for _ in range(3)]
        normalized = [_normalized_lesson(lesson) for lesson in lessons]

        self.assertEqual(normalized[0], normalized[1])
        self.assertEqual(normalized[1], normalized[2])
        self.assertEqual(normalized[0]["source_failure_reason"], "not_facing_west")
        self.assertEqual(normalized[0]["suggested_action_before_retry"], "turn(west)")
        self.assertEqual(normalized[0]["condition"], {"avatar_facing": "west"})
        self.assertEqual(normalized[0]["status"], "active")
        self.assertEqual(normalized[0]["trigger"], {"action": "pick_up", "target_type": "cube"})

    def test_second_known_failure_reason_is_not_unknown(self):
        result = generate_lesson_from_failure("session_1", _west_failure_result())

        self.assertEqual(result["trace"]["generation_status"], "supported_failure_reason")
        self.assertNotEqual(result["trace"]["generation_status"], "unknown_failure_reason")

    def test_second_known_failure_reason_does_not_generate_turn_east(self):
        lesson = build_lesson_from_failure("session_1", _west_failure_result())

        self.assertEqual(lesson["suggested_action_before_retry"], "turn(west)")
        self.assertNotEqual(lesson["suggested_action_before_retry"], "turn(east)")


if __name__ == "__main__":
    unittest.main()
