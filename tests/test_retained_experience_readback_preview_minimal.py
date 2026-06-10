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
from ashl_core.retained_experience_readback_preview_minimal import (
    build_retained_experience_readback_preview,
    run_retained_experience_readback_preview_minimal_check,
    validate_retained_experience_readback_preview,
)
from ashl_core.session_experience_record_schema_minimal import (
    run_session_experience_record_schema_minimal_check,
)
from ashl_core.teaching_cli import run_command


EXPECTED_FIELDS = {
    "readback_preview_id",
    "source_retained_record_id",
    "source_experience_record_id",
    "exact_key",
    "retention_status",
    "human_summary",
    "read_only",
    "blocked_flags",
}


class RetainedExperienceReadbackPreviewMinimalTests(unittest.TestCase):
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

    def _retained_record_from_temp_jsonl(self):
        record = self._valid_experience_record()
        decision = build_mentor_retention_decision(record, APPROVAL_PHRASE)
        tmp = tempfile.TemporaryDirectory()
        path = Path(tmp.name) / "retention" / "records.jsonl"
        append_retained_experience_jsonl(record, decision, path)
        retained = load_retained_experience_jsonl(path)[0]
        return tmp, path, retained

    def _valid_preview(self):
        tmp, _path, retained = self._retained_record_from_temp_jsonl()
        self.addCleanup(tmp.cleanup)
        preview = build_retained_experience_readback_preview(retained)
        self.assertIsNotNone(preview)
        return preview

    def test_retained_jsonl_record_can_be_loaded_and_previewed(self):
        tmp, path, retained = self._retained_record_from_temp_jsonl()
        self.addCleanup(tmp.cleanup)
        preview = build_retained_experience_readback_preview(retained)
        validation = validate_retained_experience_readback_preview(preview)

        self.assertTrue(path.exists())
        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(preview["source_retained_record_id"], retained["retained_record_id"])
        self.assertEqual(preview["source_experience_record_id"], retained["source_experience_record_id"])
        self.assertEqual(preview["retention_status"], "retained")
        self.assertTrue(preview["read_only"])

    def test_valid_readback_preview_has_only_expected_top_level_fields(self):
        preview = self._valid_preview()

        self.assertEqual(set(preview), EXPECTED_FIELDS)
        self.assertEqual(len(preview), 8)

    def test_human_summary_is_safe_display_only(self):
        preview = self._valid_preview()

        self.assertIn("what_was_retained", preview["human_summary"])
        self.assertIn("why_retained", preview["human_summary"])
        self.assertEqual(preview["human_summary"]["usable_as"], "readback_preview_only")
        self.assertIn(APPROVAL_PHRASE, preview["human_summary"]["why_retained"])

    def test_retention_status_not_retained_blocks(self):
        preview = self._valid_preview()
        preview["retention_status"] = "not_retained"
        self._assert_invalid(preview, "retention_status_not_retained")

    def test_read_only_false_blocks(self):
        preview = self._valid_preview()
        preview["read_only"] = False
        self._assert_invalid(preview, "read_only_not_true")

    def test_empty_exact_key_blocks(self):
        preview = self._valid_preview()
        preview["exact_key"] = ""
        self._assert_invalid(preview, "exact_key_empty_or_not_string")

    def test_usable_as_other_than_readback_preview_only_blocks(self):
        preview = self._valid_preview()
        preview["human_summary"]["usable_as"] = "action_hint"
        self._assert_invalid(preview, "usable_as_not_readback_preview_only")

    def test_blocked_flags_true_block(self):
        cases = {
            "lesson_applied": "lesson_applied_enabled",
            "action_selection_influence": "action_selection_influence_enabled",
            "action_behavior_changed": "action_behavior_changed_enabled",
            "predictor_modified": "predictor_modified_enabled",
            "automatic_retention": "automatic_retention_enabled",
            "proof_of_learning_claim": "proof_of_learning_claim_enabled",
        }
        for flag, error_code in cases.items():
            with self.subTest(flag=flag):
                preview = self._valid_preview()
                preview["blocked_flags"][flag] = True
                self._assert_invalid(preview, error_code)

    def test_build_returns_none_for_invalid_retention_status(self):
        tmp, _path, retained = self._retained_record_from_temp_jsonl()
        self.addCleanup(tmp.cleanup)
        retained["retention_status"] = "not_retained"

        self.assertIsNone(build_retained_experience_readback_preview(retained))

    def test_readback_preview_does_not_mutate_jsonl(self):
        tmp, path, retained = self._retained_record_from_temp_jsonl()
        self.addCleanup(tmp.cleanup)
        before = path.read_text(encoding="utf-8")
        build_retained_experience_readback_preview(retained)
        after = path.read_text(encoding="utf-8")

        self.assertEqual(before, after)

    def test_demo_summary_counts_are_deterministic(self):
        result = run_retained_experience_readback_preview_minimal_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-retained-experience-readback-preview-minimal-check")
        self.assertEqual(result["flow"], "retained_experience_readback_preview_minimal_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["retained_jsonl_record_count"], 1)
        self.assertEqual(summary["loaded_retained_record_count"], 1)
        self.assertEqual(summary["readback_preview_count"], 11)
        self.assertEqual(summary["valid_readback_preview_count"], 1)
        self.assertEqual(summary["invalid_readback_preview_count"], 10)
        self.assertEqual(summary["retention_status_blocked_count"], 1)
        self.assertEqual(summary["read_only_false_blocked_count"], 1)
        self.assertEqual(summary["empty_exact_key_blocked_count"], 1)
        self.assertEqual(summary["usable_as_blocked_count"], 1)
        self.assertEqual(summary["lesson_applied_blocked_count"], 1)
        self.assertEqual(summary["action_selection_influence_blocked_count"], 1)
        self.assertEqual(summary["action_behavior_changed_blocked_count"], 1)
        self.assertEqual(summary["predictor_modified_blocked_count"], 1)
        self.assertEqual(summary["automatic_retention_blocked_count"], 1)
        self.assertEqual(summary["proof_of_learning_claim_blocked_count"], 1)
        self.assertFalse(summary["readback_mutated_jsonl"])
        self.assertTrue(boundary["read_only"])
        self.assertTrue(boundary["display_only"])
        self.assertTrue(boundary["temp_jsonl_check_only"])
        self.assertFalse(boundary["production_listing_cli_added"])
        self.assertFalse(boundary["production_read_cli_added"])
        self.assertFalse(boundary["production_write_cli_added"])
        self.assertFalse(boundary["automatic_retention_added"])
        self.assertFalse(boundary["four_layer_memory_added"])
        self.assertFalse(boundary["lesson_application_added"])
        self.assertFalse(boundary["runtime_action_selection_added"])
        self.assertFalse(boundary["action_behavior_change_added"])
        self.assertFalse(boundary["predictor_mutation_added"])
        self.assertFalse(boundary["proof_of_learning_claimed"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-retained-experience-readback-preview-minimal-check")

        self.assertEqual(result["command"], "run-retained-experience-readback-preview-minimal-check")
        self.assertEqual(result["summary"]["valid_readback_preview_count"], 1)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-retained-experience-readback-preview-minimal-check",
            ],
            check=True,
            capture_output=True,
            encoding="utf-8",
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-retained-experience-readback-preview-minimal-check")
        self.assertEqual(result["summary"]["readback_preview_count"], 11)

    def _assert_invalid(self, preview, error_code):
        validation = validate_retained_experience_readback_preview(preview)

        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])


if __name__ == "__main__":
    unittest.main()
