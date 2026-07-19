import unittest
from tempfile import TemporaryDirectory

from ashl_core_v1.runtime.local_operator_console_store import build_default_console_store
from ashl_core_v1.runtime.local_operator_event_stream import LocalOperatorEventStream
from ashl_core_v1.runtime.operator_console_types import JSON_EVENT_SCHEMA_VERSION, LocalOperatorJsonEvent
from ashl_core_v1.runtime.host_sensor_types import utc_now


class LocalOperatorEventStreamTests(unittest.TestCase):
    def test_json_event_stream_is_ordered_and_model_free(self) -> None:
        with TemporaryDirectory() as state_dir:
            stream = LocalOperatorEventStream(build_default_console_store(state_dir))

            first = stream.append_event(event_kind="total_state_changed", source_record_refs=("state:1",))
            second = stream.append_event(event_kind="status_log_appended", source_record_refs=("log:1",))
            events = stream.list_events()

            self.assertEqual([item["event_id"] for item in events], [first.event_id, second.event_id])
            self.assertEqual([item["sequence_index"] for item in events], [0, 1])
            self.assertFalse(any(item["llm_used"] for item in events))
            self.assertFalse(any(item["codex_used"] for item in events))
            self.assertNotIn("raw_pcm", str(events).lower())
            self.assertNotIn("base64", str(events).lower())

    def test_json_event_rejects_llm_or_codex_use(self) -> None:
        with self.assertRaises(ValueError):
            LocalOperatorJsonEvent(
                event_id="operator_json_event:test",
                schema_version=JSON_EVENT_SCHEMA_VERSION,
                sequence_index=0,
                created_at=utc_now(),
                event_kind="status_log_appended",
                source_record_refs=tuple(),
                source_trace_refs=tuple(),
                llm_used=True,
                codex_used=False,
            )


if __name__ == "__main__":
    unittest.main()
