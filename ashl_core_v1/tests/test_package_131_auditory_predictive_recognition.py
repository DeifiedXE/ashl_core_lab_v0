from __future__ import annotations

import contextlib
import io
import json
import os
import sqlite3
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from ashl_core_v1.perception.audio_primitive_compiler import (
    AUDIO_PRIMITIVE_COMPILER_ID,
    AUDIO_PRIMITIVE_COMPILER_VERSION,
    RELATIVE_BANDS,
)
from ashl_core_v1.perception.audio_primitive_schema import (
    AUDIO_PRIMITIVE_SCHEMA_VERSION,
    AudioPrimitiveRecord,
)
from ashl_core_v1.runtime.auditory_concept_feature_projection import (
    build_auditory_concept_feature_projection,
    extract_source_blurred_auditory_feature_values,
)
from ashl_core_v1.runtime.auditory_concept_predictive_validation import (
    compare_low_level_auditory_features_to_template,
    compare_projection_to_template,
)
from ashl_core_v1.runtime.auditory_grounding_types import (
    BLUR_POLICY_VERSION,
    DELETION_AUDIT_SCHEMA_VERSION,
    GENERATION_SCHEMA_VERSION,
    MODEL_SCHEMA_VERSION,
    SOURCE_PROFILE_SCHEMA_VERSION,
    AuditoryConceptFeatureProjection,
    AuditoryGroundingEpisodeRecord,
    AuditoryGroundingRawAudioDeletionAudit,
    AuditorySourceConditionProfile,
    ExpectedAudioPrimitiveGenerationRecord,
    GroundedAuditoryEventConceptModel,
)
from ashl_core_v1.runtime.auditory_prediction_model_binding import (
    BLOCKED_MISSING_MODEL,
    load_package_130_prediction_evidence,
    verify_recognition_source_compatibility,
)
from ashl_core_v1.runtime.auditory_predictive_recognition import (
    build_auditory_prediction_comparison,
    build_auditory_recognition_feature_projection,
)
from ashl_core_v1.runtime.auditory_predictive_recognition_types import (
    BASELINE_COMMIT,
    CONSUMER_SCOPE,
    PACKAGE_130_PASS_STATUS,
    PASS_STATUS,
    AuditoryRecognitionObservationRecord,
    contains_forbidden_fixture_provenance,
)
from ashl_core_v1.runtime.expected_audio_primitive_generator import build_feature_template
from ashl_core_v1.runtime.host_sensor_types import canonical_json
from ashl_core_v1.runtime.operator_console_types import (
    PACKAGE_131_AUDITORY_PREDICTION_EVENT_KINDS,
)
from ashl_core_v1.runtime.package_131_auditory_predictive_recognition_audit import (
    audit_package_131_auditory_predictive_recognition,
)
from ashl_core_v1.runtime.package_131_auditory_predictive_recognition_cli import (
    build_parser,
    main as package_131_cli_main,
)
from ashl_core_v1.runtime.package_131_auditory_predictive_recognition_controls import (
    CONTROL_NAMES,
    _valid_binding,
    _valid_observation,
    run_package_131_negative_controls,
)
from ashl_core_v1.runtime.package_131_auditory_predictive_recognition_runtime import (
    create_pair_comparison,
    run_probe_worker_subprocess,
)
from ashl_core_v1.runtime.package_131_auditory_predictive_recognition_store import (
    PACKAGE_DIR,
    Package131AuditoryPredictiveRecognitionStore,
)
from ashl_core_v1.runtime.windows_wasapi_loopback_source import WindowsWasapiLoopbackSource


def _episode() -> AuditoryGroundingEpisodeRecord:
    return AuditoryGroundingEpisodeRecord(
        episode_id="episode:0",
        schema_version="ashl_auditory_grounding_episode_v0",
        created_at="2026-08-01T00:00:00+00:00",
        grounding_run_id="run:1",
        process_instance_id="process:1",
        operating_system_process_id=100,
        runtime_session_id="runtime:1",
        perception_session_id="perception:1",
        observation_window_id="window:1",
        audio_capture_session_id="audio:1",
        host_state_sampling_session_id="host:1",
        source_descriptor_id="source:1",
        source_condition_profile_id="profile:1",
        raw_audio_artifact_id="artifact:0",
        raw_audio_content_hash="a" * 64,
        raw_audio_byte_length=100,
        audio_primitive_refs=("primitive:0",),
        audio_temporal_span_refs=("span:1",),
        audio_interval_refs=tuple(),
        repeated_structure_refs=tuple(),
        capture_mode="grounding_capture",
        compiler_version=AUDIO_PRIMITIVE_COMPILER_VERSION,
        blur_policy_version=BLUR_POLICY_VERSION,
        transport_integrity_valid=True,
        semantic_label=None,
        speaker_identity=None,
        transcript=None,
        emotion_label=None,
        source_record_refs=("artifact:0", "primitive:0"),
        source_trace_refs=("trace:0",),
    )


