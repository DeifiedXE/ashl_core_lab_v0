import unittest
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

from ashl_core_v1.runtime.host_sensor_types import stable_id, utc_now
from ashl_core_v1.runtime.multimodal_perception_session_types import (
    ALIGNMENT_WINDOW_SCHEMA_VERSION,
    ARTIFACT_REPLAY_MANIFEST_SCHEMA_VERSION,
    BACKPRESSURE_SCHEMA_VERSION,
    DROPPED_SAMPLE_SCHEMA_VERSION,
    LANE_ITEM_SCHEMA_VERSION,
    TIMELINE_INPUT_REF_SCHEMA_VERSION,
    ArtifactBackedPerceptionTimelineManifest,
    MultimodalAlignmentWindowRecord,
    PerceptionBackpressureRecord,
    PerceptionDroppedSampleRecord,
    PerceptionLaneItem,
    PerceptionTimelineInputRef,
    build_default_multimodal_session_config,
)
from ashl_core_v1.runtime.package_123_cycle_runtime import run_cycle_one
from ashl_core_v1.runtime.package_123_transport_integrity import (
    HOST_STATE_INTERVAL_MS,
    Package123RequiredLaneQueuePolicy,
    REQUIRED_LANE_QUEUE_POLICY_SCHEMA_VERSION,
    TimestampPacedPerceptionReplay,
    build_required_lane_queue_policy,
    build_transport_integrity_records,
)


