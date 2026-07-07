from __future__ import annotations

import json
import subprocess
import sys
import unittest
from dataclasses import replace
from pathlib import Path

from ashl_core_v1.runtime import event_return_parent_resume as resume
from ashl_core_v1.runtime.guided_cradle_growth_teacher_console import (
    validate_parent_frame_resume_demo_from_guided_cradle_growth_console,
)


RESUME_CLI = "ashl_core_v1.runtime.event_return_parent_resume_cli"
GUIDED_CLI = "ashl_core_v1.runtime.guided_cradle_growth_teacher_console_cli"


class RuntimeEventReturnParentResumeTests(unittest.TestCase):
    def test_resume_request_builds_and_blocks_invalid_inputs(self) -> None:
        parent, child = resume._demo_parent_child_frames("request")
        request = resume.build_runtime_parent_frame_resume_request(
            child,
            parent_event_frame=parent,
            dispatch_return_payload=resume._demo_dispatch_return_payload(
                child,
                "returned_success",
            ),
        )
        self.assertEqual(
            request.parent_resume_request_status,
            "parent_resume_request_created",
        )

        missing_parent_child = resume._demo_event_frame(
            event_frame_id="runtime_event_frame:test:missing_parent",
            event_depth=2,
            parent_event_frame_id=None,
            event_type="child_event",
        )
        missing = resume.build_runtime_parent_frame_resume_request(
            missing_parent_child,
            dispatch_return_payload=resume._demo_dispatch_return_payload(
                missing_parent_child,
                "returned_success",
            ),
        )
        self.assertEqual(
            missing.parent_resume_request_status,
            "blocked_missing_parent_frame",
        )

        root = resume._demo_event_frame(
            event_frame_id="runtime_event_frame:test:root",
            event_depth=1,
            parent_event_frame_id=None,
            event_type="root_event",
        )
        root_request = resume.build_runtime_parent_frame_resume_request(
            root,
            dispatch_return_payload=resume._demo_dispatch_return_payload(
                root,
                "returned_success",
            ),
        )
        self.assertEqual(
            root_request.parent_resume_request_status,
            "parent_resume_request_created",
        )

        invalid = resume.build_runtime_parent_frame_resume_request(
            child,
            parent_event_frame=parent,
            dispatch_return_payload=resume._demo_dispatch_return_payload(
                child,
                "blocked_forbidden_authority_detected",
            ),
        )
        self.assertEqual(
            invalid.parent_resume_request_status,
            "blocked_invalid_child_return",
        )

        blocked_flags = {
            "scope_expansion_requested": "blocked_scope_expansion_requested",
            "budget_extension_requested": "blocked_budget_extension_requested",
            "new_child_event_requested": "blocked_new_child_event_requested",
            "external_execution_requested": "blocked_forbidden_authority_requested",
            "memory_layer_write_requested": "blocked_forbidden_authority_requested",
            "automatic_learning_approval_requested": (
                "blocked_forbidden_authority_requested"
            ),
            "recursive_learning_requested": "blocked_forbidden_authority_requested",
            "production_behavior_requested": "blocked_forbidden_authority_requested",
        }
        for flag, expected_status in blocked_flags.items():
            with self.subTest(flag=flag):
                blocked = resume.build_runtime_parent_frame_resume_request(
                    child,
                    parent_event_frame=parent,
                    dispatch_return_payload=resume._demo_dispatch_return_payload(
                        child,
                        "returned_success",
                    ),
                    request_payload={flag: True},
                )
                self.assertEqual(blocked.parent_resume_request_status, expected_status)

    def test_resume_decision_maps_child_return_statuses(self) -> None:
        cases = {
            "returned_success": "resume_continue_parent",
            "returned_blocked": "resume_continue_parent_with_child_blocked",
            "returned_unknown": "resume_defer_parent",
            "returned_deferred": "resume_defer_parent",
            "returned_fault": "resume_fault_parent",
        }
        for return_status, expected_decision in cases.items():
            with self.subTest(return_status=return_status):
                parent, child = resume._demo_parent_child_frames(return_status)
                request = resume.build_runtime_parent_frame_resume_request(
                    child,
                    parent_event_frame=parent,
                    dispatch_return_payload=resume._demo_dispatch_return_payload(
                        child,
                        return_status,
                    ),
                )
                decision = resume.build_runtime_parent_frame_resume_decision(
                    request,
                    parent_event_frame=parent,
                )
                self.assertEqual(decision.resume_decision, expected_decision)
                self.assertTrue(decision.parent_scope_preserved)
                self.assertTrue(decision.parent_budget_preserved)
                self.assertFalse(decision.new_child_event_creation_allowed)
                self.assertFalse(decision.free_action_selection_allowed)
                self.assertFalse(decision.external_execution_allowed)
                self.assertFalse(decision.memory_layer_write_allowed)
                self.assertFalse(decision.automatic_learning_approval_allowed)

        parent, child = resume._demo_parent_child_frames("budget_exhausted")
        exhausted_parent = replace(parent, event_budget_ticks=1, event_ticks_used=1)
        request = resume.build_runtime_parent_frame_resume_request(
            child,
            parent_event_frame=exhausted_parent,
            dispatch_return_payload=resume._demo_dispatch_return_payload(
                child,
                "returned_success",
            ),
        )
        decision = resume.build_runtime_parent_frame_resume_decision(
            request,
            parent_event_frame=exhausted_parent,
        )
        self.assertEqual(decision.resume_decision, "blocked_parent_budget_exhausted")

    def test_resume_record_reflects_decision_without_side_effects(self) -> None:
        expected = {
            "returned_success": "parent_resumed_continue",
            "returned_blocked": "parent_resumed_continue_with_child_blocked",
            "returned_unknown": "parent_deferred_after_child_return",
            "returned_fault": "parent_faulted_after_child_return",
        }
        for return_status, expected_resume_status in expected.items():
            with self.subTest(return_status=return_status):
                payload = self._resume_payload(return_status)
                record = resume.RuntimeParentFrameResumeRecord.from_dict(
                    payload["runtime_parent_frame_resume"]
                )
                self.assertEqual(record.resume_status, expected_resume_status)
                self.assertTrue(record.child_return_status_consumed)
                self.assertTrue(record.child_return_payload_attached)
                self.assertFalse(record.new_child_event_created)
                self.assertFalse(record.dynamic_scheduling_created)
                self.assertFalse(record.memory_layer_write_performed)
                self.assertFalse(record.external_execution_created)

        parent, child = resume._demo_parent_child_frames("close")
        request = resume.build_runtime_parent_frame_resume_request(
            child,
            parent_event_frame=parent,
            dispatch_return_payload=resume._demo_dispatch_return_payload(
                child,
                "returned_success",
            ),
        )
        decision = resume.build_runtime_parent_frame_resume_decision(
            request,
            parent_event_frame=parent,
            close_parent_after_success=True,
        )
        record = resume.build_runtime_parent_frame_resume_record(
            request,
            decision,
            parent_event_frame=parent,
        )
        self.assertEqual(record.resume_status, "parent_closed_after_child_return")

        root = resume._demo_event_frame(
            event_frame_id="runtime_event_frame:test:root_close",
            event_depth=1,
            parent_event_frame_id=None,
            event_type="root_event",
        )
        root_payload = resume.resume_parent_frame_from_child_return(
            root,
            dispatch_return_payload=resume._demo_dispatch_return_payload(
                root,
                "returned_success",
            ),
            stack_before_resume=(root.event_frame_id,),
        )
        root_record = resume.RuntimeParentFrameResumeRecord.from_dict(
            root_payload["runtime_parent_frame_resume"]
        )
        self.assertEqual(root_record.resume_status, "root_event_closed")

    def test_stack_update_pops_child_and_blocks_invalid_stack_cases(self) -> None:
        payload = self._resume_payload("returned_success")
        update = resume.RuntimeParentFrameResumeStackUpdateRecord.from_dict(
            payload["runtime_parent_frame_resume_stack_update"]
        )
        self.assertTrue(update.child_frame_popped)
        self.assertTrue(update.parent_frame_on_top_after_pop)
        self.assertTrue(update.parent_frame_resumed_on_stack)
        self.assertEqual(update.stack_update_status, "stack_updated_parent_resumed")

        root = resume._demo_event_frame(
            event_frame_id="runtime_event_frame:test:root_stack",
            event_depth=1,
            parent_event_frame_id=None,
            event_type="root_event",
        )
        root_payload = resume.resume_parent_frame_from_child_return(
            root,
            dispatch_return_payload=resume._demo_dispatch_return_payload(
                root,
                "returned_success",
            ),
            stack_before_resume=(root.event_frame_id,),
        )
        root_update = resume.RuntimeParentFrameResumeStackUpdateRecord.from_dict(
            root_payload["runtime_parent_frame_resume_stack_update"]
        )
        self.assertEqual(root_update.stack_update_status, "stack_updated_root_closed")
        self.assertEqual(root_update.stack_after_parent_resume, ())

        record = resume.RuntimeParentFrameResumeRecord.from_dict(
            payload["runtime_parent_frame_resume"]
        )
        forced_cases = {
            "invalid": {
                "force_invalid_parent_child_order": True,
                "expected": "blocked_invalid_parent_child_order",
            },
            "unclosed": {
                "force_unclosed_child_frame": True,
                "expected": "blocked_unclosed_child_frame",
            },
            "underflow": {
                "force_stack_underflow": True,
                "stack_before_resume": (),
                "expected": "blocked_stack_underflow",
            },
            "overflow": {
                "force_stack_overflow": True,
                "expected": "blocked_stack_overflow",
            },
        }
        for case, data in forced_cases.items():
            with self.subTest(case=case):
                expected_status = data.pop("expected")
                update = resume.build_runtime_parent_frame_resume_stack_update(
                    record,
                    **data,
                )
                self.assertEqual(update.stack_update_status, expected_status)

    def test_nested_return_resume_trace_records_4_to_3_to_2_to_1(self) -> None:
        payload = resume.build_demo_nested_4_to_3_to_2_to_1_resume()
        trace = resume.RuntimeNestedReturnResumeTrace.from_dict(
            payload["runtime_nested_return_resume_trace"]
        )
        self.assertEqual(
            trace.return_sequence,
            (
                "event_4_returned_to_event_3",
                "event_3_returned_to_event_2",
                "event_2_returned_to_event_1",
                "event_1_closed",
            ),
        )
        self.assertEqual(
            trace.resume_sequence,
            (
                "event_3_resumed_after_event_4",
                "event_2_resumed_after_event_3",
                "event_1_resumed_after_event_2",
            ),
        )
        self.assertEqual(
            trace.trace_status,
            "nested_return_resume_trace_complete",
        )
        audit = resume.RuntimeParentFrameResumeAudit.from_dict(
            payload["runtime_parent_frame_resume_audit"]
        )
        self.assertEqual(audit.audit_status, "passed_nested_return_resume_trace")

    def test_nested_return_resume_trace_blocks_missing_or_invalid_items(self) -> None:
        parent, child = resume._demo_parent_child_frames("trace_block")
        payload = resume.resume_parent_frame_from_child_return(
            child,
            parent_event_frame=parent,
            dispatch_return_payload=resume._demo_dispatch_return_payload(
                child,
                "returned_success",
            ),
        )
        record = resume.RuntimeParentFrameResumeRecord.from_dict(
            payload["runtime_parent_frame_resume"]
        )
        update = resume.RuntimeParentFrameResumeStackUpdateRecord.from_dict(
            payload["runtime_parent_frame_resume_stack_update"]
        )
        frames = (parent, child)
        missing_child = resume.build_runtime_nested_return_resume_trace(
            parent_resumes=(),
            stack_updates=(),
            event_frames=frames,
        )
        self.assertEqual(
            missing_child.trace_status,
            "nested_return_resume_trace_blocked_missing_child_return",
        )
        missing_parent = resume.build_runtime_nested_return_resume_trace(
            parent_resumes=(record,),
            stack_updates=(),
            event_frames=frames,
        )
        self.assertEqual(
            missing_parent.trace_status,
            "nested_return_resume_trace_blocked_missing_parent_resume",
        )
        invalid_update = replace(
            update,
            stack_update_status="blocked_stack_underflow",
        )
        invalid_stack = resume.build_runtime_nested_return_resume_trace(
            parent_resumes=(record,),
            stack_updates=(invalid_update,),
            event_frames=frames,
        )
        self.assertEqual(
            invalid_stack.trace_status,
            "nested_return_resume_trace_blocked_invalid_stack_update",
        )
        forbidden = resume.build_runtime_nested_return_resume_trace(
            parent_resumes=(record,),
            stack_updates=(update,),
            event_frames=frames,
            force_forbidden_authority=True,
        )
        self.assertEqual(
            forbidden.trace_status,
            "nested_return_resume_trace_blocked_forbidden_authority_detected",
        )

    def test_audit_passes_and_blocks_required_cases(self) -> None:
        expected = {
            "success": (
                resume.build_demo_child_success_parent_continue,
                "passed_parent_frame_resume_after_child_success",
            ),
            "blocked": (
                resume.build_demo_child_blocked_parent_continue,
                "passed_parent_frame_resume_after_child_blocked",
            ),
            "unknown": (
                resume.build_demo_child_unknown_parent_deferred,
                "passed_parent_frame_deferred_after_child_unknown",
            ),
            "fault": (
                resume.build_demo_child_fault_parent_faulted,
                "passed_parent_frame_faulted_after_child_fault",
            ),
            "missing": (
                resume.build_demo_blocked_missing_parent_resume,
                "blocked_missing_parent_frame",
            ),
            "new_child": (
                resume.build_demo_blocked_new_child_event_requested_resume,
                "blocked_new_child_event_created",
            ),
            "forbidden": (
                resume.build_demo_blocked_forbidden_authority_resume,
                "blocked_memory_write_detected",
            ),
        }
        for case, (builder, expected_status) in expected.items():
            with self.subTest(case=case):
                payload = builder()
                audit = resume.RuntimeParentFrameResumeAudit.from_dict(
                    payload["runtime_parent_frame_resume_audit"]
                )
                self.assertEqual(audit.audit_status, expected_status)
                self.assertTrue(audit.no_autonomous_scheduler)
                self.assertTrue(audit.no_open_ended_loop)
                self.assertTrue(audit.no_thought_engine_behavior)

        forbidden_flags = {
            "external_execution_requested": "blocked_external_execution_detected",
            "automatic_learning_approval_requested": (
                "blocked_automatic_learning_approval_detected"
            ),
            "recursive_learning_requested": "blocked_recursive_learning_detected",
            "production_behavior_requested": "blocked_production_behavior_detected",
        }
        for flag, expected_status in forbidden_flags.items():
            with self.subTest(flag=flag):
                parent, child = resume._demo_parent_child_frames(flag)
                payload = resume.resume_parent_frame_from_child_return(
                    child,
                    parent_event_frame=parent,
                    dispatch_return_payload=resume._demo_dispatch_return_payload(
                        child,
                        "returned_success",
                    ),
                    request_payload={flag: True},
                )
                audit = resume.RuntimeParentFrameResumeAudit.from_dict(
                    payload["runtime_parent_frame_resume_audit"]
                )
                self.assertEqual(audit.audit_status, expected_status)

    def test_record_validators_accept_demo_records(self) -> None:
        payload = resume.build_demo_child_success_parent_continue()
        self.assertTrue(
            resume.validate_runtime_parent_frame_resume_request(
                payload["runtime_parent_frame_resume_request"]
            )["valid"]
        )
        self.assertTrue(
            resume.validate_runtime_parent_frame_resume_decision(
                payload["runtime_parent_frame_resume_decision"]
            )["valid"]
        )
        self.assertTrue(
            resume.validate_runtime_parent_frame_resume_record(
                payload["runtime_parent_frame_resume"]
            )["valid"]
        )
        self.assertTrue(
            resume.validate_runtime_parent_frame_resume_stack_update(
                payload["runtime_parent_frame_resume_stack_update"]
            )["valid"]
        )
        nested = resume.build_demo_nested_4_to_3_to_2_to_1_resume()
        self.assertTrue(
            resume.validate_runtime_nested_return_resume_trace(
                nested["runtime_nested_return_resume_trace"]
            )["valid"]
        )
        self.assertTrue(
            resume.validate_runtime_parent_frame_resume_audit(
                payload["runtime_parent_frame_resume_audit"]
            )["valid"]
        )

    def test_cli_commands_work_without_writing_state(self) -> None:
        commands = (
            ("show-demo-success",),
            ("show-demo-blocked",),
            ("show-demo-unknown",),
            ("show-demo-fault",),
            ("show-demo-nested-resume",),
            ("show-demo-blocked-case", "--case", "missing-parent"),
            ("show-demo-blocked-case", "--case", "new-child-requested"),
            ("show-demo-blocked-case", "--case", "forbidden-authority"),
            ("validate-demo-resume",),
        )
        for command in commands:
            with self.subTest(command=command):
                payload = self._run_json_module(RESUME_CLI, *command)
                self.assertIsInstance(payload, dict)

    def test_guided_console_parent_resume_commands_work(self) -> None:
        validation = validate_parent_frame_resume_demo_from_guided_cradle_growth_console()
        self.assertEqual(
            validation["validation"]["audit_status"],
            "passed_parent_frame_resume_after_child_success",
        )
        commands = (
            "runtime-show-parent-resume-success-demo",
            "runtime-show-parent-resume-blocked-demo",
            "runtime-show-parent-resume-unknown-demo",
            "runtime-show-parent-resume-fault-demo",
            "runtime-show-nested-return-resume-demo",
            "runtime-validate-parent-frame-resume-demo",
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

    def _resume_payload(self, return_status: str) -> dict[str, object]:
        parent, child = resume._demo_parent_child_frames(return_status)
        return resume.resume_parent_frame_from_child_return(
            child,
            parent_event_frame=parent,
            dispatch_return_payload=resume._demo_dispatch_return_payload(
                child,
                return_status,
            ),
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
