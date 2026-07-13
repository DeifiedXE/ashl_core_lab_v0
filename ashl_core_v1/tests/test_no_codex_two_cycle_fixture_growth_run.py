import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.runtime.no_codex_two_cycle_fixture_growth_run import (
    create_two_cycle_fixture_growth_run,
    fixture_payload_for_kind,
    run_two_cycle_fixture_growth_demo,
    validate_two_cycle_growth_lineage,
)
from ashl_core_v1.runtime.session_learning_evidence_identity import FULL_COMMIT_APPROVAL_SCOPE
from ashl_core_v1.runtime.teacher_gated_session_store import TeacherGatedSessionStore


APPROVAL_TEXT = "I approve this exact reviewed evidence for interpretation and working readback."


class NoCodexTwoCycleFixtureGrowthRunTests(unittest.TestCase):
    def test_run_record_requires_explicit_state_dir_and_deterministic_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            record = create_two_cycle_fixture_growth_run(
                state_dir=directory,
                fixture_kind="camera_unknown_low_level_event",
            )
            self.assertEqual(record.run_status, "created")
            self.assertEqual(record.fixture_kind, "camera_unknown_low_level_event")
            self.assertNotEqual(record.fixture_payload_sha256, "")
            self.assertEqual(
                record.fixture_payload_sha256,
                create_two_cycle_fixture_growth_run(
                    state_dir=directory,
                    fixture_kind="camera_unknown_low_level_event",
                ).fixture_payload_sha256,
            )
        self.assertEqual(
            fixture_payload_for_kind("camera_unknown_low_level_event")["event_type"],
            "camera_unknown_low_level_event",
        )

    def test_two_cycle_demo_completes_with_exact_readback_consumption(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            payload = run_two_cycle_fixture_growth_demo(
                state_dir=directory,
                teacher_decision="approved",
                approval_scope=FULL_COMMIT_APPROVAL_SCOPE,
                teacher_approval_text=APPROVAL_TEXT,
                reason_code="teacher_verified_exact_evidence",
            )
            self.assertTrue(payload["lineage"]["valid"])
            self.assertEqual(payload["orchestrator_worker_subprocess_count"], 2)
            self.assertFalse(payload["shell_used"])
            self.assertEqual(payload["arbitrary_subprocess_count"], 0)

            cycle_one = payload["cycle_one"]["cycle_one_commit_receipt"]
            cycle_two = payload["cycle_two"]["cycle_two_readback_consumption_receipt"]
            self.assertTrue(cycle_one["session_committed"])
            self.assertIn(
                cycle_one["working_readback_commit_id"],
                cycle_two["loaded_working_readback_commit_ids"],
            )
            self.assertIn(
                cycle_one["evidence_identity_sha256"],
                cycle_two["loaded_evidence_identity_hashes"],
            )
            self.assertTrue(cycle_two["loaded_before_event_processing"])
            self.assertTrue(cycle_two["readback_loaded"])
            self.assertTrue(cycle_two["readback_evaluated"])
            self.assertTrue(cycle_two["matching_rule_found"])
            self.assertTrue(cycle_two["candidate_delta_applied"])
            self.assertTrue(cycle_two["readback_consumed"])
            self.assertGreaterEqual(cycle_two["nonzero_delta_count"], 1)

            store = TeacherGatedSessionStore(directory)
            lineage = validate_two_cycle_growth_lineage(Path(directory), payload["run_id"])
            self.assertTrue(lineage.valid)
            self.assertEqual(store.count_rows("two_cycle_fixture_growth_runs"), 1)
            self.assertEqual(store.count_rows("cycle_one_growth_commit_receipts"), 1)
            self.assertEqual(store.count_rows("cycle_two_readback_consumption_receipts"), 1)


if __name__ == "__main__":
    unittest.main()
