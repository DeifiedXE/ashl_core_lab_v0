import copy
import unittest

from ashl_core.minimal_body_schema_affordance_consistency_runtime import (
    BOUNDARY_INDEX_AFTER,
    build_minimal_body_schema_affordance_consistency_record,
    run_minimal_body_schema_affordance_consistency_runtime_check,
    validate_minimal_body_schema_affordance_consistency_record,
)
from ashl_core.teaching_cli import run_command
from ashl_core.visual_spatial_motor_affordance_bridge_minimal import (
    run_visual_spatial_motor_affordance_bridge_minimal_check,
)


class MinimalBodySchemaAffordanceConsistencyRuntimeTests(unittest.TestCase):
    def test_valid_body_schema_consistency_record_is_created(self):
        record = build_minimal_body_schema_affordance_consistency_record()
        result = validate_minimal_body_schema_affordance_consistency_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual(record["record_type"], "minimal_body_schema_affordance_consistency_runtime")
        self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)

    def test_body_position_and_facing_match_source_affordance_bridge(self):
        record = build_minimal_body_schema_affordance_consistency_record()
        source = record["source_affordance_bridge"]
        body = record["minimal_body_schema_state"]
        consistency = record["affordance_consistency_result"]

        self.assertEqual(body["position"], source["agent_position"])
        self.assertEqual(body["facing"], source["facing"])
        self.assertTrue(consistency["body_position_matches_visual_source"])
        self.assertTrue(consistency["body_facing_matches_visual_source"])

    def test_ready_body_allows_empty_front_step_and_turn_but_not_reach(self):
        record = build_minimal_body_schema_affordance_consistency_record()
        readiness = record["motor_readiness_preview"]

        self.assertTrue(readiness["step_forward_ready"])
        self.assertTrue(readiness["turn_left_ready"])
        self.assertTrue(readiness["turn_right_ready"])
        self.assertFalse(readiness["reach_front_ready"])
        self.assertFalse(readiness["body_blocks_movement"])

    def test_wall_front_blocks_step_through_affordance_not_body(self):
        wall_bridge = run_visual_spatial_motor_affordance_bridge_minimal_check()["valid_records"][1]
        record = build_minimal_body_schema_affordance_consistency_record(wall_bridge)
        readiness = record["motor_readiness_preview"]

        self.assertTrue(readiness["front_blocked_by_affordance"])
        self.assertFalse(readiness["step_forward_ready"])
        self.assertTrue(readiness["turn_left_ready"])
        self.assertTrue(readiness["turn_right_ready"])
        self.assertFalse(readiness["body_blocks_movement"])

    def test_item_front_allows_reach_when_hand_is_empty(self):
        item_bridge = run_visual_spatial_motor_affordance_bridge_minimal_check()["valid_records"][2]
        record = build_minimal_body_schema_affordance_consistency_record(item_bridge)
        readiness = record["motor_readiness_preview"]

        self.assertTrue(readiness["step_forward_ready"])
        self.assertTrue(readiness["reach_front_ready"])

    def test_energy_zero_blocks_movement_readiness(self):
        record = build_minimal_body_schema_affordance_consistency_record()
        bad = copy.deepcopy(record)
        bad["minimal_body_schema_state"]["energy"] = 0.0

        expected = build_minimal_body_schema_affordance_consistency_record(
            body_schema_state=bad["minimal_body_schema_state"]
        )

        self.assertTrue(expected["motor_readiness_preview"]["body_blocks_movement"])
        self.assertIn("energy_depleted", expected["motor_readiness_preview"]["blocked_by_body_state_reasons"])
        self.assertFalse(expected["motor_readiness_preview"]["step_forward_ready"])

    def test_cooldown_blocks_movement_readiness(self):
        record = build_minimal_body_schema_affordance_consistency_record()
        body = copy.deepcopy(record["minimal_body_schema_state"])
        body["movement_cooldown_ticks"] = 2
        expected = build_minimal_body_schema_affordance_consistency_record(body_schema_state=body)

        self.assertTrue(expected["motor_readiness_preview"]["body_blocks_movement"])
        self.assertIn("movement_cooldown_active", expected["motor_readiness_preview"]["blocked_by_body_state_reasons"])
        self.assertFalse(expected["motor_readiness_preview"]["turn_left_ready"])

    def test_unstable_balance_blocks_locomotion_readiness(self):
        record = build_minimal_body_schema_affordance_consistency_record()
        body = copy.deepcopy(record["minimal_body_schema_state"])
        body["balance"] = "unstable"
        expected = build_minimal_body_schema_affordance_consistency_record(body_schema_state=body)

        self.assertTrue(expected["motor_readiness_preview"]["body_blocks_movement"])
        self.assertIn("balance_not_stable", expected["motor_readiness_preview"]["blocked_by_body_state_reasons"])
        self.assertFalse(expected["motor_readiness_preview"]["step_forward_ready"])

    def test_occupied_hand_blocks_reach_readiness(self):
        item_bridge = run_visual_spatial_motor_affordance_bridge_minimal_check()["valid_records"][2]
        record = build_minimal_body_schema_affordance_consistency_record(item_bridge)
        body = copy.deepcopy(record["minimal_body_schema_state"])
        body["hand_state"] = "occupied"
        expected = build_minimal_body_schema_affordance_consistency_record(item_bridge, body)

        self.assertFalse(expected["motor_readiness_preview"]["reach_front_ready"])
        self.assertIn("hand_not_empty", expected["motor_readiness_preview"]["blocked_by_body_state_reasons"])

    def test_contact_state_blocks_normal_movement(self):
        record = build_minimal_body_schema_affordance_consistency_record()
        body = copy.deepcopy(record["minimal_body_schema_state"])
        body["contact_state"] = "front_contact"
        expected = build_minimal_body_schema_affordance_consistency_record(body_schema_state=body)

        self.assertTrue(expected["motor_readiness_preview"]["body_blocks_movement"])
        self.assertIn("contact_state_not_clear", expected["motor_readiness_preview"]["blocked_by_body_state_reasons"])
        self.assertFalse(expected["motor_readiness_preview"]["step_forward_ready"])

    def test_position_mismatch_blocks(self):
        record = build_minimal_body_schema_affordance_consistency_record()
        bad = copy.deepcopy(record)
        bad["minimal_body_schema_state"]["position"] = [99, 99]

        result = validate_minimal_body_schema_affordance_consistency_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn(
            "affordance_consistency_result_body_position_matches_visual_source_not_expected",
            result["error_codes"],
        )

    def test_selected_motor_intent_blocks(self):
        record = build_minimal_body_schema_affordance_consistency_record()
        bad = copy.deepcopy(record)
        bad["motor_readiness_preview"]["selected_motor_intent"] = "step_forward"

        result = validate_minimal_body_schema_affordance_consistency_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("motor_readiness_preview_selected_motor_intent_not_expected", result["error_codes"])
        self.assertIn("motor_readiness_preview_selected_motor_intent_not_none", result["error_codes"])

    def test_motor_execution_blocks(self):
        record = build_minimal_body_schema_affordance_consistency_record()
        bad = copy.deepcopy(record)
        bad["motor_readiness_preview"]["motor_action_executed"] = True

        result = validate_minimal_body_schema_affordance_consistency_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("motor_readiness_preview_motor_action_executed_not_expected", result["error_codes"])

    def test_persistent_body_schema_blocks(self):
        record = build_minimal_body_schema_affordance_consistency_record()
        bad = copy.deepcopy(record)
        bad["minimal_body_schema_state"]["persistent_body_schema_written"] = True

        result = validate_minimal_body_schema_affordance_consistency_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("minimal_body_schema_state_persistent_body_schema_written_not_false", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        result = run_minimal_body_schema_affordance_consistency_runtime_check()
        summary = result["summary"]

        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["body_schema_consistency_result_count"], 32)
        self.assertEqual(summary["valid_body_schema_consistency_count"], 3)
        self.assertEqual(summary["invalid_body_schema_consistency_count"], 29)
        self.assertEqual(summary["step_forward_ready_count"], 2)
        self.assertEqual(summary["reach_front_ready_count"], 1)
        self.assertEqual(summary["front_blocked_by_affordance_count"], 1)
        self.assertEqual(summary["body_blocks_movement_count"], 0)
        self.assertEqual(summary["selected_motor_intent_blocked_count"], 3)
        self.assertEqual(summary["direct_command_blocked_count"], 3)

    def test_cli_command(self):
        result = run_command("run-minimal-body-schema-affordance-consistency-runtime-check")

        self.assertEqual(result["command"], "run-minimal-body-schema-affordance-consistency-runtime-check")
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
