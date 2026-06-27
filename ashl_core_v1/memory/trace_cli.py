"""Minimal CLI for first-stage memory learning trace queries."""

from __future__ import annotations

import argparse
from pathlib import Path

from ashl_core_v1.memory.trace_store import (
    find_influence_by_thought_read_trace,
    find_memory_learning_trace,
    find_memory_learning_trace_by_reviewed_digest,
    find_thought_reads_by_memory_application_data,
    seed_blocked_sample_trace,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ASHL Core v1 memory trace query CLI")
    parser.add_argument("--data-dir", type=Path, default=None)
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("seed-blocked-sample-trace")

    show_trace = subparsers.add_parser("show-learning-trace")
    show_trace.add_argument("--trace-id", required=True)

    show_by_digest = subparsers.add_parser("show-by-reviewed-digest")
    show_by_digest.add_argument("--reviewed-digest-id", required=True)

    show_readback = subparsers.add_parser("show-readback")
    show_readback.add_argument("--memory-application-data-id", required=True)

    show_influence = subparsers.add_parser("show-influence")
    show_influence.add_argument("--thought-read-trace-id", required=True)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "seed-blocked-sample-trace":
        records = seed_blocked_sample_trace(args.data_dir)
        memory_trace = records["memory_learning_trace"]
        print(
            "seeded memory_learning_trace_id={trace_id} "
            "source_review_record_id={review_id} routing_status={routing_status}".format(
                trace_id=memory_trace["memory_learning_trace_id"],
                review_id=memory_trace["source_review_record_id"],
                routing_status=memory_trace["routing_status"],
            )
        )
        return 0

    if args.command == "show-learning-trace":
        trace = find_memory_learning_trace(args.trace_id, args.data_dir)
        if trace is None:
            print(f"not_found memory_learning_trace_id={args.trace_id}")
            return 1
        print(_format_learning_trace(trace.to_dict()))
        return 0

    if args.command == "show-by-reviewed-digest":
        trace = find_memory_learning_trace_by_reviewed_digest(
            args.reviewed_digest_id,
            args.data_dir,
        )
        if trace is None:
            print(f"not_found reviewed_digest_id={args.reviewed_digest_id}")
            return 1
        print(_format_learning_trace(trace.to_dict()))
        return 0

    if args.command == "show-readback":
        traces = find_thought_reads_by_memory_application_data(
            args.memory_application_data_id,
            args.data_dir,
        )
        if not traces:
            print(f"not_found memory_application_data_id={args.memory_application_data_id}")
            return 1
        for trace in traces:
            record = trace.to_dict()
            print(
                "thought_read_trace_id={trace_id} "
                "source_memory_application_data_refs={refs} read_reason={reason} "
                "read_result_summary={summary}".format(
                    trace_id=record["thought_read_trace_id"],
                    refs=",".join(record["source_memory_application_data_refs"]),
                    reason=record["read_reason"],
                    summary=record["read_result_summary"],
                )
            )
        return 0

    if args.command == "show-influence":
        traces = find_influence_by_thought_read_trace(args.thought_read_trace_id, args.data_dir)
        if not traces:
            print(f"not_found thought_read_trace_id={args.thought_read_trace_id}")
            return 1
        for trace in traces:
            record = trace.to_dict()
            print(
                "influence_trace_id={trace_id} source_thought_read_trace_id={source_id} "
                "affected_signal_ref={affected} influence_visible={visible} "
                "before_summary={before} after_summary={after}".format(
                    trace_id=record["influence_trace_id"],
                    source_id=record["source_thought_read_trace_id"],
                    affected=record["affected_signal_ref"],
                    visible=str(record["influence_visible"]).lower(),
                    before=record["before_summary"],
                    after=record["after_summary"],
                )
            )
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2


def _format_learning_trace(record: dict[str, object]) -> str:
    return (
        "memory_learning_trace_id={trace_id} "
        "source_reviewed_digest_id={reviewed_id} "
        "source_learning_digest_id={digest_id} "
        "source_review_record_id={review_id} "
        "source_perception_refs={perception_refs} "
        "source_endocrine_refs={endocrine_refs} "
        "state_snapshot_ref={state_ref} "
        "session_summary_ref={session_ref} "
        "last_trace_summary_ref={last_trace_ref} "
        "routing_status={routing_status} "
        "memory_layer_target={target}"
    ).format(
        trace_id=record["memory_learning_trace_id"],
        reviewed_id=record["source_reviewed_digest_id"],
        digest_id=record["source_learning_digest_id"],
        review_id=record["source_review_record_id"],
        perception_refs=",".join(record["source_perception_refs"]),
        endocrine_refs=",".join(record["source_endocrine_refs"]),
        state_ref=record["state_snapshot_ref"],
        session_ref=record["session_summary_ref"],
        last_trace_ref=record["last_trace_summary_ref"],
        routing_status=record["routing_status"],
        target=record["memory_layer_target"],
    )


if __name__ == "__main__":
    raise SystemExit(main())
