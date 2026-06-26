import copy
import unittest

from ashl_core.refactor_r2_compatibility_alias_plan_minimal import (
    COMMAND,
    STRUCTURAL_LINES,
    TARGET_FOLDERS,
    build_refactor_r2_compatibility_alias_plan_minimal_record,
    run_refactor_r2_compatibility_alias_plan_minimal_check,
    validate_refactor_r2_compatibility_alias_plan_minimal_record,
)
from ashl_core.teaching_cli import run_command


class RefactorR2CompatibilityAliasPlanMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = run_refactor_r2_compatibility_alias_plan_minimal_check()

    def test_r2_plan_exists(self):
        validation = validate_refactor_r2_compatibility_alias_plan_minimal_record(self.result)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(self.result["status"], "ok")
        self.assertTrue(self.result["r2_alias_plan_created"])

    def test_target_layout_includes_all_nine_folders_plus_spine(self):
        layout = self.result["target_package_layout"]

        self.assertTrue(self.result["target_package_layout_present"])
        self.assertEqual(set(layout), set(TARGET_FOLDERS))
        self.assertTrue(all(layout.values()))
        self.assertTrue(layout["ashl_core/spine/"])
        self.assertTrue(layout["ashl_core/governance/"])

    def test_compatibility_strategy_exists(self):
        checks = self.result["compatibility_strategy_checks"]

        self.assertTrue(self.result["compatibility_strategy_present"])
        self.assertTrue(checks["old_module_path remains importable"])
        self.assertTrue(checks["new_module_path becomes canonical"])
        self.assertTrue(checks["old path re-exports from new path"])
        self.assertTrue(checks["tests first validate both paths"])
        self.assertTrue(checks["old path deprecation happens only after compatibility passes"])

    def test_alias_candidate_table_exists(self):
        headers = self.result["table_header_checks"]

        self.assertTrue(self.result["alias_candidate_table_present"])
        self.assertTrue(headers["old_module_path"])
        self.assertTrue(headers["future_new_module_path"])
        self.assertTrue(headers["line"])
        self.assertTrue(headers["alias_strategy"])
        self.assertTrue(headers["risk_level"])
        self.assertTrue(headers["move_allowed_now"])

    def test_each_line_has_at_least_two_alias_candidates(self):
        counts = self.result["alias_candidate_counts"]

        self.assertTrue(self.result["nine_lines_have_alias_candidates"])
        for line in STRUCTURAL_LINES:
            with self.subTest(line=line):
                self.assertGreaterEqual(counts[line], 2)

    def test_spine_alias_candidates_exist(self):
        counts = self.result["alias_candidate_counts"]

        self.assertTrue(self.result["spine_alias_candidates_present"])
        self.assertGreaterEqual(counts["spine"], 2)

    def test_all_move_allowed_now_are_false(self):
        self.assertFalse(self.result["files_moved"])
        self.assertFalse(self.result["files_renamed"])
        self.assertFalse(self.result["imports_changed"])
        self.assertFalse(self.result["modules_merged"])
        self.assertFalse(self.result["old_paths_deleted"])
        self.assertFalse(self.result["runtime_behavior_changed"])

    def test_import_compatibility_test_plan_exists(self):
        checks = self.result["import_compatibility_test_plan_checks"]

        self.assertTrue(self.result["import_compatibility_test_plan_present"])
        self.assertTrue(checks["old import still works"])
        self.assertTrue(checks["new import works"])
        self.assertTrue(checks["old and new expose same public function names"])
        self.assertTrue(checks["old and new output same deterministic sample record"])
        self.assertTrue(checks["all existing tests still pass"])
        self.assertTrue(checks["smoke still passes"])

    def test_refactor_phase_gate_exists(self):
        checks = self.result["refactor_phase_gate_checks"]

        self.assertTrue(self.result["refactor_phase_gate_present"])
        self.assertTrue(checks["R1 structural map completed"])
        self.assertTrue(checks["R2 compatibility alias plan"])
        self.assertTrue(checks["R3 low-risk docs folder plan"])
        self.assertTrue(checks["R4 first small module move with compatibility shim"])
        self.assertTrue(checks["R7 old-path deprecation only after compatibility passes"])

    def test_non_movement_rules_exist(self):
        checks = self.result["non_movement_rule_checks"]

        self.assertTrue(checks["R2 must not move files."])
        self.assertTrue(checks["R2 must not rename modules."])
        self.assertTrue(checks["R2 must not change imports."])
        self.assertTrue(checks["R2 must not merge modules."])
        self.assertTrue(checks["R2 must not delete old paths."])

    def test_source_structural_map_is_validated(self):
        source = self.result["source_structural_map"]

        self.assertTrue(source["source_validated"])
        self.assertEqual(source["source_boundary_index"], "2026-06-09-b188")
        self.assertTrue(source["structural_refactor_map_created"])
        self.assertTrue(source["nine_lines_present"])
        self.assertEqual(source["line_count"], 9)
        self.assertFalse(source["files_moved"])
        self.assertFalse(source["imports_changed"])
        self.assertFalse(source["runtime_behavior_changed"])

    def test_missing_doc_content_fails_validation(self):
        record = build_refactor_r2_compatibility_alias_plan_minimal_record("")

        validation = validate_refactor_r2_compatibility_alias_plan_minimal_record(record)

        self.assertFalse(validation["valid"])
        self.assertFalse(validation["r2_alias_plan_created"])
        self.assertFalse(validation["target_package_layout_present"])
        self.assertFalse(validation["nine_lines_have_alias_candidates"])

    def test_movement_or_runtime_pollution_blocks_validation(self):
        cases = (
            ("files_moved", True),
            ("files_renamed", True),
            ("imports_changed", True),
            ("modules_merged", True),
            ("old_paths_deleted", True),
            ("runtime_behavior_changed", True),
        )
        for field, value in cases:
            bad = copy.deepcopy(self.result)
            bad[field] = value

            validation = validate_refactor_r2_compatibility_alias_plan_minimal_record(bad)

            self.assertFalse(validation["valid"], field)

    def test_low_alias_count_blocks_validation(self):
        bad = copy.deepcopy(self.result)
        bad["alias_candidate_counts"]["vision_eye_focus"] = 1

        validation = validate_refactor_r2_compatibility_alias_plan_minimal_record(bad)

        self.assertFalse(validation["valid"])
        self.assertIn("vision_eye_focus_alias_candidate_count_low", validation["error_codes"])

    def test_cli_command(self):
        result = run_command(COMMAND)

        self.assertEqual(result["command"], COMMAND)
        self.assertEqual(result["status"], "ok")
        self.assertTrue(result["r2_alias_plan_created"])
        self.assertTrue(result["nine_lines_have_alias_candidates"])
        self.assertFalse(result["files_moved"])
        self.assertFalse(result["imports_changed"])
        self.assertFalse(result["runtime_behavior_changed"])


if __name__ == "__main__":
    unittest.main()
