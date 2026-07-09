from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

from ashl_core_v1.host_body import host_body_embodied_learning_closed_loop_audit as status
from ashl_core_v1.runtime.guided_cradle_growth_teacher_console import (
    show_host_body_current_status_after_113_from_guided_cradle_growth_console,
)


STATUS_CLI = "ashl_core_v1.host_body.host_body_embodied_learning_closed_loop_audit_cli"
GUIDED_CLI = "ashl_core_v1.runtime.guided_cradle_growth_teacher_console_cli"


class HostBodyEmbodiedLearningClosedLoopCurrentStatusTests(unittest.TestCase):
    def test_current_status_report_file_generated_and_valid(self) -> None:
        report_path = Path(status.CURRENT_STATUS_REPORT_PATH)
        self.assertTrue(report_path.exists())

        report = status.get_current_status_report_markdown()
        self.assertIn("# ASHL Core v1 Current Status After Package 113", report)
        validation = status.validate_current_status_report_text(report)
        self.assertTrue(validation["valid"])
        self.assertEqual(validation["missing_fragments"], ())

    def test_current_status_report_includes_latest_milestone(self) -> None:
        report = status.get_current_status_report_markdown()
        self.assertIn("Package 113 milestone audit result", report)
        self.assertIn(status.PACKAGE_113_MILESTONE_AUDIT_RESULT, report)
        self.assertIn("Host Body embodied learning readback loop status", report)

    def test_current_status_report_includes_completed_loops_and_safe_loop(self) -> None:
        report = status.get_current_status_report_markdown()
        for completed_loop in status.COMPLETED_MAJOR_LOOPS:
            with self.subTest(completed_loop=completed_loop):
                self.assertIn(completed_loop, report)

        for safe_loop_step in status.CURRENT_SAFE_LOOP_STEPS:
            with self.subTest(safe_loop_step=safe_loop_step):
                self.assertIn(safe_loop_step, report)
        self.assertIn("Host Body event\n→ internal action", report)

    def test_current_status_report_includes_all_false_boundaries(self) -> None:
        report = status.get_current_status_report_markdown()
        required_false_boundaries = (
            "real camera access: false / not created",
            "real microphone access: false / not created",
            "semantic vision: false / not created",
            "speech recognition: false / not created",
            "Task Engine selected_action from Host Body readback: false / not created",
            "final_action / direct_command / sandbox execution: false / not created",
            "external control: false / not created",
            "OS / mouse / keyboard / browser / file / network / shell / API operation: false / not created",
            "long-term memory write: false / not created",
            "Core memory write: false / not created",
            "automatic learning approval: false / not created",
            "teacher approval creation: false / not created",
            "first_output: false / not created",
            "live Qingyin runtime session: false / not created",
            "Thought Engine behavior: false / not created",
            "production behavior: false / not created",
        )
        for boundary in required_false_boundaries:
            with self.subTest(boundary=boundary):
                self.assertIn(boundary, report)

        payload = status.build_current_ashl_core_v1_status_after_package_113_report()
        for field_name, expected in status.FORBIDDEN_CAPABILITY_FLAGS.items():
            with self.subTest(field_name=field_name):
                self.assertIs(payload[field_name], expected)

    def test_current_status_report_includes_trace_spine_and_future_cl_boundary(self) -> None:
        report = status.get_current_status_report_markdown()
        required_boundary_text = (
            "GCMC v0.3 is future AGE architecture only",
            "Qingyin v1 does not implement GCMC runtime",
            "Qingyin v1 does not create CL tokens",
            "Qingyin v1 does not create Concept Compiler",
            "Qingyin v1 does not create Pattern Miner",
            "Trace Spine format stays unified and time-aligned",
            "Raw trace is append-only during service period and is not summarized",
            "Memory layer stores reviewed interpretation + source_trace_refs",
            "concept_id is not embedded into raw history",
            "formed_under_assumption is not required now because Qingyin v1 does not use CL tokens",
        )
        for fragment in required_boundary_text:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, report)

    def test_current_status_report_lists_missing_and_next_packages(self) -> None:
        report = status.get_current_status_report_markdown()
        missing_work = (
            "bounded embodied loop runner",
            "no-Codex teacher console operation flow",
            "session end review / promote gate",
            "no-Codex fixture embodied growth loop milestone audit",
            "real camera read-only low-level adapter",
            "real mic read-only low-level adapter",
            "real sensor safety/noise audit",
            "real sensor embodied learning loop audit",
        )
        for item in missing_work:
            with self.subTest(item=item):
                self.assertIn(item, report)

        for package in status.NEXT_RECOMMENDED_PACKAGES:
            with self.subTest(package=package):
                self.assertIn(package, report)

    def test_current_status_report_blocks_forbidden_claims(self) -> None:
        report = status.get_current_status_report_markdown()
        forbidden_claims = (
            "Qingyin is awake.",
            "Qingyin can see/hear through real sensors.",
            "Qingyin can control the computer.",
            "Qingyin can self-approve learning.",
            "Qingyin has first_output.",
            "Qingyin has live runtime autonomy.",
        )
        for claim in forbidden_claims:
            with self.subTest(claim=claim):
                self.assertIn(claim, report)

        self.assertIn("not a live autonomous Qingyin runtime", report)
        self.assertIn("does not have real perception", report)
        self.assertIn("does not have real perception, external control, first_output", report)

    def test_cli_show_current_status_report_works(self) -> None:
        result = subprocess.run(
            ["py", "-3", "-m", STATUS_CLI, "show-current-status-report"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(
            payload["package_113_milestone_audit_result"],
            status.PACKAGE_113_MILESTONE_AUDIT_RESULT,
        )
        self.assertTrue(payload["validation"]["valid"])
        self.assertIn("# ASHL Core v1 Current Status After Package 113", payload["report_markdown"])
        self.assertFalse(payload["first_output_created"])
        self.assertFalse(payload["live_qingyin_runtime_session_created"])

    def test_guided_console_current_status_command_works(self) -> None:
        guided = show_host_body_current_status_after_113_from_guided_cradle_growth_console()
        self.assertEqual(
            guided["guided_console_action"],
            "host_body_show_current_status_after_113",
        )
        self.assertTrue(guided["current_status_report"]["validation"]["valid"])
        self.assertFalse(guided["first_output_created"])
        self.assertFalse(guided["live_qingyin_runtime_session_created"])

        result = subprocess.run(
            ["py", "-3", "-m", GUIDED_CLI, "host-body-show-current-status-after-113"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(
            payload["guided_console_action"],
            "host_body_show_current_status_after_113",
        )
        self.assertTrue(payload["current_status_report"]["validation"]["valid"])

    def test_no_repo_data_output_created(self) -> None:
        self.assertFalse(Path("ashl_core_v1/data").exists())


if __name__ == "__main__":
    unittest.main()
