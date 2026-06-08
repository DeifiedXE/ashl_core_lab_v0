import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ashl_core.teaching_cli import (
    run_conflict_check_flow,
    run_clear_sandbox_working_state,
    run_disable_reenable_flow,
    run_grounded_learning_check,
    run_known_flow,
    run_minimal_interaction,
    run_need_state_trial_batch_cli,
    run_tactile_interaction,
    run_unknown_flow,
)
from ashl_core.first_output_runtime import UTTERANCE_MAP


class TeachingCliTests(unittest.TestCase):
    def test_teaching_cli_known_flow_succeeds(self):
        result = run_known_flow()

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["failure_reason"], "not_facing_east")
        self.assertIsNotNone(result["lesson"])
        self.assertEqual(result["generation_status"], "supported_failure_reason")
        self.assertEqual(result["behavior_before"], "failed")
        self.assertEqual(result["behavior_after"], "success")
        self.assertTrue(result["conflict_check"]["implemented"])
        self.assertFalse(result["conflict_check"]["conflict_detected"])

    def test_teaching_cli_unknown_flow_matches_boundary_behavior(self):
        result = run_unknown_flow()

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["failure_reason"], "unmapped_obstacle_shadow")
        self.assertEqual(result["generation_status"], "unknown_failure_reason")
        self.assertIsNone(result["executable_action"])
        self.assertIsNone(result["lesson"])
        self.assertFalse(result["behavior_changed"])
        self.assertNotIn("turn(east)", str(result))
        self.assertTrue(result["conflict_check"]["implemented"])

    def test_teaching_cli_disable_reenable_preserves_causal_control(self):
        result = run_disable_reenable_flow()

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["enabled_result"], "success")
        self.assertEqual(result["disabled_result"], "failed")
        self.assertEqual(result["reenabled_result"], "success")
        self.assertTrue(result["causality"]["summary"]["causal_control_passed"])
        self.assertTrue(result["conflict_check"]["implemented"])

    def test_teaching_cli_does_not_add_new_generation_path(self):
        result = run_unknown_flow()

        self.assertIsNone(result["lesson"])
        self.assertIsNone(result["executable_action"])
        self.assertNotEqual(result["trace"]["source_failure_reason"], "not_facing_east")
        self.assertNotIn("turn(east)", str(result))

    def test_teaching_cli_conflict_check_reports_real_conflict(self):
        result = run_conflict_check_flow()
        conflict = result["conflict_check"]

        self.assertTrue(conflict["implemented"])
        self.assertTrue(conflict["conflict_detected"])
        self.assertEqual(conflict["conflict_resolution"], "require_review")
        self.assertTrue(conflict["review_required"])
        self.assertEqual(conflict["review_status"], "pending_human_review")
        self.assertEqual(conflict["conflicting_lesson_ids"], ["lesson_001", "lesson_002"])
        self.assertEqual(conflict["conflicting_actions"], ["turn(east)", "turn(west)"])
        self.assertIsNone(conflict["selected_action"])
        self.assertFalse(conflict["behavior_changed"])

    def test_module_cli_outputs_json(self):
        process = subprocess.run(
            [sys.executable, "-m", "ashl_core.teaching_cli", "run-unknown-flow"],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        result = json.loads(process.stdout)

        self.assertEqual(result["command"], "run-unknown-flow")
        self.assertEqual(result["generation_status"], "unknown_failure_reason")

    def test_module_cli_conflict_flow_outputs_json(self):
        process = subprocess.run(
            [sys.executable, "-m", "ashl_core.teaching_cli", "run-conflict-check-flow"],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        result = json.loads(process.stdout)

        self.assertEqual(result["command"], "run-conflict-check-flow")
        self.assertTrue(result["conflict_check"]["implemented"])
        self.assertTrue(result["conflict_check"]["conflict_detected"])

    def test_minimal_interaction_cli_bridge_returns_ok_flow(self):
        result = run_minimal_interaction()

        self.assertEqual(result["command"], "run-minimal-interaction")
        self.assertEqual(result["flow"], "minimal_interaction_cli_bridge_v0")
        self.assertEqual(result["status"], "ok")

    def test_minimal_interaction_cli_bridge_includes_first_output(self):
        result = run_minimal_interaction()
        first_output = result["first_output_result"]
        trace = first_output["first_output_trace"]

        self.assertEqual(first_output["first_output"], "*")
        self.assertEqual(trace["trace_type"], "first_output_trace")
        self.assertIs(trace["llm_used"], False)
        self.assertEqual(trace["engineering_stage"], "test_object")

    def test_minimal_interaction_cli_bridge_includes_mentor_feedback_trace(self):
        result = run_minimal_interaction()
        trace = result["mentor_feedback_trace"]

        self.assertEqual(trace["trace_type"], "mentor_feedback_trace")
        self.assertEqual(trace["source_first_output_trace_id"], "first_output_trace:final_check:1")
        self.assertEqual(trace["mentor_feedback_label"], "observed")
        self.assertEqual(trace["effect"], "feedback_only")

    def test_minimal_interaction_cli_bridge_does_not_create_learning_outputs(self):
        result = run_minimal_interaction()
        trace = result["mentor_feedback_trace"]
        boundary = result["boundary"]

        self.assertIs(trace["creates_lesson_candidate"], False)
        self.assertIs(trace["writes_lesson_store"], False)
        self.assertIs(trace["writes_memory_layer"], False)
        self.assertIs(boundary["llm_used"], False)
        self.assertIs(boundary["awakening_claim"], False)
        self.assertNotIn("lesson_candidate", result)
        self.assertNotIn("failure_event", result)
        self.assertNotIn("review_decision", result)
        self.assertNotIn("selection_eligibility", result)
        self.assertNotIn("activation", result)
        self.assertFalse(result["persistence"]["enabled"])

    def test_minimal_interaction_cli_bridge_accepts_optional_label(self):
        result = run_minimal_interaction(feedback_label="acceptable")

        self.assertEqual(result["mentor_feedback_trace"]["mentor_feedback_label"], "acceptable")

    def test_module_cli_minimal_interaction_outputs_json(self):
        process = subprocess.run(
            [sys.executable, "-m", "ashl_core.teaching_cli", "run-minimal-interaction"],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(process.stdout)

        self.assertEqual(result["flow"], "minimal_interaction_cli_bridge_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["first_output_result"]["first_output"], "*")
        self.assertEqual(result["mentor_feedback_trace"]["mentor_feedback_label"], "observed")
        self.assertFalse(result["boundary"]["awakening_claim"])

    def test_module_cli_minimal_interaction_accepts_feedback_label(self):
        process = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-minimal-interaction",
                "--feedback-label",
                "acceptable",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        result = json.loads(process.stdout)

        self.assertEqual(result["mentor_feedback_trace"]["mentor_feedback_label"], "acceptable")

    def test_module_cli_minimal_interaction_accepts_state_key_unknown(self):
        process = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-minimal-interaction",
                "--state-key",
                "unknown",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        result = json.loads(process.stdout)
        trace = result["first_output_result"]["first_output_trace"]

        self.assertEqual(result["first_output_result"]["first_output"], "我不知道")
        self.assertEqual(result["first_output_result"]["first_output"], UTTERANCE_MAP["unknown"])
        self.assertEqual(trace["state_key"], "unknown")
        self.assertEqual(trace["utterance_source"], "utterance_map")
        self.assertIs(trace["llm_used"], False)

    def test_minimal_interaction_cli_bridge_persist_writes_append_only_jsonl(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_minimal_interaction(persist=True, data_dir=tmp)

            self.assertTrue(result["persistence"]["enabled"])
            self.assertTrue(result["persistence"]["append_only"])
            self.assertFalse(result["persistence"]["writes_lesson_store"])
            self.assertFalse(result["persistence"]["writes_memory_layer"])
            self.assertFalse(result["persistence"]["creates_lesson_candidate"])
            self.assertTrue((Path(tmp) / "first_output_traces.jsonl").exists())
            self.assertTrue((Path(tmp) / "mentor_feedback_traces.jsonl").exists())

    def test_module_cli_minimal_interaction_persist_accepts_data_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            process = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "ashl_core.teaching_cli",
                    "run-minimal-interaction",
                    "--persist",
                    "--data-dir",
                    tmp,
                ],
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            result = json.loads(process.stdout)

            self.assertTrue(result["persistence"]["enabled"])
            self.assertEqual(len((Path(tmp) / "first_output_traces.jsonl").read_text(encoding="utf-8").splitlines()), 1)
            self.assertEqual(len((Path(tmp) / "mentor_feedback_traces.jsonl").read_text(encoding="utf-8").splitlines()), 1)

    def test_module_cli_minimal_interaction_persist_with_state_key_writes_utterance_trace(self):
        with tempfile.TemporaryDirectory() as tmp:
            process = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "ashl_core.teaching_cli",
                    "run-minimal-interaction",
                    "--state-key",
                    "unknown",
                    "--persist",
                    "--data-dir",
                    tmp,
                ],
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            result = json.loads(process.stdout)
            first_rows = [
                json.loads(line)
                for line in (Path(tmp) / "first_output_traces.jsonl").read_text(encoding="utf-8").splitlines()
            ]

            self.assertTrue(result["persistence"]["enabled"])
            self.assertEqual(first_rows[0]["first_output"], "我不知道")
            self.assertEqual(first_rows[0]["first_output"], UTTERANCE_MAP["unknown"])
            self.assertEqual(first_rows[0]["state_key"], "unknown")
            self.assertEqual(first_rows[0]["utterance_source"], "utterance_map")
            self.assertIs(first_rows[0]["llm_used"], False)

    def test_tactile_interaction_cli_bridge_push_right_returns_blocked_utterance(self):
        result = run_tactile_interaction(action="push_right")

        self.assertEqual(result["command"], "run-tactile-interaction")
        self.assertEqual(result["flow"], "tactile_interaction_cli_bridge_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["action"], "push_right")
        self.assertEqual(result["tactile_result"], "box_blocked")
        self.assertEqual(result["state_key"], "blocked")
        self.assertEqual(result["utterance"], UTTERANCE_MAP["blocked"])
        self.assertEqual(result["tactile_sandbox_trace"]["trace_type"], "tactile_sandbox_trace")

    def test_tactile_interaction_cli_bridge_touch_right_returns_observed_utterance(self):
        result = run_tactile_interaction(action="touch_right")

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["tactile_result"], "box_contact")
        self.assertEqual(result["state_key"], "observed")
        self.assertEqual(result["utterance"], UTTERANCE_MAP["observed"])

    def test_tactile_interaction_cli_bridge_boundary_has_no_learning_outputs(self):
        result = run_tactile_interaction(action="push_right")
        boundary = result["boundary"]

        self.assertIs(boundary["llm_used"], False)
        self.assertIs(boundary["creates_lesson_candidate"], False)
        self.assertIs(boundary["writes_lesson_store"], False)
        self.assertIs(boundary["writes_memory_layer"], False)
        self.assertIs(boundary["awakening_claim"], False)
        self.assertNotIn("lesson_candidate", result)
        self.assertNotIn("failure_event", result)
        self.assertNotIn("review_decision", result)
        self.assertNotIn("selection_eligibility", result)
        self.assertNotIn("activation", result)

    def test_tactile_interaction_cli_bridge_invalid_action_fails(self):
        result = run_tactile_interaction(action="push right")

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["flow"], "tactile_interaction_cli_bridge_v0")
        self.assertEqual(result["action"], "push right")
        self.assertIn("unsupported action", result["error"])
        self.assertIs(result["boundary"]["llm_used"], False)

    def test_module_cli_tactile_interaction_outputs_json(self):
        process = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-tactile-interaction",
                "--action",
                "push_right",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        result = json.loads(process.stdout)

        self.assertEqual(result["flow"], "tactile_interaction_cli_bridge_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["tactile_result"], "box_blocked")
        self.assertEqual(result["state_key"], "blocked")
        self.assertEqual(result["utterance"], UTTERANCE_MAP["blocked"])

    def test_clear_sandbox_working_state_returns_ok(self):
        result = run_clear_sandbox_working_state(session_id="final_check")

        self.assertEqual(result["command"], "clear-sandbox-working-state")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["session_id"], "final_check")
        self.assertTrue(result["working_state_cleared"])
        self.assertTrue(result["append_only_traces_preserved"])
        self.assertIn("data/first_output_traces.jsonl", result["preserved"])
        self.assertIn("data/mentor_feedback_traces.jsonl", result["preserved"])

    def test_module_cli_clear_sandbox_working_state_outputs_json(self):
        process = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "clear-sandbox-working-state",
                "--session-id",
                "final_check",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        result = json.loads(process.stdout)

        self.assertEqual(result["command"], "clear-sandbox-working-state")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["session_id"], "final_check")
        self.assertTrue(result["append_only_traces_preserved"])

    def test_grounded_learning_check_returns_repeated_blocked_steps(self):
        result = run_grounded_learning_check(actions=["push_right", "push_right"])

        self.assertEqual(result["command"], "run-grounded-learning-check")
        self.assertEqual(result["flow"], "grounded_learning_verification_cli_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(len(result["steps"]), 2)
        self.assertEqual(result["steps"][0]["tactile_result"], "box_blocked")
        self.assertEqual(result["steps"][0]["state_key"], "blocked")
        self.assertEqual(result["steps"][0]["utterance"], UTTERANCE_MAP["blocked"])
        self.assertFalse(result["steps"][0]["history"]["same_action_attempted_before"])
        self.assertEqual(result["steps"][1]["tactile_result"], "box_blocked")
        self.assertTrue(result["steps"][1]["history"]["same_action_attempted_before"])
        self.assertEqual(result["steps"][1]["history"]["previous_same_action_result"], "box_blocked")
        self.assertEqual(result["suggested_next_action"], "wait")

    def test_module_cli_grounded_learning_check_outputs_json(self):
        process = subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core.teaching_cli",
                "run-grounded-learning-check",
                "--actions",
                "push_right",
                "push_right",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        result = json.loads(process.stdout)

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["steps"][1]["history"]["previous_same_action_result"], "box_blocked")
        self.assertEqual(result["suggested_next_action"], "wait")

    def test_need_state_trial_batch_cli_wrapper_returns_boundary_flags(self):
        result = run_need_state_trial_batch_cli(random_seed=0)
        boundary = result["boundary"]

        self.assertEqual(result["command"], "run-need-state-trial-batch")
        self.assertEqual(result["flow"], "need_state_trial_batch_cli_v0")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["trial_count"], 5)
        self.assertEqual(len(result["step_counts"]), 5)
        self.assertIs(boundary["llm_used"], False)
        self.assertIs(boundary["creates_lesson_candidate"], False)
        self.assertIs(boundary["writes_lesson_store"], False)
        self.assertIs(boundary["writes_memory_layer"], False)
        self.assertIs(boundary["awakening_claim"], False)


if __name__ == "__main__":
    unittest.main()
