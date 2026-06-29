from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.runtime.guided_cradle_growth_teacher_console import (
    build_state_handoff_from_guided_cradle_growth_console,
    get_guided_cradle_growth_status,
    run_state_resume_precheck_from_guided_cradle_growth_console,
    select_authorize_state_resume_from_guided_cradle_growth_console,
    show_state_resume_authorization_from_guided_cradle_growth_console,
    show_state_resume_selection_from_guided_cradle_growth_console,
    validate_state_resume_authorization_from_guided_cradle_growth_console,
)
from ashl_core_v1.state.cradle_state_persistence_handoff import (
    build_cradle_state_handoff_bundle,
    write_cradle_state_handoff_bundle,
)
from ashl_core_v1.state.cradle_state_resume_precheck import (
    CradleResumeOptionRecord,
    build_cradle_resume_precheck,
    load_cradle_resume_precheck_bundle,
    run_cradle_resume_precheck,
)
from ashl_core_v1.state.cradle_state_resume_selection_authorization import (
    AUTHORIZATION_FILE,
    AUTHORIZATION_SAFETY_AUDIT_FILE,
    KNOWN_AUTHORIZATION_FILES,
    SELECTED_BOOKMARK_FILE,
    build_resume_authorization_safety_audit,
    build_resume_selection_authorization_bundle,
    build_selected_resume_bookmark,
    clear_resume_selection_authorization,
    find_resume_option,
    load_resume_precheck_bundle,
    load_resume_selection_authorization_bundle,
    run_resume_selection_authorization,
    validate_selected_resume_bookmark,
    validate_teacher_resume_authorization,
    write_resume_selection_authorization_bundle,
)


