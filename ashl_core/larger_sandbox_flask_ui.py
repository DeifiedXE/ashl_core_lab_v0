"""Local Flask UI prototype for the larger simulated vision sandbox."""

from __future__ import annotations

from copy import deepcopy
import time
from typing import Any

from flask import Flask, redirect, render_template_string, request, url_for

from .instinct_random_walk_runner import run_instinct_random_walk
from .instinct_wall_ui_observation import (
    build_empty_experiment_observation,
    build_random_walk_observation,
    build_wall_influence_observation,
    copy_experiment_observation,
)
from .qingyin_ui_observation import build_qingyin_observation_state, format_qingyin_log_entry
from .simulated_vision_larger_sandbox import (
    apply_larger_sandbox_action,
    build_initial_larger_sandbox_state,
    create_simulated_vision_larger_sandbox,
    render_larger_sandbox_viewport,
)
from .simulated_vision_larger_sandbox_human_replay import get_front_symbol_for_replay
from .wall_experience_influence import run_wall_experience_influence_check


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

    @app.post("/experiment/random-walk")
    def experiment_random_walk() -> Any:
        seed = _parse_experiment_int(request.form.get("seed"), 1)
        max_steps = _parse_experiment_int(request.form.get("max_steps"), 50)
        run_random_walk_experiment_observation(seed=seed, max_steps=max_steps)
        return redirect(url_for("index"))

    @app.post("/experiment/wall-influence")
    def experiment_wall_influence() -> Any:
        seed = _parse_experiment_int(request.form.get("seed"), 1)
        max_steps = _parse_experiment_int(request.form.get("max_steps"), 50)
        run_wall_influence_experiment_observation(seed=seed, max_steps=max_steps)
        return redirect(url_for("index"))

    @app.post("/experiment/clear")
    def experiment_clear() -> Any:
        clear_experiment_observation()
        return redirect(url_for("index"))

    @app.get("/state.json")
    def state_json() -> dict[str, Any]:
        return get_ui_state()

    @app.get("/qingyin_state.json")
    def qingyin_state_json() -> dict[str, Any]:
        return get_ui_state()["qingyin_observation"]

    @app.get("/experiment_state.json")
    def experiment_state_json() -> dict[str, Any]:
        return get_ui_state()["experiment_observation"]

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
        "qingyin_observation_bridge_enabled": True,
        "instinct_wall_ui_observation_bridge_enabled": True,
        "manual_observation_only": True,
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
        "last_action_result": None,
        "experiment_observation": build_empty_experiment_observation(),
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
        internal["last_action_result"] = {
            "action": action,
            "result": "cooldown_blocked",
            "effects": [],
            "failures": ["cooldown_active"],
        }
        internal["action_log"].append(_format_cooldown_blocked_log_entry(internal["step_count"], action, remaining))
        return get_ui_state()

    before = deepcopy(internal["state"])
    result = apply_larger_sandbox_action(internal["state"], internal["level"], action)
    after = result["state"]
    trace = result["trace"]
    internal["state"] = after
    internal["viewport"] = trace["viewport"]
    internal["last_action_time"] = now
    internal["last_action_result"] = {
        "action": action,
        "result": trace["result"],
        "effects": list(trace["effect_tags"]),
        "failures": list(trace["failure_reasons"]),
    }
    internal["step_count"] += 1
    internal["action_log"].append(_format_action_log_entry(internal["step_count"], action, before, trace))
    return get_ui_state()


def run_random_walk_experiment_observation(seed: int = 1, max_steps: int = 50) -> dict[str, Any]:
    internal = _get_internal_state()
    result = run_instinct_random_walk(seed=seed, max_steps=max_steps)
    internal["experiment_observation"] = build_random_walk_observation(result)
    internal["action_log"].append(
        f"Experiment: random walk sample\n"
        f"Qingyin ran a bounded random walk sample.\n"
        f"Step count: {result['metrics']['step_count']}\n"
        f"Wall blocked: {result['metrics']['wall_blocked_count']}\n"
        f"Item contact: {result['metrics']['item_contact_count']}"
    )
    return get_ui_state()


def run_wall_influence_experiment_observation(seed: int = 1, max_steps: int = 50) -> dict[str, Any]:
    internal = _get_internal_state()
    result = run_wall_experience_influence_check(seed=seed, max_steps=max_steps)
    internal["experiment_observation"] = build_wall_influence_observation(result)
    internal["action_log"].append(
        f"Experiment: wall influence check\n"
        f"Wall experience influence check passed: {str(result['summary']['all_wall_experience_influence_checks_passed']).lower()}\n"
        f"Without experience: {result['control_result']['selected_action']}\n"
        f"With wall experience: {result['influence_result']['selected_action']}"
    )
    return get_ui_state()


