from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from ashl_core_v1.runtime import event_frame_dispatch_adapter as adapter
from ashl_core_v1.runtime.guided_cradle_growth_teacher_console import (
    validate_event_dispatch_demo_from_guided_cradle_growth_console,
)


DISPATCH_CLI = "ashl_core_v1.runtime.event_frame_dispatch_adapter_cli"
GUIDED_CLI = "ashl_core_v1.runtime.guided_cradle_growth_teacher_console_cli"


class RuntimeEventFrameDispatchAdapterTests(unittest.TestCase):
    def test_classifies_supported_event_types(self) -> None:
        cases = {
            "candidate_ordering": "task_event",
            "selected_action_application": "task_event",
            "sandbox_execution": "task_event",
            "sense_observation": "sense_event",
            "sense_handoff": "sense_event",
            "learning_feedback_intake": "learning_event",
            "concept_candidate_review": "learning_event",
            "reviewed_concept_creation": "learning_event",
            "memory_readback": "memory_event",
            "working_readback_integration": "memory_event",
            "state_snapshot_request": "state_event",
            "output_candidate": "output_event",
            "thought_preview": "thought_event",
            "loop_audit": "audit_event",
            "summon_dragon": "unknown_event",
        }
        for event_type, expected_family in cases.items():
            with self.subTest(event_type=event_type):
                self.assertEqual(
                    adapter.classify_runtime_event_type(event_type),
                    expected_family,
                )

    def test_dispatch_request_builds_and_blocks_invalid_or_forbidden_inputs(self) -> None:
        valid = adapter.build_runtime_event_dispatch_request(
            adapter._demo_event_frame("candidate_ordering")
        )
        self.assertEqual(valid.dispatch_request_status, "dispatch_request_created")

        invalid = adapter.build_runtime_event_dispatch_request({})
        self.assertEqual(invalid.dispatch_request_status, "blocked_invalid_event_frame")

        unknown = adapter.build_runtime_event_dispatch_request(
            adapter._demo_event_frame("summon_dragon")
        )
        self.assertEqual(unknown.dispatch_request_status, "blocked_unknown_event_type")

        blocked_flags = {
            "external_execution_requested": True,
            "memory_layer_write_requested": True,
            "automatic_learning_approval_requested": True,
            "recursive_learning_requested": True,
            "production_behavior_requested": True,
        }
        for flag in blocked_flags:
            with self.subTest(flag=flag):
                request = adapter.build_runtime_event_dispatch_request(
                    adapter._demo_event_frame("candidate_ordering"),
                    event_payload={flag: True},
                )
                self.assertEqual(
                    request.dispatch_request_status,
                    "blocked_forbidden_authority_requested",
                )

        unbounded = adapter.build_runtime_event_dispatch_request(
            adapter._demo_event_frame("candidate_ordering"),
            max_event_budget_ticks=0,
        )
        self.assertEqual(unbounded.dispatch_request_status, "blocked_unbounded_budget")

    def test_routes_each_supported_lane_without_granting_authority(self) -> None:
        cases = {
            "candidate_ordering": ("task_engine", "routed_to_task_engine"),
            "sense_observation": ("sense_interface", "routed_to_sense_interface"),
            "learning_feedback_intake": ("learning_engine", "routed_to_learning_engine"),
            "memory_readback": ("memory_engine", "routed_to_memory_engine"),
            "state_snapshot_request": ("state_engine", "routed_to_state_engine"),
            "output_candidate": ("output_interface", "routed_to_output_interface"),
            "loop_audit": ("audit_layer", "routed_to_audit_layer"),
        }
        for event_type, (target, status) in cases.items():
            with self.subTest(event_type=event_type):
                route = self._route_for(event_type)
                self.assertEqual(route.target_engine, target)
                self.assertEqual(route.route_status, status)
                self.assertTrue(route.route_is_adapter_only)
                self.assertFalse(route.route_invokes_engine_runtime)
                self.assertFalse(route.external_execution_allowed)
                self.assertFalse(route.memory_layer_write_allowed)
                self.assertFalse(route.automatic_learning_approval_allowed)
                self.assertFalse(route.free_action_selection_allowed)

    def test_routes_thought_deferred_and_unknown_blocked(self) -> None:
        thought_route = self._route_for("thought_preview")
        self.assertEqual(thought_route.target_engine, "thought_engine")
        self.assertFalse(thought_route.handler_available)
        self.assertEqual(
            thought_route.route_status,
            "deferred_thought_engine_not_available",
        )

        unknown_route = self._route_for("summon_dragon")
        self.assertEqual(unknown_route.target_engine, "none")
        self.assertEqual(unknown_route.route_status, "blocked_unknown_event_type")

    def test_handler_adapter_created_or_deferred_without_side_effects(self) -> None:
        cases = {
            "candidate_ordering": "task_engine_adapter",
            "sense_observation": "sense_interface_adapter",
            "learning_feedback_intake": "learning_engine_adapter",
            "memory_readback": "memory_engine_adapter",
            "state_snapshot_request": "state_engine_adapter",
            "output_candidate": "output_interface_adapter",
            "loop_audit": "audit_layer_adapter",
            "thought_preview": "thought_engine_deferred_adapter",
            "summon_dragon": "blocked_unknown_adapter",
        }
        for event_type, expected_kind in cases.items():
            with self.subTest(event_type=event_type):
                adapter_record = adapter.build_runtime_event_handler_adapter(
                    self._route_for(event_type)
                )
                self.assertEqual(adapter_record.adapter_kind, expected_kind)
                self.assertFalse(adapter_record.handler_invoked)
                self.assertTrue(adapter_record.adapter_record_only)
                self.assertFalse(adapter_record.created_thought_record)
                self.assertFalse(adapter_record.external_execution_created)
                self.assertFalse(adapter_record.memory_layer_write_performed)
                self.assertFalse(adapter_record.recursive_learning_created)

    def test_dispatch_result_and_return_payload_statuses(self) -> None:
        expected = {
            "candidate_ordering": (
                "dispatch_completed_adapter_only",
                "returned_success",
            ),
            "sense_observation": (
                "dispatch_completed_adapter_only",
                "returned_success",
            ),
            "learning_feedback_intake": (
                "dispatch_completed_adapter_only",
                "returned_success",
            ),
            "memory_readback": (
                "dispatch_completed_adapter_only",
                "returned_success",
            ),
            "state_snapshot_request": (
                "dispatch_completed_adapter_only",
                "returned_success",
            ),
            "output_candidate": (
                "dispatch_completed_adapter_only",
                "returned_success",
            ),
            "thought_preview": (
                "dispatch_deferred_engine_not_available",
                "returned_deferred",
            ),
            "summon_dragon": (
                "dispatch_blocked_unknown_event_type",
                "returned_blocked",
            ),
        }
        for event_type, (result_status, return_status) in expected.items():
            with self.subTest(event_type=event_type):
                payload = adapter.dispatch_event_frame_adapter_only(
                    adapter._demo_event_frame(event_type)
                )
                result = adapter.RuntimeEventDispatchResultRecord.from_dict(
                    payload["runtime_event_dispatch_result"]
                )
                return_payload = (
                    adapter.RuntimeEventDispatchReturnPayloadRecord.from_dict(
                        payload["runtime_event_dispatch_return_payload"]
                    )
                )
                self.assertEqual(result.dispatch_result_status, result_status)
                self.assertTrue(result.return_payload_required)
                self.assertEqual(return_payload.return_status, return_status)
                self.assertTrue(return_payload.safe_for_parent_resume)
                self.assertFalse(return_payload.creates_new_event)

    def test_audit_passes_deferred_and_blocks_forbidden_or_unknown_cases(self) -> None:
        cases = {
            "candidate_ordering": "passed_event_dispatch_adapter_only",
            "sense_observation": "passed_event_dispatch_adapter_only",
            "learning_feedback_intake": "passed_event_dispatch_adapter_only",
            "memory_readback": "passed_event_dispatch_adapter_only",
            "state_snapshot_request": "passed_event_dispatch_adapter_only",
            "output_candidate": "passed_event_dispatch_adapter_only",
            "thought_preview": "passed_thought_engine_deferred",
            "summon_dragon": "blocked_unknown_event_type",
        }
        for event_type, expected_status in cases.items():
            with self.subTest(event_type=event_type):
                payload = adapter.dispatch_event_frame_adapter_only(
                    adapter._demo_event_frame(event_type)
                )
                audit = adapter.RuntimeEventDispatchAudit.from_dict(
                    payload["runtime_event_dispatch_audit"]
                )
                self.assertEqual(audit.audit_status, expected_status)
                self.assertTrue(audit.no_autonomous_scheduler)
                self.assertTrue(audit.no_open_ended_loop)
                self.assertTrue(audit.no_external_execution)
                self.assertTrue(audit.no_memory_layer_write)
                self.assertTrue(audit.no_automatic_learning_approval)
                self.assertTrue(audit.no_recursive_learning)
                self.assertTrue(audit.no_thought_engine_faked)

        forbidden_payload = adapter.build_demo_forbidden_authority_blocked_dispatch()
        forbidden_audit = adapter.RuntimeEventDispatchAudit.from_dict(
            forbidden_payload["runtime_event_dispatch_audit"]
        )
        self.assertEqual(
            forbidden_audit.audit_status,
            "blocked_external_execution_detected",
        )
        self.assertFalse(forbidden_audit.no_external_execution)

        forbidden_flags = (
            ("memory_layer_write_requested", "blocked_memory_write_detected"),
            (
                "automatic_learning_approval_requested",
                "blocked_automatic_learning_approval_detected",
            ),
            ("free_action_selection_requested", "blocked_free_action_selection_detected"),
            ("recursive_learning_requested", "blocked_recursive_learning_detected"),
            ("production_behavior_requested", "blocked_production_behavior_detected"),
        )
        for flag, expected_status in forbidden_flags:
            with self.subTest(flag=flag):
                payload = adapter.dispatch_event_frame_adapter_only(
                    adapter._demo_event_frame("candidate_ordering"),
                    event_payload={flag: True},
                )
                audit = adapter.RuntimeEventDispatchAudit.from_dict(
                    payload["runtime_event_dispatch_audit"]
                )
                self.assertEqual(audit.audit_status, expected_status)

    def test_record_validators_accept_demo_records(self) -> None:
        payload = adapter.build_demo_task_event_dispatch()
        self.assertTrue(
            adapter.validate_runtime_event_dispatch_request(
                payload["runtime_event_dispatch_request"]
            )["valid"]
        )
        self.assertTrue(
            adapter.validate_runtime_event_dispatch_route(
                payload["runtime_event_dispatch_route"]
            )["valid"]
        )
        self.assertTrue(
            adapter.validate_runtime_event_handler_adapter(
                payload["runtime_event_handler_adapter"]
            )["valid"]
        )
        self.assertTrue(
            adapter.validate_runtime_event_dispatch_result(
                payload["runtime_event_dispatch_result"]
            )["valid"]
        )
        self.assertTrue(
            adapter.validate_runtime_event_dispatch_return_payload(
                payload["runtime_event_dispatch_return_payload"]
            )["valid"]
        )
        self.assertTrue(
            adapter.validate_runtime_event_dispatch_audit(
                payload["runtime_event_dispatch_audit"]
            )["valid"]
        )

    def test_cli_commands_work_without_writing_state(self) -> None:
        commands = (
            ("show-demo-task",),
            ("show-demo-sense",),
            ("show-demo-learning",),
            ("show-demo-memory",),
            ("show-demo-state",),
            ("show-demo-output",),
            ("show-demo-thought-deferred",),
            ("show-demo-unknown-blocked",),
            ("show-demo-forbidden-authority-blocked",),
            ("classify-event", "--event-type", "sense_observation"),
            ("dispatch-demo-event", "--event-type", "candidate_ordering"),
            ("validate-demo-dispatch",),
        )
        for command in commands:
            with self.subTest(command=command):
                payload = self._run_json_module(DISPATCH_CLI, *command)
                self.assertIsInstance(payload, dict)

    def test_guided_console_event_dispatch_commands_work(self) -> None:
        validation = validate_event_dispatch_demo_from_guided_cradle_growth_console()
        self.assertEqual(
            validation["validation"]["audit_status"],
            "passed_event_dispatch_adapter_only",
        )
        commands = (
            "runtime-show-event-dispatch-task-demo",
            "runtime-show-event-dispatch-sense-demo",
            "runtime-show-event-dispatch-learning-demo",
            "runtime-show-event-dispatch-memory-demo",
            "runtime-show-event-dispatch-state-demo",
            "runtime-show-event-dispatch-output-demo",
            "runtime-show-event-dispatch-thought-deferred-demo",
            "runtime-validate-event-dispatch-demo",
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

    def _route_for(self, event_type: str) -> adapter.RuntimeEventDispatchRouteRecord:
        request = adapter.build_runtime_event_dispatch_request(
            adapter._demo_event_frame(event_type)
        )
        return adapter.build_runtime_event_dispatch_route(request)

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
