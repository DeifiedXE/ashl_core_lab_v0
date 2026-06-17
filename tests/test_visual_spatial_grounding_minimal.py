import copy
import unittest

from ashl_core.teaching_cli import run_command
from ashl_core.visual_spatial_grounding_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_visual_spatial_grounding_record,
    run_visual_spatial_grounding_minimal_check,
    validate_visual_spatial_grounding_record,
)


class VisualSpatialGroundingMinimalTests(unittest.TestCase):
    def test_valid_visual_spatial_grounding_record_is_created(self):
        record = build_visual_spatial_grounding_record()
        result = validate_visual_spatial_grounding_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual(record["record_type"], "visual_spatial_grounding")
        self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)

    def test_body_relative_position_direction_distance_are_created(self):
        record = build_visual_spatial_grounding_record()
        frame = record["body_relative_frame"]
        cells = record["spatial_cells"]

        self.assertTrue(frame["body_relative_coordinates_created"])
        self.assertTrue(frame["distance_estimates_created"])
        self.assertTrue(frame["direction_labels_created"])
        self.assertEqual(len(cells), 9)

    def test_front_far_front_and_agent_cells_are_grounded(self):
        record = build_visual_spatial_grounding_record()

        self.assertEqual(record["front_cell_spatial_summary"]["body_direction"], "front")
        self.assertEqual(record["front_cell_spatial_summary"]["distance_forward"], 1)
        self.assertEqual(record["front_cell_spatial_summary"]["manhattan_distance_from_agent"], 1)
        self.assertEqual(record["far_front_cell_spatial_summary"]["body_direction"], "front")
        self.assertEqual(record["far_front_cell_spatial_summary"]["distance_forward"], 2)
        self.assertEqual(record["agent_cell_spatial_summary"]["body_direction"], "self")
        self.assertEqual(record["agent_cell_spatial_summary"]["distance_forward"], 0)

    def test_source_is_visible_first_person_viewport_only(self):
        record = build_visual_spatial_grounding_record()
        source = record["source_visual_observation"]
        scope = record["grounding_scope"]

        self.assertTrue(source["first_person_viewport"])
        self.assertFalse(source["full_map_visible_to_agent"])
        self.assertFalse(source["real_image_vision"])
        self.assertTrue(scope["visible_cells_only"])
        self.assertFalse(scope["full_map_visible_to_agent"])

    def test_real_image_object_semantic_and_action_influence_are_blocked(self):
        record = build_visual_spatial_grounding_record()
        scope = record["grounding_scope"]
        flags = record["blocked_flags"]

        self.assertFalse(scope["real_image_vision"])
        self.assertFalse(scope["object_recognition"])
        self.assertFalse(scope["semantic_vision"])
        self.assertFalse(scope["action_selection_influence"])
        self.assertFalse(flags["active_focus_applied"])
        self.assertFalse(flags["selected_action_created"])
        self.assertFalse(flags["final_action_created"])
        self.assertFalse(flags["direct_command_created"])

    def test_wrong_facing_blocks(self):
        record = build_visual_spatial_grounding_record()
        bad = copy.deepcopy(record)
        bad["source_visual_observation"]["facing"] = "up"

        result = validate_visual_spatial_grounding_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("source_visual_observation_facing_invalid", result["error_codes"])

    def test_full_map_visible_blocks(self):
        record = build_visual_spatial_grounding_record()
        bad = copy.deepcopy(record)
        bad["grounding_scope"]["full_map_visible_to_agent"] = True

        result = validate_visual_spatial_grounding_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("grounding_scope_full_map_visible_to_agent_not_expected", result["error_codes"])

    def test_semantic_label_blocks(self):
        record = build_visual_spatial_grounding_record()
        bad = copy.deepcopy(record)
        bad["spatial_cells"][0]["semantic_label"] = "wall"

        result = validate_visual_spatial_grounding_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("spatial_cell_semantic_label_not_null", result["error_codes"])

    def test_wrong_distance_blocks(self):
        record = build_visual_spatial_grounding_record()
        bad = copy.deepcopy(record)
        bad["spatial_cells"][0]["distance_forward"] = 99

        result = validate_visual_spatial_grounding_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("spatial_cell_distance_forward_mismatch", result["error_codes"])

    def test_action_selection_influence_blocks(self):
        record = build_visual_spatial_grounding_record()
        bad = copy.deepcopy(record)
        bad["grounding_scope"]["action_selection_influence"] = True

        result = validate_visual_spatial_grounding_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("grounding_scope_action_selection_influence_not_expected", result["error_codes"])

    def test_body_schema_persistence_blocks(self):
        record = build_visual_spatial_grounding_record()
        bad = copy.deepcopy(record)
        bad["grounding_scope"]["body_schema_persistence"] = True

        result = validate_visual_spatial_grounding_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("grounding_scope_body_schema_persistence_not_expected", result["error_codes"])

    def test_memory_write_blocks(self):
        record = build_visual_spatial_grounding_record()
        bad = copy.deepcopy(record)
        bad["blocked_flags"]["memory_write_performed"] = True

        result = validate_visual_spatial_grounding_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("blocked_flags_memory_write_performed_not_false", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        result = run_visual_spatial_grounding_minimal_check()
        summary = result["summary"]

        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["visual_spatial_grounding_result_count"], 37)
        self.assertEqual(summary["valid_visual_spatial_grounding_count"], 1)
        self.assertEqual(summary["invalid_visual_spatial_grounding_count"], 36)
        self.assertEqual(summary["front_cell_grounded_count"], 1)
        self.assertEqual(summary["far_front_cell_grounded_count"], 1)
        self.assertEqual(summary["agent_cell_grounded_count"], 1)
        self.assertEqual(summary["action_selection_blocked_count"], 1)
        self.assertEqual(summary["body_schema_persistence_blocked_count"], 1)

    def test_cli_command(self):
        result = run_command("run-visual-spatial-grounding-minimal-check")

        self.assertEqual(result["command"], "run-visual-spatial-grounding-minimal-check")
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
