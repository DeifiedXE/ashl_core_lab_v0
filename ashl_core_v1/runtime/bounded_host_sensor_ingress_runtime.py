"""Bounded foreground host sensor ingress runtime for Package 120."""

from __future__ import annotations

from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.camera_sensor_adapter import CameraSensorAdapter
from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import ContentAddressedSensorArtifactStore
from ashl_core_v1.runtime.host_sensor_types import (
    SensorCaptureConfig,
    SensorCaptureError,
    SensorCaptureSessionRecord,
    SensorDeviceDescriptor,
    build_sensor_capture_config,
    plain,
    stable_id,
)
from ashl_core_v1.runtime.host_state_sensor_adapter import HostStateSensorAdapter
from ashl_core_v1.runtime.microphone_sensor_adapter import MicrophoneSensorAdapter
from ashl_core_v1.runtime.no_codex_runtime_guard import NoCodexRuntimeGuard
from ashl_core_v1.runtime.screen_sensor_adapter import ScreenSensorAdapter
from ashl_core_v1.runtime.sensor_adapter_protocol import SensorAdapter


@dataclass(frozen=True)
class HostSensorCaptureRunResult:
    capture_session_id: str
    session_id: str
    source_kind: str
    capture_status: str
    artifact_ids: tuple[str, ...]
    failure_ids: tuple[str, ...]
    trace_envelope_ids: tuple[str, ...]
    store_audit_status: str
    codex_runtime_call_count: int
    llm_runtime_call_count: int
    network_model_call_count: int
    arbitrary_runtime_subprocess_call_count: int
    dynamic_code_execution_attempt_count: int
    sensor_artifacts_entered_package_115: bool
    host_body_event_created: bool
    learning_feedback_candidate_created: bool
    teacher_review_created: bool
    memory_write_created: bool
    first_output_created: bool
    external_control_created: bool

    def to_dict(self) -> dict[str, object]:
        return {field.name: plain(getattr(self, field.name)) for field in fields(self)}


