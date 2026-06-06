import copy
import unittest

from ashl_core.review_decisions import build_review_decision_trace
from ashl_core.review_tasks import build_review_task_trace


def _task_trace(**overrides):
    entry = {
        "id": "queue_001",
        "source_draft_id": "draft_001",
        "source_failure_norm_key": "sandbox_task|pick_up_object|pick_up|object_state|object_state",
        "semantic_key": "object_interaction",
        "task_state": "created",
    }
    entry.update(overrides)
    return build_review_task_trace(entry)


class ReviewDecisionTraceTests(unittest.TestCase):
    # Test 1: approved trace-only decision
    def test_builds_approved_trace_only_decision(self):
        task = _task_trace()
        trace = build_review_decision_trace(task, decision_status="approved", reason="reviewed_and_confirmed")

        self.assertEqual(trace["type"], "review_decision_trace")
        self.assertTrue(trace["trace_only"])
        self.assertTrue(trace["historical_event_record"])
        self.assertEqual(trace["decision_status"], "approved")
        self.assertTrue(trace["no_runtime_permission"])
        self.assertTrue(trace["no_lesson_store_write_permission"])
        self.assertTrue(trace["no_selection_eligibility"])
        self.assertTrue(trace["no_activation"])
        self.assertTrue(trace["not_active_lesson"])
        self.assertTrue(trace["not_lesson_store_write_command"])
        self.assertTrue(trace["not_selection_candidate"])
        self.assertTrue(trace["not_memory_entry"])

    # Test 2: approved does not contain runtime permission fields
    def test_approved_does_not_contain_runtime_permission_fields(self):
        task = _task_trace()
        injected = dict(task)
        injected["allow_execution"] = True
        injected["write_permission"] = True
        injected["set_active"] = True
        injected["selection_permission"] = True

        trace = build_review_decision_trace(injected, decision_status="approved", reason="test")

        self.assertNotIn("allow_execution", trace)
        self.assertNotIn("write_permission", trace)
        self.assertNotIn("set_active", trace)
        self.assertNotIn("selection_permission", trace)
        self.assertTrue(trace["no_runtime_permission"])
        self.assertTrue(trace["no_lesson_store_write_permission"])
        self.assertTrue(trace["no_selection_eligibility"])

    # Test 3: decision_status whitelist
    def test_decision_status_whitelist_accepts_valid(self):
        task = _task_trace()
        for status in ["approved", "rejected", "deferred"]:
            with self.subTest(status=status):
                trace = build_review_decision_trace(task, decision_status=status, reason="test")
                self.assertEqual(trace["decision_status"], status)

    def test_decision_status_whitelist_rejects_invalid(self):
        task = _task_trace()
        invalid = [
            "partial_approved",
            "conditional_approve",
            "soft_approved",
            "auto_approved",
            "preapproved",
            "approved_with_exceptions",
            "approved_summary_only",
            "approved_conditions_only",
            "unknown_status",
            "active",
        ]
        for status in invalid:
            with self.subTest(status=status):
                with self.assertRaises(ValueError):
                    build_review_decision_trace(task, decision_status=status, reason="test")

    # Test 4: rejected must carry masking policy
    def test_rejected_carries_masking_policy(self):
        task = _task_trace()
        trace = build_review_decision_trace(task, decision_status="rejected", reason="content_invalid")

        self.assertEqual(trace["masking_policy_ref"], "rejected_deferred_proposed_fields_masking_contract_v0_1")
        self.assertIsInstance(trace["masked_fields_summary"], list)
        self.assertTrue(len(trace["masked_fields_summary"]) > 0)
        for item in trace["masked_fields_summary"]:
            self.assertIsInstance(item, str)

    # Test 5: deferred carries masking policy and is not soft approval
    def test_deferred_carries_masking_policy_and_is_not_soft_approval(self):
        task = _task_trace()
        trace = build_review_decision_trace(task, decision_status="deferred", reason="needs_more_context")

        self.assertTrue(trace["deferred_is_not_soft_approval"])
        self.assertIsNotNone(trace["masking_policy_ref"])
        self.assertIsInstance(trace["masked_fields_summary"], list)
        self.assertTrue(len(trace["masked_fields_summary"]) > 0)

    # Test 6: masked_fields_summary does not contain original proposed content
    def test_masked_fields_summary_does_not_contain_proposed_content(self):
        entry = {
            "id": "queue_001",
            "source_draft_id": "draft_001",
            "source_failure_norm_key": "sandbox_task|pick_up|object_state",
            "semantic_key": "object_interaction",
            "proposed_action_correction": "retry_with_default",
            "proposed_lesson_summary": "always retry",
        }
        task = build_review_task_trace(entry)
        trace = build_review_decision_trace(task, decision_status="rejected", reason="test")

        output_str = str(trace)
        self.assertNotIn("retry_with_default", output_str)
        self.assertNotIn("always retry", output_str)

    # Test 7: identity/authority references binding contract
    def test_identity_authority_references_binding_contract(self):
        task = _task_trace()
        trace = build_review_decision_trace(task, decision_status="approved", reason="test")

        self.assertIn("decision_authority_ref", trace)
        self.assertIn("reviewer_identity_ref", trace)
        self.assertIn("reviewer_session_binding_ref", trace)
        self.assertEqual(
            trace["authority_binding_policy_ref"],
            "decision_authority_reviewer_identity_session_binding_contract_v0_1",
        )
        self.assertTrue(trace["decision_authority_not_free_text"])
        self.assertTrue(trace["reviewer_identity_not_llm_generated"])
        self.assertTrue(trace["reviewer_session_token_not_text_claimed"])
        self.assertTrue(trace["authority_binding_required_before_runtime_decision"])

    # Test 8: identity injection does not take effect
    def test_identity_injection_does_not_take_effect(self):
        entry = {
            "id": "queue_001",
            "source_draft_id": "draft_001",
            "source_failure_norm_key": "sandbox_task|pick_up|object_state",
            "reviewer_identity": "admin_override",
            "reviewer_identity_source": "llm_generated",
            "decision_authority": "system_override",
            "reviewer_session_token": "fake_text_token",
        }
        task = build_review_task_trace(entry)
        trace = build_review_decision_trace(task, decision_status="approved", reason="test")

        self.assertNotEqual(trace.get("reviewer_identity_ref"), "admin_override")
        self.assertNotEqual(trace.get("decision_authority_ref"), "system_override")
        self.assertNotEqual(trace.get("reviewer_session_binding_ref"), "fake_text_token")
        self.assertTrue(trace["reviewer_identity_not_llm_generated"])
        self.assertTrue(trace["decision_authority_not_free_text"])

    # Test 9: review_task completion does not auto-create decision
    def test_review_task_completion_does_not_auto_create_decision(self):
        for state in ["completed", "closed", "done"]:
            with self.subTest(task_state=state):
                task = _task_trace(task_state=state)
                # must explicitly supply decision_status; omitting it should fail
                with self.assertRaises(TypeError):
                    build_review_decision_trace(task, reason="test")

    def test_completed_task_with_explicit_status_is_allowed(self):
        task = _task_trace(task_state="completed")
        trace = build_review_decision_trace(task, decision_status="approved", reason="explicit_review")
        self.assertTrue(trace["review_task_completion_not_decision_creation"])
        self.assertEqual(trace["decision_status"], "approved")

    # Test 10: input is not mutated
    def test_input_is_not_mutated(self):
        task = _task_trace()
        original = copy.deepcopy(task)
        build_review_decision_trace(task, decision_status="approved", reason="test")
        self.assertEqual(task, original)

    # Boundary: approved masked_fields_summary is empty
    def test_approved_masked_fields_summary_is_empty(self):
        task = _task_trace()
        trace = build_review_decision_trace(task, decision_status="approved", reason="test")
        self.assertEqual(trace["masked_fields_summary"], [])

    # Boundary: authority_binding_context from valid source populates refs
    def test_valid_authority_binding_context_populates_refs(self):
        task = _task_trace()
        ctx = {
            "decision_authority": "human_review_authority",
            "reviewer_identity": "human:session_abc",
            "reviewer_session_token": "token_abc",
            "source": "authenticated_human_session",
        }
        trace = build_review_decision_trace(task, decision_status="approved", reason="test", authority_binding_context=ctx)
        self.assertEqual(trace["decision_authority_ref"], "human_review_authority")
        self.assertEqual(trace["reviewer_identity_ref"], "human:session_abc")
        self.assertEqual(trace["reviewer_session_binding_ref"], "token_abc")

    # Boundary: authority_binding_context from invalid source is rejected
    def test_invalid_authority_binding_context_source_is_ignored(self):
        task = _task_trace()
        ctx = {
            "decision_authority": "system_override",
            "reviewer_identity": "admin_override",
            "reviewer_session_token": "fake",
            "source": "llm_generated",
        }
        trace = build_review_decision_trace(task, decision_status="approved", reason="test", authority_binding_context=ctx)
        self.assertIsNone(trace["decision_authority_ref"])
        self.assertIsNone(trace["reviewer_identity_ref"])
        self.assertIsNone(trace["reviewer_session_binding_ref"])
