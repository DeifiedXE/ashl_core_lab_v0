# Host Body Evidence To LearningFeedbackCandidate Bridge

Package 108 creates a bounded bridge from Qingyin Host Body v0 evidence into
teacher-reviewable LearningFeedbackCandidate bridge records.

Allowed sources include read-only Host Body trace history readback, internal-only
Host Body action choices and results, Runtime EventFrame bridge traces, and
teacher-observed Qingyin Home surface records.

This package does not create ConceptCandidate, ReviewedConcept, memory-layer
writes, automatic learning approval, teacher approval, Task Engine action
selection influence, external control, first_output, live runtime sessions,
Thought Engine behavior, or production behavior.

The existing task-closure LearningFeedbackCandidate schema is task-specific, so
Package 108 uses bridge-compatible Host Body feedback records and marks the
bridge ready for teacher review instead of forcing unrelated task closure refs.
