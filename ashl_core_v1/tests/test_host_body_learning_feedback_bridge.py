from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

from ashl_core_v1.host_body import host_body_learning_feedback_bridge as bridge
from ashl_core_v1.host_body.host_body_internal_action_choice import (
    build_demo_camera_change_marks_interesting,
    build_demo_host_idle_observe_again,
    build_demo_update_home_status_choice,
    build_host_body_internal_action_candidate,
    build_host_body_internal_action_choice,
    build_host_body_internal_action_choice_audit,
    build_host_body_internal_action_choice_plan,
    build_host_body_internal_action_choice_set,
    build_host_body_internal_action_result,
    build_host_body_internal_action_surface_effect,
)
from ashl_core_v1.host_body.host_body_runtime_bridge import (
    build_demo_deferred_dispatch_host_body_runtime_bridge,
)
from ashl_core_v1.host_body.host_body_trace_history_lane import (
    build_demo_full_host_body_trace_history_lane,
)
from ashl_core_v1.host_body.qingyin_home_internal_space_surface import (
    build_demo_qingyin_home_internal_space_surface,
)
from ashl_core_v1.host_body.qingyin_host_body_v0_milestone_audit import (
    build_demo_qingyin_host_body_v0_milestone_pass,
)
from ashl_core_v1.runtime.guided_cradle_growth_teacher_console import (
    validate_host_body_learning_bridge_from_guided_cradle_growth_console,
)


BRIDGE_CLI = "ashl_core_v1.host_body.host_body_learning_feedback_bridge_cli"
GUIDED_CLI = "ashl_core_v1.runtime.guided_cradle_growth_teacher_console_cli"


