import unittest

from ashl_core.fake_sandbox import build_initial_sandbox_state, pick_up
from ashl_core.lesson_store import build_lesson_from_failure


VOLATILE_FIELDS = {"id", "lesson_id", "created_at", "timestamp", "run_id"}


def _known_failure_result():
    return pick_up(build_initial_sandbox_state(), "cube_001")


def _generate_known_failure_lesson():
    return build_lesson_from_failure("session_1", _known_failure_result())


def _normalized_lesson(lesson):
    return {key: value for key, value in lesson.items() if key not in VOLATILE_FIELDS}


class LessonGenerationDeterminismTests(unittest.TestCase):
    def test_known_failure_reason_generates_deterministic_lesson(self):
        lessons = [_generate_known_failure_lesson() for _ in range(3)]
        normalized = [_normalized_lesson(lesson) for lesson in lessons]

        self.assertEqual(normalized[0], normalized[1])
        self.assertEqual(normalized[1], normalized[2])
        self.assertEqual(normalized[0]["source_failure_reason"], "not_facing_east")
        self.assertEqual(normalized[0]["suggested_action_before_retry"], "turn(east)")
        self.assertEqual(normalized[0]["condition"], {"avatar_facing": "east"})
        self.assertEqual(normalized[0]["status"], "active")
        self.assertEqual(normalized[0]["trigger"], {"action": "pick_up", "target_type": "cube"})


if __name__ == "__main__":
    unittest.main()
