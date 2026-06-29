from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from ashl_core_v1.learning.reviewed_concept_preparation import (
    ReviewedConceptPreparationReadinessAudit,
    build_demo_reviewed_concept_preparation_packet,
)
from ashl_core_v1.learning.reviewed_concept_record import (
    ReviewedConceptLineageRecord,
    ReviewedConceptRecord,
    ReviewedConceptSafetyAuditRecord,
    build_demo_blocked_invalid_preparation_packet,
    build_demo_blocked_invalid_scope,
    build_demo_blocked_reviewed_concept,
    build_demo_blocked_unhandled_counterexample,
    build_demo_reviewed_concept_record,
    build_reviewed_concept_record_bundle,
    build_reviewed_concept_safety_audit,
    validate_reviewed_concept_lineage_record,
    validate_reviewed_concept_record,
    validate_reviewed_concept_safety_audit,
)


class ReviewedConceptRecordTests(unittest.TestCase):
    def test_build_reviewed_concept_from_valid_preparation_packet_succeeds(self) -> None:
        reviewed = self._valid_reviewed_concept()
        self.assertEqual(reviewed.review_status, "reviewed")

    def test_reviewed_concept_preserves_source_preparation_packet_id(self) -> None:
        payload = build_demo_reviewed_concept_record()
        reviewed = ReviewedConceptRecord.from_dict(payload["reviewed_concept"])
        preparation = build_demo_reviewed_concept_preparation_packet()["preparation_packet"]
        self.assertEqual(
            reviewed.source_preparation_packet_id,
            preparation["preparation_packet_id"],
        )

    def test_reviewed_concept_preserves_source_concept_candidate_id(self) -> None:
        reviewed = self._valid_reviewed_concept()
        self.assertTrue(reviewed.source_concept_candidate_id)

    def test_reviewed_concept_preserves_source_review_decision_id(self) -> None:
        reviewed = self._valid_reviewed_concept()
        self.assertIn("teacher_review_ready", reviewed.source_review_decision_id)

    def test_reviewed_concept_preserves_source_refinement_id(self) -> None:
        reviewed = self._valid_reviewed_concept()
        self.assertIn("concept_refinement", reviewed.source_refinement_id)

    def test_reviewed_concept_includes_support_evidence_refs(self) -> None:
        reviewed = self._valid_reviewed_concept()
        self.assertGreaterEqual(len(reviewed.support_evidence_refs), 1)

    def test_reviewed_concept_includes_counterexample_evidence_refs_field(self) -> None:
        reviewed = self._valid_reviewed_concept()
        self.assertIsInstance(reviewed.counterexample_evidence_refs, tuple)

    def test_reviewed_concept_includes_scope_text(self) -> None:
        reviewed = self._valid_reviewed_concept()
        self.assertTrue(reviewed.scope_text)

    def test_reviewed_concept_includes_teacher_note(self) -> None:
        reviewed = self._valid_reviewed_concept()
        self.assertTrue(reviewed.teacher_note)

    def test_reviewed_concept_review_status_reviewed(self) -> None:
        reviewed = self._valid_reviewed_concept()
        self.assertEqual(reviewed.review_status, "reviewed")

    def test_reviewed_concept_status_reviewed_record_only(self) -> None:
        reviewed = self._valid_reviewed_concept()
        self.assertEqual(reviewed.reviewed_concept_status, "reviewed_record_only")

    def test_reviewed_concept_memory_write_allowed_false(self) -> None:
        self.assertFalse(self._valid_reviewed_concept().memory_write_allowed)

    def test_reviewed_concept_memory_write_performed_false(self) -> None:
        self.assertFalse(self._valid_reviewed_concept().memory_write_performed)

    def test_reviewed_concept_memory_application_candidate_allowed_false(self) -> None:
        self.assertFalse(
            self._valid_reviewed_concept().memory_application_candidate_allowed
        )

    def test_reviewed_concept_task_behavior_change_allowed_false(self) -> None:
        self.assertFalse(self._valid_reviewed_concept().task_behavior_change_allowed)

    def test_reviewed_concept_task_behavior_changed_false(self) -> None:
        self.assertFalse(self._valid_reviewed_concept().task_behavior_changed)

    def test_reviewed_concept_promotion_candidate_allowed_false(self) -> None:
        self.assertFalse(self._valid_reviewed_concept().promotion_candidate_allowed)

    def test_reviewed_concept_automatic_learning_approval_created_false(self) -> None:
        self.assertFalse(
            self._valid_reviewed_concept().automatic_learning_approval_created
        )

    def test_lineage_record_complete_for_valid_demo(self) -> None:
        lineage = self._valid_lineage()
        validation = validate_reviewed_concept_lineage_record(lineage)
        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertTrue(lineage.lineage_complete)

    def test_safety_audit_passes_for_valid_demo(self) -> None:
        audit = self._valid_safety_audit()
        validation = validate_reviewed_concept_safety_audit(audit)
        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(audit.audit_status, "passed")

    def test_invalid_preparation_packet_blocks(self) -> None:
        reviewed = ReviewedConceptRecord.from_dict(
            build_demo_blocked_invalid_preparation_packet()["reviewed_concept"]
        )
        self.assertEqual(reviewed.review_status, "blocked_invalid_preparation_packet")

    def test_failed_readiness_audit_blocks(self) -> None:
        payload = build_demo_reviewed_concept_preparation_packet()
        readiness = dict(payload["readiness_audit"])
        readiness["readiness_status"] = "blocked_scope_not_ready"
        readiness["blocked_reasons"] = ["blocked_scope_not_ready"]
        readiness["scope_bundle_ready"] = False
        blocked = build_reviewed_concept_record_bundle(
            {**payload, "readiness_audit": readiness}
        )
        reviewed = ReviewedConceptRecord.from_dict(blocked["reviewed_concept"])
        audit = ReviewedConceptSafetyAuditRecord.from_dict(blocked["safety_audit"])
        self.assertEqual(reviewed.review_status, "blocked_readiness_audit_failed")
        self.assertEqual(audit.audit_status, "blocked_readiness_audit_failed")

    def test_missing_support_evidence_blocks(self) -> None:
        audit = ReviewedConceptSafetyAuditRecord.from_dict(
            build_demo_blocked_invalid_preparation_packet()["safety_audit"]
        )
        self.assertEqual(audit.audit_status, "blocked_missing_support_evidence")

    def test_unhandled_counterexamples_block(self) -> None:
        reviewed = ReviewedConceptRecord.from_dict(
            build_demo_blocked_unhandled_counterexample()["reviewed_concept"]
        )
        self.assertEqual(reviewed.review_status, "blocked_unhandled_counterexamples")

    def test_invalid_scope_blocks(self) -> None:
        reviewed = ReviewedConceptRecord.from_dict(
            build_demo_blocked_invalid_scope()["reviewed_concept"]
        )
        self.assertEqual(reviewed.review_status, "blocked_invalid_scope")

    def test_forbidden_memory_write_allowed_true_blocks_safety_audit(self) -> None:
        audit = self._audit_with_reviewed_flag("memory_write_allowed", True)
        self.assertEqual(audit.audit_status, "blocked_forbidden_authority_detected")

    def test_forbidden_memory_write_performed_true_blocks_safety_audit(self) -> None:
        audit = self._audit_with_reviewed_flag("memory_write_performed", True)
        self.assertEqual(audit.audit_status, "blocked_forbidden_authority_detected")

    def test_forbidden_task_behavior_change_allowed_true_blocks_safety_audit(self) -> None:
        audit = self._audit_with_reviewed_flag("task_behavior_change_allowed", True)
        self.assertEqual(audit.audit_status, "blocked_forbidden_authority_detected")

    def test_forbidden_promotion_candidate_allowed_true_blocks_safety_audit(self) -> None:
        audit = self._audit_with_reviewed_flag("promotion_candidate_allowed", True)
        self.assertEqual(audit.audit_status, "blocked_forbidden_authority_detected")

    def test_safe_claim_contains_not_memory_admission(self) -> None:
        reviewed = self._valid_reviewed_concept()
        self.assertIn("not memory admission", reviewed.safe_claim)

    def test_blocked_claims_include_no_memory_write(self) -> None:
        reviewed = self._valid_reviewed_concept()
        self.assertIn("no_memory_write", reviewed.blocked_claims)

    def test_validate_reviewed_concept_record_passes_valid_demo(self) -> None:
        validation = validate_reviewed_concept_record(self._valid_reviewed_concept())
        self.assertTrue(validation["valid"], validation["error_codes"])

    def test_cli_build_demo_reviewed_concept_works(self) -> None:
        result = self._run_learning_cli("build-demo-reviewed-concept")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("reviewed_record_only", result.stdout)

    def test_cli_show_demo_reviewed_concept_works(self) -> None:
        result = self._run_learning_cli("show-demo-reviewed-concept")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("reviewed_concept", result.stdout)

    def test_cli_validate_demo_reviewed_concept_works(self) -> None:
        result = self._run_learning_cli("validate-demo-reviewed-concept")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"valid": true', result.stdout)

    def test_cli_blocked_invalid_preparation_works(self) -> None:
        result = self._run_learning_cli(
            "build-demo-blocked",
            "--case",
            "invalid-preparation",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("blocked_invalid_preparation_packet", result.stdout)

    def test_cli_blocked_unhandled_counterexample_works(self) -> None:
        result = self._run_learning_cli(
            "build-demo-blocked",
            "--case",
            "unhandled-counterexample",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("blocked_unhandled_counterexamples", result.stdout)

    def test_cli_blocked_invalid_scope_works(self) -> None:
        result = self._run_learning_cli(
            "build-demo-blocked",
            "--case",
            "invalid-scope",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("blocked_invalid_scope", result.stdout)

    def test_guided_console_reviewed_concept_demo_commands_work(self) -> None:
        for command in (
            "learning-build-reviewed-concept-demo",
            "learning-show-reviewed-concept-demo",
            "learning-validate-reviewed-concept-demo",
        ):
            result = self._run_guided_cli(command)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("reviewed_concept", result.stdout)

    def test_no_repo_data_created(self) -> None:
        build_demo_blocked_reviewed_concept("invalid-preparation")
        build_demo_reviewed_concept_record()
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _valid_payload(self) -> dict[str, object]:
        return build_demo_reviewed_concept_record()

    def _valid_reviewed_concept(self) -> ReviewedConceptRecord:
        return ReviewedConceptRecord.from_dict(self._valid_payload()["reviewed_concept"])

    def _valid_lineage(self) -> ReviewedConceptLineageRecord:
        return ReviewedConceptLineageRecord.from_dict(
            self._valid_payload()["lineage_record"]
        )

    def _valid_safety_audit(self) -> ReviewedConceptSafetyAuditRecord:
        return ReviewedConceptSafetyAuditRecord.from_dict(
            self._valid_payload()["safety_audit"]
        )

    def _audit_with_reviewed_flag(
        self,
        flag_name: str,
        flag_value: bool,
    ) -> ReviewedConceptSafetyAuditRecord:
        record_payload = self._valid_payload()
        reviewed_data = dict(record_payload["reviewed_concept"])
        reviewed_data[flag_name] = flag_value
        reviewed = ReviewedConceptRecord.from_dict(reviewed_data)
        preparation = build_demo_reviewed_concept_preparation_packet()
        lineage = ReviewedConceptLineageRecord.from_dict(record_payload["lineage_record"])
        return build_reviewed_concept_safety_audit(
            reviewed_concept=reviewed,
            lineage_record=lineage,
            preparation_packet=preparation["preparation_packet"],
            readiness_audit=ReviewedConceptPreparationReadinessAudit.from_dict(
                preparation["readiness_audit"]
            ),
        )

    def _run_learning_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core_v1.learning.reviewed_concept_record_cli",
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
