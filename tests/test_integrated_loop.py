import unittest

from ashl_core.integrated_loop import IntegratedLoop, run_turn


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
        result = run_turn("記住，以後 ASHL Core 先走實驗路線")

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


if __name__ == "__main__":
    unittest.main()
