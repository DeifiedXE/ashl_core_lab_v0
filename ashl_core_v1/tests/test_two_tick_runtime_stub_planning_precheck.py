import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.runtime.teacher_gated_one_tick_runtime_stub import (
    LAST_TICK_STUB_RECORD_FILE,
    PRESERVED_BLOCKED_SURFACES,
    save_tick_stub_record,
)
from ashl_core_v1.runtime.two_tick_runtime_stub_planning_precheck import (
    CURRENT_ALLOWED_CLAIM,
    PATCH_NEXT_PACKAGE,
    READY_NEXT_PACKAGE,
    build_second_tick_context_plan,
    build_second_tick_gate_plan,
    build_two_tick_runtime_stub_planning_precheck,
    evaluate_first_tick_cleanliness,
    list_two_tick_runtime_stub_planning_prechecks,
    load_last_two_tick_runtime_stub_planning_precheck,
    save_two_tick_runtime_stub_planning_precheck,
    write_two_tick_runtime_stub_planning_precheck_report,
)


ROOT = Path(__file__).resolve().parents[2]
CLI_MODULE = "ashl_core_v1.runtime.two_tick_runtime_stub_planning_precheck_cli"


class TwoTickRuntimeStubPlanningPrecheckTests(unittest.TestCase):
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

    def fake_tick_stub_record(self) -> dict:
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

    def write_raw_tick_stub_record(self, data_dir: Path, record: dict) -> None:
        data_dir.mkdir(parents=True, exist_ok=True)
        (data_dir / LAST_TICK_STUB_RECORD_FILE).write_text(
            json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def seed_valid_tick_stub(self, data_dir: Path) -> dict:
        return save_tick_stub_record(self.fake_tick_stub_record(), data_dir)

    def test_precheck_returns_dict_with_required_top_level_keys(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            precheck = build_two_tick_runtime_stub_planning_precheck(Path(temp_dir))

            for key in (
                "precheck_id",
                "status",
                "source_first_tick_stub_id",
                "source_readiness_review_id",
                "source_tick_context_id",
                "source_tick_dry_run_id",
                "source_tick_dry_run_audit_id",
                "first_tick_record_present",
                "first_tick_clean",
                "first_tick_stopped_after_one_tick",
                "first_tick_manual_trigger_only",
                "first_tick_teacher_gated",
                "first_tick_preserved_blocked_surfaces",
                "first_tick_no_scheduler",
                "first_tick_no_action_selection",
                "first_tick_no_action_execution",
                "first_tick_no_long_term_memory_write",
                "first_tick_no_external_bridge",
                "second_tick_planning_ready",
                "second_tick_context_plan",
                "second_tick_gate_plan",
                "second_tick_allowed_scope",
                "second_tick_blocked_surfaces",
                "second_tick_required_inputs",
                "second_tick_stop_conditions",
                "missing_items",
                "next_recommended_package",
                "current_allowed_claim",
                "current_not_yet_claim",
                "created_at",
                "trace_refs",
            ):
                self.assertIn(key, precheck)

    def test_missing_first_tick_makes_record_present_and_planning_ready_false(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            precheck = build_two_tick_runtime_stub_planning_precheck(Path(temp_dir))

            self.assertFalse(precheck["first_tick_record_present"])
            self.assertFalse(precheck["second_tick_planning_ready"])
            self.assertIn("first_tick_record_present", precheck["missing_items"])

    def test_valid_first_tick_makes_first_tick_clean_and_planning_ready_true(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.seed_valid_tick_stub(data_dir)

            precheck = build_two_tick_runtime_stub_planning_precheck(data_dir)

            self.assertTrue(precheck["first_tick_clean"])
            self.assertTrue(precheck["second_tick_planning_ready"])
            self.assertEqual("ready", precheck["status"])

    def test_stopped_after_one_tick_false_makes_first_tick_clean_false(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            record = self.fake_tick_stub_record()
            record["stopped_after_one_tick"] = False
            self.write_raw_tick_stub_record(data_dir, record)

            precheck = build_two_tick_runtime_stub_planning_precheck(data_dir)

            self.assertFalse(precheck["first_tick_stopped_after_one_tick"])
            self.assertFalse(precheck["first_tick_clean"])

    def test_non_manual_trigger_makes_first_tick_clean_false(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            record = self.fake_tick_stub_record()
            record["trigger_kind"] = "background_scheduler"
            self.write_raw_tick_stub_record(data_dir, record)

            precheck = build_two_tick_runtime_stub_planning_precheck(data_dir)

            self.assertFalse(precheck["first_tick_manual_trigger_only"])
            self.assertFalse(precheck["first_tick_clean"])

    def test_missing_teacher_gate_makes_first_tick_clean_false(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            record = self.fake_tick_stub_record()
            record["teacher_gate_status"] = "blocked"
            self.write_raw_tick_stub_record(data_dir, record)

            precheck = build_two_tick_runtime_stub_planning_precheck(data_dir)

            self.assertFalse(precheck["first_tick_teacher_gated"])
            self.assertFalse(precheck["first_tick_clean"])

    def test_missing_blocked_surface_makes_first_tick_clean_false(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            record = self.fake_tick_stub_record()
            record["preserved_blocked_surfaces"] = [
                surface
                for surface in record["preserved_blocked_surfaces"]
                if surface != "background_scheduler"
            ]
            self.write_raw_tick_stub_record(data_dir, record)

            precheck = build_two_tick_runtime_stub_planning_precheck(data_dir)

            self.assertFalse(precheck["first_tick_preserved_blocked_surfaces"])
            self.assertFalse(precheck["first_tick_no_scheduler"])

    def test_action_execution_not_blocked_makes_first_tick_clean_false(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            record = self.fake_tick_stub_record()
            record["preserved_blocked_surfaces"] = [
                surface
                for surface in record["preserved_blocked_surfaces"]
                if surface != "action_execution"
            ]
            self.write_raw_tick_stub_record(data_dir, record)

            precheck = build_two_tick_runtime_stub_planning_precheck(data_dir)

            self.assertFalse(precheck["first_tick_no_action_execution"])
            self.assertFalse(precheck["first_tick_clean"])

    def test_long_term_memory_write_not_blocked_makes_first_tick_clean_false(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            record = self.fake_tick_stub_record()
            record["preserved_blocked_surfaces"] = [
                surface
                for surface in record["preserved_blocked_surfaces"]
                if surface != "long_term_memory_write"
            ]
            self.write_raw_tick_stub_record(data_dir, record)

            precheck = build_two_tick_runtime_stub_planning_precheck(data_dir)

            self.assertFalse(precheck["first_tick_no_long_term_memory_write"])
            self.assertFalse(precheck["first_tick_clean"])

    def test_second_tick_context_plan_exists_when_ready(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.seed_valid_tick_stub(data_dir)

            precheck = build_two_tick_runtime_stub_planning_precheck(data_dir)
            plan = precheck["second_tick_context_plan"]

            self.assertEqual("one_tick_runtime_stub_001", plan["source_first_tick_stub_id"])
            self.assertIn(
                "plus_refresh_tick_context_before_second_tick",
                plan["next_context_source_policy"],
            )
            self.assertIn("fresh_tick_context", plan["required_refresh_sources"])

    def test_second_tick_gate_plan_requires_fresh_context_and_dry_run_audit(self):
        gate_plan = build_second_tick_gate_plan()

        self.assertTrue(gate_plan["gate_required"])
        self.assertTrue(gate_plan["requires_fresh_tick_context"])
        self.assertTrue(gate_plan["requires_teacher_gated_dry_run"])
        self.assertTrue(gate_plan["requires_dry_run_audit"])
        self.assertTrue(gate_plan["requires_manual_trigger"])

    def test_second_tick_allowed_scope_blocks_scheduler_and_action_execution(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.seed_valid_tick_stub(data_dir)

            precheck = build_two_tick_runtime_stub_planning_precheck(data_dir)

            self.assertIn("background_scheduler", precheck["second_tick_blocked_surfaces"])
            self.assertIn("scheduler", precheck["second_tick_blocked_surfaces"])
            self.assertIn("action_execution", precheck["second_tick_blocked_surfaces"])
            self.assertIn("stop_after_second_tick", precheck["second_tick_allowed_scope"])

    def test_next_recommended_package_points_to_two_tick_runtime_stub_when_ready(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.seed_valid_tick_stub(data_dir)

            precheck = build_two_tick_runtime_stub_planning_precheck(data_dir)

            self.assertEqual(READY_NEXT_PACKAGE, precheck["next_recommended_package"])

    def test_next_recommended_package_points_to_patch_when_not_ready(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            precheck = build_two_tick_runtime_stub_planning_precheck(Path(temp_dir))

            self.assertEqual(PATCH_NEXT_PACKAGE, precheck["next_recommended_package"])

    def test_save_load_last_precheck_round_trip_and_list_prechecks(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.seed_valid_tick_stub(data_dir)
            precheck = build_two_tick_runtime_stub_planning_precheck(data_dir)

            saved = save_two_tick_runtime_stub_planning_precheck(precheck, data_dir)

            self.assertEqual(
                saved,
                load_last_two_tick_runtime_stub_planning_precheck(data_dir),
            )
            self.assertEqual(
                1,
                list_two_tick_runtime_stub_planning_prechecks(data_dir)[
                    "two_tick_precheck_count"
                ],
            )

    def test_write_report_creates_markdown(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.seed_valid_tick_stub(data_dir)
            path = data_dir / "two_tick_precheck.md"

            result = write_two_tick_runtime_stub_planning_precheck_report(path, data_dir)
            text = path.read_text(encoding="utf-8")

            self.assertEqual(str(path), result["path"])
            self.assertIn(CURRENT_ALLOWED_CLAIM, text)
            self.assertIn("This is not a second runtime tick.", text)

    def test_evaluate_first_tick_cleanliness_helper_reports_missing_items(self):
        cleanliness = evaluate_first_tick_cleanliness(None)

        self.assertFalse(cleanliness["first_tick_clean"])
        self.assertIn("first_tick_record_present", cleanliness["missing_items"])

    def test_context_plan_helper_carries_forward_trace_refs(self):
        plan = build_second_tick_context_plan(self.fake_tick_stub_record())

        self.assertIn(
            "first_tick_stub_record:one_tick_runtime_stub_001",
            plan["carry_forward_refs"],
        )
        self.assertIn("tick_context:tick_context_001", plan["carry_forward_refs"])

    def test_missing_source_ids_block_planning_ready_but_not_cleanliness(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            record = self.fake_tick_stub_record()
            record["source_tick_dry_run_audit_id"] = None
            self.write_raw_tick_stub_record(data_dir, record)

            precheck = build_two_tick_runtime_stub_planning_precheck(data_dir)

            self.assertTrue(precheck["first_tick_clean"])
            self.assertFalse(precheck["second_tick_planning_ready"])
            self.assertIn("source_tick_dry_run_audit_present", precheck["missing_items"])

    def test_cli_precheck_show_list_and_report(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.seed_valid_tick_stub(data_dir)
            report_path = data_dir / "report.md"

            precheck_payload = json.loads(self.run_cli(data_dir, "precheck").stdout)
            last_payload = json.loads(self.run_cli(data_dir, "show-last-precheck").stdout)
            list_payload = json.loads(self.run_cli(data_dir, "list-prechecks").stdout)
            report_payload = json.loads(
                self.run_cli(data_dir, "write-report", "--path", str(report_path)).stdout
            )

            self.assertEqual(precheck_payload["precheck_id"], last_payload["precheck_id"])
            self.assertEqual(1, list_payload["two_tick_precheck_count"])
            self.assertEqual(str(report_path), report_payload["path"])
            self.assertTrue(report_path.exists())

    def test_cli_show_missing_precheck_returns_not_found(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_cli(Path(temp_dir), "show-last-precheck", check=False)

            self.assertEqual(1, result.returncode)
            self.assertIn("not_found", result.stdout)

    def test_repo_data_directory_is_not_polluted_during_tests(self):
        self.assertFalse((ROOT / "ashl_core_v1" / "data").exists())


if __name__ == "__main__":
    unittest.main()
