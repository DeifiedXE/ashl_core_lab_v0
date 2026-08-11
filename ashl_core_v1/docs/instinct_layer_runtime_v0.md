# Package 141 Instinct Layer Runtime v0

Status: completed only when the external Package 141 audit reports
`passed_instinct_layer_runtime_v0`.

Package 141 begins the Package 141-148 Bounded Thought Engine line with one
small, deterministic rule surface. It does not implement the complete Thought
Engine.

## Authority reconciliation

The implementation lives under the existing `ashl_core_v1.thought` namespace.
It does not promote the early `ThoughtSignal` fixture, legacy reflex/instinct
documents, tendency design, learned affordance records, or Task Engine rules
into a new authority.

The current boundaries are:

| Structure | Package 141 treatment |
| --- | --- |
| Package 128 `StructuralEvidenceCheckpoint` | The only production input kind; read-only structural fields |
| Package 132 closure | Frozen perception authority and downstream interface contract |
| Package 140 closure | Frozen self-state/drive authority contract |
| Legacy `ThoughtSignal` | Historical fixed-circulation fixture, not instinct authority |
| Legacy reflex/heuristic/instinct documents | Design vocabulary only |
| Package 135 drive trace | Separate authority; not consumed |
| Package 136 modulation | Zero production consumers remain; not consumed |
| Package 138 self-state readback | Zero production consumers remain; not consumed |
| Tendency | Historical directional-pressure design, not created or consumed |
| Learned affordance | Learning/memory evidence, not converted into instinct output |
| Teacher-gated Task Engine chain | Separate higher authority; never entered |
| Existing hard-safety gates | Higher precedence; Package 141 can only honor a block |

## Production contract

The production input allowlist contains exactly:

`package_128_structural_evidence_checkpoint_v0`

The drive-input allowlist, self-state-readback-input allowlist, and Package 141
output production-consumer allowlist are empty. This is intentional. Package
141 does not implicitly import Package 136 or Package 138 merely because those
interfaces now exist.

Each evaluation records the source checkpoint ID and hash, runtime/perception/
window lineage, event and processing time, explicit rule conditions, match
result, bounded annotation, source references, and failure reasons.

## Fixed rules

Package 141 v0 contains exactly two versioned rules:

1. `instinct_rule:visual_closed_span_present:v0`

   Matches when at least one observed visual region and one closed visual span
   are present. It emits `bounded_visual_closed_span_present`.

2. `instinct_rule:visual_open_region_present:v0`

   Matches when at least one observed visual region and one open visual region
   are present. It emits `bounded_visual_open_region_present`.

These are nonsemantic structural annotations. They do not claim an object,
event meaning, importance, interest, confidence, uncertainty, reward, desire,
emotion, or purpose.

There is no weighted score, learned rank, random tie-break, LLM, Codex, or
network call. The canonical rules are all evaluated; their serialization order
is not a priority order.

## Conflict and unknown evidence

When open and closed structural references coexist, both matching rule records
and both revocable precursor signals remain present. The conflict record has no
winner and creates no candidate ordering or action selection.

Valid evidence with no matching condition produces
`neutral_no_rule_matched`. Missing, unknown, wrong-lineage, transport-faulted,
or hard-safety-blocked evidence produces `blocked_input`. No case is guessed or
converted into uncertainty.

## Output boundary

A `BoundedInstinctSignalRecord` is internal, structured, revocable, scoped to
one evaluation bundle, and unconsumed by production runtime. It has no
authority to:

- create, extend, or replace purpose;
- order candidates or select an action;
- create a motor or direct command;
- write memory or mutate self-state;
- extend, reopen, focus, or stop perception;
- create output or external control.

Hard safety, teacher authority, existing approved purpose scope, the Package
132 perception closure, and the Package 140 self-state/drive closure remain
higher authorities.

## Runtime evidence

The guided run first verifies the actual external Package 132 and Package 140
milestone audits in query-only mode. It then executes the real Package 141 rule
runtime over controlled, typed Package 128 checkpoint conditions for closed,
open, neutral, conflict, and missing evidence. This run does not claim a new
sensor capture and does not reopen the frozen perception line.

The evidence store is external and append-only:

`package_141_instinct_layer_runtime_v0/package_141.sqlite3`

Operator events use the existing Package 122B local operator stream and are
engineering records, not Qingyin output.

## Next boundary

Package 142 may add specialized bounded thought rules only after defining its
own typed rule family and an explicit consumer of Package 141 precursor
signals. It still needs rule-family scope, input and output allowlists,
cross-family conflict semantics, bounded lifetime, and counterfactual proof
that no purpose, action, memory, output, or higher-authority boundary changes.

Package 141 does not implement Package 142, a workspace, deliberation,
verification, output, or the complete Thought Engine.
