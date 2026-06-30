from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from ashl_core_v1.learning.reviewed_concept_memory_trace_bridge import (
    ReviewedConceptMemoryApplicationDataCandidate,
    ReviewedConceptMemoryLearningTraceCandidate,
    build_demo_reviewed_concept_memory_trace_bridge,
)
from ashl_core_v1.memory.reviewed_concept_candidate_admission_review import (
    ReviewedConceptMemoryAdmissionReviewRecord,
    ReviewedConceptMemoryAdmissionSafetyAudit,
    ReviewedConceptMemoryApplicationData,
    ReviewedConceptMemoryLearningTrace,
    ReviewedConceptMemoryRoutingTrace,
    build_demo_blocked_forbidden_memory_write_admission,
    build_demo_blocked_forbidden_target_layer_admission,
    build_demo_blocked_invalid_candidates_admission,
    build_demo_held_for_more_evidence_admission,
    build_demo_reviewed_concept_memory_admission,
    build_reviewed_concept_memory_admission_review,
    build_reviewed_concept_memory_admission_safety_audit,
    build_reviewed_concept_memory_application_data,
    build_reviewed_concept_memory_learning_trace,
    build_reviewed_concept_memory_routing_trace,
    validate_reviewed_concept_memory_admission_review,
    validate_reviewed_concept_memory_admission_safety_audit,
    validate_reviewed_concept_memory_application_data,
    validate_reviewed_concept_memory_learning_trace,
    validate_reviewed_concept_memory_routing_trace,
)


