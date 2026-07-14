"""Shared compiler records for Package 121 perception primitives."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import plain, sha256_payload, stable_id, utc_now


PERCEPTION_COMPILER_DESCRIPTOR_SCHEMA_VERSION = "ashl_perception_compiler_descriptor_v0"
PERCEPTION_COMPILER_CONFIG_SCHEMA_VERSION = "ashl_perception_compiler_config_v0"
PERCEPTION_COMPILATION_BUNDLE_SCHEMA_VERSION = "ashl_perception_compilation_bundle_v0"
PERCEPTION_COMPILATION_RECORD_SCHEMA_VERSION = "ashl_perception_compilation_record_v0"
SOURCE_PRIMITIVE_LINK_SCHEMA_VERSION = "ashl_source_primitive_link_v0"
EPHEMERAL_COMPILATION_RECEIPT_SCHEMA_VERSION = "ashl_ephemeral_perception_compilation_receipt_v0"
PERCEPTION_REPLAY_VALIDATION_SCHEMA_VERSION = "ashl_perception_replay_validation_v0"
PERCEPTION_COMPILATION_FAILURE_SCHEMA_VERSION = "ashl_perception_compilation_failure_v0"
HARD_SOFT_COMPILER_AUDIT_SCHEMA_VERSION = "ashl_hard_soft_perception_primitive_compiler_audit_v0"


def tuple_of_str(value: Any) -> tuple[str, ...]:
    return tuple(str(item) for item in (value or ()))


def payload_sha256_without(payload: dict[str, Any], *excluded_keys: str) -> str:
    data = dict(payload)
    for key in excluded_keys:
        data.pop(key, None)
    return sha256_payload(data)


@dataclass(frozen=True)
class PerceptionCompilerDescriptor:
    compiler_id: str
    schema_version: str
    created_at: str
    compiler_kind: str
    compiler_version: str
    supported_source_kinds: tuple[str, ...]
    supported_media_formats: tuple[str, ...]
    deterministic: bool
    learned_model_used: bool
    llm_used: bool
    network_required: bool
    configuration_schema_version: str
    implementation_module: str
    descriptor_sha256: str

    def __post_init__(self) -> None:
        if self.schema_version != PERCEPTION_COMPILER_DESCRIPTOR_SCHEMA_VERSION:
            raise ValueError("invalid compiler descriptor schema_version")
        if self.compiler_kind != "deterministic_signal_processing":
            raise ValueError("compiler_kind must be deterministic_signal_processing")
        if not self.deterministic or self.learned_model_used or self.llm_used or self.network_required:
            raise ValueError("Package 121 compiler descriptors must be deterministic and model-free")
        object.__setattr__(self, "supported_source_kinds", tuple_of_str(self.supported_source_kinds))
        object.__setattr__(self, "supported_media_formats", tuple_of_str(self.supported_media_formats))
        expected = payload_sha256_without(self.to_dict(), "created_at", "descriptor_sha256")
        if self.descriptor_sha256 and self.descriptor_sha256 != expected:
            raise ValueError("descriptor_sha256 mismatch")
        if not self.descriptor_sha256:
            object.__setattr__(self, "descriptor_sha256", expected)

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class PerceptionCompilerConfig:
    config_id: str
    schema_version: str
    compiler_id: str
    compiler_version: str
    source_kind: str
    parameter_payload: dict[str, object]
    privacy_policy_id: str | None
    config_sha256: str

    def __post_init__(self) -> None:
        if self.schema_version != PERCEPTION_COMPILER_CONFIG_SCHEMA_VERSION:
            raise ValueError("invalid compiler config schema_version")
        if self.source_kind not in {"camera", "screen", "microphone", "host_state", "visual_change"}:
            raise ValueError("invalid compiler config source_kind")
        object.__setattr__(self, "parameter_payload", dict(self.parameter_payload))
        expected = payload_sha256_without(self.to_dict(), "config_id", "config_sha256")
        if self.config_sha256 and self.config_sha256 != expected:
            raise ValueError("config_sha256 mismatch")
        if not self.config_sha256:
            object.__setattr__(self, "config_sha256", expected)

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class EphemeralPerceptionCompilationReceipt:
    receipt_id: str
    schema_version: str
    created_at: str
    source_buffer_id: str
    primitive_id: str
    compiler_id: str
    compiler_version: str
    privacy_policy_id: str
    raw_artifact_created: bool
    raw_blob_created: bool
    raw_temp_file_created: bool
    primitive_persisted: bool
    source_window_released: bool
    source_buffer_cleared_or_overwritable: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != EPHEMERAL_COMPILATION_RECEIPT_SCHEMA_VERSION:
            raise ValueError("invalid ephemeral compilation receipt schema_version")
        if self.raw_artifact_created or self.raw_blob_created or self.raw_temp_file_created:
            raise ValueError("ephemeral compilation must not create raw artifact/blob/temp file")
        if not (self.primitive_persisted and self.source_window_released and self.source_buffer_cleared_or_overwritable):
            raise ValueError("ephemeral compilation receipt must confirm primitive persistence and source release")
        object.__setattr__(self, "source_trace_refs", tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class PerceptionCompilationRecord:
    compilation_record_id: str
    schema_version: str
    created_at: str
    source_kind: str
    source_artifact_id: str | None
    source_buffer_id: str | None
    source_content_sha256: str | None
    compiler_id: str
    compiler_version: str
    compiler_config_sha256: str
    privacy_policy_id: str | None
    primitive_record_kind: str
    primitive_record_id: str
    primitive_payload_sha256: str
    perception_readable_data_id: str
    deterministic_compilation: bool
    learned_model_used: bool
    llm_used: bool
    network_used: bool
    replay_source_available: bool
    compiled_before_source_disposal: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != PERCEPTION_COMPILATION_RECORD_SCHEMA_VERSION:
            raise ValueError("invalid compilation record schema_version")
        if not self.deterministic_compilation or self.learned_model_used or self.llm_used or self.network_used:
            raise ValueError("Package 121 compilation must be deterministic and model-free")
        object.__setattr__(self, "source_trace_refs", tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class PerceptionCompilationBundle:
    compilation_bundle_id: str
    schema_version: str
    created_at: str
    source_kind: str
    source_buffer_id: str | None
    source_artifact_id: str | None
    compiler_descriptor_id: str
    compiler_config_id: str
    primitive_record_kind: str
    primitive_record_id: str
    perception_readable_data_id: str
    compilation_record_id: str
    source_trace_refs: tuple[str, ...]
    bundle_status: str

    def __post_init__(self) -> None:
        if self.schema_version != PERCEPTION_COMPILATION_BUNDLE_SCHEMA_VERSION:
            raise ValueError("invalid compilation bundle schema_version")
        if self.bundle_status not in {"compiled", "compiled_ephemeral_source", "compiled_stored_artifact", "blocked_invalid_input", "blocked_privacy_policy", "failed"}:
            raise ValueError("invalid compilation bundle status")
        object.__setattr__(self, "source_trace_refs", tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class SourcePrimitiveLinkRecord:
    link_id: str
    schema_version: str
    created_at: str
    source_kind: str
    source_artifact_id: str | None
    source_buffer_id: str | None
    primitive_record_kind: str
    primitive_record_id: str
    perception_readable_data_id: str
    compilation_record_id: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != SOURCE_PRIMITIVE_LINK_SCHEMA_VERSION:
            raise ValueError("invalid source primitive link schema_version")
        object.__setattr__(self, "source_trace_refs", tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class PerceptionReplayValidationRecord:
    replay_validation_id: str
    schema_version: str
    created_at: str
    source_artifact_id: str
    source_compilation_record_id: str
    replay_compiler_id: str
    replay_compiler_version: str
    replay_config_sha256: str
    original_primitive_sha256: str
    replay_primitive_sha256: str
    deterministic_match: bool
    replay_status: str
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != PERCEPTION_REPLAY_VALIDATION_SCHEMA_VERSION:
            raise ValueError("invalid replay validation schema_version")
        if self.replay_status not in {"deterministic_match", "deterministic_mismatch", "source_not_available", "failed"}:
            raise ValueError("invalid replay_status")
        object.__setattr__(self, "source_trace_refs", tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class PerceptionCompilationFailureRecord:
    failure_record_id: str
    schema_version: str
    created_at: str
    source_kind: str
    source_artifact_id: str | None
    source_buffer_id: str | None
    compiler_id: str
    compiler_version: str
    failure_kind: str
    failure_message: str
    primitive_created: bool
    perception_readable_data_created: bool
    source_trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != PERCEPTION_COMPILATION_FAILURE_SCHEMA_VERSION:
            raise ValueError("invalid compilation failure schema_version")
        if self.primitive_created or self.perception_readable_data_created:
            raise ValueError("failure record cannot claim partial successful output")
        if any(token in self.failure_message.lower() for token in ("base64", "pcm bytes", "pixel bytes", "raw bytes")):
            raise ValueError("failure message must not contain raw media")
        object.__setattr__(self, "source_trace_refs", tuple_of_str(self.source_trace_refs))

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


@dataclass(frozen=True)
class HardSoftPerceptionPrimitiveCompilerAuditRecord:
    audit_id: str
    schema_version: str
    created_at: str
    visual_frame_compiler_valid: bool
    visual_change_compiler_valid: bool
    audio_compiler_valid: bool
    host_state_compiler_valid: bool
    stored_artifact_input_valid: bool
    ephemeral_audio_input_valid: bool
    perception_readable_data_valid: bool
    trace_lineage_valid: bool
    deterministic_stored_replay_valid: bool
    ephemeral_source_not_persisted: bool
    observed_expected_audio_schema_shared: bool
    low_level_prosody_compiled: bool
    semantic_labels_absent: bool
    object_recognition_absent: bool
    speech_content_absent: bool
    speaker_identity_absent: bool
    emotion_labels_absent: bool
    learned_model_used: bool
    llm_used: bool
    network_used: bool
    sensor_driven_learning_created: bool
    memory_write_created: bool
    action_influence_created: bool
    raw_trace_unchanged: bool
    source_artifacts_unchanged: bool
    audit_status: str
    failure_reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


def build_compiler_descriptor(
    *,
    compiler_id: str,
    compiler_version: str,
    supported_source_kinds: tuple[str, ...],
    supported_media_formats: tuple[str, ...],
    implementation_module: str,
) -> PerceptionCompilerDescriptor:
    return PerceptionCompilerDescriptor(
        compiler_id=compiler_id,
        schema_version=PERCEPTION_COMPILER_DESCRIPTOR_SCHEMA_VERSION,
        created_at=utc_now(),
        compiler_kind="deterministic_signal_processing",
        compiler_version=compiler_version,
        supported_source_kinds=supported_source_kinds,
        supported_media_formats=supported_media_formats,
        deterministic=True,
        learned_model_used=False,
        llm_used=False,
        network_required=False,
        configuration_schema_version=PERCEPTION_COMPILER_CONFIG_SCHEMA_VERSION,
        implementation_module=implementation_module,
        descriptor_sha256="",
    )


def build_compiler_config(
    *,
    compiler_id: str,
    compiler_version: str,
    source_kind: str,
    parameter_payload: dict[str, object],
    privacy_policy_id: str | None = None,
) -> PerceptionCompilerConfig:
    return PerceptionCompilerConfig(
        config_id=stable_id("perception_compiler_config"),
        schema_version=PERCEPTION_COMPILER_CONFIG_SCHEMA_VERSION,
        compiler_id=compiler_id,
        compiler_version=compiler_version,
        source_kind=source_kind,
        parameter_payload=parameter_payload,
        privacy_policy_id=privacy_policy_id,
        config_sha256="",
    )
