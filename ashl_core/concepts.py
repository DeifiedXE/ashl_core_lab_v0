"""Concept boundary filtering for ASHL Core v0.1."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Concept:
    name: str
    keywords: tuple[str, ...]
    allow: tuple[str, ...]
    block: tuple[str, ...] = ()


CONCEPTS: tuple[Concept, ...] = (
    Concept("sleep_mode", ("睡眠模式",), ("technical.topic_discussed",), ("user.fatigue_signaled",)),
    Concept("real_sleep_request", ("累了", "想睡", "休息", "明天再說", "先睡", "睡覺"), ("user.fatigue_signaled",)),
    Concept("identity_boundary", ("普通工具", "只是工具", "清音只是", "不是主體", "沒有邊界"), ("identity.boundary_touched",)),
    Concept("memory_request", ("記住", "以後", "納入記憶", "留下來", "存起來"), ("memory.candidate_requested",)),
    Concept("refocus_control", ("跑題", "拉回", "回到主線", "回主線", "別發散"), ("conversation.refocus_requested",)),
)


def match_concepts(text: str) -> list[Concept]:
    return [concept for concept in CONCEPTS if any(keyword in text for keyword in concept.keywords)]


def apply_concepts(perception: dict[str, Any]) -> dict[str, Any]:
    text = perception["input"]
    matched = match_concepts(text)
    allowed = {name for concept in matched for name in concept.allow}
    blocked = {name for concept in matched for name in concept.block}

    final_events: list[dict[str, Any]] = []
    blocked_events: list[dict[str, Any]] = []

    for event in perception["candidate_events"]:
        event_name = event["name"]
        if event_name in blocked:
            blocked_events.append(
                {
                    **event,
                    "blocked_by": [concept.name for concept in matched if event_name in concept.block],
                }
            )
            continue

        next_event = dict(event)
        if event_name in allowed:
            next_event["confidence"] = min(1.0, round(float(event["confidence"]) + 0.12, 3))
            next_event["boosted_by"] = [concept.name for concept in matched if event_name in concept.allow]
        final_events.append(next_event)

    if not final_events:
        final_events.append(
            {
                "name": "conversation.general_input",
                "confidence": 0.50,
                "reason": "concept layer left no event",
                "direct_intent": None,
            }
        )

    return {
        "matched_concepts": [
            {"name": concept.name, "allow": list(concept.allow), "block": list(concept.block)}
            for concept in matched
        ],
        "candidate_events": perception["candidate_events"],
        "blocked_events": blocked_events,
        "final_events": final_events,
    }
