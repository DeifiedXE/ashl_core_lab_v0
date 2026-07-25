from __future__ import annotations

import unittest

from ashl_core_v1.runtime.bounded_capture_deadline_controller import (
    BoundedCaptureDeadlineController,
)


class BoundedCaptureDeadlineControllerTests(unittest.TestCase):
    def _controller(self) -> BoundedCaptureDeadlineController:
        return BoundedCaptureDeadlineController(
            base_deadline_ns=5_000_000_000,
            hard_deadline_ns=7_000_000_000,
            participating_lanes=("screen", "microphone", "host_state"),
            maximum_extension_count=1,
            maximum_total_extension_ns=1_500_000_000,
        )

    def test_atomic_extension_updates_every_lane_once(self) -> None:
        controller = self._controller()
        result = controller.request_extension(
            expected_current_deadline_ns=5_000_000_000,
            extension_ns=1_500_000_000,
            policy_decision_id="policy:allow",
        )
        self.assertEqual(result.extension_status, "applied")
        self.assertTrue(result.atomic_compare_and_set_succeeded)
        self.assertTrue(result.all_lane_deadlines_updated)
        self.assertEqual(set(controller.lane_deadlines().values()), {6_500_000_000})
        self.assertEqual(controller.extension_count, 1)

    def test_stale_compare_and_set_cannot_change_deadline(self) -> None:
        controller = self._controller()
        result = controller.request_extension(
            expected_current_deadline_ns=4_999_999_999,
            extension_ns=1_500_000_000,
            policy_decision_id="policy:stale",
        )
        self.assertEqual(result.extension_status, "stale_deadline")
        self.assertFalse(result.atomic_compare_and_set_succeeded)
        self.assertEqual(controller.current_deadline_ns(), 5_000_000_000)

    def test_deadline_cannot_decrease_or_exceed_limits(self) -> None:
        controller = self._controller()
        decrease = controller.request_extension(
            expected_current_deadline_ns=5_000_000_000,
            extension_ns=-1,
            policy_decision_id="policy:decrease",
        )
        self.assertEqual(decrease.extension_status, "failed")
        self.assertEqual(controller.current_deadline_ns(), 5_000_000_000)

        hard_limit = controller.request_extension(
            expected_current_deadline_ns=5_000_000_000,
            extension_ns=2_000_000_001,
            policy_decision_id="policy:hard-limit",
        )
        self.assertEqual(hard_limit.extension_status, "failed")
        self.assertIn("exceeds_hard_deadline", hard_limit.failure_reasons)
        self.assertIn("maximum_total_extension_exceeded", hard_limit.failure_reasons)

    def test_extension_count_limit_is_enforced(self) -> None:
        controller = self._controller()
        first = controller.request_extension(
            expected_current_deadline_ns=5_000_000_000,
            extension_ns=1_500_000_000,
            policy_decision_id="policy:first",
        )
        second = controller.request_extension(
            expected_current_deadline_ns=6_500_000_000,
            extension_ns=1,
            policy_decision_id="policy:second",
        )
        self.assertEqual(first.extension_status, "applied")
        self.assertEqual(second.extension_status, "failed")
        self.assertIn("maximum_extension_count_exceeded", second.failure_reasons)
        self.assertEqual(controller.current_deadline_ns(), 6_500_000_000)


if __name__ == "__main__":
    unittest.main()
