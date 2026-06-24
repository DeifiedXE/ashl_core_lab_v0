# Qingyin Thought System Layering Design v0

Status: design decision draft  
Scope: ASHL Core / Qingyin runtime thought architecture  
Runtime LLM policy: no LLM runtime component; LLM may only be used as an external development tool.  
Boundary Index impact: none; this is a design document only.

## 1. Design Decision

Qingyin's thought system is not a single monolithic "thinking module".

It is divided into four decision modes with different cost, speed, verification depth, and memory access pattern:

```text
Instinct
-> Specialized Thought
-> Coarse Thought
-> Deep Thought
```

These modes are not always executed in sequence. Qingyin should use the cheapest sufficient layer first, then escalate only when uncertainty, conflict, novelty, or risk requires it.

Plain meaning:

> Instinct handles immediate low-level responses. Specialized Thought handles familiar domains through specialty memory anchors. Coarse Thought cross-checks multiple memory sources when confidence is not enough. Deep Thought performs long validation and multi-step preview for unfamiliar or difficult situations.

## 2. Non-LLM Runtime Boundary

Qingyin's runtime thought system must not use an LLM.

LLM may be used only as an external development helper to write code, tests, documents, or reviews. LLM must not become part of Qingyin's runtime cognition.

Disallowed inside Qingyin runtime:

```text
LLM candidate generation
LLM arbitration
LLM memory interpretation
LLM feedback interpretation
LLM output generation
LLM inner monologue
LLM advisor loop
LLM-written runtime state
```

Allowed outside Qingyin runtime:

```text
LLM-assisted coding
LLM-assisted documentation
LLM-assisted test generation
LLM-assisted design review
LLM-assisted package planning
```

This is a design boundary, not a security-key boundary. The purpose is to prevent conceptual contamination: Qingyin's thinking must not secretly be LLM thinking.

## 3. Layer Overview

```text
Deep Thought
  Long validation, multi-step preview, novelty

Coarse Thought
  Cross-memory verification, conflict handling

Specialized Thought
  Specialty anchors, skill-like memory lookup

Instinct
  Fast tendency, immediate block/stop/observe
```

The goal is not to make every action pass through every layer. The goal is to keep common actions fast while preserving safe escalation for difficult cases.

## 4. Instinct

Instinct is the fastest layer.

It does not perform long memory lookup. It does not run multi-step preview. It does not reason about complex goals.

It handles immediate tendency and immediate blocking.

Examples:

```text
blocked -> stop or reduce repeat tendency
denied -> stop
collision -> stop
unknown risk -> observe
repeated immediate failure -> reduce retry tendency
low information -> prefer observe
```

Instinct is not "smart". It is Qingyin's fast protective response.

Instinct input:

```text
current state
immediate action result
blocked / success / denied / collision
basic uncertainty
basic risk signal
```

Instinct output:

```text
stop
observe
retry discouraged
simple approach / avoid tendency
low-level block reason
```

Instinct must not:

```text
write long-term memory
change predictor
create selected_action directly
execute command directly
claim learning
override safety boundary
```

## 5. Specialized Thought

Specialized Thought is the layer between instinct and general reasoning.

It uses specialty anchors or specialized memory indexes to handle familiar domains quickly.

Examples of future specialty anchors:

```text
pushbox_blocked_handling
ui_affordance_operation
text_grounding_core_terms
qingyin_bridge_capability_use
tool_permission_handling
sandbox_repeated_failure_pattern
```

Specialized Thought should not search all memory. It should enter through a relevant specialty anchor and retrieve only domain-relevant memory.

Plain meaning:

> If Qingyin has seen this type of situation before, she should not reopen the entire reasoning court. She should first ask the relevant specialty memory: "Do I already have a known handling pattern for this?"

Specialized Thought input:

```text
current situation summary
detected domain
specialty anchor candidates
recent outcome labels
feedback application records
exact-key or near-key match
```

Specialized Thought output:

