import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from typing import Callable

from ashl_core_v1.runtime.no_codex_fixture_growth_loop_milestone_audit import (
    build_no_codex_fixture_growth_loop_milestone_audit,
)
from ashl_core_v1.runtime.no_codex_two_cycle_fixture_growth_run import (
    run_two_cycle_fixture_growth_demo,
)
from ashl_core_v1.runtime.session_learning_evidence_identity import FULL_COMMIT_APPROVAL_SCOPE
from ashl_core_v1.runtime.teacher_gated_session_store import STORE_FILENAME


def _build_two_cycle_run() -> tuple[tempfile.TemporaryDirectory, Path, str]:
    directory = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
    state_dir = Path(directory.name)
    result = run_two_cycle_fixture_growth_demo(
        teacher_decision="approved",
        approval_scope=FULL_COMMIT_APPROVAL_SCOPE,
        teacher_approval_text="I approve this exact reviewed evidence for interpretation and working readback.",
        reason_code="teacher_verified_exact_evidence",
        state_dir=state_dir,
    )
    return directory, state_dir, str(result["run_id"])


def _payload(connection: sqlite3.Connection, table: str, where: str, args: tuple[object, ...]) -> dict[str, object]:
    row = connection.execute(f"SELECT payload_json FROM {table} WHERE {where}", args).fetchone()
    if row is None:
        raise AssertionError(f"missing payload row: {table}")
    return dict(json.loads(row[0]))


def _update_payload(
    state_dir: Path,
    table: str,
    where: str,
    args: tuple[object, ...],
    mutate: Callable[[dict[str, object]], None],
) -> dict[str, object]:
    db_path = state_dir / STORE_FILENAME
    with sqlite3.connect(db_path) as connection:
        payload = _payload(connection, table, where, args)
        mutate(payload)
        connection.execute(
            f"UPDATE {table} SET payload_json = ? WHERE {where}",
            (json.dumps(payload, sort_keys=True, separators=(",", ":")), *args),
        )
        connection.commit()
    return payload


