# First Memory-Influenced Behavior Boundary Minimal v0

## Purpose

This document defines the high-risk boundary before any future step where retained memory may influence behavior.

It covers the possible future path:

```text
memory_influence_candidate
→ future bounded action tendency influence
→ possible future action selection consideration
```

This package does not implement memory-influenced behavior.

## Current State

Current memory influence preview line:

```text
retained JSONL
→ exact_key lookup
→ retained_experience_dry_run_context
→ memory_influence_candidate
```

Current safe claim: retained memory can create preview-only tendency advice.

## Core Principle

Memory may advise action tendency only.
Memory must not directly choose final_action.
Memory must not create direct action commands.
Memory must not prohibit exploration by itself.
Memory is a warning sign, not a ban command.
Past failure is a warning, not a prohibition.

## Allowed Future Influence Shape

Future memory influence may only adjust action tendency, not select action directly.

Future constraints:

- influence_strength must be bounded.
- default v0 max influence_strength <= 0.3.
- target action tendency must be scope-limited.
- mentor instruction overrides memory influence.
- hard safety boundaries override memory influence.
- curiosity / exploration cannot be globally disabled by memory.
- influence must be traceable and reversible.

## Forbidden Direct-Control Path

The following paths are explicitly forbidden:

```text
retained memory matched → final_action
retained memory matched → direct action command
retained memory matched → runtime action selection
retained memory matched → action behavior changed
retained memory matched → exploration blocked
```

## Required Gates

Before any real memory-influenced behavior may exist, a future package must require:

- valid retained_experience_exact_key_lookup_preview.
- valid retained_experience_dry_run_context.
- valid memory_influence_candidate.
- valid dry-run contrast showing expected effect.
- bounded influence strength.
- scope-limited target action tendency.
- mentor override preserved.
- exploration not blocked.
- rollback path defined.
- audit trace recorded.

## Exploration / Curiosity Boundary

Past failure must not automatically block curiosity or exploration.
Memory can warn that an action tendency deserves caution.
Memory cannot globally disable exploration, curiosity, or retry under future gates.

## Mentor Override Boundary

Mentor instruction must override memory influence.
Memory influence must not block mentor override.
Memory influence must not override safety boundaries or hard runtime gates.

## Rollback Boundary

Any future memory influence must be revocable.
Rollback must remove or disable the influence without deleting the retained source memory.
Retained memory and applied influence are separate.

## Future Minimal Runtime Candidate Shape

Design-only future shape:

```text
memory_influenced_action_tendency_preview_id
source_memory_influence_candidate_id
target_action_tendency
influence_direction
influence_strength
scope
mentor_override_available
exploration_allowed
runtime_action_selection_allowed
blocked_flags
```

`runtime_action_selection_allowed must remain False` until a separate implementation package opens it.

## Not Implemented

- No real memory-influenced behavior.
- No runtime action selection.
- No final_action creation.
- No direct action command.
- No action behavior change.
- No exploration blocking.
- No curiosity override.
- No mentor override blocking.
- No lesson application.
- No memory write.
- No new retention write.
- No semantic/fuzzy/vector retrieval.
- No predictor mutation.
- No four/five-layer memory runtime.
- No anchor layer runtime.
- No proof-of-learning claim.

## Future Package Order

1. Memory-influenced action tendency dry-run contrast.
2. High-risk mentor review of bounded influence scope.
3. Preview-only runtime candidate with `runtime_action_selection_allowed == False`.
4. Separate implementation package for any real behavior influence.
