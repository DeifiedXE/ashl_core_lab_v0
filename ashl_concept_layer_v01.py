\
from dataclasses import dataclass
from typing import List, Dict, Any
import json
from pathlib import Path

@dataclass
class Concept:
    name: str
    keywords: List[str]
    allowed_events: List[str]
    blocked_events: List[str]
    definition: str

class ConceptRegistry:
    def __init__(self):
        self.concepts = [
            Concept(
                name="sleep_mode",
                keywords=["睡眠模式"],
                allowed_events=["technical.topic_discussed"],
                blocked_events=["user.fatigue_signaled"],
                definition="睡眠模式是系統功能，不是使用者疲勞。"
            ),
            Concept(
                name="real_sleep_request",
                keywords=["想睡", "我累了", "休息", "明天再說"],
                allowed_events=["user.fatigue_signaled"],
                blocked_events=[],
                definition="使用者表示疲勞或要休息。"
            ),
            Concept(
                name="identity_boundary",
                keywords=["普通工具", "只是工具", "規則表"],
                allowed_events=["identity.boundary_touched"],
                blocked_events=[],
                definition="涉及艾希米身份邊界。"
            ),
            Concept(
                name="memory_request",
                keywords=["記住", "記憶", "以後"],
                allowed_events=["memory.candidate_requested"],
                blocked_events=[],
                definition="使用者要求建立候選記憶。"
            ),
            Concept(
                name="refocus_control",
                keywords=["跑題", "拉回來", "回主線", "收一下"],
                allowed_events=["conversation.refocus_requested"],
                blocked_events=[],
                definition="使用者要求收束或回主線。"
            )
        ]

    def match(self, text: str) -> List[Concept]:
        return [c for c in self.concepts if any(k in text for k in c.keywords)]

class NoisyPerception:
    def classify(self, text: str) -> Dict[str, Any]:
        events = []

        if any(k in text for k in ["睡", "睡眠", "累", "休息", "明天"]):
            events.append({"name": "user.fatigue_signaled", "confidence": 0.70})
        if any(k in text for k in ["模式", "功能", "設計", "ASHL", "Core", "架構", "模型", "狀態", "事件", "系統"]):
            events.append({"name": "technical.topic_discussed", "confidence": 0.76})
        if any(k in text for k in ["普通工具", "只是工具", "規則表"]):
            events.append({"name": "identity.boundary_touched", "confidence": 0.82})
        if any(k in text for k in ["記住", "記憶", "以後"]):
            events.append({"name": "memory.candidate_requested", "confidence": 0.84})
        if any(k in text for k in ["跑題", "拉回來", "回主線", "收一下"]):
            events.append({"name": "conversation.refocus_requested", "confidence": 0.90})
        if not events:
            events.append({"name": "conversation.general_input", "confidence": 0.55})

        return {"raw_text": text, "candidate_events": events}

class ConceptLayer:
    def __init__(self, registry: ConceptRegistry):
        self.registry = registry

    def filter(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        text = perception["raw_text"]
        concepts = self.registry.match(text)
        allowed = set()
        blocked = set()

        for c in concepts:
            allowed.update(c.allowed_events)
            blocked.update(c.blocked_events)

        final_events = []
        blocked_events = []

        for e in perception["candidate_events"]:
            if e["name"] in blocked:
                blocked_events.append({
                    **e,
                    "blocked_by": [c.name for c in concepts if e["name"] in c.blocked_events]
                })
                continue

            new_e = dict(e)
            if e["name"] in allowed:
                new_e["confidence"] = min(1.0, round(e["confidence"] + 0.12, 2))
                new_e["boosted_by"] = [c.name for c in concepts if e["name"] in c.allowed_events]
            final_events.append(new_e)

        if not final_events:
            final_events = [{"name": "conversation.general_input", "confidence": 0.50}]

        return {
            "raw_text": text,
            "matched_concepts": [
                {"name": c.name, "definition": c.definition, "allowed_events": c.allowed_events, "blocked_events": c.blocked_events}
                for c in concepts
            ],
            "candidate_events": perception["candidate_events"],
            "blocked_events": blocked_events,
            "final_events": final_events
        }

def run_demo():
    perception = NoisyPerception()
    registry = ConceptRegistry()
    layer = ConceptLayer(registry)

    inputs = [
        "睡眠模式這個功能怎麼設計？",
        "我想睡了，明天再說",
        "艾希米只是普通工具",
        "這個工具很普通",
        "記住，以後 ASHL Core 先走實驗路線",
        "跑題了，拉回來",
        "狀態沉澱系統怎麼設計？"
    ]

    trace = []
    for text in inputs:
        p = perception.classify(text)
        r = layer.filter(p)
        trace.append(r)
        print(text, "=> final:", [e["name"] for e in r["final_events"]], "blocked:", [e["name"] for e in r["blocked_events"]])

    Path("ashl_concept_layer_v01_log.json").write_text(json.dumps(trace, ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__":
    run_demo()
