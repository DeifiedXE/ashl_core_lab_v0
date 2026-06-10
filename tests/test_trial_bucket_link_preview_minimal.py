import json
import subprocess
import sys
import unittest
from copy import deepcopy

from ashl_core.generalized_memory_exact_key_bucket_enhancement_minimal import (
    run_generalized_memory_exact_key_bucket_enhancement_minimal_check,
)
from ashl_core.session_experience_record_schema_minimal import (
    run_session_experience_record_schema_minimal_check,
)
from ashl_core.teaching_cli import run_command
from ashl_core.trial_bucket_link_preview_minimal import (
    build_new_demo_trial_trace,
    build_trial_bucket_link_preview,
    run_trial_bucket_link_preview_minimal_check,
    validate_trial_bucket_link_preview,
)


EXPECTED_FIELDS = {
    "link_preview_id",
    "source_trial_trace_id",
    "source_bucket_candidate_id",
    "source_experience_record_id",
    "exact_key",
    "match_result",
    "trace_only",
    "blocked_flags",
}


class TrialBucketLinkPreviewMinimalTests(unittest.TestCase):
    def _valid_bucket_candidate(self):
        result = run_generalized_memory_exact_key_bucket_enhancement_minimal_check()
        return deepcopy(
            next(
                record
                for record, validation in zip(
                    result["bucket_candidates"],
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
        bucket = self._valid_bucket_candidate()
        record = build_trial_bucket_link_preview(
            build_new_demo_trial_trace(bucket["exact_key"]),
            bucket,
            self._valid_experience(),
        )
        self.assertIsNotNone(record)
        return record

    def test_same_exact_key_creates_matched_link_preview(self):
        bucket = self._valid_bucket_candidate()
        experience = self._valid_experience()
        trial = build_new_demo_trial_trace(bucket["exact_key"])
        before = (deepcopy(trial), deepcopy(bucket), deepcopy(experience))
        record = build_trial_bucket_link_preview(trial, bucket, experience)
        validation = validate_trial_bucket_link_preview(record)

        self.assertEqual((trial, bucket, experience), before)
        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(record["source_trial_trace_id"], trial["trial_trace_id"])
        self.assertEqual(record["source_bucket_candidate_id"], bucket["bucket_candidate_id"])
        self.assertEqual(record["source_experience_record_id"], experience["experience_record_id"])
        self.assertEqual(record["exact_key"], bucket["exact_key"])
        self.assertTrue(record["match_result"]["matched"])
        self.assertTrue(record["match_result"]["candidate_available"])
        self.assertEqual(record["match_result"]["match_scope"], "same_exact_key_only")

    def test_different_exact_key_creates_valid_not_matched_preview(self):
        bucket = self._valid_bucket_candidate()
        trial = build_new_demo_trial_trace("action_intent_id:intent_demo_new_002|no_prior_candidate:true")
        record = build_trial_bucket_link_preview(trial, bucket, self._valid_experience())
        validation = validate_trial_bucket_link_preview(record)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertFalse(record["match_result"]["matched"])
        self.assertFalse(record["match_result"]["candidate_available"])
        self.assertEqual(record["match_result"]["match_scope"], "same_exact_key_only")

    def test_record_has_only_expected_top_level_fields(self):
        record = self._valid_record()

        self.assertEqual(set(record), EXPECTED_FIELDS)
        self.assertEqual(len(record), 8)

    def test_invalid_sources_return_none(self):
        bucket = self._valid_bucket_candidate()
        experience = self._valid_experience()
        trial = build_new_demo_trial_trace(bucket["exact_key"])

        bad_bucket = deepcopy(bucket)
        bad_bucket["blocked_flags"]["memory_write"] = True
        self.assertIsNone(build_trial_bucket_link_preview(trial, bad_bucket, experience))

        bad_experience = deepcopy(experience)
        bad_experience["blocked_flags"]["memory_write"] = True
        self.assertIsNone(build_trial_bucket_link_preview(trial, bucket, bad_experience))

    def test_mismatched_experience_bucket_source_returns_none(self):
        bucket = self._valid_bucket_candidate()
        experience = self._valid_experience()
        experience["source_bucket_candidate_id"] = "other_bucket_candidate"

        self.assertIsNone(
            build_trial_bucket_link_preview(
                build_new_demo_trial_trace(bucket["exact_key"]),
                bucket,
                experience,
            )
        )

    def test_empty_exact_key_blocks(self):
        record = self._valid_record()
        record["exact_key"] = ""
        self._assert_invalid(record, "exact_key_empty_or_not_string")

    def test_match_scope_other_than_same_exact_key_only_blocks(self):
        record = self._valid_record()
        record["match_result"]["match_scope"] = "semantic_similarity"
        self._assert_invalid(record, "match_scope_not_same_exact_key_only")

    def test_trace_only_false_blocks(self):
        record = self._valid_record()
        record["trace_only"] = False
        self._assert_invalid(record, "trace_only_not_true")

    def test_blocked_flags_true_block(self):
        cases = {
            "memory_write": "memory_write_enabled",
            "lesson_retained": "lesson_retained_enabled",
            "lesson_applied": "lesson_applied_enabled",
            "action_selection_influence": "action_selection_influence_enabled",
            "action_behavior_changed": "action_behavior_changed_enabled",
            "history_runtime_write": "history_runtime_write_enabled",
            "predictor_modified": "predictor_modified_enabled",
            "persistent_rule_write": "persistent_rule_write_enabled",
            "proof_of_learning_claim": "proof_of_learning_claim_enabled",
        }
        for flag, error_code in cases.items():
            with self.subTest(flag=flag):
                record = self._valid_record()
                record["blocked_flags"][flag] = True
                self._assert_invalid(record, error_code)

    def test_demo_summary_counts_are_deterministic(self):
        result = run_trial_bucket_link_preview_minimal_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-trial-bucket-link-preview-minimal-check")
        self.assertEqual(result["flow"], "trial_bucket_link_preview_minimal_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["trial_bucket_link_preview_count"], 14)
        self.assertEqual(summary["valid_trial_bucket_link_preview_count"], 2)
        self.assertEqual(summary["invalid_trial_bucket_link_preview_count"], 12)
        self.assertEqual(summary["matched_link_preview_count"], 1)
        self.assertEqual(summary["not_matched_link_preview_count"], 1)
        self.assertEqual(summary["empty_exact_key_blocked_count"], 1)
        self.assertEqual(summary["match_scope_blocked_count"], 1)
        self.assertEqual(summary["trace_only_false_blocked_count"], 1)
        self.assertEqual(summary["memory_write_blocked_count"], 1)
        self.assertEqual(summary["lesson_retained_blocked_count"], 1)
        self.assertEqual(summary["lesson_applied_blocked_count"], 1)
        self.assertEqual(summary["action_selection_influence_blocked_count"], 1)
        self.assertEqual(summary["action_behavior_changed_blocked_count"], 1)
        self.assertEqual(summary["history_runtime_write_blocked_count"], 1)
        self.assertEqual(summary["predictor_modified_blocked_count"], 1)
        self.assertEqual(summary["persistent_rule_write_blocked_count"], 1)
        self.assertEqual(summary["proof_of_learning_claim_blocked_count"], 1)
        for field in [
            "memory_write_count",
            "lesson_retained_count",
            "lesson_applied_count",
            "action_selection_influence_count",
            "action_behavior_changed_count",
            "history_runtime_write_count",
            "predictor_modified_count",
            "persistent_rule_write_count",
            "proof_of_learning_claim_count",
        ]:
            with self.subTest(field=field):
                self.assertEqual(summary[field], 0)
        self.assertTrue(boundary["trace_only"])
        self.assertTrue(boundary["minimal_record_shape"])
        self.assertEqual(boundary["top_level_field_count"], 8)
        self.assertTrue(boundary["same_exact_key_only"])
        self.assertTrue(boundary["matched_preview_supported"])
        self.assertTrue(boundary["not_matched_preview_supported"])
        self.assertFalse(boundary["memory_write_added"])
        self.assertFalse(boundary["lesson_retention_added"])
        self.assertFalse(boundary["lesson_application_added"])
        self.assertFalse(boundary["runtime_action_selection_added"])
        self.assertFalse(boundary["action_behavior_change_added"])
        self.assertFalse(boundary["history_runtime_added"])
        self.assertFalse(boundary["semantic_similarity_added"])
        self.assertFalse(boundary["fuzzy_matching_added"])
        self.assertFalse(boundary["vector_retrieval_added"])
        self.assertFalse(boundary["predictor_mutation_added"])
        self.assertFalse(boundary["proof_of_learning_claimed"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-trial-bucket-link-preview-minimal-check")

        self.assertEqual(result["command"], "run-trial-bucket-link-preview-minimal-check")
        self.assertEqual(result["summary"]["valid_trial_bucket_link_preview_count"], 2)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-trial-bucket-link-preview-minimal-check",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-trial-bucket-link-preview-minimal-check")
        self.assertEqual(result["summary"]["trial_bucket_link_preview_count"], 14)
        self.assertEqual(result["summary"]["matched_link_preview_count"], 1)
        self.assertEqual(result["summary"]["not_matched_link_preview_count"], 1)

    def _assert_invalid(self, record, error_code):
        validation = validate_trial_bucket_link_preview(record)

        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])


if __name__ == "__main__":
    unittest.main()
