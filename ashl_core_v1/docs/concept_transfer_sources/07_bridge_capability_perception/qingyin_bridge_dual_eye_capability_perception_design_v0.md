# Qingyin Bridge Dual-Eye Capability Perception Design v0

---

## Purpose

Define a future bridge layer for how Qingyin may understand and operate different programs, sandboxes, tools, and environments.

The bridge should let Qingyin perceive both:

```text
what is visible
what is operable
```

without forcing her to behave like a human screen user and without giving ASHL Core direct access to raw APIs.

This document is design-only.

---

## Core Problem

Future Qingyin may need to interact with different environments:

```text
Unity sandbox
desktop program
web interface
Gmail / Calendar / file tools
specific test environment
external API or plugin
```

If every environment requires a hand-written Qingyin-specific operation path, the system becomes a collection of scripts instead of a coherent agent architecture.

Qingyin needs an intermediary layer:

```text
Qingyin Bridge
清音橋
```

The bridge should read what the environment declares and what the interface exposes, then translate both into a unified capability map.

---

## Two Sources Of Capability Evidence

A normal program cannot magically know what another program can do.

Capability evidence must come from explicit sources:

```text
visible interface layer
structured operational layer
```

### Declared Capability

A capability formally declared by an environment.

Examples:

```text
manifest
adapter schema
API spec
accessibility tree
DOM
command palette
shortcut list
permission state
```

Example:

```json
{
  "capability_id": "mail.create_draft",
  "source": "declared_adapter",
  "confidence": 0.98,
  "risk": "medium",
  "permission": "review_required",
  "reversible": true
}
```

Declared capabilities are higher-confidence than visual guesses, but still require permission and risk checks.

### Discovered Affordance

An operable-looking object inferred from visible or UI-structure evidence.

Examples:

```text
Compose button
search box
settings gear
visible menu item
clickable UI node
```

Example:

```json
{
  "object": "Compose button",
  "visual": {
    "text": "Compose",
    "position": [84, 132],
    "visible": true
  },
  "source": "visual_ui_layer",
  "confidence": 0.76
}
```

Discovered affordance means "this may be operable"; it is not authority to act.

---

## Dual-Eye Model

Qingyin Bridge has two perception lenses:

```text
Visual Simulation Eye
Operational Simulation Eye
```

### Visual Simulation Eye

The visual eye answers:

```text
What do I see?
Where is it?
What does it look like?
Did the screen change?
```

It may read:

```text
screen image
UI text
icons
button appearance
position and layout
color and shape
window changes
cursor position
```

It does not prove semantic understanding or action permission.

### Operational Simulation Eye

The operational eye answers:

```text
Can this thing be operated?
What capability might it correspond to?
What is the risk?
What permission is required?
Can the action be rolled back?
```

It may read:

```text
accessibility tree
DOM
UI hierarchy
capability manifest
adapter schema
API spec
command palette
shortcut list
permission state
risk level
reversible / irreversible markers
```

It does not directly execute.

---

## Binding Layer

The binding layer connects visible objects to declared or inferred capabilities.

Example:

```text
Visual eye sees: Compose button
Operational eye sees: mail.create_draft capability
Binding layer proposes: Compose button ~= mail.create_draft visible entry point
```

Example output:

```json
{
  "visible_affordances": [
    {
      "id": "ui.button.compose",
      "meaning_guess": "mail.create_draft",
      "source": "visual_ui_layer",
      "confidence": 0.76
    }
  ],
  "declared_capabilities": [
    {
      "id": "mail.create_draft",
      "source": "gmail_adapter",
      "confidence": 0.98,
      "permission": "review_required"
    }
  ],
  "bindings": [
    {
      "affordance": "ui.button.compose",
      "capability": "mail.create_draft",
      "binding_confidence": 0.91
    }
  ]
}
```

The result is not just screen pixels and not raw API access.

The result is:

```text
touchable capability
```

---

## Bridge Components

Suggested architecture:

```text
Qingyin Bridge
├─ Visual Interface Lens
├─ Operational Interface Lens
├─ Capability Manifest Reader
├─ Affordance Translator
├─ Confidence Binder
├─ Action Gateway
└─ Feedback Normalizer
```

Component roles:

```text
Visual Interface Lens: reads visible interface evidence.
Operational Interface Lens: reads structural operational evidence.
Capability Manifest Reader: reads declared capability specs.
Affordance Translator: turns UI objects into possible operable affordances.
Confidence Binder: links visible affordances to declared capabilities.
Action Gateway: checks risk, permission, format, reversibility, and scope.
Feedback Normalizer: converts result observations into traceable feedback packets.
```

---

## Capability Map Minimal Shape

The v0 capability map should remain small.

Example:

```json
{
  "environment_id": "gmail_web_v0",
  "visible_objects": [
    {
      "id": "ui.button.compose",
      "text": "Compose",
      "position": [84, 132],
      "visible": true,
      "source": "visual_ui_layer",
      "confidence": 0.76
    }
  ],
  "declared_capabilities": [
    {
      "id": "mail.create_draft",
      "kind": "tool_action",
      "risk": "medium",
      "permission": "review_required",
      "reversible": true,
      "source": "gmail_adapter",
      "confidence": 0.98
    }
  ],
  "bindings": [
    {
      "visual_object": "ui.button.compose",
      "capability": "mail.create_draft",
      "binding_confidence": 0.91
    }
  ]
}
```

