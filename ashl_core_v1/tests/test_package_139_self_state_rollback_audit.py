"""Package 139 verified-ancestor rollback, no-fork and audit tests."""

from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

from ashl_core_v1.runtime.host_sensor_types import sha256_bytes
from ashl_core_v1.state.package_133_cross_session_self_state_schema_audit import (
    create_package_133_representation_chain,
)
from ashl_core_v1.state.package_134_package_133_source import (
    load_package_133_source_read_only,
    package_133_source_tree_sha256,
)
from ashl_core_v1.state.package_137_self_state_review_store import (
    Package137SelfStateReviewStore,
)
from ashl_core_v1.state.package_138_self_state_readback_store import (
    Package138SelfStateReadbackStore,
)
from ashl_core_v1.state.package_139_self_state_rollback_audit import (
    audit_package_139_self_state_rollback,
    record_package_139_regression_receipt,
)
from ashl_core_v1.state.package_139_self_state_rollback_cli import main
from ashl_core_v1.state.package_139_self_state_rollback_controls import (
    run_package_139_self_state_rollback_controls,
)
from ashl_core_v1.state.package_139_self_state_rollback_store import (
    Package139SelfStateRollbackStore,
    package_139_store_path,
)
from ashl_core_v1.state.persistent_self_state_review_runtime import (
    run_real_persistent_self_state_review_gate,
)
from ashl_core_v1.state.persistent_self_state_review_types import (
    PASS_STATUS as PACKAGE_137_PASS_STATUS,
)
from ashl_core_v1.state.persistent_self_state_schema import (
    PACKAGE_132_PASS_STATUS,
    PASS_STATUS as PACKAGE_133_PASS_STATUS,
)
from ashl_core_v1.state.persistent_self_state_store import PersistentSelfStateStore
from ashl_core_v1.state.persistent_session_recovery_runtime import (
    run_real_fresh_process_recovery,
)
from ashl_core_v1.state.persistent_session_recovery_store import (
    PersistentSessionRecoveryStore,
)
from ashl_core_v1.state.persistent_session_recovery_types import (
    PASS_STATUS as PACKAGE_134_PASS_STATUS,
)
from ashl_core_v1.state.self_state_readback_runtime import (
    run_real_self_state_readback_boundary,
)
from ashl_core_v1.state.self_state_readback_types import (
    PASS_STATUS as PACKAGE_138_PASS_STATUS,
)
from ashl_core_v1.state.self_state_rollback_runtime import (
    run_real_self_state_rollback_and_roll_forward,
)
from ashl_core_v1.state.self_state_rollback_types import (
    BASELINE_COMMIT,
    CONTROL_NAMES,
    PASS_STATUS,
    ROLLBACK_OPERATION,
    ROLL_FORWARD_OPERATION,
)


