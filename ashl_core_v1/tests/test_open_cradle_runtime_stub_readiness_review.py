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
    CURRENT_ALLOWED_CLAIM,
    NEXT_PATCH_PACKAGE,
    NEXT_READY_PACKAGE,
    build_open_cradle_runtime_stub_readiness_review,
    collect_runtime_stub_readiness_sources,
    evaluate_runtime_stub_readiness,
    list_open_cradle_runtime_stub_readiness_reviews,
    load_last_open_cradle_runtime_stub_readiness_review,
    save_open_cradle_runtime_stub_readiness_review,
    write_open_cradle_runtime_stub_readiness_report,
)
from ashl_core_v1.runtime.open_cradle_tick_context import (
    build_open_cradle_tick_context,
    save_open_cradle_tick_context,
)
from ashl_core_v1.runtime.open_cradle_tick_dry_run import (
    build_teacher_gate_for_tick_context,
    build_tick_dry_run_record,
    run_teacher_gated_tick_dry_run,
    save_tick_dry_run,
)
from ashl_core_v1.runtime.open_cradle_tick_dry_run_audit import (
    build_tick_dry_run_audit,
    save_tick_dry_run_audit,
)


ROOT = Path(__file__).resolve().parents[2]
CLI_MODULE = "ashl_core_v1.runtime.open_cradle_runtime_stub_readiness_cli"


