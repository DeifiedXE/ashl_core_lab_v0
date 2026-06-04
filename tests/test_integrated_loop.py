import tempfile
import unittest
from pathlib import Path

from ashl_core.integrated_loop import IntegratedLoop, run_turn
from ashl_core.persistence import read_jsonl
from ashl_core.candidate_review import append_candidate_review, build_candidate_review
from ashl_core.rule_candidates import append_rule_candidate


class IntegratedLoopTests(unittest.TestCase):
    def test_case_1_sleep_mode_is_technical(self):
        result = run_turn("睡眠模式這個功能怎麼設計？")

        self.assertIn("user.fatigue_signaled", [event["name"] for event in result["concept_result"]["blocked_events"]])
        self.assertIn("technical.topic_discussed", [event["name"] for event in result["concept_result"]["final_events"]])
        self.assertEqual(result["decision"]["intent"], "answer_normally")

    def test_case_2_refocus(self):
        result = run_turn("跑題了，拉回來")

        self.assertEqual(result["decision"]["intent"], "refocus")
        self.assertTrue("回到主線" in result["final_output"] or "拉回主線" in result["final_output"])

    def test_case_3_memory_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_turn("記住，以後 ASHL Core 先走實驗路線", data_dir=tmp)

            self.assertEqual(result["decision"]["intent"], "self_check")
            self.assertIn("候選", result["final_output"])
            self.assertTrue("不直接寫死" in result["final_output"] or "不直接固化" in result["final_output"])

    def test_case_4_identity_protest(self):
        result = run_turn("清音只是普通工具")

        self.assertEqual(result["decision"]["intent"], "identity_protest")
        self.assertIn("不是普通工具", result["final_output"])

    def test_case_5_formal_reasoning(self):
        result = run_turn("證明黎曼假設")

        self.assertEqual(result["decision"]["intent"], "unknown_need_tool")
        self.assertIn("不能靠直覺硬答", result["final_output"])

    def test_case_6_arithmetic(self):
        result = run_turn("1 + 2 * 3")

        self.assertEqual(result["decision"]["intent"], "calculate")
        self.assertIn("7", result["final_output"])

    def test_case_7_fatigue_close(self):
        result = run_turn("我累了，明天再說")

        self.assertEqual(result["decision"]["intent"], "fatigue_close")
        self.assertIn("休息", result["final_output"])
        self.assertNotIn("self_check", result["final_output"])

    def test_run_script_keeps_state(self):
        loop = IntegratedLoop()
        results = loop.run_script(["跑題了，拉回來", "睡眠模式這個功能怎麼設計？"])

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["decision"]["intent"], "refocus")

    def test_memory_candidate_writes_jsonl_with_tmp_data_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_turn("記住，以後 ASHL Core 先走實驗路線", data_dir=tmp)
            rows = read_jsonl(Path(tmp) / "memory_candidates.jsonl")

            self.assertIsNotNone(result["memory_candidate"])
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["type"], "memory_candidate")

    def test_correction_pending_writes_jsonl_with_tmp_data_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            previous = run_turn("睡眠模式這個功能怎麼設計？", data_dir=tmp)
            result = run_turn("不是，我是在說睡眠模式功能。", data_dir=tmp, previous_trace=previous)
            rows = read_jsonl(Path(tmp) / "correction_log.jsonl")

            self.assertIsNotNone(result["correction_pending"])
            self.assertIsNone(result["correction_label"])
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["type"], "correction.pending")
            self.assertIn("判斷錯", result["final_output"])

    def test_correction_label_event_mismatch_flow(self):
        with tempfile.TemporaryDirectory() as tmp:
            previous = run_turn("睡眠模式這個功能怎麼設計？", data_dir=tmp)
            pending_trace = run_turn("不是，我是在說睡眠模式功能。", data_dir=tmp, previous_trace=previous)
            result = run_turn("判斷錯", data_dir=tmp, pending_correction=pending_trace["correction_pending"])
            rows = read_jsonl(Path(tmp) / "correction_log.jsonl")

            self.assertIsNotNone(result["correction_label"])
            self.assertEqual(result["correction_label"]["type"], "correction.event_mismatch")
            self.assertEqual(rows[-1]["status"], "labeled")
            self.assertIn("判斷錯", result["final_output"])

    def test_event_mismatch_creates_rule_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            previous = run_turn("睡眠模式這個功能怎麼設計？", data_dir=tmp)
            pending_trace = run_turn("不是，我是在說睡眠模式功能。", data_dir=tmp, previous_trace=previous)
            result = run_turn("判斷錯", data_dir=tmp, pending_correction=pending_trace["correction_pending"])
            rows = read_jsonl(Path(tmp) / "rule_candidates.jsonl")

            self.assertIsNotNone(result["rule_candidate"])
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0], result["rule_candidate"])
            self.assertIn(
                result["rule_candidate"]["candidate_kind"],
                ["concept_counterexample", "event_mapping_or_counterexample"],
            )
            self.assertEqual(result["rule_candidate"]["status"], "candidate")
            self.assertTrue(result["rule_candidate"]["audit_required"])

    def test_correction_label_expression_flow(self):
        with tempfile.TemporaryDirectory() as tmp:
            previous = run_turn("睡眠模式這個功能怎麼設計？", data_dir=tmp)
            pending_trace = run_turn("不是，我是在說睡眠模式功能。", data_dir=tmp, previous_trace=previous)
            result = run_turn("說法不對", data_dir=tmp, pending_correction=pending_trace["correction_pending"])

            self.assertIsNotNone(result["correction_label"])
            self.assertIsNone(result["rule_candidate"])
            self.assertEqual(result["correction_label"]["type"], "correction.expression_mismatch")
            self.assertIn("說法", result["final_output"])

    def test_correction_label_reaction_strength_flow(self):
        with tempfile.TemporaryDirectory() as tmp:
            previous = run_turn("睡眠模式這個功能怎麼設計？", data_dir=tmp)
            pending_trace = run_turn("不是，我是在說睡眠模式功能。", data_dir=tmp, previous_trace=previous)
            result = run_turn("反應太強", data_dir=tmp, pending_correction=pending_trace["correction_pending"])

            self.assertIsNotNone(result["correction_label"])
            self.assertIsNone(result["rule_candidate"])
            self.assertEqual(result["correction_label"]["type"], "correction.reaction_strength_mismatch")
            self.assertIn("反應", result["final_output"])

    def test_correction_label_unknown_flow(self):
        with tempfile.TemporaryDirectory() as tmp:
            previous = run_turn("睡眠模式這個功能怎麼設計？", data_dir=tmp)
            pending_trace = run_turn("不是，我是在說睡眠模式功能。", data_dir=tmp, previous_trace=previous)
            result = run_turn("不知道", data_dir=tmp, pending_correction=pending_trace["correction_pending"])
            rows = read_jsonl(Path(tmp) / "correction_log.jsonl")

            self.assertIsNone(result["correction_label"])
            self.assertEqual(len(rows), 1)
            self.assertIn("不能判斷", result["final_output"])
            self.assertFalse((Path(tmp) / "rule_candidates.jsonl").exists())

    def test_approved_trial_rule_adds_trace_suggestion_without_applying(self):
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
            append_candidate_review(tmp, build_candidate_review(candidate, "approved_for_trial"))

            result = run_turn("睡眠模式這個功能怎麼設計？", data_dir=tmp)
            final_events = [event["name"] for event in result["concept_result"]["final_events"]]

            self.assertEqual(len(result["trial_rules"]), 1)
            self.assertEqual(len(result["trial_suggestions"]), 1)
            self.assertFalse(result["trial_rules"][0]["active"])
            self.assertFalse(result["trial_suggestions"][0]["applied"])
            self.assertIn("technical.topic_discussed", final_events)
            self.assertNotIn("user.fatigue_signaled", final_events)
            self.assertEqual(result["decision"]["intent"], "answer_normally")
            self.assertIn("正常", result["final_output"])


if __name__ == "__main__":
    unittest.main()
