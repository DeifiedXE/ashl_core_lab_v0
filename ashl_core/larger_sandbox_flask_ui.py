"""Local Flask UI prototype for the larger simulated vision sandbox."""

from __future__ import annotations

from copy import deepcopy
import time
from typing import Any

from flask import Flask, redirect, render_template_string, request, url_for

from .simulated_vision_larger_sandbox import (
    apply_larger_sandbox_action,
    build_initial_larger_sandbox_state,
    create_simulated_vision_larger_sandbox,
    render_larger_sandbox_viewport,
)
from .simulated_vision_larger_sandbox_human_replay import get_front_symbol_for_replay


DEFAULT_UI_HOST = "127.0.0.1"
DEFAULT_UI_PORT = 7860
DEFAULT_ACTION_COOLDOWN_SECONDS = 0.5
MIN_ACTION_COOLDOWN_SECONDS = 0.0
MAX_ACTION_COOLDOWN_SECONDS = 5.0
ALLOWED_UI_ACTIONS = frozenset({"look", "turn_left", "turn_right", "move_forward"})

_SYMBOL_LABELS = {
    "w": "wall",
    "e": "empty",
    "i": "item",
    "d": "passage",
    "g": "exit placeholder",
    "x": "unseen",
    "a": "Qingyin",
}
_UI_STATE: dict[str, Any] | None = None
_NOW_FUNC = time.monotonic


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def index() -> str:
        return render_template_string(_HTML_TEMPLATE, ui=get_ui_state(), symbols=_SYMBOL_LABELS)

    @app.post("/action")
    def action() -> Any:
        action_name = request.form.get("action", "")
        if action_name not in ALLOWED_UI_ACTIONS:
            return "unsupported action", 400
        apply_ui_action(action_name)
        return redirect(url_for("index"))

    @app.post("/cooldown")
    def cooldown() -> Any:
        set_action_cooldown_seconds(request.form.get("cooldown_seconds", ""))
        return redirect(url_for("index"))

    @app.post("/reset")
    def reset() -> Any:
        reset_ui_state()
        return redirect(url_for("index"))

    @app.get("/state.json")
    def state_json() -> dict[str, Any]:
        return get_ui_state()

    return app


def get_launch_config(host: str = DEFAULT_UI_HOST, port: int = DEFAULT_UI_PORT) -> dict[str, Any]:
    level = create_simulated_vision_larger_sandbox()
    return {
        "command": "run-larger-sandbox-ui",
        "level_id": level["level_id"],
        "url": f"http://{host}:{port}",
        "host": host,
        "port": port,
        "debug": False,
        "local_only": host == DEFAULT_UI_HOST,
        "ui_prototype": True,
        "action_cooldown_enabled": True,
        "action_cooldown_configurable": True,
        "boundary_check": build_ui_boundary_check(host=host),
    }


def run_larger_sandbox_ui(host: str = DEFAULT_UI_HOST, port: int = DEFAULT_UI_PORT, debug: bool = False) -> None:
    app = create_app()
    config = get_launch_config(host=host, port=port)
    print("Larger Sandbox Flask Visual UI Prototype", flush=True)
    print(f"URL: {config['url']}", flush=True)
    print("Local only." if config["local_only"] else "Non-default host requested.", flush=True)
    print("No pathfinding / no item collection / no exit activation.", flush=True)
    app.run(host=host, port=port, debug=debug)


def get_ui_state() -> dict[str, Any]:
    internal = _get_internal_state()
    return _public_state(internal["state"], internal["viewport"], internal["action_log"])


def set_ui_now_func(now_func: Any) -> None:
    global _NOW_FUNC
    _NOW_FUNC = now_func


def reset_ui_now_func() -> None:
    set_ui_now_func(time.monotonic)


def reset_ui_state() -> dict[str, Any]:
    global _UI_STATE
    level = create_simulated_vision_larger_sandbox()
    state = build_initial_larger_sandbox_state(level)
    viewport = render_larger_sandbox_viewport(state, level)
    _UI_STATE = {
        "level": level,
        "state": state,
        "viewport": viewport,
        "action_log": [],
        "step_count": 0,
        "action_cooldown_seconds": DEFAULT_ACTION_COOLDOWN_SECONDS,
        "last_action_time": None,
    }
    return get_ui_state()