def _observed_primitive(*, privacy: str = "grounding_conservative_v0") -> AudioPrimitiveRecord:
    envelope = tuple(
        0.8 if 8 <= index < 18 or 30 <= index < 42 or 55 <= index < 82 else 0.0
        for index in range(100)
    )
    return AudioPrimitiveRecord(
        audio_primitive_id="primitive:0",
        schema_version=AUDIO_PRIMITIVE_SCHEMA_VERSION,
        created_at="2026-08-01T00:00:00+00:00",
        primitive_role="observed",
        source_kind="microphone",
        source_buffer_id="buffer:0" if privacy == "recognition_ephemeral_v0" else None,
        source_artifact_id=None if privacy == "recognition_ephemeral_v0" else "artifact:0",
        source_concept_id=None,
        window_start_offset_ms=0,
        window_end_offset_ms=2000,
        amplitude_envelope=envelope,
        relative_band_energy=tuple(
            (name, 1.0 + index) for index, (name, _bounds) in enumerate(RELATIVE_BANDS)
        ),
        onset_events=({"offset_ms": 100}, {"offset_ms": 600}, {"offset_ms": 1100}),
        offset_events=({"offset_ms": 300}, {"offset_ms": 800}, {"offset_ms": 1500}),
        rhythm_interval_pattern=(500.0, 500.0),
        pause_intervals=((300, 600), (800, 1100)),
        relative_pitch_contour=(110.0, 220.0, 440.0),
        coarse_pitch_band="low",
        harmonicity_proxy=tuple(),
        noisiness_proxy=tuple(),
        duration_ms=2000,
        uncertainty=0.0,
        compiler_id=AUDIO_PRIMITIVE_COMPILER_ID,
        compiler_version=AUDIO_PRIMITIVE_COMPILER_VERSION,
        privacy_policy_id=privacy,
        semantic_label=None,
        speech_content=None,
        speaker_identity=None,
        emotion_label=None,
        source_trace_refs=("trace:0",),
    )


def _projection(index: int, *, contrast: bool = False) -> AuditoryConceptFeatureProjection:
    if contrast:
        envelope = tuple(0.9 if 5 <= cell < 26 else 0.0 for cell in range(32))
        count, durations, intervals, silence = 1, (1.0,), tuple(), 0.34
        spectral = (0.55, 0.20, 0.10, 0.08, 0.05, 0.02)
    else:
        delta = (index - 1.5) * 0.01
        envelope = tuple(
            round(max(0.0, min(1.0, value + (delta if value else 0.0))), 6)
            for value in (
                0.8 if 0 <= cell < 5 or 9 <= cell < 14 or 19 <= cell < 30 else 0.0
                for cell in range(32)
            )
        )
        count, durations, intervals, silence = 3, (0.24, 0.25, 0.51), (1.0, 0.96 + index * 0.01), 0.34 + index * 0.01
        spectral = (0.01, 0.02, 0.05, 0.82, 0.07, 0.03)
    return AuditoryConceptFeatureProjection(
        feature_projection_id=f"projection:{index}:{'c' if contrast else 'p'}",
        schema_version="ashl_auditory_concept_feature_projection_v0",
        created_at="2026-08-01T00:00:00+00:00",
        episode_id=f"episode:{index}",
        audio_primitive_refs=(f"primitive:{index}",),
        normalized_amplitude_envelope=envelope,
        onset_count=count,
        offset_count=count,
        active_region_count=count,
        normalized_region_duration_ratios=durations,
        normalized_inter_onset_interval_ratios=intervals,
        silence_ratio=silence,
        relative_spectral_band_energy=spectral,
        coarse_pitch_contour=None,
        absolute_pitch_identity_removed=True,
        fine_spectral_identity_removed=True,
        intelligible_content_removed=True,
        semantic_label=None,
        compiler_version=AUDIO_PRIMITIVE_COMPILER_VERSION,
        blur_policy_version=BLUR_POLICY_VERSION,
        source_record_refs=(f"episode:{index}",),
        source_trace_refs=tuple(),
    )


