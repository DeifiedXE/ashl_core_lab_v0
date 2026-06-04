import unittest

from ashl_core.state_core import StateCore


class StateCoreTests(unittest.TestCase):
    def test_refocus_event_changes_state_and_direct_intent(self):
        core = StateCore()
        result = core.apply(
            [
                {
                    "name": "conversation.refocus_requested",
                    "confidence": 1.0,
                    "direct_intent": "refocus",
                }
            ]
        )

        self.assertEqual(result["direct_intent"], "refocus")
        self.assertGreater(result["after"]["task_focus"], result["before"]["task_focus"])
        self.assertGreater(result["after"]["overexpand_risk"], result["before"]["overexpand_risk"])
        self.assertLess(result["after"]["exploration_drive"], result["before"]["exploration_drive"])

    def test_state_decay_runs(self):
        core = StateCore()
        first = core.apply([{"name": "conversation.general_input", "confidence": 1.0}])
        second = core.apply([{"name": "conversation.general_input", "confidence": 1.0}])

        self.assertLess(second["after"]["task_focus"], first["after"]["task_focus"])


if __name__ == "__main__":
    unittest.main()
