import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.runtime.package_124_archive_manifest import (
    build_archive_manifest,
    verify_archive_manifest,
    write_archive_manifest,
)


class Package124ArchiveTests(unittest.TestCase):
    def test_manifest_hashes_archived_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "source_state").mkdir()
            (root / "source_state" / "record.txt").write_text("evidence", encoding="utf-8")
            manifest = build_archive_manifest(root, source_state_dir=root / "source_state")
            write_archive_manifest(manifest, root)
            verification = verify_archive_manifest(root)
            self.assertTrue(verification["valid"])
            self.assertEqual(verification["file_count"], 1)

    def test_tampered_file_fails_manifest_verification(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "source_state").mkdir()
            target = root / "source_state" / "record.txt"
            target.write_text("evidence", encoding="utf-8")
            write_archive_manifest(build_archive_manifest(root, source_state_dir=root / "source_state"), root)
            target.write_text("changed", encoding="utf-8")
            verification = verify_archive_manifest(root)
            self.assertFalse(verification["valid"])

    def test_zero_byte_archived_file_is_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "source_state").mkdir()
            (root / "source_state" / "empty.sqlite3").write_bytes(b"")
            write_archive_manifest(build_archive_manifest(root, source_state_dir=root / "source_state"), root)
            verification = verify_archive_manifest(root)
            self.assertTrue(verification["valid"])


if __name__ == "__main__":
    unittest.main()
