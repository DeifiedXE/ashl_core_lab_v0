"""Fresh-process worker for one bounded Package 138 readback attempt."""

from __future__ import annotations

import argparse
import json
from typing import Sequence

from ashl_core_v1.runtime.host_sensor_types import plain
from ashl_core_v1.state.self_state_readback_runtime import (
    run_recovered_session_readback_worker,
    run_self_state_readback_worker,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ashl-root", required=True)
    parser.add_argument("--package-133-state-dir", required=True)
    parser.add_argument("--package-134-state-dir", required=True)
    parser.add_argument("--package-137-state-dir", required=True)
    parser.add_argument("--state-dir", required=True)
    parser.add_argument("--process-role", required=True)
    parser.add_argument("--runtime-session-id", required=True)
    parser.add_argument("--process-instance-id", required=True)
    parser.add_argument("--authorization-id")
    parser.add_argument("--recovery-authorization-id")
    parser.add_argument("--recover-before-readback", action="store_true")
    parser.add_argument("--probe-missing-authorization", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.recover_before_readback:
        if not args.recovery_authorization_id:
            parser.error("--recovery-authorization-id is required")
        result = run_recovered_session_readback_worker(
            ashl_root=args.ashl_root,
            package_133_state_dir=args.package_133_state_dir,
            package_134_state_dir=args.package_134_state_dir,
            package_137_state_dir=args.package_137_state_dir,
            state_dir=args.state_dir,
            recovery_authorization_id=args.recovery_authorization_id,
            runtime_session_id=args.runtime_session_id,
            process_instance_id=args.process_instance_id,
            process_role=args.process_role,
            probe_missing_authorization=args.probe_missing_authorization,
        )
    else:
        result = run_self_state_readback_worker(
            ashl_root=args.ashl_root,
            package_133_state_dir=args.package_133_state_dir,
            package_134_state_dir=args.package_134_state_dir,
            package_137_state_dir=args.package_137_state_dir,
            state_dir=args.state_dir,
            process_role=args.process_role,
            runtime_session_id=args.runtime_session_id,
            process_instance_id=args.process_instance_id,
            authorization_id=args.authorization_id,
        )
    print(json.dumps(plain(result), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
