import contextlib
import io
import unittest

from ashl_core_v1.runtime.bounded_embodied_session_runtime import (
    BoundedEmbodiedSessionConfig,
    BoundedEmbodiedSessionRuntime,
    BoundedEmbodiedSessionStatus,
    REQUIRED_FUNCTION_BINDINGS,
    build_bounded_embodied_session_runtime_audit,
    build_demo_aborted_session_runtime,
    build_demo_blocked_session_runtime,
    build_demo_deferred_bridge_to_review_runtime,
    build_demo_unknown_camera_to_review_runtime,
    validate_bounded_embodied_session_runtime_audit,
)
from ashl_core_v1.runtime.bounded_embodied_session_runtime_cli import main as runtime_cli_main
from ashl_core_v1.runtime.guided_cradle_growth_teacher_console import (
    session_abort_from_guided_cradle_growth_console,
    session_create_bounded_demo_from_guided_cradle_growth_console,
    session_run_deferred_bridge_until_review_from_guided_cradle_growth_console,
    session_run_unknown_camera_until_review_from_guided_cradle_growth_console,
    session_show_pending_reviews_from_guided_cradle_growth_console,
    session_show_state_from_guided_cradle_growth_console,
    session_show_summary_from_guided_cradle_growth_console,
    session_show_trace_from_guided_cradle_growth_console,
    session_validate_from_guided_cradle_growth_console,
)


