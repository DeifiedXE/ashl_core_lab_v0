"""One-process worker for a single fresh Package 131 recognition probe."""

from __future__ import annotations

import argparse
import json
import sys

from ashl_core_v1.runtime.host_sensor_types import canonical_json
from ashl_core_v1.runtime.package_131_auditory_predictive_recognition_runtime import (
    run_real_recognition_probe,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", required=True)
    parser.add_argument("--probe-slot", required=True, choices=("A", "B"))
    parser.add_argument("--render-endpoint", default="default")
    parser.add_argument("--model-id")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = run_real_recognition_probe(
            state_dir=args.state_dir,
            probe_slot=args.probe_slot,
            render_endpoint=args.render_endpoint,
            model_id=args.model_id,
            strict_event_stream=True,
        )
    except Exception as error:
        print(f"{type(error).__name__}: {error}", file=sys.stderr)
        return 1
    print(canonical_json(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
