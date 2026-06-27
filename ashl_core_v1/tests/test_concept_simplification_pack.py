import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CORE_DOCS = ROOT / "ashl_core_v1" / "docs" / "core"
ARCHIVE_ROOT = ROOT / "docs_archive" / "v1_concept_sources_2026_06_27"

EXPECTED_CORE_DOCS = (
    "v1_core_overview.md",
    "v1_module_requirements.md",
    "v1_learning_memory_flow.md",
    "v1_deferred_lines.md",
    "v1_concept_source_map.md",
    "v1_doc_authority.md",
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


class ConceptSimplificationPackTests(unittest.TestCase):
    def test_core_docs_exist(self):
        for doc_name in EXPECTED_CORE_DOCS:
            with self.subTest(doc_name=doc_name):
                self.assertTrue((CORE_DOCS / doc_name).is_file())

    def test_archive_manifest_exists(self):
        self.assertTrue((ARCHIVE_ROOT / "concept_archive_manifest_v0.md").is_file())
        self.assertTrue((ARCHIVE_ROOT / "concept_archive_manifest_v0.json").is_file())

    def test_archive_contains_source_files(self):
        archived_files = [path for path in ARCHIVE_ROOT.rglob("*") if path.is_file()]

        self.assertGreaterEqual(len(archived_files), 69)

    def test_doc_authority_points_to_core_first(self):
        text = (CORE_DOCS / "v1_doc_authority.md").read_text(encoding="utf-8")

        self.assertIn("ashl_core_v1/docs/core/v1_core_overview.md", text)
        self.assertIn("docs_archive/v1_concept_sources_2026_06_27/**", text)

    def test_old_docs_and_root_readme_not_modified(self):
        self.assertEqual([], _git_status_lines("docs", "README.md"))


if __name__ == "__main__":
    unittest.main()
