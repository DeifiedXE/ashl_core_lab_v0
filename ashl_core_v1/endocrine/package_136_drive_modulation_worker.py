"""Fresh-process worker entrypoint for Package 136."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.endocrine.drive_modulation_runtime import (
    run_drive_modulation_worker,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Package 136 internal worker")
    parser.add_argument("--ashl-root", required=True)
    parser.add_argument("--package-133-state-dir", required=True)
    parser.add_argument("--package-134-state-dir", required=True)
    parser.add_argument("--package-135-state-dir", required=True)
    parser.add_argument("--state-dir", required=True)
    parser.add_argument(
        "--process-role",
        required=True,
        choices=("modulated_session_a", "neutral_session_b"),
    )
    parser.add_argument("--process-instance-id", required=True)
    parser.add_argument("--authorization-id")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = run_drive_modulation_worker(
        ashl_root=args.ashl_root,
        package_133_state_dir=args.package_133_state_dir,
        package_134_state_dir=args.package_134_state_dir,
        package_135_state_dir=args.package_135_state_dir,
        state_dir=args.state_dir,
        process_role=args.process_role,
        process_instance_id=args.process_instance_id,
        authorization_id=args.authorization_id,
    )
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
