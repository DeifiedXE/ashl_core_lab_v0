from __future__ import annotations

import ast
import json
import os
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from ashl_core_v1.runtime.local_operator_console_store import LocalOperatorConsoleStore
from ashl_core_v1.runtime.local_operator_event_stream import LocalOperatorEventStream
from ashl_core_v1.thought.instinct_layer_types import (
    BASELINE_COMMIT,
    CLOSED_SPAN_RULE_ID,
    CONTROL_NAMES,
    INPUT_EVIDENCE_KIND,
    OPEN_REGION_RULE_ID,
    PASS_STATUS,
    REGRESSION_SCHEMA_VERSION,
    Package141RegressionReceipt,
    build_hashed_record,
)
from ashl_core_v1.thought.package_141_instinct_audit import (
    audit_package_141_instinct_layer_runtime,
    repository_source_tree_sha256,
    run_package_141_boundary_controls,
)
from ashl_core_v1.thought.package_141_instinct_runtime import (
    build_controlled_structural_checkpoint,
    evaluate_instinct_checkpoint,
    load_package_141_preflight,
    run_bounded_instinct_probe_suite,
    validate_no_forbidden_instinct_authority,
)
from ashl_core_v1.thought.package_141_instinct_store import Package141InstinctStore
from ashl_core_v1.runtime.host_sensor_types import sha256_payload, utc_now


REPO_ROOT = Path(__file__).resolve().parents[2]
EXTERNAL_ROOT = Path(os.environ.get("ASHL_EXTERNAL_STATE_ROOT", r"F:\ashl_external_state"))
PACKAGE_132_STATE = EXTERNAL_ROOT / "package132_official_20260807"
PACKAGE_140_STATE = EXTERNAL_ROOT / "package140_official_20260811"


def _official_available() -> bool:
    return PACKAGE_132_STATE.is_dir() and PACKAGE_140_STATE.is_dir()


