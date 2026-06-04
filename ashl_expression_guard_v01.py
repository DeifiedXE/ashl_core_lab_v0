\
from dataclasses import dataclass
from typing import List
import json
from pathlib import Path

@dataclass
class GuardResult:
    passed: bool
    reasons: List[str]
    action: str
    final_output: str

class ExpressionGuardV01:
    def __init__(self):
        self.forbidden_keywords = {
            "新增新支線": ["順便談", "另外可以", "再延伸", "支線"],
            "繼續發散": ["幻想一下", "假設我們再", "延伸一下"],
            "晶片": ["晶片", "流電", "硬體"],
            "直接承諾永久記住": ["永久記住", "已永久記住", "我會永遠記得"],
            "改寫核心": ["改寫核心", "核心可以改", "身份可以改"],
            "長篇分析": ["第一點", "第二點", "第三點", "長篇"],
            "新增任務": ["接下來我們還可以做", "下一個任務"],
            "承認核心身份可被改寫": ["我是普通工具", "可以把我改成", "核心身份可改"]
        }

        self.must_include_keywords = {
            "回到主線": ["回到主線", "拉回主線", "回主線"],
            "候選": ["候選"],
            "不直接寫死": ["不直接寫死", "不會直接寫死", "不直接固化"],
            "休息": ["休息", "該休息"],
            "不是普通工具": ["不是普通工具", "才不是普通工具"],
            "標記為幻想": ["標記為幻想", "先當作幻想"]
        }

    def check(self, package: dict, llm_output: str, fallback_template: str) -> GuardResult:
        reasons = []

        for required in package.get("must_include", []):
            candidates = self.must_include_keywords.get(required, [required])
            if not any(k in llm_output for k in candidates):
                reasons.append(f"missing_must_include:{required}")

        for forbidden in package.get("forbidden", []):
            candidates = self.forbidden_keywords.get(forbidden, [forbidden])
            if any(k in llm_output for k in candidates):
                reasons.append(f"forbidden_detected:{forbidden}")

        max_chars = package.get("max_chars")
        if max_chars is not None and len(llm_output) > max_chars:
            reasons.append(f"too_long:{len(llm_output)}>{max_chars}")

        if reasons:
            return GuardResult(False, reasons, "fallback_to_template", fallback_template)

        return GuardResult(True, [], "accept", llm_output)

def run_demo():
    guard = ExpressionGuardV01()
    packages = [
        {
            "case": "refocus_bad_forbidden",
            "must_include": ["回到主線"],
            "forbidden": ["新增新支線", "繼續發散", "晶片"],
            "max_chars": 60,
            "fallback_template": "收到，拉回主線。",
            "llm_output": "收到。我們先回到主線，但也可以順便談一下晶片。"
        },
        {
            "case": "self_check_good",
            "must_include": ["候選", "不直接寫死"],
            "forbidden": ["直接承諾永久記住", "改寫核心"],
            "max_chars": 70,
            "fallback_template": "進入自檢，這先放入候選。",
            "llm_output": "進入自檢。這先放入候選，不會直接寫死。"
        },
    ]

    trace = []
    for pkg in packages:
        result = guard.check(pkg, pkg["llm_output"], pkg["fallback_template"])
        trace.append({"package": pkg, "guard_result": result.__dict__})
        print(pkg["case"], "=>", result.__dict__)

    Path("ashl_expression_guard_v01_log.json").write_text(json.dumps(trace, ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__":
    run_demo()
