"""CLI for Package 126 bounded capture-again and listen-again actions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import plain, stable_id, utc_now
from ashl_core_v1.runtime.package_126_reacquisition_audit import (
    audit_package_126_reacquisition,
)
from ashl_core_v1.runtime.package_126_reacquisition_runtime import (
    run_real_capture_again,
    run_real_listen_again,
    run_synthetic_package_126_smoke,
)
from ashl_core_v1.runtime.package_126_reacquisition_store import (
    Package126ReacquisitionStore,
)
from ashl_core_v1.runtime.perception_reacquisition_internal_action import (
    cancel_pending_reacquisition,
    create_bounded_reacquisition_internal_action,
)
from ashl_core_v1.runtime.perception_reacquisition_policy import (
    create_reacquisition_request,
    decide_reacquisition_eligibility,
)
from ashl_core_v1.runtime.perception_reacquisition_types import (
    CompletedObservationWindowReference,
    PerceptionReacquisitionAuthorization,
    PerceptionReacquisitionRequest,
    SamplingPlanIdentityRecord,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Package 126 bounded fresh-world perception reacquisition"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    synthetic = sub.add_parser("synthetic-smoke")
    synthetic.add_argument("--state-dir", required=True)

    for name in (
        "run-real-capture-again",
        "run-real-listen-again",
        "guided-capture-again",
        "guided-listen-again",
    ):
        command = sub.add_parser(name)
        command.add_argument("--state-dir", required=True)
        command.add_argument("--render-endpoint", default="default")
        command.add_argument("--allow-reacquisition", action="store_true")

    for name in ("request-capture-again", "request-listen-again"):
        command = sub.add_parser(name)
        command.add_argument("--state-dir", required=True)
        command.add_argument("--parent-window-id", required=True)

    cancel = sub.add_parser("cancel-request")
    cancel.add_argument("--state-dir", required=True)
    cancel.add_argument("--request-id", required=True)

    stop = sub.add_parser("stop-child-window")
    stop.add_argument("--state-dir", required=True)
    stop.add_argument("--child-window-id", required=True)

    chain = sub.add_parser("show-reacquisition-chain")
    chain.add_argument("--state-dir", required=True)
    chain.add_argument("--parent-window-id", required=True)

    deletion = sub.add_parser("show-audio-deletion-status")
    deletion.add_argument("--state-dir", required=True)
    deletion.add_argument("--child-window-id", required=True)

    audit = sub.add_parser("audit")
    audit.add_argument("--state-dir", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "synthetic-smoke":
        _human("Running Package 126 synthetic policy and identity smoke; no sensor will open.")
        return _print_json(
            run_synthetic_package_126_smoke(state_dir=args.state_dir)
        )
    if args.command in {
        "run-real-capture-again",
        "guided-capture-again",
    }:
        return _run_real(
            action_kind="capture_again",
            state_dir=args.state_dir,
            render_endpoint=args.render_endpoint,
            allow_reacquisition=args.allow_reacquisition,
            guided=args.command.startswith("guided-"),
        )
    if args.command in {
        "run-real-listen-again",
        "guided-listen-again",
    }:
        return _run_real(
            action_kind="listen_again",
            state_dir=args.state_dir,
            render_endpoint=args.render_endpoint,
            allow_reacquisition=args.allow_reacquisition,
            guided=args.command.startswith("guided-"),
        )
    if args.command in {
        "request-capture-again",
        "request-listen-again",
    }:
        return _request_existing_parent(
            state_dir=args.state_dir,
            parent_window_id=args.parent_window_id,
            action_kind=(
                "capture_again"
                if args.command == "request-capture-again"
                else "listen_again"
            ),
        )
    if args.command == "cancel-request":
        return _cancel_request(args.state_dir, args.request_id)
    if args.command == "stop-child-window":
        return _stop_child(args.state_dir, args.child_window_id)
    if args.command == "show-reacquisition-chain":
        return _show_chain(args.state_dir, args.parent_window_id)
    if args.command == "show-audio-deletion-status":
        return _show_deletion(args.state_dir, args.child_window_id)
    if args.command == "audit":
        audit = audit_package_126_reacquisition(
            state_dir=args.state_dir,
            append=True,
        )
        _human(
            "Package 126 audit passed."
            if audit.audit_status.startswith("passed_")
            else "Package 126 audit is blocked; failure reasons follow."
        )
        return _print_json(
            audit.to_dict(),
            exit_code=0 if audit.audit_status.startswith("passed_") else 1,
        )
    raise SystemExit(f"unknown command: {args.command}")


def _run_real(
    *,
    action_kind: str,
    state_dir: str,
    render_endpoint: str,
    allow_reacquisition: bool,
    guided: bool,
) -> int:
    if not allow_reacquisition:
        _human(
            "Real reacquisition is blocked because explicit --allow-reacquisition was not supplied."
        )
        return _print_json(
            {
                "status": "blocked_reacquisition_authorization_missing",
                "action_kind": action_kind,
                "child_window_created": False,
                "sensor_reopened": False,
            },
            exit_code=1,
        )
    if guided:
        _human(
            "Guided sequence: preflight, parent capture, clean finalization, explicit authorization, "
            "new child sessions, fresh evidence, external gap, audio clearing, audit evidence."
        )
    else:
        _human(
            f"Starting real {action_kind}: two separate 2.5 second windows with one explicit reacquisition."
        )
    try:
        result = (
            run_real_capture_again(
                state_dir=state_dir,
                render_endpoint=render_endpoint,
                allow_reacquisition=True,
            )
            if action_kind == "capture_again"
            else run_real_listen_again(
                state_dir=state_dir,
                render_endpoint=render_endpoint,
                allow_reacquisition=True,
            )
        )
    except Exception as error:
        _human(f"Real {action_kind} was blocked: {type(error).__name__}: {error}")
        return _print_json(
            {
                "status": f"blocked_real_{action_kind}",
                "exception_kind": type(error).__name__,
                "reason": str(error),
                "state_dir": str(Path(state_dir)),
                "raw_audio_retained": False,
                "memory_write_created": False,
                "output_created": False,
                "external_control_created": False,
            },
            exit_code=1,
        )
    _human(
        f"Real {action_kind} completed with distinct capture sessions and an explicit cross-window gap."
    )
    return _print_json(result)


def _request_existing_parent(
    *,
    state_dir: str,
    parent_window_id: str,
    action_kind: str,
) -> int:
    store = Package126ReacquisitionStore(state_dir)
    parent_payload = next(
        (
            item
            for item in reversed(
                store.list_payloads("completed_parent_window_refs")
            )
            if item.get("observation_window_id") == parent_window_id
        ),
        None,
    )
    if parent_payload is None:
        _human("No completed clean parent window was found.")
        return _print_json(
            {"status": "parent_window_not_found"},
            exit_code=1,
        )
    parent = CompletedObservationWindowReference(**parent_payload)
    plan_payload = store.get_payload(
        "sampling_plan_identity_records",
        parent.sampling_plan_identity_ref,
    )
    plan = SamplingPlanIdentityRecord(**plan_payload)
    authorization_payload = next(
        (
            item
            for item in reversed(
                store.list_payloads(
                    "perception_reacquisition_authorizations"
                )
            )
            if item.get("parent_observation_window_id") == parent_window_id
        ),
        None,
    )
    authorization = (
        PerceptionReacquisitionAuthorization(**authorization_payload)
        if authorization_payload
        else None
    )
    request = create_reacquisition_request(
        parent=parent,
        authorization=authorization,
        requested_action_kind=action_kind,
        requested_plan=plan,
    )
    store.append_record("perception_reacquisition_requests", request)
    prior_count = sum(
        1
        for item in store.list_payloads(
            "reacquisition_capture_executions"
        )
        if item.get("parent_observation_window_id") == parent_window_id
    )
    eligibility = decide_reacquisition_eligibility(
        request=request,
        parent=parent,
        parent_plan=plan,
        requested_plan=plan,
        authorization=authorization,
        prior_attempt_count=prior_count,
    )
    store.append_record("reacquisition_eligibility_decisions", eligibility)
    action = create_bounded_reacquisition_internal_action(
        request=request,
        eligibility=eligibility,
        parent=parent,
    )
    if action:
        store.append_record("bounded_reacquisition_internal_actions", action)
    _human(
        "Reacquisition request was allowed and remains pending execution."
        if action
        else f"Reacquisition request was {eligibility.decision}."
    )
    return _print_json(
        {
            "request": request.to_dict(),
            "eligibility": eligibility.to_dict(),
            "internal_action": action.to_dict() if action else None,
            "sensor_opened": False,
        },
        exit_code=0 if action else 1,
    )


def _cancel_request(state_dir: str, request_id: str) -> int:
    store = Package126ReacquisitionStore(state_dir)
    try:
        request = PerceptionReacquisitionRequest(
            **store.get_payload(
                "perception_reacquisition_requests",
                request_id,
            )
        )
    except KeyError:
        _human("Reacquisition request was not found.")
        return _print_json({"status": "request_not_found"}, exit_code=1)
    action = next(
        (
            item
            for item in reversed(
                store.list_payloads(
                    "bounded_reacquisition_internal_actions"
                )
            )
            if request.reacquisition_request_id
            in tuple(item.get("source_record_refs") or ())
        ),
        None,
    )
    started = bool(
        action
        and any(
            item.get("internal_action_id") == action.get("internal_action_id")
            for item in store.list_payloads(
                "reacquisition_capture_executions"
            )
        )
    )
    cancellation = cancel_pending_reacquisition(
        request=request,
        target_internal_action_id=(
            str(action.get("internal_action_id")) if action else None
        ),
        child_capture_started=started,
    )
    store.append_record("reacquisition_cancellations", cancellation)
    _human(
        "Pending reacquisition was cancelled."
        if cancellation.cancellation_succeeded
        else "Child capture already started; use stop-child-window."
    )
    return _print_json(
        cancellation.to_dict(),
        exit_code=0 if cancellation.cancellation_succeeded else 1,
    )


def _stop_child(state_dir: str, child_window_id: str) -> int:
    store = Package126ReacquisitionStore(state_dir)
    child = next(
        (
            item
            for item in reversed(store.list_payloads("observation_window_states"))
            if item.get("observation_window_id") == child_window_id
        ),
        None,
    )
    if child is None:
        _human("Child observation window was not found.")
        return _print_json({"status": "child_window_not_found"}, exit_code=1)
    record = {
        "cancellation_id": stable_id("reacquisition_child_stop"),
        "schema_version": "ashl_package_126_reacquisition_cancellation_v0",
        "created_at": utc_now(),
        "target_request_id": "completed_or_active_child",
        "target_internal_action_id": None,
        "requested_by": "local_operator",
        "reason": "operator_stop_child_observation",
        "cancellation_succeeded": False,
        "child_capture_started": True,
        "source_record_refs": (child_window_id,),
        "source_trace_refs": tuple(),
    }
    store.append_payload(
        "reacquisition_cancellations",
        "cancellation_id",
        record["cancellation_id"],
        record,
    )
    _human(
        "Operator stop was recorded append-only; completed history was not rewritten."
    )
    return _print_json(
        {
            "status": "operator_stop_recorded",
            "child_window_id": child_window_id,
            "history_rewritten": False,
            "record": record,
        }
    )


def _show_chain(state_dir: str, parent_window_id: str) -> int:
    store = Package126ReacquisitionStore(state_dir)
    payload = _chain_payload(store, parent_window_id)
    _human("Showing append-only Package 126 parent/child chain.")
    return _print_json(payload)


def _chain_payload(
    store: Package126ReacquisitionStore,
    parent_window_id: str,
) -> dict[str, object]:
    parent_refs = tuple(
        item
        for item in store.list_payloads("completed_parent_window_refs")
        if item.get("observation_window_id") == parent_window_id
    )
    parent_ref_ids = {
        str(item.get("completed_window_reference_id")) for item in parent_refs
    }
    requests = tuple(
        item
        for item in store.list_payloads("perception_reacquisition_requests")
        if item.get("parent_window_reference_id") in parent_ref_ids
    )
    request_ids = {
        str(item.get("reacquisition_request_id")) for item in requests
    }
    decisions = tuple(
        item
        for item in store.list_payloads("reacquisition_eligibility_decisions")
        if item.get("reacquisition_request_id") in request_ids
    )
    executions = tuple(
        item
        for item in store.list_payloads("reacquisition_capture_executions")
        if item.get("parent_observation_window_id") == parent_window_id
    )
    child_ids = {
        str(item.get("child_observation_window_id")) for item in executions
    }
    return {
        "parent_window_refs": parent_refs,
        "requests": requests,
        "decisions": decisions,
        "actions": tuple(
            item
            for item in store.list_payloads(
                "bounded_reacquisition_internal_actions"
            )
            if item.get("parent_observation_window_id") == parent_window_id
        ),
        "executions": executions,
        "child_windows": tuple(
            item
            for item in store.list_payloads("observation_window_states")
            if item.get("observation_window_id") in child_ids
        ),
        "temporal_links": tuple(
            item
            for item in store.list_payloads("cross_window_temporal_links")
            if item.get("parent_observation_window_id") == parent_window_id
        ),
    }


def _show_deletion(state_dir: str, child_window_id: str) -> int:
    store = Package126ReacquisitionStore(state_dir)
    records = tuple(
        item
        for item in store.list_payloads(
            "ephemeral_audio_deletion_verifications"
        )
        if item.get("child_observation_window_id") == child_window_id
    )
    _human(
        "Raw audio deletion is verified."
        if records and records[-1].get("deletion_verified")
        else "No verified audio deletion record was found."
    )
    return _print_json(
        {"child_window_id": child_window_id, "deletion_records": records},
        exit_code=0
        if records and records[-1].get("deletion_verified")
        else 1,
    )


def _human(text: str) -> None:
    print(text)


def _print_json(payload: Any, *, exit_code: int = 0) -> int:
    print(json.dumps(plain(payload), indent=2, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
