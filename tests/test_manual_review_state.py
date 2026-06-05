import copy
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
from ashl_core.manual_review import (
    build_review_trace,
    create_review_item,
    get_review_item,
    list_review_items,
    mark_review_approved,
    mark_review_rejected,
)


DECISION_POINT = "before_retry_pick_up_cube"
CONTEXT = {"task": "pick_up", "object_id": "cube_001", "decision_point": DECISION_POINT}


def lesson_001(stale=False):
    lesson = build_lesson_from_failure("session_east", pick_up(build_initial_sandbox_state(), "cube_001"))
    lesson["object_id"] = "cube_001"
    lesson["stale"] = False
    lesson["stale_reason"] = None
    if stale:
        lesson = mark_lesson_stale(lesson)
        lesson["stale_reason"] = "manual: review fixture"
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


def lesson_004(status="active", stale=False):
    return {
        "lesson_id": "lesson_004",
        "source_session": "manual_fixture",
        "source_failure_reason": "not_facing_east_refined",
        "trigger": {"action": "pick_up", "target_type": "cube"},
        "decision_point": DECISION_POINT,
        "object_id": "cube_001",
        "condition": {"avatar_facing": "east"},
        "suggested_action_before_retry": "turn(east)",
        "status": status,
        "stale": stale,
        "stale_reason": None,
        "confidence": "manual_fixture",
    }


def review_item():
    return create_review_item(
        target_type="conflict",
        target_id="conflict_001",
        source_lesson_id="lesson_001",
        candidate_lesson_id="lesson_004",
        reason="conflict_requires_manual_review",
        review_id="review_001",
    )


class ManualReviewStateTests(unittest.TestCase):
    def test_create_pending_review_item(self):
        item = review_item()

        self.assertEqual(item["id"], "review_001")
        self.assertEqual(item["review_state"], "pending_review")
        self.assertEqual(item["approval_state"], "unreviewed")
        self.assertEqual(item["reason"], "conflict_requires_manual_review")
        self.assertEqual(item["source_lesson_id"], "lesson_001")
        self.assertEqual(item["candidate_lesson_id"], "lesson_004")

    def test_can_query_review_item(self):
        item = review_item()
        items = [item]

        self.assertEqual(get_review_item(items, "review_001"), item)
        self.assertIn(item, list_review_items(items))
        self.assertIsNone(get_review_item(items, "missing"))
        self.assertEqual(build_review_trace(item)["review_state"], "pending_review")

    def test_approval_and_rejection_only_change_review_metadata(self):
        item = review_item()
        lesson = lesson_001()
        before_lesson = copy.deepcopy(lesson)
        approved = mark_review_approved(item)
        rejected = mark_review_rejected(item)

        self.assertEqual(approved["review_state"], "reviewed")
        self.assertEqual(approved["approval_state"], "approved")
        self.assertEqual(rejected["approval_state"], "rejected")
        self.assertEqual(lesson, before_lesson)

    def test_review_metadata_does_not_change_selection(self):
        lessons = [lesson_001(), lesson_004(status="inactive")]
        before = select_lesson_for_context(lessons, CONTEXT)
        item = mark_review_approved(review_item())
        after = select_lesson_for_context(lessons, CONTEXT)

        self.assertEqual(before, after)
        self.assertEqual(item["approval_state"], "approved")
        self.assertEqual(after["selected_lesson_id"], "lesson_001")

    def test_review_metadata_does_not_change_conflict(self):
        lessons = [lesson_001(), lesson_002()]
        before = select_lesson_for_decision_point(lessons, DECISION_POINT)
        item = mark_review_approved(review_item())
        after = select_lesson_for_decision_point(lessons, DECISION_POINT)

        self.assertEqual(before, after)
        self.assertEqual(item["approval_state"], "approved")
        self.assertTrue(after["conflict_detected"])
        self.assertEqual(after["conflict_resolution"], "require_review")

    def test_review_metadata_does_not_change_strict_supersede_activation(self):
        link = link_lesson_supersede(lesson_001(stale=True), lesson_004())
        lessons = [link["old_lesson"], link["new_lesson"]]
        before = select_lesson_for_context(lessons, CONTEXT)
        item = mark_review_approved(review_item())
        after = select_lesson_for_context(lessons, CONTEXT)

        self.assertEqual(before, after)
        self.assertEqual(item["approval_state"], "approved")
        self.assertTrue(after["supersede_activation"]["activation_applied"])

    def test_review_item_does_not_modify_lifecycle_metadata(self):
        link = link_lesson_supersede(lesson_001(stale=True), lesson_004())
        lessons = [link["old_lesson"], link["new_lesson"]]
        before = copy.deepcopy(lessons)

        mark_review_approved(review_item())

        self.assertEqual(lessons, before)
        for index in (0, 1):
            self.assertEqual(lessons[index].get("status"), before[index].get("status"))
            self.assertEqual(lessons[index].get("stale"), before[index].get("stale"))
            self.assertEqual(lessons[index].get("stale_reason"), before[index].get("stale_reason"))
            self.assertEqual(lessons[index].get("superseded_by"), before[index].get("superseded_by"))
            self.assertEqual(lessons[index].get("supersedes"), before[index].get("supersedes"))

    def test_review_trace_is_metadata_only(self):
        trace = build_review_trace(review_item())

        self.assertTrue(trace["metadata_only"])
        self.assertFalse(trace["selection_behavior_changed"])
        self.assertFalse(trace["conflict_behavior_changed"])
        self.assertFalse(trace["activation_behavior_changed"])
        self.assertEqual(trace["approval_state"], "unreviewed")

    def test_cli_has_no_review_or_lifecycle_write_command(self):
        process = subprocess.run(
            [sys.executable, "-m", "ashl_core.teaching_cli", "--help"],
            check=True,
            capture_output=True,
            text=True,
        )
        help_text = process.stdout.lower()
        for phrase in [
            "resolve-conflict",
            "apply-review",
            "enable-lesson",
            "disable-lesson",
            "mark-stale",
            "unmark-stale",
        ]:
            self.assertNotIn(phrase, help_text)


if __name__ == "__main__":
    unittest.main()