class BoundedEmbodiedSessionRuntimeTests(unittest.TestCase):
    def test_session_creates_created_state_and_transitions_to_running(self):
        runtime = BoundedEmbodiedSessionRuntime()
        state = runtime.create_session()
        self.assertEqual(state.status, BoundedEmbodiedSessionStatus.CREATED)
        runtime.inject_fixture_host_event(state.session_id, "camera_unknown_low_level_event")
        step = runtime.step(state.session_id)
        self.assertEqual(step.status_before, "created")
        self.assertEqual(step.status_after, "running")
        self.assertEqual(runtime.get_session_state(state.session_id).status, BoundedEmbodiedSessionStatus.RUNNING)

    def test_session_blocks_package_116_transitions(self):
        runtime = BoundedEmbodiedSessionRuntime()
        state = runtime.create_session()
        blocked = runtime.transition_session_status(state.session_id, BoundedEmbodiedSessionStatus.COMMITTED)
        self.assertEqual(blocked.step_status, "session_step_failed_boundary")
        self.assertEqual(runtime.get_session_state(state.session_id).status, BoundedEmbodiedSessionStatus.CREATED)

        runtime.inject_fixture_host_event(state.session_id, "camera_unknown_low_level_event")
        runtime.run_until_blocked(state.session_id)
        blocked_resume = runtime.transition_session_status(state.session_id, BoundedEmbodiedSessionStatus.RESUMED)
        self.assertEqual(blocked_resume.step_status, "session_step_failed_boundary")
        audit = build_bounded_embodied_session_runtime_audit(runtime, state.session_id)
        self.assertEqual(audit.audit_status, "blocked_invalid_state_transition")

    def test_session_enforces_bounded_limits(self):
        runtime = BoundedEmbodiedSessionRuntime()
        state = runtime.create_session(BoundedEmbodiedSessionConfig(max_runtime_steps=1))
        runtime.inject_fixture_host_event(state.session_id, "camera_unknown_low_level_event")
        result = runtime.run_until_blocked(state.session_id)
        self.assertEqual(result.final_status, "failed")
        self.assertIn("step_limit_reached", runtime.get_session_state(state.session_id).boundary_failure_codes)

        event_limited = BoundedEmbodiedSessionRuntime()
        limited_state = event_limited.create_session(BoundedEmbodiedSessionConfig(max_event_frames=0))
        event_limited.inject_fixture_host_event(limited_state.session_id, "camera_unknown_low_level_event")
        event_step = event_limited.step(limited_state.session_id)
        self.assertEqual(event_step.step_status, "session_step_failed_limit")
        self.assertIn("event_frame_limit_reached", event_limited.get_session_state(limited_state.session_id).boundary_failure_codes)

        trace_limited = BoundedEmbodiedSessionRuntime()
        trace_state = trace_limited.create_session(BoundedEmbodiedSessionConfig(max_trace_envelopes=8))
        trace_limited.inject_fixture_host_event(trace_state.session_id, "camera_unknown_low_level_event")
        trace_result = trace_limited.run_until_blocked(trace_state.session_id)
        self.assertEqual(trace_result.final_status, "failed")
        self.assertIn("trace_limit_reached", trace_limited.get_session_state(trace_state.session_id).boundary_failure_codes)

    def test_unknown_camera_demo_runs_real_chain_to_teacher_review(self):
        payload = build_demo_unknown_camera_to_review_runtime()
        self.assertEqual(payload["session_state"]["status"], "waiting_teacher_review")
        self.assertEqual(payload["run_result"]["stop_reason"], "waiting_teacher_review")
        self.assertEqual(payload["run_result"]["pending_teacher_review_ids"], [payload["pending_teacher_reviews"][0]["pending_teacher_review_id"]])
        self.assertEqual(payload["run_result"]["selected_internal_action_kinds"], ["mark_uncertain"])
        self.assertEqual(payload["pending_teacher_reviews"][0]["review_status"], "pending_teacher_review")
        self.assertIsNone(payload["pending_teacher_reviews"][0]["teacher_decision"])
        self.assertEqual(payload["session_runtime_audit"]["audit_status"], "passed_session_waiting_teacher_review")
        self.assertTrue(payload["session_runtime_audit"]["actual_function_bindings_confirmed"])
        for required in REQUIRED_FUNCTION_BINDINGS:
            self.assertIn(required, payload["actual_bound_existing_functions"])

    def test_deferred_bridge_demo_stops_at_teacher_gate(self):
        payload = build_demo_deferred_bridge_to_review_runtime()
        self.assertEqual(payload["session_state"]["status"], "waiting_teacher_review")
        self.assertIn(payload["run_result"]["selected_internal_action_kinds"][0], ("request_teacher_review", "pause_event_processing"))
        self.assertEqual(payload["session_runtime_audit"]["audit_status"], "passed_session_waiting_teacher_review")

    def test_trace_envelopes_share_session_and_preserve_refs(self):
        payload = build_demo_unknown_camera_to_review_runtime()
        traces = payload["session_trace"]
        session_ids = {item["session_id"] for item in traces}
        self.assertEqual(len(session_ids), 1)
        self.assertEqual([item["sequence_index"] for item in traces], list(range(len(traces))))
        known = set()
        for item in traces:
            for ref in item["source_trace_refs"]:
                self.assertIn(ref, known)
            known.add(item["trace_id"])
        raw = [item for item in traces if item["trace_layer"] == "raw"]
        self.assertTrue(raw)
        for item in raw:
            self.assertNotIn("concept_id", item["payload_snapshot"])
            self.assertNotIn("reviewed_concept_id", item["payload_snapshot"])

    def test_abort_preserves_raw_trace_and_pending_review_unresolved(self):
        runtime = BoundedEmbodiedSessionRuntime()
        state = runtime.create_session()
        runtime.inject_fixture_host_event(state.session_id, "camera_unknown_low_level_event")
        runtime.run_until_blocked(state.session_id)
        raw_trace_ids = [item.trace_id for item in runtime.get_session_trace(state.session_id) if item.trace_layer == "raw"]
        runtime.abort_session(state.session_id, "teacher_stopped_demo")
        self.assertEqual(runtime.get_session_state(state.session_id).status, BoundedEmbodiedSessionStatus.ABORTED)
        after_raw_trace_ids = [item.trace_id for item in runtime.get_session_trace(state.session_id) if item.trace_layer == "raw"]
        self.assertEqual(raw_trace_ids, after_raw_trace_ids)
        pending = runtime.get_pending_teacher_reviews(state.session_id)
        self.assertFalse(pending[0].resolved)
        self.assertTrue(pending[0].session_aborted)
        audit = build_bounded_embodied_session_runtime_audit(runtime, state.session_id)
        self.assertEqual(audit.audit_status, "passed_abort_preserves_raw_trace")

    def test_runtime_audit_blocks_boundary_failures(self):
        cases = {
            "invalid-transition": "blocked_invalid_state_transition",
            "cross-session-trace": "blocked_cross_session_trace_detected",
            "raw-trace-mutation": "blocked_raw_trace_mutation_detected",
            "concept-id-in-raw-trace": "blocked_concept_id_in_raw_history",
            "teacher-decision": "blocked_teacher_decision_created",
            "memory-commit": "blocked_memory_commit_detected",
            "external-control": "blocked_external_control_detected",
            "first-output": "blocked_first_output_detected",
            "live-scheduler": "blocked_live_scheduler_detected",
            "fake-function-binding": "blocked_fake_function_binding",
        }
        for case, status in cases.items():
            with self.subTest(case=case):
                payload = build_demo_blocked_session_runtime(case)
                self.assertEqual(payload["session_runtime_audit"]["audit_status"], status)

    def test_audit_validation_passes_for_normal_session(self):
        payload = build_demo_unknown_camera_to_review_runtime()
        validation = validate_bounded_embodied_session_runtime_audit(payload["session_runtime_audit"])
        self.assertTrue(validation["valid"])

    def test_cli_commands_work(self):
        commands = (
            ["run-demo-unknown-camera-to-review"],
            ["run-demo-deferred-bridge-to-review"],
            ["show-demo-trace-envelope"],
            ["show-demo-session-state"],
            ["show-demo-session-trace"],
            ["show-demo-pending-reviews"],
            ["show-demo-session-summary"],
            ["abort-demo-session"],
            ["validate-demo-session-runtime"],
            ["show-demo-blocked", "--case", "invalid-transition"],
            ["show-demo-blocked", "--case", "cross-session-trace"],
            ["show-demo-blocked", "--case", "raw-trace-mutation"],
            ["show-demo-blocked", "--case", "concept-id-in-raw-trace"],
            ["show-demo-blocked", "--case", "teacher-decision"],
            ["show-demo-blocked", "--case", "memory-commit"],
            ["show-demo-blocked", "--case", "external-control"],
            ["show-demo-blocked", "--case", "first-output"],
            ["show-demo-blocked", "--case", "live-scheduler"],
        )
        for command in commands:
            with self.subTest(command=command):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(runtime_cli_main(list(command)), 0)

    def test_guided_console_session_commands_work(self):
        commands = (
            session_create_bounded_demo_from_guided_cradle_growth_console,
            session_run_unknown_camera_until_review_from_guided_cradle_growth_console,
            session_run_deferred_bridge_until_review_from_guided_cradle_growth_console,
            session_show_state_from_guided_cradle_growth_console,
            session_show_trace_from_guided_cradle_growth_console,
            session_show_pending_reviews_from_guided_cradle_growth_console,
            session_show_summary_from_guided_cradle_growth_console,
            session_abort_from_guided_cradle_growth_console,
            session_validate_from_guided_cradle_growth_console,
        )
        for command in commands:
            with self.subTest(command=command.__name__):
                payload = command()
                self.assertIn("guided_console_action", payload)
                self.assertFalse(payload["first_output_created"])
                self.assertFalse(payload["external_control_created"])
                self.assertFalse(payload["memory_commit_performed"])

    def test_package_115_doc_exists_and_no_data_dir_created(self):
        from pathlib import Path

        self.assertTrue(Path("ashl_core_v1/docs/bounded_embodied_session_runtime_v0.md").exists())
        self.assertFalse(Path("ashl_core_v1/data").exists())


if __name__ == "__main__":
    unittest.main()