def clear_experiment_observation() -> dict[str, Any]:
    internal = _get_internal_state()
    internal["experiment_observation"] = build_empty_experiment_observation()
    internal["action_log"].append("Experiment observation cleared.")
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
        "qingyin_observation_bridge_enabled": True,
        "instinct_random_walk_ui_observation_enabled": True,
        "wall_experience_influence_ui_observation_enabled": True,
        "bounded_runner_only": True,
        "continuous_autonomous_loop_enabled": False,
        "random_walk_runner_available": True,
        "wall_experience_influence_available": True,
        "manual_observation_only": True,
        "autonomous_action_loop_enabled": False,
        "auto_exploration_enabled": False,
        "decision_loop_enabled": False,
        "item_reward_bias_enabled": False,
        "dopamine_like_signal_enabled": False,
        "runtime_behavior_modified": False,
        "viewport_geometry_modified": False,
        "action_selection_modified": False,
        "action_selection_modified_by_ui": False,
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
        "computer_vision_used": False,
        "llm_vision_used": False,
        "llm_planning_used": False,
        "lesson_store_write": False,
        "memory_layer_write": False,
        "long_term_memory_write": False,
        "lesson_candidate_pipeline_connected": False,
        "visual_understanding_claimed": False,
        "symbol_grounding_solved_claimed": False,
        "general_learning_claimed": False,
        "consciousness_claimed": False,
        "subjective_experience_claimed": False,
    }


def _get_internal_state() -> dict[str, Any]:
    global _UI_STATE
    if _UI_STATE is None:
        reset_ui_state()
    if _UI_STATE is None:
        raise RuntimeError("larger sandbox UI state was not initialized")
    _UI_STATE.setdefault("experiment_observation", build_empty_experiment_observation())
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
    public_state = {
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
        "last_action_result": deepcopy(internal["last_action_result"]),
        "experiment_observation": copy_experiment_observation(internal["experiment_observation"]),
        "boundary_check": build_ui_boundary_check(),
    }
    public_state["qingyin_observation"] = build_qingyin_observation_state(public_state)
    return public_state


