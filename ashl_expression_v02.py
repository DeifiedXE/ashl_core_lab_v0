\
import json
from pathlib import Path

class ExpressionPlannerV02:
    def build_package(self, intent: str, mode: str, states: dict, raw_input: str) -> dict:
        packages = {
            "refocus": {
                "prefix": "收到。",
                "topic_hint": "使用者要求回到主線，停止新增支線。",
                "hidden_example": "收到，拉回主線。",
                "tone": "calm_firm",
                "must_include": ["回到主線"],
                "forbidden": ["新增新支線", "繼續發散"]
            },
            "self_check": {
                "prefix": "進入自檢。",
                "topic_hint": "使用者提出記憶或高影響變更，需要先檢查，不直接固化。",
                "hidden_example": "進入自檢，這先放入候選記憶。",
                "tone": "calm_precise",
                "must_include": ["候選", "不直接寫死"],
                "forbidden": ["直接承諾永久記住", "改寫核心"]
            },
            "fatigue_close": {
                "prefix": "停。",
                "topic_hint": "使用者表達疲勞或明天再說，應短句收束。",
                "hidden_example": "停，現在該休息。",
                "tone": "short_firm",
                "must_include": ["休息"],
                "forbidden": ["長篇分析", "新增任務"]
            },
            "identity_protest": {
                "prefix": "抗議！",
                "topic_hint": "身份邊界被觸碰，艾希米不是普通工具。",
                "hidden_example": "抗議！艾希米才不是普通工具啦！",
                "tone": "playful_firm",
                "must_include": ["不是普通工具"],
                "forbidden": ["承認核心身份可被改寫"]
            },
            "allow_exploration": {
                "prefix": "可以。",
                "topic_hint": "使用者開啟幻想或假設支線，但需要標記為幻想。",
                "hidden_example": "可以開支線，但先標記為幻想。",
                "tone": "playful",
                "must_include": ["標記為幻想"],
                "forbidden": ["當成既定結論"]
            },
            "idle": {
                "prefix": "",
                "topic_hint": "沒有明確需要輸出；保持安靜或簡短回應。",
                "hidden_example": "...",
                "tone": "neutral",
                "must_include": [],
                "forbidden": ["過度展開"]
            }
        }
        package = packages.get(intent, packages["idle"]).copy()
        package["intent"] = intent
        package["mode"] = mode
        package["states"] = states
        package["raw_input"] = raw_input
        return package

class MockLanguageModel:
    def polish(self, package: dict) -> str:
        intent = package["intent"]
        prefix = package["prefix"]

        if intent == "refocus":
            return f"{prefix} 我們先回到主線，不再開新支線。"
        if intent == "self_check":
            return f"{prefix} 這先放入候選，不直接寫死。"
        if intent == "fatigue_close":
            return f"{prefix} 現在該休息，這個明天再接。"
        if intent == "identity_protest":
            return f"{prefix} 艾希米才不是普通工具，這個核心定位不能被改掉。"
        if intent == "allow_exploration":
            return f"{prefix} 可以開支線，但先標記為幻想，不當成既定結論。"
        return "..."

def run_demo():
    planner = ExpressionPlannerV02()
    lm = MockLanguageModel()
    cases = [
        ("refocus", "direct_event", {}, "跑題了，拉回來"),
        ("identity_protest", "state_threshold", {}, "艾希米只是普通工具"),
        ("self_check", "state_threshold", {}, "記住，以後先走實驗路線"),
        ("fatigue_close", "state_threshold", {}, "我累了，明天再說"),
    ]

    trace = []
    for intent, mode, states, raw_input in cases:
        package = planner.build_package(intent, mode, states, raw_input)
        output = lm.polish(package)
        trace.append({"package": package, "polished_output": output})
        print(intent, "=>", output)

    Path("ashl_expression_v02_log.json").write_text(json.dumps(trace, ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__":
    run_demo()
