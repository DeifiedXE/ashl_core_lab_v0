from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from ashl_core_v1.audit.reviewed_concept_readback_loop_milestone_audit import (
    ReviewedConceptReadbackLoopBoundaryAudit,
    ReviewedConceptReadbackLoopEvidenceChain,
    ReviewedConceptReadbackLoopMilestoneAudit,
    ReviewedConceptReadbackLoopNextStageReadinessReport,
    build_demo_blocked_candidate_ordering_changed_milestone,
    build_demo_blocked_execution_created_milestone,
    build_demo_blocked_influence_audit_failure_milestone,
    build_demo_blocked_memory_layer_write_milestone,
    build_demo_blocked_missing_hint_record_milestone,
    build_demo_blocked_missing_influence_audit_milestone,
    build_demo_blocked_missing_memory_application_data_milestone,
    build_demo_blocked_missing_reviewed_concept_milestone,
    build_demo_blocked_missing_working_memory_application_milestone,
    build_demo_blocked_selected_action_changed_milestone,
    build_demo_reviewed_concept_readback_loop_milestone,
    validate_reviewed_concept_readback_loop_boundary_audit,
    validate_reviewed_concept_readback_loop_evidence_chain,
    validate_reviewed_concept_readback_loop_milestone_audit,
    validate_reviewed_concept_readback_loop_next_stage_readiness_report,
)


AUDIT_CLI = "ashl_core_v1.audit.reviewed_concept_readback_loop_milestone_audit_cli"
GUIDED_CLI = "ashl_core_v1.runtime.guided_cradle_growth_teacher_console_cli"


