# Explicit User Approval Source Boundary v0

Date: 2026-06-12

## Purpose

This document corrects the source boundary for explicit lesson application approval.

Explicit human application approval must come from the user, not from Codex, AI, or a test fixture.

## Correct Approval Source

Only the project owner / user can provide explicit application approval.

Required real approval source fields:

```text
approval_source == explicit_user_statement
approval_actor == user
approver_role == project_owner
approval_text is non-empty
```

## Codex / AI Boundary

Codex may record approval, but cannot provide approval.
AI may validate approval, but cannot provide approval.

Codex / AI must not infer approval from:

- completed tests
- completed readiness records
- repository state
- demo fixtures
- implicit user intent
- implicit chat command text

## Not Approval

A test fixture is not real approval.
implicit chat command is not application approval.
A completed readiness record is not approval.
Passing tests are not approval.

## Allowed Recording

ASHL Core may record and validate a user-provided approval statement when the approval source is explicit and the actor is the project owner / user.

This recording still does not apply a lesson.

## Forbidden

This boundary correction does not add:

- lesson application
- sandbox lesson application
- runtime lesson application
- memory write
- retention write
- predictor mutation
- runtime behavior change
- production action selection
- selected_action creation
- final_action creation
- direct action command
- proof of learning claim