def set_action_cooldown_seconds(value: Any) -> dict[str, Any]:
    internal = _get_internal_state()
    cooldown_seconds = _clamp_cooldown_seconds(value)
    internal["action_cooldown_seconds"] = cooldown_seconds
    internal["action_log"].append(f"Cooldown updated to {cooldown_seconds:.1f}s")
    return get_ui_state()


def apply_ui_action(action: str) -> dict[str, Any]:
    if action not in ALLOWED_UI_ACTIONS:
        raise ValueError(f"unsupported larger sandbox UI action: {action}")

    internal = _get_internal_state()
    now = _NOW_FUNC()
    remaining = cooldown_remaining_seconds(
        now=now,
        last_action_time=internal["last_action_time"],
        cooldown_seconds=internal["action_cooldown_seconds"],
    )
    if remaining > 0:
        internal["step_count"] += 1
        internal["action_log"].append(_format_cooldown_blocked_log_entry(internal["step_count"], action, remaining))
        return get_ui_state()

    before = deepcopy(internal["state"])
    result = apply_larger_sandbox_action(internal["state"], internal["level"], action)
    after = result["state"]
    trace = result["trace"]
    internal["state"] = after
    internal["viewport"] = trace["viewport"]
    internal["last_action_time"] = now
    internal["step_count"] += 1
    internal["action_log"].append(_format_action_log_entry(internal["step_count"], action, before, trace))
    return get_ui_state()


def cooldown_remaining_seconds(*, now: float, last_action_time: float | None, cooldown_seconds: float) -> float:
    if cooldown_seconds <= 0 or last_action_time is None:
        return 0.0
    elapsed = max(0.0, now - last_action_time)
    return max(0.0, cooldown_seconds - elapsed)


def build_ui_boundary_check(host: str = DEFAULT_UI_HOST) -> dict[str, Any]:
    return {
        "ui_prototype": True,
        "local_only": host == DEFAULT_UI_HOST,
        "action_cooldown_enabled": True,
        "action_cooldown_configurable": True,
        "autonomous_action_loop_enabled": False,
        "runtime_behavior_modified": False,
        "viewport_geometry_modified": False,
        "action_selection_modified": False,
        "pathfinding_used": False,
        "route_planner_added": False,
        "item_collection_enabled": False,
        "item_pickup_enabled": False,
        "inventory_enabled": False,
        "exit_activation_enabled": False,
        "win_condition_enabled": False,
        "task_completion_enabled": False,
        "curiosity_enabled": False,
        "prediction_error_enabled": False,
        "place_memory_enabled": False,
        "home_sandbox_enabled": False,
        "real_image_vision": False,
        "computer_vision": False,
        "llm_vision_used": False,
        "llm_planning_used": False,
        "lesson_store_write": False,
        "memory_layer_write": False,
        "long_term_memory_write": False,
        "lesson_candidate_pipeline_connected": False,
        "visual_understanding_claimed": False,
        "symbol_grounding_solved_claimed": False,
        "general_learning_claimed": False,
    }


def _get_internal_state() -> dict[str, Any]:
    global _UI_STATE
    if _UI_STATE is None:
        reset_ui_state()
    if _UI_STATE is None:
        raise RuntimeError("larger sandbox UI state was not initialized")
    return _UI_STATE


def _public_state(state: dict[str, Any], viewport: list[list[str]], action_log: list[str]) -> dict[str, Any]:
    internal = _get_internal_state()
    cooldown_seconds = internal["action_cooldown_seconds"]
    remaining = cooldown_remaining_seconds(
        now=_NOW_FUNC(),
        last_action_time=internal["last_action_time"],
        cooldown_seconds=cooldown_seconds,
    )
    level_id = state["level_id"]
    front_symbol = get_front_symbol_for_replay(viewport)
    return {
        "level_id": level_id,
        "pos": list(state["pos"]),
        "facing": state["facing"],
        "tick": state["tick"],
        "viewport": deepcopy(viewport),
        "front_symbol": front_symbol,
        "front_label": _SYMBOL_LABELS[front_symbol],
        "action_log": list(action_log),
        "action_cooldown_seconds": cooldown_seconds,
        "cooldown_remaining_seconds": remaining,
        "cooldown_remaining_display": f"{remaining:.2f}",
        "can_act": remaining <= 0,
        "can_act_display": "yes" if remaining <= 0 else "no",
        "last_action_time": internal["last_action_time"],
        "boundary_check": build_ui_boundary_check(),
    }


