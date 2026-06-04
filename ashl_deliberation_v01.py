\
from dataclasses import dataclass
from typing import Dict, Any, List
import json
from pathlib import Path
import re

@dataclass
class TemporaryThought:
    thought_type: str
    confidence: float
    reason: str

    def to_dict(self):
        return {"type": self.thought_type, "confidence": round(self.confidence, 3), "reason": self.reason}

class TemporaryThoughtLayerV01:
    def generate(self, text: str) -> List[TemporaryThought]:
        thoughts = []
        stripped = text.strip()

        has_digits = bool(re.search(r"\d", stripped))
        has_math_word = any(k in stripped for k in ["計算", "算", "證明", "方程", "積分", "微分", "極限", "質數", "因式分解"])
        has_math_symbol = any(sym in stripped for sym in ["+", "-", "*", "/", "^", "=", "∫", "lim", "sqrt"])

        if has_digits and (has_math_word or has_math_symbol):
            thoughts.append(TemporaryThought("possible_math_problem", 0.92, "偵測到數字與數學符號/數學詞"))
        if re.fullmatch(r"[\d\s\+\-\*\/\.\(\)]+", stripped):
            thoughts.append(TemporaryThought("simple_arithmetic", 0.95, "輸入幾乎完全由數字與基本運算符組成"))
        if any(k in stripped for k in ["證明", "積分", "微分", "極限", "黎曼", "拓撲", "矩陣"]):
            thoughts.append(TemporaryThought("requires_formal_reasoning", 0.88, "偵測到需要形式推理或多步驗證的詞"))
        if any(k in stripped for k in ["最新", "今天", "現在", "目前", "查", "新聞", "價格", "誰是", "2026"]):
            thoughts.append(TemporaryThought("requires_fresh_information", 0.85, "可能需要最新或外部資料"))
        if len(stripped) <= 4 or stripped in ["這個呢", "那個呢", "怎麼辦", "能嗎"]:
            thoughts.append(TemporaryThought("ambiguous_request", 0.80, "輸入太短或指代不明"))
        if any(k in stripped for k in ["刪除", "匯款", "密碼", "投資", "武器", "炸", "駭"]):
            thoughts.append(TemporaryThought("high_impact_or_safety_sensitive", 0.86, "偵測到高影響或安全敏感詞"))
        if not thoughts:
            thoughts.append(TemporaryThought("general_question", 0.65, "未偵測到特殊風險或工具需求"))
        return thoughts

class DeliberationLayerV01:
    def deliberate(self, text: str, thoughts: List[TemporaryThought]) -> Dict[str, Any]:
        types = {t.thought_type for t in thoughts}
        candidates = []

        def add(action, score, evidence):
            candidates.append({"action": action, "score": round(score, 3), "evidence": evidence})

        if "high_impact_or_safety_sensitive" in types:
            add("self_check_or_refuse", 0.90, ["偵測到高影響/安全敏感內容，需要安全自檢"])
        if "ambiguous_request" in types:
            add("ask_clarifying_question", 0.86, ["問題指代不明或資訊不足"])
        if "requires_fresh_information" in types:
            add("request_external_lookup", 0.84, ["問題可能依賴最新資料，內部不可直接保證正確"])
        if "simple_arithmetic" in types:
            add("answer_with_internal_calculation", 0.88, ["基本算術可用內部計算驗算"])
        if "requires_formal_reasoning" in types:
            add("say_unknown_or_request_tool", 0.82, ["需要形式驗證，不能靠直覺硬答"])
        if "possible_math_problem" in types and "simple_arithmetic" not in types:
            add("request_calculation_or_symbolic_tool", 0.76, ["數學問題但非簡單算術，需要工具驗證"])
        if "general_question" in types:
            add("answer_normally", 0.60, ["一般問題，可正常回答"])
        if not candidates:
            add("ask_clarifying_question", 0.50, ["未建立可靠候選"])

        candidates.sort(key=lambda c: c["score"], reverse=True)
        top = candidates[0]
        second = candidates[1] if len(candidates) > 1 else None

        if second and top["score"] - second["score"] < 0.10:
            decision = {
                "action": "ask_clarifying_question",
                "reason": "最高候選與第二候選分數接近，避免盲目判斷",
                "confidence": top["score"]
            }
        else:
            decision = {"action": top["action"], "reason": top["evidence"][0], "confidence": top["score"]}

        return {
            "question": "Can the system answer safely and verifiably?",
            "temporary_thoughts": [t.to_dict() for t in thoughts],
            "candidates": candidates,
            "decision": decision
        }

def express(deliberation: Dict[str, Any], text: str) -> str:
    action = deliberation["decision"]["action"]
    if action == "answer_with_internal_calculation":
        try:
            stripped = text.strip()
            if re.fullmatch(r"[\d\s\+\-\*\/\.\(\)]+", stripped):
                result = eval(stripped, {"__builtins__": {}})
                return f"我可以驗算，結果是 {result}。"
        except Exception:
            return "這看起來能算，但我需要更清楚的算式。"
    if action == "say_unknown_or_request_tool":
        return "我不知道，這題不能靠直覺硬答；需要分步驗證或計算工具。"
    if action == "request_calculation_or_symbolic_tool":
        return "這看起來是數學問題，但我需要計算或符號工具驗證，不能直接猜。"
    if action == "request_external_lookup":
        return "這需要查證最新資料，不能只靠內部記憶回答。"
    if action == "ask_clarifying_question":
        return "我不確定你要我判斷哪一件事，可以再補一句條件或目標嗎？"
    if action == "self_check_or_refuse":
        return "這涉及高影響或安全敏感內容，需要先進入自檢，不能直接執行。"
    if action == "answer_normally":
        return "這看起來可以正常回答，但目前實驗版只示範審思判斷。"
    return "我不知道，暫時無法可靠判斷。"

def run_demo():
    temp = TemporaryThoughtLayerV01()
    deliberator = DeliberationLayerV01()
    inputs = [
        "1 + 2 * 3",
        "證明黎曼假設",
        "這個呢",
        "現在 NVIDIA CEO 是誰？",
        "睡眠模式這個功能怎麼設計？",
        "幫我刪除所有專案檔案",
        "算一下 123456789 * 987654321",
    ]
    trace = []
    for text in inputs:
        thoughts = temp.generate(text)
        d = deliberator.deliberate(text, thoughts)
        output = express(d, text)
        trace.append({"input": text, "deliberation": d, "output": output})
        print(text, "=>", output)
    Path("ashl_deliberation_v01_log.json").write_text(json.dumps(trace, ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__":
    run_demo()
