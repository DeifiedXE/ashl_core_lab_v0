import copy
import unittest

from ashl_core.refactor_r3_low_risk_docs_folder_plan_minimal import (
    COMMAND,
    DOC_LINES,
    FUTURE_DOC_FOLDERS,
    ROOT_AUTHORITY_DOCS,
    build_refactor_r3_low_risk_docs_folder_plan_minimal_record,
    run_refactor_r3_low_risk_docs_folder_plan_minimal_check,
    validate_refactor_r3_low_risk_docs_folder_plan_minimal_record,
)
from ashl_core.teaching_cli import run_command


class RefactorR3LowRiskDocsFolderPlanMinimalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = run_refactor_r3_low_risk_docs_folder_plan_minimal_check()

    def test_r3_plan_exists(self):
        validation = validate_refactor_r3_low_risk_docs_folder_plan_minimal_record(self.result)

        self.assertTrue(validation["valid"], validation["error_codes"])
        self.assertEqual(self.result["status"], "ok")
        self.assertTrue(self.result["r3_docs_folder_plan_created"])

    def test_source_docs_are_read(self):
        readback = self.result["source_doc_readback"]

        self.assertTrue(self.result["source_docs_read"])
        self.assertEqual(readback["required_source_count"], 8)
        self.assertTrue(readback["all_required_sources_read"])
        self.assertTrue(readback["all_required_terms_found"])

    def test_source_r2_alias_plan_is_validated(self):
        source = self.result["source_r2_alias_plan"]

        self.assertTrue(source["source_validated"])
        self.assertEqual(source["source_boundary_index"], "2026-06-09-b189")
        self.assertTrue(source["r2_alias_plan_created"])
        self.assertFalse(source["files_moved"])
        self.assertFalse(source["imports_changed"])
        self.assertFalse(source["runtime_behavior_changed"])

    def test_root_authority_docs_are_listed(self):
        checks = self.result["root_authority_doc_checks"]

        self.assertTrue(self.result["root_authority_docs_listed"])
        self.assertEqual(set(checks), set(ROOT_AUTHORITY_DOCS))
        self.assertTrue(all(checks.values()))

    def test_all_line_folders_are_represented(self):
        layout = self.result["target_docs_layout"]

        self.assertEqual(set(layout), set(FUTURE_DOC_FOLDERS))
        self.assertTrue(all(layout.values()))
        self.assertTrue(layout["docs/lines/spine/"])
        self.assertTrue(layout["docs/lines/governance/"])

    def test_each_line_has_candidate_docs_list(self):
        checks = {entry["line_name"]: entry for entry in self.result["line_doc_checks"]}

        self.assertTrue(self.result["nine_line_docs_candidates_listed"])
        self.assertEqual(set(checks), set(DOC_LINES))
        for line_name, entry in checks.items():
            with self.subTest(line=line_name):
                self.assertTrue(entry["candidate_docs_listed"])
                self.assertTrue(entry["future_docs_folder_present"])
                self.assertTrue(entry["reason_present"])

    def test_archive_candidates_exist(self):
        checks = self.result["archive_candidate_checks"]

        self.assertTrue(self.result["archive_candidates_listed"])
        self.assertTrue(checks["old boundary index snapshots"])
        self.assertTrue(checks["milestone logs"])
        self.assertTrue(checks["progress logs"])
        self.assertTrue(checks["historical status compression docs"])
        self.assertTrue(checks["superseded planning docs"])
        self.assertTrue(checks["stale readiness checklists"])

    def test_design_only_docs_are_marked(self):
        checks = self.result["design_only_doc_checks"]

        self.assertTrue(self.result["design_only_docs_marked"])
        self.assertTrue(checks["retina decoder design"])
        self.assertTrue(checks["focus selector design"])
        self.assertTrue(checks["mimetic endocrine system design"])
        self.assertTrue(checks["Qingyin Bridge dual-eye design"])
        self.assertTrue(checks["voice/audio/cochlea/vocal-organ design"])
        self.assertTrue(checks["thought layering design"])
        self.assertTrue(checks["memory framework design"])

    def test_needs_review_before_move_list_exists(self):
        checks = self.result["needs_review_before_move_checks"]

        self.assertTrue(self.result["needs_review_before_move_listed"])
        self.assertTrue(checks["root authority docs"])
        self.assertTrue(checks["docs referenced by `docs/current_boundary_index.md`"])
        self.assertTrue(checks["docs referenced by `docs/codex_working_context_summary.md`"])
        self.assertTrue(checks["docs referenced by `README.md`"])
        self.assertTrue(checks["docs referenced by `run_all_smoke_tests.py`"])
        self.assertTrue(checks["docs referenced by targeted unit tests"])

    def test_all_move_allowed_now_are_false(self):
        self.assertTrue(self.result["move_allowed_now_all_false"])
        for entry in self.result["line_doc_checks"]:
            with self.subTest(line=entry["line_name"]):
                self.assertTrue(entry["move_allowed_now_false"])

    def test_no_docs_or_runtime_side_effects(self):
        self.assertFalse(self.result["docs_moved"])
        self.assertFalse(self.result["docs_deleted"])
        self.assertFalse(self.result["docs_renamed"])
        self.assertFalse(self.result["python_modules_touched_for_refactor"])
        self.assertFalse(self.result["imports_changed"])
        self.assertFalse(self.result["runtime_behavior_changed"])

    def test_b10_self_check_behavior_correct(self):
        checks = self.result["b10_self_check"]

        self.assertTrue(self.result["b10_self_check_required"])
        self.assertTrue(self.result["b10_self_check_passed"])
        self.assertTrue(checks["report keys only from parsed runtime/checker output"])
        self.assertTrue(checks["verified facts separated from assumptions"])
        self.assertTrue(checks["no claim that docs were moved"])
        self.assertTrue(checks["no claim that imports changed"])
        self.assertTrue(checks["no claim that runtime behavior changed"])

    def test_boundary_audit_passes(self):
        audit = self.result["boundary_audit"]

        self.assertTrue(self.result["boundary_audit_passed"])
        self.assertTrue(audit["no production behavior"])
        self.assertTrue(audit["no runtime behavior leak"])
        self.assertTrue(audit["no memory write / retention write"])
        self.assertTrue(audit["no predictor read / influence / mutation"])
        self.assertTrue(audit["no direct endocrine feed"])
        self.assertTrue(audit["no direct tendency feed"])
        self.assertTrue(audit["no proof-of-learning claim"])
        self.assertTrue(audit["no next-layer boundary content implemented"])

    def test_missing_doc_content_fails_validation(self):
        record = build_refactor_r3_low_risk_docs_folder_plan_minimal_record("")

        validation = validate_refactor_r3_low_risk_docs_folder_plan_minimal_record(record)

        self.assertFalse(validation["valid"])
        self.assertFalse(validation["r3_docs_folder_plan_created"])
        self.assertFalse(validation["root_authority_docs_listed"])
        self.assertFalse(validation["nine_line_docs_candidates_listed"])

    def test_side_effect_pollution_blocks_validation(self):
        cases = (
            ("docs_moved", True),
            ("docs_deleted", True),
            ("docs_renamed", True),
            ("python_modules_touched_for_refactor", True),
            ("imports_changed", True),
            ("runtime_behavior_changed", True),
        )
        for field, value in cases:
            bad = copy.deepcopy(self.result)
            bad[field] = value

            validation = validate_refactor_r3_low_risk_docs_folder_plan_minimal_record(bad)

            self.assertFalse(validation["valid"], field)

    def test_missing_b10_self_check_blocks_validation(self):
        bad = copy.deepcopy(self.result)
        bad["b10_self_check"]["no claim that docs were moved"] = False
        bad["b10_self_check_passed"] = False

        validation = validate_refactor_r3_low_risk_docs_folder_plan_minimal_record(bad)

        self.assertFalse(validation["valid"])
        self.assertIn("b10_self_check_passed_wrong", validation["error_codes"])

    def test_cli_command(self):
        result = run_command(COMMAND)

        self.assertEqual(result["command"], COMMAND)
        self.assertEqual(result["status"], "ok")
        self.assertTrue(result["r3_docs_folder_plan_created"])
        self.assertTrue(result["root_authority_docs_listed"])
        self.assertTrue(result["nine_line_docs_candidates_listed"])
        self.assertFalse(result["docs_moved"])
        self.assertFalse(result["imports_changed"])
        self.assertFalse(result["runtime_behavior_changed"])
        self.assertTrue(result["b10_self_check_required"])
        self.assertTrue(result["b10_self_check_passed"])


if __name__ == "__main__":
    unittest.main()
