import tempfile
import unittest

from ashl_core_v1.runtime.grounded_temporal_primitive_compiler import archive_tree_fingerprint, compile_package_124_archive_temporal_bundle
from ashl_core_v1.tests._temporal_test_helpers import ARCHIVE, archive_available


class Package124AArchiveCompilationTests(unittest.TestCase):
    @unittest.skipUnless(archive_available(), "Package 124 archive not available")
    def test_archive_compilation_creates_temporal_records_without_modifying_archive(self):
        before = archive_tree_fingerprint(ARCHIVE)
        with tempfile.TemporaryDirectory() as state_dir:
            result = compile_package_124_archive_temporal_bundle(
                archive_dir=ARCHIVE,
                state_dir=state_dir,
                persist=True,
                verify_archive=False,
            )
            after = archive_tree_fingerprint(ARCHIVE)
        visual = [item for item in result.spans if item.span_kind == "observed_change_region"]
        audio = [item for item in result.spans if item.span_kind == "observed_energy_region"]
        overlaps = [item for item in result.relations if item.overlap_ns and item.overlap_ns > 0]
        self.assertEqual(len(visual), 8)
        self.assertEqual(len(audio), 4)
        self.assertEqual(len(overlaps), 4)
        self.assertEqual(result.continuity_records[0].complete_window_count, 24)
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
