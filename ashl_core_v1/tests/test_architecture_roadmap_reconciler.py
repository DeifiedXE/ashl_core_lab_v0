import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.tools.architecture_roadmap_reconciler import reconcile_roadmap


class ArchitectureRoadmapReconcilerTests(unittest.TestCase):
    def test_roadmap_reconciler_resolves_125_129_collision_and_assigns_unique_future_ids(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            docs = root / "ashl_core_v1" / "docs" / "reference"
            docs.mkdir(parents=True)
            (docs / "qingyin_master_roadmap_after_package_116_v0.md").write_text(
                "Package 122 completed. Active Perception route uses 125-132.\n",
                encoding="utf-8",
            )
            (docs / "qingyin_audio_line_decisions_v0.md").write_text(
                "Audio route previously used 125-129.\n",
                encoding="utf-8",
            )
            result = reconcile_roadmap(root)
            conflict = result["roadmap_conflicts"][0]
            registry = result["package_number_registry"]
            route_ids = [item["package_id"] for item in result["revised_route"]]

            self.assertEqual(conflict["resolution_status"], "resolved")
            self.assertEqual(registry["duplicate_package_ids"], [])
            self.assertIn("120A", registry["letter_suffix_package_ids"])
            self.assertIn("122A", registry["letter_suffix_package_ids"])
            self.assertEqual(route_ids.count("125"), 1)
            self.assertIn("173", route_ids)


if __name__ == "__main__":
    unittest.main()
