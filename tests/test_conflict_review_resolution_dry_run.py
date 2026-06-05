import copy
import subprocess
import sys
import unittest

from ashl_core.fake_sandbox import build_initial_sandbox_state, pick_up
from ashl_core.lesson_store import (
    build_conflict_review_resolution_dry_run,
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


def conflict_trace():
    return select_lesson_for_decision_point([lesson_east(), lesson_west()], DECISION_POINT)


def review_for(stable_key, candidate="lesson_002", approval_state="approved", review_id="review_001"):
    item = create_review_item(
        target_type="conflict",
        target_id=stable_key,
        source_lesson_id="lesson_001",
        candidate_lesson_id=candidate,
        reason="conflict_requires_manual_review",
        notes="dry-run note",
        review_id=review_id,
    )
    if approval_state == "approved":
        return mark_review_approved(item)
    if approval_state == "rejected":
        return mark_review_rejected(item)
    return item


class ConflictReviewResolutionDryRunTests(unittest.TestCase):
    def test_preconditions_met_dry_run_would_resolve(self):
        trace = conflict_trace()
        review = review_for(trace["stable_conflict_key"], "lesson_002", "approved")
        dry_run = build_conflict_review_resolution_dry_run(trace, [review], candidate_lesson_id="lesson_002")

        self.assertTrue(dry_run["dry_run_would_resolve"])
        self.assertEqual(dry_run["dry_run_winner_candidate_id"], "lesson_002")
        self.assertNotEqual(dry_run["dry_run_winner_candidate_id"], "lesson_001")
        self.assertIsNone(dry_run["dry_run_blocked_reason"])
        self.assertTrue(dry_run["all_preconditions_met"])
        self.assertEqual(dry_run["failed_preconditions"], [])
        self.assertFalse(dry_run["conflict_changed"])
        self.assertFalse(dry_run["resolution_applied"])
        self.assertFalse(dry_run["selection_changed"])
        self.assertFalse(dry_run["activation_changed"])

    def test_failed_preconditions_dry_run_blocked(self):
        trace = conflict_trace()
        dry_run = build_conflict_review_resolution_dry_run(trace, [], candidate_lesson_id="lesson_002")

        self.assertFalse(dry_run["dry_run_would_resolve"])
        self.assertIsNone(dry_run["dry_run_winner_candidate_id"])
        self.assertIsNotNone(dry_run["dry_run_blocked_reason"])
        self.assertFalse(dry_run["all_preconditions_met"])
        self.assertNotEqual(dry_run["failed_preconditions"], [])
        self.assertFalse(dry_run["resolution_applied"])

    def test_rejected_review_blocker_dry_run(self):
        trace = conflict_trace()
        lessons = [lesson_east(), lesson_west()]
        before = copy.deepcopy(lessons)
        rejected = review_for(trace["stable_conflict_key"], "lesson_002", "rejected")
        dry_run = build_conflict_review_resolution_dry_run(trace, [rejected], candidate_lesson_id="lesson_002")

        self.assertFalse(dry_run["dry_run_would_resolve"])
        self.assertEqual(dry_run["dry_run_blocked_reason"], "rejected_review_blocks_resolution")
        self.assertIsNone(dry_run["dry_run_winner_candidate_id"])
        self.assertFalse(dry_run["resolution_applied"])
        self.assertEqual(lessons, before)

    def test_conflicting_reviews_blocker_dry_run(self):
        trace = conflict_trace()
        approved = review_for(trace["stable_conflict_key"], "lesson_002", "approved", "review_approved")
        rejected = review_for(trace["stable_conflict_key"], "lesson_002", "rejected", "review_rejected")
        dry_run = build_conflict_review_resolution_dry_run(trace, [approved, rejected], candidate_lesson_id="lesson_002")

        self.assertFalse(dry_run["dry_run_would_resolve"])
        self.assertEqual(dry_run["dry_run_blocked_reason"], "blocked_by_conflicting_reviews")
        self.assertIsNone(dry_run["dry_run_winner_candidate_id"])
        self.assertFalse(dry_run["resolution_applied"])
        self.assertTrue(trace["review_required"])

    def test_multiple_approved_candidates_blocker_dry_run(self):
        trace = conflict_trace()
        approved_a = review_for(trace["stable_conflict_key"], "lesson_001", "approved", "review_a")
        approved_b = review_for(trace["stable_conflict_key"], "lesson_002", "approved", "review_b")
        approved_a["source_lesson_id"] = "lesson_002"
        dry_run = build_conflict_review_resolution_dry_run(trace, [approved_a, approved_b], candidate_lesson_id="lesson_002")

        self.assertFalse(dry_run["dry_run_would_resolve"])
        self.assertIsNone(dry_run["dry_run_winner_candidate_id"])
        self.assertEqual(dry_run["dry_run_blocked_reason"], "blocked_by_multiple_approvals")
        self.assertFalse(dry_run["resolution_applied"])

    def test_runtime_conflict_id_cannot_be_only_matching_anchor(self):
        trace = conflict_trace()
        runtime_only = review_for("runtime_conflict_001", "lesson_002", "approved")
        runtime_only["runtime_conflict_id"] = trace["conflict_id"]
        dry_run = build_conflict_review_resolution_dry_run(trace, [runtime_only], candidate_lesson_id="lesson_002")

        self.assertFalse(dry_run["dry_run_would_resolve"])
        self.assertNotEqual(runtime_only["target_id"], trace["stable_conflict_key"])
        self.assertIsNotNone(dry_run["dry_run_blocked_reason"])

    def test_dry_run_trace_field_completeness(self):
        trace = conflict_trace()
        successful = build_conflict_review_resolution_dry_run(
            trace,
            [review_for(trace["stable_conflict_key"], "lesson_002", "approved")],
            candidate_lesson_id="lesson_002",
        )
        blocked = build_conflict_review_resolution_dry_run(trace, [], candidate_lesson_id="lesson_002")
        required = {
            "dry_run_would_resolve",
            "dry_run_winner_candidate_id",
            "dry_run_blocked_reason",
            "all_preconditions_met",
            "failed_preconditions",
            "conflict_changed",
            "resolution_applied",
            "selection_changed",
            "activation_changed",
            "reason",
        }

        self.assertTrue(required.issubset(successful.keys()))
        self.assertTrue(required.issubset(blocked.keys()))

    def test_dry_run_does_not_introduce_conflict_side_effect(self):
        trace = conflict_trace()
        before = conflict_trace()
        build_conflict_review_resolution_dry_run(
            trace,
            [review_for(trace["stable_conflict_key"], "lesson_002", "approved")],
            candidate_lesson_id="lesson_002",
        )
        after = conflict_trace()

        self.assertEqual(before["conflict_detected"], after["conflict_detected"])
        self.assertEqual(before["conflict_resolution"], after["conflict_resolution"])
        self.assertTrue(after["review_required"])

    def test_dry_run_does_not_introduce_selection_side_effect(self):
        before = select_lesson_for_context([lesson_east()], CONTEXT)
        trace = conflict_trace()
        dry_run = build_conflict_review_resolution_dry_run(
            trace,
            [review_for(trace["stable_conflict_key"], "lesson_002", "approved")],
            candidate_lesson_id="lesson_002",
        )
        after = select_lesson_for_context([lesson_east()], CONTEXT)

        self.assertEqual(before["selected_lesson_id"], after["selected_lesson_id"])
        self.assertEqual(before["selected_action"], after["selected_action"])
        self.assertFalse(dry_run["selection_changed"])

    def test_dry_run_does_not_affect_strict_supersede_activation(self):
        old = mark_lesson_stale(lesson_east())
        old["stale_reason"] = "manual: dry-run fixture"
        link = link_lesson_supersede(old, lesson_004())
        lessons = [link["old_lesson"], link["new_lesson"]]
        before = select_lesson_for_context(lessons, CONTEXT)
        trace = conflict_trace()
        dry_run = build_conflict_review_resolution_dry_run(
            trace,
            [review_for(trace["stable_conflict_key"], "lesson_002", "approved")],
            candidate_lesson_id="lesson_002",
        )
        after = select_lesson_for_context(lessons, CONTEXT)

        self.assertEqual(before["supersede_activation"], after["supersede_activation"])
        self.assertEqual(before["selected_lesson_id"], after["selected_lesson_id"])
        self.assertFalse(dry_run["activation_changed"])

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
        self.assertEqual(known["lesson"]["lesson_id"], "lesson_001")
        self.assertEqual(unknown["trace"]["generation_status"], "unknown_failure_reason")
        self.assertIsNone(unknown["lesson"])

    def test_dry_run_does_not_modify_review_item_metadata(self):
        trace = conflict_trace()
        approved = review_for(trace["stable_conflict_key"], "lesson_002", "approved", "review_approved")
        rejected = review_for(trace["stable_conflict_key"], "lesson_002", "rejected", "review_rejected")
        reviews = [approved, rejected]
        before = copy.deepcopy(reviews)

        build_conflict_review_resolution_dry_run(trace, reviews, candidate_lesson_id="lesson_002")

        self.assertEqual(reviews, before)
        for index, review in enumerate(reviews):
            for key in ["review_state", "approval_state", "notes", "reason", "target_id", "source_lesson_id", "candidate_lesson_id"]:
                self.assertEqual(review.get(key), before[index].get(key))

    def test_dry_run_does_not_modify_lesson_lifecycle_metadata(self):
        trace = conflict_trace()
        lessons = [lesson_east(), lesson_west()]
        before = copy.deepcopy(lessons)

        build_conflict_review_resolution_dry_run(
            trace,
            [review_for(trace["stable_conflict_key"], "lesson_002", "approved")],
            candidate_lesson_id="lesson_002",
        )

        self.assertEqual(lessons, before)
        for index, lesson in enumerate(lessons):
            for key in ["status", "stale", "stale_reason", "superseded_by", "supersedes"]:
                self.assertEqual(lesson.get(key), before[index].get(key))

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
