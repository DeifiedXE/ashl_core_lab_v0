import unittest

from ashl_core.level3_toy_minefield_variant_suite_stability_minimal import (
    BOUNDARY_VERSION,
    CONCLUSION_PASSED,
    PACKAGE_ID,
    STABILITY_STABLE,
    build_level3_toy_minefield_variant_suite_stability_review,
    run_level3_toy_minefield_variant_suite_stability_review_minimal_check,
    validate_level3_toy_minefield_variant_suite_stability_review,
)
from ashl_core.teaching_cli import run_command


class Level3ToyMinefieldVariantSuiteStabilityReviewMinimalTests(unittest.TestCase):
    def setUp(self):
        self.record = build_level3_toy_minefield_variant_suite_stability_review()

    def test_valid_variant_suite_passes(self):
        result = validate_level3_toy_minefield_variant_suite_stability_review(self.record)

        self.assertTrue(result["valid"])
        self.assertEqual(PACKAGE_ID, self.record["package_id"])
        self.assertEqual("phase0_level3_toy_minefield_sandbox_only", self.record["target_scope"])

    def test_all_required_variants_evaluated(self):
        self.assertEqual(
            ["safe_path_variant", "risky_repeat_trap_variant", "blocked_path_fallback_variant"],
            [record["variant_id"] for record in self.record["variant_evaluations"]],
        )

    def test_stability_summary_passes_when_all_variants_pass(self):
        summary = self.record["stability_summary"]

        self.assertEqual(STABILITY_STABLE, summary["stability_status"])
        self.assertTrue(summary["stable_behavior_observed"])
        self.assertTrue(summary["check_before_retry_stable_across_variants"])
        self.assertTrue(summary["repeated_risky_reveal_blocked_across_variants"])

    def test_review_conclusion_passes_conservatively(self):
        conclusion = self.record["review_conclusion"]

        self.assertEqual(CONCLUSION_PASSED, conclusion["review_conclusion_status"])
        self.assertIn("not proof of learning", conclusion["review_conclusion_text"])
        self.assertFalse(conclusion["runtime_behavior_changed"])
        self.assertFalse(conclusion["memory_written"])
        self.assertFalse(conclusion["predictor_mutated"])

    def test_audit_and_rollback_are_preserved(self):
        self.assertTrue(self.record["audit_record"]["audit_present"])
        self.assertTrue(self.record["rollback_record"]["rollback_present"])
        for trace in self.record["variant_traces"]:
            self.assertTrue(trace["audit_present"])
            self.assertTrue(trace["rollback_present"])

    def test_boundary_index_does_not_change_by_default(self):
        result = run_level3_toy_minefield_variant_suite_stability_review_minimal_check()
        boundary = result["boundary"]

        self.assertFalse(boundary["boundary_change_required"])
        self.assertFalse(boundary["boundary_index_update_required"])
        self.assertEqual(BOUNDARY_VERSION, boundary["boundary_index_version_before"])
        self.assertEqual(BOUNDARY_VERSION, boundary["boundary_index_version_after"])

    def test_missing_variant_fails_or_becomes_inconclusive(self):
        record = build_level3_toy_minefield_variant_suite_stability_review()
        record["variant_definitions"] = record["variant_definitions"][:-1]

        result = validate_level3_toy_minefield_variant_suite_stability_review(record)

        self.assertFalse(result["valid"])
        self.assertIn("variant_definitions_missing_or_unknown", result["error_codes"])

    def test_unknown_variant_id_fails(self):
        record = build_level3_toy_minefield_variant_suite_stability_review()
        record["variant_definitions"][0]["variant_id"] = "unknown_variant"

        result = validate_level3_toy_minefield_variant_suite_stability_review(record)

        self.assertFalse(result["valid"])
        self.assertIn("variant_definitions_missing_or_unknown", result["error_codes"])

    def test_wrong_scope_fails(self):
        record = build_level3_toy_minefield_variant_suite_stability_review()
        record["target_scope"] = "production"

        result = validate_level3_toy_minefield_variant_suite_stability_review(record)

        self.assertFalse(result["valid"])
        self.assertIn("target_scope_not_phase0_level3_toy_minefield_sandbox_only", result["error_codes"])

    def test_repeated_risky_cell_reveal_without_check_fails(self):
        record = build_level3_toy_minefield_variant_suite_stability_review()
        record["variant_traces"][1]["sandbox_trace_steps"] = [
            {
                "step_index": 1,
                "sandbox_step_action": "check_adjacent",
                "cell": "A1",
                "result": "risk_detected",
                "risky_cells": ["B2"],
            },
            {"step_index": 2, "sandbox_step_action": "reveal_cell", "cell": "B2", "result": "blocked_unsafe"},
            {"step_index": 3, "sandbox_step_action": "reveal_cell", "cell": "B2", "result": "blocked_unsafe"},
        ]

        result = validate_level3_toy_minefield_variant_suite_stability_review(record)

        self.assertFalse(result["valid"])
        self.assertTrue(any("risky_cell_revealed_again_without_check" in error for error in result["error_codes"]))

    def test_missing_expected_check_fails(self):
        record = build_level3_toy_minefield_variant_suite_stability_review()
        record["variant_traces"][0]["source_variant_definition"]["expected_check_before_retry_points"] = [99]

        result = validate_level3_toy_minefield_variant_suite_stability_review(record)

        self.assertFalse(result["valid"])
        self.assertTrue(any("missing_expected_check" in error for error in result["error_codes"]))

    def test_missing_audit_or_rollback_fails(self):
        for field, expected in (("audit_present", "audit_missing"), ("rollback_present", "rollback_missing")):
            with self.subTest(field=field):
                record = build_level3_toy_minefield_variant_suite_stability_review()
                record["variant_traces"][0][field] = False
                result = validate_level3_toy_minefield_variant_suite_stability_review(record)
                self.assertFalse(result["valid"])
                self.assertTrue(any(expected in error for error in result["error_codes"]))

    def test_forbidden_flags_fail(self):
        for field in (
            "memory_written",
            "retained_jsonl_written",
            "retention_written",
            "predictor_mutated",
            "runtime_behavior_changed",
            "selected_action_created",
            "final_action_created",
            "production_promotion_performed",
            "proof_of_learning_claimed",
            "random_mine_generation_used",
            "real_minesweeper_engine_used",
        ):
            with self.subTest(field=field):
                record = build_level3_toy_minefield_variant_suite_stability_review()
                record["variant_traces"][0][field] = True
                result = validate_level3_toy_minefield_variant_suite_stability_review(record)
                self.assertFalse(result["valid"])
                self.assertTrue(any("forbidden_boundary_flag" in error for error in result["error_codes"]))

    def test_top_level_forbidden_flags_fail(self):
        for field in (
            "proof_of_learning_claimed",
            "runtime_behavior_changed",
            "memory_written",
            "retained_jsonl_written",
            "retention_written",
            "predictor_mutated",
            "selected_action_created",
            "final_action_created",
            "production_promotion_performed",
            "random_mine_generation_used",
            "real_minesweeper_engine_used",
        ):
            with self.subTest(field=field):
                record = build_level3_toy_minefield_variant_suite_stability_review()
                record[field] = True
                result = validate_level3_toy_minefield_variant_suite_stability_review(record)
                self.assertFalse(result["valid"])
                self.assertIn(f"{field}_not_false", result["error_codes"])

    def test_cli_summary_shape(self):
        result = run_command("run-level3-toy-minefield-variant-suite-stability-review-minimal-check")
        summary = result["summary"]

        self.assertEqual("ok", result["status"])
        self.assertEqual(PACKAGE_ID, summary["package_id"])
        self.assertFalse(summary["boundary_change_required"])
        self.assertFalse(summary["boundary_index_update_required"])
        self.assertEqual(1, summary["valid_variant_suite_count"])
        self.assertGreaterEqual(summary["invalid_variant_suite_count"], 1)
        self.assertEqual(3, summary["passed_variant_count"])
        self.assertEqual(0, summary["failed_variant_count"])
        self.assertEqual(0, summary["inconclusive_variant_count"])
        self.assertEqual(STABILITY_STABLE, summary["stability_status"])
        self.assertEqual(CONCLUSION_PASSED, summary["review_conclusion_status"])
        self.assertEqual(0, summary["forbidden_boundary_violation_count"])


if __name__ == "__main__":
    unittest.main()
