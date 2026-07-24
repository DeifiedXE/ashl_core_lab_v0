import unittest

from ashl_core_v1.runtime.host_sensor_types import stable_id, utc_now
from ashl_core_v1.runtime.package_123_types import (
    READBACK_INFLUENCE_SCHEMA_VERSION,
    RealPerceptionReadbackInfluenceRecord,
)


class Package123ReadbackInfluenceTests(unittest.TestCase):
    def test_influence_requires_hot_path_nonzero_delta_and_no_experiment_shortcut(self):
        record = RealPerceptionReadbackInfluenceRecord(
            influence_record_id=stable_id("package_123_readback_influence"),
            schema_version=READBACK_INFLUENCE_SCHEMA_VERSION,
            created_at=utc_now(),
            cycle_1_memory_application_data_id="memory_application_data:test",
            cycle_2_candidate_id="candidate:test",
            scorer_id="host_body_readback_internal_action_influence",
            scorer_version="v0",
            score_without_readback=90.0,
            score_with_readback=93.0,
            readback_contribution=3.0,
            influencing_readback_refs=("working_readback_commit:test",),
            matching_evidence_refs=("working_readback_commit:test",),
            actual_runtime_hot_path=True,
            hard_coded_experiment_match_used=False,
        )
        self.assertGreater(record.readback_contribution, 0.0)
        self.assertTrue(record.actual_runtime_hot_path)
        self.assertFalse(record.hard_coded_experiment_match_used)

        payload = record.to_dict()
        payload["readback_contribution"] = 0.0
        with self.assertRaises(ValueError):
            RealPerceptionReadbackInfluenceRecord.from_dict(payload)

        payload = record.to_dict()
        payload["hard_coded_experiment_match_used"] = True
        with self.assertRaises(ValueError):
            RealPerceptionReadbackInfluenceRecord.from_dict(payload)


if __name__ == "__main__":
    unittest.main()
