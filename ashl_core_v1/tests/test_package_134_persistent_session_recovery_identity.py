from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

from ashl_core_v1.runtime.host_sensor_types import sha256_payload
from ashl_core_v1.state.package_133_cross_session_self_state_schema_audit import (
    create_package_133_representation_chain,
)
from ashl_core_v1.state.package_134_package_133_source import (
    load_package_133_source_read_only,
    package_133_source_tree_sha256,
)
from ashl_core_v1.state.package_134_persistent_session_recovery_audit import (
    audit_package_134_persistent_session_recovery,
)
from ashl_core_v1.state.package_134_persistent_session_recovery_cli import main
from ashl_core_v1.state.package_134_persistent_session_recovery_controls import (
    run_package_134_recovery_controls,
)
from ashl_core_v1.state.persistent_self_state_schema import (
    PACKAGE_132_PASS_STATUS,
    PASS_STATUS as PACKAGE_133_PASS_STATUS,
)
from ashl_core_v1.state.persistent_self_state_store import PersistentSelfStateStore
from ashl_core_v1.state.persistent_session_recovery_runtime import (
    build_recovery_authorization,
    run_real_fresh_process_recovery,
    validate_recovery_authorization,
)
from ashl_core_v1.state.persistent_session_recovery_store import (
    PersistentSessionRecoveryStore,
)
from ashl_core_v1.state.persistent_session_recovery_types import (
    BASELINE_COMMIT,
    PASS_STATUS,
    REGRESSION_SCHEMA_VERSION,
    Package134RegressionReceipt,
    PersistentSessionIdentityBindingRecord,
)


class Package134PersistentSessionRecoveryIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repo_root = Path(__file__).resolve().parents[2]

    def test_package_133_is_unique_read_only_representation_authority(self) -> None:
        with TemporaryDirectory() as directory:
            source_root = Path(directory) / "package133"
            self._write_package_133_fixture(source_root)
            before = package_133_source_tree_sha256(source_root)
            source = load_package_133_source_read_only(source_root)
            after = package_133_source_tree_sha256(source_root)
            self.assertEqual(before, after)
            self.assertEqual(source.snapshot.package_133_audit_status, PACKAGE_133_PASS_STATUS)
            self.assertTrue(source.snapshot.unique_lineage_verified)
            self.assertTrue(source.snapshot.unique_leaf_verified)
            self.assertTrue(source.snapshot.full_parent_hash_chain_verified)
            self.assertTrue(source.snapshot.package_133_recovery_authority_absent)
            self.assertEqual(source.snapshot.state_record_count, 2)
            self.assertEqual(source.snapshot.transition_record_count, 1)

    def test_explicit_authorization_is_exact_scoped_expiring_and_single_use(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source_root = root / "package133"
            state_root = root / "package134"
            self._write_package_133_fixture(source_root)
            source = load_package_133_source_read_only(source_root)
            store = PersistentSessionRecoveryStore(state_root)
            authorization = build_recovery_authorization(
                source=source,
                operation="initialize_active_head",
                target_session_id="session-a",
                target_process_instance_id="process-a",
                expected_head=None,
            )
            store.append_record("persistent_session_recovery_authorizations", authorization)
            validate_recovery_authorization(
                store=store,
                authorization=authorization,
                source=source,
                operation="initialize_active_head",
                session_id="session-a",
                process_instance_id="process-a",
            )
            self.assertTrue(authorization.explicit_authorization)
            self.assertTrue(authorization.one_use_only)
            self.assertEqual(authorization.authorization_source, "explicit_local_operator_request")
            with self.assertRaisesRegex(RuntimeError, "scope_mismatch"):
                validate_recovery_authorization(
                    store=store,
                    authorization=authorization,
                    source=source,
                    operation="initialize_active_head",
                    session_id="wrong-session",
                    process_instance_id="process-a",
                )

    def test_real_process_a_to_process_b_recovery_and_cas(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source_root = root / "package133"
            state_root = root / "package134"
            self._write_package_133_fixture(source_root)
            source_before = package_133_source_tree_sha256(source_root)
            result = run_real_fresh_process_recovery(
                ashl_root=self.repo_root,
                package_133_state_dir=source_root,
                state_dir=state_root,
                allow_session_recovery=True,
            )
            source_after = package_133_source_tree_sha256(source_root)
            self.assertEqual(source_before, source_after)
            self.assertEqual(
                result["recovery_pair_status"],
                "passed_real_fresh_process_session_recovery",
            )
            process_a = result["process_a"]
            process_b = result["process_b"]
            self.assertNotEqual(
                process_a["operating_system_process_id"],
                process_b["operating_system_process_id"],
            )
            self.assertNotEqual(process_a["process_instance_id"], process_b["process_instance_id"])
            self.assertNotEqual(process_a["session_id"], process_b["session_id"])
            self.assertEqual(process_a["head_revision"], 1)
            self.assertEqual(process_b["head_revision"], 2)
            store = PersistentSessionRecoveryStore(state_root)
            head = store.get_active_head()
            self.assertEqual(head.head_revision, 2)
            self.assertEqual(head.bound_session_id, process_b["session_id"])
            self.assertEqual(head.previous_active_head_sha256, process_a["active_head_sha256"])
            self.assertEqual(store.count("active_head_cas_events"), 2)
            self.assertEqual(store.count("persistent_session_identity_bindings"), 2)
            self.assertEqual(store.count("recovery_authorization_consumptions"), 2)

    def test_recovery_restores_no_content_or_behavior_authority(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source_root = root / "package133"
            state_root = root / "package134"
            self._write_package_133_fixture(source_root)
            run_real_fresh_process_recovery(
                ashl_root=self.repo_root,
                package_133_state_dir=source_root,
                state_dir=state_root,
                allow_session_recovery=True,
            )
            store = PersistentSessionRecoveryStore(state_root)
            bindings = store.list_payloads("persistent_session_identity_bindings")
            forbidden = (
                "memory_content_restored",
                "perception_history_restored",
                "working_readback_restored",
                "drive_state_restored",
                "attention_state_restored",
                "thought_engine_state_restored",
                "output_state_restored",
                "action_state_restored",
                "learning_created",
                "behavior_influence_created",
            )
            self.assertTrue(all(item[name] is False for item in bindings for name in forbidden))
            payload = dict(bindings[-1])
            payload["memory_content_restored"] = True
            with self.assertRaises(ValueError):
                PersistentSessionIdentityBindingRecord(
                    **{
                        **payload,
                        "source_record_refs": tuple(payload["source_record_refs"]),
                    }
                )

    def test_negative_controls_are_actual_blocked_paths(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source_root = root / "package133"
            state_root = root / "package134"
            self._write_package_133_fixture(source_root)
            result = run_package_134_recovery_controls(
                ashl_root=self.repo_root,
                package_133_state_dir=source_root,
                state_dir=state_root,
                append=True,
            )
            self.assertTrue(result.controls_passed)
            self.assertEqual(result.passed_count, 12)
            self.assertEqual(result.expected_count, 12)

    def test_store_keeps_mutable_head_separate_from_append_only_history(self) -> None:
        with TemporaryDirectory() as directory:
            store = PersistentSessionRecoveryStore(directory)
            integrity = store.audit_integrity()
            self.assertTrue(integrity["valid"])
            self.assertTrue(integrity["active_head_separate_from_history"])
            self.assertTrue(integrity["history_tables_append_only"])
            with self.assertRaises(TypeError):
                store.update_history()
            with self.assertRaises(TypeError):
                store.delete_history()

    def test_recovery_requires_explicit_cli_flag(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source_root = root / "package133"
            state_root = root / "package134"
            self._write_package_133_fixture(source_root)
            output = io.StringIO()
            with redirect_stdout(output):
                result = main(
                    [
                        "run-real-recovery",
                        "--ashl-root",
                        str(self.repo_root),
                        "--package-133-state-dir",
                        str(source_root),
                        "--state-dir",
                        str(state_root),
                    ]
                )
            self.assertEqual(result, 2)
            self.assertIn("blocked_session_recovery_authorization_missing", output.getvalue())
            self.assertFalse((state_root / "package_134_persistent_session_recovery_v0").exists())

    def test_final_audit_passes_only_with_real_pair_controls_and_regressions(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source_root = root / "package133"
            state_root = root / "package134"
            self._write_package_133_fixture(source_root)
            run_real_fresh_process_recovery(
                ashl_root=self.repo_root,
                package_133_state_dir=source_root,
                state_dir=state_root,
                allow_session_recovery=True,
            )
            controls = run_package_134_recovery_controls(
                ashl_root=self.repo_root,
                package_133_state_dir=source_root,
                state_dir=state_root,
                append=True,
            )
            self.assertTrue(controls.controls_passed)
            store = PersistentSessionRecoveryStore(state_root)
            receipt = self._passing_regression_receipt()
            store.append_record("package_134_regression_receipts", receipt)
            audit = audit_package_134_persistent_session_recovery(
                ashl_root=self.repo_root,
                package_133_state_dir=source_root,
                state_dir=state_root,
                append=True,
            )
            self.assertEqual(audit.audit_status, PASS_STATUS)
            self.assertEqual(audit.failure_reasons, tuple())
            self.assertTrue(audit.process_ids_distinct)
            self.assertTrue(audit.active_head_cas_verified)
            self.assertTrue(audit.same_self_state_lineage_verified)
            self.assertFalse(audit.identity_fork_created)
            self.assertFalse(audit.memory_content_restored)
            self.assertFalse(audit.behavior_influence_created)
            self.assertFalse(audit.persistent_psychological_continuity_claimed)

    def test_audit_without_fresh_regressions_is_blocked(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source_root = root / "package133"
            state_root = root / "package134"
            self._write_package_133_fixture(source_root)
            run_real_fresh_process_recovery(
                ashl_root=self.repo_root,
                package_133_state_dir=source_root,
                state_dir=state_root,
                allow_session_recovery=True,
            )
            run_package_134_recovery_controls(
                ashl_root=self.repo_root,
                package_133_state_dir=source_root,
                state_dir=state_root,
                append=True,
            )
            audit = audit_package_134_persistent_session_recovery(
                ashl_root=self.repo_root,
                package_133_state_dir=source_root,
                state_dir=state_root,
                append=False,
            )
            self.assertNotEqual(audit.audit_status, PASS_STATUS)
            self.assertIn("regressions", audit.failure_reasons)

    def test_registry_route_preserves_package_134_after_package_136(self) -> None:
        registry_path = (
            self.repo_root
            / "ashl_core_v1"
            / "docs"
            / "reference"
            / "package_number_registry_v0.json"
        )
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        self.assertEqual(registry["current_package_id"], "144")
        self.assertIn("134", registry["completed_package_ids"])
        self.assertIn("135", registry["completed_package_ids"])
        self.assertNotIn("134", registry["future_package_ids"])
        self.assertEqual(registry["package_status"]["134"], "completed")
        self.assertEqual(registry["package_status"]["135"], "completed")
        self.assertEqual(registry["package_status"]["136"], "completed")
        self.assertEqual(registry["package_status"]["137"], "completed")
        self.assertEqual(registry["package_status"]["138"], "completed")
        self.assertEqual(registry["package_status"]["139"], "completed")
        self.assertEqual(registry["package_status"]["140"], "completed")
        self.assertEqual(registry["package_status"]["141"], "completed")
        self.assertEqual(registry["package_status"]["142"], "completed")
        self.assertEqual(registry["package_status"]["143"], "completed")
        self.assertEqual(registry["package_status"]["144"], "completed")
        self.assertEqual(registry["package_status"]["145"], "next_critical_path")
        digest = sha256_payload(
            {
                "current": registry["current_package_id"],
                "completed": tuple(registry["completed_package_ids"]),
                "future": tuple(registry["future_package_ids"]),
                "duplicates": tuple(registry["duplicate_package_ids"]),
            }
        )
        self.assertEqual(registry["registry_sha256"], digest)
        self.assertEqual(registry["registry_id"], f"package_number_registry:{digest[:16]}")

        document = (
            self.repo_root
            / "ashl_core_v1"
            / "docs"
            / "persistent_session_recovery_and_identity_v0.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Package 133 remains the only self-state representation authority", document)
        self.assertIn("structural cross-session identity continuity", document)
        self.assertIn("not complete psychological-state continuation", document)

        route = (
            self.repo_root
            / "ashl_core_v1"
            / "docs"
            / "reference"
            / "package_123_to_daily_runtime_revised_route_v0.md"
        ).read_text(encoding="utf-8")
        self.assertIn("| 134 | Persistent Session Recovery And Identity", route)
        self.assertIn("| 135 | Drive Signal Trace Separation", route)
        self.assertIn("| 135 | Drive Signal Trace Separation", route)
        self.assertIn("Package 138 exposes that exact state", route)
        self.assertIn("Package 139 selects only an explicit verified ancestor", route)
        self.assertIn("Package 140 is the frozen", route)
        self.assertIn("Package 145 is next", route)

        ledger = json.loads(
            (
                self.repo_root
                / "ashl_core_v1"
                / "docs"
                / "reference"
                / "architecture_capability_ledger_v0.json"
            ).read_text(encoding="utf-8")
        )
        entries = {item["package"]: item for item in ledger["capabilities"]}
        self.assertEqual(entries["134"]["status"], "completed")
        self.assertEqual(entries["135"]["status"], "completed")
        self.assertEqual(entries["136"]["status"], "completed")
        self.assertEqual(entries["137"]["status"], "completed")
        self.assertEqual(entries["138"]["status"], "completed")
        self.assertEqual(entries["139"]["status"], "completed")
        self.assertEqual(entries["140"]["status"], "completed")
        self.assertEqual(entries["141"]["status"], "completed")
        self.assertEqual(entries["142"]["status"], "completed")
        self.assertEqual(entries["143"]["status"], "completed")
        self.assertEqual(entries["144"]["status"], "completed")
        self.assertEqual(entries["145"]["status"], "next_critical_path")

    def _write_package_133_fixture(self, state_dir: Path) -> None:
        result = create_package_133_representation_chain(
            ashl_root=self.repo_root,
            state_dir=state_dir,
            parent_session_id="package_133_fixture_parent_session",
            child_session_id="package_133_fixture_child_session",
        )
        parent = result["parent"]
        child = result["child"]
        contract = result["contract"]
        payload = {
            "audit_id": "package_133_audit:test_only_explicit_fixture",
            "created_at": "2026-08-07T04:00:00+00:00",
            "audit_status": PACKAGE_133_PASS_STATUS,
            "package_132_audit_status": PACKAGE_132_PASS_STATUS,
            "package_132_closure_verified": True,
            "perception_line_remains_frozen": True,
            "representation_contract_id": contract["contract_id"],
            "representation_contract_verified": True,
            "parent_self_state_record_id": parent["self_state_record_id"],
            "child_self_state_record_id": child["self_state_record_id"],
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
        }
        PersistentSelfStateStore(state_dir).append_generic_record(
            "package_133_audits", payload
        )

    @staticmethod
    def _passing_regression_receipt() -> Package134RegressionReceipt:
        return Package134RegressionReceipt(
            regression_receipt_id="package_134_regressions:test_only_explicit_fixture",
            schema_version=REGRESSION_SCHEMA_VERSION,
            created_at="2026-08-07T04:01:00+00:00",
            baseline_commit=BASELINE_COMMIT,
            source_head=BASELINE_COMMIT,
            command_results=(("test_only_explicit_fixture", 0, "0" * 64),),
            targeted_package_134_passed=True,
            package_133_regressions_passed=True,
            state_engine_regressions_passed=True,
            full_v1_discover_passed=True,
            compileall_passed=True,
            git_diff_check_passed=True,
            pycache_redirected_outside_repo=True,
            fresh_regressions_passed=True,
        )


if __name__ == "__main__":
    unittest.main()
