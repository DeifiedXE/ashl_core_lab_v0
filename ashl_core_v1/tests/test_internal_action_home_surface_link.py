from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

from ashl_core_v1.host_body import internal_action_home_surface_link as link
from ashl_core_v1.runtime.guided_cradle_growth_teacher_console import (
    validate_host_body_home_surface_link_from_guided_cradle_growth_console,
)


LINK_CLI = "ashl_core_v1.host_body.internal_action_home_surface_link_cli"
GUIDED_CLI = "ashl_core_v1.runtime.guided_cradle_growth_teacher_console_cli"


class InternalActionHomeSurfaceLinkTests(unittest.TestCase):
    def test_plan_builds_from_sources_and_blocks_forbidden_authority(self) -> None:
        closed_loop, home_audit, boundary = link._demo_sources()
        plan = link.build_internal_action_home_surface_link_plan(
            closed_loop_milestone_audit=closed_loop,
            home_surface_audit=home_audit,
            trace_spine_boundary=boundary,
        )
        self.assertEqual(plan.plan_status, "home_surface_link_plan_created")
        self.assertTrue(plan.read_only_surface_link_allowed)
        self.assertTrue(plan.teacher_observed_surface_link_allowed)
        self.assertTrue(plan.status_light_link_allowed)
        self.assertTrue(plan.render_snapshot_link_allowed)
        self.assertFalse(plan.unity_runtime_mutation_allowed)
        self.assertFalse(plan.actual_screen_mutation_allowed)
        self.assertFalse(plan.external_message_allowed)
        self.assertFalse(plan.task_action_selection_allowed)
        self.assertFalse(plan.direct_command_allowed)
        self.assertFalse(plan.external_control_allowed)
        self.assertFalse(plan.memory_write_allowed)
        self.assertFalse(plan.first_output_allowed)
        self.assertFalse(plan.live_runtime_session_allowed)
        self.assertTrue(link.validate_internal_action_home_surface_link_plan(plan)["valid"])

        blocked = (
            (
                {"closed_loop_milestone_audit": None},
                "blocked_missing_closed_loop_milestone_audit",
            ),
            ({"home_surface_audit": None}, "blocked_missing_home_surface_audit"),
            ({"trace_spine_boundary": None}, "blocked_missing_trace_spine_boundary"),
            (
                {"unity_runtime_mutation_allowed": True},
                "blocked_unity_runtime_mutation_allowed",
            ),
            (
                {"actual_screen_mutation_allowed": True},
                "blocked_actual_screen_mutation_allowed",
            ),
            ({"external_message_allowed": True}, "blocked_external_message_allowed"),
            (
                {"task_action_selection_allowed": True},
                "blocked_task_action_selection_allowed",
            ),
            ({"direct_command_allowed": True}, "blocked_direct_command_allowed"),
            ({"external_control_allowed": True}, "blocked_external_control_allowed"),
            ({"memory_write_allowed": True}, "blocked_memory_write_allowed"),
            ({"first_output_allowed": True}, "blocked_first_output_allowed"),
            ({"live_runtime_session_allowed": True}, "blocked_live_runtime_allowed"),
        )
        for kwargs, expected in blocked:
            args = {
                "closed_loop_milestone_audit": closed_loop,
                "home_surface_audit": home_audit,
                "trace_spine_boundary": boundary,
            }
            args.update(kwargs)
            with self.subTest(expected=expected):
                item = link.build_internal_action_home_surface_link_plan(**args)
                self.assertEqual(item.plan_status, expected)
                self.assertFalse(link.validate_internal_action_home_surface_link_plan(item)["valid"])

    def test_mapping_rules_and_mapping_boundaries(self) -> None:
        plan = self._plan()
        expected = {
            "mark_uncertain": (
                "uncertainty",
                "uncertainty_marker_visible",
                "uncertainty_render_snapshot",
            ),
            "request_teacher_review": (
                "teacher_review_requested",
                "teacher_review_request_visible",
                "teacher_review_request_render_snapshot",
            ),
            "observe_again": (
                "observe_again",
                "observe_again_recommendation_visible",
                "observe_again_render_snapshot",
            ),
            "mark_event_interesting": (
                "interesting_event",
                "interesting_event_marker_visible",
                "internal_action_status_render_snapshot",
            ),
            "pause_event_processing": (
                "event_processing_paused",
                "pause_event_processing_marker_visible",
                "pause_event_processing_render_snapshot",
            ),
            "shift_internal_focus": (
                "internal_focus_shifted",
                "readback_reason_visible",
                "internal_action_status_render_snapshot",
            ),
            "update_home_status": (
                "home_status_updated",
                "no_teacher_surface_update",
                "home_status_update_render_snapshot",
            ),
        }
        for action, (status_light, teacher_update, render_kind) in expected.items():
            with self.subTest(action=action):
                mapping = link.build_internal_action_home_surface_mapping(
                    home_surface_link_plan=plan,
                    selected_internal_action_kind=action,
                    readback_reason_refs=("readback_reason:a",),
                    source_trace_refs=("trace:a",),
                )
                self.assertEqual(mapping.target_status_light_kind, status_light)
                self.assertEqual(mapping.target_teacher_observed_update_kind, teacher_update)
                self.assertEqual(mapping.target_render_snapshot_kind, render_kind)
                self.assertEqual(mapping.readback_reason_refs, ("readback_reason:a",))
                self.assertEqual(mapping.source_trace_refs, ("trace:a",))
                self.assertTrue(link.validate_internal_action_home_surface_mapping(mapping)["valid"])

        blocked = (
            ({"internal_action_result_valid": False}, "blocked_invalid_internal_action_result"),
            (
                {"selected_internal_action_kind": "task_selected_action"},
                "blocked_forbidden_internal_action_kind",
            ),
            ({"actual_surface_mutated": True}, "blocked_actual_surface_mutation_detected"),
            ({"unity_runtime_mutated": True}, "blocked_unity_runtime_mutation_detected"),
            ({"screen_mutated": True}, "blocked_screen_mutation_detected"),
            ({"external_message_created": True}, "blocked_external_message_detected"),
            ({"first_output_created": True}, "blocked_first_output_detected"),
            ({"live_runtime_session_created": True}, "blocked_live_runtime_detected"),
        )
        for kwargs, expected_status in blocked:
            args = {
                "home_surface_link_plan": plan,
                "selected_internal_action_kind": "mark_uncertain",
            }
            args.update(kwargs)
            with self.subTest(expected_status=expected_status):
                mapping = link.build_internal_action_home_surface_mapping(**args)
                self.assertEqual(mapping.mapping_status, expected_status)
                self.assertFalse(link.validate_internal_action_home_surface_mapping(mapping)["valid"])

    def test_status_light_teacher_observed_and_render_links(self) -> None:
        demos = (
            (
                link.build_demo_mark_uncertain_home_surface_link(),
                "uncertainty",
                "home_status_light_link_created_uncertainty",
                "uncertainty_marker_visible",
                "home_teacher_observed_link_created_uncertainty",
                "uncertainty_render_snapshot",
            ),
            (
                link.build_demo_request_teacher_review_home_surface_link(),
                "teacher_review_requested",
                "home_status_light_link_created_teacher_review",
                "teacher_review_request_visible",
                "home_teacher_observed_link_created_review_request",
                "teacher_review_request_render_snapshot",
            ),
            (
                link.build_demo_observe_again_home_surface_link(),
                "observe_again",
                "home_status_light_link_created_observe_again",
                "observe_again_recommendation_visible",
                "home_teacher_observed_link_created_observe_again",
                "observe_again_render_snapshot",
            ),
            (
                link.build_demo_pause_event_processing_home_surface_link(),
                "event_processing_paused",
                "home_status_light_link_created_pause",
                "pause_event_processing_marker_visible",
                "home_teacher_observed_link_created_pause",
                "pause_event_processing_render_snapshot",
            ),
            (
                link.build_demo_update_home_status_surface_link(),
                "home_status_updated",
                "home_status_light_link_created",
                "no_teacher_surface_update",
                "home_teacher_observed_link_created_noop",
                "home_status_update_render_snapshot",
            ),
        )
        for payload, light_kind, light_status, teacher_kind, teacher_status, render_kind in demos:
            with self.subTest(light_kind=light_kind):
                light = payload["internal_action_home_status_light_link"]
                teacher = payload["internal_action_home_teacher_observed_link"]
                render = payload["internal_action_home_render_snapshot_link"]
                self.assertEqual(light["status_light_kind"], light_kind)
                self.assertEqual(light["status_light_link_status"], light_status)
                self.assertTrue(light["read_only_status_record"])
                self.assertFalse(light["actual_status_light_mutated"])
                self.assertTrue(link.validate_internal_action_home_status_light_link(light)["valid"])
                self.assertEqual(teacher["teacher_observed_update_kind"], teacher_kind)
                self.assertEqual(teacher["teacher_observed_link_status"], teacher_status)
                self.assertFalse(teacher["teacher_approval_created"])
                self.assertFalse(teacher["learning_approval_created"])
                self.assertFalse(teacher["memory_write_approval_created"])
                self.assertTrue(link.validate_internal_action_home_teacher_observed_link(teacher)["valid"])
                self.assertEqual(render["render_snapshot_kind"], render_kind)
                self.assertTrue(render["read_only_render_snapshot"])
                self.assertFalse(render["unity_runtime_started"])
                self.assertFalse(render["actual_screen_mutated"])
                self.assertTrue(link.validate_internal_action_home_render_snapshot_link(render)["valid"])

        mapping = link.build_demo_mark_uncertain_home_surface_link()[
            "internal_action_home_surface_mapping"
        ]
        blocked_lights = (
            ({"actual_status_light_mutated": True}, "blocked_actual_status_light_mutation"),
            ({"actual_screen_mutated": True}, "blocked_screen_mutation"),
            ({"unity_runtime_mutated": True}, "blocked_unity_runtime_mutation"),
            ({"sound_played": True}, "blocked_sound_output"),
            ({"first_output_created": True}, "blocked_first_output"),
            ({"live_runtime_session_created": True}, "blocked_live_runtime"),
        )
        for kwargs, expected_status in blocked_lights:
            with self.subTest(expected_status=expected_status):
                item = link.build_internal_action_home_status_light_link(
                    home_surface_mapping=mapping, **kwargs
                )
                self.assertEqual(item.status_light_link_status, expected_status)
                self.assertFalse(link.validate_internal_action_home_status_light_link(item)["valid"])

        blocked_teacher = (
            ({"teacher_approval_created": True}, "blocked_teacher_approval_created"),
            ({"learning_approval_created": True}, "blocked_learning_approval_created"),
            (
                {"memory_write_approval_created": True},
                "blocked_memory_write_approval_created",
            ),
            ({"actual_surface_mutated": True}, "blocked_actual_surface_mutation"),
            ({"external_message_created": True}, "blocked_external_message_created"),
            ({"first_output_created": True}, "blocked_first_output"),
            ({"live_runtime_session_created": True}, "blocked_live_runtime"),
        )
        for kwargs, expected_status in blocked_teacher:
            with self.subTest(expected_status=expected_status):
                item = link.build_internal_action_home_teacher_observed_link(
                    home_surface_mapping=mapping, **kwargs
                )
                self.assertEqual(item.teacher_observed_link_status, expected_status)
                self.assertFalse(link.validate_internal_action_home_teacher_observed_link(item)["valid"])

        blocked_render = (
            ({"unity_runtime_started": True}, "blocked_unity_runtime_started"),
            ({"unity_scene_mutated": True}, "blocked_unity_scene_mutation"),
            ({"avatar_control_created": True}, "blocked_avatar_control"),
            ({"actual_screen_mutated": True}, "blocked_screen_mutation"),
            ({"file_written": True}, "blocked_file_write"),
            ({"network_output_created": True}, "blocked_network_output"),
            ({"first_output_created": True}, "blocked_first_output"),
            ({"production_behavior_created": True}, "blocked_production_behavior"),
            ({"live_runtime_session_created": True}, "blocked_live_runtime"),
        )
        for kwargs, expected_status in blocked_render:
            with self.subTest(expected_status=expected_status):
                item = link.build_internal_action_home_render_snapshot_link(
                    home_surface_mapping=mapping, **kwargs
                )
                self.assertEqual(item.render_snapshot_link_status, expected_status)
                self.assertFalse(link.validate_internal_action_home_render_snapshot_link(item)["valid"])

    def test_trace_audit_and_readiness(self) -> None:
        for payload in (
            link.build_demo_mark_uncertain_home_surface_link(),
            link.build_demo_request_teacher_review_home_surface_link(),
            link.build_demo_observe_again_home_surface_link(),
            link.build_demo_pause_event_processing_home_surface_link(),
            link.build_demo_mixed_internal_action_home_surface_link(),
            link.build_demo_empty_internal_action_home_surface_link(),
        ):
            with self.subTest(status=payload["internal_action_home_surface_link_audit"]["audit_status"]):
                trace = payload["internal_action_home_surface_link_trace"]
                self.assertTrue(trace["read_only_surface_links_confirmed"])
                self.assertTrue(trace["record_only_links_confirmed"])
                self.assertTrue(trace["trace_spine_boundary_preserved"])
                self.assertTrue(trace["raw_trace_append_only_confirmed"])
                self.assertFalse(trace["raw_trace_summarized_during_service_period"])
                self.assertTrue(trace["memory_layer_stores_interpretation_only"])
                self.assertTrue(trace["source_trace_refs_preserved"])
                self.assertFalse(trace["concept_id_embedded_into_raw_history"])
                self.assertTrue(link.validate_internal_action_home_surface_link_trace(trace)["valid"])
                audit = payload["internal_action_home_surface_link_audit"]
                self.assertTrue(link.validate_internal_action_home_surface_link_audit(audit)["valid"])
                self.assertTrue(audit["internal_action_home_surface_link_confirmed"])
                self.assertTrue(audit["read_only_surface_confirmed"])
                self.assertTrue(audit["record_only_link_confirmed"])
                self.assertTrue(audit["raw_trace_append_only_confirmed"])
                self.assertTrue(audit["raw_trace_not_summarized_during_service_period"])
                self.assertTrue(audit["concept_id_not_embedded_into_raw_history_confirmed"])

        blocked_payloads = (
            (link.build_demo_blocked_unity_runtime_mutation(), "blocked_unity_runtime_mutation_detected"),
            (link.build_demo_blocked_screen_mutation(), "blocked_screen_mutation_detected"),
            (link.build_demo_blocked_sound_output(), "blocked_sound_output_detected"),
            (link.build_demo_blocked_external_message(), "blocked_external_message_detected"),
            (link.build_demo_blocked_file_write(), "blocked_file_write_detected"),
            (link.build_demo_blocked_network_output(), "blocked_network_output_detected"),
            (link.build_demo_blocked_task_selected_action(), "blocked_task_selected_action_created"),
            (link.build_demo_blocked_direct_command(), "blocked_direct_command_created"),
            (link.build_demo_blocked_memory_write(), "blocked_memory_write_detected"),
            (link.build_demo_blocked_first_output(), "blocked_first_output_detected"),
            (link.build_demo_blocked_live_runtime(), "blocked_live_runtime_detected"),
        )
        for payload, expected_status in blocked_payloads:
            with self.subTest(expected_status=expected_status):
                audit = payload["internal_action_home_surface_link_audit"]
                self.assertEqual(audit["audit_status"], expected_status)
                self.assertFalse(link.validate_internal_action_home_surface_link_audit(audit)["valid"])

        plan = link.build_demo_mark_uncertain_home_surface_link()["internal_action_home_surface_link_plan"]
        closed_loop, _, boundary = link._demo_sources()
        good_trace = link.build_demo_mark_uncertain_home_surface_link()[
            "internal_action_home_surface_link_trace"
        ]
        missing_plan = link.build_internal_action_home_surface_link_audit(
            home_surface_link_plan=None,
            home_surface_link_trace=good_trace,
            closed_loop_milestone_audit=closed_loop,
            trace_spine_boundary=boundary,
        )
        self.assertEqual(missing_plan.audit_status, "blocked_missing_plan")
        missing_closed = link.build_internal_action_home_surface_link_audit(
            home_surface_link_plan=plan,
            home_surface_link_trace=good_trace,
            closed_loop_milestone_audit=None,
            trace_spine_boundary=boundary,
        )
        self.assertEqual(missing_closed.audit_status, "blocked_closed_loop_milestone_missing")
        missing_boundary = link.build_internal_action_home_surface_link_audit(
            home_surface_link_plan=plan,
            home_surface_link_trace=good_trace,
            closed_loop_milestone_audit=closed_loop,
            trace_spine_boundary=None,
        )
        self.assertEqual(missing_boundary.audit_status, "blocked_trace_spine_boundary_failure")
        invalid_trace = link.build_internal_action_home_surface_link_audit(
            home_surface_link_plan=plan,
            home_surface_link_trace=None,
            closed_loop_milestone_audit=closed_loop,
            trace_spine_boundary=boundary,
        )
        self.assertEqual(invalid_trace.audit_status, "blocked_invalid_link_trace")

        synthetic_trace = dict(good_trace)
        synthetic_trace["teacher_approval_created"] = True
        blocked_teacher = link.build_internal_action_home_surface_link_audit(
            home_surface_link_plan=plan,
            home_surface_link_trace=synthetic_trace,
            closed_loop_milestone_audit=closed_loop,
            trace_spine_boundary=boundary,
        )
        self.assertEqual(blocked_teacher.audit_status, "blocked_teacher_approval_created")
        synthetic_trace = dict(good_trace)
        synthetic_trace["production_behavior_created"] = True
        blocked_production = link.build_internal_action_home_surface_link_audit(
            home_surface_link_plan=plan,
            home_surface_link_trace=synthetic_trace,
            closed_loop_milestone_audit=closed_loop,
            trace_spine_boundary=boundary,
        )
        self.assertEqual(blocked_production.audit_status, "blocked_production_behavior_detected")

        readiness = link.build_demo_mark_uncertain_home_surface_link()[
            "internal_action_home_surface_link_readiness"
        ]
        self.assertEqual(
            readiness["readiness_status"],
            "ready_for_runtime_state_summary_session_shell_only",
        )
        for field_name in (
            "ready_for_runtime_state_summary_session_shell",
            "ready_for_bounded_embodied_loop_runner",
            "ready_for_no_codex_teacher_console_flow",
            "ready_for_session_end_review_promote_gate",
            "ready_for_no_codex_fixture_growth_loop_milestone_audit",
        ):
            self.assertTrue(readiness[field_name])
        for field_name in (
            "ready_for_unity_runtime_connection",
            "ready_for_actual_screen_mutation",
            "ready_for_external_control",
            "ready_for_task_engine_action_selection",
            "ready_for_long_term_memory_write",
            "ready_for_core_memory_write",
            "ready_for_first_output",
            "ready_for_live_runtime_session",
        ):
            self.assertFalse(readiness[field_name])
        self.assertTrue(link.validate_internal_action_home_surface_link_readiness(readiness)["valid"])

    def test_cli_guided_console_docs_and_repo_data_boundary(self) -> None:
        cli_commands = [
            ("show-demo-uncertainty",),
            ("show-demo-teacher-review",),
            ("show-demo-observe-again",),
            ("show-demo-interesting",),
            ("show-demo-pause",),
            ("show-demo-update-home-status",),
            ("show-demo-mixed",),
            ("show-demo-readiness",),
            ("validate-demo-home-surface-link",),
            ("show-demo-blocked", "--case", "unity-runtime"),
            ("show-demo-blocked", "--case", "screen-mutation"),
            ("show-demo-blocked", "--case", "sound-output"),
            ("show-demo-blocked", "--case", "external-message"),
            ("show-demo-blocked", "--case", "file-write"),
            ("show-demo-blocked", "--case", "network-output"),
            ("show-demo-blocked", "--case", "task-selected-action"),
            ("show-demo-blocked", "--case", "direct-command"),
            ("show-demo-blocked", "--case", "memory-write"),
            ("show-demo-blocked", "--case", "first-output"),
            ("show-demo-blocked", "--case", "live-runtime"),
        ]
        for command in cli_commands:
            with self.subTest(command=command):
                result = subprocess.run(
                    ["py", "-3", "-m", LINK_CLI, *command],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                self.assertTrue(json.loads(result.stdout))

        guided = validate_host_body_home_surface_link_from_guided_cradle_growth_console()
        self.assertEqual(guided["guided_console_action"], "host_body_validate_home_surface_link_demo")
        self.assertTrue(guided["validation"]["valid"])
        self.assertFalse(guided["unity_runtime_started"])
        self.assertFalse(guided["actual_screen_mutated"])
        self.assertFalse(guided["first_output_created"])
        self.assertFalse(guided["live_runtime_session_created"])

        guided_commands = [
            "host-body-show-home-surface-link-uncertainty-demo",
            "host-body-show-home-surface-link-teacher-review-demo",
            "host-body-show-home-surface-link-observe-again-demo",
            "host-body-show-home-surface-link-interesting-demo",
            "host-body-show-home-surface-link-pause-demo",
            "host-body-show-home-surface-link-update-status-demo",
            "host-body-show-home-surface-link-mixed-demo",
            "host-body-show-home-surface-link-readiness",
            "host-body-validate-home-surface-link-demo",
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

        doc = Path("ashl_core_v1/docs/internal_action_home_surface_link_v0.md")
        self.assertTrue(doc.exists())
        self.assertIn("GCMC", Path("ashl_core_v1/docs/future_age_grounded_concept_memory_compilation_gcmc_v0_3.md").read_text(encoding="utf-8"))
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _plan(self) -> object:
        closed_loop, home_audit, boundary = link._demo_sources()
        return link.build_internal_action_home_surface_link_plan(
            closed_loop_milestone_audit=closed_loop,
            home_surface_audit=home_audit,
            trace_spine_boundary=boundary,
        )


if __name__ == "__main__":
    unittest.main()
