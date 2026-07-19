import json
import sqlite3
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from ashl_core_v1.runtime.operator_console_state_reader import (
    audit_non_llm_local_output_surface,
    build_total_state_snapshot,
    build_upper_console_view_model,
)
from ashl_core_v1.runtime.teacher_gated_session_store import STORE_FILENAME


def _write_session_head(state_dir: str, session_id: str, status: str) -> None:
    db_path = Path(state_dir) / STORE_FILENAME
    connection = sqlite3.connect(str(db_path))
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS session_heads (
                session_id TEXT PRIMARY KEY,
                current_status TEXT NOT NULL,
                current_checkpoint_id TEXT,
                version INTEGER NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            INSERT OR REPLACE INTO session_heads
                (session_id, current_status, current_checkpoint_id, version, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (session_id, status, None, 1, "2026-07-19T00:00:00+00:00"),
        )
        connection.commit()
    finally:
        connection.close()


def _write_pending_review(state_dir: str, review_id: str) -> None:
    db_path = Path(state_dir) / STORE_FILENAME
    connection = sqlite3.connect(str(db_path))
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS pending_teacher_reviews (
                pending_teacher_review_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                payload_json TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            INSERT INTO pending_teacher_reviews
                (pending_teacher_review_id, created_at, payload_json)
            VALUES (?, ?, ?)
            """,
            (
                review_id,
                "2026-07-19T00:00:01+00:00",
                json.dumps({"pending_teacher_review_id": review_id, "review_status": "pending", "resolved": False}),
            ),
        )
        connection.commit()
    finally:
        connection.close()


class OperatorConsoleStateReaderTests(unittest.TestCase):
    def test_total_state_stopped_sleeping_and_running_are_derived(self) -> None:
        with TemporaryDirectory() as state_dir:
            stopped = build_total_state_snapshot(state_dir=state_dir, runtime_process_available=False)
            sleeping = build_total_state_snapshot(state_dir=state_dir, runtime_process_available=True)
            _write_session_head(state_dir, "runtime_session:active", "running")
            running = build_total_state_snapshot(state_dir=state_dir, runtime_process_available=False)

            self.assertEqual(stopped.total_state, "stopped")
            self.assertEqual(stopped.state_reason_codes, ("no_active_qingyin_runtime_session",))
            self.assertEqual(sleeping.total_state, "sleeping")
            self.assertEqual(sleeping.state_reason_codes, ("runtime_process_available_no_active_work",))
            self.assertEqual(running.total_state, "running")
            self.assertEqual(running.active_runtime_session_id, "runtime_session:active")

    def test_teacher_gate_status_is_read_from_existing_records(self) -> None:
        with TemporaryDirectory() as state_dir:
            _write_session_head(state_dir, "runtime_session:teacher_gate", "waiting_teacher_review")
            _write_pending_review(state_dir, "pending_teacher_review:test")

            snapshot = build_total_state_snapshot(state_dir=state_dir)

            self.assertTrue(snapshot.teacher_gate_active)
            self.assertEqual(snapshot.pending_teacher_review_count, 1)

    def test_view_model_and_audit_preserve_package_122b_boundaries(self) -> None:
        with TemporaryDirectory() as state_dir:
            view = build_upper_console_view_model(state_dir=state_dir)
            audit = audit_non_llm_local_output_surface(state_dir=state_dir)

            self.assertFalse(view.sound_output_enabled)
            self.assertTrue(view.sound_patterns_reserved)
            self.assertEqual(audit.audit_status, "passed_non_llm_local_output_surface_and_operator_console_foundation")
            self.assertFalse(audit.qingyin_authored_output_created)
            self.assertFalse(audit.first_output_claimed)


if __name__ == "__main__":
    unittest.main()
