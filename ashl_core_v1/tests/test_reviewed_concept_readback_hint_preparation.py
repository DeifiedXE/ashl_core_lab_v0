from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from ashl_core_v1.memory.reviewed_concept_readback_hint_candidate import (
    build_demo_reviewed_concept_readback_hint_candidate_set,
)
from ashl_core_v1.memory.reviewed_concept_readback_hint_preparation import (
    ReviewedConceptReadbackHintPreparationRecord,
    ReviewedConceptReadbackHintPreparationSafetyAudit,
    ReviewedConceptReadbackHintPreparationSet,
    build_demo_all_held_readback_hint_preparation_set,
    build_demo_blocked_forbidden_authority_preparation_set,
    build_demo_conflict_detected_readback_hint_preparation_set,
    build_demo_rejected_readback_hint_preparation_set,
    build_demo_reviewed_concept_readback_hint_preparation_set,
    build_reviewed_concept_readback_hint_preparation_bundle,
    build_reviewed_concept_readback_hint_preparation_safety_audit,
    validate_reviewed_concept_readback_hint_preparation_record,
    validate_reviewed_concept_readback_hint_preparation_safety_audit,
    validate_reviewed_concept_readback_hint_preparation_set,
)
from ashl_core_v1.memory.reviewed_concept_readback_hint_teacher_review import (
    build_reviewed_concept_readback_hint_teacher_review_bundle,
)


