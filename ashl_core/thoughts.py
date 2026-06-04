"""Temporary thought candidate generation."""

from __future__ import annotations

import re
from typing import Any


SIMPLE_ARITHMETIC_RE = re.compile(r"^[\d\s+\-*/().]+$")


def generate_thoughts(text: str, events: list[dict[str, Any]], states: dict[str, float]) -> list[dict[str, Any]]:
    stripped = text.strip()
    event_names = {event["name"] for event in events}
    thoughts: list[dict[str, Any]] = []

    def add(name: str, confidence: float, reason: str) -> None:
        thoughts.append({"type": name, "confidence": confidence, "reason": reason})

    if "memory.candidate_requested" in event_names:
        add("memory_candidate_possible", 0.92, "memory event survived concept filtering")
    if "identity.boundary_touched" in event_names:
        add("identity_boundary_touched", 0.90, "identity boundary event present")
    if "user.fatigue_signaled" in event_names or states.get("user_fatigue", 0.0) >= 0.65:
        add("user_fatigue_possible", 0.91, "fatigue event or high fatigue state")
    if any(k in stripped for k in ["證明", "黎曼假設", "嚴格推導", "定理", "反證"]):
        add("requires_formal_reasoning", 0.93, "formal proof requested")
    if SIMPLE_ARITHMETIC_RE.fullmatch(stripped) and any(ch.isdigit() for ch in stripped):
        add("simple_arithmetic", 0.96, "simple arithmetic expression")

    if not thoughts:
        add("normal_processing", 0.60, "no special temporary thought")

    return thoughts
