import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from ashl_core_v1.tests.test_bounded_multimodal_perception_session_runtime import build_manifest


class BoundedMultimodalPerceptionSessionCliTests(unittest.TestCase):
    def test_run_artifact_replay_cli_reaches_teacher_gate(self):
        with TemporaryDirectory() as state_dir:
            manifest = build_manifest(state_dir)
            manifest_path = Path(state_dir) / "manifest.json"
            manifest_path.write_text(json.dumps(manifest.to_dict()), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "ashl_core_v1.runtime.bounded_multimodal_perception_session_cli",
                    "run-artifact-replay",
                    "--state-dir",
                    state_dir,
                    "--manifest",
                    str(manifest_path),
                    "--alignment-window-ms",
                    "250",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)
            self.assertTrue(payload["stopped_at_teacher_gate"])
            self.assertEqual(payload["bounded_stop_reason"], "teacher_review_boundary")

    def test_live_mode_requires_confirmation(self):
        with TemporaryDirectory() as state_dir:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "ashl_core_v1.runtime.bounded_multimodal_perception_session_cli",
                    "run-live-bounded",
                    "--state-dir",
                    state_dir,
                    "--camera-device",
                    "0",
                    "--screen-region",
                    "0,0,64,64",
                    "--microphone-device",
                    "0",
                ],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
