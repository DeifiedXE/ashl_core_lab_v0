"""Read-only Package 130 evidence loading and Package 131 consumer binding."""

from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
from time import monotonic_ns
from typing import Any

from ashl_core_v1.perception.audio_primitive_compiler import AUDIO_PRIMITIVE_COMPILER_VERSION
from ashl_core_v1.perception.audio_primitive_schema import AudioPrimitiveRecord
from ashl_core_v1.perception.perception_primitive_store import (
    PERCEPTION_STORE_DIRNAME,
    PERCEPTION_STORE_FILENAME,
)
from ashl_core_v1.runtime.auditory_grounding_types import (
    BLUR_POLICY_VERSION,
    CONSUMER_SCOPE,
    AuditoryGroundingRawAudioDeletionAudit,
    AuditorySourceConditionProfile,
    ExpectedAudioPrimitiveGenerationRecord,
    GroundedAuditoryEventConceptModel,
)
from ashl_core_v1.runtime.auditory_predictive_recognition_types import (
    BINDING_SCHEMA_VERSION,
    PACKAGE_130_PASS_STATUS,
    READY_BINDING_STATUS,
    READY_MATURITY,
    SOURCE_COMPATIBILITY_SCHEMA_VERSION,
    AuditoryPredictionConsumerBindingRecord,
    AuditoryRecognitionSourceCompatibilityRecord,
)
from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import (
    SENSOR_STORE_DIRNAME,
    SENSOR_STORE_FILENAME,
)
from ashl_core_v1.runtime.host_sensor_types import sha256_payload, utc_now
from ashl_core_v1.runtime.package_130_auditory_concept_store import (
    DATABASE_NAME as PACKAGE_130_DATABASE_NAME,
    PACKAGE_DIR as PACKAGE_130_DIR,
)
from ashl_core_v1.runtime.package_131_auditory_predictive_recognition_store import (
    Package131AuditoryPredictiveRecognitionStore,
)
from ashl_core_v1.runtime.windows_wasapi_loopback_source import WindowsWasapiLoopbackSource


BLOCKED_MISSING_MODEL = "blocked_missing_teacher_reviewed_package_130_model"


class ReadOnlyJsonSqlite:
    """Small query-only reader that never initializes or migrates source stores."""

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)
        if not self.database_path.is_file():
            raise FileNotFoundError(self.database_path)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            f"file:{self.database_path.as_posix()}?mode=ro",
            uri=True,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA query_only = ON")
        return connection

    def list_payloads(self, table: str) -> tuple[dict[str, Any], ...]:
        if not table.replace("_", "").isalnum():
            raise ValueError("invalid read-only table name")
        with closing(self._connect()) as connection:
            rows = connection.execute(
                f"SELECT payload_json FROM {table} ORDER BY rowid"
            ).fetchall()
        return tuple(json.loads(str(row["payload_json"])) for row in rows)

    def get_payload(self, table: str, record_id: str) -> dict[str, Any]:
        if not table.replace("_", "").isalnum():
            raise ValueError("invalid read-only table name")
        with closing(self._connect()) as connection:
            columns = {
                str(row["name"])
                for row in connection.execute(f"PRAGMA table_info({table})").fetchall()
            }
            id_column = next(
                (
                    name
                    for name in columns
                    if name.endswith("_id") and name not in {"row_id", "session_id"}
                ),
                "record_id",
            )
            if "record_id" in columns:
                id_column = "record_id"
            row = connection.execute(
                f"SELECT payload_json FROM {table} WHERE {id_column} = ?",
                (str(record_id),),
            ).fetchone()
        if row is None:
            raise KeyError(record_id)
        return json.loads(str(row["payload_json"]))


@dataclass(frozen=True)
class LoadedPackage130PredictionEvidence:
    audit: dict[str, Any]
    model: GroundedAuditoryEventConceptModel
    generation: ExpectedAudioPrimitiveGenerationRecord
    expected_primitive: AudioPrimitiveRecord
    predictive_validation: dict[str, Any]
    deletion_audit: AuditoryGroundingRawAudioDeletionAudit
    source_profile: AuditorySourceConditionProfile
    memory_commit: dict[str, Any]
    reviewed_concept: dict[str, Any]
    grounding_episodes: tuple[dict[str, Any], ...]
    grounding_artifacts: tuple[dict[str, Any], ...]
    model_snapshot_sha256: str
    expected_template_sha256: str


def package_130_read_only_database_path(state_dir: str | Path) -> Path:
    return Path(state_dir) / PACKAGE_130_DIR / PACKAGE_130_DATABASE_NAME


