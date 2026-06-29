from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.runtime.guided_cradle_growth_teacher_console import (
    build_state_handoff_from_guided_cradle_growth_console,
    get_guided_cradle_growth_status,
    list_state_handoff_bookmarks_from_guided_cradle_growth_console,
    show_state_handoff_from_guided_cradle_growth_console,
    validate_state_handoff_from_guided_cradle_growth_console,
)
from ashl_core_v1.state.cradle_state_persistence_handoff import (
    BOOKMARKS_FILE,
    HANDOFF_FILE,
    KNOWN_HANDOFF_FILES,
    LAST_TRACE_SUMMARY_FILE,
    SESSION_SUMMARY_FILE,
    build_cradle_bookmarks,
    build_cradle_last_trace_summary,
    build_cradle_session_summary,
    build_cradle_state_handoff,
    build_cradle_state_handoff_bundle,
    clear_cradle_state_handoff,
    load_cradle_state_handoff_bundle,
    validate_cradle_state_handoff,
    write_cradle_state_handoff_bundle,
)


class CradleStatePersistenceHandoffTests(unittest.TestCase):
    def test_build_cradle_state_handoff_creates_valid_handoff(self) -> None:
        handoff = build_cradle_state_handoff()
        self.assertEqual(handoff.source_engine, "state_engine")
        self.assertEqual(handoff.schema_version, "state_engine_cradle_handoff_v0")
        self.assertTrue(handoff.resume_requires_teacher)
        self.assertFalse(handoff.scheduler_created)

    def test_build_cradle_session_summary_creates_compact_summary(self) -> None:
        handoff = build_cradle_state_handoff()
        summary = build_cradle_session_summary(handoff)
        self.assertEqual(summary.handoff_id, handoff.handoff_id)
        self.assertIn("Demo fixture", summary.summary_text)
        self.assertNotIn("per_tick_stub_records", summary.to_dict())

    def test_build_cradle_last_trace_summary_stores_ids_only(self) -> None:
        handoff = build_cradle_state_handoff()
        trace = build_cradle_last_trace_summary(handoff)
        self.assertTrue(trace.last_run_id)
        for key, value in trace.to_dict().items():
            if key.startswith("last_") and key.endswith("_id"):
                self.assertTrue(value is None or isinstance(value, str))

    def test_build_cradle_bookmarks_creates_teacher_visible_bookmarks(self) -> None:
        handoff = build_cradle_state_handoff()
        trace = build_cradle_last_trace_summary(handoff)
        bookmarks = build_cradle_bookmarks(handoff, trace)
        self.assertGreaterEqual(len(bookmarks), 5)
        self.assertTrue(all(bookmark.teacher_visible for bookmark in bookmarks))

    def test_handoff_bundle_validation_passes_for_valid_bundle(self) -> None:
        bundle = build_cradle_state_handoff_bundle()
        validation = validate_cradle_state_handoff(bundle)
        self.assertTrue(validation["valid"])
        self.assertTrue(validation["resume_requires_teacher"])

    def test_handoff_bundle_validation_blocks_mismatched_handoff_id(self) -> None:
        bundle = build_cradle_state_handoff_bundle().to_dict()
        bundle["session_summary"]["handoff_id"] = "different"
        validation = validate_cradle_state_handoff(bundle)
        self.assertFalse(validation["valid"])
        self.assertIn("session_summary_handoff_id_mismatch", validation["error_codes"])

    def test_handoff_bundle_validation_blocks_resume_requires_teacher_false(self) -> None:
        bundle = build_cradle_state_handoff_bundle().to_dict()
        bundle["handoff"]["resume_requires_teacher"] = False
        validation = validate_cradle_state_handoff(bundle)
        self.assertFalse(validation["valid"])
        self.assertIn("resume_requires_teacher_false", validation["error_codes"])

    def test_handoff_bundle_validation_blocks_memory_write_flags(self) -> None:
        bundle = build_cradle_state_handoff_bundle().to_dict()
        bundle["handoff"]["memory_write_performed"] = True
        validation = validate_cradle_state_handoff(bundle)
        self.assertFalse(validation["valid"])
        self.assertIn("memory_write_performed_true", validation["error_codes"])

    def test_handoff_bundle_validation_blocks_scheduler_flag(self) -> None:
        bundle = build_cradle_state_handoff_bundle().to_dict()
        bundle["handoff"]["scheduler_created"] = True
        validation = validate_cradle_state_handoff(bundle)
        self.assertFalse(validation["valid"])
        self.assertIn("scheduler_created_true", validation["error_codes"])

    def test_handoff_bundle_validation_blocks_action_execution_flag(self) -> None:
        bundle = build_cradle_state_handoff_bundle().to_dict()
        bundle["handoff"]["action_execution_created"] = True
        validation = validate_cradle_state_handoff(bundle)
        self.assertFalse(validation["valid"])
        self.assertIn("action_execution_created_true", validation["error_codes"])

    def test_handoff_bundle_validation_blocks_unknown_bookmark_target(self) -> None:
        bundle = build_cradle_state_handoff_bundle().to_dict()
        bundle["bookmarks"][0]["target_id"] = "missing:target"
        validation = validate_cradle_state_handoff(bundle)
        self.assertFalse(validation["valid"])
        self.assertIn("bookmark_target_unknown", validation["error_codes"])

    def test_write_cradle_state_handoff_bundle_writes_four_files_to_explicit_state_dir(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            bundle = build_cradle_state_handoff_bundle()
            result = write_cradle_state_handoff_bundle(bundle, temp_dir)
            for file_name in KNOWN_HANDOFF_FILES:
                self.assertTrue((Path(temp_dir) / file_name).is_file())
        self.assertEqual(set(result["files_written"]), set(KNOWN_HANDOFF_FILES))

    def test_load_cradle_state_handoff_bundle_reads_same_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            bundle = build_cradle_state_handoff_bundle()
            write_cradle_state_handoff_bundle(bundle, temp_dir)
            loaded = load_cradle_state_handoff_bundle(temp_dir)
        self.assertEqual(loaded.handoff.handoff_id, bundle.handoff.handoff_id)
        self.assertEqual(len(loaded.bookmarks), len(bundle.bookmarks))

    def test_clear_handoff_removes_only_known_handoff_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            bundle = build_cradle_state_handoff_bundle()
            write_cradle_state_handoff_bundle(bundle, temp_dir)
            extra = Path(temp_dir) / "keep_me.json"
            extra.write_text("{}", encoding="utf-8")
            result = clear_cradle_state_handoff(temp_dir)
            self.assertTrue(extra.exists())
            self.assertEqual(set(result["removed_files"]), set(KNOWN_HANDOFF_FILES))
            for file_name in KNOWN_HANDOFF_FILES:
                self.assertFalse((Path(temp_dir) / file_name).exists())

    def test_cli_build_show_list_validate_and_clear_work_with_temp_state_dir(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            build = self._run_state_cli("build-handoff", temp_dir)
            self.assertEqual(build.returncode, 0, build.stderr)
            show = self._run_state_cli("show-handoff", temp_dir)
            self.assertEqual(show.returncode, 0, show.stderr)
            bookmarks = self._run_state_cli("list-bookmarks", temp_dir)
            self.assertEqual(bookmarks.returncode, 0, bookmarks.stderr)
            validate = self._run_state_cli("validate-handoff", temp_dir)
            self.assertEqual(validate.returncode, 0, validate.stderr)
            clear = self._run_state_cli("clear-handoff", temp_dir)
            self.assertEqual(clear.returncode, 0, clear.stderr)

    def test_guided_teacher_console_state_handoff_commands_work(self) -> None:
        with tempfile.TemporaryDirectory() as state_dir:
            built = build_state_handoff_from_guided_cradle_growth_console(
                state_dir=state_dir
            )
            shown = show_state_handoff_from_guided_cradle_growth_console(
                state_dir=state_dir
            )
            bookmarks = list_state_handoff_bookmarks_from_guided_cradle_growth_console(
                state_dir=state_dir
            )
            validation = validate_state_handoff_from_guided_cradle_growth_console(
                state_dir=state_dir
            )
            status = get_guided_cradle_growth_status(state_dir=state_dir)
        self.assertTrue(built["validation"]["valid"])
        self.assertEqual(shown["handoff"]["handoff_id"], built["write_result"]["handoff_id"])
        self.assertGreaterEqual(len(bookmarks["bookmarks"]), 5)
        self.assertTrue(validation["valid"])
        self.assertTrue(status["state_handoff_available"])
        self.assertTrue(status["resume_requires_teacher"])

    def test_guided_teacher_console_cli_state_handoff_commands_work(self) -> None:
        with tempfile.TemporaryDirectory() as state_dir:
            build = self._run_guided_cli("state-handoff-build", state_dir)
            self.assertEqual(build.returncode, 0, build.stderr)
            show = self._run_guided_cli("state-handoff-show", state_dir)
            self.assertEqual(show.returncode, 0, show.stderr)
            bookmarks = self._run_guided_cli("state-handoff-bookmarks", state_dir)
            self.assertEqual(bookmarks.returncode, 0, bookmarks.stderr)
            validate = self._run_guided_cli("state-handoff-validate", state_dir)
            self.assertEqual(validate.returncode, 0, validate.stderr)

    def test_no_automatic_resume_or_forbidden_authority(self) -> None:
        bundle = build_cradle_state_handoff_bundle()
        validation = validate_cradle_state_handoff(bundle)
        self.assertFalse(validation["automatic_resume"])
        self.assertFalse(bundle.handoff.scheduler_created)
        self.assertFalse(bundle.handoff.open_ended_loop_created)
        self.assertFalse(bundle.handoff.action_execution_created)
        self.assertFalse(bundle.handoff.free_action_selection_created)
        self.assertFalse(bundle.handoff.automatic_learning_approval_created)
        self.assertFalse(bundle.handoff.core_memory_write_performed)
        self.assertFalse(bundle.handoff.long_term_memory_write_performed)
        self.assertFalse(bundle.handoff.archive_memory_write_performed)
        self.assertFalse(bundle.handoff.anchor_write_performed)

    def test_no_repo_data_pollution(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            write_cradle_state_handoff_bundle(build_cradle_state_handoff_bundle(), temp_dir)
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def test_known_handoff_file_names_are_exact(self) -> None:
        self.assertEqual(
            set(KNOWN_HANDOFF_FILES),
            {HANDOFF_FILE, SESSION_SUMMARY_FILE, LAST_TRACE_SUMMARY_FILE, BOOKMARKS_FILE},
        )

    def _run_state_cli(self, command: str, state_dir: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core_v1.state.cradle_state_persistence_handoff_cli",
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