class NoCodexFixtureGrowthLoopMissingEvidenceTests(unittest.TestCase):
    def _build_and_audit_after(self, mutation: Callable[[Path, str], None]):
        directory, state_dir, run_id = _build_two_cycle_run()
        self.addCleanup(directory.cleanup)
        mutation(state_dir, run_id)
        return build_no_codex_fixture_growth_loop_milestone_audit(
            state_dir=state_dir,
            run_id=run_id,
        )

    def test_blocks_missing_teacher_decision_authoritative_evidence(self) -> None:
        def mutate(state_dir: Path, run_id: str) -> None:
            with sqlite3.connect(state_dir / STORE_FILENAME) as connection:
                receipt = _payload(connection, "cycle_one_growth_commit_receipts", "run_id = ?", (run_id,))
                connection.execute(
                    "DELETE FROM teacher_decisions WHERE teacher_decision_id = ?",
                    (receipt["teacher_decision_id"],),
                )
                connection.commit()

        audit = self._build_and_audit_after(mutate)
        self.assertEqual(audit.audit_status, "blocked_missing_authoritative_evidence")

    def test_blocks_wrong_approval_scope(self) -> None:
        def mutate(state_dir: Path, run_id: str) -> None:
            with sqlite3.connect(state_dir / STORE_FILENAME) as connection:
                receipt = _payload(connection, "cycle_one_growth_commit_receipts", "run_id = ?", (run_id,))
                connection.execute(
                    """
                    UPDATE teacher_decisions
                    SET approval_scope = 'feedback_candidate_only',
                        scope_sufficient_for_requested_operation = 0
                    WHERE teacher_decision_id = ?
                    """,
                    (receipt["teacher_decision_id"],),
                )
                connection.commit()

        audit = self._build_and_audit_after(mutate)
        self.assertEqual(audit.audit_status, "blocked_approval_scope_invalid")

    def test_blocks_process_reuse(self) -> None:
        def mutate(state_dir: Path, run_id: str) -> None:
            with sqlite3.connect(state_dir / STORE_FILENAME) as connection:
                first = _payload(connection, "cycle_process_receipts", "run_id = ? AND cycle_index = ?", (run_id, 1))
            _update_payload(
                state_dir,
                "cycle_process_receipts",
                "run_id = ? AND cycle_index = ?",
                (run_id, 2),
                lambda payload: payload.update({"process_instance_id": first["process_instance_id"]}),
            )

        audit = self._build_and_audit_after(mutate)
        self.assertEqual(audit.audit_status, "blocked_process_boundary_invalid")

    def test_blocks_fixture_identity_mismatch(self) -> None:
        def mutate(state_dir: Path, run_id: str) -> None:
            _update_payload(
                state_dir,
                "cycle_two_readback_consumption_receipts",
                "run_id = ?",
                (run_id,),
                lambda payload: payload.update({"current_fixture_payload_sha256": "mismatched"}),
            )

        audit = self._build_and_audit_after(mutate)
        self.assertEqual(audit.audit_status, "blocked_fixture_identity_mismatch")

    def test_blocks_readback_loaded_after_event(self) -> None:
        def mutate(state_dir: Path, run_id: str) -> None:
            _update_payload(
                state_dir,
                "cycle_two_readback_consumption_receipts",
                "run_id = ?",
                (run_id,),
                lambda payload: payload.update({"loaded_before_event_processing": False}),
            )

        audit = self._build_and_audit_after(mutate)
        self.assertEqual(audit.audit_status, "blocked_readback_loaded_after_event")

    def test_blocks_zero_delta_matching_claim(self) -> None:
        def mutate(state_dir: Path, run_id: str) -> None:
            _update_payload(
                state_dir,
                "cycle_two_readback_consumption_receipts",
                "run_id = ?",
                (run_id,),
                lambda payload: payload.update({"nonzero_delta_count": 0, "candidate_delta_applied": True}),
            )

        audit = self._build_and_audit_after(mutate)
        self.assertEqual(audit.audit_status, "blocked_candidate_delta_missing")

    def test_blocks_no_codex_counter_violation(self) -> None:
        def mutate(state_dir: Path, run_id: str) -> None:
            _update_payload(
                state_dir,
                "cycle_process_receipts",
                "run_id = ? AND cycle_index = ?",
                (run_id, 1),
                lambda payload: payload.update({"codex_runtime_call_count": 1}),
            )

        audit = self._build_and_audit_after(mutate)
        self.assertEqual(audit.audit_status, "blocked_codex_runtime_call")

    def test_blocks_raw_trace_summarization(self) -> None:
        def mutate(state_dir: Path, run_id: str) -> None:
            with sqlite3.connect(state_dir / STORE_FILENAME) as connection:
                row = connection.execute(
                    "SELECT trace_id, payload_snapshot_json FROM trace_envelopes WHERE trace_layer = 'raw' LIMIT 1"
                ).fetchone()
                self.assertIsNotNone(row)
                payload = dict(json.loads(row[1]))
                payload["raw_trace_summary"] = "forbidden summary"
                connection.execute(
                    "UPDATE trace_envelopes SET payload_snapshot_json = ? WHERE trace_id = ?",
                    (json.dumps(payload, sort_keys=True, separators=(",", ":")), row[0]),
                )
                connection.commit()

        audit = self._build_and_audit_after(mutate)
        self.assertEqual(audit.audit_status, "blocked_raw_trace_summarization")

    def test_blocks_external_control_flag(self) -> None:
        def mutate(state_dir: Path, run_id: str) -> None:
            _update_payload(
                state_dir,
                "two_cycle_fixture_growth_runs",
                "run_id = ?",
                (run_id,),
                lambda payload: payload.update({"external_control_detected": True}),
            )

        audit = self._build_and_audit_after(mutate)
        self.assertEqual(audit.audit_status, "blocked_external_control")


if __name__ == "__main__":
    unittest.main()
