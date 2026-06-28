import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.environment.cradle_environment_state import (
    build_cradle_environment_state_from_last_session,
    save_cradle_environment_state,
)
from ashl_core_v1.memory.promotion_queue import enqueue_manual_promotion_candidate
from ashl_core_v1.runtime.cradle_session import run_case_in_cradle_session, start_cradle_session
from ashl_core_v1.runtime.open_cradle_tick_context import (
    BLOCKED_NEXT_SURFACES,
    build_open_cradle_tick_context,
    save_open_cradle_tick_context,
)
from ashl_core_v1.runtime.open_cradle_tick_dry_run import (
    DRY_RUN_MATRIX,
    build_teacher_gate_for_tick_context,
    build_tick_dry_run_record,
    list_tick_dry_run_history,
    load_last_tick_dry_run,
    run_teacher_gated_tick_dry_run,
    save_tick_dry_run,
)
from ashl_core_v1.runtime.open_cradle_tick_dry_run_audit import (
    build_tick_dry_run_audit,
    load_last_tick_dry_run_audit,
)
from ashl_core_v1.teacher_console.daily_teacher_note import write_daily_teacher_note
from ashl_core_v1.runtime.daily_run import run_cradle_daily


ROOT = Path(__file__).resolve().parents[2]
CLI_MODULE = "ashl_core_v1.runtime.open_cradle_tick_dry_run_cli"


