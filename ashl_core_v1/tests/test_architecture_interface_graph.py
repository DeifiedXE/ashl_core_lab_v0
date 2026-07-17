import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.tools.architecture_interface_graph import build_interface_connections
from ashl_core_v1.tools.architecture_module_classifier import classify_runtime_modules
from ashl_core_v1.tools.architecture_test_mapper import build_test_coverage_map


class ArchitectureInterfaceGraphTests(unittest.TestCase):
    def test_interface_graph_detects_imports_and_callable_use(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            runtime = root / "ashl_core_v1" / "runtime"
            tests = root / "ashl_core_v1" / "tests"
            runtime.mkdir(parents=True)
            tests.mkdir(parents=True)
            (runtime / "target.py").write_text("def make_record(): return 'ok'\n", encoding="utf-8")
            (runtime / "source.py").write_text(
                "from ashl_core_v1.runtime.target import make_record\n\ndef run(): return make_record()\n",
                encoding="utf-8",
            )
            (tests / "test_source.py").write_text(
                "from ashl_core_v1.runtime.source import run\n\ndef test_run(): assert run() == 'ok'\n",
                encoding="utf-8",
            )

            tests_map = build_test_coverage_map(root)
            modules = classify_runtime_modules(root, test_records=tests_map)
            records = build_interface_connections(root, module_records=modules, test_records=tests_map)
            matching = [
                record
                for record in records
                if record.source_module == "ashl_core_v1.runtime.source"
                and record.target_module == "ashl_core_v1.runtime.target"
            ]

            self.assertTrue(matching)
            self.assertTrue(matching[0].actual_import_exists)
            self.assertTrue(matching[0].actual_runtime_call_exists)

    def test_mandatory_perception_to_host_body_connection_exists_in_real_repo(self):
        root = Path(__file__).resolve().parents[2]
        records = build_interface_connections(root)
        ids = {record.connection_id for record in records}
        self.assertIn("perception_to_host_body", ids)


if __name__ == "__main__":
    unittest.main()
