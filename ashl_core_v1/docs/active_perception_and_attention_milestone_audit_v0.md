# Active Perception And Attention Milestone Audit v0

Package 132 is an audit-only closure package. It adds no sensor, primitive,
attention mode, internal action, memory authority, output path, self-state, or
D-Laplace runtime component.

Its passing status is:

`passed_active_perception_and_attention_milestone_audit_v0`

The closed-line status is:

`perception_capability_construction_line_frozen_after_package_132`

## Evidence rule

Package 132 does not infer completion from roadmap prose. It requires all of
the following:

- every Package 123-131 completion commit is an ancestor of the current source;
- the sealed Package 124 archive passes its existing full read-only verifier;
- the Package 123 real audit is read from the archive's source-state database;
- a fresh Package 124A audit record proves grounded temporal anchors, spans,
  continuity and the external-gap boundary;
- exact passing real audit records are read for Packages 125-131;
- Package 130 model, deletion, generation and memory-consumer records remain
  internally consistent;
- Package 131 binding and pair comparison still point to that exact Package
  130 model and audit;
- all supplied evidence trees have identical content manifests before and
  after the audit;
- twelve required cross-package lineage edges are present;
- eighteen invalid closure or authority mutations are rejected;
- targeted Package 132 tests, targeted Package 123-131 regressions, full v1
  discovery, compileall, and `git diff --check` have a fresh passing receipt.

Private absolute evidence paths are not persisted. The audit stores normalized
path fingerprints, content hashes, record identities and source references.

## Sealed capabilities

The authoritative contract records nine existing capabilities:

1. Real bounded multimodal perception.
2. Grounded temporal continuity.
3. One bounded extension of the same active observation window.
4. One fresh bounded `capture_again` or `listen_again` child observation.
5. One nonsemantic visual changed-grid focus shift for one child window.
6. Structural evidence-sufficiency stop for the current window.
7. Exact teacher-reviewed active-perception learning influence through the
   existing Package 112 advisory path and existing policy gates.
8. Teacher-reviewed anonymous low-level auditory event concept formation.
9. Fresh anonymous auditory predictive recognition using frozen structural
   tolerances.

Package 132 does not reinterpret these records as semantic understanding or
subjective experience.

## Closed action surface

The perception construction line ends with exactly these established action
kinds:

- `extend_observation_window`
- `capture_again`
- `listen_again`
- `shift_internal_perception_focus`
- `stop_observation`

Package 132 registers no action. Existing older Host Body internal record kinds
remain outside this Package 125-128 perception-lifecycle set and are not
reclassified by this milestone.

## Explicit absences

The closure contract keeps all of these absent:

- semantic sound or object identity;
- free, open-ended, or persistent attention;
- persistent autonomous observation or reacquisition loops;
- unbounded sensor runtime;
- Qingyin-authored output or external host control;
- Thought Engine;
- persistent self-state;
- automatic memory admission or teacher approval;
- Package 132 runtime behavior or action;
- Package 132A;
- DLM-1 Cost/Registry/Lineage runtime.

Package 130 remains read-only to Package 131 under the exact consumer scope
`package_131_auditory_prediction_only`. Package 132 does not broaden that scope
to Package 133 or any other consumer.

## Interface for Package 133+

Later packages may read existing source identity/privacy/deletion metadata,
low-level perception primitives, readable alignment and flush records,
grounded temporal sidecars, immutable observation histories, approved Package
129 provenance, Package 130/131 audit status, anonymous Package 131 comparison
history, and TraceEnvelope references.

Those interfaces provide no authority to open sensors, change deadlines,
select a perception action, admit memory, approve teacher review, assign
semantic identity, emit output, control the host, rewrite history, retain raw
audio/images, mutate the Package 130 model, or broaden its consumer scope.

Package 133 may build cross-session self-state under its own future contract.
It may not silently add another perception capability through these read-only
interfaces.

## CLI

The Package 132 store is external and append-only:

`<state-dir>/package_132_perception_attention_milestone_v0/package_132.sqlite3`

Typical sequence:

```powershell
py -3 -m ashl_core_v1.runtime.package_132_perception_attention_milestone_cli preflight `
  --ashl-root F:\Projects\ashl_core_lab_v0 `
  --state-dir <external-output> `
  --package-124-archive <sealed-package-124-archive> `
  --evidence-root <package-124a-root> `
  --evidence-root <package-125-root> `
  --evidence-root <package-126-root> `
  --evidence-root <package-127-root> `
  --evidence-root <package-128-root> `
  --evidence-root <package-129-root> `
  --evidence-root <package-130-131-root>

py -3 -m ashl_core_v1.runtime.package_132_perception_attention_milestone_cli run-regressions `
  --ashl-root F:\Projects\ashl_core_lab_v0 `
  --state-dir <external-output>

py -3 -m ashl_core_v1.runtime.package_132_perception_attention_milestone_cli audit `
  --ashl-root F:\Projects\ashl_core_lab_v0 `
  --state-dir <external-output> `
  --package-124-archive <sealed-package-124-archive> `
  --evidence-root <each-explicit-evidence-root>
```

`show-capabilities`, `show-boundaries`, `show-evidence`, `show-lineage`,
`show-audit`, and `verify-evidence-unchanged` inspect the sealed audit output.

## Route closure

Package 132 closes perception capability construction. There is no Package
132A. Package 133 is the next core package and begins persistent self-state
outside this line. DLM-1 is an independent post-132 migration lane that still
requires separate authorization and remains unimplemented here.
