"""CLI for Package 121 hard-soft perception primitive compiler."""

from __future__ import annotations

import argparse
import json
import math
import struct
from pathlib import Path
from typing import Any

from ashl_core_v1.perception.hard_soft_perception_primitive_compiler import (
    HardSoftPerceptionPrimitiveCompiler,
    build_all_compiler_descriptors,
)
from ashl_core_v1.perception.perception_deterministic_replay import (
    replay_stored_artifact_compilation,
)
from ashl_core_v1.perception.perception_source_buffer import (
    PERCEPTION_SOURCE_BUFFER_SCHEMA_VERSION,
    PerceptionSourceBuffer,
)


def _print_json(value: Any) -> None:
    if hasattr(value, "to_dict"):
        value = value.to_dict()
    print(json.dumps(value, indent=2, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m ashl_core_v1.perception.perception_primitive_compiler_cli",
        description="Deterministic low-level perception primitive compiler.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list-compilers")

    compile_artifact = subparsers.add_parser("compile-artifact")
    compile_artifact.add_argument("--state-dir", required=True)
    compile_artifact.add_argument("--artifact-id", required=True)

    visual_pair = subparsers.add_parser("compile-visual-pair")
    visual_pair.add_argument("--state-dir", required=True)
    visual_pair.add_argument("--previous-artifact-id", required=True)
    visual_pair.add_argument("--current-artifact-id", required=True)

    ephemeral = subparsers.add_parser("compile-ephemeral-audio")
    ephemeral.add_argument("--state-dir", required=True)
    ephemeral.add_argument("--ring-buffer-session-id", required=True)
    ephemeral.add_argument("--window-ms", type=int, default=1000)
    ephemeral.add_argument("--privacy-policy", default="recognition_ephemeral_v0")

    show_primitive = subparsers.add_parser("show-primitive")
    show_primitive.add_argument("--state-dir", required=True)
    show_primitive.add_argument("--primitive-id", required=True)

    show_data = subparsers.add_parser("show-perception-data")
    show_data.add_argument("--state-dir", required=True)
    show_data.add_argument("--perception-id", required=True)

    lineage = subparsers.add_parser("show-lineage")
    lineage.add_argument("--state-dir", required=True)
    lineage.add_argument("--perception-id", required=True)

    replay = subparsers.add_parser("replay-validate")
    replay.add_argument("--state-dir", required=True)
    replay.add_argument("--compilation-record-id", required=True)

    audit = subparsers.add_parser("audit-store")
    audit.add_argument("--state-dir", required=True)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "list-compilers":
        _print_json(tuple(descriptor.to_dict() for descriptor in build_all_compiler_descriptors()))
        return 0
    compiler = HardSoftPerceptionPrimitiveCompiler(Path(args.state_dir))
    if args.command == "compile-artifact":
        _print_json(compiler.compile_artifact(args.artifact_id))
        return 0
    if args.command == "compile-visual-pair":
        _print_json(
            compiler.compile_visual_pair(
                previous_artifact_id=args.previous_artifact_id,
                current_artifact_id=args.current_artifact_id,
            )
        )
        return 0
    if args.command == "compile-ephemeral-audio":
        _print_json(
            compiler.compile_ephemeral_audio(
                _build_cli_ephemeral_source_buffer(
                    ring_buffer_session_id=args.ring_buffer_session_id,
                    window_ms=args.window_ms,
                ),
                privacy_policy_id=args.privacy_policy,
            )
        )
        return 0
    if args.command == "show-primitive":
        _print_json(compiler.store.get_primitive(args.primitive_id))
        return 0
    if args.command == "show-perception-data":
        _print_json(compiler.store.get_perception_readable_data(args.perception_id))
        return 0
    if args.command == "show-lineage":
        _print_json(compiler.store.show_lineage_for_perception(args.perception_id))
        return 0
    if args.command == "replay-validate":
        _print_json(
            replay_stored_artifact_compilation(
                state_dir=Path(args.state_dir),
                compilation_record_id=args.compilation_record_id,
            )
        )
        return 0
    if args.command == "audit-store":
        _print_json(compiler.audit_store())
        return 0
    parser.error(f"unsupported command: {args.command}")
    return 2


def _build_cli_ephemeral_source_buffer(*, ring_buffer_session_id: str, window_ms: int) -> PerceptionSourceBuffer:
    if window_ms < 100 or window_ms > 10000:
        raise ValueError("ephemeral compilation window must be 100..10000 ms")
    sample_rate = 16000
    frame_count = int(sample_rate * window_ms / 1000)
    payload = b"".join(
        struct.pack("<h", int(8000 * math.sin(2.0 * math.pi * 220.0 * index / sample_rate)))
        for index in range(frame_count)
    )
    return PerceptionSourceBuffer(
        buffer_id=f"perception_source_buffer:{ring_buffer_session_id}",
        schema_version=PERCEPTION_SOURCE_BUFFER_SCHEMA_VERSION,
        source_kind="microphone",
        media_type="audio/pcm",
        storage_mode="recognition_ephemeral",
        captured_at_utc="cli_foreground_ephemeral_window",
        captured_at_monotonic_ns=0,
        adapter_id="cli_foreground_ephemeral_window_v0",
        adapter_version="v0",
        media_format="PCM_S16LE",
        sample_rate=sample_rate,
        channels=1,
        sample_format="int16",
        frame_count=frame_count,
        byte_length=len(payload),
        readonly_bytes=memoryview(payload),
        source_artifact_id=None,
        source_trace_refs=tuple(),
        ephemeral=True,
        persistence_allowed=False,
    )


if __name__ == "__main__":
    raise SystemExit(main())
