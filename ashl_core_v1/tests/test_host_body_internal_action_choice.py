from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

from ashl_core_v1.host_body import host_body_internal_action_choice as action
from ashl_core_v1.host_body import host_body_trace_history_lane as trace
from ashl_core_v1.host_body import qingyin_home_internal_space_surface as home
from ashl_core_v1.runtime.guided_cradle_growth_teacher_console import (
    validate_host_body_internal_action_choice_from_guided_cradle_growth_console,
)


ACTION_CLI = "ashl_core_v1.host_body.host_body_internal_action_choice_cli"
GUIDED_CLI = "ashl_core_v1.runtime.guided_cradle_growth_teacher_console_cli"


class HostBodyInternalActionChoiceTests(unittest.TestCase):
    def test_choice_plan_builds_and_blocks_forbidden_authority(self) -> None:
        trace_audit, readback, home_audit = self._plan_inputs()
        plan = action.build_host_body_internal_action_choice_plan(
            trace_history_audit=trace_audit,
            trace_history_readback=readback,
            home_surface_audit=home_audit,
        )
        self.assertEqual(plan.plan_status, "internal_action_choice_plan_created")
        self.assertTrue(plan.internal_only)
        self.assertTrue(plan.record_only)
        self.assertTrue(plan.read_only_source_required)
        self.assertIn("observe_again", plan.allowed_internal_action_kinds)
        self.assertIn("mouse_control", plan.forbidden_external_action_kinds)
        self.assertFalse(plan.task_engine_action_selection_allowed)
        self.assertFalse(plan.final_action_allowed)
        self.assertFalse(plan.direct_command_allowed)
        self.assertFalse(plan.sandbox_execution_allowed)
        self.assertFalse(plan.external_control_allowed)
        self.assertFalse(plan.memory_write_allowed)
        self.assertFalse(plan.learning_candidate_creation_allowed)
        self.assertFalse(plan.automatic_learning_approval_allowed)
        self.assertFalse(plan.first_output_allowed)
        self.assertFalse(plan.live_runtime_session_allowed)
        self.assertTrue(action.validate_host_body_internal_action_choice_plan(plan)["valid"])

        blocked = {
            "missing": ({"trace_history_audit": None}, "blocked_missing_trace_history_audit"),
            "task": (
                {"task_engine_action_selection_allowed": True},
                "blocked_task_action_selection_allowed",
            ),
            "final": ({"final_action_allowed": True}, "blocked_task_action_selection_allowed"),
            "direct": ({"direct_command_allowed": True}, "blocked_task_action_selection_allowed"),
            "sandbox": ({"sandbox_execution_allowed": True}, "blocked_task_action_selection_allowed"),
            "external": ({"external_control_allowed": True}, "blocked_external_control_allowed"),
            "memory": ({"memory_write_allowed": True}, "blocked_memory_write_allowed"),
            "learning": (
                {"learning_candidate_creation_allowed": True},
                "blocked_memory_write_allowed",
            ),
            "approval": (
                {"automatic_learning_approval_allowed": True},
                "blocked_memory_write_allowed",
            ),
            "first": ({"first_output_allowed": True}, "blocked_first_output_allowed"),
            "live": ({"live_runtime_session_allowed": True}, "blocked_live_runtime_allowed"),
        }
        for case, (kwargs, expected_status) in blocked.items():
            with self.subTest(case=case):
                args = {
                    "trace_history_audit": trace_audit,
                    "trace_history_readback": readback,
                    "home_surface_audit": home_audit,
                    **kwargs,
                }
                self.assertEqual(
                    action.build_host_body_internal_action_choice_plan(**args).plan_status,
                    expected_status,
                )

    def test_candidate_records_internal_action_kinds_and_blocks_forbidden(self) -> None:
        plan = self._plan()
        for kind in (
            "observe_again",
            "mark_event_interesting",
            "mark_uncertain",
            "request_teacher_review",
            "shift_internal_focus",
            "update_home_status",
            "pause_event_processing",
        ):
            with self.subTest(kind=kind):
                candidate = action.build_host_body_internal_action_candidate(
                    choice_plan=plan,
                    candidate_action_kind=kind,
                )
                self.assertEqual(candidate.candidate_action_kind, kind)
                self.assertEqual(candidate.candidate_status, "internal_action_candidate_created")
                self.assertTrue(action.validate_host_body_internal_action_candidate(candidate)["valid"])

        blocked = {
            "forbidden_kind": (
                {"candidate_action_kind": "not_allowed"},
                "internal_action_candidate_blocked_forbidden_kind",
            ),
            "external_kind": (
                {"candidate_action_kind": "mouse_control"},
                "internal_action_candidate_blocked_external_control",
            ),
            "external": (
                {"external_control_created": True},
                "internal_action_candidate_blocked_external_control",
            ),
            "task": (
                {"task_selected_action_created": True},
                "internal_action_candidate_blocked_task_action_selection",
            ),
            "first": (
                {"first_output_created": True},
                "internal_action_candidate_blocked_first_output",
            ),
            "memory": (
                {"memory_layer_write_performed": True},
                "internal_action_candidate_blocked_forbidden_authority",
            ),
        }
        for case, (kwargs, expected_status) in blocked.items():
            with self.subTest(case=case):
                self.assertEqual(
                    action.build_host_body_internal_action_candidate(
                        choice_plan=plan,
                        candidate_action_kind=kwargs.pop("candidate_action_kind", "observe_again"),
                        **kwargs,
                    ).candidate_status,
                    expected_status,
                )

    def test_deterministic_demos_select_expected_internal_actions(self) -> None:
        expected = {
            "camera": (
                action.build_demo_camera_change_marks_interesting(),
                "mark_event_interesting",
                "passed_host_body_internal_action_choice",
            ),
            "uncertain": (
                action.build_demo_unknown_event_marks_uncertain(),
                "mark_uncertain",
                "passed_internal_action_choice_mark_uncertain",
            ),
            "teacher": (
                action.build_demo_deferred_dispatch_requests_teacher_review(),
                "request_teacher_review",
                "passed_internal_action_choice_request_teacher_review",
            ),
            "idle": (
                action.build_demo_host_idle_observe_again(),
                "observe_again",
                "passed_internal_action_choice_observe_again",
            ),
            "home": (
                action.build_demo_update_home_status_choice(),
                "update_home_status",
                "passed_internal_action_choice_update_home_status",
            ),
        }
        for case, (payload, selected, audit_status) in expected.items():
            with self.subTest(case=case):
                self.assertEqual(payload["internal_action_choice"]["selected_internal_action_kind"], selected)
                self.assertEqual(payload["internal_action_choice_audit"]["audit_status"], audit_status)
                self.assertFalse(payload["internal_action_choice"]["task_selected_action_created"])
                self.assertFalse(payload["internal_action_result"]["first_output_created"])
                self.assertFalse(payload["internal_action_result"]["memory_layer_write_performed"])

    def test_choice_selects_highest_priority_tie_order_and_blocks(self) -> None:
        plan = self._plan()
        interesting = action.build_host_body_internal_action_candidate(
            choice_plan=plan,
            candidate_action_kind="mark_event_interesting",
            candidate_priority=10,
        )
        teacher = action.build_host_body_internal_action_candidate(
            choice_plan=plan,
            candidate_action_kind="request_teacher_review",
            candidate_priority=10,
        )
        lower = action.build_host_body_internal_action_candidate(
            choice_plan=plan,
            candidate_action_kind="observe_again",
            candidate_priority=1,
        )
        choice = action.build_host_body_internal_action_choice(
            choice_plan=plan,
            candidates=(interesting, teacher, lower),
        )
        self.assertEqual(choice.selected_internal_action_kind, "request_teacher_review")
        self.assertEqual(choice.choice_status, "internal_action_choice_selected")

        empty = action.build_host_body_internal_action_choice(choice_plan=plan, candidates=tuple())
        self.assertEqual(empty.choice_status, "internal_action_choice_deferred_no_candidates")

        invalid = action.build_host_body_internal_action_candidate(
            choice_plan=plan,
            candidate_action_kind="mouse_control",
        )
        self.assertEqual(
            action.build_host_body_internal_action_choice(
                choice_plan=plan,
                candidates=(invalid,),
            ).choice_status,
            "internal_action_choice_blocked_invalid_candidate",
        )
        self.assertEqual(
            action.build_host_body_internal_action_choice(
                choice_plan=plan,
                candidates=(interesting,),
                external_control_created=True,
            ).choice_status,
            "internal_action_choice_blocked_external_control",
        )
        self.assertEqual(
            action.build_host_body_internal_action_choice(
                choice_plan=plan,
                candidates=(interesting,),
                task_selected_action_created=True,
            ).choice_status,
            "internal_action_choice_blocked_task_action_selection",
        )
        self.assertEqual(
            action.build_host_body_internal_action_choice(
                choice_plan=plan,
                candidates=(interesting,),
                teacher_approval_created=True,
            ).choice_status,
            "internal_action_choice_blocked_teacher_approval_created",
        )
        self.assertEqual(
            action.build_host_body_internal_action_choice(
                choice_plan=plan,
                candidates=(interesting,),
                first_output_created=True,
            ).choice_status,
            "internal_action_choice_blocked_first_output",
        )

    def test_result_and_surface_effect_records_and_blocks_forbidden_outputs(self) -> None:
        plan = self._plan()
        choices = {}
        for kind in (
            "mark_event_interesting",
            "request_teacher_review",
            "update_home_status",
            "mark_uncertain",
            "observe_again",
        ):
            candidate = action.build_host_body_internal_action_candidate(
                choice_plan=plan,
                candidate_action_kind=kind,
            )
            choices[kind] = action.build_host_body_internal_action_choice(
                choice_plan=plan,
                candidates=(candidate,),
            )
        self.assertTrue(action.build_host_body_internal_action_result(
            internal_action_choice=choices["mark_event_interesting"]
        ).internal_marker_created)
        self.assertTrue(action.build_host_body_internal_action_result(
            internal_action_choice=choices["request_teacher_review"]
        ).teacher_review_request_recorded)
        self.assertTrue(action.build_host_body_internal_action_result(
            internal_action_choice=choices["update_home_status"]
        ).home_status_update_recorded)
        self.assertEqual(action.build_host_body_internal_action_result(
            internal_action_choice=choices["mark_uncertain"]
        ).result_status, "internal_action_result_recorded_mark_uncertain")
        self.assertTrue(action.build_host_body_internal_action_result(
            internal_action_choice=choices["observe_again"]
        ).observe_again_recommendation_recorded)

        blocked_result_flags = {
            "screen": "actual_screen_mutated",
            "sound": "actual_sound_played",
            "unity": "unity_runtime_mutated",
            "avatar": "avatar_control_created",
            "teacher": "teacher_approval_created",
            "task": "task_selected_action_created",
            "final": "final_action_created",
            "direct": "direct_command_created",
            "sandbox": "sandbox_execution_created",
            "external": "external_control_created",
            "os": "os_control_created",
            "mouse": "mouse_control_created",
            "keyboard": "keyboard_control_created",
            "browser": "browser_control_created",
            "file": "file_operation_created",
            "network": "network_execution_created",
            "shell": "shell_execution_created",
            "api": "external_api_call_created",
            "memory": "memory_layer_write_performed",
            "learning": "learning_candidate_created",
            "approval": "automatic_learning_approval_created",
            "first": "first_output_created",
            "live": "live_runtime_session_created",
        }
        for case, flag in blocked_result_flags.items():
            with self.subTest(case=case):
                result = action.build_host_body_internal_action_result(
                    internal_action_choice=choices["mark_event_interesting"],
                    **{flag: True},
                )
                self.assertTrue(result.result_status.startswith("internal_action_result_blocked"))

        result = action.build_host_body_internal_action_result(
            internal_action_choice=choices["update_home_status"]
        )
        self.assertEqual(
            action.build_host_body_internal_action_surface_effect(
                internal_action_result=result
            ).surface_effect_status,
            "surface_effect_recorded_status_light",
        )
        blocked_effect_flags = {
            "status": "actual_status_light_mutated",
            "home": "actual_home_surface_mutated",
            "unity": "actual_unity_runtime_mutated",
            "screen": "actual_screen_mutated",
            "sound": "actual_sound_played",
            "first": "first_output_created",
            "external": "external_message_created",
            "file": "file_written",
            "network": "network_output_created",
        }
        for case, flag in blocked_effect_flags.items():
            with self.subTest(case=case):
                effect = action.build_host_body_internal_action_surface_effect(
                    internal_action_result=result,
                    **{flag: True},
                )
                self.assertTrue(effect.surface_effect_status.startswith("surface_effect_blocked"))

    def test_choice_set_audit_readiness_and_blocked_demos(self) -> None:
        full = action.build_demo_camera_change_marks_interesting()
        self.assertEqual(
            full["internal_action_choice_set"]["choice_set_status"],
            "internal_action_choice_set_recorded",
        )
        self.assertEqual(full["internal_action_choice_set"]["candidate_count"], 1)
        self.assertEqual(full["internal_action_choice_audit"]["audit_status"], "passed_host_body_internal_action_choice")
        readiness = full["internal_action_choice_readiness"]
        self.assertEqual(readiness["readiness_status"], "ready_for_host_body_v0_milestone_audit_only")
        self.assertTrue(readiness["ready_for_host_body_internal_action_home_surface_link"])
        self.assertTrue(readiness["ready_for_teacher_observed_host_body_cli"])
        self.assertTrue(readiness["ready_for_host_body_v0_milestone_audit"])
        self.assertTrue(readiness["ready_for_runtime_state_persistence_binding"])
        self.assertFalse(readiness["ready_for_task_engine_action_selection"])
        self.assertFalse(readiness["ready_for_external_control"])
        self.assertFalse(readiness["ready_for_os_control"])
        self.assertFalse(readiness["ready_for_file_operation"])
        self.assertFalse(readiness["ready_for_network_execution"])
        self.assertFalse(readiness["ready_for_memory_layer_write"])
        self.assertFalse(readiness["ready_for_learning_candidate_creation"])
        self.assertFalse(readiness["ready_for_automatic_learning_approval"])
        self.assertFalse(readiness["ready_for_first_output"])
        self.assertFalse(readiness["ready_for_live_runtime_session"])

        choice_set = action.build_demo_internal_action_choice_set()["internal_action_choice_set"]
        self.assertEqual(choice_set["choice_set_kind"], "mixed_internal_action_choice_demo")
        self.assertGreater(choice_set["candidate_count"], 1)

        blocked = {
            "external": (
                action.build_demo_blocked_external_control_internal_action(),
                "blocked_external_control_detected",
            ),
            "task": (
                action.build_demo_blocked_task_action_selection_internal_action(),
                "blocked_task_action_selection_detected",
            ),
            "teacher": (
                action.build_demo_blocked_teacher_approval_internal_action(),
                "blocked_teacher_approval_created",
            ),
            "first": (
                action.build_demo_blocked_first_output_internal_action(),
                "blocked_first_output_detected",
            ),
            "memory": (
                action.build_demo_blocked_memory_write_internal_action(),
                "blocked_memory_write_detected",
            ),
        }
        for case, (payload, expected_status) in blocked.items():
            with self.subTest(case=case):
                self.assertEqual(payload["internal_action_choice_audit"]["audit_status"], expected_status)

        self.assertEqual(
            action.build_host_body_internal_action_choice_audit(
                choice_plan=None,
            ).audit_status,
            "blocked_invalid_plan",
        )
        self.assertEqual(
            action.build_host_body_internal_action_choice_audit(
                choice_plan=self._plan(),
                force_production_behavior=True,
            ).audit_status,
            "blocked_production_behavior_detected",
        )

    def test_cli_commands_work(self) -> None:
        commands = {
            ("show-demo-camera-interesting",): "mark_event_interesting",
            ("show-demo-uncertain",): "passed_internal_action_choice_mark_uncertain",
            ("show-demo-teacher-review",): "passed_internal_action_choice_request_teacher_review",
            ("show-demo-observe-again",): "passed_internal_action_choice_observe_again",
            ("show-demo-update-home-status",): "passed_internal_action_choice_update_home_status",
            ("show-demo-choice-set",): "mixed_internal_action_choice_demo",
            ("show-demo-readiness",): "ready_for_host_body_v0_milestone_audit_only",
            ("validate-demo-internal-action-choice",): "passed_host_body_internal_action_choice",
            ("show-demo-blocked", "--case", "external-control"): "blocked_external_control_detected",
            ("show-demo-blocked", "--case", "task-action-selection"): "blocked_task_action_selection_detected",
            ("show-demo-blocked", "--case", "teacher-approval"): "blocked_teacher_approval_created",
            ("show-demo-blocked", "--case", "first-output"): "blocked_first_output_detected",
            ("show-demo-blocked", "--case", "memory-write"): "blocked_memory_write_detected",
        }
        for command, expected_text in commands.items():
            with self.subTest(command=command):
                payload = self._run_json(ACTION_CLI, *command)
                self.assertIn(expected_text, json.dumps(payload, sort_keys=True))

    def test_guided_console_internal_action_choice_demo_works(self) -> None:
        validation = validate_host_body_internal_action_choice_from_guided_cradle_growth_console()
        self.assertEqual(validation["guided_console_action"], "host_body_validate_internal_action_choice_demo")
        self.assertTrue(validation["validation"]["valid"])
        self.assertFalse(validation["task_selected_action_created"])
        self.assertFalse(validation["external_control_created"])
        self.assertFalse(validation["memory_layer_write_performed"])
        self.assertFalse(validation["teacher_approval_created"])
        self.assertFalse(validation["first_output_created"])
        self.assertFalse(validation["live_runtime_session_created"])

        commands = {
            "host-body-show-internal-action-camera-interesting-demo": "mark_event_interesting",
            "host-body-show-internal-action-uncertain-demo": "passed_internal_action_choice_mark_uncertain",
            "host-body-show-internal-action-teacher-review-demo": "passed_internal_action_choice_request_teacher_review",
            "host-body-show-internal-action-observe-again-demo": "passed_internal_action_choice_observe_again",
            "host-body-show-internal-action-update-home-status-demo": "passed_internal_action_choice_update_home_status",
            "host-body-show-internal-action-readiness": "ready_for_host_body_v0_milestone_audit_only",
            "host-body-validate-internal-action-choice-demo": "passed_host_body_internal_action_choice",
        }
        for command, expected_text in commands.items():
            with self.subTest(command=command):
                payload = self._run_json(GUIDED_CLI, command)
                self.assertIn(expected_text, json.dumps(payload, sort_keys=True))

    def test_no_repo_data_directory_created(self) -> None:
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _plan_inputs(self):
        trace_payload = trace.build_demo_full_host_body_trace_history_lane()
        home_payload = home.build_demo_qingyin_home_internal_space_surface()
        return (
            trace_payload["trace_history_audit"],
            trace_payload["trace_history_readback"],
            home_payload["home_internal_space_surface_audit"],
        )

    def _plan(self) -> action.HostBodyInternalActionChoicePlanRecord:
        trace_audit, readback, home_audit = self._plan_inputs()
        return action.build_host_body_internal_action_choice_plan(
            trace_history_audit=trace_audit,
            trace_history_readback=readback,
            home_surface_audit=home_audit,
        )

    def _run_json(self, module: str, *args: str) -> dict[str, object]:
        completed = subprocess.run(
            ["py", "-3", "-m", module, *args],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(completed.stdout)


if __name__ == "__main__":
    unittest.main()
