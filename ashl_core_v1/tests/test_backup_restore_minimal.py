import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from ashl_core_v1.runtime.backup_restore import (
    BACKUP_MANIFEST_FILE,
    create_v1_backup,
    inspect_v1_backup,
    list_v1_backups,
    restore_v1_backup,
)


ROOT = Path(__file__).resolve().parents[2]
CLI_MODULE = "ashl_core_v1.runtime.backup_restore_cli"


class BackupRestoreMinimalTests(unittest.TestCase):
    def run_cli(
        self,
        source_base_dir: Path,
        backup_dir: Path,
        *args: str,
        restore_base_dir: Path | None = None,
        check: bool = True,
    ) -> subprocess.CompletedProcess[str]:
        command = [
            sys.executable,
            "-m",
            CLI_MODULE,
            "--source-base-dir",
            str(source_base_dir),
            "--backup-dir",
            str(backup_dir),
        ]
        if restore_base_dir is not None:
            command.extend(["--restore-base-dir", str(restore_base_dir)])
        command.extend(args)
        return subprocess.run(
            command,
            cwd=ROOT,
            check=check,
            capture_output=True,
            text=True,
        )

    def seed_source(self, source_dir: Path) -> None:
        (source_dir / "data" / "daily_run").mkdir(parents=True)
        (source_dir / "data" / "daily_run" / "last_daily_run.json").write_text(
            '{"daily_run_id": "daily_001"}',
            encoding="utf-8",
        )
        (source_dir / "docs" / "reports").mkdir(parents=True)
        (source_dir / "docs" / "reports" / "report.md").write_text("report", encoding="utf-8")

    def test_create_backup_creates_zip(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source_dir = Path(temp_dir) / "source"
            backup_dir = Path(temp_dir) / "backups"
            self.seed_source(source_dir)

            result = create_v1_backup(source_dir, backup_dir)

            self.assertTrue(Path(result["backup_path"]).is_file())
            self.assertTrue(result["backup_id"].startswith("backup_"))

    def test_backup_contains_manifest(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source_dir = Path(temp_dir) / "source"
            backup_dir = Path(temp_dir) / "backups"
            self.seed_source(source_dir)

            result = create_v1_backup(source_dir, backup_dir)

            with zipfile.ZipFile(result["backup_path"], "r") as archive:
                self.assertIn(BACKUP_MANIFEST_FILE, archive.namelist())

    def test_manifest_includes_file_count(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source_dir = Path(temp_dir) / "source"
            backup_dir = Path(temp_dir) / "backups"
            self.seed_source(source_dir)

            result = create_v1_backup(source_dir, backup_dir)

            self.assertEqual(2, result["manifest"]["file_count"])

    def test_list_backups_returns_created_backup(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source_dir = Path(temp_dir) / "source"
            backup_dir = Path(temp_dir) / "backups"
            self.seed_source(source_dir)
            result = create_v1_backup(source_dir, backup_dir)

            listed = list_v1_backups(backup_dir)

            self.assertEqual(1, listed["backup_count"])
            self.assertEqual(result["backup_id"], listed["backups"][0]["backup_id"])

    def test_inspect_backup_returns_manifest(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source_dir = Path(temp_dir) / "source"
            backup_dir = Path(temp_dir) / "backups"
            self.seed_source(source_dir)
            result = create_v1_backup(source_dir, backup_dir)

            inspected = inspect_v1_backup(result["backup_id"], backup_dir)

            self.assertEqual(result["backup_id"], inspected["manifest"]["backup_id"])

    def test_restore_backup_restores_files_into_empty_target(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source_dir = Path(temp_dir) / "source"
            restore_dir = Path(temp_dir) / "restore"
            backup_dir = Path(temp_dir) / "backups"
            self.seed_source(source_dir)
            result = create_v1_backup(source_dir, backup_dir)

            restore = restore_v1_backup(result["backup_id"], restore_dir, backup_dir)

            self.assertEqual(2, restore["restored_file_count"])
            self.assertTrue((restore_dir / "data" / "daily_run" / "last_daily_run.json").is_file())

    def test_restore_refuses_non_empty_target(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source_dir = Path(temp_dir) / "source"
            restore_dir = Path(temp_dir) / "restore"
            backup_dir = Path(temp_dir) / "backups"
            self.seed_source(source_dir)
            restore_dir.mkdir()
            (restore_dir / "existing.txt").write_text("existing", encoding="utf-8")
            result = create_v1_backup(source_dir, backup_dir)

            with self.assertRaises(RuntimeError) as error:
                restore_v1_backup(result["backup_id"], restore_dir, backup_dir)

            self.assertIn("restore_target_not_empty", str(error.exception))

    def test_missing_backup_id_returns_readable_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source_dir = Path(temp_dir) / "source"
            backup_dir = Path(temp_dir) / "backups"

            result = self.run_cli(
                source_dir,
                backup_dir,
                "inspect-backup",
                "--backup-id",
                "missing",
                check=False,
            )

            self.assertEqual(1, result.returncode)
            self.assertIn("not_found", result.stdout)

    def test_cli_create_backup_outputs_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source_dir = Path(temp_dir) / "source"
            backup_dir = Path(temp_dir) / "backups"
            self.seed_source(source_dir)

            result = self.run_cli(source_dir, backup_dir, "create-backup")
            payload = json.loads(result.stdout)

            self.assertTrue(Path(payload["backup_path"]).is_file())

    def test_repo_data_directory_is_not_polluted_during_tests(self):
        self.assertFalse((ROOT / "ashl_core_v1" / "data").exists())


if __name__ == "__main__":
    unittest.main()
