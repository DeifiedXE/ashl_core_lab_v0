import copy
import unittest

from ashl_core.fake_sandbox import build_initial_sandbox_state, pick_up
from ashl_core.failure_events import build_failure_event, validate_failure_event
from ashl_core.lesson_store import (
    build_conflict_review_resolution_dry_run,
    build_lesson_from_failure,
    select_lesson_for_decision_point,
)
from run_all_smoke_tests import (
    smoke_lesson_memory_layer_relation_docs,
    smoke_phase0_assumption_consistency_audit,
)


def _valid_event(**overrides):
    event = build_failure_event(
        trace_id="trace_001",
        failure_event_id="failure_001",
        motivation_type="sandbox_task",
        motivation_source="standing_task",
        goal="pick_up_object",
        action_intent={"action_type": "pick_up", "target_id": "cube_001"},
        expected_outcome={"type": "object_state", "target_id": "cube_001", "expected_state": "held"},
        actual_outcome={"type": "object_state", "target_id": "cube_001", "actual_state": "not_moved"},
        evaluator_source="sandbox_checker",
        mismatch=True,
        failure_reason_id="object_not_picked_up",
        failure_type="action_result_mismatch",
        needs_review=False,
        similar_context_hint=None,
    )
    event.update(overrides)
    return event


class FailureEventTests(unittest.TestCase):
    def test_valid_structured_failure_event_passes_validation(self):
        trace = validate_failure_event(_valid_event(needs_review=True))

        self.assertTrue(trace["valid_failure_event"])
        self.assertEqual(trace["event_classification"], "valid_failure_event")
        self.assertEqual(trace["missing_required_fields"], [])
        self.assertTrue(trace["authoritative_failure_reason_allowed"])
        self.assertFalse(trace["llm_authoritative_source"])

    def test_missing_expected_outcome_blocks_authoritative_failure(self):
        trace = validate_failure_event(_valid_event(expected_outcome=None))

        self.assertFalse(trace["valid_failure_event"])
        self.assertEqual(trace["event_classification"], "unclassified_event")
        self.assertIn("expected_outcome", trace["missing_required_fields"])
        self.assertFalse(trace["authoritative_failure_reason_allowed"])

    def test_missing_actual_outcome_blocks_authoritative_failure(self):
        trace = validate_failure_event(_valid_event(actual_outcome=None))

        self.assertFalse(trace["valid_failure_event"])
        self.assertEqual(trace["event_classification"], "unclassified_event")
        self.assertIn("actual_outcome", trace["missing_required_fields"])
        self.assertFalse(trace["authoritative_failure_reason_allowed"])

    def test_mismatch_false_does_not_produce_authoritative_failure(self):
        trace = validate_failure_event(_valid_event(mismatch=False))

        self.assertFalse(trace["authoritative_failure_reason_allowed"])
        self.assertFalse(trace["valid_failure_event"])
        self.assertEqual(trace["event_classification"], "non_failure_event")
        self.assertEqual(trace["reason"], "no_mismatch_not_failure")

    def test_llm_only_evaluator_cannot_authorize_failure_reason(self):
        trace = validate_failure_event(_valid_event(evaluator_source="llm"))

        self.assertTrue(trace["llm_authoritative_source"])
        self.assertFalse(trace["authoritative_failure_reason_allowed"])
        self.assertTrue(trace["needs_review"])

    def test_missing_failure_reason_id_requires_review(self):
        trace = validate_failure_event(_valid_event(failure_reason_id=None))

        self.assertFalse(trace["valid_failure_event"])
        self.assertFalse(trace["authoritative_failure_reason_allowed"])
        self.assertIn("failure_reason_id", trace["missing_required_fields"])
        self.assertTrue(trace["needs_review"])
        self.assertEqual(trace["reason"], "normalized_failure_reason_missing")

    def test_human_notes_cannot_replace_structured_fields(self):
        trace = validate_failure_event(
            build_failure_event(
                motivation_type="sandbox_task",
                motivation_source=None,
                goal="pick_up_object",
                action_intent={"action_type": "pick_up", "target_id": "cube_001"},
                expected_outcome=None,
                actual_outcome=None,
                evaluator_source="human_teacher",
                mismatch=True,
                failure_reason_id="object_not_picked_up",
                human_notes="The cube did not move.",
            )
        )

        self.assertFalse(trace["valid_failure_event"])
        self.assertFalse(trace["authoritative_failure_reason_allowed"])
        self.assertIn("expected_outcome", trace["missing_required_fields"])
        self.assertIn("actual_outcome", trace["missing_required_fields"])
        self.assertNotIn("human_notes", trace["missing_required_fields"])

    def test_similar_context_hint_is_preserved_but_not_evaluated(self):
        hint = {
            "structure_key": "pick_up:cube",
            "semantic_key": "object_interaction",
            "causal_key": "not_moved",
            "repetition_key": "cube_pickup_failure",
        }
        trace = validate_failure_event(_valid_event(similar_context_hint=hint))

        self.assertTrue(trace["similar_context_hint_present"])
        self.assertEqual(
            trace["similar_context_hint_keys"],
            ["causal_key", "repetition_key", "semantic_key", "structure_key"],
        )
        self.assertNotIn("similarity_score", trace)
        self.assertNotIn("generalized_lesson", trace)
        self.assertNotIn("lesson_candidate", trace)

    def test_validation_is_side_effect_free(self):
        event = _valid_event()
        before = copy.deepcopy(event)

        first = validate_failure_event(event)
        second = validate_failure_event(event)

        self.assertEqual(event, before)
        self.assertEqual(first, second)

    def test_failure_events_module_does_not_affect_existing_lesson_selection(self):
        east = build_lesson_from_failure("session_east", pick_up(build_initial_sandbox_state(), "cube_001"))
        west = build_lesson_from_failure(
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
        before = select_lesson_for_decision_point([east, west], "before_retry_pick_up_cube")

        validate_failure_event(_valid_event())
        after = select_lesson_for_decision_point([east, west], "before_retry_pick_up_cube")

        self.assertEqual(before, after)

    def test_failure_events_module_does_not_affect_conflict_review_dry_run(self):
        east = build_lesson_from_failure("session_east", pick_up(build_initial_sandbox_state(), "cube_001"))
        west = build_lesson_from_failure(
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
        conflict = select_lesson_for_decision_point([east, west], "before_retry_pick_up_cube")
        before = build_conflict_review_resolution_dry_run(conflict, [], candidate_lesson_id="lesson_002")

        validate_failure_event(_valid_event())
        after = build_conflict_review_resolution_dry_run(conflict, [], candidate_lesson_id="lesson_002")

        self.assertEqual(before, after)
        self.assertFalse(after["conflict_changed"])
        self.assertFalse(after["resolution_applied"])

    def test_failure_events_module_does_not_affect_docs_smoke_terms(self):
        validate_failure_event(_valid_event())

        self.assertTrue(smoke_lesson_memory_layer_relation_docs()["passed"])
        self.assertTrue(smoke_phase0_assumption_consistency_audit()["passed"])


if __name__ == "__main__":
    unittest.main()
