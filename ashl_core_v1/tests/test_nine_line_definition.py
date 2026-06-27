import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
V1_ROOT = ROOT / "ashl_core_v1"
DOC_PATH = V1_ROOT / "docs" / "nine_line_definition_v0.md"

NINE_MODULES = (
    "擬態具身模組",
    "思考運算模組",
    "五重記憶模組",
    "硬軟感知模組",
    "無限制能力橋接及可操作結構視覺化編譯模組",
    "擬態內分泌模組",
    "獨立音訊模組",
    "學習性泛化應用模組",
    "稽核邊界模組",
)

FIRST_STAGE_MODULES = (
    "思考運算模組",
    "擬態具身模組",
    "硬軟感知模組",
    "學習性泛化應用模組",
    "五重記憶模組",
    "擬態內分泌模組",
)

DEFERRED_MODULES = (
    "獨立音訊模組",
    "無限制能力橋接及可操作結構視覺化編譯模組",
    "稽核邊界模組",
)

MAIN_CYCLE_TERMS = (
    "擬態具身模組\n→ 行動訊號 / 身體輸出",
    "→ 硬軟感知模組 / 無限制能力橋接模組 / 獨立音訊模組",
    "→ 學習性泛化應用模組",
    "→ 五重記憶模組",
    "→ 思考運算模組",
    "→ 進入下一輪循環",
)


def _read_definition() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


class NineLineDefinitionAlignmentTests(unittest.TestCase):
    def test_nine_line_definition_doc_exists(self):
        self.assertTrue(DOC_PATH.is_file())

    def test_all_nine_modules_defined(self):
        text = _read_definition()

        for index, module_name in enumerate(NINE_MODULES, start=1):
            with self.subTest(module_name=module_name):
                self.assertIn(f"## {index}. {module_name}", text)
                self.assertIn(module_name, text)

        self.assertEqual(9, sum(1 for line in text.splitlines() if line.startswith("## ") and ". " in line))

    def test_each_module_has_function_input_output_and_destination(self):
        text = _read_definition()

        for index, module_name in enumerate(NINE_MODULES, start=1):
            with self.subTest(module_name=module_name):
                marker = f"## {index}. {module_name}"
                start = text.index(marker)
                next_heading = text.find("\n## ", start + len(marker))
                section = text[start:] if next_heading == -1 else text[start:next_heading]
                self.assertIn("功能：", section)
                self.assertIn("輸入：", section)
                self.assertIn("輸出：", section)
                self.assertIn("接給：", section)

    def test_main_cycle_defined(self):
        text = _read_definition()

        self.assertIn("## Main Cycle", text)
        for term in MAIN_CYCLE_TERMS:
            with self.subTest(term=term):
                self.assertIn(term, text)

    def test_first_stage_six_modules_listed(self):
        text = _read_definition()
        first_stage = text.split("## v1 First Stage", 1)[1].split(
            "## Deferred Definition-Only Lines", 1
        )[0]

        for module_name in FIRST_STAGE_MODULES:
            with self.subTest(module_name=module_name):
                self.assertIn(module_name, first_stage)

    def test_deferred_three_modules_listed(self):
        text = _read_definition()
        deferred = text.split("## Deferred Definition-Only Lines", 1)[1].split(
            "## Non-Implementation Statement", 1
        )[0]

        for module_name in DEFERRED_MODULES:
            with self.subTest(module_name=module_name):
                self.assertIn(module_name, deferred)

    def test_no_runtime_implemented(self):
        text = _read_definition()
        runtime_init = (V1_ROOT / "runtime" / "__init__.py").read_text(encoding="utf-8")

        self.assertIn("Runtime implemented: false", text)
        self.assertIn("Runtime loop created: false", text)
        self.assertNotIn("RuntimeSession", runtime_init)
        self.assertNotIn("RuntimeTick", runtime_init)
        self.assertNotIn("while True", runtime_init)

    def test_no_legacy_repo_imported(self):
        for py_file in V1_ROOT.rglob("*.py"):
            with self.subTest(py_file=py_file.relative_to(ROOT)):
                tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            self.assertFalse(
                                alias.name == "ashl_core"
                                or alias.name.startswith("ashl_core.")
                            )
                    if isinstance(node, ast.ImportFrom):
                        self.assertFalse(
                            node.module == "ashl_core"
                            or (node.module or "").startswith("ashl_core.")
                        )


if __name__ == "__main__":
    unittest.main()
