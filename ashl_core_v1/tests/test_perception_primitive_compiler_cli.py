import io
import json
import unittest
from contextlib import redirect_stdout
from tempfile import TemporaryDirectory

from ashl_core_v1.perception.perception_primitive_compiler_cli import main


class PerceptionPrimitiveCompilerCliTests(unittest.TestCase):
    def _run_cli(self, argv):
        output = io.StringIO()
        with redirect_stdout(output):
            code = main(argv)
        self.assertEqual(code, 0)
        return json.loads(output.getvalue())

    def test_list_compilers_works_without_state_dir(self):
        payload = self._run_cli(["list-compilers"])
        ids = {item["compiler_id"] for item in payload}
        self.assertIn("visual_frame_compiler_v0", ids)
        self.assertIn("audio_primitive_compiler_v0", ids)

    def test_compile_ephemeral_audio_cli_creates_no_sensor_store(self):
        with TemporaryDirectory() as state_dir:
            payload = self._run_cli(
                [
                    "compile-ephemeral-audio",
                    "--state-dir",
                    state_dir,
                    "--ring-buffer-session-id",
                    "demo",
                    "--window-ms",
                    "1000",
                    "--privacy-policy",
                    "recognition_ephemeral_v0",
                ]
            )
            self.assertEqual(payload["bundle_status"], "compiled_ephemeral_source")
            self.assertIsNone(payload["source_artifact_id"])

    def test_audit_store_cli_works(self):
        with TemporaryDirectory() as state_dir:
            payload = self._run_cli(["audit-store", "--state-dir", state_dir])
            self.assertEqual(payload["audit_status"], "passed_hard_soft_perception_primitive_compiler")

    def test_guided_teacher_console_perception_command_works(self):
        from ashl_core_v1.runtime.guided_cradle_growth_teacher_console import (
            perception_list_compilers_from_guided_cradle_growth_console,
        )

        payload = perception_list_compilers_from_guided_cradle_growth_console()
        self.assertEqual(payload["guided_console_action"], "perception_list_compilers")
        self.assertFalse(payload["learning_approval_created"])
        self.assertFalse(payload["memory_write_created"])


if __name__ == "__main__":
    unittest.main()
