from pathlib import Path
import unittest


DOC_PATH = Path("docs/explicit_user_approval_source_boundary_v0.md")


class ExplicitUserApprovalSourceBoundaryTests(unittest.TestCase):
    def test_doc_contains_required_approval_source_boundary_phrases(self):
        doc = DOC_PATH.read_text(encoding="utf-8")

        required_phrases = [
            "Codex may record approval, but cannot provide approval",
            "Only the project owner / user can provide explicit application approval",
            "A test fixture is not real approval",
            "implicit chat command is not application approval",
            "Passing tests are not approval",
        ]

        missing = [phrase for phrase in required_phrases if phrase not in doc]
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
