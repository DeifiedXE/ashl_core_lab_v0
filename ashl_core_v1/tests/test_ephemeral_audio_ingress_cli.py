import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout

from ashl_core_v1.runtime.audio_artifact_deletion import request_artifact_deletion
from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import ContentAddressedSensorArtifactStore
from ashl_core_v1.runtime.ephemeral_audio_ingress_cli import main
from ashl_core_v1.runtime.guided_cradle_growth_teacher_console import (
    audio_audit_storage_from_guided_cradle_growth_console,
    audio_start_ephemeral_buffer_from_guided_cradle_growth_console,
)
from ashl_core_v1.tests.test_audio_artifact_deletion import _write_audio_artifact


class EphemeralAudioIngressCliTests(unittest.TestCase):
    def test_audit_audio_storage_cli_works(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = _run_cli(["audit-audio-storage", "--state-dir", temp])
            payload = json.loads(output)
            self.assertEqual(payload["audit_status"], "passed_ephemeral_audio_and_auditable_deletion_foundation")

    def test_delete_audio_artifact_cli_records_tombstone(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            store = ContentAddressedSensorArtifactStore(temp)
            artifact = _write_audio_artifact(store, b"\x01\x00\x02\x00")
            request = request_artifact_deletion(
                artifact_id=artifact.artifact_id,
                expected_content_sha256=artifact.content_sha256,
                reason_code="service_period_complete",
                approval_text="Delete this local waveform artifact.",
            )
            store.append_artifact_deletion_request(request)

            output = _run_cli([
                "apply-delete-audio-artifact",
                "--state-dir",
                temp,
                "--deletion-request-id",
                request.deletion_request_id,
            ])
            payload = json.loads(output)

            self.assertTrue(payload["artifact_tombstoned"])
            self.assertEqual(
                ContentAddressedSensorArtifactStore(temp).verify_artifact(artifact.artifact_id)["status"],
                "authorized_waveform_deletion",
            )

    def test_retain_recent_excerpt_cli_refuses_cross_process_ram_buffer(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(SystemExit):
                main([
                    "retain-recent-excerpt",
                    "--state-dir",
                    temp,
                    "--ring-buffer-session-id",
                    "ephemeral_audio_session:missing",
                    "--purpose",
                    "counterexample",
                    "--pre-roll-ms",
                    "100",
                    "--post-roll-ms",
                    "100",
                    "--consent-record-id",
                    "audio_capture_consent:missing",
                ])

    def test_guided_teacher_console_audio_audit_and_ephemeral_metadata_work(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            started = audio_start_ephemeral_buffer_from_guided_cradle_growth_console(
                state_dir=temp,
                device_index=0,
                buffer_ms=1000,
                confirm_local_capture=True,
            )
            audit = audio_audit_storage_from_guided_cradle_growth_console(state_dir=temp)

            self.assertEqual(started["guided_console_action"], "audio_start_ephemeral_buffer")
            self.assertFalse(started["microphone_opened"])
            self.assertEqual(audit["audio_storage_audit"]["normal_ephemeral_pcm_blob_count"], 0)
            self.assertEqual(audit["audio_storage_audit"]["audit_status"], "passed_ephemeral_audio_and_auditable_deletion_foundation")


def _run_cli(args: list[str]) -> str:
    stream = io.StringIO()
    with redirect_stdout(stream):
        code = main(args)
    assert code == 0
    return stream.getvalue()


if __name__ == "__main__":
    unittest.main()
