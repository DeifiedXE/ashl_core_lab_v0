# Boundary Index Archive 2026-06

## Purpose

This archive preserves older Boundary Index milestones moved out of `docs/current_boundary_index.md` to keep the current index compact.

This file is archive-only.
It does not introduce runtime behavior.
It does not change safe claims or forbidden claims.
It does not change claim meaning.

## Archived Milestones

### Legacy / Dead-End Memory Milestones

- Legacy anchors: Boundary Index Version: 2026-06-06-b30; Last update log: Batch 30.
- Prior completed items: Approach Box Trial CLI / Approach Box Two-Trial Learning Check / Trial Metrics Baseline Snapshot.
- Approach Box Dead-End Level v0: `approach_box_dead_end_v0`; Trial 1 entered dead end, visited `[[4, 1], [4, 2]]`, blocked at `[4, 3]`, `step_count=11`, `llm_used=false`.
- Dead-end two-trial check: Trial 1 `step_count=11` and entered dead end; Trial 2 `step_count=5` and avoided Trial 1 dead-end action; `delta=-6 steps`, `dead_end_positions_visited_delta=-2`, `blocked_or_failed_delta=-1`.
- Dead-End Memory Control Check v0: with_memory Trial 2 `avoid_rate=1.0`, `entered_dead_end_count=0`, `average_step_count=5.0`; without_memory `avoid_rate=0.0`, `entered_dead_end_count=20`, `average_step_count=11.0`; `memory_effect_observed=true`.
- Trial1 source audit confirms all with_memory and without_memory Trial 1 runs generated local dead-end memory source; only with_memory Trial 2 read it.
- Dead-End Map Trial1 Validation v0 classified valid maps and shortcut maps; Candidate Map Trial1 ASCII Replay v0 is observer-only and does not run A/B memory control.

### Valid Dead-End Maps A/B Control v0

- CLI: `py -3 -m ashl_core.teaching_cli run-valid-dead-end-maps-ab-control --runs-per-map 3 --max-steps 100`.
- Included maps: `approach_box_dead_end_v0` / `mid_branch_dead_end_candidate_v0` / `lower_branch_dead_end_candidate_v0`.
- Excluded `user_maze_dead_end_candidate_v0` for `has_shortcut_no_dead_end_event`.
- A/B result: `maps_with_memory_effect_observed=3`; `maps_without_memory_effect_observed=0`; `maps_with_mixed_result=0`.
- Overall interpretation: bounded local memory effect observed across all 3 valid maps; per-map deltas: approach_box `-6` steps, mid/lower_branch `-3` steps.

### Simulated Vision Grounding Milestone

- Completed symbolic first-person vision loop: first-person see -> interact -> outcome -> experience -> see exact same `front_symbol` again -> consult experience -> influence immediate action.
- Viewport convention: `a=viewport[2][1]`, immediate front=`viewport[1][1]`, far front=`viewport[0][1]`; simulated vision sandbox remains a test room, not a home sandbox.
- v0 similar symbol rule: exact same `front_symbol` only (`w->w`, `e->e`, `i->i`), not fuzzy similarity, wall-like objects, semantic categories, or learned visual similarity.
- Verified: symbol grounding 3/3, experience influence 3/3 plus no-experience wall control, `py -3 -m unittest discover` Ran 1047 tests OK.
- Non-claims: no real image vision, no LLM vision/planning, no full-map vision, no pathfinding/route planning, no long-term memory, no visual understanding claim, no solved symbol grounding claim, no general learning proof, no consciousness or subjective understanding claim.
- Log: `docs/milestone_logs/simulated_vision_grounding_milestone_2026-06-09.md`.

### Experience And Memory Milestones

