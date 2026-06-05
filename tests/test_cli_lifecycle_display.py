import copy
import json
import subprocess
import sys
import unittest

from ashl_core.fake_sandbox import build_initial_sandbox_state, pick_up
from ashl_core.lesson_store import (
    build_lesson_from_failure,
    link_lesson_supersede,
    mark_lesson_stale,
    select_lesson_for_context,
    select_lesson_for_decision_point,
)
from ashl_core.teaching_cli import run_lifecycle_display


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
        "stale_reason": None,
        "confidence": "manual_fixture",
    }


class CliLifecycleDisplayTests(unittest.TestCase):
    def test_cli_lifecycle_display_shows_stale_metadata(self):
        stale_lesson = mark_lesson_stale(_lesson_001())
        stale_lesson["stale_reason"] = "manual: obsolete wording"
        result = run_lifecycle_display([stale_lesson], CONTEXT)

        self.assertEqual(result["status"], "ok")
        self.assertTrue(result["read_only"])
        self.assertIn("id: lesson_001", result["display"])
        self.assertIn("stale: true", result["display"])
        self.assertIn("stale_reason: manual: obsolete wording", result["display"])
        self.assertEqual(result["lessons"][0]["skipped_reason"], "stale")

    def test_cli_lifecycle_display_shows_supersede_metadata(self):
        link = link_lesson_supersede(_lesson_001(), _lesson_004())
        result = run_lifecycle_display([link["old_lesson"], link["new_lesson"]], CONTEXT)

        display = result["display"]
        self.assertIn("id: lesson_001", display)
        self.assertIn("superseded_by: lesson_004", display)
        self.assertIn("id: lesson_004", display)
        self.assertIn("supersedes: lesson_001", display)

    def test_cli_lifecycle_display_does_not_change_lesson_state(self):
        stale_old = mark_lesson_stale(_lesson_001())
        stale_old["stale_reason"] = "manual: obsolete wording"
        link = link_lesson_supersede(stale_old, _lesson_004())
        lessons = [link["old_lesson"], link["new_lesson"]]
        before = copy.deepcopy(lessons)

        run_lifecycle_display(lessons, CONTEXT)

        self.assertEqual(lessons, before)
        self.assertEqual(lessons[0]["status"], before[0]["status"])
        self.assertEqual(lessons[0]["stale"], before[0]["stale"])
        self.assertEqual(lessons[0]["stale_reason"], before[0]["stale_reason"])
        self.assertEqual(lessons[0]["superseded_by"], before[0]["superseded_by"])
        self.assertEqual(lessons[1]["supersedes"], before[1]["supersedes"])

    def test_cli_lifecycle_display_does_not_change_selection_behavior(self):
        lesson = _lesson_001()
        before = select_lesson_for_context([lesson], CONTEXT)
        display = run_lifecycle_display([lesson], CONTEXT)
        after = select_lesson_for_context([lesson], CONTEXT)

        self.assertEqual(before, after)
        self.assertEqual(before["selected_lesson_id"], "lesson_001")
        self.assertEqual(display["selection_trace"], before)

    def test_cli_lifecycle_display_does_not_change_conflict_behavior(self):
        stale_old = mark_lesson_stale(_lesson_001())
        stale_old["stale_reason"] = "manual: obsolete wording"
        link = link_lesson_supersede(stale_old, _lesson_004())
        lessons = [link["old_lesson"], link["new_lesson"], _lesson_002()]
        before = select_lesson_for_decision_point(lessons, DECISION_POINT)
        display = run_lifecycle_display(lessons, CONTEXT)
        after = select_lesson_for_decision_point(lessons, DECISION_POINT)

        self.assertEqual(before, after)
        self.assertFalse(after["conflict_detected"])
        self.assertEqual(after["selected_lesson_id"], "lesson_002")
        self.assertEqual(after["skipped_lessons"], [{"lesson_id": "lesson_001", "skipped_reason": "stale"}])
        self.assertFalse(display["conflict_check"]["conflict_detected"])

    def test_cli_has_no_lifecycle_write_operation(self):
        process = subprocess.run(
            [sys.executable, "-m", "ashl_core.teaching_cli", "--help"],
            check=True,
            capture_output=True,
            text=True,
        )
        help_text = process.stdout.lower()

        self.assertIn("run-lifecycle-display", help_text)
        forbidden = [
            "mark-stale",
            "unmark-stale",
            "create-supersede",
            "link-supersede",
            "supersede-activation",
            "enable-replacement",
            "disable-old-lesson",
        ]
        for phrase in forbidden:
            self.assertNotIn(phrase, help_text)

    def test_module_cli_lifecycle_display_outputs_json(self):
        process = subprocess.run(
            [sys.executable, "-m", "ashl_core.teaching_cli", "run-lifecycle-display"],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(process.stdout)

        self.assertEqual(result["command"], "run-lifecycle-display")
        self.assertTrue(result["read_only"])
        self.assertIn("Lesson Lifecycle", result["display"])


if __name__ == "__main__":
    unittest.main()
