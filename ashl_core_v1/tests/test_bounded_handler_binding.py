from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from ashl_core_v1.runtime import bounded_handler_binding as binding
from ashl_core_v1.runtime.guided_cradle_growth_teacher_console import (
    validate_bounded_handler_binding_from_guided_cradle_growth_console,
)


BINDING_CLI = "ashl_core_v1.runtime.bounded_handler_binding_cli"
GUIDED_CLI = "ashl_core_v1.runtime.guided_cradle_growth_teacher_console_cli"


class RuntimeBoundedHandlerBindingTests(unittest.TestCase):
    def test_binding_plan_builds_and_blocks_authority(self) -> None:
        payload = binding.build_demo_selected_handler_binding_trace()
        plan = binding.RuntimeBoundedHandlerBindingPlanRecord.from_dict(
            payload["runtime_bounded_handler_binding_plan"]
        )
        fixed_trace = payload["runtime_fixed_closed_loop_playback_trace"]
        fixed_audit = payload["runtime_fixed_closed_loop_playback_audit"]

        self.assertEqual(plan.binding_plan_status, "binding_plan_created")
        self.assertEqual(plan.allowed_stage_names, binding.SELECTED_BINDABLE_STAGES)
        self.assertTrue(plan.bounded_fixture_only)
        self.assertTrue(plan.fixed_sequence_only)
        self.assertTrue(plan.side_effect_free_required)
        self.assertTrue(plan.deterministic_required)
        self.assertTrue(plan.record_output_snapshot_only)
        self.assertFalse(plan.dynamic_handler_discovery_allowed)
        self.assertFalse(plan.live_engine_invocation_allowed)

        cases = {
            "missing_trace": (
                {"fixed_playback_trace": None, "fixed_playback_audit": fixed_audit},
                "blocked_missing_fixed_playback_trace",
            ),
            "missing_audit": (
                {"fixed_playback_trace": fixed_trace, "fixed_playback_audit": None},
                "blocked_missing_fixed_playback_audit",
            ),
            "unbounded": (
                {
                    "fixed_playback_trace": fixed_trace,
                    "fixed_playback_audit": fixed_audit,
                    "allowed_stage_names": (),
                },
                "blocked_unbounded_binding_plan",
            ),
            "live": (
                {
                    "fixed_playback_trace": fixed_trace,
                    "fixed_playback_audit": fixed_audit,
                    "live_engine_invocation_allowed": True,
                },
                "blocked_live_engine_invocation_requested",
            ),
            "dynamic_handler": (
                {
                    "fixed_playback_trace": fixed_trace,
                    "fixed_playback_audit": fixed_audit,
                    "dynamic_handler_discovery_allowed": True,
                },
                "blocked_forbidden_authority_detected",
            ),
            "memory": (
                {
                    "fixed_playback_trace": fixed_trace,
                    "fixed_playback_audit": fixed_audit,
                    "memory_layer_write_allowed": True,
                },
                "blocked_forbidden_authority_detected",
            ),
            "learning": (
                {
                    "fixed_playback_trace": fixed_trace,
                    "fixed_playback_audit": fixed_audit,
                    "automatic_learning_approval_allowed": True,
                },
                "blocked_forbidden_authority_detected",
            ),
            "first_output": (
                {
                    "fixed_playback_trace": fixed_trace,
                    "fixed_playback_audit": fixed_audit,
                    "first_output_allowed": True,
                },
                "blocked_forbidden_authority_detected",
            ),
        }
        for case, (kwargs, expected_status) in cases.items():
            with self.subTest(case=case):
                blocked = binding.build_runtime_bounded_handler_binding_plan(**kwargs)
                self.assertEqual(blocked.binding_plan_status, expected_status)

    def test_stage_binding_binds_selected_stages_and_blocks_invalid_handlers(self) -> None:
        payload = binding.build_demo_selected_handler_binding_trace()
        bindings = [
            binding.RuntimeFixedStageHandlerBindingRecord.from_dict(item)
            for item in payload["runtime_fixed_stage_handler_bindings"]
        ]
        by_stage = {item.closed_loop_stage_name: item for item in bindings}
        for stage in binding.SELECTED_BINDABLE_STAGES:
            with self.subTest(stage=stage):
                item = by_stage[stage]
                self.assertIn(
                    item.binding_status,
                    {"handler_bound_to_fixed_stage", "handler_bound_as_snapshot_only"},
                )
                self.assertTrue(item.handler_available)
                self.assertTrue(item.handler_side_effect_free_declared)
                self.assertTrue(item.handler_deterministic_declared)
                self.assertTrue(item.handler_fixture_bounded)
                self.assertTrue(item.handler_invocation_allowed)
                self.assertFalse(item.live_engine_invocation_allowed)
                self.assertFalse(item.creates_new_memory_write)
                self.assertFalse(item.creates_new_sandbox_execution)

        deferred = binding.build_demo_deferred_missing_handler_binding()
        deferred_binding = binding.RuntimeFixedStageHandlerBindingRecord.from_dict(
            deferred["runtime_fixed_stage_handler_bindings"][0]
        )
        self.assertEqual(deferred_binding.closed_loop_stage_name, "concept_candidate_draft")
        self.assertEqual(deferred_binding.binding_status, "handler_deferred_unavailable")

        plan = payload["runtime_bounded_handler_binding_plan"]
        step = self._step(payload, "first_task_action_chain")
        mapping = self._mapping(payload, "first_task_action_chain")
        unsupported = binding.build_runtime_fixed_stage_handler_binding(
            binding_plan=plan,
            playback_step=step,
            stage_event_mapping=mapping,
        )
        self.assertEqual(
            unsupported.binding_status,
            "handler_blocked_stage_not_allowed",
        )
        invalid_cases = {
            "not_side_effect_free": (
                {"handler_side_effect_free_declared": False},
                "handler_blocked_not_side_effect_free",
            ),
            "not_deterministic": (
                {"handler_deterministic_declared": False},
                "handler_blocked_not_deterministic",
            ),
            "not_fixture_bounded": (
                {"handler_fixture_bounded": False},
                "handler_blocked_not_fixture_bounded",
            ),
            "forbidden": (
                {"creates_new_sandbox_execution": True},
                "handler_blocked_forbidden_authority_detected",
            ),
        }
        valid_step = self._step(payload, "sense_observation")
        valid_mapping = self._mapping(payload, "sense_observation")
        for case, (kwargs, expected_status) in invalid_cases.items():
            with self.subTest(case=case):
                record = binding.build_runtime_fixed_stage_handler_binding(
                    binding_plan=plan,
                    playback_step=valid_step,
                    stage_event_mapping=valid_mapping,
                    **kwargs,
                )
                self.assertEqual(record.binding_status, expected_status)

    def test_handler_invocation_records_snapshot_and_blocks_forbidden_paths(self) -> None:
        payload = binding.build_demo_selected_handler_binding_trace()
        stage_binding = self._stage_binding(payload, "sense_observation")
        step = self._step(payload, "sense_observation")
        invocation = binding.RuntimeBoundedHandlerInvocationRecord.from_dict(
            payload["runtime_bounded_handler_invocations"][0]
        )
        self.assertEqual(
            invocation.invocation_status,
            "handler_invocation_snapshot_recorded",
        )
        self.assertEqual(invocation.invocation_mode, "snapshot_only_no_call")
        self.assertFalse(invocation.handler_called)
        self.assertTrue(invocation.handler_call_side_effect_free)
        self.assertTrue(invocation.handler_call_deterministic)
        self.assertTrue(invocation.handler_call_bounded)
        self.assertFalse(invocation.live_engine_invocation_created)

        pure = binding.build_runtime_bounded_handler_invocation(
            fixed_stage_handler_binding=stage_binding,
            playback_step=step,
            invocation_mode="pure_demo_builder_call",
        )
        self.assertEqual(
            pure.invocation_status,
            "handler_invocation_pure_demo_completed",
        )
        self.assertTrue(pure.handler_called)

        deferred = binding.build_demo_deferred_missing_handler_binding()
        self.assertEqual(
            deferred["runtime_bounded_handler_invocations"][0]["invocation_status"],
            "handler_invocation_deferred_unavailable",
        )

        live = binding.build_runtime_bounded_handler_invocation(
            fixed_stage_handler_binding=stage_binding,
            playback_step=step,
            live_engine_invocation_created=True,
        )
        self.assertEqual(
            live.invocation_status,
            "handler_invocation_blocked_live_engine_invocation",
        )
        forbidden_flags = (
            "dynamic_handler_selection_created",
            "dynamic_child_event_created",
            "new_learning_feedback_candidate_created",
            "new_concept_candidate_created",
            "new_reviewed_concept_created",
            "new_memory_application_data_created",
            "new_memory_write_performed",
            "new_sandbox_execution_performed",
            "external_execution_created",
            "automatic_learning_approval_created",
            "recursive_learning_created",
            "first_output_created",
        )
        for flag in forbidden_flags:
            with self.subTest(flag=flag):
                blocked = binding.build_runtime_bounded_handler_invocation(
                    fixed_stage_handler_binding=stage_binding,
                    playback_step=step,
                    **{flag: True},
                )
                self.assertEqual(
                    blocked.invocation_status,
                    "handler_invocation_blocked_forbidden_authority_detected",
                )

    def test_output_snapshot_and_return_payload_are_safe_and_block_side_effects(self) -> None:
        payload = binding.build_demo_selected_handler_binding_trace()
        snapshots = [
            binding.RuntimeBoundedHandlerOutputSnapshotRecord.from_dict(item)
            for item in payload["runtime_bounded_handler_output_snapshots"]
        ]
        kinds_by_stage = {item.closed_loop_stage_name: item.output_snapshot_kind for item in snapshots}
        self.assertEqual(kinds_by_stage["sense_observation"], "sense_observation_snapshot")
        self.assertEqual(kinds_by_stage["outcome_evaluation"], "outcome_evaluation_snapshot")
        self.assertEqual(kinds_by_stage["task_closure"], "task_closure_snapshot")
        self.assertEqual(kinds_by_stage["learning_feedback_candidate"], "learning_feedback_candidate_snapshot")
        self.assertEqual(kinds_by_stage["working_readback_integration"], "working_readback_snapshot")
        self.assertEqual(kinds_by_stage["closed_loop_milestone_audit"], "milestone_audit_snapshot")
        for snapshot in snapshots:
            self.assertTrue(snapshot.output_trace_refs_preserved)
            self.assertTrue(snapshot.output_safe_for_return_payload)
            self.assertFalse(snapshot.creates_new_memory_write)
            self.assertFalse(snapshot.creates_new_learning_approval)
            self.assertFalse(snapshot.creates_new_execution)
            self.assertFalse(snapshot.creates_external_side_effect)
            self.assertFalse(snapshot.creates_first_output)

        stage_binding = self._stage_binding(payload, "sense_observation")
        invocation = self._invocation(payload, "sense_observation")
        invalid = binding.build_runtime_bounded_handler_output_snapshot(
            bounded_handler_invocation=invocation,
            fixed_stage_handler_binding=stage_binding,
            force_invalid_shape=True,
        )
        self.assertEqual(invalid.output_snapshot_status, "output_snapshot_blocked_invalid_shape")
        forbidden_flags = (
            "creates_new_memory_write",
            "creates_new_learning_approval",
            "creates_new_execution",
            "creates_external_side_effect",
            "creates_first_output",
        )
        for flag in forbidden_flags:
            with self.subTest(flag=flag):
                blocked = binding.build_runtime_bounded_handler_output_snapshot(
                    bounded_handler_invocation=invocation,
                    fixed_stage_handler_binding=stage_binding,
                    **{flag: True},
                )
                self.assertEqual(
                    blocked.output_snapshot_status,
                    "output_snapshot_blocked_forbidden_authority_detected",
                )

        return_payload = binding.RuntimeBoundedHandlerReturnPayloadRecord.from_dict(
            payload["runtime_bounded_handler_return_payloads"][0]
        )
        self.assertEqual(return_payload.return_status, "returned_success")
        self.assertTrue(return_payload.safe_for_dispatch_return_payload)
        self.assertTrue(return_payload.safe_for_parent_resume)
        followup = binding.build_runtime_bounded_handler_return_payload(
            bounded_handler_output_snapshot=snapshots[0],
            bounded_handler_invocation=invocation,
            fixed_stage_handler_binding=stage_binding,
            requires_followup_event=True,
        )
        self.assertTrue(followup.requires_followup_event)
        self.assertFalse(followup.creates_followup_event)
        for flag in (
            "memory_write_performed",
            "automatic_learning_approval_created",
            "recursive_learning_created",
            "external_execution_created",
            "first_output_created",
        ):
            with self.subTest(flag=flag):
                blocked = binding.build_runtime_bounded_handler_return_payload(
                    bounded_handler_output_snapshot=snapshots[0],
                    bounded_handler_invocation=invocation,
                    fixed_stage_handler_binding=stage_binding,
                    **{flag: True},
                )
                self.assertEqual(
                    blocked.return_status,
                    "blocked_forbidden_authority_detected",
                )

    def test_binding_trace_counts_and_blocks_invalid_or_forbidden_cases(self) -> None:
        payload = binding.build_demo_selected_handler_binding_trace()
        trace = binding.RuntimeBoundedHandlerBindingTrace.from_dict(
            payload["runtime_bounded_handler_binding_trace"]
        )
        self.assertEqual(trace.binding_trace_status, "bounded_handler_binding_trace_complete")
        self.assertEqual(trace.bound_stage_names, binding.SELECTED_BINDABLE_STAGES)
        self.assertEqual(trace.deferred_stage_names, ())
        self.assertEqual(trace.handler_invocation_count, len(binding.SELECTED_BINDABLE_STAGES))
        self.assertEqual(trace.output_snapshot_count, len(binding.SELECTED_BINDABLE_STAGES))
        self.assertEqual(trace.return_payload_count, len(binding.SELECTED_BINDABLE_STAGES))
        self.assertTrue(trace.all_outputs_safe_for_return)
        self.assertTrue(trace.all_invocations_side_effect_free)
        self.assertTrue(trace.all_returns_safe_for_parent_resume)

        deferred = binding.build_demo_deferred_missing_handler_binding()
        self.assertEqual(
            deferred["runtime_bounded_handler_binding_trace"]["deferred_stage_names"],
            ["concept_candidate_draft"],
        )
        self.assertEqual(
            deferred["runtime_bounded_handler_binding_trace"]["binding_trace_status"],
            "bounded_handler_binding_trace_complete_with_deferred_handlers",
        )

        forced = {
            "missing_playback": (
                {"force_missing_playback": True},
                "bounded_handler_binding_trace_blocked_missing_playback",
                "blocked_missing_fixed_playback",
            ),
            "missing_binding": (
                {"force_missing_binding": True},
                "bounded_handler_binding_trace_blocked_missing_binding",
                "blocked_invalid_stage_binding",
            ),
            "invalid_invocation": (
                {"force_invalid_invocation": True},
                "bounded_handler_binding_trace_blocked_invalid_invocation",
                "blocked_invalid_handler_invocation",
            ),
            "invalid_output": (
                {"force_invalid_output": True},
                "bounded_handler_binding_trace_blocked_invalid_output",
                "blocked_invalid_output_snapshot",
            ),
            "dynamic_handler": (
                {"force_dynamic_handler_selection": True},
                "bounded_handler_binding_trace_blocked_forbidden_authority_detected",
                "blocked_dynamic_handler_selection_detected",
            ),
            "dynamic_child": (
                {"force_dynamic_child_event": True},
                "bounded_handler_binding_trace_blocked_forbidden_authority_detected",
                "blocked_dynamic_child_event_scheduling_detected",
            ),
            "external": (
                {"force_external_execution": True},
                "bounded_handler_binding_trace_blocked_forbidden_authority_detected",
                "blocked_external_execution_detected",
            ),
            "memory": (
                {"force_memory_write": True},
                "bounded_handler_binding_trace_blocked_forbidden_authority_detected",
                "blocked_memory_write_detected",
            ),
            "learning": (
                {"force_automatic_learning_approval": True},
                "bounded_handler_binding_trace_blocked_forbidden_authority_detected",
                "blocked_automatic_learning_approval_detected",
            ),
            "recursive": (
                {"force_recursive_learning": True},
                "bounded_handler_binding_trace_blocked_forbidden_authority_detected",
                "blocked_recursive_learning_detected",
            ),
            "thought": (
                {"force_thought_engine_behavior": True},
                "bounded_handler_binding_trace_blocked_forbidden_authority_detected",
                "blocked_thought_engine_fake_detected",
            ),
            "first_output": (
                {"force_first_output": True},
                "bounded_handler_binding_trace_blocked_forbidden_authority_detected",
                "blocked_first_output_detected",
            ),
            "production": (
                {"force_production_behavior": True},
                "bounded_handler_binding_trace_blocked_forbidden_authority_detected",
                "blocked_production_behavior_detected",
            ),
        }
        for case, (kwargs, trace_status, audit_status) in forced.items():
            with self.subTest(case=case):
                forced_trace = self._forced_trace(payload, **kwargs)
                audit = self._audit_for_trace(payload, forced_trace)
                self.assertEqual(forced_trace.binding_trace_status, trace_status)
                self.assertEqual(audit.audit_status, audit_status)

    def test_audit_and_readiness_pass_and_block_required_boundaries(self) -> None:
        payload = binding.build_demo_selected_handler_binding_trace()
        audit = binding.RuntimeBoundedHandlerBindingAudit.from_dict(
            payload["runtime_bounded_handler_binding_audit"]
        )
        self.assertEqual(audit.audit_status, "passed_bounded_handler_binding_for_fixed_playback")
        self.assertTrue(audit.fixed_sequence_confirmed)
        self.assertTrue(audit.bounded_fixture_confirmed)
        self.assertTrue(audit.side_effect_free_confirmed)
        self.assertTrue(audit.deterministic_confirmed)
        self.assertTrue(audit.snapshot_only_confirmed)
        self.assertTrue(audit.no_live_engine_invocation)
        self.assertTrue(audit.no_dynamic_handler_selection)
        self.assertTrue(audit.no_dynamic_child_event_scheduling)
        self.assertTrue(audit.no_external_execution)
        self.assertTrue(audit.no_memory_layer_write)
        self.assertTrue(audit.no_automatic_learning_approval)
        self.assertTrue(audit.no_recursive_learning)
        self.assertTrue(audit.no_new_learning_artifacts)
        self.assertTrue(audit.no_new_sandbox_execution)
        self.assertTrue(audit.no_thought_engine_behavior)
        self.assertTrue(audit.no_first_output)
        self.assertTrue(audit.no_production_behavior)

        deferred = binding.build_demo_deferred_missing_handler_binding()
        self.assertEqual(
            deferred["runtime_bounded_handler_binding_audit"]["audit_status"],
            "passed_bounded_handler_binding_with_deferred_handlers",
        )
        blocked_demos = {
            "live": (
                binding.build_demo_blocked_live_handler_invocation_binding,
                "blocked_live_engine_invocation_detected",
            ),
            "learning_artifact": (
                binding.build_demo_blocked_new_learning_artifact_binding,
                "blocked_new_learning_artifact_detected",
            ),
            "memory": (
                binding.build_demo_blocked_memory_write_binding,
                "blocked_memory_write_detected",
            ),
            "sandbox": (
                binding.build_demo_blocked_new_sandbox_execution_binding,
                "blocked_new_sandbox_execution_detected",
            ),
        }
        for case, (builder, expected_status) in blocked_demos.items():
            with self.subTest(case=case):
                self.assertEqual(
                    builder()["runtime_bounded_handler_binding_audit"]["audit_status"],
                    expected_status,
                )

        forced_audit = binding.build_runtime_bounded_handler_binding_audit(
            binding_plan=payload["runtime_bounded_handler_binding_plan"],
            binding_trace=payload["runtime_bounded_handler_binding_trace"],
            fixed_playback_audit=payload["runtime_fixed_closed_loop_playback_audit"],
            force_autonomous_scheduler=True,
        )
        self.assertEqual(
            forced_audit.audit_status,
            "blocked_autonomous_scheduler_detected",
        )
        forced_open = binding.build_runtime_bounded_handler_binding_audit(
            binding_plan=payload["runtime_bounded_handler_binding_plan"],
            binding_trace=payload["runtime_bounded_handler_binding_trace"],
            fixed_playback_audit=payload["runtime_fixed_closed_loop_playback_audit"],
            force_open_ended_loop=True,
        )
        self.assertEqual(
            forced_open.audit_status,
            "blocked_open_ended_loop_detected",
        )

        readiness = binding.RuntimeBoundedHandlerBindingReadinessRecord.from_dict(
            payload["runtime_bounded_handler_binding_readiness"]
        )
        self.assertEqual(
            readiness.readiness_status,
            "ready_for_handler_bound_fixed_playback_audit_milestone_only",
        )
        self.assertTrue(readiness.ready_for_handler_bound_fixed_playback_audit_milestone)
        self.assertTrue(readiness.ready_for_runtime_state_persistence_binding)
        self.assertTrue(readiness.ready_for_teacher_observed_playback_cli)
        self.assertFalse(readiness.ready_for_live_runtime_session)
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
        self.assertIn("Package 101", readiness.recommended_next_package)

    def test_renderers_and_validators_accept_demo_records(self) -> None:
        payload = binding.build_demo_selected_handler_binding_trace()
        self.assertTrue(
            binding.validate_runtime_bounded_handler_binding_plan(
                payload["runtime_bounded_handler_binding_plan"]
            )["valid"]
        )
        self.assertTrue(
            binding.validate_runtime_fixed_stage_handler_binding(
                payload["runtime_fixed_stage_handler_bindings"][0]
            )["valid"]
        )
        self.assertTrue(
            binding.validate_runtime_bounded_handler_invocation(
                payload["runtime_bounded_handler_invocations"][0]
            )["valid"]
        )
        self.assertTrue(
            binding.validate_runtime_bounded_handler_output_snapshot(
                payload["runtime_bounded_handler_output_snapshots"][0]
            )["valid"]
        )
        self.assertTrue(
            binding.validate_runtime_bounded_handler_return_payload(
                payload["runtime_bounded_handler_return_payloads"][0]
            )["valid"]
        )
        self.assertTrue(
            binding.validate_runtime_bounded_handler_binding_trace(
                payload["runtime_bounded_handler_binding_trace"]
            )["valid"]
        )
        self.assertTrue(
            binding.validate_runtime_bounded_handler_binding_audit(
                payload["runtime_bounded_handler_binding_audit"]
            )["valid"]
        )
        self.assertTrue(
            binding.validate_runtime_bounded_handler_binding_readiness(
                payload["runtime_bounded_handler_binding_readiness"]
            )["valid"]
        )
        summary = binding.render_bounded_handler_binding_summary_text(
            payload["runtime_bounded_handler_binding_trace"],
            payload["runtime_bounded_handler_binding_audit"],
            payload["runtime_bounded_handler_binding_readiness"],
        )
        self.assertIn("bounded_handler_binding status=", summary)
        table = binding.render_bounded_handler_binding_stage_table(
            payload["runtime_fixed_stage_handler_bindings"],
            payload["runtime_bounded_handler_invocations"],
            payload["runtime_bounded_handler_output_snapshots"],
        )
        self.assertIn("sense_observation", table)
        self.assertIn("handler_invocation_snapshot_recorded", table)

    def test_cli_commands_work_without_writing_state(self) -> None:
        commands = (
            ("show-demo-sense",),
            ("show-demo-outcome",),
            ("show-demo-learning",),
            ("show-demo-memory",),
            ("show-demo-selected-trace",),
            ("show-demo-deferred",),
            ("show-demo-readiness",),
            ("validate-demo-binding",),
            ("show-demo-blocked", "--case", "live-handler-invocation"),
            ("show-demo-blocked", "--case", "new-learning-artifact"),
            ("show-demo-blocked", "--case", "memory-write"),
            ("show-demo-blocked", "--case", "new-sandbox-execution"),
        )
        for command in commands:
            with self.subTest(command=command):
                payload = self._run_json_module(BINDING_CLI, *command)
                self.assertIsInstance(payload, dict)

    def test_guided_console_bounded_handler_binding_commands_work(self) -> None:
        validation = validate_bounded_handler_binding_from_guided_cradle_growth_console()
        self.assertEqual(
            validation["validation"]["audit_status"],
            "passed_bounded_handler_binding_for_fixed_playback",
        )
        commands = (
            "runtime-show-bounded-handler-binding-sense-demo",
            "runtime-show-bounded-handler-binding-outcome-demo",
            "runtime-show-bounded-handler-binding-learning-demo",
            "runtime-show-bounded-handler-binding-memory-demo",
            "runtime-show-bounded-handler-binding-selected-trace-demo",
            "runtime-show-bounded-handler-binding-readiness",
            "runtime-validate-bounded-handler-binding-demo",
        )
        for command in commands:
            with self.subTest(command=command):
                payload = self._run_json_module(GUIDED_CLI, command)
                self.assertFalse(payload["background_process_started"])
                self.assertFalse(payload["dynamic_handler_selection_created"])
                self.assertFalse(payload["dynamic_scheduling_created"])
                self.assertFalse(payload["autonomous_scheduler_created"])
                self.assertFalse(payload["open_ended_loop_created"])
                self.assertFalse(payload["external_execution_created"])
                self.assertFalse(payload["memory_layer_write_performed"])
                self.assertFalse(payload["automatic_learning_approval_created"])
                self.assertFalse(payload["recursive_learning_created"])
                self.assertFalse(payload["new_learning_artifact_created"])
                self.assertFalse(payload["new_sandbox_execution_performed"])

    def test_no_repo_data_directory_created(self) -> None:
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _step(
        self, payload: dict[str, object], stage: str
    ) -> binding.RuntimeFixedClosedLoopPlaybackStepRecord:
        return binding.RuntimeFixedClosedLoopPlaybackStepRecord.from_dict(
            next(
                item
                for item in payload["runtime_fixed_closed_loop_playback_steps"]
                if item["closed_loop_stage_name"] == stage
            )
        )

    def _mapping(
        self, payload: dict[str, object], stage: str
    ) -> binding.RuntimeClosedLoopStageToEventFrameMappingRecord:
        return binding.RuntimeClosedLoopStageToEventFrameMappingRecord.from_dict(
            next(
                item
                for item in payload["runtime_closed_loop_stage_event_mappings"]
                if item["closed_loop_stage_name"] == stage
            )
        )

    def _stage_binding(
        self, payload: dict[str, object], stage: str
    ) -> binding.RuntimeFixedStageHandlerBindingRecord:
        return binding.RuntimeFixedStageHandlerBindingRecord.from_dict(
            next(
                item
                for item in payload["runtime_fixed_stage_handler_bindings"]
                if item["closed_loop_stage_name"] == stage
            )
        )

    def _invocation(
        self, payload: dict[str, object], stage: str
    ) -> binding.RuntimeBoundedHandlerInvocationRecord:
        stage_binding = self._stage_binding(payload, stage)
        return binding.RuntimeBoundedHandlerInvocationRecord.from_dict(
            next(
                item
                for item in payload["runtime_bounded_handler_invocations"]
                if item["source_fixed_stage_handler_binding_id"]
                == stage_binding.fixed_stage_handler_binding_id
            )
        )

    def _forced_trace(
        self,
        payload: dict[str, object],
        **kwargs: bool,
    ) -> binding.RuntimeBoundedHandlerBindingTrace:
        return binding.build_runtime_bounded_handler_binding_trace(
            binding_plan=payload["runtime_bounded_handler_binding_plan"],
            fixed_playback_trace=payload["runtime_fixed_closed_loop_playback_trace"],
            stage_bindings=payload["runtime_fixed_stage_handler_bindings"],
            handler_invocations=payload["runtime_bounded_handler_invocations"],
            output_snapshots=payload["runtime_bounded_handler_output_snapshots"],
            handler_return_payloads=payload["runtime_bounded_handler_return_payloads"],
            **kwargs,
        )

    def _audit_for_trace(
        self,
        payload: dict[str, object],
        trace: binding.RuntimeBoundedHandlerBindingTrace,
    ) -> binding.RuntimeBoundedHandlerBindingAudit:
        return binding.build_runtime_bounded_handler_binding_audit(
            binding_plan=payload["runtime_bounded_handler_binding_plan"],
            binding_trace=trace,
            fixed_playback_audit=payload["runtime_fixed_closed_loop_playback_audit"],
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
