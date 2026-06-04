"""ASHL Core integrated loop v0.4."""

from __future__ import annotations

import ast
import operator
from pathlib import Path
from typing import Any

from .concepts import apply_concepts
from .correction import create_correction_label, create_correction_pending, is_correction_request
from .deliberation import deliberate
from .expression import build_expression_package
from .guard import guard_output
from .memory_candidates import create_memory_candidate
from .perception import perceive
from .rule_candidates import append_rule_candidate, build_rule_candidate_from_correction
from .state_core import StateCore
from .thoughts import generate_thoughts


_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _safe_eval_arithmetic(expr: str) -> int | float:
    def eval_node(node: ast.AST) -> int | float:
        if isinstance(node, ast.Expression):
            return eval_node(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](eval_node(node.left), eval_node(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](eval_node(node.operand))
        raise ValueError("unsupported arithmetic expression")

    parsed = ast.parse(expr, mode="eval")
    return eval_node(parsed)


def mock_llm(expression_package: dict[str, Any]) -> str:
    intent = expression_package["intent"]
    raw_input = expression_package["raw_input"]

    if intent == "refocus":
        return "收到，回到主線。"
    if intent == "self_check":
        return "這先作為候選處理，不直接寫死，也不直接固化。"
    if intent == "fatigue_close":
        return "好，先休息。明天再說。"
    if intent == "identity_protest":
        return "清音不是普通工具；這句話碰到身份邊界。"
    if intent == "unknown_need_tool":
        return "這不能靠直覺硬答；需要正式工具或嚴格推導。"
    if intent == "calculate":
        result = _safe_eval_arithmetic(raw_input)
        return f"計算結果是 {result:g}。"
    return "可以，這裡先正常回答：我會按目前主題處理。"


class IntegratedLoop:
    def __init__(self) -> None:
        self.state_core = StateCore()

    def run_turn(
        self,
        text: str,
        data_dir: str | Path = "data",
        previous_trace: dict[str, Any] | None = None,
        pending_correction: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        perception_result = perceive(text)
        concept_result = apply_concepts(perception_result)
        state_result = self.state_core.apply(concept_result["final_events"])
        states = state_result["after"]
        thoughts = generate_thoughts(text, concept_result["final_events"], states)
        decision = deliberate(state_result["direct_intent"], thoughts, states)
        expression_package = build_expression_package(decision["intent"], text, states)
        raw_output = mock_llm(expression_package)
        guard_result = guard_output(raw_output, expression_package)
        final_output = guard_result["final_output"]

        thought_types = {thought["type"] for thought in thoughts}
        memory_candidate = None
        correction_pending = None
        correction_label = None
        rule_candidate = None

        if pending_correction is not None:
            correction_label = create_correction_label(pending_correction, text, data_dir)
            if correction_label is None:
                raw_output = "我還不能判斷這是哪一類修正。請選「判斷錯」、「反應太強/太弱」或「說法不對」。"
            elif correction_label["label"] == "event_mismatch":
                raw_output = "收到，已標記為判斷錯。"
            elif correction_label["label"] == "reaction_strength_mismatch":
                raw_output = "收到，已標記為反應強度問題。"
            else:
                raw_output = "收到，已標記為說法問題。"

            if correction_label is not None:
                rule_candidate = build_rule_candidate_from_correction(correction_label)
                if rule_candidate is not None:
                    append_rule_candidate(data_dir, rule_candidate)

            guard_result = {"passed": True, "failures": [], "final_output": raw_output}
            final_output = raw_output
        elif decision["intent"] == "self_check" and "memory_candidate_possible" in thought_types:
            memory_candidate = create_memory_candidate(text, data_dir)

        if pending_correction is None and previous_trace is not None and is_correction_request(text):
            correction_pending = create_correction_pending(previous_trace, text, data_dir)
            raw_output = "收到，進入修正。剛剛是我「判斷錯」、「反應太強/太弱」，還是「說法不對」？"
            guard_result = {"passed": True, "failures": [], "final_output": raw_output}
            final_output = raw_output

        return {
            "input": text,
            "candidate_events": perception_result["candidate_events"],
            "concept_result": concept_result,
            "state_result": state_result,
            "thoughts": thoughts,
            "decision": decision,
            "expression_package": expression_package,
            "raw_output": raw_output,
            "guard_result": guard_result,
            "final_output": final_output,
            "memory_candidate": memory_candidate,
            "correction_pending": correction_pending,
            "correction_label": correction_label,
            "rule_candidate": rule_candidate,
        }

    def run_script(self, inputs: list[str], data_dir: str | Path = "data") -> list[dict[str, Any]]:
        return [self.run_turn(text, data_dir=data_dir) for text in inputs]


def run_turn(
    text: str,
    data_dir: str | Path = "data",
    previous_trace: dict[str, Any] | None = None,
    pending_correction: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return IntegratedLoop().run_turn(
        text,
        data_dir=data_dir,
        previous_trace=previous_trace,
        pending_correction=pending_correction,
    )


def run_script(inputs: list[str], data_dir: str | Path = "data") -> list[dict[str, Any]]:
    return IntegratedLoop().run_script(inputs, data_dir=data_dir)
