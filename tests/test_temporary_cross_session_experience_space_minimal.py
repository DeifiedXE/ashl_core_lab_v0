import json
import subprocess
import sys
import unittest
from copy import deepcopy

from ashl_core.session_experience_record_schema_minimal import (
    run_session_experience_record_schema_minimal_check,
)
from ashl_core.teaching_cli import run_command
from ashl_core.temporary_cross_session_experience_space_minimal import (
    build_temporary_experience_space,
    query_temporary_experience_space,
    run_temporary_cross_session_experience_space_minimal_check,
    validate_temporary_experience_space,
)


EXPECTED_FIELDS = {
    "space_id",
    "space_type",
    "trace_only",
    "deprecated_by_future_memory",
    "records",
    "index",
    "blocked_flags",
}


class TemporaryCrossSessionExperienceSpaceMinimalTests(unittest.TestCase):
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

    def _valid_space(self):
        return build_temporary_experience_space([self._valid_experience()])

    def test_valid_not_retained_experience_enters_temporary_space(self):
        experience = self._valid_experience()
        before = deepcopy(experience)
        space = build_temporary_experience_space([experience])
        validation = validate_temporary_experience_space(space)

        self.assertEqual(experience, before)
        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(space["space_type"], "temporary_cross_session_experience_space")
        self.assertTrue(space["trace_only"])
        self.assertTrue(space["deprecated_by_future_memory"])
        self.assertEqual(len(space["records"]), 1)
        self.assertEqual(space["records"][0]["experience_record_id"], experience["experience_record_id"])
        self.assertEqual(space["records"][0]["exact_key"], experience["exact_key"])
        self.assertEqual(space["records"][0]["retention_status"], "not_retained")

    def test_record_has_only_expected_top_level_fields(self):
        space = self._valid_space()

        self.assertEqual(set(space), EXPECTED_FIELDS)
        self.assertEqual(len(space), 7)

    def test_invalid_or_retained_experience_does_not_enter_space(self):
        invalid = self._valid_experience()
        invalid["blocked_flags"]["memory_write"] = True
        retained = self._valid_experience()
        retained["retention_status"] = "retained"

        space = build_temporary_experience_space([invalid, retained])

        self.assertEqual(space["records"], [])
        self.assertEqual(space["index"]["record_count"], 0)

    def test_same_exact_key_query_matches(self):
        experience = self._valid_experience()
        space = build_temporary_experience_space([experience])
        result = query_temporary_experience_space(space, experience["exact_key"])

        self.assertTrue(result["matched"])
        self.assertEqual(result["match_scope"], "same_exact_key_only")
        self.assertEqual(result["matched_record_ids"], [experience["experience_record_id"]])
        self.assertTrue(result["trace_only"])
        self.assertTrue(all(value is False for value in result["blocked_flags"].values()))

    def test_different_exact_key_query_does_not_match(self):
        space = self._valid_space()
        result = query_temporary_experience_space(
            space,
            "action_intent_id:intent_demo_new_002|no_prior_candidate:true",
        )

        self.assertFalse(result["matched"])
        self.assertEqual(result["matched_record_ids"], [])
        self.assertEqual(result["match_scope"], "same_exact_key_only")

    def test_trace_only_false_blocks(self):
        space = self._valid_space()
        space["trace_only"] = False
        self._assert_invalid(space, "trace_only_not_true")

    def test_deprecated_by_future_memory_false_blocks(self):
        space = self._valid_space()
        space["deprecated_by_future_memory"] = False
        self._assert_invalid(space, "deprecated_by_future_memory_not_true")

    def test_retention_status_retained_blocks(self):
        space = self._valid_space()
        space["records"][0]["retention_status"] = "retained"
        self._assert_invalid(space, "retention_status_not_not_retained")

    def test_match_scope_other_than_same_exact_key_only_blocks(self):
        space = self._valid_space()
        space["index"]["match_scope"] = "semantic_similarity"
        self._assert_invalid(space, "match_scope_not_same_exact_key_only")

    def test_blocked_flags_true_block(self):
        cases = {
            "memory_write": "memory_write_enabled",
            "lesson_retained": "lesson_retained_enabled",
            "history_runtime_write": "history_runtime_write_enabled",
            "action_selection_influence": "action_selection_influence_enabled",
            "action_behavior_changed": "action_behavior_changed_enabled",
            "proof_of_learning_claim": "proof_of_learning_claim_enabled",
        }
        for flag, error_code in cases.items():
            with self.subTest(flag=flag):
                space = self._valid_space()
                space["blocked_flags"][flag] = True
                self._assert_invalid(space, error_code)

    def test_demo_summary_counts_are_deterministic(self):
        result = run_temporary_cross_session_experience_space_minimal_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(result["command"], "run-temporary-cross-session-experience-space-minimal-check")
        self.assertEqual(result["flow"], "temporary_cross_session_experience_space_minimal_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["temporary_space_count"], 11)
        self.assertEqual(summary["valid_temporary_space_count"], 1)
        self.assertEqual(summary["invalid_temporary_space_count"], 10)
        self.assertEqual(summary["temporary_record_count"], 1)
        self.assertEqual(summary["matched_query_count"], 1)
        self.assertEqual(summary["not_matched_query_count"], 1)
        self.assertEqual(summary["trace_only_false_blocked_count"], 1)
        self.assertEqual(summary["deprecated_by_future_memory_false_blocked_count"], 1)
        self.assertEqual(summary["retention_status_blocked_count"], 1)
        self.assertEqual(summary["match_scope_blocked_count"], 1)
        self.assertEqual(summary["memory_write_blocked_count"], 1)
        self.assertEqual(summary["lesson_retained_blocked_count"], 1)
        self.assertEqual(summary["history_runtime_write_blocked_count"], 1)
        self.assertEqual(summary["action_selection_influence_blocked_count"], 1)
        self.assertEqual(summary["action_behavior_changed_blocked_count"], 1)
        self.assertEqual(summary["proof_of_learning_claim_blocked_count"], 1)
        for field in [
            "memory_write_count",
            "lesson_retained_count",
            "history_runtime_write_count",
            "persistent_rule_write_count",
            "predictor_modified_count",
            "action_selection_influence_count",
            "action_behavior_changed_count",
            "proof_of_learning_claim_count",
        ]:
            with self.subTest(field=field):
                self.assertEqual(summary[field], 0)
        self.assertTrue(boundary["trace_only"])
        self.assertTrue(boundary["minimal_record_shape"])
        self.assertEqual(boundary["top_level_field_count"], 7)
        self.assertTrue(boundary["same_exact_key_only"])
        self.assertTrue(boundary["deprecated_by_future_memory"])
        self.assertFalse(boundary["real_memory_added"])
        self.assertFalse(boundary["long_term_memory_added"])
        self.assertFalse(boundary["lesson_retention_added"])
        self.assertFalse(boundary["history_runtime_added"])
        self.assertFalse(boundary["runtime_action_selection_added"])
        self.assertFalse(boundary["action_behavior_change_added"])
        self.assertFalse(boundary["semantic_similarity_added"])
        self.assertFalse(boundary["fuzzy_matching_added"])
        self.assertFalse(boundary["vector_retrieval_added"])
        self.assertFalse(boundary["predictor_mutation_added"])
        self.assertFalse(boundary["proof_of_learning_claimed"])

    def test_run_command_dispatches_check(self):
        result = run_command("run-temporary-cross-session-experience-space-minimal-check")

        self.assertEqual(result["command"], "run-temporary-cross-session-experience-space-minimal-check")
        self.assertEqual(result["summary"]["valid_temporary_space_count"], 1)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-temporary-cross-session-experience-space-minimal-check",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-temporary-cross-session-experience-space-minimal-check")
        self.assertEqual(result["summary"]["temporary_space_count"], 11)
        self.assertEqual(result["summary"]["matched_query_count"], 1)
        self.assertEqual(result["summary"]["not_matched_query_count"], 1)

    def _assert_invalid(self, space, error_code):
        validation = validate_temporary_experience_space(space)

        self.assertFalse(validation["valid"])
        self.assertIn(error_code, validation["error_codes"])


if __name__ == "__main__":
    unittest.main()