class Package123TransportIntegrityTests(unittest.TestCase):
    def test_timestamp_paced_replay_preserves_event_time_order(self) -> None:
        now = [1_000_000_000]

        def clock():
            return now[0]

        sleeps = []

        def sleep(seconds):
            sleeps.append(seconds)
            now[0] += int(seconds * 1_000_000_000)

        records = (
            SimpleNamespace(source_kind="microphone", source_record_id="a", source_sequence_index=1, event_time_monotonic_ns=100_000_000),
            SimpleNamespace(source_kind="screen", source_record_id="s", source_sequence_index=0, event_time_monotonic_ns=0),
        )
        result = TimestampPacedPerceptionReplay(clock_ns=clock, sleep_fn=sleep).replay(
            records,
            replay_origin_monotonic_ns=now[0],
            speed=1.0,
        )
        self.assertTrue(result.timestamp_order_valid)
        self.assertFalse(result.aborted)
        self.assertEqual([item.source_record_id for item in result.submission_records], ["s", "a"])
        self.assertTrue(any(value > 0 for value in sleeps))
        self.assertNotEqual(result.submission_records[-1].event_time_monotonic_ns, result.submission_records[-1].processing_time_ns)

    def test_required_lane_queue_policy_is_abort_no_drop(self) -> None:
        with TemporaryDirectory() as state_dir:
            config = _package_123_config(state_dir)
            policy = build_required_lane_queue_policy(config)
            self.assertIsInstance(policy, Package123RequiredLaneQueuePolicy)
            self.assertEqual(policy.schema_version, REQUIRED_LANE_QUEUE_POLICY_SCHEMA_VERSION)
            self.assertEqual(policy.overflow_policy, "abort_run_no_drop")
            self.assertEqual(set(policy.required_lanes), {"screen", "microphone", "host_state"})

    def test_stable_and_silent_data_count_as_complete_non_salient_lanes(self) -> None:
        with TemporaryDirectory() as state_dir:
            prepared = _prepared_transport(
                state_dir,
                primitive_payloads={
                    "visual_frame_primitive:screen": {"visual_primitive_id": "visual_frame_primitive:screen", "quality_uncertainty": 0.0},
                    "audio_primitive:silent": {"audio_primitive_id": "audio_primitive:silent", "amplitude_envelope": (0.0, 0.0), "quality_uncertainty": 0.1},
                    "host_state_primitive:stable": {"host_state_primitive_id": "host_state_primitive:stable", "quality_uncertainty": 0.0},
                },
            )
            with patch("ashl_core_v1.runtime.package_123_transport_integrity.PerceptionPrimitiveStore") as store_cls, patch(
                "ashl_core_v1.runtime.package_123_transport_integrity.ContentAddressedSensorArtifactStore"
            ) as sensor_cls:
                store_cls.return_value.get_primitive.side_effect = lambda primitive_id: prepared.primitive_payloads[primitive_id]
                store_cls.return_value.list_compilation_failures.return_value = tuple()
                sensor_cls.return_value.list_failures.return_value = tuple()
                records = build_transport_integrity_records(
                    state_dir=state_dir,
                    experiment_run_id="package_123_experiment_run:test",
                    cycle_index=1,
                    prepared_transport=prepared,
                    configuration_hash="config_hash:test",
                )
            summary = records["integrity_summary"]
            coverage = records["coverage_records"][0]
            self.assertTrue(summary.teacher_review_eligible)
            self.assertEqual(summary.incomplete_alignment_window_count, 0)
            self.assertTrue(coverage.required_lanes_complete)
            self.assertFalse(coverage.screen.salient_change_present)
            self.assertFalse(coverage.audio.salient_change_present)

    def test_drop_and_backpressure_block_teacher_review_eligibility(self) -> None:
        with TemporaryDirectory() as state_dir:
            prepared = _prepared_transport(
                state_dir,
                dropped_records=(
                    PerceptionDroppedSampleRecord(
                        dropped_sample_record_id=stable_id("perception_dropped_sample"),
                        schema_version=DROPPED_SAMPLE_SCHEMA_VERSION,
                        created_at=utc_now(),
                        session_id="bounded_multimodal_perception_session:test",
                        source_kind="screen",
                        source_record_id="sensor_raw_artifact:screen",
                        reason_code="lane_queue_overflow",
                        drop_policy="drop_oldest_with_trace",
                        raw_artifact_deleted=False,
                        primitive_deleted=False,
                        timeline_gap_created=False,
                        uncertainty_increase=0.1,
                        source_trace_refs=tuple(),
                    ),
                ),
                backpressure_records=(
                    PerceptionBackpressureRecord(
                        backpressure_record_id=stable_id("perception_backpressure"),
                        schema_version=BACKPRESSURE_SCHEMA_VERSION,
                        created_at=utc_now(),
                        session_id="bounded_multimodal_perception_session:test",
                        source_kind="screen",
                        queue_depth_before=1,
                        queue_depth_limit=1,
                        policy="drop_oldest_with_trace",
                        action_taken="drop_oldest",
                        affected_source_record_ids=("visual_frame_primitive:screen",),
                        uncertainty_increase=0.1,
                        source_trace_refs=tuple(),
                    ),
                ),
                primitive_payloads={
                    "visual_frame_primitive:screen": {"visual_primitive_id": "visual_frame_primitive:screen", "quality_uncertainty": 0.0},
                    "audio_primitive:silent": {"audio_primitive_id": "audio_primitive:silent", "amplitude_envelope": (0.0,), "quality_uncertainty": 0.1},
                    "host_state_primitive:stable": {"host_state_primitive_id": "host_state_primitive:stable", "quality_uncertainty": 0.0},
                },
            )
            with patch("ashl_core_v1.runtime.package_123_transport_integrity.PerceptionPrimitiveStore") as store_cls, patch(
                "ashl_core_v1.runtime.package_123_transport_integrity.ContentAddressedSensorArtifactStore"
            ) as sensor_cls:
                store_cls.return_value.get_primitive.side_effect = lambda primitive_id: prepared.primitive_payloads[primitive_id]
                store_cls.return_value.list_compilation_failures.return_value = tuple()
                sensor_cls.return_value.list_failures.return_value = tuple()
                records = build_transport_integrity_records(
                    state_dir=state_dir,
                    experiment_run_id="package_123_experiment_run:test",
                    cycle_index=1,
                    prepared_transport=prepared,
                    configuration_hash="config_hash:test",
                )
            summary = records["integrity_summary"]
            self.assertFalse(summary.teacher_review_eligible)
            self.assertEqual(summary.screen_drop_count, 1)
            self.assertEqual(summary.backpressure_event_count, 1)
            self.assertTrue(records["fault_records"])

    def test_cycle_one_refuses_without_passed_transport_soak_when_required(self) -> None:
        with TemporaryDirectory() as state_dir:
            with self.assertRaises(RuntimeError):
                run_cycle_one(state_dir=state_dir, allow_dirty_tree=True, require_passed_transport_soak=True)

    def test_host_state_interval_constant_is_250_ms_for_package_123(self) -> None:
        self.assertEqual(HOST_STATE_INTERVAL_MS, 250)


