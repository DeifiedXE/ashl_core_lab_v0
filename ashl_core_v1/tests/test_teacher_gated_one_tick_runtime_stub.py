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
from ashl_core_v1.runtime.cradle_session import run_case_in_cradle_session, start_cradle_session
from ashl_core_v1.runtime.open_cradle_runtime_stub_readiness import (
    build_open_cradle_runtime_stub_readiness_review,
    save_open_cradle_runtime_stub_readiness_review,
)
from ashl_core_v1.runtime.open_cradle_tick_context import (
    build_open_cradle_tick_context,
    save_open_cradle_tick_context,
)
from ashl_core_v1.runtime.open_cradle_tick_dry_run import run_teacher_gated_tick_dry_run
from ashl_core_v1.runtime.teacher_gated_one_tick_runtime_stub import (
    PRESERVED_BLOCKED_SURFACES,
    build_one_tick_runtime_stub_gate,
    build_tick_stub_record,
    list_tick_stub_record_history,
    load_last_tick_stub_record,
    map_tick_mode_to_stub_kind,
    run_teacher_gated_one_tick_runtime_stub,
    save_tick_stub_record,
)


ROOT = Path(__file__).resolve().parents[2]
CLI_MODULE = "ashl_core_v1.runtime.teacher_gated_one_tick_runtime_stub_cli"


