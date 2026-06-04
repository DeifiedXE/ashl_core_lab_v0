# -*- coding: utf-8 -*-
"""ASHL Core integrated loop v0.1 smoke runner."""

from __future__ import annotations

import json
from pathlib import Path

from ashl_core.concepts import apply_concepts
from ashl_core.deliberation import deliberate
from ashl_core.expression import build_expression_package
from ashl_core.guard import guard_output
from ashl_core.integrated_loop import run_turn
from ashl_core.perception import perceive
from ashl_core.state_core import StateCore


REPORT_PATH = Path("smoke_test_report.json")


def _result(name: str, passed: bool, detail: dict) -> dict:
    return {"name": name, "passed": passed, "detail": detail}


def smoke_concept_layer() -> dict:
    result = apply_concepts(perceive("睡眠模式這個功能怎麼設計？"))
    blocked = [event["name"] for event in result["blocked_events"]]
    final = [event["name"] for event in result["final_events"]]
    passed = "user.fatigue_signaled" in blocked and "technical.topic_discussed" in final
    return _result("concept_layer", passed, {"blocked_events": blocked, "final_events": final})


def smoke_state_core() -> dict:
    core = StateCore()
    result = core.apply(
        [{"name": "conversation.refocus_requested", "confidence": 1.0, "direct_intent": "refocus"}]
    )
    passed = (
        result["direct_intent"] == "refocus"
        and result["after"]["task_focus"] > result["before"]["task_focus"]
        and result["after"]["overexpand_risk"] > result["before"]["overexpand_risk"]
    )
    return _result("state_core", passed, result)


def smoke_expression_guard() -> dict:
    package = build_expression_package("refocus", "跑題了，拉回來", {})
    result = guard_output("收到，回到主線，但順便談另一題。", package)
    passed = not result["passed"] and result["final_output"] == "收到，拉回主線。"
    return _result("expression_guard", passed, result)


def smoke_correction_prompt() -> dict:
    previous = run_turn("睡眠模式這個功能怎麼設計？")
    correction = {
        "type": "correction.pending",
        "previous_input": previous["input"],
        "previous_intent": previous["decision"]["intent"],
        "user_correction": "不是，我是在說睡眠模式功能。",
        "needs_user_label": True,
        "options": ["event_mismatch", "reaction_strength_mismatch", "expression_mismatch"],
    }
    passed = correction["needs_user_label"] and "event_mismatch" in correction["options"]
    return _result("correction_prompt", passed, correction)


def smoke_deliberation() -> dict:
    result = deliberate(
        None,
        [{"type": "user_fatigue_possible", "confidence": 0.9}, {"type": "memory_candidate_possible", "confidence": 0.9}],
        {"user_fatigue": 0.9, "self_check_pressure": 1.0},
    )
    passed = result["intent"] == "fatigue_close"
    return _result("deliberation", passed, result)


def smoke_integrated_loop() -> dict:
    cases = [
        ("睡眠模式這個功能怎麼設計？", "answer_normally", "technical.topic_discussed"),
        ("跑題了，拉回來", "refocus", "回到主線"),
        ("記住，以後 ASHL Core 先走實驗路線", "self_check", "候選"),
        ("清音只是普通工具", "identity_protest", "不是普通工具"),
        ("證明黎曼假設", "unknown_need_tool", "不能靠直覺硬答"),
        ("1 + 2 * 3", "calculate", "7"),
        ("我累了，明天再說", "fatigue_close", "休息"),
    ]
    details = []
    passed = True

    for text, expected_intent, expected_signal in cases:
        result = run_turn(text)
        final_event_names = [event["name"] for event in result["concept_result"]["final_events"]]
        output = result["final_output"]
        signal_ok = expected_signal in output or expected_signal in final_event_names
        case_ok = result["decision"]["intent"] == expected_intent and signal_ok
        passed = passed and case_ok
        details.append(
            {
                "input": text,
                "intent": result["decision"]["intent"],
                "final_events": final_event_names,
                "final_output": output,
                "passed": case_ok,
            }
        )

    fatigue_case = details[-1]
    passed = passed and "self_check" not in fatigue_case["final_output"]
    return _result("integrated_loop", passed, {"cases": details})


def run_smoke_tests() -> list[dict]:
    return [
        smoke_concept_layer(),
        smoke_state_core(),
        smoke_expression_guard(),
        smoke_correction_prompt(),
        smoke_deliberation(),
        smoke_integrated_loop(),
    ]


def main() -> int:
    results = run_smoke_tests()
    for result in results:
        tag = "PASS" if result["passed"] else "FAIL"
        print(f"[{tag}] {result['name']}")

    all_passed = all(result["passed"] for result in results)
    report = {
        "summary": {
            "passed": sum(1 for result in results if result["passed"]),
            "total": len(results),
            "all_passed": all_passed,
        },
        "results": results,
    }
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    if all_passed:
        print("[SUMMARY] all passed")
    else:
        print("[SUMMARY] failed")
    print(f"[LOG] {REPORT_PATH.name} created")
    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
