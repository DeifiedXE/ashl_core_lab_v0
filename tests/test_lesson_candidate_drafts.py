import copy
import unittest

from ashl_core.failure_events import (
    build_failure_event,
    build_lesson_candidate_input_trace,
    normalize_failure_event_trace,
)
from ashl_core.lesson_candidate_drafts import build_lesson_candidate_draft_trace


def _bridge_trace():
    event = build_failure_event(
        trace_id="trace_001",
        failure_event_id="failure_001",
        motivation_type="sandbox_task",
        motivation_source="standing_task",
        goal={"goal_type": "pick_up_object"},
        action_intent={"action_type": "pick_up", "target_id": "cube_001"},
        expected_outcome={"type": "object_state", "expected_state": "held"},
        actual_outcome={"type": "object_state", "actual_state": "not_moved"},
        evaluator_source="sandbox_checker",
        mismatch=True,
        failure_reason_id="object_not_picked_up",
        failure_type="action_result_mismatch",
        needs_review=True,
    )
    return build_lesson_candidate_input_trace(normalize_failure_event_trace(event))


MAIN_DRAFT_FIELDS = [
    "proposed_lesson_summary",
    "proposed_applicability_conditions",
    "proposed_action_correction",
    "evidence_refs",
    "similar_context_hint_refs",
    "evaluator_source",
]


