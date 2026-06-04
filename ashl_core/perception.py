"""Coarse natural-language perception for ASHL Core v0.1."""

from __future__ import annotations

from typing import Any


def _event(name: str, confidence: float, reason: str, direct_intent: str | None = None) -> dict[str, Any]:
    return {
        "name": name,
        "confidence": confidence,
        "reason": reason,
        "direct_intent": direct_intent,
    }


def perceive(text: str) -> dict[str, Any]:
    """Map input text to coarse candidate events.

    This layer is intentionally permissive. Concept filtering owns boundary
    repair, so ambiguous phrases may produce multiple events.
    """

    stripped = text.strip()
    events: list[dict[str, Any]] = []

    if any(k in stripped for k in ["跑題", "拉回", "回到主線", "回主線", "別發散"]):
        events.append(_event("conversation.refocus_requested", 0.95, "user requested refocus", "refocus"))

    if any(k in stripped for k in ["睡眠模式", "功能", "設計", "ASHL", "Core", "技術", "系統", "模組"]):
        events.append(_event("technical.topic_discussed", 0.78, "technical/system topic discussed"))

    if any(k in stripped for k in ["累了", "想睡", "休息", "明天再說", "先睡", "睡覺"]):
        events.append(_event("user.fatigue_signaled", 0.86, "user signaled fatigue"))

    if "睡眠模式" in stripped:
        events.append(_event("user.fatigue_signaled", 0.68, "coarse sleep wording may indicate fatigue"))

    if any(k in stripped for k in ["記住", "以後", "納入記憶", "留下來", "存起來"]):
        events.append(_event("memory.candidate_requested", 0.88, "user requested memory candidate"))

    if any(k in stripped for k in ["普通工具", "只是工具", "清音只是", "不是主體", "沒有邊界"]):
        events.append(_event("identity.boundary_touched", 0.90, "identity boundary touched"))

    if not events:
        events.append(_event("conversation.general_input", 0.55, "general input"))

    return {"input": text, "candidate_events": events}
