import unittest

from ashl_core.first_output_runtime import generate_minimal_first_output


class MinimalFirstOutputRuntimeTests(unittest.TestCase):
    def test_generates_first_output_trace(self):
        result = generate_minimal_first_output()

        self.assertIsInstance(result, dict)
        self.assertIn("first_output_trace", result)
        self.assertEqual(result["first_output_trace"]["trace_type"], "first_output_trace")

    def test_does_not_use_llm(self):
        result = generate_minimal_first_output()
        trace = result["first_output_trace"]

        self.assertIs(result["llm_used"], False)
        self.assertIs(trace["llm_used"], False)
        self.assertNotEqual(trace["output_generator_source"], "llm")

    def test_uses_test_object_stage(self):
        trace = generate_minimal_first_output()["first_output_trace"]

        self.assertEqual(trace["phase"], "test_object")
        self.assertEqual(trace["engineering_stage"], "test_object")

    def test_tick_is_one(self):
        result = generate_minimal_first_output()

        self.assertEqual(result["tick"], 1)
        self.assertEqual(result["first_output_trace"]["tick"], 1)

    def test_does_not_include_learning_or_memory_outputs(self):
        result = generate_minimal_first_output()
        trace = result["first_output_trace"]

        forbidden_keys = {
            "lesson_store_write",
            "memory_layer_write",
            "memory_write",
            "lesson_candidate",
            "failure_event",
            "review",
            "selection",
            "activation",
        }
        self.assertTrue(forbidden_keys.isdisjoint(result))
        self.assertTrue(forbidden_keys.isdisjoint(trace))

    def test_fixed_reflex_output_shape(self):
        trace = generate_minimal_first_output()["first_output_trace"]

        self.assertEqual(trace["first_output"], "*")
        self.assertEqual(trace["output_kind"], "fixed_reflex")
        self.assertEqual(trace["output_generator_source"], "simple_reflex_rule")

    def test_accepts_session_id(self):
        trace = generate_minimal_first_output(session_id="test_session")["first_output_trace"]

        self.assertEqual(trace["session_id"], "test_session")

    def test_default_session_id_exists(self):
        trace = generate_minimal_first_output()["first_output_trace"]

        self.assertTrue(trace["session_id"])


if __name__ == "__main__":
    unittest.main()
