import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.runtime.package_124_archive_manifest import (
    build_archive_manifest,
    verify_archive_manifest,
    write_archive_manifest,
)


class Package124ArchiveReverificationTests(unittest.TestCase):
    def test_manifest_reverification_rejects_missing_archived_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state = root / "source_state"
            state.mkdir()
            archived = state / "record.json"
            archived.write_text('{"kind":"evidence"}', encoding="utf-8")
            write_archive_manifest(build_archive_manifest(root, source_state_dir=state), root)
            archived.unlink()
            verification = verify_archive_manifest(root)
            self.assertFalse(verification["valid"])
            self.assertIn("missing_file:source_state/record.json", verification["failure_reasons"])


if __name__ == "__main__":
    unittest.main()
