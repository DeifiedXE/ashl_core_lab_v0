import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.environment.cradle_environment_state import (
    build_cradle_environment_state_from_case,
    build_cradle_environment_state_from_last_session,
    save_cradle_environment_state,
)
from ashl_core_v1.memory.promotion_queue import enqueue_manual_promotion_candidate
from ashl_core_v1.output.first_output_candidate import (
    build_first_output_candidate_from_last_daily,
    save_first_output_candidate,
)
from ashl_core_v1.output.first_output_followup import follow_last_first_output
from ashl_core_v1.output.first_output_promotion import promote_last_approved_first_output
from ashl_core_v1.output.first_output_review import review_last_first_output_candidate
from ashl_core_v1.runtime.cradle_session import run_case_in_cradle_session, start_cradle_session
from ashl_core_v1.runtime.daily_run import run_cradle_daily
from ashl_core_v1.runtime.open_cradle_tick_context import (
    BLOCKED_NEXT_SURFACES,
    build_open_cradle_tick_context,
    collect_tick_context_sources,
    derive_recommended_tick_mode,
    list_open_cradle_tick_context_history,
    load_last_open_cradle_tick_context,
    save_open_cradle_tick_context,
)
from ashl_core_v1.teacher_console.daily_teacher_note import write_daily_teacher_note


ROOT = Path(__file__).resolve().parents[2]
CLI_MODULE = "ashl_core_v1.runtime.open_cradle_tick_context_cli"


