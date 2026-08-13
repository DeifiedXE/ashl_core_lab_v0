from __future__ import annotations

import ast
import contextlib
import io
import json
import os
import sqlite3
import tempfile
import unittest
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

from ashl_core_v1.runtime.host_sensor_types import utc_now
from ashl_core_v1.runtime.local_operator_console_store import LocalOperatorConsoleStore
from ashl_core_v1.runtime.local_operator_event_stream import LocalOperatorEventStream
from ashl_core_v1.thought.package_141_instinct_audit import repository_source_tree_sha256
from ashl_core_v1.thought.package_143_coarse_workspace_runtime import (
    build_live_package_142_inputs,
    open_ephemeral_workspace,
)
from ashl_core_v1.thought.package_144_deep_thought_deliberation_audit import (
    audit_package_144_deep_thought_deliberation,
    run_package_144_boundary_controls,
)
from ashl_core_v1.thought.package_144_deep_thought_deliberation_cli import (
    main as package_144_cli,
)
from ashl_core_v1.thought.package_144_deep_thought_deliberation_runtime import (
    authorize_deliberation,
    build_deep_thought_counterfactual_equivalence,
    freeze_workspace_snapshot,
    load_package_143_deliberation_evidence,
    load_package_144_preflight,
    run_deep_thought_deliberation_suite,
    start_deliberation,
    validate_no_forbidden_deliberation_authority,
)
from ashl_core_v1.thought.package_144_deep_thought_deliberation_store import (
    Package144DeepThoughtDeliberationStore,
)
from ashl_core_v1.thought.deep_thought_deliberation_types import (
    BASELINE_COMMIT,
    CONTROL_NAMES,
    OPERATION_ALLOWLIST,
    PASS_STATUS,
    REGRESSION_SCHEMA_VERSION,
    Package144RegressionReceipt,
    build_hashed_record,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_143_STATE = Path(
    os.environ.get(
        "ASHL_PACKAGE_143_STATE_DIR",
        r"F:\ashl_external_state\package143_official_20260813_v2",
    )
)
PACKAGE_142_STATE = Path(
    os.environ.get(
        "ASHL_PACKAGE_142_STATE_DIR",
        r"F:\ashl_external_state\package142_official_20260813",
    )
)
PACKAGE_141_STATE = Path(
    os.environ.get(
        "ASHL_PACKAGE_141_STATE_DIR",
        r"F:\ashl_external_state\package141_official_20260811",
    )
)


def _official_available() -> bool:
    return all(
        (
            (
                PACKAGE_143_STATE
                / "package_143_coarse_thought_workspace_v0"
                / "package_143.sqlite3"
            ).is_file(),
            (
                PACKAGE_142_STATE
                / "package_142_specialized_thought_bounded_rules_v0"
                / "package_142.sqlite3"
            ).is_file(),
            (
                PACKAGE_141_STATE
                / "package_141_instinct_layer_runtime_v0"
                / "package_141.sqlite3"
            ).is_file(),
        )
    )


@unittest.skipUnless(_official_available(), "Package 141-143 official evidence unavailable")
class Package144DeepThoughtDeliberationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.preflight = load_package_144_preflight(
            ashl_root=REPO_ROOT,
            package_143_state_dir=PACKAGE_143_STATE,
            package_142_state_dir=PACKAGE_142_STATE,
            package_141_state_dir=PACKAGE_141_STATE,
        )

    def setUp(self) -> None:
        self.base = 60_000_000_000

    def _snapshot_context(self, offset: int = 0):
        base = self.base + offset
        live = build_live_package_142_inputs(
            self.preflight.package_143_runtime_preflight,
            base_monotonic_ns=base + 100,
        )
        workspace = open_ephemeral_workspace(
            self.preflight.package_143_runtime_preflight,
            opened_at_monotonic_ns=base,
            process_instance_id=f"package_144_test_process:{offset}",
            runtime_session_id=f"package_144_test_runtime:{offset}",
        )
        workspace.admit_result(
            live.closed.result,
            admitted_at_monotonic_ns=base + 1_000,
        )
        conflict = workspace.admit_conflict(
            live.conflict,
            tuple(item.result for item in live.conflict_outputs if item.result),
            admitted_at_monotonic_ns=base + 2_000,
        )
        snapshot = freeze_workspace_snapshot(
            preflight=self.preflight,
            workspace=workspace,
            conflict_carriage=conflict.conflict_carriage,
            frozen_at_monotonic_ns=base + 3_000,
        )
        return base, live, workspace, snapshot

    def _runtime(self, *, offset: int = 0, steps: int = 4, elapsed: int = 100_000_000):
        base, live, workspace, snapshot = self._snapshot_context(offset)
        authorization = authorize_deliberation(
            snapshot=snapshot,
            operation_allowlist=self.preflight.operation_allowlist,
            authorized_at_monotonic_ns=base + 4_000,
            maximum_step_count=steps,
            elapsed_time_budget_ns=elapsed,
        )
        runtime = start_deliberation(
            snapshot=snapshot,
            authorization=authorization,
            operation_allowlist=self.preflight.operation_allowlist,
            started_at_monotonic_ns=base + 4_001,
            process_instance_id=f"deliberation_test_process:{offset}",
            runtime_session_id=f"deliberation_test_runtime:{offset}",
        )
        return base, live, workspace, snapshot, authorization, runtime

    def test_package_143_read_only_consumer_binding_is_exact(self) -> None:
        binding = self.preflight.consumer_binding
        self.assertEqual(binding.consumer_scope, "package_144_deep_thought_deliberation_only")
        self.assertTrue(binding.package_143_store_read_only)
        self.assertTrue(binding.live_workspace_read_allowed_during_snapshot_freeze_only)
        self.assertFalse(binding.live_workspace_read_allowed_during_deliberation)
        self.assertFalse(binding.direct_package_142_input_allowed)
        self.assertFalse(binding.direct_perception_input_allowed)
        self.assertEqual(binding.production_result_consumer_allowlist, ())

    def test_package_143_store_is_query_only_and_unchanged(self) -> None:
        first = load_package_143_deliberation_evidence(PACKAGE_143_STATE)
        second = load_package_143_deliberation_evidence(PACKAGE_143_STATE)
        self.assertEqual(first.database_sha256, second.database_sha256)
        self.assertEqual(first.audit.audit_status, "passed_coarse_thought_workspace_v0")

    def test_snapshot_is_canonical_immutable_and_detached(self) -> None:
        _, _, _, snapshot = self._snapshot_context()
        self.assertEqual(snapshot.entry_count, 3)
        self.assertEqual(snapshot.entry_refs, tuple(sorted(snapshot.entry_refs)))
        self.assertTrue(snapshot.immutable)
        self.assertTrue(snapshot.detached_from_live_workspace)
        self.assertFalse(snapshot.live_workspace_read_after_freeze)
        with self.assertRaises(FrozenInstanceError):
            snapshot.entry_count = 1  # type: ignore[misc]

    def test_snapshot_is_deterministic_for_same_frozen_values(self) -> None:
        first = self._snapshot_context()[3]
        second = self._snapshot_context()[3]
        self.assertEqual(first.snapshot_sha256, second.snapshot_sha256)
        self.assertEqual(first.snapshot_id, second.snapshot_id)

    def test_live_workspace_change_cannot_change_frozen_snapshot(self) -> None:
        base, live, workspace, snapshot = self._snapshot_context()
        before = snapshot.to_dict()
        admission = workspace.admit_result(
            live.open.result,
            admitted_at_monotonic_ns=base + 4_000,
        )
        self.assertTrue(admission.evictions)
        self.assertEqual(snapshot.to_dict(), before)
        self.assertEqual(snapshot.snapshot_sha256, before["snapshot_sha256"])

    def test_operation_allowlist_is_fixed_and_non_executable(self) -> None:
        operations = self.preflight.operation_allowlist
        self.assertEqual(operations.operation_ids, OPERATION_ALLOWLIST)
        self.assertTrue(operations.deterministic)
        self.assertFalse(operations.free_text_reasoning_allowed)
        self.assertFalse(operations.arbitrary_program_execution_allowed)
        self.assertFalse(operations.recursive_operation_chaining_allowed)
        self.assertFalse(operations.conflict_resolution_allowed)

    def test_authorization_is_exact_one_use_and_bounded(self) -> None:
        base, _, _, snapshot = self._snapshot_context()
        authorization = authorize_deliberation(
            snapshot=snapshot,
            operation_allowlist=self.preflight.operation_allowlist,
            authorized_at_monotonic_ns=base + 4_000,
        )
        self.assertEqual(authorization.snapshot_id, snapshot.snapshot_id)
        self.assertEqual(authorization.allowed_operation_ids, OPERATION_ALLOWLIST)
        self.assertTrue(authorization.one_use)
        self.assertEqual(authorization.production_consumer_allowlist, ())

    def test_four_step_deliberation_completes_without_live_reads(self) -> None:
        base, _, _, _, _, runtime = self._runtime()
        output = runtime.execute_until_terminal(
            first_observed_at_monotonic_ns=base + 4_002
        )
        self.assertEqual(len(output.steps), 4)
        self.assertEqual(
            tuple(item.operation_id for item in output.steps), OPERATION_ALLOWLIST
        )
        self.assertTrue(all(not item.live_workspace_read for item in output.steps))
        self.assertEqual(output.terminal.terminal_state, "completed_bounded_deliberation")
        self.assertIsNotNone(output.result)

    def test_repeated_deliberation_is_deterministic(self) -> None:
        first = self._runtime(offset=0)
        second = self._runtime(offset=0)
        first_output = first[-1].execute_until_terminal(
            first_observed_at_monotonic_ns=self.base + 4_002
        )
        second_output = second[-1].execute_until_terminal(
            first_observed_at_monotonic_ns=self.base + 4_002
        )
        self.assertEqual(
            tuple(item.deterministic_output_sha256 for item in first_output.steps),
            tuple(item.deterministic_output_sha256 for item in second_output.steps),
        )
        self.assertEqual(
            first_output.result.bounded_result_annotation,
            second_output.result.bounded_result_annotation,
        )

    def test_step_budget_exhaustion_is_incomplete_without_result(self) -> None:
        base, _, _, _, _, runtime = self._runtime(steps=2)
        output = runtime.execute_until_terminal(
            first_observed_at_monotonic_ns=base + 4_002
        )
        self.assertEqual(len(output.steps), 2)
        self.assertEqual(output.terminal.terminal_state, "budget_exhausted_incomplete")
        self.assertEqual(output.terminal.terminal_reason, "step_budget_exhausted")
        self.assertIsNone(output.result)
        self.assertFalse(output.terminal.result_effective)

    def test_elapsed_budget_exhaustion_is_incomplete_without_guess(self) -> None:
        base, _, _, _, _, runtime = self._runtime(elapsed=1)
        output = runtime.execute_until_terminal(
            first_observed_at_monotonic_ns=base + 4_002
        )
        self.assertEqual(output.terminal.terminal_reason, "elapsed_time_budget_exhausted")
        self.assertEqual(output.terminal.completed_step_count, 0)
        self.assertIsNone(output.result)

    def test_cancellation_stops_following_steps_and_fails_neutral(self) -> None:
        base, _, _, _, _, runtime = self._runtime()
        runtime.execute_next(observed_at_monotonic_ns=base + 4_002)
        cancellation = runtime.cancel(requested_at_monotonic_ns=base + 4_003)
        self.assertTrue(cancellation.cancellation_succeeded)
        self.assertEqual(runtime.terminal.terminal_state, "cancelled_fail_to_neutral")
        self.assertIsNone(runtime.result)
        with self.assertRaisesRegex(ValueError, "already_terminal"):
            runtime.execute_next(observed_at_monotonic_ns=base + 4_004)

    def test_workspace_source_expiry_and_revocation_fail_neutral(self) -> None:
        for index, transition in enumerate(
            ("workspace_expired", "source_expired", "source_revoked"), start=1
        ):
            base, _, _, _, _, runtime = self._runtime(offset=index * 100_000)
            runtime.execute_next(observed_at_monotonic_ns=base + 4_002)
            invalidation = runtime.invalidate(
                transition_kind=transition,
                source_transition_ref=f"source:{transition}",
                observed_at_monotonic_ns=base + 4_003,
            )
            self.assertFalse(invalidation.snapshot_valid_after)
            self.assertFalse(invalidation.result_effective_after)
            self.assertTrue(runtime.terminal.fail_to_neutral)
            self.assertIsNone(runtime.result)

    def test_completed_result_is_revocable_and_becomes_ineffective(self) -> None:
        base, _, _, _, _, runtime = self._runtime()
        output = runtime.execute_until_terminal(
            first_observed_at_monotonic_ns=base + 4_002
        )
        self.assertTrue(output.terminal.result_effective)
        invalidation = runtime.invalidate(
            transition_kind="source_revoked",
            source_transition_ref="source:post_completion_revocation",
            observed_at_monotonic_ns=base + 4_010,
        )
        self.assertTrue(invalidation.result_effective_before)
        self.assertFalse(invalidation.result_effective_after)
        self.assertFalse(invalidation.further_steps_allowed)

    def test_invalid_snapshot_and_operation_fault_fail_neutral(self) -> None:
        base, _, _, _, _, invalid = self._runtime()
        invalid.invalidate(
            transition_kind="invalid_snapshot",
            source_transition_ref="snapshot:corrupt",
            observed_at_monotonic_ns=base + 4_002,
        )
        self.assertEqual(invalid.terminal.terminal_state, "blocked_invalid_snapshot")
        _, _, _, _, _, fault = self._runtime(offset=100_000)
        terminal = fault.execute_next(
            observed_at_monotonic_ns=self.base + 104_002,
            requested_operation_id="execute_python",
        )
        self.assertEqual(terminal.terminal_state, "operation_fault_fail_to_neutral")
        self.assertIsNone(fault.result)

    def test_unresolved_conflict_remains_unresolved_without_winner(self) -> None:
        base, _, _, snapshot, _, runtime = self._runtime()
        output = runtime.execute_until_terminal(
            first_observed_at_monotonic_ns=base + 4_002
        )
        self.assertEqual(snapshot.conflict_status, "unresolved_cross_family_conflict_preserved")
        self.assertEqual(output.result.conflict_status, snapshot.conflict_status)
        self.assertIsNone(output.result.winner_result_id)
        self.assertFalse(output.result.ranking_used)
        self.assertFalse(output.result.insertion_order_used_for_selection)
        self.assertFalse(output.result.budget_state_used_for_selection)

    def test_result_has_no_behavior_or_semantic_authority(self) -> None:
        base, _, _, _, _, runtime = self._runtime()
        result = runtime.execute_until_terminal(
            first_observed_at_monotonic_ns=base + 4_002
        ).result
        self.assertIsNone(result.semantic_label)
        self.assertEqual(result.production_consumer_count, 0)
        for field in (
            "purpose_authority",
            "memory_write_authority",
            "self_state_mutation_authority",
            "drive_authority",
            "perception_attention_authority",
            "candidate_ordering_authority",
            "action_selection_authority",
            "output_authority",
            "external_control_authority",
        ):
            self.assertFalse(getattr(result, field))

    def test_forbidden_authority_validator_rejects_each_surface(self) -> None:
        for name in (
            "purpose_created",
            "memory_write_created",
            "self_state_mutation_created",
            "drive_authority_created",
            "perception_attention_authority_created",
            "candidate_ordering_created",
            "selected_action_created",
            "output_created",
            "external_control_created",
            "llm_used",
            "codex_used",
            "network_used",
        ):
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, name):
                validate_no_forbidden_deliberation_authority(**{name: True})

    def test_store_is_append_only_and_has_no_active_or_recovery_table(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = Package144DeepThoughtDeliberationStore(directory)
            store.append_once(
                "deep_thought_workspace_consumer_bindings",
                self.preflight.consumer_binding,
            )
            self.assertEqual(store.count("deep_thought_workspace_consumer_bindings"), 1)
            with self.assertRaises(TypeError):
                store.update()
            with self.assertRaises(TypeError):
                store.delete()
            connection = sqlite3.connect(store.database_path)
            try:
                tables = {
                    row[0]
                    for row in connection.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'"
                    )
                }
            finally:
                connection.close()
            self.assertNotIn("active_deliberations", tables)
            self.assertNotIn("deliberation_recovery_heads", tables)
            self.assertFalse(store.audit_integrity()["active_deliberation_persisted"])

    def test_counterfactual_changes_only_deliberation_evidence(self) -> None:
        source = self.preflight.source.database_sha256
        record = build_deep_thought_counterfactual_equivalence(
            package_143_source_sha256_before=source,
            package_143_source_sha256_after=source,
            source_record_refs=(self.preflight.consumer_binding.consumer_binding_id,),
        )
        self.assertEqual(
            record.counterfactual_status,
            "passed_deep_thought_counterfactual_equivalence",
        )
        self.assertTrue(record.candidate_set_and_order_equivalent)
        self.assertTrue(record.selected_action_equivalent)
        self.assertTrue(record.output_equivalent)

    def test_operator_event_kinds_are_strictly_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            stream = LocalOperatorEventStream(LocalOperatorConsoleStore(directory))
            for kind in (
                "deep_thought_workspace_consumer_bound",
                "deep_thought_snapshot_contract_created",
                "deep_thought_operation_allowlist_created",
                "deep_thought_snapshot_frozen",
                "deep_thought_deliberation_authorized",
                "deep_thought_deliberation_started",
                "deep_thought_deliberation_step_completed",
                "bounded_deep_thought_result_created",
                "deep_thought_deliberation_completed",
                "deep_thought_deliberation_stopped",
                "deep_thought_deliberation_cancelled",
                "deep_thought_deliberation_invalidated",
                "deep_thought_counterfactual_verified",
                "package_144_audit_passed",
                "package_144_audit_blocked",
            ):
                event = stream.append_event(
                    event_kind=kind,
                    source_record_refs=(f"source:{kind}",),
                    source_trace_refs=("trace:test",),
                )
                self.assertFalse(event.llm_used)
                self.assertFalse(event.codex_used)
                self.assertFalse(event.network_used)

    def test_cli_requires_explicit_deliberation_authorization(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            args = [
                "run-deliberation",
                "--ashl-root",
                str(REPO_ROOT),
                "--state-dir",
                directory,
                "--package-143-state-dir",
                str(PACKAGE_143_STATE),
                "--package-142-state-dir",
                str(PACKAGE_142_STATE),
                "--package-141-state-dir",
                str(PACKAGE_141_STATE),
            ]
            with contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(package_144_cli(args), 2)
            self.assertIn(
                "blocked_deep_thought_deliberation_authorization_missing",
                output.getvalue(),
            )

    def test_runtime_suite_and_all_controls_are_real_and_pass(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            args = dict(
                ashl_root=REPO_ROOT,
                state_dir=directory,
                package_143_state_dir=PACKAGE_143_STATE,
                package_142_state_dir=PACKAGE_142_STATE,
                package_141_state_dir=PACKAGE_141_STATE,
            )
            run = run_deep_thought_deliberation_suite(
                **args, allow_deliberation=True
            )
            preflight = load_package_144_preflight(**args)
            controls = run_package_144_boundary_controls(
                preflight,
                ashl_root=REPO_ROOT,
                state_dir=directory,
            )
            self.assertEqual(run["main_terminal_state"], "completed_bounded_deliberation")
            self.assertEqual(run["step_budget_terminal"], "budget_exhausted_incomplete")
            self.assertEqual(run["elapsed_budget_terminal"], "budget_exhausted_incomplete")
            self.assertTrue(run["snapshot_unchanged_after_live_workspace_change"])
            self.assertTrue(controls.controls_passed)
            self.assertEqual(controls.passed_count, len(CONTROL_NAMES))

    def test_final_audit_passes_with_runtime_controls_and_regression_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            args = dict(
                ashl_root=REPO_ROOT,
                state_dir=directory,
                package_143_state_dir=PACKAGE_143_STATE,
                package_142_state_dir=PACKAGE_142_STATE,
                package_141_state_dir=PACKAGE_141_STATE,
            )
            run_deep_thought_deliberation_suite(**args, allow_deliberation=True)
            preflight = load_package_144_preflight(**args)
            store = Package144DeepThoughtDeliberationStore(directory)
            run_package_144_boundary_controls(
                preflight,
                ashl_root=REPO_ROOT,
                state_dir=directory,
                append_to=store,
            )
            tree_hash = repository_source_tree_sha256(REPO_ROOT)
            receipt = build_hashed_record(
                Package144RegressionReceipt,
                {
                    "regression_receipt_id": "",
                    "regression_receipt_sha256": "",
                    "schema_version": REGRESSION_SCHEMA_VERSION,
                    "created_at": utc_now(),
                    "baseline_commit": BASELINE_COMMIT,
                    "source_head": BASELINE_COMMIT,
                    "source_tree_sha256": tree_hash,
                    "command_results": (("test_scope", 0, "0" * 64),),
                    "targeted_package_144_passed": True,
                    "package_143_regressions_passed": True,
                    "package_132_140_boundary_regressions_passed": True,
                    "full_v1_discover_passed": True,
                    "compileall_passed": True,
                    "git_diff_check_passed": True,
                    "repository_pollution_absent": True,
                    "fresh_regressions_passed": True,
                    "source_record_refs": (f"source_tree:{tree_hash}",),
                },
                id_field="regression_receipt_id",
                hash_field="regression_receipt_sha256",
                prefix="deep_thought_regressions",
            )
            store.append_once("package_144_regression_receipts", receipt)
            audit = audit_package_144_deep_thought_deliberation(
                ashl_root=REPO_ROOT,
                state_dir=directory,
                package_143_state_dir=PACKAGE_143_STATE,
            )
            self.assertEqual(audit.audit_status, PASS_STATUS)
            self.assertTrue(audit.immutable_snapshot_verified)
            self.assertTrue(audit.multi_step_deliberation_verified)
            self.assertTrue(audit.step_budget_exhaustion_verified)
            self.assertTrue(audit.elapsed_budget_exhaustion_verified)
            self.assertTrue(audit.unresolved_conflict_preserved)
            self.assertEqual(audit.production_consumer_count, 0)


class Package144RepositoryBoundaryTests(unittest.TestCase):
    def test_package_144_does_not_import_forbidden_runtime_authorities(self) -> None:
        paths = tuple(
            (REPO_ROOT / "ashl_core_v1" / "thought").glob("*144*deliberation*.py")
        )
        imported: set[str] = set()
        for path in paths:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported.update(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imported.add(node.module)
        forbidden_prefixes = (
            "ashl_core_v1.perception",
            "ashl_core_v1.endocrine",
            "ashl_core_v1.memory",
            "ashl_core_v1.state",
            "ashl_core_v1.task",
            "ashl_core_v1.body",
            "ashl_core_v1.output",
        )
        self.assertFalse(
            tuple(name for name in imported if name.startswith(forbidden_prefixes))
        )

    def test_package_145_and_146_are_not_implemented(self) -> None:
        names = {
            path.name for path in (REPO_ROOT / "ashl_core_v1" / "thought").glob("*.py")
        }
        self.assertNotIn("package_145_thought_trace_boundary.py", names)
        self.assertNotIn("package_146_verification_handoff.py", names)
        self.assertNotIn("full_thought_engine.py", names)

    def test_registry_and_route_advance_only_to_145(self) -> None:
        registry = json.loads(
            (
                REPO_ROOT
                / "ashl_core_v1"
                / "docs"
                / "reference"
                / "package_number_registry_v0.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(registry["current_package_id"], "144")
        self.assertEqual(registry["package_status"]["144"], "completed")
        self.assertEqual(registry["package_status"]["145"], "next_critical_path")
        self.assertIn("144", registry["completed_package_ids"])
        self.assertNotIn("144", registry["future_package_ids"])
        route = (
            REPO_ROOT
            / "ashl_core_v1"
            / "docs"
            / "reference"
            / "package_123_to_daily_runtime_revised_route_v0.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Package 144 is completed", route)
        self.assertIn("Package 145 is next", route)
        self.assertIn("Package 144 does not implement Package 145", route)


if __name__ == "__main__":
    unittest.main()