def _format_action_log_entry(step_number: int, action: str, before: dict[str, Any], trace: dict[str, Any]) -> str:
    effects = ", ".join(trace["effect_tags"]) if trace["effect_tags"] else "none"
    failures = ", ".join(trace["failure_reasons"]) if trace["failure_reasons"] else "none"
    return (
        f"Step {step_number}: {action}\n"
        f"Before: {_format_pos(before['pos'])}, facing {before['facing']}\n"
        f"Front symbol: {trace['front_symbol']}\n"
        f"Result: {trace['result']}\n"
        f"Effect: {effects}\n"
        f"Failure: {failures}\n"
        f"After: {_format_pos(trace['after']['pos'])}, facing {trace['after']['facing']}"
    )


def _format_cooldown_blocked_log_entry(step_number: int, action: str, remaining: float) -> str:
    return f"Step {step_number}: {action}\nAction blocked by cooldown.\nRemaining: {remaining:.2f}s"


def _format_pos(pos: list[int] | tuple[int, int]) -> str:
    return f"[{pos[0]},{pos[1]}]"


def _clamp_cooldown_seconds(value: Any) -> float:
    try:
        cooldown_seconds = float(value)
    except (TypeError, ValueError):
        cooldown_seconds = DEFAULT_ACTION_COOLDOWN_SECONDS
    return min(MAX_ACTION_COOLDOWN_SECONDS, max(MIN_ACTION_COOLDOWN_SECONDS, cooldown_seconds))


_HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Larger Sandbox</title>
  <style>
    :root {
      color-scheme: light;
      --ink: #202124;
      --muted: #5f6368;
      --line: #d6d9de;
      --surface: #f7f8fa;
      --panel: #ffffff;
      --wall: #3f4752;
      --empty: #f1f4f7;
      --item: #fff0a8;
      --passage: #c9ead6;
      --exit: #c8ddff;
      --unknown: #e4e7eb;
      --agent: #f6c8c3;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      color: var(--ink);
      background: var(--surface);
      font-family: Arial, Helvetica, sans-serif;
    }
    header {
      border-bottom: 1px solid var(--line);
      background: var(--panel);
      padding: 16px 22px;
    }
    h1 {
      margin: 0 0 10px;
      font-size: 24px;
      font-weight: 700;
    }
    .meta {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      color: var(--muted);
      font-size: 14px;
    }
    .meta span {
      border: 1px solid var(--line);
      border-radius: 4px;
      padding: 5px 8px;
      background: #fff;
    }
    main {
      display: grid;
      grid-template-columns: minmax(260px, 420px) minmax(300px, 1fr);
      gap: 18px;
      padding: 18px 22px 24px;
      max-width: 1120px;
      margin: 0 auto;
    }
    section {
      min-width: 0;
    }
    h2 {
      font-size: 16px;
      margin: 0 0 10px;
    }
    .viewport {
      display: grid;
      grid-template-columns: repeat(3, minmax(72px, 1fr));
      gap: 8px;
      width: 100%;
      max-width: 360px;
    }
    .cell {
      aspect-ratio: 1 / 1;
      border: 1px solid var(--line);
      border-radius: 4px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-size: 26px;
      line-height: 1.1;
    }
    .cell small {
      margin-top: 5px;
      color: var(--muted);
      font-size: 11px;
      font-weight: 400;
      text-align: center;
    }
    .symbol-w { background: var(--wall); color: white; }
    .symbol-w small { color: #edf0f3; }
    .symbol-e { background: var(--empty); }
    .symbol-i { background: var(--item); }
    .symbol-d { background: var(--passage); }
    .symbol-g { background: var(--exit); }
    .symbol-x { background: var(--unknown); }
    .symbol-a { background: var(--agent); }
    .controls {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin: 16px 0;
    }
    button {
      min-height: 36px;
      border: 1px solid #9aa0a6;
      border-radius: 4px;
      background: white;
      color: var(--ink);
      padding: 8px 12px;
      font: inherit;
      cursor: pointer;
    }
    button:hover { background: #eef3f8; }
    .reset button { border-color: #c7a1a1; }
    .cooldown {
      border-top: 1px solid var(--line);
      padding-top: 12px;
      margin-top: 12px;
      max-width: 360px;
    }
    .cooldown form {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
      margin: 8px 0;
    }
    .cooldown input {
      width: 86px;
      min-height: 36px;
      border: 1px solid var(--line);
      border-radius: 4px;
      padding: 7px 8px;
      font: inherit;
    }
    .cooldown p {
      margin: 4px 0;
      color: var(--muted);
      font-size: 14px;
    }
    .legend, .boundary, .log {
      border-top: 1px solid var(--line);
      padding-top: 12px;
      margin-top: 12px;
    }
    .legend dl {
      display: grid;
      grid-template-columns: auto 1fr;
      gap: 6px 12px;
      margin: 0;
      font-size: 14px;
    }
    .legend dt { font-weight: 700; }
    .boundary ul {
      margin: 0;
      padding-left: 20px;
      color: var(--muted);
      font-size: 14px;
    }
    .log pre {
      min-height: 220px;
      max-height: 360px;
      overflow: auto;
      white-space: pre-wrap;
      border: 1px solid var(--line);
      border-radius: 4px;
      background: #fff;
      padding: 12px;
      font-family: Consolas, Monaco, monospace;
      font-size: 13px;
    }
    @media (max-width: 760px) {
      main { grid-template-columns: 1fr; padding: 14px; }
      header { padding: 14px; }
    }
  </style>
</head>
<body>
  <header>
    <h1>Larger Sandbox</h1>
    <div class="meta">
      <span>Level: {{ ui.level_id }}</span>
      <span>Position: [{{ ui.pos[0] }}, {{ ui.pos[1] }}]</span>
      <span>Facing: {{ ui.facing }}</span>
      <span>Front symbol: {{ ui.front_symbol }} {{ ui.front_label }}</span>
    </div>
  </header>
  <main>
    <section>
      <h2>First-person viewport</h2>
      <div class="viewport" aria-label="first-person viewport">
        {% for row in ui.viewport %}
          {% for symbol in row %}
            <div class="cell symbol-{{ symbol }}" title="{{ symbol }} {{ symbols[symbol] }}">
              {{ symbol }}
              <small>{{ symbols[symbol] }}</small>
            </div>
          {% endfor %}
        {% endfor %}
      </div>
      <div class="controls" aria-label="actions">
        <form method="post" action="{{ url_for('action') }}"><button name="action" value="look">look</button></form>
        <form method="post" action="{{ url_for('action') }}"><button name="action" value="turn_left">turn_left</button></form>
        <form method="post" action="{{ url_for('action') }}"><button name="action" value="turn_right">turn_right</button></form>
        <form method="post" action="{{ url_for('action') }}"><button name="action" value="move_forward">move_forward</button></form>
        <form class="reset" method="post" action="{{ url_for('reset') }}"><button>reset</button></form>
      </div>
      <div class="cooldown">
        <h2>Action cooldown</h2>
        <p>Cooldown: {{ "%.1f"|format(ui.action_cooldown_seconds) }}s</p>
        <p>Cooldown remaining: {{ ui.cooldown_remaining_display }} seconds</p>
        <p>Can act: {{ ui.can_act_display }}</p>
        <form method="post" action="{{ url_for('cooldown') }}">
          <label for="cooldown_seconds">Seconds</label>
          <input id="cooldown_seconds" name="cooldown_seconds" type="number" min="0" max="5" step="0.1" value="{{ "%.1f"|format(ui.action_cooldown_seconds) }}">
          <button>update cooldown</button>
        </form>
      </div>
    </section>
    <section>
      <div class="legend">
        <h2>Legend</h2>
        <dl>
          {% for symbol, label in symbols.items() %}
            <dt>{{ symbol }}</dt><dd>{{ label }}</dd>
          {% endfor %}
        </dl>
      </div>
      <div class="boundary">
        <h2>Boundary</h2>
        <ul>
          <li>Local visual inspection UI only.</li>
          <li>Action cooldown only controls timing.</li>
          <li>No autonomy.</li>
          <li>No auto exploration.</li>
          <li>No pathfinding.</li>
          <li>No route planner.</li>
          <li>No action selection change.</li>
          <li>No item collection.</li>
          <li>No exit activation.</li>
          <li>No curiosity.</li>
          <li>No prediction error.</li>
          <li>No place memory.</li>
          <li>No home sandbox.</li>
          <li>No visual understanding claim.</li>
        </ul>
      </div>
      <div class="log">
        <h2>Action log</h2>
        <pre>{% if ui.action_log %}{{ ui.action_log | join('\n\n') }}{% else %}No actions yet.{% endif %}</pre>
      </div>
    </section>
  </main>
</body>
</html>
"""
