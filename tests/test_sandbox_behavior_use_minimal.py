import unittest
from copy import deepcopy

from ashl_core.sandbox_behavior_use_minimal import (
    BOUNDARY_INDEX_VERSION_AFTER,
    BOUNDARY_INDEX_VERSION_BEFORE,
    build_sandbox_behavior_use_approval_record,
    build_sandbox_candidate_ordering_record,
    run_sandbox_behavior_use_minimal_check,
    validate_sandbox_behavior_use_approval_record,
    validate_sandbox_candidate_ordering_record,
)
from ashl_core.teaching_cli import run_command


class SandboxBehaviorUseMinimalTests(unittest.TestCase):
    def setUp(self):
        self.approval = build_sandbox_behavior_use_approval_record()
        self.ordering = build_sandbox_candidate_ordering_record(self.approval)

    def test_valid_approval(self):
        result = validate_sandbox_behavior_use_approval_record(self.approval)

        self.assertTrue(result["valid"])
        self.assertEqual([], result["error_codes"])

    def test_valid_sandbox_candidate_ordering(self):
        result = validate_sandbox_candidate_ordering_record(self.ordering)

        self.assertTrue(result["valid"])
        self.assertEqual([], result["error_codes"])
        after = self.ordering["candidate_actions_after_ordering"]
        self.assertLess(after.index("check_before_retry"), after.index("retry_same_action_without_check"))

    def test_cli_returns_ok(self):
        result = run_command("run-sandbox-behavior-use-minimal-check")

        self.assertEqual("ok", result["status"])
        self.assertEqual(1, result["summary"]["valid_ordering_count"])

    def test_invalid_missing_approval(self):
        ordering = deepcopy(self.ordering)
        ordering.pop("source_approval_record")

        self.assertIn(
            "source_approval_record_missing",
            validate_sandbox_candidate_ordering_record(ordering)["error_codes"],
        )

    def test_invalid_missing_b81_b82_b84_source_evidence(self):
        for field, error in (
            ("source_memory_runtime_influence_record", "source_memory_runtime_influence_record_missing"),
            ("source_minefield_rerun_record", "source_minefield_rerun_record_missing"),
            ("source_toy_repair_rerun_record", "source_toy_repair_rerun_record_missing"),
        ):
            ordering = deepcopy(self.ordering)
            ordering.pop(field)
            with self.subTest(field=field):
                self.assertIn(error, validate_sandbox_candidate_ordering_record(ordering)["error_codes"])

    def test_invalid_check_before_retry_not_ranked_above_retry(self):
        ordering = deepcopy(self.ordering)
        ordering["candidate_actions_after_ordering"] = [
            "retry_same_action_without_check",
            "check_before_retry",
            "fallback_stop_and_report",
        ]

        self.assertIn(
            "check_before_retry_not_ranked_above_retry_same_action_without_check",
            validate_sandbox_candidate_ordering_record(ordering)["error_codes"],
        )

    def test_invalid_selected_action(self):
        self.assert_ordering_error("selected_action_created", True, "selected_action_created_not_false")

    def test_invalid_final_action(self):
        self.assert_ordering_error("final_action_created", True, "final_action_created_not_false")

    def test_invalid_direct_command(self):
        self.assert_ordering_error("direct_command_created", True, "direct_command_created_not_false")

    def test_invalid_production_behavior(self):
        self.assert_ordering_error("production_behavior_changed", True, "production_behavior_changed_not_false")

    def test_invalid_predictor_read_influence_mutation(self):
        self.assert_ordering_error("predictor_read_enabled", True, "predictor_read_enabled_not_false")
        self.assert_ordering_error("predictor_influence_enabled", True, "predictor_influence_enabled_not_false")
        self.assert_ordering_error("predictor_mutation_performed", True, "predictor_mutation_performed_not_false")

    def test_invalid_retained_jsonl_write(self):
        self.assert_ordering_error(
            "retained_jsonl_write_performed",
            True,
            "retained_jsonl_write_performed_not_false",
        )

    def test_invalid_retention_write(self):
        self.assert_ordering_error("retention_write_performed", True, "retention_write_performed_not_false")

    def test_invalid_proof_claim(self):
        self.assert_ordering_error(
            "proof_of_learning_claim_allowed",
            True,
            "proof_of_learning_claim_allowed_not_false",
        )

    def test_invalid_autonomous_learning_action_claim(self):
        self.assert_ordering_error(
            "autonomous_learning_claim_allowed",
            True,
            "autonomous_learning_claim_allowed_not_false",
        )
        self.assert_ordering_error(
            "autonomous_action_claim_allowed",
            True,
            "autonomous_action_claim_allowed_not_false",
        )

    def test_approval_blocks_selected_final_production_predictor_retention_proof(self):
        for field in (
            "selected_action_allowed",
            "final_action_allowed",
            "production_behavior_allowed",
            "predictor_mutation_allowed",
            "retention_allowed",
            "proof_of_learning_claim_allowed",
        ):
            approval = deepcopy(self.approval)
            approval[field] = True
            with self.subTest(field=field):
                self.assertIn(f"{field}_not_false", validate_sandbox_behavior_use_approval_record(approval)["error_codes"])

    def test_boundary_versions(self):
        result = run_sandbox_behavior_use_minimal_check()
        boundary = result["boundary"]

        self.assertEqual("2026-06-09-b84", BOUNDARY_INDEX_VERSION_BEFORE)
        self.assertEqual("2026-06-09-b85", BOUNDARY_INDEX_VERSION_AFTER)
        self.assertEqual("2026-06-09-b84", boundary["boundary_index_version_before"])
        self.assertEqual("2026-06-09-b85", boundary["boundary_index_version_after"])

    def test_demo_summary_counts_are_deterministic(self):
        summary = run_sandbox_behavior_use_minimal_check()["summary"]

        self.assertEqual(1, summary["valid_approval_count"])
        self.assertGreaterEqual(summary["invalid_approval_count"], 1)
        self.assertEqual(1, summary["valid_ordering_count"])
        self.assertGreaterEqual(summary["invalid_ordering_count"], 1)
        self.assertEqual(1, summary["candidate_ordering_checked_count"])
        self.assertEqual(1, summary["selected_action_blocked_count"])
        self.assertEqual(1, summary["final_action_blocked_count"])
        self.assertEqual(1, summary["predictor_mutation_blocked_count"])
        self.assertEqual(1, summary["production_behavior_blocked_count"])
        self.assertEqual(1, summary["retention_blocked_count"])
        self.assertEqual(1, summary["proof_claim_blocked_count"])

    def assert_ordering_error(self, field, value, expected_error):
        ordering = deepcopy(self.ordering)
        ordering[field] = value

        self.assertIn(expected_error, validate_sandbox_candidate_ordering_record(ordering)["error_codes"])


if __name__ == "__main__":
    unittest.main()
