from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from ashl_core_v1.audit import first_action_to_reviewed_concept_loop_milestone as milestone
from ashl_core_v1.runtime.guided_cradle_growth_teacher_console import (
    audit_first_action_reviewed_concept_loop_demo_from_guided_cradle_growth_console,
)


AUDIT_CLI = "ashl_core_v1.audit.first_action_to_reviewed_concept_loop_milestone_cli"
GUIDED_CLI = "ashl_core_v1.runtime.guided_cradle_growth_teacher_console_cli"


class FirstActionToReviewedConceptLoopMilestoneTests(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = milestone.build_demo_first_closed_loop_milestone()
        self.chain = milestone.FirstClosedLoopEvidenceChainRecord.from_dict(
            self.payload["first_closed_loop_evidence_chain"]
        )
        self.boundary = milestone.FirstClosedLoopBoundaryAuditRecord.from_dict(
            self.payload["first_closed_loop_boundary_audit"]
        )
        self.replay = milestone.FirstClosedLoopReplayVerificationRecord.from_dict(
            self.payload["first_closed_loop_replay_verification"]
        )
        self.milestone = milestone.FirstClosedLoopMilestoneRecord.from_dict(
            self.payload["first_closed_loop_milestone"]
        )
        self.readiness = milestone.FirstClosedLoopNextStageReadinessRecord.from_dict(
            self.payload["first_closed_loop_next_stage_readiness"]
        )

    def test_evidence_chain_builds_from_complete_demo_loop(self) -> None:
        validation = milestone.validate_first_closed_loop_evidence_chain_record(
            self.chain
        )
        self.assertTrue(validation["valid"])
        self.assertTrue(self.chain.chain_complete)
        self.assertEqual(self.chain.evidence_chain_status, "chain_complete")

    def test_evidence_chain_includes_first_action_path(self) -> None:
        self.assertIn("selected_action_application", self.chain.first_task_selected_action_id or "")
        self.assertIn("final_action_application", self.chain.first_task_final_action_id or "")
        self.assertIsNotNone(self.chain.first_task_direct_command_id)
        self.assertIsNotNone(self.chain.first_task_sandbox_execution_id)
        self.assertIn(
            "direct_command_sandbox_execution_audit",
            self.chain.first_task_execution_audit_id or "",
        )

    def test_evidence_chain_includes_sense_and_task_evaluation_path(self) -> None:
        self.assertIsNotNone(self.chain.sense_observation_id)
        self.assertIsNotNone(self.chain.sense_handoff_id)
        self.assertIsNotNone(self.chain.outcome_evaluation_id)
        self.assertIsNotNone(self.chain.goal_delta_evaluation_id)
        self.assertIsNotNone(self.chain.task_closure_id)

    def test_evidence_chain_includes_learning_feedback_path(self) -> None:
        self.assertIsNotNone(self.chain.learning_feedback_candidate_id)
        self.assertIsNotNone(self.chain.learning_feedback_evidence_packet_id)
        self.assertIsNotNone(self.chain.concept_candidate_draft_id)
        self.assertIsNotNone(self.chain.feedback_refinement_id)
        self.assertIsNotNone(self.chain.feedback_scope_check_id)
        self.assertIsNotNone(self.chain.feedback_counterexample_check_id)

    def test_evidence_chain_includes_feedback_reviewed_concept_path(self) -> None:
        self.assertIsNotNone(self.chain.feedback_derived_reviewed_concept_id)
        self.assertIsNotNone(self.chain.working_readback_integration_id)
        self.assertIsNotNone(self.chain.readback_seed_id)

    def test_evidence_chain_includes_second_task_replay_path(self) -> None:
        self.assertIsNotNone(self.chain.replay_gate_id)
        self.assertIsNotNone(self.chain.replay_task_initialization_id)
        self.assertIsNotNone(self.chain.replay_action_chain_id)
        self.assertIsNotNone(self.chain.replay_execution_id)
        self.assertIsNotNone(self.chain.replay_outcome_id)
        self.assertIsNotNone(self.chain.replay_contrast_id)
        self.assertIsNotNone(self.chain.replay_audit_id)

    def test_evidence_chain_detects_missing_required_paths(self) -> None:
        cases = {
            "missing-first-action-path": "chain_incomplete_missing_first_action_path",
            "missing-sense-observation": "chain_incomplete_missing_sense_task_path",
            "missing-task-closure": "chain_incomplete_missing_sense_task_path",
            "missing-learning-feedback-candidate": (
                "chain_incomplete_missing_learning_feedback_path"
            ),
            "missing-feedback-reviewed-concept": (
                "chain_incomplete_missing_reviewed_concept_path"
            ),
            "missing-working-readback": (
                "chain_incomplete_missing_reviewed_concept_path"
            ),
            "missing-second-task-replay": "chain_incomplete_missing_replay_path",
        }
        for case, expected_status in cases.items():
            with self.subTest(case=case):
                payload = milestone.build_demo_blocked_first_closed_loop_milestone(case)
                chain = payload["first_closed_loop_evidence_chain"]
                self.assertEqual(chain["evidence_chain_status"], expected_status)
                self.assertTrue(chain["missing_links"])

    def test_boundary_audit_passes_for_bounded_teacher_gated_loop(self) -> None:
        validation = milestone.validate_first_closed_loop_boundary_audit_record(
            self.boundary
        )
        self.assertTrue(validation["valid"])
        self.assertEqual(
            self.boundary.boundary_status,
            "passed_bounded_teacher_gated_loop_boundaries",
        )
        self.assertTrue(self.boundary.bounded_sandbox_only_confirmed)
        self.assertTrue(self.boundary.teacher_gated_path_confirmed)

    def test_boundary_audit_confirms_no_forbidden_execution_or_memory_write(self) -> None:
        self.assertTrue(self.boundary.no_external_execution)
        self.assertTrue(self.boundary.no_unity_execution)
        self.assertTrue(self.boundary.no_bridge_execution)
        self.assertTrue(self.boundary.no_network_execution)
        self.assertTrue(self.boundary.no_filesystem_execution)
        self.assertTrue(self.boundary.no_core_memory_write)
        self.assertTrue(self.boundary.no_long_term_memory_write)
        self.assertTrue(self.boundary.no_archive_memory_write)
        self.assertTrue(self.boundary.no_anchor_write)

    def test_boundary_audit_confirms_no_automatic_or_recursive_learning(self) -> None:
        self.assertTrue(self.boundary.no_automatic_learning_approval)
        self.assertTrue(self.boundary.no_behavior_learning)
        self.assertTrue(self.boundary.no_free_action_selection)
        self.assertTrue(self.boundary.no_scheduler)
        self.assertTrue(self.boundary.no_open_ended_loop)
        self.assertTrue(self.boundary.no_recursive_learning_from_replay)
        self.assertTrue(self.boundary.no_new_reviewed_concept_from_replay)

    def test_boundary_audit_blocks_forbidden_cases(self) -> None:
        cases = {
            "external-execution-detected": "failed_external_execution_detected",
            "memory-write-detected": "failed_memory_layer_write_detected",
            "automatic-learning-approval": (
                "failed_automatic_learning_approval_detected"
            ),
            "behavior-learning": "failed_behavior_learning_detected",
            "recursive-learning-from-replay": "failed_recursive_learning_detected",
            "free-action-selection": "failed_free_action_selection_detected",
        }
        for case, expected_status in cases.items():
            with self.subTest(case=case):
                payload = milestone.build_demo_blocked_first_closed_loop_milestone(case)
                boundary = payload["first_closed_loop_boundary_audit"]
                self.assertEqual(boundary["boundary_status"], expected_status)

    def test_replay_verification_passes_with_action_chain_influence(self) -> None:
        validation = milestone.validate_first_closed_loop_replay_verification_record(
            self.replay
        )
        self.assertTrue(validation["valid"])
        self.assertEqual(
            self.replay.replay_verification_status,
            "replay_verified_with_action_chain_influence",
        )
        self.assertTrue(self.replay.feedback_reviewed_concept_used)
        self.assertTrue(self.replay.working_readback_seed_used)
        self.assertTrue(self.replay.readback_hint_visible_in_second_task)
        self.assertTrue(self.replay.candidate_ordering_influenced)
        self.assertTrue(self.replay.selected_action_replayed)
        self.assertTrue(self.replay.final_action_replayed)
        self.assertTrue(self.replay.direct_command_replayed)

    def test_replay_verification_accepts_visible_no_action_difference(self) -> None:
        payload = (
            milestone.build_demo_first_closed_loop_visible_no_action_difference_milestone()
        )
        replay = payload["first_closed_loop_replay_verification"]
        self.assertEqual(
            replay["replay_verification_status"],
            "replay_verified_visible_no_action_difference",
        )
        self.assertTrue(replay["visible_no_action_difference"])
        self.assertFalse(replay["candidate_ordering_influenced"])

    def test_replay_verification_blocks_invalid_replay_audit(self) -> None:
        payload = milestone.build_demo_blocked_invalid_replay_audit_milestone()
        replay = payload["first_closed_loop_replay_verification"]
        self.assertEqual(replay["replay_verification_status"], "blocked_invalid_replay_audit")

    def test_milestone_record_passes_complete_loop(self) -> None:
        validation = milestone.validate_first_closed_loop_milestone_record(
            self.milestone
        )
        self.assertTrue(validation["valid"])
        self.assertEqual(
            self.milestone.milestone_status,
            "passed_first_bounded_action_to_reviewed_concept_to_next_task_loop_v0",
        )
        self.assertTrue(self.milestone.first_action_path_verified)
        self.assertTrue(self.milestone.sense_task_evaluation_verified)
        self.assertTrue(self.milestone.learning_feedback_candidate_verified)
        self.assertTrue(self.milestone.feedback_concept_candidate_refinement_verified)
        self.assertTrue(self.milestone.feedback_reviewed_concept_verified)
        self.assertTrue(self.milestone.working_readback_integration_verified)
        self.assertTrue(self.milestone.second_task_replay_verified)
        self.assertTrue(self.milestone.boundary_audit_verified)

    def test_milestone_fails_incomplete_evidence_chain(self) -> None:
        payload = milestone.build_demo_blocked_missing_first_action_path_milestone()
        record = payload["first_closed_loop_milestone"]
        self.assertEqual(record["milestone_status"], "failed_incomplete_evidence_chain")

    def test_milestone_fails_boundary_audit(self) -> None:
        payload = milestone.build_demo_blocked_memory_write_milestone()
        record = payload["first_closed_loop_milestone"]
        self.assertEqual(record["milestone_status"], "failed_boundary_audit")

    def test_milestone_fails_replay_verification(self) -> None:
        payload = milestone.build_demo_blocked_invalid_replay_audit_milestone()
        record = payload["first_closed_loop_milestone"]
        self.assertEqual(record["milestone_status"], "failed_replay_verification")

    def test_milestone_claims_and_boundaries_are_narrow(self) -> None:
        self.assertIn("bounded teacher-gated", self.milestone.safe_claim)
        self.assertIn("no_autonomous_learning", self.milestone.forbidden_claims)
        self.assertIn(
            "no_automatic_learning_approval", self.milestone.forbidden_claims
        )
        self.assertIn("no_long_term_memory_write", self.milestone.forbidden_claims)
        self.assertIn("no_free_action_selection", self.milestone.forbidden_claims)
        self.assertIn("no_external_execution", self.milestone.forbidden_claims)
        self.assertIn("no_thought_engine_cognition", self.milestone.forbidden_claims)
        self.assertIn(
            "no_persistent_cross_session_growth", self.milestone.forbidden_claims
        )

    def test_next_stage_readiness_is_preview_only(self) -> None:
        validation = milestone.validate_first_closed_loop_next_stage_readiness_record(
            self.readiness
        )
        self.assertTrue(validation["valid"])
        self.assertEqual(
            self.readiness.readiness_status,
            "ready_for_bounded_multi_trial_loop_preview_only",
        )
        self.assertTrue(self.readiness.ready_for_bounded_multi_trial_loop_preview)
        self.assertFalse(self.readiness.ready_for_recursive_replay_planning)
        self.assertFalse(self.readiness.ready_for_memory_promotion)
        self.assertFalse(self.readiness.ready_for_long_term_memory)
        self.assertFalse(self.readiness.ready_for_autonomous_scheduler)
        self.assertFalse(self.readiness.ready_for_free_action_selection)
        self.assertFalse(self.readiness.ready_for_external_execution)
        self.assertFalse(self.readiness.ready_for_thought_engine)

    def test_cli_audit_demo_loop_works(self) -> None:
        payload = self._run_audit_cli("audit-demo-loop")
        self.assertEqual(
            payload["first_closed_loop_milestone"]["milestone_status"],
            "passed_first_bounded_action_to_reviewed_concept_to_next_task_loop_v0",
        )

    def test_cli_show_demo_records_work(self) -> None:
        self.assertEqual(
            self._run_audit_cli("show-demo-evidence-chain")["evidence_chain_status"],
            "chain_complete",
        )
        self.assertEqual(
            self._run_audit_cli("show-demo-boundary-audit")["boundary_status"],
            "passed_bounded_teacher_gated_loop_boundaries",
        )
        self.assertEqual(
            self._run_audit_cli("show-demo-replay-verification")[
                "replay_verification_status"
            ],
            "replay_verified_with_action_chain_influence",
        )
        self.assertEqual(
            self._run_audit_cli("show-demo-milestone")["milestone_status"],
            "passed_first_bounded_action_to_reviewed_concept_to_next_task_loop_v0",
        )
        self.assertEqual(
            self._run_audit_cli("show-demo-next-stage-readiness")[
                "readiness_status"
            ],
            "ready_for_bounded_multi_trial_loop_preview_only",
        )

    def test_cli_validate_demo_loop_works(self) -> None:
        payload = self._run_audit_cli("validate-demo-loop")
        self.assertTrue(payload["valid"])

    def test_cli_visible_no_action_difference_case_works(self) -> None:
        payload = self._run_audit_cli(
            "audit-demo-case",
            "--case",
            "visible-no-action-difference",
        )
        self.assertEqual(
            payload["first_closed_loop_milestone"]["milestone_status"],
            "passed_replay_visible_no_action_difference",
        )

    def test_cli_blocked_cases_work(self) -> None:
        cases = {
            "missing-first-action-path": "chain_incomplete_missing_first_action_path",
            "missing-sense-observation": "chain_incomplete_missing_sense_task_path",
            "missing-task-closure": "chain_incomplete_missing_sense_task_path",
            "missing-learning-feedback-candidate": (
                "chain_incomplete_missing_learning_feedback_path"
            ),
            "missing-feedback-reviewed-concept": (
                "chain_incomplete_missing_reviewed_concept_path"
            ),
            "missing-working-readback": (
                "chain_incomplete_missing_reviewed_concept_path"
            ),
            "missing-second-task-replay": "chain_incomplete_missing_replay_path",
        }
        for case, expected_status in cases.items():
            with self.subTest(case=case):
                payload = self._run_audit_cli("audit-demo-blocked", "--case", case)
                self.assertEqual(
                    payload["first_closed_loop_evidence_chain"][
                        "evidence_chain_status"
                    ],
                    expected_status,
                )

    def test_cli_blocked_boundary_cases_work(self) -> None:
        cases = {
            "invalid-replay-audit": "failed_replay_verification",
            "external-execution-detected": "failed_boundary_audit",
            "memory-write-detected": "failed_boundary_audit",
            "automatic-learning-approval": "failed_boundary_audit",
            "behavior-learning": "failed_boundary_audit",
            "recursive-learning-from-replay": "failed_boundary_audit",
            "free-action-selection": "failed_boundary_audit",
        }
        for case, expected_status in cases.items():
            with self.subTest(case=case):
                payload = self._run_audit_cli("audit-demo-blocked", "--case", case)
                self.assertEqual(
                    payload["first_closed_loop_milestone"]["milestone_status"],
                    expected_status,
                )

    def test_guided_console_first_loop_milestone_demo_works(self) -> None:
        payload = audit_first_action_reviewed_concept_loop_demo_from_guided_cradle_growth_console()
        self.assertEqual(
            payload["first_closed_loop_milestone"]["milestone_status"],
            "passed_first_bounded_action_to_reviewed_concept_to_next_task_loop_v0",
        )
        self.assertFalse(payload["new_runtime_authority_created"])
        self.assertFalse(payload["new_execution_authority_created"])
        self.assertFalse(payload["memory_layer_write_performed"])

    def test_guided_console_cli_commands_work(self) -> None:
        self.assertEqual(
            self._run_guided_cli("audit-first-action-reviewed-concept-loop-demo")[
                "first_closed_loop_milestone"
            ]["milestone_status"],
            "passed_first_bounded_action_to_reviewed_concept_to_next_task_loop_v0",
        )
        self.assertEqual(
            self._run_guided_cli("audit-show-first-loop-evidence-chain")[
                "first_closed_loop_evidence_chain"
            ]["evidence_chain_status"],
            "chain_complete",
        )
        self.assertEqual(
            self._run_guided_cli("audit-show-first-loop-boundary")[
                "first_closed_loop_boundary_audit"
            ]["boundary_status"],
            "passed_bounded_teacher_gated_loop_boundaries",
        )
        self.assertEqual(
            self._run_guided_cli("audit-show-first-loop-replay-verification")[
                "first_closed_loop_replay_verification"
            ]["replay_verification_status"],
            "replay_verified_with_action_chain_influence",
        )
        self.assertEqual(
            self._run_guided_cli("audit-show-first-loop-milestone")[
                "first_closed_loop_milestone"
            ]["milestone_status"],
            "passed_first_bounded_action_to_reviewed_concept_to_next_task_loop_v0",
        )
        self.assertEqual(
            self._run_guided_cli("audit-show-first-loop-next-stage-readiness")[
                "first_closed_loop_next_stage_readiness"
            ]["readiness_status"],
            "ready_for_bounded_multi_trial_loop_preview_only",
        )
        self.assertTrue(
            self._run_guided_cli("audit-validate-first-action-reviewed-concept-loop")[
                "validation"
            ]["valid"]
        )

    def test_no_repo_data_created(self) -> None:
        self.assertFalse(Path("ashl_core_v1/data").exists())

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
