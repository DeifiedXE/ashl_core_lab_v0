from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

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


class DLaplaceQM0StaticDependencyScanTests(unittest.TestCase):
    def _scan(self, root: Path):
        source = open_d_laplace_source(build_complete_source(root / "source"))
        manifest = build_source_manifest(source)
        return scan_static_dependencies(source, manifest.records)

    def test_local_and_external_dependencies_are_distinguished(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = self._scan(Path(temporary))
        core = next(
            module for module in result.modules if module.relative_path.endswith("core.py")
        )
        self.assertTrue(core.local_dependency_refs)
        self.assertIn("numpy", core.external_dependency_refs)
        self.assertNotIn("json", core.external_dependency_refs)

    def test_top_level_executable_call_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = self._scan(Path(temporary))
        core = next(
            module for module in result.modules if module.relative_path.endswith("core.py")
        )
        self.assertTrue(core.import_time_side_effect_risk)
        self.assertTrue(
            any(
                finding.category == "import_time_side_effect"
                and finding.relative_path.endswith("core.py")
                for finding in result.findings
            )
        )

    def test_file_write_process_network_and_unsafe_load_are_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = self._scan(Path(temporary))
        categories = {finding.category for finding in result.findings}
        self.assertIn("filesystem_write_authority", categories)
        self.assertIn("process_or_shell_authority", categories)
        self.assertIn("network_authority", categories)
        self.assertIn("unsafe_serialized_execution", categories)

    def test_blocking_findings_have_contextual_ast_status(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = self._scan(Path(temporary))
        blocking = [
            finding
            for finding in result.findings
            if finding.severity.startswith("blocking_")
        ]
        self.assertTrue(blocking)
        self.assertTrue(
            all(
                finding.finding_status
                == "confirmed_dataflow_or_authority_finding"
                for finding in blocking
            )
        )

    def test_environment_seed_and_global_registry_authority_are_recorded(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = self._scan(Path(temporary))
        explanations = [finding.explanation for finding in result.findings]
        self.assertTrue(any("process environment" in item for item in explanations))
        self.assertTrue(any("global random state" in item for item in explanations))
        self.assertTrue(any("registry-like global state" in item for item in explanations))

    def test_scan_never_imports_d_laplace_modules(self) -> None:
        before = {name for name in sys.modules if name == "dlp" or name.startswith("dlp.")}
        with tempfile.TemporaryDirectory() as temporary:
            self._scan(Path(temporary))
        after = {name for name in sys.modules if name == "dlp" or name.startswith("dlp.")}
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
