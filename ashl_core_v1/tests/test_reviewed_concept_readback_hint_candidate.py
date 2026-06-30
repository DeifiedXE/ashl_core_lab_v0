from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from ashl_core_v1.memory.reviewed_concept_readback_hint_candidate import (
    ReviewedConceptReadbackHintCandidate,
    ReviewedConceptReadbackHintCandidateSafetyAudit,
    ReviewedConceptReadbackHintCandidateSet,
    build_demo_blocked_forbidden_behavior_change_candidate_set,
    build_demo_blocked_forbidden_working_memory_mutation_candidate_set,
    build_demo_blocked_invalid_hint_preview_candidate_set,
    build_demo_held_for_more_evidence_hint_candidate_set,
    build_demo_reviewed_concept_readback_hint_candidate_set,
    build_reviewed_concept_readback_hint_candidate,
    build_reviewed_concept_readback_hint_candidate_set,
    build_reviewed_concept_readback_hint_candidate_safety_audit,
    validate_reviewed_concept_readback_hint_candidate,
    validate_reviewed_concept_readback_hint_candidate_safety_audit,
    validate_reviewed_concept_readback_hint_candidate_set,
)
from ashl_core_v1.memory.reviewed_concept_working_readback_preview import (
    ReviewedConceptWorkingReadbackHintPreview,
    ReviewedConceptWorkingReadbackPreview,
    build_demo_reviewed_concept_working_readback_preview_bundle,
)


