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
from ashl_core.manual_review import create_review_item, mark_review_approved, mark_review_rejected


DECISION_POINT = "before_retry_pick_up_cube"
CONTEXT = {"task": "pick_up", "object_id": "cube_001", "decision_point": DECISION_POINT}


def lesson_east():
    lesson = build_lesson_from_failure("session_east", pick_up(build_initial_sandbox_state(), "cube_001"))
    lesson["object_id"] = "cube_001"
    return lesson


def lesson_west():
    lesson = build_lesson_from_failure(
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
    lesson["object_id"] = "cube_001"
    return lesson


def lesson_004(requires_review=False):
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
        "requires_review": requires_review,
    }


def conflict_result(review_items=None):
    return select_lesson_for_decision_point([lesson_east(), lesson_west()], DECISION_POINT, review_items=review_items)


def review_for(stable_key, approval_state="approved", review_id="review_001", notes="audit note"):
    item = create_review_item(
        target_type="conflict",
        target_id=stable_key,
        source_lesson_id="lesson_001",
        candidate_lesson_id="lesson_002",
        reason="conflict_requires_manual_review",
        notes=notes,
        review_id=review_id,
    )
    return mark_review_approved(item) if approval_state == "approved" else mark_review_rejected(item)


class ConflictReviewPreviewAuditTests(unittest.TestCase):
    def test_preview_trace_field_completeness(self):
        baseline = conflict_result()
        result = conflict_result([review_for(baseline["stable_conflict_key"], "approved")])
        preview = result["conflict_review_resolution_preview"]

        for key in [
            "conflict_id",
            "stable_conflict_key",
            "matched_review_items",
            "resolution_preview_applied",
            "conflict_changed",
            "selection_changed",
            "activation_changed",
            "reason",
        ]:
            self.assertIn(key, preview)

    def test_approved_preview_invariant(self):
        baseline = conflict_result()
        result = conflict_result([review_for(baseline["stable_conflict_key"], "approved")])
        preview = result["conflict_review_resolution_preview"]
        matched = preview["matched_review_items"][0]

        self.assertEqual(matched["approval_state"], "approved")
        self.assertEqual(matched["preview_suggestion"], "candidate_has_human_approval")
        self.assertFalse(preview["resolution_preview_applied"])
        self.assertFalse(preview["conflict_changed"])
        self.assertIsNone(result["selected_lesson_id"])

    def test_rejected_preview_invariant(self):
        baseline = conflict_result()
        result = conflict_result([review_for(baseline["stable_conflict_key"], "rejected")])
        preview = result["conflict_review_resolution_preview"]
        matched = preview["matched_review_items"][0]

        self.assertEqual(matched["approval_state"], "rejected")
        self.assertEqual(matched["preview_suggestion"], "candidate_has_human_rejection")
        self.assertFalse(preview["resolution_preview_applied"])
        self.assertFalse(preview["conflict_changed"])
        self.assertIsNone(result["selected_lesson_id"])
        self.assertEqual(result["selected_lesson"], None)

    def test_no_matching_review_item_keeps_full_trace_baseline(self):
        result = conflict_result([])
        preview = result["conflict_review_resolution_preview"]

        self.assertEqual(preview["matched_review_items"], [])
        self.assertFalse(preview["resolution_preview_applied"])
        self.assertFalse(preview["conflict_changed"])
        self.assertFalse(preview["selection_changed"])
        self.assertFalse(preview["activation_changed"])
        self.assertEqual(preview["reason"], "no_matching_review_item")

    def test_matching_uses_stable_conflict_key_and_explicit_metadata(self):
        baseline = conflict_result()
        matching = review_for(baseline["stable_conflict_key"], "approved")
        mismatched = create_review_item(
            target_type="conflict",
            target_id=baseline["stable_conflict_key"],
            source_lesson_id="lesson_999",
            candidate_lesson_id="lesson_002",
            reason="conflict_requires_manual_review",
            review_id="review_bad_source",
        )
        matched_result = conflict_result([matching])
        mismatched_result = conflict_result([mark_review_approved(mismatched)])

        self.assertEqual(matched_result["conflict_review_resolution_preview"]["matched_review_items"][0]["review_id"], "review_001")
        self.assertEqual(mismatched_result["conflict_review_resolution_preview"]["matched_review_items"], [])

    def test_runtime_conflict_id_cannot_be_only_matching_anchor(self):
        baseline = conflict_result()
        runtime_only = create_review_item(
            target_type="conflict",
            target_id="runtime_conflict_001",
            source_lesson_id="lesson_001",
            candidate_lesson_id="lesson_002",
            reason="runtime id only",
            review_id="review_runtime",
        )
        runtime_only["runtime_conflict_id"] = baseline["conflict_id"]
        result = conflict_result([mark_review_approved(runtime_only)])

        self.assertNotEqual(runtime_only["target_id"], baseline["stable_conflict_key"])
        self.assertEqual(result["conflict_review_resolution_preview"]["matched_review_items"], [])

    def test_approved_review_does_not_introduce_conflict_side_effect(self):
        before = conflict_result()
        after = conflict_result([review_for(before["stable_conflict_key"], "approved")])

        self.assertEqual(before["conflict_detected"], after["conflict_detected"])
        self.assertEqual(before["conflict_resolution"], after["conflict_resolution"])
        self.assertEqual(before["review_required"], after["review_required"])
        self.assertIsNone(after["selected_lesson_id"])
        self.assertFalse(after["conflict_review_resolution_preview"]["conflict_changed"])

    def test_rejected_review_does_not_introduce_selection_side_effect(self):
        before = select_lesson_for_context([lesson_east()], CONTEXT)
        conflict_result([review_for(conflict_result()["stable_conflict_key"], "rejected")])
        after = select_lesson_for_context([lesson_east()], CONTEXT)

        self.assertEqual(before["selected_lesson_id"], after["selected_lesson_id"])
        self.assertEqual(before["selected_action"], after["selected_action"])
        self.assertEqual(after["selected_lesson"]["status"], "active")

    def test_preview_does_not_affect_strict_supersede_activation(self):
        old = mark_lesson_stale(lesson_east())
        old["stale_reason"] = "manual: preview audit fixture"
        link = link_lesson_supersede(old, lesson_004())
        lessons = [link["old_lesson"], link["new_lesson"]]
        before = select_lesson_for_context(lessons, CONTEXT)
        conflict_result([review_for(conflict_result()["stable_conflict_key"], "approved")])
        after = select_lesson_for_context(lessons, CONTEXT)

        self.assertEqual(before["supersede_activation"], after["supersede_activation"])
        self.assertEqual(before["selected_lesson_id"], after["selected_lesson_id"])
        self.assertTrue(after["supersede_activation"]["activation_applied"])

    def test_preview_does_not_modify_review_item_metadata(self):
        approved = review_for(conflict_result()["stable_conflict_key"], "approved", "review_approved", "stable approval")
        rejected = review_for(conflict_result()["stable_conflict_key"], "rejected", "review_rejected", "stable rejection")
        reviews = [approved, rejected]
        before = copy.deepcopy(reviews)

        conflict_result(reviews)

        self.assertEqual(reviews, before)
        for index, review in enumerate(reviews):
            for key in ["review_state", "approval_state", "notes", "reason", "target_id", "source_lesson_id", "candidate_lesson_id"]:
                self.assertEqual(review.get(key), before[index].get(key))

    def test_preview_does_not_modify_lesson_lifecycle_metadata(self):
        lessons = [lesson_east(), lesson_west()]
        before = copy.deepcopy(lessons)

        select_lesson_for_decision_point(lessons, DECISION_POINT, review_items=[review_for(conflict_result()["stable_conflict_key"])])

        self.assertEqual(lessons, before)
        for index, lesson in enumerate(lessons):
            for key in ["status", "stale", "stale_reason", "superseded_by", "supersedes"]:
                self.assertEqual(lesson.get(key), before[index].get(key))

    def test_matching_does_not_use_notes_or_reason_text(self):
        stable_key = conflict_result()["stable_conflict_key"]
        misleading = create_review_item(
            target_type="conflict",
            target_id="conflict:wrong",
            source_lesson_id="lesson_001",
            candidate_lesson_id="lesson_002",
            reason=f"mentions {stable_key} and lesson_002",
            notes=f"mentions {stable_key}",
            review_id="review_misleading",
        )
        result = conflict_result([mark_review_approved(misleading)])

        self.assertEqual(result["conflict_review_resolution_preview"]["matched_review_items"], [])

    def test_review_gated_selection_eligibility_remains_unchanged(self):
        candidate = lesson_004(requires_review=True)
        approved = create_review_item("conflict", "conflict_001", None, "lesson_004", "review", review_id="review_gate")
        approved = mark_review_approved(approved)
        rejected = create_review_item("conflict", "conflict_001", None, "lesson_004", "review", review_id="review_gate")
        rejected = mark_review_rejected(rejected)
        approved_result = select_lesson_for_context([candidate], CONTEXT, review_items=[approved])
        rejected_result = select_lesson_for_context([candidate], CONTEXT, review_items=[rejected])

        self.assertTrue(approved_result["review_gates"][0]["review_gate_passed"])
        self.assertFalse(rejected_result["review_gates"][0]["review_gate_passed"])
        self.assertEqual(approved_result["selected_lesson_id"], "lesson_004")
        self.assertIsNone(rejected_result["selected_lesson_id"])
        self.assertNotIn("priority", approved_result)

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
