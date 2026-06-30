from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from ashl_core_v1.task.reviewed_concept_readback_hint_application_preview import (
    TaskWorkingMemoryReadbackHintApplicationPreview,
    TaskWorkingMemoryReadbackHintApplicationPreviewSafetyAudit,
    TaskWorkingMemoryReadbackHintApplicationPreviewSet,
    build_demo_all_held_task_working_memory_readback_hint_application_preview_set,
    build_demo_blocked_invalid_hint_record_application_preview_set,
    build_demo_task_working_memory_readback_hint_application_preview_set,
    build_task_working_memory_readback_hint_application_preview_bundle,
    build_task_working_memory_readback_hint_application_preview_safety_audit,
    validate_task_working_memory_readback_hint_application_preview,
    validate_task_working_memory_readback_hint_application_preview_safety_audit,
    validate_task_working_memory_readback_hint_application_preview_set,
)
from ashl_core_v1.task.reviewed_concept_readback_hint_record import (
    TaskWorkingMemoryReadbackHintRecordSafetyAudit,
    TaskWorkingMemoryReadbackHintRecordSet,
    build_demo_all_held_task_working_memory_readback_hint_record_set,
    build_demo_blocked_invalid_preparation_hint_record_set,
    build_demo_task_working_memory_readback_hint_record_set,
)


