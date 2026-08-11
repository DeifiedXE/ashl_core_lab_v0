from __future__ import annotations

import ast
import io
import json
import os
import unittest
from contextlib import redirect_stdout
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory

from ashl_core_v1.state.package_133_cross_session_self_state_schema_audit import (
    create_package_133_representation_chain,
)
from ashl_core_v1.state.package_134_package_133_source import (
    load_package_133_source_read_only,
)
from ashl_core_v1.state.package_134_persistent_session_recovery_audit import (
    audit_package_134_persistent_session_recovery,
)
from ashl_core_v1.state.package_134_persistent_session_recovery_controls import (
    run_package_134_recovery_controls,
)
from ashl_core_v1.state.package_137_self_state_review_audit import (
    audit_package_137_persistent_self_state_review_gate,
)
from ashl_core_v1.state.package_137_self_state_review_cli import main
from ashl_core_v1.state.package_137_self_state_review_controls import (
    run_package_137_self_state_review_controls,
)
from ashl_core_v1.state.package_137_self_state_review_store import (
    Package137SelfStateReviewStore,
    package_137_store_path,
)
from ashl_core_v1.state.persistent_self_state_review_runtime import (
    run_real_persistent_self_state_review_gate,
)
from ashl_core_v1.state.persistent_self_state_review_types import (
    BASELINE_COMMIT,
    CHANGED_PERSISTENT_FIELDS,
    CONTROL_NAMES,
    PACKAGE_138_REQUIRED_GATES,
    PASS_STATUS,
    PRESERVED_PERSISTENT_FIELDS,
    REGRESSION_SCHEMA_VERSION,
    Package137RegressionReceipt,
    SelfStateSuccessorDeltaRecord,
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
    BASELINE_COMMIT as PACKAGE_134_BASELINE_COMMIT,
    PASS_STATUS as PACKAGE_134_PASS_STATUS,
    REGRESSION_SCHEMA_VERSION as PACKAGE_134_REGRESSION_SCHEMA_VERSION,
    Package134RegressionReceipt,
)


class Package137PersistentSelfStateReviewGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repo_root = Path(__file__).resolve().parents[2]
        cls.temporary = TemporaryDirectory()
        cls.root = Path(cls.temporary.name)
        cls.p133 = cls.root / "package133"
        cls.p134 = cls.root / "package134"
        cls.p137 = cls.root / "package137"
        cls._write_package_133_fixture(cls.p133)
        run_real_fresh_process_recovery(
            ashl_root=cls.repo_root,
            package_133_state_dir=cls.p133,
            state_dir=cls.p134,
            allow_session_recovery=True,
        )
        run_package_134_recovery_controls(
            ashl_root=cls.repo_root,
            package_133_state_dir=cls.p133,
            state_dir=cls.p134,
            append=True,
        )
        PersistentSessionRecoveryStore(cls.p134).append_record(
            "package_134_regression_receipts", cls._package_134_regression_receipt()
        )
        audit_134 = audit_package_134_persistent_session_recovery(
            ashl_root=cls.repo_root,
            package_133_state_dir=cls.p133,
            state_dir=cls.p134,
            append=True,
        )
        if audit_134.audit_status != PACKAGE_134_PASS_STATUS:
            raise AssertionError(audit_134.failure_reasons)
        cls.run_result = run_real_persistent_self_state_review_gate(
            ashl_root=cls.repo_root,
            package_133_state_dir=cls.p133,
            package_134_state_dir=cls.p134,
            state_dir=cls.p137,
            teacher_actor="project_owner",
            teacher_role="project_owner",
            teacher_note="Approve one exact immutable structural successor for Package 137 tests.",
            confirm_teacher_approval=True,
            allow_self_state_mutation=True,
        )
        cls.controls = run_package_137_self_state_review_controls(
            ashl_root=cls.repo_root,
            package_133_state_dir=cls.p133,
            package_134_state_dir=cls.p134,
            state_dir=cls.p137,
            append=True,
        )
        Package137SelfStateReviewStore(cls.p137).append_once(
            "package_137_regression_receipts", cls._package_137_regression_receipt()
        )
        cls.audit = audit_package_137_persistent_self_state_review_gate(
            ashl_root=cls.repo_root,
            package_133_state_dir=cls.p133,
            package_134_state_dir=cls.p134,
            state_dir=cls.p137,
            append=True,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_existing_teacher_authority_is_reused_without_learning_scope(self) -> None:
        binding = self._store().list_payloads("teacher_authority_bindings")[0]
        self.assertEqual(binding["source_engine"], "state_engine")
        self.assertTrue(binding["existing_teacher_authority_reused"])
        self.assertFalse(binding["second_teacher_system_created"])
        self.assertFalse(binding["learning_approval_scope_reused"])
        self.assertIn("project_owner", binding["allowed_teacher_actors"])
        self.assertIn("project_owner", binding["allowed_teacher_roles"])

    def test_delta_is_exact_package_133_structural_allowlist(self) -> None:
        payload = self._store().list_payloads("self_state_successor_deltas")[-1]
        delta = self._typed_delta(payload)
        self.assertEqual(delta.changed_persistent_fields, CHANGED_PERSISTENT_FIELDS)
        self.assertEqual(delta.preserved_persistent_fields, PRESERVED_PERSISTENT_FIELDS)
        self.assertEqual(delta.complete_persistent_field_allowlist, ALLOWED_PERSISTENT_FIELDS)
        self.assertFalse(delta.semantic_content_added)
        self.assertFalse(delta.memory_content_added)
        self.assertFalse(delta.perception_content_added)
        self.assertFalse(delta.drive_or_modulation_content_added)
        self.assertFalse(delta.runtime_behavior_authority_added)

    def test_forbidden_delta_content_and_authority_are_rejected(self) -> None:
        delta = self._typed_delta(
            self._store().list_payloads("self_state_successor_deltas")[-1]
        )
        for field in (
            "semantic_content_added",
            "memory_content_added",
            "perception_content_added",
            "drive_or_modulation_content_added",
            "output_content_added",
            "runtime_behavior_authority_added",
        ):
            with self.subTest(field=field), self.assertRaises(ValueError):
                replace(delta, **{field: True})

    def test_reviews_bind_exact_head_parent_delta_and_child(self) -> None:
        store = self._store()
        reviews = store.list_payloads("self_state_teacher_reviews")
        proposals = {item["proposal_id"]: item for item in store.list_payloads("self_state_successor_proposals")}
        deltas = {item["delta_id"]: item for item in store.list_payloads("self_state_successor_deltas")}
        self.assertEqual({item["decision"] for item in reviews}, {"approved", "rejected", "deferred"})
        for review in reviews:
            proposal = proposals[review["proposal_id"]]
            delta = deltas[review["delta_ref"]]
            self.assertEqual(review["proposal_sha256"], proposal["proposal_sha256"])
            self.assertEqual(review["expected_active_head_sha256"], proposal["expected_active_head_sha256"])
            self.assertEqual(review["parent_self_state_sha256"], delta["parent_self_state_sha256"])
            self.assertEqual(review["delta_sha256"], delta["delta_sha256"])
            self.assertEqual(review["proposed_child_self_state_sha256"], proposal["proposed_child_self_state_sha256"])

    def test_reject_and_defer_leave_both_authorities_unchanged(self) -> None:
        records = self._store().list_payloads("self_state_review_invariance_records")
        self.assertEqual(len(records), 2)
        self.assertEqual({item["decision"] for item in records}, {"rejected", "deferred"})
        self.assertTrue(all(item["authoritative_self_state_unchanged"] for item in records))
        self.assertTrue(all(item["active_head_unchanged"] for item in records))
        self.assertTrue(all(not item["mutation_attempted"] for item in records))

    def test_approved_successor_is_append_only_and_head_advances_by_exact_cas(self) -> None:
        source = load_package_133_source_read_only(self.p133)
        head = PersistentSessionRecoveryStore(self.p134).get_active_head()
        receipt = self._store().list_payloads("self_state_mutation_commit_receipts")[0]
        self.assertEqual(len(source.states), 3)
        self.assertEqual(source.leaf.self_state_version, 3)
        self.assertEqual(source.leaf.lineage_generation, 2)
        self.assertEqual(head.self_state_record_id, source.leaf.self_state_record_id)
        self.assertEqual(head.self_state_sha256, source.leaf.self_state_sha256)
        self.assertEqual(head.head_revision, 3)
        self.assertTrue(receipt["package_133_successor_appended"])
        self.assertTrue(receipt["package_134_active_head_advanced"])
        self.assertTrue(receipt["review_consumed_once"])
        self.assertTrue(receipt["cross_authority_commit_complete"])
        self.assertFalse(receipt["parent_modified_in_place"])
        self.assertFalse(receipt["automatic_rebase_performed"])

    def test_commit_runs_in_a_fresh_process(self) -> None:
        process = self._store().list_payloads("self_state_mutation_process_receipts")[0]
        self.assertNotEqual(process["operating_system_process_id"], os.getpid())
        self.assertEqual(
            process["worker_status"],
            "approved_successor_committed_by_package_133_then_package_134_cas",
        )

    def test_all_actual_failure_controls_pass(self) -> None:
        self.assertEqual(self.controls.control_names, CONTROL_NAMES)
        self.assertEqual(self.controls.passed_count, len(CONTROL_NAMES))
        self.assertTrue(self.controls.controls_passed)
        self.assertEqual(set(self.controls.passed_control_names), set(CONTROL_NAMES))

    def test_package_137_store_has_no_competing_authority_and_is_append_only(self) -> None:
        store = self._store()
        integrity = store.audit_integrity()
        self.assertTrue(integrity["valid"])
        self.assertFalse(integrity["active_head_table_present"])
        self.assertFalse(integrity["self_state_history_table_present"])
        for method in (store.update, store.delete, store.replace):
            with self.assertRaisesRegex(TypeError, "append-only"):
                method()

    def test_final_audit_passes_and_preserves_all_runtime_boundaries(self) -> None:
        audit = self.audit
        self.assertEqual(audit.audit_status, PASS_STATUS, audit.failure_reasons)
        self.assertEqual(audit.failure_reasons, ())
        self.assertTrue(audit.exact_head_binding_verified)
        self.assertTrue(audit.exact_parent_binding_verified)
        self.assertTrue(audit.exact_delta_binding_verified)
        self.assertTrue(audit.approved_successor_created)
        self.assertTrue(audit.rejected_authorities_unchanged)
        self.assertTrue(audit.deferred_authorities_unchanged)
        self.assertTrue(audit.all_controls_passed)
        self.assertEqual(audit.package_138_required_gates, PACKAGE_138_REQUIRED_GATES)
        forbidden = (
            audit.runtime_behavior_influence_created,
            audit.self_state_readback_created,
            audit.memory_influence_created,
            audit.drive_persisted,
            audit.perception_or_attention_created,
            audit.thought_engine_used,
            audit.action_created,
            audit.output_created,
            audit.package_138_implemented,
        )
        self.assertFalse(any(forbidden))
        self.assertEqual((audit.llm_runtime_calls, audit.codex_runtime_calls, audit.network_runtime_calls), (0, 0, 0))

    def test_cli_requires_explicit_teacher_and_mutation_authorization(self) -> None:
        with TemporaryDirectory() as directory, redirect_stdout(io.StringIO()) as output:
            exit_code = main(
                [
                    "run-real-review-gate",
                    "--ashl-root",
                    str(self.repo_root),
                    "--package-133-state-dir",
                    str(self.p133),
                    "--package-134-state-dir",
                    str(self.p134),
                    "--state-dir",
                    directory,
                    "--teacher-actor",
                    "project_owner",
                    "--teacher-role",
                    "project_owner",
                    "--teacher-note",
                    "Explicit test note.",
                ]
            )
            self.assertEqual(exit_code, 2)
            self.assertIn("approval_confirmation_missing", output.getvalue())
            self.assertFalse(package_137_store_path(directory).exists())

    def test_cli_preflight_emits_serializable_authority_summary(self) -> None:
        with redirect_stdout(io.StringIO()) as output:
            exit_code = main(
                [
                    "preflight",
                    "--ashl-root",
                    str(self.repo_root),
                    "--package-133-state-dir",
                    str(self.p133),
                    "--package-134-state-dir",
                    str(self.p134),
                    "--state-dir",
                    str(self.p137),
                ]
            )
        rendered = output.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn("ready_for_exact_teacher_reviewed_structural_successor", rendered)
        self.assertIn(load_package_133_source_read_only(self.p133).leaf.self_state_record_id, rendered)
        self.assertNotIn("Package133SourceBundle", rendered)

    def test_package_137_modules_do_not_import_behavior_consumers(self) -> None:
        forbidden = (
            "ashl_core_v1.memory",
            "ashl_core_v1.perception",
            "ashl_core_v1.endocrine",
            "ashl_core_v1.runtime.internal_action",
            "ashl_core_v1.runtime.output",
            "ashl_core_v1.thought",
        )
        paths = tuple((self.repo_root / "ashl_core_v1/state").glob("*137*.py")) + tuple(
            (self.repo_root / "ashl_core_v1/state").glob("persistent_self_state_review_*.py")
        )
        for path in dict.fromkeys(paths):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.extend(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.append(node.module)
            self.assertFalse(
                any(name.startswith(forbidden) for name in imports),
                f"forbidden Package 137 import in {path.name}: {imports}",
            )

    def test_registry_marks_137_completed_and_138_next(self) -> None:
        registry = json.loads(
            (self.repo_root / "ashl_core_v1/docs/reference/package_number_registry_v0.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(registry["current_package_id"], "140")
        self.assertEqual(registry["package_status"]["137"], "completed")
        self.assertEqual(registry["package_status"]["138"], "completed")
        self.assertEqual(registry["package_status"]["139"], "completed")
        self.assertEqual(registry["package_status"]["140"], "completed")
        self.assertEqual(registry["package_status"]["141"], "next_critical_path")
        self.assertIn("137", registry["completed_package_ids"])
        self.assertNotIn("137", registry["future_package_ids"])

    def _store(self) -> Package137SelfStateReviewStore:
        return Package137SelfStateReviewStore(self.p137)

    @staticmethod
    def _typed_delta(payload: dict[str, object]) -> SelfStateSuccessorDeltaRecord:
        values = dict(payload)
        for key in (
            "changed_persistent_fields",
            "preserved_persistent_fields",
            "complete_persistent_field_allowlist",
            "source_record_refs",
        ):
            values[key] = tuple(values[key])
        return SelfStateSuccessorDeltaRecord(**values)

    @classmethod
    def _write_package_133_fixture(cls, state_dir: Path) -> None:
        result = create_package_133_representation_chain(
            ashl_root=cls.repo_root,
            state_dir=state_dir,
            parent_session_id="package_137_fixture_parent_session",
            child_session_id="package_137_fixture_child_session",
        )
        payload = {
            "audit_id": "package_133_audit:package_137_test_only_fixture",
            "created_at": "2026-08-07T04:00:00+00:00",
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
        }
        PersistentSelfStateStore(state_dir).append_generic_record("package_133_audits", payload)

    @staticmethod
    def _package_134_regression_receipt() -> Package134RegressionReceipt:
        return Package134RegressionReceipt(
            regression_receipt_id="package_134_regressions:package_137_test_only_fixture",
            schema_version=PACKAGE_134_REGRESSION_SCHEMA_VERSION,
            created_at="2026-08-07T04:01:00+00:00",
            baseline_commit=PACKAGE_134_BASELINE_COMMIT,
            source_head=PACKAGE_134_BASELINE_COMMIT,
            command_results=(("package_137_test_only_fixture", 0, "0" * 64),),
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
    def _package_137_regression_receipt() -> Package137RegressionReceipt:
        return Package137RegressionReceipt(
            regression_receipt_id="package_137_regressions:test_only_explicit_fixture",
            schema_version=REGRESSION_SCHEMA_VERSION,
            created_at="2026-08-07T04:02:00+00:00",
            baseline_commit=BASELINE_COMMIT,
            source_head=BASELINE_COMMIT,
            command_results=(("test_only_explicit_fixture", 0, "0" * 64),),
            targeted_package_137_passed=True,
            package_133_134_regressions_passed=True,
            teacher_authority_regressions_passed=True,
            package_135_136_boundary_regressions_passed=True,
            full_v1_discover_passed=True,
            compileall_passed=True,
            git_diff_check_passed=True,
            pycache_redirected_outside_repo=True,
            fresh_regressions_passed=True,
        )


if __name__ == "__main__":
    unittest.main()
