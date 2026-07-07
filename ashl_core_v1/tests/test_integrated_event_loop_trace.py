from __future__ import annotations

import json
import subprocess
import sys
import unittest
from dataclasses import replace
from pathlib import Path

from ashl_core_v1.runtime import integrated_event_loop_trace as integrated
from ashl_core_v1.runtime.guided_cradle_growth_teacher_console import (
    validate_integrated_event_loop_demo_from_guided_cradle_growth_console,
)


INTEGRATED_CLI = "ashl_core_v1.runtime.integrated_event_loop_trace_cli"
GUIDED_CLI = "ashl_core_v1.runtime.guided_cradle_growth_teacher_console_cli"


class RuntimeIntegratedEventLoopTraceTests(unittest.TestCase):
    def test_integrated_event_step_records_lineage_and_blocks_forbidden(self) -> None:
        payload = integrated.build_demo_four_level_integrated_dispatch_resume_trace()
        steps = [
            integrated.RuntimeIntegratedEventStepRecord.from_dict(item)
            for item in payload["runtime_integrated_event_steps"]
        ]
        idle_step = next(item for item in steps if item.idle_tick)
        self.assertEqual(idle_step.step_status, "step_recorded_idle")
        self.assertIsNone(idle_step.source_event_frame_id)

        event_step = next(item for item in steps if item.source_event_frame_id)
        self.assertIsNotNone(event_step.source_runtime_tick_id)
        self.assertIsNotNone(event_step.source_dispatch_result_id)
        self.assertIsNotNone(event_step.source_dispatch_return_payload_id)
        self.assertTrue(event_step.event_frame_dispatched)
        self.assertTrue(event_step.return_payload_created)
        self.assertTrue(event_step.parent_resume_recorded)
        self.assertTrue(event_step.stack_updated)

        power_payload = integrated.build_demo_power_off_gap_integrated_trace()
        power_steps = [
            integrated.RuntimeIntegratedEventStepRecord.from_dict(item)
            for item in power_payload["runtime_integrated_event_steps"]
        ]
        power_gap = next(item for item in power_steps if item.power_off_gap)
        self.assertEqual(power_gap.step_status, "step_recorded_power_off_gap")
        self.assertIsNone(power_gap.source_runtime_tick_id)

        blocked = integrated.build_runtime_integrated_event_step_record(
            power_window=payload["runtime_power_window"],
            tick_index=99,
            timeline_symbol="1",
            step_kind="event_dispatch_step",
            force_memory_layer_write_performed=True,
        )
        self.assertEqual(
            blocked.step_status,
            "step_blocked_forbidden_authority_detected",
        )

    def test_dispatch_resume_link_validates_required_paths(self) -> None:
        simple = integrated.build_demo_simple_task_dispatch_resume_trace()
        simple_link = integrated.RuntimeIntegratedEventDispatchResumeLinkRecord.from_dict(
            simple["runtime_integrated_dispatch_resume_links"][0]
        )
        self.assertEqual(
            simple_link.link_status,
            "dispatch_resume_link_valid_root_close",
        )
        self.assertTrue(simple_link.dispatch_to_return_link_valid)
        self.assertTrue(simple_link.return_to_parent_resume_link_valid)
        self.assertTrue(simple_link.stack_update_link_valid)

        thought = integrated.build_demo_thought_deferred_integrated_trace()
        self.assertTrue(
            any(
                item["link_status"] == "dispatch_resume_link_deferred_thought_engine"
                for item in thought["runtime_integrated_dispatch_resume_links"]
            )
        )

        missing_dispatch = integrated.build_demo_blocked_missing_dispatch_integrated_trace()
        self.assertEqual(
            missing_dispatch["runtime_integrated_dispatch_resume_links"][0][
                "link_status"
            ],
            "blocked_missing_dispatch_result",
        )
        missing_parent = (
            integrated.build_demo_blocked_missing_parent_resume_integrated_trace()
        )
        self.assertTrue(
            any(
                item["link_status"] == "blocked_missing_parent_resume"
                for item in missing_parent["runtime_integrated_dispatch_resume_links"]
            )
        )

    def test_integrated_loop_trace_builds_demo_cases_and_counts(self) -> None:
        cases = {
            "simple": (
                integrated.build_demo_simple_task_dispatch_resume_trace,
                "integrated_event_loop_trace_complete",
            ),
            "nested": (
                integrated.build_demo_nested_sense_under_task_integrated_trace,
                "integrated_event_loop_trace_complete",
            ),
            "four_level": (
                integrated.build_demo_four_level_integrated_dispatch_resume_trace,
                "integrated_event_loop_trace_complete",
            ),
            "thought": (
                integrated.build_demo_thought_deferred_integrated_trace,
                "integrated_event_loop_trace_complete_with_deferred_thought",
            ),
            "power_off": (
                integrated.build_demo_power_off_gap_integrated_trace,
                "integrated_event_loop_trace_complete_with_power_off_gaps",
            ),
        }
        for case, (builder, expected_status) in cases.items():
            with self.subTest(case=case):
                payload = builder()
                trace = integrated.RuntimeIntegratedEventLoopTrace.from_dict(
                    payload["runtime_integrated_event_loop_trace"]
                )
                self.assertEqual(trace.integrated_trace_status, expected_status)
                self.assertEqual(trace.event_frame_count, len(payload["runtime_event_frames"]))
                self.assertEqual(trace.dispatch_count, len(payload["runtime_event_dispatch_results"]))
                self.assertEqual(
                    trace.return_payload_count,
                    len(payload["runtime_event_dispatch_return_payloads"]),
                )
                self.assertEqual(
                    trace.parent_resume_count,
                    len(payload["runtime_parent_frame_resumes"]),
                )
                self.assertTrue(trace.all_dispatches_returned)
                self.assertTrue(trace.all_child_returns_resumed)
                self.assertFalse(trace.dynamic_child_event_created)
                self.assertFalse(trace.external_execution_created)
                self.assertFalse(trace.memory_layer_write_performed)

        four_level = integrated.build_demo_four_level_integrated_dispatch_resume_trace()
        trace = integrated.RuntimeIntegratedEventLoopTrace.from_dict(
            four_level["runtime_integrated_event_loop_trace"]
        )
        self.assertEqual(trace.max_event_depth_observed, 4)
        self.assertEqual(trace.event_frame_count, 4)

    def test_integrated_loop_trace_blocks_missing_or_invalid_lineage(self) -> None:
        blocked_cases = {
            "missing_dispatch": (
                integrated.build_demo_blocked_missing_dispatch_integrated_trace,
                "integrated_event_loop_trace_blocked_missing_dispatch",
                "blocked_missing_dispatch_lineage",
            ),
            "missing_parent": (
                integrated.build_demo_blocked_missing_parent_resume_integrated_trace,
                "integrated_event_loop_trace_blocked_missing_parent_resume",
                "blocked_missing_parent_resume",
            ),
            "dynamic": (
                integrated.build_demo_blocked_dynamic_scheduling_integrated_trace,
                "integrated_event_loop_trace_blocked_forbidden_authority_detected",
                "blocked_dynamic_child_event_scheduling_detected",
            ),
            "forbidden": (
                integrated.build_demo_blocked_forbidden_authority_integrated_trace,
                "integrated_event_loop_trace_blocked_forbidden_authority_detected",
                "blocked_memory_write_detected",
            ),
        }
        for case, (builder, expected_trace, expected_audit) in blocked_cases.items():
            with self.subTest(case=case):
                payload = builder()
                trace = integrated.RuntimeIntegratedEventLoopTrace.from_dict(
                    payload["runtime_integrated_event_loop_trace"]
                )
                audit = integrated.RuntimeIntegratedEventLoopAudit.from_dict(
                    payload["runtime_integrated_event_loop_audit"]
                )
                self.assertEqual(trace.integrated_trace_status, expected_trace)
                self.assertEqual(audit.audit_status, expected_audit)

        invalid_stack = integrated.build_integrated_trace_from_demo_timeline(
            integrated.NESTED_SENSE_TIMELINE,
            force_invalid_stack=True,
        )
        self.assertEqual(
            invalid_stack["runtime_integrated_event_loop_audit"]["audit_status"],
            "blocked_invalid_stack_update",
        )
        unclosed = integrated.build_integrated_trace_from_demo_timeline(
            "....1",
            event_types_by_depth={1: "candidate_ordering"},
            force_unclosed_frame=True,
        )
        self.assertEqual(
            unclosed["runtime_integrated_event_loop_trace"]["integrated_trace_status"],
            "integrated_event_loop_trace_blocked_unclosed_frame",
        )

    def test_missing_return_payload_can_block_trace(self) -> None:
        payload = integrated.build_demo_simple_task_dispatch_resume_trace()
        frame = integrated.RuntimeEventFrameRecord.from_dict(
            payload["runtime_event_frames"][0]
        )
        request = integrated.RuntimeEventDispatchRequestRecord.from_dict(
            payload["runtime_event_dispatch_requests"][0]
        )
        route = integrated.RuntimeEventDispatchRouteRecord.from_dict(
            payload["runtime_event_dispatch_routes"][0]
        )
        result = integrated.RuntimeEventDispatchResultRecord.from_dict(
            payload["runtime_event_dispatch_results"][0]
        )
        link = integrated.build_runtime_integrated_dispatch_resume_link_record(
            event_frame=frame,
            dispatch_request=request,
            dispatch_route=route,
            dispatch_result=result,
            force_missing_return_payload=True,
        )
        trace = integrated.build_runtime_integrated_event_loop_trace(
            power_window=payload["runtime_power_window"],
            ticks=payload["runtime_ticks"],
            event_frames=payload["runtime_event_frames"],
            event_stacks=payload["runtime_event_stacks"],
            event_tree=payload["runtime_event_tree"],
            dispatch_resume_links=(link,),
            force_missing_return=True,
        )
        audit = integrated.build_runtime_integrated_event_loop_audit(
            integrated_loop_trace=trace,
            dispatch_resume_links=(link,),
        )
        self.assertEqual(
            trace.integrated_trace_status,
            "integrated_event_loop_trace_blocked_missing_return",
        )
        self.assertEqual(audit.audit_status, "blocked_missing_return_payload")

    def test_timeline_render_creates_readable_tree_and_legend(self) -> None:
        payload = integrated.build_demo_four_level_integrated_dispatch_resume_trace()
        render = integrated.RuntimeIntegratedEventLoopTimelineRenderRecord.from_dict(
            payload["runtime_integrated_event_loop_timeline_render"]
        )
        self.assertEqual(render.render_status, "timeline_render_created")
        self.assertIn("event_4 outcome_evaluation", render.human_readable_tree_text)
        for key in ("space", ".", "1", "2", "3", "4", "D", "R", "P", "S"):
            self.assertIn(key, render.legend)

        thought = integrated.build_demo_thought_deferred_integrated_trace()
        self.assertEqual(
            thought["runtime_integrated_event_loop_timeline_render"]["render_status"],
            "timeline_render_created_with_deferred_thought",
        )
        blocked = integrated.build_demo_blocked_missing_dispatch_integrated_trace()
        self.assertEqual(
            blocked["runtime_integrated_event_loop_timeline_render"]["render_status"],
            "timeline_render_blocked_invalid_trace",
        )

    def test_audit_passes_and_blocks_required_boundaries(self) -> None:
        expected = {
            "simple": (
                integrated.build_demo_simple_task_dispatch_resume_trace,
                "passed_integrated_event_loop_dispatch_resume_trace",
            ),
            "nested": (
                integrated.build_demo_nested_sense_under_task_integrated_trace,
                "passed_integrated_event_loop_dispatch_resume_trace",
            ),
            "four": (
                integrated.build_demo_four_level_integrated_dispatch_resume_trace,
                "passed_integrated_event_loop_dispatch_resume_trace",
            ),
            "thought": (
                integrated.build_demo_thought_deferred_integrated_trace,
                "passed_integrated_event_loop_with_deferred_thought",
            ),
            "power": (
                integrated.build_demo_power_off_gap_integrated_trace,
                "passed_integrated_event_loop_with_power_off_gaps",
            ),
        }
        for case, (builder, expected_status) in expected.items():
            with self.subTest(case=case):
                audit = integrated.RuntimeIntegratedEventLoopAudit.from_dict(
                    builder()["runtime_integrated_event_loop_audit"]
                )
                self.assertEqual(audit.audit_status, expected_status)
                self.assertTrue(audit.bounded_window_confirmed)
                self.assertTrue(audit.adapter_only_confirmed)
                self.assertTrue(audit.record_only_confirmed)
                self.assertTrue(audit.no_external_execution)
                self.assertTrue(audit.no_memory_layer_write)
                self.assertTrue(audit.no_thought_engine_behavior)

        base_payload = integrated.build_demo_simple_task_dispatch_resume_trace()
        trace = base_payload["runtime_integrated_event_loop_trace"]
        forced = {
            "power": ("force_invalid_power_window", "blocked_invalid_power_window"),
            "tick": ("force_invalid_tick_lineage", "blocked_invalid_tick_lineage"),
            "autonomous": (
                "force_autonomous_scheduler",
                "blocked_autonomous_scheduler_detected",
            ),
            "open": ("force_open_ended_loop", "blocked_open_ended_loop_detected"),
            "external": (
                "force_external_execution",
                "blocked_external_execution_detected",
            ),
            "memory": ("force_memory_write", "blocked_memory_write_detected"),
            "learning": (
                "force_automatic_learning_approval",
                "blocked_automatic_learning_approval_detected",
            ),
            "recursive": (
                "force_recursive_learning",
                "blocked_recursive_learning_detected",
            ),
            "thought": (
                "force_thought_engine_fake",
                "blocked_thought_engine_fake_detected",
            ),
            "production": (
                "force_production_behavior",
                "blocked_production_behavior_detected",
            ),
        }
        for case, (flag, expected_status) in forced.items():
            with self.subTest(case=case):
                audit = integrated.build_runtime_integrated_event_loop_audit(
                    integrated_loop_trace=trace,
                    **{flag: True},
                )
                self.assertEqual(audit.audit_status, expected_status)

    def test_readiness_recommends_fixed_playback_only(self) -> None:
        payload = integrated.build_demo_four_level_integrated_dispatch_resume_trace()
        readiness = integrated.RuntimeIntegratedEventLoopReadinessRecord.from_dict(
            payload["runtime_integrated_event_loop_readiness"]
        )
        self.assertEqual(
            readiness.readiness_status,
            "ready_for_fixed_runtime_playback_only",
        )
        self.assertTrue(readiness.ready_for_bounded_runtime_handler_binding)
        self.assertTrue(
            readiness.ready_for_fixed_runtime_playback_of_existing_closed_loop
        )
        self.assertFalse(readiness.ready_for_dynamic_child_event_scheduling)
        self.assertFalse(readiness.ready_for_autonomous_scheduler)
        self.assertFalse(readiness.ready_for_open_ended_loop)
        self.assertFalse(readiness.ready_for_external_execution)
        self.assertFalse(readiness.ready_for_memory_layer_write)
        self.assertFalse(readiness.ready_for_automatic_learning_approval)
        self.assertFalse(readiness.ready_for_recursive_learning)
        self.assertFalse(readiness.ready_for_thought_engine_runtime)
        self.assertFalse(readiness.ready_for_first_output)
        self.assertIn("Package 99", readiness.recommended_next_package)

    def test_record_validators_accept_demo_records(self) -> None:
        payload = integrated.build_demo_four_level_integrated_dispatch_resume_trace()
        self.assertTrue(
            integrated.validate_runtime_integrated_event_step_record(
                payload["runtime_integrated_event_steps"][0]
            )["valid"]
        )
        self.assertTrue(
            integrated.validate_runtime_integrated_dispatch_resume_link_record(
                payload["runtime_integrated_dispatch_resume_links"][0]
            )["valid"]
        )
        self.assertTrue(
            integrated.validate_runtime_integrated_event_loop_trace(
                payload["runtime_integrated_event_loop_trace"]
            )["valid"]
        )
        self.assertTrue(
            integrated.validate_runtime_integrated_event_loop_timeline_render(
                payload["runtime_integrated_event_loop_timeline_render"]
            )["valid"]
        )
        self.assertTrue(
            integrated.validate_runtime_integrated_event_loop_audit(
                payload["runtime_integrated_event_loop_audit"]
            )["valid"]
        )
        self.assertTrue(
            integrated.validate_runtime_integrated_event_loop_readiness(
                payload["runtime_integrated_event_loop_readiness"]
            )["valid"]
        )

        blocked = integrated.build_demo_blocked_dynamic_scheduling_integrated_trace()
        step = integrated.RuntimeIntegratedEventStepRecord.from_dict(
            blocked["runtime_integrated_event_steps"][-1]
        )
        if not step.dynamic_child_event_created:
            step = replace(step, dynamic_child_event_created=True)
        validation = integrated.validate_runtime_integrated_event_step_record(step)
        self.assertFalse(validation["valid"])

    def test_cli_commands_work_without_writing_state(self) -> None:
        commands = (
            ("show-demo-simple",),
            ("show-demo-nested-sense",),
            ("show-demo-four-level",),
            ("show-demo-thought-deferred",),
            ("show-demo-power-off",),
            ("show-demo-render",),
            ("show-demo-readiness",),
            ("validate-demo-integrated-loop",),
            ("audit-demo-timeline", "--timeline", ".......1(22222(333(4444)333)222222222)1"),
            ("show-demo-blocked", "--case", "missing-dispatch"),
            ("show-demo-blocked", "--case", "missing-parent-resume"),
            ("show-demo-blocked", "--case", "dynamic-scheduling"),
            ("show-demo-blocked", "--case", "forbidden-authority"),
        )
        for command in commands:
            with self.subTest(command=command):
                payload = self._run_json_module(INTEGRATED_CLI, *command)
                self.assertIsInstance(payload, dict)

    def test_guided_console_integrated_loop_commands_work(self) -> None:
        validation = validate_integrated_event_loop_demo_from_guided_cradle_growth_console()
        self.assertEqual(
            validation["validation"]["audit_status"],
            "passed_integrated_event_loop_dispatch_resume_trace",
        )
        commands = (
            "runtime-show-integrated-loop-simple-demo",
            "runtime-show-integrated-loop-nested-sense-demo",
            "runtime-show-integrated-loop-four-level-demo",
            "runtime-show-integrated-loop-thought-deferred-demo",
            "runtime-show-integrated-loop-render-demo",
            "runtime-show-integrated-loop-readiness-demo",
            "runtime-validate-integrated-event-loop-demo",
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

    def test_no_repo_data_directory_created(self) -> None:
        self.assertFalse(Path("ashl_core_v1/data").exists())

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
