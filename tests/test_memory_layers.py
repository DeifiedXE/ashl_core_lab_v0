import tempfile
import unittest
from pathlib import Path

import ashl_core.memory_layers as memory_layers
from ashl_core.memory_layers import (
    append_archive_memory,
    append_long_term_memory,
    build_memory_record,
    get_memory_layer_paths,
    is_core_memory_write_allowed,
    list_archive_memory,
    list_long_term_memory,
    read_core_memory,
    read_working_memory_snapshot,
    write_working_memory_snapshot,
)


class MemoryLayersTests(unittest.TestCase):
    def test_get_memory_layer_paths_returns_four_layers(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = get_memory_layer_paths(tmp)

            self.assertEqual(set(paths), {"core", "long_term", "working", "archive"})
            self.assertEqual(paths["core"].name, "core_memory.json")
            self.assertEqual(paths["long_term"].name, "long_term_memory.jsonl")
            self.assertEqual(paths["working"].name, "working_memory.json")
            self.assertEqual(paths["archive"].name, "archive_memory.jsonl")

    def test_build_long_term_record(self):
        record = build_memory_record("long_term", "stable fact", "manual_confirmation")

        self.assertEqual(record["type"], "memory_record")
        self.assertEqual(record["layer"], "long_term")
        self.assertEqual(record["status"], "active")

    def test_build_archive_record(self):
        record = build_memory_record("archive", "old context", "manual_archive")

        self.assertEqual(record["layer"], "archive")

    def test_build_unknown_layer_returns_none(self):
        self.assertIsNone(build_memory_record("unknown", "x", "test"))

    def test_append_and_list_long_term_memory(self):
        with tempfile.TemporaryDirectory() as tmp:
            record = build_memory_record("long_term", "confirmed item", "manual_confirmation")

            append_long_term_memory(tmp, record)

            self.assertEqual(list_long_term_memory(tmp), [record])
            self.assertTrue((Path(tmp) / "long_term_memory.jsonl").exists())

    def test_list_long_term_missing_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(list_long_term_memory(tmp), [])

    def test_write_and_read_working_memory_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            snapshot = {"session": "test", "recent_inputs": ["a", "b"]}

            write_working_memory_snapshot(tmp, snapshot)

            self.assertEqual(read_working_memory_snapshot(tmp), snapshot)
            self.assertTrue((Path(tmp) / "working_memory.json").exists())

    def test_read_working_memory_missing_returns_empty_dict(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(read_working_memory_snapshot(tmp), {})

    def test_append_and_list_archive_memory(self):
        with tempfile.TemporaryDirectory() as tmp:
            record = build_memory_record("archive", "archived item", "manual_archive")

            append_archive_memory(tmp, record)

            self.assertEqual(list_archive_memory(tmp), [record])
            self.assertTrue((Path(tmp) / "archive_memory.jsonl").exists())

    def test_list_archive_missing_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(list_archive_memory(tmp), [])

    def test_read_core_memory_missing_returns_empty_dict(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(read_core_memory(tmp), {})

    def test_disallowed_core_memory_sources(self):
        for source in [
            "normal_user_input",
            "memory_candidate",
            "correction_label",
            "rule_candidate",
            "trial_suggestion",
            "trial_feedback",
        ]:
            with self.subTest(source=source):
                self.assertFalse(is_core_memory_write_allowed(source))

    def test_manual_versioned_update_can_write_core_memory(self):
        self.assertTrue(is_core_memory_write_allowed("manual_versioned_update"))

    def test_no_write_core_memory_function_exists(self):
        self.assertFalse(hasattr(memory_layers, "write_core_memory"))


if __name__ == "__main__":
    unittest.main()
