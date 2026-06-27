# ASHL Core / Qingyin instinct / lesson layer relation assumption v0.1

## Definition

The lesson layer is traceable and reviewable. It is not a hidden instinct layer.

The current assumption is that lessons can influence action choice as explicit candidates, but they must remain inspectable through trace, review state, eligibility checks, and conflict checks.

## Relation Models

### A. Lesson assists instinct / drive layer

The lesson layer can assist a future instinct or drive layer by providing reviewed action knowledge. In this model, a lesson does not replace instinct; it supplies structured evidence that may shape candidate generation.

### B. Lesson competes with instinct / action candidates

The lesson layer may produce an action candidate that competes with other action candidates. An arbiter or selection helper chooses the final action candidate according to explicit eligibility and conflict rules.

### C. Future familiarity-based internalization

A lesson may become instinct-like only through familiarity-based internalization. This is not implemented now.

Internalization would require explicit evidence gates, review gates, conflict gates, failure gates, challenge gates, and rollback. A repeated lesson must not silently become instinct. The evaluator must detect mismatch between expected and actual outcomes before any lesson can claim corrective authority.

## Future Internalization Guards

A future internalization candidate should require at least:

- The lesson is approved.
- The lesson is active.
- The lesson is not stale.
- The lesson is not superseded.
- There is no active conflict.
- `success_count` meets a threshold.
- `challenge_survival_rate` meets a threshold.
- `recent_failure_count` stays below a threshold.
- Human review confirms the internalization candidate.
- A rollback path exists.

## Boundaries

- This document does not add a familiarity score.
- This document does not add success / failure / challenge counters.
- This document does not add an internalization gate.
- This document does not add an instinct-like runtime layer.
- This document does not implement an evaluator.
- This document does not implement Phase 0 runtime integration.
- This document does not change selection behavior.
- This document does not change conflict behavior.
- This document does not change strict supersede activation.
