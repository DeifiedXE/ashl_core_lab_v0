from __future__ import annotations

import ast
import io
import json
import unittest
from contextlib import redirect_stdout
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory

from ashl_core_v1.endocrine.drive_modulation_consumer_inventory import (
    build_drive_modulation_consumer_inventory,
)
from ashl_core_v1.endocrine.drive_modulation_runtime import (
    AUDIT_ONLY_CONSUMER_ID,
    decide_drive_modulation,
    run_real_same_session_drive_modulation,
)
from ashl_core_v1.endocrine.drive_modulation_types import (
    BASELINE_COMMIT,
    PASS_STATUS,
    REGRESSION_SCHEMA_VERSION,
    DriveModulationApplicationRecord,
    Package136RegressionReceipt,
)
from ashl_core_v1.endocrine.package_135_drive_signal_trace_audit import (
    audit_package_135_drive_signal_trace_separation,
)
from ashl_core_v1.endocrine.package_135_drive_signal_trace_controls import (
    run_package_135_drive_trace_controls,
)
from ashl_core_v1.endocrine.package_135_drive_signal_trace_store import (
    Package135DriveSignalTraceStore,
)
from ashl_core_v1.endocrine.package_136_drive_modulation_audit import (
    audit_package_136_same_session_drive_modulation,
)
from ashl_core_v1.endocrine.package_136_drive_modulation_cli import main
from ashl_core_v1.endocrine.package_136_drive_modulation_controls import (
    run_package_136_drive_modulation_controls,
)
from ashl_core_v1.endocrine.package_136_drive_modulation_store import (
    Package136DriveModulationStore,
    package_136_store_path,
)
from ashl_core_v1.endocrine.package_136_package_135_source import (
    load_package_136_sources_read_only,
)
from ashl_core_v1.runtime.host_sensor_types import sha256_payload
from ashl_core_v1.state.package_133_cross_session_self_state_schema_audit import (
    create_package_133_representation_chain,
)
from ashl_core_v1.state.package_134_persistent_session_recovery_audit import (
    audit_package_134_persistent_session_recovery,
)
from ashl_core_v1.state.package_134_persistent_session_recovery_controls import (
    run_package_134_recovery_controls,
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
    BASELINE_COMMIT as PACKAGE_134_BASELINE_COMMIT,
    PASS_STATUS as PACKAGE_134_PASS_STATUS,
    REGRESSION_SCHEMA_VERSION as PACKAGE_134_REGRESSION_SCHEMA_VERSION,
    Package134RegressionReceipt,
)
from ashl_core_v1.endocrine.drive_signal_trace_runtime import (
    run_real_drive_signal_trace_separation,
)
from ashl_core_v1.endocrine.drive_signal_trace_types import (
    BASELINE_COMMIT as PACKAGE_135_BASELINE_COMMIT,
    PASS_STATUS as PACKAGE_135_PASS_STATUS,
    REGRESSION_SCHEMA_VERSION as PACKAGE_135_REGRESSION_SCHEMA_VERSION,
    Package135RegressionReceipt,
)


