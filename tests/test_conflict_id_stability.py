import copy
import re
import unittest

from ashl_core.fake_sandbox import build_initial_sandbox_state, pick_up
from ashl_core.lesson_store import (
    build_lesson_from_failure,
    build_stable_conflict_key,
    generate_lesson_from_failure,
    link_lesson_supersede,
    mark_lesson_stale,
    select_lesson_for_context,
    select_lesson_for_decision_point,
)
from ashl_core.manual_review import create_review_item


DECISION_POINT = "before_retry_pick_up_cube"
OTHER_DECISION_POINT = "before_retry_push_cube"
CONTEXT = {"task": "pick_up", "object_id": "cube_001", "decision_point": DECISION_POINT}


def lesson_east():
    lesson = build_lesson_from_failure("session_east", pick_up(build_initial_sandbox_state(), "cube_001"))
    lesson["object_id"] = "cube_001"
    return lesson


def lesson_west(lesson_id="lesson_002", decision_point=DECISION_POINT):
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
    lesson["lesson_id"] = lesson_id
    lesson["decision_point"] = decision_point
    lesson["object_id"] = "cube_001"
    return lesson


def lesson_candidate_004():
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


def conflict_selection(lessons=None, decision_point=DECISION_POINT):
    return select_lesson_for_decision_point(lessons or [lesson_east(), lesson_west()], decision_point)


class ConflictIdStabilityTests(unittest.TestCase):
    def test_same_conflict_scenario_repeated_runs_have_stable_key(self):
        results = [conflict_selection() for _ in range(3)]
        keys = [result["stable_conflict_key"] for result in results]

        self.assertEqual(keys[0], keys[1])
        self.assertEqual(keys[1], keys[2])
        self.assertEqual(results[0]["conflict_id"], keys[0])
        self.assertTrue(results[0]["conflict_id_stable"])
        self.assertEqual(results[0]["stability_source"], "deterministic_conflict_metadata")

    def test_lesson_order_does_not_change_stable_key(self):
        forward = conflict_selection([lesson_east(), lesson_west()])
        reversed_order = conflict_selection([lesson_west(), lesson_east()])

        self.assertEqual(forward["stable_conflict_key"], reversed_order["stable_conflict_key"])
        self.assertEqual(forward["conflicting_lesson_ids"], ["lesson_001", "lesson_002"])
        self.assertEqual(reversed_order["conflicting_lesson_ids"], ["lesson_002", "lesson_001"])

    def test_stable_key_does_not_use_random_timestamp_or_object_id(self):
        result = conflict_selection()
        key = result["stable_conflict_key"]

        self.assertEqual(key, build_stable_conflict_key(["lesson_002", "lesson_001"], DECISION_POINT))
        self.assertNotRegex(key, re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}", re.IGNORECASE))
        self.assertNotRegex(key, re.compile(r"\d{4}-\d{2}-\d{2}t", re.IGNORECASE))
        self.assertNotIn("object at", key.lower())
        self.assertNotIn("0x", key.lower())

    def test_different_conflict_scenario_has_different_stable_key(self):
        first = conflict_selection([lesson_east(), lesson_west()])
        second = conflict_selection([lesson_east(), lesson_west(lesson_id="lesson_005")])

        self.assertNotEqual(first["stable_conflict_key"], second["stable_conflict_key"])

    def test_trace_distinguishes_runtime_conflict_id_and_stable_key(self):
        result = conflict_selection()

        self.assertIn("conflict_id", result)
        self.assertIn("stable_conflict_key", result)
        self.assertIn("conflict_id_stable", result)
        self.assertIn("stability_source", result)
        self.assertEqual(result["conflict_id"], result["stable_conflict_key"])
        self.assertTrue(result["conflict_id_stable"])

    def test_stable_key_does_not_change_conflict_result(self):
        before = conflict_selection()
        after = conflict_selection()

        for key in ["conflict_detected", "conflict_resolution", "review_required", "review_status", "selected_lesson_id"]:
            self.assertEqual(before[key], after[key])
        self.assertTrue(after["conflict_detected"])
        self.assertEqual(after["conflict_resolution"], "require_review")

    def test_stable_key_does_not_change_selection_result(self):
        lessons = [lesson_east()]
        before = select_lesson_for_context(lessons, CONTEXT)
        after = select_lesson_for_context(lessons, CONTEXT)

        self.assertEqual(before["selected_lesson_id"], after["selected_lesson_id"])
        self.assertEqual(before["selected_action"], after["selected_action"])
        self.assertNotIn("priority", after)

    def test_stable_key_does_not_change_strict_supersede_activation(self):
        old = lesson_east()
        old = mark_lesson_stale(old)
        old["stale_reason"] = "manual: conflict id stability fixture"
        link = link_lesson_supersede(old, lesson_candidate_004())
        lessons = [link["old_lesson"], link["new_lesson"]]
        before = select_lesson_for_context(lessons, CONTEXT)
        after = select_lesson_for_context(lessons, CONTEXT)

        self.assertEqual(before["supersede_activation"], after["supersede_activation"])
        self.assertTrue(after["supersede_activation"]["activation_applied"])
        self.assertEqual(before["selected_lesson_id"], after["selected_lesson_id"])

    def test_conflict_id_stability_does_not_do_review_matching(self):
        review = create_review_item(
            target_type="conflict",
            target_id="conflict:mentions:lesson_001:lesson_002",
            source_lesson_id="lesson_001",
            candidate_lesson_id="lesson_002",
            reason="mentions lesson_001 lesson_002 but must not match",
            notes="turn(east) turn(west)",
            review_id="review_001",
        )
        before = copy.deepcopy(review)
        result = conflict_selection()

        self.assertIn("conflict_review_resolution_preview", result)
        self.assertEqual(result["conflict_review_resolution_preview"]["matched_review_items"], [])
        self.assertEqual(result["conflict_review_resolution_preview"]["reason"], "no_matching_review_item")
        self.assertEqual(review, before)

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
