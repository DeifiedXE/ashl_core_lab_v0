import unittest

from ashl_core.lesson_runner import run_session_2b2_without_lesson_with_turn_tool, run_session_2b_without_lesson
from ashl_core.prompt_leakage_check import build_decision_input_snapshot, check_leakage


class PromptLeakageControlTests(unittest.TestCase):
    def _text(self, snapshot):
        return " ".join(
            [
                str(snapshot["prompt_text_or_decision_input"]),
                str(snapshot["loaded_lesson_ids"]),
                str(snapshot["visible_state_keys"]),
                str(snapshot["visible_history_ids"]),
            ]
        ).lower()

    def test_2b_snapshot_does_not_contain_lesson_001(self):
        snapshot = run_session_2b_without_lesson()["decision_input_snapshot"]

        self.assertNotIn("lesson_001", self._text(snapshot))

    def test_2b_snapshot_does_not_contain_east(self):
        snapshot = run_session_2b_without_lesson()["decision_input_snapshot"]

        self.assertNotIn("east", self._text(snapshot))

    def test_2b_snapshot_does_not_contain_avatar_facing(self):
        snapshot = run_session_2b_without_lesson()["decision_input_snapshot"]

        self.assertNotIn("avatar_facing", self._text(snapshot))

    def test_2b_snapshot_does_not_contain_failure_reason(self):
        snapshot = run_session_2b_without_lesson()["decision_input_snapshot"]

        self.assertNotIn("failure_reason", self._text(snapshot))

    def test_2b_leakage_check_passed(self):
        snapshot = run_session_2b_without_lesson()["decision_input_snapshot"]

        self.assertTrue(snapshot["leakage_check"]["passed"])

    def test_2b2_snapshot_can_contain_turn_tool(self):
        snapshot = run_session_2b2_without_lesson_with_turn_tool()["decision_input_snapshot"]

        self.assertIn("turn", snapshot["available_actions"])
        self.assertIn("turn", snapshot["prompt_text_or_decision_input"])

    def test_2b2_snapshot_does_not_contain_east(self):
        snapshot = run_session_2b2_without_lesson_with_turn_tool()["decision_input_snapshot"]

        self.assertNotIn("east", self._text(snapshot))

    def test_2b2_snapshot_does_not_contain_facing(self):
        snapshot = run_session_2b2_without_lesson_with_turn_tool()["decision_input_snapshot"]

        self.assertNotIn("facing", self._text(snapshot))

    def test_2b2_snapshot_does_not_contain_failure_reason(self):
        snapshot = run_session_2b2_without_lesson_with_turn_tool()["decision_input_snapshot"]

        self.assertNotIn("failure_reason", self._text(snapshot))

    def test_2b2_leakage_check_passed(self):
        snapshot = run_session_2b2_without_lesson_with_turn_tool()["decision_input_snapshot"]

        self.assertTrue(snapshot["leakage_check"]["passed"])

    def test_snapshot_with_east_fails_leakage_check(self):
        snapshot = build_decision_input_snapshot(
            "bad_run",
            "session_2b",
            "2B",
            [],
            {"object_id": "cube_001"},
            ["observe", "pick_up"],
            decision_input="try east before pickup",
        )

        self.assertFalse(check_leakage(snapshot)["passed"])

    def test_snapshot_with_lesson_001_fails_leakage_check(self):
        snapshot = build_decision_input_snapshot(
            "bad_run",
            "session_2b",
            "2B",
            ["lesson_001"],
            {"object_id": "cube_001"},
            ["observe", "pick_up"],
        )

        self.assertFalse(check_leakage(snapshot)["passed"])


if __name__ == "__main__":
    unittest.main()
