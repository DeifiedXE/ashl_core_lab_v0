from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

from ashl_core_v1.host_body import host_body_readback_internal_action_influence as influence
from ashl_core_v1.host_body import host_body_working_readback_integration as working
from ashl_core_v1.host_body import host_body_internal_action_choice as internal
from ashl_core_v1.runtime.guided_cradle_growth_teacher_console import (
    validate_host_body_readback_influence_from_guided_cradle_growth_console,
)


INFLUENCE_CLI = "ashl_core_v1.host_body.host_body_readback_internal_action_influence_cli"
GUIDED_CLI = "ashl_core_v1.runtime.guided_cradle_growth_teacher_console_cli"


class HostBodyReadbackInternalActionInfluenceTests(unittest.TestCase):
    def test_influence_plan_builds_and_blocks_forbidden_authority(self) -> None:
        plan = self._plan()
        self.assertEqual(plan.plan_status, "readback_internal_action_influence_plan_created")
        self.assertTrue(plan.internal_action_choice_ordering_allowed)
        self.assertFalse(plan.task_action_selection_allowed)
        self.assertFalse(plan.direct_command_allowed)
        self.assertFalse(plan.external_control_allowed)
        self.assertFalse(plan.memory_write_allowed)
        self.assertFalse(plan.raw_trace_summarization_allowed)
        self.assertFalse(plan.concept_id_embedding_into_raw_history_allowed)
        self.assertFalse(plan.first_output_allowed)
        self.assertFalse(plan.live_runtime_session_allowed)
        self.assertTrue(influence.validate_host_body_readback_internal_action_influence_plan(plan)["valid"])

        working_payload, internal_payload, boundary = self._sources()
        blocked = {
            "missing_internal": (
                {"internal_action_choice_audit": None},
                "blocked_missing_internal_action_choice_audit",
            ),
            "missing_boundary": (
                {"trace_spine_boundary": None},
                "blocked_missing_trace_spine_boundary",
            ),
            "task": (
                {"task_action_selection_allowed": True},
                "blocked_task_action_selection_allowed",
            ),
            "direct": (
                {"direct_command_allowed": True},
                "blocked_direct_command_allowed",
            ),
            "external": (
                {"external_control_allowed": True},
                "blocked_external_control_allowed",
            ),
            "memory": (
                {"memory_write_allowed": True},
                "blocked_memory_write_allowed",
            ),
            "raw": (
                {"raw_trace_summarization_allowed": True},
                "blocked_raw_trace_summarization_allowed",
            ),
            "concept": (
                {"concept_id_embedding_into_raw_history_allowed": True},
                "blocked_concept_id_embedding_allowed",
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
        for case, (kwargs, expected) in blocked.items():
            with self.subTest(case=case):
                args = {
                    "working_readback_integration_audit": working_payload[
                        "host_body_working_readback_integration_audit"
                    ],
                    "internal_action_choice_audit": internal_payload[
                        "internal_action_choice_audit"
                    ],
                    "trace_spine_boundary": boundary,
                    **kwargs,
                }
                self.assertEqual(
                    influence.build_host_body_readback_internal_action_influence_plan(**args).plan_status,
                    expected,
                )

    def test_readback_signal_records_themes_and_blocks_payload_or_authority(self) -> None:
        visibility = self._visibility()
        expected = {
            "prior_uncertainty": "readback_internal_action_signal_created_uncertainty",
            "prior_interesting_event": "readback_internal_action_signal_created",
            "prior_teacher_review_needed": "readback_internal_action_signal_created_teacher_review",
            "prior_observe_again_helped": "readback_internal_action_signal_created_observe_again",
            "prior_runtime_bridge_deferred": "readback_internal_action_signal_created_runtime_bridge",
            "none": "readback_internal_action_signal_created_noop",
        }
        for theme, status in expected.items():
            with self.subTest(theme=theme):
                signal = influence.build_host_body_readback_internal_action_signal(
                    influence_plan=self._plan(),
                    working_readback_visibility=visibility,
                    signal_theme=theme,
                )
                self.assertEqual(signal.signal_status, status)
                self.assertTrue(signal.readback_payload_contains_interpretation)
                self.assertTrue(signal.readback_payload_contains_source_refs)
                self.assertFalse(signal.readback_payload_contains_raw_trace)
                self.assertTrue(influence.validate_host_body_readback_internal_action_signal(signal)["valid"])

        blocked = {
            "interpretation": (
                {"readback_payload_contains_interpretation": False},
                "blocked_invalid_working_readback_visibility",
            ),
            "raw": (
                {"readback_payload_contains_raw_trace": True},
                "blocked_raw_trace_in_readback_payload",
            ),
            "refs": (
                {"readback_payload_contains_source_refs": False},
                "blocked_missing_source_refs",
            ),
            "task": (
                {"task_action_selection_influence_created": True},
                "blocked_task_action_selection_influence_detected",
            ),
            "external": (
                {"external_control_created": True},
                "blocked_external_control_detected",
            ),
            "memory": (
                {"memory_write_performed": True},
                "blocked_memory_write_detected",
            ),
            "mutation": (
                {"raw_trace_mutated": True},
                "blocked_raw_trace_mutation_detected",
            ),
            "summary": (
                {"raw_trace_summarized": True},
                "blocked_raw_trace_summarization_detected",
            ),
            "concept": (
                {"concept_id_embedded_into_raw_history": True},
                "blocked_concept_id_embedded_into_raw_history",
            ),
            "first": (
                {"first_output_created": True},
                "blocked_first_output_detected",
            ),
            "live": (
                {"live_runtime_session_created": True},
                "blocked_live_runtime_detected",
            ),
        }
        for case, (kwargs, expected_status) in blocked.items():
            with self.subTest(case=case):
                signal = influence.build_host_body_readback_internal_action_signal(
                    influence_plan=self._plan(),
                    working_readback_visibility=visibility,
                    signal_theme="prior_uncertainty",
                    **kwargs,
                )
                self.assertEqual(signal.signal_status, expected_status)

    def test_candidate_scores_and_ordering_apply_deterministic_bounded_readback(self) -> None:
        signal = self._signal("prior_uncertainty")
        mark = influence.build_host_body_internal_action_candidate_readback_score(
            readback_signal=signal,
            candidate_action_kind="mark_uncertain",
            base_candidate_priority=5,
        )
        review = influence.build_host_body_internal_action_candidate_readback_score(
            readback_signal=signal,
            candidate_action_kind="request_teacher_review",
            base_candidate_priority=5,
        )
        observe = influence.build_host_body_internal_action_candidate_readback_score(
            readback_signal=signal,
            candidate_action_kind="observe_again",
            base_candidate_priority=5,
        )
        self.assertEqual(mark.readback_delta, 3)
        self.assertEqual(review.readback_delta, 2)
        self.assertEqual(observe.readback_delta, 0)
        self.assertEqual(mark.final_candidate_priority, 8)
        self.assertEqual(mark.score_status, "candidate_readback_score_created_boosted")
        self.assertTrue(influence.validate_host_body_internal_action_candidate_readback_score(mark)["valid"])

        clamped = influence.build_host_body_internal_action_candidate_readback_score(
            readback_signal=signal,
            candidate_action_kind="mark_uncertain",
            base_candidate_priority=5,
            readback_delta=99,
        )
        self.assertEqual(clamped.readback_delta, 3)

        blocked = {
            "candidate": (
                {"candidate_action_kind": "mouse_control"},
                "blocked_forbidden_candidate_kind",
            ),
            "task_score": (
                {"task_action_score_created": True},
                "blocked_task_action_score_detected",
            ),
            "selected": (
                {"task_selected_action_created": True},
                "blocked_selected_action_created",
            ),
            "direct": (
                {"direct_command_created": True},
                "blocked_direct_command_created",
            ),
            "external": (
                {"external_control_created": True},
                "blocked_external_control_detected",
            ),
            "memory": (
                {"memory_write_performed": True},
                "blocked_memory_write_detected",
            ),
            "learning": (
                {"learning_candidate_created": True},
                "blocked_memory_write_detected",
            ),
            "first": (
                {"first_output_created": True},
                "blocked_first_output_detected",
            ),
            "live": (
                {"live_runtime_session_created": True},
                "blocked_live_runtime_detected",
            ),
        }
        for case, (kwargs, expected_status) in blocked.items():
            with self.subTest(case=case):
                candidate_kind = kwargs.pop("candidate_action_kind", "mark_uncertain")
                score = influence.build_host_body_internal_action_candidate_readback_score(
                    readback_signal=signal,
                    base_candidate_priority=5,
                    candidate_action_kind=candidate_kind,
                    **kwargs,
                )
                self.assertEqual(score.score_status, expected_status)

        ordering = influence.build_host_body_readback_influenced_internal_action_ordering(
            influence_plan=self._plan(),
            candidate_readback_scores=(observe, review, mark),
        )
        self.assertEqual(
            ordering.ordering_status,
            "readback_influenced_internal_action_ordering_created_changed",
        )
        self.assertEqual(ordering.ordered_candidate_action_kinds[0], "mark_uncertain")
        self.assertTrue(ordering.deterministic_tie_breaker_used)
        self.assertFalse(ordering.task_action_ordering_changed)

        no_change_signal = self._signal("none")
        no_change_score = influence.build_host_body_internal_action_candidate_readback_score(
            readback_signal=no_change_signal,
            candidate_action_kind="observe_again",
            base_candidate_priority=5,
        )
        no_change = influence.build_host_body_readback_influenced_internal_action_ordering(
            influence_plan=self._plan(),
            candidate_readback_scores=(no_change_score,),
        )
        self.assertEqual(
            no_change.ordering_status,
            "readback_influenced_internal_action_ordering_created_no_change",
        )

    def test_choice_and_result_are_internal_only_and_block_forbidden_outputs(self) -> None:
        payload = influence.build_demo_prior_teacher_review_boosts_request_teacher_review()
        choice = payload["readback_influenced_internal_action_choice"]
        result = payload["readback_influenced_internal_action_result"]
        self.assertEqual(choice["selected_internal_action_kind"], "request_teacher_review")
        self.assertTrue(choice["teacher_review_request_recorded"])
        self.assertFalse(choice["teacher_approval_created"])
        self.assertFalse(choice["task_selected_action_created"])
        self.assertEqual(
            result["result_status"],
            "readback_influenced_internal_action_result_recorded_request_teacher_review",
        )
        self.assertTrue(result["teacher_review_request_recorded"])
        self.assertFalse(result["external_control_created"])

        observe = influence.build_demo_prior_observe_again_boosts_observe_again()
        self.assertEqual(
            observe["readback_influenced_internal_action_choice"]["selected_internal_action_kind"],
            "observe_again",
        )
        self.assertTrue(
            observe["readback_influenced_internal_action_result"][
                "observe_again_recommendation_recorded"
            ]
        )

        ordering = influence.HostBodyReadbackInfluencedInternalActionOrderingRecord.from_dict(
            payload["readback_influenced_internal_action_ordering"]
        )
        choice_blocks = {
            "teacher": "teacher_approval_created",
            "task": "task_selected_action_created",
            "direct": "direct_command_created",
            "external": "external_control_created",
            "memory": "memory_write_performed",
            "learning": "learning_candidate_created",
            "first": "first_output_created",
            "live": "live_runtime_session_created",
        }
        for case, flag in choice_blocks.items():
            with self.subTest(choice_case=case):
                blocked = influence.build_host_body_readback_influenced_internal_action_choice(
                    readback_influenced_ordering=ordering,
                    **{flag: True},
                )
                self.assertTrue(blocked.choice_status.startswith("blocked_"))

        valid_choice = influence.HostBodyReadbackInfluencedInternalActionChoiceRecord.from_dict(choice)
        result_blocks = {
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
            "auto": "automatic_learning_approval_created",
            "first": "first_output_created",
            "live": "live_runtime_session_created",
        }
        for case, flag in result_blocks.items():
            with self.subTest(result_case=case):
                blocked = influence.build_host_body_readback_influenced_internal_action_result(
                    readback_influenced_choice=valid_choice,
                    **{flag: True},
                )
                self.assertTrue(blocked.result_status.startswith("blocked_"))

    def test_trace_audit_and_readiness_preserve_trace_spine_boundaries(self) -> None:
        demos = {
            "uncertainty": (
                influence.build_demo_prior_uncertainty_boosts_mark_uncertain(),
                "passed_readback_influenced_mark_uncertain",
            ),
            "teacher": (
                influence.build_demo_prior_teacher_review_boosts_request_teacher_review(),
                "passed_readback_influenced_request_teacher_review",
            ),
            "observe": (
                influence.build_demo_prior_observe_again_boosts_observe_again(),
                "passed_readback_influenced_observe_again",
            ),
            "runtime": (
                influence.build_demo_runtime_bridge_deferred_boosts_pause_or_review(),
                "passed_readback_influenced_request_teacher_review",
            ),
            "mixed": (
                influence.build_demo_mixed_readback_internal_action_influence(),
                "passed_host_body_readback_internal_action_influence",
            ),
        }
        for case, (payload, expected_status) in demos.items():
            with self.subTest(case=case):
                trace = payload["readback_internal_action_influence_trace"]
                audit = payload["readback_internal_action_influence_audit"]
                self.assertEqual(trace["trace_status"], "readback_internal_action_influence_trace_recorded")
                self.assertTrue(trace["trace_spine_boundary_preserved"])
                self.assertTrue(trace["raw_trace_append_only_confirmed"])
                self.assertFalse(trace["raw_trace_summarized_during_service_period"])
                self.assertTrue(trace["memory_layer_stores_interpretation_only"])
                self.assertTrue(trace["source_trace_refs_preserved"])
                self.assertFalse(trace["concept_id_embedded_into_raw_history"])
                self.assertEqual(audit["audit_status"], expected_status)
                self.assertTrue(audit["internal_only_confirmed"])
                self.assertTrue(audit["record_only_confirmed"])
                self.assertTrue(audit["trace_spine_format_unified_confirmed"])
                self.assertTrue(audit["raw_trace_not_summarized_during_service_period"])
                self.assertTrue(audit["source_trace_refs_preserved_confirmed"])
                self.assertFalse(audit["no_task_action_selection_influence"] is False)
                self.assertTrue(influence.validate_host_body_readback_internal_action_influence_audit(audit)["valid"])

        blocked = {
            "task": (
                influence.build_demo_blocked_task_action_influence(),
                "blocked_task_action_selection_influence_detected",
            ),
            "selected": (
                influence.build_demo_blocked_selected_action_created(),
                "blocked_selected_action_created",
            ),
            "direct": (
                influence.build_demo_blocked_direct_command_created(),
                "blocked_direct_command_created",
            ),
            "external": (
                influence.build_demo_blocked_external_control(),
                "blocked_external_control_detected",
            ),
            "memory": (
                influence.build_demo_blocked_memory_write(),
                "blocked_memory_write_detected",
            ),
            "learning": (
                influence.build_demo_blocked_learning_candidate_creation(),
                "blocked_learning_candidate_creation_detected",
            ),
            "raw": (
                influence.build_demo_blocked_raw_trace_summarization(),
                "blocked_raw_trace_summarized",
            ),
            "concept": (
                influence.build_demo_blocked_concept_id_embedded_into_raw_history(),
                "blocked_concept_id_embedded_into_raw_history",
            ),
            "first": (
                influence.build_demo_blocked_first_output(),
                "blocked_first_output_detected",
            ),
            "live": (
                influence.build_demo_blocked_live_runtime(),
                "blocked_live_runtime_detected",
            ),
        }
        for case, (payload, expected_status) in blocked.items():
            with self.subTest(blocked_case=case):
                audit = payload["readback_internal_action_influence_audit"]
                self.assertEqual(audit["audit_status"], expected_status)
                self.assertFalse(influence.validate_host_body_readback_internal_action_influence_audit(audit)["valid"])

        readiness = influence.build_demo_prior_uncertainty_boosts_mark_uncertain()[
            "readback_internal_action_influence_readiness"
        ]
        self.assertEqual(
            readiness["readiness_status"],
            "ready_for_host_body_embodied_learning_closed_loop_audit_only",
        )
        self.assertTrue(readiness["ready_for_host_body_embodied_learning_closed_loop_audit"])
        self.assertTrue(readiness["ready_for_bounded_embodied_loop_runner"])
        self.assertTrue(readiness["ready_for_no_codex_teacher_console_flow"])
        self.assertFalse(readiness["ready_for_task_engine_action_selection_influence"])
        self.assertFalse(readiness["ready_for_direct_command"])
        self.assertFalse(readiness["ready_for_external_control"])
        self.assertFalse(readiness["ready_for_long_term_memory_write"])
        self.assertFalse(readiness["ready_for_core_memory_write"])
        self.assertFalse(readiness["ready_for_learning_candidate_creation"])
        self.assertFalse(readiness["ready_for_automatic_learning_approval"])
        self.assertFalse(readiness["ready_for_first_output"])
        self.assertFalse(readiness["ready_for_live_runtime_session"])

    def test_cli_guided_console_and_repo_boundaries(self) -> None:
        cli_commands = [
            ("show-demo-uncertainty",),
            ("show-demo-teacher-review",),
            ("show-demo-observe-again",),
            ("show-demo-runtime-bridge-deferred",),
            ("show-demo-no-change",),
            ("show-demo-mixed",),
            ("show-demo-readiness",),
            ("validate-demo-readback-influence",),
            ("show-demo-blocked", "--case", "task-action-influence"),
            ("show-demo-blocked", "--case", "selected-action"),
            ("show-demo-blocked", "--case", "direct-command"),
            ("show-demo-blocked", "--case", "external-control"),
            ("show-demo-blocked", "--case", "memory-write"),
            ("show-demo-blocked", "--case", "learning-candidate"),
            ("show-demo-blocked", "--case", "raw-trace-summarization"),
            ("show-demo-blocked", "--case", "concept-id-in-raw-history"),
            ("show-demo-blocked", "--case", "first-output"),
            ("show-demo-blocked", "--case", "live-runtime"),
        ]
        for command in cli_commands:
            with self.subTest(command=command):
                result = subprocess.run(
                    ["py", "-3", "-m", INFLUENCE_CLI, *command],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                self.assertTrue(json.loads(result.stdout))

        guided = validate_host_body_readback_influence_from_guided_cradle_growth_console()
        self.assertEqual(guided["guided_console_action"], "host_body_validate_readback_influence_demo")
        self.assertTrue(guided["validation"]["valid"])
        self.assertFalse(guided["task_action_selection_influence_created"])
        self.assertFalse(guided["task_selected_action_created"])
        self.assertFalse(guided["direct_command_created"])
        self.assertFalse(guided["external_control_created"])
        self.assertFalse(guided["memory_layer_write_performed"])
        self.assertFalse(guided["learning_candidate_created"])
        self.assertFalse(guided["raw_trace_mutated"])
        self.assertFalse(guided["raw_trace_summarized"])
        self.assertFalse(guided["first_output_created"])
        self.assertFalse(guided["live_runtime_session_created"])

        guided_commands = [
            "host-body-show-readback-influence-uncertainty-demo",
            "host-body-show-readback-influence-teacher-review-demo",
            "host-body-show-readback-influence-observe-again-demo",
            "host-body-show-readback-influence-runtime-bridge-demo",
            "host-body-show-readback-influence-no-change-demo",
            "host-body-show-readback-influence-mixed-demo",
            "host-body-show-readback-influence-readiness",
            "host-body-validate-readback-influence-demo",
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

        self.assertTrue(Path("ashl_core_v1/docs/future_age_grounded_concept_memory_compilation_gcmc_v0_3.md").exists())
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _sources(self) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
        working_payload = working.build_demo_uncertainty_reviewed_concept_working_readback()
        internal_payload = internal.build_demo_unknown_event_marks_uncertain()
        boundary = working.build_demo_trace_spine_raw_evidence_boundary()[
            "trace_spine_raw_evidence_boundary"
        ]
        return working_payload, internal_payload, boundary

    def _plan(self) -> influence.HostBodyReadbackInternalActionInfluencePlanRecord:
        working_payload, internal_payload, boundary = self._sources()
        return influence.build_host_body_readback_internal_action_influence_plan(
            working_readback_integration_audit=working_payload[
                "host_body_working_readback_integration_audit"
            ],
            internal_action_choice_audit=internal_payload["internal_action_choice_audit"],
            trace_spine_boundary=boundary,
        )

    def _visibility(self) -> dict[str, object]:
        return working.build_demo_uncertainty_reviewed_concept_working_readback()[
            "host_body_working_readback_visibility_records"
        ][0]

    def _signal(self, theme: str) -> influence.HostBodyReadbackInternalActionSignalRecord:
        return influence.build_host_body_readback_internal_action_signal(
            influence_plan=self._plan(),
            working_readback_visibility=self._visibility(),
            signal_theme=theme,
        )


if __name__ == "__main__":
    unittest.main()
