from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from ashl_core_v1.task.reviewed_concept_readback_hint_application_preparation import (
    TaskWorkingMemoryReadbackHintApplicationPreparationRecord,
    TaskWorkingMemoryReadbackHintApplicationPreparationSafetyAudit,
    TaskWorkingMemoryReadbackHintApplicationPreparationSet,
    build_demo_all_held_task_working_memory_readback_hint_application_preparation_set,
    build_demo_blocked_forbidden_authority_application_preparation_set,
    build_demo_conflict_detected_task_working_memory_readback_hint_application_preparation_set,
    build_demo_rejected_task_working_memory_readback_hint_application_preparation_set,
    build_demo_task_working_memory_readback_hint_application_preparation_set,
    build_task_working_memory_readback_hint_application_preparation_record,
    build_task_working_memory_readback_hint_application_preparation_safety_audit,
    validate_task_working_memory_readback_hint_application_preparation_record,
    validate_task_working_memory_readback_hint_application_preparation_safety_audit,
    validate_task_working_memory_readback_hint_application_preparation_set,
)
from ashl_core_v1.task.reviewed_concept_readback_hint_application_preview import (
    build_demo_task_working_memory_readback_hint_application_preview_set,
)
from ashl_core_v1.task.reviewed_concept_readback_hint_application_teacher_review import (
    TaskWorkingMemoryReadbackHintApplicationPreviewSetTeacherReview,
    TaskWorkingMemoryReadbackHintApplicationTeacherReview,
    build_demo_task_working_memory_readback_hint_application_teacher_review,
    build_task_working_memory_readback_hint_application_teacher_review,
)


APPROVED = "approved_for_future_working_memory_application_preparation"


