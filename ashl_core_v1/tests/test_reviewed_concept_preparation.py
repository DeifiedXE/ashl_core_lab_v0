from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from ashl_core_v1.learning.reviewed_concept_preparation import (
    ReviewedConceptEvidenceBundle,
    ReviewedConceptPreparationPacket,
    ReviewedConceptPreparationReadinessAudit,
    ReviewedConceptScopeBundle,
    build_demo_blocked_missing_support_preparation,
    build_demo_blocked_overbroad_scope_preparation,
    build_demo_blocked_unhandled_counterexample_preparation,
    build_demo_reviewed_concept_preparation_packet,
    build_reviewed_concept_evidence_bundle,
    build_reviewed_concept_preparation_packet,
    build_reviewed_concept_preparation_readiness_audit,
    build_reviewed_concept_scope_bundle,
    validate_reviewed_concept_evidence_bundle,
    validate_reviewed_concept_preparation_packet,
    validate_reviewed_concept_preparation_readiness_audit,
    validate_reviewed_concept_scope_bundle,
)
from ashl_core_v1.learning.concept_candidate_from_task_closure_draft import (
    build_demo_draft,
)
from ashl_core_v1.learning.concept_candidate_refinement_from_teacher_review import (
    build_demo_teacher_review_ready_refinement,
)
from ashl_core_v1.learning.concept_candidate_teacher_review import (
    build_demo_teacher_review_ready_review,
)


