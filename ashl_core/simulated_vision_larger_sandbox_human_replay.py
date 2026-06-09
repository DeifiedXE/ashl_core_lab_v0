"""Human-readable replay formatter for the larger simulated vision sandbox."""

from __future__ import annotations

from typing import Any

from .simulated_vision_larger_sandbox import run_simulated_vision_larger_sandbox_demo
from .simulated_vision_larger_sandbox_contact import run_larger_sandbox_symbol_contact_smoke
from .simulated_vision_larger_sandbox_observed_map import run_larger_sandbox_observed_map_smoke


SUPPORTED_HUMAN_REPLAY_MODES = ("demo", "contact", "observed-map")


def run_larger_sandbox_human_replay(mode: str = "demo") -> str:
    if mode not in SUPPORTED_HUMAN_REPLAY_MODES:
        raise ValueError(f"unsupported larger sandbox human replay mode: {mode}")

    if mode == "contact":
        return _format_contact_replay(run_larger_sandbox_symbol_contact_smoke())
    if mode == "observed-map":
        return _format_observed_map_replay(run_larger_sandbox_observed_map_smoke())
    return _format_demo_replay(run_simulated_vision_larger_sandbox_demo())


def _format_demo_replay(result: dict[str, Any]) -> str:
    lines = _header(result["level_id"], "demo")
    lines.append("Steps:")
    for index, step in enumerate(result["action_trace"], start=1):
        after = step["after"]
        lines.extend(
            [
                "",
                f"Step {index}: {step['action']}",
                f"Position: {_format_pos(after['pos'])}",
                f"Facing: {after['facing']}",
                "Viewport:",
                _format_viewport(step["viewport"]),
                f"She sees: {_symbol_description(step['front_symbol'])}",
                f"Front symbol: {step['front_symbol']}",
                f"Result: {step['result']}",
                f"Effects: {_format_list(step['effect_tags'])}",
                f"Failures: {_format_list(step['failure_reasons'])}",
            ]
        )
    lines.extend(_boundary())
    return "\n".join(lines)


def _format_contact_replay(result: dict[str, Any]) -> str:
    lines = _header(result["level_id"], "contact")
    lines.append("Contact Steps:")
    for index, step in enumerate(result["scenario_results"], start=1):
        lines.extend(
            [
                "",
                f"Step {index}: {step['scenario']}",
                f"Action: {step['action']}",
                f"Position: {_format_pos(step['initial_pos'])}",
                f"Facing: {step['initial_facing']}",
                "Viewport:",
                _format_viewport(step["current_viewport"]),
                f"She sees: {_symbol_description(step['front_symbol'])}",
                f"Front symbol: {step['front_symbol']}",
                f"Result: {step['actual_outcome']}",
                f"Effects: {_format_list(step['effect_tags'])}",
                f"Failures: {_format_list(step['failure_reasons'])}",
                f"Position after: {_format_pos(step['position_after'])}",
            ]
        )
    lines.extend(_boundary())
    return "\n".join(lines)


def _format_observed_map_replay(result: dict[str, Any]) -> str:
    lines = _header(result["level_id"], "observed-map")
    lines.append("Observed Map Steps:")
    for index, step in enumerate(result["scenario_results"], start=1):
        state = step["initial_state"]
        lines.extend(
            [
                "",
                f"Step {index}: {step['scenario']}",
                f"Position: {_format_pos(state['pos'])}",
                f"Facing: {state['facing']}",
                "Viewport:",
                _format_viewport(step["current_viewport"]),
                f"She sees: {_symbol_description(step['target_symbol'])}",
                f"Front symbol: {step['target_symbol']}",
                f"Observed world position: {_format_pos(step['observed_world_pos'])}",
                f"Known cells after view: {step['known_cell_count_after']}",
                f"Still remembered after view change: {_format_bool(step['still_remembered'])}",
            ]
        )
    summary = result["observed_map_summary"]
    lines.extend(
        [
            "",
            "Observed Map Summary:",
            f"Known cells: {summary['known_cell_count']}",
            f"Remembered symbols: {_format_list(summary['remembered_symbols'])}",
            f"x does not erase known cells: {_format_bool(summary['x_does_not_erase_known_cells'])}",
        ]
    )
    lines.extend(_boundary())
    return "\n".join(lines)


def _header(level_id: str, mode: str) -> list[str]:
    return [
        "Larger Sandbox Human Replay",
        f"Level: {level_id}",
        f"Mode: {mode}",
        "",
        "Legend:",
        "w = wall",
        "e = empty",
        "i = item",
        "d = passage marker",
        "g = exit placeholder",
        "x = unseen / out of view",
        "a = Qingyin",
        "",
    ]


def _boundary() -> list[str]:
    return [
        "",
        "Boundary:",
        "Readability replay only.",
        "No runtime behavior changed.",
        "No action selection changed.",
        "No pathfinding.",
        "No item collection.",
        "No exit activation.",
        "No curiosity.",
        "No prediction error.",
        "No place memory.",
        "No home sandbox.",
        "No visual understanding claim.",
    ]


def _format_viewport(viewport: list[list[str]]) -> str:
    return "\n".join(" ".join(row) for row in viewport)


def _format_pos(pos: list[int] | tuple[int, int]) -> str:
    return f"({pos[0]}, {pos[1]})"


def _format_list(values: list[str]) -> str:
    return ", ".join(values) if values else "none"


def _format_bool(value: bool) -> str:
    return "true" if value else "false"


def _symbol_description(symbol: str) -> str:
    descriptions = {
        "w": "wall",
        "e": "empty",
        "i": "item",
        "d": "passage marker",
        "g": "exit placeholder",
        "x": "unseen / out of view",
        "a": "Qingyin",
    }
    return descriptions.get(symbol, f"unknown symbol {symbol}")
