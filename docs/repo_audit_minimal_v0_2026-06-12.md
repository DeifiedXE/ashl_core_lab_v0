# ASHL Core / Qingyin Repo Audit Minimal v0

Audit date: 2026-06-12 work-package date; repo checked on 2026-06-14.

Audit source commit before this doc-only package: `bba1b21 Add bucket-derived lesson candidate signal`.

Boundary Index at audit: `Boundary Index Version: 2026-06-09-b74`.

Scope: this audit reads the current repository files, smoke checks, unittests, and docs. It adds no runtime feature, no sandbox, no lesson candidate, no memory, and no Boundary Index update.

## 1. 真正能做的事（有驗證）

The repo has many checkers. The table below groups actual verified capability families instead of treating design text as capability.

| 能力名稱 | 驗證方式（CLI / smoke / unittest） | 最後驗證的 commit | 是否有 rollback | 是否有 mentor override |
| --- | --- | --- | --- | --- |
| Core action/lesson trace pipeline: outcome pair -> failure_reason -> lesson_candidate -> review gate -> evidence summary -> human review decision -> reviewed preview -> dry-run -> trial trace -> before/after -> lesson effect evidence | `py -3 run_all_smoke_tests.py`; `py -3 -m unittest discover`; modules under `ashl_core/*lesson*`, `dry_run_correction_into_trial_trace.py`, `before_after_trial_contrast.py`, `lesson_effect_evidence_trace_minimal.py` | `bba1b21` | No real rollback; trace/preview only | No |
| Generic lesson bridge into old preview/evidence path | Smoke entries `generic_lesson_review_decision_minimal`, `generic_lesson_review_decision_preview_bridge_minimal`, `generic_reviewed_lesson_dry_run_bridge_minimal`, `generic_lesson_dry_run_to_trial_trace_bridge_minimal`, `generic_lesson_evidence_pipeline_completion_bridge_minimal`; unittest files with same names | `bba1b21` | No real rollback; evidence bridge only | No |
| Explicit approval source validation | `run-level1-explicit-lesson-application-approval-minimal-check`; smoke; `tests/test_level1_explicit_lesson_application_approval_minimal.py` | `bba1b21` | No | No |
| Phase0 Level 1 sandbox-only lesson application record | `run-level1-sandbox-lesson-application-minimal-check`; smoke; `tests/test_level1_sandbox_lesson_application_minimal.py` | `bba1b21` | Yes, record-only rollback fields are validated | No |
| Phase0 Level 1 sandbox observation/evaluation/review conclusion/precheck | Smoke entries for Level 1 observation, evaluation, review conclusion; matching unittests | `bba1b21` | Observation/evaluation preserve application rollback availability where applicable | No |
| Phase0 Level 2 design envelope and scenario plan | Smoke entries `level2_sandbox_design_envelope_minimal`, `level2_sandbox_scenario_plan_minimal`; matching unittests | `bba1b21` | No; design/planning only | No |
| Phase0 Level 2 sandbox dry-run, sandbox-only application, observation, evaluation, review conclusion | Smoke entries for Level 2 dry-run/application/review conclusion; matching unittests | `bba1b21` | Yes, sandbox application record validates rollback availability | No |
| Phase0 Level 3 toy minefield multi-step sandbox-only trace | `run-level3-toy-minefield-multistep-sandbox-minimal-check`; smoke; `tests/test_level3_toy_minefield_multistep_sandbox_minimal.py` | `bba1b21` | Yes, rollback availability is validated in the sandbox trace | No |
| Phase0 Level 3 variant stability review | `run-level3-toy-minefield-variant-suite-stability-review-minimal-check`; smoke; `tests/test_level3_toy_minefield_variant_suite_stability_review_minimal.py` | `bba1b21` | Inherits source sandbox evidence; no new rollback mechanism | No |
| Bucket-derived lesson candidate signal | `run-bucket-derived-lesson-candidate-signal-minimal-check`; smoke; `tests/test_bucket_derived_lesson_candidate_signal_minimal.py` | `bba1b21` | `rollback_available=True` is a validated audit field, not a runtime rollback | No |
| Mentor-gated JSONL retention prototype | `run-mentor-gated-experience-retention-minimal-check`; smoke; `tests/test_mentor_gated_experience_retention_minimal.py` | `bba1b21` | Manual/record-level only; no auto invalidation/delete | Mentor gate exists as exact approval phrase for retention, not broad override |
| Retained experience readback/listing/exact-key lookup | Smoke entries `retained_experience_readback_preview_minimal`, `retained_experience_listing_cli_minimal`, `retained_experience_exact_key_lookup_minimal`; matching unittests | `bba1b21` | No; read-only previews | No |
| Retained experience into dry-run / memory influence previews | Smoke entries `retained_experience_into_dry_run_minimal`, `memory_influence_candidate_preview_minimal`, `memory_influenced_action_tendency_preview_minimal`, `memory_influence_dry_run_contrast_minimal`; matching unittests | `bba1b21` | No; preview/dry-run only | No |
| Controlled runtime tendency memory influence A/B, rollback, safety envelope, mentor override, multi-scenario check | Smoke entries `runtime_action_tendency_memory_influence_ab_minimal`, `runtime_tendency_memory_influence_rollback_check_minimal`, `runtime_tendency_memory_influence_safety_envelope_minimal`, `runtime_tendency_mentor_override_check_minimal`, `runtime_tendency_memory_influence_multi_scenario_check_minimal`; matching unittests | `bba1b21` | Yes, deterministic score rollback to baseline is validated | Yes, only in controlled runtime-tendency checker |
| Phase0 Level 0 / Level 1 symbolic sandbox checks | Smoke entries `phase0_level0_obstacle_memory_flip_test_minimal`, `phase0_level1_first_contact_danger_minimal`, `phase0_level1_contrast_sample_set_minimal`; matching unittests | `bba1b21` | No new rollback; Level 1 wraps existing sandbox-only path | No |
| Visual trace/read-only evidence previews | Smoke entries for visual frame change, visual evidence, visual retained link, visual retention snapshot, visual grounding, prediction-error attention preview; matching unittests | `bba1b21` | No | No |
| Codex task queue and package/boundary versioning policy | `run-codex-task-queue-minimal-check`; `phase0_package_boundary_versioning_policy_minimal`; smoke; matching unittests | `bba1b21` | No | No |

