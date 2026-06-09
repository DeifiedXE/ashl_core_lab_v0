Boundary Index Version: 2026-06-09-b39
Last update log: Mimetic Endocrine Line Milestone + Boundary Sync
Previous Boundary Index Version: 2026-06-09-b38
Previous Last update log: Generalized Memory Line Milestone + Boundary Sync
Clean count at last update log reset: 0/5
Current clean count: 0/5

## Global Hard Boundaries
- Trace/persistence records are evidence only, not authorization, lesson_store write, Memory Layer write, lesson_candidate creation, or awakening evidence.
- trace is record, not runtime action.
- no lesson_store write unless explicitly authorized by a future dedicated package.
- no Memory Layer write unless explicitly authorized by a future dedicated package.
- no Long-term Memory write unless explicitly authorized.
- LLM output must not become authoritative failure_reason. LLM output must not become Qingyin runtime, self, memory, state, perception, or learning loop.
- first_output must be generated without LLM output. first_output is a runtime milestone, not awakening, dialogue ability, or long-term growth evidence.
- mentor_feedback_stub and mentor_feedback_trace are engineering supervision records, not feedback runtime.
- Minimal First Output Runtime v0 is not awakening and must not connect to mentor feedback runtime or lesson_candidate pipeline.
- Minimal Interaction CLI Bridge v0 is an entrypoint, not dialogue.
- append-only persistence is not lesson_store write, Memory Layer write, lesson_candidate creation, or awakening evidence.
- utterance_map is fixed non-LLM lookup table. state_key unknown maps to ????隞?. state_key unknown maps to fixed unknown utterances and does not prove language understanding.
- micro push-box tactile sandbox is bounded test-object sandbox. allowed_action_set is closed. natural language actions are not allowed in micro push-box sandbox.
- tactile_sandbox_trace is evidence of sandbox interaction, not learning by itself; tactile result to state_key mapping is fixed lookup table.
- tactile interaction CLI bridge is deterministic, not autonomous action selection. tactile interaction does not prove Qingyin understands box, wall, or goal.
- repeated blocked action history is trace readback, not full learning.
- repeated blocked action avoidance is action candidate bias, not solver. outcome weighting is action candidate bias, not solver or full reinforcement learning.
- grounded learning verification CLI is human-verifiable trace flow, not teaching chat.
- clear-sandbox-working-state must preserve append-only traces; sandbox working state clear is not memory deletion.
- suggested_next_action is candidate suggestion, not autonomous planning.
- intrinsic action selection is bounded candidate selection, not solver. intrinsic action selection must only select from candidate_actions.
- bounded randomness must only act within candidate_actions.
- box_on_goal need_state is target-state tracking, not emotion / dopamine. need_state current_value 0/1 does not prove desire or understanding.
- need_state must not write lesson_store or Memory Layer.
- need-state driven trial runner is not a solver or full learning pipeline. need-state trial batch step count is measurement, not proof of learning.
- goal direction bias is distance-based candidate bias, not pathfinding. goal direction bias must not mutate sandbox state. goal direction bias must not create actions outside candidate_actions.
- box_on_goal need_state plus goal direction bias does not prove goal understanding.
- state-action outcome memory is local session memory, not Long-term Memory. state-action outcome memory must not write lesson_store or Memory Layer.
- state-action memory must not be reused across different agent_pos / box_pos / goal_pos contexts.
- trial metrics comparison is measurement only, not behavior modification. trial metrics comparison does not prove learning by itself.
- human_summary is report text, not Qingyin utterance or dialogue.
- micro navigation goal-reach is a navigation curriculum level, not proof of map understanding.
- micro navigation multi-goal level means following sequential goal markers, not autonomous planning.
- multi-goal navigation trace is evidence of sequential target following, not pathfinding.
- stuck detection / repetition penalty currently has negative observed effect and must not be treated as proven improvement.
- approach-box level is object-approach verification, not push behavior. approach-box level must not modify push-box sandbox.
- approach-box completion means agent is adjacent to box, not that it understands box.
- Two-Trial History Boundary allows only local state-action outcome memory.
- Trial 2 must not read full trace, full route, selected_actions replay, lesson_candidate, lesson_store, Memory Layer, Long-term Memory, LLM planning, or human hint.
- Trial 2 can read local context only: agent_pos / box_pos / optional goal_pos / action / result / tick.
- trial metrics baseline snapshot is comparison-only, not proof of learning, lesson_store write, or Memory Layer write.
- approach-box trial CLI is a wrapper around the existing approach-box runner and must not change runner behavior.
- approach-box trial CLI must not add box pushing, pathfinding, or learning proof.
- approach-box two-trial check is local memory verification only, not proof of learning, and must not replay route or selected_actions into Trial 2.
- baseline comparison is readback only and must not change trial runner, action selection, goal bias, state-action memory, penalty / stuck detection, or behavior.
- push-box full solve remains deferred; push-box is an experimental microscope, not the project goal.
- sandbox result is not a lesson; sandbox trace is not memory promotion.
- formal lesson_candidate creation is not lesson approval, activation, or selection eligibility.
- ASHL Core provides evidence; Qingyin Memory Layers decide memory admission.
- semantic_key is non-authoritative and review-required.
- builder output must be review-gated.
- memory freeze notice is evidence, not Memory Layer write.
- no expected_outcome / actual_outcome contrast, no authoritative failure_reason.
- expected / actual both unknown-like is system_fault, not match.
- missing required fields must be rejected, not default-filled.
- bounded senses must be connected before Qingyin can be claimed awake.
- Qingyin is currently in the test-object stage, not an awakened individual.
- The test-object stage is the prerequisite for growth, not growth itself.
- Qingyin's importance is not in birth, but in growth.
- Experience Abstraction Layer v0: temporary apply verification must not modify global predictors/action selection/persistent stores; human reviewer required; Qingyin self-approval blocked; approved means reviewed, not persistent application.
- UI expansion is paused until eye-structure simulation, generalized memory loop, and mimetic endocrine system are more developed.
- No proof of general learning.
- No autonomous learning claim.
- No visual understanding claim.
- No solved symbol grounding claim.
- No consciousness / subjective understanding claim.
- No subjective emotion proof.
- Future subjective possibility is not denied.
- No pathfinding / BFS / A* unless explicitly scoped.
- No LLM reasoning / planning / vision unless explicitly scoped.
- No long-term memory write unless explicitly scoped.
- No lesson_store / Memory Layer write unless explicitly scoped.
- No global predictor modification.
- No action selection modification.
- Qingyin self-approval remains blocked.
- Persistent Candidate Preview / Dry-run is not part of current work.
- Generalized memory v0 uses exact similar_context_key only.
- Fuzzy similarity is out of v0 scope.
- Mimetic endocrine v0 is trace-only.
- Signal interaction runtime is out of current scope.
- Endocrine runtime is out of current scope.

