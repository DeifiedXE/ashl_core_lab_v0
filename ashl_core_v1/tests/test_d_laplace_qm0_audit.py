from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from ashl_core_v1.migration_audit import (
    D_LAPLACE_QM0_AUDIT_STATUS,
    QINGYIN_MIGRATION_STATUS,
)
from ashl_core_v1.migration_audit.d_laplace_qm0_audit import (
    ASHL_BASELINE_COMMIT,
    DLaplaceQM0BlockedError,
    run_qm0_read_only_audit,
    verify_stored_source_unchanged,
)
from ashl_core_v1.migration_audit.d_laplace_qm0_store import STORE_DIRNAME
from ashl_core_v1.tests._d_laplace_qm0_test_helpers import (
    build_complete_source,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


class DLaplaceQM0AuditTests(unittest.TestCase):
    def test_full_directory_audit_passes_without_migration(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = build_complete_source(root / "source")
            state = root / "state"
            with patch(
                "ashl_core_v1.migration_audit.d_laplace_qm0_audit."
                "_ashl_changed_paths",
                return_value=tuple(),
            ):
                report = run_qm0_read_only_audit(
                    ashl_root=REPO_ROOT,
                    d_laplace_source=source,
                    state_dir=state,
                )
        audit = report["audit"]
        self.assertEqual(audit["ashl_baseline_commit"], ASHL_BASELINE_COMMIT)
        self.assertTrue(audit["package_125_baseline_verified"])
        self.assertEqual(audit["qm0_audit_status"], D_LAPLACE_QM0_AUDIT_STATUS)
        self.assertEqual(
            audit["qingyin_migration_status"],
            QINGYIN_MIGRATION_STATUS,
        )
        self.assertTrue(audit["source_unchanged"])
        self.assertEqual(audit["self_audit_gate_count"], 12)
        self.assertEqual(audit["self_audit_gate_integrated_count"], 0)
        self.assertEqual(audit["self_audit_gate_incomplete_count"], 12)

    def test_source_status_preserves_all_four_dimensions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with patch(
                "ashl_core_v1.migration_audit.d_laplace_qm0_audit."
                "_ashl_changed_paths",
                return_value=tuple(),
            ):
                report = run_qm0_read_only_audit(
                    ashl_root=REPO_ROOT,
                    d_laplace_source=build_complete_source(root / "source"),
                    state_dir=root / "state",
                )
        status = report["source_status"]
        self.assertEqual(status["synthetic_phase"], "COMPLETED")
        self.assertEqual(status["real_world_r_track"], "NOT ENTERED")
        self.assertEqual(status["primitive_authorization_depth"], "unresolved")
        self.assertEqual(status["overall_scope"], "SYNTHETIC RESEARCH CLOSED")

    def test_generic_completed_status_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = build_complete_source(root / "source")
            for document in source.glob("*.md"):
                document.write_text("D-Laplace completed\n", encoding="utf-8")
            with self.assertRaises(DLaplaceQM0BlockedError):
                run_qm0_read_only_audit(
                    ashl_root=REPO_ROOT,
                    d_laplace_source=source,
                    state_dir=root / "state",
                )

    def test_missing_authoritative_document_blocks_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = build_complete_source(root / "source")
            (source / "00_START_HERE.md").unlink()
            with self.assertRaises(DLaplaceQM0BlockedError) as raised:
                run_qm0_read_only_audit(
                    ashl_root=REPO_ROOT,
                    d_laplace_source=source,
                    state_dir=root / "state",
                )
        self.assertIn("missing_authoritative_document", str(raised.exception))

    def test_generated_bundle_is_external_and_complete(self) -> None:
        expected = {
            "qm0_audit.sqlite3",
            "source_manifest.json",
            "exclusion_manifest.json",
            "dependency_graph.json",
            "contamination_findings.json",
            "primitive_authorization_findings.json",
            "self_audit_gate_coverage.json",
            "portability_map.json",
            "ashl_substitution_map.json",
            "qm1_candidate_allowlist.json",
            "qm0_report.json",
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            state = root / "state"
            run_qm0_read_only_audit(
                ashl_root=REPO_ROOT,
                d_laplace_source=build_complete_source(root / "source"),
                state_dir=state,
            )
            generated = {path.name for path in (state / STORE_DIRNAME).iterdir()}
        self.assertEqual(generated, expected)
        self.assertFalse((REPO_ROOT / "ashl_core_v1" / "data").exists())

    def test_stored_manifest_detects_later_source_change(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = build_complete_source(root / "source")
            state = root / "state"
            run_qm0_read_only_audit(
                ashl_root=REPO_ROOT,
                d_laplace_source=source,
                state_dir=state,
            )
            unchanged = verify_stored_source_unchanged(
                state_dir=state,
                d_laplace_source=source,
            )
            (source / "tampered.txt").write_text("tampered", encoding="utf-8")
            changed = verify_stored_source_unchanged(
                state_dir=state,
                d_laplace_source=source,
            )
        self.assertTrue(unchanged["source_unchanged"])
        self.assertFalse(changed["source_unchanged"])
        self.assertTrue(changed["source_file_added"])

    def test_all_runtime_and_behavior_boundaries_remain_false(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with patch(
                "ashl_core_v1.migration_audit.d_laplace_qm0_audit."
                "_ashl_changed_paths",
                return_value=tuple(),
            ):
                report = run_qm0_read_only_audit(
                    ashl_root=REPO_ROOT,
                    d_laplace_source=build_complete_source(root / "source"),
                    state_dir=root / "state",
                )
        boundaries = report["boundaries"]
        for name in (
            "d_laplace_code_imported",
            "d_laplace_code_executed",
            "d_laplace_experiment_started",
            "organ_created",
            "organ_migrated",
            "ashl_runtime_modified",
            "qingyin_behavior_modified",
            "package_125_behavior_changed",
            "package_126_implemented",
            "memory_write",
            "output",
        ):
            self.assertFalse(boundaries[name], name)
        self.assertEqual(boundaries["llm_runtime_calls"], 0)
        self.assertEqual(boundaries["codex_runtime_calls"], 0)
        self.assertEqual(boundaries["network_runtime_calls"], 0)


if __name__ == "__main__":
    unittest.main()