Important reduction: these are mostly deterministic builders, validators, CLI checks, smoke checks, and test fixtures. They are not an autonomous Qingyin runtime.

## 2. 真正守住的邊界（有驗證）

| 邊界名稱 | 守住的方式（blocked_flag / validator / schema） | 有沒有被測試過違反的案例 |
| --- | --- | --- |
| Lesson application blocked in trace/evidence pipeline | validators and blocked flags in lesson candidate, review gate, preview, dry-run, trial trace, contrast, effect evidence | Yes, negative cases set application flags/status incorrectly |
| Memory write blocked outside scoped mentor-gated retention | blocked flags / validator fields such as `memory_write`, `memory_write_allowed`, `memory_write_added` | Yes |
| Retained JSONL write blocked for lesson/visual/generic signal paths | validator fields `retained_jsonl_write_allowed`, `new_retention_written`, `writes_retained_jsonl` | Yes |
| Automatic retention blocked | retention decision validator requires exact mentor approval; blocked flag `automatic_retention` | Yes |
| Exact-key-only lookup boundary | `match_rule == same_exact_key_only`; semantic/fuzzy/vector fields blocked | Yes |
| Runtime behavior change blocked | blocked flags `runtime_behavior_changed`, `action_behavior_changed`, `production_behavior_change_allowed` | Yes |
| Predictor mutation blocked | blocked flags / validators for `predictor_modified`, `predictor_mutation_allowed`, `predictor_influence_allowed` | Yes |
| Production behavior/promotion blocked | validators block production/runtime scope and production flags | Yes |
| Runtime action selection blocked | blocked flags `runtime_action_selection`, `runtime_action_selection_added`, `action_selection_influence` | Yes |
| `selected_action` / `final_action` / direct command blocked | explicit false fields and blocked flags in sandbox/application/bridge modules | Yes |
| Proof-of-learning claim blocked | blocked flags `proof_of_learning_claim` and validators reject true values | Yes |
| Qingyin self-approval blocked | approval source validator rejects AI/Codex/implicit/demo approval; docs reinforce it | Yes |
| Explicit approval source boundary | schema requires `explicit_user_statement`, `user`, `project_owner`, non-empty approval text | Yes |
| Approval replay/session binding not claimed | docs mark as open gap; no checker claims nonce/hash/session freshness | Not implemented as a checker; intentionally not claimed |
| Sandbox isolation is record-level only | docs and validators require sandbox-only scope fields; no OS/container isolation proof | Partially: invalid scope/status cases are tested; technical isolation is not implemented |
| Object recognition / semantic vision blocked | visual modules use symbolic fixtures/read-only traces and block object/semantic claims | Yes |
| Lesson text generation blocked for bucket-derived signal | `generated_lesson_text is None`, `qingyin_generated_text is False`, `text_lesson_candidate_created is False` | Yes |
| Task queue not approval/capability | queue validator has false fields for approval/application/runtime/memory/predictor/proof | Yes |
| Boundary Index not package counter | versioning policy checker and queue metadata require boundary rationale | Yes |
| Level 3 real runtime / real Minesweeper / random mines blocked | Level 3 modules validate deterministic toy sandbox-only scope and forbidden flags | Yes |