```text
specialized candidate action
specialty confidence
matched anchor id
reason codes
known failure warnings
```

Specialized Thought must not:

```text
directly apply long-term learning
invent new specialty anchor without boundary
override current approved purpose
directly reorder candidates without approval
treat a single anchor as absolute truth
```

## 6. Coarse Thought

Coarse Thought performs memory-interleaved verification.

It is slower than Specialized Thought but faster than Deep Thought.

It is used when one memory source is not enough, when specialty anchors conflict, or when recent feedback contradicts an older pattern.

It cross-checks:

```text
working memory
recent trace
specialty anchors
exact-key buckets
feedback evaluation records
feedback application records
current candidate ordering
recent blocked / success pattern
```

Plain meaning:

> Coarse Thought asks several memory witnesses before allowing a candidate to become trusted.

Coarse Thought input:

```text
candidate actions
specialty thought output
working memory
recent trace
feedback application records
conflicting signals
uncertainty score
```

Coarse Thought output:

```text
candidate confidence adjustment
conflict notes
escalation request
reason codes
recommendation to use Deep Thought or not
```

Coarse Thought should trigger when:

```text
candidate scores are close
specialty anchors disagree
recent outcome contradicts prior pattern
feedback was applied record-only but not yet behavior-affecting
environment state is partially unknown
same action failed repeatedly
```

Coarse Thought must not:

```text
change candidate scores directly unless a later approved package allows it
create next-cycle ordering directly
write persistent memory
claim proof of learning
turn record-only feedback into behavior change without boundary
```

## 7. Deep Thought

Deep Thought is the slowest and most expensive layer.

It is used for long validation, unfamiliar situations, multi-step preview, and difficult conflicts.

It may run internal preview or simulation, but preview is not reality.

Critical rule:

```text
preview result != execution outcome
```

Deep Thought can compare possible paths, but it cannot treat predicted outcomes as observed outcomes.

Examples:

```text
preview move_up -> move_right -> push_down
compare observe_front vs alternative_probe
test whether repeated blocked implies route change
evaluate whether current goal is underspecified
```

Deep Thought input:

```text
situation model
candidate paths
coarse thought conflict report
world model
short-term trace
risk flags
uncertainty flags
```

Deep Thought output:

```text
candidate path set
preview result
risk note
uncertainty note
reason codes
recommended candidate ordering input
```

Deep Thought should trigger when:

```text
new environment appears
no specialized anchor applies
coarse thought cannot resolve conflict
multi-step planning is required
tool/capability behavior is unknown
high uncertainty remains after observation
repeated failure has no obvious alternative
```

Deep Thought must not:

```text
execute action
write memory
change predictor
apply feedback
reorder candidates directly without boundary
create selected_action directly
claim success before execution
claim learning from preview
```

## 8. Escalation Policy

The thought system should prefer the cheapest sufficient layer.

```text
If instinct can safely handle it:
    use instinct

Else if a relevant specialty anchor exists:
    use specialized thought

Else if several memory sources must be checked:
    use coarse thought

Else if the situation is novel, conflicting, or multi-step:
    use deep thought
```

Escalation examples:

```text
blocked once
-> instinct: stop/reduce immediate retry

blocked repeatedly in a familiar pushbox pattern
-> specialized thought: use pushbox blocked handling anchor

specialty anchor says retry, recent trace says repeated failure
-> coarse thought: cross-check memory conflict

no known anchor and route requires multiple steps
-> deep thought: preview candidate paths
```

## 9. Relation To Memory Layers

This design assumes memory is layered and indexed.

Relevant memory concepts:

```text
core memory
long-term memory
working memory
archive memory
anchor layer
specialty anchors
exact-key buckets
feedback evaluation records
feedback application records
```

Specialized Thought should use specialty anchors. Coarse Thought should cross-check multiple memory sources. Deep Thought may use a broader situation model and short preview, but still should not directly mutate memory.

Memory influence should remain gated:

```text
memory lookup
-> influence candidate
-> approval boundary
-> possible ordering effect
```

