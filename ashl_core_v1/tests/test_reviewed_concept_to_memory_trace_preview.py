from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from ashl_core_v1.learning.reviewed_concept_record import (
    ReviewedConceptRecord,
    build_demo_reviewed_concept_record,
)
from ashl_core_v1.learning.reviewed_concept_to_memory_trace_preview import (
    ReviewedConceptMemoryApplicationDataPreview,
    ReviewedConceptMemoryPreviewSafetyAudit,
    ReviewedConceptMemoryRoutingPreview,
    ReviewedConceptMemoryTracePreview,
    build_demo_blocked_forbidden_target_layer_preview,
    build_demo_blocked_unhandled_counterexample_routing_preview,
    build_demo_held_for_more_evidence_overbroad_scope_preview,
    build_demo_reviewed_concept_memory_application_data_preview,
    build_demo_reviewed_concept_memory_preview_bundle,
    build_demo_reviewed_concept_memory_routing_preview,
    build_demo_reviewed_concept_memory_trace_preview,
    build_reviewed_concept_memory_application_data_preview,
    build_reviewed_concept_memory_preview_safety_audit,
    build_reviewed_concept_memory_routing_preview,
    build_reviewed_concept_memory_trace_preview,
    validate_reviewed_concept_memory_application_data_preview,
    validate_reviewed_concept_memory_preview_safety_audit,
    validate_reviewed_concept_memory_routing_preview,
    validate_reviewed_concept_memory_trace_preview,
)


