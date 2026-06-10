import json
import subprocess
import sys
import unittest
from copy import deepcopy

from ashl_core.generalized_memory_exact_key_bucket_enhancement_minimal import (
    build_exact_key_bucket_candidate,
    run_generalized_memory_exact_key_bucket_enhancement_minimal_check,
    validate_exact_key_bucket_candidate,
)
from ashl_core.lesson_effect_evidence_trace_minimal import run_lesson_effect_evidence_trace_minimal_check
from ashl_core.teaching_cli import run_command


EXPECTED_FIELDS = {
    "bucket_candidate_id",
    "source_evidence_trace_id",
    "exact_key",
    "match_scope",
    "trace_only",
    "bucket_summary",
    "blocked_flags",
}


class GeneralizedMemoryExactKeyBucketEnhancementMinimalTests(unittest.TestCase):
    def _valid_evidence_trace(self):
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

    def _valid_record(self):
        record = build_exact_key_bucket_candidate(self._valid_evidence_trace())
        self.assertIsNotNone(record)
        return record

    def test_valid_lesson_effect_evidence_trace_creates_valid_bucket_candidate(self):
        evidence = self._valid_evidence_trace()
        evidence_before = deepcopy(evidence)
        record = build_exact_key_bucket_candidate(evidence)
        validation = validate_exact_key_bucket_candidate(record)

        self.assertEqual(evidence, evidence_before)
        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(record["source_evidence_trace_id"], evidence["evidence_trace_id"])
        self.assertIn("action_intent_id:intent_demo_001", record["exact_key"])
        self.assertIn("evidence_type:trace_level_difference", record["exact_key"])
        self.assertEqual(record["match_scope"], "exact_key_only")
        self.assertTrue(record["trace_only"])
        self.assertEqual(record["bucket_summary"]["evidence_count"], 1)
        self.assertEqual(record["bucket_summary"]["visible_trace_difference_count"], 1)
        self.assertEqual(record["bucket_summary"]["reusable_hint"], "same_exact_key_only")

    def test_record_has_only_expected_top_level_fields(self):
        record = self._valid_record()

        self.assertEqual(set(record), EXPECTED_FIELDS)
        self.assertEqual(len(record), 7)

    def test_invalid_lesson_effect_evidence_trace_returns_none(self):
        evidence = self._valid_evidence_trace()
        evidence["blocked_flags"]["memory_write"] = True

        self.assertIsNone(build_exact_key_bucket_candidate(evidence))

    def test_empty_exact_key_blocks(self):
        record = self._valid_record()
        record["exact_key"] = ""
        self._assert_invalid(record, "exact_key_empty_or_not_string")

    def test_match_scope_other_than_exact_key_only_blocks(self):
        record = self._valid_record()
        record["match_scope"] = "semantic_similarity"
        self._assert_invalid(record, "match_scope_not_exact_key_only")

    def test_trace_only_false_blocks(self):
        record = self._valid_record()
        record["trace_only"] = False
        self._assert_invalid(record, "trace_only_not_true")

    def test_blocked_flags_true_block(self):
        cases = {
            "memory_write": "memory_write_enabled",
            "lesson_retained": "lesson_retained_enabled",
            "history_runtime_write": "history_runtime_write_enabled",
            "persistent_rule_write": "persistent_rule_write_enabled",
            "predictor_modified": "predictor_modified_enabled",
            "action_behavior_changed": "action_behavior_changed_enabled",
            "proof_of_learning_claim": "proof_of_learning_claim_enabled",
        }
        for flag, error_code in cases.items():
            with self.subTest(flag=flag):
                record = self._valid_record()
                record["blocked_flags"][flag] = True
                self._assert_invalid(record, error_code)

    def test_demo_summary_counts_are_deterministic(self):
        result = run_generalized_memory_exact_key_bucket_enhancement_minimal_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(
            result["command"],
            "run-generalized-memory-exact-key-bucket-enhancement-minimal-check",
        )
        self.assertEqual(result["flow"], "generalized_memory_exact_key_bucket_enhancement_minimal_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["bucket_candidate_count"], 11)
        self.assertEqual(summary["valid_bucket_candidate_count"], 1)
        self.assertEqual(summary["invalid_bucket_candidate_count"], 10)
        self.assertEqual(summary["empty_exact_key_blocked_count"], 1)
        self.assertEqual(summary["match_scope_blocked_count"], 1)
        self.assertEqual(summary["trace_only_false_blocked_count"], 1)
        self.assertEqual(summary["memory_write_blocked_count"], 1)
        self.assertEqual(summary["lesson_retained_blocked_count"], 1)
        self.assertEqual(summary["history_runtime_write_blocked_count"], 1)
        self.assertEqual(summary["persistent_rule_write_blocked_count"], 1)
        self.assertEqual(summary["predictor_modified_blocked_count"], 1)
        self.assertEqual(summary["action_behavior_changed_blocked_count"], 1)
        self.assertEqual(summary["proof_of_learning_claim_blocked_count"], 1)
        for field in [
            "memory_write_count",
            "lesson_retained_count",
            "history_runtime_write_count",
            "persistent_rule_write_count",
            "predictor_modified_count",
            "action_behavior_changed_count",
            "proof_of_learning_claim_count",
        ]:
            with self.subTest(field=field):
                self.assertEqual(summary[field], 0)
        self.assertTrue(boundary["trace_only"])
        self.assertTrue(boundary["minimal_record_shape"])
        self.assertEqual(boundary["top_level_field_count"], 7)
        self.assertTrue(boundary["exact_key_only"])
        self.assertFalse(boundary["memory_write_added"])
        self.assertFalse(boundary["lesson_retention_added"])
        self.assertFalse(boundary["lesson_store_write_added"])
        self.assertFalse(boundary["history_runtime_added"])
        self.assertFalse(boundary["persistent_learning_added"])
        self.assertFalse(boundary["persistent_rule_write_added"])
        self.assertFalse(boundary["vector_search_added"])
        self.assertFalse(boundary["semantic_similarity_added"])
        self.assertFalse(boundary["embedding_retrieval_added"])
        self.assertFalse(boundary["fuzzy_matching_added"])
        self.assertFalse(boundary["predictor_mutation_added"])
        self.assertFalse(boundary["runtime_action_selection_added"])
        self.assertFalse(boundary["action_behavior_change_added"])
        self.assertFalse(boundary["proof_of_learning_claimed"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-generalized-memory-exact-key-bucket-enhancement-minimal-check")

        self.assertEqual(
            result["command"],
            "run-generalized-memory-exact-key-bucket-enhancement-minimal-check",
        )
        self.assertEqual(result["summary"]["valid_bucket_candidate_count"], 1)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-generalized-memory-exact-key-bucket-enhancement-minimal-check",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(
            result["command"],
            "run-generalized-memory-exact-key-bucket-enhancement-minimal-check",
        )
        self.assertEqual(result["summary"]["bucket_candidate_count"], 11)

    def _assert_invalid(self, record, error_code):
        validation = validate_exact_key_bucket_candidate(record)

        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])


if __name__ == "__main__":
    unittest.main()