def _package_123_config(state_dir: str):
    config = build_default_multimodal_session_config(
        state_dir=state_dir,
        alignment_window_ms=500,
        maximum_window_count=1,
        maximum_session_duration_ms=500,
    )
    payload = config.to_dict()
    payload["enabled_source_kinds"] = ("screen", "microphone", "host_state")
    payload["required_source_kinds"] = ("screen", "microphone", "host_state")
    payload["optional_source_kinds"] = tuple()
    payload["screen_queue_depth"] = 64
    payload["microphone_queue_depth"] = 32
    payload["host_state_queue_depth"] = 32
    payload["config_sha256"] = ""
    return type(config)(**payload)


def _prepared_transport(state_dir: str, *, primitive_payloads: dict[str, dict[str, object]], dropped_records=tuple(), backpressure_records=tuple()):
    session_id = "bounded_multimodal_perception_session:test"
    refs = (
        _input_ref("screen", "sensor_raw_artifact:screen", 100),
        _input_ref("microphone", "sensor_raw_artifact:audio", 150),
        _input_ref("host_state", "sensor_raw_artifact:host", 200),
    )
    lane_items = (
        _lane_item(session_id, "screen", "sensor_raw_artifact:screen", "visual_frame_primitive", "visual_frame_primitive:screen", 100),
        _lane_item(session_id, "microphone", "sensor_raw_artifact:audio", "audio_primitive", "audio_primitive:silent", 150),
        _lane_item(session_id, "host_state", "sensor_raw_artifact:host", "host_state_primitive", "host_state_primitive:stable", 200),
    )
    window = MultimodalAlignmentWindowRecord(
        alignment_window_id="multimodal_alignment_window:test",
        schema_version=ALIGNMENT_WINDOW_SCHEMA_VERSION,
        created_at=utc_now(),
        session_id=session_id,
        window_index=0,
        window_start_relative_ns=0,
        window_end_relative_ns=500_000_000,
        camera_lane_item_ids=tuple(),
        screen_lane_item_ids=(lane_items[0].lane_item_id,),
        microphone_lane_item_ids=(lane_items[1].lane_item_id,),
        host_state_lane_item_ids=(lane_items[2].lane_item_id,),
        present_source_kinds=("host_state", "microphone", "screen"),
        missing_required_source_kinds=tuple(),
        visual_change_present=False,
        audio_activity_present=True,
        host_state_delta_present=False,
        aggregate_quality_uncertainty=0.1,
        complete_for_config=True,
        semantic_binding_created=False,
        source_trace_refs=tuple(),
    )
    return SimpleNamespace(
        session_id=session_id,
        manifest=ArtifactBackedPerceptionTimelineManifest(
            manifest_id=stable_id("package_123_manifest"),
            schema_version=ARTIFACT_REPLAY_MANIFEST_SCHEMA_VERSION,
            created_at=utc_now(),
            input_refs=refs,
            source_artifacts_are_real=True,
            sources_captured_simultaneously=False,
            deterministic_replay=True,
            manifest_sha256="",
        ),
        config=_package_123_config(state_dir),
        lane_items=lane_items,
        windows=(window,),
        backpressure_records=backpressure_records,
        dropped_records=dropped_records,
        primitive_payloads=primitive_payloads,
    )


def _input_ref(source_kind: str, artifact_id: str, offset_ms: int) -> PerceptionTimelineInputRef:
    return PerceptionTimelineInputRef(
        input_ref_id=stable_id("package_123_input_ref"),
        schema_version=TIMELINE_INPUT_REF_SCHEMA_VERSION,
        source_kind=source_kind,
        source_artifact_id=artifact_id,
        source_ephemeral_buffer_id=None,
        replay_relative_offset_ms=offset_ms,
        compiler_id="compiler",
        compiler_config_id="config",
        privacy_policy_id="grounding_conservative_v0" if source_kind == "microphone" else None,
        source_trace_refs=tuple(),
    )


def _lane_item(session_id: str, source_kind: str, artifact_id: str, primitive_kind: str, primitive_id: str, offset_ms: int) -> PerceptionLaneItem:
    return PerceptionLaneItem(
        lane_item_id=stable_id("perception_lane_item"),
        schema_version=LANE_ITEM_SCHEMA_VERSION,
        session_id=session_id,
        source_kind=source_kind,
        source_artifact_id=artifact_id,
        source_buffer_id=None,
        source_monotonic_ns=offset_ms * 1_000_000,
        session_relative_ns=offset_ms * 1_000_000,
        primitive_record_kind=primitive_kind,
        primitive_record_id=primitive_id,
        perception_readable_data_id=f"perception_readable_data:{primitive_id}",
        quality_uncertainty=0.1,
        source_trace_refs=tuple(),
    )


if __name__ == "__main__":
    unittest.main()
