from __future__ import annotations

import tempfile
import unittest

from ashl_core_v1.host_body.host_body_internal_action_choice import (
    ALLOWED_INTERNAL_ACTION_KINDS,
)
from ashl_core_v1.runtime.observation_extension_internal_action import (
    cancel_pending_observation_extension,
)
from ashl_core_v1.runtime.observation_window_types import (
    ObservationWindowExtensionCandidate,
)
from ashl_core_v1.runtime.package_125_observation_extension_runtime import (
    run_synthetic_observation_extension_scenario,
)


class ObservationExtensionInternalActionTests(unittest.TestCase):
    def test_execution_derives_same_session_result_from_identity_records(self) -> None:
        with tempfile.TemporaryDirectory() as state_dir:
            result = run_synthetic_observation_extension_scenario(state_dir=state_dir)
        action = result["action"]
        execution = result["execution"]
        before = result["active_capture_identity_before"]
        after = result["active_capture_identity_after"]
        self.assertIn("extend_observation_window", ALLOWED_INTERNAL_ACTION_KINDS)
        self.assertTrue(action["internal_only"])
        self.assertFalse(action["external_side_effect"])
        self.assertNotIn("selected_action", action)
        self.assertNotIn("final_action", action)
        self.assertNotIn("direct_command", action)
        self.assertTrue(execution["same_capture_sessions_preserved"])
        self.assertFalse(execution["sources_reopened"])
        for key in (
            "screen_capture_session_id",
            "audio_capture_session_id",
            "host_state_capture_session_id",
            "alignment_origin_monotonic_ns",
            "clock_domain_ids",
        ):
            self.assertEqual(before[key], after[key])

    def test_executed_extension_cannot_be_erased(self) -> None:
        with tempfile.TemporaryDirectory() as state_dir:
            result = run_synthetic_observation_extension_scenario(state_dir=state_dir)
        candidate = ObservationWindowExtensionCandidate(**result["candidate"])
        cancellation = cancel_pending_observation_extension(
            candidate=candidate,
            target_internal_action_id=result["action"]["internal_action_id"],
            deadline_already_extended=True,
        )
        self.assertFalse(cancellation.cancellation_succeeded)
        self.assertTrue(cancellation.deadline_already_extended)


if __name__ == "__main__":
    unittest.main()
