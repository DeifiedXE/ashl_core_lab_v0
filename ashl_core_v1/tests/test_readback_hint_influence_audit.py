from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from ashl_core_v1.task.readback_hint_influence_audit import (
    TaskWorkingMemoryReadbackHintInfluenceAuditReport,
    TaskWorkingMemoryReadbackHintNonInfluenceAudit,
    TaskWorkingMemoryReadbackHintVisibilityAudit,
    build_demo_candidate_ordering_changed_audit_report,
    build_demo_direct_command_changed_audit_report,
    build_demo_execution_created_audit_report,
    build_demo_final_action_changed_audit_report,
    build_demo_missing_visible_hints_audit_report,
    build_demo_selected_action_changed_audit_report,
    build_demo_task_behavior_changed_audit_report,
    build_demo_task_working_memory_readback_hint_influence_audit_report,
    build_demo_unexpected_visible_hints_audit_report,
    validate_task_working_memory_readback_hint_influence_audit_report,
    validate_task_working_memory_readback_hint_non_influence_audit,
    validate_task_working_memory_readback_hint_visibility_audit,
)


TASK_CLI = "ashl_core_v1.task.readback_hint_influence_audit_cli"
GUIDED_CLI = "ashl_core_v1.runtime.guided_cradle_growth_teacher_console_cli"