## Current Dead-End Memory Milestones (compressed)
- Legacy anchors: Boundary Index Version: 2026-06-06-b30; Last update log: Batch 30.
- Prior completed items: Approach Box Trial CLI / Approach Box Two-Trial Learning Check / Trial Metrics Baseline Snapshot.
- Approach Box Dead-End Level v0: approach_box_dead_end_v0; Trial 1 entered dead end, visited [[4, 1], [4, 2]], blocked at [4, 3], step_count=11, llm_used=false.
- Dead-end two-trial check: Trial 1 step_count=11 and entered dead end; Trial 2 step_count=5 and avoided Trial 1 dead-end action; delta=-6 steps, dead_end_positions_visited_delta=-2, blocked_or_failed_delta=-1.
- Dead-End Memory Control Check v0: with_memory Trial 2 avoid_rate=1.0, entered_dead_end_count=0, average_step_count=5.0; without_memory avoid_rate=0.0, entered_dead_end_count=20, average_step_count=11.0; memory_effect_observed=true.
- Trial1 source audit confirms all with_memory and without_memory Trial 1 runs generated local dead-end memory source; only with_memory Trial 2 read it.
- Dead-End Map Trial1 Validation v0 classified valid maps and shortcut maps; Candidate Map Trial1 ASCII Replay v0 is observer-only and does not run A/B memory control.

