import copy
import unittest

from ashl_core.teaching_cli import run_command
from ashl_core.visual_spatial_motor_affordance_bridge_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_visual_spatial_motor_affordance_bridge_record,
    run_visual_spatial_motor_affordance_bridge_minimal_check,
    validate_visual_spatial_motor_affordance_bridge_record,
)
from ashl_core.visual_spatial_grounding_minimal import build_visual_spatial_grounding_record


class VisualSpatialMotorAffordanceBridgeMinimalTests(unittest.TestCase):
    def test_valid_affordance_bridge_record_is_created(self):
        record = build_visual_spatial_motor_affordance_bridge_record()
        result = validate_visual_spatial_motor_affordance_bridge_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual(record["record_type"], "visual_spatial_motor_affordance_bridge")
        self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)

    def test_empty_front_allows_step_and_turn_but_not_reach(self):
        record = build_visual_spatial_motor_affordance_bridge_record()
        summary = record["affordance_summary"]

        self.assertEqual(summary["front_symbol"], "e")
        self.assertTrue(summary["can_step_forward"])
        self.assertFalse(summary["front_blocked"])
        self.assertTrue(summary["can_turn_left"])
        self.assertTrue(summary["can_turn_right"])
        self.assertFalse(summary["can_reach_front"])
        self.assertFalse(summary["front_contact_possible"])

    def test_wall_front_blocks_step_but_allows_turns(self):
        source = build_visual_spatial_grounding_record()
        source["source_visual_observation"]["front_symbol"] = "w"
        source["source_visual_observation"]["viewport"][1][1] = "w"
        for cell in source["spatial_cells"]:
            if cell["viewport_position"] == [1, 1]:
                cell["symbol"] = "w"
        source["front_cell_spatial_summary"]["front_symbol"] = "w"

        record = build_visual_spatial_motor_affordance_bridge_record(source)
        summary = record["affordance_summary"]

        self.assertEqual(summary["front_symbol"], "w")
        self.assertFalse(summary["can_step_forward"])
        self.assertTrue(summary["front_blocked"])
        self.assertTrue(summary["can_turn_left"])
        self.assertTrue(summary["can_turn_right"])

    def test_item_front_allows_step_and_reach_preview(self):
        source = build_visual_spatial_grounding_record()
        source["source_visual_observation"]["front_symbol"] = "i"
        source["source_visual_observation"]["viewport"][1][1] = "i"
        for cell in source["spatial_cells"]:
            if cell["viewport_position"] == [1, 1]:
                cell["symbol"] = "i"
        source["front_cell_spatial_summary"]["front_symbol"] = "i"

        record = build_visual_spatial_motor_affordance_bridge_record(source)
        summary = record["affordance_summary"]

        self.assertEqual(summary["front_symbol"], "i")
        self.assertTrue(summary["can_step_forward"])
        self.assertTrue(summary["can_reach_front"])
        self.assertTrue(summary["front_contact_possible"])

    def test_motor_intent_preview_does_not_select_or_execute(self):
        record = build_visual_spatial_motor_affordance_bridge_record()
        preview = record["motor_intent_preview"]

        self.assertTrue(preview["preview_created"])
        self.assertEqual(preview["selected_motor_intent"], None)
        self.assertFalse(preview["motor_action_executed"])
        self.assertFalse(preview["selected_action_created"])
        self.assertFalse(preview["final_action_created"])
        self.assertFalse(preview["direct_command_created"])
        self.assertEqual([item["motor_intent"] for item in preview["candidate_motor_intents"]], [
            "step_forward",
            "turn_left",
            "turn_right",
            "reach_front",
        ])
        self.assertTrue(all(item["preview_only"] for item in preview["candidate_motor_intents"]))
        self.assertTrue(all(item["execution_allowed"] is False for item in preview["candidate_motor_intents"]))

    def test_rule_set_blocks_semantic_pathfinding_and_goal_seeking(self):
        record = build_visual_spatial_motor_affordance_bridge_record()
        rules = record["affordance_rule_set"]

        self.assertTrue(rules["front_symbol_only_v0"])
        self.assertFalse(rules["semantic_interpretation_used"])
        self.assertFalse(rules["pathfinding_used"])
        self.assertFalse(rules["goal_seeking_used"])

    def test_unknown_front_symbol_blocks(self):
        record = build_visual_spatial_motor_affordance_bridge_record()
        bad = copy.deepcopy(record)
        bad["source_visual_spatial_grounding"]["front_symbol"] = "candy"

        result = validate_visual_spatial_motor_affordance_bridge_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_front_symbol_not_supported", result["error_codes"])

    def test_wrong_step_affordance_blocks(self):
        record = build_visual_spatial_motor_affordance_bridge_record()
        bad = copy.deepcopy(record)
        bad["body_relative_affordance_candidates"]["can_step_forward"]["available"] = False

        result = validate_visual_spatial_motor_affordance_bridge_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("affordance_can_step_forward_not_expected", result["error_codes"])

    def test_selected_motor_intent_blocks(self):
        record = build_visual_spatial_motor_affordance_bridge_record()
        bad = copy.deepcopy(record)
        bad["motor_intent_preview"]["selected_motor_intent"] = "step_forward"

        result = validate_visual_spatial_motor_affordance_bridge_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("motor_intent_preview_selected_motor_intent_not_expected", result["error_codes"])

    def test_motor_execution_blocks(self):
        record = build_visual_spatial_motor_affordance_bridge_record()
        bad = copy.deepcopy(record)
        bad["motor_intent_preview"]["motor_action_executed"] = True

        result = validate_visual_spatial_motor_affordance_bridge_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("motor_intent_preview_motor_action_executed_not_expected", result["error_codes"])

    def test_pathfinding_blocks(self):
        record = build_visual_spatial_motor_affordance_bridge_record()
        bad = copy.deepcopy(record)
        bad["affordance_rule_set"]["pathfinding_used"] = True

        result = validate_visual_spatial_motor_affordance_bridge_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("affordance_rule_set_pathfinding_used_not_expected", result["error_codes"])

    def test_persistent_body_schema_blocks(self):
        record = build_visual_spatial_motor_affordance_bridge_record()
        bad = copy.deepcopy(record)
        bad["blocked_flags"]["persistent_body_schema_written"] = True

        result = validate_visual_spatial_motor_affordance_bridge_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("blocked_flags_persistent_body_schema_written_not_false", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        result = run_visual_spatial_motor_affordance_bridge_minimal_check()
        summary = result["summary"]

        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["affordance_bridge_result_count"], 38)
        self.assertEqual(summary["valid_affordance_bridge_count"], 3)
        self.assertEqual(summary["invalid_affordance_bridge_count"], 35)
        self.assertEqual(summary["can_step_forward_count"], 2)
        self.assertEqual(summary["front_blocked_count"], 1)
        self.assertEqual(summary["can_reach_front_count"], 1)
        self.assertEqual(summary["selected_action_blocked_count"], 3)
        self.assertEqual(summary["direct_command_blocked_count"], 3)

    def test_cli_command(self):
        result = run_command("run-visual-spatial-motor-affordance-bridge-minimal-check")

        self.assertEqual(result["command"], "run-visual-spatial-motor-affordance-bridge-minimal-check")
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
