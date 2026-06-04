"""Intent deliberation with explicit priority order."""

from __future__ import annotations

from typing import Any


def deliberate(direct_intent: str | None, thoughts: list[dict[str, Any]], states: dict[str, float]) -> dict[str, Any]:
    thought_types = {thought["type"] for thought in thoughts}

    if direct_intent:
        return {"intent": direct_intent, "reason": "direct_intent priority"}
    if "user_fatigue_possible" in thought_types or states.get("user_fatigue", 0.0) >= 0.70:
        return {"intent": "fatigue_close", "reason": "fatigue outranks self_check"}
    if "requires_formal_reasoning" in thought_types:
        return {"intent": "unknown_need_tool", "reason": "formal reasoning requires verification"}
    if "simple_arithmetic" in thought_types:
        return {"intent": "calculate", "reason": "simple arithmetic can be calculated"}
    if "memory_candidate_possible" in thought_types:
        return {"intent": "self_check", "reason": "memory candidates require self_check"}
    if states.get("identity_assertion", 0.0) >= 0.70:
        return {"intent": "identity_protest", "reason": "identity assertion high"}
    if states.get("self_check_pressure", 0.0) >= 0.70:
        return {"intent": "self_check", "reason": "self_check pressure high"}
    return {"intent": "answer_normally", "reason": "default"}