def load_package_130_prediction_evidence(
    *,
    state_dir: str | Path,
    model_id: str | None = None,
) -> LoadedPackage130PredictionEvidence:
    path = Path(state_dir)
    try:
        package_reader = ReadOnlyJsonSqlite(package_130_read_only_database_path(path))
    except FileNotFoundError as error:
        raise RuntimeError(BLOCKED_MISSING_MODEL) from error

    audits = package_reader.list_payloads("package_130_audits")
    if not audits or str(audits[-1].get("audit_status")) != PACKAGE_130_PASS_STATUS:
        raise RuntimeError("blocked_package_130_audit_missing_or_not_passed")
    audit = dict(audits[-1])
    model_payloads = package_reader.list_payloads("grounded_auditory_event_concept_models")
    ready_payloads = tuple(
        item for item in model_payloads if item.get("maturity_status") == READY_MATURITY
    )
    ready_by_id = {str(item["auditory_concept_model_id"]): item for item in ready_payloads}
    if model_id is None:
        if not ready_by_id:
            raise RuntimeError(BLOCKED_MISSING_MODEL)
        if len(ready_by_id) != 1:
            raise RuntimeError("blocked_multiple_ready_models_require_model_id")
        selected_payload = next(iter(ready_by_id.values()))
    else:
        if model_id not in ready_by_id:
            raise RuntimeError("blocked_requested_model_not_ready_or_missing")
        selected_payload = ready_by_id[model_id]
    model = GroundedAuditoryEventConceptModel(**selected_payload)
    _validate_model_activation_state(model)

    generations = tuple(
        ExpectedAudioPrimitiveGenerationRecord(**item)
        for item in package_reader.list_payloads("expected_audio_primitive_generation_records")
    )
    matching_generations = tuple(
        item
        for item in generations
        if tuple(item.expected_audio_primitive_refs) == tuple(model.expected_audio_primitive_refs)
    )
    if len(matching_generations) != 1:
        raise RuntimeError("blocked_expected_generation_missing_or_ambiguous")
    generation = matching_generations[0]
    if not generation.source_positive_projection_refs or not generation.source_record_refs:
        raise RuntimeError("blocked_expected_generation_lineage_incomplete")

    primitive_reader = ReadOnlyJsonSqlite(
        path / PERCEPTION_STORE_DIRNAME / PERCEPTION_STORE_FILENAME
    )
    expected_ref = _one(model.expected_audio_primitive_refs, "expected AudioPrimitive")
    expected_payloads = tuple(
        item
        for item in primitive_reader.list_payloads("audio_primitives")
        if str(item.get("audio_primitive_id")) == expected_ref
    )
    if len(expected_payloads) != 1:
        raise RuntimeError("blocked_expected_audio_primitive_missing")
    expected_primitive = AudioPrimitiveRecord(**expected_payloads[0])
    if expected_primitive.primitive_role != "expected":
        raise RuntimeError("blocked_expected_audio_primitive_role_invalid")

    validation_payloads = tuple(
        item
        for item in package_reader.list_payloads("auditory_concept_predictive_validations")
        if str(item.get("predictive_validation_id")) == model.predictive_validation_id
    )
    if len(validation_payloads) != 1 or not validation_payloads[0].get("predictive_validation_passed"):
        raise RuntimeError("blocked_predictive_validation_missing_or_failed")
    predictive_validation = dict(validation_payloads[0])

    deletions = tuple(
        AuditoryGroundingRawAudioDeletionAudit(**item)
        for item in package_reader.list_payloads("auditory_grounding_raw_audio_deletion_audits")
        if str(item.get("deletion_audit_id")) == model.raw_audio_deletion_audit_id
    )
    if len(deletions) != 1:
        raise RuntimeError("blocked_package_130_deletion_audit_missing")
    deletion = deletions[0]
    _validate_deletion_audit(deletion)

    profiles = tuple(
        AuditorySourceConditionProfile(**item)
        for item in package_reader.list_payloads("auditory_source_condition_profiles")
        if str(item.get("source_condition_profile_id")) == model.source_condition_profile_id
    )
    if len(profiles) != 1:
        raise RuntimeError("blocked_source_condition_profile_missing")
    source_profile = profiles[0]

    memory_commits = tuple(
        item
        for item in package_reader.list_payloads("auditory_concept_memory_commit_records")
        if model.auditory_concept_model_id in tuple(item.get("source_record_refs") or ())
    )
    if len(memory_commits) != 1:
        raise RuntimeError("blocked_package_130_memory_consumer_binding_missing")
    memory_commit = dict(memory_commits[0])
    memory_application = dict(memory_commit.get("memory_application_data") or {})
    if (
        memory_commit.get("consumer_scope") != CONSUMER_SCOPE
        or memory_application.get("read_scope") != CONSUMER_SCOPE
        or memory_commit.get("active_package_112_working_readback_created") is not False
    ):
        raise RuntimeError("blocked_package_130_memory_scope_or_readback_invalid")
    reviewed_concept = dict(memory_commit.get("reviewed_concept") or {})
    if reviewed_concept.get("feedback_derived_reviewed_concept_id") != model.reviewed_concept_id:
        raise RuntimeError("blocked_reviewed_concept_lineage_mismatch")

    episodes_by_id = {
        str(item["episode_id"]): item
        for item in package_reader.list_payloads("auditory_grounding_episodes")
    }
    episode_refs = tuple(model.positive_episode_refs) + tuple(model.contrast_episode_refs)
    if len(episode_refs) != 7 or any(item not in episodes_by_id for item in episode_refs):
        raise RuntimeError("blocked_grounding_episode_metadata_incomplete")
    episodes = tuple(dict(episodes_by_id[item]) for item in episode_refs)
    sensor_reader = ReadOnlyJsonSqlite(path / SENSOR_STORE_DIRNAME / SENSOR_STORE_FILENAME)
    artifacts_by_id = {
        str(item["artifact_id"]): item
        for item in sensor_reader.list_payloads("sensor_raw_artifacts")
    }
    deletion_records = {
        str(item["deletion_record_id"]): item
        for item in sensor_reader.list_payloads("artifact_deletion_records")
    }
    artifacts = _validate_deleted_grounding_artifacts(
        state_dir=path,
        episodes=episodes,
        deletion=deletion,
        artifacts_by_id=artifacts_by_id,
        deletion_records=deletion_records,
    )
    _validate_model_identity_unchanged(model_payloads, model)

    snapshot_payload = {
        "model": model.to_dict(),
        "reviewed_concept": reviewed_concept,
        "memory_application_data": memory_application,
        "generation": generation.to_dict(),
        "expected_primitive": expected_primitive.to_dict(),
        "predictive_validation": predictive_validation,
        "deletion_audit": deletion.to_dict(),
        "source_profile": source_profile.to_dict(),
    }
    model_snapshot_sha256 = sha256_payload(snapshot_payload)
    expected_template_sha256 = sha256_payload(
        {
            "expected_audio_primitive_ref": expected_ref,
            "expected_audio_primitive": expected_primitive.to_dict(),
            "feature_centers": generation.feature_centers,
            "feature_tolerances": generation.feature_tolerances,
            "generation_id": generation.generation_id,
        }
    )
    validate_package_130_prediction_preflight_gate(
        audit_present=True,
        audit_status=str(audit["audit_status"]),
        model_maturity=model.maturity_status,
        consumer_scope=str(memory_commit["consumer_scope"]),
        package_131_consumer_allowed=model.package_131_consumer_allowed,
        raw_audio_dependency_active=model.raw_audio_dependency_active,
        deletion_audit_present=True,
        grounding_raw_blob_count=0,
        expected_primitive_present=True,
        expected_generation_present=True,
        generation_lineage_matches=True,
        active_working_readback_used=False,
        package_112_action_influence_allowed=model.package_112_action_influence_allowed,
    )
    return LoadedPackage130PredictionEvidence(
        audit=audit,
        model=model,
        generation=generation,
        expected_primitive=expected_primitive,
        predictive_validation=predictive_validation,
        deletion_audit=deletion,
        source_profile=source_profile,
        memory_commit=memory_commit,
        reviewed_concept=reviewed_concept,
        grounding_episodes=episodes,
        grounding_artifacts=artifacts,
        model_snapshot_sha256=model_snapshot_sha256,
        expected_template_sha256=expected_template_sha256,
    )