class Package131UnitTests(unittest.TestCase):
    def test_baseline_scope_and_event_surface(self) -> None:
        self.assertEqual(BASELINE_COMMIT, "1184f01983408e66c0f60eb225eacb34394f6072")
        self.assertEqual(CONSUMER_SCOPE, "package_131_auditory_prediction_only")
        self.assertEqual(PASS_STATUS, "passed_auditory_predictive_recognition_v0")
        self.assertEqual(len(PACKAGE_131_AUDITORY_PREDICTION_EVENT_KINDS), 11)
        self.assertNotIn("auditory_sound_named", PACKAGE_131_AUDITORY_PREDICTION_EVENT_KINDS)

    def test_shared_feature_extraction_preserves_package_130_golden(self) -> None:
        primitive = _observed_primitive()
        values = extract_source_blurred_auditory_feature_values(primitive)
        projection = build_auditory_concept_feature_projection(
            episode=_episode(), audio_primitive=primitive
        )
        self.assertEqual(
            projection.feature_projection_id,
            "auditory_concept_feature_projection:2d1b6fe39176b5d73df3de199f37e3a9f6e92e07ee295182fa86a1871b944bb7",
        )
        self.assertEqual(values["normalized_amplitude_envelope"], projection.normalized_amplitude_envelope)
        self.assertEqual(values["active_region_count"], 3)
        self.assertEqual(values["coarse_pitch_contour"], None)

    def test_shared_comparator_preserves_package_130_golden(self) -> None:
        positives = tuple(_projection(index) for index in range(4))
        centers, tolerances = build_feature_template(positives)
        record = compare_projection_to_template(
            projection=positives[0],
            centers=centers,
            tolerances=tolerances,
            evaluation_kind="golden",
        )
        self.assertEqual(
            record["prediction_error_record_id"],
            "auditory_prediction_error:9c332a04e787f2027a7c99ea5b94ffb94aa6fb3edff3f710ae1bcdec9a5a7a66",
        )
        self.assertFalse(record["runtime_recognition_performed"])

    def test_shared_comparator_supports_and_rejects_by_all_tolerances(self) -> None:
        positives = tuple(_projection(index) for index in range(4))
        centers, tolerances = build_feature_template(positives)
        supported_values = {name: centers[name] for name in centers}
        _errors, checks, inside = compare_low_level_auditory_features_to_template(
            observed_feature_values=supported_values,
            centers=centers,
            tolerances=tolerances,
        )
        self.assertTrue(inside)
        self.assertTrue(all(checks.values()))
        rejected_values = dict(supported_values)
        rejected_values["active_region_count"] = int(centers["active_region_count"]) + 1
        _errors, checks, inside = compare_low_level_auditory_features_to_template(
            observed_feature_values=rejected_values,
            centers=centers,
            tolerances=tolerances,
        )
        self.assertFalse(inside)
        self.assertFalse(checks["active_region_count"])

    def test_recognition_projection_reuses_shared_domain_and_rejects_semantics(self) -> None:
        observation = replace(
            _valid_observation(),
            source_buffer_id="buffer:0",
            observed_audio_primitive_ref="primitive:0",
        )
        projection = build_auditory_recognition_feature_projection(
            observation=observation,
            audio_primitive=_observed_primitive(privacy="recognition_ephemeral_v0"),
        )
        self.assertIsNone(projection.semantic_label)
        self.assertTrue(projection.absolute_pitch_identity_removed)
        with self.assertRaises(ValueError):
            replace(projection, semantic_label="tone")
        with self.assertRaisesRegex(ValueError, "microphone"):
            build_auditory_recognition_feature_projection(
                observation=observation,
                audio_primitive=replace(
                    _observed_primitive(privacy="recognition_ephemeral_v0"),
                    source_kind="file",
                ),
            )

    def test_prediction_result_cannot_be_selected_by_probe_slot(self) -> None:
        observation = replace(
            _valid_observation(),
            source_buffer_id="buffer:0",
            observed_audio_primitive_ref="primitive:0",
        )
        projection = build_auditory_recognition_feature_projection(
            observation=observation,
            audio_primitive=_observed_primitive(privacy="recognition_ephemeral_v0"),
        )
        values = {
            name: getattr(projection, name)
            for name in (
                "normalized_amplitude_envelope",
                "onset_count",
                "offset_count",
                "active_region_count",
                "normalized_region_duration_ratios",
                "normalized_inter_onset_interval_ratios",
                "silence_ratio",
                "relative_spectral_band_energy",
                "coarse_pitch_contour",
            )
        }
        comparison = build_auditory_prediction_comparison(
            probe_id="fixture_role_must_not_select",
            observation=observation,
            projection=projection,
            binding=_valid_binding(),
            feature_centers=values,
            feature_tolerances={
                key: (None if value is None else tuple(0.0 for _ in value) if isinstance(value, tuple) else 0.0)
                for key, value in values.items()
            },
        )
        self.assertTrue(comparison.inside_all_structural_tolerances)
        self.assertEqual(
            comparison.prediction_result,
            "supported_by_reviewed_anonymous_auditory_concept",
        )
        with self.assertRaises(ValueError):
            replace(
                comparison,
                prediction_result="not_supported_by_reviewed_anonymous_auditory_concept",
            )

    def test_model_load_must_precede_capture_and_stimulus(self) -> None:
        with self.assertRaises(ValueError):
            replace(
                _valid_observation(),
                model_loaded_monotonic_ns=500,
                capture_started_monotonic_ns=200,
                model_loaded_before_capture=False,
            )

    def test_fixture_firewall_is_recursive(self) -> None:
        self.assertTrue(
            contains_forbidden_fixture_provenance(
                {"nested": [{"scheduled_frequency_hz": 860}]}
            )
        )
        self.assertFalse(
            contains_forbidden_fixture_provenance(
                {"per_feature_errors": {"active_region_count": 0.0}}
            )
        )

    def test_all_46_negative_controls_execute_real_rejections(self) -> None:
        result = run_package_131_negative_controls(append=False)
        self.assertEqual(tuple(result.controls), CONTROL_NAMES)
        self.assertEqual(result.passed_count, 46)
        self.assertTrue(result.controls_passed)

    def test_append_only_store_is_external_and_rejects_duplicate(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            store = Package131AuditoryPredictiveRecognitionStore(temp)
            binding = _valid_binding()
            store.append_record("auditory_prediction_consumer_bindings", binding)
            with self.assertRaises(ValueError):
                store.append_record("auditory_prediction_consumer_bindings", binding)
            self.assertIn(PACKAGE_DIR, str(store.database_path))
            self.assertEqual(store.forbidden_mutation_operations(), ("update", "delete"))
            self.assertTrue(store.audit_append_only_store()["valid"])

    def test_cli_surface_and_capture_authorization_gate(self) -> None:
        parser = build_parser()
        for command in (
            "preflight",
            "show-model",
            "run-probe-a",
            "run-probe-b",
            "show-predictions",
            "show-comparison",
            "audit",
            "guided-run",
        ):
            with self.subTest(command=command):
                args = parser.parse_args([command, "--state-dir", "state"])
                self.assertEqual(args.command, command)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = package_131_cli_main(["run-probe-a", "--state-dir", "missing"])
        self.assertEqual(code, 2)
        self.assertIn("blocked_recognition_capture_authorization_missing", output.getvalue())

    def test_package_131_runtime_has_no_learning_action_output_or_network_binding(self) -> None:
        runtime = Path(
            "ashl_core_v1/runtime/package_131_auditory_predictive_recognition_runtime.py"
        ).read_text(encoding="utf-8")
        for forbidden in (
            "host_body_existing_learning_pipeline_compatibility",
            "host_body_learning_feedback_bridge",
            "session_learning_evidence_adapter",
            "teacher_gated_session_resume_commit",
            "from ashl_core_v1.runtime.package_112",
            "requests.",
            "ACTION_BID",
            "import working_readback",
        ):
            self.assertNotIn(forbidden, runtime)

    def test_missing_package_130_state_blocks_without_synthetic_approval(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(RuntimeError, BLOCKED_MISSING_MODEL):
                load_package_130_prediction_evidence(state_dir=temp)

    def test_test_only_ready_model_can_be_loaded_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            state = Path(temp)
            _write_test_only_package_130_state(state)
            evidence = load_package_130_prediction_evidence(state_dir=state)
            self.assertEqual(evidence.audit["audit_status"], PACKAGE_130_PASS_STATUS)
            self.assertEqual(evidence.memory_commit["consumer_scope"], CONSUMER_SCOPE)
            self.assertFalse(evidence.model.raw_audio_dependency_active)
            database = state / "package_130_grounded_auditory_concept_v0" / "package_130.sqlite3"
            before = database.read_bytes()
            load_package_130_prediction_evidence(state_dir=state)
            self.assertEqual(before, database.read_bytes())


@unittest.skipUnless(os.name == "nt", "real Package 131 integration requires Windows")
class Package131RealIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        value = os.environ.get("ASHL_PACKAGE_130_STATE_DIR")
        if not value:
            raise unittest.SkipTest("ASHL_PACKAGE_130_STATE_DIR is not configured")
        cls.state = Path(value)

    def test_real_two_probe_prediction_and_final_audit(self) -> None:
        probe_a = run_probe_worker_subprocess(state_dir=self.state, probe_slot="A")
        probe_b = run_probe_worker_subprocess(state_dir=self.state, probe_slot="B")
        self.assertNotEqual(
            probe_a["operating_system_process_id"], probe_b["operating_system_process_id"]
        )
        self.assertEqual(
            probe_a["prediction_result"],
            "supported_by_reviewed_anonymous_auditory_concept",
        )
        self.assertEqual(
            probe_b["prediction_result"],
            "not_supported_by_reviewed_anonymous_auditory_concept",
        )
        pair = create_pair_comparison(state_dir=self.state)
        self.assertEqual(
            pair.comparison_status,
            "passed_real_two_probe_anonymous_auditory_prediction",
        )
        run_package_131_negative_controls(state_dir=self.state, append=True)
        audit = audit_package_131_auditory_predictive_recognition(state_dir=self.state)
        self.assertEqual(audit.audit_status, PASS_STATUS)
        self.assertEqual(audit.raw_audio_artifact_delta, 0)
        self.assertEqual(audit.probe_a_ring_bytes_after_clear, 0)
        self.assertEqual(audit.probe_b_ring_bytes_after_clear, 0)


def _write_test_only_package_130_state(state: Path) -> None:
    model_id = "auditory_event_concept:" + "a" * 64
    expected_id = "audio_primitive:expected:" + "b" * 64
    profile_id = "auditory_source_condition_profile:test_only"
    deletion_id = "auditory_grounding_deletion_audit:test_only"
    reviewed_id = "reviewed:test_only"
    validation_id = "validation:test_only"
    generation_id = "generation:test_only"
    episode_ids = tuple(f"episode:{index}" for index in range(7))
    artifact_ids = tuple(f"artifact:{index}" for index in range(7))
    hashes = tuple(f"{index:064x}" for index in range(7))
    deletion_record_ids = tuple(f"deletion-record:{index}" for index in range(7))
    package_db = state / "package_130_grounded_auditory_concept_v0" / "package_130.sqlite3"
    primitive_db = state / "perception_primitives_v0" / "perception_primitives.sqlite3"
    sensor_db = state / "host_sensor_artifacts_v0" / "sensor_artifacts.sqlite3"
    profile = AuditorySourceConditionProfile(
        source_condition_profile_id=profile_id,
        schema_version=SOURCE_PROFILE_SCHEMA_VERSION,
        created_at="2026-08-01T00:00:00+00:00",
        source_kind="windows_wasapi_loopback",
        endpoint_descriptor_hash="c" * 64,
        audio_capture_config_hash="d" * 64,
        compiler_version=AUDIO_PRIMITIVE_COMPILER_VERSION,
        blur_policy_version=BLUR_POLICY_VERSION,
        sample_rate_hz=48000,
        channel_count=2,
        canonical_channel_mapping="stereo_mean_to_mono_low_level_features",
        environment_scope="single_verified_host_internal_audio_path_v0",
        cross_device_generalization_claimed=False,
        cross_room_generalization_claimed=False,
        speaker_identity_scope=False,
        source_record_refs=("descriptor:test_only",),
        source_trace_refs=tuple(),
    )
    model_common = dict(
        auditory_concept_model_id=model_id,
        schema_version=MODEL_SCHEMA_VERSION,
        created_at="2026-08-01T00:00:00+00:00",
        reviewed_concept_id=reviewed_id,
        concept_code=model_id,
        semantic_label=None,
        natural_language_name=None,
        source_condition_profile_id=profile_id,
        positive_episode_refs=episode_ids[:4],
        contrast_episode_refs=episode_ids[4:],
        positive_feature_projection_refs=tuple(f"projection:{index}" for index in range(4)),
        contrast_feature_projection_refs=tuple(f"projection:{index}" for index in range(4, 7)),
        expected_audio_primitive_refs=(expected_id,),
        predictive_validation_id=validation_id,
        compiler_version=AUDIO_PRIMITIVE_COMPILER_VERSION,
        blur_policy_version=BLUR_POLICY_VERSION,
        source_scope="single_verified_wasapi_endpoint_and_capture_stack_v0",
        generalization_scope="same_source_condition_only_v0",
        recognition_enabled=False,
        prediction_error_runtime_enabled=False,
        automatic_regrounding_enabled=False,
        package_112_action_influence_allowed=False,
        source_record_refs=episode_ids + (expected_id, validation_id),
        source_trace_refs=tuple(),
    )
    waiting = GroundedAuditoryEventConceptModel(
        model_record_id=model_id + ":reviewed_waiting_raw_audio_cleanup",
        maturity_status="reviewed_waiting_raw_audio_cleanup",
        raw_audio_dependency_active=True,
        raw_audio_deletion_audit_id=None,
        package_131_consumer_allowed=False,
        **model_common,
    )
    ready = GroundedAuditoryEventConceptModel(
        model_record_id=model_id + ":reviewed_grounded_ready_for_package_131",
        maturity_status="reviewed_grounded_ready_for_package_131",
        raw_audio_dependency_active=False,
        raw_audio_deletion_audit_id=deletion_id,
        package_131_consumer_allowed=True,
        **model_common,
    )
    centers = {
        "normalized_amplitude_envelope": (1.0,),
        "onset_count": 1,
        "offset_count": 1,
        "active_region_count": 1,
        "normalized_region_duration_ratios": (1.0,),
        "normalized_inter_onset_interval_ratios": tuple(),
        "silence_ratio": 0.5,
        "relative_spectral_band_energy": (1.0,),
        "coarse_pitch_contour": None,
    }
    tolerances = {
        key: (None if value is None else tuple(0.0 for _ in value) if isinstance(value, tuple) else 0.0)
        for key, value in centers.items()
    }
    generation = ExpectedAudioPrimitiveGenerationRecord(
        generation_id=generation_id,
        schema_version=GENERATION_SCHEMA_VERSION,
        created_at="2026-08-01T00:00:00+00:00",
        concept_candidate_id="candidate:test_only",
        source_positive_projection_refs=tuple(f"projection:{index}" for index in range(4)),
        expected_audio_primitive_refs=(expected_id,),
        aggregation_method="deterministic_coordinate_median",
        tolerance_method="maximum_positive_deviation_plus_fixed_margin_v0",
        observed_expected_schema_equal=True,
        deterministic_generation=True,
        stimulus_ground_truth_used=False,
        teacher_feature_values_used=False,
        feature_centers=centers,
        feature_tolerances=tolerances,
        source_record_refs=tuple(f"projection:{index}" for index in range(4)),
        source_trace_refs=tuple(),
    )
    deletion = AuditoryGroundingRawAudioDeletionAudit(
        deletion_audit_id=deletion_id,
        schema_version=DELETION_AUDIT_SCHEMA_VERSION,
        created_at="2026-08-01T00:00:00+00:00",
        auditory_concept_model_id=model_id,
        grounding_episode_refs=episode_ids,
        raw_artifact_refs=artifact_ids,
        deletion_record_refs=deletion_record_ids,
        expected_raw_artifact_count=7,
        successful_deletion_count=7,
        failed_deletion_count=0,
        raw_blob_count_after_deletion=0,
        recoverable_waveform_detected=False,
        audio_primitive_records_preserved=True,
        contrast_records_preserved=True,
        source_trace_refs_preserved=True,
        model_activation_allowed=True,
        failure_reasons=tuple(),
    )
    expected = AudioPrimitiveRecord(
        audio_primitive_id=expected_id,
        schema_version=AUDIO_PRIMITIVE_SCHEMA_VERSION,
        created_at="2026-08-01T00:00:00+00:00",
        primitive_role="expected",
        source_kind="microphone",
        source_buffer_id=None,
        source_artifact_id=None,
        source_concept_id="candidate:test_only",
        window_start_offset_ms=0,
        window_end_offset_ms=1000,
        amplitude_envelope=(1.0,),
        relative_band_energy=(("rank_0", 1.0),),
        onset_events=({"offset_ms": 100},),
        offset_events=({"offset_ms": 200},),
        rhythm_interval_pattern=tuple(),
        pause_intervals=tuple(),
        relative_pitch_contour=tuple(),
        coarse_pitch_band="removed",
        harmonicity_proxy=tuple(),
        noisiness_proxy=tuple(),
        duration_ms=1000,
        uncertainty=0.0,
        compiler_id=AUDIO_PRIMITIVE_COMPILER_ID,
        compiler_version=AUDIO_PRIMITIVE_COMPILER_VERSION,
        privacy_policy_id="grounding_conservative_v0",
        semantic_label=None,
        speech_content=None,
        speaker_identity=None,
        emotion_label=None,
        source_trace_refs=tuple(),
    )
    package_rows = {
        "package_130_audits": ({"audit_id": "audit:test_only", "audit_status": PACKAGE_130_PASS_STATUS},),
        "grounded_auditory_event_concept_models": (waiting.to_dict(), ready.to_dict()),
        "expected_audio_primitive_generation_records": (generation.to_dict(),),
        "auditory_concept_predictive_validations": ({"predictive_validation_id": validation_id, "predictive_validation_passed": True},),
        "auditory_grounding_raw_audio_deletion_audits": (deletion.to_dict(),),
        "auditory_source_condition_profiles": (profile.to_dict(),),
        "auditory_concept_memory_commit_records": ({
            "memory_commit_record_id": "memory:test_only",
            "consumer_scope": CONSUMER_SCOPE,
            "active_package_112_working_readback_created": False,
            "memory_application_data": {"memory_application_data_id": "application:test_only", "read_scope": CONSUMER_SCOPE},
            "reviewed_concept": {"feedback_derived_reviewed_concept_id": reviewed_id},
            "source_record_refs": (model_id,),
        },),
        "auditory_grounding_episodes": tuple(
            {"episode_id": episode_id, "raw_audio_artifact_id": artifact_id, "raw_audio_content_hash": content_hash}
            for episode_id, artifact_id, content_hash in zip(episode_ids, artifact_ids, hashes)
        ),
    }
    sensor_rows = {
        "sensor_raw_artifacts": tuple(
            {"artifact_id": artifact_id, "content_sha256": content_hash, "blob_relative_path": f"blobs/sha256/{content_hash}.bin", "storage_format": "PCM_S16LE"}
            for artifact_id, content_hash in zip(artifact_ids, hashes)
        ),
        "artifact_deletion_records": tuple(
            {"deletion_record_id": record_id, "artifact_id": artifact_id, "content_sha256_before_deletion": content_hash, "deletion_verified": True}
            for record_id, artifact_id, content_hash in zip(deletion_record_ids, artifact_ids, hashes)
        ),
    }
    _write_json_database(package_db, package_rows)
    _write_json_database(primitive_db, {"audio_primitives": (expected.to_dict(),)})
    _write_json_database(sensor_db, sensor_rows)


def _write_json_database(path: Path, tables: dict[str, tuple[dict[str, object], ...]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    try:
        for table, rows in tables.items():
            connection.execute(
                f"CREATE TABLE {table} (record_id TEXT PRIMARY KEY, payload_json TEXT NOT NULL)"
            )
            for index, payload in enumerate(rows):
                connection.execute(
                    f"INSERT INTO {table} (record_id, payload_json) VALUES (?, ?)",
                    (f"{table}:{index}", canonical_json(payload)),
                )
        connection.commit()
    finally:
        connection.close()


if __name__ == "__main__":
    unittest.main()
