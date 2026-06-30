# Task Engine Future Task Working Memory Readback Hint Application v0

Package 78 applies prepared reviewed-concept readback hints into a newly
initialized future Task Working Memory as advisory-only readback hints.

This is the first package in the reviewed-concept readback chain that may mark
Working Memory as mutated, but only during new task initialization and only for
the inert `readback_hints` area.

Applied hints remain:

- advisory-only
- single-task lifetime
- future task initialization only
- not candidate ordering authority
- not action selection authority
- not execution authority
- not memory-layer write authority

This package must not mutate running tasks, inject hints mid-task, change
candidate ordering, change task behavior, select actions, execute actions, or
write Core / Long-term / Archive / Anchor memory layers.