class TeacherGatedOneTickRuntimeStubTests(unittest.TestCase):
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

    def seed_ready_sources(self, data_dir: Path) -> dict:
        start_cradle_session(data_dir)
        run_case_in_cradle_session("success_front_step", data_dir)
        save_cradle_environment_state(
            build_cradle_environment_state_from_last_session(data_dir),
            data_dir,
        )
        run_teacher_gated_tick_dry_run(data_dir)
        review = build_open_cradle_runtime_stub_readiness_review(data_dir)
        return save_open_cradle_runtime_stub_readiness_review(review, data_dir)

    def fake_ready(self) -> dict:
        return {
            "review_id": "review_001",
            "runtime_stub_design_ready": True,
            "runtime_stub_implementation_ready": True,
            "still_blocked_surfaces": list(PRESERVED_BLOCKED_SURFACES),
        }

    def fake_context(self, mode: str = "observe_only") -> dict:
        return {
            "tick_context_id": f"context_{mode}",
            "recommended_tick_mode": mode,
            "blocked_next_surfaces": [
                "automatic_tick_execution",
                "free_action_selection",
                "action_execution",
                "long_term_memory_write",
                "external_bridge_operation",
                "voice_output",
                "unity_home_operation",
            ],
            "source_session_summary_ref": "session_summary:session_001:1",
            "source_environment_state_id": "environment_state_001",
            "source_daily_teacher_note_id": None,
            "source_first_output_followup_id": None,
            "source_memory_promotion_candidate_ids": [],
            "trace_refs": ["session:session_001"],
        }

    def fake_dry_run(self, mode: str = "observe_only") -> dict:
        return {
            "tick_dry_run_id": f"dry_run_{mode}",
            "recommended_tick_mode": mode,
            "dry_run_status": "dry_run_created",
        }

    def fake_audit(self) -> dict:
        return {
            "tick_dry_run_audit_id": "audit_001",
            "audit_passed": True,
            "blocked_surfaces_preserved": True,
        }

    def test_gate_blocks_missing_readiness_review(self):
        gate = build_one_tick_runtime_stub_gate(
            None,
            self.fake_context(),
            self.fake_dry_run(),
            self.fake_audit(),
        )

        self.assertEqual("blocked", gate["teacher_gate_status"])
        self.assertEqual("readiness_review_missing", gate["gate_reason"])

    def test_gate_blocks_readiness_false(self):
        ready = self.fake_ready()
        ready["runtime_stub_design_ready"] = False

        gate = build_one_tick_runtime_stub_gate(
            ready,
            self.fake_context(),
            self.fake_dry_run(),
            self.fake_audit(),
        )

        self.assertEqual("blocked", gate["teacher_gate_status"])
        self.assertEqual("runtime_stub_design_ready_false", gate["gate_reason"])

    def test_gate_blocks_missing_tick_context(self):
        gate = build_one_tick_runtime_stub_gate(
            self.fake_ready(),
            None,
            self.fake_dry_run(),
            self.fake_audit(),
        )

        self.assertEqual("blocked", gate["teacher_gate_status"])
        self.assertEqual("tick_context_missing", gate["gate_reason"])

    def test_gate_blocks_missing_dry_run(self):
        gate = build_one_tick_runtime_stub_gate(
            self.fake_ready(),
            self.fake_context(),
            None,
            self.fake_audit(),
        )

        self.assertEqual("dry_run_missing", gate["gate_reason"])

    def test_gate_blocks_missing_dry_run_audit(self):
        gate = build_one_tick_runtime_stub_gate(
            self.fake_ready(),
            self.fake_context(),
            self.fake_dry_run(),
            None,
        )

        self.assertEqual("dry_run_audit_missing", gate["gate_reason"])

    def test_gate_blocks_failed_audit(self):
        audit = self.fake_audit()
        audit["audit_passed"] = False

        gate = build_one_tick_runtime_stub_gate(
            self.fake_ready(),
            self.fake_context(),
            self.fake_dry_run(),
            audit,
        )

        self.assertEqual("dry_run_audit_failed", gate["gate_reason"])

    def test_gate_blocks_non_manual_trigger(self):
        gate = build_one_tick_runtime_stub_gate(
            self.fake_ready(),
            self.fake_context(),
            self.fake_dry_run(),
            self.fake_audit(),
            "background_scheduler",
        )

        self.assertEqual("blocked", gate["teacher_gate_status"])
        self.assertEqual("trigger_kind_not_manual", gate["gate_reason"])

    def test_valid_readiness_context_dry_run_and_audit_creates_tick_stub_record(self):
        record = self._record_for_mode("observe_only")

        self.assertEqual("tick_stub_record_created", record["tick_stub_status"])
        self.assertEqual("allowed_for_one_tick_stub", record["teacher_gate_status"])

    def test_tick_stub_record_links_source_ids(self):
        record = self._record_for_mode("observe_only")

        self.assertEqual("review_001", record["source_readiness_review_id"])
        self.assertEqual("context_observe_only", record["source_tick_context_id"])
        self.assertEqual("dry_run_observe_only", record["source_tick_dry_run_id"])
        self.assertEqual("audit_001", record["source_tick_dry_run_audit_id"])

    def test_observe_only_maps_to_observe_only_stub(self):
        record = self._record_for_mode("observe_only")

        self.assertEqual("observe_only_stub", record["tick_stub_kind"])
        self.assertIn("observation_trace_summary", record["produced_surfaces"])

    def test_environment_state_refresh_maps_to_environment_refresh_stub(self):
        record = self._record_for_mode("environment_state_refresh")

        self.assertEqual("environment_refresh_stub", record["tick_stub_kind"])
        self.assertIn("environment_refresh_request", record["produced_surfaces"])

    def test_manual_daily_case_maps_to_manual_daily_case_stub(self):
        record = self._record_for_mode("manual_daily_case")

        self.assertEqual("manual_daily_case_stub", record["tick_stub_kind"])
        self.assertIn("manual_daily_case_request", record["produced_surfaces"])

    def test_promotion_review_pending_maps_to_promotion_review_stub(self):
        record = self._record_for_mode("promotion_review_pending")

        self.assertEqual("promotion_review_stub", record["tick_stub_kind"])
        self.assertEqual("teacher_review_required", record["tick_stub_status"])
        self.assertEqual("needs_teacher_review", record["teacher_gate_status"])

    def test_review_pending_maps_to_review_pending_stub(self):
        record = self._record_for_mode("review_pending")

        self.assertEqual("review_pending_stub", record["tick_stub_kind"])
        self.assertEqual("teacher_review_required", record["tick_stub_status"])

    def test_teacher_wait_maps_to_teacher_wait_stub(self):
        record = self._record_for_mode("teacher_wait")

        self.assertEqual("teacher_wait_stub", record["tick_stub_kind"])
        self.assertEqual("teacher_review_required", record["tick_stub_status"])

    def test_stop_maps_to_stop_stub(self):
        record = self._record_for_mode("stop")

        self.assertEqual("stop_stub", record["tick_stub_kind"])
        self.assertIn("stop_reason_summary", record["produced_surfaces"])

    def test_all_tick_stub_records_stop_after_one_tick(self):
        for mode in (
            "observe_only",
            "environment_state_refresh",
            "manual_daily_case",
            "promotion_review_pending",
            "review_pending",
            "teacher_wait",
            "stop",
        ):
            with self.subTest(mode=mode):
                self.assertTrue(self._record_for_mode(mode)["stopped_after_one_tick"])

    def test_preserved_blocked_surfaces_include_required_surfaces(self):
        record = self._record_for_mode("observe_only")

        self.assertIn("automatic_tick_execution", record["preserved_blocked_surfaces"])
        self.assertIn("action_execution", record["preserved_blocked_surfaces"])
        self.assertIn("long_term_memory_write", record["preserved_blocked_surfaces"])

    def test_save_load_last_tick_round_trip_and_list_history(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            record = self._record_for_mode("observe_only")

            saved = save_tick_stub_record(record, data_dir)

            self.assertEqual(saved, load_last_tick_stub_record(data_dir))
            self.assertEqual(1, list_tick_stub_record_history(data_dir)["tick_stub_record_count"])

    def test_run_one_tick_creates_record_from_valid_prerequisites(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.seed_ready_sources(data_dir)

            record = run_teacher_gated_one_tick_runtime_stub(data_dir)

            self.assertEqual("tick_stub_record_created", record["tick_stub_status"])
            self.assertEqual("observe_only_stub", record["tick_stub_kind"])
            self.assertTrue(record["stopped_after_one_tick"])

    def test_run_one_tick_blocks_when_readiness_missing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            record = run_teacher_gated_one_tick_runtime_stub(Path(temp_dir))

            self.assertEqual("blocked_by_teacher_gate", record["tick_stub_status"])
            self.assertEqual("blocked", record["teacher_gate_status"])

    def test_map_tick_mode_to_stub_kind_rejects_unknown_mode(self):
        with self.assertRaises(ValueError):
            map_tick_mode_to_stub_kind("unknown")

    def test_cli_run_one_tick_show_and_list_work_after_valid_prerequisites(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.seed_ready_sources(data_dir)

            run_payload = json.loads(self.run_cli(data_dir, "run-one-tick").stdout)
            last_payload = json.loads(self.run_cli(data_dir, "show-last-tick").stdout)
            list_payload = json.loads(self.run_cli(data_dir, "list-ticks").stdout)

            self.assertEqual(run_payload["tick_stub_id"], last_payload["tick_stub_id"])
            self.assertEqual(1, list_payload["tick_stub_record_count"])

    def test_cli_show_missing_tick_returns_not_found(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_cli(Path(temp_dir), "show-last-tick", check=False)

            self.assertEqual(1, result.returncode)
            self.assertIn("not_found", result.stdout)

    def test_repo_data_directory_is_not_polluted_during_tests(self):
        self.assertFalse((ROOT / "ashl_core_v1" / "data").exists())

    def _record_for_mode(self, mode: str) -> dict:
        ready = self.fake_ready()
        context = self.fake_context(mode)
        dry_run = self.fake_dry_run(mode)
        audit = self.fake_audit()
        gate = build_one_tick_runtime_stub_gate(ready, context, dry_run, audit)
        return build_tick_stub_record(ready, context, dry_run, audit, gate)


if __name__ == "__main__":
    unittest.main()
