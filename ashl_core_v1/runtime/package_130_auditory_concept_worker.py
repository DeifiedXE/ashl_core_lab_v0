"""Fresh-process grounding-set worker for Package 130."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.runtime.host_sensor_types import plain
from ashl_core_v1.runtime.package_130_auditory_concept_runtime import (
    run_grounding_set,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Package 130 isolated real grounding-set worker"
    )
    parser.add_argument("--state-dir", required=True)
    parser.add_argument("--set-name", choices=("A", "B"), required=True)
    parser.add_argument("--render-endpoint", default="default")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        payload = run_grounding_set(
            state_dir=args.state_dir,
            set_name=args.set_name,
            render_endpoint=args.render_endpoint,
            allow_grounding_capture=True,
        )
        exit_code = 0
    except Exception as error:
        payload = {
            "status": f"blocked_grounding_set_{args.set_name.lower()}",
            "grounding_set_name": args.set_name,
            "exception_kind": type(error).__name__,
            "reason": str(error),
        }
        exit_code = 1
    print(
        json.dumps(
            plain(payload),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
