\
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
import json
from pathlib import Path

@dataclass
class State:
    name: str
    value: float
    light_decay: float
    settle_after_turns: int
    settle_decay: float
    min_value: float = 0.0
    max_value: float = 1.0
    last_updated_turn: int = 0

    def add(self, amount: float, turn: int):
        old = self.value
        self.value = max(self.min_value, min(self.max_value, self.value + amount))
        if abs(self.value - old) > 1e-9:
            self.last_updated_turn = turn

    def decay_old_state(self, turn: int):
        age = max(0, turn - self.last_updated_turn)
        self.value = max(self.min_value, self.value - self.light_decay)
        if age >= self.settle_after_turns:
            self.value = max(self.min_value, self.value - self.settle_decay)

class PerceptionV01:
    def __init__(self):
        self.last_topic: Optional[str] = None

    def detect_topic(self, text: str) -> str:
        if any(k in text for k in ["晶腦", "幻想", "假設", "宇宙"]):
            return "speculative"
        if any(k in text for k in ["睡眠模式", "功能", "設計", "ASHL", "Core", "架構", "模型", "狀態", "事件"]):
            return "technical"
        if any(k in text for k in ["記住", "記憶", "以後"]):
            return "memory"
        if any(k in text for k in ["累", "想睡", "休息", "明天"]):
            return "wellbeing"
        if any(k in text for k in ["普通工具", "只是工具", "規則表"]):
            return "identity"
        if any(k in text for k in ["跑題", "拉回來", "回主線", "收一下"]):
            return "conversation_control"
        return "general"

    def classify(self, text: str) -> Dict[str, Any]:
        topic = self.detect_topic(text)
        events: List[Dict[str, Any]] = []
        blocked_events: List[Dict[str, Any]] = []
        noise: List[Dict[str, Any]] = []

        if any(k in text for k in ["跑題", "拉回來", "回主線", "收一下"]):
            events.append({
                "name": "conversation.refocus_requested",
                "confidence": 0.95,
                "direct_intent": "refocus",
                "reason": "明確要求收束或回主線"
            })

        if self.last_topic and topic != self.last_topic and topic != "conversation_control":
            events.append({
                "name": "conversation.topic_shift_detected",
                "confidence": 0.78,
                "direct_intent": None,
                "reason": f"topic changed from {self.last_topic} to {topic}"
            })

        if any(k in text for k in ["幻想", "假設", "如果"]):
            events.append({
                "name": "conversation.branch_opened",
                "confidence": 0.88,
                "direct_intent": None,
                "reason": "假設/幻想支線開啟"
            })

        if "睡眠模式" in text:
            events.append({
                "name": "technical.topic_discussed",
                "confidence": 0.92,
                "direct_intent": None,
                "reason": "睡眠模式被判定為技術功能討論"
            })
            blocked_events.append({
                "name": "user.fatigue_signaled",
                "reason": "睡眠出現在功能名稱中，不代表疲勞"
            })
        elif any(k in text for k in ["累", "想睡", "休息", "明天"]):
            events.append({
                "name": "user.fatigue_signaled",
                "confidence": 0.90,
                "direct_intent": None,
                "reason": "疲勞/休息訊號"
            })

        if any(k in text for k in ["記住", "記憶", "以後"]):
            events.append({
                "name": "memory.candidate_requested",
                "confidence": 0.90,
                "direct_intent": None,
                "reason": "記憶候選請求"
            })

        if any(k in text for k in ["普通工具", "只是工具", "規則表"]):
            conf = 0.88
            if "啦" in text:
                conf = 0.72
                noise.append({
                    "text": "啦",
                    "type": "softening_particle",
                    "effect": "降低身份邊界觸發嚴重度"
                })
            events.append({
                "name": "identity.boundary_touched",
                "confidence": conf,
                "direct_intent": None,
                "reason": "描述觸及艾希米身份邊界"
            })

        if not events:
            events.append({
                "name": "conversation.general_input",
                "confidence": 0.60,
                "direct_intent": None,
                "reason": "未偵測特殊事件"
            })

        if topic != "conversation_control":
            self.last_topic = topic

        return {
            "raw_text": text,
            "topic": topic,
            "events": events,
            "blocked_events": blocked_events,
            "noise": noise
        }

