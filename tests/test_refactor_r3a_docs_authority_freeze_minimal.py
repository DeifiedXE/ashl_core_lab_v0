import copy
import unittest
from pathlib import Path

from ashl_core.refactor_r3a_docs_authority_freeze_minimal import (
    COMMAND,
    FUTURE_MOVE_PRECONDITIONS,
    ROOT_AUTHORITY_DOCS,
    build_refactor_r3a_docs_authority_freeze_minimal_record,
    run_refactor_r3a_docs_authority_freeze_minimal_check,
    validate_refactor_r3a_docs_authority_freeze_minimal_record,
)
from ashl_core.teaching_cli import run_command


class RefactorR3ADocsAuthorityFreezeMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = run_refactor_r3a_docs_authority_freeze_minimal_check()

    def test_r3a_freeze_doc_exists(self):
        validation = validate_refactor_r3a_docs_authority_freeze_minimal_record(self.result)

        self.assertTrue(Path("docs/ashl_core_refactor_r3a_docs_authority_freeze_v0.md").exists())
        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(self.result["status"], "ok")
        self.assertTrue(self.result["r3a_authority_freeze_created"])

    def test_source_r3_plan_is_read_and_validated(self):
        source = self.result["source_r3_docs_folder_plan"]

        self.assertTrue(self.result["r3_source_plan_read"])
        self.assertEqual(self.result["source_doc_readback"]["required_source_count"], 10)
        self.assertTrue(self.result["source_doc_readback"]["all_required_sources_read"])
        self.assertTrue(self.result["source_doc_readback"]["all_required_terms_found"])
        self.assertTrue(source["source_validated"])
        self.assertEqual(source["source_boundary_index"], "2026-06-09-b190")
        self.assertTrue(source["r3_docs_folder_plan_created"])
        self.assertTrue(source["root_authority_docs_listed"])
        self.assertFalse(source["docs_moved"])
        self.assertFalse(source["runtime_behavior_changed"])

    def test_frozen_root_authority_doc_count_is_eight(self):
        self.assertEqual(self.result["frozen_root_authority_doc_count"], 8)
        self.assertEqual(len(ROOT_AUTHORITY_DOCS), 8)

    def test_all_required_authority_docs_are_listed_and_present(self):
        checks = self.result["frozen_root_authority_doc_checks"]

        self.assertTrue(self.result["frozen_root_authority_docs_listed"])
        self.assertTrue(self.result["all_required_authority_docs_present"])
        self.assertEqual(set(checks), set(ROOT_AUTHORITY_DOCS))
        self.assertTrue(all(checks.values()))

    def test_future_move_preconditions_are_listed(self):
        checks = self.result["future_move_precondition_checks"]

        self.assertTrue(self.result["future_move_preconditions_listed"])
        self.assertEqual(set(checks), set(FUTURE_MOVE_PRECONDITIONS))
        self.assertTrue(all(checks.values()))

    def test_redirect_and_explicit_approval_are_required(self):
        self.assertTrue(self.result["redirect_required_before_move"])
        self.assertTrue(self.result["user_explicit_approval_required_before_authority_doc_move"])
        self.assertTrue(self.result["freeze_rule"]["future_explicit_redirect_index_package_required"])
        self.assertTrue(self.result["freeze_rule"]["user_explicit_approval_required"])

    def test_no_docs_or_runtime_side_effects(self):
        self.assertFalse(self.result["docs_moved"])
        self.assertFalse(self.result["docs_deleted"])
        self.assertFalse(self.result["docs_renamed"])
        self.assertFalse(self.result["docs_archived"])
        self.assertFalse(self.result["docs_lines_created"])
        self.assertFalse(self.result["archive_created"])
        self.assertFalse(self.result["path_references_changed"])
        self.assertFalse(self.result["python_imports_changed"])
        self.assertFalse(self.result["runtime_behavior_changed"])

    def test_boundary_is_b191_without_b10_self_check(self):
        boundary = self.result["boundary"]

        self.assertEqual(boundary["boundary_index_version_before"], "2026-06-09-b190")
        self.assertEqual(boundary["boundary_index_version_after"], "2026-06-09-b191")
        self.assertFalse(boundary["runtime_capability_change"])
        self.assertFalse(boundary["b10_boundary_self_check_triggered"])
        self.assertEqual(boundary["b_counter"], "B1/10")

    def test_missing_doc_content_fails_validation(self):
        record = build_refactor_r3a_docs_authority_freeze_minimal_record("")

        validation = validate_refactor_r3a_docs_authority_freeze_minimal_record(record)

        self.assertFalse(validation["valid"])
        self.assertFalse(validation["r3a_authority_freeze_created"])
        self.assertFalse(validation["frozen_root_authority_docs_listed"])
        self.assertFalse(validation["future_move_preconditions_listed"])

    def test_side_effect_pollution_blocks_validation(self):
        for field in (
            "docs_moved",
            "docs_deleted",
            "docs_renamed",
            "docs_archived",
            "docs_lines_created",
            "archive_created",
            "path_references_changed",
            "python_imports_changed",
            "runtime_behavior_changed",
        ):
            bad = copy.deepcopy(self.result)
            bad[field] = True

            validation = validate_refactor_r3a_docs_authority_freeze_minimal_record(bad)

            self.assertFalse(validation["valid"], field)

    def test_missing_redirect_precondition_blocks_validation(self):
        bad = copy.deepcopy(self.result)
        bad["future_move_precondition_checks"]["redirect_index_created=True"] = False
        bad["future_move_preconditions_listed"] = False
        bad["redirect_required_before_move"] = False

        validation = validate_refactor_r3a_docs_authority_freeze_minimal_record(bad)

        self.assertFalse(validation["valid"])
        self.assertIn("redirect_required_before_move_wrong", validation["error_codes"])

    def test_cli_command(self):
        result = run_command(COMMAND)

        self.assertEqual(result["command"], COMMAND)
        self.assertEqual(result["status"], "ok")
        self.assertTrue(result["r3a_authority_freeze_created"])
        self.assertEqual(result["frozen_root_authority_doc_count"], 8)
        self.assertTrue(result["redirect_required_before_move"])
        self.assertFalse(result["docs_moved"])
        self.assertFalse(result["docs_deleted"])
        self.assertFalse(result["docs_renamed"])
        self.assertFalse(result["runtime_behavior_changed"])


if __name__ == "__main__":
    unittest.main()
