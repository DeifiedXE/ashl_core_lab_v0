from __future__ import annotations

import contextlib
import io
import os
import shutil
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from ashl_core_v1.migration_audit import D_LAPLACE_QM0_AUDIT_STATUS
from ashl_core_v1.perception.audio_primitive_compiler import (
    AUDIO_PRIMITIVE_COMPILER_ID,
    AUDIO_PRIMITIVE_COMPILER_VERSION,
    RELATIVE_BANDS,
)
from ashl_core_v1.perception.audio_primitive_schema import (
    AUDIO_PRIMITIVE_SCHEMA_VERSION,
    AudioPrimitiveRecord,
)
from ashl_core_v1.runtime.active_perception_growth_types import (
    PASS_STATUS as PACKAGE_129_PASS_STATUS,
)
from ashl_core_v1.runtime.auditory_concept_feature_projection import (
    _aggregate_active_region_shape,
    build_auditory_concept_feature_projection,
)
from ashl_core_v1.runtime.auditory_concept_predictive_validation import (
    validate_grounding_corpus_prediction,
)
from ashl_core_v1.runtime.auditory_grounding_types import (
    ASSIGNMENT_SCHEMA_VERSION,
    AUTHORIZATION_SCHEMA_VERSION,
    BLUR_POLICY_VERSION,
    CAPTURE_MODE,
    CONSUMER_SCOPE,
    ENVIRONMENT_SCOPE,
    EPISODE_SCHEMA_VERSION,
    MAXIMUM_EPISODE_COUNT,
    MAXIMUM_EPISODE_DURATION_NS,
    PASS_STATUS,
    PROJECTION_SCHEMA_VERSION,
    SOURCE_PROFILE_SCHEMA_VERSION,
    SOURCE_SCOPE,
    AuditoryConceptFeatureProjection,
    AuditoryGroundingCaptureAuthorization,
    AuditoryGroundingEpisodeRecord,
    AuditoryGroundingExampleAssignment,
    AuditorySourceConditionProfile,
    GroundedAuditoryEventConceptCandidate,
)
from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import (
    ContentAddressedSensorArtifactStore,
)
from ashl_core_v1.runtime.expected_audio_primitive_generator import (
    concept_candidate_identity,
    generate_expected_audio_primitive,
)
from ashl_core_v1.runtime.grounded_auditory_concept_model import (
    activate_model_after_deletion,
    assess_auditory_concept_maturity,
    build_grounded_auditory_concept_model,
    deterministic_auditory_concept_model_id,
)
from ashl_core_v1.runtime.operator_console_types import (
    PACKAGE_130_AUDITORY_CONCEPT_EVENT_KINDS,
)
from ashl_core_v1.runtime.package_130_auditory_concept_audit import (
    audit_package_130_grounded_auditory_concept,
)
from ashl_core_v1.runtime.package_130_auditory_concept_cli import (
    _run_grounding_worker,
    build_parser,
    main as package_130_cli_main,
)
from ashl_core_v1.runtime.package_130_auditory_concept_runtime import (
    TEACHER_APPROVAL_TEXT,
    assign_grounding_examples,
    build_concept_candidate,
    delete_grounding_audio,
    reject_automatic_concept_discovery,
    reject_runtime_recognition_attempt,
    review_concept,
    validate_anonymous_concept_code,
    validate_expected_primitive_provenance,
)
from ashl_core_v1.runtime.package_130_auditory_concept_store import (
    Package130AuditoryConceptStore,
)
from ashl_core_v1.runtime.teacher_gated_session_store import (
    TeacherGatedSessionStore,
)
from ashl_core_v1.runtime.windows_wasapi_loopback_source import (
    WindowsWasapiLoopbackSource,
)


