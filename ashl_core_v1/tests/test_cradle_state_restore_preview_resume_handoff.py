from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.runtime.guided_cradle_growth_teacher_console import (
    build_state_handoff_from_guided_cradle_growth_console,
    build_state_restore_preview_from_guided_cradle_growth_console,
    create_state_resume_handoff_from_guided_cradle_growth_console,
    get_guided_cradle_growth_status,
    run_state_resume_precheck_from_guided_cradle_growth_console,
    select_authorize_state_resume_from_guided_cradle_growth_console,
    show_state_restore_preview_from_guided_cradle_growth_console,
    show_state_resume_handoff_from_guided_cradle_growth_console,
    validate_state_resume_handoff_from_guided_cradle_growth_console,
)
from ashl_core_v1.state.cradle_state_persistence_handoff import (
    build_cradle_state_handoff_bundle,
    write_cradle_state_handoff_bundle,
)
from ashl_core_v1.state.cradle_state_resume_precheck import (
    CradleResumeOptionRecord,
    load_cradle_resume_precheck_bundle,
    run_cradle_resume_precheck,
)
from ashl_core_v1.state.cradle_state_resume_selection_authorization import (
    ResumeAuthorizationSafetyAuditRecord,
    SelectedResumeBookmarkRecord,
    TeacherResumeAuthorizationRecord,
    load_resume_selection_authorization_bundle,
    run_resume_selection_authorization,
)
from ashl_core_v1.state.cradle_state_restore_preview_resume_handoff import (
    KNOWN_RESTORE_HANDOFF_FILES,
    RESUME_HANDOFF_FILE,
    RESUME_HANDOFF_SAFETY_AUDIT_FILE,
    RESTORE_PREVIEW_FILE,
    CradleRestorePreviewRecord,
    TeacherGatedResumeHandoffRecord,
    build_cradle_restore_preview,
    build_resume_handoff_safety_audit,
    build_teacher_gated_resume_handoff,
    clear_restore_resume_handoff,
    load_cradle_restore_preview,
    load_restore_resume_handoff_bundle,
    run_cradle_restore_preview,
    run_teacher_gated_resume_handoff,
    validate_cradle_restore_preview,
    validate_teacher_gated_resume_handoff,
    write_restore_resume_handoff_bundle,
)