def _format_action_log_entry(step_number: int, action: str, before: dict[str, Any], trace: dict[str, Any]) -> str:
    effects = ", ".join(trace["effect_tags"]) if trace["effect_tags"] else "none"
    failures = ", ".join(trace["failure_reasons"]) if trace["failure_reasons"] else "none"
    qingyin_line = format_qingyin_log_entry(action, trace["result"], trace["effect_tags"], trace["failure_reasons"])
    return (
        f"Step {step_number}: {action}\n"
        f"{qingyin_line}\n"
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


def _parse_experiment_int(value: Any, default: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = default
    return max(0, parsed)


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
    .experiment input {
      width: 92px;
      min-height: 36px;
      border: 1px solid var(--line);
      border-radius: 4px;
      padding: 7px 8px;
      font: inherit;
    }
    .experiment form {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
      margin: 8px 0;
    }
    .experiment dl {
      display: grid;
      grid-template-columns: max-content 1fr;
      gap: 6px 12px;
      margin: 10px 0 0;
      font-size: 14px;
    }
    .experiment dt { font-weight: 700; }
    .experiment dd { margin: 0; color: var(--muted); }
    .cooldown p {
      margin: 4px 0;
      color: var(--muted);
      font-size: 14px;
    }
    .observation, .experiment, .legend, .boundary, .log {
      border-top: 1px solid var(--line);
      padding-top: 12px;
      margin-top: 12px;
    }
    .observation dl {
      display: grid;
      grid-template-columns: max-content 1fr;
      gap: 6px 12px;
      margin: 0;
      font-size: 14px;
    }
    .observation dt { font-weight: 700; }
    .observation dd { margin: 0; color: var(--muted); }
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
      <div class="observation">
        <h2>Qingyin Observation</h2>
        <dl>
          <dt>Mode</dt><dd>manual observation</dd>
          <dt>Body</dt><dd>symbolic sandbox body</dd>
          <dt>Position</dt><dd>[{{ ui.qingyin_observation.pos[0] }}, {{ ui.qingyin_observation.pos[1] }}]</dd>
          <dt>Facing</dt><dd>{{ ui.qingyin_observation.facing }}</dd>
          <dt>Front symbol</dt><dd>{{ ui.qingyin_observation.front_symbol }} {{ ui.qingyin_observation.front_label }}</dd>
          <dt>Visible symbols</dt><dd>{% if ui.qingyin_observation.visible_symbol_labels %}{{ ui.qingyin_observation.visible_symbol_labels | join(', ') }}{% else %}none{% endif %}</dd>
          <dt>Last action</dt><dd>{{ ui.qingyin_observation.last_action }}</dd>
          <dt>Last result</dt><dd>{{ ui.qingyin_observation.last_result }}</dd>
          <dt>Effects</dt><dd>{% if ui.qingyin_observation.last_effects %}{{ ui.qingyin_observation.last_effects | join(', ') }}{% else %}none{% endif %}</dd>
          <dt>Failures</dt><dd>{% if ui.qingyin_observation.last_failures %}{{ ui.qingyin_observation.last_failures | join(', ') }}{% else %}none{% endif %}</dd>
          <dt>Cooldown</dt><dd>{{ "%.1f"|format(ui.qingyin_observation.cooldown_seconds) }}s, remaining {{ ui.qingyin_observation.cooldown_remaining_display }}s</dd>
          <dt>Can act</dt><dd>{{ ui.qingyin_observation.can_act_display }}</dd>
        </dl>
        <p>Manual observation only. No autonomy. No auto exploration. No LLM planning. No pathfinding.</p>
      </div>
      <div class="experiment">
        <h2>Instinct / Experience Observation</h2>
        <form method="post" action="{{ url_for('experiment_random_walk') }}">
          <label for="random_seed">Seed</label>
          <input id="random_seed" name="seed" type="number" step="1" value="{{ ui.experiment_observation.seed }}">
          <label for="random_max_steps">Max steps</label>
          <input id="random_max_steps" name="max_steps" type="number" min="0" step="1" value="{{ ui.experiment_observation.max_steps }}">
          <button>Run random walk sample</button>
        </form>
        <form method="post" action="{{ url_for('experiment_wall_influence') }}">
          <input name="seed" type="hidden" value="{{ ui.experiment_observation.seed }}">
          <input name="max_steps" type="hidden" value="{{ ui.experiment_observation.max_steps }}">
          <button>Run wall influence check</button>
        </form>
        <form method="post" action="{{ url_for('experiment_clear') }}">
          <button>Clear experiment observation</button>
        </form>
        <dl>
          <dt>Current experiment mode</dt><dd>{{ ui.experiment_observation.mode }}</dd>
          <dt>Random seed</dt><dd>{{ ui.experiment_observation.seed }}</dd>
          <dt>Max steps</dt><dd>{{ ui.experiment_observation.max_steps }}</dd>
          {% if ui.experiment_observation.random_walk %}
            <dt>Instinct Random Walk</dt><dd>sample shown</dd>
            <dt>Step count</dt><dd>{{ ui.experiment_observation.random_walk.step_count }}</dd>
            <dt>Wall blocked count</dt><dd>{{ ui.experiment_observation.random_walk.wall_blocked_count }}</dd>
            <dt>Item contact count</dt><dd>{{ ui.experiment_observation.random_walk.item_contact_count }}</dd>
            <dt>First item contact step</dt><dd>{{ ui.experiment_observation.random_walk.first_item_contact_step if ui.experiment_observation.random_walk.first_item_contact_step is not none else 'none' }}</dd>
            <dt>Experience count</dt><dd>{{ ui.experiment_observation.random_walk.experience_count }}</dd>
            <dt>Experience keys</dt><dd>{% if ui.experiment_observation.random_walk.experience_keys %}{{ ui.experiment_observation.random_walk.experience_keys | join(', ') }}{% else %}none{% endif %}</dd>
            <dt>Prior experience loaded</dt><dd>{{ ui.experiment_observation.random_walk.prior_experience_loaded | string | lower }}</dd>
            <dt>Experience influence enabled</dt><dd>{{ ui.experiment_observation.random_walk.experience_influence_enabled | string | lower }}</dd>
            <dt>Reward bias enabled</dt><dd>{{ ui.experiment_observation.random_walk.reward_bias_enabled | string | lower }}</dd>
            <dt>Dopamine_like_signal enabled</dt><dd>{{ ui.experiment_observation.random_walk.dopamine_like_signal_enabled | string | lower }}</dd>
          {% endif %}
          {% if ui.experiment_observation.wall_influence %}
            <dt>Wall Experience Influence</dt><dd>check shown</dd>
            <dt>No-experience control</dt><dd>{{ 'passed' if ui.experiment_observation.wall_influence.control_passed else 'failed' }}</dd>
            <dt>With-prior-experience influence</dt><dd>{{ 'passed' if ui.experiment_observation.wall_influence.influence_passed else 'failed' }}</dd>
            <dt>Selected action without experience</dt><dd>{{ ui.experiment_observation.wall_influence.selected_action_without_experience }}</dd>
            <dt>Selected action with wall experience</dt><dd>{{ ui.experiment_observation.wall_influence.selected_action_with_wall_experience }}</dd>
            <dt>Experience used for decision</dt><dd>{{ ui.experiment_observation.wall_influence.experience_used_for_decision | string | lower }}</dd>
            <dt>Influence type</dt><dd>{{ ui.experiment_observation.wall_influence.influence_type }}</dd>
            <dt>Item reward bias</dt><dd>{{ ui.experiment_observation.wall_influence.item_reward_bias_enabled | string | lower }}</dd>
            <dt>Dopamine_like_signal</dt><dd>{{ ui.experiment_observation.wall_influence.dopamine_like_signal_enabled | string | lower }}</dd>
          {% endif %}
          <dt>Wall influence enabled</dt><dd>{{ ui.experiment_observation.boundary_check.wall_experience_influence_ui_observation_enabled | string | lower }}</dd>
          <dt>Reward bias enabled</dt><dd>{{ ui.experiment_observation.boundary_check.item_reward_bias_enabled | string | lower }}</dd>
          <dt>Dopamine_like_signal enabled</dt><dd>{{ ui.experiment_observation.boundary_check.dopamine_like_signal_enabled | string | lower }}</dd>
        </dl>
        <p>No continuous loop. No auto exploration. No pathfinding. No reward bias.</p>
      </div>
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