def _episode(index: int, *, one_process: bool = False) -> AuditoryGroundingEpisodeRecord:
    run_index = 1 if one_process or index < 4 else 2
    process_index = 1 if one_process or index < 4 else 2
    return AuditoryGroundingEpisodeRecord(
        episode_id=f"episode:{index}",
        schema_version=EPISODE_SCHEMA_VERSION,
        created_at="2026-08-01T00:00:00+00:00",
        grounding_run_id=f"run:{run_index}",
        process_instance_id=f"process:{process_index}",
        operating_system_process_id=1000 + process_index,
        runtime_session_id=f"runtime:{index}",
        perception_session_id=f"perception:{index}",
        observation_window_id=f"window:{index}",
        audio_capture_session_id=f"audio-session:{index}",
        host_state_sampling_session_id=f"host-session:{index}",
        source_descriptor_id="source:one",
        source_condition_profile_id="profile:one",
        raw_audio_artifact_id=f"artifact:{index}",
        raw_audio_content_hash=f"{'a' if index < 4 else 'b'}{index:063d}",
        raw_audio_byte_length=384000,
        audio_primitive_refs=(f"primitive:{index}",),
        audio_temporal_span_refs=(f"span:{index}",),
        audio_interval_refs=(f"interval:{index}",),
        repeated_structure_refs=(f"repeat:{index}",),
        capture_mode=CAPTURE_MODE,
        compiler_version=AUDIO_PRIMITIVE_COMPILER_VERSION,
        blur_policy_version=BLUR_POLICY_VERSION,
        transport_integrity_valid=True,
        semantic_label=None,
        speaker_identity=None,
        transcript=None,
        emotion_label=None,
        source_record_refs=(f"artifact:{index}", f"primitive:{index}"),
        source_trace_refs=(f"trace:{index}",),
    )


def _projection(index: int, *, contrast: bool = False) -> AuditoryConceptFeatureProjection:
    if contrast:
        envelope = tuple(0.9 if 5 <= cell < 26 else 0.0 for cell in range(32))
        onset_count = offset_count = active_count = 1
        durations = (1.0,)
        intervals = tuple()
        silence = 0.34
        spectral = (0.55, 0.20, 0.10, 0.08, 0.05, 0.02)
    else:
        base = (
            0.8 if 0 <= cell < 5 or 9 <= cell < 14 or 19 <= cell < 30 else 0.0
            for cell in range(32)
        )
        delta = (index - 1.5) * 0.01
        envelope = tuple(round(max(0.0, min(1.0, value + (delta if value else 0.0))), 6) for value in base)
        onset_count = offset_count = active_count = 3
        durations = (0.24, 0.25, 0.51)
        intervals = (1.0, 0.96 + index * 0.01)
        silence = 0.34 + index * 0.01
        spectral = (0.01, 0.02, 0.05, 0.82, 0.07, 0.03)
    return AuditoryConceptFeatureProjection(
        feature_projection_id=f"projection:{index}:{'c' if contrast else 'p'}",
        schema_version=PROJECTION_SCHEMA_VERSION,
        created_at="2026-08-01T00:00:00+00:00",
        episode_id=f"episode:{index if not contrast else index + 4}",
        audio_primitive_refs=(f"primitive:{index}",),
        normalized_amplitude_envelope=envelope,
        onset_count=onset_count,
        offset_count=offset_count,
        active_region_count=active_count,
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
        source_trace_refs=(f"trace:{index}",),
    )


def _observed_primitive() -> AudioPrimitiveRecord:
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
        source_buffer_id=None,
        source_artifact_id="artifact:0",
        source_concept_id=None,
        window_start_offset_ms=0,
        window_end_offset_ms=2000,
        amplitude_envelope=envelope,
        relative_band_energy=tuple((name, 1.0 + index) for index, (name, _bounds) in enumerate(RELATIVE_BANDS)),
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
        privacy_policy_id="grounding_conservative_v0",
        semantic_label=None,
        speech_content=None,
        speaker_identity=None,
        emotion_label=None,
        source_trace_refs=("trace:0",),
    )


