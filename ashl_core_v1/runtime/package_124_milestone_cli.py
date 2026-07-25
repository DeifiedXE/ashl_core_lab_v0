"""CLI for Package 124 real host perception milestone audit/archive."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.host_sensor_types import plain
from ashl_core_v1.runtime.package_124_archive import (
    BOUNDARY_REPORT_FILENAME,
    PROVENANCE_FILENAME,
    create_package_124_archive,
    verify_package_124_archive,
)
from ashl_core_v1.runtime.package_124_archive_manifest import verify_archive_manifest
from ashl_core_v1.runtime.package_124_milestone_certificate import (
    load_package_124_certificate,
    validate_package_124_certificate,
)
from ashl_core_v1.runtime.package_124_source_audit import audit_package_124_source, inspect_package_124_source
from ashl_core_v1.runtime.package_124_types import (
    PACKAGE_123_CYCLE_1_EVIDENCE_IDENTITY,
    PACKAGE_123_CYCLE_2_SESSION_ID,
    PACKAGE_123_SOURCE_COMMIT,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Package 124 real host perception milestone audit/archive")
    sub = parser.add_subparsers(dest="command", required=True)

    inspect = sub.add_parser("inspect-source")
    inspect.add_argument("--state-dir", required=True)
    inspect.add_argument("--expected-commit", default=PACKAGE_123_SOURCE_COMMIT)

    audit = sub.add_parser("audit-source")
    audit.add_argument("--state-dir", required=True)
    audit.add_argument("--expected-commit", default=PACKAGE_123_SOURCE_COMMIT)
    audit.add_argument("--expected-cycle-1-evidence-identity", default=PACKAGE_123_CYCLE_1_EVIDENCE_IDENTITY)
    audit.add_argument("--expected-cycle-2-session", default=PACKAGE_123_CYCLE_2_SESSION_ID)

    create = sub.add_parser("create-archive")
    create.add_argument("--state-dir", required=True)
    create.add_argument("--archive-root", required=True)
    create.add_argument("--expected-commit", default=PACKAGE_123_SOURCE_COMMIT)
    create.add_argument("--confirm", action="store_true")

    verify = sub.add_parser("verify-archive")
    verify.add_argument("--archive-dir", required=True)

    certify = sub.add_parser("certify")
    certify.add_argument("--archive-dir", required=True)
    certify.add_argument("--confirm", action="store_true")

    show_certificate = sub.add_parser("show-certificate")
    show_certificate.add_argument("--archive-dir", required=True)

    show_provenance = sub.add_parser("show-provenance")
    show_provenance.add_argument("--archive-dir", required=True)

    show_boundaries = sub.add_parser("show-boundaries")
    show_boundaries.add_argument("--archive-dir", required=True)

    guided = sub.add_parser("audit-archive-and-certify")
    guided.add_argument("--state-dir", required=True)
    guided.add_argument("--archive-root", required=True)
    guided.add_argument("--expected-commit", default=PACKAGE_123_SOURCE_COMMIT)
    guided.add_argument("--confirm", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "inspect-source":
        return _print_json(inspect_package_124_source(args.state_dir, expected_commit=args.expected_commit))
    if args.command == "audit-source":
        return _print_json(
            audit_package_124_source(
                args.state_dir,
                expected_commit=args.expected_commit,
                expected_cycle_1_evidence_identity=args.expected_cycle_1_evidence_identity,
                expected_cycle_2_session=args.expected_cycle_2_session,
            )
        )
    if args.command == "create-archive":
        return _print_json(
            create_package_124_archive(
                state_dir=args.state_dir,
                archive_root=args.archive_root,
                expected_commit=args.expected_commit,
                confirm=args.confirm,
            )
        )
    if args.command == "verify-archive":
        return _print_json(verify_package_124_archive(args.archive_dir))
    if args.command == "certify":
        if not args.confirm:
            raise SystemExit("--confirm is required")
        verification = verify_package_124_archive(args.archive_dir)
        if not verification.get("valid"):
            raise SystemExit("archive verification failed; no certificate action performed")
        return _print_json({"status": "certificate_already_issued_and_valid", "verification": verification})
    if args.command == "show-certificate":
        certificate = load_package_124_certificate(args.archive_dir)
        validation = validate_package_124_certificate(args.archive_dir)
        return _print_json({"certificate": certificate.to_dict(), "validation": validation})
    if args.command == "show-provenance":
        return _print_json(_load_archive_json(args.archive_dir, PROVENANCE_FILENAME))
    if args.command == "show-boundaries":
        path = Path(args.archive_dir) / BOUNDARY_REPORT_FILENAME
        print(path.read_text(encoding="utf-8"))
        return 0
    if args.command == "audit-archive-and-certify":
        result = create_package_124_archive(
            state_dir=args.state_dir,
            archive_root=args.archive_root,
            expected_commit=args.expected_commit,
            confirm=args.confirm,
        )
        if result.get("status") != "certified_real_host_perception_growth_loop_v0":
            return _print_json(result)
        verification = verify_package_124_archive(str(result["archive_dir"]))
        result["post_create_archive_verification"] = verification
        result["archive_manifest"] = verify_archive_manifest(str(result["archive_dir"]))
        return _print_json(result)
    raise SystemExit(f"unknown command: {args.command}")


def _load_archive_json(archive_dir: str | Path, filename: str) -> dict[str, Any]:
    return json.loads((Path(archive_dir) / filename).read_text(encoding="utf-8"))


def _print_json(payload: Any) -> int:
    print(json.dumps(plain(payload), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
