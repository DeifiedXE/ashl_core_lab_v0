"""External nonsemantic spatial-change fixture for Package 127."""

from __future__ import annotations

from typing import Any

from ashl_core_v1.runtime.host_sensor_types import monotonic_ns, utc_now


class LocalGridFocusStimulusRuntime:
    """A fixed full-window fixture whose schedule is audit-only."""

    def __init__(
        self,
        *,
        experiment_run_id: str,
        client_width: int = 640,
        client_height: int = 360,
    ) -> None:
        self.experiment_run_id = experiment_run_id
        self.window_title = (
            "ASHL Package 127 Grid Focus "
            f"{experiment_run_id}"
        )
        self.client_width = int(client_width)
        self.client_height = int(client_height)
        self._root: Any | None = None
        self._canvas: Any | None = None
        self._started_ns: int | None = None
        self._finished_ns: int | None = None
        self._child_phase_started_ns: int | None = None
        self._stage = 0
        self._transitions: list[dict[str, Any]] = []

    def open(self) -> None:
        import tkinter as tk

        root = tk.Tk()
        root.title(self.window_title)
        root.resizable(False, False)
        root.geometry(
            f"{self.client_width}x{self.client_height}+80+80"
        )
        try:
            root.attributes("-topmost", True)
            root.lift()
            root.focus_force()
        except Exception:
            pass
        canvas = tk.Canvas(
            root,
            width=self.client_width,
            height=self.client_height,
            highlightthickness=0,
            bg="black",
        )
        canvas.pack(fill="both", expand=True)
        root.update_idletasks()
        root.update()
        self._root = root
        self._canvas = canvas

    def tick(self) -> None:
        if self._root is None or self._canvas is None:
            raise RuntimeError("focus stimulus window is not open")
        if self._started_ns is None:
            self._started_ns = monotonic_ns()
        elapsed_ms = (monotonic_ns() - self._started_ns) // 1_000_000
        if self._stage == 0 and elapsed_ms >= 400:
            self._draw_parent_changes()
            self._record_transition("parent_spatial_changes", elapsed_ms)
            self._stage = 1
        child_elapsed_ms = (
            (monotonic_ns() - self._child_phase_started_ns) // 1_000_000
            if self._child_phase_started_ns is not None
            else -1
        )
        if self._stage == 1 and child_elapsed_ms >= 600:
            self._draw_child_changes()
            self._record_transition(
                "child_spatial_changes",
                elapsed_ms,
            )
            self._stage = 2
        self._root.update_idletasks()
        self._root.update()

    def mark_finished(self) -> None:
        self._finished_ns = monotonic_ns()

    def begin_child_phase(self) -> None:
        if self._stage != 1:
            raise RuntimeError(
                "child fixture phase requires completed parent change"
            )
        if self._child_phase_started_ns is not None:
            raise RuntimeError("child fixture phase already started")
        self._child_phase_started_ns = monotonic_ns()

    def manifest(self) -> dict[str, Any]:
        if self._started_ns is None:
            raise RuntimeError("focus stimulus has not started")
        return {
            "schema_version": "ashl_package_127_external_focus_fixture_v0",
            "experiment_run_id": self.experiment_run_id,
            "created_at": utc_now(),
            "window_title": self.window_title,
            "client_width": self.client_width,
            "client_height": self.client_height,
            "started_monotonic_ns": self._started_ns,
            "finished_monotonic_ns": (
                self._finished_ns or monotonic_ns()
            ),
            "child_phase_started_monotonic_ns": (
                self._child_phase_started_ns
            ),
            "transitions": tuple(self._transitions),
            "consumed_by_perception_runtime": False,
        }

    def close(self) -> None:
        if self._root is not None:
            try:
                self._root.destroy()
            except Exception:
                pass
        self._root = None
        self._canvas = None

    def _draw_parent_changes(self) -> None:
        assert self._canvas is not None
        self._canvas.create_rectangle(
            160,
            90,
            239,
            134,
            fill="#ffffff",
            outline="#ffffff",
        )
        self._canvas.create_rectangle(
            400,
            180,
            479,
            224,
            fill="#707070",
            outline="#707070",
        )

    def _draw_child_changes(self) -> None:
        assert self._canvas is not None
        self._canvas.create_rectangle(
            160,
            90,
            239,
            134,
            fill="#000000",
            outline="#000000",
        )
        self._canvas.create_rectangle(
            400,
            180,
            479,
            224,
            fill="#606060",
            outline="#606060",
        )

    def _record_transition(self, stage: str, elapsed_ms: int) -> None:
        self._transitions.append(
            {
                "transition_index": len(self._transitions),
                "stage": stage,
                "elapsed_ms": int(elapsed_ms),
                "issued_monotonic_ns": monotonic_ns(),
                "consumed_by_perception_runtime": False,
            }
        )