@unittest.skipUnless(_official_available(), "Package 132/140 official evidence unavailable")
class Package141RuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.preflight = load_package_141_preflight(
            ashl_root=REPO_ROOT,
            package_132_state_dir=PACKAGE_132_STATE,
            package_140_state_dir=PACKAGE_140_STATE,
        )

    def test_frozen_authorities_and_empty_implicit_consumers(self) -> None:
        boundary = self.preflight.boundary
        self.assertEqual(boundary.production_input_allowlist, (INPUT_EVIDENCE_KIND,))
        self.assertEqual(boundary.production_drive_input_allowlist, ())
        self.assertEqual(boundary.production_self_state_readback_input_allowlist, ())
        self.assertEqual(boundary.production_output_consumer_allowlist, ())
        self.assertTrue(boundary.hard_safety_precedence_preserved)
        self.assertTrue(boundary.teacher_authority_precedence_preserved)
        self.assertFalse(boundary.action_selection_allowed)
        self.assertFalse(boundary.memory_write_allowed)
        self.assertFalse(boundary.output_allowed)

    def test_legacy_inventory_does_not_promote_old_thought_or_design(self) -> None:
        inventory = self.preflight.inventory
        self.assertFalse(inventory.parallel_rule_system_created)
        self.assertFalse(inventory.legacy_thought_signal_promoted)
        classifications = {item[0]: item[2] for item in inventory.inventory_entries}
        self.assertEqual(
            classifications["legacy_thought_signal"],
            "historical_fixture_not_authority",
        )
        self.assertEqual(
            classifications["legacy_reflex_instinct_heuristic_documents"],
            "historical_design_only",
        )

    def test_rule_contract_is_fixed_deterministic_and_nonranking(self) -> None:
        contract = self.preflight.rule_contract
        self.assertEqual(len(contract.rule_definitions), 2)
        self.assertTrue(contract.deterministic)
        self.assertFalse(contract.random_selection_used)
        self.assertFalse(contract.weighted_scoring_used)
        self.assertFalse(contract.learned_ranking_used)
        self.assertTrue(contract.signals_revocable)

    def test_same_grounded_input_and_rule_version_is_deterministic(self) -> None:
        checkpoint = build_controlled_structural_checkpoint("closed")
        first = evaluate_instinct_checkpoint(preflight=self.preflight, checkpoint=checkpoint)
        second = evaluate_instinct_checkpoint(preflight=self.preflight, checkpoint=checkpoint)
        self.assertEqual(first.bundle.matched_rule_ids, (CLOSED_SPAN_RULE_ID,))
        self.assertEqual(first.bundle.matched_rule_ids, second.bundle.matched_rule_ids)
        self.assertEqual(
            first.bundle.deterministic_result_sha256,
            second.bundle.deterministic_result_sha256,
        )

    def test_different_structural_condition_changes_rule_firing(self) -> None:
        closed = evaluate_instinct_checkpoint(
            preflight=self.preflight,
            checkpoint=build_controlled_structural_checkpoint("closed"),
        )
        opened = evaluate_instinct_checkpoint(
            preflight=self.preflight,
            checkpoint=build_controlled_structural_checkpoint("open"),
        )
        self.assertEqual(closed.bundle.matched_rule_ids, (CLOSED_SPAN_RULE_ID,))
        self.assertEqual(opened.bundle.matched_rule_ids, (OPEN_REGION_RULE_ID,))
        self.assertNotEqual(closed.bundle.matched_rule_ids, opened.bundle.matched_rule_ids)

    def test_neutral_missing_unknown_and_transport_fault_never_guess(self) -> None:
        neutral = evaluate_instinct_checkpoint(
            preflight=self.preflight,
            checkpoint=build_controlled_structural_checkpoint("neutral"),
        )
        self.assertEqual(neutral.bundle.evaluation_status, "neutral_no_rule_matched")
        self.assertEqual(neutral.signals, ())
        missing = evaluate_instinct_checkpoint(
            preflight=self.preflight,
            checkpoint=None,
            input_evidence_kind=None,
        )
        self.assertEqual(missing.bundle.evaluation_status, "blocked_input")
        unknown = evaluate_instinct_checkpoint(
            preflight=self.preflight,
            checkpoint=build_controlled_structural_checkpoint("closed"),
            input_evidence_kind="unknown",
        )
        self.assertIn("blocked_unknown_evidence_kind", unknown.bundle.failure_reasons)
        faulted_checkpoint = replace(
            build_controlled_structural_checkpoint("closed"),
            compile_failure_count=1,
        )
        faulted = evaluate_instinct_checkpoint(
            preflight=self.preflight,
            checkpoint=faulted_checkpoint,
        )
        self.assertIn("blocked_transport_or_compiler_integrity", faulted.bundle.failure_reasons)

    def test_hard_safety_precedes_rule_evaluation(self) -> None:
        result = evaluate_instinct_checkpoint(
            preflight=self.preflight,
            checkpoint=build_controlled_structural_checkpoint("closed"),
            hard_safety_gate_status="blocked",
        )
        self.assertEqual(result.evaluations, ())
        self.assertIn("blocked_hard_safety_precedence", result.bundle.failure_reasons)

    def test_conflict_preserves_matches_without_action_selection(self) -> None:
        result = evaluate_instinct_checkpoint(
            preflight=self.preflight,
            checkpoint=build_controlled_structural_checkpoint("conflict"),
        )
        self.assertEqual(result.bundle.evaluation_status, "conflict_preserved_no_selection")
        self.assertEqual(set(result.bundle.matched_rule_ids), {CLOSED_SPAN_RULE_ID, OPEN_REGION_RULE_ID})
        self.assertIsNotNone(result.conflict)
        self.assertIsNone(result.conflict.winner_rule_id)
        self.assertTrue(result.conflict.all_matches_preserved)
        self.assertFalse(result.conflict.candidate_ordering_created)
        self.assertFalse(result.conflict.action_selection_created)

    def test_signal_is_revocable_unconsumed_and_has_no_behavior_authority(self) -> None:
        result = evaluate_instinct_checkpoint(
            preflight=self.preflight,
            checkpoint=build_controlled_structural_checkpoint("closed"),
        )
        signal = result.signals[0]
        self.assertTrue(signal.revocable)
        self.assertFalse(signal.consumed_by_production_runtime)
        self.assertIsNone(signal.semantic_label)
        for name in (
            "purpose_authority",
            "candidate_ordering_authority",
            "action_selection_authority",
            "motor_command_authority",
            "memory_write_authority",
            "self_state_mutation_authority",
            "perception_action_authority",
            "output_authority",
            "external_control_authority",
        ):
            self.assertFalse(getattr(signal, name))

    def test_forbidden_authority_validator_is_executable(self) -> None:
        fields = (
            "drive_input_used",
            "self_state_readback_used",
            "memory_used",
            "purpose_created_or_expanded",
            "semantic_input_used",
            "confidence_used",
            "teacher_authority_overridden",
            "selected_action_created",
            "motor_command_created",
            "memory_write_created",
            "self_state_mutation_created",
            "perception_action_created",
            "output_created",
            "external_control_created",
            "random_rule_used",
            "llm_used",
            "codex_used",
            "network_used",
            "package_142_implemented",
        )
        for field in fields:
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_no_forbidden_instinct_authority(**{field: True})

    def test_all_controls_execute_validators(self) -> None:
        result = run_package_141_boundary_controls(self.preflight)
        self.assertTrue(result.controls_passed)
        self.assertEqual(result.passed_count, len(CONTROL_NAMES))
        self.assertEqual(result.failed_control_names, ())

    def test_runtime_state_dir_must_be_external(self) -> None:
        with self.assertRaisesRegex(ValueError, "outside the repository"):
            load_package_141_preflight(
                ashl_root=REPO_ROOT,
                package_132_state_dir=PACKAGE_132_STATE,
                package_140_state_dir=PACKAGE_140_STATE,
                state_dir=REPO_ROOT / "forbidden_package_141_state",
                append=True,
            )


