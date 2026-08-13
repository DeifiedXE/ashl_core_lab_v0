from __future__ import annotations

import ast
import contextlib
import io
import json
import os
import shutil
import sqlite3
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from ashl_core_v1.runtime.host_sensor_types import sha256_payload, utc_now
from ashl_core_v1.runtime.local_operator_console_store import LocalOperatorConsoleStore
from ashl_core_v1.runtime.local_operator_event_stream import LocalOperatorEventStream
from ashl_core_v1.thought.package_141_instinct_audit import repository_source_tree_sha256
from ashl_core_v1.thought.package_142_specialized_thought_audit import (
    audit_package_142_specialized_thought,
    run_package_142_boundary_controls,
)
from ashl_core_v1.thought.package_142_specialized_thought_cli import main as package_142_cli
from ashl_core_v1.thought.package_142_specialized_thought_runtime import (
    build_counterfactual_equivalence,
    create_cross_family_conflict,
    evaluate_specialized_precursor,
    invalidate_specialized_results,
    load_package_141_evidence,
    load_package_142_preflight,
    run_specialized_thought_suite,
    validate_no_forbidden_specialized_authority,
)
from ashl_core_v1.thought.package_142_specialized_thought_store import (
    Package142SpecializedThoughtStore,
)
from ashl_core_v1.thought.specialized_thought_types import (
    BASELINE_COMMIT,
    CLOSED_FAMILY_ID,
    CLOSED_RESULT,
    CONSUMER_SCOPE,
    CONTROL_NAMES,
    OPEN_FAMILY_ID,
    OPEN_RESULT,
    PASS_STATUS,
    REGRESSION_SCHEMA_VERSION,
    Package142RegressionReceipt,
    build_hashed_record,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_141_STATE = Path(
    os.environ.get(
        "ASHL_PACKAGE_141_STATE_DIR",
        r"F:\ashl_external_state\package141_official_20260811",
    )
)


def _official_available() -> bool:
    return (
        PACKAGE_141_STATE
        / "package_141_instinct_layer_runtime_v0"
        / "package_141.sqlite3"
    ).is_file()


@unittest.skipUnless(_official_available(), "Package 141 official evidence unavailable")
class Package142SpecializedRuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.preflight = load_package_142_preflight(
            ashl_root=REPO_ROOT,
            package_141_state_dir=PACKAGE_141_STATE,
        )
        cls.signal_map = {
            item.instinct_signal_id: item for item in cls.preflight.source.signals
        }

    def _closed(self, *, bound: int = 1_000_000_000, evaluated: int | None = None):
        bundle = self.preflight.source.closed_bundle
        return evaluate_specialized_precursor(
            preflight=self.preflight,
            family_id=CLOSED_FAMILY_ID,
            source_bundle=bundle,
            source_signal=self.signal_map[bundle.instinct_signal_refs[0]],
            bound_at_monotonic_ns=bound,
            evaluated_at_monotonic_ns=evaluated or bound + 1,
        )

    def _open(self, *, bound: int = 2_000_000_000):
        bundle = self.preflight.source.open_bundle
        return evaluate_specialized_precursor(
            preflight=self.preflight,
            family_id=OPEN_FAMILY_ID,
            source_bundle=bundle,
            source_signal=self.signal_map[bundle.instinct_signal_refs[0]],
            bound_at_monotonic_ns=bound,
            evaluated_at_monotonic_ns=bound + 1,
        )

    def test_read_only_consumer_binding_is_exact(self) -> None:
        binding = self.preflight.consumer_binding
        self.assertEqual(binding.consumer_scope, CONSUMER_SCOPE)
        self.assertTrue(binding.package_141_store_read_only)
        self.assertFalse(binding.package_141_history_mutated)
        self.assertFalse(binding.legacy_thought_signal_allowed)
        self.assertFalse(binding.direct_perception_input_allowed)
        self.assertEqual(binding.production_drive_input_allowlist, ())
        self.assertEqual(binding.production_self_state_readback_input_allowlist, ())
        self.assertEqual(binding.production_output_consumer_allowlist, ())

    def test_source_database_is_query_only_and_unchanged(self) -> None:
        first = load_package_141_evidence(PACKAGE_141_STATE)
        second = load_package_141_evidence(PACKAGE_141_STATE)
        self.assertEqual(first.database_sha256, second.database_sha256)
        self.assertEqual(first.audit.audit_status, "passed_instinct_layer_runtime_v0")

    def test_two_independent_versioned_families_have_exact_allowlists(self) -> None:
        families = {item.family_id: item for item in self.preflight.family_contracts}
        self.assertEqual(set(families), {CLOSED_FAMILY_ID, OPEN_FAMILY_ID})
        for family in families.values():
            self.assertTrue(family.deterministic)
            self.assertTrue(family.versioned)
            self.assertEqual(len(family.input_annotation_allowlist), 1)
            self.assertEqual(len(family.output_annotation_allowlist), 1)
            self.assertFalse(family.recursive_input_allowed)
            self.assertFalse(family.cross_family_chaining_allowed)
            self.assertFalse(family.workspace_created)
            self.assertFalse(family.iterative_search_allowed)

    def test_same_precursor_and_rule_version_is_deterministic(self) -> None:
        first = self._closed()
        second = self._closed(bound=1_000_000_100)
        self.assertEqual(
            first.evaluation.deterministic_result_sha256,
            second.evaluation.deterministic_result_sha256,
        )
        self.assertGreaterEqual(len(first.evaluation.rule_conditions), 5)
        self.assertTrue(all(item[4] for item in first.evaluation.rule_conditions))
        self.assertEqual(first.result.bounded_result_annotation, CLOSED_RESULT)

    def test_different_precursor_fires_different_family_result(self) -> None:
        self.assertEqual(self._closed().result.bounded_result_annotation, CLOSED_RESULT)
        self.assertEqual(self._open().result.bounded_result_annotation, OPEN_RESULT)

    def test_family_cannot_consume_other_family_precursor(self) -> None:
        bundle = self.preflight.source.closed_bundle
        with self.assertRaisesRegex(ValueError, "not_allowed"):
            evaluate_specialized_precursor(
                preflight=self.preflight,
                family_id=OPEN_FAMILY_ID,
                source_bundle=bundle,
                source_signal=self.signal_map[bundle.instinct_signal_refs[0]],
            )

    def test_specialized_result_cannot_recurse_as_input(self) -> None:
        closed = self._closed()
        with self.assertRaisesRegex(ValueError, "typed_package_141_precursor"):
            evaluate_specialized_precursor(
                preflight=self.preflight,
                family_id=CLOSED_FAMILY_ID,
                source_bundle=self.preflight.source.closed_bundle,
                source_signal=closed.result,  # type: ignore[arg-type]
            )

    def test_cross_family_conflict_is_unresolved_and_preserves_both(self) -> None:
        outputs = []
        for offset, signal_ref in enumerate(
            self.preflight.source.conflict_bundle.instinct_signal_refs, start=10
        ):
            signal = self.signal_map[signal_ref]
            family = (
                CLOSED_FAMILY_ID
                if signal.bounded_annotation == "bounded_visual_closed_span_present"
                else OPEN_FAMILY_ID
            )
            outputs.append(
                evaluate_specialized_precursor(
                    preflight=self.preflight,
                    family_id=family,
                    source_bundle=self.preflight.source.conflict_bundle,
                    source_signal=signal,
                    bound_at_monotonic_ns=3_000_000_000 + offset,
                    evaluated_at_monotonic_ns=3_000_000_001 + offset,
                )
            )
        conflict = create_cross_family_conflict(
            source_bundle=self.preflight.source.conflict_bundle,
            outputs=tuple(outputs),
        )
        self.assertEqual(
            conflict.conflict_status,
            "unresolved_cross_family_conflict_preserved",
        )
        self.assertIsNone(conflict.winner_result_id)
        self.assertFalse(conflict.ranking_used)
        self.assertFalse(conflict.voting_used)
        self.assertFalse(conflict.random_tie_break_used)
        self.assertFalse(conflict.deliberation_created)
        self.assertFalse(conflict.action_selection_created)

    def test_expired_precursor_blocks_and_creates_no_result(self) -> None:
        output = self._closed(
            bound=4_000_000_000,
            evaluated=5_000_000_000,
        )
        self.assertEqual(output.evaluation.evaluation_status, "blocked_expired_precursor")
        self.assertIsNone(output.result)

    def test_expiry_and_revocation_cascade_leave_no_dangling_result(self) -> None:
        closed = self._closed()
        expired = invalidate_specialized_results(
            output=closed,
            transition_kind="upstream_precursor_expired",
            observed_at_monotonic_ns=closed.precursor_binding.expires_at_monotonic_ns,
        )
        opened = self._open()
        revoked = invalidate_specialized_results(
            output=opened,
            transition_kind="upstream_precursor_revoked",
            observed_at_monotonic_ns=opened.evaluation.evaluated_at_monotonic_ns + 1,
        )
        for item in (expired, revoked):
            self.assertFalse(item.result_valid_after_transition)
            self.assertFalse(item.dangling_specialized_result)
            self.assertFalse(item.package_141_record_mutated)

    def test_result_is_nonsemantic_revocable_and_has_no_behavior_authority(self) -> None:
        result = self._closed().result
        self.assertTrue(result.revocable)
        self.assertEqual(result.production_consumer_count, 0)
        self.assertIsNone(result.semantic_label)
        for name in (
            "purpose_authority",
            "candidate_ordering_authority",
            "action_selection_authority",
            "memory_write_authority",
            "self_state_mutation_authority",
            "perception_action_authority",
            "output_authority",
            "external_control_authority",
            "drive_input_used",
            "self_state_readback_used",
        ):
            self.assertFalse(getattr(result, name))

    def test_counterfactual_keeps_every_authority_surface_equal(self) -> None:
        record = build_counterfactual_equivalence(
            root=REPO_ROOT,
            source_sha256_before=self.preflight.source.database_sha256,
            source_sha256_after=self.preflight.source.database_sha256,
            source_record_refs=(self.preflight.consumer_binding.consumer_binding_id,),
        )
        self.assertEqual(
            record.counterfactual_status,
            "passed_specialized_thought_counterfactual_equivalence",
        )
        self.assertEqual(
            record.neutral_authority_fingerprint,
            record.specialized_authority_fingerprint,
        )
        self.assertTrue(record.runtime_behavior_equivalent)
        self.assertTrue(record.memory_equivalent)
        self.assertTrue(record.purpose_equivalent)
        self.assertTrue(record.action_equivalent)
        self.assertTrue(record.output_equivalent)
        self.assertTrue(record.self_state_equivalent)
        self.assertTrue(record.drive_equivalent)
        self.assertTrue(record.perception_authority_equivalent)

    def test_forbidden_authority_validator_executes(self) -> None:
        for field in (
            "purpose_created",
            "candidate_ordering_created",
            "selected_action_created",
            "memory_write_created",
            "self_state_mutation_created",
            "perception_action_created",
            "output_created",
            "external_control_created",
            "drive_input_used",
            "self_state_readback_used",
            "recursive_input_used",
            "workspace_created",
            "iterative_search_used",
            "package_143_implemented",
            "llm_used",
            "codex_used",
            "network_used",
        ):
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_no_forbidden_specialized_authority(**{field: True})

    def test_all_controls_are_executable_and_pass(self) -> None:
        controls = run_package_142_boundary_controls(
            self.preflight,
            ashl_root=REPO_ROOT,
        )
        self.assertTrue(controls.controls_passed)
        self.assertEqual(controls.passed_count, len(CONTROL_NAMES))
        self.assertEqual(controls.failed_control_names, ())


@unittest.skipUnless(_official_available(), "Package 141 official evidence unavailable")
class Package142StoreCliAndAuditTests(unittest.TestCase):
    def _append_fake_regression(self, store: Package142SpecializedThoughtStore) -> None:
        tree_hash = repository_source_tree_sha256(REPO_ROOT)
        names = (
            "targeted_package_142",
            "package_141_regressions",
            "package_132_140_boundary_regressions",
            "full_v1_discover",
            "compileall",
            "git_diff_check",
            "repository_pollution_scan",
        )
        receipt = build_hashed_record(
            Package142RegressionReceipt,
            {
                "regression_receipt_id": "",
                "regression_receipt_sha256": "",
                "schema_version": REGRESSION_SCHEMA_VERSION,
                "created_at": utc_now(),
                "baseline_commit": BASELINE_COMMIT,
                "source_head": BASELINE_COMMIT,
                "source_tree_sha256": tree_hash,
                "command_results": tuple(
                    (name, 0, sha256_payload({"test_only": name})) for name in names
                ),
                "targeted_package_142_passed": True,
                "package_141_regressions_passed": True,
                "package_132_140_boundary_regressions_passed": True,
                "full_v1_discover_passed": True,
                "compileall_passed": True,
                "git_diff_check_passed": True,
                "repository_pollution_absent": True,
                "fresh_regressions_passed": True,
                "source_record_refs": ("test_only:explicit_package_142_regression_receipt",),
            },
            id_field="regression_receipt_id",
            hash_field="regression_receipt_sha256",
            prefix="specialized_regressions",
        )
        store.append_once("package_142_regression_receipts", receipt)

    def test_store_is_append_only_and_has_no_authority_tables(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            store = Package142SpecializedThoughtStore(temp)
            preflight = load_package_142_preflight(
                ashl_root=REPO_ROOT,
                package_141_state_dir=PACKAGE_141_STATE,
            )
            store.append_once(
                "specialized_thought_consumer_bindings",
                preflight.consumer_binding,
            )
            store.append_once(
                "specialized_thought_consumer_bindings",
                preflight.consumer_binding,
            )
            self.assertEqual(store.count("specialized_thought_consumer_bindings"), 1)
            with self.assertRaises(TypeError):
                store.update()
            with self.assertRaises(TypeError):
                store.delete()
            with self.assertRaises(TypeError):
                store.replace()
            integrity = store.audit_integrity()
            self.assertTrue(integrity["valid"])
            self.assertFalse(integrity["authority_table_present"])

    def test_runtime_state_must_be_external(self) -> None:
        with self.assertRaisesRegex(ValueError, "outside the Git repository"):
            load_package_142_preflight(
                ashl_root=REPO_ROOT,
                package_141_state_dir=PACKAGE_141_STATE,
                state_dir=REPO_ROOT / "forbidden_package_142_state",
                append=True,
            )

    def test_corrupt_package_141_payload_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / "package_141_instinct_layer_runtime_v0"
            target.mkdir()
            database = target / "package_141.sqlite3"
            shutil.copy2(
                PACKAGE_141_STATE
                / "package_141_instinct_layer_runtime_v0"
                / "package_141.sqlite3",
                database,
            )
            connection = sqlite3.connect(database)
            try:
                connection.execute(
                    "UPDATE bounded_instinct_signals SET payload_sha256 = ? WHERE row_id = 1",
                    ("0" * 64,),
                )
                connection.commit()
            finally:
                connection.close()
            with self.assertRaisesRegex(RuntimeError, "corrupt_package_141_payload"):
                load_package_141_evidence(root)

    def test_existing_operator_stream_accepts_events_and_failure_is_visible(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            preflight = load_package_142_preflight(
                ashl_root=REPO_ROOT,
                package_141_state_dir=PACKAGE_141_STATE,
            )
            bundle = preflight.source.closed_bundle
            signal = {
                item.instinct_signal_id: item for item in preflight.source.signals
            }[bundle.instinct_signal_refs[0]]
            stream = LocalOperatorEventStream(LocalOperatorConsoleStore(temp))
            evaluate_specialized_precursor(
                preflight=preflight,
                family_id=CLOSED_FAMILY_ID,
                source_bundle=bundle,
                source_signal=signal,
                event_stream=stream,
            )
            kinds = {item["event_kind"] for item in stream.list_events()}
            self.assertIn("specialized_thought_rule_evaluated", kinds)
            self.assertIn("bounded_specialized_thought_result_created", kinds)

            class BrokenStream:
                def append_event(self, **_kwargs: object) -> None:
                    raise RuntimeError("visible_package_142_delivery_failure")

            with self.assertRaisesRegex(RuntimeError, "visible_package_142_delivery_failure"):
                evaluate_specialized_precursor(
                    preflight=preflight,
                    family_id=CLOSED_FAMILY_ID,
                    source_bundle=bundle,
                    source_signal=signal,
                    event_stream=BrokenStream(),  # type: ignore[arg-type]
                )

    def test_cli_preflight_and_show_commands_execute(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(
                    package_142_cli(
                        [
                            "preflight",
                            "--ashl-root",
                            str(REPO_ROOT),
                            "--state-dir",
                            temp,
                            "--package-141-state-dir",
                            str(PACKAGE_141_STATE),
                        ]
                    ),
                    0,
                )
                self.assertEqual(package_142_cli(["show-families", "--state-dir", temp]), 0)

    def test_end_to_end_real_package_141_evidence_and_audit(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            runtime = run_specialized_thought_suite(
                ashl_root=REPO_ROOT,
                state_dir=temp,
                package_141_state_dir=PACKAGE_141_STATE,
            )
            self.assertTrue(runtime["deterministic_repeat_verified"])
            self.assertEqual(
                runtime["conflict_status"],
                "unresolved_cross_family_conflict_preserved",
            )
            self.assertEqual(
                runtime["package_141_source_sha256_before"],
                runtime["package_141_source_sha256_after"],
            )
            preflight = load_package_142_preflight(
                ashl_root=REPO_ROOT,
                package_141_state_dir=PACKAGE_141_STATE,
            )
            store = Package142SpecializedThoughtStore(temp)
            controls = run_package_142_boundary_controls(
                preflight,
                ashl_root=REPO_ROOT,
                append_to=store,
            )
            self.assertTrue(controls.controls_passed)
            self._append_fake_regression(store)
            audit = audit_package_142_specialized_thought(
                ashl_root=REPO_ROOT,
                state_dir=temp,
                package_141_state_dir=PACKAGE_141_STATE,
            )
            self.assertEqual(audit.audit_status, PASS_STATUS)
            self.assertTrue(audit.package_141_source_read_only_verified)
            self.assertTrue(audit.deterministic_repeat_verified)
            self.assertTrue(audit.cross_family_conflict_preserved)
            self.assertEqual(audit.dangling_specialized_result_count, 0)
            self.assertFalse(audit.recursive_thought_created)
            self.assertFalse(audit.workspace_created)
            self.assertFalse(audit.selected_action_created)
            self.assertFalse(audit.memory_write_created)
            self.assertFalse(audit.output_created)
            self.assertFalse(audit.package_143_implemented)


class Package142RepositoryBoundaryTests(unittest.TestCase):
    def test_runtime_does_not_import_perception_drive_readback_action_or_legacy_thought(self) -> None:
        paths = tuple((REPO_ROOT / "ashl_core_v1" / "thought").glob("*specialized_thought*.py"))
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
            "ashl_core_v1.state.self_state_readback",
            "ashl_core_v1.task",
            "ashl_core_v1.host_body",
            "ashl_core_v1.thought.types",
        )
        self.assertFalse(
            tuple(name for name in imported if name.startswith(forbidden_prefixes))
        )

    def test_package_143_workspace_exists_without_package_144_or_full_engine(self) -> None:
        thought_files = {
            path.name for path in (REPO_ROOT / "ashl_core_v1" / "thought").glob("*.py")
        }
        self.assertIn("coarse_thought_workspace_types.py", thought_files)
        self.assertIn("package_143_coarse_workspace_runtime.py", thought_files)
        self.assertNotIn("package_144_deliberation_runtime.py", thought_files)
        self.assertNotIn("full_thought_engine.py", thought_files)

    def test_registry_and_route_advance_only_to_143(self) -> None:
        registry = json.loads(
            (
                REPO_ROOT
                / "ashl_core_v1"
                / "docs"
                / "reference"
                / "package_number_registry_v0.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(registry["current_package_id"], "143")
        self.assertEqual(registry["package_status"]["142"], "completed")
        self.assertEqual(registry["package_status"]["143"], "completed")
        self.assertEqual(registry["package_status"]["144"], "next_critical_path")
        self.assertIn("142", registry["completed_package_ids"])
        self.assertNotIn("142", registry["future_package_ids"])
        route = (
            REPO_ROOT
            / "ashl_core_v1"
            / "docs"
            / "reference"
            / "package_123_to_daily_runtime_revised_route_v0.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Package 142 is completed", route)
        self.assertIn("Package 143 is completed", route)
        self.assertIn("Package 144 is next", route)
        self.assertIn("Package 143 does not implement Package 144", route)


if __name__ == "__main__":
    unittest.main()
