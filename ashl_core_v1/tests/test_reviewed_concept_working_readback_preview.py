from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from ashl_core_v1.memory.reviewed_concept_candidate_admission_review import (
    build_demo_reviewed_concept_memory_admission,
)
from ashl_core_v1.memory.reviewed_concept_working_readback_preview import (
    ReviewedConceptWorkingReadbackHintPreview,
    ReviewedConceptWorkingReadbackPreview,
    ReviewedConceptWorkingReadbackPreviewSafetyAudit,
    build_demo_blocked_forbidden_readback_hint_preview,
    build_demo_blocked_forbidden_working_memory_mutation_preview,
    build_demo_blocked_invalid_application_data_readback_preview,
    build_demo_held_for_more_evidence_readback_preview,
    build_demo_reviewed_concept_working_readback_hint_preview,
    build_demo_reviewed_concept_working_readback_preview,
    build_demo_reviewed_concept_working_readback_preview_bundle,
    build_reviewed_concept_working_readback_preview,
    build_reviewed_concept_working_readback_preview_safety_audit,
    validate_reviewed_concept_working_readback_hint_preview,
    validate_reviewed_concept_working_readback_preview,
    validate_reviewed_concept_working_readback_preview_safety_audit,
)


class ReviewedConceptWorkingReadbackPreviewTests(unittest.TestCase):
    def test_working_readback_preview_builds_from_valid_memory_application_data(self) -> None:
        preview = self._valid_readback_preview()
        validation = validate_reviewed_concept_working_readback_preview(preview)
        self.assertTrue(validation["valid"], validation["error_codes"])

    def test_working_readback_preview_preserves_reviewed_concept_id(self) -> None:
        preview = self._valid_readback_preview()
        self.assertTrue(preview.source_reviewed_concept_id.startswith("reviewed_concept:"))

    def test_working_readback_preview_preserves_memory_application_data_id(self) -> None:
        admission = build_demo_reviewed_concept_memory_admission()
        preview = build_reviewed_concept_working_readback_preview(
            memory_learning_trace=admission["memory_learning_trace"],
            memory_routing_trace=admission["memory_routing_trace"],
            memory_application_data=admission["memory_application_data"],
            admission_review=admission["admission_review"],
            admission_safety_audit=admission["admission_safety_audit"],
        )
        self.assertEqual(
            preview.source_memory_application_data_id,
            admission["memory_application_data"]["memory_application_data_id"],
        )

    def test_working_readback_preview_status_preview_ready_for_valid_demo(self) -> None:
        self.assertEqual(self._valid_readback_preview().preview_status, "preview_ready")

    def test_working_readback_preview_available_for_future_hint_package_true(self) -> None:
        self.assertTrue(
            self._valid_readback_preview().available_for_future_working_memory_hint_package
        )

    def test_working_readback_preview_authority_flags_false(self) -> None:
        preview = self._valid_readback_preview()
        self.assertFalse(preview.actual_readback_hint_created)
        self.assertFalse(preview.working_memory_mutated)
        self.assertFalse(preview.task_behavior_changed)
        self.assertFalse(preview.memory_layer_write_performed)
        self.assertFalse(preview.automatic_learning_approval_created)

    def test_hint_preview_builds_from_valid_readback_preview(self) -> None:
        hint = self._valid_hint_preview()
        validation = validate_reviewed_concept_working_readback_hint_preview(hint)
        self.assertTrue(validation["valid"], validation["error_codes"])

    def test_hint_preview_includes_observe_before_direct_retry_for_front_blocked(self) -> None:
        self.assertIn(
            "observe_before_direct_retry",
            self._valid_hint_preview().hint_labels,
        )

    def test_hint_preview_includes_avoid_same_failed_direct_retry_for_front_blocked(self) -> None:
        self.assertIn(
            "avoid_same_failed_direct_retry",
            self._valid_hint_preview().hint_labels,
        )

    def test_hint_preview_includes_verify_obstacle_type_before_generalizing(self) -> None:
        self.assertIn(
            "verify_obstacle_type_before_generalizing",
            self._valid_hint_preview().hint_labels,
        )

    def test_hint_preview_authority_flags_false(self) -> None:
        hint = self._valid_hint_preview()
        self.assertFalse(hint.actual_task_working_memory_hint_created)
        self.assertFalse(hint.applied_to_working_memory)
        self.assertFalse(hint.task_behavior_changed)
        self.assertFalse(hint.candidate_ordering_changed)
        self.assertFalse(hint.action_selection_created)
        self.assertFalse(hint.action_execution_created)

    def test_counterexample_warnings_are_preserved(self) -> None:
        hint = self._valid_hint_preview()
        self.assertIn("front_blocked + step_forward succeeds", hint.counterexample_warnings[0])

    def test_scope_warnings_are_preserved(self) -> None:
        hint = self._valid_hint_preview()
        self.assertIn("front_blocked may be too broad", hint.scope_warnings[0])

    def test_held_for_more_evidence_demo_creates_held_preview(self) -> None:
        payload = build_demo_held_for_more_evidence_readback_preview()
        preview = ReviewedConceptWorkingReadbackPreview.from_dict(
            payload["working_readback_preview"]
        )
        hint = ReviewedConceptWorkingReadbackHintPreview.from_dict(
            payload["working_readback_hint_preview"]
        )
        self.assertEqual(preview.preview_status, "held_for_more_evidence")
        self.assertEqual(hint.hint_preview_status, "held_for_more_evidence")

    def test_invalid_application_data_blocks_preview(self) -> None:
        payload = build_demo_blocked_invalid_application_data_readback_preview()
        preview = ReviewedConceptWorkingReadbackPreview.from_dict(
            payload["working_readback_preview"]
        )
        self.assertEqual(preview.preview_status, "blocked_invalid_memory_application_data")

    def test_forbidden_actual_readback_hint_flag_blocks_safety_audit(self) -> None:
        audit = self._audit_with_preview_flag("actual_readback_hint_created", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_readback_hint_detected",
        )

    def test_forbidden_task_working_memory_hint_flag_blocks_safety_audit(self) -> None:
        audit = self._audit_with_hint_flag("actual_task_working_memory_hint_created", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_readback_hint_detected",
        )

    def test_forbidden_working_memory_mutation_flag_blocks_safety_audit(self) -> None:
        audit = self._audit_with_preview_flag("working_memory_mutated", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_working_memory_mutation_detected",
        )

    def test_forbidden_task_behavior_change_flag_blocks_safety_audit(self) -> None:
        audit = self._audit_with_hint_flag("task_behavior_changed", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_behavior_change_detected",
        )

    def test_forbidden_candidate_ordering_change_flag_blocks_safety_audit(self) -> None:
        audit = self._audit_with_hint_flag("candidate_ordering_changed", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_behavior_change_detected",
        )

    def test_forbidden_action_selection_flag_blocks_safety_audit(self) -> None:
        audit = self._audit_with_hint_flag("action_selection_created", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_behavior_change_detected",
        )

    def test_forbidden_action_execution_flag_blocks_safety_audit(self) -> None:
        audit = self._audit_with_hint_flag("action_execution_created", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_behavior_change_detected",
        )

    def test_forbidden_memory_layer_write_flag_blocks_safety_audit(self) -> None:
        audit = self._audit_with_preview_flag("memory_layer_write_performed", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_memory_write_detected",
        )

    def test_blocked_forbidden_readback_hint_demo_blocks(self) -> None:
        payload = build_demo_blocked_forbidden_readback_hint_preview()
        audit = ReviewedConceptWorkingReadbackPreviewSafetyAudit.from_dict(
            payload["working_readback_preview_safety_audit"]
        )
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_readback_hint_detected",
        )

    def test_blocked_forbidden_working_memory_mutation_demo_blocks(self) -> None:
        payload = build_demo_blocked_forbidden_working_memory_mutation_preview()
        audit = ReviewedConceptWorkingReadbackPreviewSafetyAudit.from_dict(
            payload["working_readback_preview_safety_audit"]
        )
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_working_memory_mutation_detected",
        )

    def test_safety_audit_passes_for_valid_preview_chain(self) -> None:
        audit = self._valid_safety_audit()
        validation = validate_reviewed_concept_working_readback_preview_safety_audit(
            audit
        )
        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(audit.audit_status, "passed")

    def test_cli_preview_demo_readback_works(self) -> None:
        result = self._run_memory_cli("preview-demo-readback")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("preview_ready", result.stdout)

    def test_cli_show_demo_readback_preview_works(self) -> None:
        result = self._run_memory_cli("show-demo-readback-preview")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("working_readback_preview_id", result.stdout)

    def test_cli_show_demo_hint_preview_works(self) -> None:
        result = self._run_memory_cli("show-demo-hint-preview")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("observe_before_direct_retry", result.stdout)

    def test_cli_validate_demo_readback_preview_works(self) -> None:
        result = self._run_memory_cli("validate-demo-readback-preview")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"valid": true', result.stdout)

    def test_cli_held_more_evidence_works(self) -> None:
        result = self._run_memory_cli("preview-demo-held", "--case", "more-evidence")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("held_for_more_evidence", result.stdout)

    def test_cli_blocked_invalid_application_data_works(self) -> None:
        result = self._run_memory_cli(
            "preview-demo-blocked",
            "--case",
            "invalid-application-data",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("blocked_invalid_memory_application_data", result.stdout)

    def test_cli_blocked_forbidden_readback_hint_works(self) -> None:
        result = self._run_memory_cli(
            "preview-demo-blocked",
            "--case",
            "forbidden-readback-hint",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("blocked_forbidden_readback_hint_detected", result.stdout)

    def test_cli_blocked_forbidden_working_memory_mutation_works(self) -> None:
        result = self._run_memory_cli(
            "preview-demo-blocked",
            "--case",
            "forbidden-working-memory-mutation",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "blocked_forbidden_working_memory_mutation_detected",
            result.stdout,
        )

    def test_guided_console_readback_preview_demo_works(self) -> None:
        for command in (
            "memory-preview-reviewed-concept-readback-demo",
            "memory-show-reviewed-concept-readback-preview",
            "memory-show-reviewed-concept-hint-preview",
            "memory-validate-reviewed-concept-readback-preview",
        ):
            result = self._run_guided_cli(command)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("guided_console_action", result.stdout)

    def test_no_repo_data_created(self) -> None:
        build_demo_reviewed_concept_working_readback_preview_bundle()
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _valid_payload(self) -> dict[str, object]:
        return build_demo_reviewed_concept_working_readback_preview_bundle()

    def _valid_readback_preview(self) -> ReviewedConceptWorkingReadbackPreview:
        return build_demo_reviewed_concept_working_readback_preview()

    def _valid_hint_preview(self) -> ReviewedConceptWorkingReadbackHintPreview:
        return build_demo_reviewed_concept_working_readback_hint_preview()

    def _valid_safety_audit(self) -> ReviewedConceptWorkingReadbackPreviewSafetyAudit:
        return ReviewedConceptWorkingReadbackPreviewSafetyAudit.from_dict(
            self._valid_payload()["working_readback_preview_safety_audit"]
        )

    def _audit_with_preview_flag(
        self,
        flag_name: str,
        flag_value: bool,
    ) -> ReviewedConceptWorkingReadbackPreviewSafetyAudit:
        payload = self._valid_payload()
        preview_data = dict(payload["working_readback_preview"])
        preview_data[flag_name] = flag_value
        preview = ReviewedConceptWorkingReadbackPreview.from_dict(preview_data)
        hint = ReviewedConceptWorkingReadbackHintPreview.from_dict(
            payload["working_readback_hint_preview"]
        )
        admission = build_demo_reviewed_concept_memory_admission()
        return build_reviewed_concept_working_readback_preview_safety_audit(
            memory_application_data=admission["memory_application_data"],
            admission_safety_audit=admission["admission_safety_audit"],
            readback_preview=preview,
            hint_preview=hint,
        )

    def _audit_with_hint_flag(
        self,
        flag_name: str,
        flag_value: bool,
    ) -> ReviewedConceptWorkingReadbackPreviewSafetyAudit:
        payload = self._valid_payload()
        hint_data = dict(payload["working_readback_hint_preview"])
        hint_data[flag_name] = flag_value
        hint = ReviewedConceptWorkingReadbackHintPreview.from_dict(hint_data)
        admission = build_demo_reviewed_concept_memory_admission()
        return build_reviewed_concept_working_readback_preview_safety_audit(
            memory_application_data=admission["memory_application_data"],
            admission_safety_audit=admission["admission_safety_audit"],
            readback_preview=payload["working_readback_preview"],
            hint_preview=hint,
        )

    def _run_memory_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core_v1.memory.reviewed_concept_working_readback_preview_cli",
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
