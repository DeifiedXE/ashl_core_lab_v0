import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.runtime.open_cradle_event_loop_design_gate import (
    CURRENT_ALLOWED_CLAIM,
    CURRENT_NOT_YET_CLAIM,
    build_caregiver_intervention_plan,
    build_environment_tick_plan,
    build_event_loop_plan,
    build_memory_promotion_review_plan,
    build_open_cradle_event_loop_design_gate,
    build_runtime_boundary_review,
    write_open_cradle_event_loop_design_gate_report,
)


ROOT = Path(__file__).resolve().parents[2]
CLI_MODULE = "ashl_core_v1.runtime.open_cradle_event_loop_design_gate_cli"


class OpenCradleEventLoopCombinedDesignGateTests(unittest.TestCase):
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

    def test_builder_returns_required_top_level_keys(self):
        gate = build_open_cradle_event_loop_design_gate()

        for key in (
            "gate_id",
            "status",
            "event_loop_design_defined",
            "environment_tick_plan_defined",
            "caregiver_intervention_plan_defined",
            "memory_promotion_review_plan_defined",
            "runtime_boundary_review_defined",
            "open_cradle_runtime_design_ready",
            "open_cradle_runtime_implementation_ready",
            "event_loop_plan",
            "environment_tick_plan",
            "caregiver_intervention_plan",
            "memory_promotion_review_plan",
            "runtime_boundary_review",
            "ready_items",
            "missing_items",
            "current_allowed_claim",
            "current_not_yet_claim",
            "next_recommended_packages",
            "created_at",
        ):
            self.assertIn(key, gate)

    def test_event_loop_plan_exists_with_expected_modes(self):
        plan = build_event_loop_plan()
        modes = {mode["mode"]: mode for mode in plan["tick_modes"]}

        self.assertIn("load_session_state", plan["loop_steps"])
        self.assertIn("observe_only", modes)
        self.assertEqual("one_tick_only", modes["observe_only"]["stop_condition"])
        self.assertFalse(modes["observe_only"]["requires_teacher"])
        self.assertIn("promotion_review_pending", modes)
        self.assertIn("stop", modes)
        self.assertFalse(plan["runtime_created"])

    def test_environment_tick_plan_defines_inputs_outputs_and_forbidden_outputs(self):
        plan = build_environment_tick_plan()

        self.assertIn("last_cradle_environment_state", plan["read_sources"])
        self.assertIn("memory_promotion_queue", plan["read_sources"])
        self.assertIn("tick_context", plan["outputs"])
        self.assertIn("new_runtime_action", plan["forbidden_outputs"])
        self.assertFalse(plan["tick_executes_environment_action"])
        self.assertFalse(plan["tick_promotes_memory"])

    def test_caregiver_intervention_plan_defines_conditions(self):
        plan = build_caregiver_intervention_plan()
        conditions = {item["condition"] for item in plan["conditions"]}

        self.assertIn("memory_promotion_candidate_present", conditions)
        self.assertIn("unknown_feedback", conditions)
        self.assertIn("backup_missing_after_daily_run", conditions)
        self.assertTrue(plan["teacher_gate_required_for_runtime_escalation"])

    def test_memory_promotion_review_plan_blocks_memory_write(self):
        plan = build_memory_promotion_review_plan()

        self.assertIn("queued", plan["review_statuses"])
        self.assertIn("teacher_marked_interesting", plan["review_statuses"])
        self.assertIn(
            "promotion_queue_candidate_is_not_memory",
            plan["review_principles"],
        )
        self.assertFalse(plan["long_term_memory_write_created"])
        self.assertFalse(plan["runtime_influence_created"])

    def test_runtime_boundary_review_lists_missing_runtime_prerequisites(self):
        review = build_runtime_boundary_review()

        self.assertFalse(review["runtime_implementation_ready"])
        self.assertIn(
            "no_automatic_environment_scheduler",
            review["missing_runtime_prerequisites"],
        )
        self.assertIn("no_free_action_policy", review["missing_runtime_prerequisites"])
        self.assertFalse(review["automatic_tick_created"])

    def test_design_ready_can_be_true_while_implementation_ready_is_false(self):
        gate = build_open_cradle_event_loop_design_gate()

        self.assertTrue(gate["open_cradle_runtime_design_ready"])
        self.assertFalse(gate["open_cradle_runtime_implementation_ready"])
        self.assertTrue(gate["event_loop_design_defined"])
        self.assertTrue(gate["runtime_boundary_review_defined"])

    def test_missing_items_include_runtime_boundary_gaps(self):
        gate = build_open_cradle_event_loop_design_gate()

        self.assertIn("no_automatic_environment_scheduler", gate["missing_items"])
        self.assertIn("no_autonomous_tick_executor", gate["missing_items"])
        self.assertIn("no_Unity_Home_integration", gate["missing_items"])

    def test_claims_are_honest(self):
        gate = build_open_cradle_event_loop_design_gate()

        self.assertEqual(CURRENT_ALLOWED_CLAIM, gate["current_allowed_claim"])
        self.assertEqual(list(CURRENT_NOT_YET_CLAIM), gate["current_not_yet_claim"])
        self.assertIn("This is not open cradle runtime.", gate["current_not_yet_claim"])

    def test_write_report_creates_markdown_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "event_loop_gate.md"

            result = write_open_cradle_event_loop_design_gate_report(path, Path(temp_dir))
            text = path.read_text(encoding="utf-8")

            self.assertEqual(str(path), result["path"])
            self.assertIn(CURRENT_ALLOWED_CLAIM, text)
            self.assertIn("This is not open cradle runtime.", text)
            self.assertIn("Package 32", text)

    def test_cli_check_outputs_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_cli(Path(temp_dir), "check")
            payload = json.loads(result.stdout)

            self.assertTrue(payload["open_cradle_runtime_design_ready"])
            self.assertFalse(payload["open_cradle_runtime_implementation_ready"])
            self.assertIn("event_loop_plan", payload)

    def test_cli_write_report_outputs_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            report_path = data_dir / "event_loop_gate.md"

            result = self.run_cli(data_dir, "write-report", "--path", str(report_path))
            payload = json.loads(result.stdout)

            self.assertEqual(str(report_path), payload["path"])
            self.assertTrue(report_path.exists())

    def test_repo_data_directory_is_not_polluted_during_tests(self):
        self.assertFalse((ROOT / "ashl_core_v1" / "data").exists())


if __name__ == "__main__":
    unittest.main()
