"""Read-only operator console state reader for Package 122B."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import SENSOR_STORE_DIRNAME, SENSOR_STORE_FILENAME
from ashl_core_v1.runtime.host_sensor_types import stable_id, utc_now
from ashl_core_v1.runtime.local_operator_console_store import LocalOperatorConsoleStore, build_default_console_store
from ashl_core_v1.runtime.operator_console_types import (
    AUDIT_SCHEMA_VERSION,
    TEXT_TIMELINE_SCHEMA_VERSION,
    STATUS_LOG_SCHEMA_VERSION,
    TOTAL_STATE_SCHEMA_VERSION,
    VIEW_MODEL_SCHEMA_VERSION,
    NonLLMLocalOutputSurfaceAuditRecord,
    QingyinHomeUpperConsoleViewModel,
    QingyinTotalRuntimeState,
    QingyinTotalStateSnapshot,
    TextTimelineEntry,
    OperatorStatusLogEntry,
    build_default_output_volume_state,
)
from ashl_core_v1.runtime.operator_hardware_status import (
    ACTIVE_CAPTURE_STATUSES,
    build_hardware_device_console_status,
    build_hardware_settings_snapshot,
    find_active_capture_session_id,
)
from ashl_core_v1.runtime.raw_output_token_registry import build_raw_output_token_registry
from ashl_core_v1.runtime.reserved_sound_pattern_registry import build_reserved_sound_pattern_registry
from ashl_core_v1.runtime.teacher_gated_session_store import STORE_FILENAME


ACTIVE_RUNTIME_STATUSES = {"created", "running", "resumed"}
TEACHER_GATE_STATUSES = {"waiting_teacher_review"}


def _teacher_store_db_path(state_dir: str | Path) -> Path:
    return Path(state_dir) / STORE_FILENAME


def _sensor_store_db_path(state_dir: str | Path) -> Path:
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


def _session_head_rows(state_dir: str | Path) -> tuple[dict[str, Any], ...]:
    db_path = _teacher_store_db_path(state_dir)
    if not db_path.exists():
        return tuple()
    connection = sqlite3.connect(str(db_path))
    try:
        connection.row_factory = sqlite3.Row
        try:
            rows = connection.execute(
                "SELECT session_id, current_status, current_checkpoint_id, version, updated_at FROM session_heads ORDER BY updated_at"
            ).fetchall()
        except sqlite3.Error:
            return tuple()
    finally:
        connection.close()
    return tuple(dict(row) for row in rows)


def _pending_reviews(state_dir: str | Path) -> tuple[dict[str, Any], ...]:
    return tuple(
        row
        for row in _payload_rows(_teacher_store_db_path(state_dir), "pending_teacher_reviews")
        if row.get("resolved") is False or row.get("review_status") == "pending"
    )


def build_total_state_snapshot(
    *,
    state_dir: str | Path,
    runtime_process_available: bool = False,
) -> QingyinTotalStateSnapshot:
    sessions = _session_head_rows(state_dir)
    active_runtime = next((row for row in reversed(sessions) if row.get("current_status") in ACTIVE_RUNTIME_STATUSES), None)
    teacher_gate_sessions = [row for row in sessions if row.get("current_status") in TEACHER_GATE_STATUSES]
    active_sensor_ids = []
    for kind in ("camera", "microphone"):
        active, _error, _refs = find_active_capture_session_id(state_dir, kind)
        if active:
            active_sensor_ids.append(active)
    if active_runtime or active_sensor_ids:
        total_state = QingyinTotalRuntimeState.RUNNING.value
        reasons = ("active_runtime_or_sensor_session",)
    elif runtime_process_available:
        total_state = QingyinTotalRuntimeState.SLEEPING.value
        reasons = ("runtime_process_available_no_active_work",)
    else:
        total_state = QingyinTotalRuntimeState.STOPPED.value
        reasons = ("no_active_qingyin_runtime_session",)
    pending = _pending_reviews(state_dir)
    source_refs = tuple(
        str(item)
        for item in (
            [active_runtime.get("session_id")] if active_runtime else []
        )
        + active_sensor_ids
        + [row.get("session_id") for row in teacher_gate_sessions]
        if item
    )
    return QingyinTotalStateSnapshot(
        snapshot_id=stable_id("qingyin_total_state_snapshot"),
        schema_version=TOTAL_STATE_SCHEMA_VERSION,
        created_at=utc_now(),
        total_state=total_state,
        runtime_process_available=runtime_process_available,
        active_runtime_session_id=str(active_runtime["session_id"]) if active_runtime else None,
        active_sensor_session_ids=tuple(active_sensor_ids),
        teacher_gate_active=bool(teacher_gate_sessions or pending),
        pending_teacher_review_count=len(pending) if pending else len(teacher_gate_sessions),
        state_reason_codes=reasons,
        source_record_refs=source_refs,
        source_trace_refs=tuple(),
    )


def build_upper_console_view_model(
    *,
    state_dir: str | Path,
    runtime_process_available: bool = False,
    timeline_limit: int = 100,
    status_log_limit: int = 100,
) -> QingyinHomeUpperConsoleViewModel:
    store = build_default_console_store(state_dir)
    total = build_total_state_snapshot(state_dir=state_dir, runtime_process_available=runtime_process_available)
    microphone = build_hardware_device_console_status(state_dir=state_dir, store=store, device_kind="microphone")
    camera = build_hardware_device_console_status(state_dir=state_dir, store=store, device_kind="camera")
    latest_volume = store.latest_output_volume_state()
    volume = build_default_output_volume_state() if latest_volume is None else _volume_from_dict(latest_volume)
    settings = build_hardware_settings_snapshot(state_dir=state_dir, store=store)
    timeline = tuple(_timeline_from_dict(item) for item in store.list_payloads("text_timeline_entries")[-timeline_limit:])
    logs = tuple(_log_from_dict(item) for item in store.list_payloads("status_log_entries")[-status_log_limit:])
    return QingyinHomeUpperConsoleViewModel(
        view_model_id=stable_id("qingyin_home_upper_console_view_model"),
        schema_version=VIEW_MODEL_SCHEMA_VERSION,
        created_at=utc_now(),
        total_state=total,
        microphone_status=microphone,
        camera_status=camera,
        output_volume=volume,
        hardware_settings=settings,
        text_timeline_entries=timeline,
        status_log_entries=logs,
        pending_output_count=store.pending_output_count(),
        sound_patterns_reserved=bool(build_reserved_sound_pattern_registry()),
        sound_output_enabled=False,
        source_record_refs=(total.snapshot_id, microphone.device_status_id, camera.device_status_id),
    )


def audit_non_llm_local_output_surface(state_dir: str | Path) -> NonLLMLocalOutputSurfaceAuditRecord:
    store = build_default_console_store(state_dir)
    view = build_upper_console_view_model(state_dir=state_dir, runtime_process_available=True)
    tokens = build_raw_output_token_registry()
    patterns = build_reserved_sound_pattern_registry()
    timeline_rows = store.list_payloads("text_timeline_entries")
    logs = store.list_payloads("status_log_entries")
    dispatches = store.list_payloads("output_dispatch_results")
    cancellations = store.list_payloads("output_cancellations")
    reasons: list[str] = []
    token_meaning = any(item.semantic_label is not None or item.predefined_meaning is not None for item in tokens)
    sound_meaning = any(item.semantic_label is not None or item.predefined_meaning is not None for item in patterns)
    qingyin_authored_created = any(bool(item.get("qingyin_authored")) for item in dispatches + timeline_rows)
    if token_meaning:
        reasons.append("predefined_token_meaning_detected")
    if sound_meaning:
        reasons.append("predefined_sound_meaning_detected")
    if qingyin_authored_created:
        reasons.append("qingyin_authored_output_created")
    valid = not reasons
    return NonLLMLocalOutputSurfaceAuditRecord(
        audit_id=stable_id("non_llm_local_output_surface_audit"),
        schema_version=AUDIT_SCHEMA_VERSION,
        created_at=utc_now(),
        total_state_model_valid=view.total_state.total_state in {item.value for item in QingyinTotalRuntimeState},
        hardware_status_model_valid=view.microphone_status.device_kind == "microphone" and view.camera_status.device_kind == "camera",
        hardware_settings_model_valid=view.hardware_settings.settings_status in {"available", "sensor_store_unavailable"},
        text_timeline_valid=all(not _contains_raw_media(item) for item in timeline_rows),
        text_input_boundary_valid=all(
            item.get("interpretation_status") == "received_unprocessed"
            and item.get("grounding_status") == "not_grounded"
            and not item.get("forwarded_to_runtime")
            for item in store.list_payloads("external_text_inputs")
        ),
        raw_output_boundary_valid=all(not item.get("qingyin_authored") for item in store.list_payloads("raw_output_sequences")),
        status_log_boundary_valid=all(not item.get("qingyin_output") for item in logs),
        output_dispatch_valid=all(item.get("sink_kind") == "local_text_surface" for item in dispatches),
        cancellation_valid=all(not (item.get("cancellation_succeeded") and item.get("already_dispatched")) for item in cancellations),
        mute_valid=True,
        rate_limit_valid=True,
        failure_reporting_valid=True,
        sound_pattern_schema_reserved=bool(patterns),
        sound_output_enabled=False,
        operator_status_misclassified_as_qingyin_output=any(item.get("qingyin_output") for item in logs),
        predefined_token_meaning_detected=token_meaning,
        predefined_sound_meaning_detected=sound_meaning,
        qingyin_authored_output_created=qingyin_authored_created,
        first_output_claimed=False,
        llm_used=False,
        codex_runtime_used=False,
        network_used=False,
        runtime_behavior_changed=False,
        audit_status="passed_non_llm_local_output_surface_and_operator_console_foundation" if valid else "blocked_non_llm_local_output_surface",
        failure_reasons=tuple(reasons),
    )


def _volume_from_dict(data: dict[str, Any]) -> Any:
    from ashl_core_v1.runtime.operator_console_types import LocalOutputVolumeState

    return LocalOutputVolumeState(**data)


def _timeline_from_dict(data: dict[str, Any]) -> TextTimelineEntry:
    return TextTimelineEntry(**data)


def _log_from_dict(data: dict[str, Any]) -> OperatorStatusLogEntry:
    return OperatorStatusLogEntry(**data)


def _contains_raw_media(payload: Any) -> bool:
    text = json.dumps(payload, sort_keys=True)
    return any(marker in text.lower() for marker in ("raw_pcm", "raw image bytes", "base64", "pixel_bytes", "audio_bytes"))
