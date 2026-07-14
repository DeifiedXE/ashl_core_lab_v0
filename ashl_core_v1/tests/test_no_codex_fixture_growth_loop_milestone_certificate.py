import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from ashl_core_v1.runtime.no_codex_fixture_growth_loop_milestone_audit import (
    PACKAGE_COMMITS,
    build_no_codex_fixture_growth_loop_milestone_audit,
    issue_no_codex_fixture_growth_loop_milestone_certificate,
    validate_no_codex_fixture_growth_loop_milestone_certificate,
)
from ashl_core_v1.runtime.no_codex_two_cycle_fixture_growth_run import (
    run_two_cycle_fixture_growth_demo,
)
from ashl_core_v1.runtime.session_learning_evidence_identity import FULL_COMMIT_APPROVAL_SCOPE


def _build_two_cycle_run() -> tuple[tempfile.TemporaryDirectory, Path, str]:
    directory = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
    state_dir = Path(directory.name)
    result = run_two_cycle_fixture_growth_demo(
        teacher_decision="approved",
        approval_scope=FULL_COMMIT_APPROVAL_SCOPE,
        teacher_approval_text="I approve this exact reviewed evidence for interpretation and working readback.",
        reason_code="teacher_verified_exact_evidence",
        state_dir=state_dir,
    )
    return directory, state_dir, str(result["run_id"])


class NoCodexFixtureGrowthLoopMilestoneCertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._directory, cls.state_dir, cls.run_id = _build_two_cycle_run()
        cls.audit = build_no_codex_fixture_growth_loop_milestone_audit(
            state_dir=cls.state_dir,
            run_id=cls.run_id,
        )
        cls.certificate_path = cls.state_dir / "fixture_loop_certificate.json"
        cls.certificate = issue_no_codex_fixture_growth_loop_milestone_certificate(
            audit=cls.audit,
            output_path=cls.certificate_path,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls._directory.cleanup()

    def test_certificate_requires_passed_audit(self) -> None:
        blocked_audit = replace(self.audit, audit_status="blocked_missing_authoritative_evidence")
        with self.assertRaises(ValueError):
            issue_no_codex_fixture_growth_loop_milestone_certificate(
                audit=blocked_audit,
                output_path=self.state_dir / "blocked.json",
            )

    def test_certificate_contains_required_evidence_and_commits(self) -> None:
        self.assertEqual(tuple(self.certificate.package_commits), PACKAGE_COMMITS)
        self.assertTrue(self.certificate.evidence_record_ids)
        self.assertTrue(self.certificate.source_trace_refs)
        self.assertIn("teacher-gated", self.certificate.capability_claim)
        self.assertIn("no external control", self.certificate.scope_limits)

    def test_certificate_hash_is_deterministic_and_validates(self) -> None:
        first = validate_no_codex_fixture_growth_loop_milestone_certificate(self.certificate_path)
        second = validate_no_codex_fixture_growth_loop_milestone_certificate(self.certificate_path)
        self.assertTrue(first["valid"])
        self.assertEqual(first["certificate_sha256"], second["certificate_sha256"])

    def test_tampered_certificate_fails_validation(self) -> None:
        data = json.loads(self.certificate_path.read_text(encoding="utf-8"))
        data["capability_claim"] = data["capability_claim"] + " Tampered."
        tampered_path = self.state_dir / "tampered_certificate.json"
        tampered_path.write_text(json.dumps(data, sort_keys=True), encoding="utf-8")
        result = validate_no_codex_fixture_growth_loop_milestone_certificate(tampered_path)
        self.assertFalse(result["valid"])
        self.assertIn("certificate_hash_mismatch", result["reasons"])


if __name__ == "__main__":
    unittest.main()