class ReadbackHintInfluenceAuditTests(unittest.TestCase):
    def test_visibility_audit_builds_from_package_78_demo_application(self) -> None:
        audit = self._visibility_audit()
        validation = validate_task_working_memory_readback_hint_visibility_audit(audit)
        self.assertTrue(validation["valid"])

    def test_visibility_audit_preserves_task_working_memory_id(self) -> None:
        self.assertEqual(
            self._visibility_audit().source_task_working_memory_id,
            "task_working_memory:future_demo",
        )

    def test_visibility_audit_preserves_readback_snapshot_id(self) -> None:
        self.assertIn(
            "future_task_working_memory_initialization_readback_snapshot",
            self._visibility_audit().source_readback_snapshot_id,
        )

    def test_visibility_audit_expected_hints_visible(self) -> None:
        audit = self._visibility_audit()
        self.assertEqual(audit.visibility_status, "passed_visible_expected_hints")
        self.assertTrue(audit.readback_hints_visible)
        self.assertIn("observe_before_direct_retry", audit.visible_hint_labels)
        self.assertIn("avoid_same_failed_direct_retry", audit.visible_hint_labels)

    def test_visibility_audit_detects_missing_expected_hints(self) -> None:
        payload = build_demo_missing_visible_hints_audit_report()
        audit = TaskWorkingMemoryReadbackHintVisibilityAudit.from_dict(
            payload["readback_hint_visibility_audit"]
        )
        self.assertEqual(audit.visibility_status, "failed_missing_expected_hints")
        self.assertTrue(audit.missing_hint_ids)

    def test_visibility_audit_detects_unexpected_hints(self) -> None:
        payload = build_demo_unexpected_visible_hints_audit_report()
        audit = TaskWorkingMemoryReadbackHintVisibilityAudit.from_dict(
            payload["readback_hint_visibility_audit"]
        )
        self.assertEqual(audit.visibility_status, "failed_unexpected_hints")
        self.assertIn("unexpected:hint", audit.unexpected_hint_ids)

    def test_visibility_audit_confirms_advisory_only(self) -> None:
        self.assertTrue(self._visibility_audit().advisory_only_confirmed)

    def test_visibility_audit_confirms_single_task_lifetime(self) -> None:
        self.assertTrue(self._visibility_audit().single_task_lifetime_confirmed)

    def test_visibility_audit_confirms_future_task_initialization_only(self) -> None:
        self.assertTrue(
            self._visibility_audit().future_task_initialization_only_confirmed
        )

    def test_non_influence_audit_builds_from_visibility_audit(self) -> None:
        audit = self._non_influence_audit()
        validation = validate_task_working_memory_readback_hint_non_influence_audit(
            audit
        )
        self.assertTrue(validation["valid"])

    def test_non_influence_audit_passes_when_candidate_ordering_unchanged(self) -> None:
        audit = self._non_influence_audit()
        self.assertEqual(audit.non_influence_status, "passed_no_influence_detected")
        self.assertEqual(audit.baseline_candidate_ordering, ())
        self.assertEqual(audit.observed_candidate_ordering, ())

    def test_non_influence_audit_detects_candidate_ordering_change(self) -> None:
        audit = self._blocked_non_influence("candidate-ordering-changed")
        self.assertEqual(
            audit.non_influence_status,
            "failed_candidate_ordering_changed",
        )

    def test_non_influence_audit_detects_selected_action_change(self) -> None:
        audit = self._blocked_non_influence("selected-action-changed")
        self.assertEqual(
            audit.non_influence_status,
            "failed_selected_action_changed",
        )

    def test_non_influence_audit_detects_final_action_change(self) -> None:
        audit = self._blocked_non_influence("final-action-changed")
        self.assertEqual(
            audit.non_influence_status,
            "failed_final_action_changed",
        )

    def test_non_influence_audit_detects_direct_command_change(self) -> None:
        audit = self._blocked_non_influence("direct-command-changed")
        self.assertEqual(
            audit.non_influence_status,
            "failed_direct_command_changed",
        )

    def test_non_influence_audit_detects_execution_created(self) -> None:
        audit = self._blocked_non_influence("execution-created")
        self.assertEqual(audit.non_influence_status, "failed_execution_created")

    def test_non_influence_audit_detects_task_behavior_changed(self) -> None:
        audit = self._blocked_non_influence("task-behavior-changed")
        self.assertEqual(
            audit.non_influence_status,
            "failed_task_behavior_changed",
        )

    def test_non_influence_audit_confirms_memory_layer_write_false(self) -> None:
        self.assertFalse(self._non_influence_audit().memory_layer_write_performed)

    def test_influence_audit_report_passes_when_visible_and_inert(self) -> None:
        report = self._report()
        validation = validate_task_working_memory_readback_hint_influence_audit_report(
            report
        )
        self.assertTrue(validation["valid"])
        self.assertEqual(report.audit_report_status, "passed_visible_and_inert")

    def test_influence_audit_report_fails_on_visibility_failure(self) -> None:
        payload = build_demo_missing_visible_hints_audit_report()
        report = TaskWorkingMemoryReadbackHintInfluenceAuditReport.from_dict(
            payload["readback_hint_influence_audit_report"]
        )
        self.assertEqual(report.audit_report_status, "failed_visibility")

    def test_influence_audit_report_fails_on_influence_detected(self) -> None:
        payload = build_demo_candidate_ordering_changed_audit_report()
        report = TaskWorkingMemoryReadbackHintInfluenceAuditReport.from_dict(
            payload["readback_hint_influence_audit_report"]
        )
        self.assertEqual(report.audit_report_status, "failed_influence_detected")

    def test_report_safe_claim_says_visible_and_inert_only(self) -> None:
        report = self._report()
        self.assertIn("visible as advisory-only hints", report.safe_claim)
        self.assertIn("do not affect candidate ordering", report.safe_claim)

    def test_report_blocked_claims_include_behavior_changing_concept_readback(self) -> None:
        self.assertIn(
            "no_behavior-changing_concept_readback",
            self._report().blocked_claims,
        )

    def test_audit_does_not_call_action_selection(self) -> None:
        payload = build_demo_task_working_memory_readback_hint_influence_audit_report()
        self.assertFalse(payload["action_selection_called"])

    def test_audit_does_not_call_execution(self) -> None:
        payload = build_demo_task_working_memory_readback_hint_influence_audit_report()
        self.assertFalse(payload["execution_called"])

    def test_blocked_demo_builders_cover_all_influence_cases(self) -> None:
        builders = {
            "candidate-ordering-changed": build_demo_candidate_ordering_changed_audit_report,
            "selected-action-changed": build_demo_selected_action_changed_audit_report,
            "final-action-changed": build_demo_final_action_changed_audit_report,
            "direct-command-changed": build_demo_direct_command_changed_audit_report,
            "execution-created": build_demo_execution_created_audit_report,
            "task-behavior-changed": build_demo_task_behavior_changed_audit_report,
        }
        for case, builder in builders.items():
            with self.subTest(case=case):
                payload = builder()
                report = payload["readback_hint_influence_audit_report"]
                self.assertEqual(
                    report["audit_report_status"],
                    "failed_influence_detected",
                )

    def test_cli_audit_demo_readback_hints_works(self) -> None:
        payload = self._run_task_cli("audit-demo-readback-hints")
        self.assertEqual(
            payload["readback_hint_influence_audit_report"]["audit_report_status"],
            "passed_visible_and_inert",
        )

    def test_cli_show_demo_visibility_audit_works(self) -> None:
        payload = self._run_task_cli("show-demo-visibility-audit")
        self.assertEqual(payload["visibility_status"], "passed_visible_expected_hints")

    def test_cli_show_demo_non_influence_audit_works(self) -> None:
        payload = self._run_task_cli("show-demo-non-influence-audit")
        self.assertEqual(
            payload["non_influence_status"],
            "passed_no_influence_detected",
        )

    def test_cli_show_demo_audit_report_works(self) -> None:
        payload = self._run_task_cli("show-demo-audit-report")
        self.assertEqual(payload["audit_report_status"], "passed_visible_and_inert")

    def test_cli_validate_demo_audit_works(self) -> None:
        payload = self._run_task_cli("validate-demo-audit")
        self.assertTrue(payload["valid"])

    def test_cli_blocked_missing_visible_hints_works(self) -> None:
        payload = self._run_task_cli(
            "audit-demo-blocked",
            "--case",
            "missing-visible-hints",
        )
        self.assertEqual(
            payload["readback_hint_influence_audit_report"]["audit_report_status"],
            "failed_visibility",
        )

    def test_cli_blocked_candidate_ordering_changed_works(self) -> None:
        self._assert_cli_failed_influence("candidate-ordering-changed")

    def test_cli_blocked_selected_action_changed_works(self) -> None:
        self._assert_cli_failed_influence("selected-action-changed")

    def test_cli_blocked_final_action_changed_works(self) -> None:
        self._assert_cli_failed_influence("final-action-changed")

    def test_cli_blocked_direct_command_changed_works(self) -> None:
        self._assert_cli_failed_influence("direct-command-changed")

    def test_cli_blocked_execution_created_works(self) -> None:
        self._assert_cli_failed_influence("execution-created")

    def test_cli_blocked_task_behavior_changed_works(self) -> None:
        self._assert_cli_failed_influence("task-behavior-changed")

    def test_guided_console_readback_hint_influence_audit_demo_works(self) -> None:
        payload = self._run_guided_cli(
            "task-audit-reviewed-concept-readback-hint-influence-demo"
        )
        self.assertEqual(
            payload["readback_hint_influence_audit_report"]["audit_report_status"],
            "passed_visible_and_inert",
        )

    def test_guided_console_show_visibility_audit_works(self) -> None:
        payload = self._run_guided_cli(
            "task-show-reviewed-concept-readback-hint-visibility-audit"
        )
        self.assertEqual(
            payload["readback_hint_visibility_audit"]["visibility_status"],
            "passed_visible_expected_hints",
        )

    def test_guided_console_show_non_influence_audit_works(self) -> None:
        payload = self._run_guided_cli(
            "task-show-reviewed-concept-readback-hint-non-influence-audit"
        )
        self.assertEqual(
            payload["readback_hint_non_influence_audit"]["non_influence_status"],
            "passed_no_influence_detected",
        )

    def test_guided_console_show_report_works(self) -> None:
        payload = self._run_guided_cli(
            "task-show-reviewed-concept-readback-hint-influence-report"
        )
        self.assertEqual(
            payload["readback_hint_influence_audit_report"]["audit_report_status"],
            "passed_visible_and_inert",
        )

    def test_guided_console_validate_influence_audit_works(self) -> None:
        payload = self._run_guided_cli(
            "task-validate-reviewed-concept-readback-hint-influence-audit"
        )
        self.assertTrue(payload["validation"]["valid"])

    def test_no_repo_data_created(self) -> None:
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _payload(self) -> dict[str, object]:
        return build_demo_task_working_memory_readback_hint_influence_audit_report()

    def _visibility_audit(self) -> TaskWorkingMemoryReadbackHintVisibilityAudit:
        return TaskWorkingMemoryReadbackHintVisibilityAudit.from_dict(
            self._payload()["readback_hint_visibility_audit"]
        )

    def _non_influence_audit(self) -> TaskWorkingMemoryReadbackHintNonInfluenceAudit:
        return TaskWorkingMemoryReadbackHintNonInfluenceAudit.from_dict(
            self._payload()["readback_hint_non_influence_audit"]
        )

    def _report(self) -> TaskWorkingMemoryReadbackHintInfluenceAuditReport:
        return TaskWorkingMemoryReadbackHintInfluenceAuditReport.from_dict(
            self._payload()["readback_hint_influence_audit_report"]
        )

    def _blocked_non_influence(
        self,
        case: str,
    ) -> TaskWorkingMemoryReadbackHintNonInfluenceAudit:
        payload = self._run_task_cli("audit-demo-blocked", "--case", case)
        return TaskWorkingMemoryReadbackHintNonInfluenceAudit.from_dict(
            payload["readback_hint_non_influence_audit"]
        )

    def _assert_cli_failed_influence(self, case: str) -> None:
        payload = self._run_task_cli("audit-demo-blocked", "--case", case)
        self.assertEqual(
            payload["readback_hint_influence_audit_report"]["audit_report_status"],
            "failed_influence_detected",
        )

    def _run_task_cli(self, *args: str) -> dict:
        result = subprocess.run(
            [sys.executable, "-m", TASK_CLI, *args],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(result.stdout)

    def _run_guided_cli(self, *args: str) -> dict:
        result = subprocess.run(
            [sys.executable, "-m", GUIDED_CLI, *args],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(result.stdout)


if __name__ == "__main__":
    unittest.main()
