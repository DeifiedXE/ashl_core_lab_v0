from __future__ import annotations

import unittest

from ashl_core_v1.runtime.observation_extension_candidate import (
    create_observation_extension_candidate,
)
from ashl_core_v1.runtime.package_125_observation_extension_runtime import (
    build_observation_extension_authorization,
    build_observation_window_state,
    build_synthetic_package_123_coverage,
)
from ashl_core_v1.runtime.temporal_tail_evidence_adapter import build_temporal_tail_evidence


class ObservationExtensionCandidateTests(unittest.TestCase):
    def _sources(self, scenario: str = "late_event"):
        window = build_observation_window_state(
            runtime_session_id="runtime:candidate",
            perception_session_id="perception:candidate",
            observation_window_id="window:candidate",
            experiment_run_id="run:candidate",
            audit_group_id="group:candidate",
            scenario_name=scenario,
        )
        authorization = build_observation_extension_authorization(
            runtime_session_id=window.runtime_session_id,
            perception_session_id=window.perception_session_id,
        )
        tail = build_temporal_tail_evidence(
            observation_window=window,
            coverage_records=build_synthetic_package_123_coverage(
                scenario=scenario,
                experiment_run_id=window.experiment_run_id,
            ),
            temporal_bundle_or_context_id="temporal:candidate",
            evaluated_at_event_time_ns=4_750_000_000,
        ).tail_evidence
        return window, authorization, tail

    def test_open_tail_creates_structural_candidate_without_side_effect(self) -> None:
        window, authorization, tail = self._sources()
        candidate = create_observation_extension_candidate(
            observation_window=window,
            tail_evidence=tail,
            authorization=authorization,
        )
        self.assertIsNotNone(candidate)
        self.assertEqual(window.current_deadline_event_time_ns, 5_000_000_000)
        self.assertIsNone(candidate.semantic_label)
        self.assertFalse(candidate.memory_used)
        self.assertFalse(candidate.thought_engine_used)
        self.assertFalse(candidate.stimulus_ground_truth_used)

    def test_stable_tail_and_wrong_window_tail_create_no_candidate(self) -> None:
        window, authorization, stable_tail = self._sources("stable_baseline_control")
        self.assertIsNone(
            create_observation_extension_candidate(
                observation_window=window,
                tail_evidence=stable_tail,
                authorization=authorization,
            )
        )
        late_window, late_authorization, late_tail = self._sources()
        wrong_window = build_observation_window_state(
            runtime_session_id=late_window.runtime_session_id,
            perception_session_id=late_window.perception_session_id,
            observation_window_id="window:other",
            experiment_run_id=late_window.experiment_run_id,
            audit_group_id=late_window.audit_group_id,
        )
        self.assertIsNone(
            create_observation_extension_candidate(
                observation_window=wrong_window,
                tail_evidence=late_tail,
                authorization=late_authorization,
            )
        )


if __name__ == "__main__":
    unittest.main()