@unittest.skipUnless(_official_available(), "Package 132/140 official evidence unavailable")
class Package141StoreEventAndAuditTests(unittest.TestCase):
    def _append_regression_receipt(self, store: Package141InstinctStore) -> None:
        tree_hash = repository_source_tree_sha256(REPO_ROOT)
        names = (
            "targeted_package_141",
            "package_128_132_140_regressions",
            "full_v1_discover",
            "compileall",
            "git_diff_check",
            "repository_pollution_scan",
        )
        receipt = build_hashed_record(
            Package141RegressionReceipt,
            {
                "regression_receipt_id": "",
                "regression_receipt_sha256": "",
                "schema_version": REGRESSION_SCHEMA_VERSION,
                "created_at": utc_now(),
                "baseline_commit": BASELINE_COMMIT,
                "source_head": BASELINE_COMMIT,
                "source_tree_sha256": tree_hash,
                "command_results": tuple((name, 0, sha256_payload({"name": name})) for name in names),
                "targeted_package_141_passed": True,
                "package_128_132_140_regressions_passed": True,
                "full_v1_discover_passed": True,
                "compileall_passed": True,
                "git_diff_check_passed": True,
                "repository_pollution_absent": True,
                "fresh_regressions_passed": True,
                "source_record_refs": ("test_only:explicit_regression_receipt",),
            },
            id_field="regression_receipt_id",
            hash_field="regression_receipt_sha256",
            prefix="instinct_regressions",
        )
        store.append_once("package_141_regression_receipts", receipt)

    def test_store_is_append_only_and_has_no_authority_tables(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            store = Package141InstinctStore(temp)
            preflight = load_package_141_preflight(
                ashl_root=REPO_ROOT,
                package_132_state_dir=PACKAGE_132_STATE,
                package_140_state_dir=PACKAGE_140_STATE,
            )
            controls = run_package_141_boundary_controls(preflight)
            store.append_once("package_141_control_results", controls)
            store.append_once("package_141_control_results", controls)
            self.assertEqual(store.count("package_141_control_results"), 1)
            with self.assertRaises(TypeError):
                store.update()
            with self.assertRaises(TypeError):
                store.delete()
            with self.assertRaises(TypeError):
                store.replace()
            integrity = store.audit_integrity()
            self.assertTrue(integrity["valid"])
            self.assertFalse(integrity["authority_table_present"])

    def test_operator_events_use_existing_stream_and_delivery_failure_is_visible(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            stream = LocalOperatorEventStream(LocalOperatorConsoleStore(temp))
            preflight = load_package_141_preflight(
                ashl_root=REPO_ROOT,
                package_132_state_dir=PACKAGE_132_STATE,
                package_140_state_dir=PACKAGE_140_STATE,
            )
            result = evaluate_instinct_checkpoint(
                preflight=preflight,
                checkpoint=build_controlled_structural_checkpoint("closed"),
                event_stream=stream,
            )
            kinds = {item["event_kind"] for item in stream.list_events()}
            self.assertIn("instinct_rule_evaluated", kinds)
            self.assertIn("bounded_instinct_signal_created", kinds)
            self.assertIn("instinct_evaluation_completed", kinds)
            self.assertFalse(result.bundle.output_created)

            class BrokenStream:
                def append_event(self, **_kwargs: object) -> None:
                    raise RuntimeError("visible_delivery_failure")

            with self.assertRaisesRegex(RuntimeError, "visible_delivery_failure"):
                evaluate_instinct_checkpoint(
                    preflight=preflight,
                    checkpoint=build_controlled_structural_checkpoint("closed"),
                    event_stream=BrokenStream(),  # type: ignore[arg-type]
                )

    def test_end_to_end_runtime_and_audit(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            runtime = run_bounded_instinct_probe_suite(
                ashl_root=REPO_ROOT,
                state_dir=temp,
                package_132_state_dir=PACKAGE_132_STATE,
                package_140_state_dir=PACKAGE_140_STATE,
            )
            self.assertTrue(runtime["closed_deterministic_result_equal"])
            self.assertTrue(runtime["different_condition_different_firing"])
            self.assertEqual(runtime["conflict_winner_rule_id"], None)
            preflight = load_package_141_preflight(
                ashl_root=REPO_ROOT,
                package_132_state_dir=PACKAGE_132_STATE,
                package_140_state_dir=PACKAGE_140_STATE,
            )
            store = Package141InstinctStore(temp)
            run_package_141_boundary_controls(preflight, append_to=store)
            self._append_regression_receipt(store)
            audit = audit_package_141_instinct_layer_runtime(
                ashl_root=REPO_ROOT,
                state_dir=temp,
                package_132_state_dir=PACKAGE_132_STATE,
                package_140_state_dir=PACKAGE_140_STATE,
            )
            self.assertEqual(audit.audit_status, PASS_STATUS)
            self.assertEqual(audit.fixed_rule_count, 2)
            self.assertEqual(audit.production_drive_input_count, 0)
            self.assertEqual(audit.production_readback_input_count, 0)
            self.assertEqual(audit.production_output_consumer_count, 0)
            self.assertTrue(audit.conflict_preserved_without_selection)
            self.assertFalse(audit.selected_action_created)
            self.assertFalse(audit.memory_write_created)
            self.assertFalse(audit.output_created)
            self.assertFalse(audit.package_142_implemented)
            self.assertFalse(audit.full_thought_engine_implemented)


class Package141RepositoryBoundaryTests(unittest.TestCase):
    def test_package_141_does_not_import_drive_readback_task_or_action_modules(self) -> None:
        paths = tuple((REPO_ROOT / "ashl_core_v1" / "thought").glob("*instinct*.py"))
        imported: set[str] = set()
        for path in paths:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported.update(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imported.add(node.module)
        forbidden_prefixes = (
            "ashl_core_v1.endocrine.drive_modulation",
            "ashl_core_v1.endocrine.drive_signal",
            "ashl_core_v1.state.self_state_readback",
            "ashl_core_v1.task",
            "ashl_core_v1.host_body",
        )
        self.assertFalse(
            tuple(name for name in imported if name.startswith(forbidden_prefixes))
        )

    def test_old_thought_signal_shape_is_not_modified_or_used_as_authority(self) -> None:
        text = (REPO_ROOT / "ashl_core_v1" / "thought" / "types.py").read_text(encoding="utf-8")
        self.assertIn("class ThoughtSignal", text)
        runtime = (REPO_ROOT / "ashl_core_v1" / "thought" / "package_141_instinct_runtime.py").read_text(encoding="utf-8")
        self.assertNotIn("from ashl_core_v1.thought.types import ThoughtSignal", runtime)

    def test_registry_and_route_advance_only_to_142(self) -> None:
        registry = json.loads(
            (REPO_ROOT / "ashl_core_v1" / "docs" / "reference" / "package_number_registry_v0.json").read_text(encoding="utf-8")
        )
        self.assertEqual(registry["current_package_id"], "141")
        self.assertEqual(registry["package_status"]["141"], "completed")
        self.assertEqual(registry["package_status"]["142"], "next_critical_path")
        self.assertIn("141", registry["completed_package_ids"])
        self.assertNotIn("141", registry["future_package_ids"])
        route = (REPO_ROOT / "ashl_core_v1" / "docs" / "reference" / "package_123_to_daily_runtime_revised_route_v0.md").read_text(encoding="utf-8")
        self.assertIn("Package 141 is completed", route)
        self.assertIn("Package 142 is next", route)
        self.assertIn("Package 141 does not implement Package 142", route)


if __name__ == "__main__":
    unittest.main()
