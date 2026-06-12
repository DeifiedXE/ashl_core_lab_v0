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
        self.assertIn("| docs/phase0_open_risk_ledger.md | risk_ledger | current | current_status_controls |", inventory)
        self.assertIn("unknown_needs_review", inventory)
        self.assertNotIn("|  |", inventory)

    def test_doc_index_defines_authority_rules(self):
        index = self._read("docs/phase0_doc_index.md")

        self.assertIn("Conflict Resolution Rule", index)
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

        self.assertIn("Boundary Index Version: 2026-06-09-b65", boundary)
        self.assertIn("No production/runtime memory-influenced behavior is allowed.", boundary)
        self.assertIn("sandbox-only lesson application and observation records", boundary)
        self.assertIn("do not constitute production/runtime memory-influenced behavior", boundary)

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
