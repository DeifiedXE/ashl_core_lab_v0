from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.runtime.guided_cradle_growth_teacher_console import (
    build_state_handoff_from_guided_cradle_growth_console,
    get_guided_cradle_growth_status,
    list_state_resume_options_from_guided_cradle_growth_console,
    run_state_resume_precheck_from_guided_cradle_growth_console,
    show_state_resume_precheck_from_guided_cradle_growth_console,
    validate_state_resume_precheck_from_guided_cradle_growth_console,
)
from ashl_core_v1.state.cradle_state_persistence_handoff import (
    build_cradle_state_handoff_bundle,
    write_cradle_state_handoff_bundle,
)
from ashl_core_v1.state.cradle_state_resume_precheck import (
    KNOWN_PRECHECK_FILES,
    OPTIONS_FILE,
    PRECHECK_FILE,
    SAFETY_AUDIT_FILE,
    build_cradle_resume_precheck,
    build_resume_options_from_handoff,
    build_resume_safety_audit,
    clear_cradle_resume_precheck,
    load_cradle_resume_precheck_bundle,
    run_cradle_resume_precheck,
    select_recommended_resume_option,
    validate_cradle_resume_precheck,
    write_cradle_resume_precheck_bundle,
)


class CradleStateResumePrecheckTests(unittest.TestCase):
    def test_build_resume_options_from_handoff_creates_options(self) -> None:
        bundle = self._bundle()
        options = build_resume_options_from_handoff(bundle)
        self.assertGreaterEqual(len(options), 2)
        self.assertIn("inspect_status", {option.resume_kind for option in options})

    def test_select_recommended_resume_option_picks_pending_candidate_before_run_new_case(self) -> None:
        bundle = self._bundle(
            counts={"pending_candidate_count": 1},
            source_ids={"last_candidate_id": "candidate:pending"},
        )
        option = select_recommended_resume_option(
            build_resume_options_from_handoff(bundle)
        )
        self.assertEqual(option.resume_kind, "review_pending_candidates")

    def test_suspended_task_creates_resume_suspended_task_precheck_option(self) -> None:
        bundle = self._bundle(
            source_ids={"suspended_task_frame_id": "suspended:task"},
            last_task_status="suspended",
        )
        option = select_recommended_resume_option(
            build_resume_options_from_handoff(bundle)
        )
        self.assertEqual(option.resume_kind, "resume_suspended_task_precheck")
        self.assertFalse(option.allowed_to_resume_task_now)

    def test_pending_candidates_create_review_pending_candidates_option(self) -> None:
        bundle = self._bundle(
            counts={"pending_candidate_count": 2},
            source_ids={"last_candidate_id": "candidate:pending"},
        )
        options = build_resume_options_from_handoff(bundle)
        self.assertIn("review_pending_candidates", {option.resume_kind for option in options})

    def test_reviewed_learning_without_memory_trace_recommends_build_memory_trace_precheck(self) -> None:
        bundle = self._bundle(
            counts={"reviewed_learning_count": 1, "memory_application_data_count": 0},
            source_ids={
                "last_reviewed_learning_id": "reviewed:one",
                "last_memory_trace_id": None,
                "last_memory_application_data_id": None,
                "last_growth_readiness_audit_id": None,
            },
        )
        option = select_recommended_resume_option(
            build_resume_options_from_handoff(bundle)
        )
        self.assertEqual(option.resume_kind, "build_memory_trace_precheck")

    def test_memory_application_data_without_readback_preview_recommends_preview_readback_precheck(self) -> None:
        bundle = self._bundle(
            counts={
                "reviewed_learning_count": 1,
                "memory_application_data_count": 1,
                "readback_preview_count": 0,
            },
            source_ids={
                "last_memory_application_data_id": "memory_app:one",
                "last_readback_preview_id": None,
                "last_growth_readiness_audit_id": None,
            },
        )
        option = select_recommended_resume_option(
            build_resume_options_from_handoff(bundle)
        )
        self.assertEqual(option.resume_kind, "preview_readback_precheck")

    def test_readback_preview_without_application_recommends_apply_readback_precheck(self) -> None:
        bundle = self._bundle(
            counts={
                "readback_preview_count": 1,
                "readback_application_count": 0,
            },
            source_ids={
                "last_readback_preview_id": "preview:one",
                "last_readback_application_id": None,
                "last_growth_readiness_audit_id": None,
            },
        )
        option = select_recommended_resume_option(
            build_resume_options_from_handoff(bundle)
        )
        self.assertEqual(option.resume_kind, "apply_readback_precheck")

    def test_readback_application_without_contrast_recommends_run_readback_contrast_precheck(self) -> None:
        bundle = self._bundle(
            counts={"readback_application_count": 1, "contrast_count": 0},
            source_ids={
                "last_readback_application_id": "application:one",
                "last_contrast_id": None,
                "last_growth_readiness_audit_id": None,
            },
        )
        option = select_recommended_resume_option(
            build_resume_options_from_handoff(bundle)
        )
        self.assertEqual(option.resume_kind, "run_readback_contrast_precheck")

    def test_contrast_without_loop_evidence_recommends_build_loop_evidence_precheck(self) -> None:
        bundle = self._bundle(
            counts={"contrast_count": 1, "loop_evidence_count": 0},
            source_ids={
                "last_contrast_id": "contrast:one",
                "last_loop_evidence_id": None,
                "last_growth_readiness_audit_id": None,
            },
        )
        option = select_recommended_resume_option(
            build_resume_options_from_handoff(bundle)
        )
        self.assertEqual(option.resume_kind, "build_loop_evidence_precheck")

    def test_growth_readiness_audit_recommends_inspect_growth_readiness(self) -> None:
        bundle = self._bundle(
            source_ids={"last_growth_readiness_audit_id": "growth:ready"},
        )
        option = select_recommended_resume_option(
            build_resume_options_from_handoff(bundle)
        )
        self.assertEqual(option.resume_kind, "inspect_growth_readiness")

    def test_empty_safe_handoff_recommends_run_new_case_precheck(self) -> None:
        bundle = self._empty_bundle()
        option = select_recommended_resume_option(
            build_resume_options_from_handoff(bundle)
        )
        self.assertEqual(option.resume_kind, "run_new_case_precheck")

    def test_invalid_handoff_blocks_precheck(self) -> None:
        precheck, _options, safety = build_cradle_resume_precheck({})
        self.assertFalse(precheck.resume_allowed)
        self.assertEqual(precheck.resume_blocked_reason, "blocked_invalid_handoff")
        self.assertEqual(safety.audit_status, "blocked_invalid_handoff")

    def test_resume_requires_teacher_false_blocks_precheck(self) -> None:
        bundle = self._bundle().to_dict()
        bundle["handoff"]["resume_requires_teacher"] = False
        precheck, _options, safety = build_cradle_resume_precheck(bundle)
        self.assertFalse(precheck.resume_allowed)
        self.assertEqual(
            precheck.resume_blocked_reason,
            "blocked_resume_requires_teacher_false",
        )
        self.assertEqual(safety.audit_status, "blocked_resume_requires_teacher_false")

    def test_forbidden_runtime_authority_flags_block_safety_audit(self) -> None:
        bundle = self._bundle().to_dict()
        bundle["handoff"]["scheduler_created"] = True
        precheck, options, safety = build_cradle_resume_precheck(bundle)
        validation = validate_cradle_resume_precheck(precheck, options, safety)
        self.assertFalse(precheck.resume_allowed)
        self.assertEqual(
            safety.audit_status,
            "blocked_forbidden_runtime_authority_detected",
        )
        self.assertTrue(validation["valid"])

    def test_all_resume_options_are_precheck_only_and_non_authoritative(self) -> None:
        options = build_resume_options_from_handoff(self._bundle())
        self.assertTrue(all(option.precheck_only for option in options))
        self.assertTrue(all(not option.allowed_to_execute_now for option in options))
        self.assertTrue(all(not option.allowed_to_create_tick_now for option in options))
        self.assertTrue(all(not option.allowed_to_resume_task_now for option in options))
        self.assertTrue(all(not option.allowed_to_write_memory_now for option in options))

    def test_write_load_and_clear_precheck_bundle_use_only_three_known_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            precheck, options, safety = build_cradle_resume_precheck(self._bundle())
            write = write_cradle_resume_precheck_bundle(temp_dir, precheck, options, safety)
            loaded = load_cradle_resume_precheck_bundle(temp_dir)
            extra = Path(temp_dir) / "keep_me.json"
            extra.write_text("{}", encoding="utf-8")
            cleared = clear_cradle_resume_precheck(temp_dir)
            self.assertTrue(extra.exists())
            self.assertEqual(set(write["files_written"]), set(KNOWN_PRECHECK_FILES))
            self.assertEqual(loaded[0].precheck_id, precheck.precheck_id)
            self.assertEqual(set(cleared["removed_files"]), set(KNOWN_PRECHECK_FILES))
            for file_name in KNOWN_PRECHECK_FILES:
                self.assertFalse((Path(temp_dir) / file_name).exists())

    def test_cli_run_show_list_validate_and_clear_work(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            write_cradle_state_handoff_bundle(self._bundle(), temp_dir)
            run = self._run_state_cli("run-precheck", temp_dir)
            self.assertEqual(run.returncode, 0, run.stderr)
            show = self._run_state_cli("show-precheck", temp_dir)
            self.assertEqual(show.returncode, 0, show.stderr)
            options = self._run_state_cli("list-options", temp_dir)
            self.assertEqual(options.returncode, 0, options.stderr)
            validate = self._run_state_cli("validate-precheck", temp_dir)
            self.assertEqual(validate.returncode, 0, validate.stderr)
            clear = self._run_state_cli("clear-precheck", temp_dir)
            self.assertEqual(clear.returncode, 0, clear.stderr)

    def test_guided_teacher_console_state_resume_precheck_commands_work(self) -> None:
        with tempfile.TemporaryDirectory() as state_dir:
            build_state_handoff_from_guided_cradle_growth_console(state_dir=state_dir)
            run = run_state_resume_precheck_from_guided_cradle_growth_console(
                state_dir=state_dir
            )
            shown = show_state_resume_precheck_from_guided_cradle_growth_console(
                state_dir=state_dir
            )
            options = list_state_resume_options_from_guided_cradle_growth_console(
                state_dir=state_dir
            )
            validation = validate_state_resume_precheck_from_guided_cradle_growth_console(
                state_dir=state_dir
            )
            status = get_guided_cradle_growth_status(state_dir=state_dir)
        self.assertTrue(run["resume_precheck"]["validation"]["valid"])
        self.assertEqual(shown["precheck_id"], run["resume_precheck"]["precheck_id"])
        self.assertGreaterEqual(len(options["resume_options"]), 1)
        self.assertTrue(validation["valid"])
        self.assertTrue(status["resume_precheck_available"])
        self.assertTrue(status["resume_requires_teacher"])

    def test_guided_teacher_console_cli_state_resume_commands_work(self) -> None:
        with tempfile.TemporaryDirectory() as state_dir:
            handoff = self._run_guided_cli("state-handoff-build", state_dir)
            self.assertEqual(handoff.returncode, 0, handoff.stderr)
            run = self._run_guided_cli("state-resume-precheck", state_dir)
            self.assertEqual(run.returncode, 0, run.stderr)
            show = self._run_guided_cli("state-resume-show", state_dir)
            self.assertEqual(show.returncode, 0, show.stderr)
            options = self._run_guided_cli("state-resume-options", state_dir)
            self.assertEqual(options.returncode, 0, options.stderr)
            validate = self._run_guided_cli("state-resume-validate", state_dir)
            self.assertEqual(validate.returncode, 0, validate.stderr)

    def test_known_precheck_file_names_are_exact(self) -> None:
        self.assertEqual(
            set(KNOWN_PRECHECK_FILES),
            {PRECHECK_FILE, OPTIONS_FILE, SAFETY_AUDIT_FILE},
        )

    def test_no_repo_data_pollution_or_forbidden_authority(self) -> None:
        precheck, _options, safety = build_cradle_resume_precheck(self._bundle())
        self.assertFalse(precheck.automatic_resume_created)
        self.assertFalse(precheck.task_resumed)
        self.assertFalse(precheck.scheduler_created)
        self.assertFalse(precheck.open_ended_loop_created)
        self.assertFalse(precheck.action_execution_created)
        self.assertFalse(precheck.free_action_selection_created)
        self.assertFalse(precheck.automatic_learning_approval_created)
        self.assertFalse(precheck.core_memory_write_performed)
        self.assertFalse(precheck.long_term_memory_write_performed)
        self.assertFalse(precheck.archive_memory_write_performed)
        self.assertFalse(precheck.anchor_write_performed)
        self.assertTrue(safety.no_core_longterm_archive_anchor_write)
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _bundle(
        self,
        *,
        counts: dict[str, int] | None = None,
        source_ids: dict[str, str | None] | None = None,
        last_task_status: str = "closed",
    ):
        base_counts = {
            "pending_candidate_count": 0,
            "reviewed_learning_count": 1,
            "memory_application_data_count": 1,
            "readback_preview_count": 1,
            "readback_application_count": 1,
            "contrast_count": 1,
            "loop_evidence_count": 1,
        }
        base_counts.update(counts or {})
        return build_cradle_state_handoff_bundle(
            counts=base_counts,
            source_ids=source_ids,
            last_task_status=last_task_status,
            source_trace_refs=("test:state_resume_precheck",),
        )

    def _empty_bundle(self):
        source_ids = {
            "last_session_id": None,
            "last_task_id": None,
            "last_case_id": None,
            "last_run_id": None,
            "last_closure_id": None,
            "last_candidate_id": None,
            "last_reviewed_learning_id": None,
            "last_memory_trace_id": None,
            "last_memory_application_data_id": None,
            "last_readback_preview_id": None,
            "last_readback_application_id": None,
            "last_contrast_id": None,
            "last_loop_evidence_id": None,
            "last_growth_readiness_audit_id": None,
            "active_task_frame_id": None,
            "suspended_task_frame_id": None,
        }
        counts = {
            "pending_candidate_count": 0,
            "reviewed_learning_count": 0,
            "memory_application_data_count": 0,
            "readback_preview_count": 0,
            "readback_application_count": 0,
            "contrast_count": 0,
            "loop_evidence_count": 0,
        }
        return self._bundle(counts=counts, source_ids=source_ids, last_task_status="none")

    def _run_state_cli(self, command: str, state_dir: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core_v1.state.cradle_state_resume_precheck_cli",
                command,
                "--state-dir",
                state_dir,
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    def _run_guided_cli(self, command: str, state_dir: str) -> subprocess.CompletedProcess[str]:
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
