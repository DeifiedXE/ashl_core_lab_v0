# Package 125 And 126 Capture Lifecycle Distinction v0

Status: Sealed by Package 126

| Property | Package 125 | Package 126 |
| --- | --- | --- |
| Parent state | Still active | Completed cleanly |
| Window identity | Same | New child window |
| Sensor sessions | Same active sessions | New capture sessions |
| Alignment lifecycle | Same origin | New child alignment session |
| Time operation | Extend shared deadline once | Record explicit external gap |
| Source operation | No reopen | Reopen the same approved sources |
| Plan and target | Preserved | Preserved |
| Prior artifacts | Continue current acquisition | Never replay or recompile |
| Maximum additional window | No new window | One child window |

Package 125 is the only path for a still-active observation window. Package 126
is blocked until the parent has finalized and flushed cleanly. Neither package
selects focus, interprets uncertainty, writes memory, produces output, or
controls an external host capability.
