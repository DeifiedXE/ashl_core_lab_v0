from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from ashl_core_v1.task.teacher_gated_selected_action_application import (
    SelectedActionApplicationAudit,
    SelectedActionApplicationRecord,
    SelectedActionRollbackRecord,
    TeacherGatedSelectedActionApplicationGate,
    apply_selected_action_rollback,
    apply_teacher_gated_selected_action,
    build_demo_blocked_direct_command_created_application,
    build_demo_blocked_execution_created_application,
    build_demo_blocked_final_action_mutated_application,
    build_demo_blocked_invalid_proposal_audit_selected_action_application,
    build_demo_blocked_invalid_proposal_selected_action_application,
    build_demo_blocked_memory_write_selected_action_application,
    build_demo_blocked_missing_rollback_selected_action_application,
    build_demo_blocked_missing_teacher_gate_selected_action_application,
    build_demo_blocked_running_task_mutation_selected_action_application,
    build_demo_blocked_selected_action_mismatch_application,
    build_demo_blocked_task_behavior_changed_application,
    build_demo_blocked_teacher_rejected_selected_action_application,
    build_demo_selected_action_application,
    build_selected_action_rollback_record,
    build_teacher_gated_selected_action_application_gate,
    validate_selected_action_application_audit,
    validate_teacher_gated_selected_action_application_gate,
)
from ashl_core_v1.task.teacher_gated_selected_action_proposal import (
    SelectedActionProposalAudit,
    SelectedActionProposalRecord,
    build_demo_selected_action_proposal,
)


TASK_CLI = "ashl_core_v1.task.teacher_gated_selected_action_application_cli"
GUIDED_CLI = "ashl_core_v1.runtime.guided_cradle_growth_teacher_console_cli"


