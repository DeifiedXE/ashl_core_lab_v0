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
from ashl_core.manual_review import create_review_item
from ashl_core.teaching_cli import run_review_approve, run_review_display, run_review_reject


DECISION_POINT = "before_retry_pick_up_cube"
CONTEXT = {"task": "pick_up", "object_id": "cube_001", "decision_point": DECISION_POINT}


def review_item():
    return create_review_item(
        target_type="conflict",
        target_id="conflict_001",
        source_lesson_id="lesson_001",
        candidate_lesson_id="lesson_004",
        reason="conflict_requires_manual_review",
        review_id="review_001",
    )


def lesson_001(stale=False):
    lesson = build_lesson_from_failure("session_east", pick_up(build_initial_sandbox_state(), "cube_001"))
    lesson["object_id"] = "cube_001"
    lesson["stale"] = False
    lesson["stale_reason"] = None
    if stale:
        lesson = mark_lesson_stale(lesson)
        lesson["stale_reason"] = "manual: decision fixture"
    return lesson


def lesson_002():
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


def lesson_004():
    return {
        "lesson_id": "lesson_004",
        "source_session": "manual_fixture",
        "source_failure_reason": "not_facing_east_refined",
        "trigger": {"action": "pick_up", "target_type": "cube"},
        "decision_point": DECISION_POINT,
        "object_id": "cube_001",
        "condition": {"avatar_facing": "east"},
        "suggested_action_before_retry": "turn(east)",
        "status": "active",
        "stale": False,
        "stale_reason": None,
        "confidence": "manual_fixture",
    }


class ManualReviewDecisionCliTests(unittest.TestCase):
    def test_cli_approve_updates_review_metadata(self):
        item = review_item()
        result = run_review_approve([item], notes="approved manually")
        updated = result["review_item"]

        self.assertEqual(result["status"], "ok")
        self.assertEqual(updated["review_state"], "reviewed")
        self.assertEqual(updated["approval_state"], "approved")
        self.assertEqual(updated["id"], item["id"])
        self.assertEqual(updated["source_lesson_id"], item["source_lesson_id"])
        self.assertEqual(updated["candidate_lesson_id"], item["candidate_lesson_id"])
        self.assertEqual(updated["reason"], item["reason"])
        self.assertEqual(updated["notes"], "approved manually")

    def test_cli_reject_updates_review_metadata(self):
        item = review_item()
        result = run_review_reject([item], notes="reject for audit")
        updated = result["review_item"]

        self.assertEqual(result["status"], "ok")
        self.assertEqual(updated["review_state"], "reviewed")
        self.assertEqual(updated["approval_state"], "rejected")
        self.assertEqual(updated["id"], item["id"])
        self.assertEqual(updated["source_lesson_id"], item["source_lesson_id"])
        self.assertEqual(updated["candidate_lesson_id"], item["candidate_lesson_id"])
        self.assertEqual(updated["reason"], item["reason"])
        self.assertEqual(updated["notes"], "reject for audit")

    def test_decision_then_display_shows_result(self):
        approved = run_review_approve([review_item()])["review_items"]
        display = run_review_display(approved)["display"]

        self.assertIn("id: review_001", display)
        self.assertIn("review_state: reviewed", display)
        self.assertIn("approval_state: approved", display)

    def test_missing_review_id_does_not_crash_or_create_item(self):
        item = review_item()
        before = copy.deepcopy([item])
        result = run_review_approve([item], review_id="review_missing")

        self.assertEqual(result["status"], "not_found")
        self.assertEqual(result["error"], "Review item not found: review_missing")
        self.assertEqual(result["review_items"], before)
        self.assertEqual(item, before[0])

    def test_review_decision_does_not_introduce_selection_side_effect(self):
        lessons = [lesson_001(), lesson_004()]
        before = select_lesson_for_context(lessons, CONTEXT)

        run_review_approve([review_item()])
        run_review_reject([review_item()])
        after = select_lesson_for_context(lessons, CONTEXT)

        self.assertEqual(before, after)
        self.assertEqual(before["selected_lesson_id"], after["selected_lesson_id"])

    def test_review_decision_does_not_introduce_conflict_side_effect(self):
        lessons = [lesson_001(), lesson_002()]
        before = select_lesson_for_decision_point(lessons, DECISION_POINT)

        run_review_approve([review_item()])
        run_review_reject([review_item()])
        after = select_lesson_for_decision_point(lessons, DECISION_POINT)

        self.assertEqual(before, after)
        self.assertTrue(after["conflict_detected"])
        self.assertEqual(after["conflict_resolution"], "require_review")

    def test_review_decision_does_not_introduce_activation_side_effect(self):
        link = link_lesson_supersede(lesson_001(stale=True), lesson_004())
        lessons = [link["old_lesson"], link["new_lesson"]]
        before = select_lesson_for_context(lessons, CONTEXT)

        run_review_approve([review_item()])
        run_review_reject([review_item()])
        after = select_lesson_for_context(lessons, CONTEXT)

        self.assertEqual(before, after)
        self.assertTrue(after["supersede_activation"]["activation_applied"])

    def test_review_decision_does_not_modify_lesson_lifecycle_metadata(self):
        link = link_lesson_supersede(lesson_001(stale=True), lesson_004())
        lessons = [link["old_lesson"], link["new_lesson"]]
        before = copy.deepcopy(lessons)

        run_review_approve([review_item()])
        run_review_reject([review_item()])

        self.assertEqual(lessons, before)
        for index in (0, 1):
            self.assertEqual(lessons[index].get("status"), before[index].get("status"))
            self.assertEqual(lessons[index].get("stale"), before[index].get("stale"))
            self.assertEqual(lessons[index].get("stale_reason"), before[index].get("stale_reason"))
            self.assertEqual(lessons[index].get("superseded_by"), before[index].get("superseded_by"))
            self.assertEqual(lessons[index].get("supersedes"), before[index].get("supersedes"))

    def test_cli_help_has_no_lesson_lifecycle_write_commands(self):
        process = subprocess.run(
            [sys.executable, "-m", "ashl_core.teaching_cli", "--help"],
            check=True,
            capture_output=True,
            text=True,
        )
        help_text = process.stdout.lower()

        self.assertIn("run-review-approve", help_text)
        self.assertIn("run-review-reject", help_text)
        for phrase in [
            "resolve-conflict",
            "apply-review",
            "enable-lesson",
            "disable-lesson",
            "mark-stale",
            "unmark-stale",
            "apply-replacement",
        ]:
            self.assertNotIn(phrase, help_text)

    def test_module_cli_missing_review_id_outputs_json(self):
        process = subprocess.run(
            [sys.executable, "-m", "ashl_core.teaching_cli", "run-review-approve", "--review-id", "review_missing"],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(process.stdout)

        self.assertEqual(result["status"], "not_found")
        self.assertEqual(result["error"], "Review item not found: review_missing")


if __name__ == "__main__":
    unittest.main()
