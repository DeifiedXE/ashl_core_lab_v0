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


DECISION_POINT = "before_retry_pick_up_cube"
CONTEXT = {"task": "pick_up", "object_id": "cube_001", "decision_point": DECISION_POINT}


def _lesson_001(stale=False):
    lesson = build_lesson_from_failure("session_east", pick_up(build_initial_sandbox_state(), "cube_001"))
    lesson["object_id"] = "cube_001"
    lesson["stale"] = False
    if stale:
        lesson = mark_lesson_stale(lesson)
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


def _lesson_004(status="active", stale=False, object_id="cube_001", action="turn(east)"):
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
        "confidence": "manual_fixture",
    }


def _lesson_007():
    return {
        "lesson_id": "lesson_007",
        "source_session": "manual_fixture",
        "source_failure_reason": "not_facing_east_second_refinement",
        "trigger": {"action": "pick_up", "target_type": "cube"},
        "decision_point": DECISION_POINT,
        "object_id": "cube_007",
        "condition": {"avatar_facing": "east"},
        "suggested_action_before_retry": "turn(east)",
        "status": "active",
        "stale": False,
        "confidence": "manual_fixture",
    }


class StrictSupersedeActivationTests(unittest.TestCase):
    def test_all_conditions_true_applies_activation(self):
        link = link_lesson_supersede(_lesson_001(stale=True), _lesson_004())
        result = select_lesson_for_context([link["old_lesson"], link["new_lesson"]], CONTEXT)
        activation = result["supersede_activation"]

        self.assertEqual(result["selected_lesson_id"], "lesson_004")
        self.assertEqual(result["selected_action"], "turn(east)")
        self.assertTrue(activation["activation_applied"])
        self.assertTrue(activation["old_lesson_stale"])
        self.assertTrue(activation["old_lesson_has_superseded_by"])
        self.assertTrue(activation["candidate_exists"])
        self.assertTrue(activation["candidate_active"])
        self.assertTrue(activation["candidate_not_stale"])
        self.assertTrue(activation["candidate_eligible"])
        self.assertEqual(activation["activation_source"], "supersede_link")
        self.assertEqual(activation["failed_conditions"], [])

    def test_candidate_inactive_does_not_activate(self):
        link = link_lesson_supersede(_lesson_001(stale=True), _lesson_004(status="inactive"))
        result = select_lesson_for_context([link["old_lesson"], link["new_lesson"]], CONTEXT)
        activation = result["supersede_activation"]

        self.assertFalse(activation["activation_applied"])
        self.assertFalse(activation["candidate_active"])
        self.assertIn("candidate_active", activation["failed_conditions"])
        self.assertIn("candidate_eligible", activation["failed_conditions"])
        self.assertIsNone(result["selected_lesson_id"])

    def test_candidate_stale_does_not_activate(self):
        link = link_lesson_supersede(_lesson_001(stale=True), _lesson_004(stale=True))
        result = select_lesson_for_context([link["old_lesson"], link["new_lesson"]], CONTEXT)
        activation = result["supersede_activation"]

        self.assertFalse(activation["activation_applied"])
        self.assertFalse(activation["candidate_not_stale"])
        self.assertIn("candidate_not_stale", activation["failed_conditions"])
        self.assertIsNone(result["selected_lesson_id"])

    def test_candidate_ineligible_does_not_activate(self):
        link = link_lesson_supersede(_lesson_001(stale=True), _lesson_004(object_id="cube_002"))
        result = select_lesson_for_context([link["old_lesson"], link["new_lesson"]], CONTEXT)
        activation = result["supersede_activation"]

        self.assertFalse(activation["activation_applied"])
        self.assertFalse(activation["candidate_eligible"])
        self.assertIn("candidate_eligible", activation["failed_conditions"])
        self.assertIsNone(result["selected_lesson_id"])

    def test_candidate_missing_does_not_activate(self):
        old = _lesson_001(stale=True)
        old["superseded_by"] = "lesson_missing"
        result = select_lesson_for_context([old], CONTEXT)
        activation = result["supersede_activation"]

        self.assertFalse(activation["activation_applied"])
        self.assertFalse(activation["candidate_exists"])
        self.assertIn("candidate_exists", activation["failed_conditions"])
        self.assertIsNone(result["selected_lesson_id"])

    def test_old_lesson_not_stale_does_not_trigger_activation(self):
        link = link_lesson_supersede(_lesson_001(stale=False), _lesson_004())
        result = select_lesson_for_context([link["old_lesson"], link["new_lesson"]], CONTEXT)

        self.assertIsNone(result["supersede_activation"])
        self.assertEqual(result["supersede_activations"], [])
        self.assertIsNone(result["selected_lesson_id"])

    def test_supersede_link_is_not_authorization(self):
        link = link_lesson_supersede(_lesson_001(stale=True), _lesson_004(object_id="cube_002"))
        result = select_lesson_for_context([link["old_lesson"], link["new_lesson"]], CONTEXT)
        activation = result["supersede_activation"]

        self.assertFalse(activation["candidate_eligible"])
        self.assertFalse(activation["activation_applied"])
        self.assertIsNone(result["selected_lesson_id"])

    def test_conflict_behavior_does_not_prefer_replacement(self):
        link = link_lesson_supersede(_lesson_001(stale=True), _lesson_004())
        result = select_lesson_for_decision_point([link["old_lesson"], link["new_lesson"], _lesson_002()], DECISION_POINT)
        activation = result["supersede_activation"]

        self.assertTrue(result["conflict_detected"])
        self.assertEqual(result["conflict_resolution"], "require_review")
        self.assertIsNone(result["selected_lesson_id"])
        self.assertIsNone(result["selected_action"])
        self.assertFalse(activation["activation_applied"])
        self.assertIn("conflict_unresolved", activation["failed_conditions"])

    def test_multi_layer_supersede_chain_is_not_followed(self):
        lesson_004 = _lesson_004()
        lesson_004["superseded_by"] = "lesson_007"
        link = link_lesson_supersede(_lesson_001(stale=True), lesson_004)
        result = select_lesson_for_context([link["old_lesson"], link["new_lesson"], _lesson_007()], CONTEXT)
        activation = result["supersede_activation"]

        self.assertEqual(result["selected_lesson_id"], "lesson_004")
        self.assertNotEqual(result["selected_lesson_id"], "lesson_007")
        self.assertFalse(activation["chain_followed"])

    def test_activation_does_not_modify_lifecycle_metadata(self):
        link = link_lesson_supersede(_lesson_001(stale=True), _lesson_004())
        lessons = [link["old_lesson"], link["new_lesson"]]
        before = copy.deepcopy(lessons)

        result = select_lesson_for_context(lessons, CONTEXT)

        self.assertTrue(result["supersede_activation"]["activation_applied"])
        self.assertEqual(lessons, before)
        self.assertEqual(lessons[0]["status"], before[0]["status"])
        self.assertEqual(lessons[0]["stale"], before[0]["stale"])
        self.assertEqual(lessons[0]["superseded_by"], before[0]["superseded_by"])
        self.assertEqual(lessons[1]["status"], before[1]["status"])
        self.assertEqual(lessons[1]["stale"], before[1]["stale"])
        self.assertEqual(lessons[1]["supersedes"], before[1]["supersedes"])

    def test_cli_has_no_lifecycle_write_command(self):
        process = subprocess.run(
            [sys.executable, "-m", "ashl_core.teaching_cli", "--help"],
            check=True,
            capture_output=True,
            text=True,
        )
        help_text = process.stdout.lower()
        forbidden = [
            "apply-replacement",
            "enable-replacement",
            "disable-old-lesson",
            "mark-stale",
            "unmark-stale",
            "activate-supersede",
        ]
        for phrase in forbidden:
            self.assertNotIn(phrase, help_text)


if __name__ == "__main__":
    unittest.main()
