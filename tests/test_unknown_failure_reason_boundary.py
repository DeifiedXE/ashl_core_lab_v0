import tempfile
import unittest
from pathlib import Path

from ashl_core.fake_sandbox import build_initial_sandbox_state, pick_up
from ashl_core.lesson_runner import run_session_2b_without_lesson
from ashl_core.lesson_store import find_applicable_lesson, generate_lesson_from_failure


UNKNOWN_FAILURE_REASON = "unmapped_obstacle_shadow"


def _unknown_failure_result():
    return {
        "type": "sandbox_action_result",
        "tool": "pick_up",
        "object_id": "cube_001",
        "result": "failed",
        "failure_reason": UNKNOWN_FAILURE_REASON,
        "state": build_initial_sandbox_state(),
    }


class UnknownFailureReasonBoundaryTests(unittest.TestCase):
    def test_unknown_failure_reason_is_explicitly_marked_and_does_not_generate_action(self):
        result = generate_lesson_from_failure("session_unknown", _unknown_failure_result())

        self.assertEqual(result["trace"]["generation_status"], "unknown_failure_reason")
        self.assertEqual(result["trace"]["reason"], "unknown_failure_reason")
        self.assertIsNone(result["trace"]["executable_action"])

    def test_unknown_failure_reason_generates_no_active_lesson(self):
        result = generate_lesson_from_failure("session_unknown", _unknown_failure_result())

        self.assertIsNone(result["lesson"])

    def test_unknown_failure_reason_does_not_fallback_to_known_reason(self):
        result = generate_lesson_from_failure("session_unknown", _unknown_failure_result())

        self.assertEqual(result["trace"]["source_failure_reason"], UNKNOWN_FAILURE_REASON)
        self.assertNotEqual(result["trace"]["source_failure_reason"], "not_facing_east")

    def test_unknown_failure_reason_does_not_generate_turn_east(self):
        result = generate_lesson_from_failure("session_unknown", _unknown_failure_result())

        self.assertNotEqual(result["trace"]["executable_action"], "turn(east)")
        self.assertNotIn("turn(east)", str(result))

    def test_unknown_failure_reason_does_not_change_behavior(self):
        result = generate_lesson_from_failure("session_unknown", _unknown_failure_result())
        lesson_list = [] if result["lesson"] is None else [result["lesson"]]

        self.assertIsNone(find_applicable_lesson(lesson_list, {"action": "pick_up", "object_id": "cube_001"}))
        control = run_session_2b_without_lesson()
        self.assertFalse(control["success"])
        self.assertEqual([action["action"] for action in control["actions"]], ["observe()", "pick_up(cube_001)"])

    def test_unknown_failure_reason_has_no_jsonl_side_effects(self):
        with tempfile.TemporaryDirectory() as tmp:
            generate_lesson_from_failure("session_unknown", _unknown_failure_result())

            self.assertEqual(list(Path(tmp).glob("*.jsonl")), [])

    def test_known_failure_reason_still_generates_supported_lesson(self):
        known_failure = pick_up(build_initial_sandbox_state(), "cube_001")
        result = generate_lesson_from_failure("session_1", known_failure)

        self.assertEqual(result["trace"]["generation_status"], "supported_failure_reason")
        self.assertEqual(result["lesson"]["lesson_id"], "lesson_001")
        self.assertEqual(result["lesson"]["suggested_action_before_retry"], "turn(east)")


if __name__ == "__main__":
    unittest.main()
