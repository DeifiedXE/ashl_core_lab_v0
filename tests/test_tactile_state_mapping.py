import unittest

from ashl_core.first_output_runtime import UTTERANCE_MAP, generate_minimal_first_output
from ashl_core.tactile_state_mapping import TACTILE_RESULT_TO_STATE_KEY, map_tactile_result_to_state_key


class TactileStateMappingTests(unittest.TestCase):
    def test_tactile_results_map_to_state_keys(self):
        self.assertEqual(
            TACTILE_RESULT_TO_STATE_KEY,
            {
                "wall_blocked": "blocked",
                "box_blocked": "blocked",
                "box_contact": "observed",
                "box_pushed": "observed",
                "goal_reached": "observed",
                "empty": "quiet",
            },
        )

    def test_wall_blocked_maps_to_blocked(self):
        self.assertEqual(map_tactile_result_to_state_key("wall_blocked"), "blocked")

    def test_box_blocked_maps_to_blocked(self):
        self.assertEqual(map_tactile_result_to_state_key("box_blocked"), "blocked")

    def test_box_contact_maps_to_observed(self):
        self.assertEqual(map_tactile_result_to_state_key("box_contact"), "observed")

    def test_box_pushed_maps_to_observed(self):
        self.assertEqual(map_tactile_result_to_state_key("box_pushed"), "observed")

    def test_goal_reached_maps_to_observed(self):
        self.assertEqual(map_tactile_result_to_state_key("goal_reached"), "observed")

    def test_empty_maps_to_quiet(self):
        self.assertEqual(map_tactile_result_to_state_key("empty"), "quiet")

    def test_invalid_tactile_result_raises_value_error(self):
        with self.assertRaises(ValueError):
            map_tactile_result_to_state_key("random_invalid")

    def test_blocked_state_key_maps_to_non_llm_utterance(self):
        state_key = map_tactile_result_to_state_key("box_blocked")
        result = generate_minimal_first_output(state_key=state_key)

        self.assertEqual(state_key, "blocked")
        self.assertEqual(UTTERANCE_MAP["blocked"], "不行")
        self.assertEqual(result["first_output"], "不行")
        self.assertEqual(result["first_output_trace"]["utterance_source"], "utterance_map")
        self.assertIs(result["first_output_trace"]["llm_used"], False)

    def test_observed_and_quiet_state_keys_map_to_utterances(self):
        observed_key = map_tactile_result_to_state_key("goal_reached")
        quiet_key = map_tactile_result_to_state_key("empty")

        self.assertEqual(generate_minimal_first_output(state_key=observed_key)["first_output"], "看到了")
        self.assertEqual(generate_minimal_first_output(state_key=quiet_key)["first_output"], "……")


if __name__ == "__main__":
    unittest.main()
