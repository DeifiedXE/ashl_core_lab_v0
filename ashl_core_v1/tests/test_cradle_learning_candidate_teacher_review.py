from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.lesson.cradle_learning_candidate_review import (
    list_cradle_candidate_review_decisions,
    list_cradle_learning_candidates,
    list_cradle_reviewed_learning_records,
    review_cradle_learning_candidate,
)
from ashl_core_v1.runtime.cradle_task_teacher_console import (
    review_candidate_from_teacher_console,
    show_reviewed_from_teacher_console,
)
from ashl_core_v1.runtime.multi_case_closure_candidate_audit import (
    run_multi_case_closure_candidate_audit,
)
from ashl_core_v1.runtime.multi_case_cradle_task_suite import (
    run_all_multi_case_cradle_task_cases,
)


class CradleLearningCandidateTeacherReviewTests(unittest.TestCase):
    def test_list_candidates_returns_review_required_candidates(self) -> None:
        with self._seeded_temp_dir() as temp_dir:
            candidates = list_cradle_learning_candidates(temp_dir)
        self.assertTrue(candidates)
        self.assertTrue(all(candidate["review_required"] for candidate in candidates))

    def test_approved_review_creates_decision_and_reviewed_record(self) -> None:
        with self._seeded_temp_dir() as temp_dir:
            candidate_id = self._candidate_id(temp_dir)
            payload = review_cradle_learning_candidate(
                candidate_id=candidate_id,
                status="approved",
                note="valid handling pattern",
                base_dir=temp_dir,
            )
        self.assertEqual(
            payload["cradle_candidate_review_decision"]["review_status"],
            "approved",
        )
        self.assertEqual(
            payload["cradle_reviewed_learning_record"]["review_status"],
            "approved",
        )

    def test_approved_review_sets_memory_entry_allowed_true(self) -> None:
        with self._seeded_temp_dir() as temp_dir:
            payload = review_cradle_learning_candidate(
                candidate_id=self._candidate_id(temp_dir),
                status="approved",
                note="approve for working memory readback",
                base_dir=temp_dir,
            )
        self.assertTrue(payload["reviewed_learning_digest"]["memory_entry_allowed"])

    def test_non_approved_statuses_set_memory_entry_allowed_false(self) -> None:
        for status in ("rejected", "deferred", "needs_more_evidence", "conflict_detected"):
            with self.subTest(status=status), self._seeded_temp_dir() as temp_dir:
                payload = review_cradle_learning_candidate(
                    candidate_id=self._candidate_id(temp_dir),
                    status=status,
                    note=f"{status} note",
                    base_dir=temp_dir,
                )
                self.assertFalse(payload["reviewed_learning_digest"]["memory_entry_allowed"])

    def test_review_preserves_source_candidate_id(self) -> None:
        with self._seeded_temp_dir() as temp_dir:
            candidate_id = self._candidate_id(temp_dir)
            payload = review_cradle_learning_candidate(
                candidate_id=candidate_id,
                status="approved",
                note="keep source",
                base_dir=temp_dir,
            )
        self.assertEqual(
            payload["cradle_reviewed_learning_record"]["source_candidate_id"],
            candidate_id,
        )

    def test_review_preserves_source_tick_refs(self) -> None:
        with self._seeded_temp_dir() as temp_dir:
            payload = review_cradle_learning_candidate(
                candidate_id=self._candidate_id(temp_dir),
                status="approved",
                note="keep ticks",
                base_dir=temp_dir,
            )
        self.assertTrue(payload["cradle_reviewed_learning_record"]["source_tick_refs"])

    def test_review_without_teacher_note_is_conservative(self) -> None:
        with self._seeded_temp_dir() as temp_dir:
            payload = review_cradle_learning_candidate(
                candidate_id=self._candidate_id(temp_dir),
                status="approved",
                note="",
                base_dir=temp_dir,
            )
        self.assertEqual(payload["reviewed_learning_digest"]["review_status"], "needs_more_evidence")
        self.assertFalse(payload["reviewed_learning_digest"]["memory_entry_allowed"])

    def test_invalid_status_blocks(self) -> None:
        with self._seeded_temp_dir() as temp_dir:
            with self.assertRaises(ValueError):
                review_cradle_learning_candidate(
                    candidate_id=self._candidate_id(temp_dir),
                    status="invalid",
                    note="no",
                    base_dir=temp_dir,
                )

    def test_teacher_console_review_candidate_works(self) -> None:
        with self._seeded_temp_dir() as temp_dir:
            payload = review_candidate_from_teacher_console(
                candidate_id=self._candidate_id(temp_dir),
                status="approved",
                note="console approval",
                base_dir=temp_dir,
            )
        self.assertEqual(payload["console_action"], "review_candidate")
        self.assertFalse(payload["memory_write"])

    def test_show_reviewed_works(self) -> None:
        with self._seeded_temp_dir() as temp_dir:
            review_cradle_learning_candidate(
                candidate_id=self._candidate_id(temp_dir),
                status="approved",
                note="show reviewed",
                base_dir=temp_dir,
            )
            reviewed = show_reviewed_from_teacher_console(temp_dir)
        self.assertTrue(reviewed["reviewed_learning_records"])

    def test_no_automatic_review_memory_write_or_direct_promotion(self) -> None:
        with self._seeded_temp_dir() as temp_dir:
            payload = review_cradle_learning_candidate(
                candidate_id=self._candidate_id(temp_dir),
                status="approved",
                note="manual only",
                base_dir=temp_dir,
            )
        self.assertFalse(payload["cradle_candidate_review_task"]["automatic_review"])
        self.assertFalse(payload["cradle_reviewed_learning_record"]["memory_write"])
        self.assertFalse(payload["cradle_reviewed_learning_record"]["direct_memory_promotion"])

    def test_review_decision_and_reviewed_lists_work(self) -> None:
        with self._seeded_temp_dir() as temp_dir:
            review_cradle_learning_candidate(
                candidate_id=self._candidate_id(temp_dir),
                status="approved",
                note="list me",
                base_dir=temp_dir,
            )
            decisions = list_cradle_candidate_review_decisions(temp_dir)
            reviewed = list_cradle_reviewed_learning_records(temp_dir)
        self.assertEqual(len(decisions), 1)
        self.assertEqual(len(reviewed), 1)

    def test_cli_commands_work(self) -> None:
        with self._seeded_temp_dir() as temp_dir:
            candidate_id = self._candidate_id(temp_dir)
            list_result = self._run_cli(temp_dir, "list-candidates")
            self.assertEqual(list_result.returncode, 0, list_result.stderr)
            review_result = self._run_cli(
                temp_dir,
                "review-candidate",
                "--candidate-id",
                candidate_id,
                "--status",
                "approved",
                "--note",
                "cli approval",
            )
            self.assertEqual(review_result.returncode, 0, review_result.stderr)
            show_result = self._run_cli(temp_dir, "show-reviewed")
            self.assertEqual(show_result.returncode, 0, show_result.stderr)
            decisions_result = self._run_cli(temp_dir, "list-review-decisions")
            self.assertEqual(decisions_result.returncode, 0, decisions_result.stderr)

    def test_no_repo_data_pollution(self) -> None:
        with self._seeded_temp_dir() as temp_dir:
            review_cradle_learning_candidate(
                candidate_id=self._candidate_id(temp_dir),
                status="approved",
                note="temp only",
                base_dir=temp_dir,
            )
            self.assertTrue(Path(temp_dir).exists())
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _seeded_temp_dir(self) -> tempfile.TemporaryDirectory:
        temp_dir = tempfile.TemporaryDirectory()
        run_all_multi_case_cradle_task_cases(base_dir=temp_dir.name)
        run_multi_case_closure_candidate_audit(temp_dir.name)
        return temp_dir

    def _candidate_id(self, temp_dir: str) -> str:
        return list_cradle_learning_candidates(temp_dir)[0]["candidate_id"]

    def _run_cli(self, temp_dir: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core_v1.lesson.cradle_learning_candidate_review_cli",
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