def bind_package_130_model_for_prediction(
    *,
    state_dir: str | Path,
    model_id: str | None = None,
    package_131_store: Package131AuditoryPredictiveRecognitionStore | None = None,
) -> tuple[LoadedPackage130PredictionEvidence, AuditoryPredictionConsumerBindingRecord]:
    evidence = load_package_130_prediction_evidence(state_dir=state_dir, model_id=model_id)
    loaded_at = monotonic_ns()
    memory_application = dict(evidence.memory_commit["memory_application_data"])
    identity = {
        "auditory_concept_model_id": evidence.model.auditory_concept_model_id,
        "model_snapshot_sha256": evidence.model_snapshot_sha256,
        "expected_template_sha256": evidence.expected_template_sha256,
        "model_loaded_monotonic_ns": loaded_at,
    }
    binding = AuditoryPredictionConsumerBindingRecord(
        binding_id="auditory_prediction_consumer_binding:" + sha256_payload(identity),
        schema_version=BINDING_SCHEMA_VERSION,
        created_at=utc_now(),
        package_130_audit_id=str(evidence.audit["audit_id"]),
        package_130_audit_status=str(evidence.audit["audit_status"]),
        model_record_id=evidence.model.model_record_id,
        auditory_concept_model_id=evidence.model.auditory_concept_model_id,
        reviewed_concept_id=evidence.model.reviewed_concept_id,
        expected_audio_primitive_ref=evidence.expected_primitive.audio_primitive_id,
        expected_generation_ref=evidence.generation.generation_id,
        predictive_validation_ref=evidence.model.predictive_validation_id,
        deletion_audit_ref=evidence.deletion_audit.deletion_audit_id,
        source_condition_profile_ref=evidence.source_profile.source_condition_profile_id,
        memory_application_data_ref=str(memory_application["memory_application_data_id"]),
        consumer_scope=CONSUMER_SCOPE,
        model_snapshot_sha256=evidence.model_snapshot_sha256,
        expected_template_sha256=evidence.expected_template_sha256,
        model_loaded_monotonic_ns=loaded_at,
        package_131_consumer_allowed=True,
        package_112_action_influence_allowed=False,
        active_working_readback_used=False,
        raw_audio_dependency_active=False,
        binding_status=READY_BINDING_STATUS,
        source_record_refs=(
            str(evidence.audit["audit_id"]),
            evidence.model.model_record_id,
            evidence.model.reviewed_concept_id,
            evidence.expected_primitive.audio_primitive_id,
            evidence.generation.generation_id,
            evidence.model.predictive_validation_id,
            evidence.deletion_audit.deletion_audit_id,
            evidence.source_profile.source_condition_profile_id,
            str(memory_application["memory_application_data_id"]),
        ),
        source_trace_refs=evidence.model.source_trace_refs,
    )
    if package_131_store is not None:
        package_131_store.append_record("auditory_prediction_consumer_bindings", binding)
    return evidence, binding


