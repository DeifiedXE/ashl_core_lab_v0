import unittest
from tempfile import TemporaryDirectory

from ashl_core_v1.runtime.local_operator_console_store import build_default_console_store
from ashl_core_v1.runtime.operator_text_timeline import (
    append_raw_output_timeline_entry,
    build_fixture_raw_output_sequence,
    submit_local_text_input,
)


class OperatorTextTimelineTests(unittest.TestCase):
    def test_user_text_remains_unprocessed_and_not_forwarded(self) -> None:
        with TemporaryDirectory() as state_dir:
            store = build_default_console_store(state_dir)

            record, entry = submit_local_text_input(store, text="test input")

            self.assertEqual(record.interpretation_status, "received_unprocessed")
            self.assertEqual(record.grounding_status, "not_grounded")
            self.assertFalse(record.forwarded_to_runtime)
            self.assertIsNone(record.forwarded_port)
            self.assertEqual(entry.entry_kind, "user_input")
            self.assertFalse(entry.qingyin_authored)
            stored = store.list_payloads("text_timeline_entries")
            self.assertEqual(stored[-1]["display_text"], "test input")

    def test_fixture_raw_output_timeline_is_not_qingyin_authored(self) -> None:
        with TemporaryDirectory() as state_dir:
            store = build_default_console_store(state_dir)
            sequence = build_fixture_raw_output_sequence(token_codes=("T03", "T11"))
            store.append_raw_output_sequence(sequence)

            entry = append_raw_output_timeline_entry(
                store,
                display_text="T03 T11",
                source_record_id=sequence.raw_output_sequence_id,
                source_actor="fixture",
                fixture_only=True,
                qingyin_authored=False,
            )

            self.assertEqual(sequence.semantic_label, None)
            self.assertTrue(sequence.fixture_only)
            self.assertFalse(sequence.qingyin_authored)
            self.assertEqual(entry.entry_kind, "qingyin_raw_output")
            self.assertEqual(entry.semantic_status, "ungrounded")
            self.assertFalse(entry.qingyin_authored)


if __name__ == "__main__":
    unittest.main()
