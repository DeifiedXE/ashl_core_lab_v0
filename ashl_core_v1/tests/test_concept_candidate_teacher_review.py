from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from ashl_core_v1.learning.concept_candidate_from_task_closure_draft import (
    build_demo_draft,
    build_demo_teaching_test_seed,
)
from ashl_core_v1.learning.concept_candidate_teacher_review import (
    ALLOWED_TEACHER_DECISIONS,
    ConceptCandidateTeacherReviewDecision,
    ConceptCandidateTeacherReviewTask,
    build_concept_candidate_teacher_review_decision,
    build_concept_candidate_teacher_review_summary,
    build_concept_candidate_teacher_review_task,
    build_demo_needs_more_support_review,
    build_demo_rejected_review,
    build_demo_scope_narrowed_review,
    build_demo_split_required_review,
    build_demo_teacher_review_ready_review,
    validate_concept_candidate_teacher_review_decision,
    validate_concept_candidate_teacher_review_summary,
    validate_concept_candidate_teacher_review_task,
)


class ConceptCandidateTeacherReviewTests(unittest.TestCase):
    def test_build_review_task_from_blocked_draft_succeeds(self) -> None:
        task = self._blocked_review_task()
        validation = validate_concept_candidate_teacher_review_task(task)
        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(task.review_task_status, "pending_teacher_review")

    def test_review_task_requires_valid_concept_candidate_draft_record(self) -> None:
        draft = build_demo_draft("blocked")
        invalid = self._mutated_draft_dict(draft, memory_write_performed=True)
        task = build_concept_candidate_teacher_review_task(
            invalid,
            build_demo_teaching_test_seed("blocked"),
        )
        self.assertEqual(task.review_task_status, "blocked_invalid_draft")

    def test_review_task_exposes_support_evidence_count(self) -> None:
        task = self._blocked_review_task()
        self.assertEqual(task.support_evidence_count, 1)

    def test_review_task_exposes_counterexample_evidence_count(self) -> None:
        task = self._blocked_review_task()
        self.assertEqual(task.counterexample_evidence_count, 0)

    def test_review_task_allowed_decisions_include_five_statuses(self) -> None:
        task = self._blocked_review_task()
        self.assertEqual(task.allowed_teacher_decisions, ALLOWED_TEACHER_DECISIONS)

    def test_needs_more_support_decision_validates(self) -> None:
        decision = self._payload_decision(build_demo_needs_more_support_review())
        validation = validate_concept_candidate_teacher_review_decision(decision)
        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(decision.teacher_decision, "needs_more_support")

    def test_needs_more_support_requires_teacher_note(self) -> None:
        decision = build_concept_candidate_teacher_review_decision(
            self._blocked_review_task(),
            teacher_decision="needs_more_support",
            teacher_note="",
            decision_reason_codes=("insufficient_support",),
        )
        validation = validate_concept_candidate_teacher_review_decision(decision)
        self.assertFalse(validation["valid"])
        self.assertEqual(decision.decision_blocked_reason, "missing_teacher_note")

    def test_scope_narrowed_decision_validates_with_scope_change(self) -> None:
        decision = self._payload_decision(build_demo_scope_narrowed_review())
        validation = validate_concept_candidate_teacher_review_decision(decision)
        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(decision.teacher_decision, "scope_narrowed")

    def test_scope_narrowed_requires_requested_scope_changes(self) -> None:
        decision = build_concept_candidate_teacher_review_decision(
            self._blocked_review_task(),
            teacher_decision="scope_narrowed",
            teacher_note="Too broad.",
        )
        self.assertFalse(decision.decision_valid)
        self.assertEqual(
            decision.decision_blocked_reason,
            "scope_change_required_but_missing",
        )

    def test_split_required_decision_validates_with_split_labels(self) -> None:
        decision = self._payload_decision(build_demo_split_required_review())
        validation = validate_concept_candidate_teacher_review_decision(decision)
        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(decision.teacher_decision, "split_required")

    def test_split_required_requires_counterexample_evidence_or_confirmed_refs(self) -> None:
        decision = build_concept_candidate_teacher_review_decision(
            self._blocked_review_task(),
            teacher_decision="split_required",
            teacher_note="Split this broad label.",
            requested_split_labels=("front_wall_blocked", "front_box_pushable"),
        )
        self.assertFalse(decision.decision_valid)
        self.assertEqual(decision.decision_blocked_reason, "missing_counterexample_handling")

    def test_split_required_requires_requested_split_labels(self) -> None:
        decision = build_concept_candidate_teacher_review_decision(
            self._blocked_review_task(),
            teacher_decision="split_required",
            teacher_note="Counterexample present.",
            counterexample_evidence_refs_confirmed=("counterexample:001",),
        )
        self.assertFalse(decision.decision_valid)
        self.assertEqual(
            decision.decision_blocked_reason,
            "split_labels_required_but_missing",
        )

    def test_teacher_review_ready_decision_validates_with_support_evidence(self) -> None:
        decision = self._payload_decision(build_demo_teacher_review_ready_review())
        validation = validate_concept_candidate_teacher_review_decision(decision)
        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(decision.teacher_decision, "teacher_review_ready")

    def test_teacher_review_ready_requires_teacher_note(self) -> None:
        task = build_concept_candidate_teacher_review_task(
            build_demo_draft("unknown"),
            build_demo_teaching_test_seed("unknown"),
        )
        decision = build_concept_candidate_teacher_review_decision(
            task,
            teacher_decision="teacher_review_ready",
            teacher_note="",
            support_evidence_refs_confirmed=("task_closure:unknown_needs_observe",),
        )
        self.assertFalse(decision.decision_valid)
        self.assertEqual(decision.decision_blocked_reason, "missing_teacher_note")

    def test_teacher_review_ready_does_not_approve_concept(self) -> None:
        decision = self._payload_decision(build_demo_teacher_review_ready_review())
        self.assertFalse(decision.concept_approved)

    def test_teacher_review_ready_does_not_create_reviewed_concept(self) -> None:
        decision = self._payload_decision(build_demo_teacher_review_ready_review())
        self.assertFalse(decision.reviewed_concept_created)

    def test_rejected_decision_validates(self) -> None:
        decision = self._payload_decision(build_demo_rejected_review())
        validation = validate_concept_candidate_teacher_review_decision(decision)
        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(decision.teacher_decision, "rejected")

    def test_invalid_teacher_decision_blocks(self) -> None:
        decision = build_concept_candidate_teacher_review_decision(
            self._blocked_review_task(),
            teacher_decision="approved",
            teacher_note="Invalid approval attempt.",
        )
        self.assertFalse(decision.decision_valid)
        self.assertEqual(decision.decision_blocked_reason, "invalid_teacher_decision")

    def test_missing_teacher_note_blocks(self) -> None:
        decision = build_concept_candidate_teacher_review_decision(
            self._blocked_review_task(),
            teacher_decision="rejected",
            teacher_note="",
        )
        self.assertFalse(decision.decision_valid)
        self.assertEqual(decision.decision_blocked_reason, "missing_teacher_note")

    def test_review_decision_concept_approved_false(self) -> None:
        decision = self._payload_decision(build_demo_needs_more_support_review())
        self.assertFalse(decision.concept_approved)

    def test_review_decision_reviewed_concept_created_false(self) -> None:
        decision = self._payload_decision(build_demo_needs_more_support_review())
        self.assertFalse(decision.reviewed_concept_created)

    def test_review_decision_memory_write_performed_false(self) -> None:
        decision = self._payload_decision(build_demo_needs_more_support_review())
        self.assertFalse(decision.memory_write_performed)

    def test_review_decision_task_behavior_changed_false(self) -> None:
        decision = self._payload_decision(build_demo_needs_more_support_review())
        self.assertFalse(decision.task_behavior_changed)

    def test_review_decision_automatic_approval_created_false(self) -> None:
        decision = self._payload_decision(build_demo_needs_more_support_review())
        self.assertFalse(decision.automatic_approval_created)

    def test_review_summary_maps_needs_more_support(self) -> None:
        summary = self._payload_summary(build_demo_needs_more_support_review())
        self.assertEqual(
            summary.next_learning_engine_step,
            "collect_more_support_evidence",
        )

    def test_review_summary_maps_scope_narrowed(self) -> None:
        summary = self._payload_summary(build_demo_scope_narrowed_review())
        self.assertEqual(
            summary.next_learning_engine_step,
            "prepare_scope_narrowed_candidate",
        )

    def test_review_summary_maps_split_required(self) -> None:
        summary = self._payload_summary(build_demo_split_required_review())
        self.assertEqual(summary.next_learning_engine_step, "prepare_split_candidates")

    def test_review_summary_maps_teacher_review_ready(self) -> None:
        summary = self._payload_summary(build_demo_teacher_review_ready_review())
        self.assertEqual(
            summary.next_learning_engine_step,
            "prepare_future_reviewed_concept_candidate",
        )

    def test_review_summary_maps_rejected(self) -> None:
        summary = self._payload_summary(build_demo_rejected_review())
        self.assertEqual(summary.next_learning_engine_step, "stop_candidate")

    def test_review_summary_validates(self) -> None:
        summary = self._payload_summary(build_demo_scope_narrowed_review())
        validation = validate_concept_candidate_teacher_review_summary(summary)
        self.assertTrue(validation["valid"], validation["error_codes"])

    def test_cli_show_review_task_works(self) -> None:
        result = self._run_learning_cli("show-review-task", "--demo", "blocked")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("front_blocked_affordance", result.stdout)

    def test_cli_review_demo_needs_more_support_works(self) -> None:
        result = self._run_learning_cli(
            "review-demo",
            "--demo",
            "blocked",
            "--decision",
            "needs_more_support",
            "--teacher-note",
            "Need more evidence.",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("collect_more_support_evidence", result.stdout)

    def test_cli_review_demo_scope_narrowed_works(self) -> None:
        result = self._run_learning_cli(
            "review-demo",
            "--demo",
            "blocked",
            "--decision",
            "scope_narrowed",
            "--teacher-note",
            "Narrow it.",
            "--scope-change",
            "front_wall_blocked only",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("prepare_scope_narrowed_candidate", result.stdout)

    def test_cli_review_demo_split_required_works(self) -> None:
        result = self._run_learning_cli(
            "review-demo",
            "--demo",
            "blocked",
            "--decision",
            "split_required",
            "--teacher-note",
            "Split it.",
            "--split-label",
            "front_wall_blocked",
            "--split-label",
            "front_box_pushable",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("prepare_split_candidates", result.stdout)

    def test_cli_review_demo_teacher_review_ready_works(self) -> None:
        result = self._run_learning_cli(
            "review-demo",
            "--demo",
            "blocked",
            "--decision",
            "teacher_review_ready",
            "--teacher-note",
            "Ready for next package.",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("prepare_future_reviewed_concept_candidate", result.stdout)

    def test_cli_review_demo_rejected_works(self) -> None:
        result = self._run_learning_cli(
            "review-demo",
            "--demo",
            "blocked",
            "--decision",
            "rejected",
            "--teacher-note",
            "Stop it.",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("stop_candidate", result.stdout)

    def test_cli_validate_demo_review_works(self) -> None:
        result = self._run_learning_cli("validate-demo-review", "--decision", "split_required")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"valid": true', result.stdout)

    def test_guided_console_learning_show_concept_review_task_works(self) -> None:
        result = self._run_guided_cli(
            "learning-show-concept-review-task",
            "--demo",
            "blocked",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("concept_review_task", result.stdout)

    def test_guided_console_learning_review_demo_concept_works(self) -> None:
        result = self._run_guided_cli(
            "learning-review-demo-concept",
            "--demo",
            "blocked",
            "--decision",
            "needs_more_support",
            "--teacher-note",
            "Need another support case.",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("review_decision", result.stdout)

    def test_no_repo_data_created(self) -> None:
        build_demo_needs_more_support_review()
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _blocked_review_task(self) -> ConceptCandidateTeacherReviewTask:
        return build_concept_candidate_teacher_review_task(
            build_demo_draft("blocked"),
            build_demo_teaching_test_seed("blocked"),
        )

    def _payload_decision(
        self,
        payload: dict[str, object],
    ) -> ConceptCandidateTeacherReviewDecision:
        return ConceptCandidateTeacherReviewDecision.from_dict(
            dict(payload["review_decision"])
        )

    def _payload_summary(self, payload: dict[str, object]):
        from ashl_core_v1.learning.concept_candidate_teacher_review import (
            ConceptCandidateTeacherReviewSummary,
        )

        return ConceptCandidateTeacherReviewSummary.from_dict(
            dict(payload["review_summary"])
        )

    def _mutated_draft_dict(self, draft, **changes: object) -> dict[str, object]:
        data = draft.to_dict()
        data.update(changes)
        return data

    def _run_learning_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core_v1.learning.concept_candidate_teacher_review_cli",
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
