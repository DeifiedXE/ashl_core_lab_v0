from __future__ import annotations

import json
import tempfile
import unittest
from io import StringIO
from unittest.mock import patch

from ashl_core_v1.runtime import package_125_observation_extension_cli as cli


class Package125CliTests(unittest.TestCase):
    def test_real_smoke_routes_to_real_capture_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as state_dir, patch.object(
            cli,
            "run_real_late_event_observation_extension",
            return_value={"status": "mocked_real_pass"},
        ) as run_real, patch("sys.stdout", new_callable=StringIO) as output:
            status = cli.main(
                [
                    "real-smoke",
                    "--state-dir",
                    state_dir,
                    "--render-endpoint",
                    "default",
                ]
            )
        self.assertEqual(status, 0)
        self.assertEqual(json.loads(output.getvalue())["status"], "mocked_real_pass")
        run_real.assert_called_once()
        self.assertTrue(run_real.call_args.kwargs["allow_bounded_window_extension"])

    def test_real_smoke_returns_failure_status_when_capture_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as state_dir, patch.object(
            cli,
            "run_real_late_event_observation_extension",
            side_effect=RuntimeError("capture unavailable"),
        ), patch("sys.stdout", new_callable=StringIO) as output:
            status = cli.main(
                [
                    "real-smoke",
                    "--state-dir",
                    state_dir,
                    "--render-endpoint",
                    "default",
                ]
            )
        payload = json.loads(output.getvalue())
        self.assertEqual(status, 1)
        self.assertEqual(payload["status"], "blocked_real_late_event_capture")
        self.assertEqual(payload["reason"], "capture unavailable")

    def test_explicit_synthetic_verification_suite_is_available(self) -> None:
        with tempfile.TemporaryDirectory() as state_dir, patch(
            "sys.stdout",
            new_callable=StringIO,
        ) as output:
            status = cli.main(
                [
                    "run-synthetic-verification-suite",
                    "--state-dir",
                    state_dir,
                ]
            )
        payload = json.loads(output.getvalue())
        self.assertEqual(status, 0)
        self.assertEqual(
            payload["status"],
            "passed_synthetic_bounded_observation_window_extension_audit_v0",
        )

    def test_extension_disabled_is_an_isolated_control_not_real_smoke(self) -> None:
        with tempfile.TemporaryDirectory() as state_dir, patch(
            "sys.stdout",
            new_callable=StringIO,
        ) as output:
            status = cli.main(
                [
                    "run-late-event-extension",
                    "--state-dir",
                    state_dir,
                    "--extension-disabled",
                ]
            )
        payload = json.loads(output.getvalue())
        self.assertEqual(status, 0)
        self.assertEqual(payload["scenario"], "authorization_off_control")
        self.assertEqual(payload["policy"]["decision"], "block")
        self.assertIsNone(payload["execution"])


if __name__ == "__main__":
    unittest.main()
