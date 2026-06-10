import json
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from ashl_core.mentor_gated_experience_retention_minimal import (
    append_retained_experience_jsonl,
    build_mentor_retention_decision,
    load_retained_experience_jsonl,
    run_mentor_gated_experience_retention_minimal_check,
    validate_mentor_retention_decision,
)
from ashl_core.session_experience_record_schema_minimal import (
    run_session_experience_record_schema_minimal_check,
)
from ashl_core.teaching_cli import run_command


EXPECTED_DECISION_FIELDS = {
    "retention_decision_id",
    "source_experience_record_id",
    "mentor_text",
    "approved_for_retention",
    "retention_target",
    "trace_only",
    "blocked_flags",
}

EXPECTED_RETAINED_FIELDS = {
    "retained_record_id",
    "source_experience_record_id",
    "exact_key",
    "experience_type",
    "retention_status",
    "retained_by",
    "retention_reason",
    "source_snapshot",
    "blocked_flags",
}


class MentorGatedExperienceRetentionMinimalTests(unittest.TestCase):
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

    def _approved_decision(self, record=None):
        record = record or self._valid_experience_record()
        return build_mentor_retention_decision(record, "留")

    def test_mentor_text_lau_approves_retention(self):
        record = self._valid_experience_record()
        decision = build_mentor_retention_decision(record, "留")
        validation = validate_mentor_retention_decision(decision)

        self.assertEqual(set(decision), EXPECTED_DECISION_FIELDS)
        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertTrue(decision["approved_for_retention"])
        self.assertFalse(decision["trace_only"])
        self.assertEqual(decision["retention_target"], "append_only_jsonl")

    def test_mentor_text_not_lau_blocks_retention(self):
        decision = build_mentor_retention_decision(self._valid_experience_record(), "不要")
        validation = validate_mentor_retention_decision(decision)

        self.assertFalse(decision["approved_for_retention"])
        self.assertFalse(validation["valid"])
        self.assertIn("mentor_text_not_approval_phrase", validation["error_codes"])

    def test_valid_approved_decision_appends_one_jsonl_line(self):
        record = self._valid_experience_record()
        decision = self._approved_decision(record)
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "retention" / "records.jsonl"
            result = append_retained_experience_jsonl(record, decision, path)

            self.assertTrue(result["appended"], result["error_codes"])
            self.assertTrue(path.exists())
            lines = path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 1)
            self.assertEqual(json.loads(lines[0]), result["retained_record"])

    def test_loaded_jsonl_reads_retained_record_back(self):
        record = self._valid_experience_record()
        decision = self._approved_decision(record)
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "retention" / "records.jsonl"
            append_result = append_retained_experience_jsonl(record, decision, path)
            loaded = load_retained_experience_jsonl(path)

            self.assertEqual(loaded, [append_result["retained_record"]])
            self.assertTrue(append_result["loaded_records_include_appended"])

    def test_append_creates_parent_directory_if_missing(self):
        record = self._valid_experience_record()
        decision = self._approved_decision(record)
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "missing" / "nested" / "records.jsonl"
            result = append_retained_experience_jsonl(record, decision, path)

            self.assertTrue(result["appended"])
            self.assertTrue(path.parent.exists())

    def test_append_is_append_only_and_does_not_overwrite_existing_line(self):
        record = self._valid_experience_record()
        decision = self._approved_decision(record)
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "records.jsonl"
            sentinel = {"retained_record_id": "existing"}
            path.write_text(json.dumps(sentinel) + "\n", encoding="utf-8")
            append_retained_experience_jsonl(record, decision, path)

            loaded = load_retained_experience_jsonl(path)
            self.assertEqual(loaded[0], sentinel)
            self.assertEqual(len(loaded), 2)

    def test_source_id_mismatch_blocks_append(self):
        record = self._valid_experience_record()
        decision = self._approved_decision(record)
        decision["source_experience_record_id"] = "other_session_experience"
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = append_retained_experience_jsonl(record, decision, Path(tmp_dir) / "records.jsonl")

            self.assertFalse(result["appended"])
            self.assertIn("source_experience_record_id_mismatch", result["error_codes"])

    def test_not_approved_decision_blocks_append(self):
        record = self._valid_experience_record()
        decision = build_mentor_retention_decision(record, "不要")
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = append_retained_experience_jsonl(record, decision, Path(tmp_dir) / "records.jsonl")

            self.assertFalse(result["appended"])
            self.assertIn("decision_not_approved_for_retention", result["error_codes"])

    def test_retained_record_stores_minimal_fields_only(self):
        record = self._valid_experience_record()
        decision = self._approved_decision(record)
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = append_retained_experience_jsonl(record, decision, Path(tmp_dir) / "records.jsonl")
            retained = result["retained_record"]

            self.assertEqual(set(retained), EXPECTED_RETAINED_FIELDS)
            self.assertEqual(len(retained), 9)

    def test_retained_record_retention_status_is_retained(self):
        record = self._valid_experience_record()
        decision = self._approved_decision(record)
        with tempfile.TemporaryDirectory() as tmp_dir:
            retained = append_retained_experience_jsonl(
                record, decision, Path(tmp_dir) / "records.jsonl"
            )["retained_record"]

            self.assertEqual(retained["retention_status"], "retained")
            self.assertEqual(retained["retained_by"], "mentor")
            self.assertEqual(retained["retention_reason"], "mentor_text:留")

    def test_retained_record_source_snapshot_keeps_original_not_retained_status(self):
        record = self._valid_experience_record()
        decision = self._approved_decision(record)
        with tempfile.TemporaryDirectory() as tmp_dir:
            retained = append_retained_experience_jsonl(
                record, decision, Path(tmp_dir) / "records.jsonl"
            )["retained_record"]

            self.assertEqual(retained["source_snapshot"]["original_retention_status"], "not_retained")
            self.assertEqual(
                retained["source_snapshot"]["source_evidence_trace_id"],
                record["source_evidence_trace_id"],
            )
            self.assertEqual(
                retained["source_snapshot"]["source_bucket_candidate_id"],
                record["source_bucket_candidate_id"],
            )

    def test_blocked_flags_true_block_decision(self):
        cases = {
            "automatic_retention": "automatic_retention_enabled",
            "action_selection_influence": "action_selection_influence_enabled",
            "action_behavior_changed": "action_behavior_changed_enabled",
            "predictor_modified": "predictor_modified_enabled",
            "proof_of_learning_claim": "proof_of_learning_claim_enabled",
        }
        for flag, error_code in cases.items():
            with self.subTest(flag=flag):
                decision = self._approved_decision()
                decision["blocked_flags"][flag] = True
                validation = validate_mentor_retention_decision(decision)

                self.assertFalse(validation["valid"])
                self.assertIn(error_code, validation["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        result = run_mentor_gated_experience_retention_minimal_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-mentor-gated-experience-retention-minimal-check")
        self.assertEqual(result["flow"], "mentor_gated_experience_retention_minimal_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["retention_decision_count"], 7)
        self.assertEqual(summary["approved_retention_decision_count"], 1)
        self.assertEqual(summary["blocked_retention_decision_count"], 6)
        self.assertEqual(summary["jsonl_append_count"], 1)
        self.assertEqual(summary["jsonl_load_back_count"], 1)
        self.assertEqual(summary["retained_record_count"], 1)
        self.assertEqual(summary["mentor_text_blocked_count"], 1)
        self.assertEqual(summary["automatic_retention_blocked_count"], 1)
        self.assertEqual(summary["action_selection_influence_blocked_count"], 1)
        self.assertEqual(summary["action_behavior_changed_blocked_count"], 1)
        self.assertEqual(summary["predictor_modified_blocked_count"], 1)
        self.assertEqual(summary["proof_of_learning_claim_blocked_count"], 1)
        self.assertEqual(summary["not_approved_append_blocked_count"], 1)
        self.assertEqual(summary["source_mismatch_append_blocked_count"], 1)
        self.assertEqual(summary["retained_action_selection_influence_count"], 0)
        self.assertEqual(summary["retained_action_behavior_changed_count"], 0)
        self.assertEqual(summary["retained_predictor_modified_count"], 0)
        self.assertEqual(summary["retained_proof_of_learning_claim_count"], 0)
        self.assertTrue(boundary["first_true_retention_boundary"])
        self.assertTrue(boundary["append_only_jsonl"])
        self.assertTrue(boundary["durable_read_back_supported"])
        self.assertTrue(boundary["mentor_text_exact_lau_only"])
        self.assertFalse(boundary["production_write_cli_added"])
        self.assertFalse(boundary["automatic_retention_added"])
        self.assertFalse(boundary["four_layer_memory_added"])
        self.assertFalse(boundary["lesson_application_added"])
        self.assertFalse(boundary["runtime_action_selection_added"])
        self.assertFalse(boundary["action_behavior_change_added"])
        self.assertFalse(boundary["predictor_mutation_added"])
        self.assertFalse(boundary["proof_of_learning_claimed"])
        self.assertTrue(boundary["rollback_manual_only"])
        self.assertFalse(boundary["destructive_auto_delete_added"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-mentor-gated-experience-retention-minimal-check")

        self.assertEqual(result["command"], "run-mentor-gated-experience-retention-minimal-check")
        self.assertEqual(result["summary"]["approved_retention_decision_count"], 1)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-mentor-gated-experience-retention-minimal-check",
            ],
            check=True,
            capture_output=True,
            encoding="utf-8",
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-mentor-gated-experience-retention-minimal-check")
        self.assertEqual(result["summary"]["jsonl_append_count"], 1)


if __name__ == "__main__":
    unittest.main()
