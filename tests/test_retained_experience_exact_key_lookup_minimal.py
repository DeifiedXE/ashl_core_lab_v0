import json
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from ashl_core.mentor_gated_experience_retention_minimal import (
    APPROVAL_PHRASE,
    append_retained_experience_jsonl,
    build_mentor_retention_decision,
    load_retained_experience_jsonl,
)
from ashl_core.retained_experience_exact_key_lookup_minimal import (
    build_retained_exact_key_lookup_preview,
    run_retained_experience_exact_key_lookup_minimal_check,
    validate_retained_exact_key_lookup_preview,
)
from ashl_core.session_experience_record_schema_minimal import (
    run_session_experience_record_schema_minimal_check,
)
from ashl_core.teaching_cli import run_command


EXPECTED_FIELDS = {
    "lookup_preview_id",
    "query_exact_key",
    "match_rule",
    "read_only",
    "match_result",
    "human_summary",
    "blocked_flags",
}

BLOCKED_FLAG_ERRORS = {
    "jsonl_append": "jsonl_append_enabled",
    "jsonl_edit": "jsonl_edit_enabled",
    "jsonl_delete": "jsonl_delete_enabled",
    "semantic_match": "semantic_match_enabled",
    "fuzzy_match": "fuzzy_match_enabled",
    "vector_match": "vector_match_enabled",
    "dry_run_injection": "dry_run_injection_enabled",
    "lesson_applied": "lesson_applied_enabled",
    "action_selection_influence": "action_selection_influence_enabled",
    "action_behavior_changed": "action_behavior_changed_enabled",
    "memory_write": "memory_write_enabled",
    "new_retention_written": "new_retention_written_enabled",
    "predictor_modified": "predictor_modified_enabled",
    "proof_of_learning_claim": "proof_of_learning_claim_enabled",
}


