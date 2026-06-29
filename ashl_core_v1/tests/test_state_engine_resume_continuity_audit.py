from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.runtime.guided_cradle_growth_teacher_console import (
    get_guided_cradle_growth_status,
    run_state_resume_continuity_audit_from_guided_cradle_growth_console,
    show_state_resume_continuity_audit_from_guided_cradle_growth_console,
    validate_state_resume_continuity_audit_from_guided_cradle_growth_console,
)
from ashl_core_v1.state.cradle_state_persistence_handoff import (
    HANDOFF_FILE,
    build_cradle_state_handoff_bundle,
    write_cradle_state_handoff_bundle,
)
from ashl_core_v1.state.cradle_state_resume_precheck import (
    PRECHECK_FILE,
    load_cradle_resume_precheck_bundle,
    run_cradle_resume_precheck,
)
from ashl_core_v1.state.cradle_state_resume_selection_authorization import (
    AUTHORIZATION_FILE,
    SELECTED_BOOKMARK_FILE,
    run_resume_selection_authorization,
)
from ashl_core_v1.state.cradle_state_restore_preview_resume_handoff import (
    RESUME_HANDOFF_FILE,
    RESTORE_PREVIEW_FILE,
    run_cradle_restore_preview,
    run_teacher_gated_resume_handoff,
)
from ashl_core_v1.state.state_engine_resume_continuity_audit import (
    AUDIT_FILE,
    BLOCKED_CLAIMS,
    build_state_engine_resume_continuity_audit,
    clear_state_engine_resume_continuity_audit,
    load_state_engine_resume_continuity_audit,
    run_state_engine_resume_continuity_audit,
    validate_state_engine_resume_continuity_audit,
)


