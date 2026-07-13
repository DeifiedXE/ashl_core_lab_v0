import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.runtime.guided_cradle_growth_teacher_console import (
    session_review_exact_approve_from_guided_cradle_growth_console,
    session_show_approval_scopes_from_guided_cradle_growth_console,
    session_show_review_evidence_from_guided_cradle_growth_console,
    session_show_review_evidence_hash_from_guided_cradle_growth_console,
    session_validate_identity_repair_from_guided_cradle_growth_console,
    session_validate_learning_lineage_from_guided_cradle_growth_console,
)
from ashl_core_v1.runtime.session_evidence_identity_approval_scope_repair import (
    build_demo_insufficient_scope,
    build_demo_runtime_bridge_approved,
    build_demo_trace_collision,
    build_demo_uncertainty_approved,
    validate_demo_repair,
)
from ashl_core_v1.runtime.session_evidence_identity_approval_scope_repair_cli import (
    main as repair_cli_main,
)
from ashl_core_v1.runtime.teacher_gated_session_resume_commit import (
    FULL_COMMIT_APPROVAL_SCOPE,
    build_demo_persisted_waiting_session,
)
from ashl_core_v1.runtime.teacher_gated_session_store import TeacherGatedSessionStore


class SessionEvidenceIdentityApprovalScopeRepairTests(unittest.TestCase):
    def test_approved_uncertainty_path_commits_exact_identity_chain(self):
        with tempfile.TemporaryDirectory() as directory:
            payload = build_demo_uncertainty_approved(Path(directory))
            store = TeacherGatedSessionStore(Path(directory))
            session_id = str(payload["session_id"])
            pending = store.list_pending_reviews(session_id)[0]
            active = store.load_active_working_readback()[0]
            binding_hashes = {row["evidence_identity_sha256"] for row in store.list_learning_pipeline_identity_bindings(session_id)}
            self.assertEqual(payload["identity_repair_audit"]["audit_status"], "passed_session_evidence_identity_and_approval_scope_repair")
            self.assertEqual(active["evidence_identity_sha256"], pending.evidence_identity_sha256)
            self.assertEqual(binding_hashes, {pending.evidence_identity_sha256})
            self.assertEqual(store.count_rows("learning_pipeline_identity_bindings", session_id), 10)
            self.assertEqual(store.count_rows("interpretation_provenance_bindings", session_id), 1)

    def test_runtime_bridge_path_is_not_relabelled_as_uncertainty(self):
        payload = build_demo_runtime_bridge_approved()
        self.assertEqual(payload["run_result"]["final_status"], "committed")
        self.assertEqual(payload["identity_repair_audit"]["audit_status"], "passed_session_evidence_identity_and_approval_scope_repair")
        self.assertEqual(payload["active_working_readback"][0]["evidence_theme"], "runtime_bridge_deferred")

    def test_insufficient_scope_pauses_without_commit(self):
        payload = build_demo_insufficient_scope()
        self.assertEqual(payload["run_result"]["final_status"], "paused")
        self.assertEqual(payload["run_result"]["stop_reason"], "approval_scope_insufficient")
        self.assertEqual(payload["run_result"]["working_readback_commit_count"], 0)
        self.assertEqual(payload["active_working_readback"], ())

    def test_trace_collision_demo_blocks_conflicting_trace_id(self):
        payload = build_demo_trace_collision()
        self.assertEqual(payload["same_trace_id_same_payload"], "idempotent_existing_trace")
        self.assertEqual(payload["same_trace_id_different_payload"], "blocked_trace_identity_collision")
        self.assertTrue(payload["trace_collision_policy_valid"])

    def test_cli_repair_commands_work(self):
        for command in (
            ["show-approval-scopes"],
            ["run-demo-uncertainty-approved"],
            ["run-demo-runtime-bridge-approved"],
            ["run-demo-insufficient-scope"],
            ["run-demo-trace-collision"],
            ["validate-demo-repair"],
        ):
            with self.subTest(command=command):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(repair_cli_main(command), 0)

    def test_cli_persistent_evidence_display_and_lineage_validation_work(self):
        with tempfile.TemporaryDirectory() as directory:
            state_dir = Path(directory)
            persisted = build_demo_persisted_waiting_session(state_dir)
            session_id = str(persisted["session_id"])
            review = persisted["pending_teacher_reviews"][0]
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(
                    repair_cli_main(
                        [
                            "show-pending-evidence",
                            "--state-dir",
                            directory,
                            "--session-id",
                            session_id,
                            "--review-id",
                            str(review["pending_teacher_review_id"]),
                        ]
                    ),
                    0,
                )
                self.assertEqual(
                    repair_cli_main(
                        [
                            "validate-evidence-snapshot",
                            "--state-dir",
                            directory,
                            "--session-id",
                            session_id,
                            "--review-id",
                            str(review["pending_teacher_review_id"]),
                        ]
                    ),
                    0,
                )

    def test_guided_console_exact_approval_flow_works(self):
        with tempfile.TemporaryDirectory() as directory:
            state_dir = Path(directory)
            persisted = build_demo_persisted_waiting_session(state_dir)
            session_id = str(persisted["session_id"])
            review = persisted["pending_teacher_reviews"][0]
            review_id = str(review["pending_teacher_review_id"])
            self.assertIn("approval_scopes", session_show_approval_scopes_from_guided_cradle_growth_console())
            evidence = session_show_review_evidence_from_guided_cradle_growth_console(state_dir, session_id, review_id)
            evidence_hash = session_show_review_evidence_hash_from_guided_cradle_growth_console(state_dir, session_id, review_id)
            self.assertEqual(evidence["evidence_identity_sha256"], evidence_hash["evidence_identity_sha256"])
            decision = session_review_exact_approve_from_guided_cradle_growth_console(
                state_dir,
                session_id,
                review_id,
                evidence_hash["evidence_identity_sha256"],
            )
            self.assertEqual(decision["teacher_decision"]["approval_scope"], FULL_COMMIT_APPROVAL_SCOPE)
            from ashl_core_v1.runtime.guided_cradle_growth_teacher_console import session_resume_and_commit_from_guided_cradle_growth_console

            session_resume_and_commit_from_guided_cradle_growth_console(state_dir, session_id)
            lineage = session_validate_learning_lineage_from_guided_cradle_growth_console(state_dir, session_id)
            self.assertEqual(lineage["identity_repair_audit"]["audit_status"], "passed_session_evidence_identity_and_approval_scope_repair")
            self.assertTrue(session_validate_identity_repair_from_guided_cradle_growth_console()["validation"]["valid"])

    def test_validate_demo_repair_passes(self):
        self.assertTrue(validate_demo_repair()["valid"])


if __name__ == "__main__":
    unittest.main()

