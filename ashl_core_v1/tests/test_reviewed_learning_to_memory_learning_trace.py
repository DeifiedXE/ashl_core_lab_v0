from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.lesson.cradle_learning_candidate_review import (
    list_cradle_learning_candidates,
    review_cradle_learning_candidate,
)
from ashl_core_v1.memory.reviewed_learning_to_memory_trace import (
    build_all_approved_reviewed_learning_memory_traces,
    build_memory_trace_from_reviewed_learning,
    list_memory_application_data_records,
    list_memory_learning_trace_records,
)
from ashl_core_v1.runtime.multi_case_closure_candidate_audit import (
    run_multi_case_closure_candidate_audit,
)
from ashl_core_v1.runtime.multi_case_cradle_task_suite import (
    run_all_multi_case_cradle_task_cases,
)


class ReviewedLearningToMemoryLearningTraceTests(unittest.TestCase):
    def test_approved_reviewed_learning_creates_memory_learning_trace(self) -> None:
        with self._approved_temp_dir() as temp_dir:
            bundle = build_memory_trace_from_reviewed_learning(
                self._reviewed_id(temp_dir),
                base_dir=temp_dir,
            )
        self.assertTrue(bundle["memory_trace_created"])
        self.assertIn("memory_learning_trace", bundle)

    def test_approved_reviewed_learning_creates_memory_routing_trace(self) -> None:
        with self._approved_temp_dir() as temp_dir:
            bundle = build_memory_trace_from_reviewed_learning(
                self._reviewed_id(temp_dir),
                base_dir=temp_dir,
            )
        self.assertEqual(
            bundle["memory_routing_trace"]["route_decision"],
            "routed_for_working_memory_readback",
        )

    def test_approved_reviewed_learning_creates_memory_application_data(self) -> None:
        with self._approved_temp_dir() as temp_dir:
            bundle = build_memory_trace_from_reviewed_learning(
                self._reviewed_id(temp_dir),
                base_dir=temp_dir,
            )
        self.assertIn("memory_application_data", bundle)

    def test_source_candidate_id_preserved(self) -> None:
        with self._approved_temp_dir() as temp_dir:
            bundle = build_memory_trace_from_reviewed_learning(
                self._reviewed_id(temp_dir),
                base_dir=temp_dir,
            )
        item = bundle["memory_application_data"]["memory_items"][0]
        self.assertIn("task_learning_candidate:", item["source_candidate_id"])

    def test_source_tick_refs_preserved(self) -> None:
        with self._approved_temp_dir() as temp_dir:
            bundle = build_memory_trace_from_reviewed_learning(
                self._reviewed_id(temp_dir),
                base_dir=temp_dir,
            )
        item = bundle["memory_application_data"]["memory_items"][0]
        self.assertTrue(item["source_tick_refs"])

    def test_source_working_memory_refs_preserved(self) -> None:
        with self._approved_temp_dir() as temp_dir:
            bundle = build_memory_trace_from_reviewed_learning(
                self._reviewed_id(temp_dir),
                base_dir=temp_dir,
            )
        item = bundle["memory_application_data"]["memory_items"][0]
        self.assertTrue(item["source_working_memory_update_refs"])

    def test_target_layer_is_working_in_v0(self) -> None:
        with self._approved_temp_dir() as temp_dir:
            bundle = build_memory_trace_from_reviewed_learning(
                self._reviewed_id(temp_dir),
                base_dir=temp_dir,
            )
        self.assertEqual(bundle["target_layer"], "working")
        self.assertEqual(bundle["memory_routing_trace"]["target_layer"], "working")

    def test_rejected_deferred_and_needs_more_evidence_do_not_create_application_data(self) -> None:
        for status in ("rejected", "deferred", "needs_more_evidence"):
            with self.subTest(status=status), self._reviewed_temp_dir(status) as temp_dir:
                bundle = build_memory_trace_from_reviewed_learning(
                    self._reviewed_id(temp_dir),
                    base_dir=temp_dir,
                )
                self.assertFalse(bundle["memory_application_data_created"])
                self.assertEqual(bundle["routing_status"], "held_for_review")

    def test_build_all_approved_works(self) -> None:
        with self._approved_temp_dir() as temp_dir:
            payload = build_all_approved_reviewed_learning_memory_traces(temp_dir)
        self.assertEqual(payload["approved_reviewed_count"], 1)
        self.assertTrue(payload["memory_trace_bundles"])

    def test_show_memory_traces_and_application_data_work(self) -> None:
        with self._approved_temp_dir() as temp_dir:
            build_all_approved_reviewed_learning_memory_traces(temp_dir)
            traces = list_memory_learning_trace_records(temp_dir)
            app_data = list_memory_application_data_records(temp_dir)
        self.assertEqual(len(traces), 1)
        self.assertEqual(len(app_data), 1)

    def test_no_core_long_term_archive_anchor_write(self) -> None:
        with self._approved_temp_dir() as temp_dir:
            bundle = build_memory_trace_from_reviewed_learning(
                self._reviewed_id(temp_dir),
                base_dir=temp_dir,
            )
        self.assertFalse(bundle["core_memory_write"])
        self.assertFalse(bundle["long_term_memory_write"])
        self.assertFalse(bundle["archive_memory_write"])
        self.assertFalse(bundle["anchor_layer_write"])
        self.assertFalse(bundle["direct_memory_promotion"])

    def test_no_action_selection_or_scheduler(self) -> None:
        with self._approved_temp_dir() as temp_dir:
            bundle = build_memory_trace_from_reviewed_learning(
                self._reviewed_id(temp_dir),
                base_dir=temp_dir,
            )
        self.assertFalse(bundle["action_selection"])
        self.assertFalse(bundle["scheduler_created"])

    def test_cli_commands_work(self) -> None:
        with self._approved_temp_dir() as temp_dir:
            reviewed_id = self._reviewed_id(temp_dir)
            build_result = self._run_cli(temp_dir, "build-trace", "--reviewed-id", reviewed_id)
            self.assertEqual(build_result.returncode, 0, build_result.stderr)
            all_result = self._run_cli(temp_dir, "build-all-approved")
            self.assertEqual(all_result.returncode, 0, all_result.stderr)
            traces_result = self._run_cli(temp_dir, "show-memory-traces")
            self.assertEqual(traces_result.returncode, 0, traces_result.stderr)
            app_result = self._run_cli(temp_dir, "show-memory-application-data")
            self.assertEqual(app_result.returncode, 0, app_result.stderr)

    def test_no_repo_data_pollution(self) -> None:
        with self._approved_temp_dir() as temp_dir:
            build_all_approved_reviewed_learning_memory_traces(temp_dir)
            self.assertTrue(Path(temp_dir).exists())
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _approved_temp_dir(self) -> tempfile.TemporaryDirectory:
        return self._reviewed_temp_dir("approved")

    def _reviewed_temp_dir(self, status: str) -> tempfile.TemporaryDirectory:
        temp_dir = tempfile.TemporaryDirectory()
        run_all_multi_case_cradle_task_cases(base_dir=temp_dir.name)
        run_multi_case_closure_candidate_audit(temp_dir.name)
        candidate_id = list_cradle_learning_candidates(temp_dir.name)[0]["candidate_id"]
        review_cradle_learning_candidate(
            candidate_id=candidate_id,
            status=status,
            note=f"{status} note",
            base_dir=temp_dir.name,
        )
        return temp_dir

    def _reviewed_id(self, temp_dir: str) -> str:
        from ashl_core_v1.lesson.cradle_learning_candidate_review import (
            list_cradle_reviewed_learning_records,
        )

        return list_cradle_reviewed_learning_records(temp_dir)[0][
            "cradle_reviewed_learning_record_id"
        ]

    def _run_cli(self, temp_dir: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core_v1.memory.reviewed_learning_to_memory_trace_cli",
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
