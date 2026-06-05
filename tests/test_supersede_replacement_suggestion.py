import subprocess
import sys
import unittest

from ashl_core.fake_sandbox import build_initial_sandbox_state, pick_up
from ashl_core.lesson_store import (
    build_lesson_from_failure,
    build_replacement_suggestions,
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


def _lesson_004(status="active", stale=False, object_id="cube_001", decision_point=DECISION_POINT):
    return {
        "lesson_id": "lesson_004",
        "source_session": "manual_fixture",
        "source_failure_reason": "not_facing_east_refined",
        "trigger": {"action": "pick_up", "target_type": "cube"},
        "decision_point": decision_point,
        "object_id": object_id,
        "condition": {"avatar_facing": "east"},
        "suggested_action_before_retry": "turn(east)",
        "status": status,
        "stale": stale,
        "confidence": "manual_fixture",
    }


class SupersedeReplacementSuggestionTests(unittest.TestCase):
    def test_stale_lesson_with_superseded_by_produces_replacement_suggestion(self):
        link = link_lesson_supersede(mark_lesson_stale(_lesson_001()), _lesson_004())
        result = select_lesson_for_context([link["old_lesson"], link["new_lesson"]], CONTEXT)
        suggestion = result["replacement_suggestions"][0]

        self.assertEqual(suggestion["source_lesson_id"], "lesson_001")
        self.assertEqual(suggestion["source_skipped_reason"], "stale")
        self.assertEqual(suggestion["superseded_by"], "lesson_004")
        self.assertEqual(suggestion["candidate_lesson_id"], "lesson_004")
        self.assertTrue(suggestion["candidate_exists"])
        self.assertEqual(suggestion["candidate_status"], "active")
        self.assertFalse(suggestion["candidate_stale"])
        self.assertTrue(suggestion["candidate_eligible"])
        self.assertFalse(suggestion["activation_applied"])
        self.assertEqual(suggestion["reason"], "trace_only_supersede_replacement_suggestion")

    def test_replacement_suggestion_does_not_change_selection_result(self):
        stale_old_without_link = mark_lesson_stale(_lesson_001())
        replacement = _lesson_004()
        before = select_lesson_for_context([stale_old_without_link, replacement], CONTEXT)
        link = link_lesson_supersede(stale_old_without_link, replacement)
        after = select_lesson_for_context([link["old_lesson"], link["new_lesson"]], CONTEXT)

        self.assertEqual(before["selected_lesson_id"], after["selected_lesson_id"])
        self.assertEqual(before["selected_action"], after["selected_action"])
        self.assertEqual(after["selected_lesson_id"], "lesson_004")
        self.assertFalse(after["replacement_suggestions"][0]["activation_applied"])

    def test_missing_candidate_reports_missing_without_activation(self):
        old = mark_lesson_stale(_lesson_001())
        old["superseded_by"] = "lesson_missing"
        result = select_lesson_for_context([old], CONTEXT)
        suggestion = result["replacement_suggestions"][0]

        self.assertFalse(suggestion["candidate_exists"])
        self.assertFalse(suggestion["candidate_eligible"])
        self.assertFalse(suggestion["activation_applied"])
        self.assertEqual(suggestion["reason"], "replacement_candidate_missing")

    def test_stale_candidate_reports_ineligible_without_activation(self):
        link = link_lesson_supersede(mark_lesson_stale(_lesson_001()), mark_lesson_stale(_lesson_004()))
        result = select_lesson_for_context([link["old_lesson"], link["new_lesson"]], CONTEXT)
        suggestion = result["replacement_suggestions"][0]

        self.assertTrue(suggestion["candidate_exists"])
        self.assertTrue(suggestion["candidate_stale"])
        self.assertFalse(suggestion["candidate_eligible"])
        self.assertFalse(suggestion["activation_applied"])
        self.assertEqual(suggestion["reason"], "replacement_candidate_stale")

    def test_non_stale_superseded_lesson_does_not_produce_replacement_suggestion(self):
        link = link_lesson_supersede(_lesson_001(), _lesson_004(status="inactive"))
        result = select_lesson_for_context([link["old_lesson"], link["new_lesson"]], CONTEXT)

        self.assertEqual(result["replacement_suggestions"], [])
        self.assertEqual(result["selected_lesson_id"], "lesson_001")

    def test_replacement_suggestion_does_not_change_conflict_behavior(self):
        stale_old = mark_lesson_stale(_lesson_001())
        replacement = _lesson_004(status="inactive")
        base_link = link_lesson_supersede(stale_old, replacement)
        lessons = [base_link["old_lesson"], base_link["new_lesson"], _lesson_002()]
        before = select_lesson_for_decision_point(lessons, DECISION_POINT)
        after = select_lesson_for_decision_point(lessons, DECISION_POINT)

        self.assertEqual(before, after)
        self.assertFalse(after["conflict_detected"])
        self.assertEqual(after["selected_lesson_id"], "lesson_002")
        self.assertEqual(after["replacement_suggestions"][0]["candidate_status"], "inactive")
        self.assertFalse(after["replacement_suggestions"][0]["activation_applied"])

    def test_helper_only_uses_stale_skips(self):
        old = _lesson_001()
        old["superseded_by"] = "lesson_004"
        suggestions = build_replacement_suggestions([old, _lesson_004()], [])

        self.assertEqual(suggestions, [])

    def test_cli_lifecycle_display_can_show_read_only_replacement_suggestion(self):
        result = run_lifecycle_display()

        self.assertTrue(result["read_only"])
        self.assertIn("replacement_suggestions", result)
        self.assertEqual(result["replacement_suggestions"][0]["source_lesson_id"], "lesson_001")
        self.assertFalse(result["replacement_suggestions"][0]["activation_applied"])
        self.assertIn("Replacement Suggestions", result["display"])

    def test_cli_has_no_replacement_write_or_activation_command(self):
        process = subprocess.run(
            [sys.executable, "-m", "ashl_core.teaching_cli", "--help"],
            check=True,
            capture_output=True,
            text=True,
        )
        help_text = process.stdout.lower()

        forbidden = [
            "apply-replacement",
            "activate-supersede",
            "replacement-apply",
            "mark-stale",
            "unmark-stale",
            "link-supersede",
        ]
        for phrase in forbidden:
            self.assertNotIn(phrase, help_text)


if __name__ == "__main__":
    unittest.main()
