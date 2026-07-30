from __future__ import annotations

import ast
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from ashl_core_v1.migration_audit import D_LAPLACE_QM0_BLOCKED_STATUS
from ashl_core_v1.migration_audit import d_laplace_qm0_cli as cli
from ashl_core_v1.tests._d_laplace_qm0_test_helpers import (
    build_complete_source,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


class DLaplaceQM0CliAndBoundaryTests(unittest.TestCase):
    def test_cli_audit_uses_human_language_first(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with (
                patch(
                    "ashl_core_v1.migration_audit.d_laplace_qm0_audit."
                    "_ashl_changed_paths",
                    return_value=tuple(),
                ),
                patch("sys.stdout", new_callable=StringIO) as output,
            ):
                status = cli.main(
                    [
                        "audit",
                        "--ashl-root",
                        str(REPO_ROOT),
                        "--d-laplace-source",
                        str(build_complete_source(root / "source")),
                        "--state-dir",
                        str(root / "state"),
                    ]
                )
            text = output.getvalue()
        self.assertEqual(status, 0)
        self.assertTrue(text.startswith("Q-M0 read-only audit passed."))
        self.assertIn("Qingyin migration remains incomplete.", text)
        self.assertIn("No D-Laplace runtime component was imported.", text)

    def test_cli_show_commands_read_generated_reports(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            state = root / "state"
            with (
                patch(
                    "ashl_core_v1.migration_audit.d_laplace_qm0_audit."
                    "_ashl_changed_paths",
                    return_value=tuple(),
                ),
                patch("sys.stdout", new_callable=StringIO),
            ):
                self.assertEqual(
                    cli.main(
                        [
                            "audit",
                            "--ashl-root",
                            str(REPO_ROOT),
                            "--d-laplace-source",
                            str(build_complete_source(root / "source")),
                            "--state-dir",
                            str(state),
                        ]
                    ),
                    0,
                )
            for command in (
                "show-source-status",
                "show-blocking-findings",
                "show-portability-map",
                "show-self-audit-gates",
                "show-ashl-substitution-map",
                "show-qm1-candidate-allowlist",
            ):
                with patch("sys.stdout", new_callable=StringIO) as output:
                    status = cli.main([command, "--state-dir", str(state)])
                self.assertEqual(status, 0, command)
                self.assertTrue(output.getvalue().strip(), command)

    def test_missing_source_returns_required_blocked_status(self) -> None:
        with tempfile.TemporaryDirectory() as temporary, patch(
            "sys.stdout",
            new_callable=StringIO,
        ) as output:
            status = cli.main(
                [
                    "audit",
                    "--ashl-root",
                    str(REPO_ROOT),
                    "--d-laplace-source",
                    str(Path(temporary) / "missing"),
                    "--state-dir",
                    str(Path(temporary) / "state"),
                ]
            )
        self.assertEqual(status, 1)
        self.assertIn(D_LAPLACE_QM0_BLOCKED_STATUS, output.getvalue())

    def test_migration_audit_source_has_no_dynamic_import_exec_or_eval(self) -> None:
        audit_root = REPO_ROOT / "ashl_core_v1" / "migration_audit"
        forbidden_calls: list[tuple[str, str]] = []
        dlp_imports: list[tuple[str, str]] = []
        for path in audit_root.glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id in {"exec", "eval", "__import__"}:
                        forbidden_calls.append((path.name, node.func.id))
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    if node.func.attr == "import_module":
                        forbidden_calls.append((path.name, node.func.attr))
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name == "dlp" or alias.name.startswith("dlp."):
                            dlp_imports.append((path.name, alias.name))
                if isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    if module == "dlp" or module.startswith("dlp."):
                        dlp_imports.append((path.name, module))
        self.assertEqual(forbidden_calls, [])
        self.assertEqual(dlp_imports, [])

    def test_qm0_remains_outside_runtime_after_package_126(self) -> None:
        self.assertTrue((REPO_ROOT / "ashl_core_v1" / "migration_audit").is_dir())
        self.assertFalse(
            (REPO_ROOT / "ashl_core_v1" / "runtime" / "d_laplace_qm0_audit.py").exists()
        )
        package_126_modules = sorted(
            (REPO_ROOT / "ashl_core_v1" / "runtime").glob("*package_126*.py")
        )
        self.assertTrue(package_126_modules)
        for path in package_126_modules:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            imported_modules = {
                alias.name
                for node in ast.walk(tree)
                if isinstance(node, ast.Import)
                for alias in node.names
            }
            imported_modules.update(
                node.module or ""
                for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom)
            )
            self.assertFalse(
                any(
                    "d_laplace" in module.casefold()
                    or module.startswith("ashl_core_v1.migration_audit")
                    for module in imported_modules
                ),
                path.name,
            )


if __name__ == "__main__":
    unittest.main()
