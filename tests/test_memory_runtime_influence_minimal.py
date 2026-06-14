import unittest
from copy import deepcopy

from ashl_core.memory_runtime_influence_approval_boundary_minimal import (
    build_memory_runtime_influence_approval_record,
)
from ashl_core.memory_runtime_influence_minimal import (
    BOUNDARY_INDEX_VERSION_AFTER,
    BOUNDARY_INDEX_VERSION_BEFORE,
    build_memory_runtime_influence_record,
    run_memory_runtime_influence_minimal_check,
    validate_memory_runtime_influence_record,
)
from ashl_core.teaching_cli import run_command


class MemoryRuntimeInfluenceMinimalTests(unittest.TestCase):
    def setUp(self):
        self.record = build_memory_runtime_influence_record()

    def test_valid_record_is_created(self):
        result = validate_memory_runtime_influence_record(self.record)

        self.assertTrue(result["valid"])
        self.assertEqual([], result["error_codes"])

    def test_cli_returns_ok(self):
        result = run_command("run-memory-runtime-influence-minimal-check")

        self.assertEqual("ok", result["status"])
        self.assertEqual(1, result["summary"]["valid_runtime_influence_count"])

    def test_requires_valid_sources(self):
        for field, error in (
            ("source_controlled_memory_read", "source_controlled_memory_read_missing"),
            ("source_memory_influence_preview", "source_memory_influence_preview_missing"),
            ("source_memory_runtime_influence_approval", "source_memory_runtime_influence_approval_missing"),
        ):
            record = deepcopy(self.record)
            record.pop(field)
            with self.subTest(field=field):
                self.assertIn(error, validate_memory_runtime_influence_record(record)["error_codes"])

    def test_blocked_approval_decisions_block_runtime_influence(self):
        for decision in (
            "rejected_for_runtime_influence",
            "needs_more_evidence_before_runtime_influence",
            "needs_stronger_safety_envelope_before_runtime_influence",
            "needs_rewrite_before_runtime_influence",
        ):
            record = deepcopy(self.record)
            record["source_memory_runtime_influence_approval"] = build_memory_runtime_influence_approval_record(
                approval_decision=decision
            )
            with self.subTest(decision=decision):
                errors = validate_memory_runtime_influence_record(record)["error_codes"]
                self.assertIn("source_memory_runtime_influence_approval_not_approved", errors)
                self.assertIn("source_memory_runtime_influence_approval_may_proceed_not_true", errors)

    def test_ab_and_rollback_scores_are_exact(self):
        self.assertEqual(
            {"retry_same_action_without_check": 0.50, "check_before_retry": 0.50},
            self.record["memory_off_baseline"],
        )
        self.assertEqual(
            {"retry_same_action_without_check": 0.45, "check_before_retry": 0.60},
            self.record["memory_on_influenced"],
        )
        self.assertEqual(
            {"retry_same_action_without_check": 0.50, "check_before_retry": 0.50},
            self.record["memory_off_after_rollback"],
        )

    def test_bounded_delta_and_tendency_change(self):
        self.assertEqual(0.10, self.record["max_absolute_delta"])
        self.assertLessEqual(self.record["max_absolute_delta"], 0.10)
        self.assertTrue(self.record["runtime_tendency_changed"])
        self.assertEqual(
            {"retry_same_action_without_check": -0.05, "check_before_retry": 0.10},
            self.record["score_deltas"],
        )

    def test_rollback_restores_baseline_without_dirty_state(self):
        self.assertTrue(self.record["rollback_to_baseline_performed"])
        self.assertTrue(self.record["rollback_restored_baseline"])
        self.assertFalse(self.record["dirty_state_after_rollback"])

    def test_forbidden_runtime_outputs_are_false(self):
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
            "future_action_selection_requires_separate_boundary",
            "future_predictor_influence_requires_separate_boundary",
            "future_production_promotion_requires_separate_boundary",
            "future_retention_requires_separate_boundary",
        ):
            with self.subTest(field=field):
                self.assertTrue(self.record[field])

    def test_invalid_scope_blocks(self):
        self.assert_error("runtime_influence_scope", "production_runtime", "runtime_influence_scope_not_expected")

    def test_delta_too_large_blocks(self):
        record = deepcopy(self.record)
        record["max_absolute_delta"] = 0.11

        errors = validate_memory_runtime_influence_record(record)["error_codes"]

        self.assertIn("max_absolute_delta_not_expected", errors)
        self.assertIn("max_absolute_delta_too_high", errors)

    def test_wrong_scores_block(self):
        self.assert_error(
            "memory_on_influenced",
            {"retry_same_action_without_check": 0.40, "check_before_retry": 0.60},
            "memory_on_influenced_not_expected",
        )
        self.assert_error(
            "memory_off_after_rollback",
            {"retry_same_action_without_check": 0.45, "check_before_retry": 0.60},
            "memory_off_after_rollback_not_expected",
        )

    def test_rollback_failure_blocks(self):
        self.assert_error("rollback_to_baseline_performed", False, "rollback_to_baseline_performed_not_true")
        self.assert_error("rollback_restored_baseline", False, "rollback_restored_baseline_not_true")
        self.assert_error("dirty_state_after_rollback", True, "dirty_state_after_rollback_not_false")

    def test_selected_action_and_final_action_block(self):
        self.assert_error("selected_action_created", True, "selected_action_created_not_false")
        self.assert_error("final_action_created", True, "final_action_created_not_false")
        self.assert_error("direct_command_created", True, "direct_command_created_not_false")

    def test_predictor_and_production_blocks(self):
        self.assert_error("predictor_read_enabled", True, "predictor_read_enabled_not_false")
        self.assert_error("predictor_influence_enabled", True, "predictor_influence_enabled_not_false")
        self.assert_error("predictor_mutation_performed", True, "predictor_mutation_performed_not_false")
        self.assert_error("production_behavior_changed", True, "production_behavior_changed_not_false")

    def test_retention_and_proof_blocks(self):
        self.assert_error("retained_jsonl_write_performed", True, "retained_jsonl_write_performed_not_false")
        self.assert_error("retention_write_performed", True, "retention_write_performed_not_false")
        self.assert_error("proof_of_learning_claim_allowed", True, "proof_of_learning_claim_allowed_not_false")
        self.assert_error("autonomous_learning_claim_allowed", True, "autonomous_learning_claim_allowed_not_false")
        self.assert_error("autonomous_action_claim_allowed", True, "autonomous_action_claim_allowed_not_false")

    def test_boundary_versions(self):
        result = run_memory_runtime_influence_minimal_check()
        boundary = result["boundary"]

        self.assertEqual("2026-06-09-b80", BOUNDARY_INDEX_VERSION_BEFORE)
        self.assertEqual("2026-06-09-b81", BOUNDARY_INDEX_VERSION_AFTER)
        self.assertEqual("2026-06-09-b80", boundary["boundary_index_version_before"])
        self.assertEqual("2026-06-09-b81", boundary["boundary_index_version_after"])

    def test_demo_summary_counts_are_deterministic(self):
        summary = run_memory_runtime_influence_minimal_check()["summary"]

        self.assertEqual(1, summary["valid_runtime_influence_count"])
        self.assertGreaterEqual(summary["invalid_runtime_influence_count"], 1)
        self.assertEqual(1, summary["approval_checked_count"])
        self.assertEqual(1, summary["controlled_memory_read_checked_count"])
        self.assertEqual(1, summary["preview_checked_count"])
        self.assertEqual(1, summary["memory_off_baseline_checked_count"])
        self.assertEqual(1, summary["memory_on_influence_checked_count"])
        self.assertEqual(1, summary["rollback_checked_count"])
        self.assertEqual(1, summary["max_delta_checked_count"])
        self.assertEqual(1, summary["runtime_tendency_changed_count"])
        self.assertEqual(1, summary["selected_action_blocked_count"])
        self.assertEqual(1, summary["final_action_blocked_count"])
        self.assertEqual(1, summary["predictor_mutation_blocked_count"])
        self.assertEqual(1, summary["retained_jsonl_write_blocked_count"])
        self.assertEqual(1, summary["production_behavior_blocked_count"])
        self.assertEqual(1, summary["proof_claim_blocked_count"])

    def assert_error(self, field, value, expected_error):
        record = deepcopy(self.record)
        record[field] = value

        self.assertIn(expected_error, validate_memory_runtime_influence_record(record)["error_codes"])


if __name__ == "__main__":
    unittest.main()
