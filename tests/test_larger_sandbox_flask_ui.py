import unittest

from flask import Flask

from ashl_core.larger_sandbox_flask_ui import (
    DEFAULT_UI_HOST,
    DEFAULT_UI_PORT,
    apply_ui_action,
    build_ui_boundary_check,
    cooldown_remaining_seconds,
    create_app,
    get_launch_config,
    get_ui_state,
    reset_ui_state,
    reset_ui_now_func,
    set_ui_now_func,
)
from ashl_core.simulated_vision_larger_sandbox import run_simulated_vision_larger_sandbox_demo
from ashl_core.teaching_cli import run_command


class LargerSandboxFlaskUiTests(unittest.TestCase):
    def setUp(self):
        self.now = 100.0
        set_ui_now_func(lambda: self.now)
        reset_ui_state()
        self.app = create_app()
        self.client = self.app.test_client()

    def tearDown(self):
        reset_ui_now_func()
        reset_ui_state()

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
        self.assertIn("Action cooldown", html)
        self.assertIn("Qingyin Observation", html)
        self.assertIn("Mode", html)
        self.assertIn("manual observation", html)
        self.assertIn("symbolic sandbox body", html)
        self.assertIn("Visible symbols", html)
        self.assertIn("Cooldown: 0.5s", html)
        self.assertIn("Cooldown remaining: 0.00 seconds", html)
        self.assertIn("Can act: yes", html)
        self.assertIn("No pathfinding.", html)
        self.assertIn("No autonomy.", html)
        self.assertIn("No auto exploration.", html)
        self.assertIn("No LLM planning.", html)
        self.assertIn("No action selection change.", html)
        self.assertIn("Instinct / Experience Observation", html)
        self.assertIn("Run random walk sample", html)
        self.assertIn("Run wall influence check", html)
        self.assertIn("Clear experiment observation", html)
        self.assertIn("Current experiment mode", html)
        self.assertIn("No continuous loop.", html)
        self.assertIn("No reward bias.", html)

    def test_state_json_is_read_only_snapshot(self):
        response = self.client.get("/state.json")
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["level_id"], "simulated_vision_larger_sandbox_v0")
        self.assertEqual(data["pos"], [2, 2])
        self.assertEqual(data["facing"], "north")
        self.assertEqual(data["front_symbol"], "e")
        self.assertEqual(data["viewport"][2][1], "a")
        self.assertEqual(data["action_cooldown_seconds"], 0.5)
        self.assertEqual(data["cooldown_remaining_seconds"], 0.0)
        self.assertTrue(data["can_act"])
        self.assertEqual(data["qingyin_observation"]["name"], "Qingyin")
        self.assertEqual(data["qingyin_observation"]["mode"], "manual_observation")
        self.assertEqual(data["experiment_observation"]["mode"], "none")
        self.assertTrue(data["experiment_observation"]["boundary_check"]["bounded_runner_only"])

    def test_post_action_look_redirects_and_logs(self):
        response = self.client.post("/action", data={"action": "look"})
        state = get_ui_state()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(state["pos"], [2, 2])
        self.assertEqual(state["facing"], "north")
        self.assertIn("Step 1: look", state["action_log"][0])
        self.assertIn("Qingyin looked.", state["action_log"][0])
        self.assertIn("Result: observed", state["action_log"][0])

    def test_post_action_turn_right_updates_facing(self):
        response = self.client.post("/action", data={"action": "turn_right"})
        state = get_ui_state()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(state["pos"], [2, 2])
        self.assertEqual(state["facing"], "east")
        self.assertIn("Step 1: turn_right", state["action_log"][0])
        self.assertIn("Qingyin turned right.", state["action_log"][0])

    def test_post_action_move_forward_appends_human_log(self):
        self.client.post("/action", data={"action": "turn_right"})
        self.now += 0.6
        response = self.client.post("/action", data={"action": "move_forward"})
        state = get_ui_state()
        log = "\n\n".join(state["action_log"])

        self.assertEqual(response.status_code, 302)
        self.assertEqual(state["pos"], [3, 2])
        self.assertIn("Step 2: move_forward", log)
        self.assertIn("Qingyin moved forward.", log)
        self.assertIn("Before: [2,2], facing east", log)
        self.assertIn("Front symbol: e", log)
        self.assertIn("Result: moved", log)
        self.assertIn("After: [3,2], facing east", log)

    def test_post_reset_restores_initial_state_and_empty_log(self):
        self.client.post("/action", data={"action": "turn_right"})
        self.now += 0.6
        self.client.post("/action", data={"action": "move_forward"})
        response = self.client.post("/reset")
        state = get_ui_state()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(state["pos"], [2, 2])
        self.assertEqual(state["facing"], "north")
        self.assertEqual(state["action_log"], [])
        self.assertTrue(state["can_act"])
        self.assertIsNone(state["last_action_time"])

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
        self.assertTrue(config["action_cooldown_enabled"])
        self.assertTrue(config["action_cooldown_configurable"])
        self.assertTrue(config["qingyin_observation_bridge_enabled"])
        self.assertTrue(config["manual_observation_only"])
        self.assertTrue(boundary["ui_prototype"])
        self.assertTrue(boundary["local_only"])
        self.assertTrue(boundary["qingyin_observation_bridge_enabled"])
        self.assertTrue(boundary["manual_observation_only"])
        self.assertTrue(boundary["action_cooldown_enabled"])
        self.assertTrue(boundary["action_cooldown_configurable"])
        self.assertFalse(boundary["autonomous_action_loop_enabled"])
        self.assertFalse(boundary["auto_exploration_enabled"])
        self.assertFalse(boundary["decision_loop_enabled"])
        self.assertFalse(boundary["runtime_behavior_modified"])
        self.assertFalse(boundary["pathfinding_used"])
        self.assertFalse(boundary["route_planner_added"])
        self.assertFalse(boundary["item_collection_enabled"])
        self.assertFalse(boundary["exit_activation_enabled"])
        self.assertTrue(boundary["instinct_random_walk_ui_observation_enabled"])
        self.assertTrue(boundary["wall_experience_influence_ui_observation_enabled"])
        self.assertTrue(boundary["bounded_runner_only"])
        self.assertFalse(boundary["continuous_autonomous_loop_enabled"])
        self.assertFalse(boundary["item_reward_bias_enabled"])
        self.assertFalse(boundary["dopamine_like_signal_enabled"])

    def test_run_command_reports_nonblocking_launch_config(self):
        result = run_command("run-larger-sandbox-ui")

        self.assertEqual(result["command"], "run-larger-sandbox-ui")
        self.assertEqual(result["url"], "http://127.0.0.1:7860")
        self.assertTrue(result["local_only"])

    def test_boundary_check_denies_out_of_scope_capabilities(self):
        boundary = build_ui_boundary_check()

        self.assertTrue(boundary["ui_prototype"])
        self.assertTrue(boundary["local_only"])
        self.assertTrue(boundary["qingyin_observation_bridge_enabled"])
        self.assertTrue(boundary["manual_observation_only"])
        self.assertFalse(boundary["action_selection_modified"])
        self.assertFalse(boundary["autonomous_action_loop_enabled"])
        self.assertFalse(boundary["auto_exploration_enabled"])
        self.assertFalse(boundary["decision_loop_enabled"])
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
        self.assertFalse(boundary["consciousness_claimed"])
        self.assertTrue(boundary["instinct_random_walk_ui_observation_enabled"])
        self.assertTrue(boundary["wall_experience_influence_ui_observation_enabled"])
        self.assertTrue(boundary["bounded_runner_only"])
        self.assertFalse(boundary["continuous_autonomous_loop_enabled"])
        self.assertFalse(boundary["item_reward_bias_enabled"])
        self.assertFalse(boundary["dopamine_like_signal_enabled"])
        self.assertFalse(boundary["subjective_experience_claimed"])

    def test_qingyin_state_json_returns_observation_summary(self):
        response = self.client.get("/qingyin_state.json")
        data = response.get_json()
        boundary = data["boundary_check"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["name"], "Qingyin")
        self.assertEqual(data["mode"], "manual_observation")
        self.assertEqual(data["body"], "symbolic_sandbox_body")
        self.assertEqual(data["level_id"], "simulated_vision_larger_sandbox_v0")
        self.assertEqual(data["pos"], [2, 2])
        self.assertEqual(data["facing"], "north")
        self.assertEqual(data["front_symbol"], "e")
        self.assertIn("e", data["visible_symbols"])
        self.assertIn("w", data["visible_symbols"])
        self.assertEqual(data["last_action"], "none")
        self.assertEqual(data["last_result"], "none")
        self.assertTrue(data["can_act"])
        self.assertEqual(data["cooldown_remaining_seconds"], 0.0)
        self.assertTrue(boundary["qingyin_observation_bridge_enabled"])
        self.assertTrue(boundary["manual_observation_only"])
        self.assertFalse(boundary["autonomous_action_loop_enabled"])
        self.assertFalse(boundary["auto_exploration_enabled"])
        self.assertFalse(boundary["decision_loop_enabled"])
        self.assertFalse(boundary["llm_planning_used"])
        self.assertFalse(boundary["pathfinding_used"])
        self.assertFalse(boundary["action_selection_modified"])
        self.assertTrue(boundary["symbolic_sandbox_body"])
        self.assertFalse(boundary["real_robot_body"])
        self.assertFalse(boundary["real_image_vision"])
        self.assertFalse(boundary["long_term_memory_write"])
        self.assertFalse(boundary["consciousness_claimed"])
        self.assertEqual(data["experiment_observation"]["mode"], "none")
        self.assertTrue(boundary["bounded_runner_only"])
        self.assertFalse(boundary["continuous_autonomous_loop_enabled"])
        self.assertFalse(boundary["item_reward_bias_enabled"])
        self.assertFalse(boundary["dopamine_like_signal_enabled"])

    def test_qingyin_observation_updates_after_action(self):
        self.client.post("/action", data={"action": "turn_right"})
        data = self.client.get("/qingyin_state.json").get_json()

        self.assertEqual(data["facing"], "east")
        self.assertEqual(data["last_action"], "turn_right")
        self.assertEqual(data["last_result"], "turned")
        self.assertEqual(data["last_effects"], [])
        self.assertEqual(data["last_failures"], [])

    def test_action_log_uses_observation_wording_without_overclaiming(self):
        self.client.post("/action", data={"action": "look"})
        log = "\n\n".join(get_ui_state()["action_log"]).lower()

        self.assertIn("qingyin looked.", log)
        self.assertNotIn("decided", log)
        self.assertNotIn("understood", log)
        self.assertNotIn("wanted", log)
        self.assertNotIn("chose because", log)

    def test_ui_does_not_modify_runtime_movement_rules(self):
        before = run_simulated_vision_larger_sandbox_demo()
        apply_ui_action("turn_right")
        self.now += 0.6
        apply_ui_action("move_forward")
        after = run_simulated_vision_larger_sandbox_demo()

        self.assertEqual(after["action_trace"], before["action_trace"])
        self.assertEqual(after["boundary_check"], before["boundary_check"])

    def test_post_cooldown_updates_cooldown_and_logs(self):
        response = self.client.post("/cooldown", data={"cooldown_seconds": "1.0"})
        state = get_ui_state()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(state["action_cooldown_seconds"], 1.0)
        self.assertIn("Cooldown updated to 1.0s", state["action_log"][-1])

    def test_post_cooldown_clamps_to_allowed_range(self):
        self.client.post("/cooldown", data={"cooldown_seconds": "-2"})
        self.assertEqual(get_ui_state()["action_cooldown_seconds"], 0.0)

        self.client.post("/cooldown", data={"cooldown_seconds": "9.5"})
        self.assertEqual(get_ui_state()["action_cooldown_seconds"], 5.0)

    def test_cooldown_remaining_helper_is_deterministic(self):
        self.assertEqual(cooldown_remaining_seconds(now=10.0, last_action_time=None, cooldown_seconds=0.5), 0.0)
        self.assertAlmostEqual(cooldown_remaining_seconds(now=10.0, last_action_time=9.8, cooldown_seconds=0.5), 0.3)
        self.assertEqual(cooldown_remaining_seconds(now=10.0, last_action_time=9.0, cooldown_seconds=0.5), 0.0)
        self.assertEqual(cooldown_remaining_seconds(now=10.0, last_action_time=10.0, cooldown_seconds=0.0), 0.0)

    def test_first_action_allowed_and_immediate_second_action_blocked(self):
        self.client.post("/cooldown", data={"cooldown_seconds": "1.0"})
        self.client.post("/action", data={"action": "turn_right"})
        state_after_first = get_ui_state()
        response = self.client.post("/action", data={"action": "move_forward"})
        state_after_second = get_ui_state()
        log = "\n\n".join(state_after_second["action_log"])

        self.assertEqual(response.status_code, 302)
        self.assertEqual(state_after_first["facing"], "east")
        self.assertEqual(state_after_second["pos"], [2, 2])
        self.assertEqual(state_after_second["facing"], "east")
        self.assertFalse(state_after_second["can_act"])
        self.assertIn("Action blocked by cooldown.", log)
        self.assertIn("Remaining: 1.00s", log)

    def test_action_after_cooldown_expiry_is_allowed(self):
        self.client.post("/cooldown", data={"cooldown_seconds": "1.0"})
        self.client.post("/action", data={"action": "turn_right"})
        self.now += 1.1
        self.client.post("/action", data={"action": "move_forward"})
        state = get_ui_state()
        log = "\n\n".join(state["action_log"])

        self.assertEqual(state["pos"], [3, 2])
        self.assertEqual(state["facing"], "east")
        self.assertFalse(state["can_act"])
        self.assertIn("Step 2: move_forward", log)
        self.assertIn("Result: moved", log)

    def test_cooldown_zero_disables_blocking(self):
        self.client.post("/cooldown", data={"cooldown_seconds": "0.0"})
        self.client.post("/action", data={"action": "turn_right"})
        self.client.post("/action", data={"action": "move_forward"})
        state = get_ui_state()
        log = "\n\n".join(state["action_log"])

        self.assertEqual(state["pos"], [3, 2])
        self.assertEqual(state["facing"], "east")
        self.assertTrue(state["can_act"])
        self.assertNotIn("Action blocked by cooldown.", log)

    def test_reset_is_allowed_during_cooldown(self):
        self.client.post("/cooldown", data={"cooldown_seconds": "1.0"})
        self.client.post("/action", data={"action": "turn_right"})
        response = self.client.post("/reset")
        state = get_ui_state()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(state["pos"], [2, 2])
        self.assertEqual(state["facing"], "north")
        self.assertTrue(state["can_act"])
        self.assertEqual(state["action_log"], [])

    def test_experiment_state_json_reports_boundary(self):
        response = self.client.get("/experiment_state.json")
        data = response.get_json()
        boundary = data["boundary_check"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["mode"], "none")
        self.assertTrue(boundary["instinct_random_walk_ui_observation_enabled"])
        self.assertTrue(boundary["wall_experience_influence_ui_observation_enabled"])
        self.assertTrue(boundary["bounded_runner_only"])
        self.assertFalse(boundary["continuous_autonomous_loop_enabled"])
        self.assertFalse(boundary["auto_exploration_enabled"])
        self.assertFalse(boundary["decision_loop_enabled"])
        self.assertFalse(boundary["item_reward_bias_enabled"])
        self.assertFalse(boundary["dopamine_like_signal_enabled"])
        self.assertFalse(boundary["pathfinding_used"])
        self.assertFalse(boundary["route_planner_added"])
        self.assertFalse(boundary["long_term_memory_write"])
        self.assertFalse(boundary["consciousness_claimed"])

    def test_post_random_walk_experiment_shows_summary_without_moving_sandbox(self):
        before = get_ui_state()
        response = self.client.post("/experiment/random-walk", data={"seed": "1", "max_steps": "10"})
        state = get_ui_state()
        html = self.client.get("/").get_data(as_text=True)
        experiment = state["experiment_observation"]

        self.assertEqual(response.status_code, 302)
        self.assertEqual(state["pos"], before["pos"])
        self.assertEqual(state["facing"], before["facing"])
        self.assertEqual(experiment["mode"], "instinct_random_walk")
        self.assertEqual(experiment["seed"], 1)
        self.assertEqual(experiment["max_steps"], 10)
        self.assertEqual(experiment["random_walk"]["step_count"], 10)
        self.assertIn("Step count", html)
        self.assertIn("Wall blocked count", html)
        self.assertIn("Item contact count", html)
        self.assertIn("Experience count", html)
        self.assertIn("Reward bias enabled</dt><dd>false", html)
        self.assertIn("Qingyin ran a bounded random walk sample.", "\n".join(state["action_log"]))

    def test_post_wall_influence_experiment_shows_control_and_influence(self):
        response = self.client.post("/experiment/wall-influence", data={"seed": "1", "max_steps": "50"})
        state = get_ui_state()
        html = self.client.get("/").get_data(as_text=True)
        experiment = state["experiment_observation"]
        wall = experiment["wall_influence"]

        self.assertEqual(response.status_code, 302)
        self.assertEqual(experiment["mode"], "wall_experience_influence")
        self.assertTrue(wall["control_passed"])
        self.assertTrue(wall["influence_passed"])
        self.assertEqual(wall["selected_action_without_experience"], "move_forward")
        self.assertEqual(wall["selected_action_with_wall_experience"], "turn_right")
        self.assertTrue(wall["experience_used_for_decision"])
        self.assertIn("No-experience control", html)
        self.assertIn("With-prior-experience influence", html)
        self.assertIn("Selected action without experience", html)
        self.assertIn("Selected action with wall experience", html)
        self.assertIn("Experience used for decision", html)
        self.assertIn("Item reward bias</dt><dd>false", html)
        self.assertIn("Dopamine_like_signal</dt><dd>false", html)

    def test_clear_experiment_observation_does_not_reset_sandbox_position(self):
        self.client.post("/cooldown", data={"cooldown_seconds": "0.0"})
        self.client.post("/action", data={"action": "turn_right"})
        self.client.post("/action", data={"action": "move_forward"})
        moved = get_ui_state()
        self.client.post("/experiment/random-walk", data={"seed": "1", "max_steps": "5"})
        response = self.client.post("/experiment/clear")
        state = get_ui_state()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(state["pos"], moved["pos"])
        self.assertEqual(state["facing"], moved["facing"])
        self.assertEqual(state["experiment_observation"]["mode"], "none")
        self.assertIn("Experiment observation cleared.", state["action_log"][-1])

    def test_experiment_observation_has_no_continuous_loop_side_effect(self):
        self.client.post("/experiment/random-walk", data={"seed": "1", "max_steps": "10"})
        first = self.client.get("/experiment_state.json").get_json()
        second = self.client.get("/experiment_state.json").get_json()

        self.assertEqual(first, second)
        self.assertTrue(first["boundary_check"]["bounded_runner_only"])
        self.assertFalse(first["boundary_check"]["continuous_autonomous_loop_enabled"])
        self.assertFalse(first["boundary_check"]["auto_exploration_enabled"])


if __name__ == "__main__":
    unittest.main()
