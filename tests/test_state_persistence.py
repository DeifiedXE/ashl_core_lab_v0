import tempfile
import unittest
from pathlib import Path

from ashl_core.state_persistence import (
    LAST_TRACE_SUMMARY_FILE,
    SESSION_SUMMARY_FILE,
    STATE_SNAPSHOT_FILE,
    build_last_trace_summary,
    build_session_summary,
    build_state_snapshot,
    read_last_trace_summary,
    read_session_summary,
    read_state_snapshot,
    write_last_trace_summary,
    write_session_summary,
    write_state_snapshot,
)


class StatePersistenceTests(unittest.TestCase):
    def test_build_state_snapshot(self):
        states = {"task_focus": 0.5, "exploration_drive": 0.3}
        snapshot = build_state_snapshot(states, turn=3)

        self.assertEqual(snapshot["type"], "state_snapshot")
        self.assertEqual(snapshot["turn"], 3)
        self.assertEqual(snapshot["states"], states)
        self.assertIn("updated_at", snapshot)

    def test_write_and_read_state_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            snapshot = build_state_snapshot({"task_focus": 0.7}, turn=1)
            write_state_snapshot(tmp, snapshot)

            self.assertTrue((Path(tmp) / STATE_SNAPSHOT_FILE).exists())
            self.assertEqual(read_state_snapshot(tmp), snapshot)

    def test_read_missing_state_snapshot_returns_empty_dict(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(read_state_snapshot(tmp), {})

    def test_build_session_summary(self):
        summary = build_session_summary("session-a", 2, "input", "answer_normally", "output")

        self.assertEqual(summary["type"], "session_summary")
        self.assertEqual(summary["session_id"], "session-a")
        self.assertEqual(summary["turn_count"], 2)
        self.assertEqual(summary["last_intent"], "answer_normally")

    def test_write_and_read_session_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            summary = build_session_summary("session-a", 2, "輸入", "answer_normally", "輸出")
            write_session_summary(tmp, summary)

            self.assertTrue((Path(tmp) / SESSION_SUMMARY_FILE).exists())
            self.assertEqual(read_session_summary(tmp), summary)

    def test_read_missing_session_summary_returns_empty_dict(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(read_session_summary(tmp), {})

    def test_build_last_trace_summary(self):
        trace = {
            "input": "睡眠模式這個功能怎麼設計？",
            "decision": {"intent": "answer_normally"},
            "final_output": "正常回答",
            "concept_result": {
                "final_events": [
                    {"name": "technical.topic_discussed"},
                    {"name": "conversation.general_input"},
                ]
            },
            "memory_candidate": None,
            "correction_pending": {"type": "correction.pending"},
            "rule_candidate": None,
            "trial_suggestions": [{"type": "trial_suggestion"}],
            "trial_feedback": None,
            "thoughts": [{"large": "not persisted"}],
            "state_result": {"large": "not persisted"},
        }

        summary = build_last_trace_summary(trace)

        self.assertEqual(summary["type"], "last_trace_summary")
        self.assertEqual(summary["input"], trace["input"])
        self.assertEqual(summary["intent"], "answer_normally")
        self.assertEqual(summary["events"], ["technical.topic_discussed", "conversation.general_input"])
        self.assertFalse(summary["has_memory_candidate"])
        self.assertTrue(summary["has_correction_pending"])
        self.assertTrue(summary["has_trial_suggestions"])
        self.assertNotIn("thoughts", summary)
        self.assertNotIn("state_result", summary)
        self.assertNotIn("concept_result", summary)

    def test_write_and_read_last_trace_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            trace = {
                "input": "記住，以後 ASHL Core 先走實驗路線",
                "decision": {"intent": "self_check"},
                "final_output": "候選，不直接固化",
                "concept_result": {"final_events": [{"name": "memory.candidate_requested"}]},
                "memory_candidate": {"type": "memory_candidate"},
                "correction_pending": None,
                "rule_candidate": None,
                "trial_suggestions": [],
                "trial_feedback": None,
            }
            summary = build_last_trace_summary(trace)
            write_last_trace_summary(tmp, summary)

            self.assertTrue((Path(tmp) / LAST_TRACE_SUMMARY_FILE).exists())
            self.assertEqual(read_last_trace_summary(tmp), summary)

    def test_read_missing_last_trace_summary_returns_empty_dict(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(read_last_trace_summary(tmp), {})

    def test_utf8_chinese_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            summary = build_session_summary(
                "清音-session",
                1,
                "睡眠模式這個功能怎麼設計？",
                "answer_normally",
                "這是技術主題，不是休息要求。",
            )
            write_session_summary(tmp, summary)

            raw = (Path(tmp) / SESSION_SUMMARY_FILE).read_text(encoding="utf-8")
            self.assertIn("睡眠模式", raw)
            self.assertIn("清音", raw)
            self.assertEqual(read_session_summary(tmp), summary)


if __name__ == "__main__":
    unittest.main()