class ReviewedConceptPreparationTests(unittest.TestCase):
    def test_build_evidence_bundle_succeeds_with_valid_support_evidence(self) -> None:
        bundle = self._valid_evidence_bundle()
        validation = validate_reviewed_concept_evidence_bundle(bundle)
        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(validation["support_evidence_count"], 1)

    def test_evidence_bundle_blocks_missing_support_evidence(self) -> None:
        bundle = ReviewedConceptEvidenceBundle.from_dict(
            dict(build_demo_blocked_missing_support_preparation()["evidence_bundle"])
        )
        self.assertEqual(bundle.evidence_bundle_status, "blocked_no_support_evidence")
        self.assertFalse(validate_reviewed_concept_evidence_bundle(bundle)["valid"])

    def test_evidence_bundle_blocks_invalid_evidence_refs(self) -> None:
        candidate = build_demo_draft("unknown").drafted_concept_candidate
        support = candidate.support_evidence_refs[0]
        invalid_support = support.__class__.from_dict(
            {**support.to_dict(), "source_record_id": ""}
        )
        data = candidate.to_dict()
        data["support_evidence_refs"] = [invalid_support.to_dict()]
        candidate = candidate.__class__.from_dict(data)
        bundle = build_reviewed_concept_evidence_bundle(
            candidate=candidate,
            draft=build_demo_draft("unknown"),
            marker=self._marker(),
            teacher_note="Support is checked.",
        )
        self.assertEqual(bundle.evidence_bundle_status, "blocked_invalid_evidence_refs")

    def test_evidence_bundle_blocks_unhandled_counterexamples(self) -> None:
        bundle = ReviewedConceptEvidenceBundle.from_dict(
            dict(build_demo_blocked_unhandled_counterexample_preparation()["evidence_bundle"])
        )
        self.assertEqual(
            bundle.evidence_bundle_status,
            "blocked_unhandled_counterexamples",
        )

    def test_scope_bundle_succeeds_with_valid_scope(self) -> None:
        bundle = self._valid_scope_bundle()
        validation = validate_reviewed_concept_scope_bundle(bundle)
        self.assertTrue(validation["valid"], validation["error_codes"])

    def test_scope_bundle_blocks_missing_scope(self) -> None:
        bundle = self._valid_scope_bundle()
        data = bundle.to_dict()
        data["scope_text"] = ""
        invalid = ReviewedConceptScopeBundle.from_dict(data)
        validation = validate_reviewed_concept_scope_bundle(invalid)
        self.assertFalse(validation["valid"])
        self.assertIn("missing_scope_text", validation["error_codes"])

    def test_scope_bundle_blocks_overbroad_needs_split(self) -> None:
        bundle = ReviewedConceptScopeBundle.from_dict(
            dict(build_demo_blocked_overbroad_scope_preparation()["scope_bundle"])
        )
        self.assertEqual(bundle.scope_bundle_status, "blocked_scope_overbroad")

    def test_scope_bundle_blocks_invalid_confidence(self) -> None:
        bundle = self._valid_scope_bundle()
        data = bundle.to_dict()
        data["scope_confidence"] = 1.5
        invalid = ReviewedConceptScopeBundle.from_dict(data)
        validation = validate_reviewed_concept_scope_bundle(invalid)
        self.assertFalse(validation["valid"])
        self.assertIn("invalid_scope_confidence", validation["error_codes"])

    def test_readiness_audit_passes_for_valid_teacher_review_ready_marker(self) -> None:
        audit = ReviewedConceptPreparationReadinessAudit.from_dict(
            dict(build_demo_reviewed_concept_preparation_packet()["readiness_audit"])
        )
        validation = validate_reviewed_concept_preparation_readiness_audit(audit)
        self.assertTrue(validation["valid"], validation["error_codes"])

    def test_readiness_audit_blocks_missing_preparation_marker(self) -> None:
        audit = self._audit_with_marker(None)
        self.assertEqual(
            audit.readiness_status,
            "blocked_missing_teacher_review_ready_marker",
        )

    def test_readiness_audit_blocks_invalid_teacher_review_decision(self) -> None:
        review = build_demo_teacher_review_ready_review()
        decision = dict(review["review_decision"])
        decision["teacher_decision"] = "needs_more_support"
        audit = self._audit_with_decision(decision)
        self.assertEqual(audit.readiness_status, "blocked_invalid_teacher_review_decision")

    def test_readiness_audit_blocks_missing_support_evidence(self) -> None:
        audit = ReviewedConceptPreparationReadinessAudit.from_dict(
            dict(build_demo_blocked_missing_support_preparation()["readiness_audit"])
        )
        self.assertEqual(audit.readiness_status, "blocked_missing_support_evidence")

    def test_readiness_audit_blocks_unhandled_counterexamples(self) -> None:
        audit = ReviewedConceptPreparationReadinessAudit.from_dict(
            dict(build_demo_blocked_unhandled_counterexample_preparation()["readiness_audit"])
        )
        self.assertEqual(audit.readiness_status, "blocked_unhandled_counterexamples")

    def test_preparation_packet_succeeds_for_valid_teacher_review_ready_refinement(self) -> None:
        packet = ReviewedConceptPreparationPacket.from_dict(
            dict(build_demo_reviewed_concept_preparation_packet()["preparation_packet"])
        )
        validation = validate_reviewed_concept_preparation_packet(packet)
        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(packet.packet_status, "packet_ready")

    def test_preparation_packet_preserves_source_concept_candidate_id(self) -> None:
        packet = self._valid_packet()
        self.assertTrue(packet.source_concept_candidate_id)

    def test_preparation_packet_preserves_source_review_decision_id(self) -> None:
        packet = self._valid_packet()
        self.assertIn("teacher_review_ready", packet.source_review_decision_id)

    def test_preparation_packet_preserves_source_refinement_id(self) -> None:
        packet = self._valid_packet()
        self.assertIn("concept_refinement", packet.source_refinement_id)

    def test_preparation_packet_ready_for_future_reviewed_concept_package_true(self) -> None:
        packet = self._valid_packet()
        self.assertTrue(packet.ready_for_future_reviewed_concept_package)

    def test_preparation_packet_reviewed_concept_created_false(self) -> None:
        packet = self._valid_packet()
        self.assertFalse(packet.reviewed_concept_created)

    def test_preparation_packet_concept_approved_false(self) -> None:
        packet = self._valid_packet()
        self.assertFalse(packet.concept_approved)

    def test_preparation_packet_memory_write_performed_false(self) -> None:
        packet = self._valid_packet()
        self.assertFalse(packet.memory_write_performed)

    def test_preparation_packet_task_behavior_changed_false(self) -> None:
        packet = self._valid_packet()
        self.assertFalse(packet.task_behavior_changed)

    def test_preparation_packet_automatic_learning_approval_created_false(self) -> None:
        packet = self._valid_packet()
        self.assertFalse(packet.automatic_learning_approval_created)

    def test_blocked_missing_support_demo_blocks(self) -> None:
        packet = ReviewedConceptPreparationPacket.from_dict(
            dict(build_demo_blocked_missing_support_preparation()["preparation_packet"])
        )
        self.assertEqual(packet.packet_status, "blocked_invalid_evidence_bundle")

    def test_blocked_unhandled_counterexample_demo_blocks(self) -> None:
        packet = ReviewedConceptPreparationPacket.from_dict(
            dict(build_demo_blocked_unhandled_counterexample_preparation()["preparation_packet"])
        )
        self.assertEqual(packet.packet_status, "blocked_invalid_evidence_bundle")

    def test_blocked_overbroad_scope_demo_blocks(self) -> None:
        packet = ReviewedConceptPreparationPacket.from_dict(
            dict(build_demo_blocked_overbroad_scope_preparation()["preparation_packet"])
        )
        self.assertEqual(packet.packet_status, "blocked_invalid_scope_bundle")

    def test_cli_prepare_demo_works(self) -> None:
        result = self._run_learning_cli("prepare-demo")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("packet_ready", result.stdout)

    def test_cli_show_demo_packet_works(self) -> None:
        result = self._run_learning_cli("show-demo-packet")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("preparation_packet", result.stdout)

    def test_cli_validate_demo_packet_works(self) -> None:
        result = self._run_learning_cli("validate-demo-packet")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"valid": true', result.stdout)

    def test_cli_blocked_missing_support_works(self) -> None:
        result = self._run_learning_cli(
            "prepare-demo-blocked",
            "--case",
            "missing-support",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("blocked_no_support_evidence", result.stdout)

    def test_cli_blocked_unhandled_counterexample_works(self) -> None:
        result = self._run_learning_cli(
            "prepare-demo-blocked",
            "--case",
            "unhandled-counterexample",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("blocked_unhandled_counterexamples", result.stdout)

    def test_cli_blocked_overbroad_scope_works(self) -> None:
        result = self._run_learning_cli(
            "prepare-demo-blocked",
            "--case",
            "overbroad-scope",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("blocked_scope_overbroad", result.stdout)

    def test_guided_console_learning_prepare_reviewed_concept_demo_works(self) -> None:
        result = self._run_guided_cli("learning-prepare-reviewed-concept-demo")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("preparation_packet", result.stdout)

    def test_guided_console_show_reviewed_concept_preparation_demo_works(self) -> None:
        result = self._run_guided_cli(
            "learning-show-reviewed-concept-preparation-demo"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("packet_ready", result.stdout)

    def test_guided_console_validate_reviewed_concept_preparation_demo_works(self) -> None:
        result = self._run_guided_cli(
            "learning-validate-reviewed-concept-preparation-demo"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"valid": true', result.stdout)

    def test_no_repo_data_created(self) -> None:
        build_demo_reviewed_concept_preparation_packet()
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _valid_packet(self) -> ReviewedConceptPreparationPacket:
        return ReviewedConceptPreparationPacket.from_dict(
            dict(build_demo_reviewed_concept_preparation_packet()["preparation_packet"])
        )

    def _valid_evidence_bundle(self) -> ReviewedConceptEvidenceBundle:
        return ReviewedConceptEvidenceBundle.from_dict(
            dict(build_demo_reviewed_concept_preparation_packet()["evidence_bundle"])
        )

    def _valid_scope_bundle(self) -> ReviewedConceptScopeBundle:
        return ReviewedConceptScopeBundle.from_dict(
            dict(build_demo_reviewed_concept_preparation_packet()["scope_bundle"])
        )

    def _marker(self):
        return build_demo_teacher_review_ready_refinement()[
            "future_reviewed_concept_preparation_marker"
        ]

    def _audit_with_marker(self, marker) -> ReviewedConceptPreparationReadinessAudit:
        review = build_demo_teacher_review_ready_review()
        refinement = build_demo_teacher_review_ready_refinement()
        draft = build_demo_draft("unknown")
        candidate = draft.drafted_concept_candidate
        evidence = build_reviewed_concept_evidence_bundle(
            candidate=candidate,
            draft=draft,
            marker=marker,
            teacher_note=review["review_decision"]["teacher_note"],
        )
        scope = build_reviewed_concept_scope_bundle(candidate=candidate, marker=marker)
        return build_reviewed_concept_preparation_readiness_audit(
            candidate=candidate,
            draft=draft,
            decision=review["review_decision"],
            refinement=refinement["refinement_record"],
            marker=marker,
            evidence_bundle=evidence,
            scope_bundle=scope,
        )

    def _audit_with_decision(self, decision) -> ReviewedConceptPreparationReadinessAudit:
        review = build_demo_teacher_review_ready_review()
        refinement = build_demo_teacher_review_ready_refinement()
        draft = build_demo_draft("unknown")
        candidate = draft.drafted_concept_candidate
        marker = refinement["future_reviewed_concept_preparation_marker"]
        evidence = build_reviewed_concept_evidence_bundle(
            candidate=candidate,
            draft=draft,
            marker=marker,
            teacher_note=decision["teacher_note"],
        )
        scope = build_reviewed_concept_scope_bundle(candidate=candidate, marker=marker)
        return build_reviewed_concept_preparation_readiness_audit(
            candidate=candidate,
            draft=draft,
            decision=decision,
            refinement=refinement["refinement_record"],
            marker=marker,
            evidence_bundle=evidence,
            scope_bundle=scope,
        )

    def _run_learning_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core_v1.learning.reviewed_concept_preparation_cli",
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