## Valid Dead-End Maps A/B Control v0
- CLI: py -3 -m ashl_core.teaching_cli run-valid-dead-end-maps-ab-control --runs-per-map 3 --max-steps 100; included maps: approach_box_dead_end_v0 / mid_branch_dead_end_candidate_v0 / lower_branch_dead_end_candidate_v0; excluded user_maze_dead_end_candidate_v0 for has_shortcut_no_dead_end_event.
- A/B result: maps_with_memory_effect_observed=3; maps_without_memory_effect_observed=0; maps_with_mixed_result=0; overall_interpretation=Bounded local memory effect observed across all 3 valid maps; per-map deltas: approach_box -6 steps, mid/lower_branch -3 steps.

## Simulated Vision Grounding Milestone
- Completed symbolic first-person vision loop: first-person see -> interact -> outcome -> experience -> see exact same front_symbol again -> consult experience -> influence immediate action.
- Viewport convention: a=viewport[2][1], immediate front=viewport[1][1], far front=viewport[0][1]; simulated vision sandbox remains a test room, not a home sandbox.
- v0 similar symbol rule: exact same front_symbol only (w->w, e->e, i->i), not fuzzy similarity, wall-like objects, semantic categories, or learned visual similarity.
- Verified: symbol grounding 3/3, experience influence 3/3 plus no-experience wall control, py -3 -m unittest discover Ran 1047 tests OK.
- Non-claims: no real image vision, no LLM vision/planning, no full-map vision, no pathfinding/route planning, no long-term memory, no visual understanding claim, no solved symbol grounding claim, no general learning proof, no consciousness or subjective understanding claim.
- Log: docs/milestone_logs/simulated_vision_grounding_milestone_2026-06-09.md.

## Experience And Memory Milestones
- Experience Abstraction Layer (2026-06-09): controlled experience records can pass through deterministic reason classification, similar_context_key, prediction, mismatch, review-required candidate, human-gated review, approved preview, and temporary in-memory apply verification. No global predictor modification, action selection modification, persistent rule application, long-term memory, lesson_store / Memory Layer write, LLM reasoning/planning/vision. Log: docs/milestone_logs/experience_abstraction_layer_milestone_2026-06-09.md.
- Integrated Experience Session Trace (2026-06-09): scripted perception/action/outcome/experience/reason/similar_context_key/prediction/mismatch/candidate/review-gate trace; 6 steps, 4 prediction matches, 2 mismatches, 2 pending_review, 0 approved, 0 applied. Expected break: unknown_prediction at tick 6. Log: docs/milestone_logs/integrated_experience_session_trace_milestone_2026-06-09.md
- Persistent Eligibility Checker (2026-06-09): checker-only gate for approved candidates entering persistent_candidate review; 10 cases, 1 eligible_for_persistent_candidate_review, 9 blocked, 0 eligible_for_persistent_rule, 0 persistent_rule_write_allowed. No persistent preview/dry-run/write/storage/table/activation, predictor/action selection modification, long-term memory, lesson_store/Memory Layer writes. Log: docs/milestone_logs/persistent_eligibility_checker_milestone_2026-06-09.md
- Generalized Memory Line Milestone (2026-06-09): completed exact-key generalized memory check line through approved preview; 4 buckets, 2 high-confidence stable patterns, 2 generalized candidates, 2 approved previews; 0 applied, 0 predictor_modified, 0 action_selection_influence, 0 memory_write, 0 persistent_candidate. Exact key only; no fuzzy/semantic/LLM/visual similarity or persistent write. Log: docs/milestone_logs/generalized_memory_line_milestone_2026-06-09.md
- Mimetic Endocrine Line Milestone (2026-06-09): completed design/schema/trace/integration for four functional axes: dopamine_like approach_reward, norepinephrine_like attention_salience, cortisol_like pressure_load, oxytocin_like source_trust. Results: four-axis trace integration has 4 axes, 11 valid traces, 0 action_selection_influence, 0 memory_write, 0 candidate_approval_influence, 0 predictor_modified, 0 runtime_formula, 0 signal_interaction_runtime, 0 endocrine_runtime. Boundary: trace only; no formulas, no signal interactions, no endocrine runtime/state runtime, no reward bias modification, no autonomous attention, no protective mechanism, no trust-based approval, no action selection change, no memory writes, no subjective emotion/consciousness proof; future subjective possibility not denied. Log: docs/milestone_logs/mimetic_endocrine_line_milestone_2026-06-09.md

