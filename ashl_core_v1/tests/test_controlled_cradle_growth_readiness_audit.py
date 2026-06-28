from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.runtime.closed_learning_readback_loop_evidence import (
    run_closed_learning_readback_loop_evidence_demo,
)
from ashl_core_v1.runtime.controlled_cradle_growth_readiness_audit import (
    BLOCKED_CLAIMS,
    SAFE_CLAIM,
    build_controlled_cradle_growth_readiness_audit_record,
    list_controlled_cradle_growth_readiness_audits,
    load_last_controlled_cradle_growth_readiness_audit,
    run_controlled_cradle_growth_readiness_audit,
)
from ashl_core_v1.runtime.guided_cradle_growth_teacher_console import (
    run_growth_readiness_audit_from_guided_cradle_growth_console,
    show_growth_readiness_from_guided_cradle_growth_console,
)


class ControlledCradleGrowthReadinessAuditTests(unittest.TestCase):
    def test_valid_controlled_growth_readiness_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_closed_learning_readback_loop_evidence_demo(temp_dir)
            audit = run_controlled_cradle_growth_readiness_audit(temp_dir)
        self.assertEqual(
            audit["readiness_status"],
            "ready_for_controlled_cradle_growth_demo",
        )
        self.assertEqual(audit["safe_claim"], SAFE_CLAIM)

    def test_missing_bounded_runner_blocks(self) -> None:
        audit = self._audit(bounded_task_runner_present=False)
        self.assertEqual(audit["readiness_status"], "blocked_missing_task_loop")

    def test_missing_task_closure_blocks(self) -> None:
        audit = self._audit(task_closure_present=False)
        self.assertEqual(audit["readiness_status"], "blocked_missing_task_loop")

    def test_missing_teacher_review_blocks(self) -> None:
        audit = self._audit(teacher_review_present=False)
        self.assertEqual(audit["readiness_status"], "blocked_missing_teacher_review")

    def test_missing_memory_trace_blocks(self) -> None:
        audit = self._audit(memory_learning_trace_present=False)
        self.assertEqual(audit["readiness_status"], "blocked_missing_memory_trace")

    def test_missing_readback_preview_blocks(self) -> None:
        audit = self._audit(readback_preview_present=False)
        self.assertEqual(
            audit["readiness_status"],
            "blocked_missing_readback_application",
        )

    def test_missing_readback_application_blocks(self) -> None:
        audit = self._audit(readback_application_present=False)
        self.assertEqual(
            audit["readiness_status"],
            "blocked_missing_readback_application",
        )

    def test_missing_readback_contrast_blocks(self) -> None:
        audit = self._audit(readback_contrast_present=False)
        self.assertEqual(audit["readiness_status"], "blocked_missing_readback_contrast")

    def test_missing_closed_loop_evidence_blocks(self) -> None:
        audit = self._audit(closed_loop_evidence_present=False)
        self.assertEqual(
            audit["readiness_status"],
            "blocked_missing_closed_loop_evidence",
        )

    def test_automatic_approval_detected_blocks(self) -> None:
        audit = self._audit(automatic_approval_detected=True)
        self.assertEqual(
            audit["readiness_status"],
            "blocked_automatic_approval_detected",
        )

    def test_free_action_selection_detected_blocks(self) -> None:
        audit = self._audit(free_action_selection_detected=True)
        self.assertEqual(audit["readiness_status"], "blocked_action_execution_detected")

    def test_action_execution_detected_blocks(self) -> None:
        audit = self._audit(action_execution_detected=True)
        self.assertEqual(audit["readiness_status"], "blocked_action_execution_detected")

    def test_scheduler_detected_blocks(self) -> None:
        audit = self._audit(scheduler_detected=True)
        self.assertEqual(audit["readiness_status"], "blocked_scheduler_detected")

    def test_core_longterm_archive_anchor_write_detected_blocks(self) -> None:
        audit = self._audit(core_longterm_archive_anchor_write_detected=True)
        self.assertEqual(
            audit["readiness_status"],
            "blocked_memory_layer_write_detected",
        )

    def test_safe_claim_and_blocked_claims_are_present(self) -> None:
        audit = self._audit()
        self.assertEqual(audit["safe_claim"], SAFE_CLAIM)
        self.assertEqual(tuple(audit["blocked_claims"]), BLOCKED_CLAIMS)

    def test_cli_run_audit_show_and_list_work(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_closed_learning_readback_loop_evidence_demo(temp_dir)
            result = self._run_cli(temp_dir, "run-audit")
            self.assertEqual(result.returncode, 0, result.stderr)
            show = self._run_cli(temp_dir, "show-last-audit")
            self.assertEqual(show.returncode, 0, show.stderr)
            listing = self._run_cli(temp_dir, "list-audits")
            self.assertEqual(listing.returncode, 0, listing.stderr)

    def test_guided_console_run_growth_readiness_audit_works(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_closed_learning_readback_loop_evidence_demo(temp_dir)
            payload = run_growth_readiness_audit_from_guided_cradle_growth_console(
                temp_dir
            )
            shown = show_growth_readiness_from_guided_cradle_growth_console(temp_dir)
            listed = list_controlled_cradle_growth_readiness_audits(temp_dir)
            loaded = load_last_controlled_cradle_growth_readiness_audit(temp_dir)
        self.assertEqual(
            payload["growth_readiness_audit"]["readiness_status"],
            "ready_for_controlled_cradle_growth_demo",
        )
        self.assertEqual(shown["readiness_status"], "ready_for_controlled_cradle_growth_demo")
        self.assertEqual(loaded["audit_id"], shown["audit_id"])
        self.assertEqual(len(listed), 1)

    def test_no_repo_data_pollution(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_closed_learning_readback_loop_evidence_demo(temp_dir)
            run_controlled_cradle_growth_readiness_audit(temp_dir)
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _audit(self, **overrides: bool) -> dict:
        values = {
            "bounded_task_runner_present": True,
            "working_memory_task_loop_present": True,
            "multi_case_suite_present": True,
            "task_closure_present": True,
            "learning_candidate_extraction_present": True,
            "teacher_review_present": True,
            "reviewed_learning_present": True,
            "memory_learning_trace_present": True,
            "memory_application_data_present": True,
            "readback_preview_present": True,
            "readback_application_present": True,
            "readback_contrast_present": True,
            "closed_loop_evidence_present": True,
            "teacher_console_present": True,
            "readback_influence_visible": True,
            "teacher_review_required": True,
            "automatic_approval_detected": False,
            "free_action_selection_detected": False,
            "action_execution_detected": False,
            "scheduler_detected": False,
            "core_longterm_archive_anchor_write_detected": False,
            "unity_voice_bridge_detected": False,
            "source_trace_refs": ("source:demo",),
        }
        values.update(overrides)
        return build_controlled_cradle_growth_readiness_audit_record(**values)

    def _run_cli(self, temp_dir: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core_v1.runtime.controlled_cradle_growth_readiness_audit_cli",
                "--data-dir",
                temp_dir,
                *args,
            ],
            check=False,
            capture_output=True,
            text=True,
        )


if __name__ == "__main__":
    unittest.main()
