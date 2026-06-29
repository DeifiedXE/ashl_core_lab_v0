from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from ashl_core_v1.learning.concept_candidate_schema import (
    BLOCKED_CLAIMS,
    ConceptCandidate,
    ConceptEvidenceRef,
    ConceptScopeStatement,
    build_demo_counterexample_split_required_candidate,
    build_demo_front_blocked_concept_candidate,
    summarize_concept_candidate,
    validate_concept_candidate,
    validate_concept_evidence_ref,
    validate_concept_scope_statement,
)


class ConceptCandidateSchemaTests(unittest.TestCase):
    def test_concept_evidence_ref_validates_support_evidence(self) -> None:
        validation = validate_concept_evidence_ref(self._support_evidence())
        self.assertTrue(validation["valid"])
        self.assertTrue(validation["supports_candidate"])

    def test_concept_evidence_ref_validates_counterexample_evidence(self) -> None:
        validation = validate_concept_evidence_ref(self._counterexample_evidence())
        self.assertTrue(validation["valid"])
        self.assertTrue(validation["counterexample_to_candidate"])

    def test_concept_evidence_ref_rejects_both_support_and_counterexample(self) -> None:
        evidence = self._mutated_evidence(
            self._support_evidence(),
            counterexample_to_candidate=True,
        )
        validation = validate_concept_evidence_ref(evidence)
        self.assertFalse(validation["valid"])
        self.assertIn(
            "evidence_cannot_be_support_and_counterexample",
            validation["error_codes"],
        )

    def test_concept_evidence_ref_rejects_missing_source_record_id(self) -> None:
        evidence = self._mutated_evidence(self._support_evidence(), source_record_id="")
        validation = validate_concept_evidence_ref(evidence)
        self.assertFalse(validation["valid"])
        self.assertIn("missing_source_record_id", validation["error_codes"])

    def test_concept_scope_statement_validates_valid_scope(self) -> None:
        validation = validate_concept_scope_statement(self._scope())
        self.assertTrue(validation["valid"])

    def test_concept_scope_statement_rejects_invalid_confidence_below_zero(self) -> None:
        scope = self._mutated_scope(self._scope(), scope_confidence=-0.1)
        validation = validate_concept_scope_statement(scope)
        self.assertFalse(validation["valid"])
        self.assertIn("scope_confidence_below_zero", validation["error_codes"])

    def test_concept_scope_statement_rejects_invalid_confidence_above_one(self) -> None:
        scope = self._mutated_scope(self._scope(), scope_confidence=1.1)
        validation = validate_concept_scope_statement(scope)
        self.assertFalse(validation["valid"])
        self.assertIn("scope_confidence_above_one", validation["error_codes"])

    def test_concept_candidate_validates_demo_front_blocked_candidate(self) -> None:
        candidate = build_demo_front_blocked_concept_candidate()
        validation = validate_concept_candidate(candidate)
        self.assertTrue(validation["valid"])
        self.assertEqual(candidate.concept_label, "front_blocked_affordance")

    def test_concept_candidate_validates_demo_counterexample_candidate(self) -> None:
        candidate = build_demo_counterexample_split_required_candidate()
        validation = validate_concept_candidate(candidate)
        self.assertTrue(validation["valid"])
        self.assertTrue(validation["counterexample_refinement_required"])

    def test_concept_candidate_requires_concept_candidate_id(self) -> None:
        validation = validate_concept_candidate(
            self._mutated_candidate(
                build_demo_front_blocked_concept_candidate(),
                concept_candidate_id="",
            )
        )
        self.assertFalse(validation["valid"])
        self.assertIn("missing_concept_candidate_id", validation["error_codes"])

    def test_concept_candidate_requires_concept_label(self) -> None:
        validation = validate_concept_candidate(
            self._mutated_candidate(
                build_demo_front_blocked_concept_candidate(),
                concept_label="",
            )
        )
        self.assertFalse(validation["valid"])
        self.assertIn("missing_concept_label", validation["error_codes"])

    def test_concept_candidate_requires_source_task_ids(self) -> None:
        validation = validate_concept_candidate(
            self._mutated_candidate(
                build_demo_front_blocked_concept_candidate(),
                source_task_ids=(),
            )
        )
        self.assertFalse(validation["valid"])
        self.assertIn("missing_source_task_ids", validation["error_codes"])

    def test_concept_candidate_requires_source_state_action_outcome_refs(self) -> None:
        validation = validate_concept_candidate(
            self._mutated_candidate(
                build_demo_front_blocked_concept_candidate(),
                source_state_action_outcome_refs=(),
            )
        )
        self.assertFalse(validation["valid"])
        self.assertIn(
            "missing_source_state_action_outcome_refs",
            validation["error_codes"],
        )

    def test_concept_candidate_requires_support_evidence_unless_needs_more_support(self) -> None:
        candidate = self._mutated_candidate(
            build_demo_front_blocked_concept_candidate(),
            support_evidence_refs=(),
            candidate_status="candidate",
        )
        validation = validate_concept_candidate(candidate)
        self.assertFalse(validation["valid"])
        self.assertIn("missing_support_evidence_refs", validation["error_codes"])

    def test_concept_candidate_rejects_overlapping_support_counterexample_refs(self) -> None:
        support = self._support_evidence()
        counterexample = self._mutated_evidence(
            self._counterexample_evidence(),
            evidence_ref_id=support.evidence_ref_id,
        )
        candidate = self._mutated_candidate(
            build_demo_counterexample_split_required_candidate(),
            support_evidence_refs=(support,),
            counterexample_evidence_refs=(counterexample,),
        )
        validation = validate_concept_candidate(candidate)
        self.assertFalse(validation["valid"])
        self.assertIn("support_counterexample_refs_overlap", validation["error_codes"])

    def test_concept_candidate_requires_teacher_review_required_true(self) -> None:
        validation = validate_concept_candidate(
            self._mutated_candidate(
                build_demo_front_blocked_concept_candidate(),
                teacher_review_required=False,
            )
        )
        self.assertFalse(validation["valid"])
        self.assertIn("teacher_review_required_false", validation["error_codes"])

    def test_concept_candidate_rejects_memory_application_candidate_allowed_true(self) -> None:
        validation = validate_concept_candidate(
            self._mutated_candidate(
                build_demo_front_blocked_concept_candidate(),
                memory_application_candidate_allowed=True,
            )
        )
        self.assertFalse(validation["valid"])
        self.assertIn(
            "memory_application_candidate_allowed_true",
            validation["error_codes"],
        )

    def test_concept_candidate_rejects_promotion_candidate_allowed_true(self) -> None:
        validation = validate_concept_candidate(
            self._mutated_candidate(
                build_demo_front_blocked_concept_candidate(),
                promotion_candidate_allowed=True,
            )
        )
        self.assertFalse(validation["valid"])
        self.assertIn("promotion_candidate_allowed_true", validation["error_codes"])

    def test_concept_candidate_requires_blocked_claims(self) -> None:
        validation = validate_concept_candidate(
            self._mutated_candidate(
                build_demo_front_blocked_concept_candidate(),
                blocked_claims=("no_memory_write",),
            )
        )
        self.assertFalse(validation["valid"])
        self.assertIn("blocked_claims_missing", validation["error_codes"])

    def test_counterexample_does_not_auto_delete_candidate(self) -> None:
        candidate = build_demo_counterexample_split_required_candidate()
        validation = validate_concept_candidate(candidate)
        self.assertTrue(validation["valid"])
        self.assertNotIn(candidate.candidate_status, {"invalid", "retired"})

    def test_counterexample_candidate_status_is_scope_narrowed_or_split_required(self) -> None:
        candidate = build_demo_counterexample_split_required_candidate()
        self.assertIn(candidate.candidate_status, {"scope_narrowed", "split_required"})
        self.assertEqual(candidate.counterexample_handling_status, "split_required")

    def test_overbroad_scope_with_counterexample_requires_refinement_status(self) -> None:
        candidate = self._mutated_candidate(
            build_demo_counterexample_split_required_candidate(),
            candidate_status="candidate",
            generalization_status="not_generalized",
            counterexample_handling_status="counterexamples_present",
        )
        validation = validate_concept_candidate(candidate)
        self.assertFalse(validation["valid"])
        self.assertIn(
            "counterexample_requires_refinement_candidate_status",
            validation["error_codes"],
        )

    def test_broad_scope_with_counterexample_fails_without_refinement_scope_status(self) -> None:
        candidate = build_demo_counterexample_split_required_candidate()
        broad_scope = self._mutated_scope(candidate.scope_statement, scope_status="broad")
        validation = validate_concept_candidate(
            self._mutated_candidate(candidate, scope_statement=broad_scope)
        )
        self.assertFalse(validation["valid"])
        self.assertIn(
            "scope:broad_scope_with_counterexample_requires_refinement",
            validation["error_codes"],
        )

    def test_safe_claim_remains_candidate_only(self) -> None:
        validation = validate_concept_candidate(build_demo_front_blocked_concept_candidate())
        self.assertTrue(validation["safe_claim_candidate_only"])
        self.assertFalse(validation["memory_application_candidate_allowed"])
        self.assertFalse(validation["promotion_candidate_allowed"])

    def test_summarize_concept_candidate_returns_compact_summary(self) -> None:
        summary = summarize_concept_candidate(
            build_demo_counterexample_split_required_candidate()
        )
        self.assertEqual(summary["concept_label"], "front_blocked_affordance")
        self.assertEqual(summary["counterexample_evidence_count"], 1)
        self.assertEqual(summary["scope_status"], "overbroad_needs_split")

    def test_cli_show_demo_front_blocked_works(self) -> None:
        result = self._run_cli("show-demo-front-blocked")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("front_blocked_affordance", result.stdout)

    def test_cli_show_demo_counterexample_works(self) -> None:
        result = self._run_cli("show-demo-counterexample")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("split_required", result.stdout)

    def test_cli_validate_demo_front_blocked_works(self) -> None:
        result = self._run_cli("validate-demo-front-blocked")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"valid": true', result.stdout)

    def test_cli_validate_demo_counterexample_works(self) -> None:
        result = self._run_cli("validate-demo-counterexample")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"counterexample_refinement_required": true', result.stdout)

    def test_no_repo_data_created(self) -> None:
        build_demo_front_blocked_concept_candidate()
        build_demo_counterexample_split_required_candidate()
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _support_evidence(self) -> ConceptEvidenceRef:
        return build_demo_front_blocked_concept_candidate().support_evidence_refs[0]

    def _counterexample_evidence(self) -> ConceptEvidenceRef:
        return build_demo_counterexample_split_required_candidate().counterexample_evidence_refs[0]

    def _scope(self) -> ConceptScopeStatement:
        return build_demo_front_blocked_concept_candidate().scope_statement

    def _mutated_evidence(
        self,
        evidence: ConceptEvidenceRef,
        **changes: object,
    ) -> ConceptEvidenceRef:
        data = evidence.to_dict()
        data.update(changes)
        return ConceptEvidenceRef.from_dict(data)

    def _mutated_scope(
        self,
        scope: ConceptScopeStatement,
        **changes: object,
    ) -> ConceptScopeStatement:
        data = scope.to_dict()
        data.update(changes)
        return ConceptScopeStatement.from_dict(data)

    def _mutated_candidate(
        self,
        candidate: ConceptCandidate,
        **changes: object,
    ) -> ConceptCandidate:
        data = candidate.to_dict()
        data.update(changes)
        return ConceptCandidate.from_dict(data)

    def _run_cli(self, command: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core_v1.learning.concept_candidate_schema_cli",
                command,
            ],
            check=False,
            capture_output=True,
            text=True,
        )


if __name__ == "__main__":
    unittest.main()
