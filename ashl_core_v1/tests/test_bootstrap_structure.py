import ast
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
V1_ROOT = ROOT / "ashl_core_v1"

CORE_LINE_FOLDERS = (
    "spine",
    "body",
    "thought",
    "memory",
    "perception",
    "bridge",
    "endocrine",
    "voice",
    "lesson",
)

SUPPORT_FOLDERS = (
    "governance",
    "runtime",
    "tests",
    "docs",
)

EXPECTED_INIT_FILES = (
    "__init__.py",
    "spine/__init__.py",
    "body/__init__.py",
    "thought/__init__.py",
    "memory/__init__.py",
    "perception/__init__.py",
    "bridge/__init__.py",
    "endocrine/__init__.py",
    "voice/__init__.py",
    "lesson/__init__.py",
    "governance/__init__.py",
    "runtime/__init__.py",
)

LEGACY_SENTINELS = (
    "ashl_core",
    "docs",
    "tests",
    "run_all_smoke_tests.py",
    "README.md",
)

ALLOWED_OUTSIDE_V1_STATUS_PATHS = (
    "docs_archive/",
    "docs_archive/v1_concept_sources_2026_06_27/",
)


def _git_status_paths() -> list[str]:
    result = subprocess.run(
        ["git", "status", "--short"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    paths: list[str] = []
    for line in result.stdout.splitlines():
        if not line:
            continue
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1].strip()
        paths.append(path.replace("\\", "/"))
    return paths


class CleanRewriteBootstrapStructureTests(unittest.TestCase):
    def test_ashl_core_v1_exists(self):
        self.assertTrue(V1_ROOT.is_dir())

    def test_all_line_folders_exist(self):
        for folder in CORE_LINE_FOLDERS:
            with self.subTest(folder=folder):
                self.assertTrue((V1_ROOT / folder).is_dir())

    def test_support_folders_exist(self):
        for folder in SUPPORT_FOLDERS:
            with self.subTest(folder=folder):
                self.assertTrue((V1_ROOT / folder).is_dir())

    def test_package_init_files_exist(self):
        for file_name in EXPECTED_INIT_FILES:
            with self.subTest(file_name=file_name):
                self.assertTrue((V1_ROOT / file_name).is_file())

    def test_bootstrap_doc_created(self):
        doc = V1_ROOT / "docs" / "clean_rewrite_bootstrap_v1.md"

        self.assertTrue(doc.is_file())
        text = doc.read_text(encoding="utf-8")
        self.assertIn("ASHL Core Clean Rewrite Bootstrap v1", text)
        self.assertIn("old_repo_modified=False", text)
        self.assertIn("legacy_files_deleted=False", text)
        self.assertIn("No runtime loop.", text)

    def test_legacy_files_deleted_false(self):
        for path in LEGACY_SENTINELS:
            with self.subTest(path=path):
                self.assertTrue((ROOT / path).exists())

    def test_old_repo_modified_false(self):
        outside_v1 = [
            path
            for path in _git_status_paths()
            if not path.startswith("ashl_core_v1/")
            and not path.startswith(ALLOWED_OUTSIDE_V1_STATUS_PATHS)
        ]

        self.assertEqual([], outside_v1)

    def test_old_imports_changed_false(self):
        for py_file in V1_ROOT.rglob("*.py"):
            with self.subTest(py_file=py_file.relative_to(ROOT)):
                text = py_file.read_text(encoding="utf-8")
                tree = ast.parse(text, filename=str(py_file))
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

    def test_no_runtime_loop_implemented(self):
        runtime_init = (V1_ROOT / "runtime" / "__init__.py").read_text(encoding="utf-8")

        self.assertNotIn("while True", runtime_init)
        self.assertNotIn("RuntimeSession", runtime_init)
        self.assertNotIn("RuntimeTick", runtime_init)


if __name__ == "__main__":
    unittest.main()
