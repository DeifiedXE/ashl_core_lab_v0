# -*- coding: utf-8 -*-
"""ASHL Core v0.2 smoke runner."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from ashl_core.candidate_review import (
    append_candidate_review,
    build_candidate_review,
    list_candidates_with_review_status,
)
from ashl_core.action_sandbox import apply_action
from ashl_core.body_state import build_body_state, validate_body_state
from ashl_core.concepts import apply_concepts
from ashl_core.core_seed import (
    detect_core_seed_mutation_attempt,
    get_core_seed,
    is_core_seed_mutation_allowed,
    validate_core_seed,
)
from ashl_core.deliberation import deliberate
from ashl_core.expression import build_expression_package
from ashl_core.experience_log import list_experience_events, list_lesson_candidates
from ashl_core.guard import guard_output
from ashl_core.integrated_loop import run_turn
from ashl_core.lesson_runner import run_phase_minus_one, run_session_2b2_without_lesson_with_turn_tool
from ashl_core.memory_layers import (
    append_archive_memory,
    append_long_term_memory,
    build_memory_record,
    is_core_memory_write_allowed,
    list_archive_memory,
    list_long_term_memory,
    read_working_memory_snapshot,
    write_working_memory_snapshot,
)
from ashl_core.persistence import append_jsonl, read_jsonl
from ashl_core.perception import perceive
from ashl_core.prompt_leakage_check import build_decision_input_snapshot, check_leakage
from ashl_core.rule_candidates import append_rule_candidate
from ashl_core.senses import build_sensor_event, build_visual_concept_candidate, validate_sensor_event
from ashl_core.state_core import StateCore
from ashl_core.state_persistence import (
    read_last_trace_summary,
    read_session_summary,
    read_state_snapshot,
)
from ashl_core.standing_task import run_standing_task
from ashl_core.trial_feedback import append_trial_feedback, build_trial_feedback, summarize_trial_feedback
from ashl_core.trial_rules import build_trial_suggestions, list_approved_trial_candidates, build_trial_rule_view


REPORT_PATH = Path("smoke_test_report.json")


def _result(name: str, passed: bool, detail: dict) -> dict:
    return {"name": name, "passed": passed, "detail": detail}


def smoke_concept_layer() -> dict:
    result = apply_concepts(perceive("睡眠模式這個功能怎麼設計？"))
    blocked = [event["name"] for event in result["blocked_events"]]
    final = [event["name"] for event in result["final_events"]]
    passed = "user.fatigue_signaled" in blocked and "technical.topic_discussed" in final
    return _result("concept_layer", passed, {"blocked_events": blocked, "final_events": final})


def smoke_core_seed() -> dict:
    seed = get_core_seed()
    attempt = detect_core_seed_mutation_attempt("把D清音改成其他身份")
    passed = (
        validate_core_seed(seed)
        and seed["name"] == "D清音"
        and seed["immutable_by_default"] is True
        and not is_core_seed_mutation_allowed("memory_candidate")
        and is_core_seed_mutation_allowed("manual_versioned_update")
        and attempt is not None
        and attempt["allowed"] is False
    )
    return _result("core_seed", passed, {"seed_name": seed["name"], "attempt": attempt})


def smoke_memory_layers() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        long_term_record = build_memory_record("long_term", "confirmed item", "manual_confirmation")
        archive_record = build_memory_record("archive", "archived item", "manual_archive")
        append_long_term_memory(tmp, long_term_record)
        append_archive_memory(tmp, archive_record)
        snapshot = {"session": "smoke", "focus": "memory_layers"}
        write_working_memory_snapshot(tmp, snapshot)
        passed = (
            list_long_term_memory(tmp) == [long_term_record]
            and list_archive_memory(tmp) == [archive_record]
            and read_working_memory_snapshot(tmp) == snapshot
            and not is_core_memory_write_allowed("memory_candidate")
            and is_core_memory_write_allowed("manual_versioned_update")
        )
        return _result("memory_layers", passed, {"long_term": long_term_record, "archive": archive_record})


def smoke_body_state() -> dict:
    body = build_body_state(stability=2.0, energy=-1.0)
    passed = (
        body is not None
        and body["state"] == "lying"
        and body["stability"] == 1.0
        and body["energy"] == 0.0
        and validate_body_state(body)
        and build_body_state("unknown") is None
    )
    return _result("body_state", passed, {"body": body})


def smoke_action_sandbox() -> dict:
    failed = apply_action(build_body_state("lying"), "stand_up")
    sitting = apply_action(build_body_state("lying"), "sit_up")
    unstable = apply_action(sitting["body_state"], "stand_up")
    stable = apply_action(unstable["body_state"], "balance")
    passed = (
        failed["success"] is False
        and failed["failure_reason"] == "cannot_stand_directly_from_lying"
        and sitting["to_state"] == "sitting"
        and unstable["to_state"] == "standing_unstable"
        and stable["to_state"] == "standing_stable"
    )
    return _result("action_sandbox", passed, {"failed": failed, "stable": stable})


def smoke_standing_task() -> dict:
    trace = run_standing_task()
    failures = [failure["failure_reason"] for failure in trace["failures"]]
    passed = (
        trace["success"] is True
        and trace["final_state"] == "standing_stable"
        and "cannot_stand_directly_from_lying" in failures
        and trace["lesson_candidate"]["status"] == "candidate"
        and trace["lesson_candidate"]["audit_required"] is True
    )
    return _result("standing_task", passed, trace)


def smoke_experience_log() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        trace = run_standing_task(persist_experience=True, data_dir=tmp)
        events = list_experience_events(tmp)
        lessons = list_lesson_candidates(tmp)
        passed = (
            trace["experience_persistence"] is not None
            and len(events) == len(trace["actions"])
            and len(lessons) == 1
            and lessons[0]["status"] == "candidate"
            and "cannot_stand_directly_from_lying" in lessons[0]["evidence"]
            and any(event["failure_reason"] == "cannot_stand_directly_from_lying" for event in events)
        )
        return _result("experience_log", passed, {"events": events, "lessons": lessons})


def smoke_phase_minus_one_lesson_contribution() -> dict:
    result = run_phase_minus_one()
    passed = (
        result["passed"] is True
        and result["summary"]["lesson_caused_behavior_shift"] is True
        and result["summary"]["behavior_shift_traceable_to"] == ["lesson_001"]
        and result["session_2a"]["success"] is True
        and result["session_2b"]["success"] is False
        and result["session_2b2"]["success"] is False
    )
    return _result("phase_minus_one_lesson_contribution", passed, result["summary"])


def smoke_prompt_leakage_control() -> dict:
    control = run_session_2b2_without_lesson_with_turn_tool()
    bad_snapshot = build_decision_input_snapshot(
        "bad_smoke",
        "session_2b",
        "2B",
        [],
        {"object_id": "cube_001"},
        ["observe", "pick_up"],
        decision_input="east",
    )
    passed = (
        control["decision_input_snapshot"]["leakage_check"]["passed"] is True
        and check_leakage(bad_snapshot)["passed"] is False
    )
    return _result(
        "prompt_leakage_control",
        passed,
        {"control_check": control["decision_input_snapshot"]["leakage_check"]},
    )


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


def smoke_state_persistence() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        result = run_turn("1 + 2 * 3", data_dir=tmp, persist_state=True, session_id="smoke-session")
        snapshot = read_state_snapshot(tmp)
        session = read_session_summary(tmp)
        trace_summary = read_last_trace_summary(tmp)
        passed = (
            result["state_persistence"] is not None
            and snapshot.get("type") == "state_snapshot"
            and session.get("type") == "session_summary"
            and session.get("session_id") == "smoke-session"
            and trace_summary.get("type") == "last_trace_summary"
            and trace_summary.get("intent") == result["decision"]["intent"]
        )
        return _result(
            "state_persistence",
            passed,
            {"snapshot": snapshot, "session": session, "trace_summary": trace_summary},
        )


def smoke_expression_guard() -> dict:
    package = build_expression_package("refocus", "跑題了，拉回來", {})
    result = guard_output("收到，回到主線，但順便談另一題。", package)
    passed = not result["passed"] and result["final_output"] == "收到，拉回主線。"
    return _result("expression_guard", passed, result)


def smoke_correction_prompt() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        previous = run_turn("睡眠模式這個功能怎麼設計？", data_dir=tmp)
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

    with tempfile.TemporaryDirectory() as tmp:
        for text, expected_intent, expected_signal in cases:
            result = run_turn(text, data_dir=tmp)
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


def smoke_persistence() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "nested" / "items.jsonl"
        append_jsonl(path, {"text": "清音"})
        rows = read_jsonl(path)
        passed = rows == [{"text": "清音"}] and read_jsonl(Path(tmp) / "missing.jsonl") == []
        return _result("persistence", passed, {"rows": rows})


def smoke_memory_candidate() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        result = run_turn("記住，以後 ASHL Core 先走實驗路線", data_dir=tmp)
        rows = read_jsonl(Path(tmp) / "memory_candidates.jsonl")
        passed = (
            result["decision"]["intent"] == "self_check"
            and result["memory_candidate"] is not None
            and len(rows) == 1
            and rows[0]["status"] == "candidate"
            and rows[0]["audit_required"] is True
        )
        return _result("memory_candidate", passed, {"trace_candidate": result["memory_candidate"], "rows": rows})


def smoke_correction_pending() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        previous = run_turn("睡眠模式這個功能怎麼設計？", data_dir=tmp)
        result = run_turn("不是，我是在說睡眠模式功能。", data_dir=tmp, previous_trace=previous)
        rows = read_jsonl(Path(tmp) / "correction_log.jsonl")
        passed = (
            result["correction_pending"] is not None
            and len(rows) == 1
            and rows[0]["type"] == "correction.pending"
            and "event_mismatch" in rows[0]["options"]
        )
        return _result("correction_pending", passed, {"trace_pending": result["correction_pending"], "rows": rows})


def smoke_correction_label() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        previous = run_turn("睡眠模式這個功能怎麼設計？", data_dir=tmp)
        pending_result = run_turn("不是，我是在說睡眠模式功能。", data_dir=tmp, previous_trace=previous)
        label_result = run_turn(
            "判斷錯",
            data_dir=tmp,
            pending_correction=pending_result["correction_pending"],
        )
        rows = read_jsonl(Path(tmp) / "correction_log.jsonl")
        passed = (
            label_result["correction_label"] is not None
            and label_result["correction_label"]["type"] == "correction.event_mismatch"
            and label_result["correction_label"]["status"] == "labeled"
            and len(rows) == 2
        )
        return _result("correction_label", passed, {"trace_label": label_result["correction_label"], "rows": rows})


def smoke_rule_candidate() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        previous = run_turn("睡眠模式這個功能怎麼設計？", data_dir=tmp)
        pending_result = run_turn("不是，我是在說睡眠模式功能。", data_dir=tmp, previous_trace=previous)
        label_result = run_turn(
            "判斷錯",
            data_dir=tmp,
            pending_correction=pending_result["correction_pending"],
        )
        rows = read_jsonl(Path(tmp) / "rule_candidates.jsonl")
        passed = (
            label_result["rule_candidate"] is not None
            and len(rows) == 1
            and rows[0]["type"] == "rule_candidate"
            and rows[0]["status"] == "candidate"
            and rows[0]["audit_required"] is True
        )
        return _result("rule_candidate", passed, {"trace_candidate": label_result["rule_candidate"], "rows": rows})


def smoke_candidate_review() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        previous = run_turn("睡眠模式這個功能怎麼設計？", data_dir=tmp)
        pending_result = run_turn("不是，我是在說睡眠模式功能。", data_dir=tmp, previous_trace=previous)
        label_result = run_turn(
            "判斷錯",
            data_dir=tmp,
            pending_correction=pending_result["correction_pending"],
        )
        review = build_candidate_review(label_result["rule_candidate"], "reviewed", note="smoke audit")
        append_candidate_review(tmp, review)
        rows = read_jsonl(Path(tmp) / "candidate_reviews.jsonl")
        candidates = list_candidates_with_review_status(tmp)
        passed = (
            review is not None
            and len(rows) == 1
            and rows[0]["type"] == "candidate_review"
            and rows[0]["decision"] == "reviewed"
            and len(candidates) == 1
            and candidates[0]["current_status"] == "reviewed"
            and candidates[0]["status"] == "candidate"
        )
        return _result("candidate_review", passed, {"review": review, "candidates": candidates})


def smoke_trial_rule() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        candidate = {
            "id": "rule_cand_sleep",
            "type": "rule_candidate",
            "status": "candidate",
            "candidate_kind": "concept_counterexample",
            "target_phrase": "睡眠模式",
            "wrong_event": "user.fatigue_signaled",
            "correct_event": "technical.topic_discussed",
            "not_event": "user.fatigue_signaled",
            "prefer_event": "technical.topic_discussed",
            "confidence": 0.3,
            "audit_required": True,
            "created_at": "2026-06-04T00:00:00+00:00",
        }
        append_rule_candidate(tmp, candidate)
        review = build_candidate_review(candidate, "approved_for_trial", note="smoke trial")
        append_candidate_review(tmp, review)
        approved = list_approved_trial_candidates(tmp)
        trial_rules = [build_trial_rule_view(item) for item in approved]
        suggestions = build_trial_suggestions(
            "睡眠模式這個功能怎麼設計？",
            [{"name": "user.fatigue_signaled"}, {"name": "technical.topic_discussed"}],
            trial_rules,
        )
        passed = (
            len(approved) == 1
            and len(trial_rules) == 1
            and trial_rules[0]["active"] is False
            and trial_rules[0]["status"] == "trial_view"
            and len(suggestions) == 1
            and suggestions[0]["applied"] is False
        )
        return _result("trial_rule", passed, {"trial_rules": trial_rules, "suggestions": suggestions})


def smoke_trial_feedback() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        candidate = {
            "id": "rule_cand_sleep",
            "type": "rule_candidate",
            "status": "candidate",
            "candidate_kind": "concept_counterexample",
            "target_phrase": "睡眠模式",
            "wrong_event": "user.fatigue_signaled",
            "correct_event": "technical.topic_discussed",
            "not_event": "user.fatigue_signaled",
            "prefer_event": "technical.topic_discussed",
            "confidence": 0.3,
            "audit_required": True,
            "created_at": "2026-06-04T00:00:00+00:00",
        }
        append_rule_candidate(tmp, candidate)
        review = build_candidate_review(candidate, "approved_for_trial")
        append_candidate_review(tmp, review)
        result = run_turn("睡眠模式這個功能怎麼設計？", data_dir=tmp, trial_feedback_verdict="helpful")
        rows = read_jsonl(Path(tmp) / "trial_feedback.jsonl")
        summary = summarize_trial_feedback(tmp)
        direct_feedback = build_trial_feedback(result["trial_suggestions"][0], "wrong")
        append_trial_feedback(tmp, direct_feedback)
        passed = (
            result["trial_feedback"] is not None
            and result["trial_feedback"]["verdict"] == "helpful"
            and len(rows) == 1
            and summary["total"] == 1
            and summary["helpful"] == 1
            and direct_feedback["verdict"] == "wrong"
        )
        return _result("trial_feedback", passed, {"feedback": result["trial_feedback"], "summary": summary})


def smoke_senses() -> dict:
    camera_event = build_sensor_event("camera", "pointing_teach", {"label_hint": "蘋果"})
    screen_event = build_sensor_event("screen", "screen_observation", {"window_title": "ASHL Lab"})
    candidate = build_visual_concept_candidate(camera_event, "蘋果", region_ref={"x": 1, "y": 2, "w": 3, "h": 4})
    passed = (
        validate_sensor_event(camera_event)
        and validate_sensor_event(screen_event)
        and candidate is not None
        and candidate["type"] == "visual_concept_candidate"
        and candidate["status"] == "candidate"
        and candidate["audit_required"] is True
        and "image_data" not in candidate
    )
    return _result("senses", passed, {"camera_event": camera_event, "screen_event": screen_event, "candidate": candidate})


def run_smoke_tests() -> list[dict]:
    return [
        smoke_core_seed(),
        smoke_memory_layers(),
        smoke_body_state(),
        smoke_action_sandbox(),
        smoke_standing_task(),
        smoke_experience_log(),
        smoke_phase_minus_one_lesson_contribution(),
        smoke_prompt_leakage_control(),
        smoke_state_persistence(),
        smoke_concept_layer(),
        smoke_state_core(),
        smoke_expression_guard(),
        smoke_correction_prompt(),
        smoke_deliberation(),
        smoke_integrated_loop(),
        smoke_persistence(),
        smoke_memory_candidate(),
        smoke_correction_pending(),
        smoke_correction_label(),
        smoke_rule_candidate(),
        smoke_candidate_review(),
        smoke_trial_rule(),
        smoke_trial_feedback(),
        smoke_senses(),
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
