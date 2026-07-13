import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.runtime.teacher_gated_session_resume_commit import (
    FULL_COMMIT_APPROVAL_SCOPE,
    TeacherGatedSessionResumeCommitRuntime,
    build_demo_persisted_waiting_session,
)
from ashl_core_v1.runtime.teacher_gated_session_store import (
    STORE_FILENAME,
    STORE_SCHEMA_NAME,
    STORE_SCHEMA_VERSION,
    TeacherGatedSessionStore,
    payload_sha256,
)
from ashl_core_v1.runtime.trace_envelope import build_trace_envelope


class TeacherGatedSessionStoreTests(unittest.TestCase):
    def test_store_requires_explicit_state_dir_and_creates_schema(self):
        with self.assertRaises(ValueError):
            TeacherGatedSessionStore(None)  # type: ignore[arg-type]
        with tempfile.TemporaryDirectory() as directory:
            store = TeacherGatedSessionStore(Path(directory))
            validation = store.validate_schema()
            self.assertTrue(validation["valid"])
            self.assertEqual(validation["schema_name"], STORE_SCHEMA_NAME)
            self.assertEqual(validation["schema_version"], STORE_SCHEMA_VERSION)
            self.assertTrue((Path(directory) / STORE_FILENAME).exists())
            self.assertFalse(Path("ashl_core_v1/data").exists())

    def test_payload_hash_is_canonical_and_stable(self):
        self.assertEqual(
            payload_sha256({"b": 2, "a": [1, 2]}),
            payload_sha256({"a": [1, 2], "b": 2}),
        )

    def test_persist_waiting_session_survives_new_store_instance(self):
        with tempfile.TemporaryDirectory() as directory:
            payload = build_demo_persisted_waiting_session(Path(directory))
            session_id = str(payload["session_id"])
            first = TeacherGatedSessionStore(Path(directory))
            second = TeacherGatedSessionStore(Path(directory))

            state = second.load_session_state(session_id)
            checkpoint = second.load_latest_checkpoint(session_id)
            pending = second.list_pending_reviews(session_id)
            traces = second.list_trace_envelopes(session_id)

            self.assertEqual(state.status.value, "waiting_teacher_review")
            self.assertEqual(checkpoint.session_id, session_id)
            self.assertEqual(checkpoint.trace_cursor, state.raw_trace_cursor)
            self.assertEqual(checkpoint.event_stack, state.event_stack_frame_ids)
            self.assertEqual(len(pending), 1)
            self.assertGreater(len(traces), 0)
            self.assertTrue(first.validate_trace_table(session_id)["valid"])
            self.assertFalse(hasattr(first, "update_trace_envelope"))
            self.assertFalse(hasattr(first, "delete_trace_envelope"))

    def test_store_rejects_missing_and_cross_session_trace_refs(self):
        with tempfile.TemporaryDirectory() as directory:
            first_payload = build_demo_persisted_waiting_session(Path(directory))
            second_payload = build_demo_persisted_waiting_session(Path(directory))
            first_session = str(first_payload["session_id"])
            second_session = str(second_payload["session_id"])
            store = TeacherGatedSessionStore(Path(directory))
            first_trace_id = store.list_trace_envelopes(first_session)[0].trace_id
            second_state = store.load_session_state(second_session)

            with self.assertRaises(ValueError):
                store.append_trace_envelope(
                    build_trace_envelope(
                        trace_id="trace:missing-ref",
                        session_id=second_session,
                        event_id=str(second_state.current_event_id),
                        root_event_id=str(second_state.root_event_id),
                        source_line="runtime",
                        source_module="test",
                        record_kind="MissingRef",
                        record_id="missing-ref",
                        trace_layer="runtime_control",
                        payload_schema="test",
                        payload_snapshot={"kind": "missing_ref"},
                        source_trace_refs=("trace:not-present",),
                    )
                )

            with self.assertRaises(ValueError):
                store.append_trace_envelope(
                    build_trace_envelope(
                        trace_id="trace:cross-session-ref",
                        session_id=second_session,
                        event_id=str(second_state.current_event_id),
                        root_event_id=str(second_state.root_event_id),
                        source_line="runtime",
                        source_module="test",
                        record_kind="CrossSessionRef",
                        record_id="cross-session-ref",
                        trace_layer="runtime_control",
                        payload_schema="test",
                        payload_snapshot={"kind": "cross_session_ref"},
                        source_trace_refs=(first_trace_id,),
                    )
                )

    def test_teacher_decision_validation_and_duplicate_final_decision(self):
        with tempfile.TemporaryDirectory() as directory:
            payload = build_demo_persisted_waiting_session(Path(directory))
            session_id = str(payload["session_id"])
            pending_review = payload["pending_teacher_reviews"][0]
            review_id = str(pending_review["pending_teacher_review_id"])
            runtime = TeacherGatedSessionResumeCommitRuntime()
            first = runtime.apply_teacher_decision(
                session_id,
                review_id,
                "approved",
                ("teacher_verified",),
                "Explicit approval.",
                Path(directory),
                approval_scope=FULL_COMMIT_APPROVAL_SCOPE,
                expected_evidence_hash=str(pending_review["evidence_identity_sha256"]),
            )
            self.assertEqual(first.decision, "approved")
            with self.assertRaises(ValueError):
                runtime.apply_teacher_decision(
                    session_id,
                    review_id,
                    "approved",
                    ("duplicate",),
                    "Duplicate approval.",
                    Path(directory),
                    approval_scope=FULL_COMMIT_APPROVAL_SCOPE,
                    expected_evidence_hash=str(pending_review["evidence_identity_sha256"]),
                )
            with self.assertRaises(ValueError):
                runtime.apply_teacher_decision(
                    session_id,
                    review_id,
                    "unknown",
                    (),
                    "Invalid decision.",
                    Path(directory),
                )

    def test_teacher_decision_rejects_review_from_another_session(self):
        with tempfile.TemporaryDirectory() as directory:
            first_payload = build_demo_persisted_waiting_session(Path(directory))
            second_payload = build_demo_persisted_waiting_session(Path(directory))
            first_session = str(first_payload["session_id"])
            second_review = str(second_payload["pending_teacher_reviews"][0]["pending_teacher_review_id"])
            runtime = TeacherGatedSessionResumeCommitRuntime()
            with self.assertRaises(ValueError):
                runtime.apply_teacher_decision(
                    first_session,
                    second_review,
                    "deferred",
                    ("wrong_session",),
                    "Wrong session.",
                    Path(directory),
                )


if __name__ == "__main__":
    unittest.main()
