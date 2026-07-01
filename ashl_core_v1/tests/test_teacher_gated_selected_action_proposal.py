from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from ashl_core_v1.task.advisory_readback_candidate_ordering_application import (
    AdvisoryReadbackCandidateOrderingApplicationAudit,
    AdvisoryReadbackCandidateOrderingApplicationRecord,
    build_demo_teacher_gated_ordering_application,
)
from ashl_core_v1.task.teacher_gated_selected_action_proposal import (
    SelectedActionProposalAudit,
    SelectedActionProposalRecord,
    SelectedActionProposalRollbackRecord,
    TeacherGatedSelectedActionProposalGate,
    apply_selected_action_proposal_rollback,
    build_demo_blocked_empty_candidate_ordering_selected_action_proposal,
    build_demo_blocked_direct_command_created_selected_action_proposal,
    build_demo_blocked_execution_created_selected_action_proposal,
    build_demo_blocked_final_action_mutated_selected_action_proposal,
    build_demo_blocked_invalid_ordering_application_selected_action_proposal,
    build_demo_blocked_invalid_ordering_audit_selected_action_proposal,
    build_demo_blocked_memory_write_selected_action_proposal,
    build_demo_blocked_missing_rollback_selected_action_proposal,
    build_demo_blocked_missing_teacher_gate_selected_action_proposal,
    build_demo_blocked_selected_action_mutated_selected_action_proposal,
    build_demo_blocked_task_behavior_changed_selected_action_proposal,
    build_demo_blocked_teacher_rejected_selected_action_proposal,
    build_demo_selected_action_proposal,
    build_selected_action_proposal_record,
    build_teacher_gated_selected_action_proposal_gate,
    validate_selected_action_proposal_audit,
    validate_teacher_gated_selected_action_proposal_gate,
)


TASK_CLI = "ashl_core_v1.task.teacher_gated_selected_action_proposal_cli"
GUIDED_CLI = "ashl_core_v1.runtime.guided_cradle_growth_teacher_console_cli"