class StateEngineResumeContinuityAuditTests(unittest.TestCase):
    def test_valid_full_resume_chain_audit_passes(self) -> None:
        with tempfile.TemporaryDirectory() as state_dir:
            self._prepare_full_chain(state_dir)
            audit = build_state_engine_resume_continuity_audit(state_dir)
            validation = validate_state_engine_resume_continuity_audit(audit)
        self.assertEqual(
            audit.audit_status,
            "passed_state_engine_continuity_v0_closed",
        )
        self.assertTrue(audit.state_engine_continuity_v0_closed)
        self.assertTrue(validation["valid"])

    def test_missing_handoff_blocks(self) -> None:
        self._assert_missing_file_blocks(HANDOFF_FILE, "blocked_missing_handoff")

    def test_missing_precheck_blocks(self) -> None:
        self._assert_missing_file_blocks(PRECHECK_FILE, "blocked_missing_precheck")

    def test_missing_selection_blocks(self) -> None:
        self._assert_missing_file_blocks(SELECTED_BOOKMARK_FILE, "blocked_missing_selection")

    def test_missing_authorization_blocks(self) -> None:
        self._assert_missing_file_blocks(AUTHORIZATION_FILE, "blocked_missing_authorization")

    def test_missing_restore_preview_blocks(self) -> None:
        self._assert_missing_file_blocks(RESTORE_PREVIEW_FILE, "blocked_missing_restore_preview")

    def test_missing_resume_handoff_blocks(self) -> None:
        self._assert_missing_file_blocks(RESUME_HANDOFF_FILE, "blocked_missing_resume_handoff")

    def test_broken_handoff_id_lineage_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as state_dir:
            self._prepare_full_chain(state_dir)
            self._mutate_json(state_dir, PRECHECK_FILE, {"source_handoff_id": "wrong"})
            audit = build_state_engine_resume_continuity_audit(state_dir)
        self.assertEqual(audit.audit_status, "blocked_broken_lineage")
        self.assertFalse(audit.handoff_to_precheck_linked)

    def test_broken_selection_to_authorization_lineage_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as state_dir:
            self._prepare_full_chain(state_dir)
            self._mutate_json(
                state_dir,
                AUTHORIZATION_FILE,
                {"source_selected_resume_bookmark_id": "wrong"},
            )
            audit = build_state_engine_resume_continuity_audit(state_dir)
        self.assertEqual(audit.audit_status, "blocked_broken_lineage")
        self.assertFalse(audit.selection_to_authorization_linked)

    def test_broken_authorization_to_preview_lineage_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as state_dir:
            self._prepare_full_chain(state_dir)
            self._mutate_json(
                state_dir,
                RESTORE_PREVIEW_FILE,
                {"source_authorization_id": "wrong"},
            )
            audit = build_state_engine_resume_continuity_audit(state_dir)
        self.assertEqual(audit.audit_status, "blocked_broken_lineage")
        self.assertFalse(audit.authorization_to_restore_preview_linked)

    def test_broken_preview_to_handoff_lineage_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as state_dir:
            self._prepare_full_chain(state_dir)
            self._mutate_json(
                state_dir,
                RESUME_HANDOFF_FILE,
                {"source_restore_preview_id": "wrong"},
            )
            audit = build_state_engine_resume_continuity_audit(state_dir)
        self.assertEqual(audit.audit_status, "blocked_broken_lineage")
        self.assertFalse(audit.restore_preview_to_resume_handoff_linked)

    def test_missing_teacher_selection_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as state_dir:
            self._prepare_full_chain(state_dir)
            self._mutate_json(
                state_dir,
                SELECTED_BOOKMARK_FILE,
                {"teacher_selection_present": False},
            )
            audit = build_state_engine_resume_continuity_audit(state_dir)
        self.assertEqual(audit.audit_status, "blocked_missing_teacher_gate")
        self.assertFalse(audit.teacher_selection_present)

    def test_missing_teacher_confirmation_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as state_dir:
            self._prepare_full_chain(state_dir)
            self._mutate_json(
                state_dir,
                RESUME_HANDOFF_FILE,
                {"teacher_confirmation_present": False},
            )
            audit = build_state_engine_resume_continuity_audit(state_dir)
        self.assertEqual(audit.audit_status, "blocked_missing_teacher_gate")
        self.assertFalse(audit.teacher_confirmation_present)

    def test_automatic_resume_flag_blocks(self) -> None:
        self._assert_authority_flag_blocks(PRECHECK_FILE, "automatic_resume_created")

    def test_task_runner_started_flag_blocks(self) -> None:
        self._assert_authority_flag_blocks(RESUME_HANDOFF_FILE, "task_runner_started")

    def test_task_resumed_flag_blocks(self) -> None:
        self._assert_authority_flag_blocks(RESUME_HANDOFF_FILE, "task_resumed")

    def test_new_tick_flag_blocks(self) -> None:
        self._assert_authority_flag_blocks(RESUME_HANDOFF_FILE, "new_tick_created")

    def test_scheduler_flag_blocks(self) -> None:
        self._assert_authority_flag_blocks(RESUME_HANDOFF_FILE, "scheduler_created")

    def test_action_execution_flag_blocks(self) -> None:
        self._assert_authority_flag_blocks(RESUME_HANDOFF_FILE, "action_execution_created")

    def test_memory_layer_write_flags_block(self) -> None:
        for flag_name in (
            "core_memory_write_performed",
            "long_term_memory_write_performed",
            "archive_memory_write_performed",
            "anchor_write_performed",
        ):
            with self.subTest(flag=flag_name):
                self._assert_authority_flag_blocks(RESUME_HANDOFF_FILE, flag_name)

    def test_safe_claim_and_blocked_claims_present_on_passed_audit(self) -> None:
        with tempfile.TemporaryDirectory() as state_dir:
            self._prepare_full_chain(state_dir)
            audit = build_state_engine_resume_continuity_audit(state_dir)
        self.assertIn("State Engine continuity v0", audit.safe_claim)
        self.assertEqual(audit.blocked_claims, BLOCKED_CLAIMS)

    def test_cli_run_show_validate_and_clear_work(self) -> None:
        with tempfile.TemporaryDirectory() as state_dir:
            self._prepare_full_chain(state_dir)
            run = self._run_state_cli("run-audit", state_dir)
            self.assertEqual(run.returncode, 0, run.stderr)
            show = self._run_state_cli("show-audit", state_dir)
            self.assertEqual(show.returncode, 0, show.stderr)
            validate = self._run_state_cli("validate-audit", state_dir)
            self.assertEqual(validate.returncode, 0, validate.stderr)
            extra = Path(state_dir) / "keep_me.json"
            extra.write_text("{}", encoding="utf-8")
            clear = self._run_state_cli("clear-audit", state_dir)
            self.assertEqual(clear.returncode, 0, clear.stderr)
            self.assertTrue(extra.exists())
            self.assertFalse((Path(state_dir) / AUDIT_FILE).exists())

    def test_write_load_clear_audit_file_only(self) -> None:
        with tempfile.TemporaryDirectory() as state_dir:
            self._prepare_full_chain(state_dir)
            result = run_state_engine_resume_continuity_audit(state_dir)
            loaded = load_state_engine_resume_continuity_audit(state_dir)
            extra = Path(state_dir) / "keep_me.json"
            extra.write_text("{}", encoding="utf-8")
            cleared = clear_state_engine_resume_continuity_audit(state_dir)
        self.assertEqual(result["files_written"], [AUDIT_FILE])
        self.assertEqual(loaded.audit_status, "passed_state_engine_continuity_v0_closed")
        self.assertEqual(cleared["removed_files"], [AUDIT_FILE])

    def test_guided_console_state_resume_continuity_audit_works(self) -> None:
        with tempfile.TemporaryDirectory() as state_dir:
            self._prepare_full_chain(state_dir)
            result = run_state_resume_continuity_audit_from_guided_cradle_growth_console(
                state_dir=state_dir
            )
            shown = show_state_resume_continuity_audit_from_guided_cradle_growth_console(
                state_dir=state_dir
            )
            validation = validate_state_resume_continuity_audit_from_guided_cradle_growth_console(
                state_dir=state_dir
            )
            status = get_guided_cradle_growth_status(state_dir=state_dir)
        self.assertTrue(result["state_resume_continuity_audit"]["validation"]["valid"])
        self.assertEqual(shown["audit_status"], "passed_state_engine_continuity_v0_closed")
        self.assertTrue(validation["valid"])
        self.assertTrue(status["state_engine_continuity_audit_available"])
        self.assertTrue(status["state_engine_continuity_v0_closed"])
        self.assertEqual(status["recommended_next_engine_line"], "learning_engine")

    def test_guided_console_cli_state_resume_continuity_commands_work(self) -> None:
        with tempfile.TemporaryDirectory() as state_dir:
            self._prepare_full_chain(state_dir)
            run = self._run_guided_cli("state-resume-continuity-audit", state_dir)
            self.assertEqual(run.returncode, 0, run.stderr)
            show = self._run_guided_cli("state-resume-continuity-show", state_dir)
            self.assertEqual(show.returncode, 0, show.stderr)
            validate = self._run_guided_cli("state-resume-continuity-validate", state_dir)
            self.assertEqual(validate.returncode, 0, validate.stderr)

    def test_no_repo_data_created(self) -> None:
        with tempfile.TemporaryDirectory() as state_dir:
            self._prepare_full_chain(state_dir)
            run_state_engine_resume_continuity_audit(state_dir)
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _prepare_full_chain(self, state_dir: str) -> None:
        write_cradle_state_handoff_bundle(build_cradle_state_handoff_bundle(), state_dir)
        run_cradle_resume_precheck(state_dir)
        _precheck, options, _safety = load_cradle_resume_precheck_bundle(state_dir)
        option = next(
            (item for item in options if item.resume_kind != "inspect_status"),
            options[0],
        )
        run_resume_selection_authorization(
            state_dir=state_dir,
            resume_option_id=option.resume_option_id,
            teacher_selection_text="select resume option for restore preview",
        )
        run_cradle_restore_preview(state_dir)
        run_teacher_gated_resume_handoff(
            state_dir=state_dir,
            teacher_confirmation_text="confirm teacher-gated resume handoff",
        )

    def _assert_missing_file_blocks(self, file_name: str, expected_status: str) -> None:
        with tempfile.TemporaryDirectory() as state_dir:
            self._prepare_full_chain(state_dir)
            (Path(state_dir) / file_name).unlink()
            audit = build_state_engine_resume_continuity_audit(state_dir)
        self.assertEqual(audit.audit_status, expected_status)
        self.assertFalse(audit.state_engine_continuity_v0_closed)

    def _assert_authority_flag_blocks(self, file_name: str, flag_name: str) -> None:
        with tempfile.TemporaryDirectory() as state_dir:
            self._prepare_full_chain(state_dir)
            self._mutate_json(state_dir, file_name, {flag_name: True})
            audit = build_state_engine_resume_continuity_audit(state_dir)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_runtime_authority_detected",
        )
        self.assertFalse(audit.state_engine_continuity_v0_closed)

    def _mutate_json(self, state_dir: str, file_name: str, changes: dict[str, object]) -> None:
        path = Path(state_dir) / file_name
        data = json.loads(path.read_text(encoding="utf-8"))
        data.update(changes)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def _run_state_cli(self, command: str, state_dir: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core_v1.state.state_engine_resume_continuity_audit_cli",
                command,
                "--state-dir",
                state_dir,
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    def _run_guided_cli(
        self,
        command: str,
        state_dir: str,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core_v1.runtime.guided_cradle_growth_teacher_console_cli",
                "--state-dir",
                state_dir,
                command,
            ],
            check=False,
            capture_output=True,
            text=True,
        )


if __name__ == "__main__":
    unittest.main()
