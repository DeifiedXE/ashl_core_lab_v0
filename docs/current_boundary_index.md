Boundary Index Version: 2026-06-08-b32
Last update log: Batch 32
Previous Boundary Index Version: 2026-06-08-b31
Previous Last update log: Batch 31
Previous Previous Boundary Index Version: 2026-06-06-b30
Previous Previous Last update log: Batch 30
Clean count at last update log reset: 0/5
Current clean count: 0/5

## Global Hard Boundaries
- Trace/persistence records are evidence only, not authorization, lesson_store write, Memory Layer write, lesson_candidate creation, or awakening evidence.
- trace is record, not runtime action.
- no lesson_store write unless explicitly authorized by a future dedicated package.
- no Memory Layer write unless explicitly authorized by a future dedicated package.
- no Long-term Memory write unless explicitly authorized.
- LLM output must not become authoritative failure_reason.
- LLM output must not become Qingyin runtime, self, memory, state, perception, or learning loop.
- first_output must be generated without LLM output.
- first_output is a runtime milestone, not awakening, dialogue ability, or evidence of long-term growth.
- first_output_trace requires mentor feedback before it may be considered for lesson_candidate input.
- first_output_trace must not write to lesson_store or Memory Layer.
- mentor_feedback_stub and mentor_feedback_trace are engineering supervision records, not feedback runtime. They are not awakening proof, lesson_candidate creation, lesson_store write, or Memory Layer write.
- Minimal Mentor Feedback Stub Runtime v0 must not create failure_event, review decision, selection eligibility, activation, or lesson_candidate pipeline connection.
- Minimal First Output Runtime v0 is not awakening and must not connect to mentor feedback runtime or lesson_candidate pipeline.
- Minimal Interaction CLI Bridge v0 is an entrypoint, not dialogue. It must not write lesson_store or Memory Layer or connect to lesson_candidate pipeline.
- private mentor_feedback_note must not be required by smoke tests.
- append-only persistence is not lesson_store write, Memory Layer write, lesson_candidate creation, or awakening evidence.
- JSONL persistence target files are data/first_output_traces.jsonl and data/mentor_feedback_traces.jsonl.
- utterance_map is fixed non-LLM lookup table.
- state_key unknown maps to ????隞?.
- utterance_map output must preserve correct literal text encoding and does not prove language understanding.
- micro push-box tactile sandbox is bounded test-object sandbox.
- allowed_action_set is closed.
- natural language actions are not allowed in micro push-box sandbox.
- tactile_sandbox_trace is evidence of sandbox interaction, not learning by itself.
- tactile result to state_key mapping is fixed lookup table.
- tactile interaction CLI bridge is deterministic, not autonomous action selection. It must not connect to lesson_candidate pipeline or write lesson_store / Memory Layer.
- tactile interaction does not prove Qingyin understands box, wall, or goal.
- repeated blocked action history is trace readback, not full learning.
- repeated blocked action avoidance is action candidate bias, not solver.
- outcome weighting is action candidate bias, not solver or full reinforcement learning.
- grounded learning verification CLI is human-verifiable trace flow, not teaching chat.
- clear-sandbox-working-state must preserve append-only traces.
- sandbox working state clear is not memory deletion.
- suggested_next_action is candidate suggestion, not autonomous planning.
- intrinsic action selection is bounded candidate selection, not solver. intrinsic action selection must only select from candidate_actions.
- bounded randomness must only act within candidate_actions.
- box_on_goal need_state is target-state tracking, not emotion / dopamine.
- need_state current_value 0/1 does not prove desire or understanding.
- need_state must not write lesson_store or Memory Layer. need_state does not choose actions.
- need-state driven trial runner is not a solver or full learning pipeline.
- need-state trial batch step count is measurement, not proof of learning.
- goal direction bias is distance-based candidate bias, not pathfinding. goal direction bias must not mutate sandbox state. goal direction bias must not create actions outside candidate_actions.
- box_on_goal need_state plus goal direction bias does not prove goal understanding.
- state-action outcome memory is local session memory, not Long-term Memory.
- state-action outcome memory must not write lesson_store or Memory Layer.
- state-action memory must not be reused across different agent_pos / box_pos / goal_pos contexts.
- trial metrics comparison is measurement only, not behavior modification. trial metrics comparison does not prove learning by itself.
- human_summary is report text, not Qingyin utterance or dialogue.
- micro navigation goal-reach is a navigation curriculum level, not proof of map understanding.
- micro navigation multi-goal level means following sequential goal markers, not autonomous planning.
- multi-goal navigation trace is evidence of sequential target following, not pathfinding.
- stuck detection / repetition penalty currently has negative observed effect and must not be treated as proven improvement.
- approach-box level is object-approach verification, not push behavior.
- approach-box level must not modify push-box sandbox.
- approach-box completion means agent is adjacent to box, not that it understands box.
- Two-Trial History Boundary allows only local state-action outcome memory.
- Trial 2 must not read full trace, full route, selected_actions replay, lesson_candidate, lesson_store, Memory Layer, Long-term Memory, LLM planning, or human hint.
- Trial 2 can read local context only: agent_pos / box_pos / optional goal_pos / action / result / tick.
- trial metrics baseline snapshot is comparison-only, not proof of learning, lesson_store write, or Memory Layer write.
- committed trial metrics baseline uses runs=4, trial_count=5, max_steps=10, random_seed=17.
- baseline metrics are total_trials=20, total_completed=13, overall_success_rate=0.65, overall_average_step_count=6.6, max_steps_reached_count=7.
- approach-box trial CLI is a wrapper around the existing approach-box runner and must not change runner behavior.
- approach-box trial CLI must not add box pushing, pathfinding, or learning proof.
- approach-box two-trial check is local memory verification only, not proof of learning.
- approach-box two-trial check must not replay route or selected_actions into Trial 2.
- baseline comparison is readback only and must not change trial runner, action selection, goal bias, state-action memory, penalty / stuck detection, or behavior.
- baseline comparison outputs baseline/current/delta metrics and must keep comparison_only=true and proof_of_learning=false.
- push-box full solve remains deferred; push-box is an experimental microscope, not the project goal.
- sandbox result is not a lesson.
- sandbox trace is not memory promotion.
- sandbox repair suggestion is not executable action.
- formal lesson_candidate creation is not lesson approval, activation, or selection eligibility.
- ASHL Core provides evidence; Qingyin Memory Layers decide memory admission.
- semantic_key is non-authoritative and review-required.
- builder output must be review-gated.
- memory freeze notice is evidence, not Memory Layer write.
- memory freeze notice must not directly modify learned_principle.
- no expected_outcome / actual_outcome contrast, no authoritative failure_reason.
- expected / actual both unknown-like is system_fault, not match.
- missing required fields must be rejected, not default-filled.
- bounded senses must be connected before Qingyin can be claimed awake.
- Qingyin is currently in the test-object stage, not an awakened individual.
- The test-object stage is the prerequisite for growth, not growth itself.
- Qingyin's importance is not in birth, but in growth.

