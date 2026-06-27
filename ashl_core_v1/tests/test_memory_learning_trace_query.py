import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.memory.trace_store import (
    list_influence_traces,
    list_memory_application_data,
    list_memory_learning_traces,
    list_memory_routing_traces,
    list_thought_read_traces,
    seed_blocked_sample_trace,
)


ROOT = Path(__file__).resolve().parents[2]
CLI_MODULE = "ashl_core_v1.memory.trace_cli"


class MemoryLearningTraceQueryTests(unittest.TestCase):
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

    def test_seed_blocked_sample_trace_creates_memory_learning_trace_records(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)

            result = self.run_cli(data_dir, "seed-blocked-sample-trace")

            self.assertIn("seeded memory_learning_trace_id=memory_learning_front_obstacle_001", result.stdout)
            self.assertEqual(1, len(list_memory_learning_traces(data_dir)))
            self.assertEqual(1, len(list_memory_routing_traces(data_dir)))
            self.assertEqual(1, len(list_memory_application_data(data_dir)))
            self.assertEqual(1, len(list_thought_read_traces(data_dir)))
            self.assertEqual(1, len(list_influence_traces(data_dir)))

    def test_show_learning_trace_can_find_trace_by_id(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            seed_blocked_sample_trace(data_dir)

            result = self.run_cli(
                data_dir,
                "show-learning-trace",
                "--trace-id",
                "memory_learning_front_obstacle_001",
            )

            self.assertIn("memory_learning_trace_id=memory_learning_front_obstacle_001", result.stdout)
            self.assertIn("source_review_record_id=learning_review_front_obstacle_approved_001", result.stdout)
            self.assertIn("routing_status=routed", result.stdout)

    def test_show_by_reviewed_digest_can_find_trace(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            seed_blocked_sample_trace(data_dir)

            result = self.run_cli(
                data_dir,
                "show-by-reviewed-digest",
                "--reviewed-digest-id",
                "reviewed_learning_front_obstacle_001",
            )

            self.assertIn("memory_learning_trace_id=memory_learning_front_obstacle_001", result.stdout)
            self.assertIn("source_reviewed_digest_id=reviewed_learning_front_obstacle_001", result.stdout)

    def test_show_readback_can_show_thought_read_trace(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            seed_blocked_sample_trace(data_dir)

            result = self.run_cli(
                data_dir,
                "show-readback",
                "--memory-application-data-id",
                "memory_application_front_obstacle_001",
            )

            self.assertIn("thought_read_trace_id=thought_read_front_obstacle_001", result.stdout)
            self.assertIn("source_memory_application_data_refs=memory_application_front_obstacle_001", result.stdout)

    def test_show_influence_can_show_influence_trace(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            seed_blocked_sample_trace(data_dir)

            result = self.run_cli(
                data_dir,
                "show-influence",
                "--thought-read-trace-id",
                "thought_read_front_obstacle_001",
            )

            self.assertIn("influence_trace_id=influence_front_obstacle_001", result.stdout)
            self.assertIn("influence_visible=true", result.stdout)
            self.assertIn("affected_signal_ref=thought_signal_observe_or_adjust_001", result.stdout)

    def test_query_output_includes_source_review_record_id(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            seed_blocked_sample_trace(data_dir)

            result = self.run_cli(
                data_dir,
                "show-learning-trace",
                "--trace-id",
                "memory_learning_front_obstacle_001",
            )

            self.assertIn("source_review_record_id=learning_review_front_obstacle_approved_001", result.stdout)

    def test_query_output_includes_routing_status(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            seed_blocked_sample_trace(data_dir)

            result = self.run_cli(
                data_dir,
                "show-learning-trace",
                "--trace-id",
                "memory_learning_front_obstacle_001",
            )

            self.assertIn("routing_status=routed", result.stdout)
            self.assertIn("memory_layer_target=working", result.stdout)

    def test_query_output_includes_influence_visible(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            seed_blocked_sample_trace(data_dir)

            result = self.run_cli(
                data_dir,
                "show-influence",
                "--thought-read-trace-id",
                "thought_read_front_obstacle_001",
            )

            self.assertIn("influence_visible=true", result.stdout)

    def test_missing_id_returns_readable_not_found_result(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            seed_blocked_sample_trace(data_dir)

            result = self.run_cli(
                data_dir,
                "show-learning-trace",
                "--trace-id",
                "missing",
                check=False,
            )

            self.assertEqual(1, result.returncode)
            self.assertIn("not_found memory_learning_trace_id=missing", result.stdout)


if __name__ == "__main__":
    unittest.main()
