import tempfile
import unittest
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

from ashl_core_v1.runtime.session_learning_evidence_identity import (
    build_evidence_identity_payload,
    calculate_evidence_identity_sha256,
    validate_session_learning_evidence_snapshot,
)
from ashl_core_v1.runtime.teacher_gated_session_resume_commit import build_demo_persisted_waiting_session
from ashl_core_v1.runtime.teacher_gated_session_store import TeacherGatedSessionStore


class SessionLearningEvidenceIdentityTests(unittest.TestCase):
    def _snapshot(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        payload = build_demo_persisted_waiting_session(Path(directory.name))
        store = TeacherGatedSessionStore(Path(directory.name))
        review = store.list_pending_reviews(str(payload["session_id"]))[0]
        return store.load_evidence_snapshot(review.evidence_snapshot_id)

    def test_evidence_snapshot_created_from_actual_session_records(self):
        snapshot = self._snapshot()
        validation = validate_session_learning_evidence_snapshot(snapshot)
        self.assertTrue(validation["valid"])
        self.assertEqual(snapshot.schema_version, "ashl_session_learning_evidence_snapshot_v0")
        self.assertTrue(snapshot.source_learning_evidence_packet_id)
        self.assertTrue(snapshot.source_existing_review_adapter_id)
        self.assertTrue(snapshot.source_trace_refs)
        self.assertFalse(snapshot.contains_raw_sensor_payload)
        self.assertFalse(snapshot.contains_interpreted_memory)

    def test_evidence_snapshot_is_immutable(self):
        snapshot = self._snapshot()
        with self.assertRaises(FrozenInstanceError):
            snapshot.evidence_theme = "interesting_event_marked"  # type: ignore[misc]

    def test_evidence_identity_hash_is_deterministic_and_order_independent(self):
        snapshot = self._snapshot()
        payload = build_evidence_identity_payload(snapshot)
        reordered = dict(reversed(tuple(payload.items())))
        self.assertEqual(calculate_evidence_identity_sha256(payload), calculate_evidence_identity_sha256(reordered))
        self.assertEqual(calculate_evidence_identity_sha256(payload), snapshot.evidence_identity_sha256)

    def test_evidence_hash_changes_when_semantic_content_changes(self):
        snapshot = self._snapshot()
        changed = replace(
            snapshot,
            canonical_evidence_payload={**snapshot.canonical_evidence_payload, "semantic_change": "changed"},
        )
        self.assertNotEqual(
            calculate_evidence_identity_sha256(build_evidence_identity_payload(snapshot)),
            calculate_evidence_identity_sha256(build_evidence_identity_payload(changed)),
        )


if __name__ == "__main__":
    unittest.main()

