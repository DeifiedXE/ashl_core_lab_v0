from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.migration_audit.d_laplace_primitive_authorization_scan import (
    audit_primitive_authorization,
)
from ashl_core_v1.migration_audit.d_laplace_self_audit_gate_map import (
    build_self_audit_gate_map,
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


class DLaplaceQM0PrimitiveAndGateMapTests(unittest.TestCase):
    def _context(self, root: Path, *, remove_primitive: bool = False):
        source_path = build_complete_source(root / "source")
        if remove_primitive:
            (source_path / "src" / "dlp" / "primitive.py").unlink()
        source = open_d_laplace_source(source_path)
        manifest = build_source_manifest(source)
        dependencies = scan_static_dependencies(source, manifest.records)
        return source, manifest, dependencies

    def test_unresolved_and_not_run_remain_distinct(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source, manifest, dependencies = self._context(Path(temporary))
            findings = audit_primitive_authorization(
                source,
                dependencies.modules,
                authoritative_document_refs=manifest.authoritative_document_refs,
            )
        statuses = [finding.authorization_depth_status for finding in findings]
        self.assertIn("unresolved", statuses)
        self.assertIn("not_run", statuses)
        not_run = next(
            finding
            for finding in findings
            if finding.authorization_depth_status == "not_run"
        )
        self.assertIn("NOT_RUN_not_zero", not_run.claim_effect)

    def test_suspicious_primitive_and_direct_template_downgrade_claim(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source, manifest, dependencies = self._context(Path(temporary))
            findings = audit_primitive_authorization(
                source,
                dependencies.modules,
                authoritative_document_refs=manifest.authoritative_document_refs,
            )
        self.assertTrue(
            any(
                item.authorization_depth_status
                == "suspicious_high_level_authorization"
                for item in findings
            )
        )
        self.assertTrue(
            any(
                item.authorization_depth_status == "direct_answer_template"
                for item in findings
            )
        )
        unresolved = next(
            item
            for item in findings
            if item.primitive_or_interface_id == "primitive_authorization_depth"
        )
        self.assertEqual(
            unresolved.claim_effect,
            "downgraded_due_to_unresolved_primitive_authorization",
        )

    def test_missing_primitive_manifest_blocks_clean_claim(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source, manifest, dependencies = self._context(
                Path(temporary),
                remove_primitive=True,
            )
            findings = audit_primitive_authorization(
                source,
                dependencies.modules,
                authoritative_document_refs=manifest.authoritative_document_refs,
            )
        manifest_finding = next(
            item
            for item in findings
            if item.primitive_or_interface_id == "primitive_manifest"
        )
        self.assertEqual(
            manifest_finding.authorization_depth_status,
            "unresolved",
        )

    def test_exactly_twelve_gates_are_mapped_and_none_integrated(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            _, manifest, dependencies = self._context(Path(temporary))
            gates = build_self_audit_gate_map(
                file_records=manifest.records,
                modules=dependencies.modules,
                authoritative_document_refs=manifest.authoritative_document_refs,
            )
        self.assertEqual(len(gates), 12)
        self.assertEqual({gate.gate_number for gate in gates}, set(range(1, 13)))
        self.assertTrue(
            all(
                gate.qingyin_integration_status
                == "not_integrated_qm0_read_only"
                for gate in gates
            )
        )

    def test_missing_gate_evidence_remains_incomplete_or_inconclusive(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            _, manifest, dependencies = self._context(Path(temporary))
            gates = build_self_audit_gate_map(
                file_records=manifest.records,
                modules=dependencies.modules,
                authoritative_document_refs=manifest.authoritative_document_refs,
            )
        self.assertTrue(
            any(
                gate.source_coverage_status
                in {"partial_source_evidence", "source_evidence_absent"}
                or gate.evidence_status == "INCONCLUSIVE"
                for gate in gates
            )
        )

    def test_archived_output_reference_requires_static_parseable_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source, manifest, dependencies = self._context(Path(temporary))
            gates = build_self_audit_gate_map(
                file_records=manifest.records,
                modules=dependencies.modules,
                authoritative_document_refs=manifest.authoritative_document_refs,
                source=source,
            )
        self.assertTrue(any(gate.source_output_refs for gate in gates))


if __name__ == "__main__":
    unittest.main()
