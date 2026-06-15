import unittest

from ashl_core.codex_task_queue_minimal import (
    ALLOWED_STATUSES,
    ALLOWED_TASK_TYPES,
    BOUNDARY_PRINCIPLE,
    build_codex_task_queue_minimal,
    run_codex_task_queue_minimal_check,
    validate_codex_task_entry_minimal,
    validate_codex_task_queue_minimal,
)
from ashl_core.teaching_cli import run_command


class CodexTaskQueueMinimalTests(unittest.TestCase):
    def setUp(self):
        self.queue = build_codex_task_queue_minimal()

    def test_valid_queue_passes(self):
        result = validate_codex_task_queue_minimal(self.queue)

        self.assertTrue(result["valid"])
        self.assertEqual([], result["error_codes"])

    def test_valid_entries_pass(self):
        known_ids = {task["task_id"] for task in self.queue["task_entries"]}

        for task in self.queue["task_entries"]:
            with self.subTest(task_id=task["task_id"]):
                self.assertTrue(validate_codex_task_entry_minimal(task, known_ids)["valid"])

    def test_all_statuses_accepted(self):
        known_ids = {"task.test"}
        for status in ALLOWED_STATUSES:
            task = self._task(status=status)
            with self.subTest(status=status):
                self.assertTrue(validate_codex_task_entry_minimal(task, known_ids)["valid"])

    def test_all_task_types_accepted(self):
        known_ids = {"task.test"}
        for task_type in ALLOWED_TASK_TYPES:
            task = self._task(task_type=task_type)
            with self.subTest(task_type=task_type):
                self.assertTrue(validate_codex_task_entry_minimal(task, known_ids)["valid"])

    def test_unknown_status_rejected(self):
        task = self._task(status="done")

        self.assertIn("unknown_task_status", validate_codex_task_entry_minimal(task, {"task.test"})["error_codes"])

    def test_unknown_task_type_rejected(self):
        task = self._task(task_type="planner")

        self.assertIn("unknown_task_type", validate_codex_task_entry_minimal(task, {"task.test"})["error_codes"])

    def test_duplicate_task_id_rejected(self):
        queue = build_codex_task_queue_minimal()
        queue["task_entries"][1]["task_id"] = queue["task_entries"][0]["task_id"]

        errors = validate_codex_task_queue_minimal(queue)["error_codes"]

        self.assertTrue(any(error.startswith("duplicate_task_id:") for error in errors))

    def test_queue_cannot_count_as_approval(self):
        self.assert_queue_false_field_blocks("queue_counts_as_approval")

    def test_entry_cannot_count_as_approval(self):
        self.assert_entry_false_field_blocks("counts_as_approval")

    def test_queue_cannot_count_as_runtime_behavior(self):
        self.assert_queue_false_field_blocks("queue_counts_as_runtime_behavior")

    def test_queue_cannot_count_as_memory_write(self):
        self.assert_queue_false_field_blocks("queue_counts_as_memory_write")

    def test_queue_cannot_count_as_retained_jsonl_write(self):
        self.assert_queue_false_field_blocks("queue_counts_as_retained_jsonl_write")

    def test_queue_cannot_count_as_predictor_mutation(self):
        self.assert_queue_false_field_blocks("queue_counts_as_predictor_mutation")

    def test_queue_cannot_count_as_selected_action(self):
        self.assert_queue_false_field_blocks("queue_counts_as_selected_action")

    def test_queue_cannot_count_as_final_action(self):
        self.assert_queue_false_field_blocks("queue_counts_as_final_action")

    def test_queue_cannot_count_as_proof_of_learning(self):
        self.assert_queue_false_field_blocks("queue_counts_as_proof_of_learning")

    def test_unknown_dependency_rejected(self):
        queue = build_codex_task_queue_minimal()
        queue["task_entries"][1]["depends_on"] = ["task.unknown"]

        errors = validate_codex_task_queue_minimal(queue)["error_codes"]

        self.assertTrue(any("unknown_dependency:task.unknown" in error for error in errors))

    def test_blocked_task_requires_blocker_reason(self):
        task = self._task(status="blocked")
        task.pop("blocker_reason")

        self.assertIn(
            "blocked_task_missing_blocker_reason",
            validate_codex_task_entry_minimal(task, {"task.test"})["error_codes"],
        )

    def test_deferred_task_requires_deferral_reason(self):
        task = self._task(status="deferred")
        task.pop("deferral_reason")

        self.assertIn(
            "deferred_task_missing_deferral_reason",
            validate_codex_task_entry_minimal(task, {"task.test"})["error_codes"],
        )

    def test_superseded_task_requires_superseded_by_or_note(self):
        task = self._task(status="superseded", notes="")

        self.assertIn(
            "superseded_task_missing_superseded_by_or_note",
            validate_codex_task_entry_minimal(task, {"task.test"})["error_codes"],
        )

    def test_boundary_principle_is_present(self):
        self.assertIn(BOUNDARY_PRINCIPLE, self.queue["principles"])

    def test_cli_returns_status_ok(self):
        result = run_command("run-codex-task-queue-minimal-check")

        self.assertEqual("ok", result["status"])
        self.assertEqual(1, result["summary"]["valid_task_queue_count"])

    def test_demo_summary_counts_are_deterministic(self):
        summary = run_codex_task_queue_minimal_check()["summary"]

        self.assertEqual(22, summary["task_queue_result_count"])
        self.assertEqual(1, summary["valid_task_queue_count"])
        self.assertEqual(21, summary["invalid_task_queue_count"])
        self.assertEqual(43, summary["valid_task_entry_count"])
        self.assertGreaterEqual(summary["invalid_task_entry_count"], 9)
        self.assertEqual(1, summary["queue_scope_checked_count"])
        self.assertEqual(1, summary["approval_block_checked_count"])
        self.assertEqual(1, summary["runtime_block_checked_count"])
        self.assertEqual(1, summary["memory_block_checked_count"])
        self.assertEqual(1, summary["predictor_block_checked_count"])
        self.assertEqual(1, summary["proof_of_learning_block_checked_count"])

    def assert_queue_false_field_blocks(self, field):
        queue = build_codex_task_queue_minimal()
        queue[field] = True

        self.assertIn(f"{field}_not_false", validate_codex_task_queue_minimal(queue)["error_codes"])

    def assert_entry_false_field_blocks(self, field):
        task = self._task()
        task[field] = True

        self.assertIn(f"{field}_not_false", validate_codex_task_entry_minimal(task, {"task.test"})["error_codes"])

    def test_package_id_is_required(self):
        task = self._task()
        task["package_id"] = ""

        self.assertIn("package_id_missing", validate_codex_task_entry_minimal(task, {"task.test"})["error_codes"])

    def test_boundary_change_required_false_blocks_version_change(self):
        task = self._task()
        task["boundary_index_version_after"] = "2026-06-09-b99"

        self.assertIn(
            "boundary_index_changed_without_boundary_change_required",
            validate_codex_task_entry_minimal(task, {"task.test"})["error_codes"],
        )

    def test_boundary_increment_requires_explicit_rationale(self):
        task = self._task()
        task["boundary_change_required"] = True
        task["boundary_index_version_after"] = "2026-06-09-b99"
        task["boundary_change_rationale"] = ""

        self.assertIn(
            "boundary_index_changed_without_rationale",
            validate_codex_task_entry_minimal(task, {"task.test"})["error_codes"],
        )

    def test_task_completion_is_not_boundary_change_rationale(self):
        task = self._task(status="completed")
        task["boundary_change_required"] = True
        task["boundary_index_version_after"] = "2026-06-09-b99"
        task["boundary_change_rationale"] = "Completed task increments version."

        self.assertIn(
            "task_completion_treated_as_boundary_change",
            validate_codex_task_entry_minimal(task, {"task.test"})["error_codes"],
        )

    def _task(self, status="pending", task_type="workflow_only", notes="Test task."):
        task = {
            "task_id": "task.test",
            "package_id": "PKG-Test-001",
            "package_title": "Test task",
            "title": "Test task",
            "task_status": status,
            "task_type": task_type,
            "status": status,
            "boundary_index_version": "2026-06-09-b94",
            "boundary_change_required": False,
            "boundary_index_version_before": "2026-06-09-b94",
            "boundary_index_version_after": "2026-06-09-b94",
            "boundary_change_rationale": "",
            "source": "unit_test",
            "creates_capability": False,
            "counts_as_approval": False,
            "counts_as_runtime_behavior": False,
            "counts_as_memory_write": False,
            "counts_as_retained_jsonl_write": False,
            "counts_as_predictor_mutation": False,
            "counts_as_selected_action": False,
            "counts_as_final_action": False,
            "counts_as_proof_of_learning": False,
            "depends_on": [],
            "blocks": [],
            "notes": notes,
        }
        if status == "blocked" and notes == "Test task.":
            task["notes"] = "Blocked negative case."
        if status == "deferred" and notes == "Test task.":
            task["notes"] = "Deferred negative case."
        if status == "blocked":
            task["blocker_reason"] = "Blocked for unit test."
        if status == "deferred":
            task["deferral_reason"] = "Deferred for unit test."
        if status == "superseded" and notes:
            task["superseded_by"] = "task.replacement"
        return task


if __name__ == "__main__":
    unittest.main()
