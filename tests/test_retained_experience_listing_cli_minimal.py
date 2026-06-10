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
from ashl_core.retained_experience_listing_cli_minimal import (
    build_retained_experience_listing,
    run_retained_experience_listing_cli_minimal_check,
    validate_retained_experience_listing,
)
from ashl_core.session_experience_record_schema_minimal import (
    run_session_experience_record_schema_minimal_check,
)
from ashl_core.teaching_cli import run_command


EXPECTED_FIELDS = {
    "listing_id",
    "record_count",
    "records",
    "read_only",
    "summary",
    "blocked_flags",
}

EXPECTED_LISTED_RECORD_FIELDS = {
    "retained_record_id",
    "source_experience_record_id",
    "exact_key",
    "experience_type",
    "retention_status",
}


class RetainedExperienceListingCliMinimalTests(unittest.TestCase):
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
        return tmp, path

    def _valid_listing(self):
        tmp, path = self._retained_jsonl()
        self.addCleanup(tmp.cleanup)
        return build_retained_experience_listing(load_retained_experience_jsonl(path))

    def test_retained_jsonl_records_can_be_listed_read_only(self):
        listing = self._valid_listing()
        validation = validate_retained_experience_listing(listing)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(listing["record_count"], 1)
        self.assertTrue(listing["read_only"])
        self.assertTrue(listing["summary"]["has_records"])
        self.assertEqual(listing["summary"]["listing_scope"], "retained_jsonl_records_only")

    def test_empty_missing_jsonl_produces_safe_empty_listing(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            records = load_retained_experience_jsonl(Path(tmp_dir) / "missing.jsonl")
            listing = build_retained_experience_listing(records)
            validation = validate_retained_experience_listing(listing)

            self.assertTrue(validation["valid"], validation["error_codes"])
            self.assertEqual(listing["record_count"], 0)
            self.assertEqual(listing["records"], [])
            self.assertFalse(listing["summary"]["has_records"])

    def test_listing_has_only_expected_top_level_fields(self):
        listing = self._valid_listing()

        self.assertEqual(set(listing), EXPECTED_FIELDS)
        self.assertEqual(len(listing), 6)

    def test_listed_records_have_minimal_fields_only(self):
        listing = self._valid_listing()

        self.assertEqual(set(listing["records"][0]), EXPECTED_LISTED_RECORD_FIELDS)
        self.assertEqual(len(listing["records"][0]), 5)
        self.assertNotIn("source_snapshot", listing["records"][0])

    def test_record_count_mismatch_blocks(self):
        listing = self._valid_listing()
        listing["record_count"] = 2
        self._assert_invalid(listing, "record_count_mismatch")

    def test_read_only_false_blocks(self):
        listing = self._valid_listing()
        listing["read_only"] = False
        self._assert_invalid(listing, "read_only_not_true")

    def test_listed_retention_status_not_retained_blocks(self):
        listing = self._valid_listing()
        listing["records"][0]["retention_status"] = "not_retained"
        self._assert_invalid(listing, "listed_retention_status_not_retained")

    def test_blocked_flags_true_block(self):
        cases = {
            "jsonl_append": "jsonl_append_enabled",
            "jsonl_edit": "jsonl_edit_enabled",
            "jsonl_delete": "jsonl_delete_enabled",
            "lesson_applied": "lesson_applied_enabled",
            "action_selection_influence": "action_selection_influence_enabled",
            "action_behavior_changed": "action_behavior_changed_enabled",
            "predictor_modified": "predictor_modified_enabled",
            "automatic_retention": "automatic_retention_enabled",
            "proof_of_learning_claim": "proof_of_learning_claim_enabled",
        }
        for flag, error_code in cases.items():
            with self.subTest(flag=flag):
                listing = self._valid_listing()
                listing["blocked_flags"][flag] = True
                self._assert_invalid(listing, error_code)

    def test_listing_does_not_mutate_jsonl(self):
        tmp, path = self._retained_jsonl()
        self.addCleanup(tmp.cleanup)
        before = path.read_text(encoding="utf-8")
        build_retained_experience_listing(load_retained_experience_jsonl(path))
        after = path.read_text(encoding="utf-8")

        self.assertEqual(before, after)

    def test_demo_summary_counts_are_deterministic(self):
        result = run_retained_experience_listing_cli_minimal_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-retained-experience-listing-cli-minimal-check")
        self.assertEqual(result["flow"], "retained_experience_listing_cli_minimal_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["listing_count"], 14)
        self.assertEqual(summary["valid_listing_count"], 2)
        self.assertEqual(summary["invalid_listing_count"], 12)
        self.assertEqual(summary["listed_record_count"], 1)
        self.assertEqual(summary["empty_listing_count"], 1)
        self.assertEqual(summary["record_count_mismatch_blocked_count"], 1)
        self.assertEqual(summary["read_only_false_blocked_count"], 1)
        self.assertEqual(summary["retention_status_blocked_count"], 1)
        self.assertEqual(summary["jsonl_append_blocked_count"], 1)
        self.assertEqual(summary["jsonl_edit_blocked_count"], 1)
        self.assertEqual(summary["jsonl_delete_blocked_count"], 1)
        self.assertEqual(summary["lesson_applied_blocked_count"], 1)
        self.assertEqual(summary["action_selection_influence_blocked_count"], 1)
        self.assertEqual(summary["action_behavior_changed_blocked_count"], 1)
        self.assertEqual(summary["predictor_modified_blocked_count"], 1)
        self.assertEqual(summary["automatic_retention_blocked_count"], 1)
        self.assertEqual(summary["proof_of_learning_claim_blocked_count"], 1)
        self.assertFalse(summary["listing_mutated_jsonl"])
        self.assertTrue(boundary["read_only"])
        self.assertTrue(boundary["minimal_record_shape"])
        self.assertEqual(boundary["top_level_field_count"], 6)
        self.assertEqual(boundary["listed_record_field_count"], 5)
        self.assertFalse(boundary["production_write_cli_added"])
        self.assertFalse(boundary["production_listing_cli_added"])
        self.assertFalse(boundary["automatic_retention_added"])
        self.assertFalse(boundary["four_layer_memory_added"])
        self.assertFalse(boundary["lesson_application_added"])
        self.assertFalse(boundary["runtime_action_selection_added"])
        self.assertFalse(boundary["action_behavior_change_added"])
        self.assertFalse(boundary["predictor_mutation_added"])
        self.assertFalse(boundary["proof_of_learning_claimed"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-retained-experience-listing-cli-minimal-check")

        self.assertEqual(result["command"], "run-retained-experience-listing-cli-minimal-check")
        self.assertEqual(result["summary"]["valid_listing_count"], 2)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-retained-experience-listing-cli-minimal-check",
            ],
            check=True,
            capture_output=True,
            encoding="utf-8",
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-retained-experience-listing-cli-minimal-check")
        self.assertEqual(result["summary"]["listing_count"], 14)

    def _assert_invalid(self, listing, error_code):
        validation = validate_retained_experience_listing(listing)

        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])


if __name__ == "__main__":
    unittest.main()