class ReviewedConceptReadbackLoopMilestoneAuditTests(unittest.TestCase):
    def test_evidence_chain_builds_from_complete_demo_loop(self) -> None:
        chain = self._chain()
        validation = validate_reviewed_concept_readback_loop_evidence_chain(chain)
        self.assertTrue(validation["valid"])
        self.assertEqual(chain.chain_status, "chain_complete")
        self.assertTrue(chain.chain_complete)

    def test_evidence_chain_preserves_reviewed_concept_id(self) -> None:
        self.assertIn("reviewed_concept:", self._chain().source_reviewed_concept_id)

    def test_evidence_chain_includes_reviewed_concept_record_id(self) -> None:
        self.assertEqual(
            self._chain().reviewed_concept_record_id,
            self._chain().source_reviewed_concept_id,
        )

    def test_evidence_chain_includes_memory_application_data_id(self) -> None:
        self.assertIn(
            "memory_application_data",
            self._chain().memory_application_data_id or "",
        )

    def test_evidence_chain_includes_task_working_memory_readback_hint_id(self) -> None:
        self.assertIn(
            "task_working_memory_readback_hint_record_set",
            self._chain().task_working_memory_readback_hint_record_set_id or "",
        )

    def test_evidence_chain_includes_future_task_application_id(self) -> None:
        self.assertIn(
            "future_task_working_memory_readback_hint_application_set",
            self._chain().future_task_application_set_id or "",
        )

    def test_evidence_chain_includes_influence_audit_report_id(self) -> None:
        self.assertIn(
            "readback_hint_influence_audit_report",
            self._chain().influence_audit_report_id or "",
        )

    def test_evidence_chain_detects_missing_reviewed_concept(self) -> None:
        chain = self._blocked_chain(build_demo_blocked_missing_reviewed_concept_milestone)
        self.assertEqual(
            chain.chain_status,
            "chain_incomplete_missing_learning_source",
        )
        self.assertIn("reviewed_concept_record_id", chain.missing_links)

    def test_evidence_chain_detects_missing_memory_application_data(self) -> None:
        chain = self._blocked_chain(
            build_demo_blocked_missing_memory_application_data_milestone
        )
        self.assertEqual(chain.chain_status, "chain_incomplete_missing_memory_records")
        self.assertIn("memory_application_data_id", chain.missing_links)

    def test_evidence_chain_detects_missing_hint_record(self) -> None:
        chain = self._blocked_chain(build_demo_blocked_missing_hint_record_milestone)
        self.assertEqual(chain.chain_status, "chain_incomplete_missing_hint_records")
        self.assertIn(
            "task_working_memory_readback_hint_record_set_id",
            chain.missing_links,
        )

    def test_evidence_chain_detects_missing_working_memory_application(self) -> None:
        chain = self._blocked_chain(
            build_demo_blocked_missing_working_memory_application_milestone
        )
        self.assertEqual(
            chain.chain_status,
            "chain_incomplete_missing_application_records",
        )
        self.assertIn("future_task_application_set_id", chain.missing_links)

    def test_evidence_chain_detects_missing_influence_audit(self) -> None:
        chain = self._blocked_chain(build_demo_blocked_missing_influence_audit_milestone)
        self.assertEqual(chain.chain_status, "chain_incomplete_missing_influence_audit")
        self.assertIn("influence_audit_report_id", chain.missing_links)

    def test_boundary_audit_passes_for_advisory_only_demo(self) -> None:
        boundary = self._boundary()
        validation = validate_reviewed_concept_readback_loop_boundary_audit(boundary)
        self.assertTrue(validation["valid"])
        self.assertEqual(boundary.boundary_status, "passed_advisory_readback_only")

    def test_boundary_audit_confirms_new_task_initialization_only(self) -> None:
        self.assertTrue(
            self._boundary().working_memory_mutation_limited_to_new_task_initialization
        )

    def test_boundary_audit_confirms_no_running_task_mutation(self) -> None:
        self.assertTrue(self._boundary().no_running_task_mutation)

    def test_boundary_audit_confirms_no_candidate_ordering_change(self) -> None:
        self.assertFalse(self._boundary().candidate_ordering_changed)

    def test_boundary_audit_confirms_no_task_behavior_change(self) -> None:
        self.assertFalse(self._boundary().task_behavior_changed)

    def test_boundary_audit_confirms_no_action_chain_change(self) -> None:
        boundary = self._boundary()
        self.assertFalse(boundary.selected_action_changed)
        self.assertFalse(boundary.final_action_changed)
        self.assertFalse(boundary.direct_command_changed)
        self.assertFalse(boundary.execution_created)

    def test_boundary_audit_confirms_no_memory_layer_write(self) -> None:
        boundary = self._boundary()
        self.assertFalse(boundary.memory_layer_write_performed)
        self.assertFalse(boundary.core_memory_write_performed)
        self.assertFalse(boundary.long_term_memory_write_performed)
        self.assertFalse(boundary.archive_memory_write_performed)
        self.assertFalse(boundary.anchor_write_performed)

    def test_boundary_audit_fails_candidate_ordering_changed(self) -> None:
        boundary = self._blocked_boundary(
            build_demo_blocked_candidate_ordering_changed_milestone
        )
        self.assertEqual(
            boundary.boundary_status,
            "failed_candidate_ordering_change_detected",
        )

    def test_boundary_audit_fails_selected_action_changed(self) -> None:
        boundary = self._blocked_boundary(
            build_demo_blocked_selected_action_changed_milestone
        )
        self.assertEqual(boundary.boundary_status, "failed_action_authority_detected")

    def test_boundary_audit_fails_execution_created(self) -> None:
        boundary = self._blocked_boundary(build_demo_blocked_execution_created_milestone)
        self.assertEqual(boundary.boundary_status, "failed_action_authority_detected")

    def test_boundary_audit_fails_memory_layer_write(self) -> None:
        boundary = self._blocked_boundary(
            build_demo_blocked_memory_layer_write_milestone
        )
        self.assertEqual(
            boundary.boundary_status,
            "failed_memory_layer_write_detected",
        )

    def test_milestone_audit_passes_complete_loop(self) -> None:
        milestone = self._milestone()
        validation = validate_reviewed_concept_readback_loop_milestone_audit(milestone)
        self.assertTrue(validation["valid"])
        self.assertEqual(
            milestone.milestone_status,
            "passed_reviewed_concept_advisory_readback_loop_v0",
        )

    def test_milestone_audit_fails_incomplete_evidence_chain(self) -> None:
        milestone = self._blocked_milestone(
            build_demo_blocked_missing_reviewed_concept_milestone
        )
        self.assertEqual(milestone.milestone_status, "failed_incomplete_evidence_chain")

    def test_milestone_audit_fails_boundary_failure(self) -> None:
        milestone = self._blocked_milestone(
            build_demo_blocked_candidate_ordering_changed_milestone
        )
        self.assertEqual(milestone.milestone_status, "failed_boundary_audit")

    def test_milestone_audit_fails_influence_audit_failure(self) -> None:
        milestone = self._blocked_milestone(
            build_demo_blocked_influence_audit_failure_milestone
        )
        self.assertEqual(milestone.milestone_status, "failed_influence_audit")

    def test_milestone_safe_claim_says_advisory_readback_loop_only(self) -> None:
        milestone = self._milestone()
        self.assertIn("advisory", milestone.safe_claim)
        self.assertIn("visible, and inert", milestone.safe_claim)

    def test_milestone_forbidden_claims_include_behavior_changing_concept_readback(self) -> None:
        self.assertIn(
            "no_behavior-changing_concept_readback",
            self._milestone().forbidden_claims,
        )

    def test_next_stage_readiness_allows_candidate_ordering_influence_preview_only(self) -> None:
        report = self._readiness()
        validation = validate_reviewed_concept_readback_loop_next_stage_readiness_report(
            report
        )
        self.assertTrue(validation["valid"])
        self.assertTrue(report.candidate_ordering_influence_preview_allowed)

    def test_next_stage_readiness_does_not_allow_candidate_ordering_change(self) -> None:
        self.assertFalse(self._readiness().candidate_ordering_change_allowed)

    def test_next_stage_readiness_does_not_allow_task_behavior_change(self) -> None:
        self.assertFalse(self._readiness().task_behavior_change_allowed)

    def test_next_stage_readiness_does_not_allow_action_selection(self) -> None:
        self.assertFalse(self._readiness().action_selection_allowed)

    def test_next_stage_readiness_does_not_allow_execution(self) -> None:
        self.assertFalse(self._readiness().execution_allowed)

    def test_cli_audit_demo_loop_works(self) -> None:
        payload = self._run_audit_cli("audit-demo-loop")
        self.assertEqual(
            payload["milestone_audit"]["milestone_status"],
            "passed_reviewed_concept_advisory_readback_loop_v0",
        )

    def test_cli_show_demo_evidence_chain_works(self) -> None:
        payload = self._run_audit_cli("show-demo-evidence-chain")
        self.assertEqual(payload["chain_status"], "chain_complete")

    def test_cli_show_demo_boundary_audit_works(self) -> None:
        payload = self._run_audit_cli("show-demo-boundary-audit")
        self.assertEqual(payload["boundary_status"], "passed_advisory_readback_only")

    def test_cli_show_demo_milestone_audit_works(self) -> None:
        payload = self._run_audit_cli("show-demo-milestone-audit")
        self.assertEqual(
            payload["milestone_status"],
            "passed_reviewed_concept_advisory_readback_loop_v0",
        )

    def test_cli_show_demo_next_stage_readiness_works(self) -> None:
        payload = self._run_audit_cli("show-demo-next-stage-readiness")
        self.assertEqual(
            payload["readiness_status"],
            "ready_for_candidate_ordering_influence_preview_only",
        )

    def test_cli_validate_demo_loop_works(self) -> None:
        payload = self._run_audit_cli("validate-demo-loop")
        self.assertTrue(payload["valid"])

    def test_cli_blocked_missing_reviewed_concept_works(self) -> None:
        self._assert_cli_chain_status(
            "missing-reviewed-concept",
            "chain_incomplete_missing_learning_source",
        )

    def test_cli_blocked_missing_memory_application_data_works(self) -> None:
        self._assert_cli_chain_status(
            "missing-memory-application-data",
            "chain_incomplete_missing_memory_records",
        )

    def test_cli_blocked_missing_hint_record_works(self) -> None:
        self._assert_cli_chain_status(
            "missing-hint-record",
            "chain_incomplete_missing_hint_records",
        )

    def test_cli_blocked_missing_working_memory_application_works(self) -> None:
        self._assert_cli_chain_status(
            "missing-working-memory-application",
            "chain_incomplete_missing_application_records",
        )

    def test_cli_blocked_missing_influence_audit_works(self) -> None:
        self._assert_cli_chain_status(
            "missing-influence-audit",
            "chain_incomplete_missing_influence_audit",
        )

    def test_cli_blocked_candidate_ordering_changed_works(self) -> None:
        self._assert_cli_boundary_status(
            "candidate-ordering-changed",
            "failed_candidate_ordering_change_detected",
        )

    def test_cli_blocked_selected_action_changed_works(self) -> None:
        self._assert_cli_boundary_status(
            "selected-action-changed",
            "failed_action_authority_detected",
        )

    def test_cli_blocked_execution_created_works(self) -> None:
        self._assert_cli_boundary_status(
            "execution-created",
            "failed_action_authority_detected",
        )

    def test_cli_blocked_memory_layer_write_detected_works(self) -> None:
        self._assert_cli_boundary_status(
            "memory-layer-write-detected",
            "failed_memory_layer_write_detected",
        )

    def test_guided_console_milestone_audit_demo_works(self) -> None:
        payload = self._run_guided_cli("audit-reviewed-concept-readback-loop-demo")
        self.assertEqual(
            payload["milestone_audit"]["milestone_status"],
            "passed_reviewed_concept_advisory_readback_loop_v0",
        )
        self.assertFalse(payload["task_behavior_changed"])

    def test_guided_console_show_evidence_chain_works(self) -> None:
        payload = self._run_guided_cli(
            "audit-show-reviewed-concept-readback-loop-evidence-chain"
        )
        self.assertEqual(payload["evidence_chain"]["chain_status"], "chain_complete")

    def test_guided_console_show_boundary_works(self) -> None:
        payload = self._run_guided_cli(
            "audit-show-reviewed-concept-readback-loop-boundary"
        )
        self.assertEqual(
            payload["boundary_audit"]["boundary_status"],
            "passed_advisory_readback_only",
        )

    def test_guided_console_show_milestone_works(self) -> None:
        payload = self._run_guided_cli(
            "audit-show-reviewed-concept-readback-loop-milestone"
        )
        self.assertEqual(
            payload["milestone_audit"]["milestone_status"],
            "passed_reviewed_concept_advisory_readback_loop_v0",
        )

    def test_guided_console_show_next_stage_readiness_works(self) -> None:
        payload = self._run_guided_cli(
            "audit-show-reviewed-concept-readback-loop-next-stage-readiness"
        )
        self.assertEqual(
            payload["next_stage_readiness_report"]["readiness_status"],
            "ready_for_candidate_ordering_influence_preview_only",
        )

    def test_guided_console_validate_milestone_audit_works(self) -> None:
        payload = self._run_guided_cli("audit-validate-reviewed-concept-readback-loop")
        self.assertTrue(payload["validation"]["valid"])

    def test_no_repo_data_created(self) -> None:
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _payload(self) -> dict[str, object]:
        return build_demo_reviewed_concept_readback_loop_milestone()

    def _chain(self) -> ReviewedConceptReadbackLoopEvidenceChain:
        return ReviewedConceptReadbackLoopEvidenceChain.from_dict(
            self._payload()["evidence_chain"]
        )

    def _boundary(self) -> ReviewedConceptReadbackLoopBoundaryAudit:
        return ReviewedConceptReadbackLoopBoundaryAudit.from_dict(
            self._payload()["boundary_audit"]
        )

    def _milestone(self) -> ReviewedConceptReadbackLoopMilestoneAudit:
        return ReviewedConceptReadbackLoopMilestoneAudit.from_dict(
            self._payload()["milestone_audit"]
        )

    def _readiness(self) -> ReviewedConceptReadbackLoopNextStageReadinessReport:
        return ReviewedConceptReadbackLoopNextStageReadinessReport.from_dict(
            self._payload()["next_stage_readiness_report"]
        )

    def _blocked_chain(self, builder) -> ReviewedConceptReadbackLoopEvidenceChain:
        return ReviewedConceptReadbackLoopEvidenceChain.from_dict(
            builder()["evidence_chain"]
        )

    def _blocked_boundary(self, builder) -> ReviewedConceptReadbackLoopBoundaryAudit:
        return ReviewedConceptReadbackLoopBoundaryAudit.from_dict(
            builder()["boundary_audit"]
        )

    def _blocked_milestone(self, builder) -> ReviewedConceptReadbackLoopMilestoneAudit:
        return ReviewedConceptReadbackLoopMilestoneAudit.from_dict(
            builder()["milestone_audit"]
        )

    def _assert_cli_chain_status(self, case: str, expected_status: str) -> None:
        payload = self._run_audit_cli("audit-demo-blocked", "--case", case)
        self.assertEqual(payload["evidence_chain"]["chain_status"], expected_status)

    def _assert_cli_boundary_status(self, case: str, expected_status: str) -> None:
        payload = self._run_audit_cli("audit-demo-blocked", "--case", case)
        self.assertEqual(payload["boundary_audit"]["boundary_status"], expected_status)

    def _run_audit_cli(self, *args: str) -> dict:
        result = subprocess.run(
            [sys.executable, "-m", AUDIT_CLI, *args],
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
