# Learning Engine Concept Candidate From Task Closure Draft v0

## Purpose

This package turns deterministic Task Engine closure material into draft-only
Learning Engine `ConceptCandidate` records.

It also creates a simple teaching test seed so the teacher can inspect the
candidate before any later review package exists.

## Plain Meaning

Package 61 defined what a concept candidate looks like.

Package 62 drafts one candidate from task closure material:

task closure / learning candidate source
-> concept draft source
-> ConceptCandidate draft
-> teaching test seed

The result is not a learned concept.

## Draft Sources

The draft source records describe one state, one action, and one outcome from a
closed bounded task case. Supported deterministic demo cases are:

- blocked front obstacle
- simple reach success
- unknown state that needs observation
- expected-vs-actual conflict
- teacher stopped / suspended control boundary

Unknown-vs-unknown is explicitly blocked because it is not valid learning
evidence.

## Teaching Test Seed

Each valid draft can produce a teaching test seed. The seed asks the teacher to
inspect:

- support evidence
- counterexample evidence
- whether the scope is too broad
- whether the candidate should be narrowed or split
- whether more support is needed

The seed does not create a teacher decision.

## Non-Goals

This package does not create automatic concept extraction, concept approval,
reviewed concepts, memory writes, MemoryApplicationData, readback hints, task
behavior changes, scheduler behavior, action execution, or any Core /
Long-term / Archive / Anchor write.

## Safe Claim

ASHL Core v1 Learning Engine can draft `ConceptCandidate` records from
deterministic task closure sources and create simple teaching test seeds for
teacher inspection, without approving concepts, writing memory, or changing
task behavior.