def verify_recognition_source_compatibility(
    *,
    evidence: LoadedPackage130PredictionEvidence,
    audio_source: WindowsWasapiLoopbackSource,
) -> AuditoryRecognitionSourceCompatibilityRecord:
    descriptor = audio_source.source_descriptor()
    descriptor_hash = sha256_payload(
        {
            "endpoint_id": descriptor.endpoint_id,
            "endpoint_name": descriptor.endpoint_name,
            "sample_rate_hz": descriptor.sample_rate_hz,
            "channel_count": descriptor.channel_count,
            "sample_format": descriptor.sample_format,
            "loopback_scope": descriptor.loopback_scope,
            "adapter_id": audio_source.adapter_id,
            "adapter_version": audio_source.adapter_version,
        }
    )
    grounding_formats = {str(item.get("storage_format")) for item in evidence.grounding_artifacts}
    endpoint_matches = descriptor_hash == evidence.source_profile.endpoint_descriptor_hash
    sample_rate_matches = descriptor.sample_rate_hz == evidence.source_profile.sample_rate_hz
    channel_count_matches = descriptor.channel_count == evidence.source_profile.channel_count
    sample_format_matches = grounding_formats == {str(descriptor.sample_format)}
    mapping_matches = (
        evidence.source_profile.canonical_channel_mapping
        == "stereo_mean_to_mono_low_level_features"
    )
    compiler_matches = evidence.source_profile.compiler_version == AUDIO_PRIMITIVE_COMPILER_VERSION
    blur_matches = evidence.source_profile.blur_policy_version == BLUR_POLICY_VERSION
    compatible = all(
        (
            endpoint_matches,
            sample_rate_matches,
            channel_count_matches,
            sample_format_matches,
            mapping_matches,
            compiler_matches,
            blur_matches,
            descriptor.available,
        )
    )
    identity = {
        "model_id": evidence.model.auditory_concept_model_id,
        "source_descriptor_id": descriptor.source_descriptor_id,
        "descriptor_hash": descriptor_hash,
        "compiler_version": AUDIO_PRIMITIVE_COMPILER_VERSION,
        "blur_policy_version": BLUR_POLICY_VERSION,
    }
    return AuditoryRecognitionSourceCompatibilityRecord(
        source_compatibility_id="auditory_recognition_source_compatibility:" + sha256_payload(identity),
        schema_version=SOURCE_COMPATIBILITY_SCHEMA_VERSION,
        created_at=utc_now(),
        auditory_concept_model_id=evidence.model.auditory_concept_model_id,
        source_condition_profile_ref=evidence.source_profile.source_condition_profile_id,
        source_adapter_id=audio_source.adapter_id,
        source_adapter_version=audio_source.adapter_version,
        endpoint_descriptor_hash=descriptor_hash,
        endpoint_id=str(descriptor.endpoint_id),
        endpoint_name=str(descriptor.endpoint_name),
        sample_rate_hz=int(descriptor.sample_rate_hz),
        channel_count=int(descriptor.channel_count),
        sample_format=str(descriptor.sample_format),
        canonical_channel_mapping="stereo_mean_to_mono_low_level_features",
        compiler_version=AUDIO_PRIMITIVE_COMPILER_VERSION,
        blur_policy_version=BLUR_POLICY_VERSION,
        grounding_raw_policy="grounding_conservative_v0",
        recognition_raw_policy="recognition_ephemeral_v0",
        generalization_scope=evidence.model.generalization_scope,
        endpoint_identity_matches=endpoint_matches,
        sample_rate_matches=sample_rate_matches,
        channel_count_matches=channel_count_matches,
        sample_format_matches=sample_format_matches,
        channel_mapping_matches=mapping_matches,
        compiler_version_matches=compiler_matches,
        blur_policy_version_matches=blur_matches,
        privacy_mode_difference_expected=True,
        cross_device_generalization_claimed=False,
        cross_room_generalization_claimed=False,
        speaker_identity_scope=False,
        compatibility_status=(
            "compatible_same_source_condition" if compatible else "blocked_source_condition_mismatch"
        ),
        source_record_refs=(
            evidence.source_profile.source_condition_profile_id,
            str(descriptor.source_descriptor_id),
        ),
        source_trace_refs=evidence.source_profile.source_trace_refs,
    )