class ReviewedConceptToMemoryTracePreviewTests(unittest.TestCase):
    def test_memory_trace_preview_builds_from_valid_reviewed_concept(self) -> None:
        trace = build_demo_reviewed_concept_memory_trace_preview()
        validation = validate_reviewed_concept_memory_trace_preview(trace)
        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(trace.trace_preview_status, "preview_ready")

    def test_memory_trace_preview_preserves_reviewed_concept_id(self) -> None:
        payload = build_demo_reviewed_concept_record()
        trace = self._trace_from_payload(payload)
        reviewed = ReviewedConceptRecord.from_dict(payload["reviewed_concept"])
        self.assertEqual(trace.source_reviewed_concept_id, reviewed.reviewed_concept_id)

    def test_memory_trace_preview_preserves_lineage_ids(self) -> None:
        payload = build_demo_reviewed_concept_record()
        trace = self._trace_from_payload(payload)
        self.assertEqual(
            trace.source_reviewed_concept_lineage_id,
            payload["lineage_record"]["lineage_id"],
        )

    def test_memory_trace_preview_includes_support_refs(self) -> None:
        trace = build_demo_reviewed_concept_memory_trace_preview()
        self.assertGreaterEqual(len(trace.support_evidence_refs), 1)

    def test_memory_trace_preview_includes_counterexample_refs_field(self) -> None:
        trace = build_demo_reviewed_concept_memory_trace_preview()
        self.assertIsInstance(trace.counterexample_evidence_refs, tuple)

    def test_memory_trace_preview_actual_memory_learning_trace_created_false(self) -> None:
        trace = build_demo_reviewed_concept_memory_trace_preview()
        self.assertFalse(trace.actual_memory_learning_trace_created)

    def test_routing_preview_builds_from_valid_trace_preview(self) -> None:
        routing = build_demo_reviewed_concept_memory_routing_preview()
        validation = validate_reviewed_concept_memory_routing_preview(routing)
        self.assertTrue(validation["valid"], validation["error_codes"])

    def test_routing_preview_default_target_layer_working_readback_candidate(self) -> None:
        routing = build_demo_reviewed_concept_memory_routing_preview()
        self.assertEqual(routing.target_layer_preview, "working_readback_candidate")

    def test_routing_preview_blocks_core_target(self) -> None:
        self._assert_forbidden_target("core_memory")

    def test_routing_preview_blocks_long_term_target(self) -> None:
        self._assert_forbidden_target("long_term_memory")

    def test_routing_preview_blocks_archive_target(self) -> None:
        self._assert_forbidden_target("archive_memory")

    def test_routing_preview_blocks_anchor_target(self) -> None:
        self._assert_forbidden_target("anchor_layer")

    def test_routing_preview_actual_memory_routing_trace_created_false(self) -> None:
        routing = build_demo_reviewed_concept_memory_routing_preview()
        self.assertFalse(routing.actual_memory_routing_trace_created)

    def test_routing_preview_memory_write_performed_false(self) -> None:
        routing = build_demo_reviewed_concept_memory_routing_preview()
        self.assertFalse(routing.memory_write_performed)

    def test_routing_preview_requires_more_support_before_promotion_true(self) -> None:
        routing = build_demo_reviewed_concept_memory_routing_preview()
        self.assertTrue(routing.requires_more_support_before_promotion)

    def test_routing_preview_requires_counterexample_monitoring_true(self) -> None:
        routing = build_demo_reviewed_concept_memory_routing_preview()
        self.assertTrue(routing.requires_counterexample_monitoring)

    def test_application_data_preview_builds_from_valid_routing_preview(self) -> None:
        application = build_demo_reviewed_concept_memory_application_data_preview()
        validation = validate_reviewed_concept_memory_application_data_preview(
            application
        )
        self.assertTrue(validation["valid"], validation["error_codes"])

    def test_application_data_preview_preview_only_true(self) -> None:
        self.assertTrue(build_demo_reviewed_concept_memory_application_data_preview().preview_only)

    def test_application_data_preview_actual_memory_application_data_created_false(self) -> None:
        application = build_demo_reviewed_concept_memory_application_data_preview()
        self.assertFalse(application.actual_memory_application_data_created)

    def test_application_data_preview_readback_hint_created_false(self) -> None:
        application = build_demo_reviewed_concept_memory_application_data_preview()
        self.assertFalse(application.readback_hint_created)

    def test_application_data_preview_working_memory_mutated_false(self) -> None:
        application = build_demo_reviewed_concept_memory_application_data_preview()
        self.assertFalse(application.working_memory_mutated)

    def test_application_data_preview_task_behavior_changed_false(self) -> None:
        application = build_demo_reviewed_concept_memory_application_data_preview()
        self.assertFalse(application.task_behavior_changed)

    def test_application_data_preview_creates_hint_labels_for_front_blocked_affordance(self) -> None:
        payload = build_demo_reviewed_concept_record()
        reviewed_data = dict(payload["reviewed_concept"])
        reviewed_data["concept_label"] = "front_blocked_affordance"
        reviewed = ReviewedConceptRecord.from_dict(reviewed_data)
        trace = build_reviewed_concept_memory_trace_preview(
            reviewed_concept=reviewed,
            lineage_record=payload["lineage_record"],
            reviewed_concept_safety_audit=payload["safety_audit"],
        )
        routing = build_reviewed_concept_memory_routing_preview(
            memory_trace_preview=trace
        )
        application = build_reviewed_concept_memory_application_data_preview(
            reviewed_concept=reviewed,
            memory_trace_preview=trace,
            routing_preview=routing,
        )
        self.assertIn(
            "observe_before_direct_retry",
            application.suggested_working_memory_hint_labels,
        )
        self.assertIn(
            "avoid_same_failed_direct_retry",
            application.suggested_working_memory_hint_labels,
        )

    def test_safety_audit_passes_for_valid_preview_chain(self) -> None:
        audit = self._valid_preview_safety_audit()
        validation = validate_reviewed_concept_memory_preview_safety_audit(audit)
        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(audit.audit_status, "passed")

    def test_safety_audit_blocks_actual_memory_trace_flag_true(self) -> None:
        audit = self._audit_with_trace_flag("actual_memory_learning_trace_created", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_memory_write_detected",
        )

    def test_safety_audit_blocks_actual_routing_trace_flag_true(self) -> None:
        audit = self._audit_with_routing_flag("actual_memory_routing_trace_created", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_memory_write_detected",
        )

    def test_safety_audit_blocks_actual_application_data_flag_true(self) -> None:
        audit = self._audit_with_application_flag(
            "actual_memory_application_data_created",
            True,
        )
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_memory_write_detected",
        )

    def test_safety_audit_blocks_readback_hint_flag_true(self) -> None:
        audit = self._audit_with_application_flag("readback_hint_created", True)
        self.assertEqual(audit.audit_status, "blocked_forbidden_readback_detected")

    def test_safety_audit_blocks_working_memory_mutation_flag_true(self) -> None:
        audit = self._audit_with_application_flag("working_memory_mutated", True)
        self.assertEqual(audit.audit_status, "blocked_forbidden_readback_detected")

    def test_safety_audit_blocks_task_behavior_change_flag_true(self) -> None:
        audit = self._audit_with_application_flag("task_behavior_changed", True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_behavior_change_detected",
        )

    def test_unhandled_counterexample_blocks_routing(self) -> None:
        routing = build_demo_blocked_unhandled_counterexample_routing_preview()
        self.assertEqual(routing.target_layer_preview, "blocked_from_routing")
        self.assertEqual(routing.routing_status, "preview_blocked_from_routing")

    def test_overbroad_scope_held_for_more_evidence(self) -> None:
        routing = build_demo_held_for_more_evidence_overbroad_scope_preview()
        self.assertEqual(routing.target_layer_preview, "held_for_more_evidence")
        self.assertEqual(routing.routing_status, "preview_held_for_more_evidence")

    def test_forbidden_target_layer_blocks(self) -> None:
        routing = build_demo_blocked_forbidden_target_layer_preview()
        self.assertEqual(routing.routing_status, "blocked_forbidden_target_layer")

    def test_cli_preview_demo_memory_trace_works(self) -> None:
        result = self._run_learning_cli("preview-demo-memory-trace")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("memory_trace_preview", result.stdout)

    def test_cli_preview_demo_routing_works(self) -> None:
        result = self._run_learning_cli("preview-demo-routing")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("working_readback_candidate", result.stdout)

    def test_cli_preview_demo_application_data_works(self) -> None:
        result = self._run_learning_cli("preview-demo-application-data")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("actual_memory_application_data_created", result.stdout)

    def test_cli_preview_demo_full_works(self) -> None:
        result = self._run_learning_cli("preview-demo-full")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("preview_safety_audit", result.stdout)

    def test_cli_validate_demo_preview_works(self) -> None:
        result = self._run_learning_cli("validate-demo-preview")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"valid": true', result.stdout)

    def test_cli_blocked_unhandled_counterexample_works(self) -> None:
        result = self._run_learning_cli(
            "preview-demo-blocked",
            "--case",
            "unhandled-counterexample",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("preview_blocked_from_routing", result.stdout)

    def test_cli_blocked_forbidden_target_layer_works(self) -> None:
        result = self._run_learning_cli(
            "preview-demo-blocked",
            "--case",
            "forbidden-target-layer",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("blocked_forbidden_target_layer", result.stdout)

    def test_cli_held_overbroad_scope_works(self) -> None:
        result = self._run_learning_cli(
            "preview-demo-held",
            "--case",
            "overbroad-scope",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("preview_held_for_more_evidence", result.stdout)

    def test_guided_console_memory_preview_demo_commands_work(self) -> None:
        for command in (
            "learning-preview-reviewed-concept-memory-trace",
            "learning-preview-reviewed-concept-routing",
            "learning-preview-reviewed-concept-application-data",
            "learning-validate-reviewed-concept-memory-preview",
        ):
            result = self._run_guided_cli(command)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("guided_console_action", result.stdout)

    def test_no_repo_data_created(self) -> None:
        build_demo_reviewed_concept_memory_preview_bundle()
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _assert_forbidden_target(self, target_layer: str) -> None:
        routing = build_reviewed_concept_memory_routing_preview(
            memory_trace_preview=build_demo_reviewed_concept_memory_trace_preview(),
            requested_target_layer_preview=target_layer,
        )
        self.assertEqual(routing.target_layer_preview, "blocked_from_routing")
        self.assertEqual(routing.routing_status, "blocked_forbidden_target_layer")

    def _trace_from_payload(self, payload: dict[str, object]) -> ReviewedConceptMemoryTracePreview:
        return build_reviewed_concept_memory_trace_preview(
            reviewed_concept=payload["reviewed_concept"],
            lineage_record=payload["lineage_record"],
            reviewed_concept_safety_audit=payload["safety_audit"],
        )

    def _valid_preview_payload(self) -> dict[str, object]:
        return build_demo_reviewed_concept_memory_preview_bundle()

    def _valid_preview_safety_audit(self) -> ReviewedConceptMemoryPreviewSafetyAudit:
        return ReviewedConceptMemoryPreviewSafetyAudit.from_dict(
            self._valid_preview_payload()["preview_safety_audit"]
        )

    def _audit_with_trace_flag(
        self,
        flag_name: str,
        flag_value: bool,
    ) -> ReviewedConceptMemoryPreviewSafetyAudit:
        payload = self._valid_preview_payload()
        trace_data = dict(payload["memory_trace_preview"])
        trace_data[flag_name] = flag_value
        trace = ReviewedConceptMemoryTracePreview.from_dict(trace_data)
        return build_reviewed_concept_memory_preview_safety_audit(
            reviewed_concept=build_demo_reviewed_concept_record()["reviewed_concept"],
            memory_trace_preview=trace,
            routing_preview=payload["routing_preview"],
            application_data_preview=payload["application_data_preview"],
        )

    def _audit_with_routing_flag(
        self,
        flag_name: str,
        flag_value: bool,
    ) -> ReviewedConceptMemoryPreviewSafetyAudit:
        payload = self._valid_preview_payload()
        routing_data = dict(payload["routing_preview"])
        routing_data[flag_name] = flag_value
        routing = ReviewedConceptMemoryRoutingPreview.from_dict(routing_data)
        return build_reviewed_concept_memory_preview_safety_audit(
            reviewed_concept=build_demo_reviewed_concept_record()["reviewed_concept"],
            memory_trace_preview=payload["memory_trace_preview"],
            routing_preview=routing,
            application_data_preview=payload["application_data_preview"],
        )

    def _audit_with_application_flag(
        self,
        flag_name: str,
        flag_value: bool,
    ) -> ReviewedConceptMemoryPreviewSafetyAudit:
        payload = self._valid_preview_payload()
        application_data = dict(payload["application_data_preview"])
        application_data[flag_name] = flag_value
        application = ReviewedConceptMemoryApplicationDataPreview.from_dict(
            application_data
        )
        return build_reviewed_concept_memory_preview_safety_audit(
            reviewed_concept=build_demo_reviewed_concept_record()["reviewed_concept"],
            memory_trace_preview=payload["memory_trace_preview"],
            routing_preview=payload["routing_preview"],
            application_data_preview=application,
        )

    def _run_learning_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "ashl_core_v1.learning.reviewed_concept_to_memory_trace_preview_cli",
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
