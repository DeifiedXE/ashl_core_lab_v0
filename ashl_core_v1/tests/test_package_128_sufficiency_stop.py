from __future__ import annotations

import contextlib
import io
import os
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from ashl_core_v1.host_body.host_body_internal_action_choice import (
    ALLOWED_INTERNAL_ACTION_KINDS,
)
from ashl_core_v1.migration_audit import (
    D_LAPLACE_QM0_AUDIT_STATUS,
    QINGYIN_MIGRATION_STATUS,
)
from ashl_core_v1.runtime.bounded_capture_deadline_controller import (
    BoundedCaptureDeadlineController,
)
from ashl_core_v1.runtime.bounded_multimodal_perception_session_runtime import (
    BoundedMultimodalPerceptionSessionRuntime,
)
from ashl_core_v1.runtime.internal_perception_focus_types import (
    PACKAGE_127_PASS_STATUS,
)
from ashl_core_v1.runtime.observation_stop_policy import (
    decide_observation_stop_policy,
)
from ashl_core_v1.runtime.package_126_reacquisition_runtime import (
    _build_live_alignment_config,
)
from ashl_core_v1.runtime.package_128_sufficiency_stop_audit import (
    audit_package_128_sufficiency_stop,
)
from ashl_core_v1.runtime.package_128_sufficiency_stop_cli import (
    main as package_128_cli_main,
)
from ashl_core_v1.runtime.package_128_sufficiency_stop_runtime import (
    PACKAGE_128_EVENT_KINDS,
    run_real_structural_sufficiency_stop,
    run_synthetic_package_128_controls,
)
from ashl_core_v1.runtime.package_128_sufficiency_stop_store import (
    Package128SufficiencyStopStore,
)
from ashl_core_v1.runtime.perception_reacquisition_types import (
    PACKAGE_126_PASS_STATUS,
)
from ashl_core_v1.runtime.stop_observation_internal_action import (
    build_observation_completion,
    build_observation_stop_execution,
    create_stop_observation_internal_action,
)
from ashl_core_v1.runtime.structural_evidence_sufficiency_assessor import (
    assess_structural_evidence,
    create_structural_evidence_checkpoint,
    create_structural_sufficiency_contract,
)
from ashl_core_v1.runtime.structural_evidence_sufficiency_types import (
    BASELINE_COMMIT,
    CHECKPOINT_INTERVAL_NS,
    CHILD_HARD_WINDOW_NS,
    CONTRACT_KIND,
    MAXIMUM_CHECKPOINT_COUNT,
    MINIMUM_COMPLETE_ALIGNMENT_WINDOWS,
    MINIMUM_ELAPSED_NS,
    MINIMUM_POST_EVENT_COVERAGE_NS,
    PACKAGE_128_PASS_STATUS,
    REQUIRED_LANES,
    STOP_ACTION_KIND,
)


