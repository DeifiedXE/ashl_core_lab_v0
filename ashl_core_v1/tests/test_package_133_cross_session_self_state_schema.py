from __future__ import annotations

import io
import json
import sqlite3
import unittest
from contextlib import closing, redirect_stdout
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory

from ashl_core_v1.runtime.host_sensor_types import canonical_json, sha256_payload
from ashl_core_v1.state.package_133_cross_session_self_state_schema_audit import (
    audit_package_133_cross_session_self_state_schema,
    create_package_133_representation_chain,
    run_package_133_boundary_controls,
)
from ashl_core_v1.state.package_133_cross_session_self_state_schema_cli import main
from ashl_core_v1.state.persistent_self_state_boundary import (
    build_state_like_structure_inventory,
    load_authoritative_self_state_contract,
)
from ashl_core_v1.state.persistent_self_state_lineage import (
    build_initial_self_state_record,
    build_self_state_lineage_validation_record,
    build_successor_self_state_records,
    validate_persistent_self_state_lineage,
)
from ashl_core_v1.state.persistent_self_state_schema import (
    ALLOWED_PERSISTENT_FIELDS,
    BASELINE_COMMIT,
    PACKAGE_132_PASS_STATUS,
    PASS_STATUS,
    REGRESSION_SCHEMA_VERSION,
    Package133RegressionReceipt,
    PersistentSelfStateRecord,
)
from ashl_core_v1.state.persistent_self_state_store import (
    PersistentSelfStateStore,
)


