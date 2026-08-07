"""Fresh-process worker for one exact Package 137 reviewed successor commit."""

from __future__ import annotations

import argparse
import json
from typing import Sequence

from ashl_core_v1.runtime.host_sensor_types import plain
from ashl_core_v1.state.persistent_self_state_review_runtime import (
    commit_approved_self_state_successor,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ashl-root", required=True)
    parser.add_argument("--package-133-state-dir", required=True)
    parser.add_argument("--package-134-state-dir", required=True)
    parser.add_argument("--state-dir", required=True)
    parser.add_argument("--review-id", required=True)
    parser.add_argument("--process-instance-id", required=True)
    parser.add_argument("--allow-self-state-mutation", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = commit_approved_self_state_successor(
        ashl_root=args.ashl_root,
        package_133_state_dir=args.package_133_state_dir,
        package_134_state_dir=args.package_134_state_dir,
        state_dir=args.state_dir,
        review_id=args.review_id,
        process_instance_id=args.process_instance_id,
        allow_self_state_mutation=args.allow_self_state_mutation,
    )
    print(json.dumps(plain(result), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
