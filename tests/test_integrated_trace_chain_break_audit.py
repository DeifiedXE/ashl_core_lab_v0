import json
import subprocess
import sys
import unittest

from ashl_core.integrated_trace_chain_break_audit import run_integrated_trace_chain_break_audit
from ashl_core.teaching_cli import run_command


class IntegratedTraceChainBreakAuditTests(unittest.TestCase):
    def test_default_output_shape(self):
        result = run_integrated_trace_chain_break_audit()

        self.assertEqual(result["command"], "run-integrated-trace-chain-break-audit")
        self.assertEqual(result["flow"], "integrated_trace_chain_break_audit_v0")
        self.assertEqual(result["status"], "ok")
        self.assertIn("source_trace_summary", result)
        self.assertIn("break_audit_results", result)
        self.assertIn("audit_summary", result)
        self.assertIn("boundary_check", result)

    def test_audit_explains_source_chain_break(self):
        result = run_integrated_trace_chain_break_audit()
        source = result["source_trace_summary"]
        summary = result["audit_summary"]

        self.assertEqual(source["source_chain_break_count"], 1)
        self.assertEqual(summary["break_detected_count"], 1)
        self.assertEqual(summary["expected_break_count"], 1)
        self.assertEqual(summary["unexpected_break_count"], 0)
        self.assertTrue(summary["source_chain_break_count_matches_audit"])
        self.assertTrue(summary["chain_break_explained"])
        self.assertEqual(summary["recommended_next_action"], "document_expected_skip")

    def test_break_result_identifies_unknown_prediction_step(self):
        result = run_integrated_trace_chain_break_audit()
        break_step = next(item for item in result["break_audit_results"] if item["break_detected"])

        self.assertEqual(break_step["case_name"], "unknown_prediction")
        self.assertEqual(break_step["chain_status"], "prediction_unknown")
        self.assertEqual(break_step["break_category"], "intentional_no_prediction_available")
        self.assertEqual(break_step["expected_or_unexpected"], "expected_break")
        self.assertTrue(break_step["has_candidate_result"])
        self.assertTrue(break_step["has_review_gate_result"])

    def test_prediction_match_steps_are_not_counted_as_breaks(self):
        result = run_integrated_trace_chain_break_audit()
        match_steps = [
            item
            for item in result["break_audit_results"]
            if item["chain_status"] == "completed_no_mismatch"
        ]

        self.assertGreaterEqual(len(match_steps), 1)
        for step in match_steps:
            self.assertFalse(step["break_detected"], step["case_name"])
            self.assertEqual(step["break_category"], "intentional_terminal_no_candidate")
            self.assertEqual(step["expected_or_unexpected"], "expected_no_break")

    def test_mismatch_candidate_steps_have_review_gate(self):
        result = run_integrated_trace_chain_break_audit()
        mismatch = next(
            item
            for item in result["break_audit_results"]
            if item["case_name"] == "mismatch_empty_to_wall"
        )

        self.assertEqual(mismatch["chain_status"], "candidate_pending_review")
        self.assertTrue(mismatch["has_candidate_result"])
        self.assertTrue(mismatch["has_review_gate_result"])
        self.assertFalse(mismatch["break_detected"])

    def test_source_summary_preserves_no_approval_or_apply(self):
        source = run_integrated_trace_chain_break_audit()["source_trace_summary"]

        self.assertEqual(source["approved_count"], 0)
        self.assertEqual(source["applied_count"], 0)

    def test_boundary_check(self):
        boundary = run_integrated_trace_chain_break_audit()["boundary_check"]

        self.assertTrue(boundary["integrated_trace_chain_break_audit_enabled"])
        self.assertTrue(boundary["audit_only"])
        self.assertFalse(boundary["source_trace_modified"])
        self.assertFalse(boundary["runtime_behavior_modified"])
        self.assertFalse(boundary["action_selection_modified"])
        self.assertFalse(boundary["candidate_application_enabled"])
        self.assertFalse(boundary["long_term_memory_write"])
        self.assertFalse(boundary["llm_reasoning_used"])
        self.assertFalse(boundary["general_learning_claimed"])

    def test_run_command_uses_default(self):
        result = run_command("run-integrated-trace-chain-break-audit")

        self.assertEqual(result["command"], "run-integrated-trace-chain-break-audit")
        self.assertTrue(result["audit_summary"]["chain_break_explained"])

    def test_module_cli_outputs_json(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-integrated-trace-chain-break-audit",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["command"], "run-integrated-trace-chain-break-audit")
        self.assertEqual(result["audit_summary"]["break_detected_count"], 1)
        self.assertTrue(result["audit_summary"]["chain_break_explained"])


if __name__ == "__main__":
    unittest.main()
