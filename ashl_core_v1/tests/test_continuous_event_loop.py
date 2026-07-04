from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from ashl_core_v1.runtime import continuous_event_loop as loop
from ashl_core_v1.runtime.guided_cradle_growth_teacher_console import (
    validate_continuous_event_loop_demo_from_guided_cradle_growth_console,
)


LOOP_CLI = "ashl_core_v1.runtime.continuous_event_loop_cli"
GUIDED_CLI = "ashl_core_v1.runtime.guided_cradle_growth_teacher_console_cli"


class RuntimeContinuousEventLoopTests(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = loop.build_demo_nested_event_continuous_loop()
        self.power_window = loop.RuntimePowerWindowRecord.from_dict(
            self.payload["runtime_power_window"]
        )
        self.ticks = tuple(
            loop.RuntimeTickRecord.from_dict(item)
            for item in self.payload["runtime_ticks"]
        )
        self.frames = tuple(
            loop.RuntimeEventFrameRecord.from_dict(item)
            for item in self.payload["runtime_event_frames"]
        )
        self.stacks = tuple(
            loop.RuntimeEventStackRecord.from_dict(item)
            for item in self.payload["runtime_event_stacks"]
        )
        self.returns = tuple(
            loop.RuntimeEventReturnRecord.from_dict(item)
            for item in self.payload["runtime_event_returns"]
        )
        self.tree = loop.RuntimeEventTreeRecord.from_dict(
            self.payload["runtime_event_tree"]
        )
        self.trace = loop.RuntimeContinuousLoopTrace.from_dict(
            self.payload["runtime_continuous_loop_trace"]
        )
        self.audit = loop.RuntimeContinuousLoopAudit.from_dict(
            self.payload["runtime_continuous_loop_audit"]
        )

    def test_parser_accepts_idle_power_off_and_nested_symbols(self) -> None:
        self.assertEqual(loop.parse_runtime_timeline_symbols("  .."), (" ", " ", ".", "."))
        self.assertEqual(
            "".join(loop.parse_runtime_timeline_symbols(loop.NESTED_DEMO_TIMELINE)),
            ".......12222233344443332222222221",
        )
        self.assertEqual(loop.normalize_runtime_timeline_text("1(22)1"), "1221")

    def test_parser_rejects_invalid_depth_and_unbounded_requests(self) -> None:
        cases = {
            "@": "invalid_timeline_symbol",
            ".13": "event_depth_jump_without_parent",
            "2": "event_depth_started_without_parent",
            "12345": "max_depth_exceeded",
            "while true": "unbounded_loop_requested",
        }
        for timeline, expected in cases.items():
            with self.subTest(timeline=timeline):
                with self.assertRaisesRegex(ValueError, expected):
                    loop.parse_runtime_timeline_symbols(timeline)

    def test_power_window_distinguishes_power_on_and_power_off(self) -> None:
        power_off = loop.build_runtime_power_window_record(timeline_text="   .....   ")
        self.assertEqual(power_off.power_state, "mixed_power_window")
        self.assertEqual(power_off.power_off_spans_observed, 6)
        self.assertEqual(power_off.window_status, "power_window_valid")
        blocked = loop.build_runtime_power_window_record(
            timeline_text=" .",
            tick_created_during_power_off=True,
        )
        self.assertEqual(
            blocked.window_status,
            "power_window_blocked_tick_during_power_off",
        )

    def test_power_window_blocks_scheduler_and_unbounded_authority(self) -> None:
        scheduler = loop.build_runtime_power_window_record(
            timeline_text=".",
            autonomous_scheduler_created=True,
        )
        unbounded = loop.build_runtime_power_window_record(
            timeline_text="while true",
            unbounded=True,
        )
        self.assertEqual(
            scheduler.window_status,
            "power_window_blocked_scheduler_detected",
        )
        self.assertEqual(unbounded.window_status, "power_window_blocked_unbounded")

    def test_idle_ticks_record_empty_event_stack_without_side_effects(self) -> None:
        idle = loop.build_demo_idle_only_continuous_loop()
        ticks = [
            loop.RuntimeTickRecord.from_dict(item)
            for item in idle["runtime_ticks"]
        ]
        self.assertTrue(ticks)
        self.assertTrue(all(tick.tick_kind == "idle_heartbeat" for tick in ticks))
        self.assertTrue(all(tick.event_stack_snapshot == () for tick in ticks))
        self.assertTrue(all(not tick.memory_write_performed for tick in ticks))
        self.assertTrue(all(not tick.external_execution_created for tick in ticks))
        self.assertTrue(
            all(not tick.automatic_learning_approval_created for tick in ticks)
        )

    def test_event_frames_capture_nested_parent_child_lineage(self) -> None:
        self.assertEqual(tuple(frame.event_depth for frame in self.frames), (1, 2, 3, 4))
        self.assertEqual(self.frames[0].parent_event_frame_id, None)
        for parent, child in zip(self.frames, self.frames[1:]):
            self.assertEqual(child.parent_event_frame_id, parent.event_frame_id)
            self.assertIn(child.event_frame_id, parent.child_event_frame_ids)
        self.assertTrue(
            all(frame.event_status == "event_closed_returned" for frame in self.frames)
        )

    def test_event_frames_block_budget_child_scope_unclosed_and_authority(self) -> None:
        cases = (
            (
                {"event_budget_ticks": 1, "force_budget_exceeded": True},
                "event_blocked_budget_exceeded",
            ),
            ({"force_child_scope_expansion": True}, "event_blocked_child_scope_expansion"),
            ({"leave_unclosed_at_end": True}, "event_blocked_unclosed_at_window_end"),
            (
                {"force_forbidden_authority": True},
                "event_blocked_forbidden_authority_detected",
            ),
        )
        for kwargs, expected_status in cases:
            with self.subTest(expected_status=expected_status):
                frames = loop.build_runtime_event_frames_from_timeline(
                    power_window=self.power_window,
                    **kwargs,
                )
                self.assertIn(expected_status, {frame.event_status for frame in frames})

    def test_event_stack_records_idle_empty_and_nested_stack_depths(self) -> None:
        self.assertIn("stack_empty_idle", {stack.stack_status for stack in self.stacks})
        self.assertIn("stack_valid", {stack.stack_status for stack in self.stacks})
        self.assertEqual(max(stack.max_depth_observed for stack in self.stacks), 4)
        blocked = loop.build_runtime_event_stack_records(
            power_window=self.power_window,
            invalid_parent_child_order_detected=True,
        )
        self.assertIn(
            "stack_blocked_invalid_parent_child_order",
            {stack.stack_status for stack in blocked},
        )
        overflow = loop.build_runtime_event_stack_records(
            power_window=self.power_window,
            max_depth=3,
        )
        self.assertIn(
            "stack_blocked_max_depth_exceeded",
            {stack.stack_status for stack in overflow},
        )

    def test_event_return_records_close_children_and_resume_parents(self) -> None:
        self.assertEqual(len(self.returns), 4)
        self.assertTrue(all(item.return_status == "returned_success" for item in self.returns))
        child_returns = [item for item in self.returns if item.parent_event_frame_id]
        self.assertTrue(child_returns)
        self.assertTrue(all(item.parent_resumed for item in child_returns))
        root_return = [item for item in self.returns if item.parent_event_frame_id is None]
        self.assertEqual(len(root_return), 1)
        self.assertFalse(root_return[0].parent_resumed)

    def test_event_return_records_block_scope_mutation_and_forbidden_authority(self) -> None:
        scoped = loop.build_runtime_event_return_records(
            power_window=self.power_window,
            return_scope_changed_parent=True,
        )
        self.assertEqual(
            {item.return_status for item in scoped},
            {"blocked_scope_mutation_detected"},
        )
        self.assertEqual({item.return_payload["status"] for item in scoped}, {"returned_blocked"})
        authority = loop.build_runtime_event_return_records(
            power_window=self.power_window,
            force_forbidden_authority=True,
        )
        self.assertEqual(
            {item.return_status for item in authority},
            {"blocked_forbidden_authority_detected"},
        )
        self.assertTrue(all(item.external_execution_created for item in authority))

    def test_event_tree_records_all_frames_and_blocks_missing_return_or_growth(self) -> None:
        self.assertEqual(self.tree.tree_status, "tree_valid_all_frames_closed")
        self.assertEqual(self.tree.tree_frame_count, 4)
        self.assertEqual(self.tree.tree_depth_max, 4)
        missing = loop.build_runtime_event_tree_record(
            power_window=self.power_window,
            event_frames=self.frames,
            event_returns=self.returns,
            force_missing_return=True,
        )
        growth = loop.build_runtime_event_tree_record(
            power_window=self.power_window,
            event_frames=self.frames,
            event_returns=self.returns,
            force_unbounded_growth=True,
        )
        self.assertEqual(missing.tree_status, "tree_blocked_missing_return")
        self.assertEqual(growth.tree_status, "tree_blocked_unbounded_growth")

    def test_continuous_loop_trace_counts_ticks_depth_and_power_off_gaps(self) -> None:
        self.assertEqual(self.trace.loop_trace_status, "loop_trace_valid")
        self.assertEqual(self.trace.idle_tick_count, 7)
        self.assertEqual(self.trace.event_tick_count, 26)
        self.assertEqual(self.trace.max_event_depth_observed, 4)
        self.assertFalse(self.trace.continuous_loop_interrupted)
        power_off = loop.build_demo_power_off_gap_continuous_loop()
        self.assertEqual(
            power_off["runtime_continuous_loop_trace"]["loop_trace_status"],
            "loop_trace_valid_with_power_off_gaps",
        )

    def test_loop_audit_passes_nested_idle_and_power_off_demos(self) -> None:
        self.assertEqual(
            self.audit.audit_status,
            "passed_continuous_event_loop_nested_frame_demo",
        )
        self.assertEqual(
            loop.build_demo_idle_only_continuous_loop()["runtime_continuous_loop_audit"][
                "audit_status"
            ],
            "passed_idle_only_loop_demo",
        )
        self.assertEqual(
            loop.build_demo_power_off_gap_continuous_loop()["runtime_continuous_loop_audit"][
                "audit_status"
            ],
            "passed_power_off_gap_respected",
        )
        self.assertTrue(self.audit.no_autonomous_scheduler)
        self.assertTrue(self.audit.no_open_ended_loop)
        self.assertTrue(self.audit.no_memory_layer_write)

    def test_loop_audit_blocks_required_demo_cases(self) -> None:
        cases = {
            "invalid-depth-jump": "blocked_invalid_event_stack",
            "power-off-tick": "blocked_power_off_tick_detected",
            "unbounded-loop": "blocked_unbounded_loop",
            "forbidden-authority": "blocked_external_execution_detected",
        }
        for case, expected_status in cases.items():
            with self.subTest(case=case):
                payload = loop.build_demo_blocked_continuous_loop(case)
                self.assertEqual(
                    payload["runtime_continuous_loop_audit"]["audit_status"],
                    expected_status,
                )
                self.assertTrue(
                    payload["runtime_continuous_loop_audit"]["blocked_reasons"]
                )

    def test_loop_audit_blocks_scheduler_open_ended_and_memory_authority(self) -> None:
        for kwargs, expected_status in (
            ({"autonomous_scheduler_created": True}, "blocked_autonomous_scheduler_detected"),
            ({"open_ended_loop_created": True}, "blocked_open_ended_loop_detected"),
            ({"memory_layer_write_performed": True}, "blocked_memory_write_detected"),
            (
                {"automatic_learning_approval_created": True},
                "blocked_automatic_learning_approval_detected",
            ),
            ({"recursive_learning_created": True}, "blocked_recursive_learning_detected"),
            ({"production_behavior_created": True}, "blocked_production_behavior_detected"),
        ):
            with self.subTest(expected_status=expected_status):
                audit = loop.build_runtime_continuous_loop_audit(
                    loop_trace=self.trace,
                    event_tree=self.tree,
                    ticks=self.ticks,
                    event_frames=self.frames,
                    event_stacks=self.stacks,
                    event_returns=self.returns,
                    **kwargs,
                )
                self.assertEqual(audit.audit_status, expected_status)

    def test_record_validators_accept_demo_records(self) -> None:
        self.assertTrue(loop.validate_runtime_power_window_record(self.power_window)["valid"])
        self.assertTrue(all(loop.validate_runtime_tick_record(tick)["valid"] for tick in self.ticks))
        self.assertTrue(
            all(loop.validate_runtime_event_frame_record(frame)["valid"] for frame in self.frames)
        )
        self.assertTrue(
            all(loop.validate_runtime_event_stack_record(stack)["valid"] for stack in self.stacks)
        )
        self.assertTrue(
            all(loop.validate_runtime_event_return_record(item)["valid"] for item in self.returns)
        )
        self.assertTrue(loop.validate_runtime_event_tree_record(self.tree)["valid"])
        self.assertTrue(loop.validate_runtime_continuous_loop_trace(self.trace)["valid"])
        self.assertTrue(loop.validate_runtime_continuous_loop_audit(self.audit)["valid"])

    def test_render_helpers_return_timeline_and_tree_summary(self) -> None:
        self.assertEqual(
            loop.render_runtime_timeline_from_trace(self.trace),
            ".......12222233344443332222222221",
        )
        self.assertIn("depth=4", loop.render_event_tree_text(self.tree))

    def test_cli_commands_work_without_writing_state(self) -> None:
        commands = (
            ("show-demo-idle",),
            ("show-demo-power-off",),
            ("show-demo-nested",),
            ("show-demo-event-tree",),
            ("validate-demo-loop",),
            ("parse-timeline", "--timeline", "..1"),
            ("audit-timeline", "--timeline", loop.NESTED_DEMO_TIMELINE),
            ("show-demo-blocked", "--case", "invalid-depth-jump"),
            ("show-demo-blocked", "--case", "power-off-tick"),
            ("show-demo-blocked", "--case", "unbounded-loop"),
            ("show-demo-blocked", "--case", "forbidden-authority"),
        )
        for command in commands:
            with self.subTest(command=command):
                payload = self._run_json_module(LOOP_CLI, *command)
                self.assertIsInstance(payload, dict)

    def test_guided_console_commands_work_without_runtime_authority(self) -> None:
        validation = validate_continuous_event_loop_demo_from_guided_cradle_growth_console()
        self.assertEqual(
            validation["validation"]["audit_status"],
            "passed_continuous_event_loop_nested_frame_demo",
        )
        self.assertFalse(validation["background_process_started"])
        commands = (
            "runtime-show-continuous-loop-idle-demo",
            "runtime-show-continuous-loop-power-off-demo",
            "runtime-show-continuous-loop-nested-demo",
            "runtime-show-continuous-loop-event-tree-demo",
            "runtime-validate-continuous-event-loop-demo",
            "runtime-audit-continuous-event-loop-timeline",
        )
        for command in commands:
            with self.subTest(command=command):
                payload = self._run_json_module(GUIDED_CLI, command)
                self.assertFalse(payload["background_process_started"])
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
