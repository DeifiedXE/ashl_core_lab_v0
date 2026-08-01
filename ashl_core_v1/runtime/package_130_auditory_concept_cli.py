"""Human-first operator CLI for Package 130."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import plain
from ashl_core_v1.runtime.package_130_auditory_concept_audit import (
    audit_package_130_grounded_auditory_concept,
)
from ashl_core_v1.runtime.package_130_auditory_concept_preflight import (
    run_package_130_preflight,
)
from ashl_core_v1.runtime.package_130_auditory_concept_runtime import (
    assign_grounding_examples,
    build_concept_candidate,
    delete_grounding_audio,
    review_concept,
)
from ashl_core_v1.runtime.package_130_auditory_concept_store import (
    Package130AuditoryConceptStore,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Package 130 grounded anonymous auditory event concept"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    preflight = sub.add_parser("preflight")
    preflight.add_argument("--state-dir", required=True)
    preflight.add_argument("--render-endpoint", default="default")
    preflight.add_argument("--ashl-root")
    preflight.add_argument("--require-clean-tree", action="store_true")

    for name in ("run-grounding-set-a", "run-grounding-set-b"):
        command = sub.add_parser(name)
        command.add_argument("--state-dir", required=True)
        command.add_argument("--render-endpoint", default="default")
        command.add_argument("--allow-grounding-capture", action="store_true")

    for name in (
        "show-episodes",
        "build-concept-candidate",
        "show-predictive-validation",
        "show-teacher-review",
        "show-concept-model",
        "show-deletion-audit",
        "audit",
    ):
        command = sub.add_parser(name)
        command.add_argument("--state-dir", required=True)

    assignment = sub.add_parser("assign-grounding-examples")
    assignment.add_argument("--state-dir", required=True)
    assignment.add_argument("--positive", required=True)
    assignment.add_argument("--contrast", required=True)
    assignment.add_argument("--confirm", action="store_true")

    review = sub.add_parser("review-concept")
    review.add_argument("--state-dir", required=True)
    review.add_argument(
        "--decision",
        choices=("approve", "reject", "defer"),
        required=True,
    )
    review.add_argument("--reviewer", required=True)
    review.add_argument("--expected-evidence-identity", required=True)
    review.add_argument("--confirm", action="store_true")

    deletion = sub.add_parser("delete-grounding-audio")
    deletion.add_argument("--state-dir", required=True)
    deletion.add_argument("--confirm", action="store_true")

    guided = sub.add_parser("guided-run")
    guided.add_argument("--state-dir", required=True)
    guided.add_argument("--render-endpoint", default="default")
    guided.add_argument("--allow-grounding-capture", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return _dispatch(args)
    except Exception as error:
        _human(
            f"Package 130 command was blocked: {type(error).__name__}: {error}"
        )
        return _print_json(
            {
                "status": "blocked_package_130_command",
                "command": args.command,
                "exception_kind": type(error).__name__,
                "reason": str(error),
            },
            exit_code=1,
        )


def _dispatch(args: argparse.Namespace) -> int:
    if args.command == "preflight":
        _human("Checking Package 130 baseline, external state, and WASAPI loopback.")
        result = run_package_130_preflight(
            state_dir=args.state_dir,
            render_endpoint=args.render_endpoint,
            ashl_root=args.ashl_root,
            require_clean_tree=args.require_clean_tree,
        )
        return _print_json(
            result,
            exit_code=0 if result["preflight_status"] == "passed" else 1,
        )
    if args.command in {"run-grounding-set-a", "run-grounding-set-b"}:
        if not args.allow_grounding_capture:
            _human("Real grounding capture requires --allow-grounding-capture.")
            return _print_json(
                {
                    "status": "blocked_grounding_capture_authorization_missing",
                    "grounding_capture_started": False,
                },
                exit_code=1,
            )
        set_name = "A" if args.command.endswith("-a") else "B"
        _human(
            f"Starting real grounding set {set_name} in an isolated OS process."
        )
        result, code = _run_grounding_worker(
            state_dir=args.state_dir,
            set_name=set_name,
            render_endpoint=args.render_endpoint,
        )
        _human(
            f"Grounding set {set_name} completed with fresh capture sessions."
            if code == 0
            else f"Grounding set {set_name} was blocked; details follow."
        )
        return _print_json(result, exit_code=code)

    store = Package130AuditoryConceptStore(args.state_dir)
    if args.command == "show-episodes":
        _human("Showing captured episode identities and audit-only fixture slots.")
        return _print_json(_episode_inventory(store))
    if args.command == "assign-grounding-examples":
        _human("Recording the explicit teacher assignment of positives and contrasts.")
        assignment = assign_grounding_examples(
            state_dir=args.state_dir,
            positive_episode_refs=_csv_refs(args.positive),
            contrast_episode_refs=_csv_refs(args.contrast),
            confirm=args.confirm,
        )
        return _print_json(assignment.to_dict())
    if args.command == "build-concept-candidate":
        _human(
            "Building one anonymous candidate and deterministic grounding-corpus validation."
        )
        result = build_concept_candidate(state_dir=args.state_dir)
        _human("Candidate construction stopped at the exact teacher-review gate.")
        return _print_json(result)
    if args.command == "show-predictive-validation":
        _human("Showing leave-one-positive-out and contrast validation evidence.")
        return _print_json(
            store.latest_payload("auditory_concept_predictive_validations")
            or {"status": "no_predictive_validation"}
        )
    if args.command == "show-teacher-review":
        _human("Showing the exact evidence identity awaiting teacher review.")
        return _print_json(_teacher_review_payload(store))
    if args.command == "review-concept":
        _human("Applying an explicit exact-evidence teacher decision.")
        result = review_concept(
            state_dir=args.state_dir,
            decision=args.decision,
            reviewer=args.reviewer,
            expected_evidence_identity=args.expected_evidence_identity,
            confirm=args.confirm,
        )
        if result.get("model"):
            _human(
                "The reviewed model is inactive until all grounding waveform blobs are deleted."
            )
        return _print_json(result)
    if args.command == "delete-grounding-audio":
        _human(
            "Deleting the seven authorized grounding waveforms while preserving primitive evidence."
        )
        result = delete_grounding_audio(
            state_dir=args.state_dir,
            confirm=args.confirm,
        )
        cleanup = result.get("cleanup_record") or {}
        cleanup_complete = (
            cleanup.get("raw_blob_count_after_deletion") == 0
            and cleanup.get("failed_deletion_count") == 0
        )
        return _print_json(
            result,
            exit_code=0 if result.get("model_activated") or cleanup_complete else 1,
        )
    if args.command == "show-concept-model":
        _human("Showing append-only auditory concept model states.")
        models = store.list_payloads("grounded_auditory_event_concept_models")
        return _print_json(
            {"status": "concept_models_found" if models else "no_concept_model", "models": models}
        )
    if args.command == "show-deletion-audit":
        _human("Showing grounding waveform deletion and activation status.")
        return _print_json(
            store.latest_payload("auditory_grounding_raw_audio_deletion_audits")
            or {"status": "no_grounding_deletion_audit"}
        )
    if args.command == "audit":
        audit = audit_package_130_grounded_auditory_concept(
            state_dir=args.state_dir,
            append=True,
        )
        passed = audit.audit_status.startswith("passed_")
        _human(
            "Package 130 grounded anonymous auditory concept audit passed."
            if passed
            else "Package 130 audit is blocked; failure reasons follow."
        )
        return _print_json(audit.to_dict(), exit_code=0 if passed else 1)
    if args.command == "guided-run":
        return _guided_run(args, store)
    raise SystemExit(f"unknown command: {args.command}")


def _guided_run(
    args: argparse.Namespace,
    store: Package130AuditoryConceptStore,
) -> int:
    completed_sets = {
        str(item.get("grounding_set_name"))
        for item in store.list_payloads("auditory_grounding_process_receipts")
        if item.get("receipt_status") == "completed"
    }
    if "A" not in completed_sets:
        preflight = run_package_130_preflight(
            state_dir=args.state_dir,
            render_endpoint=args.render_endpoint,
        )
        if preflight["preflight_status"] != "passed":
            _human("Guided preflight was blocked.")
            return _print_json(preflight, exit_code=1)
        if not args.allow_grounding_capture:
            _human("Guided real capture requires --allow-grounding-capture.")
            return _print_json(
                {"status": "blocked_grounding_capture_authorization_missing"},
                exit_code=1,
            )
        _human("Guided preflight passed. Capturing grounding set A now.")
        result, code = _run_grounding_worker(
            state_dir=args.state_dir,
            set_name="A",
            render_endpoint=args.render_endpoint,
        )
        if code != 0:
            return _print_json(result, exit_code=code)
        next_command = _set_command(
            args.state_dir,
            "B",
            args.render_endpoint,
        )
        _human("Set A is complete. This process stops here; run set B with:")
        _human(next_command)
        return _print_json(
            {**result, "guided_run_terminated": True, "next_command": next_command}
        )
    if "B" not in completed_sets:
        _human("Set A exists. Set B must run through its own isolated worker command:")
        command = _set_command(args.state_dir, "B", args.render_endpoint)
        _human(command)
        return _print_json(
            {"status": "waiting_for_grounding_set_b", "next_command": command}
        )

    assignment = store.latest_payload("auditory_grounding_example_assignments")
    if assignment is None:
        inventory = _episode_inventory(store)
        command = _assignment_command(args.state_dir, inventory)
        _human("Both real sets are complete. Explicit example assignment is required:")
        _human(command)
        return _print_json(
            {
                **inventory,
                "status": "waiting_for_explicit_grounding_assignment",
                "next_command": command,
            }
        )
    candidate = store.latest_payload("grounded_auditory_concept_candidates")
    if candidate is None:
        result = build_concept_candidate(state_dir=args.state_dir)
        target = dict(result["teacher_review"])
        commands = _review_commands(
            args.state_dir,
            str(target["evidence_identity_hash"]),
        )
        _human("Predictive validation is complete. Exact teacher review is required:")
        for command in commands.values():
            _human(command)
        return _print_json(
            {**result, "guided_run_terminated": True, "review_commands": commands}
        )
    outcome = store.latest_payload("auditory_concept_teacher_review_outcomes")
    if outcome is None:
        target = store.latest_payload("auditory_concept_teacher_review_targets") or {}
        commands = _review_commands(
            args.state_dir,
            str(target.get("evidence_identity_hash", "missing")),
        )
        _human("The candidate is waiting for exact teacher review:")
        for command in commands.values():
            _human(command)
        return _print_json(
            {**_teacher_review_payload(store), "review_commands": commands}
        )
    if outcome.get("decision") != "approved":
        _human("Teacher review did not approve a model; no activation is available.")
        return _print_json(
            {"status": f"teacher_{outcome.get('decision')}_no_model_activation", "outcome": outcome}
        )
    deletion = store.latest_payload("auditory_grounding_raw_audio_deletion_audits")
    if deletion is None or not deletion.get("model_activation_allowed"):
        command = _deletion_command(args.state_dir)
        _human("Teacher approval is committed. Raw-audio deletion is now required:")
        _human(command)
        return _print_json(
            {"status": "waiting_for_grounding_audio_deletion", "next_command": command}
        )
    _human("The model is deletion-cleared and ready for the Package 130 audit.")
    return _print_json(
        {
            "status": "ready_for_package_130_audit",
            "next_command": _audit_command(args.state_dir),
        }
    )


def _run_grounding_worker(
    *,
    state_dir: str | Path,
    set_name: str,
    render_endpoint: str,
) -> tuple[dict[str, Any], int]:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ashl_core_v1.runtime.package_130_auditory_concept_worker",
            "--state-dir",
            str(state_dir),
            "--set-name",
            set_name,
            "--render-endpoint",
            render_endpoint,
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    try:
        payload = json.loads(result.stdout.strip())
    except json.JSONDecodeError:
        payload = {
            "status": f"blocked_grounding_set_{set_name.lower()}",
            "reason": result.stdout.strip() or result.stderr.strip() or "worker returned no result",
        }
    if result.stderr.strip():
        payload.setdefault("worker_stderr", result.stderr.strip())
    return payload, result.returncode


def _episode_inventory(store: Package130AuditoryConceptStore) -> dict[str, Any]:
    episodes = store.list_payloads("auditory_grounding_episodes")
    manifests = {
        str(item["episode_id"]): item
        for item in store.list_payloads("auditory_grounding_fixture_manifests")
    }
    items = tuple(
        {
            "episode_id": item["episode_id"],
            "grounding_run_id": item["grounding_run_id"],
            "process_instance_id": item["process_instance_id"],
            "operating_system_process_id": item["operating_system_process_id"],
            "audio_capture_session_id": item["audio_capture_session_id"],
            "fixture_slot_audit_only": manifests.get(str(item["episode_id"]), {}).get("fixture_slot"),
            "semantic_label": item.get("semantic_label"),
        }
        for item in episodes
    )
    return {
        "status": "grounding_episodes_found" if items else "no_grounding_episodes",
        "episode_count": len(items),
        "episodes": items,
    }


def _teacher_review_payload(store: Package130AuditoryConceptStore) -> dict[str, Any]:
    target = store.latest_payload("auditory_concept_teacher_review_targets")
    outcomes = store.list_payloads("auditory_concept_teacher_review_outcomes")
    return {
        "status": (
            "teacher_review_resolved"
            if outcomes
            else "auditory_concept_waiting_teacher_review"
            if target
            else "no_teacher_review_target"
        ),
        "target": target,
        "outcomes": outcomes,
    }


def _csv_refs(value: str) -> tuple[str, ...]:
    refs = tuple(item.strip() for item in value.split(",") if item.strip())
    if not refs:
        raise ValueError("at least one episode reference is required")
    return refs


def _assignment_command(state_dir: str | Path, inventory: dict[str, Any]) -> str:
    positives = [
        str(item["episode_id"])
        for item in inventory["episodes"]
        if str(item.get("fixture_slot_audit_only", "")).startswith("P")
    ]
    contrasts = [
        str(item["episode_id"])
        for item in inventory["episodes"]
        if str(item.get("fixture_slot_audit_only", "")).startswith("C")
    ]
    return (
        "py -3 -m ashl_core_v1.runtime.package_130_auditory_concept_cli "
        f"assign-grounding-examples --state-dir \"{state_dir}\" "
        f"--positive {','.join(positives)} --contrast {','.join(contrasts)} --confirm"
    )


def _review_commands(state_dir: str | Path, identity: str) -> dict[str, str]:
    prefix = (
        "py -3 -m ashl_core_v1.runtime.package_130_auditory_concept_cli "
        f"review-concept --state-dir \"{state_dir}\" "
    )
    return {
        decision: (
            f"{prefix}--decision {decision} --reviewer local_teacher "
            f"--expected-evidence-identity {identity} --confirm"
        )
        for decision in ("approve", "reject", "defer")
    }


def _set_command(state_dir: str | Path, set_name: str, endpoint: str) -> str:
    return (
        "py -3 -m ashl_core_v1.runtime.package_130_auditory_concept_cli "
        f"run-grounding-set-{set_name.lower()} --state-dir \"{state_dir}\" "
        f"--render-endpoint {endpoint} --allow-grounding-capture"
    )


def _deletion_command(state_dir: str | Path) -> str:
    return (
        "py -3 -m ashl_core_v1.runtime.package_130_auditory_concept_cli "
        f"delete-grounding-audio --state-dir \"{state_dir}\" --confirm"
    )


def _audit_command(state_dir: str | Path) -> str:
    return (
        "py -3 -m ashl_core_v1.runtime.package_130_auditory_concept_cli "
        f"audit --state-dir \"{state_dir}\""
    )


def _human(message: str) -> None:
    print(message)


def _print_json(payload: Any, *, exit_code: int = 0) -> int:
    print(json.dumps(plain(payload), ensure_ascii=False, indent=2, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