class TeacherGatedSelectedActionProposalTests(unittest.TestCase):
    def test_proposal_gate_builds_from_valid_ordering_application(self) -> None:
        gate = self._gate()
        validation = validate_teacher_gated_selected_action_proposal_gate(gate)
        self.assertTrue(validation["valid"])
        self.assertEqual(gate.teacher_gate_status, "approved_for_selected_action_proposal")
        self.assertEqual(gate.top_candidate_id, "observe")

    def test_proposal_gate_requires_ordering_application_audit_pass(self) -> None:
        audit = AdvisoryReadbackCandidateOrderingApplicationAudit.from_dict(
            {
                **self._ordering_audit().to_dict(),
                "audit_status": "failed_missing_rollback",
            }
        )
        gate = build_teacher_gated_selected_action_proposal_gate(
            ordering_application=self._ordering_application(),
            ordering_application_audit=audit,
        )
        self.assertEqual(gate.teacher_gate_status, "blocked_invalid_ordering_audit")

    def test_proposal_gate_explicit_approval_requires_non_empty_text(self) -> None:
        gate = build_teacher_gated_selected_action_proposal_gate(
            ordering_application=self._ordering_application(),
            ordering_application_audit=self._ordering_audit(),
            approval_source="explicit_teacher_review",
            approval_actor_role="teacher",
            teacher_gate_text="",
        )
        validation = validate_teacher_gated_selected_action_proposal_gate(gate)
        self.assertIn("teacher_gate_text_required", validation["error_codes"])

    def test_proposal_gate_explicit_approval_requires_teacher_or_project_owner(self) -> None:
        gate = build_teacher_gated_selected_action_proposal_gate(
            ordering_application=self._ordering_application(),
            ordering_application_audit=self._ordering_audit(),
            approval_source="explicit_teacher_review",
            approval_actor_role="system_demo",
            teacher_gate_text="approved",
        )
        validation = validate_teacher_gated_selected_action_proposal_gate(gate)
        self.assertIn("invalid_explicit_actor_role", validation["error_codes"])

    def test_proposal_gate_demo_approval_requires_system_demo_role(self) -> None:
        gate = build_teacher_gated_selected_action_proposal_gate(
            ordering_application=self._ordering_application(),
            ordering_application_audit=self._ordering_audit(),
            approval_source="demo_review",
            approval_actor_role="teacher",
        )
        validation = validate_teacher_gated_selected_action_proposal_gate(gate)
        self.assertIn("demo_review_requires_system_demo_role", validation["error_codes"])

    def test_proposal_gate_approves_selected_action_proposal_only(self) -> None:
        gate = self._gate()
        self.assertTrue(gate.approved_for_selected_action_proposal)
        self.assertFalse(gate.approved_for_actual_selected_action)
        self.assertFalse(gate.approved_for_final_action)
        self.assertFalse(gate.approved_for_direct_command)
        self.assertFalse(gate.approved_for_execution)
        self.assertFalse(gate.approved_for_task_behavior_change)
        self.assertFalse(gate.approved_for_memory_layer_write)

    def test_selected_action_proposal_builds_after_approved_gate(self) -> None:
        proposal = self._proposal()
        self.assertEqual(proposal.proposal_status, "selected_action_proposal_created")
        self.assertTrue(proposal.selected_action_proposal_created)

    def test_selected_action_proposal_uses_first_ordered_candidate(self) -> None:
        proposal = self._proposal()
        self.assertEqual(proposal.proposed_selected_action_candidate_id, "observe")
        self.assertEqual(proposal.proposal_rank, 0)

    def test_selected_action_proposal_forbidden_authority_flags_false(self) -> None:
        proposal = self._proposal()
        self.assertFalse(proposal.actual_selected_action_changed)
        self.assertFalse(proposal.final_action_changed)
        self.assertFalse(proposal.direct_command_created)
        self.assertFalse(proposal.execution_created)
        self.assertFalse(proposal.task_behavior_changed)
        self.assertFalse(proposal.candidate_ordering_changed_by_this_package)
        self.assertFalse(proposal.memory_layer_write_performed)

    def test_selected_action_proposal_blocks_invalid_ordering_application(self) -> None:
        self._assert_proposal_status(
            build_demo_blocked_invalid_ordering_application_selected_action_proposal,
            "blocked_invalid_teacher_gate",
        )

    def test_selected_action_proposal_blocks_invalid_ordering_audit(self) -> None:
        self._assert_proposal_status(
            build_demo_blocked_invalid_ordering_audit_selected_action_proposal,
            "blocked_invalid_teacher_gate",
        )

    def test_selected_action_proposal_blocks_missing_teacher_gate(self) -> None:
        self._assert_proposal_status(
            build_demo_blocked_missing_teacher_gate_selected_action_proposal,
            "blocked_invalid_teacher_gate",
        )

    def test_selected_action_proposal_blocks_teacher_rejected(self) -> None:
        self._assert_proposal_status(
            build_demo_blocked_teacher_rejected_selected_action_proposal,
            "rejected_by_teacher_gate",
        )

    def test_selected_action_proposal_blocks_empty_candidate_ordering(self) -> None:
        self._assert_proposal_status(
            build_demo_blocked_empty_candidate_ordering_selected_action_proposal,
            "blocked_empty_candidate_ordering",
        )

    def test_selected_action_proposal_blocks_forbidden_mutations(self) -> None:
        cases = (
            build_demo_blocked_selected_action_mutated_selected_action_proposal,
            build_demo_blocked_final_action_mutated_selected_action_proposal,
            build_demo_blocked_direct_command_created_selected_action_proposal,
            build_demo_blocked_execution_created_selected_action_proposal,
            build_demo_blocked_task_behavior_changed_selected_action_proposal,
            build_demo_blocked_memory_write_selected_action_proposal,
        )
        for builder in cases:
            with self.subTest(builder=builder.__name__):
                self._assert_proposal_status(
                    builder,
                    "blocked_forbidden_authority_detected",
                )

    def test_rollback_record_created_for_successful_proposal(self) -> None:
        rollback = self._rollback()
        self.assertEqual(rollback.rollback_status, "rollback_record_created")
        self.assertTrue(rollback.rollback_available)
        self.assertTrue(rollback.proposal_available_after_rollback)

    def test_rollback_record_withdraws_proposal_availability(self) -> None:
        result = apply_selected_action_proposal_rollback(self._rollback())
        self.assertEqual(
            result["rollback_status"],
            "rollback_applied_to_withdraw_proposal",
        )
        self.assertFalse(result["proposal_available_after_rollback"])
        self.assertIsNone(result["proposed_selected_action_candidate_id"])

    def test_rollback_does_not_change_action_path(self) -> None:
        rollback = self._rollback()
        self.assertFalse(rollback.actual_selected_action_changed)
        self.assertFalse(rollback.final_action_changed)
        self.assertFalse(rollback.direct_command_created)
        self.assertFalse(rollback.execution_created)
        self.assertFalse(rollback.task_behavior_changed)
        self.assertFalse(rollback.memory_layer_write_performed)

    def test_proposal_audit_passes_valid_proposal(self) -> None:
        audit = self._audit()
        validation = validate_selected_action_proposal_audit(audit)
        self.assertTrue(validation["valid"])
        self.assertEqual(audit.audit_status, "passed_selected_action_proposal_created")

    def test_proposal_audit_confirms_boundaries(self) -> None:
        audit = self._audit()
        self.assertTrue(audit.selected_action_proposal_created)
        self.assertFalse(audit.actual_selected_action_changed)
        self.assertFalse(audit.final_action_changed)
        self.assertFalse(audit.direct_command_created)
        self.assertFalse(audit.execution_created)
        self.assertFalse(audit.task_behavior_changed)
        self.assertFalse(audit.candidate_ordering_changed_by_this_package)
        self.assertTrue(audit.no_memory_layer_write)

    def test_proposal_audit_fails_missing_rollback(self) -> None:
        payload = build_demo_blocked_missing_rollback_selected_action_proposal()
        audit = SelectedActionProposalAudit.from_dict(
            payload["selected_action_proposal_audit"]
        )
        self.assertEqual(audit.audit_status, "failed_missing_rollback")

    def test_proposal_audit_blocks_forbidden_authority(self) -> None:
        expected = {
            "selected-action-mutated": "blocked_actual_selected_action_change_detected",
            "final-action-mutated": "blocked_final_action_change_detected",
            "direct-command-created": "blocked_direct_command_detected",
            "execution-created": "blocked_execution_detected",
            "task-behavior-changed": "blocked_task_behavior_change_detected",
            "memory-write-detected": "blocked_memory_write_detected",
        }
        for case, status in expected.items():
            with self.subTest(case=case):
                payload = self._run_task_cli("propose-demo-blocked", "--case", case)
                self.assertEqual(
                    payload["selected_action_proposal_audit"]["audit_status"],
                    status,
                )

    def test_cli_commands_work(self) -> None:
        commands = (
            "propose-demo-selected-action",
            "show-demo-teacher-gate",
            "show-demo-proposal",
            "show-demo-rollback",
            "show-demo-audit",
            "validate-demo-proposal",
            "rollback-demo-proposal",
        )
        for command in commands:
            with self.subTest(command=command):
                payload = self._run_task_cli(command)
                self.assertIsInstance(payload, dict)

    def test_cli_blocked_cases_work(self) -> None:
        cases = (
            "invalid-ordering-application",
            "invalid-ordering-audit",
            "missing-teacher-gate",
            "teacher-rejected",
            "empty-candidate-ordering",
            "selected-action-mutated",
            "execution-created",
            "missing-rollback",
            "memory-write-detected",
        )
        for case in cases:
            with self.subTest(case=case):
                payload = self._run_task_cli("propose-demo-blocked", "--case", case)
                self.assertIn("selected_action_proposal_audit", payload)

    def test_guided_console_selected_action_proposal_demo_works(self) -> None:
        payload = self._run_guided_cli("task-propose-selected-action-demo")
        self.assertEqual(
            payload["selected_action_proposal"]["proposed_selected_action_candidate_id"],
            "observe",
        )
        self.assertFalse(payload["actual_selected_action_changed"])

    def test_guided_console_selected_action_proposal_views_work(self) -> None:
        commands = (
            "task-show-selected-action-proposal-teacher-gate",
            "task-show-selected-action-proposal",
            "task-show-selected-action-proposal-rollback",
            "task-show-selected-action-proposal-audit",
            "task-validate-selected-action-proposal",
            "task-rollback-selected-action-proposal-demo",
        )
        for command in commands:
            with self.subTest(command=command):
                payload = self._run_guided_cli(command)
                self.assertFalse(payload.get("actual_selected_action_changed", False))
                self.assertFalse(payload.get("execution_created", False))

    def test_no_repo_data_dir_created(self) -> None:
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _payload(self) -> dict[str, object]:
        return build_demo_selected_action_proposal()

    def _gate(self) -> TeacherGatedSelectedActionProposalGate:
        return TeacherGatedSelectedActionProposalGate.from_dict(
            self._payload()["selected_action_proposal_gate"]
        )

    def _proposal(self) -> SelectedActionProposalRecord:
        return SelectedActionProposalRecord.from_dict(
            self._payload()["selected_action_proposal"]
        )

    def _rollback(self) -> SelectedActionProposalRollbackRecord:
        return SelectedActionProposalRollbackRecord.from_dict(
            self._payload()["selected_action_proposal_rollback"]
        )

    def _audit(self) -> SelectedActionProposalAudit:
        return SelectedActionProposalAudit.from_dict(
            self._payload()["selected_action_proposal_audit"]
        )

    def _ordering_payload(self) -> dict[str, object]:
        return build_demo_teacher_gated_ordering_application()

    def _ordering_application(self) -> AdvisoryReadbackCandidateOrderingApplicationRecord:
        return AdvisoryReadbackCandidateOrderingApplicationRecord.from_dict(
            self._ordering_payload()["ordering_application"]
        )

    def _ordering_audit(self) -> AdvisoryReadbackCandidateOrderingApplicationAudit:
        return AdvisoryReadbackCandidateOrderingApplicationAudit.from_dict(
            self._ordering_payload()["ordering_application_audit"]
        )

    def _assert_proposal_status(self, builder, expected_status: str) -> None:
        payload = builder()
        proposal = SelectedActionProposalRecord.from_dict(
            payload["selected_action_proposal"]
        )
        self.assertEqual(proposal.proposal_status, expected_status)

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
