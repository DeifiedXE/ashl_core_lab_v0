import unittest

from flask import Flask

from ashl_core.larger_sandbox_flask_ui import (
    DEFAULT_UI_HOST,
    DEFAULT_UI_PORT,
    apply_ui_action,
    build_ui_boundary_check,
    create_app,
    get_launch_config,
    get_ui_state,
    reset_ui_state,
)
from ashl_core.simulated_vision_larger_sandbox import run_simulated_vision_larger_sandbox_demo
from ashl_core.teaching_cli import run_command


class LargerSandboxFlaskUiTests(unittest.TestCase):
    def setUp(self):
        reset_ui_state()
        self.app = create_app()
        self.client = self.app.test_client()

    def test_create_app_returns_flask_app(self):
        self.assertIsInstance(self.app, Flask)

    def test_get_index_renders_visual_ui(self):
        response = self.client.get("/")
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Larger Sandbox", html)
        self.assertIn("Level: simulated_vision_larger_sandbox_v0", html)
        self.assertIn("Position: [2, 2]", html)
        self.assertIn("Facing: north", html)
        self.assertIn("First-person viewport", html)
        self.assertIn("w", html)
        self.assertIn("e", html)
        self.assertIn("a", html)
        self.assertIn("look", html)
        self.assertIn("turn_left", html)
        self.assertIn("turn_right", html)
        self.assertIn("move_forward", html)
        self.assertIn("reset", html)
        self.assertIn("No pathfinding.", html)

    def test_state_json_is_read_only_snapshot(self):
        response = self.client.get("/state.json")
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["level_id"], "simulated_vision_larger_sandbox_v0")
        self.assertEqual(data["pos"], [2, 2])
        self.assertEqual(data["facing"], "north")
        self.assertEqual(data["front_symbol"], "e")
        self.assertEqual(data["viewport"][2][1], "a")

    def test_post_action_look_redirects_and_logs(self):
        response = self.client.post("/action", data={"action": "look"})
        state = get_ui_state()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(state["pos"], [2, 2])
        self.assertEqual(state["facing"], "north")
        self.assertIn("Step 1: look", state["action_log"][0])
        self.assertIn("Result: observed", state["action_log"][0])

    def test_post_action_turn_right_updates_facing(self):
        response = self.client.post("/action", data={"action": "turn_right"})
        state = get_ui_state()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(state["pos"], [2, 2])
        self.assertEqual(state["facing"], "east")
        self.assertIn("Step 1: turn_right", state["action_log"][0])

    def test_post_action_move_forward_appends_human_log(self):
        self.client.post("/action", data={"action": "turn_right"})
        response = self.client.post("/action", data={"action": "move_forward"})
        state = get_ui_state()
        log = "\n\n".join(state["action_log"])

        self.assertEqual(response.status_code, 302)
        self.assertEqual(state["pos"], [3, 2])
        self.assertIn("Step 2: move_forward", log)
        self.assertIn("Before: [2,2], facing east", log)
        self.assertIn("Front symbol: e", log)
        self.assertIn("Result: moved", log)
        self.assertIn("After: [3,2], facing east", log)

    def test_post_reset_restores_initial_state_and_empty_log(self):
        self.client.post("/action", data={"action": "turn_right"})
        self.client.post("/action", data={"action": "move_forward"})
        response = self.client.post("/reset")
        state = get_ui_state()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(state["pos"], [2, 2])
        self.assertEqual(state["facing"], "north")
        self.assertEqual(state["action_log"], [])

    def test_invalid_action_returns_400(self):
        response = self.client.post("/action", data={"action": "auto_explore"})

        self.assertEqual(response.status_code, 400)

    def test_launch_config_defaults_to_localhost(self):
        config = get_launch_config()
        boundary = config["boundary_check"]

        self.assertEqual(config["command"], "run-larger-sandbox-ui")
        self.assertEqual(config["url"], "http://127.0.0.1:7860")
        self.assertEqual(config["host"], DEFAULT_UI_HOST)
        self.assertEqual(config["port"], DEFAULT_UI_PORT)
        self.assertTrue(config["local_only"])
        self.assertTrue(boundary["ui_prototype"])
        self.assertTrue(boundary["local_only"])
        self.assertFalse(boundary["runtime_behavior_modified"])
        self.assertFalse(boundary["pathfinding_used"])
        self.assertFalse(boundary["route_planner_added"])
        self.assertFalse(boundary["item_collection_enabled"])
        self.assertFalse(boundary["exit_activation_enabled"])

    def test_run_command_reports_nonblocking_launch_config(self):
        result = run_command("run-larger-sandbox-ui")

        self.assertEqual(result["command"], "run-larger-sandbox-ui")
        self.assertEqual(result["url"], "http://127.0.0.1:7860")
        self.assertTrue(result["local_only"])

    def test_boundary_check_denies_out_of_scope_capabilities(self):
        boundary = build_ui_boundary_check()

        self.assertTrue(boundary["ui_prototype"])
        self.assertTrue(boundary["local_only"])
        self.assertFalse(boundary["action_selection_modified"])
        self.assertFalse(boundary["item_pickup_enabled"])
        self.assertFalse(boundary["inventory_enabled"])
        self.assertFalse(boundary["win_condition_enabled"])
        self.assertFalse(boundary["task_completion_enabled"])
        self.assertFalse(boundary["curiosity_enabled"])
        self.assertFalse(boundary["prediction_error_enabled"])
        self.assertFalse(boundary["place_memory_enabled"])
        self.assertFalse(boundary["home_sandbox_enabled"])
        self.assertFalse(boundary["real_image_vision"])
        self.assertFalse(boundary["computer_vision"])
        self.assertFalse(boundary["llm_vision_used"])
        self.assertFalse(boundary["llm_planning_used"])
        self.assertFalse(boundary["lesson_store_write"])
        self.assertFalse(boundary["memory_layer_write"])
        self.assertFalse(boundary["long_term_memory_write"])

    def test_ui_does_not_modify_runtime_movement_rules(self):
        before = run_simulated_vision_larger_sandbox_demo()
        apply_ui_action("turn_right")
        apply_ui_action("move_forward")
        after = run_simulated_vision_larger_sandbox_demo()

        self.assertEqual(after["action_trace"], before["action_trace"])
        self.assertEqual(after["boundary_check"], before["boundary_check"])


if __name__ == "__main__":
    unittest.main()
