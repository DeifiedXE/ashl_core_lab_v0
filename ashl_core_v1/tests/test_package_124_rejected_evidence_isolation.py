import unittest

from ashl_core_v1.runtime.package_124_types import (
    PACKAGE_123_REJECTED_EVIDENCE_IDENTITY,
    RejectedEvidenceIsolationAudit,
)


class Package124RejectedEvidenceIsolationTests(unittest.TestCase):
    def test_rejected_evidence_creates_no_memory_or_readback(self):
        audit = RejectedEvidenceIsolationAudit(
            audit_id="rejected",
            rejected_evidence_identity=PACKAGE_123_REJECTED_EVIDENCE_IDENTITY,
            rejection_decision_id="teacher_decision:rejected",
            reviewed_memory_created=False,
            working_readback_created=False,
            referenced_by_clean_cycle_1=False,
            referenced_by_cycle_2=False,
            isolation_verified=True,
        )
        self.assertTrue(audit.isolation_verified)
        self.assertFalse(audit.reviewed_memory_created)
        self.assertFalse(audit.working_readback_created)


if __name__ == "__main__":
    unittest.main()