class CradleStateResumeSelectionAuthorizationTests(unittest.TestCase):
    def test_select_valid_resume_option_creates_selected_bookmark(self) -> None:
        precheck, options, safety = self._valid_precheck_bundle()
        option = self._preferred_option(options)
        selected, _authorization, _auth_safety = build_resume_selection_authorization_bundle(
            precheck=precheck,
            options=options,
            precheck_safety_audit=safety,
            resume_option_id=option.resume_option_id,
            teacher_selection_text=self._teacher_text(),
        )
        validation = validate_selected_resume_bookmark(selected)
        self.assertTrue(validation["valid"])
        self.assertTrue(selected.selection_valid)
        self.assertEqual(selected.source_resume_option_id, option.resume_option_id)

    def test_select_valid_resume_option_creates_teacher_authorization(self) -> None:
        selected, authorization, auth_safety = self._valid_authorization_bundle()
        validation = validate_teacher_resume_authorization(
            selected,
            authorization,
            auth_safety,
        )
        self.assertTrue(validation["valid"])
        self.assertEqual(authorization.authorization_status, "authorized_for_future_restore")
        self.assertTrue(authorization.authorized_for_future_restore_preview)
        self.assertTrue(authorization.authorized_for_future_teacher_gated_resume_execution)

    def test_selected_bookmark_preserves_source_ids(self) -> None:
        precheck, options, safety = self._valid_precheck_bundle()
        option = self._preferred_option(options)
        selected, _authorization, _auth_safety = build_resume_selection_authorization_bundle(
            precheck=precheck,
            options=options,
            precheck_safety_audit=safety,
            resume_option_id=option.resume_option_id,
            teacher_selection_text=self._teacher_text(),
        )
        self.assertEqual(selected.source_handoff_id, precheck.source_handoff_id)
        self.assertEqual(selected.source_precheck_id, precheck.precheck_id)
        self.assertEqual(selected.source_resume_option_id, option.resume_option_id)
        self.assertEqual(selected.source_safety_audit_id, safety.safety_audit_id)

    def test_authorization_preserves_selected_resume_bookmark_id(self) -> None:
        selected, authorization, _auth_safety = self._valid_authorization_bundle()
        self.assertEqual(
            authorization.source_selected_resume_bookmark_id,
            selected.selected_resume_bookmark_id,
        )

    def test_teacher_selection_text_is_required(self) -> None:
        precheck, options, safety = self._valid_precheck_bundle()
        option = self._preferred_option(options)
        selected, authorization, auth_safety = build_resume_selection_authorization_bundle(
            precheck=precheck,
            options=options,
            precheck_safety_audit=safety,
            resume_option_id=option.resume_option_id,
            teacher_selection_text="   ",
        )
        self.assertFalse(selected.teacher_selection_present)
        self.assertFalse(selected.selection_valid)
        self.assertEqual(auth_safety.audit_status, "blocked_missing_teacher_selection")
        self.assertEqual(
            authorization.authorization_status,
            "blocked_missing_teacher_selection",
        )

    def test_invalid_resume_option_id_blocks(self) -> None:
        precheck, options, safety = self._valid_precheck_bundle()
        selected, authorization, auth_safety = build_resume_selection_authorization_bundle(
            precheck=precheck,
            options=options,
            precheck_safety_audit=safety,
            resume_option_id="missing-option",
            teacher_selection_text=self._teacher_text(),
        )
        self.assertFalse(selected.selection_valid)
        self.assertEqual(selected.selection_blocked_reason, "blocked_invalid_option")
        self.assertEqual(auth_safety.audit_status, "blocked_invalid_option")
        self.assertEqual(authorization.authorization_status, "blocked_invalid_option")

    def test_missing_precheck_bundle_blocks_loading(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(FileNotFoundError):
                load_resume_precheck_bundle(temp_dir)

    def test_failed_precheck_blocks_authorization(self) -> None:
        precheck, options, safety = build_cradle_resume_precheck({})
        option = options[0]
        selected, authorization, auth_safety = build_resume_selection_authorization_bundle(
            precheck=precheck,
            options=options,
            precheck_safety_audit=safety,
            resume_option_id=option.resume_option_id,
            teacher_selection_text=self._teacher_text(),
        )
        self.assertFalse(precheck.resume_allowed)
        self.assertFalse(selected.selection_valid)
        self.assertEqual(auth_safety.audit_status, "blocked_invalid_precheck")
        self.assertEqual(authorization.authorization_status, "blocked_invalid_precheck")

    def test_selected_option_not_in_precheck_blocks(self) -> None:
        precheck, options, safety = self._valid_precheck_bundle()
        fake_option = self._mutated_option(options[0], resume_option_id="option:not-in-precheck")
        selected = build_selected_resume_bookmark(
            precheck=precheck,
            option=fake_option,
            precheck_safety_audit=safety,
            teacher_selection_text=self._teacher_text(),
        )
        auth_safety = build_resume_authorization_safety_audit(
            precheck=precheck,
            options=options,
            option=fake_option,
            selected=selected,
            precheck_safety_audit=safety,
        )
        self.assertEqual(
            auth_safety.audit_status,
            "blocked_selected_option_not_in_precheck",
        )

    def test_option_allowed_to_resume_task_now_true_blocks(self) -> None:
        self._assert_forbidden_option_flag_blocks("allowed_to_resume_task_now")

    def test_option_allowed_to_create_tick_now_true_blocks(self) -> None:
        self._assert_forbidden_option_flag_blocks("allowed_to_create_tick_now")

    def test_option_allowed_to_execute_now_true_blocks(self) -> None:
        self._assert_forbidden_option_flag_blocks("allowed_to_execute_now")

    def test_option_allowed_to_write_memory_now_true_blocks(self) -> None:
        self._assert_forbidden_option_flag_blocks("allowed_to_write_memory_now")

    def test_authorization_is_future_scoped(self) -> None:
        _selected, authorization, _auth_safety = self._valid_authorization_bundle()
        self.assertFalse(authorization.authorized_to_resume_now)
        self.assertFalse(authorization.authorized_to_create_tick_now)
        self.assertFalse(authorization.authorized_to_run_task_now)
        self.assertFalse(authorization.authorized_to_execute_action_now)
        self.assertFalse(authorization.authorized_to_write_memory_now)
        self.assertTrue(authorization.requires_future_restore_preview)
        self.assertTrue(authorization.requires_future_resume_execution_package)
        self.assertTrue(authorization.requires_teacher_confirmation_at_execution)

    def test_write_load_and_clear_bundle_use_only_three_known_files(self) -> None:
        selected, authorization, auth_safety = self._valid_authorization_bundle()
        with tempfile.TemporaryDirectory() as temp_dir:
            write = write_resume_selection_authorization_bundle(
                temp_dir,
                selected,
                authorization,
                auth_safety,
            )
            loaded = load_resume_selection_authorization_bundle(temp_dir)
            extra = Path(temp_dir) / "keep_me.json"
            extra.write_text("{}", encoding="utf-8")
            cleared = clear_resume_selection_authorization(temp_dir)
            self.assertTrue(extra.exists())
            self.assertEqual(set(write["files_written"]), set(KNOWN_AUTHORIZATION_FILES))
            self.assertEqual(loaded[0].selected_resume_bookmark_id, selected.selected_resume_bookmark_id)
            self.assertEqual(loaded[1].authorization_id, authorization.authorization_id)
            self.assertEqual(set(cleared["removed_files"]), set(KNOWN_AUTHORIZATION_FILES))
            for file_name in KNOWN_AUTHORIZATION_FILES:
                self.assertFalse((Path(temp_dir) / file_name).exists())

    def test_cli_select_show_validate_and_clear_work(self) -> None:
        with tempfile.TemporaryDirectory() as state_dir:
            option_id = self._prepare_state_dir_and_option_id(state_dir)
            select = self._run_state_cli(
                "select-and-authorize",
                state_dir,
                "--resume-option-id",
                option_id,
                "--teacher-selection-text",
                self._teacher_text(),
            )
            self.assertEqual(select.returncode, 0, select.stderr)
            show_selection = self._run_state_cli("show-selection", state_dir)
            self.assertEqual(show_selection.returncode, 0, show_selection.stderr)
            show_authorization = self._run_state_cli("show-authorization", state_dir)
            self.assertEqual(show_authorization.returncode, 0, show_authorization.stderr)
            validate = self._run_state_cli("validate-authorization", state_dir)
            self.assertEqual(validate.returncode, 0, validate.stderr)
            clear = self._run_state_cli("clear-authorization", state_dir)
            self.assertEqual(clear.returncode, 0, clear.stderr)

    def test_guided_console_select_authorize_and_show_authorization_work(self) -> None:
        with tempfile.TemporaryDirectory() as state_dir:
            build_state_handoff_from_guided_cradle_growth_console(state_dir=state_dir)
            run_state_resume_precheck_from_guided_cradle_growth_console(state_dir=state_dir)
            _precheck, options, _safety = load_cradle_resume_precheck_bundle(state_dir)
            option_id = self._preferred_option(options).resume_option_id
            selected = select_authorize_state_resume_from_guided_cradle_growth_console(
                state_dir=state_dir,
                resume_option_id=option_id,
                teacher_selection_text=self._teacher_text(),
            )
            shown_selection = show_state_resume_selection_from_guided_cradle_growth_console(
                state_dir=state_dir
            )
            shown_authorization = show_state_resume_authorization_from_guided_cradle_growth_console(
                state_dir=state_dir
            )
            validation = validate_state_resume_authorization_from_guided_cradle_growth_console(
                state_dir=state_dir
            )
            status = get_guided_cradle_growth_status(state_dir=state_dir)
        self.assertEqual(
            selected["resume_authorization"]["teacher_resume_authorization"][
                "authorization_status"
            ],
            "authorized_for_future_restore",
        )
        self.assertEqual(
            shown_selection["source_resume_option_id"],
            option_id,
        )
        self.assertEqual(
            shown_authorization["authorization_status"],
            "authorized_for_future_restore",
        )
        self.assertTrue(validation["valid"])
        self.assertTrue(status["resume_selection_available"])
        self.assertTrue(status["resume_authorization_available"])
        self.assertTrue(status["authorized_for_future_restore_preview"])

    def test_guided_console_cli_select_authorize_commands_work(self) -> None:
        with tempfile.TemporaryDirectory() as state_dir:
            handoff = self._run_guided_cli("state-handoff-build", state_dir)
            self.assertEqual(handoff.returncode, 0, handoff.stderr)
            precheck = self._run_guided_cli("state-resume-precheck", state_dir)
            self.assertEqual(precheck.returncode, 0, precheck.stderr)
            _precheck, options, _safety = load_cradle_resume_precheck_bundle(state_dir)
            option_id = self._preferred_option(options).resume_option_id
            select = self._run_guided_cli(
                "state-resume-select-authorize",
                state_dir,
                "--resume-option-id",
                option_id,
                "--teacher-selection-text",
                self._teacher_text(),
            )
            self.assertEqual(select.returncode, 0, select.stderr)
            show_selection = self._run_guided_cli("state-resume-show-selection", state_dir)
            self.assertEqual(show_selection.returncode, 0, show_selection.stderr)
            show_authorization = self._run_guided_cli(
                "state-resume-show-authorization",
                state_dir,
            )
            self.assertEqual(show_authorization.returncode, 0, show_authorization.stderr)
            validate = self._run_guided_cli(
                "state-resume-validate-authorization",
                state_dir,
            )
            self.assertEqual(validate.returncode, 0, validate.stderr)

    def test_run_resume_selection_authorization_writes_future_scoped_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as state_dir:
            option_id = self._prepare_state_dir_and_option_id(state_dir)
            result = run_resume_selection_authorization(
                state_dir=state_dir,
                resume_option_id=option_id,
                teacher_selection_text=self._teacher_text(),
            )
            self.assertTrue(result["validation"]["valid"])
            self.assertFalse(result["automatic_resume"])
            self.assertFalse(result["task_resumed"])
            self.assertFalse(result["new_tick_created"])

    def test_find_resume_option_returns_expected_option(self) -> None:
        precheck, options, safety = self._valid_precheck_bundle()
        option = self._preferred_option(options)
        found = find_resume_option((precheck, options, safety), option.resume_option_id)
        missing = find_resume_option((precheck, options, safety), "missing")
        self.assertEqual(found, option)
        self.assertIsNone(missing)

    def test_known_authorization_file_names_are_exact(self) -> None:
        self.assertEqual(
            set(KNOWN_AUTHORIZATION_FILES),
            {SELECTED_BOOKMARK_FILE, AUTHORIZATION_FILE, AUTHORIZATION_SAFETY_AUDIT_FILE},
        )

    def test_no_repo_data_pollution_or_forbidden_runtime_authority(self) -> None:
        selected, authorization, auth_safety = self._valid_authorization_bundle()
        self.assertFalse(selected.task_resumed)
        self.assertFalse(selected.new_task_created)
        self.assertFalse(selected.new_tick_created)
        self.assertFalse(selected.scheduler_created)
        self.assertFalse(selected.open_ended_loop_created)
        self.assertFalse(selected.action_execution_created)
        self.assertFalse(selected.free_action_selection_created)
        self.assertFalse(selected.automatic_learning_approval_created)
        self.assertFalse(selected.core_memory_write_performed)
        self.assertFalse(selected.long_term_memory_write_performed)
        self.assertFalse(selected.archive_memory_write_performed)
        self.assertFalse(selected.anchor_write_performed)
        self.assertFalse(authorization.authorized_to_resume_now)
        self.assertFalse(authorization.authorized_to_create_tick_now)
        self.assertFalse(authorization.authorized_to_execute_action_now)
        self.assertTrue(auth_safety.no_core_longterm_archive_anchor_write)
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _valid_precheck_bundle(self):
        bundle = build_cradle_state_handoff_bundle(
            counts={
                "pending_candidate_count": 0,
                "reviewed_learning_count": 1,
                "memory_application_data_count": 1,
                "readback_preview_count": 1,
                "readback_application_count": 1,
                "contrast_count": 1,
                "loop_evidence_count": 1,
            },
            source_ids={"last_growth_readiness_audit_id": "growth:ready"},
            last_task_status="closed",
            source_trace_refs=("test:state_resume_authorization",),
        )
        return build_cradle_resume_precheck(bundle)

    def _valid_authorization_bundle(self):
        precheck, options, safety = self._valid_precheck_bundle()
        option = self._preferred_option(options)
        return build_resume_selection_authorization_bundle(
            precheck=precheck,
            options=options,
            precheck_safety_audit=safety,
            resume_option_id=option.resume_option_id,
            teacher_selection_text=self._teacher_text(),
        )

    def _prepare_state_dir_and_option_id(self, state_dir: str) -> str:
        write_cradle_state_handoff_bundle(build_cradle_state_handoff_bundle(), state_dir)
        run_cradle_resume_precheck(state_dir)
        _precheck, options, _safety = load_cradle_resume_precheck_bundle(state_dir)
        return self._preferred_option(options).resume_option_id

    def _preferred_option(
        self,
        options: tuple[CradleResumeOptionRecord, ...],
    ) -> CradleResumeOptionRecord:
        return next(
            (option for option in options if option.resume_kind != "inspect_status"),
            options[0],
        )

    def _mutated_option(
        self,
        option: CradleResumeOptionRecord,
        **changes: object,
    ) -> CradleResumeOptionRecord:
        data = option.to_dict()
        data.update(changes)
        return CradleResumeOptionRecord.from_dict(data)

    def _assert_forbidden_option_flag_blocks(self, flag_name: str) -> None:
        precheck, options, safety = self._valid_precheck_bundle()
        option = self._mutated_option(self._preferred_option(options), **{flag_name: True})
        selected = build_selected_resume_bookmark(
            precheck=precheck,
            option=option,
            precheck_safety_audit=safety,
            teacher_selection_text=self._teacher_text(),
        )
        auth_safety = build_resume_authorization_safety_audit(
            precheck=precheck,
            options=options,
            option=option,
            selected=selected,
            precheck_safety_audit=safety,
        )
        self.assertEqual(auth_safety.audit_status, "blocked_invalid_option")

    def _teacher_text(self) -> str:
        return "select this resume option for future restore preview"

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
                "ashl_core_v1.state.cradle_state_resume_selection_authorization_cli",
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
