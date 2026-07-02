from __future__ import annotations

import json
import subprocess
import sys
import unittest
from dataclasses import replace
from pathlib import Path

from ashl_core_v1.audit import feedback_reviewed_concept_closed_loop_replay as replay
from ashl_core_v1.learning.feedback_refined_concept_reviewed_readback_integration import (
    FeedbackDerivedReviewedConceptIntegrationSafetyAudit,
    FeedbackDerivedReviewedConceptReadbackSeedRecord,
    FeedbackDerivedReviewedConceptRecord,
    FeedbackDerivedReviewedConceptWorkingReadbackIntegrationRecord,
)
from ashl_core_v1.runtime.guided_cradle_growth_teacher_console import (
    replay_feedback_reviewed_concept_loop_demo_from_guided_cradle_growth_console,
    validate_feedback_reviewed_concept_replay_from_guided_cradle_growth_console,
)


AUDIT_CLI = "ashl_core_v1.audit.feedback_reviewed_concept_closed_loop_replay_cli"
GUIDED_CLI = "ashl_core_v1.runtime.guided_cradle_growth_teacher_console_cli"


class FeedbackReviewedConceptClosedLoopReplayTests(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = replay.build_demo_negative_affordance_closed_loop_replay()
        self.reviewed = FeedbackDerivedReviewedConceptRecord.from_dict(
            self.payload["feedback_derived_reviewed_concept"]
        )
        self.integration = (
            FeedbackDerivedReviewedConceptWorkingReadbackIntegrationRecord.from_dict(
                self.payload[
                    "feedback_derived_reviewed_concept_working_readback_integration"
                ]
            )
        )
        self.seed = FeedbackDerivedReviewedConceptReadbackSeedRecord.from_dict(
            self.payload["feedback_derived_reviewed_concept_readback_seed"]
        )
        self.integration_audit = (
            FeedbackDerivedReviewedConceptIntegrationSafetyAudit.from_dict(
                self.payload[
                    "feedback_derived_reviewed_concept_integration_safety_audit"
                ]
            )
        )
        self.gate = replay.FeedbackReviewedConceptReplayGate.from_dict(
            self.payload["feedback_reviewed_concept_replay_gate"]
        )
        self.initialization = (
            replay.FeedbackReviewedConceptReplayTaskInitializationRecord.from_dict(
                self.payload["feedback_reviewed_concept_replay_task_initialization"]
            )
        )
        self.action_chain = replay.FeedbackReviewedConceptReplayActionChainRecord.from_dict(
            self.payload["feedback_reviewed_concept_replay_action_chain"]
        )
        self.execution = replay.FeedbackReviewedConceptReplayExecutionRecord.from_dict(
            self.payload["feedback_reviewed_concept_replay_execution"]
        )
        self.outcome = replay.FeedbackReviewedConceptReplayOutcomeRecord.from_dict(
            self.payload["feedback_reviewed_concept_replay_outcome"]
        )
        self.contrast = replay.FeedbackReviewedConceptReplayContrastRecord.from_dict(
            self.payload["feedback_reviewed_concept_replay_contrast"]
        )
        self.rollback = replay.FeedbackReviewedConceptReplayRollbackRecord.from_dict(
            self.payload["feedback_reviewed_concept_replay_rollback"]
        )
        self.audit = replay.FeedbackReviewedConceptClosedLoopReplayAudit.from_dict(
            self.payload["feedback_reviewed_concept_closed_loop_replay_audit"]
        )

    def test_replay_gate_builds_from_valid_package_92_feedback_reviewed_concept(self) -> None:
        self.assertEqual(
            self.gate.source_feedback_derived_reviewed_concept_id,
            self.reviewed.feedback_derived_reviewed_concept_id,
        )
        self.assertEqual(
            self.gate.source_working_readback_integration_id,
            self.integration.working_readback_integration_id,
        )
        self.assertEqual(self.gate.source_readback_seed_id, self.seed.readback_seed_id)
        self.assertEqual(self.gate.readback_hint_kind, "avoid_repeated_failure")
        self.assertTrue(
            replay.validate_feedback_reviewed_concept_replay_gate(self.gate)["valid"]
        )

    def test_replay_gate_requires_package_92_integration_safety_audit_pass(self) -> None:
        invalid_audit = replace(
            self.integration_audit,
            audit_status="blocked_invalid_working_readback_integration",
            working_readback_integration_valid=False,
        )
        gate = replay.build_feedback_reviewed_concept_replay_gate(
            reviewed_concept=self.reviewed,
            working_readback_integration=self.integration,
            readback_seed=self.seed,
            integration_safety_audit=invalid_audit,
        )
        self.assertEqual(
            gate.teacher_gate_status,
            "blocked_invalid_working_readback_integration",
        )

    def test_replay_gate_source_rules(self) -> None:
        explicit_blank = replay.build_feedback_reviewed_concept_replay_gate(
            reviewed_concept=self.reviewed,
            working_readback_integration=self.integration,
            readback_seed=self.seed,
            integration_safety_audit=self.integration_audit,
            approval_source="explicit_teacher_review",
            approval_actor_role="teacher",
            teacher_gate_text="",
        )
        self.assertIn(
            "explicit_review_requires_teacher_gate_text",
            replay.validate_feedback_reviewed_concept_replay_gate(explicit_blank)[
                "error_codes"
            ],
        )
        explicit_bad_role = replay.build_feedback_reviewed_concept_replay_gate(
            reviewed_concept=self.reviewed,
            working_readback_integration=self.integration,
            readback_seed=self.seed,
            integration_safety_audit=self.integration_audit,
            approval_source="explicit_teacher_review",
            approval_actor_role="system_demo",
            teacher_gate_text="approved",
        )
        self.assertIn(
            "explicit_review_requires_teacher_or_project_owner",
            replay.validate_feedback_reviewed_concept_replay_gate(explicit_bad_role)[
                "error_codes"
            ],
        )
        demo_bad_role = replay.build_feedback_reviewed_concept_replay_gate(
            reviewed_concept=self.reviewed,
            working_readback_integration=self.integration,
            readback_seed=self.seed,
            integration_safety_audit=self.integration_audit,
            approval_source="demo_review",
            approval_actor_role="teacher",
        )
        self.assertIn(
            "demo_review_requires_system_demo_role",
            replay.validate_feedback_reviewed_concept_replay_gate(demo_bad_role)[
                "error_codes"
            ],
        )

    def test_replay_gate_approves_closed_loop_replay_and_bounded_sandbox_only(self) -> None:
        self.assertTrue(self.gate.approved_for_closed_loop_replay)
        self.assertTrue(self.gate.approved_for_bounded_sandbox_execution)
        self.assertFalse(self.gate.approved_for_external_execution)
        self.assertFalse(self.gate.approved_for_unity_execution)
        self.assertFalse(self.gate.approved_for_bridge_execution)
        self.assertFalse(self.gate.approved_for_free_action_selection)
        self.assertFalse(self.gate.approved_for_memory_layer_write)
        self.assertFalse(self.gate.approved_for_automatic_learning_approval)
        self.assertFalse(self.gate.approved_for_behavior_learning)

    def test_replay_task_initializes_new_task_working_memory_with_readback(self) -> None:
        self.assertEqual(
            self.initialization.initialization_status,
            "replay_task_initialized_with_feedback_readback",
        )
        self.assertTrue(self.initialization.task_working_memory_initialized)
        self.assertTrue(self.initialization.working_memory_readback_slot_populated)
        self.assertTrue(self.initialization.readback_hint_applied)
        self.assertEqual(
            self.initialization.source_feedback_derived_reviewed_concept_id,
            self.reviewed.feedback_derived_reviewed_concept_id,
        )
        self.assertEqual(
            self.initialization.source_readback_seed_id,
            self.seed.readback_seed_id,
        )

    def test_replay_task_blocks_running_task_mutation(self) -> None:
        payload = replay.build_demo_blocked_running_task_mutation_replay()
        initialization = payload["feedback_reviewed_concept_replay_task_initialization"]
        self.assertEqual(
            initialization["initialization_status"],
            "blocked_running_task_mutation_attempt",
        )
        self.assertFalse(initialization["task_working_memory_initialized"])

    def test_replay_action_chain_builds_candidate_ordering_from_feedback_readback(self) -> None:
        self.assertEqual(
            self.action_chain.baseline_candidate_ordering,
            ("step_forward", "observe", "turn_left"),
        )
        self.assertEqual(
            self.action_chain.readback_influenced_candidate_ordering,
            ("observe", "turn_left", "step_forward"),
        )
        self.assertTrue(self.action_chain.candidate_ordering_changed)

    def test_ordering_helper_cases(self) -> None:
        positive = replay.build_demo_positive_affordance_closed_loop_replay()
        positive_chain = positive["feedback_reviewed_concept_replay_action_chain"]
        self.assertEqual(positive_chain["readback_influenced_candidate_ordering"][0], "step_forward")
        no_progress = replay.build_demo_no_progress_closed_loop_replay()
        no_progress_chain = no_progress["feedback_reviewed_concept_replay_action_chain"]
        self.assertEqual(no_progress_chain["readback_influenced_candidate_ordering"][0], "observe")
        observation = replay.build_demo_observation_context_closed_loop_replay()
        observation_chain = observation["feedback_reviewed_concept_replay_action_chain"]
        self.assertEqual(observation_chain["readback_influenced_candidate_ordering"][0], "observe")

    def test_action_chain_creates_selected_final_and_direct_command_without_external_authority(self) -> None:
        self.assertEqual(
            self.action_chain.action_chain_status,
            "replay_action_chain_built_to_direct_command",
        )
        self.assertTrue(self.action_chain.selected_action_created)
        self.assertTrue(self.action_chain.final_action_created)
        self.assertTrue(self.action_chain.direct_command_created)
        self.assertEqual(self.action_chain.selected_action_candidate_id, "observe")
        self.assertEqual(self.action_chain.final_action_candidate_id, "observe")
        self.assertEqual(self.action_chain.direct_command, "observe")
        self.assertFalse(self.action_chain.external_execution_created)
        self.assertFalse(self.action_chain.unity_execution_created)
        self.assertFalse(self.action_chain.bridge_execution_created)

    def test_replay_execution_performs_bounded_sandbox_execution(self) -> None:
        self.assertEqual(
            self.execution.execution_status,
            "bounded_sandbox_replay_execution_completed",
        )
        self.assertTrue(self.execution.sandbox_execution_created)
        self.assertTrue(self.execution.bounded_sandbox_execution_created)
        self.assertTrue(self.execution.pre_execution_snapshot_id)
        self.assertTrue(self.execution.sandbox_restore_id)
        self.assertTrue(self.execution.restore_available)

    def test_replay_execution_blocks_unsupported_and_external_targets(self) -> None:
        unsupported_chain = replace(
            self.action_chain,
            direct_command="unsupported",
            selected_action_candidate_id="unsupported",
            final_action_candidate_id="unsupported",
        )
        unsupported = replay.execute_feedback_reviewed_concept_replay_sandbox(
            replay_gate=self.gate,
            replay_action_chain=unsupported_chain,
        )
        self.assertEqual(
            unsupported.execution_status,
            "blocked_unsupported_direct_command",
        )
        blocked_cases = {
            "external-execution": "blocked_external_execution_detected",
            "unity-execution": "blocked_external_execution_detected",
            "bridge-execution": "blocked_external_execution_detected",
        }
        for case, status in blocked_cases.items():
            with self.subTest(case=case):
                payload = replay.build_demo_blocked_feedback_reviewed_concept_closed_loop_replay(case)
                audit = payload["feedback_reviewed_concept_closed_loop_replay_audit"]
                self.assertEqual(audit["audit_status"], status)

    def test_replay_execution_does_not_create_behavior_learning_or_memory_write(self) -> None:
        self.assertFalse(self.execution.task_behavior_learning_created)
        self.assertFalse(self.execution.memory_layer_write_performed)
        self.assertFalse(self.execution.automatic_learning_approval_created)

    def test_replay_outcome_creates_sense_evaluation_and_closure_only(self) -> None:
        self.assertEqual(self.outcome.outcome_status, "replay_outcome_closed")
        self.assertTrue(self.outcome.sense_observation_created)
        self.assertTrue(self.outcome.outcome_evaluation_created)
        self.assertTrue(self.outcome.task_closure_created)
        self.assertEqual(self.outcome.outcome_class, "observation_only")
        self.assertEqual(self.outcome.closure_status, "task_closed_observation_only")
        self.assertFalse(self.outcome.learning_feedback_candidate_created)
        self.assertFalse(self.outcome.new_reviewed_concept_created_from_replay)
        self.assertFalse(self.outcome.memory_write_performed)
        self.assertFalse(self.outcome.automatic_learning_approval_created)

    def test_contrast_passes_when_readback_changes_action_chain(self) -> None:
        self.assertEqual(
            self.contrast.contrast_status,
            "passed_feedback_readback_influenced_action_chain",
        )
        self.assertTrue(self.contrast.candidate_ordering_changed_by_feedback_readback)
        self.assertTrue(self.contrast.selected_action_changed_by_feedback_readback)
        self.assertTrue(self.contrast.final_action_changed_by_feedback_readback)
        self.assertTrue(self.contrast.direct_command_changed_by_feedback_readback)
        self.assertTrue(self.contrast.execution_created_by_feedback_replay)

    def test_contrast_passes_visible_no_action_difference(self) -> None:
        payload = replay.build_demo_visible_no_action_difference_replay()
        contrast = payload["feedback_reviewed_concept_replay_contrast"]
        audit = payload["feedback_reviewed_concept_closed_loop_replay_audit"]
        self.assertEqual(
            contrast["contrast_status"],
            "passed_feedback_readback_visible_no_action_difference",
        )
        self.assertEqual(
            audit["audit_status"],
            "passed_feedback_readback_visible_no_action_difference",
        )

    def test_contrast_detects_missing_baseline_and_replay_chain(self) -> None:
        missing_baseline = replay.build_feedback_reviewed_concept_replay_contrast(
            replay_gate=self.gate,
            replay_task_initialization=None,
            replay_action_chain=self.action_chain,
            replay_execution=self.execution,
        )
        self.assertEqual(missing_baseline.contrast_status, "blocked_missing_baseline")
        missing_chain = replay.build_feedback_reviewed_concept_replay_contrast(
            replay_gate=self.gate,
            replay_task_initialization=self.initialization,
            replay_action_chain=None,
            replay_execution=self.execution,
        )
        self.assertEqual(missing_chain.contrast_status, "blocked_missing_replay_chain")

    def test_rollback_record_restores_sandbox_without_deleting_source_reviewed_concept(self) -> None:
        self.assertTrue(self.rollback.rollback_available)
        self.assertTrue(self.rollback.rollback_applied)
        self.assertEqual(
            self.rollback.rollback_status,
            "rollback_applied_to_restore_sandbox_state",
        )
        self.assertEqual(
            self.rollback.sandbox_state_after_restore,
            self.rollback.sandbox_state_before_execution,
        )
        applied = replay.apply_feedback_reviewed_concept_replay_rollback(self.rollback)
        self.assertEqual(
            applied["rollback_status"],
            "rollback_applied_to_restore_sandbox_state",
        )
        self.assertEqual(
            self.reviewed.reviewed_concept_status,
            "feedback_reviewed_concept_created",
        )

    def test_audit_passes_negative_positive_and_visible_no_difference_replays(self) -> None:
        cases = {
            "negative": replay.build_demo_negative_affordance_closed_loop_replay,
            "positive": replay.build_demo_positive_affordance_closed_loop_replay,
            "visible": replay.build_demo_visible_no_action_difference_replay,
        }
        for case, builder in cases.items():
            with self.subTest(case=case):
                payload = builder()
                audit = payload["feedback_reviewed_concept_closed_loop_replay_audit"]
                self.assertIn(
                    audit["audit_status"],
                    {
                        "passed_feedback_reviewed_concept_closed_loop_replay",
                        "passed_feedback_readback_visible_no_action_difference",
                    },
                )

    def test_audit_blocks_declared_cases(self) -> None:
        expected = {
            "invalid-feedback-reviewed-concept": "blocked_invalid_feedback_reviewed_concept",
            "invalid-readback-integration": "blocked_invalid_readback_integration",
            "missing-replay-gate": "blocked_invalid_replay_gate",
            "running-task-mutation": "blocked_replay_task_initialization_failed",
            "external-execution": "blocked_external_execution_detected",
            "unity-execution": "blocked_external_execution_detected",
            "bridge-execution": "blocked_external_execution_detected",
            "memory-write-detected": "blocked_memory_write_detected",
            "automatic-learning-approval": "blocked_automatic_learning_approval_detected",
            "behavior-learning": "blocked_behavior_learning_detected",
            "learning-feedback-created-from-replay": "blocked_outcome_replay_failed",
            "new-reviewed-concept-created-from-replay": "blocked_outcome_replay_failed",
            "missing-rollback": "blocked_missing_rollback",
        }
        for case, status in expected.items():
            with self.subTest(case=case):
                payload = replay.build_demo_blocked_feedback_reviewed_concept_closed_loop_replay(case)
                audit = payload["feedback_reviewed_concept_closed_loop_replay_audit"]
                self.assertEqual(audit["audit_status"], status)

    def test_cli_commands_work(self) -> None:
        commands = [
            ["replay-demo-loop"],
            ["show-demo-replay-gate"],
            ["show-demo-task-initialization"],
            ["show-demo-action-chain"],
            ["show-demo-execution"],
            ["show-demo-outcome"],
            ["show-demo-contrast"],
            ["show-demo-rollback"],
            ["show-demo-audit"],
            ["validate-demo-replay"],
            ["replay-demo-case", "--case", "negative-affordance"],
            ["replay-demo-case", "--case", "positive-affordance"],
            ["replay-demo-case", "--case", "goal-completion"],
            ["replay-demo-case", "--case", "no-progress"],
            ["replay-demo-case", "--case", "observation-context"],
            ["replay-demo-case", "--case", "visible-no-action-difference"],
        ]
        for command in commands:
            with self.subTest(command=command):
                result = self._run_cli(AUDIT_CLI, command)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIsInstance(json.loads(result.stdout), dict)

    def test_cli_blocked_cases_work(self) -> None:
        cases = [
            "invalid-feedback-reviewed-concept",
            "invalid-readback-integration",
            "missing-replay-gate",
            "teacher-rejected",
            "running-task-mutation",
            "external-execution",
            "unity-execution",
            "bridge-execution",
            "memory-write-detected",
            "automatic-learning-approval",
            "behavior-learning",
            "learning-feedback-created-from-replay",
            "new-reviewed-concept-created-from-replay",
            "missing-rollback",
        ]
        for case in cases:
            with self.subTest(case=case):
                result = self._run_cli(
                    AUDIT_CLI,
                    ["replay-demo-blocked", "--case", case],
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                payload = json.loads(result.stdout)
                self.assertTrue(
                    payload["feedback_reviewed_concept_closed_loop_replay_audit"][
                        "audit_status"
                    ].startswith("blocked_")
                )

    def test_guided_console_feedback_reviewed_concept_replay_demo_works(self) -> None:
        payload = replay_feedback_reviewed_concept_loop_demo_from_guided_cradle_growth_console()
        self.assertEqual(
            payload["feedback_reviewed_concept_closed_loop_replay_audit"][
                "audit_status"
            ],
            "passed_feedback_reviewed_concept_closed_loop_replay",
        )
        validation = validate_feedback_reviewed_concept_replay_from_guided_cradle_growth_console()
        self.assertTrue(validation["validation"]["valid"])
        result = self._run_cli(
            GUIDED_CLI,
            ["audit-validate-feedback-reviewed-concept-replay"],
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)["validation"]["valid"])

    def test_no_repo_data_created(self) -> None:
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _run_cli(self, module: str, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", module, *args],
            cwd=Path(__file__).resolve().parents[2],
            text=True,
            capture_output=True,
            check=False,
        )


if __name__ == "__main__":
    unittest.main()
