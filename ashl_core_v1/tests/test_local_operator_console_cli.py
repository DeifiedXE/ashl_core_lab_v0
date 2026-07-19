import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

from ashl_core_v1.runtime.guided_cradle_growth_teacher_console import (
    home_console_dispatch_fixture_token_from_guided_cradle_growth_console,
)
from ashl_core_v1.runtime.local_operator_console_cli import main


def _run_cli(args: list[str]) -> dict:
    stream = io.StringIO()
    with redirect_stdout(stream):
        code = main(args)
    assert code == 0
    return json.loads(stream.getvalue())


class LocalOperatorConsoleCliTests(unittest.TestCase):
    def test_show_console_cli_builds_view_model(self) -> None:
        with TemporaryDirectory() as state_dir:
            payload = _run_cli(["show-console", "--state-dir", state_dir])

            self.assertEqual(payload["schema_version"], "ashl_qingyin_home_upper_console_view_model_v0")
            self.assertFalse(payload["sound_output_enabled"])
            self.assertTrue(payload["sound_patterns_reserved"])

    def test_submit_text_cli_does_not_forward_to_runtime(self) -> None:
        with TemporaryDirectory() as state_dir:
            payload = _run_cli(["submit-text", "--state-dir", state_dir, "--text", "hello"])

            self.assertEqual(payload["text_input"]["interpretation_status"], "received_unprocessed")
            self.assertEqual(payload["text_input"]["grounding_status"], "not_grounded")
            self.assertFalse(payload["text_input"]["forwarded_to_runtime"])
            self.assertEqual(payload["timeline_entry"]["entry_kind"], "user_input")

    def test_dispatch_fixture_token_cli_marks_fixture_only(self) -> None:
        with TemporaryDirectory() as state_dir:
            payload = _run_cli(["dispatch-fixture-token", "--state-dir", state_dir, "--tokens", "T03,T11"])

            self.assertTrue(payload["raw_output_sequence"]["fixture_only"])
            self.assertFalse(payload["raw_output_sequence"]["qingyin_authored"])
            self.assertEqual(payload["dispatch_result"]["rendered_text"], "T03 T11")
            self.assertFalse(payload["dispatch_result"]["sound_played"])

    def test_guided_console_home_command_uses_same_boundary(self) -> None:
        with TemporaryDirectory() as state_dir:
            payload = home_console_dispatch_fixture_token_from_guided_cradle_growth_console(
                state_dir=state_dir,
                tokens=("T00", "T03"),
            )

            self.assertEqual(payload["guided_console_action"], "home_console_dispatch_fixture_token")
            self.assertFalse(payload["creates_teacher_approval"])
            self.assertFalse(payload["qingyin_authored_output_created"])
            self.assertTrue(payload["home_console_result"]["fixture_only"])

    def test_preview_contains_required_regions_without_old_shortcuts(self) -> None:
        preview = Path("ashl_core_v1/ui_preview/qingyin_home_upper_console_preview_v0.html").read_text(encoding="utf-8")

        self.assertIn("Total State", preview)
        self.assertIn("Mic", preview)
        self.assertIn("Output Volume", preview)
        self.assertIn("Camera", preview)
        self.assertIn("Text Timeline", preview)
        self.assertIn("Text Input", preview)
        self.assertIn("Status Log", preview)
        self.assertIn("Developer Test Controls", preview)
        self.assertIn("T00", preview)
        self.assertNotIn("glowing core", preview.lower())
        self.assertNotIn("manual uncertainty", preview.lower())
        self.assertNotIn("teacher-wait-output", preview.lower())


if __name__ == "__main__":
    unittest.main()
