import unittest
from pathlib import Path

from ashl_core.session_experience_record_schema_minimal import (
    run_session_experience_record_schema_minimal_check,
)
from ashl_core.temporary_cross_session_experience_space_minimal import (
    build_temporary_experience_space,
    validate_temporary_experience_space,
)


class TemporaryCrossSessionRealityBoundaryTests(unittest.TestCase):
    def _valid_experience(self):
        result = run_session_experience_record_schema_minimal_check()
        return next(
            record
            for record, validation in zip(
                result["session_experience_records"],
                result["validation_results"],
            )
            if validation["valid"]
        )

    def test_temporary_space_declares_demo_or_fixture_handoff_only(self):
        space = build_temporary_experience_space([self._valid_experience()])
        boundary = space["reality_boundary"]

        self.assertEqual(boundary["persistence_model"], "demo_or_fixture_handoff_only")
        self.assertFalse(boundary["durable_across_process_restart"])

    def test_durable_across_process_restart_true_blocks(self):
        space = build_temporary_experience_space([self._valid_experience()])
        space["reality_boundary"]["durable_across_process_restart"] = True
        validation = validate_temporary_experience_space(space)

        self.assertFalse(validation["valid"])
        self.assertIn("durable_across_process_restart_not_false", validation["error_codes"])

    def test_persistence_model_other_than_demo_handoff_blocks(self):
        space = build_temporary_experience_space([self._valid_experience()])
        space["reality_boundary"]["persistence_model"] = "durable_persistence"
        validation = validate_temporary_experience_space(space)

        self.assertFalse(validation["valid"])
        self.assertIn("persistence_model_not_demo_or_fixture_handoff_only", validation["error_codes"])

    def test_reality_boundary_doc_contains_required_phrases(self):
        doc = Path("docs/temporary_cross_session_reality_boundary_clarification_v0.md").read_text(
            encoding="utf-8"
        )
        required_phrases = [
            "cross-session in v0 means controlled demo handoff, not durable persistence",
            "not durable across process restart",
            "not memory",
            "not history runtime",
            "not lesson retention",
            "deprecated or bypassed after future four-layer memory exists",
            "separate persistence boundary review",
        ]

        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, doc)


if __name__ == "__main__":
    unittest.main()