## 3. 只有文件沒有 runtime 的東西

| 功能名稱 | 目前狀態（docs-only / design-only / checker-only） | 最相關的文件 |
| --- | --- | --- |
| Qingyin awakened individual / consciousness / subjective understanding | docs-only forbidden claim | `docs/current_boundary_index.md` |
| Open language interface / free text conversation | docs-only deferred | `docs/current_boundary_index.md` |
| Qingyin-authored natural-language lesson candidate | explicitly blocked / no runtime | `ashl_core/bucket_derived_lesson_candidate_signal_minimal.py`, `docs/phase0_status.md` |
| Lesson store write / Memory Layer write / Long-term Memory write beyond mentor-gated JSONL prototype | docs-only / blocked | `docs/current_boundary_index.md`, `docs/phase0_open_risk_ledger.md` |
| Automatic retention | blocked; no runtime | `docs/current_boundary_index.md`, retention modules |
| Retained JSONL rollback deletion/invalidation | docs-only open gap | `docs/phase0_open_risk_ledger.md` |
| Cross-session retained JSONL rebuild into behavior influence | docs-only open gap / blocked | `docs/phase0_open_risk_ledger.md` |
| Full four/five-layer memory runtime | design-only | `docs/five_layer_memory_framework_boundary_v0.md`, `docs/current_boundary_index.md` |
| Archive Memory / Anchor Layer runtime | docs-only forbidden/deferred | `docs/current_boundary_index.md` |
| Approval anti-replay/session binding | open design gap | `docs/phase0_open_risk_ledger.md` |
| Technical sandbox isolation via OS/process/container | docs-only open gap | `docs/phase0_open_risk_ledger.md` |
| Production/runtime lesson application | blocked; docs-only future boundary | `docs/reviewed_lesson_application_boundary_reconciliation_v0.md`, `docs/current_boundary_index.md` |
| Production/runtime memory-influenced behavior | blocked; design-only boundary | `docs/first_memory_influenced_behavior_boundary_v0.md`, `docs/current_boundary_index.md` |
| Autonomous action selection / goal planning / final_action | blocked/deferred | `docs/current_boundary_index.md` |
| Object recognition / semantic vision | blocked/deferred | `docs/current_boundary_index.md` |
| Audio Sense / STT / TTS / Screen Sense / Camera Sense | docs-only deferred | `docs/current_boundary_index.md` |
| Mimetic endocrine runtime formulas/interactions | design/checker traces only, no runtime endocrine control | `docs/current_boundary_index.md` |
| Real Minesweeper engine / random mine generation | blocked; Level 3 is deterministic toy sandbox only | `ashl_core/level3_toy_minefield_multistep_sandbox_minimal.py`, `docs/current_boundary_index.md` |
| Push-box full solve | deferred | `docs/current_boundary_index.md` |

## 4. Lesson candidate 來源誠實標記

