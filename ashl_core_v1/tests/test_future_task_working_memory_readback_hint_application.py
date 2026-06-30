from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from ashl_core_v1.task.future_task_working_memory_readback_hint_application import (
    FutureTaskWorkingMemoryInitializationReadbackSnapshot,
    FutureTaskWorkingMemoryReadbackHintApplicationRecord,
    FutureTaskWorkingMemoryReadbackHintApplicationSafetyAudit,
    FutureTaskWorkingMemoryReadbackHintApplicationSet,
    build_demo_all_held_future_task_working_memory_readback_hint_application_set,
    build_demo_blocked_forbidden_authority_application_set,
    build_demo_blocked_non_advisory_hint_application_set,
    build_demo_blocked_running_task_mutation_application_set,
    build_demo_future_task_working_memory_readback_hint_application_set,
    build_future_task_working_memory_initialization_readback_snapshot,
    build_future_task_working_memory_readback_hint_application_bundle,
    build_future_task_working_memory_readback_hint_application_record,
    build_future_task_working_memory_readback_hint_application_safety_audit,
    initialize_future_task_working_memory_with_advisory_readback_hints,
    validate_future_task_working_memory_initialization_readback_snapshot,
    validate_future_task_working_memory_readback_hint_application_record,
    validate_future_task_working_memory_readback_hint_application_safety_audit,
    validate_future_task_working_memory_readback_hint_application_set,
)
from ashl_core_v1.task.reviewed_concept_readback_hint_application_preparation import (
    TaskWorkingMemoryReadbackHintApplicationPreparationRecord,
    TaskWorkingMemoryReadbackHintApplicationPreparationSafetyAudit,
    TaskWorkingMemoryReadbackHintApplicationPreparationSet,
    build_demo_rejected_task_working_memory_readback_hint_application_preparation_set,
    build_demo_task_working_memory_readback_hint_application_preparation_set,
)


READY_PREPARATION = "prepared_for_future_working_memory_initialization_application"
APPLIED_STATUS = "applied_to_new_task_working_memory_initialization"
TASK_CLI = "ashl_core_v1.task.future_task_working_memory_readback_hint_application_cli"
GUIDED_CLI = "ashl_core_v1.runtime.guided_cradle_growth_teacher_console_cli"


