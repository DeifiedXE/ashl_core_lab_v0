from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import re

from ashl_core_v1.host_body import (
    host_body_readback_internal_action_influence,
    internal_action_home_surface_link,
)
from ashl_core_v1.host_body.host_body_internal_action_choice import (
    ALLOWED_INTERNAL_ACTION_KINDS,
)
from ashl_core_v1.runtime.bounded_multimodal_perception_session_runtime import (
    BoundedMultimodalPerceptionSessionRuntime,
)
from ashl_core_v1.runtime.cross_window_temporal_link import (
    build_cross_window_temporal_link,
)
from ashl_core_v1.runtime.host_sensor_types import stable_id, utc_now
from ashl_core_v1.runtime.local_operator_console_store import (
    build_default_console_store,
)
from ashl_core_v1.runtime.local_operator_event_stream import LocalOperatorEventStream
from ashl_core_v1.runtime.multimodal_perception_session_types import (
    LANE_ITEM_SCHEMA_VERSION,
    MultimodalPerceptionSessionMode,
    PerceptionLaneItem,
    build_default_multimodal_session_config,
)
from ashl_core_v1.runtime.package_126_reacquisition_audit import (
    audit_package_126_reacquisition,
)
from ashl_core_v1.runtime.package_126_reacquisition_cli import _chain_payload
from ashl_core_v1.runtime.package_126_reacquisition_runtime import (
    PACKAGE_126_EVENT_KINDS,
    _emit_event,
    _synthetic_parent,
    _synthetic_plan,
    run_synthetic_package_126_controls,
    run_synthetic_package_126_smoke,
)
from ashl_core_v1.runtime.package_126_reacquisition_store import (
    Package126ReacquisitionStore,
)
from ashl_core_v1.runtime.perception_reacquisition_internal_action import (
    cancel_pending_reacquisition,
    create_bounded_reacquisition_internal_action,
)
from ashl_core_v1.runtime.perception_reacquisition_policy import (
    create_reacquisition_authorization,
    create_reacquisition_request,
    decide_reacquisition_eligibility,
)
from ashl_core_v1.runtime.perception_reacquisition_types import (
    BASELINE_COMMIT,
    MAXIMUM_REACQUISITION_WINDOW_NS,
    CompletedObservationWindowReference,
    EphemeralAudioDeletionVerificationRecord,
    ReacquisitionCaptureExecution,
)
from ashl_core_v1.runtime.sampling_plan_identity import (
    build_sampling_plan_identity,
    clone_sampling_plan_identity,
    plan_identity_equal,
)
from ashl_core_v1.runtime.windows_wasapi_loopback_source import (
    WindowsWasapiLoopbackSource,
)