class Package139SelfStateRollbackAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repo_root = Path(__file__).resolve().parents[2]
        cls.temporary = TemporaryDirectory(ignore_cleanup_errors=True)
        cls.root = Path(cls.temporary.name)
        cls.p133 = cls.root / "package133"
        cls.p134 = cls.root / "package134"
        cls.p137 = cls.root / "package137"
        cls.p138 = cls.root / "package138"
        cls.p139 = cls.root / "package139"
        cls._write_package_133_fixture(cls.p133)
        run_real_fresh_process_recovery(
            ashl_root=cls.repo_root,
            package_133_state_dir=cls.p133,
            state_dir=cls.p134,
            allow_session_recovery=True,
        )
        PersistentSessionRecoveryStore(cls.p134).append_record(
            "package_134_audits",
            {
                "audit_id": "package_134_audit:package_139_test_fixture",
                "created_at": "2026-08-10T00:00:00+00:00",
                "audit_status": PACKAGE_134_PASS_STATUS,
            },
        )
        run_real_persistent_self_state_review_gate(
            ashl_root=cls.repo_root,
            package_133_state_dir=cls.p133,
            package_134_state_dir=cls.p134,
            state_dir=cls.p137,
            teacher_actor="project_owner",
            teacher_role="project_owner",
            teacher_note="Package 139 test-only exact structural successor approval.",
            confirm_teacher_approval=True,
            allow_self_state_mutation=True,
        )
        Package137SelfStateReviewStore(cls.p137).append_once(
            "package_137_audits",
            {
                "audit_id": "package_137_audit:package_139_test_fixture",
                "created_at": "2026-08-10T00:01:00+00:00",
                "audit_status": PACKAGE_137_PASS_STATUS,
            },
        )
        run_real_self_state_readback_boundary(
            ashl_root=cls.repo_root,
            package_133_state_dir=cls.p133,
            package_134_state_dir=cls.p134,
            package_137_state_dir=cls.p137,
            state_dir=cls.p138,
            allow_self_state_readback=True,
            allow_fresh_process_recovery=True,
        )
        Package138SelfStateReadbackStore(cls.p138).append_once(
            "package_138_audits",
            {
                "audit_id": "package_138_audit:package_139_test_fixture",
                "created_at": "2026-08-10T00:02:00+00:00",
                "audit_status": PACKAGE_138_PASS_STATUS,
            },
        )
        source = load_package_133_source_read_only(cls.p133)
        cls.target = source.states[-2]
        cls.tree_before = package_133_source_tree_sha256(cls.p133)
        cls.head_before = PersistentSessionRecoveryStore(cls.p134).get_active_head()
        cls.real_run = run_real_self_state_rollback_and_roll_forward(
            ashl_root=cls.repo_root,
            package_133_state_dir=cls.p133,
            package_134_state_dir=cls.p134,
            package_137_state_dir=cls.p137,
            package_138_state_dir=cls.p138,
            state_dir=cls.p139,
            target_self_state_record_id=cls.target.self_state_record_id,
            allow_self_state_rollback=True,
            allow_exact_roll_forward=True,
        )
        cls.controls = run_package_139_self_state_rollback_controls(
            ashl_root=cls.repo_root,
            package_133_state_dir=cls.p133,
            package_134_state_dir=cls.p134,
            package_137_state_dir=cls.p137,
            package_138_state_dir=cls.p138,
            state_dir=cls.p139,
        )
        record_package_139_regression_receipt(
            state_dir=cls.p139,
            source_head=BASELINE_COMMIT,
            command_results=(("test_only_explicit_fixture", 0, sha256_bytes(b"passed")),),
            targeted_package_139_passed=True,
            package_133_passed=True,
            package_134_passed=True,
            package_137_passed=True,
            package_138_passed=True,
            full_discover_passed=True,
            compileall_passed=True,
            git_diff_check_passed=True,
            repository_pollution_absent=True,
            source_record_refs=(cls.real_run["rollback"]["receipt"].commit_receipt_id,),
        )
        cls.audit = audit_package_139_self_state_rollback(
            ashl_root=cls.repo_root,
            package_133_state_dir=cls.p133,
            package_134_state_dir=cls.p134,
            package_137_state_dir=cls.p137,
            package_138_state_dir=cls.p138,
            state_dir=cls.p139,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_rollback_contract_preserves_existing_authorities(self) -> None:
        contract = self._store().list_payloads("self_state_rollback_contracts")[0]
        self.assertEqual(contract["self_state_authority"], "package_133_immutable_self_state_lineage")
        self.assertEqual(contract["active_head_authority"], "package_134_separate_active_head_cas_authority")
        self.assertTrue(contract["verified_ancestor_only"])
        self.assertTrue(contract["exact_package_134_cas_required"])
        self.assertTrue(contract["readback_terminal_before_head_change"])
        self.assertFalse(contract["automatic_rebase_allowed"])
        self.assertFalse(contract["latest_selection_allowed"])

    def test_ancestor_proof_binds_exact_target_to_current_chain(self) -> None:
        proof = self.real_run["proof"]
        self.assertEqual(proof.target_self_state_record_id, self.target.self_state_record_id)
        self.assertEqual(proof.current_self_state_record_id, self.head_before.self_state_record_id)
        self.assertEqual(proof.ordered_target_to_current_state_refs[0], self.target.self_state_record_id)
        self.assertEqual(proof.ordered_target_to_current_state_refs[-1], self.head_before.self_state_record_id)
        self.assertTrue(proof.complete_parent_hash_chain_verified)
        self.assertTrue(proof.no_lineage_fork_verified)

    def test_rollback_and_roll_forward_are_two_new_exact_cas_revisions(self) -> None:
        rollback = self.real_run["rollback"]["receipt"]
        roll_forward = self.real_run["roll_forward"]["receipt"]
        self.assertEqual(rollback.operation, ROLLBACK_OPERATION)
        self.assertEqual(roll_forward.operation, ROLL_FORWARD_OPERATION)
        self.assertEqual(rollback.head_revision_after, self.head_before.head_revision + 1)
        self.assertEqual(roll_forward.head_revision_after, rollback.head_revision_after + 1)
        self.assertEqual(rollback.self_state_record_id_after, self.target.self_state_record_id)
        self.assertEqual(roll_forward.self_state_record_id_after, self.head_before.self_state_record_id)
        self.assertEqual(roll_forward.paired_rollback_receipt_ref, rollback.commit_receipt_id)

    def test_package_133_history_and_intervening_descendant_remain_unchanged(self) -> None:
        rollback = self.real_run["rollback"]["receipt"]
        self.assertEqual(self.tree_before, package_133_source_tree_sha256(self.p133))
        self.assertTrue(rollback.package_133_history_unchanged)
        self.assertIn(self.head_before.self_state_record_id, rollback.intervening_descendant_refs)
        records = PersistentSelfStateStore(self.p133).list_payloads("persistent_self_state_records")
        self.assertIn(self.head_before.self_state_record_id, {item["self_state_record_id"] for item in records})

    def test_readbacks_are_terminal_before_each_head_cas(self) -> None:
        gates = self._store().list_payloads("self_state_readback_invalidation_gates")
        self.assertEqual(len(gates), 2)
        self.assertTrue(all(item["active_readback_count_after"] == 0 for item in gates))
        self.assertTrue(all(item["invalidation_completed_before_cas"] for item in gates))
        self.assertTrue(all(not item["readback_authorization_granted_rollback"] for item in gates))

    def test_no_fork_rule_blocks_mutation_and_recovery_until_exact_roll_forward(self) -> None:
        guard = self.real_run["no_fork_guard"]
        self.assertTrue(guard.package_137_mutation_preflight_blocked)
        self.assertTrue(guard.package_134_recovery_resolution_blocked)
        self.assertFalse(guard.new_successor_from_selected_ancestor_allowed)
        self.assertTrue(guard.exact_roll_forward_required)
        self.assertFalse(guard.identity_fork_created)
        self.assertEqual(
            self.real_run["future_recovery_resolution"].decision,
            "allow_exact_recovery_cas",
        )

    def test_authorizations_are_single_use_and_separate_from_readback_and_teacher_review(self) -> None:
        authorizations = self._store().list_payloads("self_state_head_selection_authorizations")
        consumptions = self._store().list_payloads(
            "self_state_head_selection_authorization_consumptions"
        )
        self.assertEqual(len(authorizations), 2)
        self.assertEqual(len(consumptions), 2)
        self.assertTrue(all(item["one_use_only"] for item in authorizations))
        self.assertTrue(all(not item["readback_authorization_used"] for item in authorizations))
        self.assertTrue(all(not item["teacher_review_authorization_used"] for item in authorizations))

    def test_all_required_negative_controls_are_executable_and_pass(self) -> None:
        self.assertEqual(self.controls.control_names, CONTROL_NAMES)
        self.assertEqual(self.controls.passed_count, len(CONTROL_NAMES))
        self.assertTrue(self.controls.controls_passed, self.controls.failure_reasons)
        self.assertEqual(set(self.controls.passed_control_names), set(CONTROL_NAMES))
        cases = self._store().list_payloads("package_139_control_cases")
        self.assertEqual(tuple(item["control_name"] for item in cases), CONTROL_NAMES)
        self.assertTrue(all(item["validator_executed"] for item in cases))
        self.assertTrue(all(item["isolated_authority_clone_used"] for item in cases))
        self.assertTrue(all(not item["production_authority_changed"] for item in cases))

    def test_store_is_append_only_and_holds_no_self_state_or_head_authority(self) -> None:
        store = self._store()
        integrity = store.audit_integrity()
        self.assertTrue(integrity["valid"], integrity)
        self.assertFalse(integrity["package_133_history_table_present"])
        self.assertFalse(integrity["package_134_active_head_table_present"])
        for operation in (store.update, store.delete, store.replace):
            with self.assertRaisesRegex(TypeError, "append-only"):
                operation()

    def test_counterfactual_restores_no_runtime_or_content_state(self) -> None:
        comparison = self.real_run["comparison"]
        self.assertTrue(comparison.only_head_selection_and_audit_surfaces_differ)
        self.assertTrue(comparison.package_133_history_equivalent)
        self.assertTrue(comparison.memory_equivalent)
        self.assertTrue(comparison.perception_history_equivalent)
        self.assertTrue(comparison.drive_modulation_neutral)
        self.assertTrue(comparison.readback_requires_new_authorization)

    def test_cli_guided_run_requires_both_explicit_permissions(self) -> None:
        with TemporaryDirectory(ignore_cleanup_errors=True) as state_dir, redirect_stdout(io.StringIO()) as output:
            code = main(
                [
                    "guided-run",
                    "--ashl-root", str(self.repo_root),
                    "--package-133-state-dir", str(self.p133),
                    "--package-134-state-dir", str(self.p134),
                    "--package-137-state-dir", str(self.p137),
                    "--package-138-state-dir", str(self.p138),
                    "--state-dir", state_dir,
                    "--target-state-id", self.target.self_state_record_id,
                ]
            )
            self.assertEqual(code, 2)
            self.assertIn("requires --allow-self-state-rollback", output.getvalue())
            self.assertFalse(package_139_store_path(state_dir).exists())

    def test_final_audit_passes_without_package_140_or_behavior_authority(self) -> None:
        self.assertEqual(self.audit.audit_status, PASS_STATUS, self.audit.failure_reasons)
        self.assertEqual(self.audit.failure_reasons, ())
        self.assertTrue(self.audit.rollback_cas_verified)
        self.assertTrue(self.audit.roll_forward_cas_verified)
        self.assertTrue(self.audit.canonical_leaf_restored)
        self.assertTrue(self.audit.recovery_eligibility_restored_after_roll_forward)
        source_bindings = self._store().list_payloads(
            "self_state_rollback_source_bindings"
        )
        self.assertEqual(len(source_bindings), 2)
        self.assertIn(source_bindings[-1]["source_binding_id"], self.audit.source_record_refs)
        for field in (
            "memory_restored",
            "perception_history_restored",
            "working_readback_restored",
            "drive_trace_restored",
            "drive_modulation_restored",
            "attention_restored",
            "thought_engine_used",
            "action_created",
            "output_created",
            "identity_fork_created",
            "package_140_implemented",
        ):
            self.assertFalse(getattr(self.audit, field), field)
        self.assertEqual(
            (self.audit.llm_runtime_calls, self.audit.codex_runtime_calls, self.audit.network_runtime_calls),
            (0, 0, 0),
        )

    def test_registry_marks_139_and_140_completed_with_141_next(self) -> None:
        registry = json.loads(
            (self.repo_root / "ashl_core_v1/docs/reference/package_number_registry_v0.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(registry["current_package_id"], "140")
        self.assertEqual(registry["package_status"]["139"], "completed")
        self.assertEqual(registry["package_status"]["140"], "completed")
        self.assertEqual(registry["package_status"]["141"], "next_critical_path")
        self.assertIn("140", registry["completed_package_ids"])
        self.assertNotIn("140", registry["future_package_ids"])
        self.assertIn("139", registry["completed_package_ids"])
        self.assertNotIn("139", registry["future_package_ids"])

    def _store(self) -> Package139SelfStateRollbackStore:
        return Package139SelfStateRollbackStore(self.p139)

    @classmethod
    def _write_package_133_fixture(cls, state_dir: Path) -> None:
        result = create_package_133_representation_chain(
            ashl_root=cls.repo_root,
            state_dir=state_dir,
            parent_session_id="package_139_fixture_parent_session",
            child_session_id="package_139_fixture_child_session",
        )
        PersistentSelfStateStore(state_dir).append_generic_record(
            "package_133_audits",
            {
                "audit_id": "package_133_audit:package_139_test_fixture",
                "created_at": "2026-08-10T00:00:00+00:00",
                "audit_status": PACKAGE_133_PASS_STATUS,
                "package_132_audit_status": PACKAGE_132_PASS_STATUS,
                "package_132_closure_verified": True,
                "perception_line_remains_frozen": True,
                "representation_contract_id": result["contract"]["contract_id"],
                "representation_contract_verified": True,
                "parent_self_state_record_id": result["parent"]["self_state_record_id"],
                "child_self_state_record_id": result["child"]["self_state_record_id"],
                "parent_child_lineage_verified": True,
                "canonical_hash_chain_verified": True,
                "append_only_store_verified": True,
                "boundary_controls_passed": True,
                "fresh_regressions_passed": True,
                "legacy_state_payload_reused": False,
                "raw_perception_persisted": False,
                "world_fact_persisted": False,
                "memory_content_persisted": False,
                "semantic_history_persisted": False,
                "output_content_persisted": False,
                "cross_session_recovery_implemented": False,
                "active_head_created": False,
                "runtime_behavior_influence_created": False,
                "drive_signal_created": False,
                "memory_write_created": False,
                "perception_action_created": False,
                "thought_engine_used": False,
                "output_created": False,
                "package_134_implemented": False,
                "persistent_self_claimed": False,
                "failure_reasons": [],
            },
        )


if __name__ == "__main__":
    unittest.main()
