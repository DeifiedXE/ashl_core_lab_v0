import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.runtime.session_persistence import (
    LAST_TRACE_SUMMARY_FILE,
    SESSION_SUMMARY_FILE,
    STATE_SNAPSHOT_FILE,
    build_last_trace_summary,
    build_session_summary,
    build_state_snapshot,
    load_last_trace_summary,
    load_session_summary,
    load_state_snapshot,
    save_last_trace_summary,
    save_session_summary,
    save_state_snapshot,
)


ROOT = Path(__file__).resolve().parents[2]


class SessionPersistenceTests(unittest.TestCase):
    def test_build_state_snapshot_returns_required_fields(self):
        snapshot = build_state_snapshot(
            session_id="session_001",
            turn=2,
            state_values={"status": "active"},
        )

        self.assertEqual("session_001", snapshot["session_id"])
        self.assertEqual(2, snapshot["turn"])
        self.assertEqual({"status": "active"}, snapshot["state_values"])
        self.assertTrue(snapshot["updated_at"])

    def test_build_session_summary_returns_required_fields(self):
        summary = build_session_summary(
            session_id="session_001",
            turn_count=3,
            last_case_id="blocked_front_obstacle",
            last_summary="blocked learning summary",
        )

        self.assertEqual("session_001", summary["session_id"])
        self.assertEqual(3, summary["turn_count"])
        self.assertEqual("blocked_front_obstacle", summary["last_case_id"])
        self.assertEqual("blocked learning summary", summary["last_summary"])
        self.assertTrue(summary["updated_at"])

    def test_build_last_trace_summary_returns_required_fields(self):
        summary = build_last_trace_summary(
            trace_id="trace_001",
            case_id="blocked_front_obstacle",
            summary="trace summary",
            source_refs=("perception_001", "memory_001"),
        )

        self.assertEqual("trace_001", summary["trace_id"])
        self.assertEqual("blocked_front_obstacle", summary["case_id"])
        self.assertEqual("trace summary", summary["summary"])
        self.assertEqual(["perception_001", "memory_001"], summary["source_refs"])
        self.assertTrue(summary["updated_at"])

    def test_save_load_state_snapshot_round_trip(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            snapshot = build_state_snapshot("session_001", 1, {"case": "blocked"})

            save_state_snapshot(snapshot, data_dir)

            self.assertEqual(snapshot, load_state_snapshot(data_dir))
            self.assertTrue((data_dir / STATE_SNAPSHOT_FILE).is_file())

    def test_save_load_session_summary_round_trip(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            summary = build_session_summary(
                "session_001",
                1,
                "blocked_front_obstacle",
                "summary",
            )

            save_session_summary(summary, data_dir)

            self.assertEqual(summary, load_session_summary(data_dir))
            self.assertTrue((data_dir / SESSION_SUMMARY_FILE).is_file())

    def test_save_load_last_trace_summary_round_trip(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            summary = build_last_trace_summary(
                "memory_learning_front_obstacle_001",
                "blocked_front_obstacle",
                "trace summary",
            )

            save_last_trace_summary(summary, data_dir)

            self.assertEqual(summary, load_last_trace_summary(data_dir))
            self.assertTrue((data_dir / LAST_TRACE_SUMMARY_FILE).is_file())

    def test_missing_files_return_none(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)

            self.assertIsNone(load_state_snapshot(data_dir))
            self.assertIsNone(load_session_summary(data_dir))
            self.assertIsNone(load_last_trace_summary(data_dir))

    def test_repo_data_directory_is_not_polluted_during_tests(self):
        self.assertFalse((ROOT / "ashl_core_v1" / "data").exists())


if __name__ == "__main__":
    unittest.main()
