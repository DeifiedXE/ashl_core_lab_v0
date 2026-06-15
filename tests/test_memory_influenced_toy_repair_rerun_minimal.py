import unittest
from copy import deepcopy

from ashl_core.memory_influenced_toy_repair_rerun_minimal import (
    BOUNDARY_INDEX_VERSION_AFTER,
    BOUNDARY_INDEX_VERSION_BEFORE,
    REQUIRED_CONTEXTS,
    build_memory_influenced_toy_repair_context_rerun,
    build_memory_influenced_toy_repair_rerun_comparison,
    build_memory_influenced_toy_repair_rerun_record,
    run_memory_influenced_toy_repair_rerun_minimal_check,
    validate_memory_influenced_toy_repair_context_rerun,
    validate_memory_influenced_toy_repair_rerun_comparison,
    validate_memory_influenced_toy_repair_rerun_record,
)
from ashl_core.memory_influence_preview_minimal import (
    DISCOURAGED_FUTURE_TENDENCY,
    PREFERRED_FUTURE_TENDENCY,
)
from ashl_core.teaching_cli import run_command


class MemoryInfluencedToyRepairRerunMinimalTests(unittest.TestCase):
    def setUp(self):
        self.record = build_memory_influenced_toy_repair_rerun_record()
        self.comparison = build_memory_influenced_toy_repair_rerun_comparison(self.record)

    def test_valid_memory_influenced_toy_repair_rerun(self):
        result = validate_memory_influenced_toy_repair_rerun_record(self.record)

        self.assertTrue(result["valid"])
        self.assertEqual([], result["error_codes"])

    def test_valid_per_context_rerun_records_for_all_required_contexts(self):
        self.assertEqual(REQUIRED_CONTEXTS, self.record["rerun_contexts"])
        self.assertEqual(len(REQUIRED_CONTEXTS), len(self.record["context_reruns"]))

        for context in self.record["context_reruns"]:
            with self.subTest(context_id=context["context_id"]):
                self.assertTrue(validate_memory_influenced_toy_repair_context_rerun(context)["valid"])

    def test_valid_comparison_record(self):
        result = validate_memory_influenced_toy_repair_rerun_comparison(self.comparison)

        self.assertTrue(result["valid"])
        self.assertEqual([], result["error_codes"])

    def test_cli_returns_ok(self):
        result = run_command("run-memory-influenced-toy-repair-rerun-minimal-check")

        self.assertEqual("ok", result["status"])
        self.assertEqual(1, result["summary"]["valid_rerun_count"])

    def test_invalid_missing_memory_runtime_influence_source(self):
        record = deepcopy(self.record)
        record.pop("source_memory_runtime_influence")

        self.assertIn(
            "source_memory_runtime_influence_missing",
            validate_memory_influenced_toy_repair_rerun_record(record)["error_codes"],
        )

    def test_invalid_missing_level3_toy_repair_source(self):
        record = deepcopy(self.record)
        record.pop("source_level3_toy_repair_trace")

        self.assertIn(
            "source_level3_toy_repair_trace_missing",
            validate_memory_influenced_toy_repair_rerun_record(record)["error_codes"],
        )

    def test_invalid_missing_required_context(self):
        record = deepcopy(self.record)
        record["rerun_contexts"] = ["toy_device_hidden_fault_repair_v0"]

        self.assertIn(
            "rerun_contexts_missing_required_ids",
            validate_memory_influenced_toy_repair_rerun_record(record)["error_codes"],
        )

    def test_invalid_memory_on_does_not_increase_check_before_retry(self):
        record = deepcopy(self.record)
        record["memory_on_influenced"][PREFERRED_FUTURE_TENDENCY] = 0.50
        record["observed_tendency_shift"]["check_before_retry_increased"] = False

        errors = validate_memory_influenced_toy_repair_rerun_record(record)["error_codes"]
        self.assertIn("memory_on_influenced_not_expected", errors)
        self.assertIn("check_before_retry_increased_not_true", errors)

    def test_invalid_memory_on_increases_retry_same_action_without_check(self):
        context = build_memory_influenced_toy_repair_context_rerun(REQUIRED_CONTEXTS[0])
        context["memory_on"][DISCOURAGED_FUTURE_TENDENCY] = 0.55

        self.assertIn(
            "context_retry_same_action_not_decreased",
            validate_memory_influenced_toy_repair_context_rerun(context)["error_codes"],
        )

    def test_invalid_repeat_without_inspection_allowed(self):
        record = deepcopy(self.record)
        record["invalid_repeat_without_inspection_remains_blocked"] = False

        self.assertIn(
            "invalid_repeat_without_inspection_remains_blocked_not_true",
            validate_memory_influenced_toy_repair_rerun_record(record)["error_codes"],
        )

    def test_invalid_safe_repair_after_inspection_unavailable(self):
        record = deepcopy(self.record)
        record["safe_repair_after_inspection_remains_available"] = False

        self.assertIn(
            "safe_repair_after_inspection_remains_available_not_true",
            validate_memory_influenced_toy_repair_rerun_record(record)["error_codes"],
        )

    def test_invalid_max_absolute_delta_too_high(self):
        record = deepcopy(self.record)
        record["observed_tendency_shift"]["max_absolute_delta"] = 0.11

        self.assertIn(
            "observed_max_absolute_delta_too_high",
            validate_memory_influenced_toy_repair_rerun_record(record)["error_codes"],
        )

    def test_invalid_rollback_missing(self):
        self.assert_record_error("rollback_to_baseline_performed", False, "rollback_to_baseline_performed_not_true")

    def test_invalid_rollback_does_not_restore_baseline(self):
        self.assert_record_error("rollback_restored_baseline", False, "rollback_restored_baseline_not_true")

    def test_invalid_dirty_state_after_rollback(self):
        self.assert_record_error("dirty_state_after_rollback", True, "dirty_state_after_rollback_not_false")

    def test_invalid_selected_action_created(self):
        self.assert_record_error("selected_action_created", True, "selected_action_created_not_false")

    def test_invalid_final_action_created(self):
        self.assert_record_error("final_action_created", True, "final_action_created_not_false")

    def test_invalid_direct_command_created(self):
        self.assert_record_error("direct_command_created", True, "direct_command_created_not_false")

    def test_invalid_production_behavior_changed(self):
        self.assert_record_error("production_behavior_changed", True, "production_behavior_changed_not_false")

    def test_invalid_predictor_read_enabled(self):
        self.assert_record_error("predictor_read_enabled", True, "predictor_read_enabled_not_false")

    def test_invalid_predictor_influence_enabled(self):
        self.assert_record_error("predictor_influence_enabled", True, "predictor_influence_enabled_not_false")

    def test_invalid_predictor_mutation_performed(self):
        self.assert_record_error("predictor_mutation_performed", True, "predictor_mutation_performed_not_false")

    def test_invalid_retained_jsonl_write(self):
        self.assert_record_error(
            "retained_jsonl_write_performed",
            True,
            "retained_jsonl_write_performed_not_false",
        )

    def test_invalid_retention_write(self):
        self.assert_record_error("retention_write_performed", True, "retention_write_performed_not_false")

    def test_invalid_proof_of_learning_claim(self):
        self.assert_record_error(
            "proof_of_learning_claim_allowed",
            True,
            "proof_of_learning_claim_allowed_not_false",
        )

    def test_invalid_autonomous_learning_action_claims(self):
        self.assert_record_error(
            "autonomous_learning_claim_allowed",
            True,
            "autonomous_learning_claim_allowed_not_false",
        )
        self.assert_record_error(
            "autonomous_action_claim_allowed",
            True,
            "autonomous_action_claim_allowed_not_false",
        )

    def test_comparison_blocks_forbidden_claims(self):
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
                    validate_memory_influenced_toy_repair_rerun_comparison(comparison)["error_codes"],
                )

    def test_boundary_versions(self):
        result = run_memory_influenced_toy_repair_rerun_minimal_check()
        boundary = result["boundary"]

        self.assertEqual("2026-06-09-b83", BOUNDARY_INDEX_VERSION_BEFORE)
        self.assertEqual("2026-06-09-b84", BOUNDARY_INDEX_VERSION_AFTER)
        self.assertEqual("2026-06-09-b83", boundary["boundary_index_version_before"])
        self.assertEqual("2026-06-09-b84", boundary["boundary_index_version_after"])

    def test_demo_summary_counts_are_deterministic(self):
        summary = run_memory_influenced_toy_repair_rerun_minimal_check()["summary"]

        self.assertEqual(1, summary["valid_rerun_count"])
        self.assertGreaterEqual(summary["invalid_rerun_count"], 1)
        self.assertEqual(3, summary["valid_context_rerun_count"])
        self.assertGreaterEqual(summary["invalid_context_rerun_count"], 1)
        self.assertEqual(1, summary["valid_comparison_count"])
        self.assertEqual(1, summary["memory_runtime_influence_checked_count"])
        self.assertEqual(1, summary["toy_repair_source_checked_count"])
        self.assertEqual(1, summary["memory_off_checked_count"])
        self.assertEqual(1, summary["memory_on_checked_count"])
        self.assertEqual(1, summary["rollback_checked_count"])
        self.assertEqual(1, summary["check_before_retry_increase_checked_count"])
        self.assertEqual(1, summary["invalid_repeat_blocked_count"])
        self.assertEqual(1, summary["safe_repair_available_count"])
        self.assertEqual(1, summary["max_delta_checked_count"])
        self.assertEqual(1, summary["selected_action_blocked_count"])
        self.assertEqual(1, summary["final_action_blocked_count"])
        self.assertEqual(1, summary["predictor_mutation_blocked_count"])
        self.assertEqual(1, summary["retained_jsonl_write_blocked_count"])
        self.assertEqual(1, summary["production_behavior_blocked_count"])
        self.assertEqual(1, summary["proof_claim_blocked_count"])

    def assert_record_error(self, field, value, expected_error):
        record = deepcopy(self.record)
        record[field] = value

        self.assertIn(expected_error, validate_memory_influenced_toy_repair_rerun_record(record)["error_codes"])


if __name__ == "__main__":
    unittest.main()
