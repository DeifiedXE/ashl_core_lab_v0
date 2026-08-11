from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory

from ashl_core_v1.endocrine.drive_signal_legacy_inventory import (
    build_drive_signal_legacy_inventory,
)
from ashl_core_v1.endocrine.drive_signal_trace_runtime import (
    build_signal_trace,
    run_real_drive_signal_trace_separation,
)
from ashl_core_v1.endocrine.drive_signal_trace_types import (
    BASELINE_COMMIT,
    PASS_STATUS,
    REGRESSION_SCHEMA_VERSION,
    DriveRegulatorySignalSourceObservation,
    DriveRegulatorySignalTraceRecord,
    Package135RegressionReceipt,
)
from ashl_core_v1.endocrine.package_135_authority_source import (
    load_package_135_authority_sources_read_only,
    source_tree_sha256,
)
from ashl_core_v1.endocrine.package_135_drive_signal_trace_audit import (
    audit_package_135_drive_signal_trace_separation,
)
from ashl_core_v1.endocrine.package_135_drive_signal_trace_cli import main
from ashl_core_v1.endocrine.package_135_drive_signal_trace_controls import (
    run_package_135_drive_trace_controls,
)
from ashl_core_v1.endocrine.package_135_drive_signal_trace_store import (
    Package135DriveSignalTraceStore,
    package_135_store_path,
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


class Package135DriveSignalTraceSeparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repo_root = Path(__file__).resolve().parents[2]
        cls.temporary = TemporaryDirectory()
        cls.root = Path(cls.temporary.name)
        cls.package_133_root = cls.root / "package133"
        cls.package_134_root = cls.root / "package134"
        cls.package_135_root = cls.root / "package135"
        cls._write_package_133_fixture(cls.package_133_root)
        run_real_fresh_process_recovery(
            ashl_root=cls.repo_root,
            package_133_state_dir=cls.package_133_root,
            state_dir=cls.package_134_root,
            allow_session_recovery=True,
        )
        controls = run_package_134_recovery_controls(
            ashl_root=cls.repo_root,
            package_133_state_dir=cls.package_133_root,
            state_dir=cls.package_134_root,
            append=True,
        )
        if not controls.controls_passed:
            raise AssertionError("test-only Package 134 control fixture failed")
        PersistentSessionRecoveryStore(cls.package_134_root).append_record(
            "package_134_regression_receipts", cls._package_134_regression_receipt()
        )
        audit = audit_package_134_persistent_session_recovery(
            ashl_root=cls.repo_root,
            package_133_state_dir=cls.package_133_root,
            state_dir=cls.package_134_root,
            append=True,
        )
        if audit.audit_status != PACKAGE_134_PASS_STATUS:
            raise AssertionError(audit.failure_reasons)
        cls.real_result = run_real_drive_signal_trace_separation(
            ashl_root=cls.repo_root,
            package_133_state_dir=cls.package_133_root,
            package_134_state_dir=cls.package_134_root,
            state_dir=cls.package_135_root,
            allow_drive_trace_observation=True,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_legacy_inventory_reconciles_actual_sources(self) -> None:
        records = build_drive_signal_legacy_inventory(self.repo_root)
        self.assertEqual(len(records), 10)
        self.assertTrue(all(item.source_scan_verified for item in records))
        classifications = {item.current_classification for item in records}
        self.assertIn("legacy_value_shape_not_package_135_authority", classifications)
        self.assertIn("thought_consumer_forbidden_for_package_135", classifications)
        self.assertIn("package_133_self_state_excludes_drive", classifications)
        self.assertIn("package_134_recovery_excludes_drive", classifications)
        self.assertIn("package_132_frozen_perception_attention_boundary", classifications)

    def test_package_133_and_134_are_read_only_authority_sources(self) -> None:
        before_133 = source_tree_sha256(self.package_133_root)
        before_134 = source_tree_sha256(self.package_134_root)
        source = load_package_135_authority_sources_read_only(
            package_133_state_dir=self.package_133_root,
            package_134_state_dir=self.package_134_root,
        )
        self.assertEqual(before_133, source_tree_sha256(self.package_133_root))
        self.assertEqual(before_134, source_tree_sha256(self.package_134_root))
        self.assertEqual(source.package_133.snapshot.package_133_audit_status, PACKAGE_133_PASS_STATUS)
        self.assertEqual(source.package_134_audit["audit_status"], PACKAGE_134_PASS_STATUS)
        self.assertTrue(source.non_recovery_evidence.package_133_allowed_fields_exclude_drive)
        self.assertTrue(source.non_recovery_evidence.active_head_drive_fields_absent)
        self.assertFalse(source.non_recovery_evidence.drive_state_restored)
        self.assertFalse(source.non_recovery_evidence.behavior_influence_created)

    def test_trace_contract_is_observation_only_and_same_session(self) -> None:
        contract = self._store().list_payloads("drive_trace_contracts")[0]
        self.assertEqual(contract["signal_scope"], "same_session_observation_only")
        self.assertTrue(contract["source_provenance_required"])
        self.assertTrue(contract["event_and_processing_time_required"])
        self.assertTrue(contract["immutable_parent_hash_lineage_required"])
        self.assertTrue(contract["cross_session_reset_required"])
        for name in (
            "package_133_self_state_content_allowed",
            "package_134_recovery_allowed",
            "memory_content_allowed",
            "purpose_or_desire_allowed",
            "reward_or_semantic_emotion_allowed",
            "tendency_or_affordance_identity_allowed",
            "runtime_modulation_allowed",
            "package_136_modulation_authorized",
        ):
            self.assertFalse(contract[name])

    def test_trace_records_carry_source_time_change_and_no_semantics(self) -> None:
        store = self._store()
        observations = store.list_payloads("drive_source_observations")
        traces = store.list_payloads("drive_signal_traces")
        self.assertEqual(len(observations), 3)
        self.assertEqual(len(traces), 3)
        self.assertEqual(sorted(item["sequence_index"] for item in traces), [0, 0, 1])
        self.assertIn("increased", {item["change_kind"] for item in traces})
        for item in observations:
            self.assertLessEqual(item["observed_at_event_time_ns"], item["observed_at_processing_time_ns"])
            self.assertIsNone(item["semantic_label"])
            self.assertIsNone(item["purpose_ref"])
            self.assertIsNone(item["tendency_ref"])
            self.assertIsNone(item["selected_action_ref"])
        for item in traces:
            self.assertIsNone(item["semantic_label"])
            self.assertFalse(item["self_state_content_authority"])
            self.assertFalse(item["memory_content_authority"])
            self.assertFalse(item["perception_modulation_authority"])
            self.assertFalse(item["attention_modulation_authority"])
            self.assertFalse(item["candidate_ordering_authority"])
            self.assertFalse(item["thought_engine_authority"])
            self.assertFalse(item["action_preference_authority"])
            self.assertFalse(item["selected_action_authority"])
            self.assertFalse(item["output_authority"])

    def test_trace_validation_rejects_semantics_and_authority(self) -> None:
        trace = DriveRegulatorySignalTraceRecord.from_dict(
            self._store().list_payloads("drive_signal_traces")[0]
        )
        with self.assertRaises(ValueError):
            replace(trace, semantic_label="fear")
        with self.assertRaises(ValueError):
            replace(trace, purpose_expansion_authority=True)
        with self.assertRaises(ValueError):
            replace(trace, candidate_ordering_authority=True)
        with self.assertRaises(ValueError):
            replace(trace, output_authority=True)

    def test_cross_session_parent_is_rejected(self) -> None:
        store = self._store()
        traces = tuple(
            DriveRegulatorySignalTraceRecord.from_dict(item)
            for item in store.list_payloads("drive_signal_traces")
        )
        parent = next(item for item in traces if item.sequence_index == 0)
        observations = tuple(
            DriveRegulatorySignalSourceObservation(
                **{
                    **item,
                    "source_record_refs": tuple(item["source_record_refs"]),
                    "source_trace_refs": tuple(item["source_trace_refs"]),
                }
            )
            for item in store.list_payloads("drive_source_observations")
        )
        other = next(item for item in observations if item.runtime_session_id != parent.runtime_session_id)
        with self.assertRaisesRegex(ValueError, "cannot cross a runtime session"):
            build_signal_trace(
                contract=self._contract(),
                observation=other,
                signal_lineage_id=parent.signal_lineage_id,
                sequence_index=1,
                parent=parent,
            )

    def test_real_process_pair_proves_reset_and_non_recovery(self) -> None:
        process_a = self.real_result["process_a"]
        process_b = self.real_result["process_b"]
        self.assertNotEqual(process_a["operating_system_process_id"], process_b["operating_system_process_id"])
        self.assertNotEqual(process_a["process_instance_id"], process_b["process_instance_id"])
        self.assertNotEqual(process_a["runtime_session_id"], process_b["runtime_session_id"])
        self.assertLess(process_a["ended_monotonic_ns"], process_b["started_monotonic_ns"])
        self.assertEqual(len(process_a["signal_trace_ids"]), 2)
        self.assertEqual(len(process_b["signal_trace_ids"]), 1)
        pair = self._store().list_payloads("drive_trace_process_pairs")[0]
        reset = self._store().list_payloads("drive_cross_session_resets")[0]
        self.assertEqual(pair["comparison_status"], "passed_fresh_process_drive_trace_reset")
        self.assertTrue(pair["process_b_started_with_new_root"])
        self.assertFalse(pair["prior_trace_loaded_by_process_b"])
        self.assertEqual(reset["reset_status"], "passed_cross_session_drive_non_recovery")
        self.assertFalse(reset["package_134_drive_state_restored"])
        self.assertFalse(reset["source_trace_parent_reused"])
        self.assertFalse(reset["source_value_copied"])
        self.assertFalse(reset["source_trace_payload_loaded_in_target"])

    def test_store_is_append_only_and_has_no_drive_head_or_recovery(self) -> None:
        store = self._store()
        integrity = store.audit_integrity()
        self.assertTrue(integrity["valid"])
        self.assertTrue(integrity["append_only_history"])
        self.assertFalse(integrity["active_drive_head_present"])
        self.assertFalse(integrity["cross_session_recovery_table_present"])
        for call in (store.update, store.delete, store.select_active_head, store.recover):
            with self.assertRaises(TypeError):
                call()

    def test_all_negative_controls_use_real_rejections(self) -> None:
        result = run_package_135_drive_trace_controls(state_dir=self.package_135_root)
        self.assertTrue(result.controls_passed)
        self.assertEqual(result.passed_count, 12)
        self.assertEqual(result.expected_count, 12)

    def test_cli_requires_explicit_trace_observation_authorization(self) -> None:
        with TemporaryDirectory() as directory:
            output = io.StringIO()
            with redirect_stdout(output):
                result = main(
                    [
                        "run-real-trace-boundary",
                        "--ashl-root",
                        str(self.repo_root),
                        "--package-133-state-dir",
                        str(self.package_133_root),
                        "--package-134-state-dir",
                        str(self.package_134_root),
                        "--state-dir",
                        directory,
                    ]
                )
            self.assertEqual(result, 2)
            self.assertIn("blocked_drive_trace_observation_authorization_missing", output.getvalue())
            self.assertFalse(package_135_store_path(directory).exists())

    def test_audit_blocks_without_fresh_regressions(self) -> None:
        run_package_135_drive_trace_controls(state_dir=self.package_135_root)
        audit = audit_package_135_drive_signal_trace_separation(
            ashl_root=self.repo_root,
            package_133_state_dir=self.package_133_root,
            package_134_state_dir=self.package_134_root,
            state_dir=self.package_135_root,
            append=False,
        )
        self.assertNotEqual(audit.audit_status, PASS_STATUS)
        self.assertIn("regressions", audit.failure_reasons)
        self.assertFalse(audit.runtime_modulation_created)

    def test_final_audit_passes_with_evidence_controls_and_regressions(self) -> None:
        with TemporaryDirectory() as directory:
            run_real_drive_signal_trace_separation(
                ashl_root=self.repo_root,
                package_133_state_dir=self.package_133_root,
                package_134_state_dir=self.package_134_root,
                state_dir=directory,
                allow_drive_trace_observation=True,
            )
            run_package_135_drive_trace_controls(state_dir=directory)
            Package135DriveSignalTraceStore(directory).append_record(
                "package_135_regression_receipts", self._package_135_regression_receipt()
            )
            audit = audit_package_135_drive_signal_trace_separation(
                ashl_root=self.repo_root,
                package_133_state_dir=self.package_133_root,
                package_134_state_dir=self.package_134_root,
                state_dir=directory,
                append=True,
            )
            self.assertEqual(audit.audit_status, PASS_STATUS)
            self.assertEqual(audit.failure_reasons, tuple())
            self.assertTrue(audit.cross_session_reset_verified)
            self.assertTrue(audit.drive_tendency_affordance_purpose_action_separated)
            self.assertFalse(audit.package_134_drive_state_restored)
            self.assertFalse(audit.drive_trace_restored_across_session)
            self.assertFalse(audit.runtime_modulation_created)
            self.assertTrue(audit.package_136_implemented)
            self.assertFalse(audit.package_136_modulation_authorized)

    def test_registry_and_route_preserve_package_135_after_package_136(self) -> None:
        registry = json.loads(
            (
                self.repo_root
                / "ashl_core_v1/docs/reference/package_number_registry_v0.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(registry["current_package_id"], "140")
        self.assertIn("135", registry["completed_package_ids"])
        self.assertNotIn("135", registry["future_package_ids"])
        self.assertEqual(registry["package_status"]["135"], "completed")
        self.assertEqual(registry["package_status"]["136"], "completed")
        self.assertEqual(registry["package_status"]["137"], "completed")
        self.assertEqual(registry["package_status"]["138"], "completed")
        self.assertEqual(registry["package_status"]["139"], "completed")
        self.assertEqual(registry["package_status"]["140"], "completed")
        self.assertEqual(registry["package_status"]["141"], "next_critical_path")
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
        self.assertIn("| 135 | Drive Signal Trace Separation", route)
        self.assertIn("Package 138 exposes that exact state", route)
        self.assertIn("Package 139 selects only an explicit verified ancestor", route)
        self.assertIn("Package 140 is the frozen", route)
        self.assertIn("Package 141 is next", route)

    def _store(self) -> Package135DriveSignalTraceStore:
        return Package135DriveSignalTraceStore(self.package_135_root)

    def _contract(self):
        from ashl_core_v1.endocrine.drive_signal_trace_types import DriveRegulatorySignalTraceContract

        payload = dict(self._store().list_payloads("drive_trace_contracts")[0])
        payload["allowed_source_kinds"] = tuple(payload["allowed_source_kinds"])
        payload["source_record_refs"] = tuple(payload["source_record_refs"])
        return DriveRegulatorySignalTraceContract(**payload)

    @staticmethod
    def _write_package_133_fixture(state_dir: Path) -> None:
        result = create_package_133_representation_chain(
            ashl_root=Path(__file__).resolve().parents[2],
            state_dir=state_dir,
            parent_session_id="package_135_fixture_parent_session",
            child_session_id="package_135_fixture_child_session",
        )
        parent = result["parent"]
        child = result["child"]
        contract = result["contract"]
        payload = {
            "audit_id": "package_133_audit:package_135_test_only_fixture",
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
        PersistentSelfStateStore(state_dir).append_generic_record("package_133_audits", payload)

    @staticmethod
    def _package_134_regression_receipt() -> Package134RegressionReceipt:
        return Package134RegressionReceipt(
            regression_receipt_id="package_134_regressions:package_135_test_only_fixture",
            schema_version=PACKAGE_134_REGRESSION_SCHEMA_VERSION,
            created_at="2026-08-07T04:01:00+00:00",
            baseline_commit=PACKAGE_134_BASELINE_COMMIT,
            source_head=PACKAGE_134_BASELINE_COMMIT,
            command_results=(("package_135_test_only_fixture", 0, "0" * 64),),
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
            regression_receipt_id="package_135_regressions:test_only_explicit_fixture",
            schema_version=REGRESSION_SCHEMA_VERSION,
            created_at="2026-08-07T04:02:00+00:00",
            baseline_commit=BASELINE_COMMIT,
            source_head=BASELINE_COMMIT,
            command_results=(("test_only_explicit_fixture", 0, "0" * 64),),
            targeted_package_135_passed=True,
            package_134_regressions_passed=True,
            endocrine_and_boundary_regressions_passed=True,
            full_v1_discover_passed=True,
            compileall_passed=True,
            git_diff_check_passed=True,
            pycache_redirected_outside_repo=True,
            fresh_regressions_passed=True,
        )


if __name__ == "__main__":
    unittest.main()
