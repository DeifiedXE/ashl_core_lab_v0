import contextlib
import io
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from ashl_core_v1.runtime.guided_cradle_growth_teacher_console import (
    session_list_pending_reviews_from_guided_cradle_growth_console,
    session_list_persisted_from_guided_cradle_growth_console,
    session_persist_waiting_from_guided_cradle_growth_console,
    session_resume_and_commit_from_guided_cradle_growth_console,
    session_review_decision_from_guided_cradle_growth_console,
    session_rollback_from_guided_cradle_growth_console,
    session_show_active_readback_from_guided_cradle_growth_console,
    session_show_persistence_summary_from_guided_cradle_growth_console,
    session_validate_resume_commit_from_guided_cradle_growth_console,
)
from ashl_core_v1.runtime.teacher_gated_session_resume_commit import (
    REQUIRED_APPROVED_BINDINGS,
    TeacherGatedSessionResumeCommitRuntime,
    build_demo_approved_commit,
    build_demo_nonfinal_pause,
    build_demo_persisted_waiting_session,
    build_demo_rejected_rollback,
    build_teacher_gated_session_resume_commit_audit,
    build_teacher_gated_session_resume_commit_readiness,
    validate_reviewed_interpretation_commit_record,
    validate_teacher_decision_record,
    validate_teacher_gated_session_resume_commit_audit,
    validate_teacher_gated_session_resume_commit_readiness,
)
from ashl_core_v1.runtime.teacher_gated_session_resume_commit_cli import (
    main as resume_commit_cli_main,
)
from ashl_core_v1.runtime.teacher_gated_session_store import TeacherGatedSessionStore


