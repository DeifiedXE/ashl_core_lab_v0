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
from ashl_core_v1.runtime.teacher_gated_one_tick_runtime_stub import (
    PRESERVED_BLOCKED_SURFACES,
    save_tick_stub_record,
)
from ashl_core_v1.runtime.teacher_gated_two_tick_runtime_stub import (
    PRESERVED_SECOND_TICK_BLOCKED_SURFACES,
    build_second_tick_stub_record,
    build_two_tick_runtime_stub_gate,
    list_second_tick_stub_record_history,
    load_last_second_tick_stub_record,
    map_tick_mode_to_second_stub_kind,
    run_teacher_gated_two_tick_runtime_stub,
    save_second_tick_stub_record,
)
from ashl_core_v1.runtime.two_tick_runtime_stub_planning_precheck import (
    build_two_tick_runtime_stub_planning_precheck,
    save_two_tick_runtime_stub_planning_precheck,
)


ROOT = Path(__file__).resolve().parents[2]
CLI_MODULE = "ashl_core_v1.runtime.teacher_gated_two_tick_runtime_stub_cli"


class TeacherGatedTwoTickRuntimeStubTests(unittest.TestCase):
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

    def fake_first_tick_stub(self) -> dict:
        return {
            "tick_stub_id": "one_tick_runtime_stub_001",
            "source_readiness_review_id": "readiness_review_001",
            "source_tick_context_id": "tick_context_001",
            "source_tick_dry_run_id": "tick_dry_run_001",
            "source_tick_dry_run_audit_id": "tick_dry_run_audit_001",
            "trigger_kind": "manual_function_call",
            "teacher_gate_status": "allowed_for_one_tick_stub",
            "tick_stub_status": "tick_stub_record_created",
            "tick_mode": "observe_only",
            "tick_stub_kind": "observe_only_stub",
            "tick_stub_summary": "observe_only one-tick runtime stub record created.",
            "read_sources": [
                "runtime_stub_readiness_review",
                "tick_context",
                "tick_dry_run",
                "tick_dry_run_audit",
            ],
            "produced_surfaces": ["tick_stub_record", "observation_trace_summary"],
            "preserved_blocked_surfaces": list(PRESERVED_BLOCKED_SURFACES),
            "stopped_after_one_tick": True,
            "created_at": "2026-06-28T00:00:00+00:00",
            "trace_refs": ["tick_context:tick_context_001"],
        }

    def fake_precheck(self) -> dict:
        return {
            "precheck_id": "two_tick_precheck_001",
            "source_first_tick_stub_id": "one_tick_runtime_stub_001",
            "second_tick_planning_ready": True,
            "first_tick_clean": True,
        }

    def fake_context(self, mode: str = "observe_only") -> dict:
        return {
            "tick_context_id": f"fresh_context_{mode}",
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
            "trace_refs": [f"tick_context:fresh_context_{mode}"],
        }

    def fake_dry_run(self, mode: str = "observe_only") -> dict:
        return {
            "tick_dry_run_id": f"second_dry_run_{mode}",
            "source_tick_context_id": f"fresh_context_{mode}",
            "recommended_tick_mode": mode,
            "dry_run_status": "dry_run_created",
            "blocked_outputs": [
                "action_selection",
                "action_execution",
                "long_term_memory_write",
            ],
        }

    def fake_audit(self, mode: str = "observe_only") -> dict:
        return {
            "tick_dry_run_audit_id": f"second_audit_{mode}",
            "source_tick_dry_run_id": f"second_dry_run_{mode}",
            "audit_passed": True,
            "no_action_selection": True,
            "no_action_execution": True,
            "no_long_term_memory_write": True,
            "no_external_bridge": True,
        }

    def seed_valid_cli_prerequisites(self, data_dir: Path) -> None:
        start_cradle_session(data_dir)
        run_case_in_cradle_session("success_front_step", data_dir)
        save_cradle_environment_state(
            build_cradle_environment_state_from_last_session(data_dir),
            data_dir,
        )
        save_tick_stub_record(self.fake_first_tick_stub(), data_dir)
        precheck = build_two_tick_runtime_stub_planning_precheck(data_dir)
        save_two_tick_runtime_stub_planning_precheck(precheck, data_dir)

    def build_record_for_mode(self, mode: str) -> dict:
        precheck = self.fake_precheck()
        first_tick = self.fake_first_tick_stub()
        context = self.fake_context(mode)
        dry_run = self.fake_dry_run(mode)
        audit = self.fake_audit(mode)
        gate = build_two_tick_runtime_stub_gate(precheck, first_tick, context, dry_run, audit)
        return build_second_tick_stub_record(precheck, first_tick, context, dry_run, audit, gate)

    def test_gate_blocks_missing_precheck(self):
        gate = build_two_tick_runtime_stub_gate(
            None,
            self.fake_first_tick_stub(),
            self.fake_context(),
            self.fake_dry_run(),
            self.fake_audit(),
        )

        self.assertEqual("blocked", gate["teacher_gate_status"])
        self.assertEqual("two_tick_precheck_missing", gate["gate_reason"])

    def test_gate_blocks_second_tick_planning_ready_false(self):
        precheck = self.fake_precheck()
        precheck["second_tick_planning_ready"] = False

        gate = build_two_tick_runtime_stub_gate(
            precheck,
            self.fake_first_tick_stub(),
            self.fake_context(),
            self.fake_dry_run(),
            self.fake_audit(),
        )

        self.assertEqual("second_tick_planning_ready_false", gate["gate_reason"])

    def test_gate_blocks_first_tick_clean_false(self):
        precheck = self.fake_precheck()
        precheck["first_tick_clean"] = False

        gate = build_two_tick_runtime_stub_gate(
            precheck,
            self.fake_first_tick_stub(),
            self.fake_context(),
            self.fake_dry_run(),
            self.fake_audit(),
        )

        self.assertEqual("first_tick_clean_false", gate["gate_reason"])

    def test_gate_blocks_missing_first_tick_stub_record(self):
        gate = build_two_tick_runtime_stub_gate(
            self.fake_precheck(),
            None,
            self.fake_context(),
            self.fake_dry_run(),
            self.fake_audit(),
        )

        self.assertEqual("first_tick_stub_record_missing", gate["gate_reason"])

    def test_gate_blocks_missing_fresh_tick_context(self):
        gate = build_two_tick_runtime_stub_gate(
            self.fake_precheck(),
            self.fake_first_tick_stub(),
            None,
            self.fake_dry_run(),
            self.fake_audit(),
        )

        self.assertEqual("fresh_tick_context_missing", gate["gate_reason"])

    def test_gate_blocks_missing_second_dry_run(self):
        gate = build_two_tick_runtime_stub_gate(
            self.fake_precheck(),
            self.fake_first_tick_stub(),
            self.fake_context(),
            None,
            self.fake_audit(),
        )

        self.assertEqual("second_dry_run_missing", gate["gate_reason"])

    def test_gate_blocks_missing_second_dry_run_audit(self):
        gate = build_two_tick_runtime_stub_gate(
            self.fake_precheck(),
            self.fake_first_tick_stub(),
            self.fake_context(),
            self.fake_dry_run(),
            None,
        )

        self.assertEqual("second_dry_run_audit_missing", gate["gate_reason"])

    def test_gate_blocks_failed_second_dry_run_audit(self):
        audit = self.fake_audit()
        audit["audit_passed"] = False

        gate = build_two_tick_runtime_stub_gate(
            self.fake_precheck(),
            self.fake_first_tick_stub(),
            self.fake_context(),
            self.fake_dry_run(),
            audit,
        )

        self.assertEqual("second_dry_run_audit_failed", gate["gate_reason"])

    def test_gate_blocks_non_manual_trigger(self):
        gate = build_two_tick_runtime_stub_gate(
            self.fake_precheck(),
            self.fake_first_tick_stub(),
            self.fake_context(),
            self.fake_dry_run(),
            self.fake_audit(),
            "background_scheduler",
        )

        self.assertEqual("trigger_kind_not_manual", gate["gate_reason"])

    def test_gate_blocks_incomplete_blocked_surfaces(self):
        context = self.fake_context()
        dry_run = self.fake_dry_run()
        context["blocked_next_surfaces"] = [
            surface for surface in context["blocked_next_surfaces"] if surface != "action_execution"
        ]
        dry_run["blocked_outputs"] = [
            surface for surface in dry_run["blocked_outputs"] if surface != "action_execution"
        ]

        gate = build_two_tick_runtime_stub_gate(
            self.fake_precheck(),
            self.fake_first_tick_stub(),
            context,
            dry_run,
            self.fake_audit(),
        )

        self.assertEqual("blocked_surfaces_incomplete", gate["gate_reason"])

    def test_valid_sources_create_second_tick_stub_record(self):
        record = self.build_record_for_mode("observe_only")

        self.assertEqual("second_tick_stub_record_created", record["second_tick_status"])
        self.assertEqual("allowed_for_second_tick_stub", record["teacher_gate_status"])

    def test_second_tick_stub_record_links_all_source_ids(self):
        record = self.build_record_for_mode("observe_only")

        self.assertEqual("one_tick_runtime_stub_001", record["source_first_tick_stub_id"])
        self.assertEqual("two_tick_precheck_001", record["source_two_tick_precheck_id"])
        self.assertEqual("fresh_context_observe_only", record["source_fresh_tick_context_id"])
        self.assertEqual("second_dry_run_observe_only", record["source_second_tick_dry_run_id"])
        self.assertEqual(
            "second_audit_observe_only",
            record["source_second_tick_dry_run_audit_id"],
        )

    def test_second_tick_stub_record_marks_fresh_context_dry_run_and_audit_used(self):
        record = self.build_record_for_mode("observe_only")

        self.assertTrue(record["fresh_context_used"])
        self.assertTrue(record["second_dry_run_used"])
        self.assertTrue(record["second_audit_used"])

    def test_observe_only_maps_to_observe_only_second_stub(self):
        record = self.build_record_for_mode("observe_only")

        self.assertEqual("observe_only_second_stub", record["second_tick_stub_kind"])
        self.assertIn("observation_trace_summary", record["produced_surfaces"])

    def test_environment_state_refresh_maps_to_environment_refresh_second_stub(self):
        record = self.build_record_for_mode("environment_state_refresh")

        self.assertEqual("environment_refresh_second_stub", record["second_tick_stub_kind"])
        self.assertIn("environment_refresh_request", record["produced_surfaces"])

    def test_manual_daily_case_maps_to_manual_daily_case_second_stub(self):
        record = self.build_record_for_mode("manual_daily_case")

        self.assertEqual("manual_daily_case_second_stub", record["second_tick_stub_kind"])
        self.assertIn("manual_daily_case_request", record["produced_surfaces"])

    def test_promotion_review_pending_maps_to_promotion_review_second_stub(self):
        record = self.build_record_for_mode("promotion_review_pending")

        self.assertEqual("promotion_review_second_stub", record["second_tick_stub_kind"])
        self.assertEqual("needs_teacher_review", record["teacher_gate_status"])
        self.assertEqual("teacher_review_required", record["second_tick_status"])

    def test_review_pending_maps_to_review_pending_second_stub(self):
        record = self.build_record_for_mode("review_pending")

        self.assertEqual("review_pending_second_stub", record["second_tick_stub_kind"])
        self.assertEqual("teacher_review_required", record["second_tick_status"])

    def test_teacher_wait_maps_to_teacher_wait_second_stub(self):
        record = self.build_record_for_mode("teacher_wait")

        self.assertEqual("teacher_wait_second_stub", record["second_tick_stub_kind"])
        self.assertEqual("teacher_review_required", record["second_tick_status"])

    def test_stop_maps_to_stop_second_stub(self):
        record = self.build_record_for_mode("stop")

        self.assertEqual("stop_second_stub", record["second_tick_stub_kind"])
        self.assertIn("stop_reason_summary", record["produced_surfaces"])

    def test_second_tick_record_stops_and_does_not_create_loop(self):
        record = self.build_record_for_mode("observe_only")

        self.assertTrue(record["stopped_after_second_tick"])
        self.assertFalse(record["third_tick_created"])
        self.assertFalse(record["continuous_loop_created"])

    def test_preserved_blocked_surfaces_include_required_surfaces(self):
        record = self.build_record_for_mode("observe_only")

        self.assertIn("automatic_tick_execution", record["preserved_blocked_surfaces"])
        self.assertIn("action_execution", record["preserved_blocked_surfaces"])
        self.assertIn("long_term_memory_write", record["preserved_blocked_surfaces"])
        self.assertIn("continuous_runtime_loop", record["preserved_blocked_surfaces"])
        self.assertEqual(
            set(PRESERVED_SECOND_TICK_BLOCKED_SURFACES),
            set(record["preserved_blocked_surfaces"]),
        )

    def test_save_load_last_second_tick_round_trip_and_list_history(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            record = self.build_record_for_mode("observe_only")

            saved = save_second_tick_stub_record(record, data_dir)

            self.assertEqual(saved, load_last_second_tick_stub_record(data_dir))
            self.assertEqual(
                1,
                list_second_tick_stub_record_history(data_dir)[
                    "second_tick_stub_record_count"
                ],
            )

    def test_run_second_tick_creates_record_from_valid_prerequisites(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.seed_valid_cli_prerequisites(data_dir)

            record = run_teacher_gated_two_tick_runtime_stub(data_dir)

            self.assertEqual("second_tick_stub_record_created", record["second_tick_status"])
            self.assertEqual("observe_only_second_stub", record["second_tick_stub_kind"])
            self.assertTrue(record["stopped_after_second_tick"])
            self.assertFalse(record["third_tick_created"])

    def test_run_second_tick_blocks_when_precheck_missing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            record = run_teacher_gated_two_tick_runtime_stub(Path(temp_dir))

            self.assertEqual("blocked_by_precheck", record["second_tick_status"])
            self.assertEqual("blocked", record["teacher_gate_status"])
            self.assertFalse(record["fresh_context_used"])

    def test_map_tick_mode_to_second_stub_kind_rejects_unknown_mode(self):
        with self.assertRaises(ValueError):
            map_tick_mode_to_second_stub_kind("unknown")

    def test_cli_run_second_tick_show_and_list_work_after_valid_prerequisites(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.seed_valid_cli_prerequisites(data_dir)

            run_payload = json.loads(self.run_cli(data_dir, "run-second-tick").stdout)
            last_payload = json.loads(self.run_cli(data_dir, "show-last-second-tick").stdout)
            list_payload = json.loads(self.run_cli(data_dir, "list-second-ticks").stdout)

            self.assertEqual(
                run_payload["second_tick_stub_id"],
                last_payload["second_tick_stub_id"],
            )
            self.assertEqual(1, list_payload["second_tick_stub_record_count"])
            self.assertFalse(run_payload["third_tick_created"])
            self.assertFalse(run_payload["continuous_loop_created"])

    def test_cli_show_missing_second_tick_returns_not_found(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_cli(Path(temp_dir), "show-last-second-tick", check=False)

            self.assertEqual(1, result.returncode)
            self.assertIn("not_found", result.stdout)

    def test_repo_data_directory_is_not_polluted_during_tests(self):
        self.assertFalse((ROOT / "ashl_core_v1" / "data").exists())


if __name__ == "__main__":
    unittest.main()
