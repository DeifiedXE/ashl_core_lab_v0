import copy
import unittest

from ashl_core.qingyin_internal_response_modulation_minimal import (
    BOUNDARY_INDEX_AFTER,
    OUTCOME_RESPONSE_MAP,
    build_qingyin_internal_response_modulation_record,
    run_qingyin_internal_response_modulation_minimal_check,
    validate_qingyin_internal_response_modulation_record,
)
from ashl_core.teaching_cli import run_command


class QingyinInternalResponseModulationMinimalTests(unittest.TestCase):
    def test_valid_internal_response_modulation_record_is_created(self):
        record = build_qingyin_internal_response_modulation_record()
        result = validate_qingyin_internal_response_modulation_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual(record["record_type"], "qingyin_internal_response_modulation")
        self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)

    def test_mapping_is_generic_not_candy_specific(self):
        record = build_qingyin_internal_response_modulation_record()
        mapping = record["outcome_response_mapping"]

        self.assertTrue(mapping["mapping_schema_generic"])
        self.assertTrue(mapping["candy_contact_is_demo_only"])
        self.assertEqual(mapping["supported_outcome_types"], OUTCOME_RESPONSE_MAP)
        self.assertEqual(mapping["supported_outcome_types"]["blocked_or_failed"], "cortisol_like")
        self.assertEqual(mapping["supported_outcome_types"]["unexpected_change"], "norepinephrine_like")
        self.assertEqual(mapping["supported_outcome_types"]["trusted_help_or_mentor_support"], "oxytocin_like")

    def test_demo_candy_contact_creates_dopamine_like_response_trace(self):
        record = build_qingyin_internal_response_modulation_record()
        source = record["source_action_outcome_trace"]
        response = record["internal_response_trace"]
        signal = response["signal_record"]

        self.assertEqual(source["outcome_type"], "candy_contact")
        self.assertEqual(response["response_axis"], "dopamine_like")
        self.assertEqual(signal["signal_name"], "dopamine_like")
        self.assertTrue(response["signal_valid"])
        self.assertTrue(signal["blocked_from_action_selection"])
        self.assertTrue(signal["blocked_from_memory_write"])
        self.assertTrue(signal["blocked_from_candidate_approval"])
        self.assertFalse(signal["subjective_claim"])

    def test_same_session_modulation_state_is_preview_only(self):
        record = build_qingyin_internal_response_modulation_record()
        state = record["same_session_modulation_state_preview"]

        self.assertTrue(state["modulation_state_created"])
        self.assertEqual(state["modulation_scope"], "same_session_sandbox_only")
        self.assertTrue(state["decay_required"])
        self.assertTrue(state["rollback_available"])
        self.assertFalse(state["cross_session_available"])
        self.assertFalse(state["persistent_state_written"])
        self.assertFalse(state["memory_write_performed"])
        self.assertFalse(state["predictor_mutation_performed"])

    def test_candidate_ordering_pressure_does_not_create_action(self):
        record = build_qingyin_internal_response_modulation_record()
        pressure = record["candidate_ordering_pressure_preview"]

        self.assertTrue(pressure["pressure_preview_created"])
        self.assertEqual(pressure["pressure_scope"], "same_session_sandbox_candidate_ordering_only")
        self.assertEqual(pressure["candidate_ordering_pressure"], "approach_reward_compatible")
        self.assertEqual(pressure["suggested_delta"], 0.05)
        self.assertTrue(pressure["advisory_only"])
        self.assertFalse(pressure["selected_action_created"])
        self.assertFalse(pressure["final_action_created"])
        self.assertFalse(pressure["direct_command_created"])
        self.assertFalse(pressure["production_behavior_changed"])

    def test_rollback_preview_restores_baseline_without_dirty_state(self):
        record = build_qingyin_internal_response_modulation_record()
        rollback = record["rollback_preview"]

        self.assertEqual(rollback["rollback_status"], "available_not_applied")
        self.assertTrue(rollback["session_end_restores_baseline"])
        self.assertFalse(rollback["dirty_state_after_rollback"])
        self.assertFalse(rollback["persistent_update_performed"])

    def test_blocked_flags_keep_boundaries_closed(self):
        record = build_qingyin_internal_response_modulation_record()
        flags = record["blocked_flags"]

        for field in (
            "sandbox_specific_behavior_created",
            "selected_action_created",
            "final_action_created",
            "direct_command_created",
            "memory_write_performed",
            "retention_write_performed",
            "predictor_mutation_performed",
            "endocrine_runtime_state_persisted",
            "biological_hormone_claim_allowed",
            "subjective_emotion_claim_allowed",
            "subjective_pleasure_claim_allowed",
            "proof_of_learning_claim_allowed",
        ):
            self.assertFalse(flags[field])

    def test_candy_specific_architecture_blocks(self):
        record = build_qingyin_internal_response_modulation_record()
        bad = copy.deepcopy(record)
        bad["modulation_context"]["architecture_scope"] = "candy_sandbox_specific_layer"

        result = validate_qingyin_internal_response_modulation_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("modulation_context_architecture_scope_not_expected", result["error_codes"])

    def test_unknown_outcome_type_blocks(self):
        record = build_qingyin_internal_response_modulation_record()
        bad = copy.deepcopy(record)
        bad["source_action_outcome_trace"]["outcome_type"] = "unknown"

        result = validate_qingyin_internal_response_modulation_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_action_outcome_trace_unknown_outcome_type", result["error_codes"])

    def test_cross_session_modulation_blocks(self):
        record = build_qingyin_internal_response_modulation_record()
        bad = copy.deepcopy(record)
        bad["same_session_modulation_state_preview"]["cross_session_available"] = True

        result = validate_qingyin_internal_response_modulation_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("same_session_modulation_state_preview_cross_session_available_not_expected", result["error_codes"])

    def test_selected_action_created_blocks(self):
        record = build_qingyin_internal_response_modulation_record()
        bad = copy.deepcopy(record)
        bad["candidate_ordering_pressure_preview"]["selected_action_created"] = True

        result = validate_qingyin_internal_response_modulation_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("candidate_ordering_pressure_preview_selected_action_created_not_expected", result["error_codes"])

    def test_memory_write_blocks(self):
        record = build_qingyin_internal_response_modulation_record()
        bad = copy.deepcopy(record)
        bad["same_session_modulation_state_preview"]["memory_write_performed"] = True

        result = validate_qingyin_internal_response_modulation_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("same_session_modulation_state_preview_memory_write_performed_not_expected", result["error_codes"])

    def test_subjective_claim_blocks(self):
        record = build_qingyin_internal_response_modulation_record()
        bad = copy.deepcopy(record)
        bad["internal_response_trace"]["subjective_claim"] = True

        result = validate_qingyin_internal_response_modulation_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("internal_response_trace_subjective_claim", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        result = run_qingyin_internal_response_modulation_minimal_check()
        summary = result["summary"]

        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["valid_internal_response_modulation_count"], 1)
        self.assertEqual(summary["invalid_internal_response_modulation_count"], 35)
        self.assertEqual(summary["generic_mapping_checked_count"], 1)
        self.assertEqual(summary["internal_response_trace_valid_count"], 1)
        self.assertEqual(summary["same_session_modulation_created_count"], 1)
        self.assertEqual(summary["candidate_ordering_pressure_created_count"], 1)
        self.assertEqual(summary["selected_action_blocked_count"], 1)
        self.assertTrue(summary["all_internal_response_modulation_checks_passed"])

    def test_cli_command(self):
        result = run_command("run-qingyin-internal-response-modulation-minimal-check")

        self.assertEqual(result["command"], "run-qingyin-internal-response-modulation-minimal-check")
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