class TeacherGatedSelectedActionApplicationTests(unittest.TestCase):
    def test_application_gate_builds_from_valid_selected_action_proposal(self) -> None:
        gate = self._gate()
        validation = validate_teacher_gated_selected_action_application_gate(gate)
        self.assertTrue(validation["valid"])
        self.assertEqual(gate.teacher_gate_status, "approved_for_actual_selected_action")
        self.assertEqual(gate.proposed_selected_action_candidate_id, "observe")

    def test_application_gate_requires_proposal_audit_pass(self) -> None:
        audit = SelectedActionProposalAudit.from_dict(
            {
                **self._proposal_audit().to_dict(),
                "audit_status": "failed_missing_rollback",
            }
        )
        gate = build_teacher_gated_selected_action_application_gate(
            selected_action_proposal=self._proposal(),
            selected_action_proposal_audit=audit,
        )
        self.assertEqual(
            gate.teacher_gate_status,
            "blocked_invalid_selected_action_proposal_audit",
        )

    def test_application_gate_explicit_approval_requires_non_empty_text(self) -> None:
        gate = build_teacher_gated_selected_action_application_gate(
            selected_action_proposal=self._proposal(),
            selected_action_proposal_audit=self._proposal_audit(),
            approval_source="explicit_teacher_review",
            approval_actor_role="teacher",
            teacher_gate_text="",
        )
        validation = validate_teacher_gated_selected_action_application_gate(gate)
        self.assertIn("teacher_gate_text_required", validation["error_codes"])

    def test_application_gate_explicit_approval_requires_teacher_or_project_owner(self) -> None:
        gate = build_teacher_gated_selected_action_application_gate(
            selected_action_proposal=self._proposal(),
            selected_action_proposal_audit=self._proposal_audit(),
            approval_source="explicit_teacher_review",
            approval_actor_role="system_demo",
            teacher_gate_text="approved",
        )
        validation = validate_teacher_gated_selected_action_application_gate(gate)
        self.assertIn("invalid_explicit_actor_role", validation["error_codes"])

    def test_application_gate_demo_approval_requires_system_demo_role(self) -> None:
        gate = build_teacher_gated_selected_action_application_gate(
            selected_action_proposal=self._proposal(),
            selected_action_proposal_audit=self._proposal_audit(),
            approval_source="demo_review",
            approval_actor_role="teacher",
        )
        validation = validate_teacher_gated_selected_action_application_gate(gate)
        self.assertIn("demo_review_requires_system_demo_role", validation["error_codes"])

    def test_application_gate_approves_actual_selected_action_only(self) -> None:
        gate = self._gate()
        self.assertTrue(gate.approved_for_actual_selected_action)
        self.assertFalse(gate.approved_for_final_action)
        self.assertFalse(gate.approved_for_direct_command)
        self.assertFalse(gate.approved_for_execution)
        self.assertFalse(gate.approved_for_task_behavior_change)
        self.assertFalse(gate.approved_for_memory_layer_write)

    def test_selected_action_application_builds_after_approved_gate(self) -> None:
        application = apply_teacher_gated_selected_action(application_gate=self._gate())
        self.assertEqual(
            application.selected_action_application_status,
            "selected_action_applied",
        )

    def test_selected_action_application_uses_proposed_candidate_id(self) -> None:
        application = self._application()
        self.assertEqual(application.applied_selected_action_candidate_id, "observe")
        self.assertTrue(application.actual_selected_action_changed)

    def test_selected_action_application_forbidden_authority_flags_false(self) -> None:
        application = self._application()
        self.assertFalse(application.final_action_changed)
        self.assertFalse(application.direct_command_created)
        self.assertFalse(application.execution_created)
        self.assertFalse(application.task_behavior_changed)
        self.assertFalse(application.candidate_ordering_changed_by_this_package)
        self.assertFalse(application.memory_layer_write_performed)
        self.assertTrue(application.available_for_future_final_action_review)
        self.assertTrue(application.requires_teacher_gate_before_final_action)

    def test_selected_action_application_blocks_invalid_proposal(self) -> None:
        self._assert_application_status(
            build_demo_blocked_invalid_proposal_selected_action_application,
            "blocked_invalid_selected_action_proposal",
        )

    def test_selected_action_application_blocks_invalid_proposal_audit(self) -> None:
        self._assert_application_status(
            build_demo_blocked_invalid_proposal_audit_selected_action_application,
            "blocked_invalid_selected_action_proposal",
        )

    def test_selected_action_application_blocks_missing_teacher_gate(self) -> None:
        self._assert_application_status(
            build_demo_blocked_missing_teacher_gate_selected_action_application,
            "blocked_invalid_teacher_gate",
        )

    def test_selected_action_application_blocks_teacher_rejected(self) -> None:
        self._assert_application_status(
            build_demo_blocked_teacher_rejected_selected_action_application,
            "rejected_by_teacher_gate",
        )

    def test_selected_action_application_blocks_running_task_mutation(self) -> None:
        self._assert_application_status(
            build_demo_blocked_running_task_mutation_selected_action_application,
            "blocked_running_task_mutation_attempt",
        )

    def test_selected_action_application_blocks_selected_action_mismatch(self) -> None:
        self._assert_application_status(
            build_demo_blocked_selected_action_mismatch_application,
            "blocked_forbidden_authority_detected",
        )

    def test_selected_action_application_blocks_forbidden_mutations(self) -> None:
        cases = (
            build_demo_blocked_final_action_mutated_application,
            build_demo_blocked_direct_command_created_application,
            build_demo_blocked_execution_created_application,
            build_demo_blocked_task_behavior_changed_application,
            build_demo_blocked_memory_write_selected_action_application,
        )
        for builder in cases:
            with self.subTest(builder=builder.__name__):
                self._assert_application_status(
                    builder,
                    "blocked_forbidden_authority_detected",
                )

    def test_rollback_record_created_for_successful_application(self) -> None:
        rollback = self._rollback()
        self.assertEqual(rollback.rollback_status, "rollback_record_created")
        self.assertTrue(rollback.rollback_available)
        self.assertEqual(rollback.selected_action_after_application, "observe")

    def test_rollback_record_restores_previous_selected_action(self) -> None:
        application = apply_teacher_gated_selected_action(
            application_gate=self._gate(),
            previous_selected_action_candidate_id="previous_observe",
        )
        rollback = build_selected_action_rollback_record(
            selected_action_application=application,
            rollback_applied=True,
        )
        self.assertEqual(
            rollback.rollback_status,
            "rollback_applied_to_restore_previous_selected_action",
        )
        self.assertEqual(
            rollback.selected_action_after_rollback,
            "previous_observe",
        )

    def test_rollback_does_not_create_action_path(self) -> None:
        rollback = self._rollback()
        result = apply_selected_action_rollback(rollback)
        self.assertFalse(rollback.final_action_changed)
        self.assertFalse(rollback.direct_command_created)
        self.assertFalse(rollback.execution_created)
        self.assertFalse(rollback.task_behavior_changed)
        self.assertFalse(rollback.memory_layer_write_performed)
        self.assertFalse(result["final_action_changed"])
        self.assertFalse(result["execution_created"])

    def test_application_audit_passes_valid_selected_action_application(self) -> None:
        audit = self._audit()
        validation = validate_selected_action_application_audit(audit)
        self.assertTrue(validation["valid"])
        self.assertEqual(audit.audit_status, "passed_selected_action_applied")

    def test_application_audit_confirms_boundaries(self) -> None:
        audit = self._audit()
        self.assertTrue(audit.actual_selected_action_changed)
        self.assertFalse(audit.final_action_changed)
        self.assertFalse(audit.direct_command_created)
        self.assertFalse(audit.execution_created)
        self.assertFalse(audit.task_behavior_changed)
        self.assertFalse(audit.candidate_ordering_changed_by_this_package)
        self.assertTrue(audit.no_memory_layer_write)

    def test_application_audit_fails_missing_rollback(self) -> None:
        payload = build_demo_blocked_missing_rollback_selected_action_application()
        audit = SelectedActionApplicationAudit.from_dict(
            payload["selected_action_application_audit"]
        )
        self.assertEqual(audit.audit_status, "failed_missing_rollback")

    def test_application_audit_blocks_forbidden_authority(self) -> None:
        expected = {
            "running-task-mutation": "blocked_running_task_mutation_detected",
            "final-action-mutated": "blocked_final_action_change_detected",
            "direct-command-created": "blocked_direct_command_detected",
            "execution-created": "blocked_execution_detected",
            "task-behavior-changed": "blocked_task_behavior_change_detected",
            "memory-write-detected": "blocked_memory_write_detected",
        }
        for case, status in expected.items():
            with self.subTest(case=case):
                payload = self._run_task_cli("apply-demo-blocked", "--case", case)
                self.assertEqual(
                    payload["selected_action_application_audit"]["audit_status"],
                    status,
                )

    def test_cli_commands_work(self) -> None:
        commands = (
            "apply-demo-selected-action",
            "show-demo-teacher-gate",
            "show-demo-application",
            "show-demo-rollback",
            "show-demo-audit",
            "validate-demo-application",
            "rollback-demo-selected-action",
        )
        for command in commands:
            with self.subTest(command=command):
                payload = self._run_task_cli(command)
                self.assertIsInstance(payload, dict)

    def test_cli_blocked_cases_work(self) -> None:
        cases = (
            "invalid-proposal",
            "invalid-proposal-audit",
            "missing-teacher-gate",
            "teacher-rejected",
            "running-task-mutation",
            "selected-action-mismatch",
            "final-action-mutated",
            "execution-created",
            "missing-rollback",
            "memory-write-detected",
        )
        for case in cases:
            with self.subTest(case=case):
                payload = self._run_task_cli("apply-demo-blocked", "--case", case)
                self.assertIn("selected_action_application_audit", payload)

    def test_guided_console_selected_action_application_demo_works(self) -> None:
        payload = self._run_guided_cli("task-apply-selected-action-demo")
        self.assertEqual(
            payload["selected_action_application"]["applied_selected_action_candidate_id"],
            "observe",
        )
        self.assertTrue(payload["actual_selected_action_changed"])
        self.assertFalse(payload["final_action_changed"])
        self.assertFalse(payload["execution_created"])

    def test_guided_console_selected_action_application_views_work(self) -> None:
        commands = (
            "task-show-selected-action-application-teacher-gate",
            "task-show-selected-action-application",
            "task-show-selected-action-rollback",
            "task-show-selected-action-application-audit",
            "task-validate-selected-action-application",
            "task-rollback-selected-action-demo",
        )
        for command in commands:
            with self.subTest(command=command):
                payload = self._run_guided_cli(command)
                self.assertFalse(payload.get("final_action_changed", False))
                self.assertFalse(payload.get("execution_created", False))

    def test_no_repo_data_dir_created(self) -> None:
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _payload(self) -> dict[str, object]:
        return build_demo_selected_action_application()

    def _gate(self) -> TeacherGatedSelectedActionApplicationGate:
        return TeacherGatedSelectedActionApplicationGate.from_dict(
            self._payload()["selected_action_application_gate"]
        )

    def _application(self) -> SelectedActionApplicationRecord:
        return SelectedActionApplicationRecord.from_dict(
            self._payload()["selected_action_application"]
        )

    def _rollback(self) -> SelectedActionRollbackRecord:
        return SelectedActionRollbackRecord.from_dict(
            self._payload()["selected_action_rollback"]
        )

    def _audit(self) -> SelectedActionApplicationAudit:
        return SelectedActionApplicationAudit.from_dict(
            self._payload()["selected_action_application_audit"]
        )

    def _proposal_payload(self) -> dict[str, object]:
        return build_demo_selected_action_proposal()

    def _proposal(self) -> SelectedActionProposalRecord:
        return SelectedActionProposalRecord.from_dict(
            self._proposal_payload()["selected_action_proposal"]
        )

    def _proposal_audit(self) -> SelectedActionProposalAudit:
        return SelectedActionProposalAudit.from_dict(
            self._proposal_payload()["selected_action_proposal_audit"]
        )

    def _assert_application_status(self, builder, expected_status: str) -> None:
        payload = builder()
        application = SelectedActionApplicationRecord.from_dict(
            payload["selected_action_application"]
        )
        self.assertEqual(application.selected_action_application_status, expected_status)

    def _run_task_cli(self, *args: str) -> dict[str, object]:
        result = subprocess.run(
            [sys.executable, "-m", TASK_CLI, *args],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(result.stdout)

    def _run_guided_cli(self, *args: str) -> dict[str, object]:
        result = subprocess.run(
            [sys.executable, "-m", GUIDED_CLI, *args],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(result.stdout)


if __name__ == "__main__":
    unittest.main()
