import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.runtime.package_124_milestone_certificate import (
    build_package_124_certificate,
    validate_package_124_certificate,
    write_package_124_certificate,
)


class Package124CertificateTests(unittest.TestCase):
    def test_certificate_hash_validates(self):
        source_audit = {
            "identity": {"identity_hash": "identity"},
            "audit": {"audit_id": "audit"},
        }
        certificate = build_package_124_certificate(
            source_audit=source_audit,
            archive_manifest_sha256="manifest",
            provenance_graph_sha256="graph",
        )
        with tempfile.TemporaryDirectory() as tmp:
            write_package_124_certificate(certificate, Path(tmp))
            validation = validate_package_124_certificate(tmp)
            self.assertTrue(validation["valid"])

    def test_tampered_certificate_fails(self):
        source_audit = {
            "identity": {"identity_hash": "identity"},
            "audit": {"audit_id": "audit"},
        }
        certificate = build_package_124_certificate(
            source_audit=source_audit,
            archive_manifest_sha256="manifest",
            provenance_graph_sha256="graph",
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = write_package_124_certificate(certificate, Path(tmp))
            text = path.read_text(encoding="utf-8").replace("8c38918", "badcafe")
            path.write_text(text, encoding="utf-8")
            validation = validate_package_124_certificate(tmp)
            self.assertFalse(validation["valid"])


if __name__ == "__main__":
    unittest.main()
