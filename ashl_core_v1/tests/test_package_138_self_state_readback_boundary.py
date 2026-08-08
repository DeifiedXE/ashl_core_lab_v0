from __future__ import annotations

import ast
import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

from ashl_core_v1.state.package_133_cross_session_self_state_schema_audit import (
    create_package_133_representation_chain,
)
from ashl_core_v1.state.package_137_self_state_review_store import (
    Package137SelfStateReviewStore,
)
from ashl_core_v1.state.package_138_self_state_readback_audit import (
    _scan_package_138_boundary,
    audit_package_138_self_state_readback_boundary,
)
from ashl_core_v1.state.package_138_self_state_readback_cli import main
from ashl_core_v1.state.package_138_self_state_readback_controls import (
    run_package_138_self_state_readback_controls,
)
from ashl_core_v1.state.package_138_self_state_readback_store import (
    Package138SelfStateReadbackStore,
    package_138_store_path,
)
from ashl_core_v1.state.persistent_self_state_review_runtime import (
    run_real_persistent_self_state_review_gate,
)
from ashl_core_v1.state.persistent_self_state_review_types import (
    PASS_STATUS as PACKAGE_137_PASS_STATUS,
)
from ashl_core_v1.state.persistent_self_state_schema import (
    ALLOWED_PERSISTENT_FIELDS,
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
    create_self_state_readback_authorization,
    run_real_self_state_readback_boundary,
)
from ashl_core_v1.state.self_state_readback_types import (
    AUDIT_ONLY_CONSUMER_ID,
    BASELINE_COMMIT,
    CONTROL_NAMES,
    PASS_STATUS,
    REGRESSION_SCHEMA_VERSION,
    Package138RegressionReceipt,
)


