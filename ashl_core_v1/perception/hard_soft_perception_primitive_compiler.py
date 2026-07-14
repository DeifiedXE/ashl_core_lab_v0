"""Foreground deterministic low-level perception primitive compiler for Package 121."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from ashl_core_v1.perception.audio_primitive_compiler import (
    AUDIO_PRIMITIVE_COMPILER_ID,
    AUDIO_PRIMITIVE_COMPILER_VERSION,
    build_audio_primitive_compiler_config,
    build_audio_primitive_compiler_descriptor,
    compile_audio_primitive,
)
from ashl_core_v1.perception.host_state_primitive_compiler import (
    HOST_STATE_COMPILER_ID,
    HOST_STATE_COMPILER_VERSION,
    build_host_state_compiler_config,
    build_host_state_compiler_descriptor,
    compile_host_state_primitive,
)
from ashl_core_v1.perception.perception_compiler_types import (
    EPHEMERAL_COMPILATION_RECEIPT_SCHEMA_VERSION,
    PERCEPTION_COMPILATION_BUNDLE_SCHEMA_VERSION,
    PERCEPTION_COMPILATION_RECORD_SCHEMA_VERSION,
    SOURCE_PRIMITIVE_LINK_SCHEMA_VERSION,
    EphemeralPerceptionCompilationReceipt,
    PerceptionCompilationBundle,
    PerceptionCompilationRecord,
    PerceptionCompilerConfig,
    PerceptionCompilerDescriptor,
    SourcePrimitiveLinkRecord,
)
from ashl_core_v1.perception.perception_primitive_store import (
    PerceptionPrimitiveStore,
    primitive_payload_sha256,
)
from ashl_core_v1.perception.perception_readable_data_builder import build_perception_readable_data
from ashl_core_v1.perception.perception_source_buffer import PerceptionSourceBuffer
from ashl_core_v1.perception.perception_source_resolver import (
    ResolvedPerceptionSource,
    resolve_ephemeral_audio_buffer,
    resolve_stored_sensor_artifact,
)
from ashl_core_v1.perception.visual_change_primitive_compiler import (
    VISUAL_CHANGE_COMPILER_ID,
    VISUAL_CHANGE_COMPILER_VERSION,
    build_visual_change_compiler_config,
    build_visual_change_compiler_descriptor,
    compile_visual_change_primitive,
)
from ashl_core_v1.perception.visual_frame_primitive_compiler import (
    VISUAL_FRAME_COMPILER_ID,
    VISUAL_FRAME_COMPILER_VERSION,
    build_visual_frame_compiler_config,
    build_visual_frame_compiler_descriptor,
    compile_visual_frame_primitive,
)
from ashl_core_v1.runtime.host_sensor_types import stable_id, utc_now


class HardSoftPerceptionPrimitiveCompiler:
    def __init__(self, state_dir: str | Path) -> None:
        self.state_dir = Path(state_dir)
        self.store = PerceptionPrimitiveStore(self.state_dir)

    def list_compilers(self) -> tuple[dict[str, object], ...]:
        descriptors = build_all_compiler_descriptors()
        for descriptor in descriptors:
            self.store.append_compiler_descriptor(descriptor)
        return tuple(descriptor.to_dict() for descriptor in descriptors)

    def compile_artifact(self, artifact_id: str) -> PerceptionCompilationBundle:
        resolved = resolve_stored_sensor_artifact(state_dir=self.state_dir, artifact_id=artifact_id)
        if resolved.buffer.source_kind in {"camera", "screen"}:
            config = build_visual_frame_compiler_config(source_kind=resolved.buffer.source_kind)
            descriptor = build_visual_frame_compiler_descriptor()
            primitive = compile_visual_frame_primitive(resolved.buffer, config=config)
            return self._persist_compilation(
                resolved=resolved,
                descriptor=descriptor,
                config=config,
                primitive=primitive,
                primitive_kind="visual_frame_primitive",
                primitive_id=primitive.visual_primitive_id,
                ephemeral=False,
            )
        if resolved.buffer.source_kind == "microphone":
            config = build_audio_primitive_compiler_config(privacy_policy_id="grounding_conservative_v0")
            descriptor = build_audio_primitive_compiler_descriptor()
            primitive = compile_audio_primitive(resolved.buffer, config=config)
            return self._persist_compilation(
                resolved=resolved,
                descriptor=descriptor,
                config=config,
                primitive=primitive,
                primitive_kind="audio_primitive",
                primitive_id=primitive.audio_primitive_id,
                ephemeral=False,
            )
        if resolved.buffer.source_kind == "host_state":
            config = build_host_state_compiler_config()
            descriptor = build_host_state_compiler_descriptor()
            primitive = compile_host_state_primitive(resolved.buffer, config=config)
            return self._persist_compilation(
                resolved=resolved,
                descriptor=descriptor,
                config=config,
                primitive=primitive,
                primitive_kind="host_state_primitive",
                primitive_id=primitive.host_state_primitive_id,
                ephemeral=False,
            )
        raise ValueError("unsupported source kind")

    def compile_ephemeral_audio(
        self,
        source: PerceptionSourceBuffer,
        *,
        privacy_policy_id: str = "recognition_ephemeral_v0",
    ) -> PerceptionCompilationBundle:
        resolved = resolve_ephemeral_audio_buffer(source)
        config = build_audio_primitive_compiler_config(privacy_policy_id=privacy_policy_id)
        descriptor = build_audio_primitive_compiler_descriptor()
        primitive = compile_audio_primitive(resolved.buffer, config=config)
        bundle = self._persist_compilation(
            resolved=resolved,
            descriptor=descriptor,
            config=config,
            primitive=primitive,
            primitive_kind="audio_primitive",
            primitive_id=primitive.audio_primitive_id,
            ephemeral=True,
        )
        receipt = EphemeralPerceptionCompilationReceipt(
            receipt_id=stable_id("ephemeral_compilation_receipt"),
            schema_version=EPHEMERAL_COMPILATION_RECEIPT_SCHEMA_VERSION,
            created_at=utc_now(),
            source_buffer_id=source.buffer_id,
            primitive_id=primitive.audio_primitive_id,
            compiler_id=AUDIO_PRIMITIVE_COMPILER_ID,
            compiler_version=AUDIO_PRIMITIVE_COMPILER_VERSION,
            privacy_policy_id=privacy_policy_id,
            raw_artifact_created=False,
            raw_blob_created=False,
            raw_temp_file_created=False,
            primitive_persisted=True,
            source_window_released=True,
            source_buffer_cleared_or_overwritable=True,
            source_trace_refs=source.source_trace_refs,
        )
        self.store.append_ephemeral_compilation_receipt(receipt)
        return bundle

    def compile_visual_pair(
        self,
        *,
        previous_artifact_id: str,
        current_artifact_id: str,
    ) -> PerceptionCompilationBundle:
        previous_bundle = self.compile_artifact(previous_artifact_id)
        current_bundle = self.compile_artifact(current_artifact_id)
        previous_payload = self.store.get_primitive(previous_bundle.primitive_record_id)
        current_payload = self.store.get_primitive(current_bundle.primitive_record_id)
        from ashl_core_v1.perception.visual_primitive_schema import VisualFramePrimitiveRecord

        previous = VisualFramePrimitiveRecord(**previous_payload)
        current = VisualFramePrimitiveRecord(**current_payload)
        config = build_visual_change_compiler_config(source_kind=current.source_kind)
        descriptor = build_visual_change_compiler_descriptor()
        primitive = compile_visual_change_primitive(previous, current, config=config)
        resolved = ResolvedPerceptionSource(
            buffer=PerceptionSourceBuffer(
                buffer_id=f"visual_pair:{previous_artifact_id}:{current_artifact_id}",
                schema_version="ashl_perception_source_buffer_v0",
                source_kind=current.source_kind,
                media_type="image/raw",
                storage_mode="stored_artifact",
                captured_at_utc=utc_now(),
                captured_at_monotonic_ns=0,
                adapter_id="visual_pair_resolver_v0",
                adapter_version="v0",
                media_format=current.pixel_format,
                sample_rate=None,
                channels=None,
                sample_format=None,
                frame_count=None,
                byte_length=1,
                readonly_bytes=memoryview(b"\x00"),
                source_artifact_id=current_artifact_id,
                source_trace_refs=primitive.source_trace_refs,
                ephemeral=False,
                persistence_allowed=True,
                width=current.width,
                height=current.height,
                row_stride_bytes=current.width * (3 if current.pixel_format == "BGR8" else 4),
                source_content_sha256="visual_pair_derived_no_raw_hash",
            ),
            source_artifact=None,
            source_content_sha256=None,
            source_trace_refs=primitive.source_trace_refs,
        )
        return self._persist_compilation(
            resolved=resolved,
            descriptor=descriptor,
            config=config,
            primitive=primitive,
            primitive_kind="visual_change_primitive",
            primitive_id=primitive.visual_change_id,
            ephemeral=False,
            bundle_status="compiled_stored_artifact",
        )

    def audit_store(self):
        return self.store.audit_store()

    def _persist_compilation(
        self,
        *,
        resolved: ResolvedPerceptionSource,
        descriptor: PerceptionCompilerDescriptor,
        config: PerceptionCompilerConfig,
        primitive: object,
        primitive_kind: str,
        primitive_id: str,
        ephemeral: bool,
        bundle_status: str | None = None,
    ) -> PerceptionCompilationBundle:
        self.store.append_compiler_descriptor(descriptor)
        self.store.append_compiler_config(config)
        payload_hash = primitive_payload_sha256(primitive)
        primitive = _with_payload_hash(primitive, payload_hash)
        self._append_primitive(primitive_kind, primitive)
        readable = build_perception_readable_data(primitive, compiler_config_sha256=config.config_sha256)
        self.store.append_perception_readable_data(readable)
        compilation = PerceptionCompilationRecord(
            compilation_record_id=stable_id("perception_compilation"),
            schema_version=PERCEPTION_COMPILATION_RECORD_SCHEMA_VERSION,
            created_at=utc_now(),
            source_kind=resolved.buffer.source_kind,
            source_artifact_id=resolved.buffer.source_artifact_id,
            source_buffer_id=resolved.buffer.buffer_id,
            source_content_sha256=None if ephemeral else resolved.source_content_sha256,
            compiler_id=descriptor.compiler_id,
            compiler_version=descriptor.compiler_version,
            compiler_config_sha256=config.config_sha256,
            privacy_policy_id=config.privacy_policy_id,
            primitive_record_kind=primitive_kind,
            primitive_record_id=primitive_id,
            primitive_payload_sha256=payload_hash,
            perception_readable_data_id=readable.perception_id,
            deterministic_compilation=True,
            learned_model_used=False,
            llm_used=False,
            network_used=False,
            replay_source_available=not ephemeral,
            compiled_before_source_disposal=ephemeral,
            source_trace_refs=resolved.source_trace_refs,
        )
        self.store.append_compilation_record(compilation)
        link = SourcePrimitiveLinkRecord(
            link_id=stable_id("source_primitive_link"),
            schema_version=SOURCE_PRIMITIVE_LINK_SCHEMA_VERSION,
            created_at=utc_now(),
            source_kind=resolved.buffer.source_kind,
            source_artifact_id=resolved.buffer.source_artifact_id,
            source_buffer_id=resolved.buffer.buffer_id,
            primitive_record_kind=primitive_kind,
            primitive_record_id=primitive_id,
            perception_readable_data_id=readable.perception_id,
            compilation_record_id=compilation.compilation_record_id,
            source_trace_refs=resolved.source_trace_refs,
        )
        self.store.append_source_primitive_link(link)
        status = bundle_status or ("compiled_ephemeral_source" if ephemeral else "compiled_stored_artifact")
        return PerceptionCompilationBundle(
            compilation_bundle_id=stable_id("perception_compilation_bundle"),
            schema_version=PERCEPTION_COMPILATION_BUNDLE_SCHEMA_VERSION,
            created_at=utc_now(),
            source_kind=resolved.buffer.source_kind,
            source_buffer_id=resolved.buffer.buffer_id,
            source_artifact_id=resolved.buffer.source_artifact_id,
            compiler_descriptor_id=descriptor.compiler_id,
            compiler_config_id=config.config_id,
            primitive_record_kind=primitive_kind,
            primitive_record_id=primitive_id,
            perception_readable_data_id=readable.perception_id,
            compilation_record_id=compilation.compilation_record_id,
            source_trace_refs=resolved.source_trace_refs,
            bundle_status=status,
        )

    def _append_primitive(self, primitive_kind: str, primitive: object) -> None:
        if primitive_kind == "visual_frame_primitive":
            self.store.append_visual_frame_primitive(primitive)  # type: ignore[arg-type]
        elif primitive_kind == "visual_change_primitive":
            self.store.append_visual_change_primitive(primitive)  # type: ignore[arg-type]
        elif primitive_kind == "audio_primitive":
            self.store.append_audio_primitive(primitive)  # type: ignore[arg-type]
        elif primitive_kind == "host_state_primitive":
            self.store.append_host_state_primitive(primitive)  # type: ignore[arg-type]
        else:
            raise ValueError(f"unsupported primitive kind: {primitive_kind}")


def build_all_compiler_descriptors() -> tuple[PerceptionCompilerDescriptor, ...]:
    return (
        build_visual_frame_compiler_descriptor(),
        build_visual_change_compiler_descriptor(),
        build_audio_primitive_compiler_descriptor(),
        build_host_state_compiler_descriptor(),
    )


def _with_payload_hash(primitive: object, payload_hash: str) -> object:
    if hasattr(primitive, "primitive_payload_sha256"):
        return replace(primitive, primitive_payload_sha256=payload_hash)
    return primitive


def compiler_ids() -> dict[str, str]:
    return {
        "visual_frame": VISUAL_FRAME_COMPILER_ID,
        "visual_change": VISUAL_CHANGE_COMPILER_ID,
        "audio": AUDIO_PRIMITIVE_COMPILER_ID,
        "host_state": HOST_STATE_COMPILER_ID,
        "visual_frame_version": VISUAL_FRAME_COMPILER_VERSION,
        "visual_change_version": VISUAL_CHANGE_COMPILER_VERSION,
        "audio_version": AUDIO_PRIMITIVE_COMPILER_VERSION,
        "host_state_version": HOST_STATE_COMPILER_VERSION,
    }
