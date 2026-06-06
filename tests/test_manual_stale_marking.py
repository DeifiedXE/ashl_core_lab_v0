import unittest

from ashl_core.fake_sandbox import build_initial_sandbox_state, pick_up, turn
from ashl_core.lesson_store import (
    build_lesson_from_failure,
    build_memory_freeze_notice,
    link_lesson_supersede,
    mark_lesson_stale,
    select_lesson_for_context,
    select_lesson_for_decision_point,
    unmark_lesson_stale,
)


DECISION_POINT = "before_retry_pick_up_cube"


def _lesson_001():
    lesson = build_lesson_from_failure("session_east", pick_up(build_initial_sandbox_state(), "cube_001"))
    lesson["object_id"] = "cube_001"
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


def _run_behavior_from_context_selection(selection):
    state = build_initial_sandbox_state()
    if selection["selected_action"] == "turn(east)":
        state = turn(state, "east")["state"]
    result = pick_up(state, "cube_001")
    return result["result"]


class ManualStaleMarkingTests(unittest.TestCase):
    def test_manual_stale_lesson_is_skipped_by_selection_helper(self):
        stale_lesson = mark_lesson_stale(_lesson_001())
        result = select_lesson_for_context(
            [stale_lesson],
            {"task": "pick_up", "object_id": "cube_001", "decision_point": DECISION_POINT},
        )

        self.assertIsNone(result["selected_lesson_id"])
        self.assertIsNone(result["selected_action"])
        self.assertEqual(result["skipped_lessons"], [{"lesson_id": "lesson_001", "skipped_reason": "stale"}])
        self.assertFalse(result["conflict_detected"])
        self.assertFalse(result["behavior_changed"])
        self.assertNotEqual(result["selected_action"], "turn(east)")

    def test_unstale_restores_single_lesson_causal_control(self):
        stale_lesson = mark_lesson_stale(_lesson_001())
        stale_result = select_lesson_for_context(
            [stale_lesson],
            {"task": "pick_up", "object_id": "cube_001", "decision_point": DECISION_POINT},
        )
        restored_lesson = unmark_lesson_stale(stale_lesson)
        restored_result = select_lesson_for_context(
            [restored_lesson],
            {"task": "pick_up", "object_id": "cube_001", "decision_point": DECISION_POINT},
        )

        self.assertIsNone(stale_result["selected_lesson_id"])
        self.assertEqual(restored_result["selected_lesson_id"], "lesson_001")
        self.assertEqual(restored_result["selected_action"], "turn(east)")
        self.assertEqual(_run_behavior_from_context_selection(restored_result), "success")

    def test_stale_does_not_delete_or_mutate_lesson_identity(self):
        lesson = _lesson_001()
        stale_lesson = mark_lesson_stale(lesson)

        self.assertEqual(stale_lesson["lesson_id"], lesson["lesson_id"])
        self.assertEqual(stale_lesson["source_failure_reason"], lesson["source_failure_reason"])
        self.assertEqual(stale_lesson["suggested_action_before_retry"], lesson["suggested_action_before_retry"])
        self.assertEqual(stale_lesson["decision_point"], lesson["decision_point"])
        self.assertEqual(stale_lesson["object_id"], lesson["object_id"])

    def test_stale_lesson_does_not_create_conflict(self):
        stale_east = mark_lesson_stale(_lesson_001())
        west = _lesson_002()
        result = select_lesson_for_decision_point([stale_east, west], DECISION_POINT)

        self.assertEqual(result["skipped_lessons"], [{"lesson_id": "lesson_001", "skipped_reason": "stale"}])
        self.assertFalse(result["conflict_detected"])
        self.assertEqual(result["selected_lesson_id"], "lesson_002")
        self.assertEqual(result["selected_action"], "turn(west)")


class MemoryFreezeNoticeTests(unittest.TestCase):
    """v2.11c: build_memory_freeze_notice is a pure-data helper; evidence only, no side effects."""

    def test_stale_lesson_produces_memory_freeze_required_notice(self):
        stale = mark_lesson_stale(_lesson_001())
        notice = build_memory_freeze_notice(stale, "lesson marked stale by teacher")

        self.assertEqual(notice["notice_type"], "memory_freeze_required")
        self.assertEqual(notice["source_lesson_id"], "lesson_001")
        self.assertEqual(notice["lesson_lifecycle_state"], "stale")
        self.assertEqual(notice["stale_or_supersede_reason"], "lesson marked stale by teacher")
        self.assertEqual(notice["target"], "learned_principle")
        self.assertEqual(notice["effect"], "evidence_only")
        self.assertFalse(notice["direct_memory_write"])

    def test_superseded_lesson_produces_memory_freeze_required_notice(self):
        lesson_001 = _lesson_001()
        lesson_002 = _lesson_002()
        result = link_lesson_supersede(lesson_001, lesson_002)
        old_lesson = result["old_lesson"]
        notice = build_memory_freeze_notice(old_lesson, "superseded by lesson_002")

        self.assertEqual(notice["notice_type"], "memory_freeze_required")
        self.assertEqual(notice["source_lesson_id"], "lesson_001")
        self.assertEqual(notice["lesson_lifecycle_state"], "superseded")
        self.assertEqual(notice["superseded_by_lesson_id"], "lesson_002")
        self.assertEqual(notice["stale_or_supersede_reason"], "superseded by lesson_002")
        self.assertFalse(notice["direct_memory_write"])

    def test_notice_preserves_source_lesson_id_and_reason(self):
        stale = mark_lesson_stale(_lesson_001())
        notice = build_memory_freeze_notice(stale, "stale_reason_preserved")

        self.assertEqual(notice["source_lesson_id"], stale["lesson_id"])
        self.assertEqual(notice["stale_or_supersede_reason"], "stale_reason_preserved")

    def test_notice_direct_memory_write_is_false(self):
        stale = mark_lesson_stale(_lesson_001())
        notice = build_memory_freeze_notice(stale, "test")

        self.assertFalse(notice["direct_memory_write"])
        self.assertFalse(notice["lesson_store_write"])

    def test_notice_does_not_change_selection_eligibility_or_activation(self):
        stale = mark_lesson_stale(_lesson_001())
        notice = build_memory_freeze_notice(stale, "test")

        self.assertFalse(notice["selection_eligibility_changed"])
        self.assertFalse(notice["activation_changed"])

    def test_notice_effect_is_evidence_only(self):
        stale = mark_lesson_stale(_lesson_001())
        notice = build_memory_freeze_notice(stale, "test")

        self.assertEqual(notice["effect"], "evidence_only")
        self.assertEqual(notice["authority_boundary"], "notice_evidence_only")

    def test_notice_does_not_mutate_lesson(self):
        import copy
        stale = mark_lesson_stale(_lesson_001())
        before = copy.deepcopy(stale)
        build_memory_freeze_notice(stale, "test")

        self.assertEqual(stale, before)

    def test_non_stale_lesson_lifecycle_state_is_reported(self):
        lesson = _lesson_001()  # not stale, not superseded
        notice = build_memory_freeze_notice(lesson, "manual check")
        self.assertEqual(notice["lesson_lifecycle_state"], "not_stale_not_superseded")


if __name__ == "__main__":
    unittest.main()