Memory must not silently become action authority.

## 10. Relation To Current Action Line

Current ASHL action line:

```text
candidate ordering
-> arbitration
-> selected_action
-> final_action
-> direct_command
-> execution
-> outcome observation
-> feedback evaluation
-> feedback application
-> candidate reordering
-> next-cycle selection
```

Thought layers should feed into candidate generation and candidate ordering, not bypass the action line.

Expected relationship:

```text
Instinct
-> immediate tendency / block signal

Specialized Thought
-> specialized candidate hints

Coarse Thought
-> memory-cross-checked confidence notes

Deep Thought
-> previewed candidate paths

Candidate Ordering / Arbitration
-> chooses among candidates under boundary policy
```

The thought system must not directly jump to execution.

## 11. Relation To Habit / Skill Formation

Habit or skill is not the same as Deep Thought.

Habit grows when repeated feedback becomes safe to use as a faster tendency.

Expected path:

```text
outcome observation
-> feedback evaluation
-> feedback application
-> feedback-gated reordering
-> repeated stable pattern
-> specialty anchor / habit candidate
-> future approval for faster use
```

This means:

```text
record-only feedback application != behavior change
candidate reordering != long-term habit
habit candidate != permanent memory
specialty anchor != unrestricted authority
```

Specialized Thought is where mature habit-like patterns can later be accessed quickly.

## 12. Fast Path And Slow Path

Future runtime should not keep every Phase 0 approval chain as a hot-path burden.

Instead:

```text
Fast path:
low-risk, familiar, sandbox-only, reversible, previously validated pattern

Guarded path:
memory-influenced, feedback-influenced, new specialty anchor, tool-like action

Slow path:
novel, conflicting, high uncertainty, multi-step, real-world adjacent
```

This prevents excessive review from becoming Qingyin's electronic ankle chain.

The detailed Phase 0 boundaries are used to prove safety patterns first. Later they should be compiled into policy gates and templates.

## 13. Minimal Data Shape

Possible thought record:

```json
{
  "thought_record_id": "thought_0001",
  "thought_mode": "coarse_thought",
  "trigger": "specialty_memory_conflict",
  "llm_used": false,
  "situation_summary": {
    "last_action": "push_right",
    "last_result": "blocked",
    "repeated_failure_count": 2
  },
  "memory_sources_checked": [
    "working_memory",
    "recent_trace",
    "specialty_anchor:pushbox_blocked_handling"
  ],
  "generated_candidates": [
    "observe_front",
    "move_up",
    "wait_or_observe"
  ],
  "reason_codes": [
    "previous_push_right_blocked",
    "information_insufficient",
    "low_risk_observation"
  ],
  "output_authority": "candidate_input_only",
  "direct_execution_allowed": false,
  "memory_write_allowed": false
}
```

## 14. Initial Implementation Recommendation

Do not implement full runtime immediately.

Recommended first package type:

```text
Qingyin Thought Layering Design Assumption v0
```

Docs-only or schema-only.

It should define:

```text
Instinct
Specialized Thought
Coarse Thought
Deep Thought
escalation triggers
allowed outputs
disallowed authority
relationship to memory
relationship to candidate ordering
no LLM runtime boundary
```

Do not yet implement:

```text
actual thought runtime
actual specialty anchor lookup
actual candidate reordering
actual memory write
actual predictor influence
actual production behavior
```

## 15. Final Statement

Qingyin's thought system should be layered by cost and verification depth:

```text
Instinct:
fast tendency and immediate blocking

Specialized Thought:
familiar-domain memory through specialty anchors

Coarse Thought:
cross-memory verification and conflict handling

Deep Thought:
long validation and multi-step preview
```

This gives Qingyin a middle space between raw instinct and slow deliberation.

The system should let familiar actions become faster without allowing hidden authority, fake learning, or LLM contamination.

One-line summary:

> Instinct is fast. Specialized Thought is skilled. Coarse Thought is cross-checked. Deep Thought is careful.
