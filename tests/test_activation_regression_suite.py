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
from ashl_core.teaching_cli import run_lifecycle_display


DECISION_POINT = "before_retry_pick_up_cube"
CONTEXT = {"task": "pick_up", "object_id": "cube_001", "decision_point": DECISION_POINT}


def lesson_001(stale=False, superseded_by=None):
    lesson = build_lesson_from_failure("session_east", pick_up(build_initial_sandbox_state(), "cube_001"))
    lesson["object_id"] = "cube_001"
    lesson["stale"] = False
    lesson["stale_reason"] = None
    if stale:
        lesson = mark_lesson_stale(lesson)
        lesson["stale_reason"] = "manual: regression fixture"
    if superseded_by is not None:
        lesson["superseded_by"] = superseded_by
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


def lesson_004(status="active", stale=False, object_id="cube_001", action="turn(east)"):
    return {
        "lesson_id": "lesson_004",
        "source_session": "manual_fixture",
        "source_failure_reason": "not_facing_east_refined",
        "trigger": {"action": "pick_up", "target_type": "cube"},
        "decision_point": DECISION_POINT,
        "object_id": object_id,
        "condition": {"avatar_facing": "east"},
        "suggested_action_before_retry": action,
        "status": status,
        "stale": stale,
        "stale_reason": "manual: candidate stale" if stale else None,
        "confidence": "manual_fixture",
    }


def lesson_007():
    return {
        "lesson_id": "lesson_007",
        "source_session": "manual_fixture",
        "source_failure_reason": "not_facing_east_second_refinement",
        "trigger": {"action": "pick_up", "target_type": "cube"},
        "decision_point": DECISION_POINT,
        "object_id": "cube_001",
        "condition": {"avatar_facing": "east"},
        "suggested_action_before_retry": "turn(east)",
        "status": "active",
        "stale": False,
        "confidence": "manual_fixture",
    }


def linked_lessons(old=None, candidate=None):
    link = link_lesson_supersede(old or lesson_001(stale=True), candidate or lesson_004())
    return [link["old_lesson"], link["new_lesson"]]


