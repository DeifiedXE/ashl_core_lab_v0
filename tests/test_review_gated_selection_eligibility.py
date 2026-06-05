import copy
import subprocess
import sys
import unittest

from ashl_core.fake_sandbox import build_initial_sandbox_state, pick_up
from ashl_core.lesson_store import (
    build_lesson_from_failure,
    evaluate_review_gate,
    generate_lesson_from_failure,
    link_lesson_supersede,
    mark_lesson_stale,
    select_lesson_for_context,
    select_lesson_for_decision_point,
)
from ashl_core.manual_review import create_review_item, mark_review_approved, mark_review_rejected


DECISION_POINT = "before_retry_pick_up_cube"
CONTEXT = {"task": "pick_up", "object_id": "cube_001", "decision_point": DECISION_POINT}


def lesson_001(stale=False):
    lesson = build_lesson_from_failure("session_east", pick_up(build_initial_sandbox_state(), "cube_001"))
    lesson["object_id"] = "cube_001"
    lesson["stale"] = False
    lesson["stale_reason"] = None
    if stale:
        lesson = mark_lesson_stale(lesson)
        lesson["stale_reason"] = "manual: review gate fixture"
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


def lesson_004(requires_review=True, object_id="cube_001", status="active", stale=False):
    return {
        "lesson_id": "lesson_004",
        "source_session": "manual_fixture",
        "source_failure_reason": "not_facing_east_refined",
        "trigger": {"action": "pick_up", "target_type": "cube"},
        "decision_point": DECISION_POINT,
        "object_id": object_id,
        "condition": {"avatar_facing": "east"},
        "suggested_action_before_retry": "turn(east)",
        "status": status,
        "stale": stale,
        "stale_reason": "manual: candidate stale" if stale else None,
        "confidence": "manual_fixture",
        "requires_review": requires_review,
    }


def review_item(
    candidate_lesson_id="lesson_004",
    source_lesson_id=None,
    review_id="review_001",
    target_id="conflict_001",
):
    return create_review_item(
        target_type="conflict",
        target_id=target_id,
        source_lesson_id=source_lesson_id,
        candidate_lesson_id=candidate_lesson_id,
        reason="conflict_requires_manual_review",
        review_id=review_id,
    )


