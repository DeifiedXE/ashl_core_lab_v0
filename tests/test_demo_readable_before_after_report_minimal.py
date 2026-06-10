import json
import subprocess
import sys
import unittest
from copy import deepcopy

from ashl_core.before_after_trial_contrast import run_before_after_trial_contrast_check
from ashl_core.demo_readable_before_after_report_minimal import (
    build_demo_readable_before_after_report,
    run_demo_readable_before_after_report_minimal_check,
    validate_demo_readable_before_after_report,
)
from ashl_core.lesson_effect_evidence_trace_minimal import run_lesson_effect_evidence_trace_minimal_check
from ashl_core.session_experience_record_schema_minimal import run_session_experience_record_schema_minimal_check
from ashl_core.teaching_cli import run_command


EXPECTED_FIELDS = {
    "report_id",
    "source_contrast_id",
    "source_evidence_trace_id",
    "source_experience_record_id",
    "trace_only",
    "human_summary",
    "claim_limits",
    "blocked_flags",
}


class DemoReadableBeforeAfterReportMinimalTests(unittest.TestCase):
    def _valid_contrast(self):
        result = run_before_after_trial_contrast_check()
        return deepcopy(
            next(
                record
                for record, validation in zip(
                    result["before_after_contrasts"],
                    result["validation_results"],
                )
                if validation["valid"]
            )
        )

    def _valid_evidence(self):
        result = run_lesson_effect_evidence_trace_minimal_check()
        return deepcopy(
            next(
                record
                for record, validation in zip(
                    result["lesson_effect_evidence_traces"],
                    result["validation_results"],
                )
                if validation["valid"]
            )
        )

    def _valid_experience(self):
        result = run_session_experience_record_schema_minimal_check()
        return deepcopy(
            next(
                record
                for record, validation in zip(
                    result["session_experience_records"],
                    result["validation_results"],
                )
                if validation["valid"]
            )
        )

    def _valid_record(self):
        record = build_demo_readable_before_after_report(
            self._valid_contrast(),
            self._valid_evidence(),
            self._valid_experience(),
        )
        self.assertIsNotNone(record)
        return record

    def test_valid_sources_create_valid_report(self):
        contrast = self._valid_contrast()
        evidence = self._valid_evidence()
        experience = self._valid_experience()
        before = (deepcopy(contrast), deepcopy(evidence), deepcopy(experience))
        record = build_demo_readable_before_after_report(contrast, evidence, experience)
        validation = validate_demo_readable_before_after_report(record)

        self.assertEqual((contrast, evidence, experience), before)
        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(record["source_contrast_id"], contrast["contrast_id"])
        self.assertEqual(record["source_evidence_trace_id"], evidence["evidence_trace_id"])
        self.assertEqual(record["source_experience_record_id"], experience["experience_record_id"])
        self.assertTrue(record["trace_only"])

    def test_record_has_only_expected_top_level_fields(self):
        record = self._valid_record()

        self.assertEqual(set(record), EXPECTED_FIELDS)
        self.assertEqual(len(record), 8)

    def test_human_summary_has_required_text(self):
        record = self._valid_record()
        summary = record["human_summary"]

        for field in ["before", "after", "visible_difference", "plain_result"]:
            with self.subTest(field=field):
                self.assertIsInstance(summary[field], str)
                self.assertTrue(summary[field].strip())
        self.assertIn("precondition check", summary["visible_difference"])
        self.assertIn("not changed real behavior", summary["plain_result"])

    def test_invalid_sources_return_none(self):
        contrast = self._valid_contrast()
        evidence = self._valid_evidence()
        experience = self._valid_experience()

        bad_contrast = deepcopy(contrast)
        bad_contrast["blocked_flags"]["memory_write"] = True
        self.assertIsNone(build_demo_readable_before_after_report(bad_contrast, evidence, experience))

        bad_evidence = deepcopy(evidence)
        bad_evidence["blocked_flags"]["memory_write"] = True
        self.assertIsNone(build_demo_readable_before_after_report(contrast, bad_evidence, experience))

        bad_experience = deepcopy(experience)
        bad_experience["blocked_flags"]["memory_write"] = True
        self.assertIsNone(build_demo_readable_before_after_report(contrast, evidence, bad_experience))

    def test_mismatched_source_links_return_none(self):
        contrast = self._valid_contrast()
        evidence = self._valid_evidence()
        experience = self._valid_experience()
        evidence["source_contrast_id"] = "other_contrast"
        self.assertIsNone(build_demo_readable_before_after_report(contrast, evidence, experience))

        evidence = self._valid_evidence()
        experience["source_evidence_trace_id"] = "other_evidence"
        self.assertIsNone(build_demo_readable_before_after_report(contrast, evidence, experience))

    def test_trace_only_false_blocks(self):
        record = self._valid_record()
        record["trace_only"] = False
        self._assert_invalid(record, "trace_only_not_true")

    def test_empty_human_summary_fields_block(self):
        cases = {
            "before": "human_summary_before_empty",
            "after": "human_summary_after_empty",
            "visible_difference": "human_summary_visible_difference_empty",
        }
        for field, error_code in cases.items():
            with self.subTest(field=field):
                record = self._valid_record()
                record["human_summary"][field] = ""
                self._assert_invalid(record, error_code)

    def test_claim_limits_true_block(self):
        cases = {
            "learning_claim": "learning_claim_enabled",
            "behavior_change_claim": "behavior_change_claim_enabled",
            "retention_claim": "retention_claim_enabled",
            "memory_write_claim": "memory_write_claim_enabled",
            "proof_of_learning_claim": "proof_of_learning_claim_enabled",
        }
        for field, error_code in cases.items():
            with self.subTest(field=field):
                record = self._valid_record()
                record["claim_limits"][field] = True
                self._assert_invalid(record, error_code)

    def test_blocked_flags_true_block(self):
        cases = {
            "memory_write": "memory_write_enabled",
            "lesson_retained": "lesson_retained_enabled",
        }
        for flag, error_code in cases.items():
            with self.subTest(flag=flag):
                record = self._valid_record()
                record["blocked_flags"][flag] = True
                self._assert_invalid(record, error_code)

    def test_demo_summary_counts_are_deterministic(self):
        result = run_demo_readable_before_after_report_minimal_check()
        summary = result["summary"]
        human_summary = result["valid_human_summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-demo-readable-before-after-report-minimal-check")
        self.assertEqual(result["flow"], "demo_readable_before_after_report_minimal_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["demo_readable_report_count"], 11)
        self.assertEqual(summary["valid_demo_readable_report_count"], 1)
        self.assertEqual(summary["invalid_demo_readable_report_count"], 10)
        self.assertEqual(summary["empty_before_blocked_count"], 1)
        self.assertEqual(summary["empty_after_blocked_count"], 1)
        self.assertEqual(summary["empty_visible_difference_blocked_count"], 1)
        self.assertEqual(summary["trace_only_false_blocked_count"], 1)
        self.assertEqual(summary["learning_claim_blocked_count"], 1)
        self.assertEqual(summary["behavior_change_claim_blocked_count"], 1)
        self.assertEqual(summary["retention_claim_blocked_count"], 1)
        self.assertEqual(summary["memory_write_blocked_count"], 1)
        self.assertEqual(summary["lesson_retained_blocked_count"], 1)
        self.assertEqual(summary["proof_of_learning_claim_blocked_count"], 1)
        for field in [
            "learning_claim_count",
            "behavior_change_claim_count",
            "retention_claim_count",
            "memory_write_count",
            "lesson_retained_count",
            "proof_of_learning_claim_count",
        ]:
            with self.subTest(field=field):
                self.assertEqual(summary[field], 0)
        self.assertTrue(human_summary["before"])
        self.assertTrue(human_summary["after"])
        self.assertTrue(human_summary["visible_difference"])
        self.assertTrue(human_summary["plain_result"])
        self.assertTrue(boundary["trace_only"])
        self.assertTrue(boundary["human_readable_only"])
        self.assertEqual(boundary["top_level_field_count"], 8)
        self.assertFalse(boundary["lesson_application_added"])
        self.assertFalse(boundary["runtime_action_selection_added"])
        self.assertFalse(boundary["action_behavior_change_added"])
        self.assertFalse(boundary["memory_write_added"])
        self.assertFalse(boundary["lesson_retention_added"])
        self.assertFalse(boundary["proof_of_learning_claimed"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-demo-readable-before-after-report-minimal-check")

        self.assertEqual(result["command"], "run-demo-readable-before-after-report-minimal-check")
        self.assertEqual(result["summary"]["valid_demo_readable_report_count"], 1)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-demo-readable-before-after-report-minimal-check",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-demo-readable-before-after-report-minimal-check")
        self.assertEqual(result["summary"]["demo_readable_report_count"], 11)
        self.assertTrue(result["valid_human_summary"]["visible_difference"])

    def _assert_invalid(self, record, error_code):
        validation = validate_demo_readable_before_after_report(record)

        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])


if __name__ == "__main__":
    unittest.main()
