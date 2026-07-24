import unittest
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

from ashl_core_v1.runtime.package_123_cycle_runtime import review_cycle_one
from ashl_core_v1.runtime.package_123_cycle_store import Package123CycleStore
from ashl_core_v1.runtime.package_123_types import CYCLE_RECORD_SCHEMA_VERSION, EXPERIMENT_ID, Package123CycleRecord, utc_now
from ashl_core_v1.runtime.session_learning_evidence_identity import FULL_COMMIT_APPROVAL_SCOPE


class Package123TeacherCommitTests(unittest.TestCase):
    def test_approval_requires_explicit_text(self):
        with TemporaryDirectory() as state_dir:
            Package123CycleStore(state_dir).append_cycle_record(_cycle_record())
            with patch("ashl_core_v1.runtime.package_123_cycle_runtime.TeacherGatedSessionStore") as store_cls:
                store_cls.return_value.get_pending_review.return_value = SimpleNamespace(evidence_identity_sha256="evidence_hash:1")
                with self.assertRaises(ValueError):
                    review_cycle_one(
                        state_dir=state_dir,
                        decision="approve",
                        reviewer="local_teacher",
                        approval_text=None,
                        confirm=True,
                    )

    def test_approval_uses_existing_scope_and_exact_evidence_hash(self):
        with TemporaryDirectory() as state_dir:
            Package123CycleStore(state_dir).append_cycle_record(_cycle_record())
            decision_record = SimpleNamespace(teacher_decision_id="teacher_decision:1", to_dict=lambda: {"teacher_decision_id": "teacher_decision:1"})
            commit_result = SimpleNamespace(final_status="COMMITTED", to_dict=lambda: {"final_status": "COMMITTED"})
            with patch("ashl_core_v1.runtime.package_123_cycle_runtime.TeacherGatedSessionStore") as store_cls, patch(
                "ashl_core_v1.runtime.package_123_cycle_runtime.TeacherGatedSessionResumeCommitRuntime"
            ) as runtime_cls:
                store_cls.return_value.get_pending_review.return_value = SimpleNamespace(evidence_identity_sha256="evidence_hash:1")
                runtime_cls.return_value.apply_teacher_decision.return_value = decision_record
                runtime_cls.return_value.resume_after_approval.return_value = commit_result

                payload = review_cycle_one(
                    state_dir=state_dir,
                    decision="approve",
                    reviewer="local_teacher",
                    approval_text="I approve this exact low-level observed multimodal pattern only.",
                    confirm=True,
                )

            self.assertEqual(payload["status"], "cycle_1_committed")
            args, kwargs = runtime_cls.return_value.apply_teacher_decision.call_args
            teacher_note = args[4]
            self.assertIn("exact low-level observed multimodal pattern", teacher_note)
            self.assertEqual(kwargs["approval_scope"], FULL_COMMIT_APPROVAL_SCOPE)
            self.assertEqual(kwargs["expected_evidence_hash"], "evidence_hash:1")


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
        screen_artifact_refs=("sensor_raw_artifact:screen",),
        audio_artifact_refs=("sensor_raw_artifact:audio",),
        host_state_artifact_refs=("sensor_raw_artifact:host",),
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
