\
from dataclasses import dataclass
from typing import List, Dict, Any
import json
from pathlib import Path

@dataclass
class CorrectionPending:
    previous_input: str
    previous_events: List[str]
    previous_intent: str
    previous_output: str
    user_correction: str
    options: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "correction.pending",
            "previous_input": self.previous_input,
            "previous_events": self.previous_events,
            "previous_intent": self.previous_intent,
            "previous_output": self.previous_output,
            "user_correction": self.user_correction,
            "needs_user_label": True,
            "options": self.options
        }

class CorrectionDetectorV01:
    correction_keywords = [
        "不是",
        "不對",
        "錯了",
        "我不是這個意思",
        "你理解錯了",
        "不是這樣",
        "不是啦"
    ]

    def is_correction(self, text: str) -> bool:
        return any(k in text for k in self.correction_keywords)

class CorrectionPromptV01:
    def build_pending(self, last_trace: Dict[str, Any], user_text: str) -> CorrectionPending:
        return CorrectionPending(
            previous_input=last_trace["input"],
            previous_events=last_trace["events"],
            previous_intent=last_trace["intent"],
            previous_output=last_trace["output"],
            user_correction=user_text,
            options=[
                "event_mismatch",
                "reaction_strength_mismatch",
                "expression_mismatch"
            ]
        )

    def ask(self) -> str:
        return "收到，進入修正。剛剛是我「判斷錯」、「反應太強/太弱」，還是「說法不對」？"

def run_demo():
    detector = CorrectionDetectorV01()
    prompt = CorrectionPromptV01()
    last = {
        "input": "睡眠模式這個功能怎麼設計？",
        "events": ["user.fatigue_signaled"],
        "intent": "fatigue_close",
        "output": "停。現在該休息，這個明天再接。"
    }
    user_text = "不是，我是在說睡眠模式功能。"
    if detector.is_correction(user_text):
        pending = prompt.build_pending(last, user_text)
        result = {"ask": prompt.ask(), "correction_log": pending.to_dict()}
    else:
        result = {"ask": None, "correction_log": None}

    print(json.dumps(result, ensure_ascii=False, indent=2))
    Path("ashl_correction_prompt_v01_log.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__":
    run_demo()
