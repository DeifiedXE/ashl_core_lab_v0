import unittest

from ashl_core_v1.runtime.trace_envelope import (
    TraceEnvelopeStore,
    build_trace_envelope,
    validate_trace_envelope,
    validate_trace_envelope_store,
)


class TraceEnvelopeTests(unittest.TestCase):
    def _raw(self, trace_id="trace:demo:0000", session_id="session:demo"):
        return build_trace_envelope(
            trace_id=trace_id,
            session_id=session_id,
            event_id="event:demo",
            root_event_id="event:demo",
            source_line="host_body",
            source_module="host_body_sensor_events",
            record_kind="HostBodyEventRecord",
            record_id="host_body_event:demo",
            trace_layer="raw",
            payload_schema="qingyin_host_body_event_v0",
            payload_snapshot={"event_type": "camera_unknown_low_level_event"},
        )

    def test_trace_envelope_validates_canonical_schema(self):
        envelope = self._raw()
        validation = validate_trace_envelope(envelope)
        self.assertTrue(validation["valid"])
        self.assertEqual(envelope.trace_schema_version, "ashl_trace_envelope_v1")
        self.assertEqual(envelope.source_line, "host_body")
        self.assertEqual(envelope.trace_layer, "raw")

    def test_trace_envelope_requires_session_and_event_ids(self):
        with self.assertRaises(ValueError):
            build_trace_envelope(
                trace_id="trace:bad",
                session_id="",
                event_id="event:demo",
                root_event_id="event:demo",
                source_line="host_body",
                source_module="host_body_sensor_events",
                record_kind="HostBodyEventRecord",
                record_id="host_body_event:demo",
                trace_layer="raw",
                payload_schema="schema",
                payload_snapshot={},
            )
        with self.assertRaises(ValueError):
            build_trace_envelope(
                trace_id="trace:bad",
                session_id="session:demo",
                event_id="",
                root_event_id="event:demo",
                source_line="host_body",
                source_module="host_body_sensor_events",
                record_kind="HostBodyEventRecord",
                record_id="host_body_event:demo",
                trace_layer="raw",
                payload_schema="schema",
                payload_snapshot={},
            )

    def test_trace_envelope_enforces_allowed_source_line_and_layer(self):
        with self.assertRaises(ValueError):
            build_trace_envelope(
                trace_id="trace:bad",
                session_id="session:demo",
                event_id="event:demo",
                root_event_id="event:demo",
                source_line="not_a_line",
                source_module="x",
                record_kind="x",
                record_id="x",
                trace_layer="raw",
                payload_schema="schema",
                payload_snapshot={},
            )
        with self.assertRaises(ValueError):
            build_trace_envelope(
                trace_id="trace:bad",
                session_id="session:demo",
                event_id="event:demo",
                root_event_id="event:demo",
                source_line="host_body",
                source_module="x",
                record_kind="x",
                record_id="x",
                trace_layer="not_a_layer",
                payload_schema="schema",
                payload_snapshot={},
            )

    def test_raw_trace_rejects_interpreted_identifiers(self):
        for key in ("concept_id", "reviewed_concept_id", "memory_learning_trace_id", "interpretation_summary"):
            with self.subTest(key=key):
                with self.assertRaises(ValueError):
                    build_trace_envelope(
                        trace_id=f"trace:bad:{key}",
                        session_id="session:demo",
                        event_id="event:demo",
                        root_event_id="event:demo",
                        source_line="host_body",
                        source_module="host_body_sensor_events",
                        record_kind="HostBodyEventRecord",
                        record_id="host_body_event:demo",
                        trace_layer="raw",
                        payload_schema="schema",
                        payload_snapshot={key: "forbidden"},
                    )

    def test_interpreted_trace_requires_source_refs(self):
        with self.assertRaises(ValueError):
            build_trace_envelope(
                trace_id="trace:derived",
                session_id="session:demo",
                event_id="event:demo",
                root_event_id="event:demo",
                source_line="learning",
                source_module="demo",
                record_kind="DerivedEvidence",
                record_id="derived:demo",
                trace_layer="derived_evidence",
                payload_schema="schema",
                payload_snapshot={"summary": "not raw"},
            )

    def test_payload_is_snapshot_safe(self):
        payload = {"event": {"kind": "camera_unknown_low_level_event"}}
        envelope = build_trace_envelope(
            trace_id="trace:snapshot",
            session_id="session:demo",
            event_id="event:demo",
            root_event_id="event:demo",
            source_line="host_body",
            source_module="demo",
            record_kind="HostBodyEventRecord",
            record_id="host_body_event:demo",
            trace_layer="raw",
            payload_schema="schema",
            payload_snapshot=payload,
        )
        payload["event"]["kind"] = "mutated"
        self.assertEqual(envelope.payload_snapshot["event"]["kind"], "camera_unknown_low_level_event")

    def test_trace_envelope_store_append_only_and_monotonic(self):
        store = TraceEnvelopeStore()
        first = store.append(self._raw())
        second = store.append(
            build_trace_envelope(
                trace_id="trace:demo:0001",
                session_id=first.session_id,
                event_id=first.event_id,
                root_event_id=first.root_event_id,
                source_line="runtime",
                source_module="demo",
                record_kind="RuntimeControl",
                record_id="runtime:demo",
                trace_layer="runtime_control",
                payload_schema="schema",
                payload_snapshot={"ok": True},
                source_trace_refs=(first.trace_id,),
            )
        )
        self.assertEqual(first.sequence_index, 0)
        self.assertEqual(second.sequence_index, 1)
        self.assertTrue(store.validate_monotonic_order())
        self.assertTrue(store.validate_source_refs())
        self.assertTrue(validate_trace_envelope_store(store)["valid"])
        with self.assertRaises(TypeError):
            store.update(first.trace_id, first)
        with self.assertRaises(TypeError):
            store.delete(first.trace_id)

    def test_trace_envelope_store_rejects_bad_refs(self):
        store = TraceEnvelopeStore()
        first = store.append(self._raw())
        with self.assertRaises(ValueError):
            store.append(self._raw(trace_id=first.trace_id))
        with self.assertRaises(ValueError):
            store.append(
                build_trace_envelope(
                    trace_id="trace:missing-ref",
                    session_id=first.session_id,
                    event_id=first.event_id,
                    root_event_id=first.root_event_id,
                    source_line="runtime",
                    source_module="demo",
                    record_kind="RuntimeControl",
                    record_id="runtime:demo",
                    trace_layer="runtime_control",
                    payload_schema="schema",
                    payload_snapshot={},
                    source_trace_refs=("trace:future",),
                )
            )
        with self.assertRaises(ValueError):
            store.append(
                build_trace_envelope(
                    trace_id="trace:cross-session",
                    session_id="session:other",
                    event_id="event:other",
                    root_event_id="event:other",
                    source_line="runtime",
                    source_module="demo",
                    record_kind="RuntimeControl",
                    record_id="runtime:demo",
                    trace_layer="runtime_control",
                    payload_schema="schema",
                    payload_snapshot={},
                    source_trace_refs=(first.trace_id,),
                )
            )


if __name__ == "__main__":
    unittest.main()

