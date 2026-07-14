import unittest

from ashl_core_v1.perception.host_state_primitive_compiler import (
    build_host_state_compiler_descriptor,
    compile_host_state_primitive,
)
from ashl_core_v1.perception.perception_source_buffer import (
    PERCEPTION_SOURCE_BUFFER_SCHEMA_VERSION,
    PerceptionSourceBuffer,
)
from ashl_core_v1.runtime.host_sensor_types import canonical_json


def _host_state_buffer(payload: dict[str, object]) -> PerceptionSourceBuffer:
    data = canonical_json(payload).encode("utf-8")
    return PerceptionSourceBuffer(
        buffer_id="host-buffer",
        schema_version=PERCEPTION_SOURCE_BUFFER_SCHEMA_VERSION,
        source_kind="host_state",
        media_type="application/json",
        storage_mode="stored_artifact",
        captured_at_utc="now",
        captured_at_monotonic_ns=1,
        adapter_id="fixture",
        adapter_version="v0",
        media_format="canonical_json_utf8",
        sample_rate=None,
        channels=None,
        sample_format=None,
        frame_count=None,
        byte_length=len(data),
        readonly_bytes=memoryview(data),
        source_artifact_id="artifact:host",
        source_trace_refs=("trace:host",),
        ephemeral=False,
        persistence_allowed=True,
        source_content_sha256="hash",
    )


class HostStatePrimitiveCompilerTests(unittest.TestCase):
    def test_descriptor_is_model_free(self):
        descriptor = build_host_state_compiler_descriptor()
        self.assertTrue(descriptor.deterministic)
        self.assertFalse(descriptor.llm_used)
        self.assertFalse(descriptor.network_required)

    def test_host_state_canonical_json_compiles(self):
        primitive = compile_host_state_primitive(
            _host_state_buffer(
                {
                    "sample_monotonic_ns": 1,
                    "process_uptime_ns": 2,
                    "power_source": "ac",
                    "battery_percent": 50,
                    "cpu_utilization_percent": 25,
                    "memory_total_bytes": 100,
                    "memory_available_bytes": 40,
                    "display_count": 2,
                    "camera_adapter_available": True,
                    "microphone_adapter_available": False,
                    "screen_adapter_available": True,
                }
            )
        )
        self.assertEqual(primitive.cpu_utilization_ratio, 0.25)
        self.assertEqual(primitive.memory_available_ratio, 0.4)
        self.assertEqual(primitive.battery_ratio, 0.5)
        self.assertIsNone(primitive.semantic_label)
        self.assertIsNone(primitive.host_condition_label)

    def test_unknown_fields_rejected(self):
        with self.assertRaises(ValueError):
            compile_host_state_primitive(_host_state_buffer({"process_list": []}))

    def test_missing_fields_recorded(self):
        primitive = compile_host_state_primitive(_host_state_buffer({"cpu_utilization_percent": 10}))
        self.assertIn("memory_total_bytes", primitive.missing_field_names)
        self.assertGreater(primitive.quality_uncertainty, 0.0)


if __name__ == "__main__":
    unittest.main()
