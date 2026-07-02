from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from ashl_core_v1.task.teacher_gated_direct_command_sandbox_execution import (
    DirectCommandApplicationRecord,
    DirectCommandSandboxExecutionAudit,
    SandboxExecutionRecord,
    SandboxExecutionRestoreRecord,
    SandboxPreExecutionSnapshot,
    TeacherGatedDirectCommandExecutionGate,
    apply_sandbox_execution_restore,
    build_demo_blocked_direct_command_sandbox_execution,
    build_demo_blocked_external_execution,
    build_demo_blocked_filesystem_execution,
    build_demo_blocked_memory_write_execution,
    build_demo_blocked_missing_restore_execution,
    build_demo_blocked_missing_snapshot_execution,
    build_demo_blocked_network_execution,
    build_demo_blocked_bridge_execution,
    build_demo_blocked_task_behavior_learning_execution,
    build_demo_blocked_unity_execution,
    build_demo_direct_command_sandbox_execution,
    build_direct_command_application_record,
    build_sandbox_pre_execution_snapshot,
    build_teacher_gated_direct_command_execution_gate,
    execute_bounded_sandbox_direct_command,
    map_final_action_to_direct_command,
    validate_direct_command_application_record,
    validate_direct_command_sandbox_execution_audit,
    validate_sandbox_execution_record,
    validate_sandbox_pre_execution_snapshot,
    validate_teacher_gated_direct_command_execution_gate,
)
from ashl_core_v1.task.teacher_gated_final_action_application import (
    FinalActionApplicationAudit,
    FinalActionApplicationRecord,
    build_demo_final_action_application,
)


TASK_CLI = "ashl_core_v1.task.teacher_gated_direct_command_sandbox_execution_cli"
GUIDED_CLI = "ashl_core_v1.runtime.guided_cradle_growth_teacher_console_cli"