class Package130UnitTests(unittest.TestCase):
    def test_baseline_and_locked_boundaries_are_preserved(self) -> None:
        self.assertEqual(
            PACKAGE_129_PASS_STATUS,
            "passed_active_perception_real_two_cycle_growth_run_v0",
        )
        self.assertEqual(
            D_LAPLACE_QM0_AUDIT_STATUS,
            "passed_d_laplace_qm0_read_only_migration_audit_v0",
        )
        self.assertEqual(CONSUMER_SCOPE, "package_131_auditory_prediction_only")
        self.assertIn(
            "auditory_concept_model_ready_for_package_131",
            PACKAGE_130_AUDITORY_CONCEPT_EVENT_KINDS,
        )
        self.assertNotIn(
            "auditory_event_recognized",
            PACKAGE_130_AUDITORY_CONCEPT_EVENT_KINDS,
        )

    def test_authorization_and_source_profile_are_bounded(self) -> None:
        authorization = AuditoryGroundingCaptureAuthorization(
            authorization_id="authorization:1",
            schema_version=AUTHORIZATION_SCHEMA_VERSION,
            created_at="2026-08-01T00:00:00+00:00",
            authorized_by="local_operator",
            authorization_source="explicit_grounding_session_configuration",
            source_scope=SOURCE_SCOPE,
            selected_audio_endpoint_id="default",
            maximum_episode_count=MAXIMUM_EPISODE_COUNT,
            maximum_episode_duration_ns=MAXIMUM_EPISODE_DURATION_NS,
            maximum_total_raw_bytes=1_000_000,
            grounding_capture_allowed=True,
            permanent_raw_audio_retention_allowed=False,
            service_period_expires_at="2026-08-01T02:00:00+00:00",
            deletion_required_after_final_decision=True,
            deletion_required_before_model_activation=True,
            source_trace_refs=("trace:1",),
        )
        self.assertFalse(authorization.permanent_raw_audio_retention_allowed)
        with self.assertRaises(ValueError):
            replace(authorization, permanent_raw_audio_retention_allowed=True)
        profile = AuditorySourceConditionProfile(
            source_condition_profile_id="profile:1",
            schema_version=SOURCE_PROFILE_SCHEMA_VERSION,
            created_at="2026-08-01T00:00:00+00:00",
            source_kind="windows_wasapi_loopback",
            endpoint_descriptor_hash="endpoint-hash",
            audio_capture_config_hash="config-hash",
            compiler_version=AUDIO_PRIMITIVE_COMPILER_VERSION,
            blur_policy_version=BLUR_POLICY_VERSION,
            sample_rate_hz=48000,
            channel_count=2,
            canonical_channel_mapping="stereo_mean_to_mono_low_level_features",
            environment_scope=ENVIRONMENT_SCOPE,
            cross_device_generalization_claimed=False,
            cross_room_generalization_claimed=False,
            speaker_identity_scope=False,
            source_record_refs=("source:1",),
            source_trace_refs=("trace:1",),
        )
        with self.assertRaises(ValueError):
            replace(profile, cross_device_generalization_claimed=True)

    def test_episode_and_assignment_reject_semantics_and_reuse(self) -> None:
        episode = _episode(0)
        self.assertIsNone(episode.semantic_label)
        with self.assertRaises(ValueError):
            replace(episode, transcript="speech")
        assignment = AuditoryGroundingExampleAssignment(
            assignment_id="assignment:1",
            schema_version=ASSIGNMENT_SCHEMA_VERSION,
            created_at="2026-08-01T00:00:00+00:00",
            assigned_by="local_teacher",
            assignment_source="explicit_grounding_example_assignment",
            positive_episode_refs=("episode:0",),
            contrast_episode_refs=("episode:4",),
            natural_language_label_assigned=False,
            semantic_meaning_assigned=False,
            feature_values_supplied_by_teacher=False,
            expected_primitive_supplied_by_teacher=False,
            assignment_status="control",
            source_record_refs=("episode:0", "episode:4"),
            source_trace_refs=("trace:0",),
        )
        with self.assertRaises(ValueError):
            replace(assignment, contrast_episode_refs=("episode:0",))
        with self.assertRaises(ValueError):
            replace(assignment, natural_language_label_assigned=True)

    def test_projection_is_deterministic_event_aligned_and_source_blurred(self) -> None:
        episode = _episode(0)
        primitive = _observed_primitive()
        first = build_auditory_concept_feature_projection(
            episode=episode,
            audio_primitive=primitive,
        )
        second = build_auditory_concept_feature_projection(
            episode=episode,
            audio_primitive=primitive,
        )
        self.assertEqual(first.feature_projection_id, second.feature_projection_id)
        self.assertEqual(len(first.normalized_amplitude_envelope), 32)
        self.assertIsNone(first.coarse_pitch_contour)
        self.assertTrue(first.absolute_pitch_identity_removed)
        self.assertTrue(first.fine_spectral_identity_removed)
        self.assertTrue(first.intelligible_content_removed)
        self.assertNotIn("110", str(first.to_dict()))

    def test_projection_trims_detector_boundary_bins_before_resampling(self) -> None:
        shape = _aggregate_active_region_shape(
            (0.21, 1.0, 1.0, 1.0, 0.24),
            ((0, 5),),
        )
        self.assertEqual(shape, (1.0,) * 32)

    def test_expected_primitive_is_deterministic_and_schema_shared(self) -> None:
        positives = tuple(_projection(index) for index in range(4))
        first, generation = generate_expected_audio_primitive(
            concept_candidate_id="candidate:one",
            positive_projections=positives,
        )
        second, _ = generate_expected_audio_primitive(
            concept_candidate_id="candidate:one",
            positive_projections=positives,
        )
        self.assertEqual(first.audio_primitive_id, second.audio_primitive_id)
        self.assertEqual(first.schema_version, _observed_primitive().schema_version)
        self.assertEqual(first.primitive_role, "expected")
        self.assertTrue(generation.deterministic_generation)
        self.assertFalse(generation.stimulus_ground_truth_used)
        self.assertFalse(generation.teacher_feature_values_used)
        serialized = str(generation.to_dict()).lower()
        self.assertNotIn("fixture", serialized)
        self.assertNotIn("process_instance", serialized)

    def test_candidate_identity_excludes_process_and_experiment(self) -> None:
        common = dict(
            source_condition_profile_id="profile:1",
            positive_episode_content_identities=("p1", "p2", "p3", "p4"),
            contrast_episode_content_identities=("c1", "c2", "c3"),
            positive_projection_refs=("pp1", "pp2", "pp3", "pp4"),
            contrast_projection_refs=("cp1", "cp2", "cp3"),
            compiler_version=AUDIO_PRIMITIVE_COMPILER_VERSION,
            blur_policy_version=BLUR_POLICY_VERSION,
        )
        first = concept_candidate_identity(**common)
        second = concept_candidate_identity(**common)
        self.assertEqual(first, second)
        self.assertNotIn("host_internal", first)

    def test_leave_one_out_accepts_positives_and_distinguishes_contrasts(self) -> None:
        positives = tuple(_projection(index) for index in range(4))
        contrasts = tuple(_projection(index, contrast=True) for index in range(3))
        validation, records = validate_grounding_corpus_prediction(
            concept_candidate_id="candidate:one",
            positive_projections=positives,
            contrast_projections=contrasts,
        )
        self.assertEqual(validation.positive_holdout_count, 4)
        self.assertEqual(validation.contrast_count, 3)
        self.assertTrue(validation.all_positive_holdouts_supported)
        self.assertTrue(validation.all_contrasts_distinguished)
        self.assertTrue(validation.predictive_validation_passed)
        self.assertEqual(len(records), 7)
        self.assertTrue(all(not item["runtime_recognition_performed"] for item in records))

    def test_confusion_blocks_predictive_maturity(self) -> None:
        positives = tuple(_projection(index) for index in range(4))
        validation, _ = validate_grounding_corpus_prediction(
            concept_candidate_id="candidate:confused",
            positive_projections=positives,
            contrast_projections=positives[:3],
        )
        self.assertFalse(validation.predictive_validation_passed)
        self.assertEqual(len(validation.confusion_episode_refs), 3)

    def test_maturity_requires_two_processes_and_two_runs(self) -> None:
        positives = tuple(_projection(index) for index in range(4))
        contrasts = tuple(_projection(index, contrast=True) for index in range(3))
        validation, _ = validate_grounding_corpus_prediction(
            concept_candidate_id="candidate:one",
            positive_projections=positives,
            contrast_projections=contrasts,
        )
        episodes = tuple(_episode(index) for index in range(7))
        ready = assess_auditory_concept_maturity(
            concept_candidate_id="candidate:one",
            positive_episodes=episodes[:4],
            contrast_episodes=episodes[4:],
            predictive_validation=validation,
        )
        self.assertEqual(ready.maturity_status, "ready_for_teacher_review")
        one_process = tuple(_episode(index, one_process=True) for index in range(7))
        blocked = assess_auditory_concept_maturity(
            concept_candidate_id="candidate:one",
            positive_episodes=one_process[:4],
            contrast_episodes=one_process[4:],
            predictive_validation=validation,
        )
        self.assertIn("blocked_single_process_grounding", blocked.failure_reasons)
        self.assertIn("blocked_single_grounding_run", blocked.failure_reasons)

    def test_model_identity_and_activation_are_bounded(self) -> None:
        episodes = tuple(_episode(index) for index in range(7))
        model = build_grounded_auditory_concept_model(
            reviewed_concept_id="reviewed:1",
            source_condition_profile_id="profile:one",
            positive_episodes=episodes[:4],
            contrast_episodes=episodes[4:],
            positive_projection_refs=("p0", "p1", "p2", "p3"),
            contrast_projection_refs=("c0", "c1", "c2"),
            expected_audio_primitive_refs=("expected:1",),
            predictive_validation_id="validation:1",
            source_trace_refs=("trace:1",),
        )
        recomputed = deterministic_auditory_concept_model_id(
            reviewed_concept_id=model.reviewed_concept_id,
            positive_episode_content_identities=tuple(item.raw_audio_content_hash for item in episodes[:4]),
            contrast_episode_content_identities=tuple(item.raw_audio_content_hash for item in episodes[4:]),
            expected_audio_primitive_refs=model.expected_audio_primitive_refs,
            source_condition_profile_id=model.source_condition_profile_id,
            compiler_version=model.compiler_version,
            blur_policy_version=model.blur_policy_version,
            predictive_validation_id=model.predictive_validation_id,
        )
        self.assertEqual(model.auditory_concept_model_id, recomputed)
        self.assertFalse(model.package_131_consumer_allowed)
        self.assertFalse(model.package_112_action_influence_allowed)
        ready = activate_model_after_deletion(model, deletion_audit_id="deletion:1")
        self.assertEqual(ready.auditory_concept_model_id, model.auditory_concept_model_id)
        self.assertTrue(ready.package_131_consumer_allowed)
        self.assertFalse(ready.recognition_enabled)

    def test_semantic_and_future_runtime_attempts_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            validate_expected_primitive_provenance(
                stimulus_ground_truth_used=True,
                teacher_feature_values_used=False,
            )
        with self.assertRaises(ValueError):
            validate_anonymous_concept_code("auditory_event_concept:three_pulses")
        with self.assertRaises(ValueError):
            reject_runtime_recognition_attempt()
        with self.assertRaises(ValueError):
            reject_automatic_concept_discovery(gcmc_runtime_used=True)

    def test_candidate_semantic_injection_is_rejected(self) -> None:
        payload = dict(
            concept_candidate_id="candidate:1",
            schema_version="ashl_grounded_auditory_event_concept_candidate_v0",
            created_at="2026-08-01T00:00:00+00:00",
            source_condition_profile_id="profile:1",
            positive_episode_refs=("p1", "p2", "p3", "p4"),
            contrast_episode_refs=("c1", "c2", "c3"),
            positive_feature_projection_refs=("pp1", "pp2", "pp3", "pp4"),
            contrast_feature_projection_refs=("cp1", "cp2", "cp3"),
            expected_audio_primitive_refs=("expected:1",),
            predictive_validation_id="validation:1",
            semantic_label=None,
            natural_language_name=None,
            object_identity=None,
            action_identity=None,
            material_identity=None,
            speaker_identity=None,
            candidate_generation_method="teacher_assigned_examples_plus_deterministic_predictive_template_v0",
            pattern_miner_used=False,
            clustering_runtime_used=False,
            llm_used=False,
            stimulus_manifest_used_for_generation=False,
            candidate_status="ready_for_teacher_review",
            source_record_refs=("assignment:1",),
            source_trace_refs=("trace:1",),
        )
        GroundedAuditoryEventConceptCandidate(**payload)
        with self.assertRaises(ValueError):
            GroundedAuditoryEventConceptCandidate(**{**payload, "speaker_identity": "speaker:1"})

    def test_store_is_external_and_append_only(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = Package130AuditoryConceptStore(directory)
            payload = {
                "control_result_id": "control:1",
                "controls": {"one": True},
            }
            store.append_payload(
                "auditory_concept_control_results",
                "control_result_id",
                "control:1",
                payload,
            )
            with self.assertRaises(ValueError):
                store.append_payload(
                    "auditory_concept_control_results",
                    "control_result_id",
                    "control:1",
                    payload,
                )
            self.assertTrue(str(store.database_path).startswith(directory))

    def test_cli_surface_and_capture_authorization_gate(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            ["run-grounding-set-a", "--state-dir", "external-state"]
        )
        self.assertFalse(args.allow_grounding_capture)
        with tempfile.TemporaryDirectory() as directory:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = package_130_cli_main(
                    ["run-grounding-set-a", "--state-dir", directory]
                )
            self.assertEqual(code, 1)
            self.assertIn("blocked_grounding_capture_authorization_missing", output.getvalue())


@unittest.skipUnless(os.name == "nt", "real grounding capture requires Windows")
class Package130RealGroundingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        descriptor = WindowsWasapiLoopbackSource(endpoint_id="default").source_descriptor()
        if not descriptor.available:
            raise unittest.SkipTest(descriptor.failure_reason or "WASAPI unavailable")
        cls._temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls._temp.cleanup)
        cls.state = Path(cls._temp.name) / "real_package_130"
        cls.set_a, code = _run_grounding_worker(
            state_dir=cls.state,
            set_name="A",
            render_endpoint="default",
        )
        if code != 0:
            raise RuntimeError(cls.set_a)
        cls.set_b, code = _run_grounding_worker(
            state_dir=cls.state,
            set_name="B",
            render_endpoint="default",
        )
        if code != 0:
            raise RuntimeError(cls.set_b)
        store = Package130AuditoryConceptStore(cls.state)
        manifests = {
            str(item["episode_id"]): str(item["fixture_slot"])
            for item in store.list_payloads("auditory_grounding_fixture_manifests")
        }
        positives = tuple(
            episode_id
            for episode_id, slot in manifests.items()
            if slot.startswith("P")
        )
        contrasts = tuple(
            episode_id
            for episode_id, slot in manifests.items()
            if slot.startswith("C")
        )
        cls.assignment = assign_grounding_examples(
            state_dir=cls.state,
            positive_episode_refs=positives,
            contrast_episode_refs=contrasts,
            confirm=True,
        )
        cls.candidate = build_concept_candidate(state_dir=cls.state)
        cls.review_identity = str(
            cls.candidate["teacher_review"]["evidence_identity_hash"]
        )
        try:
            review_concept(
                state_dir=cls.state,
                decision="approve",
                reviewer="local_teacher",
                expected_evidence_identity="0" * 64,
                confirm=True,
            )
        except ValueError:
            pass
        else:
            raise AssertionError("wrong Package 130 evidence identity was accepted")
        cls.reject_state = Path(cls._temp.name) / "rejected_package_130"
        shutil.copytree(cls.state, cls.reject_state)
        cls.rejection = review_concept(
            state_dir=cls.reject_state,
            decision="reject",
            reviewer="local_teacher",
            expected_evidence_identity=cls.review_identity,
            confirm=True,
        )
        cls.review = review_concept(
            state_dir=cls.state,
            decision="approve",
            reviewer="local_teacher",
            expected_evidence_identity=cls.review_identity,
            confirm=True,
        )
        cls.waiting_model = dict(cls.review["model"])
        cls.deletion = delete_grounding_audio(
            state_dir=cls.state,
            confirm=True,
        )
        cls.audit = audit_package_130_grounded_auditory_concept(
            state_dir=cls.state,
            append=True,
        )

    def test_real_corpus_uses_seven_fresh_sessions_and_two_processes(self) -> None:
        episodes = (
            tuple(item["episode"] for item in self.set_a["episodes"])
            + tuple(item["episode"] for item in self.set_b["episodes"])
        )
        self.assertEqual(len(episodes), 7)
        self.assertEqual(len({item["audio_capture_session_id"] for item in episodes}), 7)
        self.assertEqual(len({item["raw_audio_artifact_id"] for item in episodes}), 7)
        self.assertGreaterEqual(len({item["process_instance_id"] for item in episodes}), 2)
        self.assertGreaterEqual(len({item["grounding_run_id"] for item in episodes}), 2)
        self.assertTrue(all(item["transport_integrity_valid"] for item in episodes))
        self.assertTrue(all(item["semantic_label"] is None for item in episodes))

    def test_real_predictive_validation_and_exact_teacher_review(self) -> None:
        validation = self.candidate["predictive_validation"]
        self.assertTrue(validation["predictive_validation_passed"])
        self.assertTrue(validation["all_positive_holdouts_supported"])
        self.assertTrue(validation["all_contrasts_distinguished"])
        self.assertEqual(validation["confusion_episode_refs"], [])
        self.assertEqual(
            self.review["teacher_review_outcome"]["approval_text_exact"],
            TEACHER_APPROVAL_TEXT,
        )
        self.assertEqual(
            self.review["memory_commit"]["consumer_scope"],
            CONSUMER_SCOPE,
        )
        self.assertEqual(self.review["active_working_readback"], tuple())
        self.assertFalse(self.waiting_model["package_131_consumer_allowed"])

    def test_wrong_identity_blocks_and_reject_deletes_without_model(self) -> None:
        self.assertEqual(self.rejection["status"], "auditory_concept_teacher_rejected")
        self.assertIsNone(self.rejection["model"])
        self.assertIsNone(self.rejection["memory_commit"])
        cleanup = self.rejection["teacher_review_outcome"]["raw_grounding_audio_cleanup"]
        self.assertEqual(cleanup["successful_deletion_count"], 7)
        self.assertEqual(cleanup["raw_blob_count_after_deletion"], 0)
        self.assertFalse(cleanup["model_activated"])
        self.assertEqual(
            Package130AuditoryConceptStore(self.reject_state).list_payloads(
                "grounded_auditory_event_concept_models"
            ),
            tuple(),
        )

    def test_real_deletion_preserves_history_and_activates_typed_model(self) -> None:
        deletion = self.deletion["deletion_audit"]
        model = self.deletion["model"]
        self.assertEqual(deletion["successful_deletion_count"], 7)
        self.assertEqual(deletion["raw_blob_count_after_deletion"], 0)
        self.assertFalse(deletion["recoverable_waveform_detected"])
        self.assertTrue(deletion["audio_primitive_records_preserved"])
        self.assertTrue(model["package_131_consumer_allowed"])
        self.assertFalse(model["recognition_enabled"])
        self.assertEqual(
            model["auditory_concept_model_id"],
            self.waiting_model["auditory_concept_model_id"],
        )
        sensor_store = ContentAddressedSensorArtifactStore(self.state)
        episodes = Package130AuditoryConceptStore(self.state).list_payloads(
            "auditory_grounding_episodes"
        )
        for episode in episodes:
            artifact = sensor_store.get_artifact(str(episode["raw_audio_artifact_id"]))
            self.assertFalse((sensor_store.root_dir / str(artifact["blob_relative_path"])).exists())
            self.assertEqual(artifact["content_sha256"], episode["raw_audio_content_hash"])

    def test_real_final_audit_and_boundaries(self) -> None:
        self.assertEqual(self.audit.audit_status, PASS_STATUS)
        self.assertEqual(self.audit.positive_episode_count, 4)
        self.assertEqual(self.audit.contrast_episode_count, 3)
        self.assertTrue(self.audit.controls_passed)
        self.assertFalse(self.audit.runtime_recognition_created)
        self.assertFalse(self.audit.package_112_score_changed)
        self.assertFalse(self.audit.internal_action_created)
        self.assertFalse(self.audit.output_created)
        self.assertFalse(self.audit.external_control_created)
        self.assertFalse(self.audit.package_131_implemented)
        self.assertEqual(
            TeacherGatedSessionStore(self.state).load_active_working_readback(),
            tuple(),
        )


if __name__ == "__main__":
    unittest.main()