## Current Claim Boundary
- Can claim: Bounded local memory effect observed across 3 validated dead-end maps.
- Can claim: In approach_box_dead_end_v0, local state-action outcome memory has a bounded, repeatable, controlled effect on Trial 2 behavior.
- Can claim: ASHL Core can convert controlled experience records through deterministic reason classification, position-independent keys, prediction, mismatch, review-required candidates, human-gated review, approved preview, and temporary in-memory apply verification.
- Can claim: ASHL Core can run a scripted integrated trace connecting symbolic perception/action/outcome/experience/reason/similar_context_key/prediction/mismatch/candidate/review gate pending state while keeping approval and application disabled.
- Can claim: ASHL Core can run a safe exact-key generalized memory check line through approved preview while keeping application, predictor mutation, action selection influence, persistent promotion, and memory writes disabled.
- Can claim: ASHL Core can define and validate four mimetic endocrine signal axes, map controlled reward/change/failure/trust events into schema-valid trace records, and integrate those traces into a four-axis endocrine trace summary while keeping formulas, signal interactions, endocrine runtime control, action selection influence, predictor mutation, candidate approval influence, memory writes, and subjective emotion claims disabled.
- Cannot claim: proof of general learning / map understanding / maze solving / pathfinding / Long-term Memory / lesson-store learning / fuzzy generalization / arbitrary-level generalization / biological hormone simulation / subjective emotion / consciousness or subjective understanding.

## Currently Deferred Areas
- Open language interfaces deferred: LLM response generation / teaching chat loop / free text conversation.
- Learning pipeline writes deferred: lesson_candidate pipeline / lesson_store write / Memory Layer write. persistent state-action memory deferred.
- External senses deferred: Screen Sense / Camera Sense / Symbol Grounding / Audio Sense / STT / TTS.
- Sandbox runtimes deferred: sandbox runtime / trace replay / tactile trace persistence / bounded senses runtime / state store.
- Autonomous behavior and candidate-selection runtimes deferred: autonomous action selection / autonomous goal planning / intrinsic action selection runtime / need-state driven action loop / action outcome weighting runtime integration / stable navigation curriculum metrics.
- Learning improvement and metrics behavior change deferred: automatic trial improvement / long-term learning / tactile learning / repeated failure adaptation / full learning pipeline / stable metrics comparison across fixed seeds / automatic behavior modification from metrics.
- Review, activation, formal builders, identity, and consolidation runtimes deferred: evaluator runtime / review decision runtime / selection eligibility runtime / activation runtime / lesson_candidate builders / Qingyin runtime / first_output trace schema runtime / mentor feedback runtime / Core Seed update runtime / self-modification runtime / soft-hard consolidation runtime.
- Navigation curriculum deferred: Snapshot Compare follow-ups / Push Once Level / push-box full solve / stable navigation curriculum metrics.
- Mimetic endocrine deferred: formulas / signal interactions / cortisol dampens dopamine / norepinephrine attention narrowing / endocrine state runtime / endocrine runtime / reward bias changes / autonomous attention / protective triggers / trust-based approval.
- Push-box full solve remains deferred.

## Update Rule
- This file must be updated every time an Update Log is generated.
- Boundary Index sync may also be milestone-triggered.
