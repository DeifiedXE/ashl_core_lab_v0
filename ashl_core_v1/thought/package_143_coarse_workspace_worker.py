"""Fresh-process empty-workspace proof worker for Package 143."""

from __future__ import annotations

import argparse
import json

from ashl_core_v1.runtime.host_sensor_types import monotonic_ns
from ashl_core_v1.runtime.local_operator_console_store import LocalOperatorConsoleStore
from ashl_core_v1.runtime.local_operator_event_stream import LocalOperatorEventStream
from ashl_core_v1.thought.package_143_coarse_workspace_runtime import (
    load_package_143_preflight,
    open_ephemeral_workspace,
)
from ashl_core_v1.thought.package_143_coarse_workspace_store import (
    Package143CoarseWorkspaceStore,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Package 143 fresh-process worker")
    parser.add_argument("--ashl-root", required=True)
    parser.add_argument("--state-dir", required=True)
    parser.add_argument("--package-142-state-dir", required=True)
    parser.add_argument("--package-141-state-dir", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    preflight = load_package_143_preflight(
        ashl_root=args.ashl_root,
        package_142_state_dir=args.package_142_state_dir,
        package_141_state_dir=args.package_141_state_dir,
        state_dir=args.state_dir,
        append=True,
    )
    store = Package143CoarseWorkspaceStore(args.state_dir)
    stream = LocalOperatorEventStream(LocalOperatorConsoleStore(args.state_dir))
    opened = monotonic_ns()
    workspace = open_ephemeral_workspace(
        preflight,
        opened_at_monotonic_ns=opened,
        store=store,
        event_stream=stream,
    )
    closure = workspace.close(closed_at_monotonic_ns=opened + 1)
    print(
        json.dumps(
            {
                "process_instance_id": workspace.session.process_instance_id,
                "operating_system_process_id": workspace.session.operating_system_process_id,
                "workspace_session_id": workspace.session.workspace_session_id,
                "initial_entry_count": workspace.session.initial_entry_count,
                "recovered_entry_count": workspace.session.recovered_entry_count,
                "fresh_process_empty": workspace.session.fresh_process_empty,
                "closure_id": closure.closure.closure_id,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
