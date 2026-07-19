import unittest
from tempfile import TemporaryDirectory

from ashl_core_v1.runtime.local_non_llm_output_dispatcher import LocalNonLLMOutputDispatcher
from ashl_core_v1.runtime.local_operator_console_store import build_default_console_store
from ashl_core_v1.runtime.operator_hardware_status import set_output_volume_state
from ashl_core_v1.runtime.operator_text_timeline import build_fixture_raw_output_sequence
from ashl_core_v1.runtime.output_rate_limit import build_default_output_rate_limit_policy


class LocalNonLLMOutputDispatcherTests(unittest.TestCase):
    def _fixture_intent(self, state_dir: str) -> tuple[LocalNonLLMOutputDispatcher, str]:
        store = build_default_console_store(state_dir)
        sequence = build_fixture_raw_output_sequence(token_codes=("T03", "T11"))
        store.append_raw_output_sequence(sequence)
        dispatcher = LocalNonLLMOutputDispatcher(store)
        intent = dispatcher.create_raw_output_intent(
            raw_output_sequence_id=sequence.raw_output_sequence_id,
            source_kind="fixture",
            source_record_refs=(sequence.raw_output_sequence_id,),
            fixture_only=True,
            qingyin_authored=False,
        )
        return dispatcher, intent.output_intent_id

    def test_dispatcher_transports_fixture_tokens_without_authoring_them(self) -> None:
        with TemporaryDirectory() as state_dir:
            dispatcher, intent_id = self._fixture_intent(state_dir)

            result = dispatcher.dispatch_intent(
                intent_id,
                policy=build_default_output_rate_limit_policy(minimum_interval_ms=0),
            )
            timeline = dispatcher.store.list_payloads("text_timeline_entries")

            self.assertEqual(result.dispatch_status, "dispatched")
            self.assertEqual(result.rendered_text, "T03 T11")
            self.assertTrue(result.fixture_only)
            self.assertFalse(result.qingyin_authored)
            self.assertFalse(result.sound_played)
            self.assertEqual(timeline[-1]["entry_kind"], "qingyin_raw_output")
            self.assertFalse(timeline[-1]["qingyin_authored"])

    def test_dispatcher_requires_output_intent_provenance(self) -> None:
        with TemporaryDirectory() as state_dir:
            store = build_default_console_store(state_dir)
            sequence = build_fixture_raw_output_sequence(token_codes=("T01",))
            store.append_raw_output_sequence(sequence)
            dispatcher = LocalNonLLMOutputDispatcher(store)

            with self.assertRaises(ValueError):
                dispatcher.create_raw_output_intent(
                    raw_output_sequence_id=sequence.raw_output_sequence_id,
                    source_kind="fixture",
                    source_record_refs=tuple(),
                )

    def test_pending_output_can_be_cancelled_before_dispatch(self) -> None:
        with TemporaryDirectory() as state_dir:
            dispatcher, intent_id = self._fixture_intent(state_dir)

            cancellation = dispatcher.cancel_output(output_intent_id=intent_id)
            result = dispatcher.dispatch_intent(
                intent_id,
                policy=build_default_output_rate_limit_policy(minimum_interval_ms=0),
            )

            self.assertTrue(cancellation.cancellation_succeeded)
            self.assertEqual(result.dispatch_status, "cancelled")
            self.assertTrue(result.cancelled)

    def test_muted_output_keeps_text_visible_and_sound_silent(self) -> None:
        with TemporaryDirectory() as state_dir:
            dispatcher, intent_id = self._fixture_intent(state_dir)
            set_output_volume_state(dispatcher.store, muted=True)

            result = dispatcher.dispatch_intent(
                intent_id,
                policy=build_default_output_rate_limit_policy(minimum_interval_ms=0),
            )

            self.assertEqual(result.dispatch_status, "dispatched")
            self.assertTrue(result.muted)
            self.assertEqual(result.rendered_text, "T03 T11")
            self.assertFalse(result.sound_played)

    def test_rate_limit_failure_creates_result_and_status_log(self) -> None:
        with TemporaryDirectory() as state_dir:
            dispatcher, intent_id = self._fixture_intent(state_dir)
            dispatcher.dispatch_intent(intent_id, policy=build_default_output_rate_limit_policy(minimum_interval_ms=0))
            second_dispatcher, second_intent_id = self._fixture_intent(state_dir)

            result = second_dispatcher.dispatch_intent(second_intent_id)
            logs = second_dispatcher.store.list_payloads("status_log_entries")

            self.assertEqual(result.dispatch_status, "blocked_rate_limit")
            self.assertTrue(result.rate_limited)
            self.assertEqual(logs[-1]["event_kind"], "output_rate_limited")
            self.assertFalse(logs[-1]["qingyin_output"])


if __name__ == "__main__":
    unittest.main()