class ActivationRegressionSuite(unittest.TestCase):
    def test_activation_success_requires_all_conditions(self):
        result = select_lesson_for_context(linked_lessons(), CONTEXT)
        activation = result["supersede_activation"]

        self.assertTrue(activation["activation_applied"])
        self.assertEqual(result["selected_lesson_id"], "lesson_004")
        self.assertEqual(activation["failed_conditions"], [])
        self.assertEqual(activation["activation_source"], "supersede_link")

    def test_old_lesson_not_stale_blocks_activation(self):
        result = select_lesson_for_context(linked_lessons(old=lesson_001(stale=False)), CONTEXT)

        self.assertIsNone(result["supersede_activation"])
        self.assertEqual(result["supersede_activations"], [])
        self.assertIsNone(result["selected_lesson_id"])

    def test_missing_superseded_by_blocks_activation(self):
        old = lesson_001(stale=True)
        result = select_lesson_for_context([old, lesson_004()], CONTEXT)

        self.assertIsNone(result["supersede_activation"])
        self.assertEqual(result["supersede_activations"], [])
        self.assertEqual(result["selected_lesson_id"], "lesson_004")

    def test_candidate_missing_blocks_activation(self):
        result = select_lesson_for_context([lesson_001(stale=True, superseded_by="lesson_missing")], CONTEXT)
        activation = result["supersede_activation"]

        self.assertFalse(activation["candidate_exists"])
        self.assertFalse(activation["activation_applied"])
        self.assertIn("candidate_exists", activation["failed_conditions"])
        self.assertIsNone(result["selected_lesson_id"])

    def test_candidate_inactive_blocks_activation(self):
        result = select_lesson_for_context(linked_lessons(candidate=lesson_004(status="inactive")), CONTEXT)
        activation = result["supersede_activation"]

        self.assertFalse(activation["candidate_active"])
        self.assertFalse(activation["activation_applied"])
        self.assertIn("candidate_active", activation["failed_conditions"])
        self.assertIsNone(result["selected_lesson_id"])

    def test_candidate_stale_blocks_activation(self):
        result = select_lesson_for_context(linked_lessons(candidate=lesson_004(stale=True)), CONTEXT)
        activation = result["supersede_activation"]

        self.assertFalse(activation["candidate_not_stale"])
        self.assertFalse(activation["activation_applied"])
        self.assertIn("candidate_not_stale", activation["failed_conditions"])
        self.assertIsNone(result["selected_lesson_id"])

    def test_candidate_normal_eligibility_failure_blocks_activation(self):
        result = select_lesson_for_context(linked_lessons(candidate=lesson_004(object_id="cube_002")), CONTEXT)
        activation = result["supersede_activation"]

        self.assertFalse(activation["candidate_eligible"])
        self.assertFalse(activation["activation_applied"])
        self.assertIn("candidate_eligible", activation["failed_conditions"])
        self.assertIsNone(result["selected_lesson_id"])

    def test_supersede_link_is_not_authorization(self):
        result = select_lesson_for_context(linked_lessons(candidate=lesson_004(object_id="cube_002")), CONTEXT)
        activation = result["supersede_activation"]

        self.assertFalse(activation["candidate_eligible"])
        self.assertFalse(activation["activation_applied"])
        self.assertIsNone(result["selected_lesson_id"])

    def test_conflict_behavior_independent_from_supersede(self):
        lessons = linked_lessons() + [lesson_002()]
        result = select_lesson_for_decision_point(lessons, DECISION_POINT)
        activation = result["supersede_activation"]

        self.assertTrue(result["conflict_detected"])
        self.assertEqual(result["conflict_resolution"], "require_review")
        self.assertIsNone(result["selected_lesson_id"])
        self.assertFalse(activation["activation_applied"])
        self.assertIn("conflict_unresolved", activation["failed_conditions"])

    def test_activation_does_not_mutate_lifecycle_metadata(self):
        lessons = linked_lessons()
        before = copy.deepcopy(lessons)

        result = select_lesson_for_context(lessons, CONTEXT)

        self.assertTrue(result["supersede_activation"]["activation_applied"])
        self.assertEqual(lessons, before)
        for index in (0, 1):
            self.assertEqual(lessons[index].get("status"), before[index].get("status"))
            self.assertEqual(lessons[index].get("stale"), before[index].get("stale"))
            self.assertEqual(lessons[index].get("stale_reason"), before[index].get("stale_reason"))
            self.assertEqual(lessons[index].get("superseded_by"), before[index].get("superseded_by"))
            self.assertEqual(lessons[index].get("supersedes"), before[index].get("supersedes"))

    def test_multilayer_supersede_chain_not_followed(self):
        candidate = lesson_004()
        candidate["superseded_by"] = "lesson_007"
        result = select_lesson_for_context(linked_lessons(candidate=candidate) + [lesson_007()], CONTEXT)
        activation = result["supersede_activation"]

        self.assertEqual(activation["candidate_lesson_id"], "lesson_004")
        self.assertFalse(activation["chain_followed"])
        self.assertNotEqual(result["selected_lesson_id"], "lesson_007")
        self.assertIsNone(result["selected_lesson_id"])

    def test_replacement_suggestion_and_activation_remain_consistent(self):
        result = select_lesson_for_context(linked_lessons(), CONTEXT)
        suggestion = result["replacement_suggestions"][0]
        activation = result["supersede_activation"]

        self.assertEqual(suggestion["candidate_lesson_id"], activation["candidate_lesson_id"])
        self.assertEqual(suggestion["candidate_exists"], activation["candidate_exists"])
        self.assertEqual(not suggestion["candidate_stale"], activation["candidate_not_stale"])
        self.assertEqual(suggestion["candidate_eligible"], activation["candidate_eligible"])
        self.assertTrue(activation["activation_applied"])
        self.assertTrue(suggestion["candidate_exists"])
        self.assertFalse(suggestion["candidate_stale"])
        self.assertTrue(suggestion["candidate_eligible"])

    def test_cli_lifecycle_display_remains_read_only(self):
        lessons = linked_lessons()
        before = copy.deepcopy(lessons)

        result = run_lifecycle_display(lessons, CONTEXT)

        self.assertTrue(result["read_only"])
        self.assertEqual(lessons, before)
        self.assertEqual(lessons[0]["stale"], before[0]["stale"])
        self.assertEqual(lessons[0]["stale_reason"], before[0]["stale_reason"])
        self.assertEqual(lessons[0]["superseded_by"], before[0]["superseded_by"])
        self.assertEqual(lessons[1]["supersedes"], before[1]["supersedes"])

        process = subprocess.run(
            [sys.executable, "-m", "ashl_core.teaching_cli", "--help"],
            check=True,
            capture_output=True,
            text=True,
        )
        help_text = process.stdout.lower()
        for phrase in [
            "mark-stale",
            "unmark-stale",
            "apply-replacement",
            "enable-replacement",
            "disable-old-lesson",
        ]:
            self.assertNotIn(phrase, help_text)

    def test_known_unknown_failure_reason_behavior_remains_unchanged(self):
        known_failure = pick_up(build_initial_sandbox_state(), "cube_001")
        known = generate_lesson_from_failure("session_known", known_failure)
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
        self.assertEqual(known["lesson"]["suggested_action_before_retry"], "turn(east)")
        self.assertEqual(unknown["trace"]["generation_status"], "unknown_failure_reason")
        self.assertIsNone(unknown["lesson"])
        self.assertIsNone(unknown["trace"]["executable_action"])


if __name__ == "__main__":
    unittest.main()
