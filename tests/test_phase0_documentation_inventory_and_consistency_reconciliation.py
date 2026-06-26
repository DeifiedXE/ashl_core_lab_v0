import unittest
from pathlib import Path


REQUIRED_DOCS = [
    Path("docs/phase0_status.md"),
    Path("docs/phase0_capability_matrix.md"),
    Path("docs/phase0_doc_inventory.md"),
    Path("docs/phase0_doc_index.md"),
    Path("docs/phase0_doc_consistency_audit.md"),
    Path("docs/phase0_open_risk_ledger.md"),
    Path("docs/phase0_unresolved_doc_issues.md"),
    Path("docs/phase0_versioning_policy.md"),
    Path("docs/phase1_to_phase5_growth_substrate_plan.md"),
    Path("docs/ashl_core_actual_capability_inventory_runtime_substrate_map_v0.md"),
    Path("docs/ashl_core_structural_refactor_map_v0.md"),
    Path("docs/ashl_core_refactor_r2_compatibility_alias_plan_v0.md"),
    Path("docs/ashl_core_refactor_r3_low_risk_docs_folder_plan_v0.md"),
]


class Phase0DocumentationInventoryConsistencyReconciliationTests(unittest.TestCase):
    def _read(self, path: str) -> str:
        return Path(path).read_text(encoding="utf-8")

    def test_required_docs_exist(self):
        for path in REQUIRED_DOCS:
            with self.subTest(path=path):
                self.assertTrue(path.exists())

    def test_inventory_classifies_markdown_docs(self):
        inventory = self._read("docs/phase0_doc_inventory.md")

        self.assertIn("Inventory count:", inventory)
        self.assertIn("| README.md | current_status_anchor | current | current_status_controls |", inventory)
        self.assertIn("| docs/current_boundary_index.md | boundary_anchor | current | boundary_controls |", inventory)
        self.assertIn("| docs/phase1_to_phase5_growth_substrate_plan.md | planning | planning_only | planning_only |", inventory)
        self.assertIn("| docs/ashl_core_actual_capability_inventory_runtime_substrate_map_v0.md | current_status_anchor | current | current_status_controls |", inventory)
        self.assertIn("| docs/phase0_open_risk_ledger.md | risk_ledger | current | current_status_controls |", inventory)
        self.assertIn("unknown_needs_review", inventory)
        self.assertNotIn("|  |", inventory)

    def test_doc_index_defines_authority_rules(self):
        index = self._read("docs/phase0_doc_index.md")

        self.assertIn("Conflict Resolution Rule", index)
        self.assertIn("docs/ashl_core_actual_capability_inventory_runtime_substrate_map_v0.md", index)
        self.assertIn("newer boundary/current-status document controls", index)
        self.assertIn("Older design assumptions remain historical context", index)
        self.assertIn("does not claim every old doc is fully reconciled", index)

    def test_consistency_audit_has_non_exhaustive_warning(self):
        audit = self._read("docs/phase0_doc_consistency_audit.md")

        self.assertIn("This audit does not prove that no documentation inconsistencies remain.", audit)
        self.assertIn("Known Issues Resolved", audit)
        self.assertIn("Files Still Needing Human Review", audit)

    def test_current_boundary_index_has_sandbox_production_distinction(self):
        boundary = self._read("docs/current_boundary_index.md")

        self.assertIn("Boundary Index Version: 2026-06-09-b190", boundary)
        self.assertIn("No production/runtime memory-influenced behavior is allowed.", boundary)
        self.assertIn("sandbox-only lesson application, observation, and evaluation records", boundary)
        self.assertIn("do not constitute production/runtime memory-influenced behavior", boundary)
        self.assertIn("Level 2 Sandbox Application milestone", boundary)
        self.assertIn("Level 3 Toy Minefield Multi-Step Sandbox milestone", boundary)
        self.assertIn("ASHL Core Refactor R3 Low-Risk Docs Folder Plan Minimal v0", boundary)
        self.assertIn("B0/10 self-check", boundary)
        self.assertIn("B0/10", boundary)

    def test_actual_capability_inventory_records_repo_reality(self):
        inventory = self._read("docs/ashl_core_actual_capability_inventory_runtime_substrate_map_v0.md")

        for phrase in (
            "tracked files after this package is committed: 825",
            "`ashl_core/*.py`: 294",
            "`tests/*.py`: 364",
            "top-level `docs/*.md`: 142",
            "smoke functions in `run_all_smoke_tests.py`: 430",
            "expected refreshed full smoke report: 430 / 430 passed",
            "Executable sandbox/helper capability",
            "Record/checker capability",
            "Design-only capability",
            "A readback-only package after b179 would be redundant",
            "ASHL Core Structural Refactor Map Minimal v0",
            "ASHL Core structural refactor map reports",
            "ASHL Core Refactor R2 Compatibility Alias Plan Minimal v0",
            "ASHL Core R2 compatibility alias plan reports",
            "ASHL Core Refactor R3 Low-Risk Docs Folder Plan Minimal v0",
            "ASHL Core R3 low-risk docs folder plan reports",
            "no unrestricted Qingyin long-term memory runtime",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, inventory)

    def test_capability_matrix_records_b183_phase1_closure(self):
        matrix = self._read("docs/phase0_capability_matrix.md")

        self.assertIn("phase1 closure audit minimal", matrix)
        self.assertIn("implemented_phase1_closure_audit", matrix)
        self.assertIn("Phase1 closure ready", matrix)
        self.assertIn("ashl_core/phase1_closure_audit_minimal.py", matrix)

    def test_capability_matrix_records_b184_phase2_grounding_entry(self):
        matrix = self._read("docs/phase0_capability_matrix.md")

        self.assertIn("phase2 closed phase1 substrate perception capability grounding entry minimal", matrix)
        self.assertIn("implemented_phase2_perception_capability_grounding_entry", matrix)
        self.assertIn("perception evidence candidates", matrix)
        self.assertIn("ashl_core/phase2_closed_phase1_substrate_perception_capability_grounding_entry_minimal.py", matrix)

    def test_capability_matrix_records_b185_phase2_evidence_source_link(self):
        matrix = self._read("docs/phase0_capability_matrix.md")

        self.assertIn("phase2 perception capability evidence source link minimal", matrix)
        self.assertIn("implemented_phase2_evidence_source_link_report", matrix)
        self.assertIn("visual-spatial grounding", matrix)
        self.assertIn("ashl_core/phase2_perception_capability_evidence_source_link_minimal.py", matrix)

    def test_capability_matrix_records_b186_phase2_unknown_classification_correction(self):
        matrix = self._read("docs/phase0_capability_matrix.md")

        self.assertIn("phase2 grounding unknown classification correction minimal", matrix)
        self.assertIn("implemented_phase2_unknown_classification_correction", matrix)
        self.assertIn("deferred to future Phase4 endocrine/tendency/settling review", matrix)
        self.assertIn("ashl_core/phase2_grounding_unknown_classification_correction_minimal.py", matrix)

    def test_capability_matrix_records_b187_phase2_to_phase10_cross_check(self):
        matrix = self._read("docs/phase0_capability_matrix.md")

        self.assertIn("phase2 to phase10 completed capability cross-check minimal", matrix)
        self.assertIn("implemented_docs_backed_capability_cross_check", matrix)
        self.assertIn("completed/do-not-repeat, partial/extend-only, unfinished/roadmap, and design-only/not-runtime", matrix)
        self.assertIn("ashl_core/phase2_to_phase10_completed_capability_cross_check_minimal.py", matrix)

    def test_capability_matrix_records_b188_structural_refactor_map(self):
        matrix = self._read("docs/phase0_capability_matrix.md")

        self.assertIn("structural refactor map minimal", matrix)
        self.assertIn("implemented_structural_validation_map", matrix)
        self.assertIn("do-not-rebuild anchors, extend-only anchors, duplicate/merge candidates", matrix)
        self.assertIn("ashl_core/structural_refactor_map_minimal.py", matrix)
        self.assertIn("docs/ashl_core_structural_refactor_map_v0.md", matrix)

    def test_structural_refactor_map_records_no_runtime_refactor_execution(self):
        structural_map = self._read("docs/ashl_core_structural_refactor_map_v0.md")

        self.assertIn("This document maps the current ASHL Core repository into nine structural lines.", structural_map)
        self.assertIn("It does not move files or change runtime behavior.", structural_map)
        self.assertIn("## action_body_motor", structural_map)
        self.assertIn("## governance_audit_documentation", structural_map)
        self.assertIn("No file move.", structural_map)
        self.assertIn("No import path change.", structural_map)
        self.assertIn("No runtime behavior change.", structural_map)

    def test_capability_matrix_records_b189_r2_alias_plan(self):
        matrix = self._read("docs/phase0_capability_matrix.md")

        self.assertIn("refactor r2 compatibility alias plan minimal", matrix)
        self.assertIn("implemented_refactor_alias_planning_map", matrix)
        self.assertIn("alias candidates for spine plus all nine structural lines", matrix)
        self.assertIn("ashl_core/refactor_r2_compatibility_alias_plan_minimal.py", matrix)
        self.assertIn("docs/ashl_core_refactor_r2_compatibility_alias_plan_v0.md", matrix)

    def test_r2_alias_plan_records_no_refactor_execution(self):
        plan = self._read("docs/ashl_core_refactor_r2_compatibility_alias_plan_v0.md")

        self.assertIn("R2 prepares compatibility aliases before any file movement.", plan)
        self.assertIn("No files are moved in this package.", plan)
        self.assertIn("No imports are changed in this package.", plan)
        self.assertIn("old_module_path remains importable", plan)
        self.assertIn("old path re-exports from new path", plan)
        self.assertIn("R2 must not move files.", plan)
        self.assertIn("R2 must not change imports.", plan)
        self.assertIn("No runtime behavior change.", plan)

    def test_capability_matrix_records_b190_r3_docs_folder_plan(self):
        matrix = self._read("docs/phase0_capability_matrix.md")

        self.assertIn("refactor r3 low-risk docs folder plan minimal", matrix)
        self.assertIn("implemented_docs_folder_planning_map", matrix)
        self.assertIn("root authority docs, line docs candidates, archive candidates", matrix)
        self.assertIn("ashl_core/refactor_r3_low_risk_docs_folder_plan_minimal.py", matrix)
        self.assertIn("docs/ashl_core_refactor_r3_low_risk_docs_folder_plan_v0.md", matrix)

    def test_r3_docs_folder_plan_records_no_docs_movement(self):
        plan = self._read("docs/ashl_core_refactor_r3_low_risk_docs_folder_plan_v0.md")

        self.assertIn("R3 plans future documentation organization before any documentation movement.", plan)
        self.assertIn("No docs are moved in this package.", plan)
        self.assertIn("Root Authority Docs", plan)
        self.assertIn("design_only_not_runtime_docs", plan)
        self.assertIn("b190 requires B10/10 hallucination self-check.", plan)
        self.assertIn("No docs moved.", plan)
        self.assertIn("No Python import changed.", plan)
        self.assertIn("No runtime behavior changed.", plan)

    def test_long_term_memory_priority_note_exists(self):
        design = self._read("docs/five_layer_memory_design_assumption_v0_1.md")
        boundary = self._read("docs/five_layer_memory_framework_boundary_v0.md")

        for text in (design, boundary):
            self.assertIn("Version-priority note", text)
            self.assertIn("does not grant current Long-term Memory capability", text)

    def test_open_risk_ledger_contains_required_risks(self):
        ledger = self._read("docs/phase0_open_risk_ledger.md")

        for phrase in (
            "Rollback may reverse a sandbox application record/effect",
            "Retained JSONL records must not automatically rebuild memory influence",
            "influence_strength <= 0.3",
            "checker/reviewer role must be responsible",
            "record-level and validation-level only",
            "sandbox_id alone",
            "memory is treated as a warning signal",
            "Level 1 sandbox lesson application has moved beyond design-only",
            "Mentor override may exist as a declared field",
            "corrective hardening after earlier design",
            "Approval replay protection is an open design gap",
            "not assumed to be exhaustive",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, ledger)

    def test_memory_warning_phrase_is_paired_with_practical_gate_wording(self):
        boundary = self._read("docs/current_boundary_index.md")
        ledger = self._read("docs/phase0_open_risk_ledger.md")

        self.assertIn("Memory is a warning sign, not a ban command", boundary)
        self.assertIn("memory-influenced behavior remains practically blocked", boundary + ledger)
        self.assertIn("all required gates and checks are satisfied", boundary + ledger)

    def test_unresolved_documentation_issues_are_accounted_for(self):
        unresolved = self._read("docs/phase0_unresolved_doc_issues.md")

        self.assertIn("not assumed to be exhaustive", unresolved)
        self.assertIn("This is not proof that none exist", unresolved)
        self.assertIn("unknown_needs_review", self._read("docs/phase0_doc_inventory.md"))

    def test_docs_do_not_claim_new_capabilities(self):
        combined = "\n".join(path.read_text(encoding="utf-8").lower() for path in REQUIRED_DOCS)

        for forbidden in (
            "outcome evaluation complete",
            "memory write complete",
            "retention write complete",
            "predictor mutation complete",
            "production lesson application complete",
            "selected_action enabled",
            "final_action enabled",
            "anti-replay implemented",
            "session-bound approval",
            "sandbox isolation proven",
            "proof of learning complete",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, combined)

    def test_no_repo_facing_mojibake_approval_wording_in_new_docs(self):
        combined = "\n".join(path.read_text(encoding="utf-8") for path in REQUIRED_DOCS)

        self.assertNotIn("?" + chr(0x822A) + "??", combined)
        self.assertNotIn(chr(0x876F) + chr(0x8840) + "?", combined)
        self.assertIn("implicit chat command is not application approval", combined)


if __name__ == "__main__":
    unittest.main()
