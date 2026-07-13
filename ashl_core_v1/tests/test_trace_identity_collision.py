import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.runtime.teacher_gated_session_resume_commit import build_demo_persisted_waiting_session
from ashl_core_v1.runtime.teacher_gated_session_store import TeacherGatedSessionStore
from ashl_core_v1.runtime.trace_envelope import (
    TraceEnvelopeStore,
    TraceIdentityCollisionError,
    build_trace_envelope,
)


class TraceIdentityCollisionTests(unittest.TestCase):
    def test_same_trace_id_same_canonical_identity_is_idempotent(self):
        store = TraceEnvelopeStore()
        envelope = build_trace_envelope(
            trace_id="trace:test:collision",
            session_id="session:test",
            event_id="event:test",
            root_event_id="event:test",
            source_line="runtime",
            source_module="test",
            record_kind="TraceCollisionTest",
            record_id="record:test",
            trace_layer="runtime_control",
            payload_schema="test_v0",
            payload_snapshot={"value": 1},
        )
        first = store.append(envelope)
        second = store.append(first)
        self.assertEqual(first.trace_id, second.trace_id)
        self.assertEqual(store.latest_sequence(), 0)

    def test_same_trace_id_changed_payload_or_refs_is_blocked(self):
        store = TraceEnvelopeStore()
        first = store.append(
            build_trace_envelope(
                trace_id="trace:test:collision",
                session_id="session:test",
                event_id="event:test",
                root_event_id="event:test",
                source_line="runtime",
                source_module="test",
                record_kind="TraceCollisionTest",
                record_id="record:test",
                trace_layer="runtime_control",
                payload_schema="test_v0",
                payload_snapshot={"value": 1},
            )
        )
        with self.assertRaises(TraceIdentityCollisionError):
            store.append(
                build_trace_envelope(
                    trace_id=first.trace_id,
                    session_id=first.session_id,
                    event_id=first.event_id,
                    root_event_id=first.root_event_id,
                    source_line=first.source_line,
                    source_module=first.source_module,
                    record_kind=first.record_kind,
                    record_id=first.record_id,
                    trace_layer=first.trace_layer,
                    payload_schema=first.payload_schema,
                    payload_snapshot={"value": 2},
                )
            )

    def test_persistent_store_trace_collision_creates_failure_journal(self):
        with tempfile.TemporaryDirectory() as directory:
            payload = build_demo_persisted_waiting_session(Path(directory))
            session_id = str(payload["session_id"])
            store = TeacherGatedSessionStore(Path(directory))
            first = store.list_trace_envelopes(session_id)[0]
            with self.assertRaises(TraceIdentityCollisionError):
                store.append_trace_envelope(
                    build_trace_envelope(
                        trace_id=first.trace_id,
                        session_id=first.session_id,
                        event_id=first.event_id,
                        root_event_id=first.root_event_id,
                        source_line=first.source_line,
                        source_module=first.source_module,
                        record_kind=first.record_kind,
                        record_id=first.record_id,
                        trace_layer=first.trace_layer,
                        payload_schema=first.payload_schema,
                        payload_snapshot={**first.payload_snapshot, "changed": True},
                    )
                )


if __name__ == "__main__":
    unittest.main()