class ReviewedConceptCandidateAdmissionReviewTests(unittest.TestCase):
    def test_admission_review_builds_from_valid_package_68_candidates(self) -> None:
        review = self._valid_admission_review()
        validation = validate_reviewed_concept_memory_admission_review(review)
        self.assertTrue(validation["valid"], validation["error_codes"])

    def test_admission_review_preserves_reviewed_concept_id(self) -> None:
        review = self._valid_admission_review()
        self.assertTrue(review.source_reviewed_concept_id.startswith("reviewed_concept:"))

    def test_admission_review_preserves_candidate_ids(self) -> None:
        bridge = build_demo_reviewed_concept_memory_trace_bridge()
        review = self._valid_admission_review()
        self.assertEqual(
            review.source_learning_trace_candidate_id,
            bridge["memory_learning_trace_candidate"]["memory_learning_trace_candidate_id"],
        )
        self.assertEqual(
            review.source_routing_trace_candidate_id,
            bridge["memory_routing_trace_candidate"]["memory_routing_trace_candidate_id"],
        )
        self.assertEqual(
            review.source_application_data_candidate_id,
            bridge["memory_application_data_candidate"][
                "memory_application_data_candidate_id"
            ],
        )

    def test_admission_review_status_admitted_for_valid_demo(self) -> None:
        self.assertEqual(
            self._valid_admission_review().admission_status,
            "admitted_for_working_readback_trace_only",
        )

    def test_admission_review_target_working_readback_for_valid_demo(self) -> None:
        self.assertEqual(
            self._valid_admission_review().admitted_target_layer,
            "working_readback",
        )

    def test_admission_review_blocks_invalid_candidates(self) -> None:
        payload = build_demo_blocked_invalid_candidates_admission()
        review = ReviewedConceptMemoryAdmissionReviewRecord.from_dict(
            payload["admission_review"]
        )
        self.assertEqual(review.admission_status, "blocked_invalid_candidates")

    def test_admission_review_blocks_forbidden_target_layer(self) -> None:
        payload = build_demo_blocked_forbidden_target_layer_admission()
        review = ReviewedConceptMemoryAdmissionReviewRecord.from_dict(
            payload["admission_review"]
        )
        self.assertEqual(review.admission_status, "blocked_forbidden_target_layer")

    def test_admission_review_blocks_unhandled_counterexamples(self) -> None:
        bridge = build_demo_reviewed_concept_memory_trace_bridge()
        learning_data = dict(bridge["memory_learning_trace_candidate"])
        learning_data["counterexample_evidence_refs"] = ["counterexample:front_blocked"]
        learning_data["counterexample_handling_status"] = "not_checked"
        learning = ReviewedConceptMemoryLearningTraceCandidate.from_dict(learning_data)
        review = build_reviewed_concept_memory_admission_review(
            memory_learning_trace_candidate=learning,
            memory_routing_trace_candidate=bridge["memory_routing_trace_candidate"],
            memory_application_data_candidate=bridge["memory_application_data_candidate"],
            bridge_audit=bridge["bridge_audit"],
        )
        self.assertEqual(review.admission_status, "blocked_unhandled_counterexamples")

    def test_admission_review_memory_write_flags_false(self) -> None:
        review = self._valid_admission_review()
        self.assertFalse(review.memory_layer_write_performed)
        self.assertFalse(review.core_memory_write_performed)
        self.assertFalse(review.long_term_memory_write_performed)
        self.assertFalse(review.archive_memory_write_performed)
        self.assertFalse(review.anchor_write_performed)
        self.assertFalse(review.readback_hint_created)
        self.assertFalse(review.working_memory_mutated)
        self.assertFalse(review.task_behavior_changed)

    def test_memory_learning_trace_builds_from_admitted_review(self) -> None:
        trace = self._valid_memory_learning_trace()
        validation = validate_reviewed_concept_memory_learning_trace(trace)
        self.assertTrue(validation["valid"], validation["error_codes"])

    def test_memory_learning_trace_preserves_support_refs(self) -> None:
        trace = self._valid_memory_learning_trace()
        self.assertGreaterEqual(len(trace.support_evidence_refs), 1)

    def test_memory_learning_trace_preserves_counterexample_refs(self) -> None:
        trace = self._valid_memory_learning_trace()
        self.assertIsInstance(trace.counterexample_evidence_refs, tuple)

    def test_memory_learning_trace_memory_layer_write_performed_false(self) -> None:
        self.assertFalse(self._valid_memory_learning_trace().memory_layer_write_performed)

    def test_memory_routing_trace_builds_from_admitted_review(self) -> None:
        trace = self._valid_memory_routing_trace()
        validation = validate_reviewed_concept_memory_routing_trace(trace)
        self.assertTrue(validation["valid"], validation["error_codes"])

    def test_memory_routing_trace_target_layer_working_readback(self) -> None:
        self.assertEqual(self._valid_memory_routing_trace().target_layer, "working_readback")

    def test_memory_routing_trace_forbids_memory_layer_write(self) -> None:
        trace = self._valid_memory_routing_trace()
        self.assertFalse(trace.allowed_for_memory_layer_write)
        self.assertFalse(trace.allowed_for_core_memory)
        self.assertFalse(trace.allowed_for_long_term_memory)
        self.assertFalse(trace.allowed_for_archive_memory)
        self.assertFalse(trace.allowed_for_anchor_layer)

    def test_memory_application_data_builds_from_admitted_review(self) -> None:
        data = self._valid_memory_application_data()
        validation = validate_reviewed_concept_memory_application_data(data)
        self.assertTrue(validation["valid"], validation["error_codes"])

    def test_memory_application_data_available_for_future_readback_preview_true(self) -> None:
        self.assertTrue(
            self._valid_memory_application_data().available_for_future_readback_preview
        )

    def test_memory_application_data_does_not_create_readback_or_mutate_working_memory(self) -> None:
        data = self._valid_memory_application_data()
        self.assertFalse(data.actual_readback_hint_created)
        self.assertFalse(data.working_memory_mutated)
        self.assertFalse(data.task_behavior_changed)
        self.assertFalse(data.memory_layer_write_performed)

    def test_held_for_more_evidence_demo_creates_held_records(self) -> None:
        payload = build_demo_held_for_more_evidence_admission()
        review = ReviewedConceptMemoryAdmissionReviewRecord.from_dict(
            payload["admission_review"]
        )
        learning = ReviewedConceptMemoryLearningTrace.from_dict(
            payload["memory_learning_trace"]
        )
        routing = ReviewedConceptMemoryRoutingTrace.from_dict(
            payload["memory_routing_trace"]
        )
        data = ReviewedConceptMemoryApplicationData.from_dict(
            payload["memory_application_data"]
        )
        self.assertEqual(review.admission_status, "held_for_more_evidence")
        self.assertEqual(learning.trace_status, "held_for_more_evidence")
        self.assertEqual(routing.target_layer, "held_for_more_evidence")
        self.assertEqual(data.application_status, "held_for_more_evidence")

    def test_blocked_forbidden_target_layer_demo_blocks(self) -> None:
        payload = build_demo_blocked_forbidden_target_layer_admission()
        review = ReviewedConceptMemoryAdmissionReviewRecord.from_dict(
            payload["admission_review"]
        )
        self.assertEqual(review.admission_status, "blocked_forbidden_target_layer")

    def test_blocked_forbidden_memory_write_demo_blocks(self) -> None:
        payload = build_demo_blocked_forbidden_memory_write_admission()
        review = ReviewedConceptMemoryAdmissionReviewRecord.from_dict(
            payload["admission_review"]
        )
        audit = ReviewedConceptMemoryAdmissionSafetyAudit.from_dict(
            payload["admission_safety_audit"]
        )
        self.assertEqual(
            review.admission_status,
            "blocked_forbidden_authority_detected",
        )
        self.assertEqual(
            audit.audit_status,
            "blocked_invalid_admission_review",
        )

    def test_safety_audit_passes_for_valid_admission(self) -> None:
        audit = self._valid_safety_audit()
        validation = validate_reviewed_concept_memory_admission_safety_audit(audit)
        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(audit.audit_status, "passed")

    def test_safety_audit_blocks_memory_layer_write_performed_true(self) -> None:
        audit = self._audit_with_application_flag("memory_layer_write_performed", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_memory_layer_write_detected",
        )

    def test_safety_audit_blocks_core_memory_write_true(self) -> None:
        audit = self._audit_with_review_flag("core_memory_write_performed", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_memory_layer_write_detected",
        )

    def test_safety_audit_blocks_long_term_memory_write_true(self) -> None:
        audit = self._audit_with_review_flag("long_term_memory_write_performed", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_memory_layer_write_detected",
        )

    def test_safety_audit_blocks_archive_memory_write_true(self) -> None:
        audit = self._audit_with_review_flag("archive_memory_write_performed", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_memory_layer_write_detected",
        )

    def test_safety_audit_blocks_anchor_write_true(self) -> None:
        audit = self._audit_with_review_flag("anchor_write_performed", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_memory_layer_write_detected",
        )

    def test_safety_audit_blocks_readback_hint_created_true(self) -> None:
        audit = self._audit_with_application_flag("actual_readback_hint_created", True)
        self.assertEqual(audit.audit_status, "blocked_forbidden_readback_detected")

    def test_safety_audit_blocks_working_memory_mutated_true(self) -> None:
        audit = self._audit_with_application_flag("working_memory_mutated", True)
        self.assertEqual(audit.audit_status, "blocked_forbidden_readback_detected")

    def test_safety_audit_blocks_task_behavior_changed_true(self) -> None:
        audit = self._audit_with_application_flag("task_behavior_changed", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_behavior_change_detected",
        )

    def test_cli_admit_demo_full_works(self) -> None:
        result = self._run_memory_cli("admit-demo-full")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("admitted_for_working_readback_trace_only", result.stdout)

    def test_cli_show_demo_admission_review_works(self) -> None:
        result = self._run_memory_cli("show-demo-admission-review")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("admission_review_id", result.stdout)

    def test_cli_show_demo_memory_learning_trace_works(self) -> None:
        result = self._run_memory_cli("show-demo-memory-learning-trace")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("trace_created_for_working_readback", result.stdout)

    def test_cli_show_demo_memory_routing_trace_works(self) -> None:
        result = self._run_memory_cli("show-demo-memory-routing-trace")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("working_readback", result.stdout)

    def test_cli_show_demo_memory_application_data_works(self) -> None:
        result = self._run_memory_cli("show-demo-memory-application-data")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("application_data_created_for_working_readback", result.stdout)

    def test_cli_validate_demo_admission_works(self) -> None:
        result = self._run_memory_cli("validate-demo-admission")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"valid": true', result.stdout)

    def test_cli_held_more_evidence_works(self) -> None:
        result = self._run_memory_cli("admit-demo-held", "--case", "more-evidence")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("held_for_more_evidence", result.stdout)

    def test_cli_blocked_forbidden_target_layer_works(self) -> None:
        result = self._run_memory_cli(
            "admit-demo-blocked",
            "--case",
            "forbidden-target-layer",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("blocked_forbidden_target_layer", result.stdout)

    def test_cli_blocked_forbidden_memory_write_works(self) -> None:
        result = self._run_memory_cli(
            "admit-demo-blocked",
            "--case",
            "forbidden-memory-write",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("blocked_forbidden_authority_detected", result.stdout)

    def test_guided_console_memory_admission_demo_works(self) -> None:
        for command in (
            "memory-admit-reviewed-concept-demo",
            "memory-show-reviewed-concept-admission",
            "memory-show-reviewed-concept-application-data",
            "memory-validate-reviewed-concept-admission",
        ):
            result = self._run_guided_cli(command)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("guided_console_action", result.stdout)

    def test_no_repo_data_created(self) -> None:
        build_demo_reviewed_concept_memory_admission()
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _valid_payload(self) -> dict[str, object]:
        return build_demo_reviewed_concept_memory_admission()

    def _valid_admission_review(self) -> ReviewedConceptMemoryAdmissionReviewRecord:
        return ReviewedConceptMemoryAdmissionReviewRecord.from_dict(
            self._valid_payload()["admission_review"]
        )

    def _valid_memory_learning_trace(self) -> ReviewedConceptMemoryLearningTrace:
        return ReviewedConceptMemoryLearningTrace.from_dict(
            self._valid_payload()["memory_learning_trace"]
        )

    def _valid_memory_routing_trace(self) -> ReviewedConceptMemoryRoutingTrace:
        return ReviewedConceptMemoryRoutingTrace.from_dict(
            self._valid_payload()["memory_routing_trace"]
        )

    def _valid_memory_application_data(self) -> ReviewedConceptMemoryApplicationData:
        return ReviewedConceptMemoryApplicationData.from_dict(
            self._valid_payload()["memory_application_data"]
        )

    def _valid_safety_audit(self) -> ReviewedConceptMemoryAdmissionSafetyAudit:
        return ReviewedConceptMemoryAdmissionSafetyAudit.from_dict(
            self._valid_payload()["admission_safety_audit"]
        )

    def _audit_with_review_flag(
        self,
        flag_name: str,
        flag_value: bool,
    ) -> ReviewedConceptMemoryAdmissionSafetyAudit:
        payload = self._valid_payload()
        review_data = dict(payload["admission_review"])
        review_data[flag_name] = flag_value
        return build_reviewed_concept_memory_admission_safety_audit(
            admission_review=ReviewedConceptMemoryAdmissionReviewRecord.from_dict(
                review_data
            ),
            memory_learning_trace=payload["memory_learning_trace"],
            memory_routing_trace=payload["memory_routing_trace"],
            memory_application_data=payload["memory_application_data"],
        )

    def _audit_with_application_flag(
        self,
        flag_name: str,
        flag_value: bool,
    ) -> ReviewedConceptMemoryAdmissionSafetyAudit:
        payload = self._valid_payload()
        application_data = dict(payload["memory_application_data"])
        application_data[flag_name] = flag_value
        return build_reviewed_concept_memory_admission_safety_audit(
            admission_review=payload["admission_review"],
            memory_learning_trace=payload["memory_learning_trace"],
            memory_routing_trace=payload["memory_routing_trace"],
            memory_application_data=ReviewedConceptMemoryApplicationData.from_dict(
                application_data
            ),
        )

    def _run_memory_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core_v1.memory.reviewed_concept_candidate_admission_review_cli",
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
