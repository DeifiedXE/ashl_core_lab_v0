"""Hardware preference and indicator status helpers for Package 122B."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import SENSOR_STORE_DIRNAME, SENSOR_STORE_FILENAME
from ashl_core_v1.runtime.host_sensor_types import stable_id, utc_now
from ashl_core_v1.runtime.local_operator_console_store import LocalOperatorConsoleStore
from ashl_core_v1.runtime.operator_console_types import (
    HARDWARE_SETTINGS_SCHEMA_VERSION,
    HARDWARE_STATUS_SCHEMA_VERSION,
    HardwareDeviceConsoleStatus,
    HardwareIndicatorState,
    HardwareSettingsSnapshot,
    LocalOutputVolumeState,
    build_default_output_volume_state,
)


ACTIVE_CAPTURE_STATUSES = {"started", "running", "resumed"}
ERROR_CAPTURE_STATUSES = {"device_unavailable", "permission_denied", "capture_failed", "recovered_aborted"}


def _sensor_db_path(state_dir: str | Path) -> Path:
    return Path(state_dir) / SENSOR_STORE_DIRNAME / SENSOR_STORE_FILENAME


def _payload_rows(db_path: Path, table: str) -> tuple[dict[str, Any], ...]:
    if not db_path.exists():
        return tuple()
    connection = sqlite3.connect(str(db_path))
    try:
        connection.row_factory = sqlite3.Row
        try:
            rows = connection.execute(f"SELECT payload_json FROM {table} ORDER BY created_at").fetchall()
        except sqlite3.Error:
            return tuple()
    finally:
        connection.close()
    return tuple(json.loads(str(row["payload_json"])) for row in rows)


def _latest_lifecycle_by_capture_session(state_dir: str | Path) -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    db_path = _sensor_db_path(state_dir)
    for row in _payload_rows(db_path, "sensor_capture_lifecycle_events"):
        latest[str(row.get("capture_session_id"))] = row
    for row in _payload_rows(db_path, "ephemeral_audio_lifecycle_events"):
        latest[str(row.get("ring_buffer_session_id"))] = row
    return latest


def _capture_sessions_for_kind(state_dir: str | Path, device_kind: str) -> tuple[dict[str, Any], ...]:
    db_path = _sensor_db_path(state_dir)
    rows = [row for row in _payload_rows(db_path, "sensor_capture_sessions") if row.get("source_kind") == device_kind]
    if device_kind == "microphone":
        rows.extend(_payload_rows(db_path, "ephemeral_audio_sessions"))
    return tuple(rows)


def find_active_capture_session_id(state_dir: str | Path, device_kind: str) -> tuple[str | None, str | None, tuple[str, ...]]:
    latest = _latest_lifecycle_by_capture_session(state_dir)
    refs: list[str] = []
    last_error: str | None = None
    for session in _capture_sessions_for_kind(state_dir, device_kind):
        session_id = str(session.get("capture_session_id") or session.get("ephemeral_audio_session_id"))
        refs.append(session_id)
        lifecycle = latest.get(session_id)
        status = str((lifecycle or {}).get("new_status") or session.get("capture_status") or "")
        if status in ACTIVE_CAPTURE_STATUSES:
            return session_id, None, tuple(refs)
        if status in ERROR_CAPTURE_STATUSES:
            last_error = status
    return None, last_error, tuple(refs)


def list_sensor_device_descriptors(state_dir: str | Path, device_kind: str) -> tuple[dict[str, Any], ...]:
    if device_kind not in {"camera", "microphone"}:
        raise ValueError("device_kind must be camera or microphone")
    rows = [
        row
        for row in _payload_rows(_sensor_db_path(state_dir), "sensor_device_descriptors")
        if row.get("source_kind") == device_kind
    ]
    sanitized = []
    for row in rows:
        sanitized.append(
            {
                "device_id": row.get("device_id"),
                "device_index": row.get("device_index"),
                "device_display_name": row.get("device_display_name"),
                "backend_name": row.get("backend_name"),
                "available": row.get("available"),
                "permission_status": row.get("permission_status"),
                "adapter_id": row.get("adapter_id"),
                "adapter_version": row.get("adapter_version"),
            }
        )
    return tuple(sanitized)


def build_hardware_device_console_status(
    *,
    state_dir: str | Path,
    store: LocalOperatorConsoleStore,
    device_kind: str,
) -> HardwareDeviceConsoleStatus:
    if device_kind not in {"camera", "microphone"}:
        raise ValueError("device_kind must be camera or microphone")
    preference = store.latest_hardware_preference(device_kind) or {
        "enabled_preference": False,
        "preferred_device_id": None,
    }
    active_session_id, last_error, source_refs = find_active_capture_session_id(state_dir, device_kind)
    descriptors = list_sensor_device_descriptors(state_dir, device_kind)
    permission = "unknown"
    if descriptors:
        permission = str(descriptors[-1].get("permission_status") or "unknown")
    enabled = bool(preference.get("enabled_preference"))
    if last_error:
        indicator = HardwareIndicatorState.ERROR.value
    elif active_session_id:
        indicator = HardwareIndicatorState.ACTIVE.value
    elif permission == "not_requested" and enabled:
        indicator = HardwareIndicatorState.PERMISSION_PENDING.value
    elif enabled:
        indicator = HardwareIndicatorState.ENABLED_IDLE.value
    else:
        indicator = HardwareIndicatorState.DISABLED.value
    return HardwareDeviceConsoleStatus(
        device_status_id=stable_id("hardware_device_console_status"),
        schema_version=HARDWARE_STATUS_SCHEMA_VERSION,
        created_at=utc_now(),
        device_kind=device_kind,
        preferred_device_id=preference.get("preferred_device_id"),
        enabled_preference=enabled,
        indicator_state=indicator,
        active_capture_session_id=active_session_id,
        permission_status=permission,
        last_error_code=last_error,
        source_record_refs=source_refs,
        source_trace_refs=tuple(),
    )


def build_hardware_settings_snapshot(
    *,
    state_dir: str | Path,
    store: LocalOperatorConsoleStore,
) -> HardwareSettingsSnapshot:
    camera_pref = store.latest_hardware_preference("camera") or {}
    mic_pref = store.latest_hardware_preference("microphone") or {}
    volume = store.latest_output_volume_state()
    if volume is None:
        default = build_default_output_volume_state()
        store.append_output_volume_state(default)
        volume = default.to_dict()
    return HardwareSettingsSnapshot(
        settings_snapshot_id=stable_id("hardware_settings_snapshot"),
        schema_version=HARDWARE_SETTINGS_SCHEMA_VERSION,
        created_at=utc_now(),
        available_camera_devices=list_sensor_device_descriptors(state_dir, "camera"),
        available_microphone_devices=list_sensor_device_descriptors(state_dir, "microphone"),
        available_output_devices=tuple(),
        preferred_camera_device_id=camera_pref.get("preferred_device_id"),
        preferred_microphone_device_id=mic_pref.get("preferred_device_id"),
        preferred_output_device_id=None,
        output_gain=float(volume.get("normalized_gain", 0.5)),
        camera_enabled_preference=bool(camera_pref.get("enabled_preference", False)),
        microphone_enabled_preference=bool(mic_pref.get("enabled_preference", False)),
        settings_status="available" if _sensor_db_path(state_dir).exists() else "sensor_store_unavailable",
    )


def set_output_volume_state(
    store: LocalOperatorConsoleStore,
    *,
    gain: float | None = None,
    muted: bool | None = None,
    source: str = "local_operator_console",
) -> LocalOutputVolumeState:
    latest = store.latest_output_volume_state() or build_default_output_volume_state().to_dict()
    state = LocalOutputVolumeState(
        volume_state_id=stable_id("output_volume_state"),
        schema_version="ashl_local_output_volume_state_v0",
        created_at=utc_now(),
        normalized_gain=float(latest.get("normalized_gain", 0.5) if gain is None else gain),
        muted=bool(latest.get("muted", False) if muted is None else muted),
        sound_sink_available=bool(latest.get("sound_sink_available", False)),
        sound_sink_enabled_by_policy=False,
        source=source,
    )
    store.append_output_volume_state(state)
    return state