class ReviewedConceptReadbackHintPreparationTests(unittest.TestCase):
    def test_preparation_record_builds_from_approved_teacher_review(self) -> None:
        record = self._first_prepared_record()
        validation = validate_reviewed_concept_readback_hint_preparation_record(record)
        self.assertTrue(validation["valid"], validation["error_codes"])

    def test_preparation_record_preserves_reviewed_concept_id(self) -> None:
        record = self._first_prepared_record()
        self.assertEqual(
            record.source_reviewed_concept_id,
            self._candidate_payload()["hint_candidate_set"]["source_reviewed_concept_id"],
        )

    def test_preparation_record_preserves_hint_candidate_id(self) -> None:
        record = self._first_prepared_record()
        self.assertIn("observe_before_direct_retry", record.source_hint_candidate_id)

    def test_preparation_record_preserves_teacher_review_id(self) -> None:
        record = self._first_prepared_record()
        self.assertIn(
            record.source_hint_candidate_id,
            record.source_hint_candidate_teacher_review_id,
        )

    def test_preparation_record_preserves_hint_label(self) -> None:
        self.assertEqual(self._first_prepared_record().hint_label, "observe_before_direct_retry")

    def test_preparation_record_preserves_hint_kind(self) -> None:
        self.assertEqual(self._first_prepared_record().hint_kind, "observe_before_retry")

    def test_preparation_record_preserves_task_handling_note(self) -> None:
        self.assertIn("Do not treat all front_blocked", self._first_prepared_record().prepared_task_handling_note)

    def test_preparation_record_preserves_scope_warning(self) -> None:
        self.assertIn(
            "front_blocked may be too broad",
            self._first_prepared_record().prepared_scope_warning or "",
        )

    def test_preparation_record_preserves_counterexample_warning(self) -> None:
        self.assertIn(
            "front_blocked + step_forward succeeds",
            self._first_prepared_record().prepared_counterexample_warning or "",
        )

    def test_approved_teacher_review_creates_prepared_status(self) -> None:
        self.assertEqual(
            self._record_for_status("approved_for_future_hint_preparation").preparation_status,
            "prepared_for_future_hint_creation_review",
        )

    def test_held_teacher_review_creates_held_for_more_evidence(self) -> None:
        self.assertEqual(
            self._record_for_status("held_for_more_evidence").preparation_status,
            "held_for_more_evidence",
        )

    def test_needs_more_evidence_review_creates_held_for_more_evidence(self) -> None:
        self.assertEqual(
            self._record_for_status("needs_more_evidence").preparation_status,
            "held_for_more_evidence",
        )

    def test_rejected_review_creates_blocked_candidate_rejected(self) -> None:
        self.assertEqual(
            self._record_for_status("rejected").preparation_status,
            "blocked_candidate_rejected",
        )

    def test_conflict_detected_review_creates_blocked_conflict_detected(self) -> None:
        self.assertEqual(
            self._record_for_status("conflict_detected").preparation_status,
            "blocked_conflict_detected",
        )

    def test_preparation_record_ready_flag_true_only_when_approved(self) -> None:
        expected = {
            "approved_for_future_hint_preparation": True,
            "held_for_more_evidence": False,
            "needs_more_evidence": False,
            "rejected": False,
            "conflict_detected": False,
        }
        for status, ready in expected.items():
            with self.subTest(status=status):
                self.assertIs(
                    self._record_for_status(status).ready_for_future_task_working_memory_hint_creation_review,
                    ready,
                )

    def test_preparation_record_requires_task_engine_hint_creation_package_true(self) -> None:
        self.assertTrue(self._first_prepared_record().requires_task_engine_hint_creation_package)

    def test_preparation_record_requires_teacher_review_before_application_true(self) -> None:
        self.assertTrue(self._first_prepared_record().requires_teacher_review_before_application)

    def test_preparation_record_authority_flags_false(self) -> None:
        record = self._first_prepared_record()
        self.assertFalse(record.actual_task_working_memory_hint_created)
        self.assertFalse(record.applied_to_working_memory)
        self.assertFalse(record.working_memory_mutated)
        self.assertFalse(record.task_behavior_changed)
        self.assertFalse(record.candidate_ordering_changed)
        self.assertFalse(record.action_selection_created)
        self.assertFalse(record.action_execution_created)

    def test_preparation_set_builds_from_reviewed_candidate_set(self) -> None:
        preparation_set = self._valid_preparation_set()
        validation = validate_reviewed_concept_readback_hint_preparation_set(
            preparation_set
        )
        self.assertTrue(validation["valid"], validation["error_codes"])

    def test_preparation_set_counts_prepared_records_correctly(self) -> None:
        self.assertEqual(self._valid_preparation_set().prepared_count, 2)

    def test_preparation_set_counts_held_records_correctly(self) -> None:
        self.assertEqual(self._valid_preparation_set().held_count, 1)

    def test_preparation_set_counts_blocked_records_correctly(self) -> None:
        payload = build_demo_rejected_readback_hint_preparation_set()
        preparation_set = ReviewedConceptReadbackHintPreparationSet.from_dict(
            payload["readback_hint_preparation_set"]
        )
        self.assertEqual(preparation_set.blocked_count, 3)

    def test_preparation_set_status_created_with_ready_records_when_ready_exists(self) -> None:
        self.assertEqual(
            self._valid_preparation_set().set_preparation_status,
            "preparation_set_created_with_ready_records",
        )

    def test_preparation_set_status_all_held_or_blocked_when_none_ready(self) -> None:
        payload = build_demo_all_held_readback_hint_preparation_set()
        preparation_set = ReviewedConceptReadbackHintPreparationSet.from_dict(
            payload["readback_hint_preparation_set"]
        )
        self.assertEqual(
            preparation_set.set_preparation_status,
            "preparation_set_created_all_held_or_blocked",
        )

    def test_safety_audit_passes_for_valid_demo_preparation(self) -> None:
        payload = build_demo_reviewed_concept_readback_hint_preparation_set()
        validation = validate_reviewed_concept_readback_hint_preparation_safety_audit(
            payload["readback_hint_preparation_safety_audit"]
        )
        self.assertTrue(validation["valid"], validation["error_codes"])

    def test_safety_audit_blocks_forbidden_actual_hint_creation(self) -> None:
        audit = self._audit_with_record_flag(
            "actual_task_working_memory_hint_created",
            True,
        )
        self.assertEqual(audit.audit_status, "blocked_forbidden_hint_creation_detected")

    def test_safety_audit_blocks_forbidden_working_memory_mutation(self) -> None:
        audit = self._audit_with_record_flag("working_memory_mutated", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_working_memory_mutation_detected",
        )

    def test_safety_audit_blocks_forbidden_task_behavior_change(self) -> None:
        audit = self._audit_with_record_flag("task_behavior_changed", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_behavior_change_detected",
        )

    def test_safety_audit_blocks_forbidden_candidate_ordering_change(self) -> None:
        audit = self._audit_with_record_flag("candidate_ordering_changed", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_behavior_change_detected",
        )

    def test_safety_audit_blocks_forbidden_action_selection(self) -> None:
        audit = self._audit_with_record_flag("action_selection_created", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_action_authority_detected",
        )

    def test_safety_audit_blocks_forbidden_action_execution(self) -> None:
        audit = self._audit_with_record_flag("action_execution_created", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_action_authority_detected",
        )

    def test_safety_audit_blocks_forbidden_memory_layer_write(self) -> None:
        audit = self._audit_with_record_flag("memory_layer_write_performed", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_memory_write_detected",
        )

    def test_blocked_forbidden_authority_demo_blocks(self) -> None:
        payload = build_demo_blocked_forbidden_authority_preparation_set()
        self.assertEqual(
            payload["readback_hint_preparation_safety_audit"]["audit_status"],
            "blocked_forbidden_hint_creation_detected",
        )

    def test_cli_prepare_demo_hints_works(self) -> None:
        result = self._run_memory_cli("prepare-demo-hints")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("preparation_set_created_with_ready_records", result.stdout)

    def test_cli_show_demo_preparation_works(self) -> None:
        result = self._run_memory_cli("show-demo-preparation")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("prepared_hint_labels", result.stdout)

    def test_cli_show_demo_safety_audit_works(self) -> None:
        result = self._run_memory_cli("show-demo-safety-audit")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"audit_status": "passed"', result.stdout)

    def test_cli_validate_demo_preparation_works(self) -> None:
        result = self._run_memory_cli("validate-demo-preparation")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"valid": true', result.stdout)

    def test_cli_all_held_works(self) -> None:
        result = self._run_memory_cli("prepare-demo-held", "--case", "all-held")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("preparation_set_created_all_held_or_blocked", result.stdout)

    def test_cli_rejected_blocked_works(self) -> None:
        result = self._run_memory_cli("prepare-demo-blocked", "--case", "rejected")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("blocked_candidate_rejected", result.stdout)

    def test_cli_conflict_blocked_works(self) -> None:
        result = self._run_memory_cli("prepare-demo-blocked", "--case", "conflict")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("blocked_conflict_detected", result.stdout)

    def test_cli_forbidden_authority_blocked_works(self) -> None:
        result = self._run_memory_cli(
            "prepare-demo-blocked",
            "--case",
            "forbidden-authority",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("blocked_forbidden_hint_creation_detected", result.stdout)

    def test_guided_console_hint_preparation_demo_works(self) -> None:
        for command in (
            "memory-prepare-reviewed-concept-hints-demo",
            "memory-show-reviewed-concept-hint-preparation",
            "memory-validate-reviewed-concept-hint-preparation",
        ):
            result = self._run_guided_cli(command)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("guided_console_action", result.stdout)

    def test_no_repo_data_created(self) -> None:
        build_demo_reviewed_concept_readback_hint_preparation_set()
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _candidate_payload(self) -> dict[str, object]:
        return build_demo_reviewed_concept_readback_hint_candidate_set()

    def _valid_payload(self) -> dict[str, object]:
        return build_demo_reviewed_concept_readback_hint_preparation_set()

    def _valid_preparation_set(self) -> ReviewedConceptReadbackHintPreparationSet:
        return ReviewedConceptReadbackHintPreparationSet.from_dict(
            self._valid_payload()["readback_hint_preparation_set"]
        )

    def _first_prepared_record(self) -> ReviewedConceptReadbackHintPreparationRecord:
        return next(
            record
            for record in self._valid_preparation_set().preparation_records
            if record.preparation_status == "prepared_for_future_hint_creation_review"
        )

    def _record_for_status(
        self,
        status: str,
    ) -> ReviewedConceptReadbackHintPreparationRecord:
        candidate_payload = self._candidate_payload()
        first_label = candidate_payload["hint_candidate_set"]["candidate_labels"][0]
        decisions = {
            label: "held_for_more_evidence"
            for label in candidate_payload["hint_candidate_set"]["candidate_labels"]
        }
        decisions[first_label] = status
        teacher_payload = build_reviewed_concept_readback_hint_teacher_review_bundle(
            candidate_payload,
            review_decisions=decisions,
        )
        preparation_payload = build_reviewed_concept_readback_hint_preparation_bundle(
            candidate_payload=candidate_payload,
            teacher_review_payload=teacher_payload,
        )
        return ReviewedConceptReadbackHintPreparationRecord.from_dict(
            preparation_payload["readback_hint_preparation_records"][0]
        )

    def _audit_with_record_flag(
        self,
        flag_name: str,
        flag_value: bool,
    ) -> ReviewedConceptReadbackHintPreparationSafetyAudit:
        payload = self._valid_payload()
        preparation_set = ReviewedConceptReadbackHintPreparationSet.from_dict(
            payload["readback_hint_preparation_set"]
        )
        records = list(preparation_set.preparation_records)
        first = dict(records[0].to_dict())
        first[flag_name] = flag_value
        records[0] = ReviewedConceptReadbackHintPreparationRecord.from_dict(first)
        preparation_set = ReviewedConceptReadbackHintPreparationSet.from_dict(
            {
                **preparation_set.to_dict(),
                "preparation_records": [record.to_dict() for record in records],
            }
        )
        teacher_payload = build_reviewed_concept_readback_hint_teacher_review_bundle(
            self._candidate_payload()
        )
        return build_reviewed_concept_readback_hint_preparation_safety_audit(
            hint_candidate_set_teacher_review=teacher_payload[
                "hint_candidate_set_teacher_review"
            ],
            teacher_review_safety_audit=teacher_payload[
                "hint_teacher_review_safety_audit"
            ],
            preparation_set=preparation_set,
        )

    def _run_memory_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core_v1.memory.reviewed_concept_readback_hint_preparation_cli",
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
