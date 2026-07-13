import tempfile
import unittest

from ashl_core_v1.runtime.bounded_embodied_session_runtime import (
    BoundedEmbodiedSessionConfig,
    BoundedEmbodiedSessionRuntime,
    BoundedEmbodiedSessionStatus,
)
from ashl_core_v1.runtime.no_codex_two_cycle_fixture_growth_run import (
    create_two_cycle_fixture_growth_run,
    run_worker_process,
)
from ashl_core_v1.runtime.session_learning_evidence_identity import FULL_COMMIT_APPROVAL_SCOPE
from ashl_core_v1.runtime.teacher_gated_session_store import TeacherGatedSessionStore


class CycleTwoReadbackConsumptionTests(unittest.TestCase):
    def test_empty_store_has_no_active_readback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = TeacherGatedSessionStore(directory)
            self.assertEqual(store.load_active_working_readback(), tuple())

    def test_runtime_records_no_consumption_without_loaded_snapshot(self) -> None:
        runtime = BoundedEmbodiedSessionRuntime()
        state = runtime.create_session(BoundedEmbodiedSessionConfig())
        runtime.inject_fixture_host_event(state.session_id, "camera_unknown_low_level_event")
        result = runtime.run_until_blocked(state.session_id)
        self.assertEqual(result.final_status, BoundedEmbodiedSessionStatus.WAITING_TEACHER_REVIEW.value)
        evaluation = runtime._records[state.session_id]["readback_consumption_evaluation"]
        self.assertFalse(evaluation["readback_loaded"])
        self.assertFalse(evaluation["candidate_delta_applied"])
        self.assertFalse(evaluation["readback_consumed"])

    def test_cycle_two_consumption_receipt_has_score_and_lineage_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run = create_two_cycle_fixture_growth_run(state_dir=directory)
            cycle_one = run_worker_process(
                mode="cycle-one",
                state_dir=directory,
                run_id=run.run_id,
                teacher_decision="approved",
                approval_scope=FULL_COMMIT_APPROVAL_SCOPE,
                teacher_approval_text="I approve this exact reviewed evidence for interpretation and working readback.",
                reason_code="teacher_verified_exact_evidence",
            )
            cycle_two = run_worker_process(
                mode="cycle-two",
                state_dir=directory,
                run_id=run.run_id,
            )
            commit = cycle_one["cycle_one_commit_receipt"]
            consumption = cycle_two["cycle_two_readback_consumption_receipt"]
            self.assertEqual(consumption["source_cycle_one_session_id"], commit["session_id"])
            self.assertEqual(consumption["loaded_working_readback_commit_ids"][0], commit["working_readback_commit_id"])
            self.assertEqual(consumption["loaded_evidence_identity_hashes"][0], commit["evidence_identity_sha256"])
            self.assertTrue(consumption["readback_signal_ids"])
            self.assertTrue(consumption["candidate_score_record_ids"])
            self.assertTrue(consumption["ordering_record_ids"])
            self.assertTrue(consumption["internal_action_choice_ids"])
            self.assertTrue(consumption["source_trace_refs"])


if __name__ == "__main__":
    unittest.main()
