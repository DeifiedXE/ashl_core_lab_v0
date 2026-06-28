import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.runtime.open_cradle_life_design_gate import (
    CURRENT_ALLOWED_CLAIM,
    CURRENT_NOT_YET_CLAIM,
    build_open_cradle_life_design_gate,
    write_open_cradle_life_design_gate_report,
)


ROOT = Path(__file__).resolve().parents[2]
CLI_MODULE = "ashl_core_v1.runtime.open_cradle_life_design_gate_cli"


class OpenCradleLifeDesignGateTests(unittest.TestCase):
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

    def test_gate_builder_returns_required_keys(self):
        gate = build_open_cradle_life_design_gate()

        for key in (
            "gate_id",
            "status",
            "fixed_daily_operation_ready",
            "first_output_followup_ready",
            "daily_teacher_note_ready",
            "memory_promotion_queue_ready",
            "environment_state_model_ready",
            "state_continuity_stress_ready",
            "open_cradle_life_design_ready",
            "open_cradle_life_runtime_ready",
            "ready_items",
            "missing_items",
            "current_allowed_claim",
            "current_not_yet_claim",
            "next_recommended_packages",
            "created_at",
        ):
            self.assertIn(key, gate)

    def test_design_ready_can_be_true_while_runtime_ready_is_false(self):
        gate = build_open_cradle_life_design_gate()

        self.assertTrue(gate["open_cradle_life_design_ready"])
        self.assertFalse(gate["open_cradle_life_runtime_ready"])

    def test_missing_items_include_runtime_gaps(self):
        gate = build_open_cradle_life_design_gate()

        self.assertIn("no_open_ended_event_loop", gate["missing_items"])
        self.assertIn("no_autonomous_environment_ticking", gate["missing_items"])
        self.assertIn("no_Unity_Home_integration", gate["missing_items"])

    def test_claims_are_honest(self):
        gate = build_open_cradle_life_design_gate()

        self.assertEqual(CURRENT_ALLOWED_CLAIM, gate["current_allowed_claim"])
        self.assertEqual(list(CURRENT_NOT_YET_CLAIM), gate["current_not_yet_claim"])
        self.assertIn("This is not open cradle life runtime.", gate["current_not_yet_claim"])

    def test_write_report_creates_markdown(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "gate.md"

            result = write_open_cradle_life_design_gate_report(path, Path(temp_dir))
            text = path.read_text(encoding="utf-8")

            self.assertEqual(str(path), result["path"])
            self.assertIn(CURRENT_ALLOWED_CLAIM, text)
            self.assertIn("This is not open cradle life runtime.", text)
            self.assertIn("Package 31", text)

    def test_cli_check_outputs_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_cli(Path(temp_dir), "check")
            payload = json.loads(result.stdout)

            self.assertFalse(payload["open_cradle_life_runtime_ready"])
            self.assertIn("memory_promotion_queue_ready", payload)

    def test_cli_write_report_outputs_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            report_path = data_dir / "gate.md"
            result = self.run_cli(data_dir, "write-report", "--path", str(report_path))
            payload = json.loads(result.stdout)

            self.assertEqual(str(report_path), payload["path"])
            self.assertTrue(report_path.exists())

    def test_repo_data_directory_is_not_polluted_during_tests(self):
        self.assertFalse((ROOT / "ashl_core_v1" / "data").exists())


if __name__ == "__main__":
    unittest.main()
