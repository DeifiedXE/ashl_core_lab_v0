from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from ashl_core_v1.audit.reviewed_concept_readback_loop_milestone_audit import (
    ReviewedConceptReadbackLoopMilestoneAudit,
    build_demo_blocked_missing_influence_audit_milestone,
    build_demo_reviewed_concept_readback_loop_milestone,
)
from ashl_core_v1.task.advisory_readback_candidate_ordering_application import (
    AdvisoryReadbackCandidateOrderingApplicationAudit,
    AdvisoryReadbackCandidateOrderingApplicationRecord,
    AdvisoryReadbackCandidateOrderingRollbackRecord,
    AdvisoryReadbackCandidateOrderingTeacherGate,
    apply_advisory_readback_candidate_ordering_rollback,
    apply_teacher_gated_advisory_readback_candidate_ordering,
    build_advisory_readback_candidate_ordering_application_audit,
    build_advisory_readback_candidate_ordering_teacher_gate,
    build_demo_blocked_candidate_created_ordering_application,
    build_demo_blocked_candidate_deleted_ordering_application,
    build_demo_blocked_direct_command_created_ordering_application,
    build_demo_blocked_execution_created_ordering_application,
    build_demo_blocked_final_action_changed_ordering_application,
    build_demo_blocked_invalid_milestone_ordering_application,
    build_demo_blocked_memory_write_ordering_application,
    build_demo_blocked_missing_rollback_ordering_application,
    build_demo_blocked_missing_teacher_gate_ordering_application,
    build_demo_blocked_running_task_mutation_ordering_application,
    build_demo_blocked_selected_action_changed_ordering_application,
    build_demo_blocked_task_behavior_changed_ordering_application,
    build_demo_blocked_teacher_rejected_ordering_application,
    build_demo_teacher_gated_ordering_application,
    compute_advisory_readback_ordering,
    validate_advisory_readback_candidate_ordering_application_audit,
    validate_advisory_readback_candidate_ordering_application_record,
    validate_advisory_readback_candidate_ordering_teacher_gate,
)
from ashl_core_v1.task.future_task_working_memory_readback_hint_application import (
    FutureTaskWorkingMemoryInitializationReadbackSnapshot,
    build_demo_future_task_working_memory_readback_hint_application_set,
)


TASK_CLI = "ashl_core_v1.task.advisory_readback_candidate_ordering_application_cli"
GUIDED_CLI = "ashl_core_v1.runtime.guided_cradle_growth_teacher_console_cli"


