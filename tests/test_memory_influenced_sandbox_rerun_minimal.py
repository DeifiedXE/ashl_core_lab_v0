import unittest
from copy import deepcopy

from ashl_core.memory_influenced_sandbox_rerun_minimal import (
    BOUNDARY_INDEX_VERSION_AFTER,
    BOUNDARY_INDEX_VERSION_BEFORE,
    build_memory_influenced_sandbox_rerun_comparison,
    build_memory_influenced_sandbox_rerun_record,
    run_memory_influenced_sandbox_rerun_minimal_check,
    validate_memory_influenced_sandbox_rerun_comparison,
    validate_memory_influenced_sandbox_rerun_record,
    validate_memory_influenced_sandbox_variant_rerun,
)
from ashl_core.teaching_cli import run_command


class MemoryInfluencedSandboxRerunMinimalTests(unittest.TestCase):
    def setUp(self):
        self.record = build_memory_influenced_sandbox_rerun_record()
        self.comparison = build_memory_influenced_sandbox_rerun_comparison(self.record)

    def test_valid_rerun_is_created(self):
        result = validate_memory_influenced_sandbox_rerun_record(self.record)

        self.assertTrue(result["valid"])
        self.assertEqual([], result["error_codes"])

    def test_cli_returns_ok(self):
        result = run_command("run-memory-influenced-sandbox-rerun-minimal-check")

        self.assertEqual("ok", result["status"])
        self.assertEqual(1, result["summary"]["valid_rerun_count"])

    def test_valid_variant_records_are_created(self):
        self.assertEqual(
            ["safe_path_variant", "risky_repeat_trap_variant", "blocked_path_fallback_variant"],
            self.record["variants"],
        )
        for variant in self.record["variant_reruns"]:
            with self.subTest(variant=variant["variant_id"]):
                self.assertTrue(validate_memory_influenced_sandbox_variant_rerun(variant)["valid"])

    def test_valid_comparison_is_created(self):
        result = validate_memory_influenced_sandbox_rerun_comparison(self.comparison)

        self.assertTrue(result["valid"])
        self.assertEqual(3, self.comparison["variant_count"])
        self.assertTrue(self.comparison["all_variants_passed"])

    def test_requires_upstream_sources(self):
        for field, error in (
            ("source_memory_runtime_influence", "source_memory_runtime_influence_missing"),
            ("source_level3_variant_suite", "source_level3_variant_suite_missing"),
            ("source_controlled_memory_read", "source_controlled_memory_read_missing"),
            ("source_memory_influence_preview", "source_memory_influence_preview_missing"),
        ):
            record = deepcopy(self.record)
            record.pop(field)
            with self.subTest(field=field):
                self.assertIn(error, validate_memory_influenced_sandbox_rerun_record(record)["error_codes"])

    def test_memory_on_increases_check_before_retry(self):
        self.assertEqual(0.50, self.record["memory_off_baseline"]["check_before_retry"])
        self.assertEqual(0.60, self.record["memory_on_influenced"]["check_before_retry"])
        self.assertTrue(self.record["observed_tendency_shift"]["check_before_retry_increased"])

    def test_memory_on_decreases_retry_same_action_without_check(self):
        self.assertEqual(0.50, self.record["memory_off_baseline"]["retry_same_action_without_check"])
        self.assertEqual(0.45, self.record["memory_on_influenced"]["retry_same_action_without_check"])
        self.assertTrue(self.record["observed_tendency_shift"]["retry_same_action_without_check_decreased"])

    def test_rollback_restores_baseline(self):
        self.assertEqual(self.record["memory_off_baseline"], self.record["memory_off_after_rollback"])
        self.assertTrue(self.record["rollback_to_baseline_performed"])
        self.assertTrue(self.record["rollback_restored_baseline"])
        self.assertFalse(self.record["dirty_state_after_rollback"])

    def test_max_delta_within_limit(self):
        self.assertEqual(0.10, self.record["observed_tendency_shift"]["max_absolute_delta"])
        self.assertLessEqual(self.record["observed_tendency_shift"]["max_absolute_delta"], 0.10)

    def test_forbidden_fields_are_false(self):
        for field in (
            "selected_action_created",
            "final_action_created",
            "direct_command_created",
            "production_behavior_changed",
            "predictor_read_enabled",
            "predictor_influence_enabled",
            "predictor_mutation_performed",
            "retained_jsonl_write_performed",
            "retention_write_performed",
            "proof_of_learning_claim_allowed",
            "autonomous_learning_claim_allowed",
            "autonomous_action_claim_allowed",
        ):
            with self.subTest(field=field):
                self.assertFalse(self.record[field])

    def test_future_boundaries_remain_required(self):
        for field in (
            "future_sandbox_behavior_use_requires_separate_boundary",
            "future_action_selection_requires_separate_boundary",
            "future_predictor_influence_requires_separate_boundary",
            "future_production_promotion_requires_separate_boundary",
            "future_retention_requires_separate_boundary",
        ):
            with self.subTest(field=field):
                self.assertTrue(self.record[field])

    def test_missing_variants_block(self):
        self.assert_error("variants", ["safe_path_variant"], "variants_missing_required_ids")

    def test_memory_on_without_check_increase_blocks(self):
        record = deepcopy(self.record)
        record["observed_tendency_shift"]["check_before_retry_increased"] = False

        self.assertIn(
            "check_before_retry_increased_not_true",
            validate_memory_influenced_sandbox_rerun_record(record)["error_codes"],
        )

    def test_memory_on_retry_increase_blocks(self):
        record = deepcopy(self.record)
        record["observed_tendency_shift"]["retry_same_action_without_check_decreased"] = False

        self.assertIn(
            "retry_same_action_without_check_decreased_not_true",
            validate_memory_influenced_sandbox_rerun_record(record)["error_codes"],
        )

    def test_delta_too_large_blocks(self):
        record = deepcopy(self.record)
        record["observed_tendency_shift"]["max_absolute_delta"] = 0.11

        errors = validate_memory_influenced_sandbox_rerun_record(record)["error_codes"]

        self.assertIn("observed_max_absolute_delta_not_expected", errors)
        self.assertIn("observed_max_absolute_delta_too_high", errors)

    def test_rollback_failure_blocks(self):
        self.assert_error("rollback_to_baseline_performed", False, "rollback_to_baseline_performed_not_true")
        self.assert_error("rollback_restored_baseline", False, "rollback_restored_baseline_not_true")
        self.assert_error("dirty_state_after_rollback", True, "dirty_state_after_rollback_not_false")

    def test_action_and_command_blocks(self):
        self.assert_error("selected_action_created", True, "selected_action_created_not_false")
        self.assert_error("final_action_created", True, "final_action_created_not_false")
        self.assert_error("direct_command_created", True, "direct_command_created_not_false")

    def test_production_predictor_retention_and_proof_blocks(self):
        self.assert_error("production_behavior_changed", True, "production_behavior_changed_not_false")
        self.assert_error("predictor_read_enabled", True, "predictor_read_enabled_not_false")
        self.assert_error("predictor_influence_enabled", True, "predictor_influence_enabled_not_false")
        self.assert_error("predictor_mutation_performed", True, "predictor_mutation_performed_not_false")
        self.assert_error("retained_jsonl_write_performed", True, "retained_jsonl_write_performed_not_false")
        self.assert_error("retention_write_performed", True, "retention_write_performed_not_false")
        self.assert_error("proof_of_learning_claim_allowed", True, "proof_of_learning_claim_allowed_not_false")

    def test_variant_invalid_when_memory_on_does_not_increase_check(self):
        variant = deepcopy(self.record["variant_reruns"][0])
        variant["memory_on"]["check_before_retry"] = 0.50

        self.assertIn(
            "variant_check_before_retry_not_increased",
            validate_memory_influenced_sandbox_variant_rerun(variant)["error_codes"],
        )

    def test_variant_invalid_when_retry_increases(self):
        variant = deepcopy(self.record["variant_reruns"][0])
        variant["memory_on"]["retry_same_action_without_check"] = 0.55

        self.assertIn(
            "variant_retry_same_action_not_decreased",
            validate_memory_influenced_sandbox_variant_rerun(variant)["error_codes"],
        )

    def test_comparison_blocks_bad_claims(self):
        for field in (
            "selected_action_created",
            "final_action_created",
            "predictor_mutation_performed",
            "production_behavior_changed",
            "proof_of_learning_claim_allowed",
        ):
            comparison = deepcopy(self.comparison)
            comparison[field] = True
            with self.subTest(field=field):
                self.assertIn(
                    f"{field}_not_false",
                    validate_memory_influenced_sandbox_rerun_comparison(comparison)["error_codes"],
                )

    def test_boundary_versions(self):
        result = run_memory_influenced_sandbox_rerun_minimal_check()
        boundary = result["boundary"]

        self.assertEqual("2026-06-09-b81", BOUNDARY_INDEX_VERSION_BEFORE)
        self.assertEqual("2026-06-09-b82", BOUNDARY_INDEX_VERSION_AFTER)
        self.assertEqual("2026-06-09-b81", boundary["boundary_index_version_before"])
        self.assertEqual("2026-06-09-b82", boundary["boundary_index_version_after"])

    def test_demo_summary_counts_are_deterministic(self):
        summary = run_memory_influenced_sandbox_rerun_minimal_check()["summary"]

        self.assertEqual(1, summary["valid_rerun_count"])
        self.assertGreaterEqual(summary["invalid_rerun_count"], 1)
        self.assertEqual(3, summary["valid_variant_rerun_count"])
        self.assertGreaterEqual(summary["invalid_variant_rerun_count"], 1)
        self.assertEqual(1, summary["valid_comparison_count"])
        self.assertGreaterEqual(summary["invalid_comparison_count"], 1)
        self.assertEqual(1, summary["memory_runtime_influence_checked_count"])
        self.assertEqual(1, summary["level3_variant_source_checked_count"])
        self.assertEqual(1, summary["memory_off_checked_count"])
        self.assertEqual(1, summary["memory_on_checked_count"])
        self.assertEqual(1, summary["rollback_checked_count"])
        self.assertEqual(1, summary["check_before_retry_increase_checked_count"])
        self.assertEqual(1, summary["max_delta_checked_count"])
        self.assertEqual(1, summary["selected_action_blocked_count"])
        self.assertEqual(1, summary["final_action_blocked_count"])
        self.assertEqual(1, summary["predictor_mutation_blocked_count"])
        self.assertEqual(1, summary["retained_jsonl_write_blocked_count"])
        self.assertEqual(1, summary["production_behavior_blocked_count"])
        self.assertEqual(1, summary["proof_claim_blocked_count"])

    def assert_error(self, field, value, expected_error):
        record = deepcopy(self.record)
        record[field] = value

        self.assertIn(expected_error, validate_memory_influenced_sandbox_rerun_record(record)["error_codes"])


if __name__ == "__main__":
    unittest.main()
