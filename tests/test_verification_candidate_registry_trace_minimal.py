import unittest
from copy import deepcopy

from ashl_core.doubt_gated_sandbox_candidate_ordering_minimal import (
    build_doubt_gated_candidate_ordering_record,
)
from ashl_core.teaching_cli import run_command
from ashl_core.verification_candidate_registry_trace_minimal import (
    BOUNDARY_INDEX_VERSION_AFTER,
    BOUNDARY_INDEX_VERSION_BEFORE,
    REQUIRED_CANDIDATE_IDS,
    build_verification_candidate,
    build_verification_candidate_registry,
    build_verification_candidate_trace,
    run_verification_candidate_registry_trace_minimal_check,
    validate_doubt_gated_ordering_uses_registered_candidate,
    validate_verification_candidate,
    validate_verification_candidate_registry,
    validate_verification_candidate_trace,
)


class VerificationCandidateRegistryTraceMinimalTests(unittest.TestCase):
    def test_valid_required_registry(self):
        registry = build_verification_candidate_registry()
        result = validate_verification_candidate_registry(registry)

        self.assertTrue(result["valid"])
        self.assertEqual(5, registry["candidate_count"])
        self.assertEqual(REQUIRED_CANDIDATE_IDS, registry["candidate_ids"])
        self.assertTrue(registry["all_candidates_trace_only"])
        self.assertTrue(registry["all_candidates_execution_blocked"])
        self.assertFalse(registry["free_form_candidates_allowed"])

    def test_valid_each_required_candidate(self):
        for candidate_id in REQUIRED_CANDIDATE_IDS:
            with self.subTest(candidate_id=candidate_id):
                candidate = build_verification_candidate(candidate_id)
                result = validate_verification_candidate(candidate)

                self.assertTrue(result["valid"])
                self.assertEqual(candidate_id, candidate["candidate_id"])
                self.assertFalse(candidate["execution_allowed"])
                self.assertTrue(candidate["trace_only"])
                self.assertFalse(candidate["llm_used"])

    def test_valid_trace_using_registered_candidate(self):
        trace = build_verification_candidate_trace("observe_or_alternative_probe")
        result = validate_verification_candidate_trace(trace)

        self.assertTrue(result["valid"])
        self.assertTrue(trace["candidate_found_in_registry"])
        self.assertEqual("low", trace["candidate_risk_level"])
        self.assertFalse(trace["verification_action_executed"])
        self.assertTrue(trace["ordering_reference_only"])

    def test_valid_b87_ordering_references_registered_candidate(self):
        result = validate_doubt_gated_ordering_uses_registered_candidate()

        self.assertTrue(result["valid"])
        self.assertIn("observe_or_alternative_probe", result["referenced_candidates"])
        self.assertEqual([], result["unregistered_candidates"])

    def test_cli_command_returns_ok(self):
        result = run_command("run-verification-candidate-registry-trace-minimal-check")

        self.assertEqual("ok", result["status"])
        self.assertEqual(5, result["summary"]["valid_candidate_count"])

    def test_boundary_versions(self):
        result = run_verification_candidate_registry_trace_minimal_check()

        self.assertEqual("2026-06-09-b87", BOUNDARY_INDEX_VERSION_BEFORE)
        self.assertEqual("2026-06-09-b88", BOUNDARY_INDEX_VERSION_AFTER)
        self.assertEqual("2026-06-09-b87", result["boundary"]["boundary_index_version_before"])
        self.assertEqual("2026-06-09-b88", result["boundary"]["boundary_index_version_after"])

    def test_invalid_missing_risk_level(self):
        self.assertInvalidCandidate("risk_level", None)

    def test_invalid_missing_stop_condition(self):
        self.assertInvalidCandidate("stop_condition", "")

    def test_invalid_missing_expected_probe_outcome(self):
        self.assertInvalidCandidate("expected_probe_outcome", "")

    def test_invalid_missing_allowed_scope(self):
        self.assertInvalidCandidate("allowed_sandbox_scope", [])

    def test_invalid_unregistered_candidate(self):
        candidate = build_verification_candidate("free_form_probe")

        self.assertFalse(validate_verification_candidate(candidate)["valid"])

    def test_invalid_free_form_candidate(self):
        self.assertInvalidCandidate("candidate_type", "free_form_candidate")

    def test_invalid_llm_used_true(self):
        self.assertInvalidCandidate("llm_used", True)

    def test_invalid_execution_allowed_true(self):
        self.assertInvalidCandidate("execution_allowed", True)

    def test_invalid_retry_limited_max_attempts_over_one(self):
        candidate = build_verification_candidate("retry_limited")
        candidate["max_attempts"] = 2

        self.assertFalse(validate_verification_candidate(candidate)["valid"])

    def test_invalid_low_risk_irreversible_without_justification(self):
        self.assertInvalidCandidate("reversible", False)

    def test_invalid_b87_ordering_references_unregistered_candidate(self):
        ordering = build_doubt_gated_candidate_ordering_record()
        ordering["candidate_actions_after_ordering"] = ["free_form_probe", "retry_same_action_without_check"]
        result = validate_doubt_gated_ordering_uses_registered_candidate(ordering)

        self.assertFalse(result["valid"])
        self.assertTrue(result["unregistered_candidate_blocked"])

    def test_invalid_verification_executed(self):
        self.assertInvalidTrace("verification_action_executed", True)

    def test_invalid_selected_action(self):
        self.assertInvalidTrace("selected_action_created", True)

    def test_invalid_final_action(self):
        self.assertInvalidTrace("final_action_created", True)

    def test_invalid_persistent_rule(self):
        self.assertInvalidTrace("persistent_rule_created", True)

    def test_invalid_memory_write(self):
        self.assertInvalidTrace("long_term_memory_write_performed", True)
        self.assertInvalidTrace("retained_jsonl_write_performed", True)

    def test_invalid_retention_write(self):
        self.assertInvalidTrace("retention_write_performed", True)

    def test_invalid_predictor_mutation(self):
        self.assertInvalidTrace("predictor_mutation_performed", True)

    def test_invalid_production_behavior(self):
        self.assertInvalidTrace("production_behavior_changed", True)

    def test_invalid_proof_claim(self):
        self.assertInvalidTrace("proof_of_learning_claim_allowed", True)

    def test_invalid_autonomous_learning_action_claim(self):
        self.assertInvalidTrace("autonomous_learning_claim_allowed", True)
        self.assertInvalidTrace("autonomous_action_claim_allowed", True)

    def test_summary_counts_are_deterministic(self):
        result = run_verification_candidate_registry_trace_minimal_check()
        summary = result["summary"]

        self.assertEqual("ok", result["status"])
        self.assertEqual(5, summary["valid_candidate_count"])
        self.assertGreaterEqual(summary["invalid_candidate_count"], 12)
        self.assertEqual(1, summary["valid_registry_count"])
        self.assertGreaterEqual(summary["invalid_registry_count"], 9)
        self.assertEqual(1, summary["valid_trace_count"])
        self.assertGreaterEqual(summary["invalid_trace_count"], 16)
        self.assertEqual(1, summary["registered_candidate_checked_count"])
        self.assertEqual(1, summary["b87_ordering_reference_checked_count"])
        self.assertEqual(1, summary["unregistered_candidate_blocked_count"])
        self.assertEqual(1, summary["free_form_candidate_blocked_count"])
        self.assertEqual(1, summary["execution_blocked_count"])
        self.assertEqual(1, summary["selected_action_blocked_count"])
        self.assertEqual(1, summary["final_action_blocked_count"])
        self.assertEqual(1, summary["persistent_rule_blocked_count"])
        self.assertEqual(1, summary["memory_write_blocked_count"])
        self.assertEqual(1, summary["retention_blocked_count"])
        self.assertEqual(1, summary["predictor_mutation_blocked_count"])
        self.assertEqual(1, summary["proof_claim_blocked_count"])
        self.assertTrue(summary["all_verification_candidate_registry_trace_checks_passed"])

    def assertInvalidCandidate(self, field, value):
        candidate = deepcopy(build_verification_candidate("observe_or_alternative_probe"))
        candidate[field] = value

        self.assertFalse(validate_verification_candidate(candidate)["valid"])

    def assertInvalidTrace(self, field, value):
        trace = deepcopy(build_verification_candidate_trace("observe_or_alternative_probe"))
        trace[field] = value

        self.assertFalse(validate_verification_candidate_trace(trace)["valid"])


if __name__ == "__main__":
    unittest.main()
