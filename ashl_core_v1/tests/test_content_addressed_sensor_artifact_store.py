import json
import sqlite3
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from ashl_core_v1.runtime.bounded_host_sensor_ingress_runtime import BoundedHostSensorIngressRuntime
from ashl_core_v1.runtime.content_addressed_sensor_artifact_store import ContentAddressedSensorArtifactStore
from ashl_core_v1.runtime.host_sensor_types import build_sensor_capture_config, sha256_bytes
from ashl_core_v1.tests.test_sensor_adapter_protocol import FixtureSensorAdapter


class ContentAddressedSensorArtifactStoreTests(unittest.TestCase):
    def _run_fixture_capture(self, directory: str, count: int = 1):
        config = build_sensor_capture_config(
            source_kind="host_state",
            adapter_id="fixture_sensor_adapter_v0",
            device_id="fixture:host_state",
            explicit_state_dir=directory,
            source_specific_config={"host_state_fields": "restricted_v0"},
            maximum_artifact_count=count,
        )
        runtime = BoundedHostSensorIngressRuntime(
            state_dir=directory,
            adapter=FixtureSensorAdapter(),
        )
        session = runtime.start(config)
        artifact_ids = [runtime.capture_next_sample()]
        if runtime.status == "running":
            runtime.stop()
        return ContentAddressedSensorArtifactStore(directory), session, artifact_ids

    def test_content_addressed_blob_and_trace_integrity(self) -> None:
        with TemporaryDirectory() as directory:
            store, session, artifact_ids = self._run_fixture_capture(directory)
            artifact = store.get_artifact(artifact_ids[0])
            blob_path = Path(directory) / "host_sensor_artifacts_v0" / artifact["blob_relative_path"]
            self.assertTrue(blob_path.exists())
            self.assertEqual(sha256_bytes(blob_path.read_bytes()), artifact["content_sha256"])
            self.assertTrue(store.verify_artifact(artifact_ids[0])["valid"])
            traces = store.list_trace_envelopes(session.session_id)
            self.assertEqual(len([t for t in traces if t.record_kind == "sensor_raw_artifact"]), 1)
            payload = [t.payload_snapshot for t in traces if t.record_kind == "sensor_raw_artifact"][0]
            self.assertNotIn("raw_bytes", payload)
            self.assertNotIn("pixel_bytes", payload)
            self.assertNotIn("pcm_bytes", payload)
            self.assertNotIn("base64", json.dumps(payload).lower())
            self.assertEqual(payload["byte_length"], len(b"fixture"))

    def test_identical_bytes_reuse_blob_but_create_distinct_artifacts(self) -> None:
        with TemporaryDirectory() as directory:
            config = build_sensor_capture_config(
                source_kind="host_state",
                adapter_id="fixture_sensor_adapter_v0",
                device_id="fixture:host_state",
                explicit_state_dir=directory,
                source_specific_config={"host_state_fields": "restricted_v0"},
                maximum_artifact_count=2,
            )
            runtime = BoundedHostSensorIngressRuntime(state_dir=directory, adapter=FixtureSensorAdapter())
            runtime.start(config)
            first = runtime.capture_next_sample()
            second = runtime.capture_next_sample()
            store = ContentAddressedSensorArtifactStore(directory)
            artifacts = [store.get_artifact(first), store.get_artifact(second)]
            self.assertNotEqual(artifacts[0]["artifact_id"], artifacts[1]["artifact_id"])
            self.assertEqual(artifacts[0]["content_sha256"], artifacts[1]["content_sha256"])
            self.assertEqual(artifacts[0]["blob_relative_path"], artifacts[1]["blob_relative_path"])

    def test_store_blocks_missing_blob_hash_path_and_mutation_surfaces(self) -> None:
        with TemporaryDirectory() as directory:
            store, _session, artifact_ids = self._run_fixture_capture(directory)
            artifact = store.get_artifact(artifact_ids[0])
            blob_path = Path(directory) / "host_sensor_artifacts_v0" / artifact["blob_relative_path"]
            blob_path.unlink()
            audit = store.audit_store()
            self.assertEqual(audit.audit_status, "blocked_missing_blob")
            with self.assertRaises(TypeError):
                store.update_artifact(artifact_ids[0])
            with self.assertRaises(TypeError):
                store.delete_trace("trace")

    def test_metadata_without_blob_blocks_audit(self) -> None:
        with TemporaryDirectory() as directory:
            store, _session, artifact_ids = self._run_fixture_capture(directory)
            artifact = store.get_artifact(artifact_ids[0])
            corrupted = dict(artifact)
            corrupted["blob_relative_path"] = "blobs/sha256/ff/missing.bin"
            connection = sqlite3.connect(store.db_path)
            try:
                connection.execute(
                    "UPDATE sensor_raw_artifacts SET blob_relative_path = ?, payload_json = ? WHERE artifact_id = ?",
                    ("blobs/sha256/ff/missing.bin", json.dumps(corrupted, sort_keys=True), artifact_ids[0]),
                )
                connection.commit()
            finally:
                connection.close()
            self.assertEqual(store.audit_store().audit_status, "blocked_missing_blob")
            self.assertTrue(store.get_artifact(artifact_ids[0])["blob_relative_path"].endswith("missing.bin"))
            self.assertNotEqual(artifact["blob_relative_path"], store.get_artifact(artifact_ids[0])["blob_relative_path"])

    def test_orphan_blob_is_reported_not_promoted_to_artifact(self) -> None:
        with TemporaryDirectory() as directory:
            store, _session, _artifact_ids = self._run_fixture_capture(directory)
            orphan = store.blob_root / "aa" / ("a" * 64 + ".bin")
            orphan.parent.mkdir(parents=True, exist_ok=True)
            orphan.write_bytes(b"orphan")
            audit = store.audit_store()
            self.assertEqual(audit.audit_status, "passed_with_reported_orphan_blob")
            self.assertEqual(audit.orphan_blob_count, 1)


if __name__ == "__main__":
    unittest.main()
