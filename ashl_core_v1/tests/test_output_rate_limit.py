import unittest

from ashl_core_v1.runtime.output_rate_limit import (
    build_default_output_rate_limit_policy,
    rate_limit_allows_dispatch,
)


class OutputRateLimitTests(unittest.TestCase):
    def test_default_policy_matches_package_122b_defaults(self) -> None:
        policy = build_default_output_rate_limit_policy()
        self.assertEqual(policy.minimum_interval_ms, 2000)
        self.assertEqual(policy.maximum_queue_depth, 8)
        self.assertEqual(policy.overflow_policy, "reject_new_with_log")

    def test_interval_and_queue_limits_apply_to_output_only(self) -> None:
        policy = build_default_output_rate_limit_policy(minimum_interval_ms=2000, maximum_queue_depth=1)

        allowed, reason = rate_limit_allows_dispatch(
            policy=policy,
            pending_output_count=0,
            latest_dispatch_age_ms=None,
        )
        self.assertTrue(allowed)
        self.assertIsNone(reason)

        allowed, reason = rate_limit_allows_dispatch(
            policy=policy,
            pending_output_count=0,
            latest_dispatch_age_ms=100,
        )
        self.assertFalse(allowed)
        self.assertEqual(reason, "minimum_interval_not_elapsed")

        allowed, reason = rate_limit_allows_dispatch(
            policy=policy,
            pending_output_count=1,
            latest_dispatch_age_ms=3000,
        )
        self.assertFalse(allowed)
        self.assertEqual(reason, "queue_depth_exceeded")


if __name__ == "__main__":
    unittest.main()