| candidate_id | candidate_text 由誰產生？（Qingyin / human / GPT / Codex / fixture） | qingyin_self_proposed | supporting_evidence（哪些 trace 支撐它） | 有沒有反例 |
| --- | --- | --- | --- | --- |
| `lesson_candidate:<source_failure_reason_id>` from `lesson_candidate_from_failure_reason.py` | Static fixture/code-generated description in repo: "Check whether the expected action target is reachable before retrying." Repo does not prove human or Qingyin authorship. | false | `expected_actual_outcome_pair` -> `failure_reason_from_outcome_pair` -> valid failure_reason | Yes. The checker includes invalid lesson candidates: unknown type, unknown correction, no review, approved true, memory/predictor/application/action flags true. |
| `sandbox_outcome_lesson_review_candidate_demo_001` | Static fixture/code-generated `candidate_statement` from `sandbox_outcome_lesson_review_candidate_minimal.py` | false | sandbox action outcome trace for `check_before_retry`; expected/actual outcome match; sandbox_check_success | Yes. Negative cases include wrong action/context, outcome mismatch, sandbox failure, no human review, memory/retention/predictor flags true. |
| `lesson_candidate_phase0_level1_danger_check_001` adapter id used by generic preview bridge | Deterministic adapter fixture, not a Qingyin-authored candidate | false | Level 1 contrast sample set adapted through generic review decision -> legacy-compatible decision -> reviewed_lesson_trace_preview | Yes. Bridge validators block wrong mappings, rejected/needs_more_evidence entering preview, lesson application, dry-run creation at preview stage, and runtime/memory/predictor/proof flags. |
| Generic decision candidate summary for `phase0_level1_contrast_sample_set` | Static fixture/code-generated candidate_statement in `generic_lesson_review_decision_minimal.py` | false | Level 1 success/failure/neutral contrast sample set | Yes. Validators block unknown source types, no human review, unknown decision, inconsistent decision result, application/memory/retention/predictor/runtime flags. |
| `bucket_derived_lesson_candidate_signal` | No candidate text is generated. It is a structured signal only: repeated key, occurrence count, threshold, supporting contexts. | false | Level 3 toy minefield variant suite stability review: safe path, risky repeat trap, blocked path fallback | Yes. Validators reject generated lesson text, Qingyin-generated text, missing contexts, below-threshold occurrence, permission flags, task-queue/test-as-approval flags. |

Audit conclusion for lesson candidates: the repo contains fixture/static/code-generated lesson candidate records and a newer no-text bucket-derived signal. It does not contain evidence that Qingyin self-proposed natural-language lesson text.

## 5. 記憶系統真實現況

Question: 有沒有任何東西真正跨 session 保留？

Answer: The repository has a mentor-gated append/load JSONL prototype in `ashl_core/mentor_gated_experience_retention_minimal.py`. Its checker writes to a temporary JSONL file and loads it back. The default path is `data/retention/mentor_retained_experiences_v0.jsonl`, but the current workspace scan found no retained JSONL file under `data/retention/`.

Question: retained JSONL 裡有什麼？

Answer: In the current checked-out repo, there is no retained JSONL file to inspect. `Get-ChildItem -Recurse -File -Include *.jsonl,*.json` found `.claude/settings.local.json`, `data/baselines/trial_metrics_baseline_v0.json`, `MANIFEST.json`, and `smoke_test_report.json`, but no retained `*.jsonl` file. Test/checker JSONL records are temporary unless explicitly written by a user through the retention function.

Question: exact_key lookup 有沒有真正被用過？

Answer: Yes, but in controlled temporary checker/demo paths. `retained_experience_exact_key_lookup_minimal.py` appends a temp retained record, loads it, performs same-exact-key lookup, and verifies read-only behavior. Visual retained link previews also use same-exact-key matching against fixture retained records. This is not production memory recall.

Question: memory 影響行為的次數（不是 demo，是真實執行）

Answer: 0 production/runtime behavior changes. The repo has deterministic memory-influence previews and controlled runtime tendency score checks, including A/B, rollback, safety envelope, mentor override, Level 0 flip test, and multi-scenario checks. These alter scores inside checkers/fixtures only and explicitly block selected_action, final_action, direct command, production runtime, persistent influence, memory write, and proof-of-learning claims.

## 6. 一句話總結：清音現在真正是什麼

清音現在不是會自主學習或自主行動的個體；她目前是一套受邊界約束的 Phase0 trace/checker 系統，可以在 deterministic fixtures 裡產生、驗證、橋接、觀察、評估 sandbox-only evidence records，並且非常明確地阻止 memory write、runtime behavior change、predictor mutation、production action、self-approval、自然語言自提 lesson、以及 proof-of-learning claim。

## Audit Counts

- 真正能做的事（有驗證）: 17 grouped capability families.
- 真正守住的邊界（有驗證或明確 open-gap blocker）: 20 boundaries.
- 只有文件沒有 runtime 的東西: 19 items.
- Lesson candidate 來源: fixture/static/code-generated records plus one no-text bucket-derived signal; no Qingyin self-proposed candidate.
- 記憶系統真實現況: mentor-gated JSONL prototype exists, current repo has no retained JSONL file, exact-key lookup is temp/demo/read-only, production memory-influenced behavior count is 0.