class LessonCandidateDraftTests(unittest.TestCase):
    def test_builds_trace_only_draft(self):
        draft = build_lesson_candidate_draft_trace(_bridge_trace())

        self.assertTrue(draft["draft_trace"])
        self.assertEqual(draft["draft_type"], "lesson_candidate_draft")
        self.assertEqual(draft["authority_boundary"], "trace_only_draft")
        self.assertTrue(draft["not_a_lesson_candidate"])
        self.assertEqual(draft["type"], "lesson_candidate_draft_trace")

    def test_draft_is_review_gated(self):
        draft = build_lesson_candidate_draft_trace(_bridge_trace())

        self.assertTrue(draft["needs_review"])
        self.assertEqual(draft["review_state"], "pending")
        self.assertTrue(draft["not_approved"])
        self.assertTrue(draft["not_active"])
        self.assertTrue(draft["not_selection_eligible"])
        self.assertTrue(draft["not_internalized"])
        self.assertTrue(draft["not_written_to_lesson_store"])
        self.assertTrue(draft["not_written_to_long_term_memory"])

    def test_every_draft_field_declares_source_authority_and_review_required(self):
        draft = build_lesson_candidate_draft_trace(_bridge_trace())

        for field in MAIN_DRAFT_FIELDS:
            self.assertIn("source", draft[field])
            self.assertIn("authority", draft[field])
            self.assertIn("review_required", draft[field])
            self.assertTrue(draft[field]["review_required"])

    def test_draft_fields_do_not_use_unknown_sources(self):
        draft = build_lesson_candidate_draft_trace(_bridge_trace())
        forbidden = {"TBD", "unknown", "inferred_without_trace", "llm_default", None, ""}

        for field in MAIN_DRAFT_FIELDS:
            self.assertNotIn(draft[field]["source"], forbidden)

    def test_draft_is_not_approved_active_or_selectable_lesson(self):
        draft = build_lesson_candidate_draft_trace(_bridge_trace())

        self.assertTrue(draft["not_a_lesson_candidate"])
        self.assertTrue(draft["not_approved"])
        self.assertTrue(draft["not_active"])
        self.assertTrue(draft["not_selection_eligible"])
        self.assertTrue(draft["not_internalized"])
        self.assertTrue(draft["not_written_to_lesson_store"])
        self.assertTrue(draft["not_written_to_long_term_memory"])
        self.assertNotIn("approved", draft)
        self.assertNotIn("active", draft)
        self.assertNotIn("selection_eligible", draft)
        self.assertNotIn("internalized", draft)
        self.assertNotIn("written_to_lesson_store", draft)
        self.assertNotIn("written_to_long_term_memory", draft)

    def test_review_required_is_always_true_for_main_fields(self):
        draft = build_lesson_candidate_draft_trace(_bridge_trace())

        for field in MAIN_DRAFT_FIELDS:
            self.assertIs(draft[field]["review_required"], True)

    def test_review_required_is_not_missing_none_or_false(self):
        draft = build_lesson_candidate_draft_trace(_bridge_trace())

        for field in MAIN_DRAFT_FIELDS:
            self.assertIn("review_required", draft[field])
            self.assertIsNotNone(draft[field]["review_required"])
            self.assertIsNot(draft[field]["review_required"], False)

    def test_input_review_required_false_override_is_ignored(self):
        bridge = _bridge_trace()
        bridge["proposed_lesson_summary"] = {"review_required": False}
        bridge["evidence_refs"] = {"review_required": False}

        draft = build_lesson_candidate_draft_trace(bridge)

        for field in MAIN_DRAFT_FIELDS:
            self.assertIs(draft[field]["review_required"], True)

    def test_semantic_key_is_not_proof_or_eligibility_source(self):
        draft = build_lesson_candidate_draft_trace(_bridge_trace())
        semantic_key = draft["similar_context_hint_refs"]["value"]["semantic_key"]
        applicability = draft["proposed_applicability_conditions"]["value"]

        self.assertEqual(semantic_key["authority"], "non_authoritative_review_required")
        self.assertEqual(draft["similar_context_hint_refs"]["authority"], "hint_not_proof")
        self.assertNotIn(semantic_key, applicability)
        self.assertNotIn("semantic_key_proof", draft)
        self.assertNotIn("semantic_key_eligibility", draft)
        self.assertNotIn("selection_eligible", draft)
        self.assertNotIn("eligible", draft)

    def test_proposed_action_correction_is_not_executable_action(self):
        draft = build_lesson_candidate_draft_trace(_bridge_trace())

        self.assertEqual(draft["proposed_action_correction"]["authority"], "draft_correction_not_executable")
        self.assertNotIn("executable_action", draft)
        self.assertNotIn("action_candidate", draft)
        self.assertNotIn("ready_to_execute", draft)

    def test_evidence_refs_are_not_proof_or_approval(self):
        draft = build_lesson_candidate_draft_trace(_bridge_trace())

        self.assertEqual(draft["evidence_refs"]["authority"], "evidence_pointers_not_proof")
        self.assertNotIn("proof", draft)
        self.assertNotIn("approval_source", draft)
        self.assertNotIn("approved", draft)
        self.assertTrue(draft["not_approved"])

    def test_proposed_applicability_conditions_are_not_verified_proof(self):
        draft = build_lesson_candidate_draft_trace(_bridge_trace())

        self.assertEqual(draft["proposed_applicability_conditions"]["authority"], "draft_conditions_not_proof")
        self.assertNotIn("verified_applicability", draft)
        self.assertNotIn("applicability_proof", draft)
        self.assertNotIn("selection_eligible", draft)

    def test_raw_or_normalized_input_cannot_build_draft(self):
        event = build_failure_event(
            motivation_type="sandbox_task",
            motivation_source="standing_task",
            goal={"goal_type": "pick_up_object"},
            action_intent={"action_type": "pick_up", "target_id": "cube_001"},
            expected_outcome={"type": "object_state"},
            actual_outcome={"type": "object_state"},
            evaluator_source="sandbox_checker",
            mismatch=True,
            failure_reason_id="object_not_picked_up",
        )
        normalized = normalize_failure_event_trace(event)

        with self.assertRaises(ValueError):
            build_lesson_candidate_draft_trace(event)
        with self.assertRaises(ValueError):
            build_lesson_candidate_draft_trace(normalized)

    def test_build_draft_does_not_mutate_input(self):
        bridge = _bridge_trace()
        before = copy.deepcopy(bridge)

        build_lesson_candidate_draft_trace(bridge)

        self.assertEqual(bridge, before)


if __name__ == "__main__":
    unittest.main()