class Package133CrossSessionSelfStateSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repo_root = Path(__file__).resolve().parents[2]
        cls.contract = load_authoritative_self_state_contract(cls.repo_root)

    def _chain(self):
        parent = build_initial_self_state_record(
            contract=self.contract,
            origin_session_id="session-parent",
            created_at="2026-08-07T00:01:00+00:00",
        )
        child, transition = build_successor_self_state_records(
            parent=parent,
            contract=self.contract,
            source_session_id="session-child",
            created_at="2026-08-07T00:02:00+00:00",
        )
        validation = build_self_state_lineage_validation_record(
            parent=parent,
            child=child,
            transition=transition,
            created_at="2026-08-07T00:03:00+00:00",
        )
        return parent, child, transition, validation

    def test_authoritative_contract_is_exact_hashed_and_representation_only(self) -> None:
        contract = self.contract
        self.assertEqual(contract.baseline_commit, BASELINE_COMMIT)
        self.assertEqual(contract.allowed_persistent_fields, ALLOWED_PERSISTENT_FIELDS)
        self.assertTrue(contract.state_engine_continuity_authority_reused)
        self.assertFalse(contract.legacy_state_payload_reused)
        self.assertFalse(contract.legacy_store_directly_reused)
        self.assertFalse(contract.active_head_created)
        self.assertFalse(contract.cross_session_recovery_enabled)
        self.assertFalse(contract.runtime_behavior_influence_enabled)
        self.assertFalse(contract.persistent_self_claim_authorized)
        self.assertEqual(contract.next_package, "134")

    def test_state_like_inventory_is_source_grounded_and_complete(self) -> None:
        records = build_state_like_structure_inventory(self.repo_root)
        self.assertEqual(len(records), 9)
        self.assertTrue(all(item.source_scan_verified for item in records))
        kinds = {item.structure_kind: item for item in records}
        self.assertEqual(
            kinds["legacy_session_state_snapshot"].self_state_classification,
            "legacy_persistence_not_self_state",
        )
        self.assertEqual(
            kinds["state_engine_cradle_handoff"].self_state_classification,
            "continuity_authority_reused_boundary_only",
        )
        self.assertEqual(
            kinds["working_readback"].self_state_classification,
            "content_system_not_self_state",
        )
        self.assertEqual(
            kinds["perception_and_temporal_history"].self_state_classification,
            "evidence_history_not_self_state",
        )
        self.assertEqual(
            kinds["operator_runtime_status"].self_state_classification,
            "operational_view_not_self_state",
        )

    def test_parent_child_lineage_is_canonical_and_cross_session(self) -> None:
        parent, child, transition, validation = self._chain()
        result = validate_persistent_self_state_lineage(parent, child, transition)
        self.assertTrue(result["valid"])
        self.assertTrue(validation.lineage_valid)
        self.assertEqual(parent.self_state_version, 1)
        self.assertEqual(child.self_state_version, 2)
        self.assertEqual(parent.lineage_generation, 0)
        self.assertEqual(child.lineage_generation, 1)
        self.assertNotEqual(parent.source_session_id, child.source_session_id)
        self.assertEqual(child.parent_self_state_record_id, parent.self_state_record_id)
        self.assertEqual(child.parent_self_state_sha256, parent.self_state_sha256)
        self.assertEqual(child.transition_provenance_ref, transition.transition_id)

    def test_forbidden_content_is_rejected_by_record_constructor(self) -> None:
        parent, _child, _transition, _validation = self._chain()
        for field in (
            "raw_perception_embedded",
            "world_facts_embedded",
            "memory_content_embedded",
            "semantic_history_embedded",
            "output_content_embedded",
        ):
            with self.subTest(field=field), self.assertRaises(ValueError):
                replace(parent, **{field: True})

    def test_forbidden_authority_is_rejected_by_record_constructor(self) -> None:
        parent, _child, _transition, _validation = self._chain()
        for field in (
            "cross_session_recovery_authority",
            "active_head_selection_authority",
            "runtime_behavior_influence_authority",
            "drive_signal_authority",
            "memory_write_authority",
            "perception_control_authority",
            "action_selection_authority",
            "output_authority",
            "thought_engine_authority",
        ):
            with self.subTest(field=field), self.assertRaises(ValueError):
                replace(parent, **{field: True})

    def test_unknown_field_same_session_and_hash_tamper_are_rejected(self) -> None:
        parent, child, _transition, _validation = self._chain()
        with self.assertRaises(ValueError):
            replace(
                parent,
                persistent_field_names=parent.persistent_field_names + ("world_model",),
            )
        with self.assertRaises(ValueError):
            build_successor_self_state_records(
                parent=parent,
                contract=self.contract,
                source_session_id=parent.source_session_id,
            )
        tampered = child.to_dict()
        tampered["parent_self_state_sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            PersistentSelfStateRecord.from_dict(tampered)

    def test_store_is_append_only_has_no_active_head_and_rejects_fork(self) -> None:
        parent, child, transition, validation = self._chain()
        with TemporaryDirectory() as temp:
            store = PersistentSelfStateStore(temp)
            store.append_generic_record(
                "persistent_self_state_representation_contracts", self.contract
            )
            store.append_lineage_chain(
                parent=parent,
                child=child,
                transition=transition,
                validation=validation,
            )
            integrity = store.audit_integrity()
            self.assertTrue(integrity["valid"])
            self.assertFalse(integrity["active_head_present"])
            self.assertFalse(integrity["recovery_table_present"])
            for method in (
                store.update,
                store.delete,
                store.replace,
                store.recover,
                store.select_active_head,
            ):
                with self.assertRaises(TypeError):
                    method()
            fork_child, fork_transition = build_successor_self_state_records(
                parent=parent,
                contract=self.contract,
                source_session_id="session-fork",
            )
            fork_validation = build_self_state_lineage_validation_record(
                parent=parent,
                child=fork_child,
                transition=fork_transition,
            )
            with self.assertRaises(ValueError):
                store.append_lineage_chain(
                    parent=parent,
                    child=fork_child,
                    transition=fork_transition,
                    validation=fork_validation,
                )
            self.assertEqual(store.count("persistent_self_state_records"), 2)

    def test_boundary_controls_are_real_rejections(self) -> None:
        parent, child, transition, validation = self._chain()
        with TemporaryDirectory() as temp:
            store = PersistentSelfStateStore(temp)
            store.append_lineage_chain(
                parent=parent,
                child=child,
                transition=transition,
                validation=validation,
            )
            controls = run_package_133_boundary_controls(
                contract=self.contract,
                parent=parent,
                child=child,
                transition=transition,
                validation=validation,
                store=store,
            )
            self.assertTrue(controls.controls_passed)
            self.assertEqual(controls.passed_count, 20)

    def test_state_store_rejects_private_absolute_paths(self) -> None:
        record = build_state_like_structure_inventory(self.repo_root)[0]
        payload = record.to_dict()
        payload["source_record_refs"] = [r"C:\private\state.json"]
        with TemporaryDirectory() as temp:
            store = PersistentSelfStateStore(temp)
            with self.assertRaises(ValueError):
                store.append_generic_record(
                    "state_like_structure_boundary_records", payload
                )

    def test_create_chain_is_rerunnable_without_a_second_lineage(self) -> None:
        with TemporaryDirectory() as temp:
            first = create_package_133_representation_chain(
                ashl_root=self.repo_root,
                state_dir=temp,
                parent_session_id="session-a",
                child_session_id="session-b",
            )
            second = create_package_133_representation_chain(
                ashl_root=self.repo_root,
                state_dir=temp,
                parent_session_id="session-a",
                child_session_id="session-b",
            )
            self.assertFalse(first["existing_chain_reused"])
            self.assertTrue(second["existing_chain_reused"])
            self.assertEqual(first["parent"]["self_state_record_id"], second["parent"]["self_state_record_id"])

    def test_end_to_end_audit_passes_with_package_132_evidence_and_fresh_receipt(self) -> None:
        with TemporaryDirectory() as temp:
            root = Path(temp)
            package_132 = root / "package132"
            package_133 = root / "package133"
            self._write_package_132_fixture(package_132)
            create_package_133_representation_chain(
                ashl_root=self.repo_root,
                state_dir=package_133,
                parent_session_id="session-a",
                child_session_id="session-b",
            )
            store = PersistentSelfStateStore(package_133)
            receipt = self._passing_regression_receipt()
            store.append_generic_record("package_133_regression_receipts", receipt)
            before = self._tree_hash(package_132)
            audit = audit_package_133_cross_session_self_state_schema(
                ashl_root=self.repo_root,
                state_dir=package_133,
                package_132_state_dir=package_132,
                append=True,
            )
            self.assertEqual(audit.audit_status, PASS_STATUS)
            self.assertEqual(audit.failure_reasons, tuple())
            self.assertTrue(audit.parent_child_lineage_verified)
            self.assertTrue(audit.state_like_inventory_verified)
            self.assertTrue(audit.append_only_store_verified)
            self.assertFalse(audit.cross_session_recovery_implemented)
            self.assertFalse(audit.runtime_behavior_influence_created)
            self.assertFalse(audit.persistent_self_claimed)
            self.assertEqual(before, self._tree_hash(package_132))

    def test_audit_without_fresh_regression_receipt_is_blocked(self) -> None:
        with TemporaryDirectory() as temp:
            root = Path(temp)
            package_132 = root / "package132"
            package_133 = root / "package133"
            self._write_package_132_fixture(package_132)
            create_package_133_representation_chain(
                ashl_root=self.repo_root,
                state_dir=package_133,
                parent_session_id="session-a",
                child_session_id="session-b",
            )
            audit = audit_package_133_cross_session_self_state_schema(
                ashl_root=self.repo_root,
                state_dir=package_133,
                package_132_state_dir=package_132,
                append=False,
            )
            self.assertNotEqual(audit.audit_status, PASS_STATUS)
            self.assertIn("fresh_regressions", audit.failure_reasons)

    def test_cli_schema_chain_and_show_lineage(self) -> None:
        with TemporaryDirectory() as temp:
            output = io.StringIO()
            with redirect_stdout(output):
                result = main(
                    [
                        "synthetic-smoke",
                        "--ashl-root",
                        str(self.repo_root),
                        "--state-dir",
                        temp,
                    ]
                )
            self.assertEqual(result, 0)
            self.assertIn("representation-only", output.getvalue())
            output = io.StringIO()
            with redirect_stdout(output):
                result = main(["show-lineage", "--state-dir", temp])
            self.assertEqual(result, 0)
            self.assertIn("persistent_self_state", output.getvalue())

    def _passing_regression_receipt(self) -> Package133RegressionReceipt:
        return Package133RegressionReceipt(
            regression_receipt_id="package_133_regressions:test_only",
            schema_version=REGRESSION_SCHEMA_VERSION,
            created_at="2026-08-07T00:04:00+00:00",
            baseline_commit=BASELINE_COMMIT,
            source_head=BASELINE_COMMIT,
            command_results=(("test_only_explicit_fixture", 0, "0" * 64),),
            targeted_package_133_passed=True,
            state_engine_regressions_passed=True,
            package_132_regressions_passed=True,
            full_v1_discover_passed=True,
            compileall_passed=True,
            git_diff_check_passed=True,
            pycache_redirected_outside_repo=True,
            fresh_regressions_passed=True,
        )

    @staticmethod
    def _write_package_132_fixture(state_dir: Path) -> None:
        database = (
            state_dir
            / "package_132_perception_attention_milestone_v0"
            / "package_132.sqlite3"
        )
        database.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "audit_id": "package_132_audit:test_only",
            "audit_status": PACKAGE_132_PASS_STATUS,
            "perception_line_status": "perception_capability_construction_line_frozen_after_package_132",
            "persistent_self_state_created": False,
            "new_internal_action_created": False,
            "failure_reasons": [],
        }
        with closing(sqlite3.connect(database)) as connection:
            connection.execute(
                """
                CREATE TABLE package_132_audits (
                    row_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    payload_json TEXT NOT NULL,
                    payload_sha256 TEXT NOT NULL
                )
                """
            )
            connection.execute(
                "INSERT INTO package_132_audits (payload_json, payload_sha256) VALUES (?, ?)",
                (canonical_json(payload), sha256_payload(payload)),
            )
            connection.commit()

    @staticmethod
    def _tree_hash(root: Path) -> str:
        entries = []
        for path in sorted(root.rglob("*")):
            if path.is_file():
                entries.append((path.relative_to(root).as_posix(), path.read_bytes()))
        return sha256_payload(
            [(relative, sha256_payload(list(data))) for relative, data in entries]
        )


if __name__ == "__main__":
    unittest.main()
