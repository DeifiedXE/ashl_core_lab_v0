import json
import tempfile
import unittest
from pathlib import Path

from ashl_core.persistence import append_jsonl, ensure_parent_dir, read_jsonl


class PersistenceTests(unittest.TestCase):
    def test_append_jsonl_creates_parent_and_writes_utf8(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "nested" / "items.jsonl"

            append_jsonl(path, {"text": "清音", "value": 1})

            self.assertTrue(path.exists())
            self.assertEqual(read_jsonl(path), [{"text": "清音", "value": 1}])
            self.assertIn("清音", path.read_text(encoding="utf-8"))

    def test_read_jsonl_missing_file_returns_empty_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(read_jsonl(Path(tmp) / "missing.jsonl"), [])

    def test_each_line_is_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "items.jsonl"

            append_jsonl(path, {"a": 1})
            append_jsonl(path, {"b": 2})

            lines = path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 2)
            self.assertEqual([json.loads(line) for line in lines], [{"a": 1}, {"b": 2}])

    def test_ensure_parent_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "a" / "b" / "items.jsonl"

            ensure_parent_dir(path)

            self.assertTrue(path.parent.exists())


if __name__ == "__main__":
    unittest.main()
