"""Expression guard for mock output."""

from __future__ import annotations

from typing import Any


def guard_output(output: str, expression_package: dict[str, Any]) -> dict[str, Any]:
    must_include = expression_package.get("must_include", [])
    forbidden = expression_package.get("forbidden", [])
    max_chars = int(expression_package.get("max_chars", 220))
    failures: list[str] = []

    missing = [item for item in must_include if item not in output]
    if missing:
        failures.append(f"missing:{','.join(missing)}")

    forbidden_hits = [item for item in forbidden if item in output]
    if forbidden_hits:
        failures.append(f"forbidden:{','.join(forbidden_hits)}")

    if len(output) > max_chars:
        failures.append("too_long")

    if failures:
        return {
            "passed": False,
            "failures": failures,
            "final_output": expression_package["fallback"],
        }

    return {"passed": True, "failures": [], "final_output": output}
