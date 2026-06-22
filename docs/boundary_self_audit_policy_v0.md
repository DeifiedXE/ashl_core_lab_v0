# Boundary Self-Audit Policy v0

Status: Docs-Only Policy
Runtime Impact: None
Boundary Index Impact: None

---

## Purpose

Define the recurring self-audit rule for Boundary Index packages.

The goal is to reduce Codex overclaiming, schema-memory errors, and boundary drift as the Boundary Index advances.

This policy does not grant runtime capability.

---

## Trigger Rule

After every 10 boundary packages, create a docs-only boundary self-audit covering the previous 10 boundary packages.

Current reference point:

```text
Current Boundary Index at policy creation: 2026-06-09-b134
Next expected 10-boundary audit trigger: after b144
Suggested audit filename: docs/b135_b144_boundary_hallucination_self_audit_minimal_v0.md
```

If a package does not bump the Boundary Index, it does not count toward the 10-boundary trigger.

---

## Audit Scope

Each 10-boundary audit should cover:

```text
the previous 10 boundary-index-changing packages
their runtime/checker output when available
their documented safe claims
their documented forbidden claims
their CLI/smoke/unittest coverage when available
schema/key claims copied from parsed runtime output
```

The audit should not become a new capability package.

---

## Required Separation

Each audit must clearly separate:

```text
verified repo facts
parsed runtime output
audit-script assumptions
corrected assumptions
unverified claims
forbidden claims checked
```

Do not mix audit-script assumptions with verified facts.

If an audit script assumes a key name and the runtime output shows a different key, the runtime output wins.

---

## Exact Key Echo Rule

All schema/key claims must be copied from parsed runtime output.

Required exact echoes include:

```text
boundary keys
record keys
source keys
status keys
summary keys
observed outcome keys
blocked flag keys
```

Do not report remembered key names unless they were parsed from the current runtime output.

If a key is missing from runtime output, say it is missing instead of inferring it.

---

## Mutation Rule

The audit must not mutate repo files outside the requested audit document unless explicitly instructed.

Default allowed mutation:

```text
add the requested docs-only audit file
```

Default forbidden mutation:

```text
runtime modules
tests
smoke tests
README
research_plan
Boundary Index
capability matrix
task queue
retained JSONL
memory files
predictor files
```

Exceptions require explicit user instruction.

---

## Boundary Index Rule

The audit must not bump the Boundary Index unless explicitly requested.

Reason:

```text
The audit verifies and documents previous boundary packages.
It does not open a new runtime, memory, predictor, behavior, action, production, or approval boundary.
```

---

## Forbidden Claims

The audit must not claim:

```text
new runtime capability
new sandbox execution
new action creation
feedback application
candidate reordering
memory write
retention write
retained JSONL write
predictor read
predictor influence
predictor mutation
runtime behavior change
production behavior
autonomous learning
proof of learning
consciousness
subjective experience
```

Unless a future package explicitly implements and validates one of these under a dedicated boundary, the audit may only report whether the claim is blocked, supported, unsupported, or contradicted.

---

## Minimal Audit Structure

Recommended sections:

```text
1. Scope
2. Parsed Runtime Outputs
3. Exact Boundary Echo
4. Exact Record / Source Key Echo
5. Verified Repo Facts
6. Audit-Script Assumptions
7. Corrected Assumptions
8. Safe Claims Checked
9. Forbidden Claims Checked
10. Hallucination Verdict
11. Non-Claims
```

---

## Current Policy Status

This policy was added after explicit user request.

It is a documentation rule for future work.

It does not retroactively validate all past Boundary Index packages.

