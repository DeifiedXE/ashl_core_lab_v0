import unittest

from ashl_core_v1.runtime.temporal_continuity_compiler import compile_temporal_continuity


def window(index, start, end, complete=True):
    lane = {
        "source_artifact_present": True,
        "compiled_primitive_present": True,
        "delivered_to_alignment": True,
    }
    return {
        "coverage_record_id": f"coverage:{index}",
        "alignment_window_id": f"window:{index}",
        "window_index": index,
        "start_event_time_ns": start,
        "end_event_time_ns": end,
        "required_lanes_complete": complete,
        "partial_edge_window": False,
        "screen": lane,
        "audio": lane,
        "host_state": lane,
        "source_trace_refs": ("trace:test",),
    }


class TemporalContinuityCompilerTests(unittest.TestCase):
    def test_stable_and_silent_data_count_as_present(self):
        continuity = compile_temporal_continuity((window(0, 0, 100), window(1, 100, 200)))
        self.assertEqual(continuity.continuity_status, "continuous")
        self.assertTrue(continuity.stable_data_counted_as_present)
        self.assertTrue(continuity.silent_data_counted_as_present)

    def test_missing_coverage_creates_interruption(self):
        continuity = compile_temporal_continuity((window(0, 0, 100), window(1, 200, 300)))
        self.assertEqual(continuity.continuity_status, "interrupted")
        self.assertEqual(continuity.uncovered_gap_count, 1)


if __name__ == "__main__":
    unittest.main()

