from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from ashl_core_v1.runtime import fixed_closed_loop_playback as playback
from ashl_core_v1.runtime.guided_cradle_growth_teacher_console import (
    validate_fixed_closed_loop_playback_from_guided_cradle_growth_console,
)


PLAYBACK_CLI = "ashl_core_v1.runtime.fixed_closed_loop_playback_cli"
GUIDED_CLI = "ashl_core_v1.runtime.guided_cradle_growth_teacher_console_cli"


class RuntimeFixedClosedLoopPlaybackTests(unittest.TestCase):
    def test_playback_plan_builds_and_blocks_boundaries(self) -> None:
        payload = playback.build_demo_full_fixed_closed_loop_playback()
        plan = playback.RuntimeFixedClosedLoopPlaybackPlanRecord.from_dict(
            payload["runtime_fixed_closed_loop_playback_plan"]
        )
        milestone = payload["source_package94_milestone"]["first_closed_loop_milestone"]
        integrated_trace = payload["runtime_integrated_event_loop_trace"]

        self.assertEqual(plan.playback_plan_status, "playback_plan_created")
        self.assertEqual(plan.playback_name, "package_94_closed_loop_fixed_playback")
        self.assertEqual(plan.fixed_stage_sequence, playback.REQUIRED_CLOSED_LOOP_STAGES)
        self.assertGreater(plan.bounded_tick_budget, 0)
        self.assertFalse(plan.dynamic_child_event_scheduling_allowed)
        self.assertFalse(plan.live_engine_invocation_allowed)
        self.assertTrue(
            playback.validate_runtime_fixed_closed_loop_playback_plan(plan)["valid"]
        )

        blocked_cases = {
            "missing_milestone": (
                {"closed_loop_milestone": None, "integrated_event_loop_trace": integrated_trace},
                "blocked_missing_closed_loop_milestone",
            ),
            "missing_integrated": (
                {"closed_loop_milestone": milestone, "integrated_event_loop_trace": None},
                "blocked_missing_integrated_event_loop_trace",
            ),
            "empty_sequence": (
                {
                    "closed_loop_milestone": milestone,
                    "integrated_event_loop_trace": integrated_trace,
                    "fixed_stage_sequence": (),
                },
                "blocked_unbounded_playback",
            ),
            "unbounded_tick": (
                {
                    "closed_loop_milestone": milestone,
                    "integrated_event_loop_trace": integrated_trace,
                    "bounded_tick_budget": 0,
                },
                "blocked_unbounded_playback",
            ),
            "dynamic": (
                {
                    "closed_loop_milestone": milestone,
                    "integrated_event_loop_trace": integrated_trace,
                    "dynamic_child_event_scheduling_allowed": True,
                },
                "blocked_forbidden_authority_detected",
            ),
            "live": (
                {
                    "closed_loop_milestone": milestone,
                    "integrated_event_loop_trace": integrated_trace,
                    "live_engine_invocation_allowed": True,
                },
                "blocked_forbidden_authority_detected",
            ),
            "memory": (
                {
                    "closed_loop_milestone": milestone,
                    "integrated_event_loop_trace": integrated_trace,
                    "memory_layer_write_allowed": True,
                },
                "blocked_forbidden_authority_detected",
            ),
            "learning": (
                {
                    "closed_loop_milestone": milestone,
                    "integrated_event_loop_trace": integrated_trace,
                    "automatic_learning_approval_allowed": True,
                },
                "blocked_forbidden_authority_detected",
            ),
        }
        for case, (kwargs, expected_status) in blocked_cases.items():
            with self.subTest(case=case):
                blocked = playback.build_runtime_fixed_closed_loop_playback_plan(**kwargs)
                self.assertEqual(blocked.playback_plan_status, expected_status)

    def test_stage_mapping_covers_required_stages_and_blocks_invalid(self) -> None:
        payload = playback.build_demo_full_fixed_closed_loop_playback()
        plan = payload["runtime_fixed_closed_loop_playback_plan"]
        mappings = [
            playback.RuntimeClosedLoopStageToEventFrameMappingRecord.from_dict(item)
            for item in payload["runtime_closed_loop_stage_event_mappings"]
        ]
        mapping_by_stage = {item.closed_loop_stage_name: item for item in mappings}

        for stage in playback.REQUIRED_CLOSED_LOOP_STAGES:
            with self.subTest(stage=stage):
                mapping = mapping_by_stage[stage]
                config = playback.STAGE_CONFIG[stage]
                self.assertEqual(mapping.mapping_status, "stage_mapped_to_event_frame")
                self.assertEqual(mapping.target_event_family, config["event_family"])
                self.assertEqual(mapping.target_engine_lane, config["target_engine"])
                self.assertTrue(mapping.stage_represented)
                self.assertTrue(mapping.dispatch_required)
                self.assertTrue(mapping.return_payload_required)
                self.assertFalse(mapping.live_engine_invocation_allowed)
                self.assertFalse(mapping.memory_layer_write_allowed)

        grouped = playback.build_demo_grouped_stage_fixed_closed_loop_playback()
        grouped_mappings = [
            playback.RuntimeClosedLoopStageToEventFrameMappingRecord.from_dict(item)
            for item in grouped["runtime_closed_loop_stage_event_mappings"]
        ]
        grouped_by_stage = {item.closed_loop_stage_name: item for item in grouped_mappings}
        for stage, members in playback.GROUPED_STAGE_MEMBERS.items():
            self.assertEqual(
                grouped_by_stage[stage].mapping_status,
                "stage_mapped_as_group_member",
            )
            self.assertEqual(grouped_by_stage[stage].stage_group_members, members)

        frame = payload["runtime_event_frames"][1]
        invalid_cases = {
            "unknown": (
                {
                    "closed_loop_stage_name": "not_a_closed_loop_stage",
                    "target_event_frame": frame,
                    "source_closed_loop_record_id": "source",
                    "source_closed_loop_record_kind": "fixture",
                },
                "blocked_unknown_closed_loop_stage",
            ),
            "missing_source": (
                {
                    "closed_loop_stage_name": "sense_observation",
                    "target_event_frame": frame,
                    "source_closed_loop_record_id": None,
                    "source_closed_loop_record_kind": "fixture",
                },
                "blocked_missing_source_record",
            ),
            "missing_frame": (
                {
                    "closed_loop_stage_name": "sense_observation",
                    "target_event_frame": None,
                    "source_closed_loop_record_id": "source",
                    "source_closed_loop_record_kind": "fixture",
                },
                "blocked_invalid_event_frame_mapping",
            ),
            "forbidden": (
                {
                    "closed_loop_stage_name": "sense_observation",
                    "target_event_frame": frame,
                    "source_closed_loop_record_id": "source",
                    "source_closed_loop_record_kind": "fixture",
                    "force_forbidden_authority": True,
                },
                "blocked_forbidden_authority_detected",
            ),
        }
        for case, (kwargs, expected_status) in invalid_cases.items():
            with self.subTest(case=case):
                record = playback.build_runtime_closed_loop_stage_to_event_frame_mapping(
                    playback_plan=plan,
                    closed_loop_stage_index=99,
                    **kwargs,
                )
                self.assertEqual(record.mapping_status, expected_status)

    def test_playback_step_records_lineage_and_blocks_new_behavior(self) -> None:
        payload = playback.build_demo_full_fixed_closed_loop_playback()
        plan = payload["runtime_fixed_closed_loop_playback_plan"]
        mapping = playback.RuntimeClosedLoopStageToEventFrameMappingRecord.from_dict(
            payload["runtime_closed_loop_stage_event_mappings"][0]
        )
        integrated_step = self._integrated_step_for_mapping(payload, mapping)
        link = self._link_for_mapping(payload, mapping)
        step = playback.RuntimeFixedClosedLoopPlaybackStepRecord.from_dict(
            payload["runtime_fixed_closed_loop_playback_steps"][0]
        )

        self.assertEqual(step.playback_step_status, "playback_step_recorded")
        self.assertEqual(step.event_frame_id, mapping.target_event_frame_id)
        self.assertIsNotNone(step.source_stage_event_mapping_id)
        self.assertIsNotNone(step.source_integrated_event_step_id)
        self.assertIsNotNone(step.source_dispatch_resume_link_id)
        self.assertEqual(step.return_status, "returned_success")
        self.assertIsNotNone(step.parent_resume_status)
        self.assertTrue(step.stage_evidence_referenced)
        self.assertTrue(step.stage_replayed_as_record)
        self.assertFalse(step.live_handler_invoked)
        self.assertFalse(step.new_engine_behavior_created)
        self.assertFalse(step.new_memory_write_performed)
        self.assertFalse(step.external_execution_created)

        missing_mapping = playback.build_runtime_fixed_closed_loop_playback_step(
            playback_plan=plan,
            stage_event_mapping=None,
        )
        self.assertEqual(
            missing_mapping.playback_step_status,
            "blocked_missing_stage_mapping",
        )
        missing_link = playback.build_runtime_fixed_closed_loop_playback_step(
            playback_plan=plan,
            stage_event_mapping=mapping,
            integrated_event_step=integrated_step,
            dispatch_resume_link=None,
        )
        self.assertEqual(
            missing_link.playback_step_status,
            "blocked_missing_dispatch_resume_link",
        )
        live = playback.build_runtime_fixed_closed_loop_playback_step(
            playback_plan=plan,
            stage_event_mapping=mapping,
            integrated_event_step=integrated_step,
            dispatch_resume_link=link,
            live_handler_invoked=True,
        )
        self.assertEqual(
            live.playback_step_status,
            "blocked_live_handler_invocation_detected",
        )
        new_engine = playback.build_runtime_fixed_closed_loop_playback_step(
            playback_plan=plan,
            stage_event_mapping=mapping,
            integrated_event_step=integrated_step,
            dispatch_resume_link=link,
            new_engine_behavior_created=True,
        )
        self.assertEqual(
            new_engine.playback_step_status,
            "blocked_new_engine_behavior_detected",
        )

        forbidden_flags = (
            "new_learning_feedback_candidate_created",
            "new_concept_candidate_created",
            "new_reviewed_concept_created",
            "new_memory_write_performed",
            "new_sandbox_execution_performed",
            "dynamic_child_event_created",
            "external_execution_created",
            "automatic_learning_approval_created",
            "recursive_learning_created",
            "thought_engine_behavior_created",
            "production_behavior_created",
        )
        for flag in forbidden_flags:
            with self.subTest(flag=flag):
                blocked = playback.build_runtime_fixed_closed_loop_playback_step(
                    playback_plan=plan,
                    stage_event_mapping=mapping,
                    integrated_event_step=integrated_step,
                    dispatch_resume_link=link,
                    **{flag: True},
                )
                self.assertEqual(
                    blocked.playback_step_status,
                    "blocked_forbidden_authority_detected",
                )

    def test_fixed_playback_trace_builds_and_blocks_lineage(self) -> None:
        full = playback.build_demo_full_fixed_closed_loop_playback()
        trace = playback.RuntimeFixedClosedLoopPlaybackTrace.from_dict(
            full["runtime_fixed_closed_loop_playback_trace"]
        )
        self.assertEqual(trace.fixed_playback_status, "fixed_closed_loop_playback_complete")
        self.assertEqual(trace.playback_stage_count, len(playback.REQUIRED_CLOSED_LOOP_STAGES))
        self.assertEqual(trace.represented_stage_count, len(playback.REQUIRED_CLOSED_LOOP_STAGES))
        self.assertTrue(trace.all_required_stages_represented)
        self.assertTrue(trace.all_steps_have_event_frames)
        self.assertTrue(trace.all_steps_have_dispatch_lineage)
        self.assertTrue(trace.all_steps_have_return_payloads)
        self.assertTrue(trace.all_child_returns_resumed)
        self.assertTrue(trace.root_frame_closed)
        self.assertFalse(trace.live_engine_invocation_created)
        self.assertFalse(trace.dynamic_child_event_created)

        grouped = playback.build_demo_grouped_stage_fixed_closed_loop_playback()
        self.assertEqual(
            grouped["runtime_fixed_closed_loop_playback_trace"]["fixed_playback_status"],
            "fixed_closed_loop_playback_complete_with_grouped_stages",
        )
        blocked_demos = {
            "missing_stage": (
                playback.build_demo_blocked_missing_stage_fixed_playback,
                "fixed_closed_loop_playback_blocked_missing_required_stage",
                "blocked_missing_required_stage",
            ),
            "missing_mapping": (
                playback.build_demo_blocked_missing_event_frame_mapping_fixed_playback,
                "fixed_closed_loop_playback_blocked_missing_event_frame",
                "blocked_missing_event_frame_mapping",
            ),
            "missing_dispatch": (
                playback.build_demo_blocked_missing_dispatch_lineage_fixed_playback,
                "fixed_closed_loop_playback_blocked_missing_dispatch_lineage",
                "blocked_missing_dispatch_lineage",
            ),
        }
        for case, (builder, trace_status, audit_status) in blocked_demos.items():
            with self.subTest(case=case):
                payload = builder()
                self.assertEqual(
                    payload["runtime_fixed_closed_loop_playback_trace"][
                        "fixed_playback_status"
                    ],
                    trace_status,
                )
                self.assertEqual(
                    payload["runtime_fixed_closed_loop_playback_audit"]["audit_status"],
                    audit_status,
                )

        forced = {
            "missing_return": (
                {"force_missing_return_payload": True},
                "fixed_closed_loop_playback_blocked_missing_return_payload",
                "blocked_missing_return_payload",
            ),
            "missing_parent": (
                {"force_missing_parent_resume": True},
                "fixed_closed_loop_playback_blocked_missing_parent_resume",
                "blocked_missing_parent_resume",
            ),
            "unclosed": (
                {"force_unclosed_root_frame": True},
                "fixed_closed_loop_playback_blocked_unclosed_root_frame",
                "blocked_unclosed_root_event",
            ),
            "live": (
                {"force_live_engine_invocation": True},
                "fixed_closed_loop_playback_blocked_forbidden_authority_detected",
                "blocked_live_engine_invocation_detected",
            ),
            "dynamic": (
                {"force_dynamic_child_event": True},
                "fixed_closed_loop_playback_blocked_forbidden_authority_detected",
                "blocked_dynamic_child_event_scheduling_detected",
            ),
            "autonomous": (
                {"force_autonomous_scheduler": True},
                "fixed_closed_loop_playback_blocked_forbidden_authority_detected",
                "blocked_autonomous_scheduler_detected",
            ),
            "open": (
                {"force_open_ended_loop": True},
                "fixed_closed_loop_playback_blocked_forbidden_authority_detected",
                "blocked_open_ended_loop_detected",
            ),
            "external": (
                {"force_external_execution": True},
                "fixed_closed_loop_playback_blocked_forbidden_authority_detected",
                "blocked_external_execution_detected",
            ),
            "memory": (
                {"force_memory_write": True},
                "fixed_closed_loop_playback_blocked_forbidden_authority_detected",
                "blocked_memory_write_detected",
            ),
            "learning": (
                {"force_automatic_learning_approval": True},
                "fixed_closed_loop_playback_blocked_forbidden_authority_detected",
                "blocked_automatic_learning_approval_detected",
            ),
            "recursive": (
                {"force_recursive_learning": True},
                "fixed_closed_loop_playback_blocked_forbidden_authority_detected",
                "blocked_recursive_learning_detected",
            ),
            "thought": (
                {"force_thought_engine_behavior": True},
                "fixed_closed_loop_playback_blocked_forbidden_authority_detected",
                "blocked_thought_engine_fake_detected",
            ),
            "production": (
                {"force_production_behavior": True},
                "fixed_closed_loop_playback_blocked_forbidden_authority_detected",
                "blocked_production_behavior_detected",
            ),
        }
        for case, (kwargs, expected_trace, expected_audit) in forced.items():
            with self.subTest(case=case):
                trace = self._forced_trace(full, **kwargs)
                audit = playback.build_runtime_fixed_closed_loop_playback_audit(
                    playback_plan=full["runtime_fixed_closed_loop_playback_plan"],
                    fixed_playback_trace=trace,
                    fixed_playback_render=full[
                        "runtime_fixed_closed_loop_playback_render"
                    ],
                    closed_loop_milestone=full["source_package94_milestone"][
                        "first_closed_loop_milestone"
                    ],
                    integrated_event_loop_trace=full[
                        "runtime_integrated_event_loop_trace"
                    ],
                )
                self.assertEqual(trace.fixed_playback_status, expected_trace)
                self.assertEqual(audit.audit_status, expected_audit)

    def test_render_and_summary_records_are_readable_and_bounded(self) -> None:
        payload = playback.build_demo_full_fixed_closed_loop_playback()
        render = playback.RuntimeFixedClosedLoopPlaybackRenderRecord.from_dict(
            payload["runtime_fixed_closed_loop_playback_render"]
        )
        self.assertEqual(render.render_status, "fixed_playback_render_created")
        self.assertEqual(
            len(render.stage_summary_lines),
            len(playback.REQUIRED_CLOSED_LOOP_STAGES),
        )
        self.assertIn("first_task_action_chain", render.human_readable_playback_text)
        self.assertIn("working_readback_integration", render.human_readable_playback_text)
        for key in ("space", ".", "1", "2", "3", "4", "D", "R", "P", "S"):
            self.assertIn(key, render.legend)

        grouped = playback.build_demo_grouped_stage_fixed_closed_loop_playback()
        self.assertEqual(
            grouped["runtime_fixed_closed_loop_playback_render"]["render_status"],
            "fixed_playback_render_created_with_grouped_stages",
        )
        blocked = playback.build_demo_blocked_missing_stage_fixed_playback()
        self.assertEqual(
            blocked["runtime_fixed_closed_loop_playback_render"]["render_status"],
            "fixed_playback_render_blocked_invalid_trace",
        )
        summary = playback.render_fixed_closed_loop_playback_summary_text(
            payload["runtime_fixed_closed_loop_playback_trace"],
            payload["runtime_fixed_closed_loop_playback_audit"],
            payload["runtime_fixed_closed_loop_playback_readiness"],
        )
        self.assertIn("fixed_playback status=fixed_closed_loop_playback_complete", summary)
        self.assertIn("readiness=ready_for_bounded_handler_binding_only", summary)

    def test_audit_passes_and_blocks_required_boundaries(self) -> None:
        full = playback.build_demo_full_fixed_closed_loop_playback()
        audit = playback.RuntimeFixedClosedLoopPlaybackAudit.from_dict(
            full["runtime_fixed_closed_loop_playback_audit"]
        )
        self.assertEqual(
            audit.audit_status,
            "passed_fixed_closed_loop_playback_over_event_frames",
        )
        self.assertTrue(audit.fixed_playback_only_confirmed)
        self.assertTrue(audit.record_only_confirmed)
        self.assertTrue(audit.adapter_only_confirmed)
        self.assertTrue(audit.no_live_engine_invocation)
        self.assertTrue(audit.no_dynamic_child_event_scheduling)
        self.assertTrue(audit.no_external_execution)
        self.assertTrue(audit.no_memory_layer_write)
        self.assertTrue(audit.no_automatic_learning_approval)
        self.assertTrue(audit.no_recursive_learning)
        self.assertTrue(audit.no_thought_engine_behavior)
        self.assertTrue(audit.no_first_output)

        grouped = playback.build_demo_grouped_stage_fixed_closed_loop_playback()
        self.assertEqual(
            grouped["runtime_fixed_closed_loop_playback_audit"]["audit_status"],
            "passed_fixed_closed_loop_playback_with_grouped_stages",
        )
        demo_audits = {
            "missing_stage": (
                playback.build_demo_blocked_missing_stage_fixed_playback,
                "blocked_missing_required_stage",
            ),
            "missing_mapping": (
                playback.build_demo_blocked_missing_event_frame_mapping_fixed_playback,
                "blocked_missing_event_frame_mapping",
            ),
            "missing_dispatch": (
                playback.build_demo_blocked_missing_dispatch_lineage_fixed_playback,
                "blocked_missing_dispatch_lineage",
            ),
            "live": (
                playback.build_demo_blocked_live_handler_invocation_fixed_playback,
                "blocked_live_engine_invocation_detected",
            ),
            "learning_artifact": (
                playback.build_demo_blocked_new_learning_artifact_fixed_playback,
                "blocked_recursive_learning_detected",
            ),
            "forbidden": (
                playback.build_demo_blocked_forbidden_authority_fixed_playback,
                "blocked_memory_write_detected",
            ),
        }
        for case, (builder, expected_status) in demo_audits.items():
            with self.subTest(case=case):
                self.assertEqual(
                    builder()["runtime_fixed_closed_loop_playback_audit"][
                        "audit_status"
                    ],
                    expected_status,
                )

        forced_audits = {
            "missing_milestone": (
                {"force_missing_closed_loop_milestone": True},
                "blocked_missing_closed_loop_milestone",
            ),
            "missing_integrated": (
                {"force_missing_integrated_event_loop_trace": True},
                "blocked_missing_integrated_event_loop_trace",
            ),
            "first_output": (
                {"force_first_output": True},
                "blocked_first_output_detected",
            ),
        }
        for case, (kwargs, expected_status) in forced_audits.items():
            with self.subTest(case=case):
                blocked = playback.build_runtime_fixed_closed_loop_playback_audit(
                    playback_plan=full["runtime_fixed_closed_loop_playback_plan"],
                    fixed_playback_trace=full[
                        "runtime_fixed_closed_loop_playback_trace"
                    ],
                    fixed_playback_render=full[
                        "runtime_fixed_closed_loop_playback_render"
                    ],
                    closed_loop_milestone=full["source_package94_milestone"][
                        "first_closed_loop_milestone"
                    ],
                    integrated_event_loop_trace=full[
                        "runtime_integrated_event_loop_trace"
                    ],
                    **kwargs,
                )
                self.assertEqual(blocked.audit_status, expected_status)

    def test_readiness_recommends_bounded_handler_binding_only(self) -> None:
        payload = playback.build_demo_full_fixed_closed_loop_playback()
        readiness = playback.RuntimeFixedClosedLoopPlaybackReadinessRecord.from_dict(
            payload["runtime_fixed_closed_loop_playback_readiness"]
        )
        self.assertEqual(
            readiness.readiness_status,
            "ready_for_bounded_handler_binding_only",
        )
        self.assertTrue(readiness.ready_for_bounded_handler_binding)
        self.assertTrue(readiness.ready_for_runtime_state_persistence_binding)
        self.assertTrue(readiness.ready_for_teacher_observed_playback_cli)
        self.assertFalse(readiness.ready_for_dynamic_child_event_scheduling)
        self.assertFalse(readiness.ready_for_autonomous_scheduler)
        self.assertFalse(readiness.ready_for_open_ended_loop)
        self.assertFalse(readiness.ready_for_live_engine_invocation)
        self.assertFalse(readiness.ready_for_external_execution)
        self.assertFalse(readiness.ready_for_memory_layer_write)
        self.assertFalse(readiness.ready_for_automatic_learning_approval)
        self.assertFalse(readiness.ready_for_recursive_learning)
        self.assertFalse(readiness.ready_for_thought_engine_runtime)
        self.assertFalse(readiness.ready_for_first_output)
        self.assertIn("Package 100", readiness.recommended_next_package)

        blocked_audit = playback.build_runtime_fixed_closed_loop_playback_audit(
            force_missing_closed_loop_milestone=True
        )
        blocked_readiness = playback.build_runtime_fixed_closed_loop_playback_readiness(
            blocked_audit
        )
        self.assertEqual(
            blocked_readiness.readiness_status,
            "not_ready_missing_fixed_playback",
        )

    def test_record_validators_accept_demo_records(self) -> None:
        payload = playback.build_demo_full_fixed_closed_loop_playback()
        self.assertTrue(
            playback.validate_runtime_fixed_closed_loop_playback_plan(
                payload["runtime_fixed_closed_loop_playback_plan"]
            )["valid"]
        )
        self.assertTrue(
            playback.validate_runtime_closed_loop_stage_to_event_frame_mapping(
                payload["runtime_closed_loop_stage_event_mappings"][0]
            )["valid"]
        )
        self.assertTrue(
            playback.validate_runtime_fixed_closed_loop_playback_step(
                payload["runtime_fixed_closed_loop_playback_steps"][0]
            )["valid"]
        )
        self.assertTrue(
            playback.validate_runtime_fixed_closed_loop_playback_trace(
                payload["runtime_fixed_closed_loop_playback_trace"]
            )["valid"]
        )
        self.assertTrue(
            playback.validate_runtime_fixed_closed_loop_playback_render(
                payload["runtime_fixed_closed_loop_playback_render"]
            )["valid"]
        )
        self.assertTrue(
            playback.validate_runtime_fixed_closed_loop_playback_audit(
                payload["runtime_fixed_closed_loop_playback_audit"]
            )["valid"]
        )
        self.assertTrue(
            playback.validate_runtime_fixed_closed_loop_playback_readiness(
                payload["runtime_fixed_closed_loop_playback_readiness"]
            )["valid"]
        )

    def test_cli_commands_work_without_writing_state(self) -> None:
        commands = (
            ("show-demo-full",),
            ("show-demo-grouped",),
            ("show-demo-render",),
            ("show-demo-readiness",),
            ("validate-demo-fixed-playback",),
            ("show-demo-blocked", "--case", "missing-stage"),
            ("show-demo-blocked", "--case", "missing-event-frame-mapping"),
            ("show-demo-blocked", "--case", "missing-dispatch-lineage"),
            ("show-demo-blocked", "--case", "live-handler-invocation"),
            ("show-demo-blocked", "--case", "new-learning-artifact"),
            ("show-demo-blocked", "--case", "forbidden-authority"),
        )
        for command in commands:
            with self.subTest(command=command):
                payload = self._run_json_module(PLAYBACK_CLI, *command)
                self.assertIsInstance(payload, dict)

    def test_guided_console_fixed_playback_commands_work(self) -> None:
        validation = validate_fixed_closed_loop_playback_from_guided_cradle_growth_console()
        self.assertEqual(
            validation["validation"]["audit_status"],
            "passed_fixed_closed_loop_playback_over_event_frames",
        )
        commands = (
            "runtime-show-fixed-closed-loop-playback-demo",
            "runtime-show-fixed-closed-loop-playback-grouped-demo",
            "runtime-show-fixed-closed-loop-playback-render",
            "runtime-show-fixed-closed-loop-playback-readiness",
            "runtime-validate-fixed-closed-loop-playback",
        )
        for command in commands:
            with self.subTest(command=command):
                payload = self._run_json_module(GUIDED_CLI, command)
                self.assertFalse(payload["background_process_started"])
                self.assertFalse(payload["dynamic_scheduling_created"])
                self.assertFalse(payload["autonomous_scheduler_created"])
                self.assertFalse(payload["open_ended_loop_created"])
                self.assertFalse(payload["external_execution_created"])
                self.assertFalse(payload["memory_layer_write_performed"])
                self.assertFalse(payload["automatic_learning_approval_created"])
                self.assertFalse(payload["recursive_learning_created"])
                self.assertFalse(payload["new_learning_artifact_created"])

    def test_no_repo_data_directory_created(self) -> None:
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _integrated_step_for_mapping(
        self,
        payload: dict[str, object],
        mapping: playback.RuntimeClosedLoopStageToEventFrameMappingRecord,
    ) -> dict[str, object]:
        return next(
            item
            for item in payload["runtime_integrated_event_steps"]
            if item["source_event_frame_id"] == mapping.target_event_frame_id
        )

    def _link_for_mapping(
        self,
        payload: dict[str, object],
        mapping: playback.RuntimeClosedLoopStageToEventFrameMappingRecord,
    ) -> dict[str, object]:
        return next(
            item
            for item in payload["runtime_integrated_dispatch_resume_links"]
            if item["source_event_frame_id"] == mapping.target_event_frame_id
        )

    def _forced_trace(
        self,
        payload: dict[str, object],
        **kwargs: bool,
    ) -> playback.RuntimeFixedClosedLoopPlaybackTrace:
        return playback.build_runtime_fixed_closed_loop_playback_trace(
            playback_plan=payload["runtime_fixed_closed_loop_playback_plan"],
            stage_mappings=payload["runtime_closed_loop_stage_event_mappings"],
            playback_steps=payload["runtime_fixed_closed_loop_playback_steps"],
            integrated_event_loop_trace=payload["runtime_integrated_event_loop_trace"],
            closed_loop_milestone=payload["source_package94_milestone"][
                "first_closed_loop_milestone"
            ],
            **kwargs,
        )

    def _run_json_module(self, module: str, *args: str) -> dict[str, object]:
        result = subprocess.run(
            [sys.executable, "-m", module, *args],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(result.stdout)


if __name__ == "__main__":
    unittest.main()
