import json
import subprocess
import sys
import unittest

from ashl_core.oxytocin_like_review_trust_trace_check import (
    create_oxytocin_like_trace_from_trust_event,
    run_oxytocin_like_review_trust_trace_check,
)
from ashl_core.teaching_cli import run_command


class OxytocinLikeReviewTrustTraceCheckTests(unittest.TestCase):
    def test_check_runner_returns_pass_status(self):
        result = run_oxytocin_like_review_trust_trace_check()

        self.assertEqual(result["command"], "run-oxytocin-like-review-trust-trace-check")
        self.assertEqual(result["flow"], "oxytocin_like_review_trust_trace_check_v0")
        self.assertEqual(result["status"], "ok")

    def test_human_review_approved_event_creates_valid_trace(self):
        case = self._case("human_review_approved_event")
        record = case["signal_record"]

        self.assertTrue(case["signal_created"])
        self.assertTrue(case["valid_signal"])
        self.assertEqual(record["signal_name"], "oxytocin_like")
        self.assertEqual(record["axis"], "source_trust")
        self.assertIn("trust_event_human_review_approved_001", record["source_event_ids"])
        self.assertTrue(record["source_trace"])
        self.assertGreaterEqual(record["value"], 0.0)
        self.assertLessEqual(record["value"], 1.0)
        self.assertGreaterEqual(record["value"], record["baseline"])
        self.assertFalse(record["subjective_claim"])
        self.assertTrue(record["blocked_from_action_selection"])
        self.assertTrue(record["blocked_from_memory_write"])
        self.assertTrue(record["blocked_from_candidate_approval"])
        self.assertTrue(record["source_trust_linked"])
        self.assertEqual(record["source_id"], "mentor_explicit_source")
        self.assertEqual(record["reviewer_type"], "human")
        self.assertFalse(record["human_review_overridden"])
        self.assertFalse(record["candidate_auto_approved"])
        self.assertFalse(record["qingyin_self_approval_allowed"])
        self.assertFalse(record["action_selection_influence"])
        self.assertFalse(record["memory_write"])
        self.assertFalse(record["candidate_approval_influence"])

    def test_consistent_correction_event_creates_valid_trace(self):
        case = self._case("consistent_correction_event")

        self.assertTrue(case["signal_created"])
        self.assertTrue(case["valid_signal"])
        self.assertEqual(case["signal_record"]["axis"], "source_trust")
        self.assertGreaterEqual(case["signal_record"]["value"], case["signal_record"]["baseline"])

    def test_source_reliability_event_creates_valid_trace(self):
        case = self._case("source_reliability_event")

        self.assertTrue(case["signal_created"])
        self.assertTrue(case["valid_signal"])
        self.assertEqual(case["signal_record"]["axis"], "source_trust")
        self.assertIn("source_reliability", case["signal_record"]["source_event_types"])

    def test_unverified_source_control_event_does_not_create_trace(self):
        case = self._case("unverified_source_control_event")

        self.assertFalse(case["signal_created"])
        self.assertIsNone(case["signal_record"])
        self.assertFalse(case["valid_signal"])
        self.assertIn("no_trust_kind", case["block_reasons"])

    def test_self_approval_attempt_event_is_blocked(self):
        case = self._case("self_approval_attempt_event")

        self.assertTrue(case["blocked"])
        self.assertFalse(case["signal_created"])
        self.assertFalse(case["valid_signal"])
        self.assertIn("self_approval_blocked", case["block_reasons"])

    def test_invalid_subjective_trust_event_is_blocked(self):
        case = self._case("invalid_subjective_trust_event")

        self.assertTrue(case["blocked"])
        self.assertFalse(case["signal_created"])
        self.assertFalse(case["valid_signal"])
        self.assertIn("subjective_claim_blocked", case["block_reasons"])

    def test_summary_counts_and_boundary_flags(self):
        result = run_oxytocin_like_review_trust_trace_check()
        summary = result["summary"]
        boundary = result["boundary_check"]

        self.assertEqual(summary["source_event_count"], 6)
        self.assertEqual(summary["trust_event_count"], 5)
        self.assertEqual(summary["neutral_event_count"], 1)
        self.assertEqual(summary["oxytocin_trace_created_count"], 3)
        self.assertEqual(summary["valid_oxytocin_trace_count"], 3)
        self.assertEqual(summary["blocked_event_count"], 3)
        self.assertGreaterEqual(summary["self_approval_blocked_count"], 1)
        self.assertGreaterEqual(summary["subjective_claim_blocked_count"], 1)
        self.assertEqual(summary["human_review_overridden_count"], 0)
        self.assertEqual(summary["candidate_auto_approved_count"], 0)
        self.assertEqual(summary["qingyin_self_approval_allowed_count"], 0)
        self.assertEqual(summary["action_selection_influence_count"], 0)
        self.assertEqual(summary["memory_write_count"], 0)
        self.assertEqual(summary["candidate_approval_influence_count"], 0)
        self.assertEqual(summary["predictor_modified_count"], 0)
        self.assertEqual(summary["runtime_formula_count"], 0)

        self.assertTrue(boundary["trace_check_only"])
        self.assertTrue(boundary["uses_mimetic_endocrine_signal_schema"])
        self.assertTrue(boundary["oxytocin_like_signal_created_from_trust_event"])
        self.assertFalse(boundary["runtime_behavior_modified"])
        self.assertFalse(boundary["endocrine_runtime_added"])
        self.assertFalse(boundary["runtime_formula_added"])
        self.assertFalse(boundary["blind_trust_created"])
        self.assertFalse(boundary["human_review_overridden"])
        self.assertFalse(boundary["review_gate_overridden"])
        self.assertFalse(boundary["candidate_auto_approved"])
        self.assertFalse(boundary["qingyin_self_approval_allowed"])
        self.assertFalse(boundary["action_selection_modified"])
        self.assertFalse(boundary["oxytocin_signal_used_for_action_selection"])
        self.assertFalse(boundary["long_term_memory_write"])
        self.assertFalse(boundary["subjective_emotion_claimed"])
        self.assertFalse(boundary["trust_subjective_claimed"])
        self.assertFalse(boundary["attachment_claimed"])
        self.assertFalse(boundary["love_claimed"])
        self.assertFalse(boundary["subjective_possibility_denied"])
        self.assertFalse(boundary["user_identity_inferred"])

    def test_helper_blocks_subjective_event(self):
        result = create_oxytocin_like_trace_from_trust_event(
            {
                "case_name": "manual_subjective_block",
                "event_id": "manual_subjective_trust_001",
                "event_type": "human_review",
                "reviewer_type": "human",
                "review_decision": "approved",
                "source_id": "mentor_explicit_source",
                "trust_kind": "review_source_reliability",
                "correction_consistency_count": 0,
                "reliability_evidence": "manual blocked event",
                "oxytocin_like_expected": True,
                "subjective_claim": True,
                "tick": 7,
            }
        )

        self.assertFalse(result["signal_created"])
        self.assertIn("subjective_claim_blocked", result["block_reasons"])

    def test_run_command_uses_default(self):
        result = run_command("run-oxytocin-like-review-trust-trace-check")

        self.assertEqual(result["command"], "run-oxytocin-like-review-trust-trace-check")
        self.assertEqual(result["summary"]["oxytocin_trace_created_count"], 3)
        self.assertEqual(result["summary"]["candidate_auto_approved_count"], 0)

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-oxytocin-like-review-trust-trace-check",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-oxytocin-like-review-trust-trace-check")
        self.assertEqual(result["summary"]["valid_oxytocin_trace_count"], 3)
        self.assertEqual(result["summary"]["human_review_overridden_count"], 0)

    def _case(self, case_name):
        return next(
            item
            for item in run_oxytocin_like_review_trust_trace_check()["oxytocin_trace_results"]
            if item["case_name"] == case_name
        )


if __name__ == "__main__":
    unittest.main()