## Batch 32 Sync Items
- Current Boundary Index Batch 31 Sync Patch completed.
- Approach Box Dead-End Level v0 established CLI: py -3 -m ashl_core.teaching_cli run-approach-box-dead-end-trial --max-steps 100.
- Dead-end level_id is approach_box_dead_end_v0.
- Dead-end approach_positions are [[3, 4]].
- Dead-end trial entered_dead_end_area=true, dead_end_positions_visited=[[4, 1], [4, 2]], blocked_or_failed_actions=blocked at [4, 3], step_count=11, llm_used=false.
- Dead-end verification fields are established, not proof of learning.
- Approach Box Dead-End Two-Trial Learning Check v0 CLI: py -3 -m ashl_core.teaching_cli run-approach-box-dead-end-two-trial-check --max-steps 100.
- Dead-end two-trial Trial 1 uses approach_box_dead_end_v0.
- Dead-end two-trial Trial 2 reads Trial 1 local outcome memory.
- Dead-end two-trial output includes trial_1 / trial_2 / comparison / boundary_check.
- Dead-end two-trial result: trial1_step_count=11, trial2_step_count=5, step_count_delta=-6.
- Dead-end two-trial result: trial1_entered_dead_end_area=true, trial2_entered_dead_end_area=false.
- Dead-end two-trial result: dead_end_positions_visited_delta=-2, blocked_or_failed_delta=-1, avoided_trial1_dead_end_action=true.
- Dead-end two-trial boundary: trial2_replayed_full_route=false, trial2_used_llm=false, trial2_used_pathfinding=false, trial2_used_lesson_store=false, trial2_used_memory_layer=false.
- Single with-memory two-trial improvement was observed, but alone was not enough to prove memory-specific effect.
- Dead-End Memory Control Check v0 CLI: py -3 -m ashl_core.teaching_cli run-approach-box-dead-end-memory-control-check --max-steps 100 --runs 20.
- Memory control A/B comparison is with_memory vs without_memory.
- with_memory Trial 2: entered_dead_end_count=0, blocked_or_failed_total=0, average_step_count=5.0, completed_count=20.
- without_memory Trial 2: entered_dead_end_count=20, blocked_or_failed_total=20, average_step_count=11.0, completed_count=20.
- Memory control comparison: entered_dead_end_count_delta=-20, blocked_or_failed_total_delta=-20, average_step_count_delta=-6.0, memory_effect_observed=true, control_group_used=true.
- A/B control supports a bounded local memory effect, not proof of general learning.
- Dead-End Memory Control Trial1 Source Audit v0 patched the memory-control CLI output.
- Trial1 source audit added trial1_source_audit and conditioned_on_trial1_dead_end.
- Trial1 source audit with_memory: trial1_entered_dead_end_count=20, trial1_blocked_or_failed_total=20, trial1_local_memory_written_count=20, trial1_average_step_count=11.0.
- Trial1 source audit without_memory: trial1_entered_dead_end_count=20, trial1_blocked_or_failed_total=20, trial1_local_memory_written_count=20, trial1_average_step_count=11.0.
- Conditioned result: with_memory_sample_count=20, with_memory_trial2_avoided_count=20, with_memory_trial2_avoid_rate=1.0.
- Conditioned result: without_memory_sample_count=20, without_memory_trial2_avoided_count=0, without_memory_trial2_avoid_rate=0.0.
- Conditioned result: conditioned_memory_effect_observed=true.
- Trial 1 memory source is auditable.
- All 20 with_memory Trial 1 runs generated dead-end local memory.
- All 20 without_memory Trial 1 runs also generated dead-end local memory, but Trial 2 did not read it.
- Conditioned control confirms memory-specific behavior difference in this bounded fixture.
- Completed since Batch 31: Approach Box Trial CLI / Approach Box Two-Trial Learning Check / Trial Metrics Baseline Snapshot / Approach Box Dead-End Level v0 / Approach Box Dead-End Two-Trial Learning Check v0 / Dead-End Memory Control Check v0 / Dead-End Memory Control Trial1 Source Audit v0.

