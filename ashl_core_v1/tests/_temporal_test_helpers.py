from __future__ import annotations

from pathlib import Path

from ashl_core_v1.runtime.grounded_temporal_primitive_compiler import DEFAULT_PACKAGE_124_ARCHIVE
from ashl_core_v1.runtime.temporal_relation_compiler import build_temporal_anchor, build_temporal_span


ARCHIVE = DEFAULT_PACKAGE_124_ARCHIVE


def archive_available() -> bool:
    return (Path(ARCHIVE) / "archive_manifest.json").exists()


def anchor(clock_domain_id: str, time_ns: int, *, record_id: str | None = None):
    return build_temporal_anchor(
        source_record_id=record_id or f"record:{time_ns}",
        source_record_kind="test_record",
        source_lane="test_lane",
        clock_domain_id=clock_domain_id,
        normalized_event_time_ns=time_ns,
        source_native_time_ns=time_ns,
        processing_time_ns=time_ns + 1000,
        replay_submission_time_ns=time_ns + 500,
        event_sequence_index=int(time_ns // 100),
        timestamp_resolution_ns=1,
        timestamp_uncertainty_ns=10,
        source_record_refs=(record_id or f"record:{time_ns}",),
        source_trace_refs=("trace:test",),
    )


def span(clock_domain_id: str, start_ns: int, end_ns: int, *, lane: str = "screen"):
    start = anchor(clock_domain_id, start_ns, record_id=f"{lane}:{start_ns}:start")
    end = anchor(clock_domain_id, end_ns, record_id=f"{lane}:{end_ns}:end")
    return build_temporal_span(
        span_kind="observed_change_region" if lane != "microphone" else "observed_energy_region",
        start_anchor=start,
        end_anchor=end,
        source_lane=lane,
        source_record_refs=(f"{lane}:{start_ns}:{end_ns}",),
        source_trace_refs=("trace:test",),
    )