class Package128PolicyUnitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = self._contract()

    def _contract(self):
        return create_structural_sufficiency_contract(
            runtime_session_id="runtime:test",
            perception_session_id="perception:test",
            observation_window_id="window:test",
            focus_context_id="focus_context:test",
            hard_deadline_event_time_ns=3_000_000_000,
            source_record_refs=(
                "focus_context:test",
                "focus_plan:test",
            ),
        )

    def _checkpoint(
        self,
        *,
        event_time_ns: int = 2_000_000_000,
        complete_windows: int = 3,
        focused_count: int = 1,
        observed: bool = True,
        open_region: bool = False,
        post_coverage_ns: int = 600_000_000,
        drops: int = 0,
        backpressure: int = 0,
        capture_failures: int = 0,
        compile_failures: int = 0,
        window_id: str | None = None,
    ):
        closure = (
            event_time_ns - post_coverage_ns
            if observed and not open_region
            else None
        )
        return create_structural_evidence_checkpoint(
            contract=self.contract,
            checkpoint_index=0,
            evaluated_at_event_time_ns=event_time_ns,
            evaluated_at_processing_time_ns=event_time_ns + 25,
            elapsed_observation_ns=event_time_ns,
            complete_alignment_window_count=complete_windows,
            partial_alignment_window_count=0,
            focused_region_view_id="focused_view:test",
            full_frame_perception_readable_data_refs=(
                "readable:test",
            ),
            focused_region_evidence_record_count=focused_count,
            observed_visual_region_refs=(
                ("visual_change:test",) if observed else tuple()
            ),
            open_visual_region_refs=(
                ("visual_change:test",)
                if observed and open_region
                else tuple()
            ),
            closed_visual_span_refs=(
                ("temporal_span:test",)
                if observed and not open_region
                else tuple()
            ),
            latest_visual_closure_event_time_ns=closure,
            latest_complete_source_coverage_event_time_ns=event_time_ns,
            screen_source_coverage_present=True,
            host_state_source_coverage_present=True,
            required_lane_drop_count=drops,
            backpressure_fault_count=backpressure,
            capture_failure_count=capture_failures,
            compile_failure_count=compile_failures,
            observation_window_id=window_id,
            source_record_refs=(
                "screen_artifact:test",
                "host_artifact:test",
            ),
        )

    def test_baseline_and_predecessor_statuses_are_locked(self) -> None:
        self.assertEqual(
            BASELINE_COMMIT,
            "8da7facb9195a8ae753789835bb05674cd917e6d",
        )
        self.assertEqual(
            PACKAGE_127_PASS_STATUS,
            "passed_internal_perception_focus_shift_v0",
        )
        self.assertEqual(
            PACKAGE_126_PASS_STATUS,
            "passed_bounded_re_sampling_and_listen_again_internal_action_v0",
        )
        self.assertEqual(
            D_LAPLACE_QM0_AUDIT_STATUS,
            "passed_d_laplace_qm0_read_only_migration_audit_v0",
        )
        self.assertEqual(
            QINGYIN_MIGRATION_STATUS,
            "QINGYIN_MIGRATION_INCOMPLETE_AUDIT_LAYER",
        )

    def test_contract_has_exact_v0_bounds(self) -> None:
        self.assertEqual(self.contract.contract_kind, CONTRACT_KIND)
        self.assertEqual(self.contract.required_lanes, REQUIRED_LANES)
        self.assertEqual(
            self.contract.minimum_elapsed_ns,
            MINIMUM_ELAPSED_NS,
        )
        self.assertEqual(
            self.contract.minimum_complete_alignment_windows,
            MINIMUM_COMPLETE_ALIGNMENT_WINDOWS,
        )
        self.assertEqual(
            self.contract.minimum_post_event_coverage_ns,
            MINIMUM_POST_EVENT_COVERAGE_NS,
        )
        self.assertEqual(
            self.contract.checkpoint_interval_ns,
            CHECKPOINT_INTERVAL_NS,
        )
        self.assertEqual(
            self.contract.maximum_checkpoint_count,
            MAXIMUM_CHECKPOINT_COUNT,
        )

    def test_contract_rejects_semantic_goal_object_and_label(self) -> None:
        for field in ("semantic_goal", "expected_object", "expected_label"):
            with self.subTest(field=field), self.assertRaises(ValueError):
                replace(self.contract, **{field: "forbidden"})

    def test_contract_rejects_stimulus_schedule_provenance(self) -> None:
        with self.assertRaises(ValueError):
            create_structural_sufficiency_contract(
                runtime_session_id="runtime:bad",
                perception_session_id="perception:bad",
                observation_window_id="window:bad",
                focus_context_id="focus_context:bad",
                hard_deadline_event_time_ns=3_000_000_000,
                source_record_refs=("fixture_schedule:bad",),
            )
        with self.assertRaises(ValueError):
            replace(
                self.contract,
                source_trace_refs=("expected_stop:forbidden",),
            )

    def test_checkpoint_is_event_time_grounded_and_semantic_free(self) -> None:
        checkpoint = self._checkpoint()
        self.assertNotEqual(
            checkpoint.evaluated_at_event_time_ns,
            checkpoint.evaluated_at_processing_time_ns,
        )
        self.assertIsNone(checkpoint.semantic_label)
        self.assertIsNone(checkpoint.uncertainty_score)
        self.assertIsNone(checkpoint.confidence_score)
        self.assertEqual(checkpoint.post_event_coverage_ns, 600_000_000)
        with self.assertRaises(ValueError):
            replace(
                checkpoint,
                checkpoint_index=MAXIMUM_CHECKPOINT_COUNT,
            )
        with self.assertRaises(ValueError):
            replace(
                checkpoint,
                source_trace_refs=("fixture:forbidden",),
            )

    def test_checkpoint_rejects_future_source_coverage(self) -> None:
        with self.assertRaises(ValueError):
            create_structural_evidence_checkpoint(
                contract=self.contract,
                checkpoint_index=0,
                evaluated_at_event_time_ns=2_000_000_000,
                elapsed_observation_ns=2_000_000_000,
                complete_alignment_window_count=3,
                partial_alignment_window_count=0,
                focused_region_view_id="focused_view:test",
                full_frame_perception_readable_data_refs=("readable:test",),
                focused_region_evidence_record_count=1,
                observed_visual_region_refs=("visual_change:test",),
                open_visual_region_refs=tuple(),
                closed_visual_span_refs=("temporal_span:test",),
                latest_visual_closure_event_time_ns=1_000_000_000,
                latest_complete_source_coverage_event_time_ns=2_000_000_001,
                screen_source_coverage_present=True,
                host_state_source_coverage_present=True,
                source_record_refs=(
                    "screen_artifact:test",
                    "host_artifact:test",
                ),
            )

    def test_all_criteria_produce_sufficient(self) -> None:
        assessment = assess_structural_evidence(
            contract=self.contract,
            checkpoint=self._checkpoint(),
        )
        self.assertEqual(assessment.assessment_status, "sufficient")
        self.assertTrue(assessment.contract_satisfied)

    def test_each_missing_structural_gate_continues(self) -> None:
        cases = (
            self._checkpoint(event_time_ns=500_000_000),
            self._checkpoint(complete_windows=2),
            self._checkpoint(focused_count=0),
            self._checkpoint(open_region=True),
            self._checkpoint(post_coverage_ns=100_000_000),
            self._checkpoint(observed=False, focused_count=0),
        )
        for checkpoint in cases:
            with self.subTest(checkpoint=checkpoint.checkpoint_id):
                assessment = assess_structural_evidence(
                    contract=self.contract,
                    checkpoint=checkpoint,
                )
                self.assertEqual(
                    assessment.assessment_status,
                    "insufficient_continue",
                )
                self.assertFalse(assessment.contract_satisfied)

    def test_every_observed_region_requires_a_closed_span(self) -> None:
        checkpoint = replace(
            self._checkpoint(),
            observed_visual_region_refs=(
                "visual_change:first",
                "visual_change:second",
            ),
            closed_visual_span_refs=("temporal_span:first",),
        )
        assessment = assess_structural_evidence(
            contract=self.contract,
            checkpoint=checkpoint,
        )
        self.assertEqual(
            assessment.assessment_status,
            "insufficient_continue",
        )

    def test_hard_deadline_without_event_is_inconclusive(self) -> None:
        assessment = assess_structural_evidence(
            contract=self.contract,
            checkpoint=self._checkpoint(
                event_time_ns=3_000_000_000,
                observed=False,
                focused_count=0,
            ),
        )
        self.assertEqual(
            assessment.assessment_status,
            "inconclusive_at_hard_deadline",
        )

    def test_transport_fault_is_not_insufficient_evidence(self) -> None:
        for kwargs in (
            {"drops": 1},
            {"backpressure": 1},
            {"capture_failures": 1},
            {"compile_failures": 1},
        ):
            assessment = assess_structural_evidence(
                contract=self.contract,
                checkpoint=self._checkpoint(**kwargs),
            )
            self.assertEqual(
                assessment.assessment_status,
                "blocked_transport_failure",
            )

    def test_wrong_window_and_stale_checkpoint_are_invalid_lineage(self) -> None:
        wrong = assess_structural_evidence(
            contract=self.contract,
            checkpoint=self._checkpoint(window_id="window:other"),
        )
        stale = assess_structural_evidence(
            contract=self.contract,
            checkpoint=self._checkpoint(),
            active_window=False,
        )
        incomplete_focus = assess_structural_evidence(
            contract=self.contract,
            checkpoint=self._checkpoint(),
            focus_context_valid=False,
        )
        self.assertEqual(wrong.assessment_status, "blocked_invalid_lineage")
        self.assertEqual(stale.assessment_status, "blocked_invalid_lineage")
        self.assertEqual(
            incomplete_focus.assessment_status,
            "blocked_invalid_lineage",
        )

    def test_policy_precedence_and_no_other_perception_action(self) -> None:
        sufficient = assess_structural_evidence(
            contract=self.contract,
            checkpoint=self._checkpoint(),
        )
        operator = decide_observation_stop_policy(
            contract=self.contract,
            assessment=sufficient,
            contract_authorized=True,
            operator_stop_requested=True,
        )
        self.assertEqual(operator.decision, "operator_stop_precedence")
        transport = assess_structural_evidence(
            contract=self.contract,
            checkpoint=self._checkpoint(drops=1),
        )
        failed = decide_observation_stop_policy(
            contract=self.contract,
            assessment=transport,
            contract_authorized=True,
        )
        self.assertEqual(failed.decision, "fail_session")
        unauthorized = decide_observation_stop_policy(
            contract=self.contract,
            assessment=sufficient,
            contract_authorized=False,
        )
        self.assertEqual(
            unauthorized.decision,
            "continue_current_window",
        )
        self.assertNotIn(
            unauthorized.decision,
            {
                "extend_observation_window",
                "capture_again",
                "listen_again",
                "shift_internal_perception_focus",
            },
        )

    def test_sufficient_authorized_policy_creates_one_internal_action(self) -> None:
        assessment = assess_structural_evidence(
            contract=self.contract,
            checkpoint=self._checkpoint(),
        )
        decision = decide_observation_stop_policy(
            contract=self.contract,
            assessment=assessment,
            contract_authorized=True,
        )
        action = create_stop_observation_internal_action(
            decision=decision,
            contract=self.contract,
        )
        self.assertIsNotNone(action)
        assert action is not None
        self.assertEqual(action.action_kind, STOP_ACTION_KIND)
        self.assertTrue(action.internal_only)
        self.assertFalse(action.external_side_effect)
        self.assertFalse(action.opens_new_window)
        self.assertFalse(action.extends_deadline)
        self.assertFalse(action.changes_focus)
        self.assertFalse(action.selected_action_created)
        self.assertFalse(action.final_action_created)
        self.assertFalse(action.direct_command_created)
        with self.assertRaises(ValueError):
            create_stop_observation_internal_action(
                decision=decision,
                contract=self.contract,
                existing_action_count=1,
            )

    def test_stop_observation_is_canonical_host_body_kind(self) -> None:
        self.assertIn(STOP_ACTION_KIND, ALLOWED_INTERNAL_ACTION_KINDS)

    def test_package_125_controller_stop_is_shared_and_distinct(self) -> None:
        controller = BoundedCaptureDeadlineController(
            base_deadline_ns=CHILD_HARD_WINDOW_NS,
            hard_deadline_ns=CHILD_HARD_WINDOW_NS,
            participating_lanes=REQUIRED_LANES,
            maximum_extension_count=0,
            maximum_total_extension_ns=0,
        )
        original = controller.current_deadline_ns()
        controller.request_stop(
            "structural_evidence_sufficiency_policy"
        )
        self.assertTrue(controller.stop_requested)
        self.assertEqual(controller.current_deadline_ns(), original)
        self.assertEqual(controller.extension_count, 0)

    def test_stop_execution_derives_active_identity_continuity(self) -> None:
        assessment = assess_structural_evidence(
            contract=self.contract,
            checkpoint=self._checkpoint(),
        )
        decision = decide_observation_stop_policy(
            contract=self.contract,
            assessment=assessment,
            contract_authorized=True,
        )
        action = create_stop_observation_internal_action(
            decision=decision,
            contract=self.contract,
        )
        assert action is not None
        controller = BoundedCaptureDeadlineController(
            base_deadline_ns=CHILD_HARD_WINDOW_NS,
            hard_deadline_ns=CHILD_HARD_WINDOW_NS,
            participating_lanes=REQUIRED_LANES,
            maximum_extension_count=0,
            maximum_total_extension_ns=0,
        )
        controller.request_stop(
            "structural_evidence_sufficiency_policy"
        )
        child = {
            "participating_lanes": REQUIRED_LANES,
            "capture_session_refs": (
                "capture:screen",
                "capture:host",
            ),
            "alignment_session_id": "perception:test",
            "sessions_started": True,
            "sessions_stopped": True,
            "original_hard_deadline_monotonic_ns": 3_000_000_000,
            "ended_monotonic_ns": 2_000_000_000,
            "flush_remaining_count": 0,
            "screen_artifact_ids": ("screen:artifact",),
            "host_artifact_ids": ("host:artifact",),
            "alignment_window_ids": ("alignment:window",),
            "transport_flush_record_id": "transport:flush",
        }
        execution = build_observation_stop_execution(
            action=action,
            controller=controller,
            child_window=child,
            stop_requested_at_event_time_ns=1_900_000_000,
            focus_context_id_before="focus:active",
            focus_context_id_at_completion="focus:active",
            active_capture_session_refs=(
                "capture:screen",
                "capture:host",
            ),
            active_alignment_origin_ref="perception:test",
        )
        self.assertEqual(
            execution.execution_status,
            "completed_policy_stop",
        )
        self.assertFalse(execution.source_sessions_reopened)
        self.assertFalse(execution.alignment_origin_changed)
        changed = build_observation_stop_execution(
            action=action,
            controller=controller,
            child_window=child,
            stop_requested_at_event_time_ns=1_900_000_000,
            focus_context_id_before="focus:active",
            focus_context_id_at_completion="focus:active",
            active_capture_session_refs=("capture:old",),
            active_alignment_origin_ref="perception:old",
        )
        self.assertEqual(changed.execution_status, "failed")
        self.assertTrue(changed.source_sessions_reopened)
        self.assertTrue(changed.alignment_origin_changed)

    def test_terminal_completion_kinds_preserve_precedence(self) -> None:
        inconclusive = assess_structural_evidence(
            contract=self.contract,
            checkpoint=self._checkpoint(
                event_time_ns=3_000_000_000,
                observed=False,
                focused_count=0,
            ),
        )
        deadline_policy = decide_observation_stop_policy(
            contract=self.contract,
            assessment=inconclusive,
            contract_authorized=True,
        )
        child = {
            "ended_monotonic_ns": 3_000_000_000,
            "original_hard_deadline_monotonic_ns": 3_000_000_000,
            "temporal_bundle_id": "temporal_bundle:test",
            "required_windows_complete": 3,
            "required_lane_drop_count": 0,
            "backpressure_fault_count": 0,
            "capture_failure_count": 0,
            "compile_failure_count": 0,
            "flush_remaining_count": 0,
        }
        completion = build_observation_completion(
            contract=self.contract,
            assessment=inconclusive,
            decision=deadline_policy,
            execution=None,
            child_window=child,
            final_focus_context_id="focus_context:released",
        )
        self.assertEqual(
            completion.completion_kind,
            "hard_deadline_inconclusive",
        )
        self.assertFalse(completion.ended_before_hard_deadline)

        sufficient = assess_structural_evidence(
            contract=self.contract,
            checkpoint=self._checkpoint(),
        )
        operator_policy = decide_observation_stop_policy(
            contract=self.contract,
            assessment=sufficient,
            contract_authorized=True,
            operator_stop_requested=True,
        )
        operator_completion = build_observation_completion(
            contract=self.contract,
            assessment=sufficient,
            decision=operator_policy,
            execution=None,
            child_window={
                **child,
                "ended_monotonic_ns": 2_000_000_000,
            },
            final_focus_context_id="focus_context:released",
        )
        self.assertEqual(
            operator_completion.completion_kind,
            "operator_interrupted",
        )

    def test_synthetic_controls_all_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            controls = run_synthetic_package_128_controls(
                state_dir=temp_dir
            )
        for key, value in controls.items():
            if key.endswith("_passed"):
                self.assertTrue(value, key)

    def test_store_is_append_only_external_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = Package128SufficiencyStopStore(temp_dir)
            store.append_record(
                "structural_sufficiency_contracts",
                self.contract,
            )
            with self.assertRaises(Exception):
                store.append_record(
                    "structural_sufficiency_contracts",
                    self.contract,
                )
            self.assertTrue(
                str(store.db_path).startswith(str(Path(temp_dir)))
            )

    def test_event_kinds_are_exact_and_nonsemantic(self) -> None:
        self.assertEqual(len(PACKAGE_128_EVENT_KINDS), 12)
        self.assertIn(
            "stop_observation_internal_action_created",
            PACKAGE_128_EVENT_KINDS,
        )
        self.assertNotIn("evidence_understood", PACKAGE_128_EVENT_KINDS)

    def test_active_alignment_view_does_not_finalize_session(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime = BoundedMultimodalPerceptionSessionRuntime(temp_dir)
            config = _build_live_alignment_config(
                path=Path(temp_dir),
                participating_lanes=REQUIRED_LANES,
                window_duration_ns=CHILD_HARD_WINDOW_NS,
                queue_depth=64,
            )
            self.assertEqual(config.required_source_kinds, REQUIRED_LANES)
            self.assertEqual(
                runtime.store.list_payloads("multimodal_timelines"),
                tuple(),
            )

    def test_cli_blocks_real_run_without_explicit_authorization(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = package_128_cli_main(
                    [
                        "run-real-sufficiency-stop",
                        "--state-dir",
                        temp_dir,
                    ]
                )
            self.assertEqual(code, 1)
            self.assertIn("authorization", output.getvalue())
            with self.assertRaises(PermissionError):
                run_real_structural_sufficiency_stop(
                    state_dir=temp_dir,
                )

    def test_cli_synthetic_smoke_and_views(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(
                    package_128_cli_main(
                        [
                            "synthetic-smoke",
                            "--state-dir",
                            temp_dir,
                        ]
                    ),
                    0,
                )
                self.assertEqual(
                    package_128_cli_main(
                        ["show-checkpoints", "--state-dir", temp_dir]
                    ),
                    0,
                )


@unittest.skipUnless(os.name == "nt", "real capture requires Windows")
class Package128RealRunTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._temp = tempfile.TemporaryDirectory()
        cls.result = run_real_structural_sufficiency_stop(
            state_dir=cls._temp.name,
            allow_structural_sufficiency_stop=True,
        )
        cls.audit = audit_package_128_sufficiency_stop(
            state_dir=cls._temp.name,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls._temp.cleanup()

    def test_real_focused_child_stops_before_hard_deadline(self) -> None:
        self.assertEqual(
            self.result["final_assessment_status"],
            "sufficient",
        )
        self.assertEqual(
            self.result["policy_decision"],
            "allow_policy_stop",
        )
        self.assertTrue(self.result["stopped_before_hard_deadline"])
        self.assertLessEqual(
            self.result["child"]["actual_window_ns"],
            2_500_000_000,
        )
        self.assertGreaterEqual(
            self.result["post_event_coverage_ns"],
            MINIMUM_POST_EVENT_COVERAGE_NS,
        )
        self.assertGreaterEqual(
            self.result["complete_alignment_window_count"],
            MINIMUM_COMPLETE_ALIGNMENT_WINDOWS,
        )

    def test_real_evidence_and_flush_are_clean(self) -> None:
        self.assertTrue(self.result["full_frame_preserved"])
        self.assertTrue(
            self.result["focused_region_evidence_present"]
        )
        self.assertFalse(
            self.result["source_sessions_reopened_by_stop"]
        )
        self.assertFalse(
            self.result["alignment_origin_changed_by_stop"]
        )
        for key in (
            "required_lane_drop_count",
            "backpressure_fault_count",
            "capture_failure_count",
            "compile_failure_count",
            "flush_remaining_count",
        ):
            self.assertEqual(self.result[key], 0)

    def test_real_event_end_precedes_stop_processing(self) -> None:
        execution = Package128SufficiencyStopStore(
            self._temp.name
        ).get_payload(
            "observation_stop_executions",
            self.result["stop_execution_id"],
        )
        self.assertLess(
            execution["final_observation_end_event_time_ns"],
            execution["stop_applied_at_processing_time_ns"],
        )

    def test_real_boundaries_remain_false(self) -> None:
        for key in (
            "memory_write_created",
            "working_readback_created",
            "package_128_extension_action_created",
            "package_128_reacquisition_action_created",
            "package_128_focus_shift_action_created",
            "uncertainty_signal_created",
            "novelty_signal_created",
            "thought_engine_used",
            "endocrine_signal_used",
            "output_created",
            "external_control_created",
            "semantic_understanding_claimed",
            "recognition_claimed",
            "certainty_claimed",
            "subjective_time_claimed",
            "package_129_implemented",
            "package_130_implemented",
            "package_131_implemented",
            "d_laplace_component_used",
            "dlm_1_implemented",
        ):
            self.assertFalse(self.result[key], key)

    def test_real_final_audit_passes(self) -> None:
        self.assertEqual(
            self.audit.audit_status,
            PACKAGE_128_PASS_STATUS,
        )
        self.assertEqual(self.audit.failure_reasons, tuple())

    def test_operator_stop_record_does_not_shadow_controls(self) -> None:
        with contextlib.redirect_stdout(io.StringIO()):
            code = package_128_cli_main(
                [
                    "stop-observation",
                    "--state-dir",
                    self._temp.name,
                    "--reason",
                    "operator_stop",
                ]
            )
        self.assertEqual(code, 0)
        audit = audit_package_128_sufficiency_stop(
            state_dir=self._temp.name,
            append=False,
        )
        self.assertEqual(audit.audit_status, PACKAGE_128_PASS_STATUS)


if __name__ == "__main__":
    unittest.main()