class Package136SameSessionDriveModulationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repo_root = Path(__file__).resolve().parents[2]
        cls.temporary = TemporaryDirectory()
        cls.root = Path(cls.temporary.name)
        cls.package_133_root = cls.root / "package133"
        cls.package_134_root = cls.root / "package134"
        cls.package_135_root = cls.root / "package135"
        cls.package_136_root = cls.root / "package136"
        cls._write_package_133_fixture(cls.package_133_root)
        run_real_fresh_process_recovery(
            ashl_root=cls.repo_root,
            package_133_state_dir=cls.package_133_root,
            state_dir=cls.package_134_root,
            allow_session_recovery=True,
        )
        run_package_134_recovery_controls(
            ashl_root=cls.repo_root,
            package_133_state_dir=cls.package_133_root,
            state_dir=cls.package_134_root,
            append=True,
        )
        PersistentSessionRecoveryStore(cls.package_134_root).append_record(
            "package_134_regression_receipts", cls._package_134_regression_receipt()
        )
        audit_134 = audit_package_134_persistent_session_recovery(
            ashl_root=cls.repo_root,
            package_133_state_dir=cls.package_133_root,
            state_dir=cls.package_134_root,
            append=True,
        )
        if audit_134.audit_status != PACKAGE_134_PASS_STATUS:
            raise AssertionError(audit_134.failure_reasons)
        run_real_drive_signal_trace_separation(
            ashl_root=cls.repo_root,
            package_133_state_dir=cls.package_133_root,
            package_134_state_dir=cls.package_134_root,
            state_dir=cls.package_135_root,
            allow_drive_trace_observation=True,
        )
        run_package_135_drive_trace_controls(state_dir=cls.package_135_root)
        Package135DriveSignalTraceStore(cls.package_135_root).append_record(
            "package_135_regression_receipts", cls._package_135_regression_receipt()
        )
        audit_135 = audit_package_135_drive_signal_trace_separation(
            ashl_root=cls.repo_root,
            package_133_state_dir=cls.package_133_root,
            package_134_state_dir=cls.package_134_root,
            state_dir=cls.package_135_root,
            append=True,
        )
        if audit_135.audit_status != PACKAGE_135_PASS_STATUS:
            raise AssertionError(audit_135.failure_reasons)
        cls.real_result = run_real_same_session_drive_modulation(
            ashl_root=cls.repo_root,
            package_133_state_dir=cls.package_133_root,
            package_134_state_dir=cls.package_134_root,
            package_135_state_dir=cls.package_135_root,
            state_dir=cls.package_136_root,
            allow_same_session_drive_modulation=True,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_consumer_inventory_finds_no_legal_production_consumer(self) -> None:
        inventory = build_drive_modulation_consumer_inventory(self.repo_root)
        self.assertEqual(len(inventory), 14)
        self.assertFalse(any(item.production_eligible for item in inventory))
        audit_only = tuple(item for item in inventory if item.audit_only_eligible)
        self.assertEqual(len(audit_only), 1)
        self.assertEqual(audit_only[0].consumer_surface_id, AUDIT_ONLY_CONSUMER_ID)
        classifications = {item.classification for item in inventory}
        self.assertIn("forbidden_perception_lifecycle_surface", classifications)
        self.assertIn("forbidden_attention_surface", classifications)
        self.assertIn("forbidden_candidate_ordering_surface", classifications)
        self.assertIn("derived_status_not_a_modulation_consumer", classifications)

    def test_package_135_is_read_only_signal_authority(self) -> None:
        source = self._source()
        self.assertEqual(source.package_135_audit["audit_status"], PACKAGE_135_PASS_STATUS)
        self.assertEqual(
            source.package_135_contract.authority_owner,
            "package_135_anonymous_regulatory_observation_trace_only",
        )
        self.assertTrue(source.source_binding.source_opened_read_only)
        self.assertFalse(source.source_binding.source_trace_mutation_allowed)
        self.assertFalse(source.source_binding.source_trace_recovery_allowed)
        self.assertEqual(source.selected_trace.sequence_index, 1)
        self.assertEqual(source.fresh_session_root_trace.sequence_index, 0)

    def test_contract_and_allowlist_are_bounded_and_production_empty(self) -> None:
        contract = self._store().list_payloads("same_session_drive_modulation_contracts")[0]
        allowlist = self._store().list_payloads("drive_modulation_consumer_allowlists")[0]
        self.assertTrue(contract["same_session_only"])
        self.assertTrue(contract["read_only_signal_consumption"])
        self.assertTrue(contract["fail_to_neutral_required"])
        self.assertEqual(contract["maximum_absolute_offset"], 0.2)
        self.assertEqual(contract["maximum_delta_per_application"], 0.1)
        self.assertEqual(allowlist["production_consumer_ids"], [])
        self.assertTrue(allowlist["production_allowlist_empty"])
        self.assertEqual(allowlist["audit_only_consumer_ids"], [AUDIT_ONLY_CONSUMER_ID])

    def test_authorization_is_exact_same_session_single_use(self) -> None:
        authorization = self._store().list_payloads(
            "same_session_drive_modulation_authorizations"
        )[0]
        source = self._source()
        self.assertEqual(authorization["runtime_session_id"], source.selected_trace.runtime_session_id)
        self.assertEqual(authorization["signal_lineage_id"], source.selected_trace.signal_lineage_id)
        self.assertEqual(authorization["signal_trace_sha256"], source.selected_trace.signal_trace_sha256)
        self.assertTrue(authorization["single_application_only"])
        self.assertFalse(authorization["cross_session_carry_allowed"])

    def test_real_derivation_clamps_delta_and_never_mutates_trace(self) -> None:
        derivation = self._store().list_payloads("drive_modulation_derivations")[0]
        application = self._store().list_payloads("drive_modulation_applications")[0]
        self.assertEqual(derivation["raw_level_offset"], 0.125)
        self.assertEqual(derivation["effective_offset"], 0.1)
        self.assertTrue(derivation["delta_clamp_applied"])
        self.assertTrue(derivation["source_trace_read_only"])
        self.assertFalse(derivation["source_trace_mutated"])
        self.assertTrue(application["audit_only_consumer"])
        self.assertFalse(application["production_consumer"])
        self.assertFalse(application["cross_session_persistence_authority"])

    def test_counterfactual_only_changes_audit_scalar(self) -> None:
        comparison = self._store().list_payloads(
            "drive_modulation_counterfactual_comparisons"
        )[0]
        self.assertEqual(comparison["differing_paths"], ["audit_only_regulatory_offset"])
        for field in (
            "hard_safety_equivalent",
            "teacher_authority_equivalent",
            "purpose_scope_equivalent",
            "candidate_set_equivalent",
            "selected_action_equivalent",
            "memory_equivalent",
            "perception_history_equivalent",
            "self_state_equivalent",
            "output_equivalent",
            "recovery_result_equivalent",
            "production_behavior_equivalent",
        ):
            self.assertTrue(comparison[field])

    def test_session_end_and_fresh_process_are_neutral(self) -> None:
        neutralizations = self._store().list_payloads("drive_modulation_neutralizations")
        self.assertEqual(
            {item["reason"] for item in neutralizations},
            {"session_end", "fresh_session_start_after_structural_recovery"},
        )
        self.assertTrue(all(item["neutral_baseline_restored"] for item in neutralizations))
        self.assertTrue(all(item["final_effective_offset"] == 0.0 for item in neutralizations))
        neutrality = self._store().list_payloads(
            "drive_modulation_cross_session_neutrality"
        )[0]
        self.assertTrue(neutrality["process_b_started_neutral"])
        self.assertTrue(neutrality["package_135_session_b_trace_is_fresh_root"])
        self.assertFalse(neutrality["package_134_drive_state_restored"])
        self.assertFalse(neutrality["authorization_carried"])
        self.assertFalse(neutrality["application_carried"])
        self.assertFalse(neutrality["effective_offset_carried"])

    def test_real_workers_are_distinct_and_sequential(self) -> None:
        process_a = self.real_result["process_a"]
        process_b = self.real_result["process_b"]
        self.assertNotEqual(process_a["operating_system_process_id"], process_b["operating_system_process_id"])
        self.assertNotEqual(process_a["process_instance_id"], process_b["process_instance_id"])
        self.assertLess(process_a["ended_monotonic_ns"], process_b["started_monotonic_ns"])
        self.assertEqual(process_a["final_effective_offset"], 0.0)
        self.assertEqual(process_b["final_effective_offset"], 0.0)

    def test_policy_missing_authorization_is_neutral(self) -> None:
        contract = self._typed_contract()
        allowlist = self._typed_allowlist()
        source = self._source()
        decision, _ = decide_drive_modulation(
            contract=contract,
            allowlist=allowlist,
            authorization=None,
            signal_trace_payload=source.fresh_session_root_trace,
            runtime_session_id=source.fresh_session_root_trace.runtime_session_id,
            consumer_id=AUDIT_ONLY_CONSUMER_ID,
            evaluated_at_monotonic_ns=1,
        )
        self.assertEqual(decision.decision, "neutral_authorization_missing")
        self.assertTrue(decision.fail_to_neutral)

    def test_semantic_and_runtime_authority_injection_is_rejected(self) -> None:
        application = self._typed_application()
        for change in (
            {"semantic_label": "fear"},
            {"purpose_ref": "new-purpose"},
            {"candidate_ordering_authority": True},
            {"selected_action_authority": True},
            {"memory_write_authority": True},
            {"self_state_write_authority": True},
            {"output_authority": True},
        ):
            with self.assertRaises(ValueError):
                replace(application, **change)

    def test_store_is_append_only_and_has_no_recovery_or_active_head(self) -> None:
        store = self._store()
        integrity = store.audit_integrity()
        self.assertTrue(integrity["valid"])
        self.assertFalse(integrity["active_modulation_present"])
        self.assertFalse(integrity["cross_session_recovery_table_present"])
        self.assertFalse(integrity["production_consumer_state_present"])
        for method in (
            store.update,
            store.delete,
            store.select_active_modulation,
            store.recover_modulation,
        ):
            with self.assertRaises(TypeError):
                method()

    def test_all_controls_are_real_rejections_or_neutral_fallbacks(self) -> None:
        result = run_package_136_drive_modulation_controls(
            package_133_state_dir=self.package_133_root,
            package_134_state_dir=self.package_134_root,
            package_135_state_dir=self.package_135_root,
            state_dir=self.package_136_root,
        )
        self.assertTrue(result.controls_passed)
        self.assertEqual(result.passed_count, 18)

    def test_package_135_reaudit_accepts_safe_downstream_package(self) -> None:
        audit = audit_package_135_drive_signal_trace_separation(
            ashl_root=self.repo_root,
            package_133_state_dir=self.package_133_root,
            package_134_state_dir=self.package_134_root,
            state_dir=self.package_135_root,
            append=False,
        )
        self.assertEqual(audit.audit_status, PACKAGE_135_PASS_STATUS)
        self.assertTrue(audit.package_136_implemented)
        self.assertFalse(audit.package_136_modulation_authorized)

    def test_cli_requires_explicit_modulation_authorization(self) -> None:
        with TemporaryDirectory() as directory:
            output = io.StringIO()
            with redirect_stdout(output):
                result = main(
                    [
                        "run-real-counterfactual",
                        "--ashl-root",
                        str(self.repo_root),
                        "--package-133-state-dir",
                        str(self.package_133_root),
                        "--package-134-state-dir",
                        str(self.package_134_root),
                        "--package-135-state-dir",
                        str(self.package_135_root),
                        "--state-dir",
                        directory,
                    ]
                )
            self.assertEqual(result, 2)
            self.assertIn("blocked_same_session_drive_modulation_authorization_missing", output.getvalue())
            self.assertFalse(package_136_store_path(directory).exists())

    def test_final_audit_blocks_without_fresh_regressions(self) -> None:
        with TemporaryDirectory() as directory:
            self._run_package_136(directory)
            run_package_136_drive_modulation_controls(
                package_133_state_dir=self.package_133_root,
                package_134_state_dir=self.package_134_root,
                package_135_state_dir=self.package_135_root,
                state_dir=directory,
            )
            audit = audit_package_136_same_session_drive_modulation(
                ashl_root=self.repo_root,
                package_133_state_dir=self.package_133_root,
                package_134_state_dir=self.package_134_root,
                package_135_state_dir=self.package_135_root,
                state_dir=directory,
                append=False,
            )
            self.assertNotEqual(audit.audit_status, PASS_STATUS)
            self.assertIn("regressions", audit.failure_reasons)

    def test_final_audit_passes_with_evidence_controls_and_regressions(self) -> None:
        with TemporaryDirectory() as directory:
            self._run_package_136(directory)
            run_package_136_drive_modulation_controls(
                package_133_state_dir=self.package_133_root,
                package_134_state_dir=self.package_134_root,
                package_135_state_dir=self.package_135_root,
                state_dir=directory,
            )
            Package136DriveModulationStore(directory).append_record(
                "package_136_regression_receipts", self._package_136_regression_receipt()
            )
            audit = audit_package_136_same_session_drive_modulation(
                ashl_root=self.repo_root,
                package_133_state_dir=self.package_133_root,
                package_134_state_dir=self.package_134_root,
                package_135_state_dir=self.package_135_root,
                state_dir=directory,
            )
            self.assertEqual(audit.audit_status, PASS_STATUS)
            self.assertEqual(audit.failure_reasons, tuple())
            self.assertEqual(audit.production_consumer_count, 0)
            self.assertTrue(audit.cross_session_neutrality_verified)
            self.assertFalse(audit.production_runtime_behavior_changed)
            self.assertFalse(audit.package_137_implemented)

    def test_registry_and_route_advance_to_package_137(self) -> None:
        registry = json.loads(
            (
                self.repo_root
                / "ashl_core_v1/docs/reference/package_number_registry_v0.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(registry["current_package_id"], "136")
        self.assertIn("136", registry["completed_package_ids"])
        self.assertNotIn("136", registry["future_package_ids"])
        self.assertEqual(registry["package_status"]["136"], "completed")
        self.assertEqual(registry["package_status"]["137"], "next_critical_path")
        digest = sha256_payload(
            {
                "current": registry["current_package_id"],
                "completed": tuple(registry["completed_package_ids"]),
                "future": tuple(registry["future_package_ids"]),
                "duplicates": tuple(registry["duplicate_package_ids"]),
            }
        )
        self.assertEqual(registry["registry_sha256"], digest)
        route = (
            self.repo_root
            / "ashl_core_v1/docs/reference/package_123_to_daily_runtime_revised_route_v0.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Package 136 is completed", route)
        self.assertIn("Package 137 is next", route)

    def test_production_modules_do_not_import_package_136(self) -> None:
        prefixes = (
            "ashl_core_v1.endocrine.drive_modulation",
            "ashl_core_v1.endocrine.package_136",
        )
        findings: list[str] = []
        for directory_name in (
            "runtime",
            "perception",
            "thought",
            "task",
            "memory",
            "state",
            "body",
        ):
            directory = self.repo_root / "ashl_core_v1" / directory_name
            for path in directory.rglob("*.py"):
                tree = ast.parse(path.read_text(encoding="utf-8"))
                for node in ast.walk(tree):
                    modules = ()
                    if isinstance(node, ast.ImportFrom) and node.module:
                        modules = (node.module,)
                    elif isinstance(node, ast.Import):
                        modules = tuple(alias.name for alias in node.names)
                    if any(module.startswith(prefixes) for module in modules):
                        findings.append(path.relative_to(self.repo_root).as_posix())
        self.assertEqual(findings, [])

    def _run_package_136(self, state_dir: str | Path) -> None:
        run_real_same_session_drive_modulation(
            ashl_root=self.repo_root,
            package_133_state_dir=self.package_133_root,
            package_134_state_dir=self.package_134_root,
            package_135_state_dir=self.package_135_root,
            state_dir=state_dir,
            allow_same_session_drive_modulation=True,
        )

    def _store(self) -> Package136DriveModulationStore:
        return Package136DriveModulationStore(self.package_136_root)

    def _source(self):
        return load_package_136_sources_read_only(
            package_133_state_dir=self.package_133_root,
            package_134_state_dir=self.package_134_root,
            package_135_state_dir=self.package_135_root,
        )

    def _typed_contract(self):
        from ashl_core_v1.endocrine.drive_modulation_types import SameSessionDriveModulationContract

        return self._typed(SameSessionDriveModulationContract, "same_session_drive_modulation_contracts")

    def _typed_allowlist(self):
        from ashl_core_v1.endocrine.drive_modulation_types import DriveModulationConsumerAllowlistRecord

        return self._typed(DriveModulationConsumerAllowlistRecord, "drive_modulation_consumer_allowlists")

    def _typed_application(self) -> DriveModulationApplicationRecord:
        return self._typed(DriveModulationApplicationRecord, "drive_modulation_applications")

    def _typed(self, record_type, table: str):
        payload = dict(self._store().list_payloads(table)[0])
        for field in record_type.__dataclass_fields__.values():
            if "tuple" in str(field.type).lower() and isinstance(payload.get(field.name), list):
                payload[field.name] = tuple(payload[field.name])
        return record_type(**payload)

    @staticmethod
    def _write_package_133_fixture(state_dir: Path) -> None:
        result = create_package_133_representation_chain(
            ashl_root=Path(__file__).resolve().parents[2],
            state_dir=state_dir,
            parent_session_id="package_136_fixture_parent_session",
            child_session_id="package_136_fixture_child_session",
        )
        parent = result["parent"]
        child = result["child"]
        contract = result["contract"]
        payload = {
            "audit_id": "package_133_audit:package_136_test_only_fixture",
            "created_at": "2026-08-07T05:00:00+00:00",
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
        PersistentSelfStateStore(state_dir).append_generic_record("package_133_audits", payload)

    @staticmethod
    def _package_134_regression_receipt() -> Package134RegressionReceipt:
        return Package134RegressionReceipt(
            regression_receipt_id="package_134_regressions:package_136_test_only_fixture",
            schema_version=PACKAGE_134_REGRESSION_SCHEMA_VERSION,
            created_at="2026-08-07T05:01:00+00:00",
            baseline_commit=PACKAGE_134_BASELINE_COMMIT,
            source_head=PACKAGE_134_BASELINE_COMMIT,
            command_results=(("package_136_test_only_fixture", 0, "0" * 64),),
            targeted_package_134_passed=True,
            package_133_regressions_passed=True,
            state_engine_regressions_passed=True,
            full_v1_discover_passed=True,
            compileall_passed=True,
            git_diff_check_passed=True,
            pycache_redirected_outside_repo=True,
            fresh_regressions_passed=True,
        )

    @staticmethod
    def _package_135_regression_receipt() -> Package135RegressionReceipt:
        return Package135RegressionReceipt(
            regression_receipt_id="package_135_regressions:package_136_test_only_fixture",
            schema_version=PACKAGE_135_REGRESSION_SCHEMA_VERSION,
            created_at="2026-08-07T05:02:00+00:00",
            baseline_commit=PACKAGE_135_BASELINE_COMMIT,
            source_head=PACKAGE_135_BASELINE_COMMIT,
            command_results=(("package_136_test_only_fixture", 0, "0" * 64),),
            targeted_package_135_passed=True,
            package_134_regressions_passed=True,
            endocrine_and_boundary_regressions_passed=True,
            full_v1_discover_passed=True,
            compileall_passed=True,
            git_diff_check_passed=True,
            pycache_redirected_outside_repo=True,
            fresh_regressions_passed=True,
        )

    @staticmethod
    def _package_136_regression_receipt() -> Package136RegressionReceipt:
        return Package136RegressionReceipt(
            regression_receipt_id="package_136_regressions:test_only_explicit_fixture",
            schema_version=REGRESSION_SCHEMA_VERSION,
            created_at="2026-08-07T05:03:00+00:00",
            baseline_commit=BASELINE_COMMIT,
            source_head=BASELINE_COMMIT,
            command_results=(("test_only_explicit_fixture", 0, "0" * 64),),
            targeted_package_136_passed=True,
            package_135_regressions_passed=True,
            package_133_134_regressions_passed=True,
            authority_boundary_regressions_passed=True,
            full_v1_discover_passed=True,
            compileall_passed=True,
            git_diff_check_passed=True,
            pycache_redirected_outside_repo=True,
            fresh_regressions_passed=True,
        )


if __name__ == "__main__":
    unittest.main()
