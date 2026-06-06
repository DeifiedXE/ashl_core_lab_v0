import copy
import unittest

from ashl_core.fake_sandbox import build_initial_sandbox_state, pick_up
from ashl_core.failure_events import (
    build_failure_event,
    build_lesson_candidate_input_trace,
    normalize_failure_event_trace,
    validate_failure_event,
)
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

    def test_normalization_does_not_mutate_failure_event(self):
        event = _valid_event(needs_review=True)
        before = copy.deepcopy(event)

        normalize_failure_event_trace(event)

        self.assertEqual(event, before)

    def test_normalization_returns_deterministic_view(self):
        first_event = _valid_event(raw_event_ref={"transient": "first"})
        second_event = _valid_event(raw_event_ref={"transient": "second"}, human_notes="Different raw note")

        first = normalize_failure_event_trace(first_event)
        second = normalize_failure_event_trace(second_event)

        self.assertEqual(first["failure_norm_key"], second["failure_norm_key"])
        self.assertEqual(first["motivation_type"], second["motivation_type"])
        self.assertEqual(first["goal_type"], second["goal_type"])
        self.assertEqual(first["action_type"], second["action_type"])
        self.assertEqual(first["expected_outcome_type"], second["expected_outcome_type"])
        self.assertEqual(first["actual_outcome_type"], second["actual_outcome_type"])
        self.assertEqual(first["mismatch_type"], second["mismatch_type"])
        self.assertEqual(first["evaluator_source"], second["evaluator_source"])

    def test_normalization_preserves_needs_review_boundary(self):
        trace = normalize_failure_event_trace(_valid_event(needs_review=True, review_state="pending_review"))

        self.assertTrue(trace["needs_review"])
        self.assertEqual(trace["review_state"], "pending_review")
        self.assertEqual(trace["authority_boundary"], "trace_only")

    def test_normalization_preserves_evaluator_source_boundary(self):
        trace = normalize_failure_event_trace(_valid_event(evaluator_source="sandbox_checker"))

        self.assertEqual(trace["evaluator_source"], "sandbox_checker")
        self.assertEqual(trace["normalization_authority"], "not_authoritative")

    def test_normalization_does_not_create_lesson_candidate_or_side_effects(self):
        trace = normalize_failure_event_trace(_valid_event())

        self.assertNotIn("lesson_candidate", trace)
        self.assertFalse(trace["lesson_candidate_created"])
        self.assertEqual(trace["side_effects"], [])

    def test_normalization_does_not_make_llm_only_event_authoritative(self):
        trace = normalize_failure_event_trace(
            _valid_event(
                evaluator_source="llm",
                expected_outcome=None,
                actual_outcome=None,
                raw_event_ref="I think the cube failed because it looked stuck.",
            )
        )

        self.assertTrue(trace["normalized"])
        self.assertTrue(trace["llm_authoritative_source"])
        self.assertEqual(trace["normalization_authority"], "not_authoritative")
        self.assertEqual(trace["authority_boundary"], "trace_only")
        self.assertIn("missing", trace["failure_norm_key"])
        self.assertNotIn("lesson_candidate", trace)

    def test_bridge_returns_trace_only_input_view(self):
        normalized = normalize_failure_event_trace(_valid_event(needs_review=True))

        bridge = build_lesson_candidate_input_trace(normalized)

        self.assertTrue(bridge["bridge_trace"])
        self.assertEqual(bridge["bridge_type"], "failure_event_to_lesson_candidate_input")
        self.assertEqual(bridge["authority_boundary"], "trace_only_input_view")
        self.assertTrue(bridge["not_a_lesson_candidate"])
        self.assertEqual(bridge["type"], "lesson_candidate_input_trace")

    def test_bridge_does_not_mutate_normalized_input(self):
        normalized = normalize_failure_event_trace(_valid_event(needs_review=True))
        before = copy.deepcopy(normalized)

        build_lesson_candidate_input_trace(normalized)

        self.assertEqual(normalized, before)

    def test_bridge_preserves_needs_review(self):
        normalized = normalize_failure_event_trace(_valid_event(needs_review=True, review_state="pending_review"))

        bridge = build_lesson_candidate_input_trace(normalized)

        self.assertTrue(bridge["needs_review"])
        self.assertEqual(bridge["review_state"], "pending_review")

    def test_bridge_preserves_evaluator_source(self):
        normalized = normalize_failure_event_trace(_valid_event(evaluator_source="sandbox_checker"))

        bridge = build_lesson_candidate_input_trace(normalized)

        self.assertEqual(bridge["evaluator_source"], "sandbox_checker")

    def test_bridge_does_not_create_lesson_candidate(self):
        bridge = build_lesson_candidate_input_trace(normalize_failure_event_trace(_valid_event()))

        self.assertNotIn("lesson_candidate", bridge)
        self.assertNotIn("approved_lesson", bridge)
        self.assertNotIn("eligible_lesson", bridge)
        self.assertNotIn("active_lesson", bridge)
        self.assertTrue(bridge["not_a_lesson_candidate"])
        self.assertFalse(bridge["lesson_candidate_created"])
        self.assertFalse(bridge["lesson_store_written"])
        self.assertEqual(bridge["side_effects"], [])

    def test_bridge_similar_context_hint_records_source_and_authority(self):
        bridge = build_lesson_candidate_input_trace(normalize_failure_event_trace(_valid_event()))
        hint = bridge["similar_context_hint"]

        self.assertEqual(hint["structure_key"]["source"], "schema_fields")
        self.assertEqual(hint["structure_key"]["authority"], "deterministic_hint")
        self.assertEqual(hint["causal_key"]["source"], "mismatch_type")
        self.assertEqual(hint["causal_key"]["authority"], "structured_hint")
        self.assertEqual(hint["semantic_key"]["source"], "not_provided")
        self.assertEqual(hint["semantic_key"]["authority"], "non_authoritative_review_required")

    def test_bridge_semantic_key_is_not_proof_or_eligibility(self):
        bridge = build_lesson_candidate_input_trace(normalize_failure_event_trace(_valid_event()))
        semantic_key = bridge["similar_context_hint"]["semantic_key"]

        self.assertIsNone(semantic_key["value"])
        self.assertNotEqual(semantic_key["authority"], "deterministic_hint")
        self.assertNotEqual(semantic_key["authority"], "proof")
        self.assertNotIn("eligible", semantic_key)
        self.assertNotIn("eligibility", semantic_key)
        self.assertNotIn("eligible", bridge)
        self.assertNotIn("eligibility", bridge)
        self.assertNotIn("selection_eligible", bridge)

    def test_bridge_rejects_non_normalized_input(self):
        with self.assertRaises(ValueError):
            build_lesson_candidate_input_trace(_valid_event())

        with self.assertRaises(ValueError):
            build_lesson_candidate_input_trace({"type": "raw_failure_event"})

    def test_missing_expected_outcome_cannot_enter_bridge(self):
        event = _valid_event(expected_outcome=None)
        validation = validate_failure_event(event)
        normalized = normalize_failure_event_trace(event)

        self.assertFalse(validation["valid_failure_event"])
        self.assertFalse(normalized["valid_normalized_failure_event"])
        with self.assertRaises(ValueError):
            build_lesson_candidate_input_trace(normalized)

    def test_missing_actual_outcome_cannot_enter_bridge(self):
        event = _valid_event(actual_outcome=None)
        validation = validate_failure_event(event)
        normalized = normalize_failure_event_trace(event)

        self.assertFalse(validation["valid_failure_event"])
        self.assertFalse(normalized["valid_normalized_failure_event"])
        with self.assertRaises(ValueError):
            build_lesson_candidate_input_trace(normalized)

    def test_llm_only_raw_description_cannot_authorize_failure_reason_at_bridge(self):
        event = _valid_event(evaluator_source="llm")
        event["raw_failure_description"] = "The object probably failed because it felt blocked."
        event["llm_summary"] = "Likely pickup failure."

        validation = validate_failure_event(event)
        normalized = normalize_failure_event_trace(event)

        self.assertTrue(validation["llm_authoritative_source"])
        self.assertFalse(validation["authoritative_failure_reason_allowed"])
        self.assertFalse(normalized["valid_normalized_failure_event"])
        self.assertTrue(normalized["llm_authoritative_source"])
        self.assertNotIn("authoritative_failure_reason", normalized)
        self.assertNotIn("normalized_failure_reason", normalized)
        with self.assertRaises(ValueError):
            build_lesson_candidate_input_trace(normalized)

    def test_typed_unknown_outcomes_are_invalid_for_failure_learning(self):
        event = _valid_event(
            expected_outcome={"type": "object_state", "status": "unknown"},
            actual_outcome={"type": "object_state", "status": "unknown"},
        )

        validation = validate_failure_event(event)
        normalized = normalize_failure_event_trace(event)

        self.assertFalse(validation["valid_failure_event"])
        self.assertFalse(validation["authoritative_failure_reason_allowed"])
        self.assertEqual(validation["reason"], "unknown_vs_unknown_is_not_evidence")
        self.assertFalse(normalized["valid_normalized_failure_event"])
        self.assertEqual(normalized["expected_outcome_type"], "unknown")
        self.assertEqual(normalized["actual_outcome_type"], "unknown")
        with self.assertRaises(ValueError):
            build_lesson_candidate_input_trace(normalized)

    def test_typed_not_available_outcomes_are_invalid_for_failure_learning(self):
        event = _valid_event(
            expected_outcome={"type": "action_result", "status": "not_available"},
            actual_outcome={"type": "action_result", "status": "not_available"},
        )

        validation = validate_failure_event(event)
        normalized = normalize_failure_event_trace(event)

        self.assertFalse(validation["valid_failure_event"])
        self.assertEqual(validation["reason"], "unknown_vs_unknown_is_not_evidence")
        self.assertFalse(normalized["valid_normalized_failure_event"])
        with self.assertRaises(ValueError):
            build_lesson_candidate_input_trace(normalized)

    def test_nested_unknown_status_outcomes_are_invalid_even_with_type(self):
        event = _valid_event(
            expected_outcome={"type": "perception_result", "value": {"status": "unknown"}},
            actual_outcome={"type": "perception_result", "value": {"status": "unknown"}},
        )

        validation = validate_failure_event(event)
        normalized = normalize_failure_event_trace(event)

        self.assertFalse(validation["valid_failure_event"])
        self.assertFalse(validation["authoritative_failure_reason_allowed"])
        self.assertEqual(validation["reason"], "unknown_vs_unknown_is_not_evidence")
        self.assertFalse(normalized["valid_normalized_failure_event"])
        with self.assertRaises(ValueError):
            build_lesson_candidate_input_trace(normalized)