class Package126PolicyAndIdentityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.plan = _synthetic_plan()
        self.parent = _synthetic_parent(self.plan)
        self.authorization = create_reacquisition_authorization(
            parent=self.parent
        )
        self.request = create_reacquisition_request(
            parent=self.parent,
            authorization=self.authorization,
            requested_action_kind="capture_again",
            requested_plan=self.plan,
        )

    def decide(self, **kwargs):
        return decide_reacquisition_eligibility(
            request=kwargs.pop("request", self.request),
            parent=kwargs.pop("parent", self.parent),
            parent_plan=kwargs.pop("parent_plan", self.plan),
            requested_plan=kwargs.pop("requested_plan", self.plan),
            authorization=kwargs.pop("authorization", self.authorization),
            **kwargs,
        )

    def test_baseline_and_exact_new_internal_action_kinds(self) -> None:
        self.assertEqual(
            BASELINE_COMMIT,
            "acb543ed79a9d56bbf4a1660628200f8916497d2",
        )
        self.assertIn("capture_again", ALLOWED_INTERNAL_ACTION_KINDS)
        self.assertIn("listen_again", ALLOWED_INTERNAL_ACTION_KINDS)
        self.assertIn("extend_observation_window", ALLOWED_INTERNAL_ACTION_KINDS)

    def test_readback_and_home_surface_cannot_source_reacquisition(self) -> None:
        self.assertNotIn(
            "capture_again",
            host_body_readback_internal_action_influence.ALLOWED_INTERNAL_ACTION_KINDS,
        )
        self.assertNotIn(
            "listen_again",
            host_body_readback_internal_action_influence.ALLOWED_INTERNAL_ACTION_KINDS,
        )
        self.assertNotIn(
            "capture_again",
            internal_action_home_surface_link.ALLOWED_INTERNAL_ACTION_KINDS,
        )

    def test_deterministic_plan_hash_excludes_record_identity_and_time(self) -> None:
        clone = clone_sampling_plan_identity(self.plan)
        self.assertNotEqual(
            self.plan.sampling_plan_identity_id,
            clone.sampling_plan_identity_id,
        )
        self.assertNotEqual(self.plan.created_at, clone.created_at)
        self.assertTrue(plan_identity_equal(self.plan, clone))

    def test_each_material_plan_change_changes_hash(self) -> None:
        base = self.plan
        changes = {
            "screen_target_descriptor_hash": "different-target",
            "screen_region_hash": "different-region",
            "audio_endpoint_descriptor_hash": "different-endpoint",
            "audio_capture_config_hash": "different-audio-config",
            "audio_privacy_mode": "different-privacy",
            "audio_compiler_version": "different-compiler",
            "required_lanes": ("screen", "host_state"),
        }
        for name, value in changes.items():
            payload = {
                key: getattr(base, key)
                for key in (
                    "plan_kind",
                    "modality_scope",
                    "required_lanes",
                    "participating_lanes",
                    "screen_target_descriptor_hash",
                    "screen_region_hash",
                    "screen_capture_config_hash",
                    "audio_endpoint_descriptor_hash",
                    "audio_capture_config_hash",
                    "audio_privacy_mode",
                    "audio_blur_policy_version",
                    "host_state_config_hash",
                    "visual_compiler_version",
                    "audio_compiler_version",
                    "redaction_config_hash",
                    "event_clock_domain",
                    "processing_clock_domain",
                    "replay_clock_domain",
                )
            }
            payload[name] = value
            changed = build_sampling_plan_identity(**payload)
            self.assertNotEqual(
                base.canonical_plan_hash,
                changed.canonical_plan_hash,
                name,
            )

    def test_explicit_authorization_and_request_do_not_open_sensor(self) -> None:
        self.assertEqual(
            self.authorization.authorized_by,
            "local_operator",
        )
        self.assertEqual(self.request.request_status, "pending")
        self.assertFalse(self.request.thought_engine_used)
        self.assertFalse(self.request.memory_used)
        self.assertFalse(self.request.uncertainty_signal_used)

    def test_completed_clean_parent_is_eligible(self) -> None:
        decision = self.decide()
        self.assertEqual(decision.decision, "allow")
        self.assertEqual(
            decision.granted_window_ns,
            MAXIMUM_REACQUISITION_WINDOW_NS,
        )

    def test_parent_integrity_failures_block(self) -> None:
        for field in (
            "required_lane_drop_count",
            "backpressure_fault_count",
            "capture_failure_count",
            "compile_failure_count",
            "flush_remaining_count",
        ):
            payload = self.parent.to_dict()
            payload["completed_window_reference_id"] = stable_id("bad-parent")
            payload[field] = 1
            bad = CompletedObservationWindowReference(**payload)
            result = self.decide(parent=bad)
            self.assertEqual(result.decision, "block", field)

    def test_active_and_interrupted_parent_block(self) -> None:
        for status in ("active", "interrupted"):
            payload = self.parent.to_dict()
            payload["completed_window_reference_id"] = stable_id("bad-parent")
            payload["completion_status"] = status
            result = self.decide(
                parent=CompletedObservationWindowReference(**payload)
            )
            self.assertEqual(result.decision, "block")
            self.assertIn(
                "parent_window_not_completed",
                result.failure_reasons,
            )

    def test_authorization_chain_binding_and_missing_authorization(self) -> None:
        self.assertEqual(
            self.decide(authorization=None).decision,
            "block",
        )
        other_parent = _synthetic_parent(self.plan)
        wrong = create_reacquisition_authorization(parent=other_parent)
        self.assertEqual(
            self.decide(authorization=wrong).decision,
            "block",
        )

    def test_budget_precedence_and_second_attempt(self) -> None:
        self.assertEqual(
            self.decide(prior_attempt_count=1).decision,
            "block",
        )
        self.assertEqual(
            self.decide(parent_to_request_gap_ns=5_000_000_001).decision,
            "expired",
        )
        self.assertEqual(
            self.decide(chain_duration_ns=9_000_000_000).decision,
            "block",
        )

    def test_operator_stop_has_highest_precedence(self) -> None:
        result = self.decide(
            operator_stop_requested=True,
            parent_to_request_gap_ns=5_000_000_001,
        )
        self.assertIn("operator_stop", result.failure_reasons)
        self.assertEqual(result.decision, "expired")

    def test_plan_privacy_and_old_artifact_mismatch_block(self) -> None:
        mismatch = build_sampling_plan_identity(
            plan_kind="multimodal_same_plan",
            modality_scope=("screen", "microphone", "host_state"),
            required_lanes=("screen", "microphone", "host_state"),
            participating_lanes=("screen", "microphone", "host_state"),
            screen_target_descriptor_hash="different",
            screen_region_hash="synthetic-screen-region",
            screen_capture_config_hash="synthetic-screen-config",
            audio_endpoint_descriptor_hash="synthetic-audio-endpoint",
            audio_capture_config_hash="synthetic-audio-config",
            audio_privacy_mode="recognition_ephemeral",
            audio_blur_policy_version="recognition_ephemeral_v0",
            host_state_config_hash="synthetic-host-config",
            visual_compiler_version="visual_frame_primitive_compiler_v0",
            audio_compiler_version="audio_primitive_compiler_v0",
            redaction_config_hash="synthetic-redaction",
        )
        self.assertEqual(
            self.decide(requested_plan=mismatch).decision,
            "block",
        )
        self.assertEqual(
            self.decide(old_artifact_supplied=True).decision,
            "block",
        )

    def test_allowed_decision_creates_only_internal_action(self) -> None:
        decision = self.decide()
        action = create_bounded_reacquisition_internal_action(
            request=self.request,
            eligibility=decision,
            parent=self.parent,
        )
        self.assertIsNotNone(action)
        self.assertTrue(action.internal_only)
        self.assertTrue(action.creates_new_capture_window)
        self.assertFalse(action.external_side_effect)
        self.assertFalse(action.selected_action_created)
        self.assertFalse(action.final_action_created)
        self.assertFalse(action.direct_command_created)
        self.assertFalse(action.replays_old_artifact)

    def test_blocked_decision_creates_no_action(self) -> None:
        action = create_bounded_reacquisition_internal_action(
            request=self.request,
            eligibility=self.decide(authorization=None),
            parent=self.parent,
        )
        self.assertIsNone(action)

    def test_pending_cancellation_and_started_stop_distinction(self) -> None:
        pending = cancel_pending_reacquisition(request=self.request)
        started = cancel_pending_reacquisition(
            request=self.request,
            child_capture_started=True,
        )
        self.assertTrue(pending.cancellation_succeeded)
        self.assertFalse(started.cancellation_succeeded)
        self.assertTrue(started.child_capture_started)

    def test_cross_window_link_never_merges_windows(self) -> None:
        link = build_cross_window_temporal_link(
            parent_observation_window_id="parent",
            child_observation_window_id="child",
            parent_final_anchor_ref="parent-end",
            child_start_anchor_ref="child-start",
            parent_final_event_time_ns=100,
            child_start_event_time_ns=150,
            parent_clock_domain="event",
            child_clock_domain="event",
            parent_processing_clock_domain="processing",
            child_processing_clock_domain="processing",
        )
        self.assertEqual(link.external_gap_ns, 50)
        self.assertFalse(link.windows_temporally_contiguous)
        self.assertTrue(link.gap_explicit)

    def test_session_identity_collision_rejects_clean_execution(self) -> None:
        with self.assertRaises(ValueError):
            ReacquisitionCaptureExecution(
                reacquisition_execution_id="execution",
                schema_version="ashl_package_126_reacquisition_capture_execution_v0",
                created_at=utc_now(),
                internal_action_id="action",
                parent_runtime_session_id="p-runtime",
                parent_perception_session_id="p-perception",
                parent_observation_window_id="p-window",
                child_runtime_session_id="c-runtime",
                child_perception_session_id="c-perception",
                child_observation_window_id="c-window",
                parent_plan_identity_ref="p-plan",
                child_plan_identity_ref="c-plan",
                parent_capture_session_refs=("collision",),
                child_capture_session_refs=("collision",),
                parent_alignment_origin_ref="p-origin",
                child_alignment_origin_ref="c-origin",
                event_clock_domain_preserved=True,
                processing_clock_domain_preserved=True,
                capture_session_ids_reused=False,
                source_targets_preserved=True,
                source_configuration_preserved=True,
                privacy_policy_preserved=True,
                sources_reopened=True,
                old_artifact_reused=False,
                requested_window_ns=2_500_000_000,
                actual_window_ns=2_500_000_000,
                execution_status="completed_clean",
                failure_kind=None,
                source_record_refs=tuple(),
                source_trace_refs=tuple(),
            )