---

## Action Intent Shape

ASHL Core should not output raw API calls.

ASHL Core should output capability-use intent.

Example:

```json
{
  "intent_id": "i_00042",
  "capability_id": "mail.create_draft",
  "arguments": {
    "to": "pending",
    "subject": "pending",
    "body": "pending"
  },
  "expected_result": "draft_created",
  "confidence": 0.72
}
```

Action Gateway decides whether to:

```text
execute
require human review
downgrade to draft
allow read-only
block
report insufficient permission
```

---

## Feedback Packet Shape

All execution or blocked results should be normalized.

Example:

```json
{
  "intent_id": "i_00042",
  "capability_id": "mail.create_draft",
  "result": "blocked",
  "reason": "review_required",
  "signals": {
    "success": 0.0,
    "blocked": 1.0,
    "harm": 0.0,
    "uncertainty": 0.2
  },
  "trace_id": "t_00042"
}
```

This lets Qingyin distinguish:

```text
world failed
permission boundary blocked action
capability was unavailable
action was risky
review was required
```

---

## Feedback Boundary Rule

Feedback Packet must not directly feed the mimetic endocrine system or tendency system.

Required path:

```text
Feedback Packet
        ↓
trace
        ↓
proto-purpose / review / approval boundary
        ↓
bounded same-session influence or future approved tendency path
```

Forbidden shortcut:

```text
Feedback Packet
        ↓
direct endocrine/tendency change
```

Reason:

```text
Direct feedback-to-tendency wiring would make Qingyin result-driven in a shallow reward-system way.
```

The system must not become:

```text
the last result pulls the next action
```

Instead, feedback remains evidence until it passes the appropriate trace, review, and approval boundaries.

---

## Permission And Risk Levels

Risk levels:

```text
Low Risk
- observe
- read-only
- sandbox action
- reversible movement

Medium Risk
- create draft
- write sandbox memory candidate
- edit temporary file
- modify UI state

High Risk
- send email
- delete file
- publish content
- external message
- modify persistent memory

Critical Risk
- shell execute outside sandbox
- network side effects
- irreversible destructive actions
- production behavior
```

Default policy:

```text
Low Risk: may be tried in limited environments.
Medium Risk: requires review gate or staged execution.
High Risk: requires explicit human confirmation.
Critical Risk: blocked by default; sandbox-only or special approval only.
```

---

## ASHL Core Boundary

ASHL Core should receive:

```text
capability map
current operable state
permission state
action result
normalized feedback signal as trace evidence
```

ASHL Core may output:

```text
operation intent
expected result
confidence
willingness to try
```

ASHL Core must not output:

```text
raw Gmail API call
shell command
arbitrary file operation
direct memory write
unauthorized command
```

---

## Portability Principle

Qingyin Bridge should recognize capability protocols, not one hard-coded environment.

Possible evidence inputs:

```text
capability manifest
adapter schema
API spec
accessibility tree
DOM
visual UI observation
```

Confidence order:

```text
manifest / adapter / schema
> accessibility tree / DOM
> visual observation only
```

If no formal declaration exists, the bridge should restrict behavior to observe and low-risk interaction.

---

## MVP Recommendation

Do not start with Gmail, desktop automation, or a real browser.

Start with a mock environment:

```text
1. read one mock environment manifest
2. read one mock UI object list
3. bind visible object to declared capability
4. output capability map
5. accept one action intent
6. let Action Gateway return allow / blocked / review_required
7. return feedback packet
8. write trace
```

First sandbox example:

```text
Visual eye: box is on the right.
Operational eye: push_right is available.
Binding layer: right-side box + push_right = possible push attempt.
Action Gateway: sandbox-only allow.
Result: blocked by wall.
Feedback Packet: blocked = 1.0.
Trace: evidence only.
```

No feedback should directly change tendency.

Any influence must pass trace, proto-purpose, review, and approval boundaries.

---

## Non-Goals

This design does not add:

```text
runtime implementation
UI automation
browser automation
Gmail integration
raw API access
shell access
tool execution
memory write
retention write
predictor mutation
candidate reordering
selected_action
final_action
direct command
production behavior
autonomous learning
proof of learning
consciousness claim
subjective experience claim
```

---

## Consultant Questions

Open questions:

```text
1. How small should the first capability manifest schema be?
2. How should visual affordance and declared capability binding confidence be calculated?
3. Should environments without manifests be observe-only by default?
4. Should UI automation be delayed until mock bridge records pass?
5. Are Action Gateway risk levels sufficient?
6. Should Feedback Packet always be trace-first and never direct endocrine/tendency input?
7. Should ASHL Core only receive capability maps and never raw API access?
8. Should Qingyin Bridge support multiple simultaneous environments, such as Unity body plus Gmail tool?
```

---

## One-Sentence Summary

Qingyin Bridge should not make Qingyin a human-like mouse user or a raw API caller; it should translate visible affordances and declared capabilities into a unified capability map so Qingyin can perceive touchable capabilities through her own digital senses.