## Batch 32 Claim Boundary
- Can claim: In approach_box_dead_end_v0, local state-action outcome memory has a bounded, repeatable, controlled effect on Trial 2 behavior.
- Cannot claim: proof of general learning / map understanding / maze solving / pathfinding / Long-term Memory / lesson-store learning / generalization across arbitrary levels / consciousness or subjective understanding.

## Currently Deferred Areas
- Open language interfaces deferred: LLM response generation / teaching chat loop / free text conversation.
- Learning pipeline writes deferred: lesson_candidate pipeline / lesson_store write / Memory Layer write. persistent state-action memory and Long-term Memory write remain deferred.
- External senses deferred: Screen Sense / Camera Sense / Symbol Grounding / Audio Sense / STT / TTS. Sandbox runtimes deferred: sandbox runtime / trace replay / tactile trace persistence / bounded senses runtime / state store.
- Autonomous behavior and candidate-selection runtimes deferred: autonomous action selection / autonomous goal planning / intrinsic action selection runtime / need-state driven action loop / action outcome weighting runtime integration / stable navigation curriculum metrics.
- Learning improvement and metrics behavior change deferred: automatic trial improvement / long-term learning / tactile learning / repeated failure adaptation / full learning pipeline / stable metrics comparison across fixed seeds / automatic behavior modification from metrics.
- Review, activation, formal builders, identity, and consolidation runtimes deferred: evaluator runtime / review decision runtime / selection eligibility runtime / activation runtime / lesson_candidate builders / Qingyin runtime / first_output trace schema runtime / mentor feedback runtime / Core Seed update runtime / self-modification runtime / soft-hard consolidation runtime.
- Navigation curriculum deferred: Snapshot Compare follow-ups / Push Once Level / push-box full solve / stable navigation curriculum metrics.
- Push-box full solve remains deferred.

## Update Rule
- This file must be updated every time an Update Log is generated. No Update Log package is complete without this corresponding update.
