import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BLUEPRINT_PATH = (
    ROOT / "ashl_core_v1" / "docs" / "core" / "v1_master_construction_blueprint.md"
)

SIX_SYSTEMS = (
    "成長核心系統",
    "初生艙 / 家園系統",
    "教師系統",
    "連續性系統",
    "表達系統",
    "外界橋接系統",
)

PHASES = tuple(f"Phase {index}" for index in range(13))

NEXT_PACKAGES = (
    "Next 1：First-Stage Data Shapes",
    "Next 2：Blocked Manual Circulation Sample",
    "Next 3：Learning Review CLI Minimal",
    "Next 4：Memory Learning Trace Query Minimal",
    "Next 5：Fixed Circulation Runner Minimal",
)


def _git_status_lines(*paths: str) -> list[str]:
    result = subprocess.run(
        ["git", "status", "--short", "--untracked-files=all", "--", *paths],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line]


class MasterConstructionBlueprintTests(unittest.TestCase):
    def test_blueprint_exists(self):
        self.assertTrue(BLUEPRINT_PATH.is_file())

    def test_minimal_core_loop_is_present(self):
        text = BLUEPRINT_PATH.read_text(encoding="utf-8")

        for term in (
            "感知",
            "學入",
            "教師審查",
            "記憶學習追蹤",
            "記憶化應用資料",
            "思考訊號",
            "具身訊號",
            "新結果",
            "再感知",
        ):
            with self.subTest(term=term):
                self.assertIn(term, text)

    def test_six_systems_are_defined(self):
        text = BLUEPRINT_PATH.read_text(encoding="utf-8")

        for system_name in SIX_SYSTEMS:
            with self.subTest(system_name=system_name):
                self.assertIn(system_name, text)

    def test_phase_plan_is_complete(self):
        text = BLUEPRINT_PATH.read_text(encoding="utf-8")

        for phase in PHASES:
            with self.subTest(phase=phase):
                self.assertIn(phase, text)

    def test_thresholds_are_present(self):
        text = BLUEPRINT_PATH.read_text(encoding="utf-8")

        for threshold in ("門檻 A", "門檻 B", "門檻 C"):
            with self.subTest(threshold=threshold):
                self.assertIn(threshold, text)

    def test_next_package_order_is_present(self):
        text = BLUEPRINT_PATH.read_text(encoding="utf-8")

        for package_name in NEXT_PACKAGES:
            with self.subTest(package_name=package_name):
                self.assertIn(package_name, text)

    def test_no_legacy_docs_or_root_readme_modified(self):
        self.assertEqual([], _git_status_lines("docs", "README.md"))


if __name__ == "__main__":
    unittest.main()
