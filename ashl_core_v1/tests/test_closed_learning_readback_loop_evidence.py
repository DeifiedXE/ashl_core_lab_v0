from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.runtime.closed_learning_readback_loop_evidence import (
    build_closed_learning_readback_loop_evidence_from_existing,
    build_closed_learning_readback_loop_evidence_record,
    list_closed_learning_readback_loop_evidence,
    load_last_closed_learning_readback_loop_evidence,
    run_closed_learning_readback_loop_evidence_demo,
)
from ashl_core_v1.runtime.cradle_task_teacher_console import (
    show_growth_loop_evidence_from_teacher_console,
)


class ClosedLearningReadbackLoopEvidenceTests(unittest.TestCase):
    def test_valid_complete_loop_evidence_passes(self) -> None:
        record = build_closed_learning_readback_loop_evidence_record(**self._sources())
        self.assertEqual(record["loop_status"], "closed_loop_evidence_visible")
        self.assertTrue(record["readback_influence_visible"])

    def test_missing_initial_run_blocks(self) -> None:
        sources = self._sources()
        sources["initial_run"] = None
        record = build_closed_learning_readback_loop_evidence_record(**sources)
        self.assertEqual(record["loop_status"], "blocked_missing_initial_run")

    def test_missing_candidate_blocks(self) -> None:
        sources = self._sources()
        sources["learning_candidate"] = None
        record = build_closed_learning_readback_loop_evidence_record(**sources)
        self.assertEqual(record["loop_status"], "blocked_missing_candidate")

    def test_missing_teacher_review_blocks(self) -> None:
        sources = self._sources()
        sources["review_decision"] = None
        record = build_closed_learning_readback_loop_evidence_record(**sources)
        self.assertEqual(record["loop_status"], "blocked_missing_teacher_review")

    def test_review_not_approved_blocks(self) -> None:
        sources = self._sources()
        sources["review_decision"] = {
            **sources["review_decision"],
            "review_status": "rejected",
        }
        record = build_closed_learning_readback_loop_evidence_record(**sources)
        self.assertEqual(record["loop_status"], "blocked_review_not_approved")

    def test_missing_memory_trace_blocks(self) -> None:
        sources = self._sources()
        sources["memory_learning_trace"] = None
        record = build_closed_learning_readback_loop_evidence_record(**sources)
        self.assertEqual(record["loop_status"], "blocked_missing_memory_trace")

    def test_missing_readback_preview_blocks(self) -> None:
        sources = self._sources()
        sources["readback_preview"] = None
        record = build_closed_learning_readback_loop_evidence_record(**sources)
        self.assertEqual(record["loop_status"], "blocked_missing_readback_preview")

    def test_missing_readback_application_blocks(self) -> None:
        sources = self._sources()
        sources["readback_application"] = None
        record = build_closed_learning_readback_loop_evidence_record(**sources)
        self.assertEqual(record["loop_status"], "blocked_missing_readback_application")

    def test_missing_contrast_blocks(self) -> None:
        sources = self._sources()
        sources["contrast"] = None
        record = build_closed_learning_readback_loop_evidence_record(**sources)
        self.assertEqual(record["loop_status"], "blocked_missing_contrast")

    def test_readback_influence_not_visible_blocks(self) -> None:
        sources = self._sources()
        sources["contrast"] = {
            **sources["contrast"],
            "task_processing_difference_visible": False,
        }
        record = build_closed_learning_readback_loop_evidence_record(**sources)
        self.assertEqual(
            record["loop_status"],
            "blocked_readback_influence_not_visible",
        )

    def test_loop_evidence_preserves_all_source_ids(self) -> None:
        record = build_closed_learning_readback_loop_evidence_record(**self._sources())
        self.assertEqual(record["source_initial_run_id"], "run:blocked")
        self.assertEqual(record["source_learning_candidate_id"], "candidate:blocked")
        self.assertEqual(record["source_reviewed_learning_id"], "reviewed:blocked")
        self.assertEqual(record["source_memory_application_data_id"], "memory_app:blocked")
        self.assertEqual(record["source_contrast_id"], "contrast:blocked")

    def test_demo_loop_evidence_works(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = run_closed_learning_readback_loop_evidence_demo(temp_dir)
        evidence = payload["closed_learning_readback_loop_evidence"]
        self.assertEqual(evidence["loop_status"], "closed_loop_evidence_visible")
        self.assertTrue(payload["fixture_approval_used"])

    def test_build_from_existing_works_with_temp_records(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_closed_learning_readback_loop_evidence_demo(temp_dir)
            evidence = build_closed_learning_readback_loop_evidence_from_existing(
                temp_dir
            )
            loaded = load_last_closed_learning_readback_loop_evidence(temp_dir)
            listed = list_closed_learning_readback_loop_evidence(temp_dir)
        self.assertEqual(evidence["loop_status"], "closed_loop_evidence_visible")
        self.assertEqual(loaded["loop_evidence_id"], evidence["loop_evidence_id"])
        self.assertGreaterEqual(len(listed), 2)

    def test_teacher_console_show_growth_loop_evidence_works(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_closed_learning_readback_loop_evidence_demo(temp_dir)
            payload = show_growth_loop_evidence_from_teacher_console(temp_dir)
        self.assertEqual(payload["loop_status"], "closed_loop_evidence_visible")

    def test_cli_run_demo_and_show_work(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            demo = self._run_cli(temp_dir, "run-demo")
            self.assertEqual(demo.returncode, 0, demo.stderr)
            show = self._run_cli(temp_dir, "show-last-loop-evidence")
            self.assertEqual(show.returncode, 0, show.stderr)
            listing = self._run_cli(temp_dir, "list-loop-evidence")
            self.assertEqual(listing.returncode, 0, listing.stderr)

    def test_no_forbidden_runtime_flags_or_repo_pollution(self) -> None:
        record = build_closed_learning_readback_loop_evidence_record(**self._sources())
        self.assertFalse(record["automatic_approval"])
        self.assertFalse(record["memory_layer_promotion_used"])
        self.assertFalse(record["free_action_selection_used"])
        self.assertFalse(record["action_execution_used"])
        self.assertFalse(record["scheduler_used"])
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _sources(self) -> dict:
        return {
            "initial_run": {
                "bounded_task_tick_run_record": {
                    "run_id": "run:blocked",
                    "task_id": "task:blocked",
                    "case_id": "blocked_front_obstacle",
                }
            },
            "task_closure": {
                "task_run_closure_record": {
                    "task_run_closure_record_id": "closure:blocked"
                }
            },
            "learning_candidate": {
                "candidate_id": "candidate:blocked",
                "task_id": "task:blocked",
                "case_id": "blocked_front_obstacle",
            },
            "review_decision": {
                "cradle_candidate_review_decision_id": "review:blocked",
                "review_status": "approved",
            },
            "reviewed_learning": {
                "cradle_reviewed_learning_record_id": "reviewed:blocked",
                "review_status": "approved",
            },
            "memory_learning_trace": {
                "memory_learning_trace_id": "memory_trace:blocked"
            },
            "memory_routing_trace": {
                "memory_routing_trace_id": "memory_route:blocked"
            },
            "memory_application_data": {
                "memory_application_data_id": "memory_app:blocked"
            },
            "readback_preview": {"readback_preview_id": "preview:blocked"},
            "readback_application": {
                "task_working_memory_readback_application_record": {
                    "readback_application_id": "application:blocked",
                    "working_memory_updated": True,
                }
            },
            "contrast": {
                "contrast_id": "contrast:blocked",
                "contrast_status": "passed",
                "task_processing_difference_visible": True,
            },
        }

    def _run_cli(self, temp_dir: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core_v1.runtime.closed_learning_readback_loop_evidence_cli",
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
