"""CLI for Package 122B local operator console foundation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ashl_core_v1.runtime.local_non_llm_output_dispatcher import LocalNonLLMOutputDispatcher
from ashl_core_v1.runtime.local_operator_console_store import build_default_console_store
from ashl_core_v1.runtime.local_operator_event_stream import LocalOperatorEventStream
from ashl_core_v1.runtime.operator_console_state_reader import (
    audit_non_llm_local_output_surface,
    build_total_state_snapshot,
    build_upper_console_view_model,
)
from ashl_core_v1.runtime.operator_hardware_status import build_hardware_settings_snapshot, set_output_volume_state
from ashl_core_v1.runtime.operator_text_timeline import build_fixture_raw_output_sequence, submit_local_text_input


def _print_json(value: object) -> None:
    print(json.dumps(_plain(value), indent=2, sort_keys=True))


def _plain(value: object) -> object:
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if isinstance(value, dict):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    return value


def _bool_arg(value: str) -> bool:
    text = value.strip().lower()
    if text in {"true", "1", "yes", "on"}:
        return True
    if text in {"false", "0", "no", "off"}:
        return False
    raise argparse.ArgumentTypeError("expected true or false")


def _state_dir(args: argparse.Namespace) -> Path:
    return Path(args.state_dir)


def _cmd_show_console(args: argparse.Namespace) -> int:
    _print_json(build_upper_console_view_model(state_dir=_state_dir(args), runtime_process_available=True))
    return 0


def _cmd_show_total_state(args: argparse.Namespace) -> int:
    _print_json(build_total_state_snapshot(state_dir=_state_dir(args), runtime_process_available=True))
    return 0


def _cmd_set_camera_preference(args: argparse.Namespace) -> int:
    store = build_default_console_store(_state_dir(args))
    preference = store.set_hardware_preference(device_kind="camera", enabled=args.enabled)
    LocalOperatorEventStream(store).append_event(
        event_kind="hardware_preference_changed",
        source_record_refs=(preference["preference_id"],),
    )
    _print_json(preference)
    return 0


def _cmd_set_microphone_preference(args: argparse.Namespace) -> int:
    store = build_default_console_store(_state_dir(args))
    preference = store.set_hardware_preference(device_kind="microphone", enabled=args.enabled)
    LocalOperatorEventStream(store).append_event(
        event_kind="hardware_preference_changed",
        source_record_refs=(preference["preference_id"],),
    )
    _print_json(preference)
    return 0


def _cmd_set_output_volume(args: argparse.Namespace) -> int:
    store = build_default_console_store(_state_dir(args))
    state = set_output_volume_state(store, gain=args.gain)
    LocalOperatorEventStream(store).append_event(event_kind="output_volume_changed", source_record_refs=(state.volume_state_id,))
    _print_json(state)
    return 0


def _cmd_set_output_muted(args: argparse.Namespace) -> int:
    store = build_default_console_store(_state_dir(args))
    state = set_output_volume_state(store, muted=args.muted)
    LocalOperatorEventStream(store).append_event(event_kind="output_volume_changed", source_record_refs=(state.volume_state_id,))
    _print_json(state)
    return 0


def _cmd_show_hardware_settings(args: argparse.Namespace) -> int:
    store = build_default_console_store(_state_dir(args))
    _print_json(build_hardware_settings_snapshot(state_dir=_state_dir(args), store=store))
    return 0


def _cmd_submit_text(args: argparse.Namespace) -> int:
    store = build_default_console_store(_state_dir(args))
    record, entry = submit_local_text_input(store, text=args.text)
    _print_json({"text_input": record, "timeline_entry": entry})
    return 0


def _cmd_dispatch_fixture_token(args: argparse.Namespace) -> int:
    store = build_default_console_store(_state_dir(args))
    tokens = tuple(token.strip() for token in args.tokens.split(",") if token.strip())
    sequence = build_fixture_raw_output_sequence(token_codes=tokens)
    store.append_raw_output_sequence(sequence)
    dispatcher = LocalNonLLMOutputDispatcher(store)
    intent = dispatcher.create_raw_output_intent(
        raw_output_sequence_id=sequence.raw_output_sequence_id,
        source_kind="fixture",
        source_record_refs=(sequence.raw_output_sequence_id,),
        fixture_only=True,
        qingyin_authored=False,
    )
    result = dispatcher.dispatch_intent(intent.output_intent_id)
    _print_json({"raw_output_sequence": sequence, "output_intent": intent, "dispatch_result": result})
    return 0


def _cmd_cancel_output(args: argparse.Namespace) -> int:
    store = build_default_console_store(_state_dir(args))
    cancellation = LocalNonLLMOutputDispatcher(store).cancel_output(output_intent_id=args.intent_id)
    _print_json(cancellation)
    return 0


def _cmd_show_status_log(args: argparse.Namespace) -> int:
    store = build_default_console_store(_state_dir(args))
    _print_json(store.list_payloads("status_log_entries")[-100:])
    return 0


def _cmd_stream_json_events(args: argparse.Namespace) -> int:
    store = build_default_console_store(_state_dir(args))
    for event in LocalOperatorEventStream(store).list_events():
        print(json.dumps(event, sort_keys=True))
    return 0


def _cmd_audit_console(args: argparse.Namespace) -> int:
    _print_json(audit_non_llm_local_output_surface(_state_dir(args)))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Package 122B local operator console")
    sub = parser.add_subparsers(dest="command", required=True)

    def stateful(name: str) -> argparse.ArgumentParser:
        item = sub.add_parser(name)
        item.add_argument("--state-dir", required=True)
        return item

    stateful("show-console").set_defaults(func=_cmd_show_console)
    stateful("show-total-state").set_defaults(func=_cmd_show_total_state)

    camera = stateful("set-camera-preference")
    camera.add_argument("--enabled", required=True, type=_bool_arg)
    camera.set_defaults(func=_cmd_set_camera_preference)

    mic = stateful("set-microphone-preference")
    mic.add_argument("--enabled", required=True, type=_bool_arg)
    mic.set_defaults(func=_cmd_set_microphone_preference)

    volume = stateful("set-output-volume")
    volume.add_argument("--gain", required=True, type=float)
    volume.set_defaults(func=_cmd_set_output_volume)

    muted = stateful("set-output-muted")
    muted.add_argument("--muted", required=True, type=_bool_arg)
    muted.set_defaults(func=_cmd_set_output_muted)

    stateful("show-hardware-settings").set_defaults(func=_cmd_show_hardware_settings)

    text = stateful("submit-text")
    text.add_argument("--text", required=True)
    text.set_defaults(func=_cmd_submit_text)

    fixture = stateful("dispatch-fixture-token")
    fixture.add_argument("--tokens", required=True)
    fixture.set_defaults(func=_cmd_dispatch_fixture_token)

    cancel = stateful("cancel-output")
    cancel.add_argument("--intent-id", required=True)
    cancel.set_defaults(func=_cmd_cancel_output)

    stateful("show-status-log").set_defaults(func=_cmd_show_status_log)
    stateful("stream-json-events").set_defaults(func=_cmd_stream_json_events)
    stateful("audit-console").set_defaults(func=_cmd_audit_console)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
