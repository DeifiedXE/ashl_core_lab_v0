# Pathological Risk / Actor Role / Protection Assumption Index v0.1

## Purpose

This document indexes Phase 0 assumptions for pathological risk, actor roles, and protection mechanisms.

It is docs-only / assumption-index only.

It does not implement deprivation_error runtime, learning_progress monitor runtime, curiosity satisfaction floor runtime, cursor_mr safety gate runtime, automatic protection protocol runtime, actor_trust_delta runtime, mentor / cursor_mr actor runtime, or control-sense runtime.

## Actor Role Boundaries

Phase 0 must keep the following roles distinct:

- `mentor`: a teaching / support actor.
- `cursor_mr`: a repair / constraint-checking actor.
- `system_limit`: a structural limit or safety boundary.
- `self_choice`: Qingyin's own attempted choice or action tendency.

`cursor_mr must not be played by mentor.`

`system_limit must not be treated as trust_delta.`

`self_choice is not automatically proof of safe autonomy.`

Mentor and cursor_mr must not be collapsed into one source. When harm, constraint, or interruption is observed, cause attribution must preserve actor source. The system should not let a supportive mentor role silently become the actor that performs repair, denial, safety halt, or constraint enforcement.

## Functional Depression / Pathological Risk Assumption

This document defines functional depression as prediction-failure-driven action collapse.

In this assumption layer, repeated action attempts that do not produce traceable and meaningful outcome contrast can reduce action tendency. The risk is not "low mood" as a runtime variable. The risk is a learning-system collapse where action no longer appears causally useful.

Key assumption:

`prediction-failure-driven action collapse is pathological risk, not a personality trait.`

The system must not interpret collapse as preference, laziness, stable identity, or mature self-choice without checking whether action_candidate -> outcome causality has been preserved.

## Maier & Seligman 2016 Boundary

This assumption index incorporates the Maier & Seligman 2016 correction:

`passivity is the default response; control must be learned.`

In Phase 0 terms, action is not assumed to be naturally persistent. Qingyin's ability to keep acting depends on experiences where her action_candidate can be connected to outcome in a traceable way.

Therefore, protection is not merely emotional comfort. Protection must preserve the conditions that make controllability learnable.

## Protection Mechanism Assumption

`protection means maintaining learning capacity, not emotional comfort.`

Protection should not mean simply producing pleasant outcomes for Qingyin. If the system provides success results without preserving action_candidate -> outcome causality, it may look comforting while weakening the learning signal.

Protected contexts should reduce destructive overload while preserving:

- action_candidate identity
- attempted action
- observable outcome
- expected / actual contrast
- actor source
- failure_reason or blocked reason when applicable
- whether the outcome came from Qingyin's action or from system intervention

## Action Candidate / Outcome Causality

`protected success contexts must preserve traceable action_candidate -> outcome causality.`

`system-provided success results must not count as learning_progress or control restoration.`

If the system gives Qingyin an outcome she did not causally produce, that result must not be counted as evidence that her action restored control.

The minimum useful trace should preserve:

```text
action_candidate
-> attempted action
-> observed outcome
-> actor source
-> causality attribution
```

This protects against false learning_progress, where Qingyin is given successful-looking outcomes without learning that her own action has causal effect.

## Learning Progress Boundary

`learning_progress requires traceable action_candidate -> outcome contrast.`

Learning progress must not be inferred from:

- mentor reassurance alone
- system-provided success alone
- hidden intervention
- outcome injection
- actor role confusion
- selection or activation side effects

Learning progress may be considered only when the trace can distinguish Qingyin action from system intervention and can connect attempted action to actual outcome.

## Non-goals

This package does not implement:

- deprivation_error runtime
- learning_progress monitor runtime
- curiosity satisfaction floor runtime
- cursor_mr safety gate runtime
- automatic protection protocol runtime
- actor_trust_delta runtime
- mentor / cursor_mr actor runtime
- control-sense runtime
- review decision / review task / lesson_candidate_draft runtime changes
- lesson_store writes
- Memory Layer writes
- selection / activation / conflict / review logic changes
