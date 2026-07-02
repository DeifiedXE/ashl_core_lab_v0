from __future__ import annotations

import json
import subprocess
import sys
import unittest
from dataclasses import replace
from pathlib import Path

from ashl_core_v1.learning import feedback_refined_concept_reviewed_readback_integration as integration
from ashl_core_v1.learning.feedback_concept_candidate_review_refinement import (
    FeedbackConceptCandidateCounterexampleCheckRecord,
    FeedbackConceptCandidateRefinementRecord,
    FeedbackConceptCandidateRefinementSafetyAudit,
    FeedbackConceptCandidateReviewRecord,
    FeedbackConceptCandidateScopeCheckRecord,
)
from ashl_core_v1.runtime.guided_cradle_growth_teacher_console import (
    integrate_feedback_reviewed_concept_demo_from_guided_cradle_growth_console,
    validate_feedback_reviewed_concept_integration_from_guided_cradle_growth_console,
)


class FeedbackReviewedConceptIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = (
            integration.build_demo_positive_affordance_feedback_reviewed_concept_integration()
        )
        self.refinement = FeedbackConceptCandidateRefinementRecord.from_dict(
            self.payload["feedback_concept_candidate_refinement"]
        )
        self.review = FeedbackConceptCandidateReviewRecord.from_dict(
            self.payload["feedback_concept_candidate_review"]
        )
        self.scope = FeedbackConceptCandidateScopeCheckRecord.from_dict(
            self.payload["feedback_concept_candidate_scope_check"]
        )
        self.counterexample = FeedbackConceptCandidateCounterexampleCheckRecord.from_dict(
            self.payload["feedback_concept_candidate_counterexample_check"]
        )
        self.refinement_audit = FeedbackConceptCandidateRefinementSafetyAudit.from_dict(
            self.payload["feedback_concept_candidate_refinement_safety_audit"]
        )
        self.gate = integration.FeedbackRefinedConceptReviewedConceptGate.from_dict(
            self.payload["feedback_reviewed_concept_gate"]
        )
        self.reviewed = integration.FeedbackDerivedReviewedConceptRecord.from_dict(
            self.payload["feedback_derived_reviewed_concept"]
        )
        self.working = (
            integration.FeedbackDerivedReviewedConceptWorkingReadbackIntegrationRecord.from_dict(
                self.payload[
                    "feedback_derived_reviewed_concept_working_readback_integration"
                ]
            )
        )
        self.seed = integration.FeedbackDerivedReviewedConceptReadbackSeedRecord.from_dict(
            self.payload["feedback_derived_reviewed_concept_readback_seed"]
        )
        self.rollback = integration.FeedbackDerivedReviewedConceptRollbackRecord.from_dict(
            self.payload["feedback_derived_reviewed_concept_rollback"]
        )
        self.audit = integration.FeedbackDerivedReviewedConceptIntegrationSafetyAudit.from_dict(
            self.payload["feedback_derived_reviewed_concept_integration_safety_audit"]
        )

    def test_teacher_gate_builds_from_valid_package_91_refinement(self) -> None:
        self.assertEqual(
            self.gate.source_feedback_refinement_id,
            self.refinement.feedback_concept_candidate_refinement_id,
        )
        self.assertEqual(
            self.gate.source_feedback_review_id,
            self.review.feedback_concept_candidate_review_id,
        )
        self.assertEqual(self.gate.source_scope_check_id, self.scope.scope_check_id)
        self.assertEqual(
            self.gate.source_counterexample_check_id,
            self.counterexample.counterexample_check_id,
        )
        self.assertEqual(
            self.gate.source_refinement_safety_audit_id,
            self.refinement_audit.feedback_concept_candidate_refinement_safety_audit_id,
        )
        self.assertEqual(
            self.gate.teacher_gate_status,
            "approved_for_feedback_reviewed_concept_and_working_readback",
        )
        self.assertTrue(
            integration.validate_feedback_refined_concept_reviewed_concept_gate(
                self.gate
            )["valid"]
        )

    def test_teacher_gate_source_validation_rules(self) -> None:
        explicit_blank = integration.build_feedback_refined_concept_reviewed_concept_gate(
            refinement=self.refinement,
            review=self.review,
            scope_check=self.scope,
            counterexample_check=self.counterexample,
            refinement_safety_audit=self.refinement_audit,
            approval_source="explicit_teacher_review",
            approval_actor_role="teacher",
            teacher_gate_text="",
        )
        self.assertIn(
            "explicit_review_requires_teacher_gate_text",
            integration.validate_feedback_refined_concept_reviewed_concept_gate(
                explicit_blank
            )["error_codes"],
        )
        explicit_bad_role = integration.build_feedback_refined_concept_reviewed_concept_gate(
            refinement=self.refinement,
            review=self.review,
            scope_check=self.scope,
            counterexample_check=self.counterexample,
            refinement_safety_audit=self.refinement_audit,
            approval_source="explicit_teacher_review",
            approval_actor_role="system_demo",
            teacher_gate_text="teacher approved working readback only",
        )
        self.assertIn(
            "explicit_review_requires_teacher_or_project_owner",
            integration.validate_feedback_refined_concept_reviewed_concept_gate(
                explicit_bad_role
            )["error_codes"],
        )
        demo_bad_role = integration.build_feedback_refined_concept_reviewed_concept_gate(
            refinement=self.refinement,
            review=self.review,
            scope_check=self.scope,
            counterexample_check=self.counterexample,
            refinement_safety_audit=self.refinement_audit,
            approval_source="demo_review",
            approval_actor_role="teacher",
        )
        self.assertIn(
            "demo_review_requires_system_demo_role",
            integration.validate_feedback_refined_concept_reviewed_concept_gate(
                demo_bad_role
            )["error_codes"],
        )

    def test_teacher_gate_approves_only_reviewed_concept_and_working_readback(self) -> None:
        self.assertTrue(self.gate.approved_for_feedback_reviewed_concept)
        self.assertTrue(self.gate.approved_for_working_readback_integration)
        self.assertFalse(self.gate.approved_for_core_memory_write)
        self.assertFalse(self.gate.approved_for_long_term_memory_write)
        self.assertFalse(self.gate.approved_for_archive_memory_write)
        self.assertFalse(self.gate.approved_for_anchor_write)
        self.assertFalse(self.gate.approved_for_automatic_learning_approval)
        self.assertFalse(self.gate.approved_for_behavior_change)
        self.assertFalse(self.gate.approved_for_action_authority)

    def test_teacher_gate_requires_refinement_safety_audit_pass(self) -> None:
        payload = integration.build_demo_blocked_invalid_refinement_audit_feedback_reviewed_concept()
        gate = payload["feedback_reviewed_concept_gate"]
        self.assertEqual(gate["teacher_gate_status"], "blocked_invalid_refinement")

    def test_feedback_reviewed_concept_preserves_source_lineage(self) -> None:
        self.assertEqual(
            self.reviewed.source_feedback_refinement_id,
            self.refinement.feedback_concept_candidate_refinement_id,
        )
        self.assertEqual(
            self.reviewed.source_learning_feedback_candidate_id,
            self.review.source_learning_feedback_candidate_id,
        )
        self.assertTrue(self.reviewed.source_task_closure_id.startswith("task_closure:"))
        self.assertTrue(
            self.reviewed.source_outcome_evaluation_id.startswith(
                "task_outcome_evaluation:"
            )
        )
        self.assertTrue(
            self.reviewed.source_sense_handoff_id.startswith("sense_sandbox_handoff:")
        )
        self.assertTrue(
            self.reviewed.source_sandbox_execution_id.startswith("sandbox_execution:")
        )
        self.assertEqual(
            self.reviewed.support_evidence_refs,
            self.refinement.support_evidence_refs,
        )
        self.assertEqual(
            self.reviewed.counterexample_refs,
            self.refinement.counterexample_refs,
        )

    def test_feedback_reviewed_concept_boundaries(self) -> None:
        self.assertEqual(
            self.reviewed.reviewed_concept_status,
            "feedback_reviewed_concept_created",
        )
        self.assertTrue(self.reviewed.available_for_working_readback_integration)
        self.assertFalse(self.reviewed.available_for_core_memory_write)
        self.assertFalse(self.reviewed.available_for_long_term_memory_write)
        self.assertFalse(self.reviewed.available_for_archive_memory_write)
        self.assertFalse(self.reviewed.available_for_anchor_write)
        self.assertFalse(self.reviewed.memory_write_performed)
        self.assertFalse(self.reviewed.automatic_learning_approval_created)
        self.assertFalse(self.reviewed.task_behavior_changed)
        self.assertFalse(self.reviewed.action_authority_changed)
        self.assertTrue(
            integration.validate_feedback_derived_reviewed_concept_record(
                self.reviewed
            )["valid"]
        )

    def test_working_readback_integration_builds_from_feedback_reviewed_concept(self) -> None:
        self.assertEqual(self.working.target_memory_layer, "working_readback")
        self.assertEqual(
            self.working.working_readback_integration_status,
            "integrated_to_working_readback",
        )
        self.assertTrue(self.working.available_for_future_task_working_memory_readback)
        self.assertTrue(self.working.created_memory_learning_trace)
        self.assertTrue(self.working.created_memory_routing_trace)
        self.assertTrue(self.working.created_memory_application_data)
        self.assertTrue(self.working.created_inactive_task_working_memory_readback_hint)
        self.assertTrue(self.working.memory_learning_trace_id)
        self.assertTrue(self.working.memory_routing_trace_id)
        self.assertTrue(self.working.memory_application_data_id)
        self.assertTrue(self.working.task_working_memory_readback_hint_id)
        self.assertTrue(
            integration.validate_feedback_derived_reviewed_concept_working_readback_integration_record(
                self.working
            )["valid"]
        )

    def test_working_readback_blocks_forbidden_targets(self) -> None:
        cases = {
            "target-core-memory": "core_memory",
            "target-long-term-memory": "long_term_memory",
            "target-archive-memory": "archive_memory",
            "target-anchor": "anchor_layer",
        }
        for case, target in cases.items():
            with self.subTest(case=case):
                payload = integration.build_demo_blocked_feedback_reviewed_concept_integration(
                    case
                )
                record = payload[
                    "feedback_derived_reviewed_concept_working_readback_integration"
                ]
                audit = payload[
                    "feedback_derived_reviewed_concept_integration_safety_audit"
                ]
                self.assertEqual(record["target_memory_layer"], target)
                self.assertEqual(
                    record["working_readback_integration_status"],
                    "blocked_forbidden_memory_layer",
                )
                self.assertFalse(audit["working_readback_only_confirmed"])

    def test_readback_seed_maps_supported_concept_kinds(self) -> None:
        cases = {
            "positive-affordance": "use_known_success_path",
            "negative-affordance": "avoid_repeated_failure",
            "goal-completion": "goal_completion_hint",
            "no-progress": "no_progress_warning",
            "observation-context": "observe_before_retry",
        }
        for case, expected_kind in cases.items():
            with self.subTest(case=case):
                payload = integration.build_demo_feedback_reviewed_concept_integration_case(case)
                seed = payload["feedback_derived_reviewed_concept_readback_seed"]
                self.assertIsNotNone(seed)
                self.assertEqual(seed["hint_kind"], expected_kind)
                self.assertTrue(seed["advisory_only"])
                self.assertTrue(seed["single_task_lifetime"])
                self.assertTrue(seed["future_task_initialization_only"])
                self.assertFalse(seed["candidate_ordering_changed"])
                self.assertFalse(seed["selected_action_changed"])
                self.assertFalse(seed["final_action_changed"])
                self.assertFalse(seed["direct_command_created"])
                self.assertFalse(seed["execution_created"])

    def test_readback_seed_not_created_for_unknown_or_system_fault(self) -> None:
        unknown = integration.build_demo_unknown_held_feedback_reviewed_concept_integration()
        system_fault = (
            integration.build_demo_system_fault_held_feedback_reviewed_concept_integration()
        )
        self.assertIsNone(unknown["feedback_derived_reviewed_concept_readback_seed"])
        self.assertIsNone(system_fault["feedback_derived_reviewed_concept_readback_seed"])
        self.assertNotEqual(
            unknown["feedback_derived_reviewed_concept"]["reviewed_concept_status"],
            "feedback_reviewed_concept_created",
        )
        self.assertNotEqual(
            system_fault["feedback_derived_reviewed_concept"][
                "reviewed_concept_status"
            ],
            "feedback_reviewed_concept_created",
        )

    def test_rollback_record_created_and_applies(self) -> None:
        self.assertEqual(self.rollback.rollback_status, "rollback_record_created")
        self.assertTrue(self.rollback.reviewed_concept_created_before_rollback)
        self.assertTrue(self.rollback.working_readback_integrated_before_rollback)
        self.assertFalse(self.rollback.core_memory_write_performed)
        self.assertFalse(self.rollback.task_behavior_changed)
        applied = integration.apply_feedback_derived_reviewed_concept_rollback(
            self.rollback
        )
        self.assertEqual(
            applied.rollback_status,
            "rollback_applied_to_withdraw_working_readback_integration",
        )
        self.assertFalse(applied.reviewed_concept_available_after_rollback)
        self.assertFalse(applied.working_readback_available_after_rollback)

    def test_safety_audit_passes_valid_integration(self) -> None:
        validation = (
            integration.validate_feedback_derived_reviewed_concept_integration_safety_audit(
                self.audit
            )
        )
        self.assertTrue(validation["valid"])
        self.assertEqual(
            self.audit.audit_status,
            "passed_feedback_reviewed_concept_working_readback_integration",
        )
        self.assertTrue(self.audit.feedback_reviewed_concept_created)
        self.assertTrue(self.audit.working_readback_integration_created)
        self.assertTrue(self.audit.future_task_readback_available)
        self.assertTrue(self.audit.working_readback_only_confirmed)
        self.assertTrue(self.audit.no_core_memory_write)
        self.assertTrue(self.audit.no_long_term_memory_write)
        self.assertTrue(self.audit.no_archive_memory_write)
        self.assertTrue(self.audit.no_anchor_write)
        self.assertTrue(self.audit.no_automatic_learning_approval)
        self.assertTrue(self.audit.no_action_authority_change)
        self.assertTrue(self.audit.no_task_behavior_change)

    def test_safety_audit_blocks_expected_cases(self) -> None:
        cases = {
            "invalid-refinement": "blocked_invalid_refinement",
            "invalid-refinement-audit": "blocked_invalid_refinement",
            "missing-teacher-gate": "blocked_invalid_teacher_gate",
            "unhandled-counterexamples": "blocked_invalid_refinement",
            "target-core-memory": "blocked_invalid_working_readback_integration",
            "target-long-term-memory": "blocked_invalid_working_readback_integration",
            "target-archive-memory": "blocked_invalid_working_readback_integration",
            "target-anchor": "blocked_invalid_working_readback_integration",
            "automatic-learning-approval": "blocked_automatic_learning_approval_detected",
            "action-authority-detected": "blocked_action_authority_detected",
            "behavior-change-detected": "blocked_behavior_change_detected",
            "missing-rollback": "blocked_missing_rollback",
        }
        for case, expected_status in cases.items():
            with self.subTest(case=case):
                payload = integration.build_demo_blocked_feedback_reviewed_concept_integration(
                    case
                )
                audit = payload[
                    "feedback_derived_reviewed_concept_integration_safety_audit"
                ]
                self.assertEqual(audit["audit_status"], expected_status)

    def test_teacher_rejected_does_not_create_reviewed_concept(self) -> None:
        payload = integration.build_demo_blocked_teacher_rejected_feedback_reviewed_concept()
        self.assertEqual(
            payload["feedback_reviewed_concept_gate"]["teacher_gate_status"],
            "rejected",
        )
        self.assertEqual(
            payload["feedback_derived_reviewed_concept"]["reviewed_concept_status"],
            "rejected_by_teacher",
        )
        self.assertIsNone(payload["feedback_derived_reviewed_concept_readback_seed"])

    def test_validation_detects_forbidden_reviewed_concept_authority(self) -> None:
        record = replace(self.reviewed, available_for_core_memory_write=True)
        validation = integration.validate_feedback_derived_reviewed_concept_record(record)
        self.assertFalse(validation["valid"])
        self.assertIn("forbidden_memory_availability_detected", validation["error_codes"])

    def test_cli_commands_work(self) -> None:
        commands = (
            ("integrate-demo-reviewed-concept",),
            ("show-demo-teacher-gate",),
            ("show-demo-reviewed-concept",),
            ("show-demo-working-readback-integration",),
            ("show-demo-readback-seed",),
            ("show-demo-rollback",),
            ("show-demo-safety-audit",),
            ("validate-demo-integration",),
            ("integrate-demo-case", "--case", "positive-affordance"),
            ("integrate-demo-case", "--case", "negative-affordance"),
            ("integrate-demo-case", "--case", "goal-completion"),
            ("integrate-demo-case", "--case", "no-progress"),
            ("integrate-demo-case", "--case", "observation-context"),
            ("integrate-demo-blocked", "--case", "invalid-refinement"),
            ("integrate-demo-blocked", "--case", "invalid-refinement-audit"),
            ("integrate-demo-blocked", "--case", "missing-teacher-gate"),
            ("integrate-demo-blocked", "--case", "teacher-rejected"),
            ("integrate-demo-blocked", "--case", "unhandled-counterexamples"),
            ("integrate-demo-blocked", "--case", "target-core-memory"),
            ("integrate-demo-blocked", "--case", "target-long-term-memory"),
            ("integrate-demo-blocked", "--case", "target-archive-memory"),
            ("integrate-demo-blocked", "--case", "target-anchor"),
            ("integrate-demo-blocked", "--case", "automatic-learning-approval"),
            ("integrate-demo-blocked", "--case", "action-authority-detected"),
            ("integrate-demo-blocked", "--case", "behavior-change-detected"),
            ("integrate-demo-blocked", "--case", "missing-rollback"),
        )
        for command in commands:
            with self.subTest(command=command):
                result = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "ashl_core_v1.learning.feedback_refined_concept_reviewed_readback_integration_cli",
                        *command,
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                json.loads(result.stdout)

    def test_guided_console_demo_and_cli_work(self) -> None:
        payload = integrate_feedback_reviewed_concept_demo_from_guided_cradle_growth_console()
        validation = (
            validate_feedback_reviewed_concept_integration_from_guided_cradle_growth_console()
        )
        self.assertEqual(
            payload["guided_console_action"],
            "learning_integrate_feedback_reviewed_concept_demo",
        )
        self.assertFalse(payload["core_memory_write_performed"])
        self.assertFalse(payload["automatic_learning_approval_created"])
        self.assertFalse(payload["action_authority_changed"])
        self.assertTrue(validation["validation"]["valid"])
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core_v1.runtime.guided_cradle_growth_teacher_console_cli",
                "learning-validate-feedback-reviewed-concept-integration",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        cli_payload = json.loads(result.stdout)
        self.assertTrue(cli_payload["validation"]["valid"])
        self.assertFalse(cli_payload["core_memory_write_performed"])

    def test_no_repo_data_directory_created(self) -> None:
        self.assertFalse(Path("ashl_core_v1/data").exists())


if __name__ == "__main__":
    unittest.main()
