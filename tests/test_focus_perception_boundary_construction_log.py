import unittest
from pathlib import Path


class FocusPerceptionBoundaryConstructionLogTests(unittest.TestCase):
    def setUp(self):
        self.doc_path = Path("docs/focus_perception_boundary_construction_log_v0.md")
        self.doc = self.doc_path.read_text(encoding="utf-8")

    def test_construction_log_document_exists(self):
        self.assertTrue(self.doc_path.exists())
        self.assertIn("Focus / Perception Boundary Construction Log v0", self.doc)

    def test_snapshot_and_trace_path_are_recorded(self):
        for phrase in [
            "Boundary Index Version: 2026-06-09-b41",
            "latest completed commit: fd7843b Add perception-to-action boundary review",
            "py -3 run_all_smoke_tests.py: PASS",
            "py -3 -m unittest discover: PASS, Ran 1553 tests",
            "symbolic/hybrid demo input",
            "retina feature records",
            "visual frame assembly",
            "low-level change_records",
            "focus_candidate records",
            "deterministic ranking_trace",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.doc)

    def test_focus_and_action_boundaries_are_recorded(self):
        for phrase in [
            "ranking_trace is only an ordering record",
            "rank_position 1 is not selected focus",
            "highest total_score is not selected focus",
            "no active_focus",
            "no focus_applied",
            "no attention_control",
            "retina feature is not an action reason",
            "visual_frame is not an action context",
            "change_record is not an action trigger",
            "focus_candidate is not an action intent",
            "ranking_trace is not action selection",
            "No direct mapping from focus rank to action.",
            "No direct mapping from total_score to action.",
            "No direct mapping from change_salience to action.",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.doc)

    def test_lock_prevention_and_gate_summary_are_recorded(self):
        for phrase in [
            "attention_intensity_cap",
            "attention_duration_limit / forced decay",
            "norepinephrine_like_interrupt",
            "cortisol_like_forced_diffusion",
            "external_mentor_interrupt as unconditional future priority",
            "No endocrine runtime controls focus.",
            "No runtime attention control exists.",
            "focus_application_candidate_gate",
            "focus_lock_prevention_gate",
            "mentor_interrupt_gate",
            "endocrine_boundary_gate",
            "perception_to_action_boundary_gate",
            "runtime_permission_gate",
            "The gates are review-only in v0.",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.doc)

    def test_safe_claim_and_forbidden_claims_are_recorded(self):
        for phrase in [
            "trace/checker/review only",
            "no perception-to-action bridge",
            "no action selection influence",
            "no visual memory write",
            "no predictor mutation",
            "no object recognition",
            "no semantic vision",
            "no subjective visual proof",
            "Do not claim Qingyin sees like a human.",
            "Do not claim object recognition.",
            "Do not claim object tracking.",
            "Do not claim semantic vision.",
            "Do not claim solved symbol grounding.",
            "Do not claim subjective visual experience.",
            "Do not claim visual action control.",
            "Do not claim attention runtime.",
            "Do not claim endocrine-controlled focus.",
            "Do not claim visual memory formation.",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.doc)

    def test_options_and_commit_timeline_are_recorded(self):
        for phrase in [
            "Option A: Perception-to-Action Gate Schema Check v0",
            "Option B: Focus Application Dry-Run Trace Design v0",
            "Option C: Stop focus/action boundary line and return to Phase 0 action/lesson loop.",
            "Recommended: pause and discuss before any package that introduces active_focus",
            "420bfa1 Add retina decoder feature schema",
            "4b5c007 Add eye structure line milestone and sync boundary index",
            "8c2edd6 Add focus line milestone and sync boundary index",
            "f1a59d2 Add focus application boundary review",
            "955b8ac Add focus application gate schema check",
            "fd7843b Add perception-to-action boundary review",
        ]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.doc)


if __name__ == "__main__":
    unittest.main()
