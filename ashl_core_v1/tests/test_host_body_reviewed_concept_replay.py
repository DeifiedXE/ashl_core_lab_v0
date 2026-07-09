from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

from ashl_core_v1.host_body import host_body_existing_learning_pipeline_compatibility as existing
from ashl_core_v1.host_body import host_body_reviewed_concept_replay as replay
from ashl_core_v1.runtime.guided_cradle_growth_teacher_console import (
    validate_host_body_reviewed_concept_replay_from_guided_cradle_growth_console,
)


REPLAY_CLI = "ashl_core_v1.host_body.host_body_reviewed_concept_replay_cli"
GUIDED_CLI = "ashl_core_v1.runtime.guided_cradle_growth_teacher_console_cli"


class HostBodyReviewedConceptReplayTests(unittest.TestCase):
    def test_replay_plan_builds_and_blocks_forbidden_authority(self) -> None:
        source = existing.build_demo_uncertainty_existing_pipeline_compatibility()
        plan = replay.build_host_body_reviewed_concept_replay_plan(
            existing_learning_pipeline_compatibility_audit=source[
                "host_body_existing_learning_pipeline_compatibility_audit"
            ],
            existing_learning_pipeline_trace=source[
                "host_body_feedback_existing_learning_pipeline_trace"
            ],
        )
        self.assertEqual(plan.plan_status, "reviewed_concept_replay_plan_created")
        self.assertIn("Package 90", plan.existing_pipeline_packages)
        self.assertIn("Package 91", plan.existing_pipeline_packages)
        self.assertIn("Package 92", plan.existing_pipeline_packages)
        self.assertTrue(plan.reuse_existing_review_path_required)
        self.assertTrue(plan.reuse_existing_concept_path_required)
        self.assertTrue(plan.reuse_existing_refinement_path_required)
        self.assertTrue(plan.reuse_existing_reviewed_concept_path_required)
        self.assertFalse(plan.parallel_teacher_review_allowed)
        self.assertFalse(plan.parallel_concept_system_allowed)
        self.assertFalse(plan.memory_write_allowed)
        self.assertFalse(plan.working_readback_mutation_allowed)
        self.assertFalse(plan.action_selection_influence_allowed)
        self.assertFalse(plan.first_output_allowed)
        self.assertFalse(plan.live_runtime_session_allowed)
        self.assertTrue(replay.validate_host_body_reviewed_concept_replay_plan(plan)["valid"])

        blocked = {
            "missing_audit": (
                {"existing_learning_pipeline_compatibility_audit": None},
                "blocked_missing_existing_learning_pipeline_compatibility_audit",
            ),
            "missing_trace": (
                {"existing_learning_pipeline_trace": None},
                "blocked_missing_existing_learning_pipeline_trace",
            ),
            "missing_package_90_path": (
                {"reuse_existing_review_path_required": False},
                "blocked_forbidden_authority_detected",
            ),
            "missing_package_91_path": (
                {"reuse_existing_refinement_path_required": False},
                "blocked_forbidden_authority_detected",
            ),
            "missing_package_92_path": (
                {"reuse_existing_reviewed_concept_path_required": False},
                "blocked_forbidden_authority_detected",
            ),
            "parallel_teacher": (
                {"parallel_teacher_review_allowed": True},
                "blocked_parallel_teacher_review_allowed",
            ),
            "parallel_concept": (
                {"parallel_concept_system_allowed": True},
                "blocked_parallel_concept_system_allowed",
            ),
            "auto": (
                {"automatic_learning_approval_allowed": True},
                "blocked_automatic_learning_approval_allowed",
            ),
            "memory": (
                {"memory_write_allowed": True},
                "blocked_memory_write_allowed",
            ),
            "working": (
                {"working_readback_mutation_allowed": True},
                "blocked_working_readback_mutation_allowed",
            ),
            "action": (
                {"action_selection_influence_allowed": True},
                "blocked_action_selection_influence_allowed",
            ),
            "first": (
                {"first_output_allowed": True},
                "blocked_first_output_allowed",
            ),
            "live": (
                {"live_runtime_session_allowed": True},
                "blocked_live_runtime_allowed",
            ),
        }
        for case, (kwargs, expected_status) in blocked.items():
            with self.subTest(case=case):
                args = {
                    "existing_learning_pipeline_compatibility_audit": source[
                        "host_body_existing_learning_pipeline_compatibility_audit"
                    ],
                    "existing_learning_pipeline_trace": source[
                        "host_body_feedback_existing_learning_pipeline_trace"
                    ],
                    **kwargs,
                }
                self.assertEqual(
                    replay.build_host_body_reviewed_concept_replay_plan(**args).plan_status,
                    expected_status,
                )

    def test_approved_feedback_replay_input_accepts_allowed_kinds_and_blocks_unsafe_results(self) -> None:
        cases = {
            "uncertainty": (
                replay.build_demo_uncertainty_feedback_reviewed_concept_replay(),
                "host_body_uncertainty_feedback_candidate",
            ),
            "interesting": (
                replay.build_demo_interesting_event_feedback_reviewed_concept_replay(),
                "host_body_interesting_event_feedback_candidate",
            ),
            "runtime": (
                replay.build_demo_runtime_bridge_feedback_reviewed_concept_replay(),
                "host_body_runtime_bridge_feedback_candidate",
            ),
        }
        for case, (payload, candidate_kind) in cases.items():
            with self.subTest(case=case):
                item = payload["host_body_approved_feedback_replay_inputs"][0]
                self.assertEqual(item["input_candidate_kind"], candidate_kind)
                self.assertEqual(item["existing_review_result"], "approved")
                self.assertEqual(item["input_status"], "approved_host_body_feedback_replay_input_recorded")
                self.assertTrue(item["approved_for_replay"])
                self.assertTrue(item["teacher_review_required"])
                self.assertFalse(item["teacher_approval_created"])
                self.assertTrue(item["host_body_scope_preserved"])
                self.assertTrue(item["counterexample_scope_required"])
                self.assertTrue(item["safe_for_concept_candidate_draft_replay"])
                self.assertTrue(replay.validate_host_body_approved_feedback_replay_input(item)["valid"])

        plan, normalization, adapter, review_replay = self._input_sources()
        for result in ("rejected", "deferred", "needs_more_evidence", "conflict_detected"):
            with self.subTest(result=result):
                item = replay.build_host_body_approved_feedback_replay_input(
                    reviewed_concept_replay_plan=plan,
                    normalization=normalization,
                    existing_review_adapter=adapter,
                    existing_review_replay=review_replay,
                    existing_review_result=result,
                )
                self.assertEqual(item.input_status, "blocked_non_approved_review_result")
                self.assertFalse(replay.validate_host_body_approved_feedback_replay_input(item)["valid"])

        blocked_flags = {
            "teacher": "teacher_approval_created",
            "auto": "automatic_learning_approval_created",
            "concept": "concept_candidate_created_by_this_record",
            "reviewed": "reviewed_concept_created_by_this_record",
            "memory": "memory_write_performed",
            "action": "action_selection_influence_created",
            "first": "first_output_created",
            "live": "live_runtime_session_created",
        }
        for case, flag in blocked_flags.items():
            with self.subTest(case=case):
                item = replay.build_host_body_approved_feedback_replay_input(
                    reviewed_concept_replay_plan=plan,
                    normalization=normalization,
                    existing_review_adapter=adapter,
                    existing_review_replay=review_replay,
                    **{flag: True},
                )
                self.assertTrue(item.input_status.startswith("blocked_"))

    def test_draft_replay_uses_package_90_path_and_blocks_forbidden_outputs(self) -> None:
        demo_cases = {
            "uncertainty": (
                replay.build_demo_uncertainty_feedback_reviewed_concept_replay(),
                "host_body_uncertainty_concept_candidate_draft_replay",
            ),
            "interesting": (
                replay.build_demo_interesting_event_feedback_reviewed_concept_replay(),
                "host_body_interesting_event_concept_candidate_draft_replay",
            ),
            "runtime": (
                replay.build_demo_runtime_bridge_feedback_reviewed_concept_replay(),
                "host_body_runtime_bridge_concept_candidate_draft_replay",
            ),
        }
        for case, (payload, draft_kind) in demo_cases.items():
            with self.subTest(case=case):
                draft = payload["host_body_existing_concept_candidate_draft_replays"][0]
                self.assertEqual(draft["draft_replay_kind"], draft_kind)
                self.assertEqual(draft["draft_replay_status"], "existing_concept_candidate_draft_replay_ready")
                self.assertTrue(draft["uses_existing_package_90_draft_path"])
                self.assertFalse(draft["creates_parallel_concept_system"])
                self.assertTrue(draft["host_body_source_preserved"])
                self.assertTrue(draft["counterexample_scope_required"])
                self.assertTrue(draft["concept_candidate_draft_ready"])
                self.assertFalse(draft["concept_candidate_created_by_this_package"])
                self.assertTrue(replay.validate_host_body_existing_concept_candidate_draft_replay(draft)["valid"])

        approved_input = self._approved_input()
        blocked = {
            "parallel": (
                {"creates_parallel_concept_system": True},
                "blocked_parallel_concept_system_detected",
            ),
            "concept": (
                {"concept_candidate_created_by_this_package": True},
                "blocked_concept_candidate_created_by_this_package",
            ),
            "teacher": (
                {"teacher_approval_created": True},
                "blocked_teacher_approval_created",
            ),
            "auto": (
                {"automatic_learning_approval_created": True},
                "blocked_automatic_learning_approval_detected",
            ),
            "reviewed": (
                {"reviewed_concept_created": True},
                "blocked_reviewed_concept_created",
            ),
            "memory": (
                {"memory_write_performed": True},
                "blocked_memory_write_detected",
            ),
            "action": (
                {"action_selection_influence_created": True},
                "blocked_action_selection_influence_detected",
            ),
            "first": (
                {"first_output_created": True},
                "blocked_first_output_detected",
            ),
            "live": (
                {"live_runtime_session_created": True},
                "blocked_live_runtime_detected",
            ),
        }
        for case, (kwargs, expected_status) in blocked.items():
            with self.subTest(case=case):
                draft = replay.build_host_body_existing_concept_candidate_draft_replay(
                    approved_feedback_replay_input=approved_input,
                    **kwargs,
                )
                self.assertEqual(draft.draft_replay_status, expected_status)

    def test_refinement_and_reviewed_concept_readiness_replays_block_later_authority(self) -> None:
        draft = self._draft()
        refinement = replay.build_host_body_existing_concept_candidate_refinement_replay(
            concept_candidate_draft_replay=draft
        )
        self.assertEqual(
            refinement.refinement_replay_status,
            "existing_concept_candidate_refinement_replay_ready",
        )
        self.assertTrue(refinement.uses_existing_package_91_refinement_path)
        self.assertTrue(refinement.host_body_scope_preserved)
        self.assertTrue(refinement.counterexample_scope_checked)
        self.assertTrue(refinement.refined_concept_candidate_ready)
        self.assertFalse(refinement.refined_concept_candidate_created_by_this_package)
        self.assertTrue(replay.validate_host_body_existing_concept_candidate_refinement_replay(refinement)["valid"])

        refinement_blocks = {
            "parallel": "creates_parallel_refinement_system",
            "counterexample": "counterexample_scope_checked",
            "refined": "refined_concept_candidate_created_by_this_package",
            "teacher": "teacher_approval_created",
            "auto": "automatic_learning_approval_created",
            "reviewed": "reviewed_concept_created",
            "memory": "memory_write_performed",
            "action": "action_selection_influence_created",
            "first": "first_output_created",
            "live": "live_runtime_session_created",
        }
        for case, flag in refinement_blocks.items():
            with self.subTest(refinement_case=case):
                kwargs = {flag: False} if flag == "counterexample_scope_checked" else {flag: True}
                blocked = replay.build_host_body_existing_concept_candidate_refinement_replay(
                    concept_candidate_draft_replay=draft,
                    **kwargs,
                )
                self.assertTrue(blocked.refinement_replay_status.startswith("blocked_"))

        readiness = replay.build_host_body_reviewed_concept_readiness_replay(
            concept_candidate_refinement_replay=refinement
        )
        self.assertEqual(
            readiness.reviewed_concept_replay_status,
            "host_body_reviewed_concept_readiness_replay_ready",
        )
        self.assertTrue(readiness.uses_existing_package_92_reviewed_concept_path)
        self.assertTrue(readiness.reviewed_concept_ready)
        self.assertFalse(readiness.reviewed_concept_created_by_this_package)
        self.assertTrue(readiness.host_body_scope_preserved)
        self.assertTrue(readiness.teacher_review_result_preserved)
        self.assertTrue(readiness.counterexample_scope_preserved)
        self.assertTrue(readiness.safe_for_working_readback_integration_later)
        self.assertFalse(readiness.working_readback_created)
        self.assertFalse(readiness.memory_application_data_created)
        self.assertTrue(replay.validate_host_body_reviewed_concept_readiness_replay(readiness)["valid"])

        readiness_blocks = {
            "parallel": "creates_parallel_reviewed_concept_system",
            "reviewed": "reviewed_concept_created_by_this_package",
            "working": "working_readback_created",
            "memory_data": "memory_application_data_created",
            "memory": "memory_layer_write_performed",
            "auto": "automatic_learning_approval_created",
            "teacher": "teacher_approval_created",
            "action": "action_selection_influence_created",
            "external": "external_control_created",
            "first": "first_output_created",
            "live": "live_runtime_session_created",
        }
        for case, flag in readiness_blocks.items():
            with self.subTest(readiness_case=case):
                blocked = replay.build_host_body_reviewed_concept_readiness_replay(
                    concept_candidate_refinement_replay=refinement,
                    **{flag: True},
                )
                self.assertTrue(blocked.reviewed_concept_replay_status.startswith("blocked_"))

    def test_replay_trace_records_counts_and_blocks_forbidden_authority(self) -> None:
        mixed = replay.build_demo_mixed_feedback_reviewed_concept_replay()
        trace = mixed["host_body_reviewed_concept_replay_trace"]
        self.assertEqual(trace["trace_status"], "host_body_feedback_reviewed_concept_replay_trace_recorded")
        self.assertEqual(trace["trace_kind"], "mixed_host_body_feedback_reviewed_concept_replay")
        self.assertEqual(trace["approved_feedback_input_count"], 3)
        self.assertEqual(trace["draft_replay_count"], 3)
        self.assertEqual(trace["refinement_replay_count"], 3)
        self.assertEqual(trace["reviewed_concept_readiness_count"], 3)
        self.assertEqual(trace["reviewed_concept_ready_count"], 3)
        self.assertTrue(trace["uses_existing_pipeline_only"])
        self.assertFalse(trace["parallel_learning_pipeline_created"])
        self.assertTrue(replay.validate_host_body_reviewed_concept_replay_trace(trace)["valid"])

        plan = replay.HostBodyReviewedConceptReplayPlanRecord.from_dict(
            mixed["host_body_reviewed_concept_replay_plan"]
        )
        empty = replay.build_host_body_reviewed_concept_replay_trace(
            reviewed_concept_replay_plan=plan
        )
        self.assertEqual(
            empty.trace_status,
            "host_body_feedback_reviewed_concept_replay_trace_recorded_empty",
        )
        self.assertTrue(replay.validate_host_body_reviewed_concept_replay_trace(empty)["valid"])

        trace_blocks = {
            "parallel": "parallel_learning_pipeline_created",
            "reviewed": "reviewed_concept_created_by_this_package",
            "working": "working_readback_created",
            "memory_data": "memory_application_data_created",
            "memory": "memory_write_performed",
            "action": "action_selection_influence_created",
            "first": "first_output_created",
            "live": "live_runtime_session_created",
        }
        for case, flag in trace_blocks.items():
            with self.subTest(case=case):
                blocked = replay.build_host_body_reviewed_concept_replay_trace(
                    reviewed_concept_replay_plan=plan,
                    **{flag: True},
                )
                self.assertTrue(blocked.trace_status.startswith("blocked_"))

    def test_audit_passes_demo_cases_and_blocks_forbidden_boundaries(self) -> None:
        expected_passes = {
            "uncertainty": (
                replay.build_demo_uncertainty_feedback_reviewed_concept_replay(),
                "passed_host_body_uncertainty_reviewed_concept_replay",
            ),
            "interesting": (
                replay.build_demo_interesting_event_feedback_reviewed_concept_replay(),
                "passed_host_body_interesting_event_reviewed_concept_replay",
            ),
            "runtime": (
                replay.build_demo_runtime_bridge_feedback_reviewed_concept_replay(),
                "passed_host_body_runtime_bridge_reviewed_concept_replay",
            ),
            "mixed": (
                replay.build_demo_mixed_feedback_reviewed_concept_replay(),
                "passed_host_body_feedback_through_reviewed_concept_replay",
            ),
        }
        for case, (payload, expected_status) in expected_passes.items():
            with self.subTest(case=case):
                audit = payload["host_body_reviewed_concept_replay_audit"]
                self.assertEqual(audit["audit_status"], expected_status)
                self.assertTrue(audit["host_body_feedback_pipeline_compatibility_confirmed"])
                self.assertTrue(audit["existing_package_90_review_path_confirmed"])
                self.assertTrue(audit["existing_package_91_refinement_path_confirmed"])
                self.assertTrue(audit["existing_package_92_reviewed_concept_path_confirmed"])
                self.assertTrue(audit["reviewed_concept_readiness_confirmed"])
                self.assertTrue(audit["no_parallel_teacher_review"])
                self.assertTrue(audit["no_parallel_concept_system"])
                self.assertTrue(audit["no_reviewed_concept_created_by_this_package"])
                self.assertTrue(audit["no_working_readback_created"])
                self.assertTrue(audit["no_memory_application_data_created"])
                self.assertTrue(audit["no_memory_layer_write"])
                self.assertTrue(audit["no_automatic_learning_approval"])
                self.assertTrue(audit["no_teacher_approval_created"])
                self.assertTrue(audit["no_task_action_selection_influence"])
                self.assertTrue(audit["no_external_control"])
                self.assertTrue(audit["no_first_output"])
                self.assertTrue(audit["no_live_runtime_session"])
                self.assertTrue(replay.validate_host_body_reviewed_concept_replay_audit(audit)["valid"])

        blocked = {
            "non_approved": (
                replay.build_demo_blocked_non_approved_review_result(),
                "blocked_invalid_approved_feedback_input",
            ),
            "parallel": (
                replay.build_demo_blocked_parallel_concept_system_reviewed_concept_replay(),
                "blocked_parallel_concept_system_detected",
            ),
            "reviewed": (
                replay.build_demo_blocked_reviewed_concept_created_by_this_package(),
                "blocked_reviewed_concept_created_by_this_package",
            ),
            "working": (
                replay.build_demo_blocked_working_readback_created(),
                "blocked_working_readback_created",
            ),
            "memory": (
                replay.build_demo_blocked_memory_write_reviewed_concept_replay(),
                "blocked_memory_write_detected",
            ),
            "first": (
                replay.build_demo_blocked_first_output_reviewed_concept_replay(),
                "blocked_first_output_detected",
            ),
            "live": (
                replay.build_demo_blocked_live_runtime_reviewed_concept_replay(),
                "blocked_live_runtime_detected",
            ),
        }
        for case, (payload, expected_status) in blocked.items():
            with self.subTest(case=case):
                audit = payload["host_body_reviewed_concept_replay_audit"]
                self.assertEqual(audit["audit_status"], expected_status)
                self.assertFalse(replay.validate_host_body_reviewed_concept_replay_audit(audit)["valid"])

        payload = replay.build_demo_uncertainty_feedback_reviewed_concept_replay()
        missing = replay.build_host_body_reviewed_concept_replay_audit(
            reviewed_concept_replay_plan=None,
            reviewed_concept_replay_trace=payload["host_body_reviewed_concept_replay_trace"],
        )
        self.assertEqual(missing.audit_status, "blocked_missing_replay_plan")

    def test_readiness_cli_guided_console_and_repo_data_boundary(self) -> None:
        readiness = replay.build_demo_uncertainty_feedback_reviewed_concept_replay()[
            "host_body_reviewed_concept_replay_readiness"
        ]
        self.assertEqual(
            readiness["readiness_status"],
            "ready_for_host_body_reviewed_concept_working_readback_only",
        )
        self.assertTrue(readiness["ready_for_host_body_reviewed_concept_working_readback"])
        self.assertTrue(readiness["ready_for_host_body_readback_internal_action_influence"])
        self.assertTrue(readiness["ready_for_host_body_closed_loop_milestone_audit"])
        self.assertFalse(readiness["ready_for_memory_layer_write"])
        self.assertFalse(readiness["ready_for_memory_application_data_creation_by_this_package"])
        self.assertFalse(readiness["ready_for_working_readback_mutation_by_this_package"])
        self.assertFalse(readiness["ready_for_automatic_learning_approval"])
        self.assertFalse(readiness["ready_for_action_selection_influence"])
        self.assertFalse(readiness["ready_for_external_control"])
        self.assertFalse(readiness["ready_for_first_output"])
        self.assertFalse(readiness["ready_for_live_runtime_session"])
        self.assertTrue(replay.validate_host_body_reviewed_concept_replay_readiness(readiness)["valid"])

        cli_commands = [
            ("show-demo-uncertainty",),
            ("show-demo-interesting",),
            ("show-demo-runtime-bridge",),
            ("show-demo-mixed",),
            ("show-demo-readiness",),
            ("validate-demo-reviewed-concept-replay",),
            ("show-demo-blocked", "--case", "non-approved-review"),
            ("show-demo-blocked", "--case", "parallel-concept-system"),
            ("show-demo-blocked", "--case", "reviewed-concept-created"),
            ("show-demo-blocked", "--case", "working-readback-created"),
            ("show-demo-blocked", "--case", "memory-write"),
            ("show-demo-blocked", "--case", "first-output"),
            ("show-demo-blocked", "--case", "live-runtime"),
        ]
        for command in cli_commands:
            with self.subTest(command=command):
                result = subprocess.run(
                    ["py", "-3", "-m", REPLAY_CLI, *command],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                self.assertTrue(json.loads(result.stdout))

        guided = validate_host_body_reviewed_concept_replay_from_guided_cradle_growth_console()
        self.assertEqual(guided["guided_console_action"], "host_body_validate_reviewed_concept_replay_demo")
        self.assertTrue(guided["validation"]["valid"])
        self.assertFalse(guided["new_teacher_review_system_created"])
        self.assertFalse(guided["new_concept_system_created"])
        self.assertFalse(guided["reviewed_concept_created_by_this_package"])
        self.assertFalse(guided["working_readback_created"])
        self.assertFalse(guided["memory_application_data_created"])
        self.assertFalse(guided["memory_layer_write_performed"])
        self.assertFalse(guided["task_action_selection_influence_created"])
        self.assertFalse(guided["first_output_created"])
        self.assertFalse(guided["live_runtime_session_created"])

        guided_commands = [
            "host-body-show-reviewed-concept-replay-uncertainty-demo",
            "host-body-show-reviewed-concept-replay-interesting-demo",
            "host-body-show-reviewed-concept-replay-runtime-bridge-demo",
            "host-body-show-reviewed-concept-replay-mixed-demo",
            "host-body-show-reviewed-concept-replay-readiness",
            "host-body-validate-reviewed-concept-replay-demo",
        ]
        for command in guided_commands:
            with self.subTest(guided_command=command):
                result = subprocess.run(
                    ["py", "-3", "-m", GUIDED_CLI, command],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                self.assertTrue(json.loads(result.stdout))

        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _source(self) -> dict[str, object]:
        return existing.build_demo_uncertainty_existing_pipeline_compatibility()

    def _plan(self) -> replay.HostBodyReviewedConceptReplayPlanRecord:
        source = self._source()
        return replay.build_host_body_reviewed_concept_replay_plan(
            existing_learning_pipeline_compatibility_audit=source[
                "host_body_existing_learning_pipeline_compatibility_audit"
            ],
            existing_learning_pipeline_trace=source[
                "host_body_feedback_existing_learning_pipeline_trace"
            ],
        )

    def _input_sources(self) -> tuple[
        replay.HostBodyReviewedConceptReplayPlanRecord,
        dict[str, object],
        dict[str, object],
        dict[str, object],
    ]:
        source = self._source()
        return (
            self._plan(),
            source["host_body_feedback_candidate_normalizations"][0],
            source["host_body_feedback_existing_review_adapters"][0],
            source["host_body_feedback_existing_review_replays"][0],
        )

    def _approved_input(self) -> replay.HostBodyApprovedFeedbackReplayInputRecord:
        plan, normalization, adapter, review_replay = self._input_sources()
        return replay.build_host_body_approved_feedback_replay_input(
            reviewed_concept_replay_plan=plan,
            normalization=normalization,
            existing_review_adapter=adapter,
            existing_review_replay=review_replay,
        )

    def _draft(self) -> replay.HostBodyExistingConceptCandidateDraftReplayRecord:
        return replay.build_host_body_existing_concept_candidate_draft_replay(
            approved_feedback_replay_input=self._approved_input()
        )


if __name__ == "__main__":
    unittest.main()