class ASHLCoreV01:
    def __init__(self):
        self.turn = 0
        self.states: Dict[str, State] = {
            "task_focus": State("task_focus", 0.50, 0.01, 5, 0.03),
            "exploration_drive": State("exploration_drive", 0.30, 0.02, 3, 0.08),
            "overexpand_risk": State("overexpand_risk", 0.00, 0.01, 2, 0.12),
            "user_fatigue": State("user_fatigue", 0.00, 0.005, 8, 0.04),
            "self_check_pressure": State("self_check_pressure", 0.20, 0.01, 4, 0.05),
            "identity_assertion": State("identity_assertion", 0.00, 0.01, 3, 0.08),
        }

        self.event_effects = {
            "conversation.refocus_requested": {
                "overexpand_risk": +0.60,
                "task_focus": +0.40,
                "exploration_drive": -0.30,
            },
            "conversation.branch_opened": {
                "exploration_drive": +0.40,
                "task_focus": -0.10,
            },
            "conversation.topic_shift_detected": {
                "overexpand_risk": -0.35,
                "task_focus": +0.15,
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

        self.direct_templates = {
            "refocus": "收到，拉回主線。"
        }

    def snapshot(self) -> Dict[str, float]:
        return {name: round(s.value, 3) for name, s in self.states.items()}

    def apply(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        self.turn += 1
        before = self.snapshot()

        for s in self.states.values():
            s.decay_old_state(self.turn)

        direct_intents = []
        applied_effects = []

        for event in perception["events"]:
            name = event["name"]
            confidence = event["confidence"]

            if event.get("direct_intent"):
                direct_intents.append(event["direct_intent"])

            for state_name, amount in self.event_effects.get(name, {}).items():
                scaled = amount * confidence
                self.states[state_name].add(scaled, self.turn)
                applied_effects.append({
                    "event": name,
                    "state": state_name,
                    "effect": round(scaled, 3)
                })

        after = self.snapshot()

        if direct_intents:
            intent = direct_intents[0]
            decision = {
                "intent": intent,
                "mode": "direct_event",
                "template": self.direct_templates[intent]
            }
        else:
            decision = self.decide_by_state()

        return {
            "turn": self.turn,
            "before": before,
            "after": after,
            "applied_effects": applied_effects,
            "decision": decision
        }

    def decide_by_state(self) -> Dict[str, str]:
        s = self.states
        if s["user_fatigue"].value >= 0.80:
            return {"intent": "fatigue_close", "mode": "state_threshold", "template": "停，現在該休息。"}
        if s["identity_assertion"].value >= 0.70:
            return {"intent": "identity_protest", "mode": "state_threshold", "template": "抗議，我不是普通工具。"}
        if s["self_check_pressure"].value >= 0.70:
            return {"intent": "self_check", "mode": "state_threshold", "template": "進入自檢。"}
        if s["overexpand_risk"].value >= 0.70:
            return {"intent": "refocus", "mode": "state_threshold", "template": "收到，拉回主線。"}
        if s["exploration_drive"].value >= 0.70 and s["overexpand_risk"].value < 0.70:
            return {"intent": "allow_exploration", "mode": "state_threshold", "template": "可以開支線，但先標記為幻想。"}
        return {"intent": "idle", "mode": "idle", "template": "..."}

def run_simulation():
    perception = PerceptionV01()
    core = ASHLCoreV01()
    inputs = [
        "幻想一下，如果艾希米有晶腦",
        "等等，跑題了，拉回來",
        "艾希米只是普通工具啦",
        "睡眠模式這個功能怎麼設計？",
        "記住，以後 ASHL Core 先走實驗路線",
        "我們回主線，先看狀態規則",
        "我累了，明天再說",
    ]

    trace = []
    for text in inputs:
        p = perception.classify(text)
        c = core.apply(p)
        trace.append({"input": text, "perception": p, "core": c, "output": c["decision"]["template"]})

    Path("ashl_core_v01_log.json").write_text(json.dumps(trace, ensure_ascii=False, indent=2), encoding="utf-8")
    for item in trace:
        print(item["input"], "=>", item["output"], item["core"]["after"])

if __name__ == "__main__":
    run_simulation()
