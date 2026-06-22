import copy
import unittest

from ashl_core.qingyin_bridge_grounded_capability_map_minimal import (
    BOUNDARY_INDEX_AFTER,
    build_qingyin_bridge_grounded_capability_map_record,
    run_qingyin_bridge_grounded_capability_map_minimal_check,
    validate_qingyin_bridge_grounded_capability_map_record,
)
from ashl_core.teaching_cli import run_command


class QingyinBridgeGroundedCapabilityMapMinimalTests(unittest.TestCase):
    def test_valid_grounded_capability_map_is_created(self):
        record = build_qingyin_bridge_grounded_capability_map_record()
        result = validate_qingyin_bridge_grounded_capability_map_record(record)

        self.assertTrue(result["valid"])
        self.assertEqual(record["record_type"], "qingyin_bridge_grounded_capability_map")
        self.assertEqual(record["boundary_index_after"], BOUNDARY_INDEX_AFTER)
        self.assertTrue(record["capability_map"]["capability_map_created"])

    def test_visible_object_echoes_grounded_front_symbol(self):
        record = build_qingyin_bridge_grounded_capability_map_record()
        visible = record["capability_map"]["visible_objects"][0]
        alignment = record["grounding_alignment"]

        self.assertEqual(visible["id"], "sandbox.front_cell")
        self.assertEqual(visible["front_symbol"], "e")
        self.assertEqual(visible["body_direction"], "front")
        self.assertEqual(alignment["grounded_text_token"], "front_symbol:e")
        self.assertTrue(alignment["symbolic_text_grounding_only"])

    def test_declared_capabilities_are_sandbox_body_capabilities(self):
        record = build_qingyin_bridge_grounded_capability_map_record()
        capability_ids = [item["id"] for item in record["capability_map"]["declared_capabilities"]]

        self.assertEqual(capability_ids, [
            "sandbox.body.step_forward",
            "sandbox.body.turn_left",
            "sandbox.body.turn_right",
            "sandbox.body.reach_front",
        ])
        self.assertTrue(all(item["risk"] == "low" for item in record["capability_map"]["declared_capabilities"]))
        self.assertTrue(all(item["execution_allowed"] is False for item in record["capability_map"]["declared_capabilities"]))

    def test_declared_and_discovered_are_kept_separate(self):
        record = build_qingyin_bridge_grounded_capability_map_record()

        self.assertIn("visible_objects", record["capability_map"])
        self.assertIn("declared_capabilities", record["capability_map"])
        self.assertIn("bindings", record["capability_map"])
        self.assertTrue(record["grounding_alignment"]["declared_and_discovered_kept_separate"])

    def test_item_front_binds_reach_front_as_available(self):
        result = run_qingyin_bridge_grounded_capability_map_minimal_check()
        item_record = result["valid_records"][2]
        reach_binding = [
            item for item in item_record["capability_map"]["bindings"]
            if item["capability"] == "sandbox.body.reach_front"
        ][0]

        self.assertEqual(item_record["source_affordance_bridge"]["front_symbol"], "i")
        self.assertTrue(reach_binding["available"])

    def test_wall_front_blocks_step_forward_binding(self):
        result = run_qingyin_bridge_grounded_capability_map_minimal_check()
        wall_record = result["valid_records"][1]
        step_binding = [
            item for item in wall_record["capability_map"]["bindings"]
            if item["capability"] == "sandbox.body.step_forward"
        ][0]

        self.assertEqual(wall_record["source_affordance_bridge"]["front_symbol"], "w")
        self.assertFalse(step_binding["available"])

    def test_no_action_intent_gateway_or_execution_is_created(self):
        record = build_qingyin_bridge_grounded_capability_map_record()

        self.assertFalse(record["capability_map"]["action_intent_created"])
        self.assertFalse(record["capability_map"]["action_gateway_called"])
        self.assertFalse(record["capability_map"]["execution_created"])
        self.assertFalse(record["blocked_flags"]["action_intent_created"])
        self.assertFalse(record["blocked_flags"]["action_gateway_called"])
        self.assertFalse(record["blocked_flags"]["sandbox_execution_created"])

    def test_feedback_does_not_directly_feed_endocrine_or_tendency(self):
        record = build_qingyin_bridge_grounded_capability_map_record()
        feedback = record["feedback_boundary"]

        self.assertFalse(feedback["feedback_packet_created"])
        self.assertTrue(feedback["feedback_must_enter_trace_first"])
        self.assertFalse(feedback["direct_endocrine_feed_allowed"])
        self.assertFalse(feedback["direct_tendency_feed_allowed"])
        self.assertTrue(feedback["requires_proto_purpose_review_approval_before_influence"])

    def test_semantic_vision_object_recognition_and_raw_api_are_blocked(self):
        record = build_qingyin_bridge_grounded_capability_map_record()

        self.assertFalse(record["visual_simulation_eye"]["semantic_vision"])
        self.assertFalse(record["visual_simulation_eye"]["object_recognition"])
        self.assertFalse(record["operational_simulation_eye"]["raw_api_access"])

    def test_bad_binding_blocks(self):
        record = build_qingyin_bridge_grounded_capability_map_record()
        bad = copy.deepcopy(record)
        bad["capability_map"]["bindings"][0]["creates_action_intent"] = True

        result = validate_qingyin_bridge_grounded_capability_map_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("binding_sandbox.body.step_forward_creates_action_intent_not_false", result["error_codes"])

    def test_direct_feedback_to_tendency_blocks(self):
        record = build_qingyin_bridge_grounded_capability_map_record()
        bad = copy.deepcopy(record)
        bad["feedback_boundary"]["direct_tendency_feed_allowed"] = True

        result = validate_qingyin_bridge_grounded_capability_map_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("feedback_boundary_direct_tendency_feed_allowed_not_expected", result["error_codes"])

    def test_blocked_flags_true_block(self):
        record = build_qingyin_bridge_grounded_capability_map_record()
        bad = copy.deepcopy(record)
        bad["blocked_flags"]["predictor_modified"] = True

        result = validate_qingyin_bridge_grounded_capability_map_record(bad)

        self.assertFalse(result["valid"])
        self.assertIn("blocked_flags_predictor_modified_not_false", result["error_codes"])

    def test_demo_summary_counts_are_deterministic(self):
        result = run_qingyin_bridge_grounded_capability_map_minimal_check()
        summary = result["summary"]

        self.assertEqual(result["status"], "ok")
        self.assertEqual(summary["capability_map_result_count"], 50)
        self.assertEqual(summary["valid_capability_map_count"], 3)
        self.assertEqual(summary["invalid_capability_map_count"], 47)
        self.assertEqual(summary["visible_object_total"], 3)
        self.assertEqual(summary["declared_capability_total"], 12)
        self.assertEqual(summary["binding_total"], 12)
        self.assertEqual(summary["front_empty_record_count"], 1)
        self.assertEqual(summary["front_wall_record_count"], 1)
        self.assertEqual(summary["front_item_record_count"], 1)
        self.assertEqual(summary["action_intent_blocked_count"], 3)
        self.assertEqual(summary["direct_feedback_to_tendency_blocked_count"], 3)

    def test_cli_command(self):
        result = run_command("run-qingyin-bridge-grounded-capability-map-minimal-check")

        self.assertEqual(result["command"], "run-qingyin-bridge-grounded-capability-map-minimal-check")
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
