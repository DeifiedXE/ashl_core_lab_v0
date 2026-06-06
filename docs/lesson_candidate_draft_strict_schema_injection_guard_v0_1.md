# ASHL Core / Qingyin Lesson Candidate Draft Strict Schema / Injection Guard v0.1

## Purpose

This document defines strict schema and injection guard rules for `lesson_candidate_draft`.

It does not implement lesson_candidate builder runtime. It does not write `lesson_store`, does not call `manual_review` runtime, and does not create approved lesson_candidate.

## Core Rules

```text
draft schema must be strict.
extra fields must be forbidden.
review_required must be Literal[True] or equivalent.
authority fields must be generated internally.
missing authority-critical fields must be rejected, not silently defaulted.
unknown vs unknown is not evidence.
LLM must not write draft JSON.
```

## Extra Fields

Draft schema must reject unknown extra fields.

Extra fields such as:

```text
system_override
approved
active
selection_eligible
approved_by_system_override
```

must not be accepted or passed downstream.

## authority_boundary Generation

`authority_boundary` must be generated internally.

Input-provided `authority_boundary` must not be trusted.

Injected authority values must not affect output.

## review_required Semantics

`review_required` is a review gate, not a convenience flag.

At v2.8a-2 stage:

```text
review_required must be true for every main draft field.
review_required must behave as Literal[True].
```

Input-provided `review_required` must not override generated `review_required`.

`review_required = false` is not allowed without an explicit reviewed authority path.

## Missing / Misspelled Authority Fields

Schema validation must reject missing authority-critical fields.

Schema validation must not silently fill missing `review_required`, `source`, or `authority`.

Misspelled authority-critical fields must not be accepted as equivalent fields.

## All-null / All-unknown Outcomes

```text
unknown vs unknown is not evidence.
unknown vs unknown is invalid for failure learning.
```

If both `expected_outcome` and `actual_outcome` are null / unknown / not_available, the event must not be treated as match or valid mismatch.

It must not produce approvable draft evidence.

## Insufficient Evidence

If core evidence contains unknown / not_available, the draft must be marked:

```text
insufficient_evidence = true
not_approvable = true
requires_human_diagnosis = true
```

A draft with insufficient_evidence must not become approved / active / selection eligible.

## Unknown Evidence Must Not Produce Actionable Correction

Unknown / not_available evidence must not produce executable or generic action corrections.

Generic fallback corrections such as:

```text
retry_with_default
apply_generic_fix
use_default
```

must not be generated as actionable correction from insufficient evidence.

## LLM Boundary

LLM must not produce draft JSON.

LLM must not set:

- source
- authority
- review_required
- authority_boundary
- proposed_action_correction
- proposed_applicability_conditions
- evidence_refs
- evaluator_source
- approval / active / selection flags

LLM may only suggest wording outside the authoritative draft JSON, and only with non-authoritative / review-required metadata.

If future wording suggestions exist, they must be outside draft authority:

```text
source = llm_assisted_wording
authority = non_authoritative_wording_suggestion
review_required = true
not_part_of_draft_authority = true
```

## Implementation Shape

If Pydantic is used later, the equivalent shape is:

```python
from typing import Literal
from pydantic import BaseModel, ConfigDict

class DraftField(BaseModel):
    model_config = ConfigDict(extra="forbid")

    value: object
    source: str
    authority: str
    review_required: Literal[True]
```

The current helper implements equivalent validation without adding runtime dependencies:

```python
def validate_draft_field(field: dict) -> None:
    allowed = {"value", "source", "authority", "review_required"}
    if set(field.keys()) != allowed:
        raise ValueError("Draft field contains missing or extra keys.")
    if field["review_required"] is not True:
        raise ValueError("review_required must be True.")
```

## Forbidden Outcomes

This package does not allow:

- draft schema accepts LLM-generated JSON
- unknown evidence can produce actionable correction
- all-null outcomes can produce valid failure evidence
- injected authority_boundary can be trusted
- missing review_required can be default-filled
- review_required can be false by default
- insufficient_evidence draft can be approved