class OpenCradleTickContextBuilderTests(unittest.TestCase):
    def run_cli(
        self,
        data_dir: Path,
        *args: str,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", CLI_MODULE, "--data-dir", str(data_dir), *args],
            cwd=ROOT,
            check=check,
            capture_output=True,
            text=True,
        )

    def seed_active_session(
        self,
        data_dir: Path,
        case_id: str = "success_front_step",
        save_environment: bool = True,
    ) -> dict:
        session = start_cradle_session(data_dir)
        run_case_in_cradle_session(case_id, data_dir)
        if save_environment:
            save_cradle_environment_state(
                build_cradle_environment_state_from_last_session(data_dir),
                data_dir,
            )
        return session

    def seed_first_output_followup(self, data_dir: Path) -> dict:
        run_cradle_daily("basic", data_dir)
        save_first_output_candidate(build_first_output_candidate_from_last_daily(data_dir), data_dir)
        review_last_first_output_candidate("approved", "ok", data_dir)
        promote_last_approved_first_output(data_dir)
        return follow_last_first_output("teacher_note", "follow this", None, data_dir)

    def test_build_context_returns_dict_with_required_top_level_keys(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.seed_active_session(data_dir)

            context = build_open_cradle_tick_context(data_dir)

            for key in (
                "tick_context_id",
                "tick_context_status",
                "source_session_id",
                "source_turn_count",
                "source_state_snapshot_ref",
                "source_session_summary_ref",
                "source_last_trace_summary_ref",
                "source_environment_state_id",
                "source_daily_teacher_note_id",
                "source_first_output_followup_id",
                "source_memory_promotion_candidate_ids",
                "pending_review_items",
                "caregiver_attention_items",
                "environment_summary",
                "memory_queue_summary",
                "recommended_tick_mode",
                "tick_mode_reason_codes",
                "allowed_next_surfaces",
                "blocked_next_surfaces",
                "created_at",
                "trace_refs",
            ):
                self.assertIn(key, context)

    def test_missing_active_session_produces_stop_mode(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            context = build_open_cradle_tick_context(Path(temp_dir))

            self.assertEqual("not_ready", context["tick_context_status"])
            self.assertEqual("stop", context["recommended_tick_mode"])
            self.assertIn("no_active_session", context["tick_mode_reason_codes"])

    def test_existing_environment_state_is_linked(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.seed_active_session(data_dir, "blocked_front_obstacle")

            context = build_open_cradle_tick_context(data_dir)

            self.assertTrue(context["source_environment_state_id"])
            self.assertTrue(context["environment_summary"]["environment_state_present"])
            self.assertEqual("obstacle", context["environment_summary"]["front_state_kind"])

    def test_teacher_note_is_linked_when_present(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            run_cradle_daily("basic", data_dir)
            note = write_daily_teacher_note("daily note", ("watch",), None, data_dir)
            self.seed_active_session(data_dir)

            context = build_open_cradle_tick_context(data_dir)

            self.assertEqual(note["note_id"], context["source_daily_teacher_note_id"])
            self.assertIn("watch", context["caregiver_attention_items"])

    def test_first_output_followup_is_linked_when_present(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            followup = self.seed_first_output_followup(data_dir)
            self.seed_active_session(data_dir)

            context = build_open_cradle_tick_context(data_dir)

            self.assertEqual(followup["followup_id"], context["source_first_output_followup_id"])

    def test_memory_promotion_queue_candidate_ids_are_linked(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.seed_active_session(data_dir)
            candidate = enqueue_manual_promotion_candidate(
                "interesting trace",
                "future memory review",
                "normal",
                data_dir,
            )

            context = build_open_cradle_tick_context(data_dir)

            self.assertEqual(
                [candidate["promotion_candidate_id"]],
                context["source_memory_promotion_candidate_ids"],
            )
            self.assertEqual("promotion_review_pending", context["recommended_tick_mode"])
            self.assertIn(
                "memory_promotion_candidate_present",
                context["tick_mode_reason_codes"],
            )

    def test_missing_environment_state_produces_environment_state_refresh_mode(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.seed_active_session(data_dir, save_environment=False)

            context = build_open_cradle_tick_context(data_dir)

            self.assertEqual("missing_sources", context["tick_context_status"])
            self.assertEqual("environment_state_refresh", context["recommended_tick_mode"])
            self.assertIn("environment_state_missing", context["tick_mode_reason_codes"])

    def test_unknown_environment_state_produces_review_pending_mode(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.seed_active_session(data_dir, save_environment=False)
            state = build_cradle_environment_state_from_case(
                "unknown_feedback",
                session_id="session_001",
                turn=1,
            )
            save_cradle_environment_state(state, data_dir)

            context = build_open_cradle_tick_context(data_dir)

            self.assertEqual("review_pending", context["recommended_tick_mode"])
            self.assertTrue(context["pending_review_items"])

    def test_teacher_wait_mode_can_be_derived_from_teacher_note_attention(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            run_cradle_daily("basic", data_dir)
            write_daily_teacher_note("teacher rejected this", ("teacher_rejected",), None, data_dir)
            self.seed_active_session(data_dir)

            context = build_open_cradle_tick_context(data_dir)

            self.assertEqual("teacher_wait", context["recommended_tick_mode"])
            self.assertIn("caregiver_attention_required", context["tick_mode_reason_codes"])

    def test_preferred_mode_manual_daily_case_can_produce_manual_daily_case_mode(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.seed_active_session(data_dir, save_environment=False)

            context = build_open_cradle_tick_context(data_dir, "manual_daily_case")

            self.assertEqual("manual_daily_case", context["recommended_tick_mode"])
            self.assertIn("preferred_manual_daily_case", context["tick_mode_reason_codes"])

    def test_allowed_and_blocked_surfaces_are_present(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.seed_active_session(data_dir)

            context = build_open_cradle_tick_context(data_dir)

            self.assertIn("show_context", context["allowed_next_surfaces"])
            self.assertIn("automatic_tick_execution", context["blocked_next_surfaces"])
            self.assertIn("free_action_selection", context["blocked_next_surfaces"])
            self.assertEqual(list(BLOCKED_NEXT_SURFACES), context["blocked_next_surfaces"])

    def test_save_load_last_context_round_trip_and_history_list(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.seed_active_session(data_dir)
            context = build_open_cradle_tick_context(data_dir)

            saved = save_open_cradle_tick_context(context, data_dir)

            self.assertEqual(saved, load_last_open_cradle_tick_context(data_dir))
            self.assertEqual(1, list_open_cradle_tick_context_history(data_dir)["tick_context_count"])

    def test_collect_sources_and_derive_mode_helpers_work(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.seed_active_session(data_dir)

            sources = collect_tick_context_sources(data_dir)
            mode = derive_recommended_tick_mode(sources)

            self.assertTrue(sources["active_session"])
            self.assertEqual("observe_only", mode["recommended_tick_mode"])

    def test_cli_build_show_and_list_context_history(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.seed_active_session(data_dir)

            build_result = self.run_cli(data_dir, "build-context")
            built = json.loads(build_result.stdout)
            last = json.loads(self.run_cli(data_dir, "show-last-context").stdout)
            history = json.loads(self.run_cli(data_dir, "list-context-history").stdout)

            self.assertEqual(built["tick_context_id"], last["tick_context_id"])
            self.assertEqual(1, history["tick_context_count"])

    def test_cli_preferred_manual_daily_case_outputs_manual_mode(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.seed_active_session(data_dir, save_environment=False)

            result = self.run_cli(
                data_dir,
                "build-context",
                "--preferred-mode",
                "manual_daily_case",
            )
            payload = json.loads(result.stdout)

            self.assertEqual("manual_daily_case", payload["recommended_tick_mode"])

    def test_repo_data_directory_is_not_polluted_during_tests(self):
        self.assertFalse((ROOT / "ashl_core_v1" / "data").exists())


if __name__ == "__main__":
    unittest.main()