class BoundedHostSensorIngressRuntime:
    def __init__(
        self,
        *,
        state_dir: str | Path,
        adapter: SensorAdapter,
        store: ContentAddressedSensorArtifactStore | None = None,
    ) -> None:
        self.state_dir = Path(state_dir)
        self.adapter = adapter
        self.store = store or ContentAddressedSensorArtifactStore(self.state_dir)
        self.active_session: SensorCaptureSessionRecord | None = None
        self.active_config: SensorCaptureConfig | None = None
        self.active_descriptor: SensorDeviceDescriptor | None = None
        self.status = "idle"
        self.artifact_ids: list[str] = []
        self.failure_ids: list[str] = []
        self.total_bytes = 0
        self._guard = NoCodexRuntimeGuard()

    def start(self, config: SensorCaptureConfig) -> SensorCaptureSessionRecord:
        if self.active_session is not None and self.status not in {"stopped", "hard_budget_stopped", "capture_failed"}:
            raise RuntimeError("one active sensor source per bounded capture session is allowed")
        descriptor = self._select_descriptor(config)
        session = self.store.create_capture_session(
            source_kind=config.source_kind,
            config=config,
            descriptor=descriptor,
        )
        self.active_session = session
        self.active_config = config
        self.active_descriptor = descriptor
        self.status = "created"
        with self._guard:
            try:
                self.adapter.open(config)
                self.store.append_lifecycle_event(
                    session=session,
                    previous_status="created",
                    new_status="started",
                    manual_command="start",
                    reason_code="manual_start_confirmed",
                )
                self.store.append_lifecycle_event(
                    session=session,
                    previous_status="started",
                    new_status="running",
                    manual_command=None,
                    reason_code="adapter_opened_read_only",
                )
                self.status = "running"
            except SensorCaptureError as error:
                self._record_failure(error)
                self.store.append_lifecycle_event(
                    session=session,
                    previous_status=self.status,
                    new_status=_failure_status(error.failure_kind),
                    manual_command=None,
                    reason_code=error.failure_kind,
                )
                self.status = "capture_failed"
                self.adapter.close()
                raise
            except Exception as error:
                failure = SensorCaptureError("unexpected_adapter_failure", str(error))
                self._record_failure(failure)
                self.store.append_lifecycle_event(
                    session=session,
                    previous_status=self.status,
                    new_status="capture_failed",
                    manual_command=None,
                    reason_code="unexpected_adapter_failure",
                )
                self.status = "capture_failed"
                self.adapter.close()
                raise
        return session

    def capture_next_sample(self) -> str:
        if self.active_session is None or self.active_config is None or self.active_descriptor is None:
            raise RuntimeError("capture session has not started")
        if self.status == "paused":
            raise RuntimeError("cannot capture artifact while lifecycle status is paused")
        if self.status != "running":
            raise RuntimeError(f"cannot capture while status is {self.status}")
        if len(self.artifact_ids) >= self.active_config.maximum_artifact_count:
            self.hard_stop("artifact_budget_exhausted")
            raise SensorCaptureError("artifact_budget_exhausted", "maximum artifact count reached")
        try:
            with self._guard:
                sample = self.adapter.read_sample()
            projected = self.total_bytes + len(sample.data)
            if projected > self.active_config.maximum_total_bytes:
                self.hard_stop("byte_budget_exhausted")
                raise SensorCaptureError("byte_budget_exhausted", "maximum total byte budget reached")
            artifact = self.store.write_raw_artifact(
                session=self.active_session,
                descriptor=self.active_descriptor,
                config=self.active_config,
                sample=sample,
            )
            self.artifact_ids.append(artifact.artifact_id)
            self.total_bytes = projected
            if len(self.artifact_ids) >= self.active_config.maximum_artifact_count:
                self.hard_stop("artifact_budget_exhausted")
            return artifact.artifact_id
        except SensorCaptureError as error:
            self._record_failure(error)
            if self.active_session is not None:
                self.store.append_lifecycle_event(
                    session=self.active_session,
                    previous_status=self.status,
                    new_status=_failure_status(error.failure_kind),
                    manual_command=None,
                    reason_code=error.failure_kind,
                )
            self.status = "capture_failed"
            self.adapter.close()
            raise

    def pause(self) -> None:
        if self.active_session is None or self.status != "running":
            raise RuntimeError("pause requires a running capture session")
        self.adapter.pause()
        self.store.append_lifecycle_event(
            session=self.active_session,
            previous_status="running",
            new_status="paused",
            manual_command="pause",
            reason_code="manual_pause",
        )
        self.status = "paused"

    def resume(self) -> None:
        if self.active_session is None or self.status != "paused":
            raise RuntimeError("resume requires a paused capture session")
        self.adapter.resume()
        self.store.append_lifecycle_event(
            session=self.active_session,
            previous_status="paused",
            new_status="resumed",
            manual_command="resume",
            reason_code="manual_resume",
        )
        self.store.append_lifecycle_event(
            session=self.active_session,
            previous_status="resumed",
            new_status="running",
            manual_command=None,
            reason_code="capture_running_after_resume",
        )
        self.status = "running"

    def stop(self, reason_code: str = "manual_stop") -> None:
        if self.active_session is None:
            raise RuntimeError("stop requires an active capture session")
        if self.status in {"stopped", "hard_budget_stopped", "capture_failed"}:
            raise RuntimeError("capture session is already terminal")
        self.store.append_lifecycle_event(
            session=self.active_session,
            previous_status=self.status,
            new_status="stopping",
            manual_command="stop",
            reason_code=reason_code,
        )
        self.adapter.close()
        self.store.append_lifecycle_event(
            session=self.active_session,
            previous_status="stopping",
            new_status="stopped",
            manual_command=None,
            reason_code="adapter_closed",
        )
        self.status = "stopped"

    def hard_stop(self, reason_code: str) -> None:
        if self.active_session is None:
            return
        if self.status in {"hard_budget_stopped", "stopped", "capture_failed"}:
            return
        self.adapter.close()
        self.store.append_lifecycle_event(
            session=self.active_session,
            previous_status=self.status,
            new_status="hard_budget_stopped",
            manual_command=None,
            reason_code=reason_code,
        )
        self.status = "hard_budget_stopped"

    def run_once(self, config: SensorCaptureConfig) -> HostSensorCaptureRunResult:
        session = self.start(config)
        try:
            self.capture_next_sample()
            if self.status == "running":
                self.stop()
        except Exception:
            if self.status not in {"capture_failed", "hard_budget_stopped"}:
                self.adapter.close()
            raise
        return self.result(session)

    def result(self, session: SensorCaptureSessionRecord | None = None) -> HostSensorCaptureRunResult:
        session = session or self.active_session
        if session is None:
            raise RuntimeError("capture session has not started")
        traces = self.store.list_trace_envelopes(session.session_id)
        audit = self.store.audit_store()
        counters = self._guard.counters()
        return HostSensorCaptureRunResult(
            capture_session_id=session.capture_session_id,
            session_id=session.session_id,
            source_kind=session.source_kind,
            capture_status=self.status,
            artifact_ids=tuple(self.artifact_ids),
            failure_ids=tuple(self.failure_ids),
            trace_envelope_ids=tuple(trace.trace_id for trace in traces),
            store_audit_status=audit.audit_status,
            codex_runtime_call_count=counters.codex_runtime_call_count,
            llm_runtime_call_count=counters.llm_runtime_call_count,
            network_model_call_count=counters.network_connection_attempt_count,
            arbitrary_runtime_subprocess_call_count=counters.arbitrary_subprocess_attempt_count,
            dynamic_code_execution_attempt_count=counters.dynamic_code_execution_attempt_count,
            sensor_artifacts_entered_package_115=False,
            host_body_event_created=False,
            learning_feedback_candidate_created=False,
            teacher_review_created=False,
            memory_write_created=False,
            first_output_created=False,
            external_control_created=False,
        )

    def _select_descriptor(self, config: SensorCaptureConfig) -> SensorDeviceDescriptor:
        descriptors = self.adapter.enumerate_devices()
        if config.source_kind == "host_state":
            descriptor = descriptors[0]
        else:
            requested_index = config.source_specific_config.get("device_index")
            if requested_index is None:
                requested_index = config.source_specific_config.get("input_device_index")
            if requested_index is None and config.source_kind == "screen":
                descriptor = descriptors[0]
            else:
                descriptor = next((item for item in descriptors if item.device_index == int(requested_index)), None)
                if descriptor is None:
                    raise SensorCaptureError("device_unavailable", f"device not found: {requested_index}")
        if not descriptor.available:
            raise SensorCaptureError("backend_missing", descriptor.device_display_name)
        return descriptor

    def _record_failure(self, error: SensorCaptureError) -> None:
        if self.active_session is None:
            return
        failure = self.store.record_failure(
            session=self.active_session,
            source_kind=self.active_session.source_kind,
            failure_kind=error.failure_kind,
            failure_message=str(error),
            recoverable=error.recoverable,
        )
        self.failure_ids.append(failure.failure_record_id)


