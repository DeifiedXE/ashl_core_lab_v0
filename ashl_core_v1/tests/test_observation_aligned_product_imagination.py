import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
V1_ROOT = ROOT / "ashl_core_v1"
DOC_PATH = V1_ROOT / "docs" / "observation_aligned_product_imagination_v0.md"

FIRST_STAGE_CYCLE_TERMS = (
    "硬軟感知模組",
    "學習性泛化應用模組",
    "五重記憶模組",
    "思考運算模組",
    "擬態具身模組",
    "再回到硬軟感知模組",
    "擬態內分泌模組",
)

DEFERRED_MODULE_TERMS = (
    "獨立音訊模組：未來輸出口，目前只保留位置。",
    "無限制能力橋接及可操作結構視覺化編譯模組：未來外部能力感知與操作接口，目前只保留位置。",
    "稽核邊界模組：未來旁路監督者，目前只保留位置。",
)

NON_CLAIMS = (
    "這不是 runtime。",
    "這不是清音已醒來。",
    "這不是語音或聊天能力。",
    "這不是 long-term memory runtime。",
    "這不是 action execution。",
    "這不是 semantic vision。",
    "這不是舊 repo 功能搬家。",
    "這不是 proof of learning。",
)


def _read_doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def _git_status_lines() -> list[str]:
    import subprocess

    result = subprocess.run(
        ["git", "status", "--short", "--untracked-files=all"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line]


ALLOWED_OUTSIDE_V1_STATUS_PREFIXES = (
    "?? docs_archive/v1_concept_sources_2026_06_27/",
    "A  docs_archive/v1_concept_sources_2026_06_27/",
)


class ObservationAlignedProductImaginationTests(unittest.TestCase):
    def test_observation_aligned_product_imagination_doc_exists(self):
        self.assertTrue(DOC_PATH.is_file())

    def test_contains_observation_alignment_definition(self):
        text = _read_doc()

        self.assertIn("觀察對齊後，不是清音看懂世界。", text)
        self.assertIn(
            "而是硬軟感知模組產出的資料，能被學習性泛化應用模組消化，能被五重記憶模組整理，再能被思考運算模組讀回。",
            text,
        )
        for term in (
            "觀察資料",
            "可讀資料",
            "學習消化",
            "記憶化應用資料",
            "思考訊號",
            "行動訊號",
            "新觀察",
        ):
            with self.subTest(term=term):
                self.assertIn(term, text)

    def test_contains_first_stage_six_module_cycle(self):
        text = _read_doc()

        self.assertIn("## B. Internal Data Flow Imagination", text)
        for term in FIRST_STAGE_CYCLE_TERMS:
            with self.subTest(term=term):
                self.assertIn(term, text)
        self.assertIn("It must not directly replace thought decision-making", text)

    def test_contains_deferred_three_module_note(self):
        text = _read_doc()

        self.assertIn("## C. Deferred Three-Line Interface Imagination", text)
        for term in DEFERRED_MODULE_TERMS:
            with self.subTest(term=term):
                self.assertIn(term, text)
        self.assertIn("does not implement voice, bridge, or governance", text)
        self.assertIn("runtime", text)

    def test_contains_concrete_sandbox_example(self):
        text = _read_doc()

        for term in (
            "Event: 前方被擋住。",
            "blocked / front_obstacle",
            "cortisol_like",
            "norepinephrine_like",
            "這次前方行動受阻",
            "降低直接重試，傾向觀察或改向",
            "observe_or_adjust",
            "This is product imagination, not implemented capability.",
        ):
            with self.subTest(term=term):
                self.assertIn(term, text)

    def test_contains_non_claims(self):
        text = _read_doc()

        for term in NON_CLAIMS:
            with self.subTest(term=term):
                self.assertIn(term, text)

    def test_runtime_implemented_false(self):
        text = _read_doc()
        runtime_init = (V1_ROOT / "runtime" / "__init__.py").read_text(encoding="utf-8")

        self.assertIn("Runtime implemented: false", text)
        self.assertIn("Product imagination implemented as runtime: false", text)
        self.assertNotIn("RuntimeSession", runtime_init)
        self.assertNotIn("RuntimeTick", runtime_init)
        self.assertNotIn("while True", runtime_init)

    def test_dataclasses_implemented_false(self):
        text = _read_doc()

        self.assertIn("Dataclasses implemented: false", text)
        for py_file in V1_ROOT.rglob("*.py"):
            with self.subTest(py_file=py_file.relative_to(ROOT)):
                tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        decorator_names = [
                            getattr(decorator, "id", "")
                            for decorator in node.decorator_list
                            if isinstance(decorator, ast.Name)
                        ]
                        self.assertNotIn("dataclass", decorator_names)

    def test_old_repo_modified_false(self):
        text = _read_doc()
        outside_v1 = [
            line
            for line in _git_status_lines()
            if " ashl_core_v1/" not in line
            and not line.startswith(ALLOWED_OUTSIDE_V1_STATUS_PREFIXES)
        ]

        self.assertIn("Old docs modified: false", text)
        self.assertIn("Old repo imported: false", text)
        self.assertEqual([], outside_v1)

    def test_no_old_repo_imported(self):
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
