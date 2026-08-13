from __future__ import annotations

import ast
import contextlib
import io
import json
import os
import sqlite3
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from ashl_core_v1.runtime.host_sensor_types import utc_now
from ashl_core_v1.runtime.local_operator_console_store import LocalOperatorConsoleStore
from ashl_core_v1.runtime.local_operator_event_stream import LocalOperatorEventStream
from ashl_core_v1.thought.package_141_instinct_audit import repository_source_tree_sha256
from ashl_core_v1.thought.package_142_specialized_thought_runtime import (
    invalidate_specialized_results,
)
from ashl_core_v1.thought.package_143_coarse_workspace_audit import (
    audit_package_143_coarse_workspace,
    run_package_143_boundary_controls,
)
from ashl_core_v1.thought.package_143_coarse_workspace_cli import main as package_143_cli
from ashl_core_v1.thought.package_143_coarse_workspace_runtime import (
    build_live_package_142_inputs,
    build_workspace_counterfactual_equivalence,
    load_package_142_workspace_evidence,
    load_package_143_preflight,
    open_ephemeral_workspace,
    recover_workspace_from_store,
    run_coarse_workspace_suite,
    validate_no_forbidden_workspace_authority,
)
from ashl_core_v1.thought.package_143_coarse_workspace_store import (
    Package143CoarseWorkspaceStore,
)
from ashl_core_v1.thought.coarse_thought_workspace_types import (
    BASELINE_COMMIT,
    CAPACITY,
    CONTROL_NAMES,
    EVICTION_POLICY,
    PASS_STATUS,
    REGRESSION_SCHEMA_VERSION,
    Package143RegressionReceipt,
    build_hashed_record,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
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


@unittest.skipUnless(_official_available(), "Package 141/142 official evidence unavailable")
class Package143CoarseWorkspaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.preflight = load_package_143_preflight(
            ashl_root=REPO_ROOT,
            package_142_state_dir=PACKAGE_142_STATE,
            package_141_state_dir=PACKAGE_141_STATE,
        )

    def setUp(self) -> None:
        self.base = 30_000_000_000
        self.live = build_live_package_142_inputs(
            self.preflight,
            base_monotonic_ns=self.base + 100,
        )

    def _workspace(self, offset: int = 0):
        return open_ephemeral_workspace(
            self.preflight,
            opened_at_monotonic_ns=self.base + offset,
            process_instance_id=f"test_process:{offset}",
            runtime_session_id=f"test_runtime:{offset}",
        )

    @property
    def closed(self):
        return self.live.closed.result

    @property
    def opened(self):
        return self.live.open.result

    @property
    def conflict_results(self):
        return tuple(item.result for item in self.live.conflict_outputs if item.result)

    def test_read_only_package_142_consumer_binding_is_exact(self) -> None:
        binding = self.preflight.consumer_binding
        self.assertEqual(binding.consumer_scope, "package_143_coarse_thought_workspace_only")
        self.assertTrue(binding.package_142_store_read_only)
        self.assertFalse(binding.package_142_history_mutated)
        self.assertFalse(binding.direct_perception_input_allowed)
        self.assertFalse(binding.legacy_thought_signal_allowed)
        self.assertEqual(binding.drive_input_allowlist, ())
        self.assertEqual(binding.self_state_readback_input_allowlist, ())
        self.assertEqual(binding.production_output_consumer_allowlist, ())

    def test_package_142_database_is_query_only_and_unchanged(self) -> None:
        first = load_package_142_workspace_evidence(PACKAGE_142_STATE)
        second = load_package_142_workspace_evidence(PACKAGE_142_STATE)
        self.assertEqual(first.database_sha256, second.database_sha256)
        self.assertEqual(first.audit.audit_status, "passed_specialized_thought_bounded_rules_v0")

    def test_workspace_contract_is_ephemeral_bounded_and_non_authoritative(self) -> None:
        contract = self.preflight.workspace_contract
        self.assertEqual(contract.maximum_entry_count, 3)
        self.assertTrue(contract.ephemeral)
        self.assertTrue(contract.fresh_process_starts_empty)
        self.assertFalse(contract.cross_session_recovery_allowed)
        self.assertFalse(contract.persistent_workspace_state_created)
        for field in (
            "iterative_reasoning_allowed",
            "recursive_rule_chaining_allowed",
            "deep_search_allowed",
            "conflict_resolution_allowed",
            "verification_proposal_authority",
            "purpose_authority",
            "candidate_ordering_authority",
            "action_selection_authority",
            "memory_write_authority",
            "self_state_mutation_authority",
            "perception_action_authority",
            "output_authority",
            "external_control_authority",
        ):
            self.assertFalse(getattr(contract, field), field)

    def test_fresh_workspace_starts_empty_and_process_local(self) -> None:
        workspace = self._workspace()
        self.assertEqual(workspace.occupancy, 0)
        self.assertEqual(workspace.session.initial_entry_count, 0)
        self.assertEqual(workspace.session.recovered_entry_count, 0)
        self.assertFalse(workspace.session.persistent_recovery_used)

    def test_active_typed_result_is_admitted_with_source_bounded_expiry(self) -> None:
        workspace = self._workspace()
        output = workspace.admit_result(
            self.closed,
            admitted_at_monotonic_ns=self.base + 1_000,
        )
        self.assertEqual(workspace.occupancy, 1)
        self.assertEqual(output.admission.admission_status, "admitted")
        self.assertEqual(output.entries[0].source_specialized_result_id, self.closed.specialized_result_id)
        self.assertLessEqual(output.entries[0].expires_at_monotonic_ns, self.closed.expires_at_monotonic_ns)
        self.assertIsNone(output.entries[0].priority)
        self.assertIsNone(output.entries[0].rank)
        self.assertIsNone(output.entries[0].truth_value)

    def test_expired_or_precreation_result_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "expired"):
            self._workspace().admit_result(
                self.closed,
                admitted_at_monotonic_ns=self.closed.expires_at_monotonic_ns,
            )
        with self.assertRaisesRegex(ValueError, "before_creation"):
            self._workspace().admit_result(
                self.closed,
                admitted_at_monotonic_ns=self.closed.created_at_monotonic_ns - 1,
            )

    def test_revoked_result_is_rejected_from_typed_invalidation(self) -> None:
        invalidation = invalidate_specialized_results(
            output=self.live.closed,
            transition_kind="upstream_precursor_revoked",
            observed_at_monotonic_ns=self.base + 500,
        )
        with self.assertRaisesRegex(ValueError, "revoked"):
            self._workspace().admit_result(
                self.closed,
                admitted_at_monotonic_ns=self.base + 1_000,
                source_invalidation=invalidation,
            )

    def test_duplicate_result_is_rejected_for_entire_session(self) -> None:
        workspace = self._workspace()
        workspace.admit_result(self.closed, admitted_at_monotonic_ns=self.base + 1_000)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            workspace.admit_result(self.closed, admitted_at_monotonic_ns=self.base + 1_001)

    def test_unresolved_conflict_is_admitted_atomically_and_unchanged(self) -> None:
        workspace = self._workspace()
        output = workspace.admit_conflict(
            self.live.conflict,
            self.conflict_results,
            admitted_at_monotonic_ns=self.base + 1_000,
        )
        self.assertEqual(workspace.occupancy, 2)
        self.assertEqual(len(output.entries), 2)
        carriage = output.conflict_carriage
        self.assertIsNotNone(carriage)
        self.assertEqual(carriage.conflict_status_in_workspace, "unresolved_cross_family_conflict_preserved")
        self.assertTrue(carriage.all_results_preserved)
        self.assertIsNone(carriage.winner_entry_id)
        self.assertFalse(carriage.priority_used)
        self.assertFalse(carriage.ranking_used)
        self.assertFalse(carriage.truth_selection_created)

    def test_known_conflict_cannot_be_partially_admitted(self) -> None:
        workspace = self._workspace()
        with self.assertRaisesRegex(ValueError, "partial_conflict"):
            workspace.admit_result(
                self.conflict_results[0],
                admitted_at_monotonic_ns=self.base + 1_000,
            )

    def test_zero_priority_injection_is_rejected(self) -> None:
        workspace = self._workspace()
        output = workspace.admit_result(
            self.closed,
            admitted_at_monotonic_ns=self.base + 1_000,
        )
        with self.assertRaisesRegex(ValueError, "selection metadata"):
            replace(output.entries[0], priority=0)

    def test_capacity_three_and_oldest_group_eviction_are_deterministic(self) -> None:
        evicted_ids = []
        for offset in (0, 10):
            workspace = self._workspace(offset)
            first = workspace.admit_result(
                self.closed,
                admitted_at_monotonic_ns=self.base + offset + 1_000,
            )
            workspace.admit_conflict(
                self.live.conflict,
                self.conflict_results,
                admitted_at_monotonic_ns=self.base + offset + 1_001,
            )
            self.assertEqual(workspace.occupancy, CAPACITY)
            final = workspace.admit_result(
                self.opened,
                admitted_at_monotonic_ns=self.base + offset + 1_002,
            )
            self.assertEqual(workspace.occupancy, CAPACITY)
            self.assertEqual(final.evictions[0].evicted_admission_group_id, first.admission.admission_group_id)
            self.assertEqual(final.evictions[0].eviction_policy, EVICTION_POLICY)
            evicted_ids.append(final.evictions[0].evicted_admission_group_id)
        self.assertEqual(evicted_ids[0], evicted_ids[1])

    def test_eviction_has_no_error_importance_forgetting_or_winner_semantics(self) -> None:
        workspace = self._workspace()
        workspace.admit_result(self.closed, admitted_at_monotonic_ns=self.base + 1_000)
        workspace.admit_conflict(
            self.live.conflict,
            self.conflict_results,
            admitted_at_monotonic_ns=self.base + 1_001,
        )
        eviction = workspace.admit_result(
            self.opened,
            admitted_at_monotonic_ns=self.base + 1_002,
        ).evictions[0]
        self.assertEqual(eviction.eviction_reason, "capacity_bookkeeping_only")
        self.assertFalse(eviction.error_claimed)
        self.assertFalse(eviction.negation_claimed)
        self.assertFalse(eviction.forgetting_claimed)
        self.assertFalse(eviction.low_importance_claimed)
        self.assertFalse(eviction.behavior_suppression_claimed)
        self.assertFalse(eviction.winner_created)

    def test_conflict_group_is_evicted_atomically(self) -> None:
        second = build_live_package_142_inputs(
            self.preflight,
            base_monotonic_ns=self.base + 400,
        )
        second_results = tuple(item.result for item in second.conflict_outputs if item.result)
        workspace = self._workspace()
        workspace.admit_conflict(
            self.live.conflict,
            self.conflict_results,
            admitted_at_monotonic_ns=self.base + 1_000,
        )
        workspace.admit_result(self.closed, admitted_at_monotonic_ns=self.base + 1_001)
        output = workspace.admit_conflict(
            second.conflict,
            second_results,
            admitted_at_monotonic_ns=self.base + 1_002,
        )
        self.assertEqual(len(output.evictions), 1)
        self.assertEqual(len(output.evictions[0].evicted_entry_refs), 2)
        self.assertTrue(output.evictions[0].group_evicted_atomically)

    def test_source_expiry_cascades_without_orphan(self) -> None:
        workspace = self._workspace()
        admitted = workspace.admit_result(
            self.opened,
            admitted_at_monotonic_ns=self.base + 1_000,
        )
        cascade = workspace.cascade_invalidate(
            source_result_refs=(self.opened.specialized_result_id,),
            transition_kind="source_result_expired",
            observed_at_monotonic_ns=self.opened.expires_at_monotonic_ns,
        )
        self.assertEqual(workspace.occupancy, 0)
        self.assertEqual(cascade.invalidated_workspace_entry_refs, (admitted.entries[0].workspace_entry_id,))
        self.assertEqual(cascade.orphan_entry_count_after, 0)
        self.assertFalse(cascade.entries_valid_after_transition)

    def test_one_conflict_member_revocation_invalidates_group_atomically(self) -> None:
        workspace = self._workspace()
        admitted = workspace.admit_conflict(
            self.live.conflict,
            self.conflict_results,
            admitted_at_monotonic_ns=self.base + 1_000,
        )
        cascade = workspace.cascade_invalidate(
            source_result_refs=(self.conflict_results[0].specialized_result_id,),
            transition_kind="source_result_revoked",
            observed_at_monotonic_ns=self.base + 1_001,
        )
        self.assertEqual(workspace.occupancy, 0)
        self.assertTrue(cascade.conflict_group_invalidated_atomically)
        self.assertEqual(len(cascade.invalidated_workspace_entry_refs), len(admitted.entries))

    def test_close_invalidates_remaining_entries_and_cannot_be_recovered(self) -> None:
        workspace = self._workspace()
        workspace.admit_result(self.closed, admitted_at_monotonic_ns=self.base + 1_000)
        output = workspace.close(closed_at_monotonic_ns=self.base + 2_000)
        self.assertEqual(output.closure.entry_count_after_close, 0)
        self.assertTrue(output.closure.all_entries_invalidated)
        self.assertFalse(output.closure.workspace_recoverable)
        self.assertFalse(output.closure.active_workspace_payload_persisted)
        self.assertTrue(output.cascades[0].result_valid_after_transition)
        self.assertFalse(output.cascades[0].entries_valid_after_transition)
        with self.assertRaisesRegex(ValueError, "recovery_forbidden"):
            recover_workspace_from_store("anything")

    def test_cross_session_admission_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "cross_session"):
            self._workspace().admit_result(
                self.closed,
                admitted_at_monotonic_ns=self.base + 1_000,
                target_workspace_session_id="different_session",
            )

    def test_counterfactual_preserves_all_authority_surfaces(self) -> None:
        record = build_workspace_counterfactual_equivalence(
            root=REPO_ROOT,
            source_sha256_before=self.preflight.source.database_sha256,
            source_sha256_after=self.preflight.source.database_sha256,
            source_record_refs=(self.preflight.consumer_binding.consumer_binding_id,),
        )
        self.assertEqual(record.counterfactual_status, "passed_coarse_workspace_counterfactual_equivalence")
        self.assertTrue(record.runtime_behavior_equivalent)
        self.assertTrue(record.memory_equivalent)
        self.assertTrue(record.purpose_equivalent)
        self.assertTrue(record.action_equivalent)
        self.assertTrue(record.output_equivalent)
        self.assertTrue(record.self_state_equivalent)
        self.assertTrue(record.drive_equivalent)
        self.assertTrue(record.perception_authority_equivalent)

    def test_forbidden_authority_validator_blocks_every_later_capability(self) -> None:
        for name in (
            "iterative_reasoning_created",
            "recursive_rule_chaining_created",
            "deep_search_created",
            "conflict_resolution_created",
            "verification_proposal_created",
            "purpose_created",
            "selected_action_created",
            "memory_write_created",
            "self_state_write_created",
            "drive_input_used",
            "self_state_readback_used",
            "output_created",
            "external_control_created",
            "package_144_implemented",
            "llm_used",
            "codex_used",
            "network_used",
        ):
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, "forbidden"):
                validate_no_forbidden_workspace_authority(**{name: True})

    def test_store_is_append_only_and_has_no_active_workspace_table(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = Package143CoarseWorkspaceStore(directory)
            store.append_once("coarse_workspace_consumer_bindings", self.preflight.consumer_binding)
            store.append_once("coarse_workspace_consumer_bindings", self.preflight.consumer_binding)
            self.assertEqual(store.count("coarse_workspace_consumer_bindings"), 1)
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
            self.assertNotIn("active_workspace", tables)
            self.assertNotIn("workspace_snapshots", tables)
            self.assertNotIn("workspace_recovery_heads", tables)
            self.assertFalse(store.audit_integrity()["active_workspace_state_persisted"])

    def test_store_rejects_private_absolute_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = Package143CoarseWorkspaceStore(directory)
            payload = self.preflight.consumer_binding.to_dict()
            payload["source_trace_refs"] = [r"C:\private\workspace"]
            with self.assertRaisesRegex(ValueError, "absolute paths"):
                store.append_once("coarse_workspace_consumer_bindings", payload)

    def test_fresh_process_probe_starts_empty_with_distinct_pid(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = run_coarse_workspace_suite(
                ashl_root=REPO_ROOT,
                state_dir=directory,
                package_142_state_dir=PACKAGE_142_STATE,
                package_141_state_dir=PACKAGE_141_STATE,
            )
            self.assertTrue(result["fresh_process_empty"])
            self.assertNotEqual(result["operating_system_process_id"], result["fresh_process_pid"])
            store = Package143CoarseWorkspaceStore(directory)
            reset = store.latest_payload("coarse_workspace_fresh_process_resets")
            self.assertTrue(reset["processes_distinct"])
            self.assertEqual(reset["initial_entry_count"], 0)
            self.assertEqual(reset["recovered_entry_count"], 0)

    def test_all_boundary_controls_are_real_and_pass(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run_coarse_workspace_suite(
                ashl_root=REPO_ROOT,
                state_dir=directory,
                package_142_state_dir=PACKAGE_142_STATE,
                package_141_state_dir=PACKAGE_141_STATE,
            )
            result = run_package_143_boundary_controls(
                self.preflight,
                ashl_root=REPO_ROOT,
                state_dir=directory,
            )
            self.assertTrue(result.controls_passed)
            self.assertEqual(result.passed_count, len(CONTROL_NAMES))
            self.assertEqual(result.failed_control_names, ())

    def test_operator_event_kinds_are_strictly_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            stream = LocalOperatorEventStream(LocalOperatorConsoleStore(directory))
            for kind in (
                "coarse_workspace_consumer_bound",
                "coarse_workspace_contract_created",
                "coarse_workspace_session_started",
                "coarse_workspace_result_admitted",
                "coarse_workspace_conflict_carried",
                "coarse_workspace_capacity_eviction",
                "coarse_workspace_entry_invalidated",
                "coarse_workspace_closed",
                "coarse_workspace_fresh_process_reset_verified",
                "coarse_workspace_counterfactual_verified",
                "package_143_audit_passed",
                "package_143_audit_blocked",
            ):
                event = stream.append_event(
                    event_kind=kind,
                    source_record_refs=(f"source:{kind}",),
                    source_trace_refs=("trace:test",),
                )
                self.assertFalse(event.llm_used)
                self.assertFalse(event.codex_used)
                self.assertFalse(event.network_used)

    def test_cli_preflight_workspace_and_show_are_unambiguous(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            common = [
                "--ashl-root",
                str(REPO_ROOT),
                "--state-dir",
                directory,
                "--package-142-state-dir",
                str(PACKAGE_142_STATE),
                "--package-141-state-dir",
                str(PACKAGE_141_STATE),
            ]
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(package_143_cli(["preflight", *common]), 0)
                self.assertEqual(package_143_cli(["run-workspace", *common]), 0)
                self.assertEqual(package_143_cli(["show-contract", "--state-dir", directory]), 0)
                self.assertEqual(package_143_cli(["show-evictions", "--state-dir", directory]), 0)

    def test_final_audit_passes_with_real_lifecycle_and_fresh_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run_coarse_workspace_suite(
                ashl_root=REPO_ROOT,
                state_dir=directory,
                package_142_state_dir=PACKAGE_142_STATE,
                package_141_state_dir=PACKAGE_141_STATE,
            )
            store = Package143CoarseWorkspaceStore(directory)
            controls = run_package_143_boundary_controls(
                self.preflight,
                ashl_root=REPO_ROOT,
                state_dir=directory,
                append_to=store,
            )
            tree_hash = repository_source_tree_sha256(REPO_ROOT)
            receipt = build_hashed_record(
                Package143RegressionReceipt,
                {
                    "regression_receipt_id": "",
                    "regression_receipt_sha256": "",
                    "schema_version": REGRESSION_SCHEMA_VERSION,
                    "created_at": utc_now(),
                    "baseline_commit": BASELINE_COMMIT,
                    "source_head": BASELINE_COMMIT,
                    "source_tree_sha256": tree_hash,
                    "command_results": (("test_scope", 0, "0" * 64),),
                    "targeted_package_143_passed": True,
                    "package_142_regressions_passed": True,
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
                prefix="coarse_workspace_regressions",
            )
            store.append_once("package_143_regression_receipts", receipt)
            audit = audit_package_143_coarse_workspace(
                ashl_root=REPO_ROOT,
                state_dir=directory,
                package_142_state_dir=PACKAGE_142_STATE,
                package_141_state_dir=PACKAGE_141_STATE,
            )
            self.assertTrue(controls.controls_passed)
            self.assertEqual(audit.audit_status, PASS_STATUS)
            self.assertEqual(audit.maximum_observed_occupancy, CAPACITY)
            self.assertEqual(audit.orphan_workspace_entry_count, 0)
            self.assertTrue(audit.conflict_carriage_verified)
            self.assertTrue(audit.fresh_process_reset_verified)
            self.assertFalse(audit.persistent_workspace_state_created)
            self.assertFalse(audit.iterative_reasoning_created)
            self.assertFalse(audit.package_144_implemented)


class Package143RepositoryBoundaryTests(unittest.TestCase):
    def test_package_143_runtime_does_not_import_forbidden_authorities(self) -> None:
        paths = tuple((REPO_ROOT / "ashl_core_v1" / "thought").glob("*143*workspace*.py"))
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
            "ashl_core_v1.thought.types",
        )
        self.assertFalse(
            tuple(name for name in imported if name.startswith(forbidden_prefixes))
        )

    def test_no_package_145_trace_boundary_or_full_thought_engine_created(self) -> None:
        names = {
            path.name for path in (REPO_ROOT / "ashl_core_v1" / "thought").glob("*.py")
        }
        self.assertNotIn("package_145_thought_trace_boundary.py", names)
        self.assertNotIn("full_thought_engine.py", names)

    def test_registry_and_route_advance_only_to_144(self) -> None:
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
        self.assertEqual(registry["package_status"]["143"], "completed")
        self.assertEqual(registry["package_status"]["144"], "completed")
        self.assertEqual(registry["package_status"]["145"], "next_critical_path")
        self.assertIn("143", registry["completed_package_ids"])
        self.assertNotIn("143", registry["future_package_ids"])
        route = (
            REPO_ROOT
            / "ashl_core_v1"
            / "docs"
            / "reference"
            / "package_123_to_daily_runtime_revised_route_v0.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Package 143 is completed", route)
        self.assertIn("Package 144 is completed", route)
        self.assertIn("Package 145 is next", route)
        self.assertIn("Package 144 does not implement Package 145", route)


if __name__ == "__main__":
    unittest.main()