def _failure_status(failure_kind: str) -> str:
    if failure_kind == "device_unavailable":
        return "device_unavailable"
    if failure_kind == "permission_denied":
        return "permission_denied"
    return "capture_failed"


def adapter_for_source(source_kind: str) -> SensorAdapter:
    if source_kind == "camera":
        return CameraSensorAdapter()
    if source_kind == "screen":
        return ScreenSensorAdapter()
    if source_kind == "microphone":
        return MicrophoneSensorAdapter()
    if source_kind == "host_state":
        return HostStateSensorAdapter()
    raise ValueError(f"unsupported source_kind: {source_kind}")


def list_sensor_backends() -> dict[str, object]:
    result: dict[str, object] = {}
    for source in ("camera", "screen", "microphone", "host_state"):
        adapter = adapter_for_source(source)
        devices = adapter.enumerate_devices()
        result[source] = {
            "adapter_id": adapter.adapter_id,
            "adapter_version": adapter.adapter_version,
            "source_kind": source,
            "available": any(item.available for item in devices),
            "devices": tuple(item.to_dict() for item in devices),
            "fixture_capture": False,
        }
    return result


def build_default_config_for_source(
    *,
    state_dir: str | Path,
    source_kind: str,
    device_index: int | None = None,
    monitor_index: int | None = None,
    region: tuple[int, int, int, int] | None = None,
    duration_ms: int | None = None,
) -> SensorCaptureConfig:
    adapter = adapter_for_source(source_kind)
    source_specific: dict[str, object]
    device_id = f"{source_kind}:default"
    if source_kind == "camera":
        if device_index is None:
            raise ValueError("camera capture requires explicit device_index")
        source_specific = {
            "device_index": int(device_index),
            "requested_width": 640,
            "requested_height": 480,
            "requested_fps": 1,
            "capture_frame_count": 1,
            "read_timeout_ms": 1000,
        }
        device_id = f"camera:opencv:{device_index}"
    elif source_kind == "screen":
        source_specific = {}
        if monitor_index is not None:
            source_specific["monitor_index"] = int(monitor_index)
        if region is not None:
            left, top, width, height = region
            source_specific.update({"left": left, "top": top, "width": width, "height": height})
        if not source_specific:
            raise ValueError("screen capture requires explicit monitor_index or region")
        device_id = "screen:local-display"
    elif source_kind == "microphone":
        if device_index is None:
            raise ValueError("microphone capture requires explicit device_index")
        source_specific = {
            "input_device_index": int(device_index),
            "requested_sample_rate": 16000,
            "requested_channels": 1,
            "requested_sample_format": "int16",
            "chunk_duration_ms": 100,
            "capture_duration_ms": int(duration_ms or 500),
        }
        device_id = f"microphone:input:{device_index}"
    elif source_kind == "host_state":
        source_specific = {"host_state_fields": "restricted_v0"}
        device_id = "host_state:restricted"
    else:
        raise ValueError(f"unsupported source_kind: {source_kind}")
    return build_sensor_capture_config(
        source_kind=source_kind,
        adapter_id=adapter.adapter_id,
        device_id=device_id,
        explicit_state_dir=state_dir,
        source_specific_config=source_specific,
        capture_duration_ms=int(duration_ms or (500 if source_kind == "microphone" else 5000)),
        maximum_artifact_count=1,
    )


def capture_once(
    *,
    state_dir: str | Path,
    source_kind: str,
    device_index: int | None = None,
    monitor_index: int | None = None,
    region: tuple[int, int, int, int] | None = None,
    duration_ms: int | None = None,
) -> HostSensorCaptureRunResult:
    config = build_default_config_for_source(
        state_dir=state_dir,
        source_kind=source_kind,
        device_index=device_index,
        monitor_index=monitor_index,
        region=region,
        duration_ms=duration_ms,
    )
    runtime = BoundedHostSensorIngressRuntime(
        state_dir=state_dir,
        adapter=adapter_for_source(source_kind),
    )
    return runtime.run_once(config)
