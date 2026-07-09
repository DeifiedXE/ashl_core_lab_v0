from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

from ashl_core_v1.host_body import host_body_reviewed_concept_replay as replay
from ashl_core_v1.host_body import host_body_working_readback_integration as working
from ashl_core_v1.runtime.guided_cradle_growth_teacher_console import (
    validate_host_body_working_readback_from_guided_cradle_growth_console,
)


WORKING_CLI = "ashl_core_v1.host_body.host_body_working_readback_integration_cli"
GUIDED_CLI = "ashl_core_v1.runtime.guided_cradle_growth_teacher_console_cli"


class HostBodyWorkingReadbackIntegrationTests(unittest.TestCase):
    def test_integration_plan_builds_and_blocks_forbidden_authority(self) -> None:
        replay_payload = replay.build_demo_uncertainty_feedback_reviewed_concept_replay()
        plan = self._plan()
        self.assertEqual(plan.plan_status, "working_readback_integration_plan_created")
        self.assertTrue(plan.existing_memory_path_required)
        self.assertTrue(plan.existing_working_readback_path_required)
        self.assertTrue(plan.trace_spine_boundary_required)
        self.assertTrue(plan.raw_evidence_boundary_required)
        self.assertFalse(plan.raw_trace_storage_allowed_in_memory_learning_trace)
        self.assertFalse(plan.raw_trace_summarization_allowed)
        self.assertFalse(plan.concept_id_embedding_into_raw_history_allowed)
        self.assertFalse(plan.long_term_memory_write_allowed)
        self.assertFalse(plan.internal_action_choice_influence_allowed)
        self.assertFalse(plan.task_action_selection_allowed)
        self.assertFalse(plan.first_output_allowed)
        self.assertFalse(plan.live_runtime_session_allowed)
        self.assertTrue(working.validate_host_body_working_readback_integration_plan(plan)["valid"])

        blocked = {
            "missing_trace": (
                {"reviewed_concept_replay_trace": None},
                "blocked_missing_reviewed_concept_replay_trace",
            ),
            "memory_path": (
                {"existing_memory_path_required": False},
                "blocked_forbidden_authority_detected",
            ),
            "readback_path": (
                {"existing_working_readback_path_required": False},
                "blocked_forbidden_authority_detected",
            ),
            "trace_boundary": (
                {"trace_spine_boundary_required": False},
                "blocked_forbidden_authority_detected",
            ),
            "raw_storage": (
                {"raw_trace_storage_allowed_in_memory_learning_trace": True},
                "blocked_raw_trace_storage_allowed",
            ),
            "raw_summary": (
                {"raw_trace_summarization_allowed": True},
                "blocked_raw_trace_summarization_allowed",
            ),
            "concept_id": (
                {"concept_id_embedding_into_raw_history_allowed": True},
                "blocked_concept_id_embedding_allowed",
            ),
            "long_memory": (
                {"long_term_memory_write_allowed": True},
                "blocked_long_term_memory_write_allowed",
            ),
            "internal_action": (
                {"internal_action_choice_influence_allowed": True},
                "blocked_internal_action_choice_influence_allowed",
            ),
            "task": (
                {"task_action_selection_allowed": True},
                "blocked_task_action_selection_allowed",
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
                    "reviewed_concept_replay_audit": replay_payload[
                        "host_body_reviewed_concept_replay_audit"
                    ],
                    "reviewed_concept_replay_trace": replay_payload[
                        "host_body_reviewed_concept_replay_trace"
                    ],
                    **kwargs,
                }
                self.assertEqual(
                    working.build_host_body_working_readback_integration_plan(**args).plan_status,
                    expected_status,
                )

    def test_memory_learning_trace_bridge_preserves_interpretation_and_blocks_raw_trace(self) -> None:
        bridge = self._learning_bridge()
        self.assertEqual(bridge.bridge_status, "memory_learning_trace_bridge_created")
        self.assertTrue(bridge.memory_layer_stores_interpretation_only)
        self.assertTrue(bridge.source_trace_refs_preserved)
        self.assertTrue(bridge.host_body_scope_preserved)
        self.assertTrue(bridge.counterexample_scope_preserved)
        self.assertFalse(bridge.raw_trace_dumped_into_memory_learning_trace)
        self.assertFalse(bridge.raw_trace_summarized_during_service_period)
        self.assertFalse(bridge.concept_id_embedded_into_raw_history)
        self.assertTrue(working.validate_host_body_memory_learning_trace_bridge(bridge)["valid"])

        blocked = {
            "raw": (
                {"raw_trace_dumped_into_memory_learning_trace": True},
                "blocked_raw_trace_dump_detected",
            ),
            "summary": (
                {"raw_trace_summarized_during_service_period": True},
                "blocked_raw_trace_summarization_detected",
            ),
            "concept": (
                {"concept_id_embedded_into_raw_history": True},
                "blocked_concept_id_embedded_into_raw_history",
            ),
            "refs": (
                {"source_trace_refs_preserved": False},
                "blocked_missing_source_trace_refs",
            ),
            "long": (
                {"long_term_memory_write_performed": True},
                "blocked_long_term_memory_write_detected",
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
        plan = self._plan()
        readiness = self._readiness_replay()
        for case, (kwargs, expected_status) in blocked.items():
            with self.subTest(case=case):
                blocked_bridge = working.build_host_body_memory_learning_trace_bridge(
                    working_readback_integration_plan=plan,
                    reviewed_concept_readiness_replay=readiness,
                    **kwargs,
                )
                self.assertEqual(blocked_bridge.bridge_status, expected_status)

    def test_routing_application_and_visibility_records_block_influence(self) -> None:
        routing = working.build_host_body_memory_routing_trace_bridge(
            memory_learning_trace_bridge=self._learning_bridge()
        )
        self.assertEqual(routing.bridge_status, "memory_routing_trace_bridge_created")
        self.assertTrue(routing.host_body_readback_route_enabled)
        self.assertFalse(routing.task_readback_route_enabled)
        self.assertTrue(routing.routing_uses_interpretation_not_raw_trace)
        self.assertFalse(routing.raw_trace_copied_into_routing_trace)
        self.assertTrue(working.validate_host_body_memory_routing_trace_bridge(routing)["valid"])

        app = working.build_host_body_memory_application_data_bridge(
            memory_routing_trace_bridge=routing
        )
        self.assertEqual(app.bridge_status, "memory_application_data_bridge_created")
        self.assertTrue(app.working_readback_visible)
        self.assertTrue(app.application_data_stores_interpretation_only)
        self.assertFalse(app.raw_trace_copied_into_application_data)
        self.assertFalse(app.internal_action_choice_influence_created)
        self.assertFalse(app.task_action_selection_influence_created)
        self.assertTrue(working.validate_host_body_memory_application_data_bridge(app)["valid"])

        visibility = working.build_host_body_working_readback_visibility(
            memory_application_data_bridge=app
        )
        self.assertEqual(
            visibility.visibility_status,
            "working_readback_visibility_created_for_future_host_body_context",
        )
        self.assertTrue(visibility.readback_payload_contains_interpretation)
        self.assertTrue(visibility.readback_payload_contains_source_refs)
        self.assertFalse(visibility.readback_payload_contains_raw_trace)
        self.assertFalse(visibility.internal_action_choice_influence_created)
        self.assertFalse(visibility.task_action_selection_influence_created)
        self.assertFalse(visibility.candidate_ordering_changed)
        self.assertFalse(visibility.selected_action_created)
        self.assertTrue(working.validate_host_body_working_readback_visibility(visibility)["valid"])

        routing_block_flags = {
            "raw_trace_copied_into_routing_trace": "blocked_raw_trace_copied_into_routing_trace",
            "concept_id_embedded_into_raw_history": "blocked_concept_id_embedded_into_raw_history",
            "internal_action_choice_influence_created": "blocked_internal_action_choice_influence_detected",
            "task_action_selection_created": "blocked_task_action_selection_detected",
            "long_term_memory_write_performed": "blocked_long_term_memory_write_detected",
            "first_output_created": "blocked_first_output_detected",
            "live_runtime_session_created": "blocked_live_runtime_detected",
        }
        for flag, expected in routing_block_flags.items():
            with self.subTest(routing_flag=flag):
                self.assertEqual(
                    working.build_host_body_memory_routing_trace_bridge(
                        memory_learning_trace_bridge=self._learning_bridge(),
                        **{flag: True},
                    ).bridge_status,
                    expected,
                )

        app_block_flags = {
            "raw_trace_copied_into_application_data": "blocked_raw_trace_copied_into_application_data",
            "concept_id_embedded_into_raw_history": "blocked_concept_id_embedded_into_raw_history",
            "internal_action_choice_influence_created": "blocked_internal_action_choice_influence_detected",
            "task_action_selection_influence_created": "blocked_task_action_selection_influence_detected",
            "working_readback_mutated_running_task": "blocked_running_task_mutation_detected",
            "long_term_memory_write_performed": "blocked_long_term_memory_write_detected",
            "first_output_created": "blocked_first_output_detected",
            "live_runtime_session_created": "blocked_live_runtime_detected",
        }
        for flag, expected in app_block_flags.items():
            with self.subTest(app_flag=flag):
                self.assertEqual(
                    working.build_host_body_memory_application_data_bridge(
                        memory_routing_trace_bridge=routing,
                        **{flag: True},
                    ).bridge_status,
                    expected,
                )

        visibility_block_flags = {
            "readback_payload_contains_raw_trace": "blocked_raw_trace_in_readback_payload",
            "readback_payload_contains_source_refs": "blocked_missing_source_trace_refs",
            "concept_id_embedded_into_raw_history": "blocked_concept_id_embedded_into_raw_history",
            "internal_action_choice_influence_created": "blocked_internal_action_choice_influence_detected",
            "task_action_selection_influence_created": "blocked_task_action_selection_influence_detected",
            "candidate_ordering_changed": "blocked_candidate_ordering_changed",
            "selected_action_created": "blocked_selected_action_created",
            "first_output_created": "blocked_first_output_detected",
            "live_runtime_session_created": "blocked_live_runtime_detected",
        }
        for flag, expected in visibility_block_flags.items():
            with self.subTest(visibility_flag=flag):
                value = False if flag == "readback_payload_contains_source_refs" else True
                self.assertEqual(
                    working.build_host_body_working_readback_visibility(
                        memory_application_data_bridge=app,
                        **{flag: value},
                    ).visibility_status,
                    expected,
                )

    def test_trace_spine_boundary_confirms_docs_only_gcmc_and_blocks_pollution(self) -> None:
        boundary = working.build_trace_spine_raw_evidence_boundary(
            working_readback_integration_plan=self._plan()
        )
        self.assertEqual(boundary.boundary_status, "passed_trace_spine_raw_evidence_boundary")
        self.assertTrue(boundary.gcmc_document_added_as_future_age_architecture)
        self.assertFalse(boundary.gcmc_runtime_implemented)
        self.assertFalse(boundary.cl_token_created)
        self.assertFalse(boundary.concept_compiler_created)
        self.assertFalse(boundary.pattern_miner_created)
        self.assertFalse(boundary.formed_under_assumption_required_now)
        self.assertTrue(boundary.trace_spine_format_unified)
        self.assertTrue(boundary.trace_spine_time_aligned)
        self.assertTrue(boundary.raw_trace_append_only_confirmed)
        self.assertFalse(boundary.raw_trace_summarized_during_service_period)
        self.assertTrue(boundary.memory_layer_stores_interpretation_only)
        self.assertTrue(boundary.source_trace_refs_preserved)
        self.assertFalse(boundary.concept_id_embedded_into_raw_history)
        self.assertFalse(boundary.raw_trace_dumped_into_memory_learning_trace)
        self.assertTrue(boundary.future_cl_ore_preserved)
        self.assertTrue(working.validate_trace_spine_raw_evidence_boundary(boundary)["valid"])

        blocked = {
            "gcmc_runtime_implemented": "blocked_gcmc_runtime_implemented",
            "cl_token_created": "blocked_cl_token_created",
            "trace_spine_format_unified": "blocked_trace_spine_format_not_unified",
            "trace_spine_time_aligned": "blocked_trace_spine_time_not_aligned",
            "raw_trace_append_only_confirmed": "blocked_raw_trace_not_append_only",
            "raw_trace_summarized_during_service_period": "blocked_raw_trace_summarized",
            "memory_layer_stores_interpretation_only": "blocked_memory_layer_not_interpretation_only",
            "source_trace_refs_preserved": "blocked_missing_source_trace_refs",
            "concept_id_embedded_into_raw_history": "blocked_concept_id_embedded_into_raw_history",
            "raw_trace_dumped_into_memory_learning_trace": "blocked_raw_trace_dumped_into_memory_learning_trace",
            "future_cl_ore_preserved": "blocked_future_cl_ore_polluted",
        }
        for flag, expected in blocked.items():
            with self.subTest(flag=flag):
                value = False if flag in {
                    "trace_spine_format_unified",
                    "trace_spine_time_aligned",
                    "raw_trace_append_only_confirmed",
                    "memory_layer_stores_interpretation_only",
                    "source_trace_refs_preserved",
                    "future_cl_ore_preserved",
                } else True
                self.assertEqual(
                    working.build_trace_spine_raw_evidence_boundary(
                        working_readback_integration_plan=self._plan(),
                        **{flag: value},
                    ).boundary_status,
                    expected,
                )

    def test_integration_trace_records_counts_and_blocks_invalid_records(self) -> None:
        payload = working.build_demo_mixed_reviewed_concept_working_readback()
        trace = payload["host_body_working_readback_integration_trace"]
        self.assertEqual(trace["trace_status"], "host_body_working_readback_integration_trace_recorded")
        self.assertEqual(trace["trace_kind"], "mixed_host_body_reviewed_concept_working_readback")
        self.assertEqual(trace["memory_learning_trace_bridge_count"], 3)
        self.assertEqual(trace["memory_routing_trace_bridge_count"], 3)
        self.assertEqual(trace["memory_application_data_bridge_count"], 3)
        self.assertEqual(trace["working_readback_visibility_count"], 3)
        self.assertEqual(trace["working_readback_visible_count"], 3)
        self.assertTrue(trace["trace_spine_boundary_confirmed"])
        self.assertTrue(trace["raw_evidence_boundary_confirmed"])
        self.assertTrue(trace["memory_layer_interpretation_only_confirmed"])
        self.assertTrue(trace["source_trace_refs_preserved_confirmed"])
        self.assertTrue(trace["concept_id_not_embedded_into_raw_history_confirmed"])
        self.assertTrue(working.validate_host_body_working_readback_integration_trace(trace)["valid"])

        plan = working.HostBodyWorkingReadbackIntegrationPlanRecord.from_dict(
            payload["host_body_working_readback_integration_plan"]
        )
        empty = working.build_host_body_working_readback_integration_trace(
            working_readback_integration_plan=plan
        )
        self.assertEqual(
            empty.trace_status,
            "host_body_working_readback_integration_trace_recorded_empty",
        )

        blocked = {
            "internal_action_choice_influence_created": "blocked_internal_action_choice_influence_detected",
            "task_action_selection_influence_created": "blocked_task_action_selection_influence_detected",
            "candidate_ordering_changed": "blocked_candidate_ordering_changed",
            "long_term_memory_write_performed": "blocked_long_term_memory_write_detected",
            "first_output_created": "blocked_first_output_detected",
            "live_runtime_session_created": "blocked_live_runtime_detected",
        }
        for flag, expected in blocked.items():
            with self.subTest(flag=flag):
                self.assertEqual(
                    working.build_host_body_working_readback_integration_trace(
                        working_readback_integration_plan=plan,
                        **{flag: True},
                    ).trace_status,
                    expected,
                )

        bad_boundary = working.build_trace_spine_raw_evidence_boundary(
            working_readback_integration_plan=plan,
            raw_trace_summarized_during_service_period=True,
        )
        self.assertEqual(
            working.build_host_body_working_readback_integration_trace(
                working_readback_integration_plan=plan,
                trace_spine_boundary_records=(bad_boundary,),
            ).trace_status,
            "blocked_trace_spine_boundary_failure",
        )

    def test_audit_and_readiness_pass_and_block_required_boundaries(self) -> None:
        expected_passes = {
            "working": (
                working.build_demo_uncertainty_reviewed_concept_working_readback(),
                "passed_host_body_reviewed_concept_working_readback_integration",
            ),
            "trace_spine": (
                working.build_demo_trace_spine_raw_evidence_boundary(),
                "passed_trace_spine_raw_evidence_boundary",
            ),
            "gcmc_docs": (
                working.build_demo_gcmc_docs_only_future_architecture(),
                "passed_gcmc_docs_only_future_architecture",
            ),
        }
        for case, (payload, expected) in expected_passes.items():
            with self.subTest(case=case):
                audit = payload["host_body_working_readback_integration_audit"]
                self.assertEqual(audit["audit_status"], expected)
                self.assertTrue(audit["host_body_reviewed_concept_replay_confirmed"])
                self.assertTrue(audit["existing_memory_path_reuse_confirmed"])
                self.assertTrue(audit["working_readback_visibility_confirmed"])
                self.assertTrue(audit["trace_spine_format_unified_confirmed"])
                self.assertTrue(audit["trace_spine_time_aligned_confirmed"])
                self.assertTrue(audit["raw_trace_append_only_confirmed"])
                self.assertTrue(audit["raw_trace_not_summarized_during_service_period"])
                self.assertTrue(audit["memory_layer_stores_interpretation_only_confirmed"])
                self.assertTrue(audit["source_trace_refs_preserved_confirmed"])
                self.assertTrue(audit["concept_id_not_embedded_into_raw_history_confirmed"])
                self.assertTrue(audit["raw_trace_not_dumped_into_memory_learning_trace_confirmed"])
                self.assertTrue(audit["gcmc_runtime_not_implemented_confirmed"])
                self.assertTrue(audit["cl_token_not_created_confirmed"])
                self.assertTrue(working.validate_host_body_working_readback_integration_audit(audit)["valid"])

        blocked = {
            "raw": (
                working.build_demo_blocked_raw_trace_dump(),
                "blocked_raw_trace_dumped_into_memory_learning_trace",
            ),
            "summary": (
                working.build_demo_blocked_raw_trace_summarization(),
                "blocked_raw_trace_summarized",
            ),
            "concept": (
                working.build_demo_blocked_concept_id_embedded_into_raw_history(),
                "blocked_concept_id_embedded_into_raw_history",
            ),
            "internal": (
                working.build_demo_blocked_internal_action_influence(),
                "blocked_internal_action_choice_influence_detected",
            ),
            "task": (
                working.build_demo_blocked_task_action_influence(),
                "blocked_task_action_selection_influence_detected",
            ),
            "gcmc": (
                working.build_demo_blocked_gcmc_runtime(),
                "blocked_gcmc_runtime_implemented",
            ),
            "cl": (
                working.build_demo_blocked_cl_token_creation(),
                "blocked_cl_token_created",
            ),
            "first": (
                working.build_demo_blocked_first_output(),
                "blocked_first_output_detected",
            ),
            "live": (
                working.build_demo_blocked_live_runtime(),
                "blocked_live_runtime_detected",
            ),
        }
        for case, (payload, expected) in blocked.items():
            with self.subTest(case=case):
                audit = payload["host_body_working_readback_integration_audit"]
                self.assertEqual(audit["audit_status"], expected)
                self.assertFalse(working.validate_host_body_working_readback_integration_audit(audit)["valid"])

        missing = working.build_host_body_working_readback_integration_audit(
            working_readback_integration_plan=None,
            working_readback_integration_trace=None,
            trace_spine_boundary=None,
        )
        self.assertEqual(missing.audit_status, "blocked_missing_working_readback_integration_plan")

        readiness = working.build_demo_uncertainty_reviewed_concept_working_readback()[
            "host_body_working_readback_integration_readiness"
        ]
        self.assertEqual(
            readiness["readiness_status"],
            "ready_for_host_body_readback_internal_action_influence_only",
        )
        self.assertTrue(readiness["ready_for_host_body_readback_internal_action_influence"])
        self.assertTrue(readiness["ready_for_host_body_closed_loop_milestone_audit"])
        self.assertTrue(readiness["ready_for_bounded_embodied_loop_runner"])
        self.assertFalse(readiness["ready_for_long_term_memory_write"])
        self.assertFalse(readiness["ready_for_core_memory_write"])
        self.assertFalse(readiness["ready_for_raw_trace_summarization"])
        self.assertFalse(readiness["ready_for_cl_token_creation"])
        self.assertFalse(readiness["ready_for_gcmc_runtime"])
        self.assertFalse(readiness["ready_for_task_action_selection_influence"])
        self.assertFalse(readiness["ready_for_external_control"])
        self.assertFalse(readiness["ready_for_first_output"])
        self.assertFalse(readiness["ready_for_live_runtime_session"])

    def test_cli_guided_console_docs_and_repo_data_boundary(self) -> None:
        cli_commands = [
            ("show-demo-uncertainty",),
            ("show-demo-interesting",),
            ("show-demo-runtime-bridge",),
            ("show-demo-mixed",),
            ("show-demo-trace-spine-boundary",),
            ("show-demo-gcmc-docs-only",),
            ("show-demo-readiness",),
            ("validate-demo-working-readback",),
            ("show-demo-blocked", "--case", "raw-trace-dump"),
            ("show-demo-blocked", "--case", "raw-trace-summarization"),
            ("show-demo-blocked", "--case", "concept-id-in-raw-history"),
            ("show-demo-blocked", "--case", "internal-action-influence"),
            ("show-demo-blocked", "--case", "task-action-influence"),
            ("show-demo-blocked", "--case", "gcmc-runtime"),
            ("show-demo-blocked", "--case", "cl-token"),
            ("show-demo-blocked", "--case", "first-output"),
            ("show-demo-blocked", "--case", "live-runtime"),
        ]
        for command in cli_commands:
            with self.subTest(command=command):
                result = subprocess.run(
                    ["py", "-3", "-m", WORKING_CLI, *command],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                self.assertTrue(json.loads(result.stdout))

        guided = validate_host_body_working_readback_from_guided_cradle_growth_console()
        self.assertEqual(guided["guided_console_action"], "host_body_validate_working_readback_demo")
        self.assertTrue(guided["validation"]["valid"])
        self.assertFalse(guided["internal_action_choice_influence_created"])
        self.assertFalse(guided["task_action_selection_influence_created"])
        self.assertFalse(guided["long_term_memory_write_performed"])
        self.assertFalse(guided["gcmc_runtime_implemented"])
        self.assertFalse(guided["cl_token_created"])
        self.assertFalse(guided["raw_trace_summarized_during_service_period"])
        self.assertFalse(guided["first_output_created"])
        self.assertFalse(guided["live_runtime_session_created"])

        guided_commands = [
            "host-body-show-working-readback-uncertainty-demo",
            "host-body-show-working-readback-interesting-demo",
            "host-body-show-working-readback-runtime-bridge-demo",
            "host-body-show-working-readback-mixed-demo",
            "host-body-show-trace-spine-boundary-demo",
            "host-body-show-gcmc-docs-only-demo",
            "host-body-show-working-readback-readiness",
            "host-body-validate-working-readback-demo",
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

        gcmc_doc = Path("ashl_core_v1/docs/future_age_grounded_concept_memory_compilation_gcmc_v0_3.md")
        trace_doc = Path("ashl_core_v1/docs/trace_spine_raw_evidence_boundary_v1.md")
        self.assertTrue(gcmc_doc.exists())
        self.assertTrue(trace_doc.exists())
        gcmc_text = gcmc_doc.read_text(encoding="utf-8")
        self.assertIn("Status: Future AGE Architecture", gcmc_text)
        self.assertIn("Type: Docs-Only", gcmc_text)
        self.assertIn("Runtime Impact: None", gcmc_text)
        self.assertIn("Qingyin v1 Runtime: Not Implemented", gcmc_text)
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _replay_payload(self) -> dict[str, object]:
        return replay.build_demo_uncertainty_feedback_reviewed_concept_replay()

    def _plan(self) -> working.HostBodyWorkingReadbackIntegrationPlanRecord:
        payload = self._replay_payload()
        return working.build_host_body_working_readback_integration_plan(
            reviewed_concept_replay_audit=payload["host_body_reviewed_concept_replay_audit"],
            reviewed_concept_replay_trace=payload["host_body_reviewed_concept_replay_trace"],
        )

    def _readiness_replay(self) -> dict[str, object]:
        return self._replay_payload()["host_body_reviewed_concept_readiness_replays"][0]

    def _learning_bridge(self) -> working.HostBodyReviewedConceptMemoryLearningTraceBridgeRecord:
        return working.build_host_body_memory_learning_trace_bridge(
            working_readback_integration_plan=self._plan(),
            reviewed_concept_readiness_replay=self._readiness_replay(),
        )


if __name__ == "__main__":
    unittest.main()