class ReviewedConceptReadbackHintApplicationPreparationTests(unittest.TestCase):
    def test_application_preparation_record_builds_from_approved_review(self) -> None:
        record = self._preparation_for_first_review(APPROVED)
        validation = validate_task_working_memory_readback_hint_application_preparation_record(
            record
        )
        self.assertTrue(validation["valid"], validation["error_codes"])

    def test_preparation_record_preserves_reviewed_concept_id(self) -> None:
        record = self._first_prepared_record()
        self.assertEqual(
            record.source_reviewed_concept_id,
            self._teacher_review_payload()[
                "hint_application_preview_set_teacher_review"
            ]["source_reviewed_concept_id"],
        )

    def test_preparation_record_preserves_application_preview_id(self) -> None:
        record = self._first_prepared_record()
        self.assertIn("application_preview", record.source_hint_application_preview_id)

    def test_preparation_record_preserves_teacher_review_id(self) -> None:
        record = self._first_prepared_record()
        self.assertIn(
            "application_teacher_review",
            record.source_hint_application_teacher_review_id,
        )

    def test_preparation_record_preserves_hint_record_id(self) -> None:
        record = self._first_prepared_record()
        self.assertIn(
            "task_working_memory_readback_hint:",
            record.source_task_working_memory_readback_hint_id,
        )

    def test_preparation_record_preserves_hint_label(self) -> None:
        self.assertEqual(
            self._first_prepared_record().hint_label,
            "observe_before_direct_retry",
        )

    def test_preparation_record_preserves_hint_kind(self) -> None:
        self.assertEqual(self._first_prepared_record().hint_kind, "observe_before_retry")

    def test_preparation_record_preserves_hint_priority(self) -> None:
        self.assertEqual(self._first_prepared_record().hint_priority, 1)

    def test_preparation_record_preserves_hint_summary(self) -> None:
        self.assertIn("Preview hint label", self._first_prepared_record().hint_summary)

    def test_preparation_record_preserves_working_memory_slot(self) -> None:
        self.assertEqual(
            self._first_prepared_record().prepared_working_memory_slot,
            "readback_hints",
        )

    def test_preparation_record_preserves_application_scope(self) -> None:
        self.assertEqual(
            self._first_prepared_record().prepared_application_scope,
            "future_task_initialization",
        )

    def test_preparation_record_preserves_visibility(self) -> None:
        self.assertEqual(
            self._first_prepared_record().prepared_visibility,
            "advisory_only",
        )

    def test_preparation_record_preserves_lifetime(self) -> None:
        self.assertEqual(self._first_prepared_record().prepared_lifetime, "single_task")

    def test_approved_review_creates_ready_preparation(self) -> None:
        self.assertEqual(
            self._preparation_for_first_review(APPROVED).preparation_status,
            "prepared_for_future_working_memory_initialization_application",
        )

    def test_held_review_creates_held_for_more_evidence(self) -> None:
        self.assertEqual(
            self._preparation_for_first_review(
                "held_for_more_evidence"
            ).preparation_status,
            "held_for_more_evidence",
        )

    def test_needs_more_evidence_review_creates_held_for_more_evidence(self) -> None:
        self.assertEqual(
            self._preparation_for_first_review(
                "needs_more_evidence"
            ).preparation_status,
            "held_for_more_evidence",
        )

    def test_rejected_review_creates_blocked_rejected(self) -> None:
        self.assertEqual(
            self._preparation_for_first_review("rejected").preparation_status,
            "blocked_application_preview_rejected",
        )

    def test_conflict_detected_review_creates_blocked_conflict(self) -> None:
        self.assertEqual(
            self._preparation_for_first_review("conflict_detected").preparation_status,
            "blocked_conflict_detected",
        )

    def test_preparation_ready_flag_true_only_when_approved(self) -> None:
        expected = {
            APPROVED: True,
            "held_for_more_evidence": False,
            "needs_more_evidence": False,
            "rejected": False,
            "conflict_detected": False,
        }
        for status, ready in expected.items():
            with self.subTest(status=status):
                self.assertIs(
                    self._preparation_for_first_review(
                        status
                    ).ready_for_future_working_memory_initialization_application,
                    ready,
                )

    def test_preparation_keeps_advisory_future_single_task_scope(self) -> None:
        record = self._first_prepared_record()
        self.assertEqual(record.prepared_visibility, "advisory_only")
        self.assertEqual(record.prepared_application_scope, "future_task_initialization")
        self.assertEqual(record.prepared_lifetime, "single_task")

    def test_preparation_authority_flags_false(self) -> None:
        record = self._first_prepared_record()
        self.assertFalse(record.applied_to_working_memory)
        self.assertFalse(record.working_memory_mutated)
        self.assertFalse(record.task_behavior_changed)
        self.assertFalse(record.candidate_ordering_changed)
        self.assertFalse(record.selected_action_changed)
        self.assertFalse(record.final_action_changed)
        self.assertFalse(record.direct_command_changed)
        self.assertFalse(record.execution_created)
        self.assertFalse(record.memory_layer_write_performed)

    def test_preparation_set_builds_from_teacher_review_set(self) -> None:
        prep_set = self._valid_preparation_set()
        validation = validate_task_working_memory_readback_hint_application_preparation_set(
            prep_set
        )
        self.assertTrue(validation["valid"], validation["error_codes"])

    def test_preparation_set_counts_prepared_records_correctly(self) -> None:
        self.assertEqual(self._valid_preparation_set().prepared_count, 2)

    def test_preparation_set_counts_held_records_correctly(self) -> None:
        self.assertEqual(self._valid_preparation_set().held_count, 1)

    def test_preparation_set_counts_blocked_records_correctly(self) -> None:
        payload = (
            build_demo_rejected_task_working_memory_readback_hint_application_preparation_set()
        )
        prep_set = TaskWorkingMemoryReadbackHintApplicationPreparationSet.from_dict(
            payload["hint_application_preparation_set"]
        )
        self.assertEqual(prep_set.blocked_count, prep_set.prepared_count + 3)

    def test_preparation_set_status_with_ready_records(self) -> None:
        self.assertEqual(
            self._valid_preparation_set().set_preparation_status,
            "preparation_set_created_with_ready_application_records",
        )

    def test_preparation_set_status_all_held_or_blocked_when_none_ready(self) -> None:
        payload = (
            build_demo_all_held_task_working_memory_readback_hint_application_preparation_set()
        )
        prep_set = TaskWorkingMemoryReadbackHintApplicationPreparationSet.from_dict(
            payload["hint_application_preparation_set"]
        )
        self.assertEqual(
            prep_set.set_preparation_status,
            "preparation_set_created_all_held_or_blocked",
        )

    def test_safety_audit_passes_for_valid_demo_preparation(self) -> None:
        payload = build_demo_task_working_memory_readback_hint_application_preparation_set()
        validation = validate_task_working_memory_readback_hint_application_preparation_safety_audit(
            payload["hint_application_preparation_safety_audit"]
        )
        self.assertTrue(validation["valid"], validation["error_codes"])

    def test_safety_audit_blocks_forbidden_active_hint_application(self) -> None:
        audit = self._audit_with_preparation_flag("applied_to_working_memory", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_active_hint_application_detected",
        )

    def test_safety_audit_blocks_forbidden_working_memory_mutation(self) -> None:
        audit = self._audit_with_preparation_flag("working_memory_mutated", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_working_memory_mutation_detected",
        )

    def test_safety_audit_blocks_forbidden_task_behavior_change(self) -> None:
        audit = self._audit_with_preparation_flag("task_behavior_changed", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_behavior_change_detected",
        )

    def test_safety_audit_blocks_forbidden_candidate_ordering_change(self) -> None:
        audit = self._audit_with_preparation_flag("candidate_ordering_changed", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_behavior_change_detected",
        )

    def test_safety_audit_blocks_forbidden_selected_action_change(self) -> None:
        audit = self._audit_with_preparation_flag("selected_action_changed", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_action_authority_detected",
        )

    def test_safety_audit_blocks_forbidden_final_action_change(self) -> None:
        audit = self._audit_with_preparation_flag("final_action_changed", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_action_authority_detected",
        )

    def test_safety_audit_blocks_forbidden_direct_command_change(self) -> None:
        audit = self._audit_with_preparation_flag("direct_command_changed", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_action_authority_detected",
        )

    def test_safety_audit_blocks_forbidden_execution(self) -> None:
        audit = self._audit_with_preparation_flag("execution_created", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_action_authority_detected",
        )

    def test_safety_audit_blocks_forbidden_memory_layer_write(self) -> None:
        audit = self._audit_with_preparation_flag("memory_layer_write_performed", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_memory_write_detected",
        )

    def test_cli_prepare_demo_application_works(self) -> None:
        result = self._run_task_cli("prepare-demo-application")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "preparation_set_created_with_ready_application_records",
            result.stdout,
        )

    def test_cli_show_demo_preparation_works(self) -> None:
        result = self._run_task_cli("show-demo-preparation")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("prepared_record_ids", result.stdout)

    def test_cli_show_demo_safety_audit_works(self) -> None:
        result = self._run_task_cli("show-demo-safety-audit")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"audit_status": "passed"', result.stdout)

    def test_cli_validate_demo_preparation_works(self) -> None:
        result = self._run_task_cli("validate-demo-preparation")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"valid": true', result.stdout)

    def test_cli_all_held_works(self) -> None:
        result = self._run_task_cli("prepare-demo-held", "--case", "all-held")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("preparation_set_created_all_held_or_blocked", result.stdout)

    def test_cli_rejected_blocked_works(self) -> None:
        result = self._run_task_cli("prepare-demo-blocked", "--case", "rejected")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("blocked_application_preview_rejected", result.stdout)

    def test_cli_conflict_blocked_works(self) -> None:
        result = self._run_task_cli("prepare-demo-blocked", "--case", "conflict")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("blocked_conflict_detected", result.stdout)

    def test_cli_forbidden_authority_blocked_works(self) -> None:
        result = self._run_task_cli(
            "prepare-demo-blocked",
            "--case",
            "forbidden-authority",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("blocked_forbidden_active_hint_application_detected", result.stdout)

    def test_guided_console_application_preparation_demo_works(self) -> None:
        for command in (
            "task-prepare-reviewed-concept-hint-application-demo",
            "task-show-reviewed-concept-hint-application-preparation",
            "task-validate-reviewed-concept-hint-application-preparation",
        ):
            result = self._run_guided_cli(command)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("guided_console_action", result.stdout)

    def test_no_repo_data_created(self) -> None:
        build_demo_task_working_memory_readback_hint_application_preparation_set()
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _teacher_review_payload(self) -> dict[str, object]:
        return build_demo_task_working_memory_readback_hint_application_teacher_review()

    def _preview_payload(self) -> dict[str, object]:
        return build_demo_task_working_memory_readback_hint_application_preview_set()

    def _valid_preparation_set(
        self,
    ) -> TaskWorkingMemoryReadbackHintApplicationPreparationSet:
        payload = build_demo_task_working_memory_readback_hint_application_preparation_set()
        return TaskWorkingMemoryReadbackHintApplicationPreparationSet.from_dict(
            payload["hint_application_preparation_set"]
        )

    def _first_prepared_record(
        self,
    ) -> TaskWorkingMemoryReadbackHintApplicationPreparationRecord:
        return next(
            record
            for record in self._valid_preparation_set().application_preparation_records
            if record.preparation_status
            == "prepared_for_future_working_memory_initialization_application"
        )

    def _review_for_first_preview(
        self,
        status: str,
    ) -> TaskWorkingMemoryReadbackHintApplicationTeacherReview:
        preview_payload = self._preview_payload()
        return build_task_working_memory_readback_hint_application_teacher_review(
            application_preview=preview_payload[
                "task_working_memory_readback_hint_application_previews"
            ][0],
            application_preview_set=preview_payload[
                "task_working_memory_readback_hint_application_preview_set"
            ],
            application_preview_safety_audit=preview_payload[
                "task_working_memory_readback_hint_application_preview_safety_audit"
            ],
            teacher_review_status=status,
        )

    def _preparation_for_first_review(
        self,
        status: str,
    ) -> TaskWorkingMemoryReadbackHintApplicationPreparationRecord:
        teacher_payload = self._teacher_review_payload()
        return build_task_working_memory_readback_hint_application_preparation_record(
            application_teacher_review=self._review_for_first_preview(status),
            application_preview_set_teacher_review=teacher_payload[
                "hint_application_preview_set_teacher_review"
            ],
            application_teacher_review_safety_audit=teacher_payload[
                "hint_application_teacher_review_safety_audit"
            ],
        )

    def _audit_with_preparation_flag(
        self,
        flag_name: str,
        flag_value: bool,
    ) -> TaskWorkingMemoryReadbackHintApplicationPreparationSafetyAudit:
        payload = build_demo_task_working_memory_readback_hint_application_preparation_set()
        prep_set = TaskWorkingMemoryReadbackHintApplicationPreparationSet.from_dict(
            payload["hint_application_preparation_set"]
        )
        records = list(prep_set.application_preparation_records)
        first = dict(records[0].to_dict())
        first[flag_name] = flag_value
        records[0] = TaskWorkingMemoryReadbackHintApplicationPreparationRecord.from_dict(
            first
        )
        prep_set = TaskWorkingMemoryReadbackHintApplicationPreparationSet.from_dict(
            {
                **prep_set.to_dict(),
                "application_preparation_records": [
                    record.to_dict() for record in records
                ],
            }
        )
        teacher_payload = self._teacher_review_payload()
        return build_task_working_memory_readback_hint_application_preparation_safety_audit(
            application_preview_set_teacher_review=teacher_payload[
                "hint_application_preview_set_teacher_review"
            ],
            application_teacher_review_safety_audit=teacher_payload[
                "hint_application_teacher_review_safety_audit"
            ],
            application_preparation_set=prep_set,
        )

    def _run_task_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core_v1.task.reviewed_concept_readback_hint_application_preparation_cli",
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
