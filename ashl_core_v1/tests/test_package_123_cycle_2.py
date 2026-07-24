import unittest
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

from ashl_core_v1.runtime.package_123_cycle_runtime import run_cycle_two
from ashl_core_v1.runtime.package_123_cycle_store import Package123CycleStore
from ashl_core_v1.runtime.package_123_types import CYCLE_RECORD_SCHEMA_VERSION, EXPERIMENT_ID, Package123CycleRecord, PREFLIGHT_SCHEMA_VERSION, Package123PreflightRecord, build_source_profile, utc_now


class Package123CycleTwoTests(unittest.TestCase):
    def test_cycle_two_loads_readback_before_stimulus_and_records_hot_path_influence(self):
        with TemporaryDirectory() as state_dir:
            Package123CycleStore(state_dir).append_cycle_record(_cycle_record())
            active_readback = (
                {
                    "working_readback_commit_id": "working_readback_commit:cycle1",
                    "memory_application_data_ref": "memory_application_data:cycle1",
                },
            )
            result = SimpleNamespace(
                stopped_at_teacher_gate=True,
                package_115_session_id="bounded_embodied_session:cycle2",
                perception_readable_data_ids=("perception_readable_data:2",),
                session_id="bounded_multimodal_perception_session:2",
                pending_teacher_review_ids=("pending_teacher_review:cycle2:1",),
                source_trace_refs=("multimodal_trace:2",),
            )
            score = SimpleNamespace(
                readback_delta=2,
                source_internal_action_candidate_id="host_body_internal_action_candidate:request_teacher_review",
                schema_version="qingyin_host_body_readback_influenced_candidate_score_v0",
                base_candidate_priority=10,
                final_candidate_priority=12,
            )
            runtime = SimpleNamespace(
                embodied_runtime=SimpleNamespace(
                    _records={
                        "bounded_embodied_session:cycle2": {
                            "readback_candidate_scores": (score,),
                            "readback_consumption_evaluation": {
                                "matched_readback_item_ids": ("working_readback_commit:cycle1",)
                            },
                        }
                    }
                )
            )

            with patch("ashl_core_v1.runtime.package_123_cycle_runtime.TeacherGatedSessionStore") as store_cls, patch(
                "ashl_core_v1.runtime.package_123_cycle_runtime.run_package_123_preflight",
                return_value=_preflight(),
            ), patch(
                "ashl_core_v1.runtime.package_123_cycle_runtime.capture_package_123_sources",
                return_value=_capture_payload(),
            ), patch(
                "ashl_core_v1.runtime.package_123_cycle_runtime._run_package_122_session",
                return_value=(result, runtime),
            ), patch(
                "ashl_core_v1.runtime.package_123_cycle_runtime.monotonic_ns",
                side_effect=(100, 200, 400),
            ):
                store_cls.return_value.load_active_working_readback.return_value = active_readback
                payload = run_cycle_two(state_dir=state_dir, render_endpoint="default", allow_dirty_tree=True)

            self.assertEqual(payload["status"], "cycle_2_waiting_teacher_review")
            self.assertTrue(payload["readback_load_timing"]["loaded_before_stimulus"])
            self.assertTrue(payload["readback_load_timing"]["loaded_before_candidate_evaluation"])
            self.assertEqual(payload["readback_influence"]["readback_contribution"], 2.0)
            self.assertTrue(payload["readback_influence"]["actual_runtime_hot_path"])
            self.assertFalse(payload["readback_influence"]["hard_coded_experiment_match_used"])
            self.assertTrue(payload["comparison"]["process_instances_different"])
            self.assertTrue(payload["comparison"]["readback_contribution_nonzero"])


def _preflight() -> Package123PreflightRecord:
    return Package123PreflightRecord(
        preflight_id="package_123_preflight:cycle2",
        schema_version=PREFLIGHT_SCHEMA_VERSION,
        created_at=utc_now(),
        experiment_run_id="package_123_experiment_run:cycle2",
        cycle_index=2,
        window_capture_ready=True,
        visual_contrast_verified=True,
        loopback_source_ready=True,
        loopback_tone_verified=True,
        background_audio_silent=True,
        host_state_ready=True,
        compiler_compatibility_verified=True,
        perception_profile_verified=True,
        llm_runtime_available=False,
        network_required=False,
        preflight_status="passed",
        failure_reasons=tuple(),
    )


def _capture_payload():
    profile = build_source_profile(
        experiment_run_id="package_123_experiment_run:cycle2",
        screen_binding_id="window_binding:cycle2",
        audio_source_descriptor_id="loopback_descriptor:cycle2",
    )
    return {
        "source_profile": profile,
        "stimulus_manifest": SimpleNamespace(experiment_run_id="package_123_experiment_run:cycle2"),
        "screen_artifact_ids": ("sensor_raw_artifact:screen2",),
        "audio_artifact_ids": ("sensor_raw_artifact:audio2",),
        "host_state_artifact_ids": ("sensor_raw_artifact:host2",),
        "manifest": object(),
        "stimulus_started_monotonic_ns": 300,
    }


def _cycle_record() -> Package123CycleRecord:
    return Package123CycleRecord(
        cycle_record_id="package_123_cycle_record:cycle1",
        schema_version=CYCLE_RECORD_SCHEMA_VERSION,
        created_at=utc_now(),
        experiment_id=EXPERIMENT_ID,
        experiment_run_id="package_123_experiment_run:cycle1",
        cycle_index=1,
        process_instance_id="package_123_process_instance:cycle1",
        operating_system_process_id=1,
        preflight_id="package_123_preflight:cycle1",
        source_profile_id="package_123_source_profile:cycle1",
        stimulus_manifest_id="package_123_experiment_run:cycle1",
        screen_artifact_refs=("sensor_raw_artifact:screen1",),
        audio_artifact_refs=("sensor_raw_artifact:audio1",),
        host_state_artifact_refs=("sensor_raw_artifact:host1",),
        perception_readable_data_refs=("perception_readable_data:1",),
        perception_session_id="bounded_multimodal_perception_session:1",
        bounded_runtime_session_id="bounded_embodied_session:cycle1",
        final_session_state="WAITING_TEACHER_REVIEW",
        pending_teacher_review_id="pending_teacher_review:cycle1:1",
        readback_loaded_before_event=False,
        readback_record_refs=tuple(),
        source_trace_refs=("multimodal_trace:1",),
    )


if __name__ == "__main__":
    unittest.main()
