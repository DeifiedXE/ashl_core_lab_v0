import unittest

from ashl_core_v1.runtime.operator_console_types import (
    STATUS_LOG_SCHEMA_VERSION,
    OperatorStatusLogEntry,
)
from ashl_core_v1.runtime.operator_status_log import build_operator_status_log_entry
from ashl_core_v1.runtime.host_sensor_types import utc_now


class OperatorStatusLogTests(unittest.TestCase):
    def test_operator_status_log_is_not_qingyin_output(self) -> None:
        entry = build_operator_status_log_entry(
            level="notice",
            event_kind="teacher_gate_changed",
            operator_message="Teacher review is pending.",
            source_module="test",
            source_record_refs=("pending_review:test",),
        )

        self.assertFalse(entry.qingyin_output)
        self.assertEqual(entry.operator_message, "Teacher review is pending.")

    def test_status_log_rejects_qingyin_output_misclassification(self) -> None:
        with self.assertRaises(ValueError):
            OperatorStatusLogEntry(
                status_log_id="status_log:test",
                schema_version=STATUS_LOG_SCHEMA_VERSION,
                created_at=utc_now(),
                level="info",
                event_kind="runtime_status",
                operator_message="Runtime entered RUNNING state.",
                source_module="test",
                source_record_refs=tuple(),
                source_trace_refs=tuple(),
                qingyin_output=True,
            )


if __name__ == "__main__":
    unittest.main()
