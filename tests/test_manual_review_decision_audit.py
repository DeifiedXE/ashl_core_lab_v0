import copy
import subprocess
import sys
import unittest

from ashl_core.fake_sandbox import build_initial_sandbox_state, pick_up
from ashl_core.lesson_store import (
    build_lesson_from_failure,
    generate_lesson_from_failure,
    link_lesson_supersede,
    mark_lesson_stale,
    select_lesson_for_context,
    select_lesson_for_decision_point,
)
from ashl_core.manual_review import create_review_item
from ashl_core.teaching_cli import run_review_approve, run_review_display, run_review_reject


DECISION_POINT = "before_retry_pick_up_cube"
CONTEXT = {"task": "pick_up", "object_id": "cube_001", "decision_point": DECISION_POINT}


def review_item(review_id="review_001"):
    return create_review_item(
        target_type="conflict",
        target_id="conflict_001",
        source_lesson_id="lesson_001",
        candidate_lesson_id="lesson_004",
        reason="conflict_requires_manual_review",
        notes="initial note",
        review_id=review_id,
    )


def lesson_001(stale=False):
    lesson = build_lesson_from_failure("session_east", pick_up(build_initial_sandbox_state(), "cube_001"))
    lesson["object_id"] = "cube_001"
    lesson["stale"] = False
    lesson["stale_reason"] = None
    if stale:
        lesson = mark_lesson_stale(lesson)
        lesson["stale_reason"] = "manual: decision audit fixture"
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


def assert_identity_fields_unchanged(testcase, before, after):
    for key in ["id", "target_type", "target_id", "source_lesson_id", "candidate_lesson_id", "reason"]:
        testcase.assertEqual(after[key], before[key])


class ManualReviewDecisionAuditTests(unittest.TestCase):
    def test_approve_only_modifies_review_metadata(self):
        item = review_item()
        approved = run_review_approve([item], notes="approved note")["review_item"]

        self.assertEqual(approved["review_state"], "reviewed")
        self.assertEqual(approved["approval_state"], "approved")
        self.assertEqual(approved["notes"], "approved note")
        assert_identity_fields_unchanged(self, item, approved)

    def test_reject_only_modifies_review_metadata(self):
        item = review_item()
        rejected = run_review_reject([item], notes="rejected note")["review_item"]

        self.assertEqual(rejected["review_state"], "reviewed")
        self.assertEqual(rejected["approval_state"], "rejected")
        self.assertEqual(rejected["notes"], "rejected note")
        assert_identity_fields_unchanged(self, item, rejected)

    def test_decision_then_display_state_is_consistent(self):
        approved_items = run_review_approve([review_item()], notes="display audit")["review_items"]
        display = run_review_display(approved_items)

        self.assertIn("review_state: reviewed", display["display"])
        self.assertIn("approval_state: approved", display["display"])
        self.assertIn("notes: display audit", display["display"])
        self.assertIn("reason: conflict_requires_manual_review", display["display"])
        self.assertIn("source_lesson_id: lesson_001", display["display"])
        self.assertIn("candidate_lesson_id: lesson_004", display["display"])

    def test_missing_review_id_does_not_create_new_item(self):
        item = review_item()
        before = copy.deepcopy([item])
        result = run_review_reject([item], review_id="review_missing")

        self.assertEqual(result["status"], "not_found")
        self.assertEqual(result["review_items"], before)
        self.assertEqual(item, before[0])

    def test_repeated_approve_is_stable(self):
        first_items = run_review_approve([review_item()], notes="first approval")["review_items"]
        second = run_review_approve(first_items, notes="second approval")
        item = second["review_item"]

        self.assertEqual(len(second["review_items"]), 1)
        self.assertEqual(item["review_state"], "reviewed")
        self.assertEqual(item["approval_state"], "approved")
        self.assertEqual(item["notes"], "second approval")

    def test_approve_then_reject_only_updates_review_metadata(self):
        approved = run_review_approve([review_item()], notes="approved first")["review_items"]
        rejected = run_review_reject(approved, notes="then rejected")["review_item"]

        self.assertEqual(rejected["review_state"], "reviewed")
        self.assertEqual(rejected["approval_state"], "rejected")
        self.assertEqual(rejected["notes"], "then rejected")
        self.assertEqual(rejected["source_lesson_id"], "lesson_001")
        self.assertEqual(rejected["candidate_lesson_id"], "lesson_004")

    def test_reject_then_approve_only_updates_review_metadata(self):
        rejected = run_review_reject([review_item()], notes="rejected first")["review_items"]
        approved = run_review_approve(rejected, notes="then approved")["review_item"]

        self.assertEqual(approved["review_state"], "reviewed")
        self.assertEqual(approved["approval_state"], "approved")
        self.assertEqual(approved["notes"], "then approved")
        self.assertEqual(approved["source_lesson_id"], "lesson_001")
        self.assertEqual(approved["candidate_lesson_id"], "lesson_004")

    def test_decision_cli_does_not_modify_lesson_lifecycle_metadata(self):
        link = link_lesson_supersede(lesson_001(stale=True), lesson_004())
        lessons = [link["old_lesson"], link["new_lesson"]]
        before = copy.deepcopy(lessons)

        run_review_approve([review_item()])
        run_review_reject([review_item()])

        self.assertEqual(lessons, before)
        for index in (0, 1):
            for key in ["status", "stale", "stale_reason", "superseded_by", "supersedes"]:
                self.assertEqual(lessons[index].get(key), before[index].get(key))

    def test_review_decision_does_not_introduce_selection_side_effect(self):
        lessons = [lesson_001(), lesson_004()]
        before = select_lesson_for_context(lessons, CONTEXT)

        run_review_approve([review_item()])
        run_review_reject([review_item()])
        after = select_lesson_for_context(lessons, CONTEXT)

        self.assertEqual(before, after)

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

    def test_display_cli_does_not_modify_decision_metadata(self):
        approved_items = run_review_approve([review_item()], notes="stable note")["review_items"]
        before = copy.deepcopy(approved_items)

        run_review_display(approved_items)

        self.assertEqual(approved_items, before)
        self.assertEqual(approved_items[0]["review_state"], "reviewed")
        self.assertEqual(approved_items[0]["approval_state"], "approved")
        self.assertEqual(approved_items[0]["notes"], "stable note")
        self.assertEqual(approved_items[0]["reason"], "conflict_requires_manual_review")

    def test_cli_command_guard_allows_review_decision_only(self):
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

    def test_known_unknown_failure_reason_behavior_remains_unchanged(self):
        known = generate_lesson_from_failure("session_known", pick_up(build_initial_sandbox_state(), "cube_001"))
        unknown = generate_lesson_from_failure(
            "session_unknown",
            {
                "type": "sandbox_action_result",
                "tool": "pick_up",
                "object_id": "cube_001",
                "result": "failed",
                "failure_reason": "unmapped_obstacle_shadow",
                "state": build_initial_sandbox_state(),
            },
        )

        self.assertEqual(known["trace"]["generation_status"], "supported_failure_reason")
        self.assertEqual(known["lesson"]["lesson_id"], "lesson_001")
        self.assertEqual(unknown["trace"]["generation_status"], "unknown_failure_reason")
        self.assertIsNone(unknown["lesson"])


if __name__ == "__main__":
    unittest.main()