class RetainedExperienceExactKeyLookupMinimalTests(unittest.TestCase):
    def _valid_experience_record(self):
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

    def _retained_jsonl(self):
        record = self._valid_experience_record()
        decision = build_mentor_retention_decision(record, APPROVAL_PHRASE)
        tmp = tempfile.TemporaryDirectory()
        path = Path(tmp.name) / "retention" / "records.jsonl"
        append_retained_experience_jsonl(record, decision, path)
        return tmp, path, record

    def _valid_lookup(self):
        tmp, path, record = self._retained_jsonl()
        self.addCleanup(tmp.cleanup)
        records = load_retained_experience_jsonl(path)
        return build_retained_exact_key_lookup_preview(records, record["exact_key"])

    def test_retained_record_can_be_looked_up_by_same_exact_key(self):
        lookup = self._valid_lookup()
        validation = validate_retained_exact_key_lookup_preview(lookup)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertTrue(lookup["match_result"]["matched"])
        self.assertEqual(lookup["match_result"]["matched_count"], 1)
        self.assertEqual(len(lookup["match_result"]["matched_retained_record_ids"]), 1)

    def test_different_exact_key_returns_valid_not_matched_lookup(self):
        tmp, path, _record = self._retained_jsonl()
        self.addCleanup(tmp.cleanup)
        lookup = build_retained_exact_key_lookup_preview(
            load_retained_experience_jsonl(path),
            "action_type:turn|correction_type:other|failure_type:not_present",
        )
        validation = validate_retained_exact_key_lookup_preview(lookup)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertFalse(lookup["match_result"]["matched"])
        self.assertEqual(lookup["match_result"]["matched_count"], 0)

    def test_non_retained_record_cannot_match(self):
        tmp, path, record = self._retained_jsonl()
        self.addCleanup(tmp.cleanup)
        retained = load_retained_experience_jsonl(path)[0]
        retained["retention_status"] = "not_retained"
        lookup = build_retained_exact_key_lookup_preview([retained], record["exact_key"])

        self.assertFalse(lookup["match_result"]["matched"])
        self.assertEqual(lookup["match_result"]["matched_count"], 0)

    def test_lookup_preview_has_only_expected_top_level_fields(self):
        lookup = self._valid_lookup()

        self.assertEqual(set(lookup), EXPECTED_FIELDS)
        self.assertEqual(len(lookup), 7)

    def test_empty_query_exact_key_blocks(self):
        lookup = self._valid_lookup()
        lookup["query_exact_key"] = ""
        self._assert_invalid(lookup, "query_exact_key_empty_or_not_string")

    def test_wrong_match_rule_blocks(self):
        lookup = self._valid_lookup()
        lookup["match_rule"] = "semantic_similarity"
        self._assert_invalid(lookup, "match_rule_not_same_exact_key_only")

    def test_read_only_false_blocks(self):
        lookup = self._valid_lookup()
        lookup["read_only"] = False
        self._assert_invalid(lookup, "read_only_not_true")

    def test_matched_count_mismatch_blocks(self):
        lookup = self._valid_lookup()
        lookup["match_result"]["matched_count"] += 1
        self._assert_invalid(lookup, "matched_count_mismatch")

    def test_blocked_flags_true_block(self):
        for flag, error_code in BLOCKED_FLAG_ERRORS.items():
            with self.subTest(flag=flag):
                lookup = self._valid_lookup()
                lookup["blocked_flags"][flag] = True
                self._assert_invalid(lookup, error_code)

    def test_lookup_does_not_mutate_jsonl(self):
        tmp, path, record = self._retained_jsonl()
        self.addCleanup(tmp.cleanup)
        before = path.read_text(encoding="utf-8")
        build_retained_exact_key_lookup_preview(load_retained_experience_jsonl(path), record["exact_key"])
        after = path.read_text(encoding="utf-8")

        self.assertEqual(before, after)

    def test_demo_summary_counts_are_deterministic(self):
        result = run_retained_experience_exact_key_lookup_minimal_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-retained-experience-exact-key-lookup-minimal-check")
        self.assertEqual(result["flow"], "retained_experience_exact_key_lookup_minimal_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["lookup_preview_count"], 20)
        self.assertEqual(summary["valid_lookup_preview_count"], 2)
        self.assertEqual(summary["invalid_lookup_preview_count"], 18)
        self.assertEqual(summary["matched_lookup_count"], 1)
        self.assertEqual(summary["not_matched_lookup_count"], 1)
        self.assertEqual(summary["retained_record_source_count"], 1)
        self.assertEqual(summary["empty_query_exact_key_blocked_count"], 1)
        self.assertEqual(summary["match_rule_blocked_count"], 1)
        self.assertEqual(summary["read_only_false_blocked_count"], 1)
        self.assertEqual(summary["matched_count_mismatch_blocked_count"], 1)
        for field in BLOCKED_FLAG_ERRORS:
            self.assertEqual(summary[f"{field}_blocked_count"], 1)
            self.assertEqual(summary[f"{field}_count"], 0)
        self.assertFalse(summary["lookup_mutated_jsonl"])
        self.assertTrue(boundary["read_only"])
        self.assertTrue(boundary["same_exact_key_only"])
        self.assertEqual(boundary["top_level_field_count"], 7)
        self.assertFalse(boundary["production_write_cli_added"])
        self.assertFalse(boundary["production_lookup_cli_added"])
        self.assertFalse(boundary["semantic_retrieval_added"])
        self.assertFalse(boundary["fuzzy_retrieval_added"])
        self.assertFalse(boundary["vector_retrieval_added"])
        self.assertFalse(boundary["dry_run_injection_added"])
        self.assertFalse(boundary["lesson_application_added"])
        self.assertFalse(boundary["runtime_action_selection_added"])
        self.assertFalse(boundary["action_behavior_change_added"])
        self.assertFalse(boundary["memory_write_added"])
        self.assertFalse(boundary["new_retention_write_added"])
        self.assertFalse(boundary["predictor_mutation_added"])
        self.assertFalse(boundary["proof_of_learning_claimed"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-retained-experience-exact-key-lookup-minimal-check")

        self.assertEqual(result["command"], "run-retained-experience-exact-key-lookup-minimal-check")
        self.assertEqual(result["summary"]["valid_lookup_preview_count"], 2)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-retained-experience-exact-key-lookup-minimal-check",
            ],
            check=True,
            capture_output=True,
            encoding="utf-8",
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-retained-experience-exact-key-lookup-minimal-check")
        self.assertEqual(result["summary"]["lookup_preview_count"], 20)

    def _assert_invalid(self, lookup, error_code):
        validation = validate_retained_exact_key_lookup_preview(lookup)

        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])


if __name__ == "__main__":
    unittest.main()
