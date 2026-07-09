from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

from ashl_core_v1.host_body import host_body_embodied_learning_closed_loop_audit as closed
from ashl_core_v1.runtime.guided_cradle_growth_teacher_console import (
    validate_host_body_closed_loop_from_guided_cradle_growth_console,
)


CLOSED_LOOP_CLI = "ashl_core_v1.host_body.host_body_embodied_learning_closed_loop_audit_cli"
GUIDED_CLI = "ashl_core_v1.runtime.guided_cradle_growth_teacher_console_cli"


class HostBodyEmbodiedLearningClosedLoopAuditTests(unittest.TestCase):
    def test_scope_builds_with_packages_and_blocks_forbidden_authority(self) -> None:
        scope = closed.build_host_body_embodied_learning_closed_loop_scope()
        self.assertEqual(scope.scope_status, "closed_loop_scope_created")
        self.assertEqual(scope.schema_version, closed.SCOPE_SCHEMA_VERSION)
        self.assertIn("Package 107", scope.included_packages)
        self.assertIn("Package 112", scope.included_packages)
        self.assertIn("Package 113 report add-on", scope.included_packages)
        self.assertIn("56e9b22", scope.included_commits)
        self.assertTrue(scope.current_status_report_required)
        self.assertTrue(
            closed.validate_host_body_embodied_learning_closed_loop_scope(scope)["valid"]
        )

        blocked = (
            ({"host_body_v0_required": False}, "blocked_missing_required_loop_step"),
            ({"learning_feedback_bridge_required": False}, "blocked_missing_required_loop_step"),
            (
                {"existing_learning_pipeline_compatibility_required": False},
                "blocked_missing_required_loop_step",
            ),
            ({"reviewed_concept_replay_required": False}, "blocked_missing_required_loop_step"),
            (
                {"working_readback_integration_required": False},
                "blocked_missing_required_loop_step",
            ),
            (
                {"readback_internal_action_influence_required": False},
                "blocked_missing_required_loop_step",
            ),
            ({"trace_spine_boundary_required": False}, "blocked_missing_required_loop_step"),
            (
                {"current_status_report_available": False},
                "blocked_missing_current_status_report",
            ),
            ({"new_behavior_allowed": True}, "blocked_new_behavior_allowed"),
            ({"new_learning_allowed": True}, "blocked_new_learning_allowed"),
            ({"new_memory_write_allowed": True}, "blocked_new_memory_write_allowed"),
            ({"external_control_allowed": True}, "blocked_external_control_allowed"),
            ({"first_output_allowed": True}, "blocked_first_output_allowed"),
            ({"live_runtime_allowed": True}, "blocked_live_runtime_allowed"),
        )
        for kwargs, expected in blocked:
            with self.subTest(kwargs=kwargs):
                item = closed.build_host_body_embodied_learning_closed_loop_scope(**kwargs)
                self.assertEqual(item.scope_status, expected)
                self.assertFalse(
                    closed.validate_host_body_embodied_learning_closed_loop_scope(item)["valid"]
                )

    def test_capability_ledger_confirms_chain_and_blocks_missing_packages(self) -> None:
        scope = closed.build_host_body_embodied_learning_closed_loop_scope()
        ledger = closed.build_host_body_embodied_learning_closed_loop_capability_ledger(
            closed_loop_scope=scope
        )
        self.assertEqual(
            ledger.capability_ledger_status, "closed_loop_capability_ledger_recorded"
        )
        self.assertTrue(ledger.host_body_v0_verified)
        self.assertTrue(ledger.host_body_evidence_to_learning_feedback_verified)
        self.assertTrue(ledger.existing_learning_pipeline_compatibility_verified)
        self.assertTrue(ledger.reviewed_concept_replay_verified)
        self.assertTrue(ledger.working_readback_integration_verified)
        self.assertTrue(ledger.readback_internal_action_influence_verified)
        self.assertTrue(ledger.trace_spine_raw_evidence_boundary_verified)
        self.assertTrue(ledger.current_status_report_verified)
        self.assertFalse(ledger.new_capability_created_by_this_package)
        self.assertEqual(ledger.capability_count, 8)
        self.assertTrue(
            closed.validate_host_body_embodied_learning_closed_loop_capability_ledger(
                ledger
            )["valid"]
        )

        blocked = (
            ({"host_body_v0_verified": False}, "blocked_missing_host_body_v0"),
            (
                {"host_body_evidence_to_learning_feedback_verified": False},
                "blocked_missing_learning_feedback_bridge",
            ),
            (
                {"existing_learning_pipeline_compatibility_verified": False},
                "blocked_missing_existing_learning_pipeline_compatibility",
            ),
            (
                {"reviewed_concept_replay_verified": False},
                "blocked_missing_reviewed_concept_replay",
            ),
            (
                {"working_readback_integration_verified": False},
                "blocked_missing_working_readback_integration",
            ),
            (
                {"readback_internal_action_influence_verified": False},
                "blocked_missing_readback_internal_action_influence",
            ),
            (
                {"trace_spine_raw_evidence_boundary_verified": False},
                "blocked_missing_trace_spine_boundary",
            ),
            (
                {"current_status_report_verified": False},
                "blocked_missing_current_status_report",
            ),
            (
                {"new_capability_created_by_this_package": True},
                "blocked_unexpected_new_capability_detected",
            ),
        )
        for kwargs, expected in blocked:
            with self.subTest(kwargs=kwargs):
                item = closed.build_host_body_embodied_learning_closed_loop_capability_ledger(
                    closed_loop_scope=scope, **kwargs
                )
                self.assertEqual(item.capability_ledger_status, expected)
                self.assertFalse(
                    closed.validate_host_body_embodied_learning_closed_loop_capability_ledger(
                        item
                    )["valid"]
                )

    def test_boundary_ledger_confirms_all_boundaries_and_blocks_key_cases(self) -> None:
        scope = closed.build_host_body_embodied_learning_closed_loop_scope()
        boundary = closed.build_host_body_embodied_learning_closed_loop_boundary_ledger(
            closed_loop_scope=scope
        )
        self.assertEqual(boundary.boundary_ledger_status, "closed_loop_boundary_ledger_recorded")
        self.assertTrue(boundary.fixture_only_confirmed)
        self.assertTrue(boundary.teacher_gated_confirmed)
        self.assertTrue(boundary.audit_only_package_confirmed)

        true_fields = (
            "no_real_camera_access",
            "no_real_microphone_access",
            "no_semantic_vision",
            "no_speech_recognition",
            "no_task_engine_selected_action",
            "no_final_action",
            "no_direct_command",
            "no_sandbox_execution",
            "no_external_control",
            "no_os_control",
            "no_mouse_control",
            "no_keyboard_control",
            "no_browser_control",
            "no_file_operation",
            "no_network_execution",
            "no_shell_execution",
            "no_external_api_call",
            "no_unity_runtime_connection",
            "no_avatar_control",
            "no_long_term_memory_write",
            "no_core_memory_write",
            "no_raw_trace_summarization",
            "no_raw_trace_mutation",
            "no_raw_trace_dump_into_memory_learning_trace",
            "no_concept_id_embedded_into_raw_history",
            "source_trace_refs_preserved",
            "no_first_output",
            "no_live_runtime_session",
        )
        for field_name in true_fields:
            with self.subTest(field_name=field_name):
                self.assertTrue(getattr(boundary, field_name))
        self.assertTrue(
            closed.validate_host_body_embodied_learning_closed_loop_boundary_ledger(
                boundary
            )["valid"]
        )

        blocked = (
            ({"no_external_control": False}, "blocked_external_control_detected"),
            (
                {"no_memory_layer_write_by_this_package": False},
                "blocked_memory_write_detected",
            ),
            (
                {"no_raw_trace_summarization": False},
                "blocked_raw_trace_summarization_detected",
            ),
            (
                {"no_concept_id_embedded_into_raw_history": False},
                "blocked_concept_id_embedded_into_raw_history",
            ),
            ({"no_first_output": False}, "blocked_first_output_detected"),
            ({"no_live_runtime_session": False}, "blocked_live_runtime_detected"),
        )
        for kwargs, expected in blocked:
            with self.subTest(kwargs=kwargs):
                item = closed.build_host_body_embodied_learning_closed_loop_boundary_ledger(
                    closed_loop_scope=scope, **kwargs
                )
                self.assertEqual(item.boundary_ledger_status, expected)
                self.assertFalse(
                    closed.validate_host_body_embodied_learning_closed_loop_boundary_ledger(
                        item
                    )["valid"]
                )

    def test_integrated_trace_records_full_loop_and_blocks_missing_steps(self) -> None:
        scope = closed.build_host_body_embodied_learning_closed_loop_scope()
        trace = closed.build_host_body_embodied_learning_closed_loop_integrated_trace(
            closed_loop_scope=scope
        )
        self.assertEqual(trace.integrated_trace_status, "closed_loop_integrated_trace_recorded")
        self.assertEqual(trace.step_count, 7)
        names = [step["name"] for step in trace.integrated_loop_steps]
        self.assertEqual(
            names,
            [
                "host_body_event_and_internal_action",
                "host_body_evidence_to_learning_feedback_candidate",
                "existing_learning_pipeline_compatibility",
                "reviewed_concept_readiness_replay",
                "working_readback_visibility",
                "readback_influenced_internal_action_choice",
                "current_status_report_output",
            ],
        )
        self.assertTrue(trace.trace_spine_boundary_confirmed)
        self.assertTrue(trace.current_status_report_confirmed)
        self.assertFalse(trace.new_runtime_behavior_created)
        self.assertFalse(trace.new_memory_write_created)
        self.assertTrue(
            closed.validate_host_body_embodied_learning_closed_loop_integrated_trace(
                trace
            )["valid"]
        )

        blocked = (
            ({"host_body_event_step_confirmed": False}, "blocked_missing_host_body_v0_step"),
            (
                {"learning_feedback_candidate_step_confirmed": False},
                "blocked_missing_learning_feedback_step",
            ),
            (
                {"existing_learning_pipeline_step_confirmed": False},
                "blocked_missing_existing_pipeline_step",
            ),
            (
                {"reviewed_concept_readiness_step_confirmed": False},
                "blocked_missing_reviewed_concept_replay_step",
            ),
            (
                {"working_readback_step_confirmed": False},
                "blocked_missing_working_readback_step",
            ),
            (
                {"readback_influenced_internal_action_step_confirmed": False},
                "blocked_missing_readback_influence_step",
            ),
            (
                {"current_status_report_confirmed": False},
                "blocked_missing_current_status_report",
            ),
            (
                {"trace_spine_boundary_confirmed": False},
                "blocked_trace_spine_boundary_failure",
            ),
            (
                {"new_runtime_behavior_created": True},
                "blocked_forbidden_runtime_behavior_detected",
            ),
            (
                {"new_memory_write_created": True},
                "blocked_forbidden_memory_write_detected",
            ),
        )
        for kwargs, expected in blocked:
            with self.subTest(kwargs=kwargs):
                item = closed.build_host_body_embodied_learning_closed_loop_integrated_trace(
                    closed_loop_scope=scope, **kwargs
                )
                self.assertEqual(item.integrated_trace_status, expected)
                self.assertFalse(
                    closed.validate_host_body_embodied_learning_closed_loop_integrated_trace(
                        item
                    )["valid"]
                )

    def test_milestone_audit_passes_and_blocks_required_failures(self) -> None:
        payload = closed.build_demo_host_body_embodied_learning_closed_loop_pass()
        audit = payload["host_body_embodied_learning_closed_loop_milestone_audit"]
        self.assertEqual(audit["audit_status"], closed.PASSED_AUDIT_STATUS)
        self.assertTrue(audit["host_body_embodied_learning_closed_loop_established"])
        self.assertFalse(audit["new_capability_created_by_this_package"])
        self.assertTrue(audit["audit_only_package_confirmed"])
        self.assertTrue(audit["fixture_only_confirmed"])
        self.assertTrue(audit["teacher_gated_confirmed"])
        for field_name in (
            "package_107_verified",
            "package_108_verified",
            "package_109_verified",
            "package_110_verified",
            "package_111_verified",
            "package_112_verified",
            "current_status_report_verified",
            "trace_spine_format_unified_confirmed",
            "raw_trace_append_only_confirmed",
            "raw_trace_not_summarized_during_service_period",
            "memory_layer_stores_interpretation_only_confirmed",
            "source_trace_refs_preserved_confirmed",
            "concept_id_not_embedded_into_raw_history_confirmed",
            "raw_trace_not_dumped_into_memory_learning_trace_confirmed",
            "gcmc_docs_only_future_architecture_confirmed",
            "gcmc_runtime_not_implemented_confirmed",
            "cl_token_not_created_confirmed",
        ):
            with self.subTest(field_name=field_name):
                self.assertTrue(audit[field_name])
        self.assertTrue(
            closed.validate_host_body_embodied_learning_closed_loop_milestone_audit(
                audit
            )["valid"]
        )

        scope = payload["host_body_embodied_learning_closed_loop_scope"]
        ledger = payload["host_body_embodied_learning_closed_loop_capability_ledger"]
        boundary = payload["host_body_embodied_learning_closed_loop_boundary_ledger"]
        trace = payload["host_body_embodied_learning_closed_loop_integrated_trace"]
        missing_cases = (
            (
                {"closed_loop_scope": None, "capability_ledger": ledger, "boundary_ledger": boundary, "integrated_trace": trace},
                "blocked_missing_scope",
            ),
            (
                {"closed_loop_scope": scope, "capability_ledger": None, "boundary_ledger": boundary, "integrated_trace": trace},
                "blocked_missing_capability_ledger",
            ),
            (
                {"closed_loop_scope": scope, "capability_ledger": ledger, "boundary_ledger": None, "integrated_trace": trace},
                "blocked_missing_boundary_ledger",
            ),
            (
                {"closed_loop_scope": scope, "capability_ledger": ledger, "boundary_ledger": boundary, "integrated_trace": None},
                "blocked_missing_integrated_trace",
            ),
        )
        for kwargs, expected in missing_cases:
            with self.subTest(expected=expected):
                item = closed.build_host_body_embodied_learning_closed_loop_milestone_audit(
                    **kwargs
                )
                self.assertEqual(item.audit_status, expected)

        blocked_payloads = (
            (closed.build_demo_closed_loop_missing_host_body_v0(), "blocked_package_107_unverified"),
            (closed.build_demo_closed_loop_missing_learning_feedback(), "blocked_package_108_unverified"),
            (closed.build_demo_closed_loop_missing_existing_pipeline(), "blocked_package_109_unverified"),
            (closed.build_demo_closed_loop_missing_reviewed_concept_replay(), "blocked_package_110_unverified"),
            (closed.build_demo_closed_loop_missing_working_readback(), "blocked_package_111_unverified"),
            (closed.build_demo_closed_loop_missing_readback_influence(), "blocked_package_112_unverified"),
            (closed.build_demo_closed_loop_missing_current_status_report(), "blocked_current_status_report_missing"),
            (
                closed.build_demo_closed_loop_blocked_unexpected_new_capability(),
                "blocked_unexpected_new_capability_detected",
            ),
            (closed.build_demo_closed_loop_blocked_raw_trace_summarized(), "blocked_raw_trace_summarized"),
            (
                closed.build_demo_closed_loop_blocked_concept_id_in_raw_history(),
                "blocked_concept_id_embedded_into_raw_history",
            ),
            (
                self._blocked_audit(no_real_camera_access=False),
                "blocked_real_hardware_detected",
            ),
            (
                self._blocked_audit(no_semantic_vision=False),
                "blocked_semantic_interpretation_detected",
            ),
            (
                self._blocked_audit(no_speech_recognition=False),
                "blocked_speech_recognition_detected",
            ),
            (
                closed.build_demo_closed_loop_blocked_task_action_selection(),
                "blocked_task_action_selection_detected",
            ),
            (
                closed.build_demo_closed_loop_blocked_external_control(),
                "blocked_external_control_detected",
            ),
            (self._blocked_audit(no_unity_runtime_connection=False), "blocked_unity_runtime_detected"),
            (closed.build_demo_closed_loop_blocked_memory_write(), "blocked_memory_write_detected"),
            (
                self._blocked_audit(no_learning_candidate_creation_by_this_package=False),
                "blocked_learning_candidate_creation_detected",
            ),
            (
                self._blocked_audit(no_concept_candidate_creation_by_this_package=False),
                "blocked_concept_candidate_creation_detected",
            ),
            (
                self._blocked_audit(no_reviewed_concept_creation_by_this_package=False),
                "blocked_reviewed_concept_creation_detected",
            ),
            (
                self._blocked_audit(no_teacher_approval_created=False),
                "blocked_teacher_approval_created",
            ),
            (closed.build_demo_closed_loop_blocked_first_output(), "blocked_first_output_detected"),
            (closed.build_demo_closed_loop_blocked_live_runtime(), "blocked_live_runtime_detected"),
            (
                self._blocked_audit(no_production_behavior=False),
                "blocked_production_behavior_detected",
            ),
        )
        for blocked_payload, expected in blocked_payloads:
            with self.subTest(expected=expected):
                item = blocked_payload["host_body_embodied_learning_closed_loop_milestone_audit"]
                self.assertEqual(item["audit_status"], expected)
                self.assertFalse(
                    closed.validate_host_body_embodied_learning_closed_loop_milestone_audit(
                        item
                    )["valid"]
                )

    def test_readiness_recommends_next_fixture_only_packages(self) -> None:
        readiness = closed.build_demo_host_body_embodied_learning_closed_loop_pass()[
            "host_body_embodied_learning_closed_loop_readiness"
        ]
        self.assertEqual(
            readiness["readiness_status"],
            "ready_for_internal_action_home_surface_link_only",
        )
        for field_name in (
            "ready_for_internal_action_home_surface_link",
            "ready_for_runtime_state_summary_session_shell",
            "ready_for_bounded_embodied_loop_runner",
            "ready_for_no_codex_teacher_console_flow",
            "ready_for_session_end_review_promote_gate",
            "ready_for_no_codex_fixture_growth_loop_milestone_audit",
        ):
            with self.subTest(field_name=field_name):
                self.assertTrue(readiness[field_name])
        for field_name in (
            "ready_for_real_camera_connection",
            "ready_for_real_microphone_connection",
            "ready_for_task_engine_action_selection_influence",
            "ready_for_external_control",
            "ready_for_long_term_memory_write",
            "ready_for_core_memory_write",
            "ready_for_cl_token_creation",
            "ready_for_gcmc_runtime",
            "ready_for_first_output",
            "ready_for_live_runtime_session",
        ):
            with self.subTest(field_name=field_name):
                self.assertFalse(readiness[field_name])
        self.assertTrue(
            closed.validate_host_body_embodied_learning_closed_loop_readiness(
                readiness
            )["valid"]
        )

    def test_cli_guided_console_docs_status_report_and_repo_data_boundary(self) -> None:
        cli_commands = [
            ("show-demo-closed-loop-pass",),
            ("show-demo-scope",),
            ("show-demo-capability-ledger",),
            ("show-demo-boundary-ledger",),
            ("show-demo-integrated-trace",),
            ("show-demo-readiness",),
            ("validate-demo-closed-loop",),
            ("show-current-status-report",),
            ("show-demo-blocked", "--case", "missing-host-body-v0"),
            ("show-demo-blocked", "--case", "missing-learning-feedback"),
            ("show-demo-blocked", "--case", "missing-existing-pipeline"),
            ("show-demo-blocked", "--case", "missing-reviewed-concept-replay"),
            ("show-demo-blocked", "--case", "missing-working-readback"),
            ("show-demo-blocked", "--case", "missing-readback-influence"),
            ("show-demo-blocked", "--case", "missing-current-status-report"),
            ("show-demo-blocked", "--case", "raw-trace-summarized"),
            ("show-demo-blocked", "--case", "concept-id-in-raw-history"),
            ("show-demo-blocked", "--case", "task-action-selection"),
            ("show-demo-blocked", "--case", "external-control"),
            ("show-demo-blocked", "--case", "memory-write"),
            ("show-demo-blocked", "--case", "first-output"),
            ("show-demo-blocked", "--case", "live-runtime"),
        ]
        for command in cli_commands:
            with self.subTest(command=command):
                result = subprocess.run(
                    ["py", "-3", "-m", CLOSED_LOOP_CLI, *command],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                self.assertTrue(json.loads(result.stdout))

        guided = validate_host_body_closed_loop_from_guided_cradle_growth_console()
        self.assertEqual(guided["guided_console_action"], "host_body_validate_closed_loop_demo")
        self.assertTrue(guided["validation"]["valid"])
        self.assertFalse(guided["first_output_created"])
        self.assertFalse(guided["live_runtime_session_created"])

        guided_commands = [
            "host-body-show-closed-loop-pass-demo",
            "host-body-show-closed-loop-scope-demo",
            "host-body-show-closed-loop-capability-ledger-demo",
            "host-body-show-closed-loop-boundary-ledger-demo",
            "host-body-show-closed-loop-integrated-trace-demo",
            "host-body-show-closed-loop-readiness",
            "host-body-validate-closed-loop-demo",
            "host-body-show-current-status-after-113",
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

        self.assertTrue(
            Path("ashl_core_v1/docs/host_body_embodied_learning_closed_loop_milestone_audit_v0.md").exists()
        )
        self.assertTrue(Path(closed.CURRENT_STATUS_REPORT_PATH).exists())
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _blocked_audit(self, **boundary_kwargs: bool) -> dict[str, object]:
        scope = closed.build_host_body_embodied_learning_closed_loop_scope()
        ledger = closed.build_host_body_embodied_learning_closed_loop_capability_ledger(
            closed_loop_scope=scope
        )
        boundary = closed.build_host_body_embodied_learning_closed_loop_boundary_ledger(
            closed_loop_scope=scope, **boundary_kwargs
        )
        trace = closed.build_host_body_embodied_learning_closed_loop_integrated_trace(
            closed_loop_scope=scope
        )
        audit = closed.build_host_body_embodied_learning_closed_loop_milestone_audit(
            closed_loop_scope=scope,
            capability_ledger=ledger,
            boundary_ledger=boundary,
            integrated_trace=trace,
        )
        return {
            "host_body_embodied_learning_closed_loop_milestone_audit": audit.to_dict()
        }


if __name__ == "__main__":
    unittest.main()
