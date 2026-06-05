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
from ashl_core.teaching_cli import run_lifecycle_display


DECISION_POINT = "before_retry_pick_up_cube"
CONTEXT = {"task": "pick_up", "object_id": "cube_001", "decision_point": DECISION_POINT}
REQUIRED_ACTIVATION_KEYS = {
    "source_lesson_id",
    "candidate_lesson_id",
    "old_lesson_stale",
    "old_lesson_has_superseded_by",
    "candidate_exists",
    "candidate_active",
    "candidate_not_stale",
    "candidate_eligible",
    "activation_source",
    "activation_applied",
    "failed_conditions",
}


def _lesson_001(stale=False):
    lesson = build_lesson_from_failure("session_east", pick_up(build_initial_sandbox_state(), "cube_001"))
    lesson["object_id"] = "cube_001"
    lesson["stale"] = False
    lesson["stale_reason"] = None
    if stale:
        lesson = mark_lesson_stale(lesson)
        lesson["stale_reason"] = "manual: audit fixture"
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
        "stale_reason": "manual: candidate stale" if stale else None,
        "confidence": "manual_fixture",
    }


def _lesson_007():
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


class ActivationAuditTests(unittest.TestCase):
    def test_activation_trace_contains_all_required_fields(self):
        link = link_lesson_supersede(_lesson_001(stale=True), _lesson_004())
        result = select_lesson_for_context([link["old_lesson"], link["new_lesson"]], CONTEXT)
        activation = result["supersede_activation"]

        self.assertTrue(REQUIRED_ACTIVATION_KEYS.issubset(activation.keys()))

    def test_successful_activation_has_empty_failed_conditions(self):
        link = link_lesson_supersede(_lesson_001(stale=True), _lesson_004())
        activation = select_lesson_for_context([link["old_lesson"], link["new_lesson"]], CONTEXT)[
            "supersede_activation"
        ]

        self.assertTrue(activation["activation_applied"])
        self.assertEqual(activation["failed_conditions"], [])
        self.assertEqual(activation["activation_source"], "supersede_link")

    def test_failed_activation_lists_correct_condition(self):
        link = link_lesson_supersede(_lesson_001(stale=True), _lesson_004(status="inactive"))
        activation = select_lesson_for_context([link["old_lesson"], link["new_lesson"]], CONTEXT)[
            "supersede_activation"
        ]

        self.assertFalse(activation["activation_applied"])
        self.assertNotEqual(activation["failed_conditions"], [])
        self.assertIn("candidate_active", activation["failed_conditions"])

    def test_multiple_failed_conditions_are_all_listed(self):
        link = link_lesson_supersede(
            _lesson_001(stale=True),
            _lesson_004(status="inactive", stale=True, object_id="cube_002"),
        )
        activation = select_lesson_for_context([link["old_lesson"], link["new_lesson"]], CONTEXT)[
            "supersede_activation"
        ]

        self.assertFalse(activation["activation_applied"])
        self.assertIn("candidate_active", activation["failed_conditions"])
        self.assertIn("candidate_not_stale", activation["failed_conditions"])
        self.assertIn("candidate_eligible", activation["failed_conditions"])

    def test_activation_does_not_modify_old_lesson_metadata(self):
        link = link_lesson_supersede(_lesson_001(stale=True), _lesson_004())
        lessons = [link["old_lesson"], link["new_lesson"]]
        before_old = copy.deepcopy(lessons[0])

        select_lesson_for_context(lessons, CONTEXT)

        self.assertEqual(lessons[0]["status"], before_old["status"])
        self.assertEqual(lessons[0]["stale"], before_old["stale"])
        self.assertEqual(lessons[0]["stale_reason"], before_old["stale_reason"])
        self.assertEqual(lessons[0]["superseded_by"], before_old["superseded_by"])
        self.assertEqual(lessons[0].get("supersedes"), before_old.get("supersedes"))

    def test_activation_does_not_modify_candidate_metadata(self):
        link = link_lesson_supersede(_lesson_001(stale=True), _lesson_004())
        lessons = [link["old_lesson"], link["new_lesson"]]
        before_candidate = copy.deepcopy(lessons[1])

        select_lesson_for_context(lessons, CONTEXT)

        self.assertEqual(lessons[1]["status"], before_candidate["status"])
        self.assertEqual(lessons[1]["stale"], before_candidate["stale"])
        self.assertEqual(lessons[1]["stale_reason"], before_candidate["stale_reason"])
        self.assertEqual(lessons[1].get("superseded_by"), before_candidate.get("superseded_by"))
        self.assertEqual(lessons[1]["supersedes"], before_candidate["supersedes"])

    def test_candidate_cannot_bypass_normal_eligibility(self):
        link = link_lesson_supersede(_lesson_001(stale=True), _lesson_004(object_id="cube_002"))
        result = select_lesson_for_context([link["old_lesson"], link["new_lesson"]], CONTEXT)
        activation = result["supersede_activation"]

        self.assertFalse(activation["candidate_eligible"])
        self.assertFalse(activation["activation_applied"])
        self.assertIsNone(result["selected_lesson_id"])

    def test_non_stale_old_lesson_does_not_produce_activation(self):
        link = link_lesson_supersede(_lesson_001(stale=False), _lesson_004())
        result = select_lesson_for_context([link["old_lesson"], link["new_lesson"]], CONTEXT)

        self.assertIsNone(result["supersede_activation"])
        self.assertEqual(result["supersede_activations"], [])
        self.assertIsNone(result["selected_lesson_id"])

    def test_missing_candidate_does_not_crash(self):
        old = _lesson_001(stale=True)
        old["superseded_by"] = "lesson_missing"
        result = select_lesson_for_context([old], CONTEXT)
        activation = result["supersede_activation"]

        self.assertFalse(activation["candidate_exists"])
        self.assertFalse(activation["activation_applied"])
        self.assertIn("candidate_exists", activation["failed_conditions"])

    def test_multilayer_chain_is_not_followed(self):
        lesson_004 = _lesson_004()
        lesson_004["superseded_by"] = "lesson_007"
        link = link_lesson_supersede(_lesson_001(stale=True), lesson_004)
        result = select_lesson_for_context([link["old_lesson"], link["new_lesson"], _lesson_007()], CONTEXT)
        activation = result["supersede_activation"]

        self.assertEqual(activation["candidate_lesson_id"], "lesson_004")
        self.assertFalse(activation["chain_followed"])
        self.assertNotEqual(result["selected_lesson_id"], "lesson_007")

    def test_conflict_behavior_is_independent_from_supersede_link(self):
        link = link_lesson_supersede(_lesson_001(stale=True), _lesson_004())
        result = select_lesson_for_decision_point([link["old_lesson"], link["new_lesson"], _lesson_002()], DECISION_POINT)
        activation = result["supersede_activation"]

        self.assertTrue(result["conflict_detected"])
        self.assertEqual(result["conflict_resolution"], "require_review")
        self.assertIsNone(result["selected_lesson_id"])
        self.assertIsNone(result["selected_action"])
        self.assertFalse(activation["activation_applied"])
        self.assertIn("conflict_unresolved", activation["failed_conditions"])

    def test_replacement_suggestion_and_activation_trace_are_consistent(self):
        link = link_lesson_supersede(_lesson_001(stale=True), _lesson_004())
        result = select_lesson_for_context([link["old_lesson"], link["new_lesson"]], CONTEXT)
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
        link = link_lesson_supersede(_lesson_001(stale=True), _lesson_004())
        lessons = [link["old_lesson"], link["new_lesson"]]
        before = copy.deepcopy(lessons)

        result = run_lifecycle_display(lessons, CONTEXT)

        self.assertTrue(result["read_only"])
        self.assertEqual(lessons, before)
        self.assertEqual(lessons[0]["stale"], before[0]["stale"])
        self.assertEqual(lessons[0]["superseded_by"], before[0]["superseded_by"])
        self.assertEqual(lessons[1]["supersedes"], before[1]["supersedes"])

    def test_cli_has_no_lifecycle_write_commands(self):
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
            "link-supersede",
        ]
        for phrase in forbidden:
            self.assertNotIn(phrase, help_text)


if __name__ == "__main__":
    unittest.main()
