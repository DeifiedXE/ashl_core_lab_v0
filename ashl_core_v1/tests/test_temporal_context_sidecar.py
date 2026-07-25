import unittest

from ashl_core_v1.runtime.temporal_context_sidecar import attach_temporal_context_sidecar, verify_package_112_score_equivalence
from ashl_core_v1.runtime.temporal_types import TEMPORAL_BUNDLE_SCHEMA_VERSION, GroundedTemporalPrimitiveBundle


class TemporalContextSidecarTests(unittest.TestCase):
    def test_sidecar_is_read_only_context(self):
        bundle = GroundedTemporalPrimitiveBundle(
            temporal_bundle_id="grounded_temporal_bundle:test",
            schema_version=TEMPORAL_BUNDLE_SCHEMA_VERSION,
            created_at="2026-07-24T00:00:00+00:00",
            clock_domain_refs=("clock:test",),
            anchor_refs=("anchor:test",),
            span_refs=("span:test",),
            interval_refs=("interval:test",),
            relation_refs=("relation:test",),
            continuity_refs=("continuity:test",),
            repeated_structure_refs=(),
            external_gap_refs=(),
            source_perception_record_refs=("perception:test",),
            source_alignment_window_refs=("window:test",),
            source_trace_refs=("trace:test",),
            stimulus_ground_truth_used_for_compilation=False,
            subjective_time_claimed=False,
            rhythm_semantics_claimed=False,
            waiting_semantics_claimed=False,
        )
        sidecar = attach_temporal_context_sidecar(source_perception_record_id="perception:test", bundle=bundle)
        self.assertTrue(sidecar.read_only)
        self.assertFalse(sidecar.scoring_authority)
        self.assertFalse(sidecar.memory_write_authority)
        self.assertFalse(sidecar.action_selection_authority)
        self.assertFalse(sidecar.output_authority)
        self.assertFalse(verify_package_112_score_equivalence(93.0, 93.0)["package_112_score_changed"])


if __name__ == "__main__":
    unittest.main()