class FutureTaskWorkingMemoryReadbackHintApplicationTests(unittest.TestCase):
    def test_application_record_builds_from_prepared_application_preparation(self) -> None:
        record = self._first_applied_record()
        validation = validate_future_task_working_memory_readback_hint_application_record(
            record
        )
        self.assertTrue(validation["valid"])

    def test_application_record_preserves_reviewed_concept_id(self) -> None:
        prep = self._first_ready_preparation()
        record = self._application_record_from_preparation(prep)
        self.assertEqual(record.source_reviewed_concept_id, prep.source_reviewed_concept_id)

    def test_application_record_preserves_preparation_id(self) -> None:
        prep = self._first_ready_preparation()
        record = self._application_record_from_preparation(prep)
        self.assertEqual(
            record.source_hint_application_preparation_id,
            prep.hint_application_preparation_id,
        )

    def test_application_record_preserves_hint_record_id(self) -> None:
        prep = self._first_ready_preparation()
        record = self._application_record_from_preparation(prep)
        self.assertEqual(
            record.source_task_working_memory_readback_hint_id,
            prep.source_task_working_memory_readback_hint_id,
        )

    def test_application_record_preserves_hint_label(self) -> None:
        prep = self._first_ready_preparation()
        record = self._application_record_from_preparation(prep)
        self.assertEqual(record.hint_label, prep.hint_label)

    def test_application_record_preserves_hint_kind(self) -> None:
        prep = self._first_ready_preparation()
        record = self._application_record_from_preparation(prep)
        self.assertEqual(record.hint_kind, prep.hint_kind)

    def test_application_record_preserves_hint_priority(self) -> None:
        prep = self._first_ready_preparation()
        record = self._application_record_from_preparation(prep)
        self.assertEqual(record.hint_priority, prep.hint_priority)

    def test_application_record_preserves_hint_summary(self) -> None:
        prep = self._first_ready_preparation()
        record = self._application_record_from_preparation(prep)
        self.assertEqual(record.hint_summary, prep.hint_summary)

    def test_application_record_preserves_task_handling_note(self) -> None:
        prep = self._first_ready_preparation()
        record = self._application_record_from_preparation(prep)
        self.assertEqual(record.task_handling_note, prep.prepared_task_handling_note)

    def test_application_record_preserves_scope_warning(self) -> None:
        prep = self._first_ready_preparation()
        record = self._application_record_from_preparation(prep)
        self.assertEqual(record.scope_warning, prep.prepared_scope_warning)

    def test_application_record_preserves_counterexample_warning(self) -> None:
        prep = self._first_ready_preparation()
        record = self._application_record_from_preparation(prep)
        self.assertEqual(
            record.counterexample_warning,
            prep.prepared_counterexample_warning,
        )

    def test_prepared_application_creates_applied_status(self) -> None:
        self.assertEqual(self._first_applied_record().application_status, APPLIED_STATUS)

    def test_held_application_creates_held_for_more_evidence(self) -> None:
        held = next(
            record
            for record in self._valid_application_set().application_records
            if record.application_status == "held_for_more_evidence"
        )
        self.assertEqual(held.application_status, "held_for_more_evidence")
        self.assertFalse(held.working_memory_mutated)

    def test_blocked_application_creates_blocked_invalid_preparation(self) -> None:
        payload = build_future_task_working_memory_readback_hint_application_bundle(
            build_demo_rejected_task_working_memory_readback_hint_application_preparation_set()
        )
        app_set = FutureTaskWorkingMemoryReadbackHintApplicationSet.from_dict(
            payload["future_task_readback_hint_application_set"]
        )
        self.assertEqual(
            app_set.application_records[0].application_status,
            "blocked_invalid_preparation",
        )

    def test_application_record_applied_slot_readback_hints(self) -> None:
        self.assertEqual(
            self._first_applied_record().applied_working_memory_slot,
            "readback_hints",
        )

    def test_application_record_scope_future_task_initialization(self) -> None:
        self.assertEqual(
            self._first_applied_record().application_scope,
            "future_task_initialization",
        )

    def test_application_record_visibility_advisory_only(self) -> None:
        self.assertEqual(self._first_applied_record().visibility, "advisory_only")

    def test_application_record_lifetime_single_task(self) -> None:
        self.assertEqual(self._first_applied_record().lifetime, "single_task")

    def test_application_record_applied_flag_true_only_when_ready(self) -> None:
        app_set = self._valid_application_set()
        for record in app_set.application_records:
            self.assertEqual(
                record.applied_to_new_task_working_memory_initialization,
                record.application_status == APPLIED_STATUS,
            )

    def test_application_record_applied_to_running_task_false(self) -> None:
        self.assertFalse(self._first_applied_record().applied_to_running_task)

    def test_application_record_working_memory_mutated_true_only_for_application(self) -> None:
        app_set = self._valid_application_set()
        for record in app_set.application_records:
            self.assertEqual(
                record.working_memory_mutated,
                record.application_status == APPLIED_STATUS,
            )

    def test_application_record_keeps_forbidden_authority_false(self) -> None:
        record = self._first_applied_record()
        for flag in (
            "candidate_ordering_changed",
            "task_behavior_changed",
            "selected_action_changed",
            "final_action_changed",
            "direct_command_changed",
            "execution_created",
            "memory_layer_write_performed",
        ):
            self.assertFalse(getattr(record, flag), flag)

    def test_application_set_builds_from_preparation_set(self) -> None:
        validation = validate_future_task_working_memory_readback_hint_application_set(
            self._valid_application_set()
        )
        self.assertTrue(validation["valid"])

    def test_application_set_counts_applied_records_correctly(self) -> None:
        self.assertEqual(self._valid_application_set().applied_count, 2)

    def test_application_set_counts_held_records_correctly(self) -> None:
        self.assertEqual(self._valid_application_set().held_count, 1)

    def test_application_set_counts_blocked_records_correctly(self) -> None:
        payload = build_future_task_working_memory_readback_hint_application_bundle(
            build_demo_rejected_task_working_memory_readback_hint_application_preparation_set()
        )
        app_set = FutureTaskWorkingMemoryReadbackHintApplicationSet.from_dict(
            payload["future_task_readback_hint_application_set"]
        )
        self.assertEqual(app_set.blocked_count, 3)

    def test_application_set_status_created_with_advisory_hints_when_applied(self) -> None:
        self.assertEqual(
            self._valid_application_set().application_set_status,
            "application_set_created_with_advisory_hints",
        )

    def test_application_set_status_all_held_or_blocked_when_none_applied(self) -> None:
        payload = build_demo_all_held_future_task_working_memory_readback_hint_application_set()
        app_set = FutureTaskWorkingMemoryReadbackHintApplicationSet.from_dict(
            payload["future_task_readback_hint_application_set"]
        )
        self.assertEqual(
            app_set.application_set_status,
            "application_set_created_all_held_or_blocked",
        )

    def test_readback_snapshot_builds_from_application_set(self) -> None:
        snapshot = self._valid_snapshot()
        validation = validate_future_task_working_memory_initialization_readback_snapshot(
            snapshot
        )
        self.assertTrue(validation["valid"])

    def test_readback_snapshot_contains_applied_hint_labels(self) -> None:
        snapshot = self._valid_snapshot()
        self.assertIn("observe_before_direct_retry", snapshot.readback_hint_labels)
        self.assertIn("avoid_same_failed_direct_retry", snapshot.readback_hint_labels)

    def test_readback_snapshot_hint_count_matches_applied_count(self) -> None:
        self.assertEqual(self._valid_snapshot().hint_count, self._valid_application_set().applied_count)

    def test_readback_snapshot_authority_flags_are_safe(self) -> None:
        snapshot = self._valid_snapshot()
        self.assertTrue(snapshot.advisory_only)
        self.assertTrue(snapshot.single_task_lifetime)
        self.assertTrue(snapshot.future_task_initialization_only)
        self.assertFalse(snapshot.candidate_ordering_changed)
        self.assertFalse(snapshot.task_behavior_changed)
        self.assertFalse(snapshot.selected_action_changed)
        self.assertFalse(snapshot.final_action_changed)
        self.assertFalse(snapshot.direct_command_changed)
        self.assertFalse(snapshot.execution_created)

    def test_wrapper_initializes_new_task_working_memory_with_readback_hints_only(self) -> None:
        initialized = initialize_future_task_working_memory_with_advisory_readback_hints(
            application_set=self._valid_application_set(),
            readback_snapshot=self._valid_snapshot(),
        )
        self.assertTrue(initialized["future_task_working_memory_created"])
        memory = initialized["task_working_memory"]
        self.assertTrue(memory["readback_hints"])
        self.assertEqual(memory["working_memory_mutation_scope"], "readback_hints_only")
        self.assertEqual(memory["candidate_ordering"], [])
        self.assertIsNone(memory["selected_action"])
        self.assertIsNone(memory["final_action"])
        self.assertIsNone(memory["direct_command"])
        self.assertIsNone(memory["execution"])

    def test_wrapper_rejects_running_task_mutation(self) -> None:
        initialized = initialize_future_task_working_memory_with_advisory_readback_hints(
            application_set=self._valid_application_set(),
            readback_snapshot=self._valid_snapshot(),
            target_task_is_running=True,
        )
        self.assertFalse(initialized["future_task_working_memory_created"])
        self.assertEqual(
            initialized["initialization_status"],
            "blocked_running_task_mutation_attempt",
        )

    def test_safety_audit_passes_for_valid_demo_application(self) -> None:
        validation = validate_future_task_working_memory_readback_hint_application_safety_audit(
            self._valid_safety_audit()
        )
        self.assertTrue(validation["valid"])

    def test_safety_audit_blocks_running_task_mutation(self) -> None:
        payload = build_demo_blocked_running_task_mutation_application_set()
        audit = FutureTaskWorkingMemoryReadbackHintApplicationSafetyAudit.from_dict(
            payload["future_task_working_memory_readback_hint_application_safety_audit"]
        )
        self.assertEqual(
            audit.audit_status,
            "blocked_running_task_mutation_detected",
        )

    def test_safety_audit_blocks_non_advisory_hint(self) -> None:
        payload = build_demo_blocked_non_advisory_hint_application_set()
        audit = FutureTaskWorkingMemoryReadbackHintApplicationSafetyAudit.from_dict(
            payload["future_task_working_memory_readback_hint_application_safety_audit"]
        )
        self.assertEqual(audit.audit_status, "blocked_non_advisory_hint_detected")

    def test_safety_audit_blocks_persistent_hint_lifetime(self) -> None:
        audit = self._audit_with_mutated_applied_record(lifetime="persistent")
        self.assertEqual(
            audit.audit_status,
            "blocked_persistent_hint_lifetime_detected",
        )

    def test_safety_audit_blocks_forbidden_candidate_ordering_change(self) -> None:
        audit = self._audit_with_mutated_applied_record(
            candidate_ordering_changed=True
        )
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_ordering_change_detected",
        )

    def test_safety_audit_blocks_forbidden_task_behavior_change(self) -> None:
        audit = self._audit_with_mutated_applied_record(task_behavior_changed=True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_behavior_change_detected",
        )

    def test_safety_audit_blocks_forbidden_selected_action_change(self) -> None:
        audit = self._audit_with_mutated_applied_record(selected_action_changed=True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_action_authority_detected",
        )

    def test_safety_audit_blocks_forbidden_final_action_change(self) -> None:
        audit = self._audit_with_mutated_applied_record(final_action_changed=True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_action_authority_detected",
        )

    def test_safety_audit_blocks_forbidden_direct_command_change(self) -> None:
        audit = self._audit_with_mutated_applied_record(direct_command_changed=True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_action_authority_detected",
        )

    def test_safety_audit_blocks_forbidden_execution(self) -> None:
        audit = self._audit_with_mutated_applied_record(execution_created=True)
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_action_authority_detected",
        )

    def test_safety_audit_blocks_forbidden_memory_layer_write(self) -> None:
        audit = self._audit_with_mutated_applied_record(
            memory_layer_write_performed=True
        )
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_memory_write_detected",
        )

    def test_forbidden_authority_demo_blocks(self) -> None:
        payload = build_demo_blocked_forbidden_authority_application_set()
        audit = FutureTaskWorkingMemoryReadbackHintApplicationSafetyAudit.from_dict(
            payload["future_task_working_memory_readback_hint_application_safety_audit"]
        )
        self.assertEqual(
            audit.audit_status,
            "blocked_forbidden_ordering_change_detected",
        )

    def test_cli_apply_demo_readback_hints_works(self) -> None:
        payload = self._run_task_cli("apply-demo-readback-hints")
        self.assertEqual(
            payload["future_task_readback_hint_application_set"][
                "application_set_status"
            ],
            "application_set_created_with_advisory_hints",
        )

    def test_cli_show_demo_application_works(self) -> None:
        payload = self._run_task_cli("show-demo-application")
        self.assertEqual(
            payload["application_set_status"],
            "application_set_created_with_advisory_hints",
        )

    def test_cli_show_demo_readback_snapshot_works(self) -> None:
        payload = self._run_task_cli("show-demo-readback-snapshot")
        self.assertEqual(
            payload["snapshot_status"],
            "snapshot_created_with_advisory_readback_hints",
        )

    def test_cli_show_demo_safety_audit_works(self) -> None:
        payload = self._run_task_cli("show-demo-safety-audit")
        self.assertEqual(payload["audit_status"], "passed")

    def test_cli_validate_demo_application_works(self) -> None:
        payload = self._run_task_cli("validate-demo-application")
        self.assertTrue(payload["valid"])

    def test_cli_all_held_works(self) -> None:
        payload = self._run_task_cli("apply-demo-held", "--case", "all-held")
        self.assertEqual(
            payload["future_task_readback_hint_application_set"][
                "application_set_status"
            ],
            "application_set_created_all_held_or_blocked",
        )

    def test_cli_running_task_mutation_blocked_works(self) -> None:
        payload = self._run_task_cli(
            "apply-demo-blocked",
            "--case",
            "running-task-mutation",
        )
        self.assertEqual(
            payload["future_task_working_memory_readback_hint_application_safety_audit"][
                "audit_status"
            ],
            "blocked_running_task_mutation_detected",
        )

    def test_cli_non_advisory_hint_blocked_works(self) -> None:
        payload = self._run_task_cli(
            "apply-demo-blocked",
            "--case",
            "non-advisory-hint",
        )
        self.assertEqual(
            payload["future_task_working_memory_readback_hint_application_safety_audit"][
                "audit_status"
            ],
            "blocked_non_advisory_hint_detected",
        )

    def test_cli_forbidden_authority_blocked_works(self) -> None:
        payload = self._run_task_cli(
            "apply-demo-blocked",
            "--case",
            "forbidden-authority",
        )
        self.assertEqual(
            payload["future_task_working_memory_readback_hint_application_safety_audit"][
                "audit_status"
            ],
            "blocked_forbidden_ordering_change_detected",
        )

    def test_guided_console_future_task_readback_hint_application_demo_works(self) -> None:
        payload = self._run_guided_cli(
            "task-apply-reviewed-concept-readback-hints-demo"
        )
        self.assertEqual(
            payload["future_task_readback_hint_application_set"][
                "application_set_status"
            ],
            "application_set_created_with_advisory_hints",
        )

    def test_guided_console_show_application_works(self) -> None:
        payload = self._run_guided_cli(
            "task-show-reviewed-concept-readback-hint-application"
        )
        self.assertIn("future_task_readback_hint_application_set", payload)

    def test_guided_console_show_snapshot_works(self) -> None:
        payload = self._run_guided_cli("task-show-reviewed-concept-readback-snapshot")
        self.assertIn(
            "future_task_working_memory_initialization_readback_snapshot",
            payload,
        )

    def test_guided_console_validate_application_works(self) -> None:
        payload = self._run_guided_cli(
            "task-validate-reviewed-concept-readback-hint-application"
        )
        self.assertTrue(payload["validation"]["valid"])

    def test_no_repo_data_created(self) -> None:
        self.assertFalse(Path("ashl_core_v1/data").exists())

    def _valid_application_set(self) -> FutureTaskWorkingMemoryReadbackHintApplicationSet:
        payload = build_demo_future_task_working_memory_readback_hint_application_set()
        return FutureTaskWorkingMemoryReadbackHintApplicationSet.from_dict(
            payload["future_task_readback_hint_application_set"]
        )

    def _valid_snapshot(self) -> FutureTaskWorkingMemoryInitializationReadbackSnapshot:
        payload = build_demo_future_task_working_memory_readback_hint_application_set()
        return FutureTaskWorkingMemoryInitializationReadbackSnapshot.from_dict(
            payload["future_task_working_memory_initialization_readback_snapshot"]
        )

    def _valid_safety_audit(self) -> FutureTaskWorkingMemoryReadbackHintApplicationSafetyAudit:
        payload = build_demo_future_task_working_memory_readback_hint_application_set()
        return FutureTaskWorkingMemoryReadbackHintApplicationSafetyAudit.from_dict(
            payload["future_task_working_memory_readback_hint_application_safety_audit"]
        )

    def _first_applied_record(self) -> FutureTaskWorkingMemoryReadbackHintApplicationRecord:
        return next(
            record
            for record in self._valid_application_set().application_records
            if record.application_status == APPLIED_STATUS
        )

    def _preparation_parts(
        self,
    ) -> tuple[
        TaskWorkingMemoryReadbackHintApplicationPreparationSet,
        TaskWorkingMemoryReadbackHintApplicationPreparationSafetyAudit,
    ]:
        payload = build_demo_task_working_memory_readback_hint_application_preparation_set()
        return (
            TaskWorkingMemoryReadbackHintApplicationPreparationSet.from_dict(
                payload["hint_application_preparation_set"]
            ),
            TaskWorkingMemoryReadbackHintApplicationPreparationSafetyAudit.from_dict(
                payload["hint_application_preparation_safety_audit"]
            ),
        )

    def _first_ready_preparation(
        self,
    ) -> TaskWorkingMemoryReadbackHintApplicationPreparationRecord:
        preparation_set, _ = self._preparation_parts()
        return next(
            record
            for record in preparation_set.application_preparation_records
            if record.preparation_status == READY_PREPARATION
        )

    def _application_record_from_preparation(
        self,
        preparation: TaskWorkingMemoryReadbackHintApplicationPreparationRecord,
    ) -> FutureTaskWorkingMemoryReadbackHintApplicationRecord:
        preparation_set, preparation_safety = self._preparation_parts()
        return build_future_task_working_memory_readback_hint_application_record(
            application_preparation_record=preparation,
            application_preparation_set=preparation_set,
            application_preparation_safety_audit=preparation_safety,
            target_task_working_memory_id="task_working_memory:test",
            target_task_initialization_id="task_initialization:test",
        )

    def _audit_with_mutated_applied_record(
        self,
        **changes: object,
    ) -> FutureTaskWorkingMemoryReadbackHintApplicationSafetyAudit:
        preparation_set, preparation_safety = self._preparation_parts()
        app_set = self._valid_application_set()
        records = list(app_set.application_records)
        index = next(
            idx for idx, record in enumerate(records) if record.application_status == APPLIED_STATUS
        )
        records[index] = FutureTaskWorkingMemoryReadbackHintApplicationRecord.from_dict(
            {**records[index].to_dict(), **changes}
        )
        app_set = FutureTaskWorkingMemoryReadbackHintApplicationSet.from_dict(
            {
                **app_set.to_dict(),
                "application_records": [record.to_dict() for record in records],
                **{
                    flag: value
                    for flag, value in changes.items()
                    if flag in {
                        "candidate_ordering_changed",
                        "task_behavior_changed",
                        "selected_action_changed",
                        "final_action_changed",
                        "direct_command_changed",
                        "execution_created",
                        "memory_layer_write_performed",
                    }
                },
            }
        )
        snapshot = build_future_task_working_memory_initialization_readback_snapshot(
            application_set=app_set
        )
        return build_future_task_working_memory_readback_hint_application_safety_audit(
            application_preparation_set=preparation_set,
            application_preparation_safety_audit=preparation_safety,
            application_set=app_set,
            readback_snapshot=snapshot,
        )

    def _run_task_cli(self, *args: str) -> dict:
        result = subprocess.run(
            [sys.executable, "-m", TASK_CLI, *args],
            check=True,
            capture_output=True,
            text=True,
        )
        import json

        return json.loads(result.stdout)

    def _run_guided_cli(self, *args: str) -> dict:
        result = subprocess.run(
            [sys.executable, "-m", GUIDED_CLI, *args],
            check=True,
            capture_output=True,
            text=True,
        )
        import json

        return json.loads(result.stdout)


if __name__ == "__main__":
    unittest.main()
