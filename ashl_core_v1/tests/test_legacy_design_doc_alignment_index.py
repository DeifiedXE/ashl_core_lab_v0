import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
V1_ROOT = ROOT / "ashl_core_v1"
DOC_PATH = V1_ROOT / "docs" / "legacy_design_doc_alignment_index_v0.md"

V1_MODULES = (
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

REQUIRED_OLD_DOCS = (
    "docs/body_motor_affordance_tendency_endocrine_reconciliation_design_v0.md",
    "docs/focus_selector_design_v0.md",
    "docs/qingyin_bridge_dual_eye_capability_perception_design_v0.md",
    "docs/qingyin_thought_system_layering_design_v0.md",
    "docs/phase0_minimal_learning_action_memory_loop_plan.md",
    "docs/state_persistence.md",
    "docs/lesson_application_boundary_review_v0.md",
    "docs/ashl_core_actual_capability_inventory_runtime_substrate_map_v0.md",
    "docs/codex_working_context_summary.md",
    "docs/phase0_line_document_index.md",
)

ALLOWED_ALIGNMENT_STATUS = {
    "aligned",
    "rename_needed",
    "historical_only",
    "design_only_reference",
    "deferred",
    "needs_review",
}

ALLOWED_REUSE_POLICY = {
    "reuse_as_design_source",
    "reuse_with_v1_terms",
    "reference_only",
    "do_not_use_for_v1_runtime",
    "defer_until_later_phase",
}

ALLOWED_OUTSIDE_V1_STATUS_PREFIXES = (
    "?? docs_archive/v1_concept_sources_2026_06_27/",
    "A  docs_archive/v1_concept_sources_2026_06_27/",
)


def _read_index() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def _alignment_rows() -> list[dict[str, str]]:
    text = _read_index()
    rows: list[dict[str, str]] = []
    in_table = False
    headers: list[str] = []
    for line in text.splitlines():
        if line.startswith("| old_doc_path |"):
            in_table = True
            headers = [cell.strip() for cell in line.strip("|").split("|")]
            continue
        if in_table and line.startswith("| ---"):
            continue
        if in_table and line.startswith("| "):
            cells = [cell.strip().strip("`") for cell in line.strip("|").split("|")]
            rows.append(dict(zip(headers, cells, strict=True)))
            continue
        if in_table:
            break
    return rows


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


class LegacyDesignDocAlignmentIndexTests(unittest.TestCase):
    def test_legacy_alignment_index_exists(self):
        self.assertTrue(DOC_PATH.is_file())

    def test_all_v1_nine_modules_have_alignment_sections(self):
        text = _read_index()

        for module_name in V1_MODULES:
            with self.subTest(module_name=module_name):
                self.assertIn(f"### {module_name}", text)

    def test_required_old_docs_listed(self):
        text = _read_index()

        for old_doc in REQUIRED_OLD_DOCS:
            with self.subTest(old_doc=old_doc):
                self.assertIn(old_doc, text)
                self.assertTrue((ROOT / old_doc).is_file())

    def test_alignment_table_has_required_columns(self):
        rows = _alignment_rows()

        self.assertGreaterEqual(len(rows), len(REQUIRED_OLD_DOCS))
        self.assertEqual(
            {
                "old_doc_path",
                "old_line_name",
                "v1_module_name",
                "alignment_status",
                "reuse_policy",
                "notes",
            },
            set(rows[0]),
        )

    def test_alignment_status_values_are_known(self):
        for row in _alignment_rows():
            with self.subTest(old_doc_path=row["old_doc_path"]):
                self.assertIn(row["alignment_status"], ALLOWED_ALIGNMENT_STATUS)

    def test_reuse_policy_values_are_known(self):
        for row in _alignment_rows():
            with self.subTest(old_doc_path=row["old_doc_path"]):
                self.assertIn(row["reuse_policy"], ALLOWED_REUSE_POLICY)

    def test_each_v1_module_has_at_least_one_alignment_row(self):
        modules_in_rows = {row["v1_module_name"] for row in _alignment_rows()}

        for module_name in V1_MODULES:
            with self.subTest(module_name=module_name):
                self.assertIn(module_name, modules_in_rows)

    def test_dataclasses_were_not_created_by_alignment_doc_package(self):
        text = _read_index()

        self.assertIn("Dataclasses implemented: false", text)

    def test_runtime_implemented_false(self):
        text = _read_index()
        runtime_init = (V1_ROOT / "runtime" / "__init__.py").read_text(encoding="utf-8")

        self.assertIn("Runtime implemented: false", text)
        self.assertNotIn("RuntimeSession", runtime_init)
        self.assertNotIn("RuntimeTick", runtime_init)
        self.assertNotIn("while True", runtime_init)

    def test_old_docs_modified_false_and_docs_moved_false(self):
        text = _read_index()

        self.assertIn("Old docs modified: false", text)
        self.assertIn("Docs moved: false", text)
        outside_v1 = [
            line
            for line in _git_status_lines()
            if " ashl_core_v1/" not in line
            and not line.startswith(ALLOWED_OUTSIDE_V1_STATUS_PREFIXES)
        ]
        renamed_or_deleted = [
            line for line in _git_status_lines() if line[:2].strip() in {"D", "R"}
        ]
        self.assertEqual([], outside_v1)
        self.assertEqual([], renamed_or_deleted)

    def test_old_repo_imported_false(self):
        text = _read_index()

        self.assertIn("Old repo imported: false", text)
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
