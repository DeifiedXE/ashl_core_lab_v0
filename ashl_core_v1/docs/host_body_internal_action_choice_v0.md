# Package 106 / Host Body Internal Action Choice v0

Package 106 defines internal-only Host Body action choice records.

It can create deterministic internal action candidates from read-only Host Body
trace history and Qingyin Home evidence, select one internal action, record an
internal result, and record read-only Home/teacher/status surface effects.

Allowed internal choices are:

- observe_again
- mark_event_interesting
- mark_uncertain
- request_teacher_review
- shift_internal_focus
- update_home_status
- pause_event_processing

These are not Task Engine selected_action, final_action, direct_command,
computer control commands, memory writes, learning approvals, first_output, or
live runtime behavior.
