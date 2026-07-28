from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.migration_audit.d_laplace_authority_scan import (
    scan_state_authority,
)
from ashl_core_v1.migration_audit.d_laplace_portability_classifier import (
    QM1_ALLOWED_KINDS,
    build_qm1_candidate_allowlist,
    classify_portable_mechanisms,
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


class DLaplaceQM0PortabilityAndAllowlistTests(unittest.TestCase):
    def _classify(self, root: Path):
        source = open_d_laplace_source(build_complete_source(root / "source"))
        manifest = build_source_manifest(source)
        dependencies = scan_static_dependencies(source, manifest.records)
        findings = (
            *dependencies.findings,
            *scan_state_authority(source, dependencies.modules),
            *scan_semantic_contamination(source, dependencies.modules),
        )
        candidates = classify_portable_mechanisms(
            dependencies.modules,
            findings,
            migration_document_refs=manifest.authoritative_document_refs,
        )
        return candidates, build_qm1_candidate_allowlist(candidates)

    def test_portable_candidate_requires_source_code_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            candidates, _ = self._classify(Path(temporary))
        portable = [
            candidate
            for candidate in candidates
            if candidate.portability_status == "portable_mechanism_candidate"
        ]
        self.assertTrue(portable)
        self.assertTrue(all(candidate.source_module_refs for candidate in portable))

    def test_documentation_only_item_is_not_reported_as_implemented(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            candidates, _ = self._classify(Path(temporary))
        counterfactual = next(
            item
            for item in candidates
            if item.mechanism_kind == "counterfactual_consequence_credit"
        )
        self.assertEqual(
            counterfactual.portability_status,
            "documentation_only_candidate",
        )
        self.assertFalse(counterfactual.source_module_refs)

    def test_anonymous_identity_remains_candidate_but_score_adapter_is_forbidden(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            candidates, _ = self._classify(Path(temporary))
        by_kind = {candidate.mechanism_kind: candidate for candidate in candidates}
        self.assertEqual(
            by_kind["anonymous_organ_registry"].portability_status,
            "portable_mechanism_candidate",
        )
        self.assertEqual(
            by_kind["synthetic_task_score_adapter"].portability_status,
            "forbidden_direct_migration",
        )

    def test_qm1_allowlist_contains_only_six_permitted_kinds(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            candidates, allowlist = self._classify(Path(temporary))
        by_id = {candidate.migration_candidate_id: candidate for candidate in candidates}
        allowed_kinds = {
            by_id[reference].mechanism_kind
            for reference in allowlist.mechanism_candidate_refs
        }
        self.assertTrue(allowed_kinds)
        self.assertLessEqual(allowed_kinds, QM1_ALLOWED_KINDS)
        self.assertFalse(allowlist.q_m1_execution_authorized)

    def test_lifecycle_action_bid_reset_and_rollback_are_not_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            candidates, allowlist = self._classify(Path(temporary))
        allowed = set(allowlist.mechanism_candidate_refs)
        by_kind = {candidate.mechanism_kind: candidate for candidate in candidates}
        for kind in (
            "organ_lifecycle_protocol",
            "ACTION_BID",
            "research_reset_fork_history_authority",
            "rollback",
        ):
            self.assertNotIn(by_kind[kind].migration_candidate_id, allowed)
        self.assertIn(
            by_kind["rollback"].migration_candidate_id,
            allowlist.unresolved_mechanism_refs,
        )

    def test_snapshot_candidate_requires_append_only_constraints(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            candidates, allowlist = self._classify(Path(temporary))
        snapshot = next(
            item for item in candidates if item.mechanism_kind == "snapshot"
        )
        self.assertIn("append_only_attempt_history", snapshot.qingyin_constraints_required)
        self.assertIn(snapshot.migration_candidate_id, allowlist.mechanism_candidate_refs)


if __name__ == "__main__":
    unittest.main()