class ReviewGatedSelectionEligibilityTests(unittest.TestCase):
    def test_approved_review_allows_candidate_through_review_gate(self):
        candidate = lesson_004()
        review = mark_review_approved(review_item())
        result = select_lesson_for_context([candidate], CONTEXT, review_items=[review])
        gate = result["review_gates"][0]

        self.assertTrue(gate["review_gate_passed"])
        self.assertEqual(gate["matched_review_id"], "review_001")
        self.assertEqual(gate["review_state"], "reviewed")
        self.assertEqual(gate["approval_state"], "approved")
        self.assertEqual(gate["reason"], "approved_review_allows_selection_eligibility")
        self.assertEqual(result["selected_lesson_id"], "lesson_004")

    def test_rejected_review_blocks_candidate_review_gate(self):
        candidate = lesson_004()
        review = mark_review_rejected(review_item())
        result = select_lesson_for_context([candidate], CONTEXT, review_items=[review])
        gate = result["review_gates"][0]

        self.assertFalse(gate["review_gate_passed"])
        self.assertEqual(gate["review_state"], "reviewed")
        self.assertEqual(gate["approval_state"], "rejected")
        self.assertEqual(gate["reason"], "rejected_review_blocks_selection_eligibility")
        self.assertIsNone(result["selected_lesson_id"])

    def test_pending_unreviewed_review_blocks_review_gate(self):
        candidate = lesson_004()
        review = review_item()
        result = select_lesson_for_context([candidate], CONTEXT, review_items=[review])
        gate = result["review_gates"][0]

        self.assertFalse(gate["review_gate_passed"])
        self.assertEqual(gate["review_state"], "pending_review")
        self.assertEqual(gate["approval_state"], "unreviewed")
        self.assertEqual(gate["reason"], "review_not_approved")
        self.assertIsNone(result["selected_lesson_id"])

    def test_missing_review_blocks_review_gate(self):
        candidate = lesson_004()
        result = select_lesson_for_context([candidate], CONTEXT, review_items=[])
        gate = result["review_gates"][0]

        self.assertIsNone(gate["matched_review_id"])
        self.assertIsNone(gate["review_state"])
        self.assertIsNone(gate["approval_state"])
        self.assertFalse(gate["review_gate_passed"])
        self.assertEqual(gate["reason"], "missing_required_review")
        self.assertIsNone(result["selected_lesson_id"])

    def test_candidate_without_review_gate_keeps_normal_selection_eligibility(self):
        candidate = lesson_004(requires_review=False)
        result = select_lesson_for_context([candidate], CONTEXT)
        gate = result["review_gates"][0]

        self.assertFalse(gate["requires_review"])
        self.assertTrue(gate["review_gate_passed"])
        self.assertFalse(gate["included_in_selection_eligibility"])
        self.assertEqual(gate["reason"], "review_gate_not_required")
        self.assertEqual(result["selected_lesson_id"], "lesson_004")

    def test_approval_does_not_grant_priority(self):
        lesson_a = lesson_004(requires_review=True)
        lesson_b = lesson_001()
        review = mark_review_approved(review_item(candidate_lesson_id="lesson_004"))

        result = select_lesson_for_decision_point([lesson_a, lesson_b], DECISION_POINT, review_items=[review])

        self.assertFalse(result["conflict_detected"])
        self.assertIsNone(result["selected_lesson_id"])
        self.assertNotIn("priority", result)

    def test_approval_does_not_bypass_normal_eligibility(self):
        candidate = lesson_004(object_id="cube_002")
        review = mark_review_approved(review_item())
        result = select_lesson_for_context([candidate], CONTEXT, review_items=[review])
        gate = result["review_gates"][0]

        self.assertTrue(gate["review_gate_passed"])
        self.assertEqual(gate["reason"], "approved_review_allows_selection_eligibility")
        self.assertEqual(result["matched_lesson_ids"], [])
        self.assertIsNone(result["selected_lesson_id"])

    def test_approval_does_not_affect_conflict(self):
        lessons = [lesson_001(), lesson_002()]
        before = select_lesson_for_decision_point(lessons, DECISION_POINT)
        review = mark_review_approved(review_item(candidate_lesson_id="lesson_001"))
        after = select_lesson_for_decision_point(lessons, DECISION_POINT, review_items=[review])

        self.assertTrue(before["conflict_detected"])
        self.assertTrue(after["conflict_detected"])
        self.assertEqual(before["conflict_resolution"], after["conflict_resolution"])
        self.assertIsNone(after["selected_lesson_id"])
        self.assertTrue(all(gate["conflict_changed"] is False for gate in after["review_gates"]))

    def test_review_gate_does_not_rewrite_strict_supersede_activation_conditions(self):
        link = link_lesson_supersede(lesson_001(stale=True), lesson_004())
        lessons = [link["old_lesson"], link["new_lesson"]]
        approved = mark_review_approved(review_item(source_lesson_id="lesson_001"))
        rejected = mark_review_rejected(review_item(source_lesson_id="lesson_001"))

        approved_result = select_lesson_for_context(lessons, CONTEXT, review_items=[approved])
        rejected_result = select_lesson_for_context(lessons, CONTEXT, review_items=[rejected])

        self.assertTrue(approved_result["supersede_activation"]["activation_applied"])
        self.assertEqual(approved_result["supersede_activation"]["activation_source"], "supersede_link")
        self.assertTrue(approved_result["supersede_activation"]["review_gate"]["review_gate_passed"])
        self.assertFalse(rejected_result["supersede_activation"]["activation_applied"])
        self.assertFalse(rejected_result["supersede_activation"]["candidate_eligible"])
        self.assertFalse(rejected_result["supersede_activation"]["review_gate"]["review_gate_passed"])
        self.assertIn("candidate_eligible", rejected_result["supersede_activation"]["failed_conditions"])
        self.assertTrue(all(gate["activation_changed"] is False for gate in rejected_result["review_gates"]))

    def test_rejection_does_not_mark_stale_or_disable_lesson(self):
        candidate = lesson_004()
        before = copy.deepcopy(candidate)
        review = mark_review_rejected(review_item())

        result = select_lesson_for_context([candidate], CONTEXT, review_items=[review])

        self.assertEqual(candidate, before)
        self.assertEqual(candidate["status"], before["status"])
        self.assertEqual(candidate["stale"], before["stale"])
        self.assertEqual(candidate["stale_reason"], before["stale_reason"])
        self.assertEqual(candidate.get("superseded_by"), before.get("superseded_by"))
        self.assertEqual(candidate.get("supersedes"), before.get("supersedes"))
        self.assertIsNone(result["selected_lesson_id"])

    def test_matching_does_not_use_notes_or_reason_text(self):
        candidate = lesson_004()
        misleading = create_review_item(
            target_type="conflict",
            target_id="conflict_001",
            source_lesson_id=None,
            candidate_lesson_id="lesson_other",
            reason="mentions lesson_004 but must not match by text",
            notes="lesson_004 approved-looking text",
            review_id="review_misleading",
        )
        misleading = mark_review_approved(misleading)
        gate = evaluate_review_gate(candidate, [misleading])

        self.assertIsNone(gate["matched_review_id"])
        self.assertFalse(gate["review_gate_passed"])
        self.assertEqual(gate["reason"], "missing_required_review")

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
        self.assertEqual(known["lesson"]["suggested_action_before_retry"], "turn(east)")
        self.assertEqual(unknown["trace"]["generation_status"], "unknown_failure_reason")
        self.assertIsNone(unknown["lesson"])

    def test_cli_does_not_add_review_or_lifecycle_write_commands(self):
        process = subprocess.run(
            [sys.executable, "-m", "ashl_core.teaching_cli", "--help"],
            check=True,
            capture_output=True,
            text=True,
        )
        help_text = process.stdout.lower()
        for phrase in [
            "apply-review",
            "resolve-conflict",
            "enable-lesson",
            "disable-lesson",
            "mark-stale",
            "unmark-stale",
            "apply-replacement",
            "batch-review-query",
        ]:
            self.assertNotIn(phrase, help_text)


if __name__ == "__main__":
    unittest.main()