class ReviewedConceptReadbackHintCandidateTests(unittest.TestCase):
    def test_hint_candidate_builds_from_observe_before_direct_retry(self) -> None:
        candidate = self._candidate_for_label("observe_before_direct_retry")
        validation = validate_reviewed_concept_readback_hint_candidate(candidate)
        self.assertTrue(validation["valid"], validation["error_codes"])

    def test_observe_before_direct_retry_maps_to_observe_before_retry(self) -> None:
        self.assertEqual(
            self._candidate_for_label("observe_before_direct_retry").hint_kind,
            "observe_before_retry",
        )

    def test_avoid_same_failed_direct_retry_maps_to_avoid_repeated_failure(self) -> None:
        self.assertEqual(
            self._candidate_for_label("avoid_same_failed_direct_retry").hint_kind,
            "avoid_repeated_failure",
        )

    def test_verify_obstacle_type_before_generalizing_maps_to_verify_scope(self) -> None:
        self.assertEqual(
            self._candidate_for_label("verify_obstacle_type_before_generalizing").hint_kind,
            "verify_scope",
        )

    def test_unknown_observe_or_adjust_maps_to_gather_context(self) -> None:
        self.assertEqual(
            self._candidate_for_label("observe_or_adjust").hint_kind,
            "gather_context",
        )

    def test_expected_actual_mismatch_labels_map_to_verify_expected_actual(self) -> None:
        for label in (
            "verify_expected_actual_before_reuse",
            "do_not_reuse_unverified_prediction",
            "prefer_low_risk_verification",
        ):
            with self.subTest(label=label):
                self.assertEqual(
                    self._candidate_for_label(label).hint_kind,
                    "verify_expected_actual",
                )

    def test_known_success_path_available_maps_to_use_known_success_path(self) -> None:
        self.assertEqual(
            self._candidate_for_label("known_success_path_available").hint_kind,
            "use_known_success_path",
        )

    def test_candidate_set_builds_from_valid_hint_preview(self) -> None:
        candidate_set = self._valid_candidate_set()
        validation = validate_reviewed_concept_readback_hint_candidate_set(candidate_set)
        self.assertTrue(validation["valid"], validation["error_codes"])

    def test_candidate_set_preserves_reviewed_concept_id(self) -> None:
        payload = self._valid_payload()
        candidate_set = self._valid_candidate_set()
        self.assertEqual(
            candidate_set.source_reviewed_concept_id,
            payload["working_readback_preview"]["source_reviewed_concept_id"],
        )

    def test_candidate_set_preserves_readback_preview_id(self) -> None:
        payload = self._valid_payload()
        candidate_set = self._valid_candidate_set()
        self.assertEqual(
            candidate_set.source_working_readback_preview_id,
            payload["working_readback_preview"]["working_readback_preview_id"],
        )

    def test_candidate_set_candidate_count_matches_labels(self) -> None:
        candidate_set = self._valid_candidate_set()
        self.assertEqual(candidate_set.candidate_count, len(candidate_set.candidate_labels))

    def test_candidate_set_requires_teacher_review_before_application_true(self) -> None:
        self.assertTrue(self._valid_candidate_set().requires_teacher_review_before_application)

    def test_candidate_authority_flags_false(self) -> None:
        for candidate in self._valid_candidate_set().hint_candidates:
            with self.subTest(label=candidate.hint_label):
                self.assertFalse(candidate.actual_task_working_memory_hint_created)
                self.assertFalse(candidate.applied_to_working_memory)
                self.assertFalse(candidate.working_memory_mutated)
                self.assertFalse(candidate.task_behavior_changed)
                self.assertFalse(candidate.candidate_ordering_changed)
                self.assertFalse(candidate.action_selection_created)
                self.assertFalse(candidate.action_execution_created)

    def test_scope_warnings_preserved(self) -> None:
        warnings = tuple(
            candidate.scope_warning for candidate in self._valid_candidate_set().hint_candidates
        )
        self.assertTrue(any("front_blocked may be too broad" in warning for warning in warnings if warning))

    def test_counterexample_warnings_preserved(self) -> None:
        warnings = tuple(
            candidate.counterexample_warning
            for candidate in self._valid_candidate_set().hint_candidates
        )
        self.assertTrue(
            any("front_blocked + step_forward succeeds" in warning for warning in warnings if warning)
        )

    def test_held_for_more_evidence_demo_creates_held_candidate_set(self) -> None:
        payload = build_demo_held_for_more_evidence_hint_candidate_set()
        candidate_set = ReviewedConceptReadbackHintCandidateSet.from_dict(
            payload["hint_candidate_set"]
        )
        self.assertEqual(candidate_set.set_status, "held_for_more_evidence")

    def test_invalid_hint_preview_blocks(self) -> None:
        payload = build_demo_blocked_invalid_hint_preview_candidate_set()
        candidate_set = ReviewedConceptReadbackHintCandidateSet.from_dict(
            payload["hint_candidate_set"]
        )
        self.assertEqual(candidate_set.set_status, "blocked_invalid_hint_preview")

    def test_empty_hint_labels_block(self) -> None:
        payload = self._valid_payload()
        hint_data = dict(payload["working_readback_hint_preview"])
        hint_data["hint_labels"] = []
        hint = ReviewedConceptWorkingReadbackHintPreview.from_dict(hint_data)
        candidate_set = build_reviewed_concept_readback_hint_candidate_set(
            readback_preview=payload["working_readback_preview"],
            hint_preview=hint,
        )
        self.assertEqual(candidate_set.set_status, "blocked_empty_candidate_set")

    def test_forbidden_actual_hint_creation_blocks_safety_audit(self) -> None:
        audit = self._audit_with_candidate_flag(
            "actual_task_working_memory_hint_created",
            True,
        )
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_hint_creation_detected",
        )

    def test_forbidden_working_memory_mutation_blocks_safety_audit(self) -> None:
        audit = self._audit_with_candidate_flag("working_memory_mutated", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_working_memory_mutation_detected",
        )

    def test_forbidden_task_behavior_change_blocks_safety_audit(self) -> None:
        audit = self._audit_with_candidate_flag("task_behavior_changed", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_behavior_change_detected",
        )

    def test_forbidden_candidate_ordering_change_blocks_safety_audit(self) -> None:
        audit = self._audit_with_candidate_flag("candidate_ordering_changed", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_behavior_change_detected",
        )

    def test_forbidden_action_selection_blocks_safety_audit(self) -> None:
        audit = self._audit_with_candidate_flag("action_selection_created", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_action_authority_detected",
        )

    def test_forbidden_action_execution_blocks_safety_audit(self) -> None:
        audit = self._audit_with_candidate_flag("action_execution_created", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_action_authority_detected",
        )

    def test_forbidden_memory_layer_write_blocks_safety_audit(self) -> None:
        audit = self._audit_with_candidate_flag("memory_layer_write_performed", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_memory_write_detected",
        )

    def test_blocked_forbidden_working_memory_mutation_demo_blocks(self) -> None:
        payload = build_demo_blocked_forbidden_working_memory_mutation_candidate_set()
        self.assertEqual(
            payload["hint_candidate_safety_audit"]["audit_status"],
            "blocked_forbidden_working_memory_mutation_detected",
        )

    def test_blocked_forbidden_behavior_change_demo_blocks(self) -> None:
        payload = build_demo_blocked_forbidden_behavior_change_candidate_set()
        self.assertEqual(
            payload["hint_candidate_safety_audit"]["audit_status"],
            "blocked_forbidden_behavior_change_detected",
        )

    def test_safety_audit_passes_for_valid_candidate_set(self) -> None:
        payload = build_demo_reviewed_concept_readback_hint_candidate_set()
        validation = validate_reviewed_concept_readback_hint_candidate_safety_audit(
            payload["hint_candidate_safety_audit"]
        )
        self.assertTrue(validation["valid"], validation["error_codes"])

    def test_cli_build_demo_candidates_works(self) -> None:
        result = self._run_memory_cli("build-demo-candidates")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("candidate_set_created", result.stdout)

    def test_cli_show_demo_candidates_works(self) -> None:
        result = self._run_memory_cli("show-demo-candidates")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("observe_before_direct_retry", result.stdout)

    def test_cli_show_demo_safety_audit_works(self) -> None:
        result = self._run_memory_cli("show-demo-safety-audit")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"audit_status": "passed"', result.stdout)

    def test_cli_validate_demo_candidates_works(self) -> None:
        result = self._run_memory_cli("validate-demo-candidates")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"valid": true', result.stdout)

    def test_cli_held_more_evidence_works(self) -> None:
        result = self._run_memory_cli("build-demo-held", "--case", "more-evidence")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("held_for_more_evidence", result.stdout)

    def test_cli_blocked_invalid_hint_preview_works(self) -> None:
        result = self._run_memory_cli(
            "build-demo-blocked",
            "--case",
            "invalid-hint-preview",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("blocked_invalid_hint_preview", result.stdout)

    def test_cli_blocked_forbidden_working_memory_mutation_works(self) -> None:
        result = self._run_memory_cli(
            "build-demo-blocked",
            "--case",
            "forbidden-working-memory-mutation",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("blocked_forbidden_working_memory_mutation_detected", result.stdout)

    def test_cli_blocked_forbidden_behavior_change_works(self) -> None:
        result = self._run_memory_cli(
            "build-demo-blocked",
            "--case",
            "forbidden-behavior-change",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("blocked_forbidden_behavior_change_detected", result.stdout)

    def test_guided_console_readback_hint_candidate_demo_works(self) -> None:
        for command in (
            "memory-build-reviewed-concept-hint-candidates-demo",
            "memory-show-reviewed-concept-hint-candidates",
            "memory-validate-reviewed-concept-hint-candidates",
        ):
            result = self._run_guided_cli(command)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("guided_console_action", result.stdout)

    def test_no_repo_data_created(self) -> None:
        build_demo_reviewed_concept_readback_hint_candidate_set()
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _valid_payload(self) -> dict[str, object]:
        return build_demo_reviewed_concept_working_readback_preview_bundle()

    def _valid_candidate_set(self) -> ReviewedConceptReadbackHintCandidateSet:
        payload = build_demo_reviewed_concept_readback_hint_candidate_set()
        return ReviewedConceptReadbackHintCandidateSet.from_dict(
            payload["hint_candidate_set"]
        )

    def _candidate_for_label(self, label: str) -> ReviewedConceptReadbackHintCandidate:
        payload = self._valid_payload()
        hint_data = dict(payload["working_readback_hint_preview"])
        hint_data["hint_labels"] = [label]
        hint = ReviewedConceptWorkingReadbackHintPreview.from_dict(hint_data)
        return build_reviewed_concept_readback_hint_candidate(
            readback_preview=payload["working_readback_preview"],
            hint_preview=hint,
            hint_label=label,
        )

    def _audit_with_candidate_flag(
        self,
        flag_name: str,
        flag_value: bool,
    ) -> ReviewedConceptReadbackHintCandidateSafetyAudit:
        payload = build_demo_reviewed_concept_readback_hint_candidate_set()
        readback_payload = self._valid_payload()
        candidates = [
            ReviewedConceptReadbackHintCandidate.from_dict(item)
            for item in payload["hint_candidates"]
        ]
        first = dict(candidates[0].to_dict())
        first[flag_name] = flag_value
        candidates[0] = ReviewedConceptReadbackHintCandidate.from_dict(first)
        candidate_set = ReviewedConceptReadbackHintCandidateSet.from_dict(
            {
                **payload["hint_candidate_set"],
                "hint_candidates": [candidate.to_dict() for candidate in candidates],
            }
        )
        return build_reviewed_concept_readback_hint_candidate_safety_audit(
            readback_preview=readback_payload["working_readback_preview"],
            hint_preview=readback_payload["working_readback_hint_preview"],
            candidate_set=candidate_set,
        )

    def _run_memory_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core_v1.memory.reviewed_concept_readback_hint_candidate_cli",
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
