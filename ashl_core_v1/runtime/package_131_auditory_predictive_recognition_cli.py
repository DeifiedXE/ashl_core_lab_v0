"""CLI for Package 131 anonymous auditory predictive recognition."""

from __future__ import annotations

import argparse
import json
from typing import Any

from ashl_core_v1.runtime.auditory_prediction_model_binding import (
    load_package_130_prediction_evidence,
)
from ashl_core_v1.runtime.auditory_predictive_recognition_types import PASS_STATUS
from ashl_core_v1.runtime.host_sensor_types import canonical_json
from ashl_core_v1.runtime.package_131_auditory_predictive_recognition_audit import (
    audit_package_131_auditory_predictive_recognition,
)
from ashl_core_v1.runtime.package_131_auditory_predictive_recognition_controls import (
    run_package_131_negative_controls,
)
from ashl_core_v1.runtime.package_131_auditory_predictive_recognition_runtime import (
    create_pair_comparison,
    preflight_package_131_prediction,
    run_probe_worker_subprocess,
)
from ashl_core_v1.runtime.package_131_auditory_predictive_recognition_store import (
    Package131AuditoryPredictiveRecognitionStore,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    def common(name: str, *, endpoint: bool = False, model: bool = True) -> argparse.ArgumentParser:
        command = subparsers.add_parser(name)
        command.add_argument("--state-dir", required=True)
        if endpoint:
            command.add_argument("--render-endpoint", default="default")
        if model:
            command.add_argument("--model-id")
        return command

    common("preflight", endpoint=True)
    common("show-model")
    for name in ("run-probe-a", "run-probe-b"):
        command = common(name, endpoint=True)
        command.add_argument("--allow-recognition-capture", action="store_true")
    common("show-predictions", model=False)
    common("show-comparison", model=False)
    common("audit")
    guided = common("guided-run", endpoint=True)
    guided.add_argument("--allow-recognition-capture", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "preflight":
            result = preflight_package_131_prediction(
                state_dir=args.state_dir,
                render_endpoint=args.render_endpoint,
                model_id=args.model_id,
            )
            _print_preflight(result)
            return 0
        if args.command == "show-model":
            evidence = load_package_130_prediction_evidence(
                state_dir=args.state_dir,
                model_id=args.model_id,
            )
            result = {
                "model": evidence.model.to_dict(),
                "package_130_audit_id": evidence.audit["audit_id"],
                "package_130_audit_status": evidence.audit["audit_status"],
                "expected_generation_id": evidence.generation.generation_id,
                "expected_audio_primitive_id": evidence.expected_primitive.audio_primitive_id,
                "deletion_audit_id": evidence.deletion_audit.deletion_audit_id,
                "consumer_scope": evidence.memory_commit["consumer_scope"],
                "model_snapshot_sha256": evidence.model_snapshot_sha256,
                "expected_template_sha256": evidence.expected_template_sha256,
            }
            print("已載入唯讀 Package 130 匿名聽覺模型。")
            print(canonical_json(result))
            return 0
        if args.command in {"run-probe-a", "run-probe-b"}:
            if not args.allow_recognition_capture:
                print("blocked_recognition_capture_authorization_missing")
                return 2
            slot = "A" if args.command.endswith("a") else "B"
            result = run_probe_worker_subprocess(
                state_dir=args.state_dir,
                probe_slot=slot,
                render_endpoint=args.render_endpoint,
                model_id=args.model_id,
            )
            if slot == "B":
                pair = create_pair_comparison(state_dir=args.state_dir)
                result = {
                    **result,
                    "pair_comparison_id": pair.pair_comparison_id,
                    "pair_comparison_status": pair.comparison_status,
                }
            print(f"Probe {slot} 已在獨立 process 完成 fresh WASAPI capture。")
            print(canonical_json(result))
            return 0
        if args.command == "show-predictions":
            rows = Package131AuditoryPredictiveRecognitionStore(args.state_dir).list_payloads(
                "auditory_prediction_comparisons"
            )
            print(f"Package 131 prediction records: {len(rows)}")
            print(canonical_json(rows))
            return 0
        if args.command == "show-comparison":
            row = Package131AuditoryPredictiveRecognitionStore(args.state_dir).latest_payload(
                "auditory_predictive_recognition_pair_comparisons"
            )
            print("最新兩 probe 比較。")
            print(canonical_json(row or {}))
            return 0 if row else 2
        if args.command == "audit":
            audit = audit_package_131_auditory_predictive_recognition(
                state_dir=args.state_dir,
                model_id=args.model_id,
                append=True,
            )
            print(
                "Package 131 audit passed."
                if audit.audit_status == PASS_STATUS
                else "Package 131 audit blocked."
            )
            print(canonical_json(audit.to_dict()))
            return 0 if audit.audit_status == PASS_STATUS else 2
        if args.command == "guided-run":
            if not args.allow_recognition_capture:
                print("blocked_recognition_capture_authorization_missing")
                return 2
            preflight = preflight_package_131_prediction(
                state_dir=args.state_dir,
                render_endpoint=args.render_endpoint,
                model_id=args.model_id,
            )
            print("1/6 preflight: ready")
            probe_a = run_probe_worker_subprocess(
                state_dir=args.state_dir,
                probe_slot="A",
                render_endpoint=args.render_endpoint,
                model_id=args.model_id,
            )
            print(f"2/6 Probe A: {probe_a['prediction_result']}")
            probe_b = run_probe_worker_subprocess(
                state_dir=args.state_dir,
                probe_slot="B",
                render_endpoint=args.render_endpoint,
                model_id=args.model_id,
            )
            print(f"3/6 Probe B: {probe_b['prediction_result']}")
            pair = create_pair_comparison(state_dir=args.state_dir)
            print(f"4/6 pair comparison: {pair.comparison_status}")
            controls = run_package_131_negative_controls(
                state_dir=args.state_dir,
                append=True,
            )
            print(f"5/6 controls: {controls.passed_count}/{controls.expected_count}")
            audit = audit_package_131_auditory_predictive_recognition(
                state_dir=args.state_dir,
                model_id=args.model_id,
                append=True,
            )
            result = {
                "preflight": preflight,
                "probe_a": probe_a,
                "probe_b": probe_b,
                "pair_comparison": pair.to_dict(),
                "controls": controls.to_dict(),
                "audit": audit.to_dict(),
            }
            print(f"6/6 audit: {audit.audit_status}")
            print(canonical_json(result))
            return 0 if audit.audit_status == PASS_STATUS else 2
    except Exception as error:
        print(f"{type(error).__name__}: {error}")
        return 2
    return 2


def _print_preflight(result: dict[str, Any]) -> None:
    print("Package 130 模型已通過唯讀 preflight；尚未開啟感測器。")
    for label, key in (
        ("Package 130 audit", "package_130_audit_status"),
        ("Ready model", "ready_model_id"),
        ("Expected primitive", "expected_primitive_id"),
        ("Generation", "expected_generation_id"),
        ("Deletion audit", "deletion_audit_id"),
        ("Consumer scope", "consumer_scope"),
        ("Endpoint", "endpoint_compatibility"),
        ("Recognition", "recognition_readiness"),
    ):
        print(f"{label}: {result[key]}")
    print(canonical_json(result))


if __name__ == "__main__":
    raise SystemExit(main())
