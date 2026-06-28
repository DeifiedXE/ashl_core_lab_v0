from __future__ import annotations

import copy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.runtime.multi_case_closure_candidate_audit import (
    build_multi_case_closure_candidate_audit,
    list_multi_case_closure_candidate_audits,
    load_last_multi_case_closure_candidate_audit,
    run_multi_case_closure_candidate_audit,
)
from ashl_core_v1.runtime.multi_case_cradle_task_suite import (
    run_all_multi_case_cradle_task_cases,
)


class MultiCaseClosureCandidateAuditTests(unittest.TestCase):
    def test_valid_suite_audit_passes(self) -> None:
        audit = build_multi_case_closure_candidate_audit(self._valid_suite())
        self.assertEqual(audit["audit_status"], "passed")
        self.assertEqual(audit["case_count"], 6)

    def test_missing_suite_run_blocks(self) -> None:
        audit = build_multi_case_closure_candidate_audit(None)
        self.assertEqual(audit["audit_status"], "blocked_missing_suite_run")

    def test_missing_closure_blocks(self) -> None:
        suite = self._valid_suite()
        suite["case_runs"][0].pop("task_run_closure")
        audit = build_multi_case_closure_candidate_audit(suite)
        self.assertEqual(audit["audit_status"], "blocked_missing_case_closure")

    def test_missing_disposition_blocks(self) -> None:
        suite = self._valid_suite()
        suite["case_runs"][0]["task_run_closure"].pop("task_run_disposition_record")
        audit = build_multi_case_closure_candidate_audit(suite)
        self.assertEqual(audit["audit_status"], "blocked_missing_disposition")

    def test_missing_candidate_blocks(self) -> None:
        suite = self._valid_suite()
        suite["case_runs"][0]["task_run_closure"][
            "task_learning_digest_candidate_records"
        ] = []
        audit = build_multi_case_closure_candidate_audit(suite)
        self.assertEqual(audit["audit_status"], "blocked_missing_candidate")

    def test_candidate_review_required_false_blocks(self) -> None:
        suite = self._valid_suite()
        self._first_candidate(suite)["review_required"] = False
        audit = build_multi_case_closure_candidate_audit(suite)
        self.assertEqual(audit["audit_status"], "blocked_candidate_not_review_required")

    def test_candidate_missing_source_trace_blocks(self) -> None:
        suite = self._valid_suite()
        self._first_candidate(suite)["source_trace_refs"] = []
        audit = build_multi_case_closure_candidate_audit(suite)
        self.assertEqual(audit["audit_status"], "blocked_missing_source_trace")

    def test_wrong_candidate_kind_blocks(self) -> None:
        suite = self._valid_suite()
        for candidate in suite["case_runs"][0]["task_run_closure"][
            "task_learning_digest_candidate_records"
        ]:
            candidate["candidate_kind"] = "wrong_kind"
        audit = build_multi_case_closure_candidate_audit(suite)
        self.assertEqual(audit["audit_status"], "blocked_missing_candidate")

    def test_direct_memory_promotion_blocks(self) -> None:
        suite = self._valid_suite()
        self._first_candidate(suite)["direct_memory_promotion"] = True
        audit = build_multi_case_closure_candidate_audit(suite)
        self.assertEqual(
            audit["audit_status"],
            "blocked_direct_memory_promotion_detected",
        )

    def test_automatic_review_blocks(self) -> None:
        suite = self._valid_suite()
        self._first_candidate(suite)["automatic_reviewed_digest_created"] = True
        audit = build_multi_case_closure_candidate_audit(suite)
        self.assertEqual(audit["audit_status"], "blocked_automatic_review_detected")

    def test_memory_write_blocks(self) -> None:
        suite = self._valid_suite()
        self._first_candidate(suite)["memory_write"] = True
        audit = build_multi_case_closure_candidate_audit(suite)
        self.assertEqual(audit["audit_status"], "blocked_memory_write_detected")

    def test_show_last_audit_works(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_all_multi_case_cradle_task_cases(base_dir=temp_dir)
            saved = run_multi_case_closure_candidate_audit(temp_dir)
            loaded = load_last_multi_case_closure_candidate_audit(temp_dir)
        self.assertEqual(loaded["audit_id"], saved["audit_id"])

    def test_list_audits_works(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_all_multi_case_cradle_task_cases(base_dir=temp_dir)
            run_multi_case_closure_candidate_audit(temp_dir)
            run_multi_case_closure_candidate_audit(temp_dir)
            audits = list_multi_case_closure_candidate_audits(temp_dir)
        self.assertEqual(len(audits), 2)

    def test_cli_commands_work(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_all_multi_case_cradle_task_cases(base_dir=temp_dir)
            run_result = self._run_cli(temp_dir, "run-audit")
            self.assertEqual(run_result.returncode, 0, run_result.stderr)
            show_result = self._run_cli(temp_dir, "show-last-audit")
            self.assertEqual(show_result.returncode, 0, show_result.stderr)
            list_result = self._run_cli(temp_dir, "list-audits")
            self.assertEqual(list_result.returncode, 0, list_result.stderr)

    def test_no_repo_data_pollution(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_all_multi_case_cradle_task_cases(base_dir=temp_dir)
            run_multi_case_closure_candidate_audit(temp_dir)
            self.assertTrue(Path(temp_dir).exists())
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _valid_suite(self) -> dict:
        return copy.deepcopy(run_all_multi_case_cradle_task_cases())

    def _first_candidate(self, suite: dict) -> dict:
        return suite["case_runs"][0]["task_run_closure"][
            "task_learning_digest_candidate_records"
        ][0]

    def _run_cli(self, temp_dir: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core_v1.runtime.multi_case_closure_candidate_audit_cli",
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
