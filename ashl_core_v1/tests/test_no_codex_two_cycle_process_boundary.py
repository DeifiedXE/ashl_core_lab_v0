import tempfile
import unittest

from ashl_core_v1.runtime.no_codex_two_cycle_fixture_growth_run import (
    create_two_cycle_fixture_growth_run,
    run_worker_process,
)
from ashl_core_v1.runtime.session_learning_evidence_identity import FULL_COMMIT_APPROVAL_SCOPE
from ashl_core_v1.runtime.teacher_gated_session_store import TeacherGatedSessionStore


class NoCodexTwoCycleProcessBoundaryTests(unittest.TestCase):
    def test_stepwise_workers_are_distinct_process_runtime_store_and_session(self) -> None:
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

            one = cycle_one["cycle_process_receipt"]
            two = cycle_two["cycle_process_receipt"]
            self.assertNotEqual(one["operating_system_pid"], two["operating_system_pid"])
            self.assertNotEqual(one["process_instance_id"], two["process_instance_id"])
            self.assertNotEqual(one["runtime_instance_id"], two["runtime_instance_id"])
            self.assertNotEqual(one["store_connection_id"], two["store_connection_id"])
            self.assertNotEqual(one["session_id"], two["session_id"])
            self.assertTrue(one["store_closed"])
            self.assertTrue(two["store_closed"])
            self.assertTrue(one["process_exit_requested"])
            self.assertTrue(two["process_exit_requested"])

            store = TeacherGatedSessionStore(directory)
            receipts = store.list_cycle_process_receipts(run.run_id)
            self.assertEqual(len(receipts), 2)
            final_run = store.get_two_cycle_run(run.run_id)
            self.assertEqual(final_run["run_status"], "completed")


if __name__ == "__main__":
    unittest.main()
