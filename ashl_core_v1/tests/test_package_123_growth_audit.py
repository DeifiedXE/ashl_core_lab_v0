import unittest
from tempfile import TemporaryDirectory
from unittest.mock import patch

from ashl_core_v1.runtime.package_123_cycle_store import Package123CycleStore
from ashl_core_v1.runtime.package_123_growth_audit import audit_package_123_real_perception_growth
from ashl_core_v1.runtime.package_123_types import (
    CYCLE_RECORD_SCHEMA_VERSION,
    EXPERIMENT_ID,
    Package123CycleRecord,
    Package123TwoCycleComparisonRecord,
    RealPerceptionReadbackInfluenceRecord,
    READBACK_INFLUENCE_SCHEMA_VERSION,
    SOURCE_PROFILE_SCHEMA_VERSION,
    TWO_CYCLE_COMPARISON_SCHEMA_VERSION,
    Package123ExperienceSourceProfile,
    utc_now,
)


class Package123GrowthAuditTests(unittest.TestCase):
    def test_missing_authoritative_evidence_blocks_audit(self):
        with TemporaryDirectory() as state_dir:
            record = audit_package_123_real_perception_growth(state_dir)

        self.assertEqual(record.audit_status, "blocked_package_123_authoritative_evidence_missing")
        self.assertIn("cycle_1_waiting_review_not_verified", record.failure_reasons)
        self.assertIn("cycle_2_readback_influence_not_verified", record.failure_reasons)

    def test_complete_records_pass_without_reconstructing_missing_artifacts(self):
        with TemporaryDirectory() as state_dir:
            store = Package123CycleStore(state_dir)
            cycle1 = _cycle_record(1, "cycle1")
            cycle2 = _cycle_record(2, "cycle2", readback=True)
            store.append_cycle_record(cycle1)
            store.append_cycle_record(cycle2)
            store.append_source_profile(
                Package123ExperienceSourceProfile(
                    source_profile_id="package_123_source_profile:audit",
                    schema_version=SOURCE_PROFILE_SCHEMA_VERSION,
                    created_at=utc_now(),
                    experiment_id=EXPERIMENT_ID,
                    experiment_run_id="package_123_experiment_run:cycle2",
                    screen_lane="windows_window_capture",
                    audio_lane="system_audio_loopback",
                    host_state_lane="real_host_state",
                    camera_lane="not_participating_by_design",
                    screen_binding_id="window_binding:audit",
                    audio_source_descriptor_id="loopback_descriptor:audit",
                    real_live_capture=True,
                    prerecorded_fixture_used=False,
                    source_trace_refs=tuple(),
                )
            )
            influence = RealPerceptionReadbackInfluenceRecord(
                influence_record_id="package_123_readback_influence:audit",
                schema_version=READBACK_INFLUENCE_SCHEMA_VERSION,
                created_at=utc_now(),
                cycle_1_memory_application_data_id="memory_application_data:cycle1",
                cycle_2_candidate_id="candidate:cycle2",
                scorer_id="host_body_readback_internal_action_influence",
                scorer_version="v0",
                score_without_readback=10.0,
                score_with_readback=12.0,
                readback_contribution=2.0,
                influencing_readback_refs=("working_readback_commit:cycle1",),
                matching_evidence_refs=("working_readback_commit:cycle1",),
                actual_runtime_hot_path=True,
                hard_coded_experiment_match_used=False,
            )
            store.append_readback_influence(influence)
            store.append_two_cycle_comparison(
                Package123TwoCycleComparisonRecord(
                    comparison_id="package_123_comparison:audit",
                    schema_version=TWO_CYCLE_COMPARISON_SCHEMA_VERSION,
                    created_at=utc_now(),
                    experiment_id=EXPERIMENT_ID,
                    cycle_1_record_id=cycle1.cycle_record_id,
                    cycle_2_record_id=cycle2.cycle_record_id,
                    cycle_1_process_instance_id=cycle1.process_instance_id,
                    cycle_2_process_instance_id=cycle2.process_instance_id,
                    process_instances_different=True,
                    raw_artifacts_different=True,
                    runtime_sessions_different=True,
                    cycle_1_commit_present=True,
                    cycle_2_readback_loaded_before_event=True,
                    readback_influence_record_id=influence.influence_record_id,
                    readback_contribution_nonzero=True,
                    cycle_2_final_state="WAITING_TEACHER_REVIEW",
                    no_llm_runtime=True,
                    no_codex_runtime=True,
                    no_network_runtime=True,
                )
            )

            with patch("ashl_core_v1.runtime.package_123_growth_audit._real_artifacts", return_value=True), patch(
                "ashl_core_v1.runtime.package_123_growth_audit._teacher_decision_exists",
                return_value=True,
            ), patch(
                "ashl_core_v1.runtime.package_123_growth_audit._session_commit_exists",
                return_value=True,
            ):
                record = audit_package_123_real_perception_growth(state_dir)

        self.assertEqual(record.audit_status, "passed_no_codex_real_perception_two_cycle_growth_run")
        self.assertTrue(record.real_host_state_verified)
        self.assertFalse(record.prerecorded_fixture_used)
        self.assertFalse(record.camera_claimed)


def _cycle_record(cycle_index: int, suffix: str, *, readback: bool = False) -> Package123CycleRecord:
    return Package123CycleRecord(
        cycle_record_id=f"package_123_cycle_record:{suffix}",
        schema_version=CYCLE_RECORD_SCHEMA_VERSION,
        created_at=utc_now(),
        experiment_id=EXPERIMENT_ID,
        experiment_run_id=f"package_123_experiment_run:{suffix}",
        cycle_index=cycle_index,
        process_instance_id=f"package_123_process_instance:{suffix}",
        operating_system_process_id=cycle_index,
        preflight_id=f"package_123_preflight:{suffix}",
        source_profile_id=f"package_123_source_profile:{suffix}",
        stimulus_manifest_id=f"package_123_experiment_run:{suffix}",
        screen_artifact_refs=(f"sensor_raw_artifact:screen_{suffix}",),
        audio_artifact_refs=(f"sensor_raw_artifact:audio_{suffix}",),
        host_state_artifact_refs=(f"sensor_raw_artifact:host_{suffix}",),
        perception_readable_data_refs=(f"perception_readable_data:{suffix}",),
        perception_session_id=f"bounded_multimodal_perception_session:{suffix}",
        bounded_runtime_session_id=f"bounded_embodied_session:{suffix}",
        final_session_state="WAITING_TEACHER_REVIEW",
        pending_teacher_review_id=f"pending_teacher_review:{suffix}:1",
        readback_loaded_before_event=readback,
        readback_record_refs=("working_readback_commit:cycle1",) if readback else tuple(),
        source_trace_refs=(f"multimodal_trace:{suffix}",),
    )


if __name__ == "__main__":
    unittest.main()
