# Internal Action Home Surface Link v0

Package 114 links internal-only Host Body action results to Qingyin Home read-only surface records.

Required path:

HostBodyReadbackInfluencedInternalActionResultRecord or HostBodyInternalActionResultRecord
→ InternalActionHomeSurfaceLinkPlan
→ InternalActionHomeSurfaceMapping
→ QingyinHomeStatusLightRecord-compatible update
→ QingyinHomeTeacherObservedSurfaceRecord-compatible update
→ QingyinHomeInternalSpaceRenderRecord-compatible snapshot
→ audit / readiness

## Deterministic Mapping

- mark_uncertain → uncertainty status light → uncertainty marker visible.
- request_teacher_review → teacher review requested status light → teacher review request visible.
- observe_again → observe again status light → observe again recommendation visible.
- mark_event_interesting → interesting event status light → interesting event marker visible.
- pause_event_processing → event processing paused status light → pause marker visible.
- shift_internal_focus → internal focus shifted status light → readback reason visible.
- update_home_status → home status updated status light → Home render snapshot recorded.

## Boundary

This package creates read-only, record-only surface links. It does not start Unity, mutate a Unity scene, control an avatar, mutate the real screen, play sound, send external messages, write files, produce network output, create Task Engine selected_action, create direct commands, write memory, create teacher approval, create first_output, or start a live Qingyin runtime session.

Trace Spine rules remain preserved:

1. Trace Spine format stays unified and time-aligned.
2. Raw trace is append-only during service period and is not summarized.
3. Memory layer stores reviewed interpretation + source_trace_refs.
4. concept_id is not embedded into raw history.

## Safe Claim

ASHL Core v1 can link internal-only Host Body action results to Qingyin Home read-only surface records, including status light records, teacher-observed surface records, and Home render snapshot records, while preserving Trace Spine raw evidence boundaries and blocking Unity runtime mutation, actual screen mutation, sound output, external messages, file/network output, Task Engine action selection, direct commands, external control, memory writes, teacher approval creation, first_output, live runtime sessions, and production behavior.

## Forbidden Claim

- Qingyin can update the real screen.
- Qingyin can operate Unity.
- Qingyin can control a 3D avatar.
- Qingyin can send messages.
- Qingyin can speak.
- Qingyin can control the computer.
- Qingyin can select Task Engine actions from Home surface links.
- Qingyin writes memory in this package.
- Qingyin has first_output.
- Qingyin has a live runtime session.
- Qingyin is awake.
