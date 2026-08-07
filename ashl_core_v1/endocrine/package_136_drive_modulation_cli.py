"""CLI for Package 136 same-session drive modulation infrastructure."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.endocrine.drive_modulation_runtime import (
    preflight_same_session_drive_modulation,
    run_real_same_session_drive_modulation,
)
from ashl_core_v1.endocrine.package_136_drive_modulation_audit import (
    audit_package_136_same_session_drive_modulation,
    run_package_136_regressions,
)
from ashl_core_v1.endocrine.package_136_drive_modulation_controls import (
    run_package_136_drive_modulation_controls,
)
from ashl_core_v1.endocrine.package_136_drive_modulation_store import (
    Package136DriveModulationStore,
    package_136_store_path,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Package 136 bounded same-session drive modulation"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("preflight", "run-real-counterfactual", "guided-run", "audit"):
        command = subparsers.add_parser(name)
        _add_source_arguments(command)
        if name in {"run-real-counterfactual", "guided-run"}:
            command.add_argument(
                "--allow-same-session-drive-modulation", action="store_true"
            )
    controls = subparsers.add_parser("run-controls")
    _add_source_arguments(controls, include_ashl_root=False)
    regressions = subparsers.add_parser("run-regressions")
    regressions.add_argument("--ashl-root", required=True)
    regressions.add_argument("--state-dir", required=True)
    for name in (
        "show-consumer-inventory",
        "show-allowlist",
        "show-authorization",
        "show-applications",
        "show-counterfactual",
        "show-cross-session-neutrality",
        "show-audit",
    ):
        command = subparsers.add_parser(name)
        command.add_argument("--state-dir", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "preflight":
            result = preflight_same_session_drive_modulation(**_source_kwargs(args))
            return _print(
                "Package 136 preflight: production allowlist is empty; audit-only infrastructure is ready.",
                result,
            )
        if args.command == "run-real-counterfactual":
            result = run_real_same_session_drive_modulation(
                **_source_kwargs(args),
                allow_same_session_drive_modulation=args.allow_same_session_drive_modulation,
            )
            return _print(
                "Package 136 counterfactual completed; same-session offset expired to neutral.",
                result,
            )
        if args.command == "run-controls":
            result = run_package_136_drive_modulation_controls(
                package_133_state_dir=args.package_133_state_dir,
                package_134_state_dir=args.package_134_state_dir,
                package_135_state_dir=args.package_135_state_dir,
                state_dir=args.state_dir,
            )
            _print("Package 136 fail-neutral controls:", result.to_dict())
            return 0 if result.controls_passed else 2
        if args.command == "run-regressions":
            result = run_package_136_regressions(
                ashl_root=args.ashl_root, state_dir=args.state_dir
            )
            _print("Package 136 fresh regression receipt:", result.to_dict())
            return 0 if result.fresh_regressions_passed else 2
        if args.command == "audit":
            result = audit_package_136_same_session_drive_modulation(
                **_source_kwargs(args)
            )
            _print(
                (
                    "Package 136 audit passed; production consumer allowlist remains empty."
                    if result.audit_status.startswith("passed_")
                    else "Package 136 audit blocked."
                ),
                result.to_dict(),
            )
            return 0 if result.audit_status.startswith("passed_") else 2
        if args.command == "guided-run":
            preflight = preflight_same_session_drive_modulation(**_source_kwargs(args))
            run = run_real_same_session_drive_modulation(
                **_source_kwargs(args),
                allow_same_session_drive_modulation=args.allow_same_session_drive_modulation,
            )
            controls = run_package_136_drive_modulation_controls(
                package_133_state_dir=args.package_133_state_dir,
                package_134_state_dir=args.package_134_state_dir,
                package_135_state_dir=args.package_135_state_dir,
                state_dir=args.state_dir,
            )
            regressions = run_package_136_regressions(
                ashl_root=args.ashl_root, state_dir=args.state_dir
            )
            audit = audit_package_136_same_session_drive_modulation(
                **_source_kwargs(args)
            )
            _print(
                "Package 136 guided run completed; no production runtime consumer was created.",
                {
                    "preflight": preflight,
                    "run": run,
                    "controls": controls.to_dict(),
                    "regressions": regressions.to_dict(),
                    "audit": audit.to_dict(),
                },
            )
            return 0 if audit.audit_status.startswith("passed_") else 2
        _require_store(args.state_dir)
        store = Package136DriveModulationStore(args.state_dir)
        table_by_command = {
            "show-consumer-inventory": "drive_modulation_consumer_inventory",
            "show-allowlist": "drive_modulation_consumer_allowlists",
            "show-authorization": "same_session_drive_modulation_authorizations",
            "show-applications": "drive_modulation_applications",
            "show-counterfactual": "drive_modulation_counterfactual_comparisons",
            "show-cross-session-neutrality": "drive_modulation_cross_session_neutrality",
            "show-audit": "package_136_audits",
        }
        table = table_by_command[args.command]
        payloads = store.list_payloads(table)
        return _print(f"Package 136 {args.command.replace('-', ' ')}:", payloads)
    except (FileNotFoundError, KeyError, RuntimeError, TypeError, ValueError) as error:
        print(f"Package 136 blocked: {error}")
        return 2


def _add_source_arguments(
    parser: argparse.ArgumentParser, *, include_ashl_root: bool = True
) -> None:
    if include_ashl_root:
        parser.add_argument("--ashl-root", required=True)
    parser.add_argument("--package-133-state-dir", required=True)
    parser.add_argument("--package-134-state-dir", required=True)
    parser.add_argument("--package-135-state-dir", required=True)
    parser.add_argument("--state-dir", required=True)


def _source_kwargs(args: argparse.Namespace) -> dict[str, str]:
    return {
        "ashl_root": args.ashl_root,
        "package_133_state_dir": args.package_133_state_dir,
        "package_134_state_dir": args.package_134_state_dir,
        "package_135_state_dir": args.package_135_state_dir,
        "state_dir": args.state_dir,
    }


def _require_store(state_dir: str | Path) -> None:
    if not package_136_store_path(state_dir).is_file():
        raise FileNotFoundError(package_136_store_path(state_dir))


def _print(label: str, payload: object) -> int:
    print(label)
    print(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
