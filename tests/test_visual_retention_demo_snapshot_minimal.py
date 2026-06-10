import json
import subprocess
import sys
import unittest
from copy import deepcopy

from ashl_core.teaching_cli import run_command
from ashl_core.visual_retention_demo_snapshot_minimal import (
    build_visual_retention_demo_snapshot,
    run_visual_retention_demo_snapshot_minimal_check,
    validate_visual_retention_demo_snapshot,
)
from ashl_core.visual_retained_experience_link_preview_minimal import (
    run_visual_retained_experience_link_preview_minimal_check,
)


EXPECTED_FIELDS = {
    "snapshot_id",
    "source_retina_focus_preview_id",
    "source_visual_lesson_evidence_candidate_id",
    "source_visual_retained_link_preview_id",
    "read_only",
    "human_summary",
    "safe_claims",
    "blocked_flags",
}


class VisualRetentionDemoSnapshotMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = run_visual_retention_demo_snapshot_minimal_check()

    def _snapshot(self, match_status="matched"):
        for snapshot in self.result["visual_retention_demo_snapshots"]:
            if snapshot["human_summary"]["retained_match_status"] == match_status:
                return deepcopy(snapshot)
        raise AssertionError(f"missing snapshot: {match_status}")

    def _source_records(self, match_status="matched"):
        link_result = run_visual_retained_experience_link_preview_minimal_check()
        evidence_result = link_result["source_visual_lesson_evidence_result"]
        retina_result = evidence_result["source_retina_focus_preview_result"]
        retina_preview = deepcopy(retina_result["retina_focus_previews"][0])
        visual_evidence = deepcopy(evidence_result["visual_lesson_evidence_candidates"][0])
        link_preview = deepcopy(
            next(
                preview
                for preview in link_result["visual_retained_experience_link_previews"]
                if preview["match_status"] == match_status
            )
        )
        return retina_preview, visual_evidence, link_preview

    def test_valid_matched_visual_retention_demo_snapshot_is_created(self):
        retina_preview, visual_evidence, link_preview = self._source_records("matched")
        snapshot = build_visual_retention_demo_snapshot(retina_preview, visual_evidence, link_preview)
        validation = validate_visual_retention_demo_snapshot(snapshot)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(snapshot["human_summary"]["retained_match_status"], "matched")

    def test_valid_not_matched_visual_retention_demo_snapshot_is_created(self):
        retina_preview, visual_evidence, link_preview = self._source_records("not_matched")
        snapshot = build_visual_retention_demo_snapshot(retina_preview, visual_evidence, link_preview)
        validation = validate_visual_retention_demo_snapshot(snapshot)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(snapshot["human_summary"]["retained_match_status"], "not_matched")

    def test_record_has_only_expected_top_level_fields(self):
        snapshot = self._snapshot()

        self.assertEqual(set(snapshot), EXPECTED_FIELDS)
        self.assertEqual(len(snapshot), 8)

    def test_human_summary_includes_expected_fields(self):
        summary = self._snapshot()["human_summary"]

        self.assertIn("what_changed", summary)
        self.assertIn("what_focus_preview_says", summary)
        self.assertIn("what_lesson_evidence_says", summary)
        self.assertIn("retained_match_status", summary)
        self.assertIn("plain_result", summary)

    def test_safe_claims_same_exact_key_only_true(self):
        snapshot = self._snapshot()

        self.assertTrue(snapshot["safe_claims"]["same_exact_key_only"])

    def test_read_only_false_blocks(self):
        snapshot = self._snapshot()
        snapshot["read_only"] = False
        self._assert_invalid(snapshot, "read_only_not_true")

    def test_missing_source_ids_block(self):
        cases = {
            "source_retina_focus_preview_id": "source_retina_focus_preview_id_missing",
            "source_visual_lesson_evidence_candidate_id": "source_visual_lesson_evidence_candidate_id_missing",
            "source_visual_retained_link_preview_id": "source_visual_retained_link_preview_id_missing",
        }
        for field, error_code in cases.items():
            with self.subTest(field=field):
                snapshot = self._snapshot()
                snapshot[field] = ""
                self._assert_invalid(snapshot, error_code)

    def test_empty_what_changed_blocks(self):
        snapshot = self._snapshot()
        snapshot["human_summary"]["what_changed"] = ""
        self._assert_invalid(snapshot, "what_changed_empty_or_not_string")

    def test_empty_plain_result_blocks(self):
        snapshot = self._snapshot()
        snapshot["human_summary"]["plain_result"] = ""
        self._assert_invalid(snapshot, "plain_result_empty_or_not_string")

    def test_bad_retained_match_status_blocks(self):
        snapshot = self._snapshot()
        snapshot["human_summary"]["retained_match_status"] = "semantic_match"
        self._assert_invalid(snapshot, "retained_match_status_not_matched_or_not_matched")

    def test_same_exact_key_only_false_blocks(self):
        snapshot = self._snapshot()
        snapshot["safe_claims"]["same_exact_key_only"] = False
        self._assert_invalid(snapshot, "same_exact_key_only_not_true")

    def test_blocked_flags_true_block(self):
        cases = {
            "object_recognition": "object_recognition_enabled",
            "semantic_vision": "semantic_vision_enabled",
            "active_focus_applied": "active_focus_applied_enabled",
            "lesson_applied": "lesson_applied_enabled",
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
        for flag, error_code in cases.items():
            with self.subTest(flag=flag):
                snapshot = self._snapshot()
                snapshot["blocked_flags"][flag] = True
                self._assert_invalid(snapshot, error_code)

    def test_demo_summary_counts_are_deterministic(self):
        summary = self.result["summary"]
        boundary = self.result["boundary_check"]

        self.assertEqual(self.result["command"], "run-visual-retention-demo-snapshot-minimal-check")
        self.assertEqual(self.result["flow"], "visual_retention_demo_snapshot_minimal_v0")
        self.assertEqual(self.result["status"], "ok")
        self.assertEqual(summary["visual_retention_demo_snapshot_count"], 23)
        self.assertEqual(summary["valid_visual_retention_demo_snapshot_count"], 2)
        self.assertEqual(summary["invalid_visual_retention_demo_snapshot_count"], 21)
        self.assertEqual(summary["matched_snapshot_count"], 1)
        self.assertEqual(summary["not_matched_snapshot_count"], 1)
        self.assertEqual(summary["read_only_false_blocked_count"], 1)
        self.assertEqual(summary["missing_source_retina_focus_preview_blocked_count"], 1)
        self.assertEqual(summary["missing_source_visual_lesson_evidence_blocked_count"], 1)
        self.assertEqual(summary["missing_source_visual_retained_link_blocked_count"], 1)
        self.assertEqual(summary["empty_what_changed_blocked_count"], 1)
        self.assertEqual(summary["empty_plain_result_blocked_count"], 1)
        self.assertEqual(summary["retained_match_status_blocked_count"], 1)
        self.assertEqual(summary["same_exact_key_only_false_blocked_count"], 1)
        self.assertEqual(summary["object_recognition_blocked_count"], 1)
        self.assertEqual(summary["semantic_vision_blocked_count"], 1)
        self.assertEqual(summary["active_focus_applied_blocked_count"], 1)
        self.assertEqual(summary["lesson_applied_blocked_count"], 1)
        self.assertEqual(summary["action_selection_influence_blocked_count"], 1)
        self.assertEqual(summary["action_behavior_changed_blocked_count"], 1)
        self.assertEqual(summary["memory_write_blocked_count"], 1)
        self.assertEqual(summary["new_retention_written_blocked_count"], 1)
        self.assertEqual(summary["semantic_match_blocked_count"], 1)
        self.assertEqual(summary["fuzzy_match_blocked_count"], 1)
        self.assertEqual(summary["vector_match_blocked_count"], 1)
        self.assertEqual(summary["predictor_modified_blocked_count"], 1)
        self.assertEqual(summary["proof_of_learning_claim_blocked_count"], 1)
        self.assertEqual(summary["object_recognition_count"], 0)
        self.assertEqual(summary["semantic_vision_count"], 0)
        self.assertEqual(summary["active_focus_applied_count"], 0)
        self.assertEqual(summary["lesson_applied_count"], 0)
        self.assertEqual(summary["action_selection_influence_count"], 0)
        self.assertEqual(summary["action_behavior_changed_count"], 0)
        self.assertEqual(summary["memory_write_count"], 0)
        self.assertEqual(summary["new_retention_written_count"], 0)
        self.assertEqual(summary["semantic_match_count"], 0)
        self.assertEqual(summary["fuzzy_match_count"], 0)
        self.assertEqual(summary["vector_match_count"], 0)
        self.assertEqual(summary["predictor_modified_count"], 0)
        self.assertEqual(summary["proof_of_learning_claim_count"], 0)
        self.assertTrue(boundary["read_only"])
        self.assertTrue(boundary["same_exact_key_only"])
        self.assertFalse(boundary["writes_retained_jsonl"])
        self.assertFalse(boundary["object_recognition_added"])
        self.assertFalse(boundary["semantic_vision_added"])
        self.assertFalse(boundary["lesson_application_added"])
        self.assertFalse(boundary["runtime_action_selection_added"])
        self.assertFalse(boundary["memory_write_added"])
        self.assertFalse(boundary["new_retention_write_added"])
        self.assertFalse(boundary["proof_of_learning_claimed"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-visual-retention-demo-snapshot-minimal-check")

        self.assertEqual(result["command"], "run-visual-retention-demo-snapshot-minimal-check")
        self.assertEqual(result["summary"]["valid_visual_retention_demo_snapshot_count"], 2)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-visual-retention-demo-snapshot-minimal-check",
            ],
            check=True,
            capture_output=True,
            encoding="utf-8",
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-visual-retention-demo-snapshot-minimal-check")
        self.assertEqual(result["summary"]["visual_retention_demo_snapshot_count"], 23)
        self.assertEqual(len(result["valid_human_summaries"]), 2)

    def _assert_invalid(self, snapshot, error_code):
        validation = validate_visual_retention_demo_snapshot(snapshot)

        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])


if __name__ == "__main__":
    unittest.main()
