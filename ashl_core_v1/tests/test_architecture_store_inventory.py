import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.tools.architecture_store_inventory import build_store_surface_inventory


class ArchitectureStoreInventoryTests(unittest.TestCase):
    def test_store_inventory_discovers_tables_and_store_apis(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            runtime = root / "ashl_core_v1" / "runtime"
            runtime.mkdir(parents=True)
            (runtime / "sample_store.py").write_text(
                """
import sqlite3
STORE_FILENAME = "sample.sqlite3"
class SampleStore:
    def __init__(self, state_dir):
        if state_dir is None:
            raise ValueError("explicit state_dir is required")
    def append_sample(self): pass
    def get_sample(self): pass
    def delete_sample(self): pass
SQL = "CREATE TABLE IF NOT EXISTS sample_records (sample_id TEXT PRIMARY KEY)"
""",
                encoding="utf-8",
            )

            records = build_store_surface_inventory(root)
            self.assertEqual(len(records), 1)
            record = records[0]
            self.assertIn("sample_records", record.table_names)
            self.assertIn("append_sample", record.write_callables)
            self.assertIn("get_sample", record.read_callables)
            self.assertIn("delete_sample", record.delete_callables)
            self.assertTrue(record.explicit_state_dir_required)
            self.assertIn("delete_callable_present_review_required", record.store_risks)


if __name__ == "__main__":
    unittest.main()
