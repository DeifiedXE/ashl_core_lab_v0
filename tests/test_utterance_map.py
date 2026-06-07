import unittest

from ashl_core.first_output_runtime import UTTERANCE_MAP, generate_minimal_first_output


class MinimalNonLlmUtteranceMapTests(unittest.TestCase):
    def test_default_first_output_remains_star(self):
        result = generate_minimal_first_output(session_id="final_check", state_key=None)

        self.assertEqual(result["first_output"], "*")
        self.assertEqual(result["first_output_trace"]["first_output"], "*")
        self.assertIsNone(result["state_key"])
        self.assertIs(result["llm_used"], False)

    def test_state_key_unknown_maps_to_utterance(self):
        result = generate_minimal_first_output(session_id="final_check", state_key="unknown")
        trace = result["first_output_trace"]

        self.assertEqual(result["first_output"], UTTERANCE_MAP["unknown"])
        self.assertEqual(trace["first_output"], UTTERANCE_MAP["unknown"])
        self.assertEqual(trace["state_key"], "unknown")
        self.assertEqual(trace["utterance_source"], "utterance_map")
        self.assertIs(trace["llm_used"], False)

    def test_supported_state_keys_map_to_expected_utterances(self):
        self.assertEqual(
            UTTERANCE_MAP,
            {
                "unknown": "我不知道",
                "blocked": "不行",
                "observed": "看到了",
                "retry": "再一次",
                "quiet": "……",
            },
        )
        for state_key, utterance in UTTERANCE_MAP.items():
            with self.subTest(state_key=state_key):
                result = generate_minimal_first_output(state_key=state_key)

                self.assertEqual(result["first_output"], utterance)
                self.assertEqual(result["first_output_trace"]["first_output"], utterance)
                self.assertEqual(result["first_output_trace"]["state_key"], state_key)
                self.assertEqual(result["first_output_trace"]["utterance_source"], "utterance_map")

    def test_invalid_state_key_raises_value_error(self):
        with self.assertRaises(ValueError):
            generate_minimal_first_output(state_key="random_invalid")

    def test_utterance_map_does_not_use_llm(self):
        result = generate_minimal_first_output(state_key="unknown")
        trace = result["first_output_trace"]

        self.assertIs(result["llm_used"], False)
        self.assertIs(trace["llm_used"], False)
        self.assertNotEqual(trace["output_generator_source"], "llm")


if __name__ == "__main__":
    unittest.main()
