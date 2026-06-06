"""Minimal non-LLM first_output runtime for the test-object stage."""

from __future__ import annotations


DEFAULT_SESSION_ID = "first_output_session_v0"
TICK = 1
FIRST_OUTPUT = "*"
CORE_SEED_REFERENCE = "core_seed:first_output_v0"
UTTERANCE_MAP = {
    "unknown": "我不知道",
    "observed": "看到了",
    "retry": "再一次",
    "quiet": "……",
}


def generate_minimal_first_output(session_id: str = DEFAULT_SESSION_ID, state_key: str | None = None) -> dict:
    """Generate one fixed-reflex first_output and its trace.

    This is test-object engineering verification only. It does not call an LLM,
    write lesson or memory data, or connect learning pipelines.
    """
    if state_key is not None and state_key not in UTTERANCE_MAP:
        raise ValueError(f"unsupported state_key: {state_key}")

    resolved_session_id = session_id or DEFAULT_SESSION_ID
    first_output = FIRST_OUTPUT if state_key is None else UTTERANCE_MAP[state_key]
    output_generator_source = "simple_reflex_rule" if state_key is None else "utterance_map"
    output_kind = "fixed_reflex" if state_key is None else "mapped_utterance"
    minimal_state_snapshot = {
        "state_version": "first_output_v0",
        "tick": TICK,
        "phase": "test_object",
        "core_seed_reference": CORE_SEED_REFERENCE,
        "last_output_id": None,
        "random_seed": None,
        "state_key": state_key,
    }
    output_id = f"first_output:{resolved_session_id}:{TICK}"
    trace = {
        "trace_id": f"first_output_trace:{resolved_session_id}:{TICK}",
        "trace_type": "first_output_trace",
        "session_id": resolved_session_id,
        "tick": TICK,
        "phase": "test_object",
        "engineering_stage": "test_object",
        "output_id": output_id,
        "first_output": first_output,
        "output_kind": output_kind,
        "output_generator_source": output_generator_source,
        "utterance_source": output_generator_source,
        "state_key": state_key,
        "core_seed_reference": CORE_SEED_REFERENCE,
        "minimal_state_snapshot": minimal_state_snapshot,
        "llm_used": False,
        "created_at_or_tick": TICK,
    }
    return {
        "session_id": resolved_session_id,
        "tick": TICK,
        "minimal_state_snapshot": minimal_state_snapshot,
        "output_generator_source": output_generator_source,
        "utterance_source": output_generator_source,
        "state_key": state_key,
        "first_output": first_output,
        "first_output_trace": trace,
        "llm_used": False,
        "engineering_stage": "test_object",
    }
