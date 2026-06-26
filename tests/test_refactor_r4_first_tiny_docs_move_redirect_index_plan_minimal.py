import copy
import unittest
from pathlib import Path

from ashl_core.refactor_r4_first_tiny_docs_move_redirect_index_plan_minimal import (
    COMMAND,
    FUTURE_MOVE_PRECONDITIONS,
    PREFERRED_CANDIDATE_NEW_PATH,
    PREFERRED_CANDIDATE_OLD_PATH,
    ROOT_AUTHORITY_DOCS,
    build_refactor_r4_first_tiny_docs_move_redirect_index_plan_minimal_record,
    run_refactor_r4_first_tiny_docs_move_redirect_index_plan_minimal_check,
    validate_refactor_r4_first_tiny_docs_move_redirect_index_plan_minimal_record,
)
from ashl_core.teaching_cli import run_command


class RefactorR4FirstTinyDocsMoveRedirectIndexPlanMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = run_refactor_r4_first_tiny_docs_move_redirect_index_plan_minimal_check()

    def test_r4_plan_doc_exists(self):
        validation = validate_refactor_r4_first_tiny_docs_move_redirect_index_plan_minimal_record(self.result)

        self.assertTrue(Path("docs/ashl_core_refactor_r4_first_tiny_docs_move_redirect_index_plan_v0.md").exists())
        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(self.result["status"], "ok")
        self.assertTrue(self.result["r4_tiny_docs_move_plan_created"])

    def test_source_r3a_freeze_is_read_and_validated(self):
        source = self.result["source_r3a_authority_freeze"]

        self.assertTrue(self.result["source_plans_read"])
        self.assertEqual(self.result["source_doc_readback"]["required_source_count"], 10)
        self.assertTrue(self.result["source_doc_readback"]["all_required_sources_read"])
        self.assertTrue(self.result["source_doc_readback"]["all_required_terms_found"])
        self.assertTrue(source["source_validated"])
        self.assertEqual(source["source_boundary_index"], "2026-06-09-b191")
        self.assertTrue(source["r3a_authority_freeze_created"])
        self.assertEqual(source["frozen_root_authority_doc_count"], 8)
        self.assertFalse(source["docs_moved"])
        self.assertFalse(source["runtime_behavior_changed"])

    def test_selected_candidate_exists_or_valid_fallback_used(self):
        self.assertTrue(self.result["selected_candidate_exists"])
        if Path(PREFERRED_CANDIDATE_OLD_PATH).exists():
            self.assertFalse(self.result["fallback_candidate_used"])
            self.assertEqual(self.result["selected_candidate_old_path"], PREFERRED_CANDIDATE_OLD_PATH)
            self.assertEqual(self.result["planned_candidate_new_path"], PREFERRED_CANDIDATE_NEW_PATH)
        else:
            self.assertTrue(self.result["fallback_candidate_used"])
            self.assertEqual(self.result["fallback_reason"], "source_candidate_missing")

    def test_selected_candidate_is_not_frozen_authority_doc(self):
        self.assertTrue(self.result["selected_candidate_not_root_authority"])
        self.assertFalse(self.result["root_authority_candidate_selected"])
        self.assertNotIn(self.result["selected_candidate_old_path"], ROOT_AUTHORITY_DOCS)

    def test_selected_candidate_is_historical_or_archive_candidate(self):
        self.assertTrue(self.result["selected_candidate_is_historical_or_archive_candidate"])
        self.assertTrue(self.result["selected_candidate_old_path"].startswith("docs/milestone_logs/"))

    def test_planned_new_path_is_under_archive_or_lines(self):
        new_path = self.result["planned_candidate_new_path"]

        self.assertTrue(new_path.startswith("docs/archive/") or new_path.startswith("docs/lines/"))
        self.assertTrue(new_path.endswith(Path(self.result["selected_candidate_old_path"]).name))

    def test_redirect_index_plan_exists(self):
        plan = self.result["redirect_index_plan"]

        self.assertTrue(self.result["redirect_index_plan_created"])
        self.assertTrue(plan["old_path"])
        self.assertTrue(plan["new_path"])
        self.assertTrue(plan["old_path_policy"])
        self.assertTrue(plan["new_path_policy"])
        self.assertTrue(plan["old_path_lookup_rule"])
        self.assertTrue(plan["new_path_lookup_rule"])

    def test_future_move_preconditions_exist(self):
        checks = self.result["future_move_precondition_checks"]

        self.assertTrue(self.result["future_move_preconditions_listed"])
        self.assertEqual(set(checks), set(FUTURE_MOVE_PRECONDITIONS))
        self.assertTrue(all(checks.values()))

    def test_frozen_authority_docs_are_protected(self):
        checks = self.result["frozen_authority_doc_checks"]

        self.assertTrue(self.result["frozen_authority_docs_protected"])
        self.assertEqual(set(checks), set(ROOT_AUTHORITY_DOCS))
        self.assertTrue(all(checks.values()))

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

    def test_boundary_is_b192_without_b10_self_check(self):
        boundary = self.result["boundary"]

        self.assertEqual(boundary["boundary_index_version_before"], "2026-06-09-b191")
        self.assertEqual(boundary["boundary_index_version_after"], "2026-06-09-b192")
        self.assertFalse(boundary["runtime_capability_change"])
        self.assertFalse(boundary["b10_boundary_self_check_triggered"])
        self.assertEqual(boundary["b_counter"], "B2/10")

    def test_missing_doc_content_fails_validation(self):
        record = build_refactor_r4_first_tiny_docs_move_redirect_index_plan_minimal_record("")

        validation = validate_refactor_r4_first_tiny_docs_move_redirect_index_plan_minimal_record(record)

        self.assertFalse(validation["valid"])
        self.assertFalse(validation["r4_tiny_docs_move_plan_created"])
        self.assertFalse(validation["redirect_index_plan_created"])
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

            validation = validate_refactor_r4_first_tiny_docs_move_redirect_index_plan_minimal_record(bad)

            self.assertFalse(validation["valid"], field)

    def test_selecting_root_authority_doc_blocks_validation(self):
        bad = copy.deepcopy(self.result)
        bad["selected_candidate_old_path"] = "docs/current_boundary_index.md"
        bad["selected_candidate_not_root_authority"] = False
        bad["root_authority_candidate_selected"] = True

        validation = validate_refactor_r4_first_tiny_docs_move_redirect_index_plan_minimal_record(bad)

        self.assertFalse(validation["valid"])
        self.assertIn("selected_candidate_not_root_authority_wrong", validation["error_codes"])

    def test_cli_command(self):
        result = run_command(COMMAND)

        self.assertEqual(result["command"], COMMAND)
        self.assertEqual(result["status"], "ok")
        self.assertTrue(result["r4_tiny_docs_move_plan_created"])
        self.assertTrue(result["selected_candidate_not_root_authority"])
        self.assertTrue(result["redirect_index_plan_created"])
        self.assertTrue(result["future_move_preconditions_listed"])
        self.assertFalse(result["docs_moved"])
        self.assertFalse(result["path_references_changed"])
        self.assertFalse(result["runtime_behavior_changed"])


if __name__ == "__main__":
    unittest.main()
