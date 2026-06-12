import unittest
from pathlib import Path


DOCS = [
    Path("docs/phase0_status.md"),
    Path("docs/phase0_capability_matrix.md"),
    Path("docs/phase0_doc_index.md"),
]

FORBIDDEN_COMPLETED_CLAIMS = (
    "proof of learning complete",
    "runtime behavior changed",
    "memory write complete",
    "retention write complete",
    "predictor mutation complete",
    "production lesson application complete",
    "selected_action enabled",
    "final_action enabled",
    "outcome evaluation complete",
)


class Phase0DocumentationConsolidationTests(unittest.TestCase):
    def _read(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")

    def test_consolidated_docs_exist(self):
        for path in DOCS:
            with self.subTest(path=path):
                self.assertTrue(path.exists())

    def test_readme_references_consolidated_docs(self):
        readme = self._read(Path("README.md"))

        self.assertIn("docs/phase0_status.md", readme)
        self.assertIn("docs/phase0_capability_matrix.md", readme)
        self.assertIn("docs/current_boundary_index.md", readme)

    def test_research_plan_references_consolidated_docs(self):
        plan = self._read(Path("docs/research_plan.md"))

        self.assertIn("docs/phase0_status.md", plan)
        self.assertIn("docs/phase0_capability_matrix.md", plan)
        self.assertIn("docs/current_boundary_index.md", plan)
        self.assertIn("docs/phase0_doc_index.md", plan)

    def test_current_safe_capability_does_not_claim_proof_of_learning(self):
        status = self._read(Path("docs/phase0_status.md"))

        self.assertIn("Current Safe Capability", status)
        self.assertIn("proof of learning remain blocked", status)
        self.assertNotIn("proof of learning complete", status.lower())

    def test_outcome_evaluation_is_not_marked_complete(self):
        matrix = self._read(Path("docs/phase0_capability_matrix.md"))
        status = self._read(Path("docs/phase0_status.md"))

        self.assertIn("| outcome evaluation | not_implemented |", matrix)
        self.assertIn("Outcome evaluation is planned next and is not marked complete.", status)
        self.assertNotIn("outcome evaluation complete", (matrix + status).lower())

    def test_blocked_capabilities_remain_blocked(self):
        matrix = self._read(Path("docs/phase0_capability_matrix.md"))

        for capability in (
            "retention write",
            "predictor mutation",
            "runtime behavior change",
            "production lesson application",
            "proof of learning",
        ):
            with self.subTest(capability=capability):
                self.assertIn(f"| {capability} | blocked |", matrix)

    def test_forbidden_completed_claims_absent_from_consolidated_docs(self):
        combined = "\n".join(self._read(path).lower() for path in DOCS)

        for claim in FORBIDDEN_COMPLETED_CLAIMS:
            with self.subTest(claim=claim):
                self.assertNotIn(claim, combined)

    def test_no_repo_facing_mojibake_approval_wording_in_consolidated_docs(self):
        combined = "\n".join(self._read(path) for path in DOCS)

        self.assertNotIn("?" + chr(0x822A) + "??", combined)
        self.assertNotIn(chr(0x876F) + chr(0x8840) + "?", combined)
        self.assertIn("implicit chat command is not application approval", combined)


if __name__ == "__main__":
    unittest.main()