class TeacherGatedSessionResumeCommitTests(unittest.TestCase):
    def test_approved_path_commits_reviewed_interpretation_and_readback(self):
        with tempfile.TemporaryDirectory() as directory:
            payload = build_demo_approved_commit(Path(directory))
            session_id = str(payload["session_id"])
            store = TeacherGatedSessionStore(Path(directory))
            result = payload["run_result"]
            audit = payload["resume_commit_audit"]
            readiness = payload["resume_commit_readiness"]
            active_readback = payload["active_working_readback"]
            binding_paths = {
                item["module_path"] + "." + item["callable_name"]
                for item in result["binding_audit_entries"]
            }

            self.assertEqual(result["final_status"], "committed")
            self.assertEqual(result["reviewed_concept_count"], 1)
            self.assertEqual(result["reviewed_interpretation_commit_count"], 1)
            self.assertEqual(result["working_readback_commit_count"], 1)
            self.assertEqual(result["raw_trace_deleted_count"], 0)
            self.assertEqual(result["raw_trace_modified_count"], 0)
            self.assertEqual(audit["audit_status"], "passed_approved_session_commit")
            self.assertTrue(audit["actual_package_90_binding_confirmed"])
            self.assertTrue(audit["actual_package_91_binding_confirmed"])
            self.assertTrue(audit["actual_package_92_binding_confirmed"])
            self.assertTrue(audit["actual_memory_path_binding_confirmed"])
            self.assertEqual(readiness["readiness_status"], "ready_for_no_codex_two_cycle_embodied_growth_run_only")
            self.assertEqual(store.count_rows("reviewed_interpretation_commits", session_id), 1)
            self.assertEqual(store.count_rows("working_readback_commits", session_id), 1)
            self.assertEqual(store.count_rows("session_commit_records", session_id), 1)
            self.assertGreaterEqual(len(active_readback), 1)
            self.assertNotIn("raw_trace_payload", active_readback[0])
            self.assertTrue(active_readback[0]["source_trace_refs"])
            for required in REQUIRED_APPROVED_BINDINGS:
                self.assertIn(required, binding_paths)
            validation = validate_teacher_gated_session_resume_commit_audit(audit)
            self.assertTrue(validation["valid"])
            self.assertTrue(validate_teacher_gated_session_resume_commit_readiness(readiness)["valid"])

    def test_rejected_path_rolls_back_without_interpretation_commit(self):
        with tempfile.TemporaryDirectory() as directory:
            payload = build_demo_rejected_rollback(Path(directory))
            session_id = str(payload["session_id"])
            store = TeacherGatedSessionStore(Path(directory))

            self.assertEqual(payload["run_result"]["final_status"], "rolled_back")
            self.assertEqual(payload["resume_commit_audit"]["audit_status"], "passed_rejected_session_rollback")
            self.assertEqual(store.count_rows("reviewed_interpretation_commits", session_id), 0)
            self.assertEqual(store.count_rows("working_readback_commits", session_id), 0)
            self.assertEqual(store.count_rows("session_rollback_records", session_id), 1)
            self.assertEqual(payload["run_result"]["raw_trace_deleted_count"], 0)
            self.assertEqual(payload["run_result"]["raw_trace_modified_count"], 0)

    def test_nonfinal_teacher_decisions_pause_without_commit(self):
        for decision in ("deferred", "needs_more_evidence", "conflict_detected"):
            with self.subTest(decision=decision):
                with tempfile.TemporaryDirectory() as directory:
                    payload = build_demo_nonfinal_pause(Path(directory), decision=decision)
                    session_id = str(payload["session_id"])
                    store = TeacherGatedSessionStore(Path(directory))
                    self.assertEqual(payload["run_result"]["final_status"], "paused")
                    self.assertEqual(payload["teacher_decision"]["decision"], decision)
                    self.assertEqual(payload["resume_commit_audit"]["audit_status"], "passed_nonfinal_session_pause")
                    self.assertEqual(store.count_rows("reviewed_interpretation_commits", session_id), 0)
                    self.assertEqual(store.count_rows("working_readback_commits", session_id), 0)

    def test_raw_trace_hashes_are_preserved_across_commit_and_rollback(self):
        with tempfile.TemporaryDirectory() as directory:
            persisted = build_demo_persisted_waiting_session(Path(directory))
            session_id = str(persisted["session_id"])
            review_id = str(persisted["pending_teacher_reviews"][0]["pending_teacher_review_id"])
            store = TeacherGatedSessionStore(Path(directory))
            before = store.raw_trace_payload_hashes(session_id)
            runtime = TeacherGatedSessionResumeCommitRuntime()
            decision = runtime.apply_teacher_decision(
                session_id,
                review_id,
                "approved",
                ("teacher_verified",),
                "Approved.",
                Path(directory),
            )
            runtime.resume_after_approval(session_id, decision.teacher_decision_id, Path(directory))
            self.assertEqual(before, store.raw_trace_payload_hashes(session_id))

        with tempfile.TemporaryDirectory() as directory:
            persisted = build_demo_persisted_waiting_session(Path(directory))
            session_id = str(persisted["session_id"])
            review_id = str(persisted["pending_teacher_reviews"][0]["pending_teacher_review_id"])
            store = TeacherGatedSessionStore(Path(directory))
            before = store.raw_trace_payload_hashes(session_id)
            runtime = TeacherGatedSessionResumeCommitRuntime()
            decision = runtime.apply_teacher_decision(
                session_id,
                review_id,
                "rejected",
                ("teacher_rejected",),
                "Rejected.",
                Path(directory),
            )
            runtime.close_rejected_session(session_id, decision.teacher_decision_id, Path(directory))
            self.assertEqual(before, store.raw_trace_payload_hashes(session_id))

    def test_atomic_failure_leaves_no_interpreted_commit(self):
        with tempfile.TemporaryDirectory() as directory:
            persisted = build_demo_persisted_waiting_session(Path(directory))
            session_id = str(persisted["session_id"])
            review_id = str(persisted["pending_teacher_reviews"][0]["pending_teacher_review_id"])
            store = TeacherGatedSessionStore(Path(directory))
            runtime = TeacherGatedSessionResumeCommitRuntime()
            decision = runtime.apply_teacher_decision(
                session_id,
                review_id,
                "approved",
                ("teacher_verified",),
                "Approved.",
                Path(directory),
            )
            result = runtime.resume_after_approval(
                session_id,
                decision.teacher_decision_id,
                Path(directory),
                force_fail_after="working_readback_commits",
            )
            audit = build_teacher_gated_session_resume_commit_audit(
                store=store,
                session_id=session_id,
                run_result=result,
            )
            self.assertEqual(result.final_status, "failed")
            self.assertEqual(store.count_rows("reviewed_interpretation_commits", session_id), 0)
            self.assertEqual(store.count_rows("working_readback_commits", session_id), 0)
            self.assertEqual(audit.audit_status, "passed_teacher_gated_session_resume_and_commit")
            self.assertEqual(store.list_sessions()[0]["current_status"], "failed")

    def test_validation_blocks_automatic_and_unreviewed_records(self):
        with tempfile.TemporaryDirectory() as directory:
            waiting = build_demo_persisted_waiting_session(Path(directory))
            session_id = str(waiting["session_id"])
            store = TeacherGatedSessionStore(Path(directory))
            pending = store.list_pending_reviews(session_id)[0]
            decision = TeacherGatedSessionResumeCommitRuntime().apply_teacher_decision(
                session_id,
                pending.pending_teacher_review_id,
                "deferred",
                ("later",),
                "Need more review.",
                Path(directory),
            )
            bad_decision = replace(decision, explicit_teacher_action=False)
            self.assertFalse(validate_teacher_decision_record(bad_decision, pending_review=pending)["valid"])

        with tempfile.TemporaryDirectory() as directory:
            payload = build_demo_approved_commit(Path(directory))
            session_id = str(payload["session_id"])
            store = TeacherGatedSessionStore(Path(directory))
            commit_payload = store.load_active_working_readback()[0]
            self.assertIn("source_trace_refs", commit_payload)
            bad_audit = build_teacher_gated_session_resume_commit_audit(
                store=store,
                session_id=session_id,
                run_result=type("Run", (), payload["run_result"])(),  # type: ignore[arg-type]
                force_unreviewed_interpretation_commit=True,
            )
            self.assertEqual(bad_audit.audit_status, "blocked_unreviewed_interpretation_commit")

    def test_reviewed_interpretation_commit_validator_blocks_raw_payload_and_missing_refs(self):
        with tempfile.TemporaryDirectory() as directory:
            payload = build_demo_approved_commit(Path(directory))
            store = TeacherGatedSessionStore(Path(directory))
            readback = store.load_active_working_readback()[0]
            commit_row = {
                "reviewed_interpretation_commit_id": readback["interpretation_commit_id"],
                "schema_version": "qingyin_reviewed_interpretation_commit_v0",
                "created_at": "2026-07-12T00:00:00+00:00",
                "session_id": str(payload["session_id"]),
                "teacher_decision_id": str(payload["teacher_decision"]["teacher_decision_id"]),
                "source_learning_feedback_candidate_ref": "candidate",
                "source_concept_candidate_ref": "concept_candidate",
                "source_refined_concept_candidate_ref": "refined",
                "source_reviewed_concept_ref": "reviewed",
                "memory_learning_trace_ref": "memory_learning_trace",
                "memory_routing_trace_ref": "memory_routing_trace",
                "memory_application_data_ref": "memory_application_data",
                "working_readback_commit_ref": readback["working_readback_commit_id"],
                "reviewed_interpretation_summary": "summary",
                "reviewed_scope": "scope",
                "counterexample_scope": "counterexamples",
                "source_trace_refs": tuple(),
                "stores_interpretation_only": False,
                "contains_raw_trace_payload": True,
                "concept_id_embedded_into_raw_history": False,
                "teacher_approved": True,
                "automatic_approval_created": False,
                "commit_status": "active",
            }
            validation = validate_reviewed_interpretation_commit_record(commit_row)
            self.assertFalse(validation["valid"])
            self.assertIn("missing_source_trace_refs", validation["reasons"])
            self.assertIn("raw_payload_or_non_interpretation_commit", validation["reasons"])

    def test_audit_blocked_cases(self):
        with tempfile.TemporaryDirectory() as directory:
            payload = build_demo_approved_commit(Path(directory))
            session_id = str(payload["session_id"])
            store = TeacherGatedSessionStore(Path(directory))
            result = type("Run", (), payload["run_result"])()  # type: ignore[arg-type]
            cases = {
                "force_automatic_teacher_decision": "blocked_automatic_teacher_decision",
                "force_duplicate_final_decision": "blocked_duplicate_final_decision",
                "force_fake_package_90": "blocked_fake_learning_pipeline_binding",
                "force_fake_package_91": "blocked_fake_learning_pipeline_binding",
                "force_fake_package_92": "blocked_fake_learning_pipeline_binding",
                "force_fake_memory_path": "blocked_fake_memory_path_binding",
                "force_raw_trace_deletion": "blocked_raw_trace_deletion",
                "force_raw_trace_modification": "blocked_raw_trace_modification",
                "force_raw_trace_summarization": "blocked_raw_trace_summarization",
                "force_concept_id_in_raw_history": "blocked_concept_id_in_raw_history",
                "force_missing_source_refs": "blocked_missing_source_trace_refs",
                "force_partial_commit": "blocked_partial_commit",
                "force_core_memory_write": "blocked_core_memory_write",
                "force_external_control": "blocked_external_control",
                "force_first_output": "blocked_first_output",
                "force_live_scheduler": "blocked_live_scheduler",
            }
            for flag, status in cases.items():
                with self.subTest(flag=flag):
                    audit = build_teacher_gated_session_resume_commit_audit(
                        store=store,
                        session_id=session_id,
                        run_result=result,
                        **{flag: True},
                    )
                    self.assertEqual(audit.audit_status, status)

    def test_readiness_recommendations_keep_forbidden_scopes_false(self):
        with tempfile.TemporaryDirectory() as directory:
            payload = build_demo_approved_commit(Path(directory))
            readiness = payload["resume_commit_readiness"]
            self.assertTrue(readiness["ready_for_no_codex_two_cycle_embodied_growth_run"])
            self.assertTrue(readiness["ready_for_persisted_readback_second_session"])
            self.assertFalse(readiness["ready_for_unrestricted_long_term_memory"])
            self.assertFalse(readiness["ready_for_core_memory"])
            self.assertFalse(readiness["ready_for_real_hardware"])
            self.assertFalse(readiness["ready_for_external_control"])
            self.assertFalse(readiness["ready_for_first_output"])
            self.assertFalse(readiness["ready_for_live_scheduler"])
            self.assertFalse(readiness["ready_for_open_ended_loop"])

    def test_cli_commands_work(self):
        commands = (
            ["run-demo-approved-commit"],
            ["run-demo-rejected-rollback"],
            ["run-demo-needs-more-evidence-pause"],
            ["validate-demo-resume-commit"],
        )
        for command in commands:
            with self.subTest(command=command):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(resume_commit_cli_main(list(command)), 0)

        with tempfile.TemporaryDirectory() as directory:
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(
                    resume_commit_cli_main(["persist-demo-waiting-session", "--state-dir", directory]),
                    0,
                )
            store = TeacherGatedSessionStore(Path(directory))
            session_id = store.list_sessions()[0]["session_id"]
            review_id = store.list_pending_reviews(str(session_id))[0].pending_teacher_review_id
            persistent_commands = (
                ["list-sessions", "--state-dir", directory],
                ["show-session", "--state-dir", directory, "--session-id", str(session_id)],
                ["list-pending-reviews", "--state-dir", directory, "--session-id", str(session_id)],
                [
                    "decide",
                    "--state-dir",
                    directory,
                    "--session-id",
                    str(session_id),
                    "--review-id",
                    review_id,
                    "--decision",
                    "approved",
                    "--reason-code",
                    "teacher_verified",
                    "--teacher-note",
                    "Approved.",
                ],
                ["resume-and-commit", "--state-dir", directory, "--session-id", str(session_id)],
                ["show-active-readback", "--state-dir", directory],
                ["validate-store", "--state-dir", directory],
            )
            for command in persistent_commands:
                with self.subTest(command=command):
                    with contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(resume_commit_cli_main(list(command)), 0)

    def test_guided_console_persistent_flow_works(self):
        with tempfile.TemporaryDirectory() as directory:
            persisted = session_persist_waiting_from_guided_cradle_growth_console(Path(directory))
            session_id = str(persisted["session_id"])
            review_id = str(persisted["pending_teacher_reviews"][0]["pending_teacher_review_id"])
            self.assertEqual(
                session_list_persisted_from_guided_cradle_growth_console(Path(directory))["sessions"][0]["session_id"],
                session_id,
            )
            pending = session_list_pending_reviews_from_guided_cradle_growth_console(Path(directory), session_id)
            self.assertEqual(len(pending["pending_teacher_reviews"]), 1)
            decision = session_review_decision_from_guided_cradle_growth_console(
                Path(directory),
                session_id,
                review_id,
                "approved",
                ("teacher_verified",),
                "Approved from guided console.",
            )
            self.assertFalse(decision["automatic_teacher_decision_created"])
            committed = session_resume_and_commit_from_guided_cradle_growth_console(Path(directory), session_id)
            self.assertEqual(committed["run_result"]["final_status"], "committed")
            self.assertGreaterEqual(len(session_show_active_readback_from_guided_cradle_growth_console(Path(directory))["active_working_readback"]), 1)
            self.assertIn("Teacher-Gated Persisted Session", session_show_persistence_summary_from_guided_cradle_growth_console(Path(directory), session_id)["summary"])
            self.assertTrue(session_validate_resume_commit_from_guided_cradle_growth_console()["validation"]["valid"])

    def test_guided_console_rejected_rollback_works(self):
        with tempfile.TemporaryDirectory() as directory:
            persisted = session_persist_waiting_from_guided_cradle_growth_console(Path(directory))
            session_id = str(persisted["session_id"])
            review_id = str(persisted["pending_teacher_reviews"][0]["pending_teacher_review_id"])
            session_review_decision_from_guided_cradle_growth_console(
                Path(directory),
                session_id,
                review_id,
                "rejected",
                ("teacher_rejected",),
                "Rejected from guided console.",
            )
            rolled_back = session_rollback_from_guided_cradle_growth_console(Path(directory), session_id)
            self.assertEqual(rolled_back["run_result"]["final_status"], "rolled_back")


if __name__ == "__main__":
    unittest.main()
