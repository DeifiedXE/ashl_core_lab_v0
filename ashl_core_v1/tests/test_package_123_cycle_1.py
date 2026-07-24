import unittest
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import Mock, patch

from ashl_core_v1.runtime.package_123_cycle_runtime import run_cycle_one
from ashl_core_v1.runtime.package_123_cycle_store import Package123CycleStore
from ashl_core_v1.runtime.package_123_types import (
    PREFLIGHT_SCHEMA_VERSION,
    Package123PreflightRecord,
    build_source_profile,
    utc_now,
)


class Package123CycleOneTests(unittest.TestCase):
    def test_cycle_one_persists_waiting_review_without_auto_approval(self):
        with TemporaryDirectory() as state_dir:
            result = SimpleNamespace(
                stopped_at_teacher_gate=True,
                package_115_session_id="bounded_embodied_session:cycle1",
                perception_readable_data_ids=("perception_readable_data:1",),
                session_id="bounded_multimodal_perception_session:1",
                pending_teacher_review_ids=("pending_teacher_review:cycle1:1",),
                source_trace_refs=("multimodal_trace:1",),
            )
            runtime = SimpleNamespace(embodied_runtime=object())
            preflight = Package123PreflightRecord(
                preflight_id="package_123_preflight:test",
                schema_version=PREFLIGHT_SCHEMA_VERSION,
                created_at=utc_now(),
                experiment_run_id="package_123_experiment_run:test",
                cycle_index=1,
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
            capture = _capture_payload()
            prepared = SimpleNamespace(
                session_id="bounded_multimodal_perception_session:prepared",
                lane_items=tuple(),
                source_trace_refs=("multimodal_trace:prepared",),
            )
            integrity = {
                "integrity_summary": SimpleNamespace(
                    teacher_review_eligible=True,
                    to_dict=lambda: {"teacher_review_eligible": True},
                )
            }

            with patch("ashl_core_v1.runtime.package_123_cycle_runtime.run_package_123_preflight", return_value=preflight), patch(
                "ashl_core_v1.runtime.package_123_cycle_runtime.capture_package_123_sources",
                return_value=capture,
            ), patch(
                "ashl_core_v1.runtime.package_123_cycle_runtime._prepare_package_122_transport",
                return_value=(prepared, runtime),
            ), patch(
                "ashl_core_v1.runtime.package_123_cycle_runtime._persist_transport_integrity",
                return_value=integrity,
            ), patch(
                "ashl_core_v1.runtime.package_123_cycle_runtime._run_prepared_package_122_session",
                return_value=result,
            ), patch(
                "ashl_core_v1.runtime.package_123_cycle_runtime.TeacherGatedSessionResumeCommitRuntime"
            ) as runtime_cls:
                persist_runtime = runtime_cls.return_value
                payload = run_cycle_one(state_dir=state_dir, render_endpoint="default", allow_dirty_tree=True)

            self.assertEqual(payload["status"], "cycle_1_waiting_teacher_review")
            persist_runtime.persist_waiting_session.assert_called_once()
            cycle = Package123CycleStore(state_dir).latest_cycle_record(1)
            self.assertEqual(cycle["final_session_state"], "WAITING_TEACHER_REVIEW")
            self.assertFalse(cycle["readback_loaded_before_event"])
            self.assertEqual(cycle["readback_record_refs"], [])


def _capture_payload():
    profile = build_source_profile(
        experiment_run_id="package_123_experiment_run:test",
        screen_binding_id="window_binding:test",
        audio_source_descriptor_id="loopback_descriptor:test",
    )
    return {
        "source_profile": profile,
        "stimulus_manifest": SimpleNamespace(experiment_run_id="package_123_experiment_run:test"),
        "screen_artifact_ids": ("sensor_raw_artifact:screen",),
        "audio_artifact_ids": ("sensor_raw_artifact:audio",),
        "host_state_artifact_ids": ("sensor_raw_artifact:host",),
        "manifest": object(),
        "stimulus_started_monotonic_ns": 300,
    }


if __name__ == "__main__":
    unittest.main()