class Package126TransportStoreAndEventTests(unittest.TestCase):
    def test_wasapi_reacquisition_metadata_is_recognition_ephemeral(self) -> None:
        actual = {
            "sample_rate": 48_000,
            "channels": 2,
            "original_format": "float32",
            "channel_mapping": "stereo",
            "silence_fill_performed": False,
            "inserted_silence_frame_count": 0,
        }
        pcm = bytes(48_000 * 2 * 2 // 10)
        with patch(
            "ashl_core_v1.runtime.windows_wasapi_loopback_source._probe_default_endpoint_format",
            return_value=actual,
        ), patch(
            "ashl_core_v1.runtime.windows_wasapi_loopback_source._capture_wasapi_loopback_pcm_s16le",
            return_value=(pcm, actual),
        ):
            source = WindowsWasapiLoopbackSource()
            samples = source.capture_samples(
                duration_ms=100,
                capture_mode="recognition_ephemeral",
            )
        self.assertTrue(samples)
        self.assertEqual(
            samples[0].metadata["capture_mode"],
            "recognition_ephemeral",
        )
        self.assertEqual(
            samples[0].metadata["retention_classification"],
            "ram_only_recognition_ephemeral",
        )

    def test_live_compiled_package_122_alignment_accepts_audio_host(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime = BoundedMultimodalPerceptionSessionRuntime(tmp)
            config = build_default_multimodal_session_config(
                state_dir=tmp,
                mode=MultimodalPerceptionSessionMode.LIVE_BOUNDED_MULTIMODAL_CAPTURE.value,
                alignment_window_ms=500,
                maximum_window_count=2,
                maximum_session_duration_ms=2500,
            )
            payload = config.to_dict()
            payload.update(
                {
                    "config_id": stable_id("listen-config"),
                    "enabled_source_kinds": ("microphone", "host_state"),
                    "required_source_kinds": ("microphone", "host_state"),
                    "optional_source_kinds": tuple(),
                    "config_sha256": "",
                }
            )
            config = type(config)(**payload)
            session_id = "child-perception"
            items = (
                self._lane(session_id, "microphone", "audio_primitive"),
                self._lane(session_id, "host_state", "host_state_primitive"),
            )
            prepared = runtime.prepare_live_compiled_alignment_transport(
                lane_items=items,
                config=config,
                session_id=session_id,
            )
            self.assertEqual(len(prepared.windows), 1)
            self.assertTrue(prepared.windows[0].complete_for_config)
            self.assertEqual(prepared.dropped_records, tuple())
            self.assertEqual(prepared.backpressure_records, tuple())

    def test_live_alignment_rejects_missing_required_lane(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime = BoundedMultimodalPerceptionSessionRuntime(tmp)
            config = build_default_multimodal_session_config(
                state_dir=tmp,
                mode=MultimodalPerceptionSessionMode.LIVE_BOUNDED_MULTIMODAL_CAPTURE.value,
            )
            with self.assertRaises(ValueError):
                runtime.prepare_live_compiled_alignment_transport(
                    lane_items=(
                        self._lane("child", "microphone", "audio_primitive"),
                    ),
                    config=config,
                    session_id="child",
                )

    def test_append_only_store_rejects_duplicate_record_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = Package126ReacquisitionStore(tmp)
            payload = {
                "control_result_id": "same-id",
                "created_at": utc_now(),
            }
            store.append_payload(
                "package_126_control_results",
                "control_result_id",
                "same-id",
                payload,
            )
            with self.assertRaises(Exception):
                store.append_payload(
                    "package_126_control_results",
                    "control_result_id",
                    "same-id",
                    payload,
                )

    def test_chain_view_filters_every_record_family_to_requested_parent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = Package126ReacquisitionStore(tmp)
            for suffix in ("a", "b"):
                parent_window_id = f"parent-{suffix}"
                parent_ref_id = f"parent-ref-{suffix}"
                request_id = f"request-{suffix}"
                child_window_id = f"child-{suffix}"
                records = (
                    (
                        "completed_parent_window_refs",
                        "completed_window_reference_id",
                        parent_ref_id,
                        {
                            "completed_window_reference_id": parent_ref_id,
                            "observation_window_id": parent_window_id,
                        },
                    ),
                    (
                        "perception_reacquisition_requests",
                        "reacquisition_request_id",
                        request_id,
                        {
                            "reacquisition_request_id": request_id,
                            "parent_window_reference_id": parent_ref_id,
                        },
                    ),
                    (
                        "reacquisition_eligibility_decisions",
                        "eligibility_decision_id",
                        f"decision-{suffix}",
                        {
                            "eligibility_decision_id": f"decision-{suffix}",
                            "reacquisition_request_id": request_id,
                        },
                    ),
                    (
                        "bounded_reacquisition_internal_actions",
                        "internal_action_id",
                        f"action-{suffix}",
                        {
                            "internal_action_id": f"action-{suffix}",
                            "parent_observation_window_id": parent_window_id,
                        },
                    ),
                    (
                        "reacquisition_capture_executions",
                        "reacquisition_execution_id",
                        f"execution-{suffix}",
                        {
                            "reacquisition_execution_id": f"execution-{suffix}",
                            "parent_observation_window_id": parent_window_id,
                            "child_observation_window_id": child_window_id,
                        },
                    ),
                    (
                        "observation_window_states",
                        "observation_window_state_id",
                        f"window-state-{suffix}",
                        {
                            "observation_window_state_id": f"window-state-{suffix}",
                            "observation_window_id": child_window_id,
                        },
                    ),
                    (
                        "cross_window_temporal_links",
                        "continuity_link_id",
                        f"link-{suffix}",
                        {
                            "continuity_link_id": f"link-{suffix}",
                            "parent_observation_window_id": parent_window_id,
                        },
                    ),
                )
                for table, id_column, record_id, payload in records:
                    store.append_payload(
                        table,
                        id_column,
                        record_id,
                        {"created_at": utc_now(), **payload},
                    )
            payload = _chain_payload(store, "parent-b")
            for records in payload.values():
                self.assertEqual(len(records), 1)
            self.assertEqual(
                payload["requests"][0]["reacquisition_request_id"],
                "request-b",
            )

    def test_all_package_126_event_kinds_accept_required_identities(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            stream = LocalOperatorEventStream(build_default_console_store(tmp))
            for event_kind in PACKAGE_126_EVENT_KINDS:
                event = stream.append_event(
                    event_kind=event_kind,
                    parent_runtime_session_id="parent-runtime",
                    parent_perception_session_id="parent-perception",
                    parent_observation_window_id="parent-window",
                    child_runtime_session_id="child-runtime",
                    child_perception_session_id="child-perception",
                    child_observation_window_id="child-window",
                )
                self.assertFalse(event.llm_used)
                self.assertFalse(event.codex_used)
                self.assertFalse(event.network_used)

    def test_event_delivery_failure_is_visible_and_strict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = Package126ReacquisitionStore(tmp)
            parent = {
                "runtime_session_id": "parent-runtime",
                "perception_session_id": "parent-perception",
                "observation_window_id": "parent-window",
            }
            with patch.object(
                LocalOperatorEventStream,
                "append_event",
                side_effect=RuntimeError("delivery fault"),
            ):
                self.assertFalse(
                    _emit_event(
                        Path(tmp),
                        store=store,
                        event_kind="perception_reacquisition_requested",
                        parent=parent,
                        refs=("request",),
                        strict=False,
                    )
                )
                with self.assertRaises(RuntimeError):
                    _emit_event(
                        Path(tmp),
                        store=store,
                        event_kind="perception_reacquisition_requested",
                        parent=parent,
                        refs=("request",),
                        strict=True,
                    )
            self.assertEqual(
                len(store.list_payloads("operator_event_delivery_failures")),
                2,
            )

    def test_ephemeral_deletion_requires_overwrite_and_zero_live_bytes(self) -> None:
        valid = EphemeralAudioDeletionVerificationRecord(
            deletion_record_id="deletion",
            schema_version="ashl_package_126_ephemeral_audio_deletion_verification_v0",
            created_at=utc_now(),
            child_observation_window_id="child",
            ephemeral_audio_session_id="ring",
            content_sha256_before_deletion="hash",
            transient_file_path_fingerprint=None,
            backend_transient_file_created=False,
            ring_buffer_overwritten=True,
            ring_buffer_live_bytes_after=0,
            transient_file_absent_after=True,
            raw_audio_retained=False,
            deletion_verified=True,
            source_record_refs=tuple(),
            source_trace_refs=tuple(),
        )
        self.assertTrue(valid.deletion_verified)
        with self.assertRaises(ValueError):
            EphemeralAudioDeletionVerificationRecord(
                **{
                    **valid.to_dict(),
                    "deletion_record_id": "invalid",
                    "ring_buffer_live_bytes_after": 1,
                }
            )

    def test_synthetic_smoke_opens_no_sensor_and_all_controls_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_synthetic_package_126_smoke(state_dir=tmp)
            self.assertEqual(result["sensor_open_count"], 0)
            self.assertTrue(all(result["controls"].values()))
            self.assertFalse(result["memory_write_created"])
            self.assertFalse(result["output_created"])
            self.assertFalse(result["external_control_created"])

    @staticmethod
    def _lane(
        session_id: str,
        source_kind: str,
        primitive_kind: str,
    ) -> PerceptionLaneItem:
        return PerceptionLaneItem(
            lane_item_id=stable_id("lane-item"),
            schema_version=LANE_ITEM_SCHEMA_VERSION,
            session_id=session_id,
            source_kind=source_kind,
            source_artifact_id=(
                f"artifact:{source_kind}"
                if source_kind != "microphone"
                else None
            ),
            source_buffer_id=(
                "ephemeral-buffer"
                if source_kind == "microphone"
                else None
            ),
            source_monotonic_ns=1,
            session_relative_ns=0,
            primitive_record_kind=primitive_kind,
            primitive_record_id=f"primitive:{source_kind}",
            perception_readable_data_id=f"readable:{source_kind}",
            quality_uncertainty=0.0,
            source_trace_refs=tuple(),
        )


class Package126BoundaryTests(unittest.TestCase):
    def test_runtime_files_do_not_import_d_laplace_or_future_packages(self) -> None:
        runtime = Path(__file__).parents[1] / "runtime"
        files = (
            "perception_reacquisition_types.py",
            "sampling_plan_identity.py",
            "perception_reacquisition_policy.py",
            "perception_reacquisition_internal_action.py",
            "cross_window_temporal_link.py",
            "package_126_reacquisition_store.py",
            "package_126_reacquisition_runtime.py",
        )
        text = "\n".join(
            (runtime / name).read_text(encoding="utf-8") for name in files
        )
        self.assertIsNone(
            re.search(
                r"^\s*(?:from|import)\s+.*d_laplace",
                text,
                flags=re.IGNORECASE | re.MULTILINE,
            )
        )
        self.assertNotIn("ACTION_BID", text)

    def test_no_repository_data_path_is_used(self) -> None:
        runtime = Path(__file__).parents[1] / "runtime"
        text = (
            runtime / "package_126_reacquisition_store.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("ashl_core_v1/data", text)
        self.assertIn("explicit external state_dir", text)

    def test_controls_include_no_event_valid_execution_case(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            controls = run_synthetic_package_126_controls(state_dir=tmp)
            self.assertTrue(controls["no_event_child_control_passed"])

    def test_final_audit_requires_and_accepts_two_bounded_real_run_records(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = Package126ReacquisitionStore(tmp)
            controls = run_synthetic_package_126_controls(state_dir=tmp)
            for action_kind in ("capture_again", "listen_again"):
                run = self._passing_run(action_kind)
                store.append_payload(
                    "package_126_real_run_records",
                    "real_run_record_id",
                    run["real_run_record_id"],
                    run,
                )
                score = {
                    "score_equivalence_record_id": stable_id("score"),
                    "created_at": utc_now(),
                    "package_112_score_changed": False,
                    "package_126_score_contribution": 0,
                    "authoritative_score_before": 5,
                    "authoritative_score_after": 5,
                }
                store.append_payload(
                    "package_112_score_equivalence_records",
                    "score_equivalence_record_id",
                    score["score_equivalence_record_id"],
                    score,
                )
            self.assertTrue(all(controls.values()))
            audit = audit_package_126_reacquisition(
                state_dir=tmp,
                append=True,
            )
            self.assertEqual(
                audit.audit_status,
                "passed_bounded_re_sampling_and_listen_again_internal_action_v0",
            )
            self.assertTrue(audit.capture_again_real_run_verified)
            self.assertTrue(audit.listen_again_real_run_verified)
            self.assertFalse(audit.raw_audio_retained)
            self.assertFalse(audit.package_112_score_changed)

    def test_final_audit_rejects_overlong_capture_window(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = Package126ReacquisitionStore(tmp)
            run_synthetic_package_126_controls(state_dir=tmp)
            for action_kind in ("capture_again", "listen_again"):
                run = self._passing_run(action_kind)
                if action_kind == "capture_again":
                    run["child"]["actual_window_ns"] = 2_500_000_001
                store.append_payload(
                    "package_126_real_run_records",
                    "real_run_record_id",
                    run["real_run_record_id"],
                    run,
                )
                score = {
                    "score_equivalence_record_id": stable_id("score"),
                    "created_at": utc_now(),
                    "package_112_score_changed": False,
                    "package_126_score_contribution": 0,
                    "authoritative_score_before": 5,
                    "authoritative_score_after": 5,
                }
                store.append_payload(
                    "package_112_score_equivalence_records",
                    "score_equivalence_record_id",
                    score["score_equivalence_record_id"],
                    score,
                )
            audit = audit_package_126_reacquisition(
                state_dir=tmp,
                append=False,
            )
            self.assertNotEqual(
                audit.audit_status,
                "passed_bounded_re_sampling_and_listen_again_internal_action_v0",
            )
            self.assertIn(
                "capture_again_real_run_not_verified",
                audit.failure_reasons,
            )

    @staticmethod
    def _passing_run(action_kind: str) -> dict[str, object]:
        deletion = {
            "deletion_verified": True,
            "ring_buffer_live_bytes_after": 0,
            "raw_audio_retained": False,
            "backend_transient_file_created": False,
        }
        parent = {
            "role": "parent",
            "observation_window_id": f"{action_kind}-parent",
            "actual_window_ns": 2_500_000_000,
            "required_windows_expected": 1,
            "required_windows_complete": 1,
            "required_lane_drop_count": 0,
            "backpressure_fault_count": 0,
            "capture_failure_count": 0,
            "compile_failure_count": 0,
            "flush_remaining_count": 0,
        }
        child = {
            "role": "child",
            "observation_window_id": f"{action_kind}-child",
            "actual_window_ns": 2_500_000_000,
            "required_windows_expected": 1,
            "required_windows_complete": 1,
            "screen_capture_session_id": (
                "child-screen" if action_kind == "capture_again" else None
            ),
            "ephemeral_audio_session_id": f"{action_kind}-ring",
            "visual_primitive_refs": (
                ("visual",) if action_kind == "capture_again" else tuple()
            ),
            "audio_primitive_refs": ("audio",),
            "host_state_primitive_refs": ("host",),
            "audio_event_region_present": True,
            "raw_audio_retained": False,
            "raw_parent_artifact_reused": False,
            "semantic_interpretation_created": False,
            "recognition_result_created": False,
            "required_lane_drop_count": 0,
            "backpressure_fault_count": 0,
            "capture_failure_count": 0,
            "compile_failure_count": 0,
            "flush_remaining_count": 0,
            "audio_deletion": deletion,
        }
        return {
            "real_run_record_id": stable_id("real-run"),
            "created_at": utc_now(),
            "action_kind": action_kind,
            "run_status": "passed_real_bounded_reacquisition",
            "internal_action_id": f"{action_kind}-action",
            "parent_plan_hash": "same-plan",
            "child_plan_hash": "same-plan",
            "target_identity_equal": True,
            "configuration_identity_equal": True,
            "capture_session_ids_distinct": True,
            "sources_reopened": True,
            "old_artifact_reused": False,
            "cross_window_gap_ns": 10,
            "continuity_link_id": f"{action_kind}-gap",
            "operator_event_delivery_failure_count": 0,
            "parent": parent,
            "child": child,
        }


if __name__ == "__main__":
    unittest.main()
