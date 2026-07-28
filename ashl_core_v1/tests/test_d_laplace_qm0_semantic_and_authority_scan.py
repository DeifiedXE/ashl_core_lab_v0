from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.migration_audit.d_laplace_authority_scan import (
    scan_state_authority,
)
from ashl_core_v1.migration_audit.d_laplace_semantic_contamination_scan import (
    scan_semantic_contamination,
)
from ashl_core_v1.migration_audit.d_laplace_source_manifest import (
    build_source_manifest,
)
from ashl_core_v1.migration_audit.d_laplace_source_reader import (
    open_d_laplace_source,
)
from ashl_core_v1.migration_audit.d_laplace_static_dependency_scan import (
    scan_static_dependencies,
)
from ashl_core_v1.tests._d_laplace_qm0_test_helpers import (
    build_complete_source,
)


class DLaplaceQM0SemanticAndAuthorityScanTests(unittest.TestCase):
    def _results(self, root: Path):
        source = open_d_laplace_source(build_complete_source(root / "source"))
        manifest = build_source_manifest(source)
        dependencies = scan_static_dependencies(source, manifest.records)
        return (
            scan_semantic_contamination(source, dependencies.modules),
            scan_state_authority(source, dependencies.modules),
        )

    def test_synthetic_world_and_fixed_score_are_not_portable_core(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            semantic, _ = self._results(Path(temporary))
        categories = {finding.category for finding in semantic}
        self.assertIn("synthetic_world_semantics", categories)
        self.assertIn("synthetic_task_score_semantics", categories)

    def test_family_flow_to_selector_is_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            semantic, _ = self._results(Path(temporary))
        family = [
            finding
            for finding in semantic
            if finding.category == "family_semantic_leakage"
        ]
        self.assertTrue(family)
        self.assertTrue(
            all(
                finding.severity == "blocking_for_direct_migration"
                for finding in family
            )
        )

    def test_verified_analysis_non_interference_is_counter_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            semantic, _ = self._results(Path(temporary))
        analysis = [
            finding
            for finding in semantic
            if finding.category == "human_analysis_tag_runtime_leakage"
        ]
        self.assertTrue(
            any(
                finding.finding_status == "bounded_counter_evidence"
                and finding.severity == "informational"
                for finding in analysis
            )
        )
        self.assertFalse(
            any(
                finding.severity == "blocking_for_direct_migration"
                and finding.relative_path.endswith("analysis.py")
                for finding in analysis
            )
        )

    def test_comment_alone_does_not_prove_or_create_runtime_isolation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_path = build_complete_source(root / "source")
            (source_path / "src" / "dlp" / "comments.py").write_text(
                "# family analysis_tag enters proposer, but this is only a comment\n",
                encoding="utf-8",
            )
            source = open_d_laplace_source(source_path)
            manifest = build_source_manifest(source)
            dependencies = scan_static_dependencies(source, manifest.records)
            findings = scan_semantic_contamination(source, dependencies.modules)
        self.assertFalse(
            any(finding.relative_path.endswith("comments.py") for finding in findings)
        )

    def test_teacher_rule_creating_organ_is_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            semantic, _ = self._results(Path(temporary))
        self.assertTrue(
            any(
                finding.category == "teacher_rule_leakage"
                and finding.severity == "blocking_for_direct_migration"
                for finding in semantic
            )
        )

    def test_reset_fork_and_history_overwrite_are_not_qm1_safe(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            _, authority = self._results(Path(temporary))
        categories = {finding.category for finding in authority}
        self.assertIn("reset_authority", categories)
        self.assertIn("fork_authority", categories)
        self.assertIn("history_overwrite_authority", categories)
        self.assertTrue(
            all(
                finding.severity == "blocking_for_qm1"
                for finding in authority
                if finding.category
                in {
                    "reset_authority",
                    "fork_authority",
                    "history_overwrite_authority",
                }
            )
        )


if __name__ == "__main__":
    unittest.main()
