"""ASHL Core integrated loop v0.1."""

from __future__ import annotations

import ast
import operator
from typing import Any

from .concepts import apply_concepts
from .deliberation import deliberate
from .expression import build_expression_package
from .guard import guard_output
from .perception import perceive
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

    def run_turn(self, text: str) -> dict[str, Any]:
        perception_result = perceive(text)
        concept_result = apply_concepts(perception_result)
        state_result = self.state_core.apply(concept_result["final_events"])
        states = state_result["after"]
        thoughts = generate_thoughts(text, concept_result["final_events"], states)
        decision = deliberate(state_result["direct_intent"], thoughts, states)
        expression_package = build_expression_package(decision["intent"], text, states)
        raw_output = mock_llm(expression_package)
        guard_result = guard_output(raw_output, expression_package)

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
            "final_output": guard_result["final_output"],
        }

    def run_script(self, inputs: list[str]) -> list[dict[str, Any]]:
        return [self.run_turn(text) for text in inputs]


def run_turn(text: str) -> dict[str, Any]:
    return IntegratedLoop().run_turn(text)


def run_script(inputs: list[str]) -> list[dict[str, Any]]:
    return IntegratedLoop().run_script(inputs)
