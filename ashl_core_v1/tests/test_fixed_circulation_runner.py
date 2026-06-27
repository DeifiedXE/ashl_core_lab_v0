import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.runtime.fixed_circulation_runner import run_blocked_cycle, show_last_cycle


ROOT = Path(__file__).resolve().parents[2]
CLI_MODULE = "ashl_core_v1.runtime.runner_cli"


class FixedCirculationRunnerTests(unittest.TestCase):
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

    def test_run_blocked_cycle_creates_complete_cycle_summary(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            cycle = run_blocked_cycle(Path(temp_dir))

            self.assertEqual("fixed_blocked_cycle_001", cycle["cycle_id"])
            self.assertEqual("blocked_front_obstacle", cycle["case_id"])
            self.assertTrue(cycle["summary"]["influence_visible"])
            self.assertEqual("observe_or_adjust", cycle["summary"]["body_action_signal_type"])
            self.assertEqual("next_observation", cycle["summary"]["next_expected_feedback_kind"])

    def test_all_required_ids_exist(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            cycle = run_blocked_cycle(Path(temp_dir))
            records = cycle["records"]

            for key in (
                "perception_id",
                "endocrine_signal_id",
                "learning_digest_id",
                "review_record_id",
                "reviewed_digest_id",
                "memory_learning_trace_id",
                "memory_routing_trace_id",
                "memory_application_data_id",
                "thought_read_trace_id",
                "influence_trace_id",
                "thought_signal_id",
                "body_action_signal_id",
            ):
                with self.subTest(key=key):
                    self.assertIn(key, records)
                    self.assertTrue(records[key])

    def test_learning_digest_appears_before_learning_review_record(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            order = run_blocked_cycle(Path(temp_dir))["record_order"]

            self.assertLess(order.index("learning_digest"), order.index("learning_review_record"))

    def test_learning_review_record_appears_before_reviewed_learning_digest(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            order = run_blocked_cycle(Path(temp_dir))["record_order"]

            self.assertLess(order.index("learning_review_record"), order.index("reviewed_learning_digest"))

    def test_reviewed_learning_digest_appears_before_memory_learning_trace(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            order = run_blocked_cycle(Path(temp_dir))["record_order"]

            self.assertLess(order.index("reviewed_learning_digest"), order.index("memory_learning_trace"))

    def test_memory_application_data_appears_before_thought_read_trace(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            order = run_blocked_cycle(Path(temp_dir))["record_order"]

            self.assertLess(order.index("memory_application_data"), order.index("thought_read_trace"))

    def test_thought_read_trace_appears_before_influence_trace(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            order = run_blocked_cycle(Path(temp_dir))["record_order"]

            self.assertLess(order.index("thought_read_trace"), order.index("influence_trace"))

    def test_thought_signal_appears_before_body_action_signal(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            order = run_blocked_cycle(Path(temp_dir))["record_order"]

            self.assertLess(order.index("thought_signal"), order.index("body_action_signal"))

    def test_body_action_signal_type_is_observe_or_adjust(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            cycle = run_blocked_cycle(Path(temp_dir))

            self.assertEqual("observe_or_adjust", cycle["summary"]["body_action_signal_type"])

    def test_influence_visible_is_true(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            cycle = run_blocked_cycle(Path(temp_dir))

            self.assertTrue(cycle["summary"]["influence_visible"])

    def test_show_last_cycle_returns_last_cycle_summary(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            cycle = run_blocked_cycle(data_dir)
            last = show_last_cycle(data_dir)

            self.assertEqual(cycle, last)

    def test_runner_output_is_repeatable_for_fixed_case(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            first = run_blocked_cycle(data_dir)
            second = run_blocked_cycle(data_dir)

            self.assertEqual(first, second)

    def test_runner_cli_run_blocked_cycle_outputs_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)

            result = self.run_cli(data_dir, "run-blocked-cycle")
            cycle = json.loads(result.stdout)

            self.assertEqual("blocked_front_obstacle", cycle["case_id"])
            self.assertEqual("observe_or_adjust", cycle["summary"]["body_action_signal_type"])

    def test_runner_cli_show_last_cycle_returns_last_cycle(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.run_cli(data_dir, "run-blocked-cycle")

            result = self.run_cli(data_dir, "show-last-cycle")
            cycle = json.loads(result.stdout)

            self.assertEqual("fixed_blocked_cycle_001", cycle["cycle_id"])
            self.assertTrue(cycle["summary"]["influence_visible"])

    def test_show_last_cycle_without_prior_run_returns_not_found(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.run_cli(Path(temp_dir), "show-last-cycle", check=False)

            self.assertEqual(1, result.returncode)
            self.assertIn("not_found last_blocked_cycle", result.stdout)


if __name__ == "__main__":
    unittest.main()
