from __future__ import annotations

import unittest

from ashl_core_v1.runtime.package_125_observation_extension_runtime import (
    build_observation_window_state,
    build_synthetic_package_123_coverage,
)
from ashl_core_v1.runtime.temporal_tail_evidence_adapter import (
    build_closure_links,
    build_temporal_tail_evidence,
)


class TemporalTailEvidenceAdapterTests(unittest.TestCase):
    def test_late_structural_regions_are_open_and_semantic_free(self) -> None:
        window = build_observation_window_state(
            runtime_session_id="runtime:test",
            perception_session_id="perception:test",
            observation_window_id="window:test",
            experiment_run_id="run:test",
            audit_group_id="group:test",
        )
        coverage = build_synthetic_package_123_coverage(
            scenario="late_event",
            experiment_run_id="run:test",
        )
        result = build_temporal_tail_evidence(
            observation_window=window,
            coverage_records=coverage,
            temporal_bundle_or_context_id="temporal:test",
            evaluated_at_event_time_ns=4_750_000_000,
        )
        self.assertIsNone(result.tail_evidence.semantic_label)
        self.assertTrue(result.tail_evidence.structural_tail_only)
        self.assertTrue(result.tail_evidence.open_visual_region_refs)
        self.assertTrue(result.tail_evidence.open_audio_region_refs)
        self.assertEqual(result.tail_evidence.experiment_run_id, "run:test")

        links = build_closure_links(
            open_regions=result.open_regions,
            coverage_records=coverage,
            base_deadline_event_time_ns=5_000_000_000,
            final_deadline_event_time_ns=6_500_000_000,
        )
        self.assertTrue(links)
        self.assertTrue(all(item.closure_event_time_ns > 5_000_000_000 for item in links))
        self.assertTrue(
            all(
                item.open_region_observation_id
                in {region.open_region_observation_id for region in result.open_regions}
                for item in links
            )
        )

    def test_stable_tail_does_not_create_open_region(self) -> None:
        window = build_observation_window_state(
            runtime_session_id="runtime:stable",
            perception_session_id="perception:stable",
            observation_window_id="window:stable",
            experiment_run_id="run:stable",
            audit_group_id="group:stable",
            scenario_name="stable_baseline_control",
        )
        result = build_temporal_tail_evidence(
            observation_window=window,
            coverage_records=build_synthetic_package_123_coverage(
                scenario="stable_baseline_control",
                experiment_run_id="run:stable",
            ),
            temporal_bundle_or_context_id="temporal:stable",
            evaluated_at_event_time_ns=4_750_000_000,
        )
        self.assertEqual(result.open_regions, tuple())

    def test_coverage_from_another_run_is_not_consumed(self) -> None:
        window = build_observation_window_state(
            runtime_session_id="runtime:scope",
            perception_session_id="perception:scope",
            observation_window_id="window:scope",
            experiment_run_id="run:expected",
            audit_group_id="group:scope",
        )
        result = build_temporal_tail_evidence(
            observation_window=window,
            coverage_records=build_synthetic_package_123_coverage(
                scenario="late_event",
                experiment_run_id="run:other",
            ),
            temporal_bundle_or_context_id="temporal:scope",
            evaluated_at_event_time_ns=4_750_000_000,
        )
        self.assertFalse(result.tail_evidence.continuous_source_coverage)
        self.assertEqual(result.open_regions, tuple())


if __name__ == "__main__":
    unittest.main()