class TeacherGatedDirectCommandSandboxExecutionTests(unittest.TestCase):
    def test_execution_gate_builds_from_valid_final_action_application(self) -> None:
        gate = self._gate()
        validation = validate_teacher_gated_direct_command_execution_gate(gate)
        self.assertTrue(validation["valid"])
        self.assertEqual(
            gate.teacher_gate_status,
            "approved_for_direct_command_and_bounded_sandbox_execution",
        )
        self.assertEqual(gate.final_action_candidate_id, "observe")
        self.assertEqual(gate.requested_direct_command, "observe")

    def test_execution_gate_requires_final_action_audit_pass(self) -> None:
        audit = FinalActionApplicationAudit.from_dict(
            {
                **self._final_action_audit().to_dict(),
                "audit_status": "failed_missing_rollback",
            }
        )
        gate = build_teacher_gated_direct_command_execution_gate(
            final_action_application=self._final_action(),
            final_action_application_audit=audit,
        )
        self.assertEqual(
            gate.teacher_gate_status,
            "blocked_invalid_final_action_audit",
        )

    def test_execution_gate_explicit_approval_requires_non_empty_text(self) -> None:
        gate = build_teacher_gated_direct_command_execution_gate(
            final_action_application=self._final_action(),
            final_action_application_audit=self._final_action_audit(),
            approval_source="explicit_teacher_review",
            approval_actor_role="teacher",
            teacher_gate_text="",
        )
        validation = validate_teacher_gated_direct_command_execution_gate(gate)
        self.assertIn("teacher_gate_text_required", validation["error_codes"])

    def test_execution_gate_explicit_approval_requires_teacher_or_project_owner(self) -> None:
        gate = build_teacher_gated_direct_command_execution_gate(
            final_action_application=self._final_action(),
            final_action_application_audit=self._final_action_audit(),
            approval_source="explicit_teacher_review",
            approval_actor_role="system_demo",
            teacher_gate_text="approved",
        )
        validation = validate_teacher_gated_direct_command_execution_gate(gate)
        self.assertIn("invalid_explicit_actor_role", validation["error_codes"])

    def test_execution_gate_demo_approval_requires_system_demo_role(self) -> None:
        gate = build_teacher_gated_direct_command_execution_gate(
            final_action_application=self._final_action(),
            final_action_application_audit=self._final_action_audit(),
            approval_source="demo_review",
            approval_actor_role="teacher",
        )
        validation = validate_teacher_gated_direct_command_execution_gate(gate)
        self.assertIn("demo_review_requires_system_demo_role", validation["error_codes"])

    def test_execution_gate_approves_direct_command_and_bounded_sandbox_only(self) -> None:
        gate = self._gate()
        self.assertTrue(gate.approved_for_direct_command)
        self.assertTrue(gate.approved_for_bounded_sandbox_execution)
        self.assertFalse(gate.approved_for_external_execution)
        self.assertFalse(gate.approved_for_unity_execution)
        self.assertFalse(gate.approved_for_bridge_execution)
        self.assertFalse(gate.approved_for_network_execution)
        self.assertFalse(gate.approved_for_filesystem_execution)
        self.assertFalse(gate.approved_for_task_behavior_learning)
        self.assertFalse(gate.approved_for_memory_layer_write)

    def test_final_action_to_direct_command_mapping_is_deterministic(self) -> None:
        expected = {
            "observe": "observe",
            "step_forward": "step_forward",
            "turn_left": "turn_left",
            "push_right": "push_right",
            "unsupported": None,
        }
        for final_action, direct_command in expected.items():
            with self.subTest(final_action=final_action):
                self.assertEqual(
                    map_final_action_to_direct_command(final_action),
                    direct_command,
                )

    def test_direct_command_application_builds_after_approved_gate(self) -> None:
        command = self._direct_command()
        validation = validate_direct_command_application_record(command)
        self.assertTrue(validation["valid"])
        self.assertEqual(command.direct_command_status, "direct_command_created")

    def test_direct_command_application_creates_observe_command_in_demo(self) -> None:
        command = self._direct_command()
        self.assertEqual(command.final_action_candidate_id, "observe")
        self.assertEqual(command.applied_direct_command, "observe")
        self.assertTrue(command.direct_command_created)
        self.assertTrue(command.available_for_bounded_sandbox_execution)

    def test_direct_command_application_blocks_invalid_inputs(self) -> None:
        expected = {
            "invalid-final-action": "blocked_invalid_final_action",
            "invalid-final-action-audit": "blocked_invalid_final_action",
            "missing-teacher-gate": "blocked_invalid_teacher_gate",
            "teacher-rejected": "rejected_by_teacher_gate",
            "unsupported-command": "blocked_unsupported_direct_command",
        }
        for case, status in expected.items():
            with self.subTest(case=case):
                payload = build_demo_blocked_direct_command_sandbox_execution(case)
                command = DirectCommandApplicationRecord.from_dict(
                    payload["direct_command_application"]
                )
                self.assertEqual(command.direct_command_status, status)
                self.assertFalse(command.direct_command_created)

    def test_pre_execution_snapshot_builds_before_execution(self) -> None:
        snapshot = self._snapshot()
        validation = validate_sandbox_pre_execution_snapshot(snapshot)
        self.assertTrue(validation["valid"])
        self.assertEqual(snapshot.snapshot_status, "snapshot_created")
        self.assertTrue(snapshot.snapshot_created)
        self.assertTrue(snapshot.restore_possible)
        self.assertFalse(snapshot.external_state_captured)
        self.assertFalse(snapshot.memory_layer_state_captured)

    def test_execution_blocks_if_snapshot_missing(self) -> None:
        payload = build_demo_blocked_missing_snapshot_execution()
        execution = SandboxExecutionRecord.from_dict(payload["sandbox_execution"])
        self.assertEqual(
            execution.execution_status,
            "blocked_missing_pre_execution_snapshot",
        )
        self.assertFalse(execution.execution_created)

    def test_sandbox_execution_executes_observe_in_bounded_sandbox(self) -> None:
        execution = self._execution()
        validation = validate_sandbox_execution_record(execution)
        self.assertTrue(validation["valid"])
        self.assertEqual(
            execution.execution_status,
            "bounded_sandbox_execution_completed",
        )
        self.assertEqual(execution.direct_command, "observe")
        self.assertEqual(execution.observed_outcome, "observed")
        self.assertTrue(execution.execution_created)
        self.assertTrue(execution.bounded_sandbox_execution_created)
        self.assertEqual(execution.sandbox_state_after_execution["observations"], 1)

    def test_sandbox_execution_forbidden_authority_flags_false(self) -> None:
        execution = self._execution()
        self.assertFalse(execution.external_execution_created)
        self.assertFalse(execution.unity_execution_created)
        self.assertFalse(execution.bridge_execution_created)
        self.assertFalse(execution.network_execution_created)
        self.assertFalse(execution.filesystem_execution_created)
        self.assertFalse(execution.task_behavior_learning_created)
        self.assertFalse(execution.memory_layer_write_performed)
        self.assertFalse(execution.automatic_learning_approval_created)
        self.assertFalse(execution.selected_action_changed_by_this_package)
        self.assertFalse(execution.final_action_changed_by_this_package)
        self.assertFalse(execution.direct_command_changed_by_execution)

    def test_restore_record_created_for_successful_execution(self) -> None:
        restore = self._restore()
        self.assertEqual(restore.restore_status, "restore_record_created")
        self.assertTrue(restore.restore_available)
        self.assertFalse(restore.restore_applied)
        self.assertEqual(restore.sandbox_state_after_execution["observations"], 1)

    def test_restore_record_restores_pre_execution_sandbox_state(self) -> None:
        result = apply_sandbox_execution_restore(self._restore())
        self.assertEqual(
            result["restore_status"],
            "restore_applied_to_pre_execution_sandbox_state",
        )
        self.assertEqual(result["sandbox_state_after_restore"]["observations"], 0)

    def test_restore_does_not_replay_or_change_action_records(self) -> None:
        restore = self._restore()
        result = apply_sandbox_execution_restore(restore)
        self.assertFalse(restore.external_state_restored)
        self.assertFalse(restore.memory_layer_state_restored)
        self.assertFalse(restore.selected_action_changed)
        self.assertFalse(restore.final_action_changed)
        self.assertFalse(restore.direct_command_changed)
        self.assertFalse(restore.execution_replayed)
        self.assertFalse(restore.task_behavior_learning_created)
        self.assertFalse(restore.memory_layer_write_performed)
        self.assertFalse(result["selected_action_changed"])
        self.assertFalse(result["final_action_changed"])
        self.assertFalse(result["direct_command_changed"])
        self.assertFalse(result["execution_replayed"])

    def test_audit_passes_valid_direct_command_sandbox_execution(self) -> None:
        audit = self._audit()
        validation = validate_direct_command_sandbox_execution_audit(audit)
        self.assertTrue(validation["valid"])
        self.assertEqual(
            audit.audit_status,
            "passed_direct_command_and_bounded_sandbox_execution",
        )

    def test_audit_confirms_direct_command_and_sandbox_boundaries(self) -> None:
        audit = self._audit()
        self.assertTrue(audit.direct_command_created)
        self.assertTrue(audit.bounded_sandbox_execution_created)
        self.assertTrue(audit.execution_created)
        self.assertTrue(audit.no_external_execution)
        self.assertTrue(audit.no_unity_execution)
        self.assertTrue(audit.no_bridge_execution)
        self.assertTrue(audit.no_network_execution)
        self.assertTrue(audit.no_filesystem_execution)
        self.assertTrue(audit.no_task_behavior_learning)
        self.assertTrue(audit.no_memory_layer_write)
        self.assertTrue(audit.no_automatic_learning_approval)

    def test_audit_fails_missing_snapshot_and_restore(self) -> None:
        expected = {
            build_demo_blocked_missing_snapshot_execution: "failed_missing_snapshot",
            build_demo_blocked_missing_restore_execution: "failed_missing_restore",
        }
        for builder, status in expected.items():
            with self.subTest(builder=builder.__name__):
                payload = builder()
                audit = DirectCommandSandboxExecutionAudit.from_dict(
                    payload["direct_command_sandbox_execution_audit"]
                )
                self.assertEqual(audit.audit_status, status)

    def test_audit_blocks_forbidden_execution_authority(self) -> None:
        expected = {
            build_demo_blocked_external_execution: "blocked_external_execution_detected",
            build_demo_blocked_unity_execution: "blocked_unity_execution_detected",
            build_demo_blocked_bridge_execution: "blocked_bridge_execution_detected",
            build_demo_blocked_network_execution: "blocked_network_execution_detected",
            build_demo_blocked_filesystem_execution: "blocked_filesystem_execution_detected",
            build_demo_blocked_task_behavior_learning_execution: (
                "blocked_task_behavior_learning_detected"
            ),
            build_demo_blocked_memory_write_execution: "blocked_memory_write_detected",
        }
        for builder, status in expected.items():
            with self.subTest(builder=builder.__name__):
                payload = builder()
                audit = DirectCommandSandboxExecutionAudit.from_dict(
                    payload["direct_command_sandbox_execution_audit"]
                )
                self.assertEqual(audit.audit_status, status)

    def test_cli_commands_work(self) -> None:
        commands = (
            "execute-demo-command",
            "show-demo-teacher-gate",
            "show-demo-direct-command",
            "show-demo-pre-execution-snapshot",
            "show-demo-execution",
            "show-demo-restore",
            "show-demo-audit",
            "validate-demo-execution",
            "restore-demo-sandbox",
        )
        for command in commands:
            with self.subTest(command=command):
                payload = self._run_task_cli(command)
                self.assertIsInstance(payload, dict)

    def test_cli_blocked_cases_work(self) -> None:
        cases = (
            "invalid-final-action",
            "invalid-final-action-audit",
            "missing-teacher-gate",
            "teacher-rejected",
            "unsupported-command",
            "missing-snapshot",
            "missing-restore",
            "external-execution",
            "unity-execution",
            "bridge-execution",
            "network-execution",
            "filesystem-execution",
            "task-behavior-learning",
            "memory-write-detected",
        )
        for case in cases:
            with self.subTest(case=case):
                payload = self._run_task_cli("execute-demo-blocked", "--case", case)
                self.assertIn("direct_command_sandbox_execution_audit", payload)

    def test_guided_console_direct_command_sandbox_execution_demo_works(self) -> None:
        payload = self._run_guided_cli("task-execute-direct-command-demo")
        self.assertEqual(
            payload["direct_command_application"]["applied_direct_command"],
            "observe",
        )
        self.assertTrue(payload["direct_command_created"])
        self.assertTrue(payload["bounded_sandbox_execution_created"])
        self.assertFalse(payload["external_execution_created"])
        self.assertFalse(payload["memory_layer_write_performed"])

    def test_guided_console_direct_command_sandbox_execution_views_work(self) -> None:
        commands = (
            "task-show-direct-command-execution-teacher-gate",
            "task-show-direct-command",
            "task-show-pre-execution-snapshot",
            "task-show-sandbox-execution",
            "task-show-sandbox-restore",
            "task-show-direct-command-execution-audit",
            "task-validate-direct-command-execution",
            "task-restore-sandbox-execution-demo",
        )
        for command in commands:
            with self.subTest(command=command):
                payload = self._run_guided_cli(command)
                self.assertFalse(payload.get("external_execution_created", False))
                self.assertFalse(payload.get("unity_execution_created", False))
                self.assertFalse(payload.get("bridge_execution_created", False))
                self.assertFalse(payload.get("network_execution_created", False))
                self.assertFalse(payload.get("filesystem_execution_created", False))
                self.assertFalse(payload.get("memory_layer_write_performed", False))

    def test_no_repo_data_dir_created(self) -> None:
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def test_core_functions_can_build_records_directly(self) -> None:
        command = build_direct_command_application_record(execution_gate=self._gate())
        snapshot = build_sandbox_pre_execution_snapshot(
            direct_command_application=command,
            sandbox_state={"observations": 0},
        )
        execution = execute_bounded_sandbox_direct_command(
            direct_command_application=command,
            pre_execution_snapshot=snapshot,
            execution_gate=self._gate(),
        )
        self.assertEqual(command.applied_direct_command, "observe")
        self.assertEqual(snapshot.snapshot_status, "snapshot_created")
        self.assertEqual(execution.observed_outcome, "observed")

    def _payload(self) -> dict[str, object]:
        return build_demo_direct_command_sandbox_execution()

    def _gate(self) -> TeacherGatedDirectCommandExecutionGate:
        return TeacherGatedDirectCommandExecutionGate.from_dict(
            self._payload()["direct_command_execution_gate"]
        )

    def _direct_command(self) -> DirectCommandApplicationRecord:
        return DirectCommandApplicationRecord.from_dict(
            self._payload()["direct_command_application"]
        )

    def _snapshot(self) -> SandboxPreExecutionSnapshot:
        return SandboxPreExecutionSnapshot.from_dict(
            self._payload()["sandbox_pre_execution_snapshot"]
        )

    def _execution(self) -> SandboxExecutionRecord:
        return SandboxExecutionRecord.from_dict(self._payload()["sandbox_execution"])

    def _restore(self) -> SandboxExecutionRestoreRecord:
        return SandboxExecutionRestoreRecord.from_dict(
            self._payload()["sandbox_execution_restore"]
        )

    def _audit(self) -> DirectCommandSandboxExecutionAudit:
        return DirectCommandSandboxExecutionAudit.from_dict(
            self._payload()["direct_command_sandbox_execution_audit"]
        )

    def _final_action_payload(self) -> dict[str, object]:
        return build_demo_final_action_application()

    def _final_action(self) -> FinalActionApplicationRecord:
        return FinalActionApplicationRecord.from_dict(
            self._final_action_payload()["final_action_application"]
        )

    def _final_action_audit(self) -> FinalActionApplicationAudit:
        return FinalActionApplicationAudit.from_dict(
            self._final_action_payload()["final_action_application_audit"]
        )

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
