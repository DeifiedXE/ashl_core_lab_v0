import copy
import unittest

from ashl_core.structural_refactor_map_minimal import (
    COMMAND,
    STRUCTURAL_LINES,
    build_structural_refactor_map_minimal_record,
    run_structural_refactor_map_minimal_check,
    validate_structural_refactor_map_minimal_record,
)
from ashl_core.teaching_cli import run_command


class StructuralRefactorMapMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = run_structural_refactor_map_minimal_check()

    def test_structural_refactor_map_is_created(self):
        validation = validate_structural_refactor_map_minimal_record(self.result)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(self.result["status"], "ok")
        self.assertTrue(self.result["structural_refactor_map_created"])

    def test_nine_lines_are_present(self):
        line_names = {check["line_name"] for check in self.result["line_checks"]}

        self.assertTrue(self.result["nine_lines_present"])
        self.assertEqual(self.result["line_count"], 9)
        self.assertEqual(line_names, set(STRUCTURAL_LINES))

    def test_each_line_has_plain_role_and_future_folder(self):
        for check in self.result["line_checks"]:
            with self.subTest(line=check["line_name"]):
                self.assertTrue(check["plain_role_present"])
                self.assertTrue(check["future_folder_suggestion_present"])

    def test_each_line_has_required_map_fields(self):
        required_fields = (
            "core_modules_present",
            "related_tests_present",
            "related_docs_present",
            "current_outputs_present",
            "partial_or_design_only_parts_present",
            "duplicate_or_merge_candidates_present",
            "historical_or_archive_candidates_present",
        )
        for check in self.result["line_checks"]:
            for field in required_fields:
                with self.subTest(line=check["line_name"], field=field):
                    self.assertTrue(check[field])

    def test_completed_do_not_rebuild_anchors_exist(self):
        self.assertTrue(self.result["completed_do_not_rebuild_section_present"])
        anchors = self.result["completed_do_not_rebuild_anchors"]

        self.assertTrue(anchors["Phase0 thought/action/memory mini-loop"])
        self.assertTrue(anchors["Phase1 session trace spine / frame / tick handoff / three-line index / closure"])
        self.assertTrue(anchors["Phase2 entry / source-link / unknown classification correction"])
        self.assertTrue(anchors["sandbox action chain"])

    def test_partial_extend_only_anchors_exist(self):
        self.assertTrue(self.result["partial_extend_only_section_present"])
        anchors = self.result["partial_extend_only_anchors"]

        self.assertTrue(anchors["memory line should be integrated, not rebuilt"])
        self.assertTrue(anchors["first_output should be persisted / connected, not rebuilt"])
        self.assertTrue(anchors["symbolic eye should be connected to runtime focus, not replaced"])
        self.assertTrue(anchors["endocrine trace should become bounded context surface, not direct action authority"])

    def test_duplicate_merge_candidates_exist(self):
        self.assertTrue(self.result["duplicate_merge_candidates_listed"])
        families = self.result["duplicate_merge_candidate_families"]

        self.assertTrue(families["selected_action approval / selected_action minimal"])
        self.assertTrue(families["final_action approval / final_action minimal"])
        self.assertTrue(families["direct_command approval / direct_command minimal"])
        self.assertTrue(families["readback / index / closure audit packages"])

    def test_historical_archive_candidates_are_listed_only(self):
        historical = self.result["historical_archive_candidate_summary"]

        self.assertTrue(self.result["historical_archive_candidates_listed"])
        self.assertTrue(historical["archive_candidates_listed_only"])
        self.assertFalse(historical["files_deleted"])
        self.assertFalse(historical["files_archived"])

    def test_non_goals_and_no_runtime_change(self):
        validation = validate_structural_refactor_map_minimal_record(self.result)

        self.assertFalse(validation["runtime_behavior_changed"])
        self.assertFalse(validation["files_moved"])
        self.assertFalse(validation["files_deleted"])
        self.assertFalse(validation["files_renamed"])
        self.assertFalse(validation["imports_changed"])
        self.assertFalse(validation["new_runtime_authority_created"])
        self.assertFalse(self.result["runtime_behavior_changed"])
        self.assertFalse(self.result["files_moved"])
        self.assertFalse(self.result["files_deleted"])
        self.assertFalse(self.result["files_renamed"])
        self.assertFalse(self.result["imports_changed"])
        self.assertFalse(self.result["new_runtime_authority_created"])
        self.assertTrue(all(self.result["non_goals"].values()))

    def test_future_folder_suggestions_exist(self):
        folders = self.result["future_folder_suggestions"]

        self.assertTrue(self.result["future_folder_suggestions_present"])
        self.assertTrue(folders["ashl_core/body/"])
        self.assertTrue(folders["ashl_core/thought/"])
        self.assertTrue(folders["ashl_core/memory/"])
        self.assertTrue(folders["ashl_core/perception/"])
        self.assertTrue(folders["ashl_core/governance/"])

    def test_missing_doc_content_fails_validation(self):
        record = build_structural_refactor_map_minimal_record("")

        validation = validate_structural_refactor_map_minimal_record(record)

        self.assertFalse(validation["valid"])
        self.assertFalse(validation["structural_refactor_map_created"])
        self.assertFalse(validation["nine_lines_present"])

    def test_pollution_blocks_validation(self):
        cases = (
            ("runtime_behavior_changed", True),
            ("files_moved", True),
            ("files_deleted", True),
            ("files_renamed", True),
            ("imports_changed", True),
            ("new_runtime_authority_created", True),
        )
        for field, value in cases:
            bad = copy.deepcopy(self.result)
            bad[field] = value

            validation = validate_structural_refactor_map_minimal_record(bad)

            self.assertFalse(validation["valid"], field)

    def test_cli_command(self):
        result = run_command(COMMAND)

        self.assertEqual(result["command"], COMMAND)
        self.assertEqual(result["status"], "ok")
        self.assertTrue(result["structural_refactor_map_created"])
        self.assertTrue(result["nine_lines_present"])
        self.assertEqual(result["line_count"], 9)
        self.assertFalse(result["runtime_behavior_changed"])
        self.assertFalse(result["files_moved"])
        self.assertFalse(result["files_deleted"])
        self.assertFalse(result["files_renamed"])


if __name__ == "__main__":
    unittest.main()
