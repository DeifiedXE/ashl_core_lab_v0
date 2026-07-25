import argparse
import tempfile
import unittest

from ashl_core_v1.runtime.package_124a_temporal_cli import dispatch
from ashl_core_v1.tests._temporal_test_helpers import ARCHIVE, archive_available


class Package124ACliTests(unittest.TestCase):
    @unittest.skipUnless(archive_available(), "Package 124 archive not available")
    def test_compile_and_show_bundle_commands(self):
        with tempfile.TemporaryDirectory() as state_dir:
            compiled = dispatch(argparse.Namespace(command="compile-milestone-archive", archive_dir=str(ARCHIVE), state_dir=state_dir, verify_archive=False))
            shown = dispatch(argparse.Namespace(command="show-temporal-bundle", state_dir=state_dir))
        self.assertEqual(compiled["status"], "compiled")
        self.assertGreater(compiled["anchor_count"], 0)
        self.assertEqual(shown["latest_bundle"]["temporal_bundle_id"], compiled["temporal_bundle_id"])


if __name__ == "__main__":
    unittest.main()
