"""State core for ASHL Core v0.1."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class StateValue:
    value: float
    light_decay: float = 0.01
    settle_after_turns: int = 4
    settle_decay: float = 0.04
    last_updated_turn: int = 0

    def decay(self, turn: int) -> None:
        self.value = max(0.0, self.value - self.light_decay)
        if turn - self.last_updated_turn >= self.settle_after_turns:
            self.value = max(0.0, self.value - self.settle_decay)

    def add(self, amount: float, turn: int) -> None:
        old = self.value
        self.value = max(0.0, min(1.0, self.value + amount))
        if abs(old - self.value) > 1e-9:
            self.last_updated_turn = turn


INITIAL_STATES = {
    "task_focus": 0.50,
    "exploration_drive": 0.30,
    "overexpand_risk": 0.00,
    "user_fatigue": 0.00,
    "self_check_pressure": 0.20,
    "identity_assertion": 0.00,
}

EVENT_EFFECTS = {
    "conversation.refocus_requested": {
        "overexpand_risk": +0.60,
        "task_focus": +0.40,
        "exploration_drive": -0.30,
    },
    "technical.topic_discussed": {
        "task_focus": +0.20,
        "exploration_drive": +0.10,
    },
    "user.fatigue_signaled": {
        "user_fatigue": +0.70,
        "exploration_drive": -0.40,
        "self_check_pressure": +0.20,
    },
    "memory.candidate_requested": {
        "self_check_pressure": +0.50,
    },
    "identity.boundary_touched": {
        "identity_assertion": +0.80,
        "self_check_pressure": +0.20,
    },
}


class StateCore:
    def __init__(self) -> None:
        self.turn = 0
        self.states = {name: StateValue(value) for name, value in INITIAL_STATES.items()}

    def snapshot(self) -> dict[str, float]:
        return {name: round(state.value, 3) for name, state in self.states.items()}

    def apply(self, final_events: list[dict[str, Any]]) -> dict[str, Any]:
        self.turn += 1
        before = self.snapshot()

        for state in self.states.values():
            state.decay(self.turn)

        applied_effects: list[dict[str, Any]] = []
        direct_intent = None

        for event in final_events:
            if event.get("direct_intent") and direct_intent is None:
                direct_intent = event["direct_intent"]

            confidence = float(event.get("confidence", 1.0))
            for state_name, amount in EVENT_EFFECTS.get(event["name"], {}).items():
                effect = amount * confidence
                self.states[state_name].add(effect, self.turn)
                applied_effects.append({"event": event["name"], "state": state_name, "effect": round(effect, 3)})

        return {
            "turn": self.turn,
            "before": before,
            "after": self.snapshot(),
            "applied_effects": applied_effects,
            "direct_intent": direct_intent,
        }
