from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from ashl_core_v1.memory.reviewed_concept_readback_hint_preparation import (
    build_demo_all_held_readback_hint_preparation_set,
    build_demo_rejected_readback_hint_preparation_set,
    build_demo_reviewed_concept_readback_hint_preparation_set,
)
from ashl_core_v1.task.reviewed_concept_readback_hint_record import (
    TaskWorkingMemoryReadbackHint,
    TaskWorkingMemoryReadbackHintRecordSafetyAudit,
    TaskWorkingMemoryReadbackHintRecordSet,
    build_demo_all_held_task_working_memory_readback_hint_record_set,
    build_demo_blocked_forbidden_authority_hint_record_set,
    build_demo_blocked_invalid_preparation_hint_record_set,
    build_demo_task_working_memory_readback_hint_record_set,
    build_task_working_memory_readback_hint_record_bundle,
    build_task_working_memory_readback_hint_record_safety_audit,
    validate_task_working_memory_readback_hint,
    validate_task_working_memory_readback_hint_record_safety_audit,
    validate_task_working_memory_readback_hint_record_set,
)


class ReviewedConceptReadbackHintRecordTests(unittest.TestCase):
    def test_hint_record_builds_from_prepared_hint_preparation(self) -> None:
        hint = self._first_created_hint()
        validation = validate_task_working_memory_readback_hint(hint)
        self.assertTrue(validation["valid"], validation["error_codes"])

    def test_hint_record_preserves_reviewed_concept_id(self) -> None:
        hint = self._first_created_hint()
        self.assertEqual(
            hint.source_reviewed_concept_id,
            self._preparation_payload()["readback_hint_preparation_set"][
                "source_reviewed_concept_id"
            ],
        )

    def test_hint_record_preserves_preparation_id(self) -> None:
        hint = self._first_created_hint()
        self.assertIn("observe_before_direct_retry", hint.source_readback_hint_preparation_id)

    def test_hint_record_preserves_hint_label(self) -> None:
        self.assertEqual(self._first_created_hint().hint_label, "observe_before_direct_retry")

    def test_hint_record_preserves_hint_kind(self) -> None:
        self.assertEqual(self._first_created_hint().hint_kind, "observe_before_retry")

    def test_hint_record_preserves_hint_priority(self) -> None:
        self.assertEqual(self._first_created_hint().hint_priority, 1)

    def test_hint_record_preserves_hint_summary(self) -> None:
        self.assertIn("Preview hint label", self._first_created_hint().hint_summary)

    def test_hint_record_preserves_task_handling_note(self) -> None:
        self.assertIn("Do not treat all front_blocked", self._first_created_hint().task_handling_note)

    def test_hint_record_preserves_scope_warning(self) -> None:
        self.assertIn(
            "front_blocked may be too broad",
            self._first_created_hint().scope_warning or "",
        )

    def test_hint_record_preserves_counterexample_warning(self) -> None:
        self.assertIn(
            "front_blocked + step_forward succeeds",
            self._first_created_hint().counterexample_warning or "",
        )

    def test_prepared_preparation_creates_inactive_hint(self) -> None:
        self.assertEqual(
            self._record_for_preparation_demo("valid").hint_record_status,
            "hint_record_created_inactive",
        )

    def test_held_preparation_creates_held_for_more_evidence(self) -> None:
        self.assertEqual(
            self._record_for_preparation_demo("held").hint_record_status,
            "held_for_more_evidence",
        )

    def test_blocked_preparation_creates_blocked_invalid_preparation(self) -> None:
        self.assertEqual(
            self._record_for_preparation_demo("blocked").hint_record_status,
            "blocked_invalid_preparation",
        )

    def test_hint_record_available_flag_true_only_when_inactive_created(self) -> None:
        expected = {
            "valid": True,
            "held": False,
            "blocked": False,
        }
        for demo, available in expected.items():
            with self.subTest(demo=demo):
                self.assertIs(
                    self._record_for_preparation_demo(
                        demo
                    ).available_for_future_working_memory_application_review,
                    available,
                )

    def test_hint_record_requires_teacher_review_before_application_true(self) -> None:
        self.assertTrue(self._first_created_hint().requires_teacher_review_before_application)

    def test_hint_record_requires_task_engine_application_package_true(self) -> None:
        self.assertTrue(self._first_created_hint().requires_task_engine_application_package)

    def test_hint_record_authority_flags_false(self) -> None:
        hint = self._first_created_hint()
        self.assertFalse(hint.applied_to_working_memory)
        self.assertFalse(hint.working_memory_mutated)
        self.assertFalse(hint.task_behavior_changed)
        self.assertFalse(hint.candidate_ordering_changed)
        self.assertFalse(hint.selected_action_changed)
        self.assertFalse(hint.final_action_changed)
        self.assertFalse(hint.direct_command_changed)
        self.assertFalse(hint.execution_created)
        self.assertFalse(hint.memory_layer_write_performed)

    def test_record_set_builds_from_preparation_set(self) -> None:
        record_set = self._valid_record_set()
        validation = validate_task_working_memory_readback_hint_record_set(record_set)
        self.assertTrue(validation["valid"], validation["error_codes"])

    def test_record_set_counts_created_records_correctly(self) -> None:
        self.assertEqual(self._valid_record_set().created_count, 2)

    def test_record_set_counts_held_records_correctly(self) -> None:
        self.assertEqual(self._valid_record_set().held_count, 1)

    def test_record_set_counts_blocked_records_correctly(self) -> None:
        payload = build_demo_blocked_invalid_preparation_hint_record_set()
        record_set = TaskWorkingMemoryReadbackHintRecordSet.from_dict(
            payload["task_working_memory_readback_hint_record_set"]
        )
        self.assertEqual(record_set.blocked_count, 3)

    def test_record_set_status_with_inactive_hints_when_created(self) -> None:
        self.assertEqual(
            self._valid_record_set().record_set_status,
            "record_set_created_with_inactive_hints",
        )

    def test_record_set_status_all_held_or_blocked_when_none_created(self) -> None:
        payload = build_demo_all_held_task_working_memory_readback_hint_record_set()
        record_set = TaskWorkingMemoryReadbackHintRecordSet.from_dict(
            payload["task_working_memory_readback_hint_record_set"]
        )
        self.assertEqual(
            record_set.record_set_status,
            "record_set_created_all_held_or_blocked",
        )

    def test_safety_audit_passes_for_valid_demo_record_set(self) -> None:
        payload = build_demo_task_working_memory_readback_hint_record_set()
        validation = validate_task_working_memory_readback_hint_record_safety_audit(
            payload["task_working_memory_readback_hint_record_safety_audit"]
        )
        self.assertTrue(validation["valid"], validation["error_codes"])

    def test_safety_audit_actual_hint_records_created_true_when_inactive_hints_created(self) -> None:
        audit = self._valid_safety_audit()
        self.assertTrue(audit.actual_task_working_memory_readback_hint_records_created)

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

    def test_safety_audit_blocks_forbidden_selected_action_change(self) -> None:
        audit = self._audit_with_record_flag("selected_action_changed", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_action_authority_detected",
        )

    def test_safety_audit_blocks_forbidden_final_action_change(self) -> None:
        audit = self._audit_with_record_flag("final_action_changed", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_action_authority_detected",
        )

    def test_safety_audit_blocks_forbidden_direct_command_change(self) -> None:
        audit = self._audit_with_record_flag("direct_command_changed", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_action_authority_detected",
        )

    def test_safety_audit_blocks_forbidden_execution(self) -> None:
        audit = self._audit_with_record_flag("execution_created", True)
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
        payload = build_demo_blocked_forbidden_authority_hint_record_set()
        self.assertEqual(
            payload["task_working_memory_readback_hint_record_safety_audit"][
                "audit_status"
            ],
            "blocked_forbidden_working_memory_mutation_detected",
        )

    def test_cli_create_demo_hint_records_works(self) -> None:
        result = self._run_task_cli("create-demo-hint-records")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("record_set_created_with_inactive_hints", result.stdout)

    def test_cli_show_demo_hint_records_works(self) -> None:
        result = self._run_task_cli("show-demo-hint-records")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("task_working_memory_readback_hint_id", result.stdout)

    def test_cli_show_demo_safety_audit_works(self) -> None:
        result = self._run_task_cli("show-demo-safety-audit")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"audit_status": "passed"', result.stdout)

    def test_cli_validate_demo_hint_records_works(self) -> None:
        result = self._run_task_cli("validate-demo-hint-records")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"valid": true', result.stdout)

    def test_cli_all_held_works(self) -> None:
        result = self._run_task_cli("create-demo-held", "--case", "all-held")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("record_set_created_all_held_or_blocked", result.stdout)

    def test_cli_invalid_preparation_blocked_works(self) -> None:
        result = self._run_task_cli(
            "create-demo-blocked",
            "--case",
            "invalid-preparation",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("blocked_invalid_preparation", result.stdout)

    def test_cli_forbidden_authority_blocked_works(self) -> None:
        result = self._run_task_cli(
            "create-demo-blocked",
            "--case",
            "forbidden-authority",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("blocked_forbidden_working_memory_mutation_detected", result.stdout)

    def test_guided_console_hint_record_demo_works(self) -> None:
        for command in (
            "task-create-reviewed-concept-hint-records-demo",
            "task-show-reviewed-concept-hint-records",
            "task-validate-reviewed-concept-hint-records",
        ):
            result = self._run_guided_cli(command)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("guided_console_action", result.stdout)

    def test_no_repo_data_created(self) -> None:
        build_demo_task_working_memory_readback_hint_record_set()
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _preparation_payload(self) -> dict[str, object]:
        return build_demo_reviewed_concept_readback_hint_preparation_set()

    def _valid_payload(self) -> dict[str, object]:
        return build_demo_task_working_memory_readback_hint_record_set()

    def _valid_record_set(self) -> TaskWorkingMemoryReadbackHintRecordSet:
        return TaskWorkingMemoryReadbackHintRecordSet.from_dict(
            self._valid_payload()["task_working_memory_readback_hint_record_set"]
        )

    def _valid_safety_audit(self) -> TaskWorkingMemoryReadbackHintRecordSafetyAudit:
        return TaskWorkingMemoryReadbackHintRecordSafetyAudit.from_dict(
            self._valid_payload()["task_working_memory_readback_hint_record_safety_audit"]
        )

    def _first_created_hint(self) -> TaskWorkingMemoryReadbackHint:
        return next(
            record
            for record in self._valid_record_set().hint_records
            if record.hint_record_status == "hint_record_created_inactive"
        )

    def _record_for_preparation_demo(self, demo: str) -> TaskWorkingMemoryReadbackHint:
        if demo == "valid":
            payload = build_demo_task_working_memory_readback_hint_record_set()
        elif demo == "held":
            payload = build_task_working_memory_readback_hint_record_bundle(
                build_demo_all_held_readback_hint_preparation_set()
            )
        elif demo == "blocked":
            payload = build_task_working_memory_readback_hint_record_bundle(
                build_demo_rejected_readback_hint_preparation_set()
            )
        else:
            raise ValueError(demo)
        return TaskWorkingMemoryReadbackHint.from_dict(
            payload["task_working_memory_readback_hint_records"][0]
        )

    def _audit_with_record_flag(
        self,
        flag_name: str,
        flag_value: bool,
    ) -> TaskWorkingMemoryReadbackHintRecordSafetyAudit:
        payload = self._valid_payload()
        record_set = TaskWorkingMemoryReadbackHintRecordSet.from_dict(
            payload["task_working_memory_readback_hint_record_set"]
        )
        records = list(record_set.hint_records)
        first = dict(records[0].to_dict())
        first[flag_name] = flag_value
        records[0] = TaskWorkingMemoryReadbackHint.from_dict(first)
        record_set = TaskWorkingMemoryReadbackHintRecordSet.from_dict(
            {
                **record_set.to_dict(),
                "hint_records": [record.to_dict() for record in records],
            }
        )
        preparation_payload = self._preparation_payload()
        return build_task_working_memory_readback_hint_record_safety_audit(
            readback_hint_preparation_set=preparation_payload[
                "readback_hint_preparation_set"
            ],
            preparation_safety_audit=preparation_payload[
                "readback_hint_preparation_safety_audit"
            ],
            hint_record_set=record_set,
        )

    def _run_task_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core_v1.task.reviewed_concept_readback_hint_record_cli",
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