class Package138SelfStateReadbackBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repo_root = Path(__file__).resolve().parents[2]
        cls.temporary = TemporaryDirectory()
        cls.root = Path(cls.temporary.name)
        cls.p133 = cls.root / "package133"
        cls.p134 = cls.root / "package134"
        cls.p137 = cls.root / "package137"
        cls.p138 = cls.root / "package138"
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
                "audit_id": "package_134_audit:package_138_test_fixture",
                "created_at": "2026-08-08T00:00:00+00:00",
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
            teacher_note="Package 138 test-only exact structural successor approval.",
            confirm_teacher_approval=True,
            allow_self_state_mutation=True,
        )
        Package137SelfStateReviewStore(cls.p137).append_once(
            "package_137_audits",
            {
                "audit_id": "package_137_audit:package_138_test_fixture",
                "created_at": "2026-08-08T00:01:00+00:00",
                "audit_status": PACKAGE_137_PASS_STATUS,
            },
        )
        cls.real_run = run_real_self_state_readback_boundary(
            ashl_root=cls.repo_root,
            package_133_state_dir=cls.p133,
            package_134_state_dir=cls.p134,
            package_137_state_dir=cls.p137,
            state_dir=cls.p138,
            allow_self_state_readback=True,
            allow_fresh_process_recovery=True,
        )
        cls.controls = run_package_138_self_state_readback_controls(
            ashl_root=cls.repo_root,
            package_133_state_dir=cls.p133,
            package_134_state_dir=cls.p134,
            package_137_state_dir=cls.p137,
            state_dir=cls.p138,
        )
        Package138SelfStateReadbackStore(cls.p138).append_once(
            "package_138_regression_receipts", cls._regression_receipt()
        )
        cls.audit = audit_package_138_self_state_readback_boundary(
            ashl_root=cls.repo_root,
            package_133_state_dir=cls.p133,
            package_134_state_dir=cls.p134,
            package_137_state_dir=cls.p137,
            state_dir=cls.p138,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_contract_reuses_exact_authorities_without_new_state_fields(self) -> None:
        contract = self._store().list_payloads("self_state_readback_contracts")[0]
        self.assertEqual(contract["self_state_authority"], "package_133_immutable_self_state_lineage")
        self.assertEqual(contract["active_head_authority"], "package_134_separate_active_head_cas_authority")
        self.assertEqual(contract["review_gate_authority"], "package_137_exact_teacher_reviewed_self_state_successor_only")
        self.assertEqual(tuple(contract["exposed_structural_fields"]), ALLOWED_PERSISTENT_FIELDS)
        self.assertTrue(contract["same_session_only"])
        self.assertTrue(contract["stale_on_head_revision_change"])
        self.assertFalse(contract["persistent_working_readback_allowed"])
        self.assertFalse(contract["runtime_behavior_authority_allowed"])

    def test_consumer_allowlist_has_zero_production_and_one_audit_consumer(self) -> None:
        allowlist = self._store().list_payloads("self_state_readback_consumer_allowlists")[0]
        self.assertEqual(allowlist["production_consumer_ids"], [])
        self.assertEqual(allowlist["implicit_consumer_ids"], [])
        self.assertEqual(allowlist["audit_only_consumer_ids"], [AUDIT_ONLY_CONSUMER_ID])
        self.assertTrue(allowlist["exact_consumer_id_match_required"])

    def test_readbacks_bind_exact_head_state_session_process_and_expire(self) -> None:
        store = self._store()
        readbacks = store.list_payloads("bounded_self_state_readbacks")
        consumptions = store.list_payloads("self_state_readback_consumptions")
        lifecycles = store.list_payloads("self_state_readback_lifecycle_records")
        self.assertEqual(len(readbacks), 2)
        self.assertEqual(len(consumptions), 2)
        self.assertTrue(all(item["read_only"] and item["same_session_only"] for item in readbacks))
        self.assertTrue(all(item["exact_head_match"] and item["exact_state_match"] for item in consumptions))
        self.assertTrue(all(item["same_session_match"] and item["same_process_match"] for item in consumptions))
        expired = {item["readback_ref"] for item in lifecycles if item["lifecycle_kind"] == "expired_session_end"}
        self.assertEqual(expired, {item["readback_id"] for item in readbacks})

    def test_authorization_requires_current_head_process_and_live_session(self) -> None:
        head = PersistentSessionRecoveryStore(self.p134).get_active_head()
        with self.assertRaisesRegex(ValueError, "active_process_mismatch"):
            create_self_state_readback_authorization(
                ashl_root=self.repo_root,
                package_133_state_dir=self.p133,
                package_134_state_dir=self.p134,
                package_137_state_dir=self.p137,
                state_dir=self.p138,
                runtime_session_id=head.bound_session_id,
                process_instance_id="wrong_active_head_process",
            )
        with self.assertRaisesRegex(ValueError, "active_session_already_shutdown"):
            create_self_state_readback_authorization(
                ashl_root=self.repo_root,
                package_133_state_dir=self.p133,
                package_134_state_dir=self.p134,
                package_137_state_dir=self.p137,
                state_dir=self.p138,
                runtime_session_id=head.bound_session_id,
                process_instance_id=head.bound_process_instance_id,
            )

    def test_readback_is_opaque_and_has_no_behavior_authority(self) -> None:
        for readback in self._store().list_payloads("bounded_self_state_readbacks"):
            self.assertEqual(tuple(readback["exposed_structural_fields"]), ALLOWED_PERSISTENT_FIELDS)
            forbidden = (
                readback["semantic_identity_created"],
                readback["autobiographical_memory_created"],
                readback["psychological_state_created"],
                readback["world_knowledge_created"],
                readback["runtime_behavior_authority"],
                readback["memory_authority"],
                readback["drive_authority"],
                readback["perception_authority"],
                readback["attention_authority"],
                readback["candidate_ordering_authority"],
                readback["purpose_authority"],
                readback["thought_engine_authority"],
                readback["action_authority"],
                readback["output_authority"],
            )
            self.assertFalse(any(forbidden))

    def test_real_head_change_stales_old_readback_without_follow_refresh_or_rebind(self) -> None:
        reset = self._store().list_payloads("self_state_readback_fresh_process_resets")[0]
        stale = [
            item for item in self._store().list_payloads("self_state_readback_lifecycle_records")
            if item["lifecycle_kind"] == "stale_active_head_revision_changed"
        ]
        self.assertEqual(len(stale), 1)
        self.assertEqual(reset["head_revision_after"], reset["head_revision_before"] + 1)
        self.assertEqual(reset["self_state_record_id_before"], reset["self_state_record_id_after"])
        self.assertFalse(stale[0]["readback_active_after"])
        self.assertFalse(stale[0]["automatically_refreshed"])
        self.assertFalse(stale[0]["automatically_rebound"])

    def test_fresh_process_recovery_restores_no_prior_readback(self) -> None:
        reset = self._store().list_payloads("self_state_readback_fresh_process_resets")[0]
        self.assertNotEqual(reset["process_a_operating_system_process_id"], reset["process_b_operating_system_process_id"])
        self.assertNotEqual(reset["process_a_session_id"], reset["process_b_session_id"])
        self.assertFalse(reset["prior_readback_restored"])
        self.assertFalse(reset["prior_readback_consumable"])
        self.assertTrue(reset["fresh_authorization_required"])
        self.assertTrue(reset["fresh_binding_created"])
        noauth = self._store().get_payload(
            "self_state_readback_blocked_attempts",
            reset["missing_authorization_blocked_attempt_ref"],
        )
        self.assertEqual(noauth["failure_reason"], "blocked_readback_authorization_missing")

    def test_counterfactual_differs_only_on_readback_surface(self) -> None:
        comparison = self._store().list_payloads("self_state_readback_counterfactual_comparisons")[0]
        self.assertEqual(comparison["differing_paths"], ["readback_surface"])
        self.assertTrue(comparison["readback_surface_only_difference"])
        for field in (
            "runtime_behavior_equivalent",
            "selected_action_equivalent",
            "memory_equivalent",
            "drive_equivalent",
            "perception_history_equivalent",
            "self_state_history_equivalent",
            "active_head_equivalent",
            "output_equivalent",
            "recovery_result_equivalent",
            "production_behavior_equivalent",
        ):
            self.assertTrue(comparison[field], field)

    def test_all_validator_controls_pass_and_failures_are_auditable(self) -> None:
        self.assertEqual(self.controls.control_names, CONTROL_NAMES)
        self.assertEqual(
            self.controls.passed_count,
            len(CONTROL_NAMES),
            sorted(set(CONTROL_NAMES) - set(self.controls.passed_control_names)),
        )
        self.assertTrue(self.controls.controls_passed)
        blocked = self._store().list_payloads("self_state_readback_blocked_attempts")
        reasons = {item["failure_reason"] for item in blocked}
        self.assertTrue(any("consumer_not_allowlisted" in item for item in reasons))
        self.assertTrue(any("authorization_expired" in item for item in reasons))
        self.assertTrue(any("head_revision_mismatch" in item for item in reasons))
        self.assertTrue(all(not item["authoritative_state_changed"] for item in blocked))

    def test_store_is_append_only_and_contains_no_competing_authority(self) -> None:
        store = self._store()
        integrity = store.audit_integrity()
        self.assertTrue(integrity["valid"])
        self.assertFalse(integrity["active_head_table_present"])
        self.assertFalse(integrity["self_state_history_table_present"])
        self.assertFalse(integrity["persistent_working_readback_table_present"])
        for operation in (store.update, store.delete, store.replace):
            with self.assertRaisesRegex(TypeError, "append-only"):
                operation()

    def test_cli_requires_both_explicit_authorizations(self) -> None:
        with TemporaryDirectory() as state_dir, redirect_stdout(io.StringIO()) as output:
            code = main(
                [
                    "run-real-readback",
                    "--ashl-root", str(self.repo_root),
                    "--package-133-state-dir", str(self.p133),
                    "--package-134-state-dir", str(self.p134),
                    "--package-137-state-dir", str(self.p137),
                    "--state-dir", state_dir,
                ]
            )
            self.assertEqual(code, 2)
            self.assertIn("authorization_missing", output.getvalue())
            self.assertFalse(package_138_store_path(state_dir).exists())

    def test_final_audit_passes_and_package_139_is_not_implemented(self) -> None:
        self.assertEqual(self.audit.audit_status, PASS_STATUS, self.audit.failure_reasons)
        self.assertEqual(self.audit.failure_reasons, ())
        self.assertTrue(self.audit.exact_source_binding_verified)
        self.assertTrue(self.audit.stale_head_invalidation_verified)
        self.assertTrue(self.audit.fresh_process_reset_verified)
        self.assertTrue(self.audit.counterfactual_equivalence_verified)
        self.assertFalse(self.audit.persistent_working_readback_created)
        self.assertFalse(self.audit.package_139_implemented)
        self.assertEqual(
            (self.audit.llm_runtime_calls, self.audit.codex_runtime_calls, self.audit.network_runtime_calls),
            (0, 0, 0),
        )

    def test_package_138_has_no_production_consumer_imports(self) -> None:
        boundary = _scan_package_138_boundary(self.repo_root)
        self.assertTrue(boundary["valid"], boundary)
        state_paths = tuple((self.repo_root / "ashl_core_v1/state").glob("*138*.py")) + tuple(
            (self.repo_root / "ashl_core_v1/state").glob("self_state_readback_*.py")
        )
        for path in dict.fromkeys(state_paths):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.extend(item.name for item in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.append(node.module)
            self.assertFalse(any(name.startswith("ashl_core_v1.runtime.internal_action") for name in imports))

    def test_registry_marks_138_completed_and_139_next(self) -> None:
        registry = json.loads(
            (self.repo_root / "ashl_core_v1/docs/reference/package_number_registry_v0.json").read_text(encoding="utf-8")
        )
        self.assertEqual(registry["current_package_id"], "138")
        self.assertEqual(registry["package_status"]["138"], "completed")
        self.assertEqual(registry["package_status"]["139"], "next_critical_path")
        self.assertIn("138", registry["completed_package_ids"])
        self.assertNotIn("138", registry["future_package_ids"])

    def _store(self) -> Package138SelfStateReadbackStore:
        return Package138SelfStateReadbackStore(self.p138)

    @classmethod
    def _write_package_133_fixture(cls, state_dir: Path) -> None:
        result = create_package_133_representation_chain(
            ashl_root=cls.repo_root,
            state_dir=state_dir,
            parent_session_id="package_138_fixture_parent_session",
            child_session_id="package_138_fixture_child_session",
        )
        PersistentSelfStateStore(state_dir).append_generic_record(
            "package_133_audits",
            {
                "audit_id": "package_133_audit:package_138_test_fixture",
                "created_at": "2026-08-08T00:00:00+00:00",
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

    @staticmethod
    def _regression_receipt() -> Package138RegressionReceipt:
        return Package138RegressionReceipt(
            regression_receipt_id="package_138_regressions:test_only_explicit_fixture",
            schema_version=REGRESSION_SCHEMA_VERSION,
            created_at="2026-08-08T00:02:00+00:00",
            baseline_commit=BASELINE_COMMIT,
            source_head=BASELINE_COMMIT,
            command_results=(("test_only_explicit_fixture", 0, "0" * 64),),
            targeted_package_138_passed=True,
            package_133_134_137_regressions_passed=True,
            package_135_136_boundary_regressions_passed=True,
            teacher_authority_regressions_passed=True,
            full_v1_discover_passed=True,
            compileall_passed=True,
            git_diff_check_passed=True,
            pycache_redirected_outside_repo=True,
            fresh_regressions_passed=True,
        )


if __name__ == "__main__":
    unittest.main()
