import unittest

from ashl_core.action_sandbox import apply_action, validate_action_result
from ashl_core.body_state import build_body_state


class ActionSandboxTests(unittest.TestCase):
    def test_lying_stand_up_fails(self):
        result = apply_action(build_body_state("lying"), "stand_up")

        self.assertFalse(result["success"])
        self.assertEqual(result["from_state"], "lying")
        self.assertEqual(result["to_state"], "lying")
        self.assertTrue(validate_action_result(result))

    def test_lying_stand_up_failure_reason(self):
        result = apply_action(build_body_state("lying"), "stand_up")

        self.assertEqual(result["failure_reason"], "cannot_stand_directly_from_lying")

    def test_lying_sit_up_succeeds(self):
        result = apply_action(build_body_state("lying"), "sit_up")

        self.assertTrue(result["success"])
        self.assertEqual(result["to_state"], "sitting")
        self.assertEqual(result["body_state"]["stability"], 0.4)

    def test_sitting_stand_up_succeeds(self):
        result = apply_action(build_body_state("sitting", stability=0.4), "stand_up")

        self.assertTrue(result["success"])
        self.assertEqual(result["to_state"], "standing_unstable")
        self.assertEqual(result["body_state"]["stability"], 0.45)

    def test_standing_unstable_balance_succeeds(self):
        result = apply_action(build_body_state("standing_unstable", stability=0.45), "balance")

        self.assertTrue(result["success"])
        self.assertEqual(result["to_state"], "standing_stable")
        self.assertEqual(result["body_state"]["stability"], 0.85)

    def test_unknown_action_returns_unknown_action(self):
        result = apply_action(build_body_state("lying"), "jump")

        self.assertFalse(result["success"])
        self.assertEqual(result["failure_reason"], "unknown_action")


if __name__ == "__main__":
    unittest.main()
