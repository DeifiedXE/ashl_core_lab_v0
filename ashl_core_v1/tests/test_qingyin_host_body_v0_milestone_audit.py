from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

from ashl_core_v1.host_body import qingyin_host_body_v0_milestone_audit as milestone
from ashl_core_v1.runtime.guided_cradle_growth_teacher_console import (
    validate_host_body_v0_milestone_from_guided_cradle_growth_console,
)


MILESTONE_CLI = "ashl_core_v1.host_body.qingyin_host_body_v0_milestone_audit_cli"
GUIDED_CLI = "ashl_core_v1.runtime.guided_cradle_growth_teacher_console_cli"


class QingyinHostBodyV0MilestoneAuditTests(unittest.TestCase):
    def test_milestone_scope_builds_and_blocks_missing_pillars_or_forbidden_scope(self) -> None:
        scope = milestone.build_qingyin_host_body_v0_milestone_scope()
        self.assertEqual(scope.scope_status, "host_body_v0_scope_created")
        self.assertEqual(scope.included_packages, milestone.INCLUDED_PACKAGES)
        self.assertEqual(scope.included_commits, milestone.INCLUDED_COMMITS)
        self.assertTrue(scope.host_body_identity_required)
        self.assertTrue(scope.sensor_event_shell_required)
        self.assertTrue(scope.runtime_eventframe_bridge_required)
        self.assertTrue(scope.qingyin_home_surface_required)
        self.assertTrue(scope.trace_history_lane_required)
        self.assertTrue(scope.internal_action_choice_required)
        self.assertFalse(scope.real_hardware_allowed)
        self.assertFalse(scope.external_control_allowed)
        self.assertFalse(scope.memory_write_allowed)
        self.assertFalse(scope.first_output_allowed)
        self.assertFalse(scope.live_runtime_allowed)
        self.assertTrue(milestone.validate_qingyin_host_body_v0_milestone_scope(scope)["valid"])

        for pillar in milestone.INCLUDED_PILLARS:
            with self.subTest(pillar=pillar):
                included = tuple(item for item in milestone.INCLUDED_PILLARS if item != pillar)
                self.assertEqual(
                    milestone.build_qingyin_host_body_v0_milestone_scope(
                        included_pillars=included
                    ).scope_status,
                    "blocked_missing_required_pillar",
                )

        forbidden = {
            "real": {"real_hardware_allowed": True},
            "external": {"external_control_allowed": True},
            "memory": {"memory_write_allowed": True},
            "first": {"first_output_allowed": True},
            "live": {"live_runtime_allowed": True},
        }
        for case, kwargs in forbidden.items():
            with self.subTest(case=case):
                self.assertEqual(
                    milestone.build_qingyin_host_body_v0_milestone_scope(**kwargs).scope_status,
                    "blocked_forbidden_capability_in_scope",
                )

    def test_capability_ledger_confirms_six_packages_and_blocks_missing_or_new_capability(self) -> None:
        scope = milestone.build_qingyin_host_body_v0_milestone_scope()
        ledger = milestone.build_qingyin_host_body_v0_capability_ledger(milestone_scope=scope)
        self.assertEqual(
            ledger.capability_ledger_status,
            "host_body_v0_capability_ledger_recorded",
        )
        self.assertTrue(ledger.host_body_identity_capability_confirmed)
        self.assertTrue(ledger.host_body_port_map_capability_confirmed)
        self.assertTrue(ledger.fixture_sensor_event_capability_confirmed)
        self.assertTrue(ledger.runtime_eventframe_bridge_capability_confirmed)
        self.assertTrue(ledger.home_internal_space_surface_capability_confirmed)
        self.assertTrue(ledger.trace_history_lane_capability_confirmed)
        self.assertTrue(ledger.internal_action_choice_capability_confirmed)
        self.assertFalse(ledger.new_capability_created_by_this_package)
        self.assertGreaterEqual(ledger.capability_count, 7)
        self.assertTrue(milestone.validate_qingyin_host_body_v0_capability_ledger(ledger)["valid"])

        blocked = {
            "package_101_identity": (
                {"host_body_identity_capability_confirmed": False},
                "blocked_missing_host_body_identity_capability",
            ),
            "package_101_port": (
                {"host_body_port_map_capability_confirmed": False},
                "blocked_missing_host_body_identity_capability",
            ),
            "package_102": (
                {"fixture_sensor_event_capability_confirmed": False},
                "blocked_missing_sensor_event_capability",
            ),
            "package_103": (
                {"runtime_eventframe_bridge_capability_confirmed": False},
                "blocked_missing_runtime_bridge_capability",
            ),
            "package_104": (
                {"home_internal_space_surface_capability_confirmed": False},
                "blocked_missing_home_surface_capability",
            ),
            "package_105": (
                {"trace_history_lane_capability_confirmed": False},
                "blocked_missing_trace_history_capability",
            ),
            "package_106": (
                {"internal_action_choice_capability_confirmed": False},
                "blocked_missing_internal_action_choice_capability",
            ),
            "new": (
                {"new_capability_created_by_this_package": True},
                "blocked_unexpected_new_capability_detected",
            ),
        }
        for case, (kwargs, expected_status) in blocked.items():
            with self.subTest(case=case):
                self.assertEqual(
                    milestone.build_qingyin_host_body_v0_capability_ledger(
                        milestone_scope=scope,
                        **kwargs,
                    ).capability_ledger_status,
                    expected_status,
                )

    def test_boundary_ledger_confirms_absences_and_blocks_forbidden_boundaries(self) -> None:
        scope = milestone.build_qingyin_host_body_v0_milestone_scope()
        ledger = milestone.build_qingyin_host_body_v0_boundary_ledger(milestone_scope=scope)
        self.assertEqual(ledger.boundary_ledger_status, "host_body_v0_boundary_ledger_recorded")
        self.assertTrue(ledger.no_real_camera_access)
        self.assertTrue(ledger.no_real_microphone_access)
        self.assertTrue(ledger.no_semantic_vision)
        self.assertTrue(ledger.no_speech_recognition)
        self.assertTrue(ledger.no_task_engine_selected_action)
        self.assertTrue(ledger.no_final_action)
        self.assertTrue(ledger.no_direct_command)
        self.assertTrue(ledger.no_sandbox_execution)
        self.assertTrue(ledger.no_external_control)
        self.assertTrue(ledger.no_unity_runtime_connection)
        self.assertTrue(ledger.no_avatar_control)
        self.assertTrue(ledger.no_memory_layer_write)
        self.assertTrue(ledger.no_long_term_memory_write)
        self.assertTrue(ledger.no_state_persistence_write)
        self.assertTrue(ledger.no_learning_candidate_creation)
        self.assertTrue(ledger.no_automatic_learning_approval)
        self.assertTrue(ledger.no_teacher_approval_created)
        self.assertTrue(ledger.no_first_output)
        self.assertTrue(ledger.no_live_runtime_session)
        self.assertTrue(ledger.no_production_behavior)
        self.assertTrue(milestone.validate_qingyin_host_body_v0_boundary_ledger(ledger)["valid"])

        blocked = {
            "hardware": ({"no_real_camera_access": False}, "blocked_real_hardware_detected"),
            "semantic": ({"no_semantic_vision": False}, "blocked_semantic_interpretation_detected"),
            "task": ({"no_task_engine_selected_action": False}, "blocked_task_action_detected"),
            "external": ({"no_mouse_control": False}, "blocked_external_control_detected"),
            "unity": ({"no_unity_runtime_connection": False}, "blocked_unity_runtime_detected"),
            "memory": ({"no_memory_layer_write": False}, "blocked_memory_write_detected"),
            "learning": ({"no_learning_candidate_creation": False}, "blocked_learning_creation_detected"),
            "first": ({"no_first_output": False}, "blocked_first_output_detected"),
            "live": ({"no_live_runtime_session": False}, "blocked_live_runtime_detected"),
            "production": ({"no_production_behavior": False}, "blocked_production_behavior_detected"),
        }
        for case, (kwargs, expected_status) in blocked.items():
            with self.subTest(case=case):
                self.assertEqual(
                    milestone.build_qingyin_host_body_v0_boundary_ledger(
                        milestone_scope=scope,
                        **kwargs,
                    ).boundary_ledger_status,
                    expected_status,
                )

    def test_integrated_trace_records_six_steps_and_blocks_missing_or_forbidden_runtime_behavior(self) -> None:
        scope = milestone.build_qingyin_host_body_v0_milestone_scope()
        trace = milestone.build_qingyin_host_body_v0_integrated_trace(milestone_scope=scope)
        self.assertEqual(
            trace.integrated_trace_status,
            "host_body_v0_integrated_trace_recorded",
        )
        self.assertEqual(trace.step_count, 6)
        self.assertTrue(trace.port_map_step_confirmed)
        self.assertTrue(trace.sensor_event_step_confirmed)
        self.assertTrue(trace.runtime_bridge_step_confirmed)
        self.assertTrue(trace.home_surface_step_confirmed)
        self.assertTrue(trace.trace_history_step_confirmed)
        self.assertTrue(trace.internal_action_choice_step_confirmed)
        self.assertTrue(milestone.validate_qingyin_host_body_v0_integrated_trace(trace)["valid"])

        blocked = {
            "port": ({"port_map_step_confirmed": False}, "blocked_missing_port_map_step"),
            "sensor": ({"sensor_event_step_confirmed": False}, "blocked_missing_sensor_event_step"),
            "runtime": (
                {"runtime_bridge_step_confirmed": False},
                "blocked_missing_runtime_bridge_step",
            ),
            "home": ({"home_surface_step_confirmed": False}, "blocked_missing_home_surface_step"),
            "trace": ({"trace_history_step_confirmed": False}, "blocked_missing_trace_history_step"),
            "action": (
                {"internal_action_choice_step_confirmed": False},
                "blocked_missing_internal_action_choice_step",
            ),
            "runtime_behavior": (
                {"new_runtime_behavior_created": True},
                "blocked_forbidden_runtime_behavior_detected",
            ),
            "authority": (
                {"new_first_output_created": True},
                "blocked_forbidden_authority_detected",
            ),
        }
        for case, (kwargs, expected_status) in blocked.items():
            with self.subTest(case=case):
                self.assertEqual(
                    milestone.build_qingyin_host_body_v0_integrated_trace(
                        milestone_scope=scope,
                        **kwargs,
                    ).integrated_trace_status,
                    expected_status,
                )

    def test_milestone_audit_passes_and_blocked_demos_cover_required_failures(self) -> None:
        payload = milestone.build_demo_qingyin_host_body_v0_milestone_pass()
        audit = payload["host_body_v0_milestone_audit"]
        self.assertEqual(audit["audit_status"], "passed_qingyin_host_body_v0_milestone")
        self.assertTrue(audit["host_body_v0_established"])
        self.assertTrue(audit["audit_only_package_confirmed"])
        self.assertFalse(audit["new_capability_created_by_this_package"])
        for package_number in range(101, 107):
            self.assertTrue(audit[f"package_{package_number}_verified"])
        self.assertTrue(milestone.validate_qingyin_host_body_v0_milestone_audit(audit)["valid"])

        scope = milestone.build_qingyin_host_body_v0_milestone_scope()
        capability = milestone.build_qingyin_host_body_v0_capability_ledger(milestone_scope=scope)
        boundary = milestone.build_qingyin_host_body_v0_boundary_ledger(milestone_scope=scope)
        trace = milestone.build_qingyin_host_body_v0_integrated_trace(milestone_scope=scope)
        self.assertEqual(
            milestone.build_qingyin_host_body_v0_milestone_audit(
                milestone_scope=None,
                capability_ledger=capability,
                boundary_ledger=boundary,
                integrated_trace=trace,
            ).audit_status,
            "blocked_missing_scope",
        )
        self.assertEqual(
            milestone.build_qingyin_host_body_v0_milestone_audit(
                milestone_scope=scope,
                capability_ledger=None,
                boundary_ledger=boundary,
                integrated_trace=trace,
            ).audit_status,
            "blocked_missing_capability_ledger",
        )
        self.assertEqual(
            milestone.build_qingyin_host_body_v0_milestone_audit(
                milestone_scope=scope,
                capability_ledger=capability,
                boundary_ledger=None,
                integrated_trace=trace,
            ).audit_status,
            "blocked_missing_boundary_ledger",
        )
        self.assertEqual(
            milestone.build_qingyin_host_body_v0_milestone_audit(
                milestone_scope=scope,
                capability_ledger=capability,
                boundary_ledger=boundary,
                integrated_trace=None,
            ).audit_status,
            "blocked_missing_integrated_trace",
        )

        blocked = {
            "sensor": (
                milestone.build_demo_missing_sensor_event_pillar(),
                "blocked_package_102_unverified",
            ),
            "runtime": (
                milestone.build_demo_missing_runtime_bridge_pillar(),
                "blocked_package_103_unverified",
            ),
            "home": (
                milestone.build_demo_missing_home_surface_pillar(),
                "blocked_package_104_unverified",
            ),
            "trace": (
                milestone.build_demo_missing_trace_history_pillar(),
                "blocked_package_105_unverified",
            ),
            "action": (
                milestone.build_demo_missing_internal_action_choice_pillar(),
                "blocked_package_106_unverified",
            ),
            "new": (
                milestone.build_demo_blocked_unexpected_new_capability(),
                "blocked_unexpected_new_capability_detected",
            ),
            "external": (
                milestone.build_demo_blocked_external_control_host_body_v0(),
                "blocked_external_control_detected",
            ),
            "memory": (
                milestone.build_demo_blocked_memory_write_host_body_v0(),
                "blocked_memory_write_detected",
            ),
            "first": (
                milestone.build_demo_blocked_first_output_host_body_v0(),
                "blocked_first_output_detected",
            ),
            "live": (
                milestone.build_demo_blocked_live_runtime_host_body_v0(),
                "blocked_live_runtime_detected",
            ),
        }
        for case, (payload, expected_status) in blocked.items():
            with self.subTest(case=case):
                self.assertEqual(
                    payload["host_body_v0_milestone_audit"]["audit_status"],
                    expected_status,
                )
                self.assertFalse(payload["host_body_v0_milestone_audit"]["host_body_v0_established"])

    def test_readiness_recommends_next_bounded_host_body_steps_only(self) -> None:
        payload = milestone.build_demo_qingyin_host_body_v0_milestone_pass()
        readiness = payload["host_body_v0_readiness"]
        self.assertEqual(
            readiness["readiness_status"],
            "ready_for_internal_action_home_surface_link_only",
        )
        self.assertTrue(readiness["ready_for_internal_action_home_surface_link"])
        self.assertTrue(readiness["ready_for_teacher_observed_host_body_cli"])
        self.assertTrue(readiness["ready_for_runtime_state_persistence_binding"])
        self.assertTrue(readiness["ready_for_host_body_v0_to_runtime_state_summary"])
        self.assertFalse(readiness["ready_for_real_camera_connection"])
        self.assertFalse(readiness["ready_for_real_microphone_connection"])
        self.assertFalse(readiness["ready_for_semantic_vision"])
        self.assertFalse(readiness["ready_for_speech_recognition"])
        self.assertFalse(readiness["ready_for_task_engine_action_selection"])
        self.assertFalse(readiness["ready_for_external_control"])
        self.assertFalse(readiness["ready_for_unity_runtime_connection"])
        self.assertFalse(readiness["ready_for_memory_layer_write"])
        self.assertFalse(readiness["ready_for_learning_candidate_creation"])
        self.assertFalse(readiness["ready_for_first_output"])
        self.assertFalse(readiness["ready_for_live_runtime_session"])
        self.assertTrue(milestone.validate_qingyin_host_body_v0_readiness(readiness)["valid"])

    def test_cli_commands_work(self) -> None:
        commands = {
            ("show-demo-pass",): "passed_qingyin_host_body_v0_milestone",
            ("show-demo-scope",): "host_body_v0_scope_created",
            ("show-demo-capability-ledger",): "host_body_v0_capability_ledger_recorded",
            ("show-demo-boundary-ledger",): "host_body_v0_boundary_ledger_recorded",
            ("show-demo-integrated-trace",): "host_body_v0_integrated_trace_recorded",
            ("show-demo-readiness",): "ready_for_internal_action_home_surface_link_only",
            ("validate-demo-host-body-v0",): "passed_qingyin_host_body_v0_milestone",
            ("show-demo-blocked", "--case", "missing-sensor-event"): "blocked_package_102_unverified",
            ("show-demo-blocked", "--case", "missing-runtime-bridge"): "blocked_package_103_unverified",
            ("show-demo-blocked", "--case", "missing-home-surface"): "blocked_package_104_unverified",
            ("show-demo-blocked", "--case", "missing-trace-history"): "blocked_package_105_unverified",
            ("show-demo-blocked", "--case", "missing-internal-action-choice"): "blocked_package_106_unverified",
            ("show-demo-blocked", "--case", "unexpected-new-capability"): "blocked_unexpected_new_capability_detected",
            ("show-demo-blocked", "--case", "external-control"): "blocked_external_control_detected",
            ("show-demo-blocked", "--case", "memory-write"): "blocked_memory_write_detected",
            ("show-demo-blocked", "--case", "first-output"): "blocked_first_output_detected",
            ("show-demo-blocked", "--case", "live-runtime"): "blocked_live_runtime_detected",
        }
        for command, expected_text in commands.items():
            with self.subTest(command=command):
                payload = self._run_json(MILESTONE_CLI, *command)
                self.assertIn(expected_text, json.dumps(payload, sort_keys=True))

    def test_guided_console_host_body_v0_milestone_demo_works(self) -> None:
        validation = validate_host_body_v0_milestone_from_guided_cradle_growth_console()
        self.assertEqual(validation["guided_console_action"], "host_body_validate_v0_milestone_demo")
        self.assertTrue(validation["validation"]["valid"])
        self.assertFalse(validation["new_host_body_capability_created"])
        self.assertFalse(validation["real_hardware_access_created"])
        self.assertFalse(validation["external_control_created"])
        self.assertFalse(validation["memory_layer_write_performed"])
        self.assertFalse(validation["teacher_approval_created"])
        self.assertFalse(validation["first_output_created"])
        self.assertFalse(validation["live_runtime_session_created"])
        self.assertFalse(validation["production_behavior_created"])

        commands = {
            "host-body-show-v0-milestone-pass-demo": "passed_qingyin_host_body_v0_milestone",
            "host-body-show-v0-scope-demo": "host_body_v0_scope_created",
            "host-body-show-v0-capability-ledger-demo": "host_body_v0_capability_ledger_recorded",
            "host-body-show-v0-boundary-ledger-demo": "host_body_v0_boundary_ledger_recorded",
            "host-body-show-v0-integrated-trace-demo": "host_body_v0_integrated_trace_recorded",
            "host-body-show-v0-readiness": "ready_for_internal_action_home_surface_link_only",
            "host-body-validate-v0-milestone-demo": "passed_qingyin_host_body_v0_milestone",
        }
        for command, expected_text in commands.items():
            with self.subTest(command=command):
                payload = self._run_json(GUIDED_CLI, command)
                self.assertIn(expected_text, json.dumps(payload, sort_keys=True))

    def test_no_repo_data_directory_created(self) -> None:
        self.assertFalse(Path("ashl_core_v1/data").exists())

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
