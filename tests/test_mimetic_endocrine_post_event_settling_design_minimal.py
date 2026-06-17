import unittest
from copy import deepcopy

from ashl_core.mimetic_endocrine_post_event_settling_design_minimal import (
    BOUNDARY_INDEX,
    SETTLING_MODES,
    build_mimetic_endocrine_post_event_settling_design_record,
    run_mimetic_endocrine_post_event_settling_design_minimal_check,
    validate_mimetic_endocrine_post_event_settling_design_record,
)


class MimeticEndocrinePostEventSettlingDesignMinimalTests(unittest.TestCase):
    def setUp(self):
        self.record = build_mimetic_endocrine_post_event_settling_design_record()

    def test_valid_post_event_settling_design_record(self):
        result = validate_mimetic_endocrine_post_event_settling_design_record(self.record)
        self.assertTrue(result["valid"], result["error_codes"])
        self.assertEqual("mimetic_endocrine_post_event_settling_design", self.record["record_type"])
        self.assertEqual("valid_design_only_post_event_settling", self.record["design_status"])
        self.assertEqual(BOUNDARY_INDEX, self.record["boundary_index_before"])
        self.assertEqual(BOUNDARY_INDEX, self.record["boundary_index_after"])
        self.assertFalse(self.record["boundary_change_required"])

    def test_four_axis_source_is_checked(self):
        source = self.record["source_four_axis_trace_integration"]
        result = validate_mimetic_endocrine_post_event_settling_design_record(self.record)
        self.assertTrue(result["four_axis_source_checked"])
        self.assertEqual("ok", source["status"])
        self.assertEqual(4, source["axis_count"])
        self.assertEqual(4, source["axis_complete_count"])
        self.assertGreaterEqual(source["total_valid_trace_count"], 4)
        self.assertEqual(0, source["endocrine_runtime_count"])

    def test_four_axis_settling_roles_are_present(self):
        roles = self.record["axis_settling_roles"]
        self.assertEqual(
            {"dopamine_like", "norepinephrine_like", "cortisol_like", "oxytocin_like"},
            set(roles),
        )
        self.assertEqual("reward_decay_to_baseline", roles["dopamine_like"]["settling_role"])
        self.assertEqual("attention_interrupt_then_settle", roles["norepinephrine_like"]["settling_role"])
        self.assertEqual("pressure_decay_or_safety_reset", roles["cortisol_like"]["settling_role"])
        self.assertEqual("comfort_modulated_settling", roles["oxytocin_like"]["settling_role"])

    def test_settling_modes_are_design_only(self):
        result = validate_mimetic_endocrine_post_event_settling_design_record(self.record)
        self.assertEqual(set(SETTLING_MODES), set(self.record["settling_modes"]))
        self.assertTrue(result["natural_settling_designed"])
        self.assertTrue(result["comfort_modulated_settling_designed"])
        self.assertTrue(result["attention_interrupt_settling_designed"])
        self.assertTrue(result["safety_reset_designed"])
        self.assertTrue(result["evidence_for_review_designed"])
        self.assertTrue(result["all_settling_modes_design_only"])
        for mode in self.record["settling_modes"].values():
            self.assertFalse(mode["implemented_as_runtime"])

    def test_safety_reset_is_sedation_metaphor_only(self):
        safety_reset = self.record["settling_modes"]["safety_reset"]
        self.assertTrue(safety_reset["sedation_metaphor_only"])
        self.assertFalse(safety_reset["medical_sedation_claim"])
        self.assertFalse(safety_reset["implemented_as_runtime"])

    def test_evidence_review_does_not_write_memory(self):
        evidence = self.record["settling_modes"]["evidence_for_review"]
        self.assertFalse(evidence["memory_write_allowed"])
        self.assertFalse(evidence["retention_write_allowed"])

    def test_boundaries_block_runtime_and_action_effects(self):
        result = validate_mimetic_endocrine_post_event_settling_design_record(self.record)
        self.assertTrue(result["design_only_blocked"])
        self.assertTrue(result["endocrine_runtime_blocked"])
        self.assertTrue(result["settling_runtime_blocked"])
        self.assertTrue(result["safety_reset_runtime_blocked"])
        self.assertTrue(result["action_selection_blocked"])
        self.assertTrue(result["action_creation_blocked"])
        self.assertTrue(result["memory_write_blocked"])
        self.assertTrue(result["retention_write_blocked"])
        self.assertTrue(result["predictor_mutation_blocked"])
        self.assertTrue(result["subjective_claim_blocked"])

    def test_missing_settling_mode_blocks(self):
        bad = deepcopy(self.record)
        bad["settling_modes"].pop("natural_settling")
        result = validate_mimetic_endocrine_post_event_settling_design_record(bad)
        self.assertFalse(result["valid"])
        self.assertIn("settling_modes_set_not_expected", result["error_codes"])

    def test_runtime_settling_blocks(self):
        for mode in SETTLING_MODES:
            bad = deepcopy(self.record)
            bad["settling_modes"][mode]["implemented_as_runtime"] = True
            result = validate_mimetic_endocrine_post_event_settling_design_record(bad)
            self.assertFalse(result["valid"], mode)
            self.assertIn(f"{mode}_implemented_as_runtime_not_expected", result["error_codes"])

    def test_medical_sedation_claim_blocks(self):
        bad = deepcopy(self.record)
        bad["settling_modes"]["safety_reset"]["medical_sedation_claim"] = True
        result = validate_mimetic_endocrine_post_event_settling_design_record(bad)
        self.assertFalse(result["valid"])
        self.assertIn("safety_reset_medical_sedation_claim_not_false", result["error_codes"])

    def test_action_memory_predictor_and_subjective_claims_block(self):
        for field in (
            "action_selection_influence",
            "selected_action_created",
            "final_action_created",
            "direct_command_created",
            "memory_write",
            "retention_write",
            "predictor_mutation",
            "subjective_emotion_claim",
            "consciousness_claim",
            "proof_of_learning_claim",
        ):
            bad = deepcopy(self.record)
            bad["design_boundaries"][field] = True
            result = validate_mimetic_endocrine_post_event_settling_design_record(bad)
            self.assertFalse(result["valid"], field)
            self.assertIn(f"design_boundaries_{field}_not_false", result["error_codes"])

    def test_blocked_flags_true_block(self):
        for field in self.record["blocked_flags"]:
            bad = deepcopy(self.record)
            bad["blocked_flags"][field] = True
            result = validate_mimetic_endocrine_post_event_settling_design_record(bad)
            self.assertFalse(result["valid"], field)
            self.assertIn(f"blocked_flags_{field}_not_false", result["error_codes"])

    def test_human_summary_fields_required(self):
        for field in self.record["human_summary"]:
            bad = deepcopy(self.record)
            bad["human_summary"][field] = ""
            result = validate_mimetic_endocrine_post_event_settling_design_record(bad)
            self.assertFalse(result["valid"], field)
            self.assertIn(f"human_summary_{field}_empty", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        result = run_mimetic_endocrine_post_event_settling_design_minimal_check()
        summary = result["summary"]
        self.assertEqual("ok", result["status"])
        self.assertEqual(1, summary["valid_post_event_settling_design_count"])
        self.assertEqual(66, summary["invalid_post_event_settling_design_count"])
        self.assertEqual(1, summary["four_axis_source_checked_count"])
        self.assertEqual(1, summary["natural_settling_design_count"])
        self.assertEqual(1, summary["comfort_modulated_settling_design_count"])
        self.assertEqual(1, summary["attention_interrupt_settling_design_count"])
        self.assertEqual(1, summary["safety_reset_design_count"])
        self.assertEqual(1, summary["evidence_for_review_design_count"])
        self.assertEqual(1, summary["all_settling_modes_design_only_count"])
        self.assertEqual(1, summary["endocrine_runtime_blocked_count"])
        self.assertEqual(1, summary["settling_runtime_blocked_count"])
        self.assertEqual(1, summary["safety_reset_runtime_blocked_count"])
        self.assertEqual(1, summary["action_selection_blocked_count"])
        self.assertEqual(1, summary["memory_write_blocked_count"])
        self.assertEqual(1, summary["predictor_mutation_blocked_count"])
        self.assertEqual(1, summary["subjective_claim_blocked_count"])
        self.assertTrue(summary["all_mimetic_endocrine_post_event_settling_design_checks_passed"])


if __name__ == "__main__":
    unittest.main()
