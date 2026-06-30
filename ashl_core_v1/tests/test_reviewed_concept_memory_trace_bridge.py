from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from ashl_core_v1.learning.reviewed_concept_memory_trace_bridge import (
    ReviewedConceptMemoryApplicationDataCandidate,
    ReviewedConceptMemoryLearningTraceCandidate,
    ReviewedConceptMemoryRoutingTraceCandidate,
    ReviewedConceptMemoryTraceBridgeAudit,
    build_demo_blocked_forbidden_memory_write_bridge,
    build_demo_blocked_forbidden_target_layer_bridge,
    build_demo_blocked_from_routing_bridge,
    build_demo_held_for_more_evidence_bridge,
    build_demo_reviewed_concept_memory_trace_bridge,
    build_reviewed_concept_memory_application_data_candidate,
    build_reviewed_concept_memory_learning_trace_candidate,
    build_reviewed_concept_memory_routing_trace_candidate,
    build_reviewed_concept_memory_trace_bridge,
    build_reviewed_concept_memory_trace_bridge_audit,
    validate_reviewed_concept_memory_application_data_candidate,
    validate_reviewed_concept_memory_learning_trace_candidate,
    validate_reviewed_concept_memory_routing_trace_candidate,
    validate_reviewed_concept_memory_trace_bridge_audit,
)
from ashl_core_v1.learning.reviewed_concept_record import (
    build_demo_reviewed_concept_record,
)
from ashl_core_v1.learning.reviewed_concept_to_memory_trace_preview import (
    ReviewedConceptMemoryApplicationDataPreview,
    ReviewedConceptMemoryRoutingPreview,
    ReviewedConceptMemoryTracePreview,
    build_demo_reviewed_concept_memory_preview_bundle,
    build_demo_reviewed_concept_memory_trace_preview,
    build_reviewed_concept_memory_application_data_preview,
    build_reviewed_concept_memory_preview_safety_audit,
    build_reviewed_concept_memory_routing_preview,
)


