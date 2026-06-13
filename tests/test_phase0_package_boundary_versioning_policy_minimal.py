import unittest

from ashl_core.phase0_package_boundary_versioning_policy_minimal import (
    build_phase0_package_boundary_versioning_policy_record,
    run_phase0_package_boundary_versioning_policy_minimal_check,
    validate_phase0_package_boundary_task_versioning,
    validate_phase0_package_boundary_versioning_policy_record,
)
from ashl_core.teaching_cli import run_command


class Phase0PackageBoundaryVersioningPolicyMinimalTests(unittest.TestCase):
    def setUp(self):
        self.record = build_phase0_package_boundary_versioning_policy_record()

    def test_valid_policy_record(self):
        result = validate_phase0_package_boundary_versioning_policy_record(self.record)

        self.assertTrue(result["valid"])
        self.assertTrue(self.record["package_id_required"])
        self.assertTrue(self.record["boundary_index_is_not_package_counter"])

    def test_package_id_required(self):
        record = build_phase0_package_boundary_versioning_policy_record()
        record["package_id"] = ""

        self.assertIn("package_id_missing", self._policy_errors(record))

    def test_completed_task_does_not_auto_increment_boundary_index(self):
        record = build_phase0_package_boundary_versioning_policy_record()
        record["codex_task_completion_auto_increments_boundary_index"] = True

        self.assertIn("codex_task_completion_auto_increments_boundary_index_not_false", self._policy_errors(record))

    def test_boundary_increment_requires_explicit_rationale(self):
        task = self._task(after="2026-06-09-b99", boundary_change_required=True, rationale="")

        self.assertIn("boundary_index_changed_without_rationale", self._task_errors(task))

    def test_boundary_change_required_false_blocks_version_change(self):
        task = self._task(after="2026-06-09-b99")

        self.assertIn("boundary_index_changed_without_boundary_change_required", self._task_errors(task))

    def test_documentation_only_task_does_not_update_boundary_index(self):
        record = build_phase0_package_boundary_versioning_policy_record()
        record["documentation_update_counts_as_boundary_change"] = True

        self.assertIn("documentation_update_counts_as_boundary_change_not_false", self._policy_errors(record))

    def test_workflow_only_task_does_not_update_boundary_index_by_completion(self):
        task = self._task(
            after="2026-06-09-b99",
            boundary_change_required=True,
            rationale="Completed task increments version.",
        )

        self.assertIn("task_completion_treated_as_boundary_change", self._task_errors(task))

    def test_task_queue_completion_is_not_approval_and_not_boundary_change(self):
        record = build_phase0_package_boundary_versioning_policy_record()
        record["task_queue_status_update_counts_as_boundary_change"] = True

        self.assertIn("task_queue_status_update_counts_as_boundary_change_not_false", self._policy_errors(record))

    def test_no_runtime_memory_predictor_action_or_proof_flags_are_enabled(self):
        for field in (
            "runtime_behavior_changed",
            "memory_written",
            "retention_written",
            "predictor_mutated",
            "selected_action_created",
            "final_action_created",
            "production_promoted",
            "proof_of_learning_claimed",
        ):
            with self.subTest(field=field):
                record = build_phase0_package_boundary_versioning_policy_record()
                record[field] = True
                self.assertIn(f"{field}_not_false", self._policy_errors(record))

    def test_cli_path_returns_ok(self):
        result = run_command("run-phase0-package-boundary-versioning-policy-minimal-check")

        self.assertEqual("ok", result["status"])

    def test_demo_summary_counts_are_deterministic(self):
        summary = run_phase0_package_boundary_versioning_policy_minimal_check()["summary"]

        self.assertEqual(1, summary["valid_versioning_policy_count"])
        self.assertGreaterEqual(summary["invalid_versioning_policy_count"], 1)
        self.assertTrue(summary["package_id_required"])
        self.assertTrue(summary["boundary_index_is_not_package_counter"])
        self.assertTrue(summary["codex_completion_auto_increment_blocked"])
        self.assertTrue(summary["boundary_change_rationale_required"])

    def _policy_errors(self, record):
        return validate_phase0_package_boundary_versioning_policy_record(record)["error_codes"]

    def _task_errors(self, task):
        return validate_phase0_package_boundary_task_versioning(task)["error_codes"]

    def _task(
        self,
        package_id="PKG-Test-001",
        before="2026-06-09-b72",
        after="2026-06-09-b72",
        boundary_change_required=False,
        rationale="",
    ):
        return {
            "package_id": package_id,
            "boundary_index_version_before": before,
            "boundary_index_version_after": after,
            "boundary_change_required": boundary_change_required,
            "boundary_change_rationale": rationale,
        }


if __name__ == "__main__":
    unittest.main()
