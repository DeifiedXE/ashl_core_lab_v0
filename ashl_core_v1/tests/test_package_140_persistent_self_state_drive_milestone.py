from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import tempfile
import unittest
from contextlib import closing
from dataclasses import replace
from pathlib import Path

from ashl_core_v1.runtime.host_sensor_types import sha256_payload, utc_now
from ashl_core_v1.state.package_140_persistent_self_state_drive_milestone_audit import (
    audit_package_140_persistent_self_state_and_drive_milestone,
    load_authoritative_capability_contract,
    run_package_140_boundary_controls,
    validate_no_runtime_capability_delta,
    validate_package_140_audit_status,
    validate_source_snapshot,
    verify_package_140_evidence_unchanged,
)
from ashl_core_v1.state.package_140_persistent_self_state_drive_milestone_store import (
    Package140PersistentSelfStateDriveMilestoneStore,
)
from ashl_core_v1.state.package_140_persistent_self_state_drive_sources import (
    ReadOnlyEvidenceDatabase,
    load_package_140_sources_read_only,
)
from ashl_core_v1.state.persistent_self_state_drive_closure_types import (
    ABSENT_CAPABILITIES,
    AUTHORITY_BINDINGS,
    BASELINE_COMMIT,
    CONTROL_NAMES,
    PASS_STATUS,
    REGRESSION_SCHEMA_VERSION,
    Package140RegressionReceipt,
    build_hashed_record,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def _official_roots() -> dict[str, Path]:
    base = Path(os.environ.get("ASHL_EXTERNAL_STATE_ROOT", r"F:\ashl_external_state"))
    values = {
        "133": base / "package133_official_20260807",
        "134": base / "package134_official_20260807",
        "135": base / "package135_official_20260807",
        "136": base / "package136_official_20260807",
        "137": base / "package137_official_20260807",
        "138": base / "package138_official_20260808",
        "139": base / "package139_official_20260810",
    }
    return values if all(path.is_dir() for path in values.values()) else {}


class Package140ContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = load_authoritative_capability_contract(REPO_ROOT)

    def test_authority_ownership_is_exact(self) -> None:
        self.assertEqual(self.contract.authority_bindings, AUTHORITY_BINDINGS)
        self.assertEqual(tuple(item[0] for item in AUTHORITY_BINDINGS), ("133", "134", "135", "136", "137", "138", "139"))
        self.assertTrue(self.contract.authority_line_frozen)
        self.assertTrue(self.contract.stable_consumer_boundary)

    def test_production_consumers_remain_empty(self) -> None:
        self.assertEqual(self.contract.production_drive_consumer_count, 0)
        self.assertEqual(self.contract.production_readback_consumer_count, 0)
        self.assertIn("production_drive_modulation_consumer", ABSENT_CAPABILITIES)
        self.assertIn("production_self_state_readback_consumer", ABSENT_CAPABILITIES)

    def test_structural_identity_is_not_psychological_continuity(self) -> None:
        self.assertFalse(self.contract.structural_identity_is_psychological_continuity)
        self.assertIn("complete_psychological_continuity", self.contract.absent_capabilities)
        self.assertIn("semantic_identity", self.contract.absent_capabilities)
        self.assertIn("autobiographical_self_state", self.contract.absent_capabilities)

    def test_package_141_can_consume_but_not_expand(self) -> None:
        self.assertTrue(self.contract.package_141_plus_may_consume_existing_contracts)
        self.assertFalse(self.contract.package_141_plus_may_bypass_or_expand_authorities)
        self.assertTrue(self.contract.new_authority_package_required_for_contract_expansion)
        self.assertEqual(self.contract.next_core_package, "141")
        self.assertEqual(self.contract.next_core_line, "package_141_to_148_bounded_thought_engine")

    def test_contract_rejects_authority_and_consumer_expansion(self) -> None:
        with self.assertRaises(ValueError):
            replace(self.contract, authority_bindings=self.contract.authority_bindings[:-1])
        with self.assertRaises(ValueError):
            replace(self.contract, production_drive_consumer_count=1)
        with self.assertRaises(ValueError):
            replace(self.contract, production_readback_consumer_count=1)
        with self.assertRaises(ValueError):
            replace(self.contract, package_141_plus_may_bypass_or_expand_authorities=True)

    def test_no_fork_rules_are_not_optional(self) -> None:
        self.assertIn("selected_ancestor_blocks_package_137_mutation", self.contract.no_fork_rules)
        self.assertIn("selected_ancestor_blocks_normal_package_134_recovery", self.contract.no_fork_rules)
        self.assertIn("only_separately_authorized_exact_roll_forward_to_preserved_descendant_is_allowed", self.contract.no_fork_rules)
        with self.assertRaises(ValueError):
            replace(self.contract, no_fork_rules=self.contract.no_fork_rules[:-1])

    def test_boundary_controls_execute_real_validators(self) -> None:
        result = run_package_140_boundary_controls(self.contract)
        self.assertTrue(result.controls_passed)
        self.assertEqual(result.passed_count, len(CONTROL_NAMES))
        self.assertEqual(result.passed_control_names, CONTROL_NAMES)

    def test_direct_validation_guards(self) -> None:
        validate_source_snapshot("a" * 64, "a" * 64)
        with self.assertRaises(ValueError):
            validate_source_snapshot("a" * 64, "b" * 64)
        validate_package_140_audit_status(PASS_STATUS)
        with self.assertRaises(ValueError):
            validate_package_140_audit_status("completed")
        validate_no_runtime_capability_delta(
            runtime_capability_created=False,
            action_created=False,
            production_consumer_created=False,
        )
        with self.assertRaises(ValueError):
            validate_no_runtime_capability_delta(
                runtime_capability_created=True,
                action_created=False,
                production_consumer_created=False,
            )


class Package140StoreAndReaderTests(unittest.TestCase):
    def test_store_is_append_only_and_contains_no_authority_tables(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            store = Package140PersistentSelfStateDriveMilestoneStore(temp)
            control = run_package_140_boundary_controls(
                load_authoritative_capability_contract(REPO_ROOT)
            )
            store.append_once("package_140_boundary_control_results", control)
            store.append_once("package_140_boundary_control_results", control)
            self.assertEqual(store.count("package_140_boundary_control_results"), 1)
            with self.assertRaises(TypeError):
                store.update()
            with self.assertRaises(TypeError):
                store.delete()
            with self.assertRaises(TypeError):
                store.replace()
            integrity = store.audit_integrity()
            self.assertTrue(integrity["valid"])
            self.assertFalse(integrity["authority_table_present"])

    def test_query_only_reader_verifies_payload_hash(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            database = Path(temp) / "evidence.sqlite3"
            payload = {"record_id": "record:1", "value": 3}
            with closing(sqlite3.connect(database)) as connection:
                connection.execute(
                    "CREATE TABLE evidence (payload_json TEXT, payload_sha256 TEXT)"
                )
                connection.execute(
                    "INSERT INTO evidence VALUES (?, ?)",
                    (json.dumps(payload), sha256_payload(payload)),
                )
                connection.commit()
            reader = ReadOnlyEvidenceDatabase(database)
            self.assertTrue(reader.integrity_valid())
            self.assertEqual(reader.list_payloads("evidence"), (payload,))
            before = database.stat().st_mtime_ns
            reader.load_and_verify_all_payloads()
            self.assertEqual(database.stat().st_mtime_ns, before)

    def test_query_only_reader_rejects_corrupt_payload_hash(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            database = Path(temp) / "evidence.sqlite3"
            with closing(sqlite3.connect(database)) as connection:
                connection.execute(
                    "CREATE TABLE evidence (payload_json TEXT, payload_sha256 TEXT)"
                )
                connection.execute(
                    "INSERT INTO evidence VALUES (?, ?)",
                    (json.dumps({"record_id": "record:1"}), "0" * 64),
                )
                connection.commit()
            with self.assertRaises(RuntimeError):
                ReadOnlyEvidenceDatabase(database).list_payloads("evidence")


@unittest.skipUnless(_official_roots(), "Package 133-139 official external evidence is unavailable")
class Package140OfficialEvidenceTests(unittest.TestCase):
    def test_read_only_end_to_end_milestone_revalidation(self) -> None:
        roots = _official_roots()
        source_bundle = load_package_140_sources_read_only(roots)
        before = {
            package_id: item.snapshot_after.tree_sha256
            for package_id, item in source_bundle.packages.items()
        }
        self.assertTrue(all(item.database_integrity_valid for item in source_bundle.packages.values()))
        self.assertTrue(all(item.all_payload_hashes_verified for item in source_bundle.packages.values()))
        self.assertTrue(all(item.snapshot_before == item.snapshot_after for item in source_bundle.packages.values()))

        with tempfile.TemporaryDirectory() as temp:
            store = Package140PersistentSelfStateDriveMilestoneStore(temp)
            regression_payload = {
                "regression_receipt_id": "",
                "regression_receipt_sha256": "",
                "schema_version": REGRESSION_SCHEMA_VERSION,
                "created_at": utc_now(),
                "baseline_commit": BASELINE_COMMIT,
                "source_head": subprocess.run(
                    ("git", "rev-parse", "HEAD"),
                    cwd=REPO_ROOT,
                    capture_output=True,
                    text=True,
                    check=True,
                ).stdout.strip(),
                "command_results": (
                    ("targeted_package_140", 0, "a" * 64),
                    ("package_133_to_139", 0, "b" * 64),
                    ("full_v1_discover", 0, "c" * 64),
                    ("compileall", 0, "d" * 64),
                    ("git_diff_check", 0, "e" * 64),
                    ("repository_pollution_scan", 0, "f" * 64),
                ),
                "targeted_package_140_passed": True,
                "package_133_to_139_regressions_passed": True,
                "full_v1_discover_passed": True,
                "compileall_passed": True,
                "git_diff_check_passed": True,
                "repository_pollution_absent": True,
                "pycache_redirected_outside_repo": True,
                "fresh_regressions_passed": True,
                "source_record_refs": ("test_only:explicit_regression_fixture",),
            }
            receipt = build_hashed_record(
                Package140RegressionReceipt,
                regression_payload,
                id_field="regression_receipt_id",
                hash_field="regression_receipt_sha256",
                prefix="package_140_regressions",
            )
            store.append_once("package_140_regression_receipts", receipt)
            audit = audit_package_140_persistent_self_state_and_drive_milestone(
                ashl_root=REPO_ROOT,
                state_dir=temp,
                package_state_dirs=roots,
                append=True,
            )
            self.assertEqual(audit.audit_status, PASS_STATUS)
            self.assertEqual(audit.cross_package_lineage_record_count, 12)
            self.assertEqual(audit.production_drive_consumer_count, 0)
            self.assertEqual(audit.production_readback_consumer_count, 0)
            self.assertTrue(audit.package_139_no_fork_rule_verified)
            self.assertTrue(audit.final_active_head_matches_canonical_leaf)
            self.assertFalse(audit.complete_psychological_continuity_claimed)
            self.assertFalse(audit.semantic_identity_created)
            self.assertFalse(audit.thought_engine_created)
            self.assertFalse(audit.automatic_action_created)
            self.assertFalse(audit.output_authority_created)
            recheck = verify_package_140_evidence_unchanged(
                state_dir=temp,
                package_state_dirs=roots,
            )
            self.assertTrue(recheck["all_sources_unchanged"])
        after = load_package_140_sources_read_only(roots)
        self.assertEqual(
            before,
            {
                package_id: item.snapshot_after.tree_sha256
                for package_id, item in after.packages.items()
            },
        )


class Package140RepositoryBoundaryTests(unittest.TestCase):
    def test_no_package_140_runtime_or_action_module_exists(self) -> None:
        self.assertFalse(tuple((REPO_ROOT / "ashl_core_v1" / "runtime").glob("*package_140*")))
        text = (REPO_ROOT / "ashl_core_v1" / "host_body" / "host_body_internal_action_choice.py").read_text(encoding="utf-8")
        self.assertNotIn("package_140", text)

    def test_registry_and_route_close_at_140_then_enter_141(self) -> None:
        registry = json.loads(
            (REPO_ROOT / "ashl_core_v1" / "docs" / "reference" / "package_number_registry_v0.json").read_text(encoding="utf-8")
        )
        self.assertEqual(registry["current_package_id"], "144")
        self.assertEqual(registry["package_status"]["140"], "completed")
        self.assertEqual(registry["package_status"]["141"], "completed")
        self.assertEqual(registry["package_status"]["142"], "completed")
        self.assertEqual(registry["package_status"]["143"], "completed")
        self.assertEqual(registry["package_status"]["144"], "completed")
        self.assertEqual(registry["package_status"]["145"], "next_critical_path")
        self.assertIn("140", registry["completed_package_ids"])
        self.assertNotIn("140", registry["future_package_ids"])
        route = (REPO_ROOT / "ashl_core_v1" / "docs" / "reference" / "package_123_to_daily_runtime_revised_route_v0.md").read_text(encoding="utf-8")
        self.assertIn("Package 140 is the frozen", route)
        self.assertIn("Package 145 is next", route)
        self.assertIn("Package 132A and Package 140A do not exist", route)


if __name__ == "__main__":
    unittest.main()
