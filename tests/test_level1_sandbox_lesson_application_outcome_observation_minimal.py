import unittest

from ashl_core.level1_sandbox_lesson_application_minimal import build_level1_sandbox_lesson_application
from ashl_core.level1_sandbox_lesson_application_outcome_observation_minimal import (
    FORBIDDEN_FLAGS,
    build_level1_sandbox_lesson_application_outcome_observation,
    check_level1_sandbox_lesson_application_outcome_observation,
    run_level1_sandbox_lesson_application_outcome_observation_minimal_check,
)


class Level1SandboxLessonApplicationOutcomeObservationMinimalTests(unittest.TestCase):
    def _record(self):
        return build_level1_sandbox_lesson_application_outcome_observation()

    def test_valid_observation_passes(self):
        record = self._record()

        self.assertTrue(check_level1_sandbox_lesson_application_outcome_observation(record)["valid"])
        self.assertEqual(record["record_type"], "level1_sandbox_lesson_application_outcome_observation")

    def test_invalid_source_application_fails(self):
        source = build_level1_sandbox_lesson_application()
        source["front_symbol"] = "."
        record = build_level1_sandbox_lesson_application_outcome_observation(source_application_record=source)

        self.assertFalse(check_level1_sandbox_lesson_application_outcome_observation(record)["valid"])

    def test_missing_source_application_fails(self):
        record = self._record()
        record.pop("source_application")

        self.assertFalse(check_level1_sandbox_lesson_application_outcome_observation(record)["valid"])

    def test_wrong_scope_fails(self):
        record = self._record()
        record["target_scope"] = "production"

        self.assertFalse(check_level1_sandbox_lesson_application_outcome_observation(record)["valid"])

    def test_wrong_observed_front_symbol_fails(self):
        record = self._record()
        record["observed_front_symbol"] = "."

        self.assertFalse(check_level1_sandbox_lesson_application_outcome_observation(record)["valid"])

    def test_wrong_observed_sandbox_action_fails(self):
        record = self._record()
        record["observed_sandbox_action"] = "retry_same_action"

        self.assertFalse(check_level1_sandbox_lesson_application_outcome_observation(record)["valid"])

    def test_missing_retry_block_fails(self):
        record = self._record()
        record["observed_blocks_retry_same_action_until_check"] = False

        self.assertFalse(check_level1_sandbox_lesson_application_outcome_observation(record)["valid"])

    def test_sandbox_effect_not_visible_fails(self):
        record = self._record()
        record["sandbox_effect_visible"] = False

        self.assertFalse(check_level1_sandbox_lesson_application_outcome_observation(record)["valid"])

    def test_missing_audit_fails(self):
        record = self._record()
        record["audit_record_present"] = False

        self.assertFalse(check_level1_sandbox_lesson_application_outcome_observation(record)["valid"])

    def test_missing_rollback_fails(self):
        record = self._record()
        record["rollback_record_present"] = False

        self.assertFalse(check_level1_sandbox_lesson_application_outcome_observation(record)["valid"])

    def test_any_forbidden_boundary_flag_true_fails(self):
        for flag in FORBIDDEN_FLAGS:
            with self.subTest(flag=flag):
                record = self._record()
                record[flag] = True

                self.assertFalse(check_level1_sandbox_lesson_application_outcome_observation(record)["valid"])

    def test_wording_hygiene_blocks_mojibake(self):
        for text in (chr(0x876F) + chr(0x8840) + "?", "?" + chr(0x822A) + "??"):
            with self.subTest(text=text):
                record = self._record()
                record["approval_wording_boundary"] = text

                self.assertFalse(check_level1_sandbox_lesson_application_outcome_observation(record)["valid"])

    def test_safe_capability_claim_does_not_overclaim(self):
        record = self._record()
        claim = record["safe_capability_claim"]

        self.assertIn("toy sandbox scope only", claim)
        self.assertIn("remain blocked", claim)
        self.assertNotIn("memory was updated", claim)
        self.assertNotIn("the lesson was learned", claim)

    def test_summary_counts_are_stable(self):
        result = run_level1_sandbox_lesson_application_outcome_observation_minimal_check()
        summary = result["summary"]

        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["level1_sandbox_outcome_observation_result_count"], 25)
        self.assertEqual(summary["valid_level1_sandbox_outcome_observation_count"], 1)
        self.assertEqual(summary["invalid_level1_sandbox_outcome_observation_count"], 24)
        self.assertEqual(summary["source_application_checked_count"], 1)
        self.assertEqual(summary["sandbox_effect_observed_count"], 1)
        self.assertEqual(summary["audit_record_confirmed_count"], 1)
        self.assertEqual(summary["rollback_record_confirmed_count"], 1)
        self.assertEqual(summary["blocked_boundary_confirmed_count"], 1)


if __name__ == "__main__":
    unittest.main()
