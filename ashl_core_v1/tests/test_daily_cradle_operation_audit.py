import tempfile
import unittest
from pathlib import Path

from ashl_core_v1.output.first_output_candidate import (
    build_first_output_candidate_from_last_daily,
    save_first_output_candidate,
)
from ashl_core_v1.output.first_output_promotion import promote_last_approved_first_output
from ashl_core_v1.output.first_output_review import review_last_first_output_candidate
from ashl_core_v1.runtime.daily_operation_audit import (
    build_daily_operation_audit,
    load_last_daily_operation_audit,
    save_daily_operation_audit,
    write_daily_operation_audit_report,
)
from ashl_core_v1.runtime.daily_run import run_cradle_daily


ROOT = Path(__file__).resolve().parents[2]


class DailyCradleOperationAuditTests(unittest.TestCase):
    def seed_complete_daily_operation(self, data_dir: Path) -> None:
        run_cradle_daily("basic", data_dir)
        save_first_output_candidate(build_first_output_candidate_from_last_daily(data_dir), data_dir)
        review_last_first_output_candidate("approved", "ok", data_dir)
        promote_last_approved_first_output(data_dir)

    def test_audit_detects_missing_daily_run(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            audit = build_daily_operation_audit(Path(temp_dir))

            self.assertFalse(audit["daily_run_present"])
            self.assertIn("daily_run_present", audit["missing_items"])

    def test_audit_detects_missing_first_output_review(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            run_cradle_daily("basic", data_dir)
            save_first_output_candidate(build_first_output_candidate_from_last_daily(data_dir), data_dir)

            audit = build_daily_operation_audit(data_dir)

            self.assertFalse(audit["first_output_review_present"])
            self.assertIn("first_output_review_present", audit["missing_items"])

    def test_audit_detects_missing_first_output_record(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            run_cradle_daily("basic", data_dir)
            save_first_output_candidate(build_first_output_candidate_from_last_daily(data_dir), data_dir)
            review_last_first_output_candidate("approved", "ok", data_dir)

            audit = build_daily_operation_audit(data_dir)

            self.assertFalse(audit["first_output_record_present"])
            self.assertIn("first_output_record_present", audit["missing_items"])

    def test_complete_audit_passes_when_required_pieces_exist(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.seed_complete_daily_operation(data_dir)

            audit = build_daily_operation_audit(data_dir)

            self.assertTrue(audit["manual_daily_operation_complete"])
            self.assertEqual([], audit["missing_items"])

    def test_backup_present_can_be_false_without_failing_completion(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            self.seed_complete_daily_operation(data_dir)

            audit = build_daily_operation_audit(data_dir)

            self.assertFalse(audit["backup_present"])
            self.assertTrue(audit["manual_daily_operation_complete"])

    def test_save_load_last_audit_works(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            audit = build_daily_operation_audit(data_dir)

            save_daily_operation_audit(audit, data_dir)

            self.assertEqual(audit, load_last_daily_operation_audit(data_dir))

    def test_write_audit_report_creates_markdown(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            path = data_dir / "audit.md"

            result = write_daily_operation_audit_report(path, data_dir)

            self.assertEqual(str(path), result["path"])
            self.assertTrue(path.is_file())

    def test_human_readable_audit_is_non_empty(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            audit = build_daily_operation_audit(Path(temp_dir))

            self.assertTrue(audit["human_readable_audit"])

    def test_repo_data_directory_is_not_polluted_during_tests(self):
        self.assertFalse((ROOT / "ashl_core_v1" / "data").exists())


if __name__ == "__main__":
    unittest.main()