class ReviewedConceptReadbackHintApplicationPreviewTests(unittest.TestCase):
    def test_application_preview_builds_from_inactive_hint_record(self) -> None:
        preview = self._first_ready_preview()
        validation = validate_task_working_memory_readback_hint_application_preview(
            preview
        )
        self.assertTrue(validation["valid"], validation["error_codes"])

    def test_application_preview_preserves_reviewed_concept_id(self) -> None:
        self.assertEqual(
            self._first_ready_preview().source_reviewed_concept_id,
            self._valid_record_set().source_reviewed_concept_id,
        )

    def test_application_preview_preserves_hint_record_id(self) -> None:
        self.assertIn(
            "task_working_memory_readback_hint:",
            self._first_ready_preview().source_task_working_memory_readback_hint_id,
        )

    def test_application_preview_preserves_hint_label(self) -> None:
        self.assertEqual(
            self._first_ready_preview().hint_label,
            "observe_before_direct_retry",
        )

    def test_application_preview_preserves_hint_kind(self) -> None:
        self.assertEqual(
            self._first_ready_preview().hint_kind,
            "observe_before_retry",
        )

    def test_application_preview_preserves_hint_priority(self) -> None:
        self.assertEqual(self._first_ready_preview().hint_priority, 1)

    def test_application_preview_preserves_hint_summary(self) -> None:
        self.assertIn("Preview hint label", self._first_ready_preview().hint_summary)

    def test_application_preview_preserves_task_handling_note(self) -> None:
        self.assertIn(
            "Do not treat all front_blocked",
            self._first_ready_preview().task_handling_note,
        )

    def test_application_preview_preserves_scope_warning(self) -> None:
        self.assertIn(
            "front_blocked may be too broad",
            self._first_ready_preview().scope_warning or "",
        )

    def test_application_preview_preserves_counterexample_warning(self) -> None:
        self.assertIn(
            "front_blocked + step_forward succeeds",
            self._first_ready_preview().counterexample_warning or "",
        )

    def test_inactive_hint_record_creates_application_preview_ready(self) -> None:
        self.assertEqual(
            self._preview_for_hint_record_demo("valid").preview_status,
            "application_preview_ready",
        )

    def test_held_hint_record_creates_held_for_more_evidence(self) -> None:
        self.assertEqual(
            self._preview_for_hint_record_demo("held").preview_status,
            "held_for_more_evidence",
        )

    def test_blocked_hint_record_creates_blocked_invalid_hint_record(self) -> None:
        self.assertEqual(
            self._preview_for_hint_record_demo("blocked").preview_status,
            "blocked_invalid_hint_record",
        )

    def test_ready_application_preview_proposes_readback_hints_slot(self) -> None:
        self.assertEqual(
            self._first_ready_preview().proposed_working_memory_slot,
            "readback_hints",
        )

    def test_ready_application_preview_proposes_future_task_initialization(self) -> None:
        self.assertEqual(
            self._first_ready_preview().proposed_application_scope,
            "future_task_initialization",
        )

    def test_ready_application_preview_proposes_advisory_only_visibility(self) -> None:
        self.assertEqual(
            self._first_ready_preview().proposed_visibility,
            "advisory_only",
        )

    def test_ready_application_preview_proposes_single_task_lifetime(self) -> None:
        self.assertEqual(self._first_ready_preview().proposed_lifetime, "single_task")

    def test_ready_flag_true_only_when_ready(self) -> None:
        expected = {"valid": True, "held": False, "blocked": False}
        for demo, ready in expected.items():
            with self.subTest(demo=demo):
                self.assertIs(
                    self._preview_for_hint_record_demo(
                        demo
                    ).ready_for_teacher_application_review,
                    ready,
                )

    def test_application_preview_authority_flags_false(self) -> None:
        preview = self._first_ready_preview()
        self.assertFalse(preview.applied_to_working_memory)
        self.assertFalse(preview.working_memory_mutated)
        self.assertFalse(preview.task_behavior_changed)
        self.assertFalse(preview.candidate_ordering_changed)
        self.assertFalse(preview.selected_action_changed)
        self.assertFalse(preview.final_action_changed)
        self.assertFalse(preview.direct_command_changed)
        self.assertFalse(preview.execution_created)
        self.assertFalse(preview.memory_layer_write_performed)

    def test_preview_set_builds_from_hint_record_set(self) -> None:
        preview_set = self._valid_preview_set()
        validation = validate_task_working_memory_readback_hint_application_preview_set(
            preview_set
        )
        self.assertTrue(validation["valid"], validation["error_codes"])

    def test_preview_set_counts_ready_previews_correctly(self) -> None:
        self.assertEqual(self._valid_preview_set().ready_count, 2)

    def test_preview_set_counts_held_previews_correctly(self) -> None:
        self.assertEqual(self._valid_preview_set().held_count, 1)

    def test_preview_set_counts_blocked_previews_correctly(self) -> None:
        payload = build_demo_blocked_invalid_hint_record_application_preview_set()
        preview_set = TaskWorkingMemoryReadbackHintApplicationPreviewSet.from_dict(
            payload["task_working_memory_readback_hint_application_preview_set"]
        )
        self.assertEqual(preview_set.blocked_count, 3)

    def test_preview_set_status_with_ready_previews_when_at_least_one_ready(self) -> None:
        self.assertEqual(
            self._valid_preview_set().preview_set_status,
            "preview_set_created_with_ready_previews",
        )

    def test_preview_set_status_all_held_or_blocked_when_none_ready(self) -> None:
        payload = build_demo_all_held_task_working_memory_readback_hint_application_preview_set()
        preview_set = TaskWorkingMemoryReadbackHintApplicationPreviewSet.from_dict(
            payload["task_working_memory_readback_hint_application_preview_set"]
        )
        self.assertEqual(
            preview_set.preview_set_status,
            "preview_set_created_all_held_or_blocked",
        )

    def test_safety_audit_passes_for_valid_demo_preview_set(self) -> None:
        payload = build_demo_task_working_memory_readback_hint_application_preview_set()
        validation = validate_task_working_memory_readback_hint_application_preview_safety_audit(
            payload["task_working_memory_readback_hint_application_preview_safety_audit"]
        )
        self.assertTrue(validation["valid"], validation["error_codes"])

    def test_safety_audit_blocks_forbidden_active_hint_application(self) -> None:
        audit = self._audit_with_preview_flag("applied_to_working_memory", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_active_hint_application_detected",
        )

    def test_safety_audit_blocks_forbidden_working_memory_mutation(self) -> None:
        audit = self._audit_with_preview_flag("working_memory_mutated", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_working_memory_mutation_detected",
        )

    def test_safety_audit_blocks_forbidden_task_behavior_change(self) -> None:
        audit = self._audit_with_preview_flag("task_behavior_changed", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_behavior_change_detected",
        )

    def test_safety_audit_blocks_forbidden_candidate_ordering_change(self) -> None:
        audit = self._audit_with_preview_flag("candidate_ordering_changed", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_behavior_change_detected",
        )

    def test_safety_audit_blocks_forbidden_selected_action_change(self) -> None:
        audit = self._audit_with_preview_flag("selected_action_changed", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_action_authority_detected",
        )

    def test_safety_audit_blocks_forbidden_final_action_change(self) -> None:
        audit = self._audit_with_preview_flag("final_action_changed", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_action_authority_detected",
        )

    def test_safety_audit_blocks_forbidden_direct_command_change(self) -> None:
        audit = self._audit_with_preview_flag("direct_command_changed", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_action_authority_detected",
        )

    def test_safety_audit_blocks_forbidden_execution(self) -> None:
        audit = self._audit_with_preview_flag("execution_created", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_action_authority_detected",
        )

    def test_safety_audit_blocks_forbidden_memory_layer_write(self) -> None:
        audit = self._audit_with_preview_flag("memory_layer_write_performed", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_memory_write_detected",
        )

    def test_cli_preview_demo_application_works(self) -> None:
        result = self._run_task_cli("preview-demo-application")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("preview_set_created_with_ready_previews", result.stdout)

    def test_cli_show_demo_application_preview_works(self) -> None:
        result = self._run_task_cli("show-demo-application-preview")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("hint_application_preview_id", result.stdout)

    def test_cli_show_demo_safety_audit_works(self) -> None:
        result = self._run_task_cli("show-demo-safety-audit")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"audit_status": "passed"', result.stdout)

    def test_cli_validate_demo_application_preview_works(self) -> None:
        result = self._run_task_cli("validate-demo-application-preview")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"valid": true', result.stdout)

    def test_cli_all_held_works(self) -> None:
        result = self._run_task_cli("preview-demo-held", "--case", "all-held")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("preview_set_created_all_held_or_blocked", result.stdout)

    def test_cli_invalid_hint_record_blocked_works(self) -> None:
        result = self._run_task_cli(
            "preview-demo-blocked",
            "--case",
            "invalid-hint-record",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("blocked_invalid_hint_record", result.stdout)

    def test_cli_forbidden_authority_blocked_works(self) -> None:
        result = self._run_task_cli(
            "preview-demo-blocked",
            "--case",
            "forbidden-authority",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("blocked_forbidden", result.stdout)

    def test_guided_console_application_preview_demo_works(self) -> None:
        for command in (
            "task-preview-reviewed-concept-hint-application-demo",
            "task-show-reviewed-concept-hint-application-preview",
            "task-validate-reviewed-concept-hint-application-preview",
        ):
            result = self._run_guided_cli(command)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("guided_console_action", result.stdout)

    def test_no_repo_data_created(self) -> None:
        build_demo_task_working_memory_readback_hint_application_preview_set()
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _valid_payload(self) -> dict[str, object]:
        return build_demo_task_working_memory_readback_hint_application_preview_set()

    def _valid_record_payload(self) -> dict[str, object]:
        return build_demo_task_working_memory_readback_hint_record_set()

    def _valid_record_set(self) -> TaskWorkingMemoryReadbackHintRecordSet:
        return TaskWorkingMemoryReadbackHintRecordSet.from_dict(
            self._valid_record_payload()[
                "task_working_memory_readback_hint_record_set"
            ]
        )

    def _valid_record_safety_audit(self) -> TaskWorkingMemoryReadbackHintRecordSafetyAudit:
        return TaskWorkingMemoryReadbackHintRecordSafetyAudit.from_dict(
            self._valid_record_payload()[
                "task_working_memory_readback_hint_record_safety_audit"
            ]
        )

    def _valid_preview_set(self) -> TaskWorkingMemoryReadbackHintApplicationPreviewSet:
        return TaskWorkingMemoryReadbackHintApplicationPreviewSet.from_dict(
            self._valid_payload()[
                "task_working_memory_readback_hint_application_preview_set"
            ]
        )

    def _first_ready_preview(self) -> TaskWorkingMemoryReadbackHintApplicationPreview:
        return next(
            preview
            for preview in self._valid_preview_set().application_previews
            if preview.preview_status == "application_preview_ready"
        )

    def _preview_for_hint_record_demo(
        self,
        demo: str,
    ) -> TaskWorkingMemoryReadbackHintApplicationPreview:
        if demo == "valid":
            payload = build_demo_task_working_memory_readback_hint_application_preview_set()
        elif demo == "held":
            payload = build_task_working_memory_readback_hint_application_preview_bundle(
                build_demo_all_held_task_working_memory_readback_hint_record_set()
            )
        elif demo == "blocked":
            payload = build_task_working_memory_readback_hint_application_preview_bundle(
                build_demo_blocked_invalid_preparation_hint_record_set()
            )
        else:
            raise ValueError(demo)
        return TaskWorkingMemoryReadbackHintApplicationPreview.from_dict(
            payload["task_working_memory_readback_hint_application_previews"][0]
        )

    def _audit_with_preview_flag(
        self,
        flag_name: str,
        flag_value: bool,
    ) -> TaskWorkingMemoryReadbackHintApplicationPreviewSafetyAudit:
        payload = self._valid_payload()
        preview_set = TaskWorkingMemoryReadbackHintApplicationPreviewSet.from_dict(
            payload["task_working_memory_readback_hint_application_preview_set"]
        )
        previews = list(preview_set.application_previews)
        first = dict(previews[0].to_dict())
        first[flag_name] = flag_value
        previews[0] = TaskWorkingMemoryReadbackHintApplicationPreview.from_dict(first)
        preview_set = TaskWorkingMemoryReadbackHintApplicationPreviewSet.from_dict(
            {
                **preview_set.to_dict(),
                "application_previews": [preview.to_dict() for preview in previews],
            }
        )
        return build_task_working_memory_readback_hint_application_preview_safety_audit(
            task_working_memory_readback_hint_record_set=self._valid_record_set(),
            hint_record_safety_audit=self._valid_record_safety_audit(),
            application_preview_set=preview_set,
        )

    def _run_task_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core_v1.task.reviewed_concept_readback_hint_application_preview_cli",
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
