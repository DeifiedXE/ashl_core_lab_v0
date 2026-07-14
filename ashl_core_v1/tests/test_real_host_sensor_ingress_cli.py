import json
import subprocess
import sys
import unittest
from tempfile import TemporaryDirectory


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "ashl_core_v1.runtime.real_host_sensor_ingress_cli", *args],
        text=True,
        capture_output=True,
        check=False,
    )


class RealHostSensorIngressCliTests(unittest.TestCase):
    def test_list_backends_cli_works(self) -> None:
        result = _run_cli("list-backends")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertIn("host_state", payload)
        self.assertFalse(payload["host_state"]["fixture_capture"])

    def test_capture_requires_confirmation(self) -> None:
        with TemporaryDirectory() as directory:
            result = _run_cli("capture-host-state-once", "--state-dir", directory)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--confirm-local-capture", result.stderr + result.stdout)

    def test_host_state_capture_and_metadata_only_show_artifact(self) -> None:
        with TemporaryDirectory() as directory:
            capture = _run_cli(
                "capture-host-state-once",
                "--state-dir",
                directory,
                "--confirm-local-capture",
            )
            self.assertEqual(capture.returncode, 0, capture.stderr)
            payload = json.loads(capture.stdout)
            artifact_id = payload["artifact_ids"][0]
            show = _run_cli("show-artifact", "--state-dir", directory, "--artifact-id", artifact_id)
            self.assertEqual(show.returncode, 0, show.stderr)
            artifact = json.loads(show.stdout)
            self.assertFalse(artifact["raw_bytes_displayed"])
            self.assertNotIn("data", artifact)
            verify = _run_cli("verify-artifact", "--state-dir", directory, "--artifact-id", artifact_id)
            self.assertTrue(json.loads(verify.stdout)["valid"])

    def test_screen_cli_requires_monitor_or_region(self) -> None:
        with TemporaryDirectory() as directory:
            result = _run_cli(
                "capture-screen-once",
                "--state-dir",
                directory,
                "--confirm-local-capture",
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("screen capture requires", result.stderr + result.stdout)


if __name__ == "__main__":
    unittest.main()
