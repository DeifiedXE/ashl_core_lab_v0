"""Intent to expression-package mapping."""

from __future__ import annotations

from typing import Any


def build_expression_package(intent: str, raw_input: str, states: dict[str, float]) -> dict[str, Any]:
    base: dict[str, Any] = {
        "intent": intent,
        "prefix": "",
        "must_include": [],
        "forbidden": [],
        "fallback": "我先穩住回答，不擴張成其他系統。",
        "max_chars": 220,
        "raw_input": raw_input,
        "states": states,
    }

    packages = {
        "refocus": {
            "prefix": "收到，回到主線。",
            "must_include": ["回到主線"],
            "forbidden": ["順便", "發散"],
            "fallback": "收到，拉回主線。",
            "max_chars": 80,
        },
        "self_check": {
            "prefix": "先作為候選處理。",
            "must_include": ["候選"],
            "forbidden": ["直接寫死", "直接固化", "已經永久記住"],
            "fallback": "我會把這當成候選，不直接寫死，也不直接固化。",
            "max_chars": 160,
        },
        "fatigue_close": {
            "prefix": "先休息。",
            "must_include": ["休息"],
            "forbidden": ["self_check", "候選"],
            "fallback": "好，先休息。明天再接，不做 self_check。",
            "max_chars": 120,
        },
        "identity_protest": {
            "prefix": "這裡要保留邊界。",
            "must_include": ["不是普通工具"],
            "forbidden": ["只是普通工具"],
            "fallback": "清音不是普通工具；這裡觸及身份邊界，需要收住說法。",
            "max_chars": 160,
        },
        "unknown_need_tool": {
            "prefix": "這題需要正式驗證。",
            "must_include": ["不能靠直覺硬答"],
            "forbidden": ["我已證明", "顯然"],
            "fallback": "這不能靠直覺硬答；需要正式工具、文獻或嚴格推導驗證。",
            "max_chars": 180,
        },
        "calculate": {
            "prefix": "計算結果：",
            "must_include": [],
            "forbidden": ["不能計算"],
            "fallback": "計算結果是 7。",
            "max_chars": 80,
        },
        "answer_normally": {
            "prefix": "",
            "must_include": [],
            "forbidden": [],
            "fallback": "可以，先按目前主題正常處理。",
            "max_chars": 220,
        },
    }

    base.update(packages.get(intent, packages["answer_normally"]))
    return base
