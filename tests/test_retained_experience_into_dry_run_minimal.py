import json
import subprocess
import sys
import unittest
from copy import deepcopy

from ashl_core.retained_experience_exact_key_lookup_minimal import (
    run_retained_experience_exact_key_lookup_minimal_check,
)
from ashl_core.retained_experience_into_dry_run_minimal import (
    build_retained_experience_dry_run_context,
    run_retained_experience_into_dry_run_minimal_check,
    validate_retained_experience_dry_run_context,
)
from ashl_core.teaching_cli import run_command


EXPECTED_FIELDS = {
    "dry_run_context_id",
    "source_lookup_preview_id",
    "source_trial_intent_id",
    "context_status",
    "trace_only",
    "human_summary",
    "blocked_flags",
}

BLOCKED_FLAG_ERRORS = {
    "lesson_applied": "lesson_applied_enabled",
    "runtime_action_selection": "runtime_action_selection_enabled",
    "action_selection_influence": "action_selection_influence_enabled",
    "action_behavior_changed": "action_behavior_changed_enabled",
    "memory_write": "memory_write_enabled",
    "new_retention_written": "new_retention_written_enabled",
    "semantic_match": "semantic_match_enabled",
    "fuzzy_match": "fuzzy_match_enabled",
    "vector_match": "vector_match_enabled",
    "predictor_modified": "predictor_modified_enabled",
    "proof_of_learning_claim": "proof_of_learning_claim_enabled",
}


class RetainedExperienceIntoDryRunMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        lookup_result = run_retained_experience_exact_key_lookup_minimal_check()
        cls.matched_lookup = next(
            lookup
            for lookup, validation in zip(
                lookup_result["retained_exact_key_lookup_previews"],
                lookup_result["validation_results"],
            )
            if validation["valid"] and lookup["match_result"]["matched"] is True
        )
        cls.not_matched_lookup = next(
            lookup
            for lookup, validation in zip(
                lookup_result["retained_exact_key_lookup_previews"],
                lookup_result["validation_results"],
            )
            if validation["valid"] and lookup["match_result"]["matched"] is False
        )

    def _valid_context(self):
        return build_retained_experience_dry_run_context(self.matched_lookup)

    def test_matched_lookup_creates_retained_dry_run_context(self):
        context = build_retained_experience_dry_run_context(self.matched_lookup)
        validation = validate_retained_experience_dry_run_context(context)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertTrue(context["context_status"]["retained_context_available"])
        self.assertEqual(context["context_status"]["matched_retained_record_count"], 1)

    def test_not_matched_lookup_creates_retained_dry_run_context(self):
        context = build_retained_experience_dry_run_context(self.not_matched_lookup)
        validation = validate_retained_experience_dry_run_context(context)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertFalse(context["context_status"]["retained_context_available"])
        self.assertEqual(context["context_status"]["matched_retained_record_count"], 0)

    def test_invalid_lookup_does_not_create_context(self):
        lookup = deepcopy(self.matched_lookup)
        lookup["read_only"] = False

        self.assertIsNone(build_retained_experience_dry_run_context(lookup))

    def test_record_has_only_expected_top_level_fields(self):
        context = self._valid_context()

        self.assertEqual(set(context), EXPECTED_FIELDS)
        self.assertEqual(len(context), 7)

    def test_usable_for_dry_run_true_and_runtime_action_false(self):
        context = self._valid_context()

        self.assertTrue(context["context_status"]["usable_for_dry_run"])
        self.assertFalse(context["context_status"]["usable_for_runtime_action"])

    def test_trace_only_false_blocks(self):
        context = self._valid_context()
        context["trace_only"] = False
        self._assert_invalid(context, "trace_only_not_true")

    def test_usable_for_dry_run_false_blocks(self):
        context = self._valid_context()
        context["context_status"]["usable_for_dry_run"] = False
        self._assert_invalid(context, "usable_for_dry_run_not_true")

    def test_usable_for_runtime_action_true_blocks(self):
        context = self._valid_context()
        context["context_status"]["usable_for_runtime_action"] = True
        self._assert_invalid(context, "usable_for_runtime_action_not_false")

    def test_missing_source_lookup_preview_id_blocks(self):
        context = self._valid_context()
        context["source_lookup_preview_id"] = ""
        self._assert_invalid(context, "source_lookup_preview_id_missing")

    def test_empty_lookup_result_blocks(self):
        context = self._valid_context()
        context["human_summary"]["lookup_result"] = ""
        self._assert_invalid(context, "lookup_result_empty_or_not_string")

    def test_empty_plain_result_blocks(self):
        context = self._valid_context()
        context["human_summary"]["plain_result"] = ""
        self._assert_invalid(context, "plain_result_empty_or_not_string")

    def test_blocked_flags_true_block(self):
        for flag, error_code in BLOCKED_FLAG_ERRORS.items():
            with self.subTest(flag=flag):
                context = self._valid_context()
                context["blocked_flags"][flag] = True
                self._assert_invalid(context, error_code)

    def test_demo_summary_counts_are_deterministic(self):
        result = run_retained_experience_into_dry_run_minimal_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-retained-experience-into-dry-run-minimal-check")
        self.assertEqual(result["flow"], "retained_experience_into_dry_run_minimal_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["retained_dry_run_context_count"], 19)
        self.assertEqual(summary["valid_retained_dry_run_context_count"], 2)
        self.assertEqual(summary["invalid_retained_dry_run_context_count"], 17)
        self.assertEqual(summary["matched_context_count"], 1)
        self.assertEqual(summary["not_matched_context_count"], 1)
        self.assertEqual(summary["trace_only_false_blocked_count"], 1)
        self.assertEqual(summary["usable_for_dry_run_false_blocked_count"], 1)
        self.assertEqual(summary["usable_for_runtime_action_blocked_count"], 1)
        self.assertEqual(summary["missing_source_lookup_preview_blocked_count"], 1)
        self.assertEqual(summary["empty_lookup_result_blocked_count"], 1)
        self.assertEqual(summary["empty_plain_result_blocked_count"], 1)
        for field in BLOCKED_FLAG_ERRORS:
            self.assertEqual(summary[f"{field}_blocked_count"], 1)
            self.assertEqual(summary[f"{field}_count"], 0)
        self.assertTrue(boundary["trace_only"])
        self.assertTrue(boundary["dry_run_preview_only"])
        self.assertEqual(boundary["top_level_field_count"], 7)
        self.assertTrue(boundary["uses_retained_experience_exact_key_lookup_minimal"])
        self.assertTrue(boundary["references_reviewed_lesson_dry_run_correction_minimal"])
        self.assertTrue(boundary["references_dry_run_correction_into_trial_trace"])
        self.assertFalse(boundary["retained_context_injected_into_existing_dry_run_flows"])
        self.assertFalse(boundary["usable_for_runtime_action"])
        self.assertFalse(boundary["lesson_application_added"])
        self.assertFalse(boundary["runtime_action_selection_added"])
        self.assertFalse(boundary["action_behavior_change_added"])
        self.assertFalse(boundary["memory_write_added"])
        self.assertFalse(boundary["new_retention_write_added"])
        self.assertFalse(boundary["semantic_retrieval_added"])
        self.assertFalse(boundary["fuzzy_retrieval_added"])
        self.assertFalse(boundary["vector_retrieval_added"])
        self.assertFalse(boundary["predictor_mutation_added"])
        self.assertFalse(boundary["proof_of_learning_claimed"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-retained-experience-into-dry-run-minimal-check")

        self.assertEqual(result["command"], "run-retained-experience-into-dry-run-minimal-check")
        self.assertEqual(result["summary"]["valid_retained_dry_run_context_count"], 2)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-retained-experience-into-dry-run-minimal-check",
            ],
            check=True,
            capture_output=True,
            encoding="utf-8",
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-retained-experience-into-dry-run-minimal-check")
        self.assertEqual(result["summary"]["retained_dry_run_context_count"], 19)

    def _assert_invalid(self, context, error_code):
        validation = validate_retained_experience_dry_run_context(context)

        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])


if __name__ == "__main__":
    unittest.main()
