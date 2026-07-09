from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

from ashl_core_v1.host_body import host_body_existing_learning_pipeline_compatibility as compat
from ashl_core_v1.host_body import host_body_learning_feedback_bridge as bridge
from ashl_core_v1.runtime.guided_cradle_growth_teacher_console import (
    validate_host_body_existing_learning_pipeline_from_guided_cradle_growth_console,
)


COMPAT_CLI = "ashl_core_v1.host_body.host_body_existing_learning_pipeline_compatibility_cli"
GUIDED_CLI = "ashl_core_v1.runtime.guided_cradle_growth_teacher_console_cli"


class HostBodyExistingLearningPipelineCompatibilityTests(unittest.TestCase):
    def test_compatibility_plan_builds_and_blocks_parallel_authority(self) -> None:
        audit, candidate_set = self._plan_inputs()
        plan = compat.build_host_body_existing_learning_pipeline_compatibility_plan(
            host_body_learning_bridge_audit=audit,
            host_body_learning_candidate_set=candidate_set,
        )
        self.assertEqual(plan.plan_status, "compatibility_plan_created")
        self.assertIn("Package 90", plan.existing_pipeline_packages)
        self.assertIn("existing_learning_feedback_candidate_review", plan.existing_pipeline_stages)
        self.assertTrue(plan.reuse_existing_teacher_review_required)
        self.assertFalse(plan.new_teacher_review_system_allowed)
        self.assertFalse(plan.new_concept_system_allowed)
        self.assertFalse(plan.direct_reviewed_concept_allowed)
        self.assertFalse(plan.memory_write_allowed)
        self.assertFalse(plan.action_selection_influence_allowed)
        self.assertFalse(plan.first_output_allowed)
        self.assertFalse(plan.live_runtime_session_allowed)
        self.assertTrue(
            compat.validate_host_body_existing_learning_pipeline_compatibility_plan(plan)[
                "valid"
            ]
        )

        blocked = {
            "missing_audit": (
                {"host_body_learning_bridge_audit": None},
                "blocked_missing_host_body_learning_bridge_audit",
            ),
            "missing_set": (
                {"host_body_learning_candidate_set": None},
                "blocked_missing_candidate_set",
            ),
            "missing_package_90": (
                {"existing_pipeline_packages": ("Package 91", "Package 92")},
                "blocked_forbidden_authority_detected",
            ),
            "missing_stages": (
                {"existing_pipeline_stages": ("existing_learning_feedback_candidate_review",)},
                "blocked_forbidden_authority_detected",
            ),
            "new_teacher": (
                {"new_teacher_review_system_allowed": True},
                "blocked_new_teacher_review_system_allowed",
            ),
            "no_package_90_reuse": (
                {"reuse_existing_teacher_review_required": False},
                "blocked_new_teacher_review_system_allowed",
            ),
            "new_concept": (
                {"new_concept_system_allowed": True},
                "blocked_new_concept_system_allowed",
            ),
            "direct_reviewed": (
                {"direct_reviewed_concept_allowed": True},
                "blocked_direct_reviewed_concept_allowed",
            ),
            "memory": (
                {"memory_write_allowed": True},
                "blocked_memory_write_allowed",
            ),
            "auto": (
                {"automatic_learning_approval_allowed": True},
                "blocked_memory_write_allowed",
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
                    "host_body_learning_bridge_audit": audit,
                    "host_body_learning_candidate_set": candidate_set,
                    **kwargs,
                }
                self.assertEqual(
                    compat.build_host_body_existing_learning_pipeline_compatibility_plan(
                        **args
                    ).plan_status,
                    expected_status,
                )

    def test_normalization_handles_host_body_kinds_and_blocks_forbidden_outputs(self) -> None:
        cases = {
            "uncertainty": (
                bridge.build_demo_uncertainty_to_learning_feedback_candidate(),
                "host_body_uncertainty_feedback_candidate",
                "host_body_uncertainty_evidence",
            ),
            "interesting": (
                bridge.build_demo_interesting_event_to_learning_feedback_candidate(),
                "host_body_interesting_event_feedback_candidate",
                "host_body_interesting_event_evidence",
            ),
            "teacher": (
                bridge.build_demo_teacher_review_request_to_learning_feedback_candidate(),
                "host_body_teacher_review_feedback_candidate",
                "host_body_teacher_review_request_evidence",
            ),
            "runtime": (
                bridge.build_demo_deferred_runtime_bridge_to_learning_feedback_candidate(),
                "host_body_runtime_bridge_feedback_candidate",
                "host_body_runtime_bridge_evidence",
            ),
        }
        for case, (payload, candidate_kind, normalized_kind) in cases.items():
            with self.subTest(case=case):
                plan, evidence, mapping, feedback_bridge = self._normalization_inputs(payload)
                item = compat.build_host_body_feedback_candidate_normalization(
                    compatibility_plan=plan,
                    evidence_packet=evidence,
                    mapping=mapping,
                    bridge=feedback_bridge,
                )
                self.assertEqual(item.source_candidate_kind, candidate_kind)
                self.assertEqual(item.normalized_learning_feedback_kind, normalized_kind)
                self.assertEqual(
                    item.normalization_status,
                    "host_body_feedback_candidate_normalized_for_existing_review",
                )
                self.assertTrue(item.host_body_source_preserved)
                self.assertTrue(item.teacher_review_required_preserved)
                self.assertTrue(
                    compat.validate_host_body_feedback_candidate_normalization(item)[
                        "valid"
                    ]
                )

        plan, evidence, mapping, feedback_bridge = self._normalization_inputs()
        unknown = compat.build_host_body_feedback_candidate_normalization(
            compatibility_plan=plan,
            evidence_packet=evidence,
            mapping=mapping,
            bridge=feedback_bridge,
            source_candidate_kind="unknown",
        )
        self.assertEqual(unknown.normalization_status, "blocked_unknown_host_body_feedback_candidate_kind")

        blocked_flags = {
            "semantic": "semantic_vision_created",
            "speech": "speech_recognition_created",
            "new_teacher": "new_teacher_review_system_created",
            "concept": "concept_candidate_created",
            "reviewed": "reviewed_concept_created",
            "memory": "memory_write_performed",
            "action": "action_selection_influence_created",
            "first": "first_output_created",
            "live": "live_runtime_session_created",
        }
        for case, flag in blocked_flags.items():
            with self.subTest(case=case):
                item = compat.build_host_body_feedback_candidate_normalization(
                    compatibility_plan=plan,
                    evidence_packet=evidence,
                    mapping=mapping,
                    bridge=feedback_bridge,
                    **{flag: True},
                )
                self.assertTrue(item.normalization_status.startswith("blocked_"))
                self.assertFalse(
                    compat.validate_host_body_feedback_candidate_normalization(item)[
                        "valid"
                    ]
                )

    def test_existing_review_adapter_uses_package_90_path_and_blocks_parallel_outputs(self) -> None:
        status_cases = {
            "uncertainty": (
                bridge.build_demo_uncertainty_to_learning_feedback_candidate(),
                "existing_review_adapter_created_for_uncertainty",
            ),
            "interesting": (
                bridge.build_demo_interesting_event_to_learning_feedback_candidate(),
                "existing_review_adapter_created_for_interesting_event",
            ),
            "teacher": (
                bridge.build_demo_teacher_review_request_to_learning_feedback_candidate(),
                "existing_review_adapter_created_for_teacher_review_request",
            ),
            "runtime": (
                bridge.build_demo_deferred_runtime_bridge_to_learning_feedback_candidate(),
                "existing_review_adapter_created_for_runtime_bridge",
            ),
        }
        for case, (payload, expected_status) in status_cases.items():
            with self.subTest(case=case):
                normalization = self._normalization_for_payload(payload)
                adapter = compat.build_host_body_feedback_existing_review_adapter(
                    normalization=normalization
                )
                self.assertEqual(adapter.adapter_status, expected_status)
                self.assertTrue(adapter.uses_existing_package_90_review_path)
                self.assertFalse(adapter.creates_parallel_review_path)
                self.assertTrue(adapter.teacher_review_required)
                self.assertFalse(adapter.teacher_approval_created)
                self.assertFalse(adapter.concept_candidate_created)
                self.assertFalse(adapter.reviewed_concept_created)
                self.assertTrue(
                    compat.validate_host_body_feedback_existing_review_adapter(adapter)[
                        "valid"
                    ]
                )

        normalization = self._normalization_for_payload()
        blocked_flags = {
            "parallel": (
                {"creates_parallel_review_path": True},
                "blocked_parallel_review_path_detected",
            ),
            "teacher": (
                {"teacher_approval_created": True},
                "blocked_teacher_approval_created",
            ),
            "concept": (
                {"concept_candidate_created": True},
                "blocked_concept_candidate_created",
            ),
            "reviewed": (
                {"reviewed_concept_created": True},
                "blocked_reviewed_concept_created",
            ),
            "memory": (
                {"memory_write_performed": True},
                "blocked_memory_write_detected",
            ),
            "auto": (
                {"automatic_learning_approval_created": True},
                "blocked_memory_write_detected",
            ),
            "action": (
                {"action_selection_influence_created": True},
                "blocked_action_selection_influence_detected",
            ),
            "external": (
                {"external_control_created": True},
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
        for case, (kwargs, expected_status) in blocked_flags.items():
            with self.subTest(case=case):
                adapter = compat.build_host_body_feedback_existing_review_adapter(
                    normalization=normalization,
                    **kwargs,
                )
                self.assertEqual(adapter.adapter_status, expected_status)
                self.assertFalse(
                    compat.validate_host_body_feedback_existing_review_adapter(adapter)[
                        "valid"
                    ]
                )

    def test_review_replay_and_concept_candidate_compatibility_reuse_existing_result_types(self) -> None:
        adapter = compat.build_host_body_feedback_existing_review_adapter(
            normalization=self._normalization_for_payload()
        )
        result_cases = {
            "approved": (
                "approved",
                "existing_review_replay_recorded_approved",
                "host_body_feedback_compatible_with_existing_concept_candidate_path",
            ),
            "rejected": (
                "rejected",
                "existing_review_replay_recorded_rejected",
                "host_body_feedback_review_result_not_approved_no_concept_path",
            ),
            "deferred": (
                "deferred",
                "existing_review_replay_recorded_deferred",
                "host_body_feedback_review_result_not_approved_no_concept_path",
            ),
            "needs": (
                "needs_more_evidence",
                "existing_review_replay_recorded_needs_more_evidence",
                "host_body_feedback_review_result_not_approved_no_concept_path",
            ),
            "conflict": (
                "conflict_detected",
                "existing_review_replay_recorded_conflict_detected",
                "host_body_feedback_review_result_not_approved_no_concept_path",
            ),
        }
        for case, (result, replay_status, compat_status) in result_cases.items():
            with self.subTest(case=case):
                replay = compat.build_host_body_feedback_existing_review_replay(
                    existing_review_adapter=adapter,
                    simulated_existing_review_result=result,
                )
                self.assertEqual(replay.replay_status, replay_status)
                self.assertTrue(replay.uses_existing_review_result_types)
                self.assertFalse(replay.creates_new_review_result_types)
                self.assertTrue(
                    compat.validate_host_body_feedback_existing_review_replay(replay)[
                        "valid"
                    ]
                )
                concept_path = compat.build_host_body_feedback_concept_candidate_compatibility(
                    existing_review_replay=replay
                )
                self.assertEqual(concept_path.compatibility_status, compat_status)
                self.assertTrue(concept_path.host_body_scope_preserved)
                self.assertTrue(concept_path.counterexample_scope_required)
                self.assertTrue(concept_path.teacher_review_result_required)
                self.assertFalse(concept_path.concept_candidate_created_by_this_package)
                self.assertFalse(concept_path.reviewed_concept_created_by_this_package)

        bad_result = compat.build_host_body_feedback_existing_review_replay(
            existing_review_adapter=adapter,
            simulated_existing_review_result="new_result_type",
        )
        self.assertEqual(bad_result.replay_status, "blocked_new_review_result_type_detected")
        blocked_replay_flags = {
            "teacher": "teacher_approval_created",
            "concept": "concept_candidate_created",
            "reviewed": "reviewed_concept_created",
            "memory": "memory_write_performed",
            "first": "first_output_created",
            "live": "live_runtime_session_created",
        }
        for case, flag in blocked_replay_flags.items():
            with self.subTest(case=case):
                replay = compat.build_host_body_feedback_existing_review_replay(
                    existing_review_adapter=adapter,
                    **{flag: True},
                )
                self.assertTrue(replay.replay_status.startswith("blocked_"))

        replay = compat.build_host_body_feedback_existing_review_replay(
            existing_review_adapter=adapter
        )
        blocked_compat_flags = {
            "concept": "concept_candidate_created_by_this_package",
            "reviewed": "reviewed_concept_created_by_this_package",
            "memory": "memory_write_performed",
            "action": "action_selection_influence_created",
            "first": "first_output_created",
            "live": "live_runtime_session_created",
        }
        for case, flag in blocked_compat_flags.items():
            with self.subTest(case=case):
                concept_path = compat.build_host_body_feedback_concept_candidate_compatibility(
                    existing_review_replay=replay,
                    **{flag: True},
                )
                self.assertTrue(concept_path.compatibility_status.startswith("blocked_"))
                self.assertFalse(
                    compat.validate_host_body_feedback_concept_candidate_compatibility(
                        concept_path
                    )["valid"]
                )

    def test_pipeline_trace_counts_and_blocks_forbidden_authority(self) -> None:
        mixed = compat.build_demo_mixed_existing_pipeline_compatibility()
        trace = mixed["host_body_feedback_existing_learning_pipeline_trace"]
        self.assertEqual(trace["trace_status"], "host_body_feedback_existing_learning_pipeline_trace_recorded")
        self.assertEqual(trace["trace_kind"], "mixed_host_body_feedback_existing_pipeline_trace")
        self.assertEqual(trace["normalized_candidate_count"], 3)
        self.assertEqual(trace["existing_review_adapter_count"], 3)
        self.assertEqual(trace["existing_review_replay_count"], 3)
        self.assertEqual(trace["concept_candidate_compatibility_count"], 3)
        self.assertEqual(trace["approved_replay_count"], 3)
        self.assertTrue(trace["uses_existing_learning_pipeline_only"])
        self.assertFalse(trace["parallel_learning_pipeline_created"])
        self.assertTrue(
            compat.validate_host_body_feedback_existing_learning_pipeline_trace(trace)[
                "valid"
            ]
        )

        plan = compat.HostBodyExistingLearningPipelineCompatibilityPlanRecord.from_dict(
            mixed["host_body_existing_learning_pipeline_compatibility_plan"]
        )
        empty = compat.build_host_body_feedback_existing_learning_pipeline_trace(
            compatibility_plan=plan
        )
        self.assertEqual(
            empty.trace_status,
            "host_body_feedback_existing_learning_pipeline_trace_recorded_empty",
        )
        self.assertTrue(
            compat.validate_host_body_feedback_existing_learning_pipeline_trace(empty)[
                "valid"
            ]
        )
        blocked = {
            "parallel": "parallel_learning_pipeline_created",
            "concept": "concept_candidate_created_by_this_package",
            "reviewed": "reviewed_concept_created_by_this_package",
            "memory": "memory_write_performed",
            "action": "action_selection_influence_created",
            "first": "first_output_created",
            "live": "live_runtime_session_created",
        }
        for case, flag in blocked.items():
            with self.subTest(case=case):
                blocked_trace = compat.build_host_body_feedback_existing_learning_pipeline_trace(
                    compatibility_plan=plan,
                    **{flag: True},
                )
                self.assertTrue(blocked_trace.trace_status.startswith("blocked_"))

    def test_audit_passes_demo_cases_and_blocks_forbidden_boundaries(self) -> None:
        expected_passes = {
            "uncertainty": (
                compat.build_demo_uncertainty_existing_pipeline_compatibility(),
                "passed_host_body_feedback_existing_learning_pipeline_compatibility",
            ),
            "interesting": (
                compat.build_demo_interesting_existing_pipeline_compatibility(),
                "passed_host_body_feedback_existing_learning_pipeline_compatibility",
            ),
            "teacher": (
                compat.build_demo_teacher_review_existing_pipeline_compatibility(),
                "passed_host_body_feedback_existing_learning_pipeline_compatibility",
            ),
            "approved": (
                compat.build_demo_existing_review_approved_replay(),
                "passed_existing_concept_candidate_path_compatibility",
            ),
            "needs": (
                compat.build_demo_existing_review_needs_more_evidence_replay(),
                "passed_existing_learning_pipeline_replay",
            ),
        }
        for case, (payload, expected_status) in expected_passes.items():
            with self.subTest(case=case):
                audit = payload["host_body_existing_learning_pipeline_compatibility_audit"]
                self.assertEqual(audit["audit_status"], expected_status)
                self.assertTrue(audit["host_body_learning_bridge_confirmed"])
                self.assertTrue(audit["existing_learning_pipeline_reuse_confirmed"])
                self.assertTrue(audit["no_parallel_teacher_review_confirmed"])
                self.assertTrue(audit["no_parallel_concept_system_confirmed"])
                self.assertTrue(audit["no_concept_candidate_created_by_this_package"])
                self.assertTrue(audit["no_reviewed_concept_created_by_this_package"])
                self.assertTrue(audit["no_memory_layer_write"])
                self.assertTrue(audit["no_automatic_learning_approval"])
                self.assertTrue(audit["no_teacher_approval_created"])
                self.assertTrue(audit["no_task_action_selection_influence"])
                self.assertTrue(audit["no_external_control"])
                self.assertTrue(audit["no_first_output"])
                self.assertTrue(audit["no_live_runtime_session"])
                self.assertTrue(
                    compat.validate_host_body_existing_learning_pipeline_compatibility_audit(
                        audit
                    )["valid"]
                )

        blocked = {
            "parallel_teacher": (
                compat.build_demo_blocked_parallel_teacher_review(),
                "blocked_parallel_teacher_review_detected",
            ),
            "parallel_concept": (
                compat.build_demo_blocked_parallel_concept_system(),
                "blocked_parallel_concept_system_detected",
            ),
            "concept": (
                compat.build_demo_blocked_concept_candidate_created_by_adapter(),
                "blocked_concept_candidate_created_by_this_package",
            ),
            "reviewed": (
                compat.build_demo_blocked_reviewed_concept_created_by_adapter(),
                "blocked_reviewed_concept_created_by_this_package",
            ),
            "memory": (
                compat.build_demo_blocked_memory_write_existing_pipeline(),
                "blocked_memory_write_detected",
            ),
            "first": (
                compat.build_demo_blocked_first_output_existing_pipeline(),
                "blocked_first_output_detected",
            ),
            "live": (
                compat.build_demo_blocked_live_runtime_existing_pipeline(),
                "blocked_live_runtime_detected",
            ),
        }
        for case, (payload, expected_status) in blocked.items():
            with self.subTest(case=case):
                audit = payload["host_body_existing_learning_pipeline_compatibility_audit"]
                self.assertEqual(audit["audit_status"], expected_status)
                self.assertFalse(
                    compat.validate_host_body_existing_learning_pipeline_compatibility_audit(
                        audit
                    )["valid"]
                )

        payload = compat.build_demo_uncertainty_existing_pipeline_compatibility()
        audit = compat.build_host_body_existing_learning_pipeline_compatibility_audit(
            compatibility_plan=None,
            existing_learning_pipeline_trace=payload[
                "host_body_feedback_existing_learning_pipeline_trace"
            ],
        )
        self.assertEqual(audit.audit_status, "blocked_missing_compatibility_plan")

    def test_readiness_cli_guided_console_and_repo_data_boundary(self) -> None:
        readiness = compat.build_demo_uncertainty_existing_pipeline_compatibility()[
            "host_body_existing_learning_pipeline_readiness"
        ]
        self.assertEqual(
            readiness["readiness_status"],
            "ready_for_host_body_feedback_through_reviewed_concept_replay_only",
        )
        self.assertTrue(readiness["ready_for_host_body_feedback_through_reviewed_concept_replay"])
        self.assertTrue(readiness["ready_for_host_body_reviewed_concept_working_readback"])
        self.assertTrue(readiness["ready_for_host_body_readback_internal_action_influence"])
        self.assertTrue(readiness["ready_for_host_body_closed_loop_milestone_audit"])
        self.assertFalse(readiness["ready_for_parallel_teacher_review"])
        self.assertFalse(readiness["ready_for_concept_candidate_creation_by_adapter"])
        self.assertFalse(readiness["ready_for_reviewed_concept_without_existing_pipeline"])
        self.assertFalse(readiness["ready_for_memory_layer_write"])
        self.assertFalse(readiness["ready_for_action_selection_influence"])
        self.assertFalse(readiness["ready_for_external_control"])
        self.assertFalse(readiness["ready_for_first_output"])
        self.assertFalse(readiness["ready_for_live_runtime_session"])
        self.assertTrue(compat.validate_host_body_existing_learning_pipeline_readiness(readiness)["valid"])

        cli_commands = [
            ("show-demo-uncertainty",),
            ("show-demo-interesting",),
            ("show-demo-teacher-review",),
            ("show-demo-approved-replay",),
            ("show-demo-needs-more-evidence",),
            ("show-demo-mixed",),
            ("show-demo-readiness",),
            ("validate-demo-existing-pipeline",),
            ("show-demo-blocked", "--case", "parallel-teacher-review"),
            ("show-demo-blocked", "--case", "parallel-concept-system"),
            ("show-demo-blocked", "--case", "concept-candidate-created"),
            ("show-demo-blocked", "--case", "reviewed-concept-created"),
            ("show-demo-blocked", "--case", "memory-write"),
            ("show-demo-blocked", "--case", "first-output"),
            ("show-demo-blocked", "--case", "live-runtime"),
        ]
        for command in cli_commands:
            with self.subTest(command=command):
                result = subprocess.run(
                    ["py", "-3", "-m", COMPAT_CLI, *command],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                self.assertTrue(json.loads(result.stdout))

        guided = validate_host_body_existing_learning_pipeline_from_guided_cradle_growth_console()
        self.assertEqual(guided["guided_console_action"], "host_body_validate_existing_learning_pipeline_demo")
        self.assertTrue(guided["validation"]["valid"])
        self.assertFalse(guided["new_teacher_review_system_created"])
        self.assertFalse(guided["new_concept_system_created"])
        self.assertFalse(guided["concept_candidate_created_by_this_package"])
        self.assertFalse(guided["reviewed_concept_created_by_this_package"])
        self.assertFalse(guided["memory_layer_write_performed"])
        self.assertFalse(guided["task_action_selection_influence_created"])
        self.assertFalse(guided["first_output_created"])
        self.assertFalse(guided["live_runtime_session_created"])

        guided_commands = [
            "host-body-show-existing-learning-pipeline-uncertainty-demo",
            "host-body-show-existing-learning-pipeline-interesting-demo",
            "host-body-show-existing-learning-pipeline-teacher-review-demo",
            "host-body-show-existing-learning-pipeline-approved-replay-demo",
            "host-body-show-existing-learning-pipeline-mixed-demo",
            "host-body-show-existing-learning-pipeline-readiness",
            "host-body-validate-existing-learning-pipeline-demo",
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

    def _plan_inputs(self) -> tuple[dict[str, object], dict[str, object]]:
        payload = bridge.build_demo_uncertainty_to_learning_feedback_candidate()
        return (
            payload["host_body_learning_bridge_audit"],
            payload["host_body_learning_feedback_candidate_set"],
        )

    def _normalization_inputs(
        self,
        payload: dict[str, object] | None = None,
    ) -> tuple[compat.HostBodyExistingLearningPipelineCompatibilityPlanRecord, dict[str, object], dict[str, object], dict[str, object]]:
        payload = payload or bridge.build_demo_uncertainty_to_learning_feedback_candidate()
        plan = compat.build_host_body_existing_learning_pipeline_compatibility_plan(
            host_body_learning_bridge_audit=payload["host_body_learning_bridge_audit"],
            host_body_learning_candidate_set=payload["host_body_learning_feedback_candidate_set"],
        )
        return (
            plan,
            payload["host_body_learning_evidence_packets"][0],
            payload["host_body_learning_feedback_mappings"][0],
            payload["host_body_learning_feedback_bridges"][0],
        )

    def _normalization_for_payload(
        self,
        payload: dict[str, object] | None = None,
    ) -> compat.HostBodyFeedbackCandidateNormalizationRecord:
        plan, evidence, mapping, feedback_bridge = self._normalization_inputs(payload)
        return compat.build_host_body_feedback_candidate_normalization(
            compatibility_plan=plan,
            evidence_packet=evidence,
            mapping=mapping,
            bridge=feedback_bridge,
        )


if __name__ == "__main__":
    unittest.main()