def _validate_model_activation_state(model: GroundedAuditoryEventConceptModel) -> None:
    if model.maturity_status != READY_MATURITY:
        raise RuntimeError("blocked_model_not_ready_after_cleanup")
    if model.raw_audio_dependency_active or not model.raw_audio_deletion_audit_id:
        raise RuntimeError("blocked_model_raw_audio_dependency_active")
    if not model.package_131_consumer_allowed:
        raise RuntimeError("blocked_package_131_consumer_not_allowed")
    if model.package_112_action_influence_allowed:
        raise RuntimeError("blocked_package_112_action_influence")
    if any(
        (
            model.recognition_enabled,
            model.prediction_error_runtime_enabled,
            model.automatic_regrounding_enabled,
        )
    ):
        raise RuntimeError("blocked_package_130_model_runtime_mutation")


def validate_package_130_prediction_preflight_gate(
    *,
    audit_present: bool,
    audit_status: str | None,
    model_maturity: str,
    consumer_scope: str,
    package_131_consumer_allowed: bool,
    raw_audio_dependency_active: bool,
    deletion_audit_present: bool,
    grounding_raw_blob_count: int,
    expected_primitive_present: bool,
    expected_generation_present: bool,
    generation_lineage_matches: bool,
    active_working_readback_used: bool,
    package_112_action_influence_allowed: bool,
) -> None:
    """Typed preflight gate reused by runtime and negative controls."""

    if not audit_present:
        raise ValueError("blocked_package_130_audit_missing")
    if audit_status != PACKAGE_130_PASS_STATUS:
        raise ValueError("blocked_package_130_audit_not_passed")
    if model_maturity != READY_MATURITY:
        raise ValueError("blocked_model_not_ready_after_cleanup")
    if consumer_scope != CONSUMER_SCOPE:
        raise ValueError("blocked_wrong_package_131_consumer_scope")
    if not package_131_consumer_allowed:
        raise ValueError("blocked_package_131_consumer_not_allowed")
    if raw_audio_dependency_active:
        raise ValueError("blocked_raw_audio_dependency_active")
    if not deletion_audit_present:
        raise ValueError("blocked_package_130_deletion_audit_missing")
    if grounding_raw_blob_count:
        raise ValueError("blocked_grounding_raw_blob_still_exists")
    if not expected_primitive_present:
        raise ValueError("blocked_expected_audio_primitive_missing")
    if not expected_generation_present:
        raise ValueError("blocked_expected_generation_missing")
    if not generation_lineage_matches:
        raise ValueError("blocked_expected_generation_lineage_mismatch")
    if active_working_readback_used:
        raise ValueError("blocked_active_working_readback_used")
    if package_112_action_influence_allowed:
        raise ValueError("blocked_package_112_action_influence")