class TestSystemFaultBothUnknown(unittest.TestCase):
    """v2.11a: When both expected and actual are unknown-like (strict), trigger system_fault."""

    def _base_event(self, expected, actual):
        return build_failure_event(
            trace_id="trace_sf_001",
            failure_event_id="fe_sf_001",
            motivation_type="sandbox_task",
            goal="test_goal",
            action_intent={"action_type": "test_action"},
            expected_outcome=expected,
            actual_outcome=actual,
            evaluator_source="human",
            mismatch=True,
            failure_reason_id="test_fault_reason",
        )

    # 8.1 None / None
    def test_none_none_triggers_system_fault(self):
        event = self._base_event(None, None)
        validation = validate_failure_event(event)
        self.assertFalse(validation["valid_failure_event"])
        self.assertFalse(validation["authoritative_failure_reason_allowed"])
        self.assertEqual(validation["event_classification"], "system_fault")
        self.assertEqual(validation["reason"], "insufficient_expected_actual_contrast")

    # 8.2 "unknown" / "unknown"
    def test_unknown_string_triggers_system_fault(self):
        event = self._base_event("unknown", "unknown")
        validation = validate_failure_event(event)
        self.assertFalse(validation["valid_failure_event"])
        self.assertFalse(validation["authoritative_failure_reason_allowed"])
        self.assertEqual(validation["event_classification"], "system_fault")
        self.assertEqual(validation["reason"], "insufficient_expected_actual_contrast")

    # 8.3 "" / "   "
    def test_empty_and_whitespace_triggers_system_fault(self):
        event = self._base_event("", "   ")
        validation = validate_failure_event(event)
        self.assertFalse(validation["valid_failure_event"])
        self.assertFalse(validation["authoritative_failure_reason_allowed"])
        self.assertEqual(validation["event_classification"], "system_fault")
        self.assertEqual(validation["reason"], "insufficient_expected_actual_contrast")

    # 8.4 "UNKNOWN" / "Unknown"
    def test_mixed_case_unknown_triggers_system_fault(self):
        event = self._base_event("UNKNOWN", "Unknown")
        validation = validate_failure_event(event)
        self.assertFalse(validation["valid_failure_event"])
        self.assertFalse(validation["authoritative_failure_reason_allowed"])
        self.assertEqual(validation["event_classification"], "system_fault")
        self.assertEqual(validation["reason"], "insufficient_expected_actual_contrast")

    # 8.5 0 / 0 — must NOT trigger system_fault via unknown-like rule
    def test_zero_zero_not_system_fault_from_unknown_rule(self):
        event = self._base_event(0, 0)
        validation = validate_failure_event(event)
        self.assertNotEqual(validation["event_classification"], "system_fault")
        self.assertNotEqual(validation.get("reason"), "insufficient_expected_actual_contrast")

    # 8.5 False / False — must NOT trigger system_fault via unknown-like rule
    def test_false_false_not_system_fault_from_unknown_rule(self):
        event = self._base_event(False, False)
        validation = validate_failure_event(event)
        self.assertNotEqual(validation["event_classification"], "system_fault")
        self.assertNotEqual(validation.get("reason"), "insufficient_expected_actual_contrast")

    # 8.5 [] / [] — must NOT trigger system_fault via unknown-like rule
    def test_empty_list_not_system_fault_from_unknown_rule(self):
        event = self._base_event([], [])
        validation = validate_failure_event(event)
        self.assertNotEqual(validation["event_classification"], "system_fault")
        self.assertNotEqual(validation.get("reason"), "insufficient_expected_actual_contrast")

    # 8.5 {} / {} — must NOT trigger system_fault via unknown-like rule
    def test_empty_dict_not_system_fault_from_unknown_rule(self):
        event = self._base_event({}, {})
        validation = validate_failure_event(event)
        self.assertNotEqual(validation["event_classification"], "system_fault")
        self.assertNotEqual(validation.get("reason"), "insufficient_expected_actual_contrast")

    # system_fault must not produce authoritative failure_reason
    def test_system_fault_not_authoritative(self):
        event = self._base_event(None, None)
        validation = validate_failure_event(event)
        normalized = normalize_failure_event_trace(event)
        self.assertFalse(validation["authoritative_failure_reason_allowed"])
        self.assertFalse(normalized["valid_normalized_failure_event"])
        self.assertNotIn("authoritative_failure_reason", normalized)
        with self.assertRaises(ValueError):
            build_lesson_candidate_input_trace(normalized)


if __name__ == "__main__":
    unittest.main()