class OpenCradleRuntimeStubReadinessReviewTests(unittest.TestCase):
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

    def seed_active_context(self, data_dir: Path) -> dict:
        start_cradle_session(data_dir)
        run_case_in_cradle_session("success_front_step", data_dir)
        save_cradle_environment_state(
            build_cradle_environment_state_from_last_session(data_dir),
            data_dir,
        )
        return save_open_cradle_tick_context(build_open_cradle_tick_context(data_dir), data_dir)

    def seed_passing_readiness_sources(self, data_dir: Path) -> dict:
        self.seed_active_context(data_dir)
        return run_teacher_gated_tick_dry_run(data_dir)

    def test_review_returns_dict_with_required_top_level_keys(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            review = build_open_cradle_runtime_stub_readiness_review(Path(temp_dir))

            for key in (
                "review_id",
                "status",
                "source_tick_context_id",
                "source_tick_dry_run_id",
                "source_tick_dry_run_audit_id",
                "tick_context_ready",
                "teacher_gate_ready",
                "dry_run_ready",
                "dry_run_audit_passed",
                "blocked_surfaces_preserved",
                "supported_tick_modes",
                "teacher_gated_modes",
                "runtime_stub_design_ready",
                "runtime_stub_implementation_ready",
                "minimal_stub_scope",
                "required_teacher_gates",
                "still_blocked_surfaces",
                "missing_items",
                "current_allowed_claim",
                "current_not_yet_claim",
                "next_recommended_package",
                "created_at",
                "trace_refs",
            ):
                self.assertIn(key, review)

    def test_missing_tick_context_makes_tick_context_ready_false(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            review = build_open_cradle_runtime_stub_readiness_review(Path(temp_dir))

            self.assertFalse(review["tick_context_ready"])
            self.assertIn("tick_context_ready", review["missing_items"])

    def test_missing_dry_run_makes_dry_run_ready_false(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.seed_active_context(data_dir)

            review = build_open_cradle_runtime_stub_readiness_review(data_dir)

            self.assertFalse(review["dry_run_ready"])
            self.assertFalse(review["teacher_gate_ready"])
            self.assertIn("dry_run_ready", review["missing_items"])

    def test_missing_audit_makes_dry_run_audit_passed_false(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            context = self.seed_active_context(data_dir)
            gate = build_teacher_gate_for_tick_context(context)
            save_tick_dry_run(build_tick_dry_run_record(context, gate), data_dir)

            review = build_open_cradle_runtime_stub_readiness_review(data_dir)

            self.assertFalse(review["dry_run_audit_passed"])
            self.assertIn("dry_run_audit_passed", review["missing_items"])

    def test_valid_sources_make_runtime_stub_design_ready_true(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.seed_passing_readiness_sources(data_dir)

            review = build_open_cradle_runtime_stub_readiness_review(data_dir)

            self.assertTrue(review["tick_context_ready"])
            self.assertTrue(review["teacher_gate_ready"])
            self.assertTrue(review["dry_run_ready"])
            self.assertTrue(review["dry_run_audit_passed"])
            self.assertTrue(review["blocked_surfaces_preserved"])
            self.assertTrue(review["runtime_stub_design_ready"])
            self.assertTrue(review["runtime_stub_implementation_ready"])

    def test_blocked_dry_run_gate_makes_teacher_gate_ready_false(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            context = self.seed_active_context(data_dir)
            broken_context = copy.deepcopy(context)
            broken_context["blocked_next_surfaces"] = []
            gate = build_teacher_gate_for_tick_context(broken_context)
            dry_run = build_tick_dry_run_record(broken_context, gate)
            save_tick_dry_run(dry_run, data_dir)
            save_tick_dry_run_audit(build_tick_dry_run_audit(dry_run, gate, broken_context), data_dir)

            review = build_open_cradle_runtime_stub_readiness_review(data_dir)

            self.assertFalse(review["teacher_gate_ready"])
            self.assertFalse(review["runtime_stub_design_ready"])

    def test_failed_audit_makes_runtime_stub_design_ready_false(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.seed_passing_readiness_sources(data_dir)
            sources = collect_runtime_stub_readiness_sources(data_dir)
            bad_audit = copy.deepcopy(sources["tick_dry_run_audit"])
            bad_audit["audit_passed"] = False
            bad_audit["no_action_execution"] = False
            save_tick_dry_run_audit(bad_audit, data_dir)

            review = build_open_cradle_runtime_stub_readiness_review(data_dir)

            self.assertFalse(review["dry_run_audit_passed"])
            self.assertFalse(review["runtime_stub_design_ready"])

    def test_blocked_surfaces_preserved_false_blocks_design_ready(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.seed_passing_readiness_sources(data_dir)
            sources = collect_runtime_stub_readiness_sources(data_dir)
            broken_context = copy.deepcopy(sources["tick_context"])
            broken_context["blocked_next_surfaces"] = ["automatic_tick_execution"]
            save_open_cradle_tick_context(broken_context, data_dir)

            review = build_open_cradle_runtime_stub_readiness_review(data_dir)

            self.assertFalse(review["blocked_surfaces_preserved"])
            self.assertFalse(review["runtime_stub_design_ready"])

    def test_still_blocked_surfaces_include_required_surfaces(self):
        review = build_open_cradle_runtime_stub_readiness_review()

        self.assertIn("automatic_tick_execution", review["still_blocked_surfaces"])
        self.assertIn("action_execution", review["still_blocked_surfaces"])
        self.assertIn("long_term_memory_write", review["still_blocked_surfaces"])

    def test_minimal_stub_scope_exists_when_design_ready(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.seed_passing_readiness_sources(data_dir)

            review = build_open_cradle_runtime_stub_readiness_review(data_dir)

            self.assertIn("one_teacher_gated_tick_stub", review["minimal_stub_scope"])
            self.assertIn("stops_after_one_record", review["minimal_stub_scope"])

    def test_next_recommended_package_points_to_one_tick_stub_when_ready(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.seed_passing_readiness_sources(data_dir)

            review = build_open_cradle_runtime_stub_readiness_review(data_dir)

            self.assertEqual(NEXT_READY_PACKAGE, review["next_recommended_package"])

    def test_next_recommended_package_points_to_patch_when_not_ready(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            review = build_open_cradle_runtime_stub_readiness_review(Path(temp_dir))

            self.assertEqual(NEXT_PATCH_PACKAGE, review["next_recommended_package"])

    def test_save_load_last_review_round_trip_and_list_reviews(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            review = build_open_cradle_runtime_stub_readiness_review(data_dir)

            saved = save_open_cradle_runtime_stub_readiness_review(review, data_dir)

            self.assertEqual(saved, load_last_open_cradle_runtime_stub_readiness_review(data_dir))
            self.assertEqual(
                1,
                list_open_cradle_runtime_stub_readiness_reviews(data_dir)[
                    "runtime_stub_readiness_review_count"
                ],
            )

    def test_write_report_creates_markdown(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            path = data_dir / "readiness.md"

            result = write_open_cradle_runtime_stub_readiness_report(path, data_dir)
            text = path.read_text(encoding="utf-8")

            self.assertEqual(str(path), result["path"])
            self.assertIn(CURRENT_ALLOWED_CLAIM, text)
            self.assertIn("This is not open cradle runtime.", text)

    def test_evaluate_sources_helper_reports_missing_items(self):
        readiness = evaluate_runtime_stub_readiness(
            {
                "tick_context": None,
                "tick_dry_run": None,
                "tick_dry_run_audit": None,
                "teacher_gate_status": None,
            }
        )

        self.assertFalse(readiness["runtime_stub_design_ready"])
        self.assertIn("tick_context_ready", readiness["missing_items"])

    def test_cli_review_show_list_and_report(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.seed_passing_readiness_sources(data_dir)
            report_path = data_dir / "report.md"

            review_payload = json.loads(self.run_cli(data_dir, "review").stdout)
            last_payload = json.loads(self.run_cli(data_dir, "show-last-review").stdout)
            list_payload = json.loads(self.run_cli(data_dir, "list-reviews").stdout)
            report_payload = json.loads(
                self.run_cli(data_dir, "write-report", "--path", str(report_path)).stdout
            )

            self.assertEqual(review_payload["review_id"], last_payload["review_id"])
            self.assertEqual(1, list_payload["runtime_stub_readiness_review_count"])
            self.assertEqual(str(report_path), report_payload["path"])
            self.assertTrue(report_path.exists())

    def test_cli_show_missing_review_returns_not_found(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_cli(Path(temp_dir), "show-last-review", check=False)

            self.assertEqual(1, result.returncode)
            self.assertIn("not_found", result.stdout)

    def test_repo_data_directory_is_not_polluted_during_tests(self):
        self.assertFalse((ROOT / "ashl_core_v1" / "data").exists())


if __name__ == "__main__":
    unittest.main()