def _validate_deletion_audit(deletion: AuditoryGroundingRawAudioDeletionAudit) -> None:
    if (
        deletion.expected_raw_artifact_count != 7
        or deletion.successful_deletion_count != 7
        or deletion.failed_deletion_count != 0
        or deletion.raw_blob_count_after_deletion != 0
        or deletion.recoverable_waveform_detected
        or not deletion.model_activation_allowed
    ):
        raise RuntimeError("blocked_package_130_raw_audio_cleanup_incomplete")


def _validate_deleted_grounding_artifacts(
    *,
    state_dir: Path,
    episodes: tuple[dict[str, Any], ...],
    deletion: AuditoryGroundingRawAudioDeletionAudit,
    artifacts_by_id: dict[str, dict[str, Any]],
    deletion_records: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], ...]:
    artifacts: list[dict[str, Any]] = []
    episode_hashes: dict[str, str] = {}
    for episode in episodes:
        artifact_id = str(episode["raw_audio_artifact_id"])
        artifact = artifacts_by_id.get(artifact_id)
        if artifact is None:
            raise RuntimeError("blocked_grounding_artifact_metadata_missing")
        if str(artifact.get("content_sha256")) != str(episode.get("raw_audio_content_hash")):
            raise RuntimeError("blocked_grounding_episode_hash_mismatch")
        blob_path = state_dir / SENSOR_STORE_DIRNAME / str(artifact["blob_relative_path"])
        if blob_path.exists():
            raise RuntimeError("blocked_grounding_raw_blob_still_exists")
        episode_hashes[artifact_id] = str(episode["raw_audio_content_hash"])
        artifacts.append(dict(artifact))
    if set(deletion.raw_artifact_refs) != set(episode_hashes):
        raise RuntimeError("blocked_deletion_artifact_lineage_mismatch")
    records = tuple(
        deletion_records.get(record_id) for record_id in deletion.deletion_record_refs
    )
    if any(item is None for item in records):
        raise RuntimeError("blocked_deletion_record_missing")
    by_artifact = {str(item["artifact_id"]): item for item in records if item is not None}
    for artifact_id, expected_hash in episode_hashes.items():
        record = by_artifact.get(artifact_id)
        if (
            record is None
            or str(record.get("content_sha256_before_deletion")) != expected_hash
            or not record.get("deletion_verified")
        ):
            raise RuntimeError("blocked_deletion_hash_or_verification_mismatch")
    return tuple(artifacts)


def _validate_model_identity_unchanged(
    model_payloads: tuple[dict[str, Any], ...],
    ready_model: GroundedAuditoryEventConceptModel,
) -> None:
    states = tuple(
        item
        for item in model_payloads
        if item.get("auditory_concept_model_id") == ready_model.auditory_concept_model_id
    )
    if len(states) < 2:
        raise RuntimeError("blocked_model_activation_lineage_incomplete")
    waiting = tuple(
        item for item in states if item.get("maturity_status") == "reviewed_waiting_raw_audio_cleanup"
    )
    if len(waiting) != 1:
        raise RuntimeError("blocked_model_waiting_cleanup_lineage_missing")
    immutable_fields = (
        "auditory_concept_model_id",
        "reviewed_concept_id",
        "source_condition_profile_id",
        "positive_episode_refs",
        "contrast_episode_refs",
        "positive_feature_projection_refs",
        "contrast_feature_projection_refs",
        "expected_audio_primitive_refs",
        "predictive_validation_id",
        "compiler_version",
        "blur_policy_version",
        "source_scope",
        "generalization_scope",
    )
    ready_payload = ready_model.to_dict()
    if any(waiting[0].get(name) != ready_payload.get(name) for name in immutable_fields):
        raise RuntimeError("blocked_package_130_model_identity_changed")


def _one(values: tuple[str, ...], label: str) -> str:
    if len(values) != 1:
        raise RuntimeError(f"blocked_{label.lower().replace(' ', '_')}_cardinality")
    return values[0]
