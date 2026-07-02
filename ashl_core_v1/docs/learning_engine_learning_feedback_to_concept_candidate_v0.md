# Learning Engine Learning Feedback To Concept Candidate v0

Package 90 adds teacher-gated conversion from `LearningFeedbackCandidate`
records into ConceptCandidate draft bridge records.

The package can create:

- `LearningFeedbackTeacherReviewRecord`
- `LearningFeedbackTeacherReviewSet`
- `LearningFeedbackToConceptCandidateDraftRecord`
- `LearningFeedbackToConceptCandidateRollbackRecord`
- `LearningFeedbackToConceptCandidateSafetyAudit`

The package does not create `ReviewedConcept`, does not write memory layers,
does not approve learning automatically, and does not change task behavior or
the action path.

Teacher approval means only `approved_for_concept_candidate_draft`.
Draft records still require later ConceptCandidate review, counterexample
checking, ReviewedConcept gates, and memory write gates.
