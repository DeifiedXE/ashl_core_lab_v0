import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from ashl_core_v1.runtime.session_learning_evidence_adapter import (
    adapt_session_evidence_to_learning_feedback_candidate,
)
from ashl_core_v1.runtime.session_learning_evidence_identity import FULL_COMMIT_APPROVAL_SCOPE
from ashl_core_v1.runtime.teacher_gated_session_resume_commit import build_demo_persisted_waiting_session
from ashl_core_v1.runtime.teacher_gated_session_store import TeacherGatedSessionStore


class SessionLearningEvidenceAdapterTests(unittest.TestCase):
    def _snapshot_and_decision(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        payload = build_demo_persisted_waiting_session(Path(directory.name))
        store = TeacherGatedSessionStore(Path(directory.name))
        review = store.list_pending_reviews(str(payload["session_id"]))[0]
        snapshot = store.load_evidence_snapshot(review.evidence_snapshot_id)
        decision = {
            "teacher_decision_id": "teacher_decision:test",
            "decision": "approved",
            "approval_scope": FULL_COMMIT_APPROVAL_SCOPE,
            "target_evidence_identity_sha256": snapshot.evidence_identity_sha256,
        }
        return snapshot, decision

    def test_canonical_adapter_maps_supported_evidence_without_uncertainty_fallback(self):
        snapshot, decision = self._snapshot_and_decision()
        expected = {
            "uncertainty_detected": "host_body_uncertainty_feedback_candidate",
            "interesting_event_marked": "host_body_interesting_event_feedback_candidate",
            "teacher_review_requested": "host_body_teacher_review_feedback_candidate",
            "runtime_bridge_deferred": "host_body_runtime_bridge_feedback_candidate",
            "observe_again_requested": "host_body_observation_feedback_candidate",
            "event_processing_paused": "host_body_pause_feedback_candidate",
            "home_status_updated": "host_body_status_feedback_candidate",
            "unknown_event_seen": "host_body_unknown_event_feedback_candidate",
        }
        for theme, host_body_kind in expected.items():
            with self.subTest(theme=theme):
                themed_snapshot = replace(snapshot, evidence_theme=theme, evidence_summary=f"summary for {theme}")
                candidate = adapt_session_evidence_to_learning_feedback_candidate(themed_snapshot, decision)
                self.assertIn(f"evidence_theme:{theme}", candidate.candidate_evidence_labels)
                self.assertIn(f"host_body_candidate_kind:{host_body_kind}", candidate.candidate_evidence_labels)
                self.assertEqual(candidate.source_trace_refs, snapshot.source_trace_refs)
                if theme == "runtime_bridge_deferred":
                    self.assertNotIn("host_body_uncertainty_feedback_candidate", candidate.candidate_evidence_labels)

    def test_adapter_rejects_unsupported_evidence_and_insufficient_scope(self):
        snapshot, decision = self._snapshot_and_decision()
        with self.assertRaises(ValueError):
            adapt_session_evidence_to_learning_feedback_candidate(replace(snapshot, evidence_theme="unsupported"), decision)
        with self.assertRaises(ValueError):
            adapt_session_evidence_to_learning_feedback_candidate(
                snapshot,
                {**decision, "approval_scope": "feedback_candidate_only"},
            )
        with self.assertRaises(ValueError):
            adapt_session_evidence_to_learning_feedback_candidate(
                snapshot,
                {**decision, "target_evidence_identity_sha256": "wrong"},
            )


if __name__ == "__main__":
    unittest.main()

