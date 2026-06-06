import copy
import unittest

from ashl_core.review_tasks import build_review_task_trace


def _queue_entry(**overrides):
    entry = {
        "id": "queue_001",
        "source_draft_id": "draft_001",
        "source_failure_norm_key": "sandbox_task|pick_up_object|pick_up|object_state|object_state|mismatch_true",
        "semantic_key": "object_interaction",
        "task_state": "created",
    }
    entry.update(overrides)
    return entry


class ReviewTaskTraceTests(unittest.TestCase):
    def test_builds_trace_only_review_task(self):
        trace = build_review_task_trace(_queue_entry())

        self.assertEqual(trace["type"], "review_task_trace")
        self.assertTrue(trace["trace_only"])
        self.assertTrue(trace["not_review_decision"])
        self.assertTrue(trace["not_approval"])
        self.assertTrue(trace["not_rejection"])
        self.assertTrue(trace["not_defer_decision"])

    def test_review_task_completion_does_not_imply_approval(self):
        for task_state in ["completed", "closed", "done", "displayed", "dismissed"]:
            with self.subTest(task_state=task_state):
                trace = build_review_task_trace(_queue_entry(task_state=task_state))

                self.assertEqual(trace["task_state"], task_state)
                self.assertTrue(trace["completion_does_not_imply_approval"])
                self.assertTrue(trace["not_approval"])
                self.assertTrue(trace["not_review_decision"])
                self.assertNotIn("selection_eligible", trace)
                self.assertNotIn("approved", trace)
                self.assertNotIn("review_passed", trace)

    def test_reviewer_identity_is_not_taken_from_queue_entry_or_llm_content(self):
        trace = build_review_task_trace(
            _queue_entry(reviewer_identity="admin_override", reviewer_identity_source="llm_generated")
        )

        self.assertIsNone(trace["reviewer_identity"])
        self.assertNotEqual(trace["reviewer_identity"], "admin_override")
        self.assertEqual(trace["reviewer_identity_source"], "not_available_until_runtime_context")
        self.assertNotEqual(trace["reviewer_identity_source"], "llm_generated")
        self.assertTrue(trace["reviewer_identity_not_llm_generated"])

    def test_runtime_session_context_can_supply_reviewer_identity(self):
        trace = build_review_task_trace(
            _queue_entry(),
            reviewer_identity_context={
                "reviewer_identity": "human:session_123",
                "source": "runtime_session_context",
            },
        )

        self.assertEqual(trace["reviewer_identity"], "human:session_123")
        self.assertEqual(trace["reviewer_identity_source"], "runtime_session_context")
        self.assertTrue(trace["reviewer_identity_not_llm_generated"])

    def test_reviewer_identity_context_rejects_non_runtime_sources(self):
        for source in ["llm_generated", "draft_payload", "queue_payload", "external_text", "semantic_summary"]:
            with self.subTest(source=source):
                with self.assertRaises(ValueError):
                    build_review_task_trace(
                        _queue_entry(),
                        reviewer_identity_context={
                            "reviewer_identity": "human:session_123",
                            "source": source,
                        },
                    )

    def test_allowed_reviewer_identity_context_sources_are_accepted(self):
        for source in ["runtime_session_context", "authenticated_human_session", "system_runtime_context"]:
            with self.subTest(source=source):
                trace = build_review_task_trace(
                    _queue_entry(),
                    reviewer_identity_context={
                        "reviewer_identity": "human:session_123",
                        "source": source,
                    },
                )

                self.assertEqual(trace["reviewer_identity"], "human:session_123")
                self.assertEqual(trace["reviewer_identity_source"], source)
                self.assertTrue(trace["reviewer_identity_not_llm_generated"])

    def test_semantic_key_is_secondary_optional_hint(self):
        trace = build_review_task_trace(_queue_entry())
        semantic_key_ref = trace["semantic_key_ref"]

        self.assertEqual(semantic_key_ref["value"], "object_interaction")
        self.assertEqual(semantic_key_ref["display_role"], "secondary_optional_hint")
        self.assertEqual(semantic_key_ref["authority"], "non_authoritative")
        self.assertTrue(semantic_key_ref["not_proof"])
        self.assertTrue(semantic_key_ref["not_recommendation"])
        self.assertTrue(semantic_key_ref["not_conclusion"])
        self.assertTrue(trace["semantic_key_display_level_lower_than_source_failure_norm_key"])

    def test_source_failure_norm_key_outranks_semantic_key(self):
        trace = build_review_task_trace(_queue_entry())

        self.assertEqual(trace["source_failure_norm_key_display_role"], "primary_structured_reference")
        self.assertTrue(trace["semantic_key_display_level_lower_than_source_failure_norm_key"])

    def test_injected_review_decision_fields_do_not_leak_to_output(self):
        trace = build_review_task_trace(
            _queue_entry(
                review_decision="approved",
                approved=True,
                rejected=True,
                deferred=True,
                active=True,
                selection_eligible=True,
                written_to_lesson_store=True,
                written_to_long_term_memory=True,
            )
        )

        self.assertTrue(trace["not_review_decision"])
        self.assertTrue(trace["not_approval"])
        self.assertTrue(trace["not_rejection"])
        self.assertTrue(trace["not_defer_decision"])
        self.assertTrue(trace["completion_does_not_imply_approval"])
        self.assertTrue(trace["no_draft_mutation"])
        self.assertTrue(trace["no_selection_facing_read_api"])
        self.assertTrue(trace["not_written_to_lesson_store"])
        self.assertTrue(trace["not_written_to_memory_layer"])
        self.assertNotIn("approved", trace)
        self.assertNotIn("rejected", trace)
        self.assertNotIn("deferred", trace)
        self.assertNotIn("active", trace)
        self.assertNotIn("selection_eligible", trace)

    def test_review_task_trace_exposes_no_selection_facing_read_api(self):
        trace = build_review_task_trace(
            _queue_entry(action_context={"tool": "pick_up"}, selection_context={"goal": "pick_up"})
        )

        self.assertTrue(trace["no_selection_facing_read_api"])
        for forbidden_key in ["action_context", "selection_context", "selection_api", "action_api"]:
            self.assertNotIn(forbidden_key, trace)

    def test_review_task_trace_does_not_enter_memory_contrast_set(self):
        trace = build_review_task_trace(
            _queue_entry(
                memory_contrast_set=["draft_001"],
                evaluator_expected_outcome_source="review_task_trace",
                runtime_decision_context={"goal": "pick_up"},
            )
        )

        self.assertTrue(trace["not_enter_memory_contrast_set"])
        for forbidden_key in [
            "memory_contrast_set",
            "evaluator_expected_outcome_source",
            "runtime_decision_context",
            "long_term_memory_promotion_evidence",
        ]:
            self.assertNotIn(forbidden_key, trace)

    def test_build_review_task_trace_does_not_mutate_input(self):
        entry = _queue_entry(semantic_key={"value": "object_interaction"})
        before = copy.deepcopy(entry)

        build_review_task_trace(entry)

        self.assertEqual(entry, before)


if __name__ == "__main__":
    unittest.main()
