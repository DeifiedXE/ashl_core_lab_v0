import unittest

from ashl_core.concepts import apply_concepts
from ashl_core.perception import perceive


class ConceptLayerTests(unittest.TestCase):
    def test_sleep_mode_blocks_fatigue(self):
        result = apply_concepts(perceive("睡眠模式這個功能怎麼設計？"))

        self.assertIn("user.fatigue_signaled", [event["name"] for event in result["blocked_events"]])
        self.assertIn("technical.topic_discussed", [event["name"] for event in result["final_events"]])

    def test_memory_request_is_allowed(self):
        result = apply_concepts(perceive("記住，以後 ASHL Core 先走實驗路線"))

        self.assertIn("memory.candidate_requested", [event["name"] for event in result["final_events"]])


if __name__ == "__main__":
    unittest.main()