class CradleStateRestorePreviewResumeHandoffTests(unittest.TestCase):
    def test_build_restore_preview_from_valid_authorization_succeeds(self) -> None:
        bundle, selected, authorization, auth_safety = self._valid_sources()
        preview = build_cradle_restore_preview(
            handoff_bundle=bundle,
            selected=selected,
            authorization=authorization,
            authorization_safety_audit=auth_safety,
        )
        validation = validate_cradle_restore_preview(preview)
        self.assertTrue(validation["valid"])
        self.assertEqual(preview.preview_status, "preview_ready")
        self.assertTrue(preview.would_create_resume_handoff)

    def test_restore_preview_preserves_source_ids(self) -> None:
        bundle, selected, authorization, auth_safety = self._valid_sources()
        preview = build_cradle_restore_preview(
            handoff_bundle=bundle,
            selected=selected,
            authorization=authorization,
            authorization_safety_audit=auth_safety,
        )
        self.assertEqual(preview.source_handoff_id, bundle.handoff.handoff_id)
        self.assertEqual(
            preview.source_selected_resume_bookmark_id,
            selected.selected_resume_bookmark_id,
        )
        self.assertEqual(preview.source_authorization_id, authorization.authorization_id)

    def test_restore_preview_maps_inspect_status_to_teacher_interface_status(self) -> None:
        self._assert_mapping("inspect_status", "teacher_interface_status")

    def test_restore_preview_maps_review_pending_candidates_to_teacher_interface_review_candidates(self) -> None:
        self._assert_mapping(
            "review_pending_candidates",
            "teacher_interface_review_candidates",
        )

    def test_restore_preview_maps_build_memory_trace_precheck_to_memory_engine_build_trace(self) -> None:
        self._assert_mapping("build_memory_trace_precheck", "memory_engine_build_trace")

    def test_restore_preview_maps_preview_readback_precheck_to_memory_engine_preview_readback(self) -> None:
        self._assert_mapping("preview_readback_precheck", "memory_engine_preview_readback")

    def test_restore_preview_maps_apply_readback_precheck_to_memory_engine_apply_readback(self) -> None:
        self._assert_mapping("apply_readback_precheck", "memory_engine_apply_readback")

    def test_restore_preview_maps_run_readback_contrast_precheck_to_task_engine_readback_contrast_entry(self) -> None:
        self._assert_mapping(
            "run_readback_contrast_precheck",
            "task_engine_readback_contrast_entry",
        )

    def test_restore_preview_maps_build_loop_evidence_precheck_to_task_engine_loop_evidence_entry(self) -> None:
        self._assert_mapping(
            "build_loop_evidence_precheck",
            "task_engine_loop_evidence_entry",
        )

    def test_restore_preview_maps_inspect_growth_readiness_to_state_engine_growth_readiness_inspect(self) -> None:
        self._assert_mapping(
            "inspect_growth_readiness",
            "state_engine_growth_readiness_inspect",
        )

    def test_restore_preview_maps_resume_suspended_task_precheck_to_task_engine_suspended_task_resume_entry(self) -> None:
        self._assert_mapping(
            "resume_suspended_task_precheck",
            "task_engine_suspended_task_resume_entry",
        )

    def test_restore_preview_maps_run_new_case_precheck_to_task_engine_new_case_entry(self) -> None:
        self._assert_mapping("run_new_case_precheck", "task_engine_new_case_entry")

    def test_missing_authorization_blocks_preview(self) -> None:
        bundle, selected, _authorization, _auth_safety = self._valid_sources()
        preview = build_cradle_restore_preview(
            handoff_bundle=bundle,
            selected=selected,
            authorization=None,
            authorization_safety_audit=None,
        )
        self.assertEqual(preview.preview_status, "blocked_missing_authorization")
        self.assertFalse(preview.would_create_resume_handoff)

    def test_invalid_authorization_blocks_preview(self) -> None:
        bundle, selected, authorization, auth_safety = self._valid_sources()
        bad_authorization = self._mutated_authorization(
            authorization,
            authorization_status="blocked_invalid_option",
        )
        preview = build_cradle_restore_preview(
            handoff_bundle=bundle,
            selected=selected,
            authorization=bad_authorization,
            authorization_safety_audit=auth_safety,
        )
        self.assertEqual(preview.preview_status, "blocked_invalid_authorization")

    def test_authorization_authorized_to_resume_now_true_blocks_preview(self) -> None:
        self._assert_authorization_flag_blocks_preview("authorized_to_resume_now")

    def test_authorization_authorized_to_create_tick_now_true_blocks_preview(self) -> None:
        self._assert_authorization_flag_blocks_preview("authorized_to_create_tick_now")

    def test_authorization_authorized_to_execute_action_now_true_blocks_preview(self) -> None:
        self._assert_authorization_flag_blocks_preview("authorized_to_execute_action_now")

    def test_authorization_authorized_to_write_memory_now_true_blocks_preview(self) -> None:
        self._assert_authorization_flag_blocks_preview("authorized_to_write_memory_now")

    def test_create_resume_handoff_from_valid_preview_succeeds(self) -> None:
        bundle, selected, authorization, auth_safety = self._valid_sources()
        preview = build_cradle_restore_preview(
            handoff_bundle=bundle,
            selected=selected,
            authorization=authorization,
            authorization_safety_audit=auth_safety,
        )
        handoff = build_teacher_gated_resume_handoff(
            preview=preview,
            selected=selected,
            authorization=authorization,
            teacher_confirmation_text=self._teacher_confirmation_text(),
        )
        safety = build_resume_handoff_safety_audit(
            preview=preview,
            selected=selected,
            authorization=authorization,
            authorization_safety_audit=auth_safety,
            handoff=handoff,
        )
        validation = validate_teacher_gated_resume_handoff(preview, handoff, safety)
        self.assertTrue(validation["valid"])
        self.assertEqual(handoff.handoff_status, "handoff_ready")
        self.assertTrue(handoff.handoff_created)
        self.assertEqual(safety.audit_status, "passed")

    def test_resume_handoff_requires_teacher_confirmation_text(self) -> None:
        bundle, selected, authorization, auth_safety = self._valid_sources()
        preview = build_cradle_restore_preview(
            handoff_bundle=bundle,
            selected=selected,
            authorization=authorization,
            authorization_safety_audit=auth_safety,
        )
        handoff = build_teacher_gated_resume_handoff(
            preview=preview,
            selected=selected,
            authorization=authorization,
            teacher_confirmation_text=" ",
        )
        safety = build_resume_handoff_safety_audit(
            preview=preview,
            selected=selected,
            authorization=authorization,
            authorization_safety_audit=auth_safety,
            handoff=handoff,
        )
        self.assertEqual(handoff.handoff_status, "blocked_missing_teacher_confirmation")
        self.assertFalse(handoff.handoff_created)
        self.assertEqual(safety.audit_status, "blocked_missing_teacher_confirmation")

    def test_handoff_creates_target_engine_entry_payload_without_executable_entries(self) -> None:
        _preview, handoff, _safety = self._valid_handoff_bundle()
        payload = handoff.target_engine_entry_payload
        self.assertTrue(payload["manual_next_step_required"])
        self.assertIn("resume_kind", payload)
        self.assertNotIn("callback", payload)
        self.assertNotIn("command_object", payload)
        self.assertNotIn("runner", payload)

    def test_handoff_has_allowed_next_manual_command_label(self) -> None:
        _preview, handoff, _safety = self._valid_handoff_bundle()
        self.assertIsInstance(handoff.allowed_next_manual_command, str)
        self.assertTrue(handoff.allowed_next_manual_command)
        self.assertTrue(handoff.next_manual_command_requires_teacher)

    def test_safety_audit_blocks_forbidden_runtime_authority_flags(self) -> None:
        preview, handoff, _handoff_safety = self._valid_handoff_bundle()
        _bundle, selected, authorization, auth_safety = self._valid_sources()
        bad_handoff = self._mutated_handoff(handoff, scheduler_created=True)
        safety = build_resume_handoff_safety_audit(
            preview=preview,
            selected=selected,
            authorization=authorization,
            authorization_safety_audit=auth_safety,
            handoff=bad_handoff,
        )
        self.assertEqual(
            safety.audit_status,
            "blocked_forbidden_runtime_authority_detected",
        )
        self.assertFalse(safety.no_scheduler)

    def test_forbidden_runtime_flags_are_false_for_valid_handoff(self) -> None:
        preview, handoff, safety = self._valid_handoff_bundle()
        self.assertFalse(preview.task_resumed)
        self.assertFalse(preview.task_runner_started)
        self.assertFalse(preview.new_task_created)
        self.assertFalse(preview.new_tick_created)
        self.assertFalse(preview.scheduler_created)
        self.assertFalse(preview.open_ended_loop_created)
        self.assertFalse(preview.action_selected)
        self.assertFalse(preview.action_execution_created)
        self.assertFalse(preview.free_action_selection_created)
        self.assertFalse(preview.automatic_learning_approval_created)
        self.assertFalse(preview.core_memory_write_performed)
        self.assertFalse(preview.long_term_memory_write_performed)
        self.assertFalse(preview.archive_memory_write_performed)
        self.assertFalse(preview.anchor_write_performed)
        self.assertFalse(handoff.task_resumed)
        self.assertFalse(handoff.task_runner_started)
        self.assertFalse(handoff.new_task_created)
        self.assertFalse(handoff.new_tick_created)
        self.assertFalse(handoff.scheduler_created)
        self.assertFalse(handoff.action_selected)
        self.assertFalse(handoff.action_execution_created)
        self.assertTrue(safety.no_core_longterm_archive_anchor_write)

    def test_write_load_and_clear_bundle_use_only_three_known_files(self) -> None:
        preview, handoff, safety = self._valid_handoff_bundle()
        with tempfile.TemporaryDirectory() as temp_dir:
            write = write_restore_resume_handoff_bundle(
                temp_dir,
                preview,
                handoff,
                safety,
            )
            loaded = load_restore_resume_handoff_bundle(temp_dir)
            extra = Path(temp_dir) / "keep_me.json"
            extra.write_text("{}", encoding="utf-8")
            cleared = clear_restore_resume_handoff(temp_dir)
            self.assertTrue(extra.exists())
            self.assertEqual(set(write["files_written"]), set(KNOWN_RESTORE_HANDOFF_FILES))
            self.assertEqual(loaded[0].restore_preview_id, preview.restore_preview_id)
            self.assertEqual(loaded[1].resume_handoff_id, handoff.resume_handoff_id)
            self.assertEqual(set(cleared["removed_files"]), set(KNOWN_RESTORE_HANDOFF_FILES))
            for file_name in KNOWN_RESTORE_HANDOFF_FILES:
                self.assertFalse((Path(temp_dir) / file_name).exists())

    def test_cli_build_show_create_validate_and_clear_work(self) -> None:
        with tempfile.TemporaryDirectory() as state_dir:
            self._prepare_state_dir(state_dir)
            build = self._run_state_cli("build-restore-preview", state_dir)
            self.assertEqual(build.returncode, 0, build.stderr)
            show_preview = self._run_state_cli("show-restore-preview", state_dir)
            self.assertEqual(show_preview.returncode, 0, show_preview.stderr)
            create = self._run_state_cli(
                "create-resume-handoff",
                state_dir,
                "--teacher-confirmation-text",
                self._teacher_confirmation_text(),
            )
            self.assertEqual(create.returncode, 0, create.stderr)
            show_handoff = self._run_state_cli("show-resume-handoff", state_dir)
            self.assertEqual(show_handoff.returncode, 0, show_handoff.stderr)
            validate = self._run_state_cli("validate-resume-handoff", state_dir)
            self.assertEqual(validate.returncode, 0, validate.stderr)
            clear = self._run_state_cli("clear-resume-handoff", state_dir)
            self.assertEqual(clear.returncode, 0, clear.stderr)

    def test_guided_console_restore_preview_and_resume_handoff_work(self) -> None:
        with tempfile.TemporaryDirectory() as state_dir:
            build_state_handoff_from_guided_cradle_growth_console(state_dir=state_dir)
            run_state_resume_precheck_from_guided_cradle_growth_console(state_dir=state_dir)
            _precheck, options, _safety = load_cradle_resume_precheck_bundle(state_dir)
            option_id = self._preferred_option(options).resume_option_id
            select_authorize_state_resume_from_guided_cradle_growth_console(
                state_dir=state_dir,
                resume_option_id=option_id,
                teacher_selection_text=self._teacher_selection_text(),
            )
            preview = build_state_restore_preview_from_guided_cradle_growth_console(
                state_dir=state_dir
            )
            shown_preview = show_state_restore_preview_from_guided_cradle_growth_console(
                state_dir=state_dir
            )
            handoff = create_state_resume_handoff_from_guided_cradle_growth_console(
                state_dir=state_dir,
                teacher_confirmation_text=self._teacher_confirmation_text(),
            )
            shown_handoff = show_state_resume_handoff_from_guided_cradle_growth_console(
                state_dir=state_dir
            )
            validation = validate_state_resume_handoff_from_guided_cradle_growth_console(
                state_dir=state_dir
            )
            status = get_guided_cradle_growth_status(state_dir=state_dir)
        self.assertEqual(
            preview["restore_preview"]["restore_preview"]["preview_status"],
            "preview_ready",
        )
        self.assertEqual(shown_preview["preview_status"], "preview_ready")
        self.assertEqual(
            handoff["resume_handoff"]["resume_handoff"]["handoff_status"],
            "handoff_ready",
        )
        self.assertEqual(shown_handoff["handoff_status"], "handoff_ready")
        self.assertTrue(validation["valid"])
        self.assertTrue(status["restore_preview_available"])
        self.assertTrue(status["resume_handoff_available"])
        self.assertTrue(status["allowed_next_manual_command"])

    def test_guided_console_cli_restore_and_handoff_commands_work(self) -> None:
        with tempfile.TemporaryDirectory() as state_dir:
            self.assertEqual(
                self._run_guided_cli("state-handoff-build", state_dir).returncode,
                0,
            )
            self.assertEqual(
                self._run_guided_cli("state-resume-precheck", state_dir).returncode,
                0,
            )
            _precheck, options, _safety = load_cradle_resume_precheck_bundle(state_dir)
            option_id = self._preferred_option(options).resume_option_id
            self.assertEqual(
                self._run_guided_cli(
                    "state-resume-select-authorize",
                    state_dir,
                    "--resume-option-id",
                    option_id,
                    "--teacher-selection-text",
                    self._teacher_selection_text(),
                ).returncode,
                0,
            )
            self.assertEqual(
                self._run_guided_cli("state-restore-preview", state_dir).returncode,
                0,
            )
            self.assertEqual(
                self._run_guided_cli("state-restore-show-preview", state_dir).returncode,
                0,
            )
            self.assertEqual(
                self._run_guided_cli(
                    "state-resume-create-handoff",
                    state_dir,
                    "--teacher-confirmation-text",
                    self._teacher_confirmation_text(),
                ).returncode,
                0,
            )
            self.assertEqual(
                self._run_guided_cli("state-resume-show-handoff", state_dir).returncode,
                0,
            )
            self.assertEqual(
                self._run_guided_cli("state-resume-validate-handoff", state_dir).returncode,
                0,
            )

    def test_run_functions_write_expected_state_without_runtime_authority(self) -> None:
        with tempfile.TemporaryDirectory() as state_dir:
            self._prepare_state_dir(state_dir)
            preview = run_cradle_restore_preview(state_dir)
            handoff = run_teacher_gated_resume_handoff(
                state_dir=state_dir,
                teacher_confirmation_text=self._teacher_confirmation_text(),
            )
            loaded_preview = load_cradle_restore_preview(state_dir)
        self.assertEqual(preview["restore_preview"]["preview_status"], "preview_ready")
        self.assertEqual(handoff["resume_handoff"]["handoff_status"], "handoff_ready")
        self.assertFalse(handoff["task_resumed"])
        self.assertFalse(handoff["task_runner_started"])
        self.assertFalse(handoff["new_tick_created"])
        self.assertFalse(loaded_preview.task_resumed)

    def test_known_restore_handoff_file_names_are_exact(self) -> None:
        self.assertEqual(
            set(KNOWN_RESTORE_HANDOFF_FILES),
            {RESTORE_PREVIEW_FILE, RESUME_HANDOFF_FILE, RESUME_HANDOFF_SAFETY_AUDIT_FILE},
        )

    def test_no_repo_data_pollution(self) -> None:
        with tempfile.TemporaryDirectory() as state_dir:
            self._prepare_state_dir(state_dir)
            run_cradle_restore_preview(state_dir)
            run_teacher_gated_resume_handoff(
                state_dir=state_dir,
                teacher_confirmation_text=self._teacher_confirmation_text(),
            )
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _valid_sources(
        self,
        resume_kind: str = "inspect_growth_readiness",
    ):
        bundle = build_cradle_state_handoff_bundle(
            source_ids={"last_growth_readiness_audit_id": "growth:ready"},
            source_trace_refs=("test:restore_preview_resume_handoff",),
        )
        selected = SelectedResumeBookmarkRecord(
            selected_resume_bookmark_id=f"selected:{resume_kind}",
            schema_version="state_engine_selected_resume_bookmark_v0",
            created_at="2026-06-29T00:00:00+00:00",
            source_engine="state_engine",
            source_handoff_id=bundle.handoff.handoff_id,
            source_precheck_id="precheck:test",
            source_resume_option_id=f"option:{resume_kind}",
            source_safety_audit_id="precheck_safety:test",
            selected_resume_kind=resume_kind,
            selected_target_kind="target_kind:test",
            selected_target_id=f"target:{resume_kind}",
            source_bookmark_id=f"bookmark:{resume_kind}",
            teacher_actor="user",
            teacher_role="project_owner",
            teacher_selection_text=self._teacher_selection_text(),
            teacher_selection_required=True,
            teacher_selection_present=True,
            selection_valid=True,
            selection_blocked_reason=None,
            precheck_only_source=True,
            resume_allowed_by_precheck=True,
            task_resumed=False,
            new_task_created=False,
            new_tick_created=False,
            scheduler_created=False,
            open_ended_loop_created=False,
            action_execution_created=False,
            free_action_selection_created=False,
            automatic_learning_approval_created=False,
            memory_write_performed=False,
            core_memory_write_performed=False,
            long_term_memory_write_performed=False,
            archive_memory_write_performed=False,
            anchor_write_performed=False,
            source_trace_refs=(bundle.handoff.handoff_id, f"option:{resume_kind}"),
        )
        auth_safety = ResumeAuthorizationSafetyAuditRecord(
            safety_audit_id="authorization_safety:test",
            schema_version="state_engine_resume_authorization_safety_audit_v0",
            created_at="2026-06-29T00:00:00+00:00",
            source_handoff_id=bundle.handoff.handoff_id,
            source_precheck_id="precheck:test",
            source_resume_option_id=f"option:{resume_kind}",
            source_selected_resume_bookmark_id=selected.selected_resume_bookmark_id,
            precheck_valid=True,
            resume_option_valid=True,
            teacher_selection_present=True,
            selected_option_matches_precheck=True,
            no_task_resume=True,
            no_new_task=True,
            no_new_tick=True,
            no_scheduler=True,
            no_open_ended_loop=True,
            no_action_execution=True,
            no_free_action_selection=True,
            no_automatic_learning_approval=True,
            no_core_longterm_archive_anchor_write=True,
            audit_status="passed",
            blocked_reasons=(),
        )
        authorization = TeacherResumeAuthorizationRecord(
            authorization_id=f"authorization:{resume_kind}",
            schema_version="state_engine_teacher_resume_authorization_v0",
            created_at="2026-06-29T00:00:00+00:00",
            source_engine="state_engine",
            source_handoff_id=bundle.handoff.handoff_id,
            source_precheck_id="precheck:test",
            source_resume_option_id=f"option:{resume_kind}",
            source_selected_resume_bookmark_id=selected.selected_resume_bookmark_id,
            authorized_resume_kind=resume_kind,
            authorized_target_kind=selected.selected_target_kind,
            authorized_target_id=selected.selected_target_id,
            authorization_scope="selected_resume_bookmark_only",
            authorization_status="authorized_for_future_restore",
            authorization_text="fixture authorization",
            authorized_by_actor="user",
            authorized_by_role="project_owner",
            authorized_for_future_restore_preview=True,
            authorized_for_future_teacher_gated_resume_execution=True,
            authorized_to_resume_now=False,
            authorized_to_create_tick_now=False,
            authorized_to_run_task_now=False,
            authorized_to_execute_action_now=False,
            authorized_to_write_memory_now=False,
            requires_future_restore_preview=True,
            requires_future_resume_execution_package=True,
            requires_teacher_confirmation_at_execution=True,
            safety_audit_id=auth_safety.safety_audit_id,
            source_trace_refs=selected.source_trace_refs,
        )
        return bundle, selected, authorization, auth_safety

    def _valid_handoff_bundle(self):
        bundle, selected, authorization, auth_safety = self._valid_sources()
        preview = build_cradle_restore_preview(
            handoff_bundle=bundle,
            selected=selected,
            authorization=authorization,
            authorization_safety_audit=auth_safety,
        )
        handoff = build_teacher_gated_resume_handoff(
            preview=preview,
            selected=selected,
            authorization=authorization,
            teacher_confirmation_text=self._teacher_confirmation_text(),
        )
        safety = build_resume_handoff_safety_audit(
            preview=preview,
            selected=selected,
            authorization=authorization,
            authorization_safety_audit=auth_safety,
            handoff=handoff,
        )
        return preview, handoff, safety

    def _assert_mapping(self, resume_kind: str, expected_target: str) -> None:
        bundle, selected, authorization, auth_safety = self._valid_sources(resume_kind)
        preview = build_cradle_restore_preview(
            handoff_bundle=bundle,
            selected=selected,
            authorization=authorization,
            authorization_safety_audit=auth_safety,
        )
        self.assertEqual(preview.preview_status, "preview_ready")
        self.assertEqual(preview.target_engine_entry_kind, expected_target)

    def _assert_authorization_flag_blocks_preview(self, flag_name: str) -> None:
        bundle, selected, authorization, auth_safety = self._valid_sources()
        bad_authorization = self._mutated_authorization(authorization, **{flag_name: True})
        preview = build_cradle_restore_preview(
            handoff_bundle=bundle,
            selected=selected,
            authorization=bad_authorization,
            authorization_safety_audit=auth_safety,
        )
        self.assertEqual(preview.preview_status, "blocked_invalid_authorization")

    def _prepare_state_dir(self, state_dir: str) -> str:
        write_cradle_state_handoff_bundle(build_cradle_state_handoff_bundle(), state_dir)
        run_cradle_resume_precheck(state_dir)
        _precheck, options, _safety = load_cradle_resume_precheck_bundle(state_dir)
        option_id = self._preferred_option(options).resume_option_id
        run_resume_selection_authorization(
            state_dir=state_dir,
            resume_option_id=option_id,
            teacher_selection_text=self._teacher_selection_text(),
        )
        return option_id

    def _preferred_option(
        self,
        options: tuple[CradleResumeOptionRecord, ...],
    ) -> CradleResumeOptionRecord:
        return next(
            (option for option in options if option.resume_kind != "inspect_status"),
            options[0],
        )

    def _mutated_authorization(
        self,
        authorization: TeacherResumeAuthorizationRecord,
        **changes: object,
    ) -> TeacherResumeAuthorizationRecord:
        data = authorization.to_dict()
        data.update(changes)
        return TeacherResumeAuthorizationRecord.from_dict(data)

    def _mutated_handoff(
        self,
        handoff: TeacherGatedResumeHandoffRecord,
        **changes: object,
    ) -> TeacherGatedResumeHandoffRecord:
        data = handoff.to_dict()
        data.update(changes)
        return TeacherGatedResumeHandoffRecord.from_dict(data)

    def _teacher_selection_text(self) -> str:
        return "select this resume option for future restore preview"

    def _teacher_confirmation_text(self) -> str:
        return "confirm this restore preview for a teacher-gated resume handoff"

    def _run_state_cli(
        self,
        command: str,
        state_dir: str,
        *extra_args: str,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core_v1.state.cradle_state_restore_preview_resume_handoff_cli",
                command,
                "--state-dir",
                state_dir,
                *extra_args,
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    def _run_guided_cli(
        self,
        command: str,
        state_dir: str,
        *extra_args: str,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core_v1.runtime.guided_cradle_growth_teacher_console_cli",
                "--state-dir",
                state_dir,
                command,
                *extra_args,
            ],
            check=False,
            capture_output=True,
            text=True,
        )


if __name__ == "__main__":
    unittest.main()