class AdvisoryReadbackCandidateOrderingApplicationTests(unittest.TestCase):
    def test_teacher_gate_builds_from_valid_milestone_and_readback_hints(self) -> None:
        gate = self._teacher_gate()
        validation = validate_advisory_readback_candidate_ordering_teacher_gate(gate)
        self.assertTrue(validation["valid"])
        self.assertEqual(
            gate.teacher_gate_status,
            "approved_for_candidate_ordering_change",
        )

    def test_teacher_gate_requires_package_80_milestone_pass(self) -> None:
        payload = build_demo_blocked_missing_influence_audit_milestone()
        milestone = ReviewedConceptReadbackLoopMilestoneAudit.from_dict(
            payload["milestone_audit"]
        )
        gate = build_advisory_readback_candidate_ordering_teacher_gate(
            milestone_audit=milestone,
            readback_snapshot=self._snapshot(),
            baseline_candidate_ordering=("step_forward", "observe", "turn_left"),
        )
        self.assertEqual(gate.teacher_gate_status, "blocked_invalid_milestone")

    def test_teacher_gate_explicit_approval_requires_non_empty_text(self) -> None:
        gate = build_advisory_readback_candidate_ordering_teacher_gate(
            milestone_audit=self._milestone(),
            readback_snapshot=self._snapshot(),
            baseline_candidate_ordering=("step_forward", "observe", "turn_left"),
            approval_source="explicit_teacher_review",
            approval_actor_role="teacher",
            teacher_gate_text="",
        )
        validation = validate_advisory_readback_candidate_ordering_teacher_gate(gate)
        self.assertIn("teacher_gate_text_required", validation["error_codes"])

    def test_teacher_gate_explicit_approval_requires_teacher_or_project_owner(self) -> None:
        gate = build_advisory_readback_candidate_ordering_teacher_gate(
            milestone_audit=self._milestone(),
            readback_snapshot=self._snapshot(),
            baseline_candidate_ordering=("step_forward", "observe", "turn_left"),
            approval_source="explicit_teacher_review",
            approval_actor_role="system_demo",
            teacher_gate_text="approved",
        )
        validation = validate_advisory_readback_candidate_ordering_teacher_gate(gate)
        self.assertIn("invalid_explicit_actor_role", validation["error_codes"])

    def test_teacher_gate_demo_approval_requires_system_demo_role(self) -> None:
        gate = build_advisory_readback_candidate_ordering_teacher_gate(
            milestone_audit=self._milestone(),
            readback_snapshot=self._snapshot(),
            baseline_candidate_ordering=("step_forward", "observe", "turn_left"),
            approval_source="demo_review",
            approval_actor_role="teacher",
        )
        validation = validate_advisory_readback_candidate_ordering_teacher_gate(gate)
        self.assertIn("demo_review_requires_system_demo_role", validation["error_codes"])

    def test_teacher_gate_approves_candidate_ordering_change_only(self) -> None:
        self.assertTrue(self._teacher_gate().approved_for_candidate_ordering_change)

    def test_teacher_gate_does_not_approve_action_or_memory_authority(self) -> None:
        gate = self._teacher_gate()
        self.assertFalse(gate.approved_for_selected_action_change)
        self.assertFalse(gate.approved_for_final_action_change)
        self.assertFalse(gate.approved_for_direct_command)
        self.assertFalse(gate.approved_for_execution)
        self.assertFalse(gate.approved_for_task_behavior_change)
        self.assertFalse(gate.approved_for_memory_layer_write)

    def test_ordering_helper_promotes_observe_for_observe_before_retry(self) -> None:
        ordering = compute_advisory_readback_ordering(
            ("step_forward", "observe", "turn_left"),
            ({"hint_kind": "observe_before_retry"},),
        )
        self.assertEqual(ordering[0], "observe")

    def test_ordering_helper_demotes_repeated_failure_candidate(self) -> None:
        ordering = compute_advisory_readback_ordering(
            ("step_forward", "observe", "turn_left"),
            ({"hint_kind": "avoid_repeated_failure"},),
        )
        self.assertEqual(ordering[-1], "step_forward")

    def test_ordering_helper_preserves_candidate_id_set(self) -> None:
        baseline = ("step_forward", "observe", "turn_left")
        ordering = compute_advisory_readback_ordering(
            baseline,
            (
                {"hint_kind": "observe_before_retry"},
                {"hint_kind": "avoid_repeated_failure"},
            ),
        )
        self.assertEqual(sorted(ordering), sorted(baseline))

    def test_ordering_helper_does_not_create_or_delete_candidates(self) -> None:
        baseline = ("step_forward", "observe", "turn_left")
        ordering = compute_advisory_readback_ordering(
            baseline,
            ({"hint_kind": "verify_expected_actual"},),
        )
        self.assertEqual(len(ordering), len(baseline))
        self.assertEqual(set(ordering), set(baseline))

    def test_ordering_application_applies_only_after_approved_teacher_gate(self) -> None:
        record = apply_teacher_gated_advisory_readback_candidate_ordering(
            teacher_gate=self._teacher_gate()
        )
        self.assertEqual(
            record.application_status,
            "candidate_ordering_changed_by_teacher_gated_readback_hints",
        )

    def test_ordering_application_changes_candidate_ordering_for_valid_demo(self) -> None:
        self.assertEqual(
            self._application().applied_candidate_ordering,
            ("observe", "turn_left", "step_forward"),
        )

    def test_ordering_application_preserves_candidate_ids(self) -> None:
        application = self._application()
        self.assertEqual(
            sorted(application.applied_candidate_ordering),
            sorted(application.baseline_candidate_ordering),
        )

    def test_ordering_application_applied_to_new_task_initialization_true(self) -> None:
        self.assertTrue(self._application().applied_to_new_task_initialization)

    def test_ordering_application_applied_to_running_task_false(self) -> None:
        self.assertFalse(self._application().applied_to_running_task)

    def test_ordering_application_forbidden_action_flags_false(self) -> None:
        application = self._application()
        validation = validate_advisory_readback_candidate_ordering_application_record(
            application
        )
        self.assertTrue(validation["valid"])
        self.assertFalse(application.selected_action_changed)
        self.assertFalse(application.final_action_changed)
        self.assertFalse(application.direct_command_changed)
        self.assertFalse(application.execution_created)
        self.assertFalse(application.task_behavior_changed)
        self.assertFalse(application.memory_layer_write_performed)

    def test_ordering_application_blocks_invalid_milestone(self) -> None:
        self._assert_application_status(
            build_demo_blocked_invalid_milestone_ordering_application,
            "blocked_invalid_teacher_gate",
        )

    def test_ordering_application_blocks_missing_teacher_gate(self) -> None:
        self._assert_application_status(
            build_demo_blocked_missing_teacher_gate_ordering_application,
            "blocked_invalid_teacher_gate",
        )

    def test_ordering_application_blocks_teacher_rejected(self) -> None:
        self._assert_application_status(
            build_demo_blocked_teacher_rejected_ordering_application,
            "rejected_by_teacher_gate",
        )

    def test_ordering_application_blocks_running_task_mutation(self) -> None:
        self._assert_application_status(
            build_demo_blocked_running_task_mutation_ordering_application,
            "blocked_running_task_mutation_attempt",
        )

    def test_ordering_application_blocks_candidate_deleted(self) -> None:
        self._assert_application_status(
            build_demo_blocked_candidate_deleted_ordering_application,
            "blocked_invalid_teacher_gate",
        )

    def test_ordering_application_blocks_candidate_created(self) -> None:
        self._assert_application_status(
            build_demo_blocked_candidate_created_ordering_application,
            "blocked_invalid_teacher_gate",
        )

    def test_ordering_application_blocks_selected_action_changed(self) -> None:
        self._assert_audit_status(
            build_demo_blocked_selected_action_changed_ordering_application,
            "blocked_selected_action_change_detected",
        )

    def test_ordering_application_blocks_final_action_changed(self) -> None:
        self._assert_audit_status(
            build_demo_blocked_final_action_changed_ordering_application,
            "blocked_final_action_change_detected",
        )

    def test_ordering_application_blocks_direct_command_created(self) -> None:
        self._assert_audit_status(
            build_demo_blocked_direct_command_created_ordering_application,
            "blocked_direct_command_detected",
        )

    def test_ordering_application_blocks_execution_created(self) -> None:
        self._assert_audit_status(
            build_demo_blocked_execution_created_ordering_application,
            "blocked_execution_detected",
        )

    def test_ordering_application_blocks_task_behavior_changed(self) -> None:
        self._assert_audit_status(
            build_demo_blocked_task_behavior_changed_ordering_application,
            "blocked_task_behavior_change_detected",
        )

    def test_ordering_application_blocks_memory_write(self) -> None:
        self._assert_audit_status(
            build_demo_blocked_memory_write_ordering_application,
            "blocked_memory_write_detected",
        )

    def test_rollback_record_created_for_successful_application(self) -> None:
        self.assertEqual(self._rollback().rollback_status, "rollback_record_created")
        self.assertTrue(self._rollback().rollback_available)

    def test_rollback_record_preserves_baseline_ordering(self) -> None:
        self.assertEqual(
            self._rollback().baseline_candidate_ordering,
            ("step_forward", "observe", "turn_left"),
        )

    def test_rollback_record_restores_baseline_ordering(self) -> None:
        result = apply_advisory_readback_candidate_ordering_rollback(self._rollback())
        self.assertEqual(
            tuple(result["candidate_ordering"]),
            ("step_forward", "observe", "turn_left"),
        )

    def test_rollback_does_not_change_action_path(self) -> None:
        result = apply_advisory_readback_candidate_ordering_rollback(self._rollback())
        self.assertFalse(result["selected_action_changed"])
        self.assertFalse(result["final_action_changed"])
        self.assertFalse(result["direct_command_changed"])
        self.assertFalse(result["execution_created"])

    def test_audit_passes_valid_teacher_gated_ordering_change(self) -> None:
        audit = self._audit()
        validation = validate_advisory_readback_candidate_ordering_application_audit(
            audit
        )
        self.assertTrue(validation["valid"])
        self.assertEqual(
            audit.audit_status,
            "passed_teacher_gated_candidate_ordering_change",
        )

    def test_audit_confirms_candidate_ordering_changed_true(self) -> None:
        self.assertTrue(self._audit().candidate_ordering_changed)

    def test_audit_confirms_action_path_unchanged(self) -> None:
        audit = self._audit()
        self.assertTrue(audit.no_selected_action_change)
        self.assertTrue(audit.no_final_action_change)
        self.assertTrue(audit.no_direct_command_change)
        self.assertTrue(audit.no_action_execution)
        self.assertTrue(audit.no_task_behavior_change)

    def test_audit_confirms_memory_layer_write_false(self) -> None:
        self.assertTrue(self._audit().no_memory_layer_write)

    def test_audit_fails_missing_rollback(self) -> None:
        self._assert_audit_status(
            build_demo_blocked_missing_rollback_ordering_application,
            "failed_missing_rollback",
        )

    def test_audit_blocks_running_task_mutation(self) -> None:
        self._assert_audit_status(
            build_demo_blocked_running_task_mutation_ordering_application,
            "blocked_running_task_mutation_detected",
        )

    def test_cli_apply_demo_ordering_works(self) -> None:
        payload = self._run_task_cli("apply-demo-ordering")
        self.assertEqual(
            payload["ordering_application"]["applied_candidate_ordering"],
            ["observe", "turn_left", "step_forward"],
        )

    def test_cli_show_demo_teacher_gate_works(self) -> None:
        payload = self._run_task_cli("show-demo-teacher-gate")
        self.assertEqual(
            payload["teacher_gate_status"],
            "approved_for_candidate_ordering_change",
        )

    def test_cli_show_demo_application_works(self) -> None:
        payload = self._run_task_cli("show-demo-application")
        self.assertTrue(payload["candidate_ordering_changed"])

    def test_cli_show_demo_rollback_works(self) -> None:
        payload = self._run_task_cli("show-demo-rollback")
        self.assertEqual(payload["rollback_status"], "rollback_record_created")

    def test_cli_show_demo_audit_works(self) -> None:
        payload = self._run_task_cli("show-demo-audit")
        self.assertEqual(
            payload["audit_status"],
            "passed_teacher_gated_candidate_ordering_change",
        )

    def test_cli_validate_demo_application_works(self) -> None:
        payload = self._run_task_cli("validate-demo-application")
        self.assertTrue(payload["valid"])

    def test_cli_rollback_demo_ordering_works(self) -> None:
        payload = self._run_task_cli("rollback-demo-ordering")
        self.assertEqual(payload["candidate_ordering"], ["step_forward", "observe", "turn_left"])

    def test_cli_blocked_cases_work(self) -> None:
        expected = {
            "invalid-milestone": "blocked_invalid_milestone",
            "missing-teacher-gate": "blocked_invalid_teacher_gate",
            "teacher-rejected": "passed_no_ordering_change",
            "running-task-mutation": "blocked_running_task_mutation_detected",
            "candidate-deleted": "blocked_invalid_teacher_gate",
            "candidate-created": "blocked_invalid_teacher_gate",
            "selected-action-changed": "blocked_selected_action_change_detected",
            "execution-created": "blocked_execution_detected",
            "missing-rollback": "failed_missing_rollback",
            "memory-write-detected": "blocked_memory_write_detected",
        }
        for case, status in expected.items():
            with self.subTest(case=case):
                payload = self._run_task_cli("apply-demo-blocked", "--case", case)
                self.assertEqual(
                    payload["ordering_application_audit"]["audit_status"],
                    status,
                )

    def test_guided_console_teacher_gated_ordering_application_demo_works(self) -> None:
        payload = self._run_guided_cli("task-apply-advisory-readback-ordering-demo")
        self.assertTrue(payload["candidate_ordering_changed"])
        self.assertFalse(payload["selected_action_changed"])

    def test_guided_console_show_and_validate_commands_work(self) -> None:
        show_payload = self._run_guided_cli("task-show-advisory-readback-ordering-audit")
        self.assertEqual(
            show_payload["ordering_application_audit"]["audit_status"],
            "passed_teacher_gated_candidate_ordering_change",
        )
        validate_payload = self._run_guided_cli(
            "task-validate-advisory-readback-ordering-application"
        )
        self.assertTrue(validate_payload["validation"]["valid"])
        rollback_payload = self._run_guided_cli(
            "task-rollback-advisory-readback-ordering-demo"
        )
        self.assertEqual(
            rollback_payload["rollback_result"]["candidate_ordering"],
            ["step_forward", "observe", "turn_left"],
        )

    def test_no_repo_data_created(self) -> None:
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _payload(self) -> dict[str, object]:
        return build_demo_teacher_gated_ordering_application()

    def _milestone(self) -> ReviewedConceptReadbackLoopMilestoneAudit:
        payload = build_demo_reviewed_concept_readback_loop_milestone()
        return ReviewedConceptReadbackLoopMilestoneAudit.from_dict(
            payload["milestone_audit"]
        )

    def _snapshot(self) -> FutureTaskWorkingMemoryInitializationReadbackSnapshot:
        payload = build_demo_future_task_working_memory_readback_hint_application_set()
        return FutureTaskWorkingMemoryInitializationReadbackSnapshot.from_dict(
            payload["future_task_working_memory_initialization_readback_snapshot"]
        )

    def _teacher_gate(self) -> AdvisoryReadbackCandidateOrderingTeacherGate:
        return AdvisoryReadbackCandidateOrderingTeacherGate.from_dict(
            self._payload()["ordering_teacher_gate"]
        )

    def _application(self) -> AdvisoryReadbackCandidateOrderingApplicationRecord:
        return AdvisoryReadbackCandidateOrderingApplicationRecord.from_dict(
            self._payload()["ordering_application"]
        )

    def _rollback(self) -> AdvisoryReadbackCandidateOrderingRollbackRecord:
        return AdvisoryReadbackCandidateOrderingRollbackRecord.from_dict(
            self._payload()["ordering_rollback"]
        )

    def _audit(self) -> AdvisoryReadbackCandidateOrderingApplicationAudit:
        return AdvisoryReadbackCandidateOrderingApplicationAudit.from_dict(
            self._payload()["ordering_application_audit"]
        )

    def _assert_application_status(self, builder, expected_status: str) -> None:
        payload = builder()
        self.assertEqual(
            payload["ordering_application"]["application_status"],
            expected_status,
        )

    def _assert_audit_status(self, builder, expected_status: str) -> None:
        payload = builder()
        self.assertEqual(
            payload["ordering_application_audit"]["audit_status"],
            expected_status,
        )

    def _run_task_cli(self, *args: str) -> dict:
        result = subprocess.run(
            [sys.executable, "-m", TASK_CLI, *args],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(result.stdout)

    def _run_guided_cli(self, *args: str) -> dict:
        result = subprocess.run(
            [sys.executable, "-m", GUIDED_CLI, *args],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(result.stdout)


if __name__ == "__main__":
    unittest.main()