- Experience Abstraction Layer (2026-06-09): controlled experience records can pass through deterministic reason classification, `similar_context_key`, prediction, mismatch, review-required candidate, human-gated review, approved preview, and temporary in-memory apply verification. No global predictor modification, action selection modification, persistent rule application, long-term memory, lesson_store / Memory Layer write, LLM reasoning/planning/vision. Log: `docs/milestone_logs/experience_abstraction_layer_milestone_2026-06-09.md`.
- Integrated Experience Session Trace (2026-06-09): scripted perception/action/outcome/experience/reason/`similar_context_key`/prediction/mismatch/candidate/review gate pending state; 6 steps, 4 prediction matches, 2 mismatches, 2 pending_review, 0 approved, 0 applied. Expected break: `unknown_prediction` at tick 6. Log: `docs/milestone_logs/integrated_experience_session_trace_milestone_2026-06-09.md`.
- Persistent Eligibility Checker (2026-06-09): checker-only gate for approved candidates entering persistent_candidate review; 10 cases, 1 eligible_for_persistent_candidate_review, 9 blocked, 0 eligible_for_persistent_rule, 0 persistent_rule_write_allowed. No persistent preview/dry-run/write/storage/table/activation, predictor/action selection modification, long-term memory, lesson_store/Memory Layer writes. Log: `docs/milestone_logs/persistent_eligibility_checker_milestone_2026-06-09.md`.
- Generalized Memory Line Milestone (2026-06-09): completed exact-key generalized memory check line through approved preview; 4 buckets, 2 high-confidence stable patterns, 2 generalized candidates, 2 approved previews; 0 applied, 0 predictor_modified, 0 action_selection_influence, 0 memory_write, 0 persistent_candidate. Exact key only; no fuzzy/semantic/LLM/visual similarity or persistent write. Log: `docs/milestone_logs/generalized_memory_line_milestone_2026-06-09.md`.
- Mimetic Endocrine Line Milestone (2026-06-09): completed design/schema/trace/integration for four functional axes: dopamine_like approach_reward, norepinephrine_like attention_salience, cortisol_like pressure_load, oxytocin_like source_trust. Results: four-axis trace integration has 4 axes, 11 valid traces, 0 action_selection_influence, 0 memory_write, 0 candidate_approval_influence, 0 predictor_modified, 0 runtime_formula, 0 signal_interaction_runtime, 0 endocrine_runtime. Boundary: trace only; no formulas, no signal interactions, no endocrine runtime/state runtime, no reward bias modification, no autonomous attention, no protective mechanism, no trust-based approval, no action selection change, no memory writes, no subjective emotion/consciousness proof; future subjective possibility not denied. Log: `docs/milestone_logs/mimetic_endocrine_line_milestone_2026-06-09.md`.
- Eye-Structure Simulation Line Milestone (2026-06-09): completed Retina Decoder -> Feature Schema -> Symbolic Decode -> Visual Frame Schema/Assembly -> Frame Pair -> Change Schema/Trace. Status: low-level trace/checker only; no runtime frame storage, continuous change detection, focus selector, action selection influence, memory write, predictor mutation, object recognition, object tracking, semantic vision, or subjective visual proof.
- Focus Selector Trace/Checker Milestone (2026-06-09): completed Focus Selector Design -> Focus Candidate Schema -> Candidate From Change Trace -> Ranking Trace Design/Schema/Check. Status: trace/checker only; no runtime focus selector/ranking, active_focus, focus_applied, attention_control, endocrine runtime, action selection influence, memory write, predictor mutation, object/tracking/semantic vision, or subjective proof.
- Phase 0 Action-Lesson Review Line Milestone (2026-06-09): Outcome Pair -> Failure Reason -> Lesson Candidate -> Review Gate -> Evidence Summary -> Human Review Decision -> Reviewed Lesson Trace Preview completed; trace/checker/review/preview only; no lesson application, action selection influence, behavior change, memory write, predictor mutation, persistent learning/rule write, history runtime, or proof of learning claim.
- Phase 0 Lesson Dry-Run / Evidence / Experience milestone (2026-06-10): reviewed_lesson_trace_preview -> dry_run_correction_minimal -> corrected_trial_trace_preview -> before_after_trial_contrast -> lesson_effect_evidence_trace -> exact_key_bucket_candidate -> session_experience_record completed. Status: trace-only / not_retained. Safe claim: visible trace-level difference can be packaged as evidence and a not_retained session experience record. Forbidden: no lesson application, action selection influence, behavior change, memory write, lesson retention, history runtime, persistent learning, predictor mutation, or proof-of-learning claim.
- Trial/Bucket Link Preview milestone (2026-06-10): demo_readable_before_after_report and trial_bucket_link_preview completed. Safe claim: before/after trace difference is human-readable, and a new same-exact-key demo trial can trace-only link to a prior not_retained session_experience_record candidate. Forbidden: no cross-session storage, memory write, lesson retention/application, behavior change, action selection influence, history runtime, semantic/fuzzy/vector retrieval, predictor mutation, or proof-of-learning claim.
- Mentor-Gated Retention milestone (2026-06-10): temporary cross-session reality boundary clarified as demo/fixture handoff only, not durable persistence or memory. First true retention path added: valid session_experience_record + exact mentor_text `留` -> append-only JSONL -> load back. Status: mentor-gated durable retention only. Forbidden: no automatic retention, four-layer memory, semantic/fuzzy/vector retrieval, lesson application, action selection influence, behavior change, predictor mutation, history runtime beyond append/load JSONL, or proof-of-learning claim.
- Retention Readback/Listing milestone (2026-06-10): Retained Experience Readback Preview Minimal v0 and Retained Experience Listing CLI Minimal v0 completed. Mentor-gated retained JSONL records can be loaded back, shown as read-only previews, and listed read-only. Status: durable append/load/list path exists for exact mentor_text `留`; no production write CLI beyond approved retention path. Forbidden: no automatic retention, four-layer memory, semantic/fuzzy/vector retrieval, lesson application, action selection influence, behavior change, predictor mutation, JSONL edit/delete during listing, or proof-of-learning claim.

### Recent Visual-Retention Milestones

- Visual-Retention Snapshot milestone (2026-06-10): Visual-Retention Demo Snapshot Minimal v0 completed; visual change -> focus preview -> visual lesson evidence -> retained experience link preview -> demo snapshot is read-only/human-inspection-only; exact-key preview only; no object/semantic vision, active focus, lesson/action influence, memory/new retention write, retrieval expansion, predictor mutation, or proof claim.
- Minimal Visual Grounding Trial milestone (2026-06-10): Minimal Visual Grounding Trial v0 completed; controlled symbolic visual change -> visual_experience_candidate -> retina_focus_preview -> visual_lesson_evidence_candidate -> visual_retention_demo_snapshot -> human-readable grounding trial summary.
- Safe claim: trace/read-only visual grounding can show what changed, what focus preview points to, what evidence says, and whether retained experience matched by same_exact_key_only.
- Forbidden: no object recognition, semantic vision, active focus, lesson application, action influence, behavior change, memory write, new retention write, semantic/fuzzy/vector retrieval, predictor mutation, or proof-of-learning claim.
