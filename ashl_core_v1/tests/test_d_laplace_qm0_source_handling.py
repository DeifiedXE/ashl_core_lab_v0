from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from ashl_core_v1.migration_audit.d_laplace_source_manifest import (
    build_source_manifest,
    manifests_identical,
)
from ashl_core_v1.migration_audit.d_laplace_source_reader import (
    DLaplaceSourceBoundaryError,
    open_d_laplace_source,
)
from ashl_core_v1.tests._d_laplace_qm0_test_helpers import (
    add_zip_symlink,
    build_complete_source,
    build_source_zip,
)


class DLaplaceQM0SourceHandlingTests(unittest.TestCase):
    def test_directory_source_is_inventoried_without_import(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source_path = build_complete_source(Path(temporary) / "source")
            snapshot = build_source_manifest(open_d_laplace_source(source_path))
        self.assertEqual(snapshot.source_kind, "directory")
        self.assertTrue(snapshot.authoritative_document_refs)
        self.assertGreater(len(snapshot.included_records), 0)

    def test_zip_source_is_inventoried_without_extraction(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_path = build_complete_source(root / "source")
            archive = build_source_zip(source_path, root / "D_lps.zip")
            snapshot = build_source_manifest(open_d_laplace_source(archive))
        self.assertEqual(snapshot.source_kind, "zip")
        self.assertIsNotNone(snapshot.original_archive_sha256)
        self.assertFalse((root / "D_lps").exists())

    def test_zip_path_traversal_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            archive = Path(temporary) / "bad.zip"
            with ZipFile(archive, "w") as zip_file:
                zip_file.writestr("../escape.py", "raise RuntimeError()")
            with self.assertRaises(DLaplaceSourceBoundaryError):
                open_d_laplace_source(archive)

    def test_zip_symlink_is_listed_and_not_followed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_path = build_complete_source(root / "source")
            archive = build_source_zip(source_path, root / "source.zip")
            add_zip_symlink(archive, "D_lps/external-link", "../../outside")
            snapshot = build_source_manifest(open_d_laplace_source(archive))
        link = next(
            record
            for record in snapshot.records
            if record.relative_path.endswith("external-link")
        )
        self.assertFalse(link.included_in_semantic_scan)
        self.assertEqual(link.exclusion_reason, "symlink_not_followed")

    def test_exclusions_are_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source_path = build_complete_source(Path(temporary) / "source")
            snapshot = build_source_manifest(open_d_laplace_source(source_path))
        reasons = {
            record.exclusion_reason for record in snapshot.excluded_records
        }
        self.assertTrue(any(str(reason).startswith("archived_output") for reason in reasons))
        self.assertTrue(
            any(str(reason).startswith("generated_or_environment") for reason in reasons)
        )

    def test_manifest_order_and_hash_are_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source_path = build_complete_source(Path(temporary) / "source")
            source = open_d_laplace_source(source_path)
            first = build_source_manifest(source)
            second = build_source_manifest(source)
        self.assertTrue(manifests_identical(first, second))
        self.assertEqual(
            [record.relative_path for record in first.records],
            sorted(
                (record.relative_path for record in first.records),
                key=str.casefold,
            ),
        )

    def test_file_addition_changes_manifest_without_touching_existing_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source_path = build_complete_source(Path(temporary) / "source")
            source = open_d_laplace_source(source_path)
            before = build_source_manifest(source)
            (source_path / "new.txt").write_text("new", encoding="utf-8")
            after = build_source_manifest(source)
        self.assertNotEqual(before.manifest_sha256, after.manifest_sha256)
        self.assertEqual(
            {
                record.relative_path: record.sha256
                for record in before.records
            },
            {
                record.relative_path: record.sha256
                for record in after.records
                if record.relative_path != "new.txt"
            },
        )

    def test_static_inventory_creates_no_source_pycache(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source_path = build_complete_source(Path(temporary) / "source")
            build_source_manifest(open_d_laplace_source(source_path))
            pycache = list(source_path.rglob("__pycache__"))
        self.assertEqual(pycache, [])


if __name__ == "__main__":
    unittest.main()