class ReviewedConceptMemoryTraceBridgeTests(unittest.TestCase):
    def test_learning_trace_candidate_builds_from_valid_preview(self) -> None:
        candidate = self._valid_learning_candidate()
        validation = validate_reviewed_concept_memory_learning_trace_candidate(candidate)
        self.assertTrue(validation["valid"], validation["error_codes"])

    def test_learning_trace_candidate_preserves_reviewed_concept_id(self) -> None:
        bridge = build_demo_reviewed_concept_memory_trace_bridge()
        candidate = ReviewedConceptMemoryLearningTraceCandidate.from_dict(
            bridge["memory_learning_trace_candidate"]
        )
        self.assertTrue(candidate.source_reviewed_concept_id.startswith("reviewed_concept:"))

    def test_learning_trace_candidate_preserves_support_refs(self) -> None:
        candidate = self._valid_learning_candidate()
        self.assertGreaterEqual(len(candidate.support_evidence_refs), 1)

    def test_learning_trace_candidate_preserves_counterexample_refs(self) -> None:
        candidate = self._valid_learning_candidate()
        self.assertIsInstance(candidate.counterexample_evidence_refs, tuple)

    def test_learning_trace_candidate_actual_memory_learning_trace_created_false(self) -> None:
        self.assertFalse(self._valid_learning_candidate().actual_memory_learning_trace_created)

    def test_learning_trace_candidate_memory_layer_write_performed_false(self) -> None:
        self.assertFalse(self._valid_learning_candidate().memory_layer_write_performed)

    def test_routing_trace_candidate_builds_from_valid_routing_preview(self) -> None:
        candidate = self._valid_routing_candidate()
        validation = validate_reviewed_concept_memory_routing_trace_candidate(candidate)
        self.assertTrue(validation["valid"], validation["error_codes"])

    def test_routing_trace_candidate_target_layer_working_readback_candidate_for_valid_demo(self) -> None:
        candidate = self._valid_routing_candidate()
        self.assertEqual(candidate.target_layer_candidate, "working_readback_candidate")

    def test_routing_trace_candidate_blocks_core_memory_target(self) -> None:
        self._assert_forbidden_target_blocks("core_memory")

    def test_routing_trace_candidate_blocks_long_term_memory_target(self) -> None:
        self._assert_forbidden_target_blocks("long_term_memory")

    def test_routing_trace_candidate_blocks_archive_memory_target(self) -> None:
        self._assert_forbidden_target_blocks("archive_memory")

    def test_routing_trace_candidate_blocks_anchor_layer_target(self) -> None:
        self._assert_forbidden_target_blocks("anchor_layer")

    def test_routing_trace_candidate_requires_memory_engine_review_true(self) -> None:
        self.assertTrue(self._valid_routing_candidate().requires_memory_engine_review)

    def test_routing_trace_candidate_requires_teacher_review_before_memory_write_true(self) -> None:
        self.assertTrue(
            self._valid_routing_candidate().requires_teacher_review_before_memory_write
        )

    def test_application_data_candidate_builds_from_valid_application_preview(self) -> None:
        candidate = self._valid_application_candidate()
        validation = validate_reviewed_concept_memory_application_data_candidate(candidate)
        self.assertTrue(validation["valid"], validation["error_codes"])

    def test_application_data_candidate_includes_suggested_hint_labels(self) -> None:
        candidate = self._valid_application_candidate()
        self.assertIn("observe_or_adjust", candidate.suggested_working_memory_hint_labels)

    def test_application_data_candidate_actual_memory_application_data_created_false(self) -> None:
        self.assertFalse(
            self._valid_application_candidate().actual_memory_application_data_created
        )

    def test_application_data_candidate_readback_hint_created_false(self) -> None:
        self.assertFalse(self._valid_application_candidate().readback_hint_created)

    def test_application_data_candidate_working_memory_mutated_false(self) -> None:
        self.assertFalse(self._valid_application_candidate().working_memory_mutated)

    def test_application_data_candidate_task_behavior_changed_false(self) -> None:
        self.assertFalse(self._valid_application_candidate().task_behavior_changed)

    def test_bridge_audit_passes_for_valid_demo(self) -> None:
        audit = self._valid_bridge_audit()
        validation = validate_reviewed_concept_memory_trace_bridge_audit(audit)
        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(audit.audit_status, "passed")

    def test_bridge_audit_blocks_invalid_preview_chain(self) -> None:
        bridge = self._bridge_with_trace_preview_status("blocked_incomplete_lineage")
        audit = ReviewedConceptMemoryTraceBridgeAudit.from_dict(bridge["bridge_audit"])
        self.assertEqual(audit.audit_status, "blocked_invalid_preview_chain")

    def test_bridge_audit_blocks_forbidden_target_layer(self) -> None:
        bridge = build_demo_blocked_forbidden_target_layer_bridge()
        routing = ReviewedConceptMemoryRoutingTraceCandidate.from_dict(
            bridge["memory_routing_trace_candidate"]
        )
        audit = ReviewedConceptMemoryTraceBridgeAudit.from_dict(bridge["bridge_audit"])
        self.assertEqual(routing.routing_candidate_status, "blocked_forbidden_target_layer")
        self.assertNotEqual(audit.audit_status, "passed")

    def test_bridge_audit_blocks_forbidden_memory_write_flag(self) -> None:
        bridge = build_demo_blocked_forbidden_memory_write_bridge()
        audit = ReviewedConceptMemoryTraceBridgeAudit.from_dict(bridge["bridge_audit"])
        self.assertEqual(audit.audit_status, "blocked_forbidden_memory_write_detected")

    def test_bridge_audit_blocks_readback_hint_created_flag(self) -> None:
        audit = self._audit_with_application_flag("readback_hint_created", True)
        self.assertEqual(audit.audit_status, "blocked_forbidden_readback_detected")

    def test_bridge_audit_blocks_working_memory_mutation_flag(self) -> None:
        audit = self._audit_with_application_flag("working_memory_mutated", True)
        self.assertEqual(audit.audit_status, "blocked_forbidden_readback_detected")

    def test_bridge_audit_blocks_task_behavior_changed_flag(self) -> None:
        audit = self._audit_with_application_flag("task_behavior_changed", True)
        self.assertEqual(audit.audit_status, "blocked_forbidden_behavior_change_detected")

    def test_held_for_more_evidence_demo_creates_held_candidates(self) -> None:
        bridge = build_demo_held_for_more_evidence_bridge()
        routing = ReviewedConceptMemoryRoutingTraceCandidate.from_dict(
            bridge["memory_routing_trace_candidate"]
        )
        application = ReviewedConceptMemoryApplicationDataCandidate.from_dict(
            bridge["memory_application_data_candidate"]
        )
        self.assertEqual(
            routing.routing_candidate_status,
            "candidate_held_for_more_evidence",
        )
        self.assertEqual(application.candidate_status, "candidate_held_for_more_evidence")

    def test_blocked_from_routing_demo_creates_blocked_candidates(self) -> None:
        bridge = build_demo_blocked_from_routing_bridge()
        routing = ReviewedConceptMemoryRoutingTraceCandidate.from_dict(
            bridge["memory_routing_trace_candidate"]
        )
        application = ReviewedConceptMemoryApplicationDataCandidate.from_dict(
            bridge["memory_application_data_candidate"]
        )
        self.assertEqual(routing.routing_candidate_status, "candidate_blocked_from_routing")
        self.assertEqual(application.candidate_status, "candidate_blocked")

    def test_cli_bridge_demo_full_works(self) -> None:
        result = self._run_learning_cli("bridge-demo-full")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("memory_learning_trace_candidate", result.stdout)

    def test_cli_show_demo_learning_trace_candidate_works(self) -> None:
        result = self._run_learning_cli("show-demo-learning-trace-candidate")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("candidate_ready_for_memory_engine_review", result.stdout)

    def test_cli_show_demo_routing_candidate_works(self) -> None:
        result = self._run_learning_cli("show-demo-routing-candidate")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("candidate_routed_to_working_readback_review", result.stdout)

    def test_cli_show_demo_application_data_candidate_works(self) -> None:
        result = self._run_learning_cli("show-demo-application-data-candidate")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("working_memory_hint_candidate", result.stdout)

    def test_cli_validate_demo_bridge_works(self) -> None:
        result = self._run_learning_cli("validate-demo-bridge")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"valid": true', result.stdout)

    def test_cli_bridge_demo_held_works(self) -> None:
        result = self._run_learning_cli("bridge-demo-held", "--case", "more-evidence")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("candidate_held_for_more_evidence", result.stdout)

    def test_cli_bridge_demo_blocked_forbidden_target_layer_works(self) -> None:
        result = self._run_learning_cli(
            "bridge-demo-blocked",
            "--case",
            "forbidden-target-layer",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("blocked_forbidden_target_layer", result.stdout)

    def test_cli_bridge_demo_blocked_forbidden_memory_write_works(self) -> None:
        result = self._run_learning_cli(
            "bridge-demo-blocked",
            "--case",
            "forbidden-memory-write",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("blocked_forbidden_memory_write_detected", result.stdout)

    def test_guided_console_reviewed_concept_memory_bridge_demo_works(self) -> None:
        for command in (
            "learning-bridge-reviewed-concept-memory-demo",
            "learning-show-reviewed-concept-memory-candidates",
            "learning-validate-reviewed-concept-memory-bridge",
        ):
            result = self._run_guided_cli(command)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("guided_console_action", result.stdout)

    def test_no_repo_data_created(self) -> None:
        build_demo_reviewed_concept_memory_trace_bridge()
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _valid_bridge(self) -> dict[str, object]:
        return build_demo_reviewed_concept_memory_trace_bridge()

    def _valid_learning_candidate(self) -> ReviewedConceptMemoryLearningTraceCandidate:
        return ReviewedConceptMemoryLearningTraceCandidate.from_dict(
            self._valid_bridge()["memory_learning_trace_candidate"]
        )

    def _valid_routing_candidate(self) -> ReviewedConceptMemoryRoutingTraceCandidate:
        return ReviewedConceptMemoryRoutingTraceCandidate.from_dict(
            self._valid_bridge()["memory_routing_trace_candidate"]
        )

    def _valid_application_candidate(self) -> ReviewedConceptMemoryApplicationDataCandidate:
        return ReviewedConceptMemoryApplicationDataCandidate.from_dict(
            self._valid_bridge()["memory_application_data_candidate"]
        )

    def _valid_bridge_audit(self) -> ReviewedConceptMemoryTraceBridgeAudit:
        return ReviewedConceptMemoryTraceBridgeAudit.from_dict(
            self._valid_bridge()["bridge_audit"]
        )

    def _assert_forbidden_target_blocks(self, target_layer: str) -> None:
        preview = build_reviewed_concept_memory_routing_preview(
            memory_trace_preview=build_demo_reviewed_concept_memory_trace_preview(),
            requested_target_layer_preview=target_layer,
        )
        candidate = build_reviewed_concept_memory_routing_trace_candidate(
            memory_learning_trace_candidate=self._valid_learning_candidate(),
            routing_preview=preview,
        )
        self.assertEqual(candidate.target_layer_candidate, "blocked_from_routing")
        self.assertEqual(candidate.routing_candidate_status, "blocked_forbidden_target_layer")

    def _bridge_with_trace_preview_status(self, status: str) -> dict[str, object]:
        concept_payload = build_demo_reviewed_concept_record()
        preview_payload = build_demo_reviewed_concept_memory_preview_bundle()
        trace_data = dict(preview_payload["memory_trace_preview"])
        trace_data["trace_preview_status"] = status
        trace = ReviewedConceptMemoryTracePreview.from_dict(trace_data)
        routing = build_reviewed_concept_memory_routing_preview(memory_trace_preview=trace)
        application = build_reviewed_concept_memory_application_data_preview(
            reviewed_concept=concept_payload["reviewed_concept"],
            memory_trace_preview=trace,
            routing_preview=routing,
        )
        preview_safety = build_reviewed_concept_memory_preview_safety_audit(
            reviewed_concept=concept_payload["reviewed_concept"],
            memory_trace_preview=trace,
            routing_preview=routing,
            application_data_preview=application,
        )
        return build_reviewed_concept_memory_trace_bridge(
            reviewed_concept_payload=concept_payload,
            preview_payload={
                "memory_trace_preview": trace.to_dict(),
                "routing_preview": routing.to_dict(),
                "application_data_preview": application.to_dict(),
                "preview_safety_audit": preview_safety.to_dict(),
            },
        )

    def _audit_with_application_flag(
        self,
        flag_name: str,
        flag_value: bool,
    ) -> ReviewedConceptMemoryTraceBridgeAudit:
        bridge = self._valid_bridge()
        application_data = dict(bridge["memory_application_data_candidate"])
        application_data[flag_name] = flag_value
        application = ReviewedConceptMemoryApplicationDataCandidate.from_dict(
            application_data
        )
        concept_payload = build_demo_reviewed_concept_record()
        preview_payload = build_demo_reviewed_concept_memory_preview_bundle()
        audit = build_reviewed_concept_memory_trace_bridge_audit(
            reviewed_concept=concept_payload["reviewed_concept"],
            memory_trace_preview=preview_payload["memory_trace_preview"],
            routing_preview=preview_payload["routing_preview"],
            application_data_preview=preview_payload["application_data_preview"],
            memory_learning_trace_candidate=bridge["memory_learning_trace_candidate"],
            memory_routing_trace_candidate=bridge["memory_routing_trace_candidate"],
            memory_application_data_candidate=application,
            memory_preview_safety_audit=preview_payload["preview_safety_audit"],
        )
        return audit

    def _run_learning_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core_v1.learning.reviewed_concept_memory_trace_bridge_cli",
                *args,
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    def _run_guided_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core_v1.runtime.guided_cradle_growth_teacher_console_cli",
                *args,
            ],
            check=False,
            capture_output=True,
            text=True,
        )


if __name__ == "__main__":
    unittest.main()
