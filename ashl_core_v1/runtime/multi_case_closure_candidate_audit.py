"""Audit multi-case task closures and learning candidates for ASHL Core v1."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ashl_core_v1.runtime.multi_case_cradle_task_suite import (
    load_last_multi_case_cradle_task_suite_summary,
)


MULTI_CASE_CLOSURE_CANDIDATE_AUDIT_ENV = (
    "ASHL_CORE_V1_MULTI_CASE_CLOSURE_CANDIDATE_AUDIT_DIR"
)
DEFAULT_MULTI_CASE_CLOSURE_CANDIDATE_AUDIT_DIR = (
    Path(__file__).resolve().parents[1] / "data" / "multi_case_closure_candidate_audit"
)

LAST_MULTI_CASE_CLOSURE_CANDIDATE_AUDIT_FILE = (
    "last_multi_case_closure_candidate_audit.json"
)
MULTI_CASE_CLOSURE_CANDIDATE_AUDIT_HISTORY_FILE = (
    "multi_case_closure_candidate_audit_history.jsonl"
)

EXPECTED_CASE_CANDIDATE_KINDS: dict[str, tuple[str, ...]] = {
    "blocked_front_obstacle": ("blocked_front_obstacle", "repeated_blocked"),
    "success_simple_reach": ("successful_path", "success_simple_reach"),
    "unknown_needs_observe": ("unknown_resolved", "needs_observe"),
    "teacher_stopped": ("teacher_stopped",),
    "suspended_waiting_for_teacher": ("suspended", "waiting_for_teacher"),
    "conflict_expected_vs_actual": (
        "expected_vs_actual_mismatch",
        "conflict_detected",
    ),
}


def build_multi_case_closure_candidate_audit(
    suite_run_payload: dict[str, Any] | None,
) -> dict[str, Any]:
    if suite_run_payload is None:
        return _record(
            suite_run_id=None,
            case_runs=[],
            status="blocked_missing_suite_run",
            notes=("suite run missing",),
        )
    case_runs = list(suite_run_payload.get("case_runs") or [])
    suite_run_id = suite_run_payload.get("suite_summary", {}).get("suite_run_id")
    status = _audit_status(case_runs)
    notes = (status,) if status != "passed" else ("passed", "all case closures and candidates are consistent")
    return _record(
        suite_run_id=suite_run_id,
        case_runs=case_runs,
        status=status,
        notes=notes,
    )


def run_multi_case_closure_candidate_audit(
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    suite = load_last_multi_case_cradle_task_suite_summary(base_dir)
    audit = build_multi_case_closure_candidate_audit(suite)
    return save_multi_case_closure_candidate_audit(audit, base_dir)


def save_multi_case_closure_candidate_audit(
    audit: dict[str, Any],
    base_dir: str | Path | None = None,
) -> dict[str, Any]:
    audit_dir = ensure_multi_case_closure_candidate_audit_store(base_dir)
    (audit_dir / LAST_MULTI_CASE_CLOSURE_CANDIDATE_AUDIT_FILE).write_text(
        json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    with (audit_dir / MULTI_CASE_CLOSURE_CANDIDATE_AUDIT_HISTORY_FILE).open(
        "a",
        encoding="utf-8",
        newline="\n",
    ) as file:
        file.write(json.dumps(audit, ensure_ascii=False, sort_keys=True))
        file.write("\n")
    return dict(audit)


def load_last_multi_case_closure_candidate_audit(
    base_dir: str | Path | None = None,
) -> dict[str, Any] | None:
    path = (
        resolve_multi_case_closure_candidate_audit_dir(base_dir)
        / LAST_MULTI_CASE_CLOSURE_CANDIDATE_AUDIT_FILE
    )
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def list_multi_case_closure_candidate_audits(
    base_dir: str | Path | None = None,
) -> list[dict[str, Any]]:
    path = (
        resolve_multi_case_closure_candidate_audit_dir(base_dir)
        / MULTI_CASE_CLOSURE_CANDIDATE_AUDIT_HISTORY_FILE
    )
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def resolve_multi_case_closure_candidate_audit_dir(
    base_dir: str | Path | None = None,
) -> Path:
    if base_dir is not None:
        return Path(base_dir)
    env_value = os.environ.get(MULTI_CASE_CLOSURE_CANDIDATE_AUDIT_ENV)
    if env_value:
        return Path(env_value)
    return DEFAULT_MULTI_CASE_CLOSURE_CANDIDATE_AUDIT_DIR


def ensure_multi_case_closure_candidate_audit_store(
    base_dir: str | Path | None = None,
) -> Path:
    audit_dir = resolve_multi_case_closure_candidate_audit_dir(base_dir)
    audit_dir.mkdir(parents=True, exist_ok=True)
    (audit_dir / MULTI_CASE_CLOSURE_CANDIDATE_AUDIT_HISTORY_FILE).touch(exist_ok=True)
    return audit_dir


def _record(
    *,
    suite_run_id: str | None,
    case_runs: list[dict[str, Any]],
    status: str,
    notes: tuple[str, ...],
) -> dict[str, Any]:
    case_ids = tuple(case_run.get("case_id") for case_run in case_runs)
    cases_failed = tuple(_failed_cases(case_runs))
    cases_passed = tuple(case_id for case_id in case_ids if case_id not in cases_failed)
    missing_candidate_cases = tuple(_missing_candidate_cases(case_runs))
    return {
        "audit_id": _new_audit_id(),
        "suite_run_id": suite_run_id,
        "case_count": len(case_runs),
        "cases_checked": list(case_ids),
        "cases_passed": list(cases_passed),
        "cases_failed": list(cases_failed),
        "all_cases_have_closure": all(_closure(case_run) for case_run in case_runs),
        "all_cases_have_disposition": all(_disposition(case_run) for case_run in case_runs),
        "all_candidates_review_required": all(
            candidate.get("review_required") is True
            for candidate in _all_candidates(case_runs)
        ),
        "all_candidates_source_traced": all(
            bool(candidate.get("source_trace_refs")) for candidate in _all_candidates(case_runs)
        ),
        "case_to_candidate_kinds": _case_to_candidate_kinds(case_runs),
        "missing_candidate_cases": list(missing_candidate_cases),
        "unexpected_candidate_cases": list(_unexpected_candidate_cases(case_runs)),
        "direct_memory_promotion_detected": any(
            bool(candidate.get("direct_memory_promotion"))
            or bool(_closure(case_run).get("task_run_closure_record", {}).get("direct_memory_promotion"))
            or bool(_disposition(case_run).get("direct_memory_promotion"))
            for case_run in case_runs
            for candidate in (_candidates(case_run) or [{}])
        ),
        "automatic_review_detected": any(
            bool(candidate.get("automatic_reviewed_digest_created"))
            or bool(_closure(case_run).get("task_run_closure_record", {}).get("automatic_reviewed_digest_created"))
            for case_run in case_runs
            for candidate in (_candidates(case_run) or [{}])
        ),
        "memory_write_detected": any(
            bool(candidate.get("memory_write"))
            or bool(_closure(case_run).get("task_run_closure_record", {}).get("memory_write"))
            or bool(_disposition(case_run).get("memory_write"))
            for case_run in case_runs
            for candidate in (_candidates(case_run) or [{}])
        ),
        "audit_status": status,
        "audit_notes": list(notes),
        "created_at": _now(),
    }


def _audit_status(case_runs: list[dict[str, Any]]) -> str:
    if not case_runs:
        return "blocked_missing_suite_run"
    if not all(_closure(case_run) for case_run in case_runs):
        return "blocked_missing_case_closure"
    if not all(_disposition(case_run) for case_run in case_runs):
        return "blocked_missing_disposition"
    if _missing_candidate_cases(case_runs):
        return "blocked_missing_candidate"
    if not all(candidate.get("review_required") is True for candidate in _all_candidates(case_runs)):
        return "blocked_candidate_not_review_required"
    if not all(bool(candidate.get("source_trace_refs")) for candidate in _all_candidates(case_runs)):
        return "blocked_missing_source_trace"
    if _unexpected_candidate_cases(case_runs):
        return "blocked_missing_candidate"
    if any(
        bool(candidate.get("direct_memory_promotion"))
        or bool(_closure(case_run).get("task_run_closure_record", {}).get("direct_memory_promotion"))
        or bool(_disposition(case_run).get("direct_memory_promotion"))
        for case_run in case_runs
        for candidate in (_candidates(case_run) or [{}])
    ):
        return "blocked_direct_memory_promotion_detected"
    if any(
        bool(candidate.get("automatic_reviewed_digest_created"))
        or bool(_closure(case_run).get("task_run_closure_record", {}).get("automatic_reviewed_digest_created"))
        for case_run in case_runs
        for candidate in (_candidates(case_run) or [{}])
    ):
        return "blocked_automatic_review_detected"
    if any(
        bool(candidate.get("memory_write"))
        or bool(_closure(case_run).get("task_run_closure_record", {}).get("memory_write"))
        or bool(_disposition(case_run).get("memory_write"))
        for case_run in case_runs
        for candidate in (_candidates(case_run) or [{}])
    ):
        return "blocked_memory_write_detected"
    return "passed"


def _closure(case_run: dict[str, Any]) -> dict[str, Any]:
    return dict(case_run.get("task_run_closure") or {})


def _disposition(case_run: dict[str, Any]) -> dict[str, Any]:
    return dict(_closure(case_run).get("task_run_disposition_record") or {})


def _candidates(case_run: dict[str, Any]) -> list[dict[str, Any]]:
    return list(_closure(case_run).get("task_learning_digest_candidate_records") or [])


def _all_candidates(case_runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [candidate for case_run in case_runs for candidate in _candidates(case_run)]


def _case_to_candidate_kinds(case_runs: list[dict[str, Any]]) -> dict[str, list[str]]:
    return {
        str(case_run.get("case_id")): [
            candidate.get("candidate_kind") for candidate in _candidates(case_run)
        ]
        for case_run in case_runs
    }


def _missing_candidate_cases(case_runs: list[dict[str, Any]]) -> list[str]:
    missing: list[str] = []
    for case_run in case_runs:
        case_id = str(case_run.get("case_id"))
        expected = set(EXPECTED_CASE_CANDIDATE_KINDS.get(case_id, ()))
        actual = {candidate.get("candidate_kind") for candidate in _candidates(case_run)}
        if expected and not expected.intersection(actual):
            missing.append(case_id)
    return missing


def _unexpected_candidate_cases(case_runs: list[dict[str, Any]]) -> list[str]:
    unexpected: list[str] = []
    for case_run in case_runs:
        case_id = str(case_run.get("case_id"))
        if case_id not in EXPECTED_CASE_CANDIDATE_KINDS:
            unexpected.append(case_id)
    return unexpected


def _failed_cases(case_runs: list[dict[str, Any]]) -> list[str]:
    failed = set(_missing_candidate_cases(case_runs))
    failed.update(_unexpected_candidate_cases(case_runs))
    return sorted(failed)


def _new_audit_id() -> str:
    return "multi_case_closure_candidate_audit_" + datetime.now(timezone.utc).strftime(
        "%Y%m%d%H%M%S%f"
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
