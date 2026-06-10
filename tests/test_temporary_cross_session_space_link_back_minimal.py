import json
import subprocess
import sys
import unittest
from copy import deepcopy

from ashl_core.temporary_cross_session_experience_space_minimal import (
    run_temporary_cross_session_experience_space_minimal_check,
)
from ashl_core.temporary_cross_session_space_link_back_minimal import (
    build_trial_bucket_link_preview_from_temporary_space,
    run_temporary_cross_session_space_link_back_minimal_check,
    validate_space_link_back_result,
)
from ashl_core.teaching_cli import run_command
from ashl_core.trial_bucket_link_preview_minimal import (
    build_new_demo_trial_trace,
    validate_trial_bucket_link_preview,
)


EXPECTED_NOT_MATCHED_FIELDS = {
    "link_back_id",
    "source_trial_trace_id",
    "source_temporary_space_id",
    "query_exact_key",
    "match_result",
    "trace_only",
    "blocked_flags",
}


class TemporaryCrossSessionSpaceLinkBackMinimalTests(unittest.TestCase):
    def _valid_space(self):
        result = run_temporary_cross_session_experience_space_minimal_check()
        return deepcopy(
            next(
                record
                for record, validation in zip(
                    result["temporary_spaces"],
                    result["validation_results"],
                )
                if validation["valid"]
            )
        )

    def _not_matched_record(self):
        space = self._valid_space()
        trial = build_new_demo_trial_trace("action_intent_id:intent_demo_new_002|no_prior_candidate:true")
        trial["trial_trace_id"] = "trial_demo_new_002"
        record = build_trial_bucket_link_preview_from_temporary_space(trial, space)
        self.assertIsNotNone(record)
        return record

    def test_same_exact_key_query_from_temporary_space_creates_matched_link_back(self):
        space = self._valid_space()
        trial = build_new_demo_trial_trace(space["records"][0]["exact_key"])
        before = (deepcopy(trial), deepcopy(space))
        record = build_trial_bucket_link_preview_from_temporary_space(trial, space)
        validation = validate_trial_bucket_link_preview(record)

        self.assertEqual((trial, space), before)
        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertTrue(record["match_result"]["matched"])
        self.assertTrue(record["match_result"]["candidate_available"])
        self.assertEqual(record["source_trial_trace_id"], trial["trial_trace_id"])
        self.assertEqual(record["source_experience_record_id"], space["records"][0]["experience_record_id"])
        self.assertEqual(record["match_result"]["match_scope"], "same_exact_key_only")

    def test_matched_result_can_produce_valid_trial_bucket_link_preview(self):
        result = run_temporary_cross_session_space_link_back_minimal_check()
        validation = result["trial_bucket_link_preview_validation"]

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(result["summary"]["valid_trial_bucket_link_preview_from_space_count"], 1)

    def test_different_exact_key_creates_not_matched_link_back(self):
        record = self._not_matched_record()
        validation = validate_space_link_back_result(record)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(set(record), EXPECTED_NOT_MATCHED_FIELDS)
        self.assertFalse(record["match_result"]["matched"])
        self.assertEqual(record["match_result"]["matched_record_ids"], [])
        self.assertEqual(record["match_result"]["match_scope"], "same_exact_key_only")
        self.assertTrue(record["trace_only"])

    def test_invalid_temporary_space_returns_none(self):
        space = self._valid_space()
        trial = build_new_demo_trial_trace(space["records"][0]["exact_key"])
        space["trace_only"] = False

        self.assertIsNone(build_trial_bucket_link_preview_from_temporary_space(trial, space))

    def test_trace_only_false_blocks(self):
        record = self._not_matched_record()
        record["trace_only"] = False
        self._assert_invalid(record, "trace_only_not_true")

    def test_match_scope_other_than_same_exact_key_only_blocks(self):
        record = self._not_matched_record()
        record["match_result"]["match_scope"] = "semantic_similarity"
        self._assert_invalid(record, "match_scope_not_same_exact_key_only")

    def test_blocked_flags_true_block(self):
        cases = {
            "memory_read": "memory_read_enabled",
            "memory_write": "memory_write_enabled",
            "lesson_retained": "lesson_retained_enabled",
            "lesson_applied": "lesson_applied_enabled",
            "history_runtime_write": "history_runtime_write_enabled",
            "action_selection_influence": "action_selection_influence_enabled",
            "action_behavior_changed": "action_behavior_changed_enabled",
            "proof_of_learning_claim": "proof_of_learning_claim_enabled",
        }
        for flag, error_code in cases.items():
            with self.subTest(flag=flag):
                record = self._not_matched_record()
                record["blocked_flags"][flag] = True
                self._assert_invalid(record, error_code)

    def test_deprecated_by_future_memory_false_blocks_in_demo(self):
        result = run_temporary_cross_session_space_link_back_minimal_check()

        self.assertEqual(result["summary"]["deprecated_by_future_memory_false_blocked_count"], 1)

    def test_demo_summary_counts_are_deterministic(self):
        result = run_temporary_cross_session_space_link_back_minimal_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-temporary-cross-session-space-link-back-minimal-check")
        self.assertEqual(result["flow"], "temporary_cross_session_space_link_back_minimal_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["space_link_back_result_count"], 10)
        self.assertEqual(summary["matched_link_back_count"], 1)
        self.assertEqual(summary["not_matched_link_back_count"], 1)
        self.assertEqual(summary["valid_trial_bucket_link_preview_from_space_count"], 1)
        self.assertEqual(summary["invalid_link_back_count"], 11)
        self.assertEqual(summary["trace_only_false_blocked_count"], 1)
        self.assertEqual(summary["deprecated_by_future_memory_false_blocked_count"], 1)
        self.assertEqual(summary["match_scope_blocked_count"], 1)
        self.assertEqual(summary["memory_read_blocked_count"], 1)
        self.assertEqual(summary["memory_write_blocked_count"], 1)
        self.assertEqual(summary["lesson_retained_blocked_count"], 1)
        self.assertEqual(summary["lesson_applied_blocked_count"], 1)
        self.assertEqual(summary["history_runtime_write_blocked_count"], 1)
        self.assertEqual(summary["action_selection_influence_blocked_count"], 1)
        self.assertEqual(summary["action_behavior_changed_blocked_count"], 1)
        self.assertEqual(summary["proof_of_learning_claim_blocked_count"], 1)
        for field in [
            "memory_read_count",
            "memory_write_count",
            "lesson_retained_count",
            "lesson_applied_count",
            "history_runtime_write_count",
            "persistent_rule_write_count",
            "action_selection_influence_count",
            "action_behavior_changed_count",
            "predictor_modified_count",
            "proof_of_learning_claim_count",
        ]:
            with self.subTest(field=field):
                self.assertEqual(summary[field], 0)
        self.assertTrue(boundary["trace_only"])
        self.assertTrue(boundary["same_exact_key_only"])
        self.assertTrue(boundary["temporary_space_deprecated_by_future_memory"])
        self.assertFalse(boundary["real_memory_read_added"])
        self.assertFalse(boundary["real_memory_write_added"])
        self.assertFalse(boundary["lesson_retention_added"])
        self.assertFalse(boundary["lesson_application_added"])
        self.assertFalse(boundary["history_runtime_added"])
        self.assertFalse(boundary["semantic_similarity_added"])
        self.assertFalse(boundary["fuzzy_matching_added"])
        self.assertFalse(boundary["vector_retrieval_added"])
        self.assertFalse(boundary["predictor_mutation_added"])
        self.assertFalse(boundary["proof_of_learning_claimed"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-temporary-cross-session-space-link-back-minimal-check")

        self.assertEqual(result["command"], "run-temporary-cross-session-space-link-back-minimal-check")
        self.assertEqual(result["summary"]["matched_link_back_count"], 1)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-temporary-cross-session-space-link-back-minimal-check",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-temporary-cross-session-space-link-back-minimal-check")
        self.assertEqual(result["summary"]["matched_link_back_count"], 1)
        self.assertEqual(result["summary"]["not_matched_link_back_count"], 1)

    def _assert_invalid(self, record, error_code):
        validation = validate_space_link_back_result(record)

        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])


if __name__ == "__main__":
    unittest.main()