class OpenCradleTeacherGatedTickDryRunTests(unittest.TestCase):
    def run_cli(
        self,
        data_dir: Path,
        *args: str,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", CLI_MODULE, "--data-dir", str(data_dir), *args],
            cwd=ROOT,
            check=check,
            capture_output=True,
            text=True,
        )

    def fake_context(
        self,
        mode: str = "observe_only",
        pending_review_items: list[dict] | None = None,
        caregiver_attention_items: list[str] | None = None,
        blocked_next_surfaces: list[str] | None = None,
    ) -> dict:
        return {
            "tick_context_id": f"context_{mode}",
            "tick_context_status": "built",
            "source_session_id": "session_001",
            "source_turn_count": 1,
            "recommended_tick_mode": mode,
            "tick_mode_reason_codes": [f"{mode}_reason"],
            "pending_review_items": pending_review_items or [],
            "caregiver_attention_items": caregiver_attention_items or [],
            "blocked_next_surfaces": blocked_next_surfaces
            if blocked_next_surfaces is not None
            else list(BLOCKED_NEXT_SURFACES),
            "trace_refs": ["session:session_001"],
        }

    def seed_active_context(self, data_dir: Path) -> dict:
        start_cradle_session(data_dir)
        run_case_in_cradle_session("success_front_step", data_dir)
        save_cradle_environment_state(
            build_cradle_environment_state_from_last_session(data_dir),
            data_dir,
        )
        return save_open_cradle_tick_context(build_open_cradle_tick_context(data_dir), data_dir)

    def test_teacher_gate_blocks_missing_tick_context(self):
        gate = build_teacher_gate_for_tick_context(None)

        self.assertEqual("blocked", gate["gate_status"])
        self.assertEqual("tick_context_missing", gate["gate_reason"])
        self.assertFalse(gate["allowed_for_dry_run"])

    def test_teacher_gate_blocks_unknown_recommended_tick_mode(self):
        gate = build_teacher_gate_for_tick_context(self.fake_context("unknown_mode"))

        self.assertEqual("blocked", gate["gate_status"])
        self.assertEqual("recommended_tick_mode_unknown", gate["gate_reason"])

    def test_teacher_gate_blocks_when_blocked_next_surfaces_are_incomplete(self):
        context = self.fake_context(blocked_next_surfaces=["automatic_tick_execution"])

        gate = build_teacher_gate_for_tick_context(context)

        self.assertEqual("blocked", gate["gate_status"])
        self.assertIn("blocked_next_surfaces_missing", gate["gate_reason"])

    def test_teacher_gate_marks_pending_items_as_needs_teacher_review(self):
        context = self.fake_context(
            "review_pending",
            pending_review_items=[{"item_kind": "unknown_feedback"}],
        )

        gate = build_teacher_gate_for_tick_context(context, "please review")

        self.assertEqual("needs_teacher_review", gate["gate_status"])
        self.assertTrue(gate["allowed_for_dry_run"])
        self.assertEqual("please review", gate["teacher_note"])

    def test_observe_only_creates_observe_only_dry_run(self):
        dry_run = self._dry_run_for_mode("observe_only")

        self.assertEqual("observe_only_dry_run", dry_run["dry_run_kind"])
        self.assertIn("environment_observation_summary", dry_run["proposed_outputs"])
        self.assertFalse(dry_run["requires_teacher_followup"])

    def test_environment_state_refresh_creates_environment_refresh_dry_run(self):
        dry_run = self._dry_run_for_mode("environment_state_refresh")

        self.assertEqual("environment_refresh_dry_run", dry_run["dry_run_kind"])
        self.assertIn("environment_refresh_request", dry_run["proposed_outputs"])

    def test_manual_daily_case_creates_manual_daily_case_dry_run(self):
        dry_run = self._dry_run_for_mode("manual_daily_case")

        self.assertEqual("manual_daily_case_dry_run", dry_run["dry_run_kind"])
        self.assertIn("manual_case_plan", dry_run["proposed_outputs"])

    def test_promotion_review_pending_creates_promotion_review_dry_run(self):
        dry_run = self._dry_run_for_mode(
            "promotion_review_pending",
            pending_review_items=[{"item_kind": "memory_promotion_candidate"}],
        )

        self.assertEqual("promotion_review_dry_run", dry_run["dry_run_kind"])
        self.assertTrue(dry_run["requires_teacher_followup"])
        self.assertEqual("teacher_review_required", dry_run["dry_run_status"])

    def test_review_pending_creates_review_pending_dry_run(self):
        dry_run = self._dry_run_for_mode(
            "review_pending",
            pending_review_items=[{"item_kind": "environment_state_unknown"}],
        )

        self.assertEqual("review_pending_dry_run", dry_run["dry_run_kind"])
        self.assertTrue(dry_run["requires_teacher_followup"])

    def test_teacher_wait_creates_teacher_wait_dry_run(self):
        dry_run = self._dry_run_for_mode("teacher_wait", caregiver_attention_items=["wait"])

        self.assertEqual("teacher_wait_dry_run", dry_run["dry_run_kind"])
        self.assertTrue(dry_run["requires_teacher_followup"])

    def test_stop_creates_stop_dry_run(self):
        dry_run = self._dry_run_for_mode("stop")

        self.assertEqual("stop_dry_run", dry_run["dry_run_kind"])
        self.assertIn("stop_reason_summary", dry_run["proposed_outputs"])

    def test_dry_run_preserves_blocked_action_execution_and_memory_write(self):
        dry_run = self._dry_run_for_mode("observe_only")

        self.assertIn("action_execution", dry_run["blocked_outputs"])
        self.assertIn("long_term_memory_write", dry_run["blocked_outputs"])

    def test_audit_passes_for_valid_dry_run(self):
        context = self.fake_context("observe_only")
        gate = build_teacher_gate_for_tick_context(context)
        dry_run = build_tick_dry_run_record(context, gate)

        audit = build_tick_dry_run_audit(dry_run, gate, context)

        self.assertTrue(audit["audit_passed"])
        self.assertTrue(audit["blocked_surfaces_preserved"])
        self.assertTrue(audit["no_runtime_execution"])

    def test_audit_fails_if_blocked_surfaces_are_missing(self):
        context = self.fake_context("manual_daily_case", blocked_next_surfaces=[])
        gate = build_teacher_gate_for_tick_context(context)
        dry_run = build_tick_dry_run_record(context, gate)
        broken = copy.deepcopy(dry_run)
        broken["blocked_outputs"] = []

        audit = build_tick_dry_run_audit(broken, gate, context)

        self.assertFalse(audit["audit_passed"])
        self.assertIn("blocked_surfaces_preserved_failed", audit["audit_notes"])

    def test_save_load_last_dry_run_round_trip_and_history_lists_records(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            dry_run = self._dry_run_for_mode("observe_only")

            saved = save_tick_dry_run(dry_run, data_dir)

            self.assertEqual(saved, load_last_tick_dry_run(data_dir))
            self.assertEqual(1, list_tick_dry_run_history(data_dir)["tick_dry_run_count"])

    def test_run_teacher_gated_tick_dry_run_creates_audit(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.seed_active_context(data_dir)

            result = run_teacher_gated_tick_dry_run(data_dir)

            self.assertEqual("observe_only", result["recommended_tick_mode"])
            self.assertEqual("dry_run_created", result["dry_run_status"])
            self.assertTrue(result["audit_passed"])
            self.assertEqual(
                result["tick_dry_run_audit"],
                load_last_tick_dry_run_audit(data_dir),
            )

    def test_promotion_review_pending_requires_teacher_followup_in_run(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.seed_active_context(data_dir)
            enqueue_manual_promotion_candidate(
                "interesting trace",
                "future review",
                "normal",
                data_dir,
            )

            result = run_teacher_gated_tick_dry_run(data_dir)

            self.assertEqual("promotion_review_pending", result["recommended_tick_mode"])
            self.assertTrue(result["requires_teacher_followup"])
            self.assertEqual("teacher_review_required", result["dry_run_status"])

    def test_cli_run_show_list_and_show_audit(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.seed_active_context(data_dir)

            run_result = self.run_cli(data_dir, "run-dry-run")
            run_payload = json.loads(run_result.stdout)
            last = json.loads(self.run_cli(data_dir, "show-last-dry-run").stdout)
            history = json.loads(self.run_cli(data_dir, "list-dry-runs").stdout)
            audit = json.loads(self.run_cli(data_dir, "show-last-audit").stdout)

            self.assertEqual(run_payload["tick_dry_run_id"], last["tick_dry_run_id"])
            self.assertEqual(1, history["tick_dry_run_count"])
            self.assertTrue(audit["audit_passed"])

    def test_cli_preferred_manual_daily_case_outputs_manual_dry_run(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.seed_active_context(data_dir)

            result = self.run_cli(
                data_dir,
                "run-dry-run",
                "--preferred-mode",
                "manual_daily_case",
                "--teacher-note",
                "manual only",
            )
            payload = json.loads(result.stdout)

            self.assertEqual("manual_daily_case", payload["recommended_tick_mode"])
            self.assertEqual("manual_daily_case_dry_run", payload["dry_run_kind"])

    def test_cli_show_missing_audit_returns_not_found(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_cli(Path(temp_dir), "show-last-audit", check=False)

            self.assertEqual(1, result.returncode)
            self.assertIn("not_found", result.stdout)

    def test_all_matrix_modes_have_expected_dry_run_kinds(self):
        expected = {
            "observe_only": "observe_only_dry_run",
            "environment_state_refresh": "environment_refresh_dry_run",
            "manual_daily_case": "manual_daily_case_dry_run",
            "promotion_review_pending": "promotion_review_dry_run",
            "review_pending": "review_pending_dry_run",
            "teacher_wait": "teacher_wait_dry_run",
            "stop": "stop_dry_run",
        }

        self.assertEqual(expected, {mode: spec["dry_run_kind"] for mode, spec in DRY_RUN_MATRIX.items()})

    def test_repo_data_directory_is_not_polluted_during_tests(self):
        self.assertFalse((ROOT / "ashl_core_v1" / "data").exists())

    def _dry_run_for_mode(
        self,
        mode: str,
        pending_review_items: list[dict] | None = None,
        caregiver_attention_items: list[str] | None = None,
    ) -> dict:
        context = self.fake_context(mode, pending_review_items, caregiver_attention_items)
        gate = build_teacher_gate_for_tick_context(context)
        return build_tick_dry_run_record(context, gate)


if __name__ == "__main__":
    unittest.main()