class HostBodyLearningFeedbackBridgeTests(unittest.TestCase):
    def test_bridge_plan_builds_and_blocks_forbidden_authority(self) -> None:
        v0_audit, trace_audit, action_audit = self._plan_inputs()
        plan = bridge.build_host_body_learning_bridge_plan(
            host_body_v0_audit=v0_audit,
            trace_history_audit=trace_audit,
            internal_action_choice_audit=action_audit,
        )
        self.assertEqual(plan.bridge_plan_status, "host_body_learning_bridge_plan_created")
        self.assertTrue(plan.learning_feedback_candidate_allowed)
        self.assertIn("host_body_trace_history_readback", plan.allowed_evidence_sources)
        self.assertIn("host_body_uncertainty_feedback_candidate", plan.allowed_feedback_candidate_kinds)
        self.assertFalse(plan.concept_candidate_allowed)
        self.assertFalse(plan.reviewed_concept_allowed)
        self.assertFalse(plan.memory_write_allowed)
        self.assertFalse(plan.automatic_learning_approval_allowed)
        self.assertFalse(plan.teacher_approval_creation_allowed)
        self.assertFalse(plan.task_action_selection_allowed)
        self.assertFalse(plan.external_control_allowed)
        self.assertFalse(plan.first_output_allowed)
        self.assertFalse(plan.live_runtime_session_allowed)
        self.assertTrue(bridge.validate_host_body_learning_bridge_plan(plan)["valid"])

        blocked = {
            "v0": (
                {"host_body_v0_audit": None},
                "blocked_missing_host_body_v0_audit",
            ),
            "trace": (
                {"trace_history_audit": None},
                "blocked_missing_trace_history_audit",
            ),
            "action": (
                {"internal_action_choice_audit": None},
                "blocked_missing_internal_action_choice_audit",
            ),
            "concept": (
                {"concept_candidate_allowed": True},
                "blocked_concept_candidate_allowed",
            ),
            "reviewed": (
                {"reviewed_concept_allowed": True},
                "blocked_reviewed_concept_allowed",
            ),
            "memory": (
                {"memory_write_allowed": True},
                "blocked_memory_write_allowed",
            ),
            "auto": (
                {"automatic_learning_approval_allowed": True},
                "blocked_memory_write_allowed",
            ),
            "teacher": (
                {"teacher_approval_creation_allowed": True},
                "blocked_memory_write_allowed",
            ),
            "action_selection": (
                {"task_action_selection_allowed": True},
                "blocked_action_selection_allowed",
            ),
            "external": (
                {"external_control_allowed": True},
                "blocked_action_selection_allowed",
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
                    "host_body_v0_audit": v0_audit,
                    "trace_history_audit": trace_audit,
                    "internal_action_choice_audit": action_audit,
                    **kwargs,
                }
                self.assertEqual(
                    bridge.build_host_body_learning_bridge_plan(**args).bridge_plan_status,
                    expected_status,
                )

    def test_evidence_packet_records_allowed_themes_and_blocks_forbidden_outputs(self) -> None:
        cases = {
            "uncertainty": (
                bridge.build_demo_uncertainty_to_learning_feedback_candidate(),
                "uncertainty_detected",
            ),
            "interesting": (
                bridge.build_demo_interesting_event_to_learning_feedback_candidate(),
                "interesting_event_marked",
            ),
            "teacher": (
                bridge.build_demo_teacher_review_request_to_learning_feedback_candidate(),
                "teacher_review_requested",
            ),
            "deferred": (
                bridge.build_demo_deferred_runtime_bridge_to_learning_feedback_candidate(),
                "runtime_bridge_deferred",
            ),
        }
        for case, (payload, theme) in cases.items():
            with self.subTest(case=case):
                packet = payload["host_body_learning_evidence_packets"][0]
                self.assertEqual(packet["evidence_theme"], theme)
                self.assertTrue(packet["teacher_review_required"])
                self.assertTrue(packet["safe_for_learning_feedback_candidate"])
                self.assertFalse(packet["concept_candidate_created"])
                self.assertFalse(packet["reviewed_concept_created"])
                self.assertFalse(packet["memory_write_performed"])
                self.assertFalse(packet["teacher_approval_created"])
                self.assertFalse(packet["first_output_created"])
                self.assertFalse(packet["live_runtime_session_created"])
                self.assertTrue(bridge.validate_host_body_learning_evidence_packet(packet)["valid"])

        plan, trace_readback, action_choice, action_result, runtime_trace, teacher_surface = self._evidence_inputs()
        extra_themes = {
            "observe_again_requested": build_demo_host_idle_observe_again(),
            "home_status_updated": build_demo_update_home_status_choice(),
            "event_processing_paused": self._action_payload_for_kind("pause_event_processing"),
            "unknown_event_seen": build_demo_camera_change_marks_interesting(),
        }
        for theme, action_payload in extra_themes.items():
            with self.subTest(theme=theme):
                packet = bridge.build_host_body_learning_evidence_packet(
                    bridge_plan=plan,
                    trace_history_readback=trace_readback,
                    internal_action_choice=action_payload["internal_action_choice"],
                    internal_action_result=action_payload["internal_action_result"],
                    runtime_bridge_trace=runtime_trace,
                    teacher_observed_surface=teacher_surface,
                    evidence_theme=theme,
                )
                self.assertEqual(packet.evidence_theme, theme)
                self.assertTrue(bridge.validate_host_body_learning_evidence_packet(packet)["valid"])

        blocked_flags = {
            "semantic": "semantic_interpretation_created",
            "speech": "speech_recognition_created",
            "action": "task_action_selection_influence_created",
            "external": "external_control_created",
            "memory": "memory_write_performed",
            "concept": "concept_candidate_created",
            "reviewed": "reviewed_concept_created",
            "auto": "automatic_learning_approval_created",
            "teacher": "teacher_approval_created",
            "first": "first_output_created",
            "live": "live_runtime_session_created",
        }
        for case, flag in blocked_flags.items():
            with self.subTest(case=case):
                packet = bridge.build_host_body_learning_evidence_packet(
                    bridge_plan=plan,
                    trace_history_readback=trace_readback,
                    internal_action_choice=action_choice,
                    internal_action_result=action_result,
                    runtime_bridge_trace=runtime_trace,
                    teacher_observed_surface=teacher_surface,
                    **{flag: True},
                )
                self.assertEqual(packet.evidence_kind, "blocked_evidence")
                self.assertFalse(bridge.validate_host_body_learning_evidence_packet(packet)["valid"])

    def test_mapping_bridge_and_candidate_set_record_bridge_compatible_candidates(self) -> None:
        payload = bridge.build_demo_uncertainty_to_learning_feedback_candidate()
        mapping = payload["host_body_learning_feedback_mappings"][0]
        feedback_bridge = payload["host_body_learning_feedback_bridges"][0]
        candidate_set = payload["host_body_learning_feedback_candidate_set"]
        self.assertEqual(mapping["mapping_kind"], "host_body_evidence_to_bridge_compatible_candidate")
        self.assertEqual(mapping["mapping_status"], "host_body_evidence_mapped_to_bridge_compatible_candidate")
        self.assertEqual(mapping["feedback_candidate_kind"], "host_body_uncertainty_feedback_candidate")
        self.assertFalse(mapping["candidate_created"])
        self.assertTrue(mapping["candidate_bridge_ready"])
        self.assertTrue(bridge.validate_host_body_learning_feedback_candidate_mapping(mapping)["valid"])
        self.assertEqual(feedback_bridge["bridge_status"], "host_body_learning_feedback_candidate_bridge_ready")
        self.assertFalse(feedback_bridge["learning_feedback_candidate_created"])
        self.assertTrue(feedback_bridge["learning_feedback_candidate_bridge_ready"])
        self.assertTrue(feedback_bridge["teacher_review_required"])
        self.assertFalse(feedback_bridge["teacher_approval_created"])
        self.assertTrue(bridge.validate_host_body_learning_feedback_candidate_bridge(feedback_bridge)["valid"])
        self.assertEqual(candidate_set["candidate_set_status"], "host_body_learning_feedback_candidate_set_recorded")
        self.assertEqual(candidate_set["evidence_packet_count"], 1)
        self.assertEqual(candidate_set["mapping_count"], 1)
        self.assertEqual(candidate_set["bridge_count"], 1)
        self.assertEqual(candidate_set["learning_feedback_candidate_count"], 0)
        self.assertEqual(candidate_set["teacher_review_required_count"], 1)
        self.assertTrue(bridge.validate_host_body_learning_feedback_candidate_set(candidate_set)["valid"])

        mixed = bridge.build_demo_host_body_learning_feedback_candidate_set()
        mixed_set = mixed["host_body_learning_feedback_candidate_set"]
        self.assertEqual(mixed_set["candidate_set_kind"], "mixed_host_body_feedback_candidate_demo")
        self.assertEqual(mixed_set["candidate_set_status"], "host_body_learning_feedback_candidate_set_recorded")
        self.assertEqual(mixed_set["evidence_packet_count"], 3)

        plan, trace_readback, action_choice, action_result, runtime_trace, teacher_surface = self._evidence_inputs()
        packet = bridge.build_host_body_learning_evidence_packet(
            bridge_plan=plan,
            trace_history_readback=trace_readback,
            internal_action_choice=action_choice,
            internal_action_result=action_result,
            runtime_bridge_trace=runtime_trace,
            teacher_observed_surface=teacher_surface,
            concept_candidate_created=True,
        )
        mapping = bridge.map_host_body_evidence_to_learning_feedback_candidate(evidence_packet=packet)
        self.assertEqual(mapping.mapping_status, "blocked_concept_candidate_creation_detected")
        feedback_bridge = bridge.build_host_body_learning_feedback_candidate_bridge(
            bridge_plan=plan,
            evidence_packet=packet,
            mapping=mapping,
        )
        self.assertEqual(feedback_bridge.bridge_status, "blocked_invalid_mapping")

    def test_audit_passes_expected_demo_statuses_and_blocks_forbidden_authority(self) -> None:
        expected = {
            "uncertainty": (
                bridge.build_demo_uncertainty_to_learning_feedback_candidate(),
                "passed_host_body_uncertainty_feedback_candidate_bridge",
            ),
            "interesting": (
                bridge.build_demo_interesting_event_to_learning_feedback_candidate(),
                "passed_host_body_interesting_event_feedback_candidate_bridge",
            ),
            "teacher": (
                bridge.build_demo_teacher_review_request_to_learning_feedback_candidate(),
                "passed_host_body_teacher_review_feedback_candidate_bridge",
            ),
            "runtime": (
                bridge.build_demo_deferred_runtime_bridge_to_learning_feedback_candidate(),
                "passed_host_body_runtime_bridge_feedback_candidate_bridge",
            ),
            "mixed": (
                bridge.build_demo_host_body_learning_feedback_candidate_set(),
                "passed_host_body_evidence_to_learning_feedback_candidate_bridge",
            ),
        }
        for case, (payload, expected_status) in expected.items():
            with self.subTest(case=case):
                audit = payload["host_body_learning_bridge_audit"]
                self.assertEqual(audit["audit_status"], expected_status)
                self.assertTrue(audit["host_body_v0_confirmed"])
                self.assertTrue(audit["learning_feedback_candidate_stage_only_confirmed"])
                self.assertTrue(audit["teacher_review_required_confirmed"])
                self.assertFalse(audit["no_concept_candidate_created"] is False)
                self.assertTrue(bridge.validate_host_body_learning_bridge_audit(audit)["valid"])

        blocked = {
            "concept": (
                bridge.build_demo_blocked_concept_candidate_creation(),
                "blocked_concept_candidate_created",
            ),
            "reviewed": (
                bridge.build_demo_blocked_reviewed_concept_creation(),
                "blocked_reviewed_concept_created",
            ),
            "memory": (
                bridge.build_demo_blocked_memory_write_learning_bridge(),
                "blocked_memory_write_detected",
            ),
            "action": (
                bridge.build_demo_blocked_action_influence_learning_bridge(),
                "blocked_action_selection_influence_detected",
            ),
            "first": (
                bridge.build_demo_blocked_first_output_learning_bridge(),
                "blocked_first_output_detected",
            ),
            "live": (
                bridge.build_demo_blocked_live_runtime_learning_bridge(),
                "blocked_live_runtime_detected",
            ),
        }
        for case, (payload, expected_status) in blocked.items():
            with self.subTest(case=case):
                self.assertEqual(payload["host_body_learning_bridge_audit"]["audit_status"], expected_status)

        plan, trace_readback, action_choice, action_result, runtime_trace, teacher_surface = self._evidence_inputs()
        packet = bridge.build_host_body_learning_evidence_packet(
            bridge_plan=plan,
            trace_history_readback=trace_readback,
            internal_action_choice=action_choice,
            internal_action_result=action_result,
            runtime_bridge_trace=runtime_trace,
            teacher_observed_surface=teacher_surface,
        )
        mapping = bridge.map_host_body_evidence_to_learning_feedback_candidate(evidence_packet=packet)
        feedback_bridge = bridge.build_host_body_learning_feedback_candidate_bridge(
            bridge_plan=plan,
            evidence_packet=packet,
            mapping=mapping,
            automatic_learning_approval_created=True,
        )
        candidate_set = bridge.build_host_body_learning_feedback_candidate_set(
            bridge_plan=plan,
            evidence_packets=(packet,),
            mappings=(mapping,),
            bridges=(feedback_bridge,),
        )
        audit = bridge.build_host_body_learning_bridge_audit(
            bridge_plan=plan,
            evidence_packets=(packet,),
            mappings=(mapping,),
            bridges=(feedback_bridge,),
            candidate_set=candidate_set,
        )
        self.assertEqual(audit.audit_status, "blocked_automatic_learning_approval_detected")

        audit = bridge.build_host_body_learning_bridge_audit(
            bridge_plan=plan,
            evidence_packets=(packet,),
            mappings=(mapping,),
            bridges=(feedback_bridge,),
            candidate_set=candidate_set,
            force_external_control=True,
        )
        self.assertEqual(audit.audit_status, "blocked_automatic_learning_approval_detected")
        self.assertEqual(
            bridge.build_host_body_learning_bridge_audit(
                bridge_plan=None,
            ).audit_status,
            "blocked_missing_bridge_plan",
        )
        self.assertEqual(
            bridge.build_host_body_learning_bridge_audit(
                bridge_plan=plan,
                force_production_behavior=True,
            ).audit_status,
            "blocked_production_behavior_detected",
        )

    def test_readiness_recommends_teacher_review_only(self) -> None:
        payload = bridge.build_demo_uncertainty_to_learning_feedback_candidate()
        readiness = payload["host_body_learning_bridge_readiness"]
        self.assertEqual(
            readiness["readiness_status"],
            "ready_for_teacher_review_of_host_body_feedback_only",
        )
        self.assertTrue(readiness["ready_for_teacher_review_of_host_body_feedback"])
        self.assertTrue(readiness["ready_for_host_body_feedback_to_concept_candidate_review"])
        self.assertTrue(readiness["ready_for_host_body_feedback_closed_loop_replay"])
        self.assertFalse(readiness["ready_for_concept_candidate_auto_creation"])
        self.assertFalse(readiness["ready_for_reviewed_concept_creation_without_teacher"])
        self.assertFalse(readiness["ready_for_memory_layer_write"])
        self.assertFalse(readiness["ready_for_action_selection_influence"])
        self.assertFalse(readiness["ready_for_external_control"])
        self.assertFalse(readiness["ready_for_first_output"])
        self.assertFalse(readiness["ready_for_live_runtime_session"])
        self.assertTrue(bridge.validate_host_body_learning_bridge_readiness(readiness)["valid"])

    def test_cli_commands_work(self) -> None:
        commands = {
            ("show-demo-uncertainty",): "passed_host_body_uncertainty_feedback_candidate_bridge",
            ("show-demo-interesting",): "passed_host_body_interesting_event_feedback_candidate_bridge",
            ("show-demo-teacher-review",): "passed_host_body_teacher_review_feedback_candidate_bridge",
            ("show-demo-deferred-bridge",): "passed_host_body_runtime_bridge_feedback_candidate_bridge",
            ("show-demo-candidate-set",): "passed_host_body_evidence_to_learning_feedback_candidate_bridge",
            ("show-demo-readiness",): "ready_for_teacher_review_of_host_body_feedback_only",
            ("validate-demo-learning-bridge",): "passed_host_body_uncertainty_feedback_candidate_bridge",
            ("show-demo-blocked", "--case", "concept-candidate"): "blocked_concept_candidate_created",
            ("show-demo-blocked", "--case", "reviewed-concept"): "blocked_reviewed_concept_created",
            ("show-demo-blocked", "--case", "memory-write"): "blocked_memory_write_detected",
            ("show-demo-blocked", "--case", "action-influence"): "blocked_action_selection_influence_detected",
            ("show-demo-blocked", "--case", "first-output"): "blocked_first_output_detected",
            ("show-demo-blocked", "--case", "live-runtime"): "blocked_live_runtime_detected",
        }
        for command, expected_text in commands.items():
            with self.subTest(command=command):
                payload = self._run_json(BRIDGE_CLI, *command)
                self.assertIn(expected_text, json.dumps(payload, sort_keys=True))

    def test_guided_console_learning_bridge_demo_works(self) -> None:
        validation = validate_host_body_learning_bridge_from_guided_cradle_growth_console()
        self.assertEqual(validation["guided_console_action"], "host_body_validate_learning_bridge_demo")
        self.assertTrue(validation["validation"]["valid"])
        self.assertFalse(validation["concept_candidate_created"])
        self.assertFalse(validation["reviewed_concept_created"])
        self.assertFalse(validation["memory_layer_write_performed"])
        self.assertFalse(validation["automatic_learning_approval_created"])
        self.assertFalse(validation["teacher_approval_created"])
        self.assertFalse(validation["task_action_selection_influence_created"])
        self.assertFalse(validation["external_control_created"])
        self.assertFalse(validation["first_output_created"])
        self.assertFalse(validation["live_runtime_session_created"])

        commands = {
            "host-body-show-learning-bridge-uncertainty-demo": "passed_host_body_uncertainty_feedback_candidate_bridge",
            "host-body-show-learning-bridge-interesting-demo": "passed_host_body_interesting_event_feedback_candidate_bridge",
            "host-body-show-learning-bridge-teacher-review-demo": "passed_host_body_teacher_review_feedback_candidate_bridge",
            "host-body-show-learning-bridge-deferred-runtime-demo": "passed_host_body_runtime_bridge_feedback_candidate_bridge",
            "host-body-show-learning-bridge-candidate-set-demo": "passed_host_body_evidence_to_learning_feedback_candidate_bridge",
            "host-body-show-learning-bridge-readiness": "ready_for_teacher_review_of_host_body_feedback_only",
            "host-body-validate-learning-bridge-demo": "passed_host_body_uncertainty_feedback_candidate_bridge",
        }
        for command, expected_text in commands.items():
            with self.subTest(command=command):
                payload = self._run_json(GUIDED_CLI, command)
                self.assertIn(expected_text, json.dumps(payload, sort_keys=True))

    def test_no_repo_data_directory_created(self) -> None:
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _plan_inputs(self):
        return (
            build_demo_qingyin_host_body_v0_milestone_pass()["host_body_v0_milestone_audit"],
            build_demo_full_host_body_trace_history_lane()["trace_history_audit"],
            build_demo_camera_change_marks_interesting()["internal_action_choice_audit"],
        )

    def _evidence_inputs(self):
        v0_audit, trace_audit, action_audit = self._plan_inputs()
        plan = bridge.build_host_body_learning_bridge_plan(
            host_body_v0_audit=v0_audit,
            trace_history_audit=trace_audit,
            internal_action_choice_audit=action_audit,
        )
        trace_payload = build_demo_full_host_body_trace_history_lane()
        action_payload = build_demo_camera_change_marks_interesting()
        runtime_payload = build_demo_deferred_dispatch_host_body_runtime_bridge()
        home_payload = build_demo_qingyin_home_internal_space_surface()
        return (
            plan,
            trace_payload["trace_history_readback"],
            action_payload["internal_action_choice"],
            action_payload["internal_action_result"],
            runtime_payload["host_body_runtime_bridge_trace"],
            home_payload["home_teacher_observed_surface"],
        )

    def _action_payload_for_kind(self, kind: str) -> dict[str, object]:
        trace_payload = build_demo_full_host_body_trace_history_lane()
        home_payload = build_demo_qingyin_home_internal_space_surface()
        plan = build_host_body_internal_action_choice_plan(
            trace_history_audit=trace_payload["trace_history_audit"],
            trace_history_readback=trace_payload["trace_history_readback"],
            home_surface_audit=home_payload["home_internal_space_surface_audit"],
        )
        candidate = build_host_body_internal_action_candidate(
            choice_plan=plan,
            candidate_action_kind=kind,
        )
        choice = build_host_body_internal_action_choice(
            choice_plan=plan,
            candidates=(candidate,),
        )
        result = build_host_body_internal_action_result(internal_action_choice=choice)
        effect = build_host_body_internal_action_surface_effect(internal_action_result=result)
        choice_set = build_host_body_internal_action_choice_set(
            choice_plan=plan,
            candidates=(candidate,),
            choices=(choice,),
            results=(result,),
            surface_effects=(effect,),
        )
        audit = build_host_body_internal_action_choice_audit(
            choice_plan=plan,
            candidates=(candidate,),
            choices=(choice,),
            results=(result,),
            surface_effects=(effect,),
            choice_set=choice_set,
        )
        return {
            "internal_action_choice": choice.to_dict(),
            "internal_action_result": result.to_dict(),
            "internal_action_choice_audit": audit.to_dict(),
        }

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
