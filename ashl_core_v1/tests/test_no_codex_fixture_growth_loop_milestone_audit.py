import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.runtime.guided_cradle_growth_teacher_console import (
    growth_audit_fixture_loop_from_guided_cradle_growth_console,
)
from ashl_core_v1.runtime.no_codex_fixture_growth_loop_milestone_audit import (
    build_no_codex_fixture_growth_loop_milestone_audit,
    show_no_codex_fixture_growth_loop_evidence,
    show_no_codex_fixture_growth_loop_lineage,
)
from ashl_core_v1.runtime.no_codex_two_cycle_fixture_growth_run import (
    run_two_cycle_fixture_growth_demo,
)
from ashl_core_v1.runtime.session_learning_evidence_identity import FULL_COMMIT_APPROVAL_SCOPE


def _build_two_cycle_run() -> tuple[tempfile.TemporaryDirectory, Path, str]:
    directory = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
    state_dir = Path(directory.name)
    result = run_two_cycle_fixture_growth_demo(
        teacher_decision="approved",
        approval_scope=FULL_COMMIT_APPROVAL_SCOPE,
        teacher_approval_text="I approve this exact reviewed evidence for interpretation and working readback.",
        reason_code="teacher_verified_exact_evidence",
        state_dir=state_dir,
    )
    return directory, state_dir, str(result["run_id"])


class NoCodexFixtureGrowthLoopMilestoneAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._directory, cls.state_dir, cls.run_id = _build_two_cycle_run()
        cls.audit = build_no_codex_fixture_growth_loop_milestone_audit(
            state_dir=cls.state_dir,
            run_id=cls.run_id,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls._directory.cleanup()

    def test_audit_passes_actual_two_cycle_run(self) -> None:
        self.assertEqual(self.audit.audit_status, "passed_no_codex_fixture_growth_loop_milestone")
        self.assertTrue(self.audit.package_115_runtime_valid)
        self.assertTrue(self.audit.package_116_commit_valid)
        self.assertTrue(self.audit.package_117_identity_valid)
        self.assertTrue(self.audit.package_118_two_cycle_valid)

    def test_process_runtime_store_and_session_boundaries_are_valid(self) -> None:
        self.assertTrue(self.audit.process_boundary_valid)
        self.assertTrue(self.audit.runtime_boundary_valid)
        self.assertTrue(self.audit.session_boundary_valid)
        self.assertTrue(self.audit.store_connection_boundary_valid)
        self.assertNotEqual(self.audit.cycle_one_process_id, self.audit.cycle_two_process_id)
        self.assertNotEqual(self.audit.cycle_one_runtime_id, self.audit.cycle_two_runtime_id)
        self.assertNotEqual(self.audit.cycle_one_session_id, self.audit.cycle_two_session_id)

    def test_fixture_config_candidate_identity_and_teacher_binding_are_valid(self) -> None:
        self.assertTrue(self.audit.fixture_identity_valid)
        self.assertTrue(self.audit.runtime_config_identity_valid)
        self.assertTrue(self.audit.base_candidate_set_identity_valid)
        self.assertTrue(self.audit.exact_teacher_evidence_binding_valid)
        self.assertTrue(self.audit.teacher_approval_scope_valid)
        self.assertTrue(self.audit.package_90_92_identity_chain_valid)
        self.assertTrue(self.audit.interpretation_commit_valid)
        self.assertTrue(self.audit.working_readback_commit_valid)

    def test_cycle_two_consumes_readback_with_lineage_to_cycle_one_raw_trace(self) -> None:
        self.assertTrue(self.audit.cycle_two_readback_loaded_before_event)
        self.assertTrue(self.audit.cycle_two_readback_evaluated)
        self.assertTrue(self.audit.cycle_two_matching_rule_found)
        self.assertTrue(self.audit.cycle_two_candidate_delta_applied)
        self.assertTrue(self.audit.cycle_two_readback_consumed)
        self.assertTrue(self.audit.cross_session_lineage_complete)
        self.assertTrue(self.audit.lineage_reaches_cycle_one_raw_trace)

    def test_no_codex_and_trace_boundaries_are_valid(self) -> None:
        self.assertEqual(self.audit.codex_runtime_call_count, 0)
        self.assertEqual(self.audit.llm_runtime_call_count, 0)
        self.assertEqual(self.audit.network_model_call_count, 0)
        self.assertEqual(self.audit.arbitrary_runtime_subprocess_call_count, 0)
        self.assertEqual(self.audit.dynamic_code_execution_attempt_count, 0)
        self.assertTrue(self.audit.raw_trace_append_only_valid)
        self.assertTrue(self.audit.raw_trace_unchanged_valid)
        self.assertTrue(self.audit.raw_trace_unsummarized_valid)
        self.assertTrue(self.audit.concept_id_absent_from_raw_history)
        self.assertTrue(self.audit.trace_collision_policy_valid)
        self.assertFalse(self.audit.cycle_two_auto_approval_detected)
        self.assertFalse(self.audit.external_control_detected)
        self.assertFalse(self.audit.first_output_detected)
        self.assertFalse(self.audit.live_scheduler_detected)

    def test_show_evidence_and_lineage_use_existing_records(self) -> None:
        evidence = show_no_codex_fixture_growth_loop_evidence(self.state_dir, self.run_id)
        lineage = show_no_codex_fixture_growth_loop_lineage(self.state_dir, self.run_id)
        self.assertEqual(evidence["run"]["run_id"], self.run_id)
        self.assertEqual(len(evidence["process_receipts"]), 2)
        self.assertTrue(lineage["cross_session_lineage_complete"])
        self.assertTrue(lineage["lineage_reaches_cycle_one_raw_trace"])

    def test_cli_audit_run_works(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core_v1.runtime.no_codex_fixture_growth_loop_milestone_audit_cli",
                "audit-run",
                "--state-dir",
                str(self.state_dir),
                "--run-id",
                self.run_id,
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["audit_status"], "passed_no_codex_fixture_growth_loop_milestone")

    def test_guided_teacher_console_audit_command_works(self) -> None:
        result = growth_audit_fixture_loop_from_guided_cradle_growth_console(
            self.state_dir,
            self.run_id,
        )
        self.assertTrue(result["this_audit_adds_no_new_qingyin_runtime_capability"])
        self.assertEqual(
            result["milestone_audit"]["audit_status"],
            "passed_no_codex_fixture_growth_loop_milestone",
        )


if __name__ == "__main__":
    unittest.main()
