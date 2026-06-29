from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from ashl_core_v1.learning.concept_candidate_refinement_from_teacher_review import (
    ConceptCandidateRefinementRecord,
    ConceptEvidenceRequestRecord,
    FutureReviewedConceptPreparationMarker,
    ScopeNarrowedConceptDraftRecord,
    SplitConceptDraftSetRecord,
    build_demo_more_support_refinement,
    build_demo_refinement,
    build_demo_rejected_refinement,
    build_demo_scope_narrowed_refinement,
    build_demo_split_required_refinement,
    build_demo_teacher_review_ready_refinement,
    refine_concept_candidate_from_teacher_review,
    validate_concept_candidate_refinement_record,
    validate_concept_candidate_stop_record,
    validate_concept_evidence_request,
    validate_future_reviewed_concept_preparation_marker,
    validate_scope_narrowed_concept_draft,
    validate_split_concept_draft_set,
)
from ashl_core_v1.learning.concept_candidate_teacher_review import (
    build_concept_candidate_teacher_review_decision,
    build_concept_candidate_teacher_review_summary,
    build_concept_candidate_teacher_review_task,
)
from ashl_core_v1.learning.concept_candidate_from_task_closure_draft import (
    build_demo_draft,
    build_demo_teaching_test_seed,
)


class ConceptCandidateRefinementFromTeacherReviewTests(unittest.TestCase):
    def test_needs_more_support_refinement_creates_evidence_request(self) -> None:
        payload = build_demo_more_support_refinement()
        self.assertIsNotNone(payload["evidence_request"])
        request = ConceptEvidenceRequestRecord.from_dict(dict(payload["evidence_request"]))
        self.assertEqual(request.request_status, "request_created")

    def test_needs_more_support_refinement_does_not_run_task(self) -> None:
        request = ConceptEvidenceRequestRecord.from_dict(
            dict(build_demo_more_support_refinement()["evidence_request"])
        )
        validation = validate_concept_evidence_request(request)
        self.assertTrue(validation["does_not_run_task"])

    def test_needs_more_support_refinement_does_not_collect_evidence_automatically(self) -> None:
        request = ConceptEvidenceRequestRecord.from_dict(
            dict(build_demo_more_support_refinement()["evidence_request"])
        )
        validation = validate_concept_evidence_request(request)
        self.assertTrue(validation["does_not_collect_evidence_automatically"])

    def test_scope_narrowed_refinement_creates_scope_narrowed_draft(self) -> None:
        payload = build_demo_scope_narrowed_refinement()
        self.assertIsNotNone(payload["scope_narrowed_draft"])
        record = ScopeNarrowedConceptDraftRecord.from_dict(
            dict(payload["scope_narrowed_draft"])
        )
        self.assertEqual(record.narrowed_status, "narrowed_draft_created")

    def test_scope_narrowed_requires_requested_scope_changes(self) -> None:
        payload = self._blocked_scope_narrowed_payload()
        refinement = ConceptCandidateRefinementRecord.from_dict(
            dict(payload["refinement_record"])
        )
        self.assertEqual(
            refinement.refinement_status,
            "blocked_missing_required_scope_change",
        )

    def test_scope_narrowed_candidate_remains_teacher_review_required(self) -> None:
        record = ScopeNarrowedConceptDraftRecord.from_dict(
            dict(build_demo_scope_narrowed_refinement()["scope_narrowed_draft"])
        )
        validation = validate_scope_narrowed_concept_draft(record)
        self.assertTrue(validation["teacher_review_required"])

    def test_scope_narrowed_candidate_memory_application_candidate_allowed_false(self) -> None:
        record = ScopeNarrowedConceptDraftRecord.from_dict(
            dict(build_demo_scope_narrowed_refinement()["scope_narrowed_draft"])
        )
        validation = validate_scope_narrowed_concept_draft(record)
        self.assertFalse(validation["memory_application_candidate_allowed"])

    def test_split_required_refinement_creates_split_draft_set(self) -> None:
        payload = build_demo_split_required_refinement()
        self.assertIsNotNone(payload["split_draft_set"])
        split_set = SplitConceptDraftSetRecord.from_dict(dict(payload["split_draft_set"]))
        self.assertEqual(split_set.split_status, "split_drafts_created")

    def test_split_required_requires_requested_split_labels(self) -> None:
        payload = self._blocked_split_payload()
        refinement = ConceptCandidateRefinementRecord.from_dict(
            dict(payload["refinement_record"])
        )
        self.assertEqual(
            refinement.refinement_status,
            "blocked_missing_required_split_labels",
        )

    def test_split_required_creates_multiple_split_candidates(self) -> None:
        split_set = SplitConceptDraftSetRecord.from_dict(
            dict(build_demo_split_required_refinement()["split_draft_set"])
        )
        validation = validate_split_concept_draft_set(split_set)
        self.assertGreaterEqual(validation["split_candidate_count"], 2)

    def test_split_candidates_remain_teacher_review_required(self) -> None:
        split_set = SplitConceptDraftSetRecord.from_dict(
            dict(build_demo_split_required_refinement()["split_draft_set"])
        )
        self.assertTrue(
            all(candidate.teacher_review_required for candidate in split_set.split_concept_candidates)
        )

    def test_split_candidates_memory_application_candidate_allowed_false(self) -> None:
        split_set = SplitConceptDraftSetRecord.from_dict(
            dict(build_demo_split_required_refinement()["split_draft_set"])
        )
        self.assertTrue(
            all(
                candidate.memory_application_candidate_allowed is False
                for candidate in split_set.split_concept_candidates
            )
        )

    def test_teacher_review_ready_creates_future_preparation_marker(self) -> None:
        payload = build_demo_teacher_review_ready_refinement()
        marker = FutureReviewedConceptPreparationMarker.from_dict(
            dict(payload["future_reviewed_concept_preparation_marker"])
        )
        validation = validate_future_reviewed_concept_preparation_marker(marker)
        self.assertTrue(validation["valid"], validation["error_codes"])

    def test_teacher_review_ready_marker_does_not_create_reviewed_concept(self) -> None:
        marker = FutureReviewedConceptPreparationMarker.from_dict(
            dict(build_demo_teacher_review_ready_refinement()["future_reviewed_concept_preparation_marker"])
        )
        self.assertFalse(marker.reviewed_concept_created)

    def test_teacher_review_ready_marker_does_not_approve_concept(self) -> None:
        marker = FutureReviewedConceptPreparationMarker.from_dict(
            dict(build_demo_teacher_review_ready_refinement()["future_reviewed_concept_preparation_marker"])
        )
        self.assertFalse(marker.concept_approved)

    def test_rejected_creates_concept_candidate_stop_record(self) -> None:
        payload = build_demo_rejected_refinement()
        self.assertIsNotNone(payload["stop_record"])
        validation = validate_concept_candidate_stop_record(payload["stop_record"])
        self.assertTrue(validation["valid"], validation["error_codes"])

    def test_rejected_stop_record_can_be_reopened_by_teacher_true(self) -> None:
        validation = validate_concept_candidate_stop_record(
            build_demo_rejected_refinement()["stop_record"]
        )
        self.assertTrue(validation["can_be_reopened_by_teacher"])

    def test_refinement_record_maps_each_teacher_decision_to_correct_refinement_kind(self) -> None:
        expected = {
            "needs_more_support": "more_support_request",
            "scope_narrowed": "scope_narrowed_draft",
            "split_required": "split_draft_set",
            "teacher_review_ready": "future_reviewed_concept_preparation",
            "rejected": "stopped_candidate",
        }
        for decision, kind in expected.items():
            with self.subTest(decision=decision):
                refinement = ConceptCandidateRefinementRecord.from_dict(
                    dict(build_demo_refinement(decision)["refinement_record"])
                )
                self.assertEqual(refinement.refinement_kind, kind)

    def test_invalid_teacher_decision_blocks_refinement(self) -> None:
        payload = self._invalid_decision_payload()
        refinement = ConceptCandidateRefinementRecord.from_dict(
            dict(payload["refinement_record"])
        )
        self.assertEqual(refinement.refinement_status, "blocked_unsupported_decision")

    def test_missing_required_scope_change_blocks(self) -> None:
        payload = self._blocked_scope_narrowed_payload()
        self.assertEqual(
            payload["refinement_record"]["refinement_status"],
            "blocked_missing_required_scope_change",
        )

    def test_missing_required_split_labels_blocks(self) -> None:
        payload = self._blocked_split_payload()
        self.assertEqual(
            payload["refinement_record"]["refinement_status"],
            "blocked_missing_required_split_labels",
        )

    def test_missing_support_confirmation_for_teacher_review_ready_blocks(self) -> None:
        payload = self._blocked_teacher_review_ready_payload()
        self.assertEqual(
            payload["refinement_record"]["refinement_status"],
            "blocked_missing_required_evidence_request",
        )

    def test_all_refinement_records_concept_approved_false(self) -> None:
        for decision in self._decisions():
            record = build_demo_refinement(decision)["refinement_record"]
            self.assertFalse(record["concept_approved"])

    def test_all_refinement_records_reviewed_concept_created_false(self) -> None:
        for decision in self._decisions():
            record = build_demo_refinement(decision)["refinement_record"]
            self.assertFalse(record["reviewed_concept_created"])

    def test_all_refinement_records_memory_write_performed_false(self) -> None:
        for decision in self._decisions():
            record = build_demo_refinement(decision)["refinement_record"]
            self.assertFalse(record["memory_write_performed"])

    def test_all_refinement_records_task_behavior_changed_false(self) -> None:
        for decision in self._decisions():
            record = build_demo_refinement(decision)["refinement_record"]
            self.assertFalse(record["task_behavior_changed"])

    def test_cli_refine_demo_needs_more_support_works(self) -> None:
        result = self._run_learning_cli("refine-demo", "--decision", "needs_more_support")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("more_support_request", result.stdout)

    def test_cli_refine_demo_scope_narrowed_works(self) -> None:
        result = self._run_learning_cli("refine-demo", "--decision", "scope_narrowed")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("scope_narrowed_draft", result.stdout)

    def test_cli_refine_demo_split_required_works(self) -> None:
        result = self._run_learning_cli("refine-demo", "--decision", "split_required")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("split_draft_set", result.stdout)

    def test_cli_refine_demo_teacher_review_ready_works(self) -> None:
        result = self._run_learning_cli("refine-demo", "--decision", "teacher_review_ready")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("future_reviewed_concept_preparation", result.stdout)

    def test_cli_refine_demo_rejected_works(self) -> None:
        result = self._run_learning_cli("refine-demo", "--decision", "rejected")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("stopped_candidate", result.stdout)

    def test_cli_validate_demo_works(self) -> None:
        result = self._run_learning_cli("validate-demo", "--decision", "split_required")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"valid": true', result.stdout)

    def test_cli_show_refinement_summary_works(self) -> None:
        result = self._run_learning_cli(
            "show-refinement-summary",
            "--decision",
            "scope_narrowed",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("refinement_summary", result.stdout)

    def test_guided_console_learning_refine_demo_concept_works(self) -> None:
        result = self._run_guided_cli(
            "learning-refine-demo-concept",
            "--decision",
            "needs_more_support",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("refinement_record", result.stdout)

    def test_guided_console_learning_validate_demo_refinement_works(self) -> None:
        result = self._run_guided_cli(
            "learning-validate-demo-refinement",
            "--decision",
            "split_required",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"valid": true', result.stdout)

    def test_no_repo_data_created(self) -> None:
        build_demo_refinement("needs_more_support")
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _invalid_decision_payload(self) -> dict[str, object]:
        task = build_concept_candidate_teacher_review_task(
            build_demo_draft("blocked"),
            build_demo_teaching_test_seed("blocked"),
        )
        decision = build_concept_candidate_teacher_review_decision(
            task,
            teacher_decision="approved",
            teacher_note="Invalid approval attempt.",
        )
        summary = build_concept_candidate_teacher_review_summary(task, decision)
        return refine_concept_candidate_from_teacher_review(
            task=task,
            decision=decision,
            summary=summary,
            draft=build_demo_draft("blocked"),
        )

    def _blocked_scope_narrowed_payload(self) -> dict[str, object]:
        task = build_concept_candidate_teacher_review_task(
            build_demo_draft("blocked"),
            build_demo_teaching_test_seed("blocked"),
        )
        decision = build_concept_candidate_teacher_review_decision(
            task,
            teacher_decision="scope_narrowed",
            teacher_note="Too broad.",
        )
        summary = build_concept_candidate_teacher_review_summary(task, decision)
        return refine_concept_candidate_from_teacher_review(
            task=task,
            decision=decision,
            summary=summary,
            draft=build_demo_draft("blocked"),
        )

    def _blocked_split_payload(self) -> dict[str, object]:
        task = build_concept_candidate_teacher_review_task(
            build_demo_draft("blocked"),
            build_demo_teaching_test_seed("blocked"),
        )
        decision = build_concept_candidate_teacher_review_decision(
            task,
            teacher_decision="split_required",
            teacher_note="Counterexample present.",
            counterexample_evidence_refs_confirmed=("counterexample:001",),
        )
        summary = build_concept_candidate_teacher_review_summary(task, decision)
        return refine_concept_candidate_from_teacher_review(
            task=task,
            decision=decision,
            summary=summary,
            draft=build_demo_draft("blocked"),
        )

    def _blocked_teacher_review_ready_payload(self) -> dict[str, object]:
        task = build_concept_candidate_teacher_review_task(
            build_demo_draft("unknown"),
            build_demo_teaching_test_seed("unknown"),
        )
        decision = build_concept_candidate_teacher_review_decision(
            task,
            teacher_decision="teacher_review_ready",
            teacher_note="Ready but missing support confirmation.",
        )
        summary = build_concept_candidate_teacher_review_summary(task, decision)
        return refine_concept_candidate_from_teacher_review(
            task=task,
            decision=decision,
            summary=summary,
            draft=build_demo_draft("unknown"),
        )

    def _decisions(self) -> tuple[str, ...]:
        return (
            "needs_more_support",
            "scope_narrowed",
            "split_required",
            "teacher_review_ready",
            "rejected",
        )

    def _run_learning_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core_v1.learning.concept_candidate_refinement_from_teacher_review_cli",
                *args,
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    def _run_guided_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core_v1.runtime.guided_cradle_growth_teacher_console_cli",
                *args,
            ],
            check=False,
            capture_output=True,
            text=True,
        )


if __name__ == "__main__":
    unittest.main()
