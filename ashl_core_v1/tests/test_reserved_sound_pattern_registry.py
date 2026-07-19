import unittest
from tempfile import TemporaryDirectory

from ashl_core_v1.runtime.local_non_llm_output_dispatcher import LocalNonLLMOutputDispatcher
from ashl_core_v1.runtime.local_operator_console_store import build_default_console_store
from ashl_core_v1.runtime.reserved_sound_pattern_registry import (
    build_reserved_sound_pattern_registry,
    get_reserved_sound_pattern,
)


class ReservedSoundPatternRegistryTests(unittest.TestCase):
    def test_p00_through_p07_exist_without_meaning_and_disabled(self) -> None:
        patterns = build_reserved_sound_pattern_registry()
        self.assertEqual(tuple(item.pattern_code for item in patterns), tuple(f"P{index:02d}" for index in range(8)))
        self.assertTrue(all(item.semantic_label is None for item in patterns))
        self.assertTrue(all(item.predefined_meaning is None for item in patterns))
        self.assertFalse(any(item.output_enabled for item in patterns))

    def test_sound_dispatch_is_blocked_by_policy(self) -> None:
        with TemporaryDirectory() as state_dir:
            store = build_default_console_store(state_dir)
            dispatcher = LocalNonLLMOutputDispatcher(store)
            intent = dispatcher.create_sound_pattern_intent(sound_pattern_id=get_reserved_sound_pattern("P03").sound_pattern_id)

            result = dispatcher.dispatch_intent(intent.output_intent_id)

            self.assertEqual(result.dispatch_status, "blocked_sound_sink_disabled")
            self.assertFalse(result.sound_played)


if __name__ == "__main__":
    unittest.main()
