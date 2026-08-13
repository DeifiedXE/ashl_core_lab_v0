"""External visual fixture for the Package 129 real two-cycle run."""

from __future__ import annotations

from typing import Any

from ashl_core_v1.runtime.host_sensor_types import monotonic_ns, utc_now


class LocalActivePerceptionGrowthStimulusRuntime:
    """One fixed visual schedule that never enters runtime decisions."""

    def __init__(
        self,
        *,
        experiment_run_id: str,
        client_width: int = 128,
        client_height: int = 72,
    ) -> None:
        self.experiment_run_id = experiment_run_id
        self.window_title = (
            "ASHL Package 129 Active Perception " f"{experiment_run_id}"
        )
        self.client_width = int(client_width)
        self.client_height = int(client_height)
        self._root: Any | None = None
        self._canvas: Any | None = None
        self._started_ns: int | None = None
        self._finished_ns: int | None = None
        self._child_started_ns: int | None = None
        self._parent_phase_armed = False
        self._child_phase_armed = False
        self._parent_stage = 0
        self._child_stage = 0
        self._transitions: list[dict[str, Any]] = []

    def open(self) -> None:
        import tkinter as tk

        root = tk.Tk()
        root.title(self.window_title)
        root.resizable(False, False)
        root.geometry(f"{self.client_width}x{self.client_height}+80+80")
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
            raise RuntimeError("Package 129 fixture window is not open")
        now_ns = monotonic_ns()
        if self._parent_phase_armed:
            self._started_ns = now_ns
            self._parent_phase_armed = False
        elif self._started_ns is None:
            self._started_ns = now_ns
        parent_elapsed_ms = (now_ns - self._started_ns) // 1_000_000
        if self._parent_stage == 0 and parent_elapsed_ms >= 3_900:
            self._draw_parent_open()
            self._record("parent_late_visual_regions_open", now_ns)
            self._parent_stage = 1
        elif self._parent_stage == 1 and parent_elapsed_ms >= 5_400:
            self._draw_baseline()
            self._record("parent_late_visual_regions_closed", now_ns)
            self._parent_stage = 2

        if self._child_phase_armed:
            self._child_started_ns = now_ns
            self._child_phase_armed = False
        if self._child_started_ns is not None:
            child_elapsed_ms = (
                now_ns - self._child_started_ns
            ) // 1_000_000
            if self._child_stage == 0 and child_elapsed_ms >= 400:
                self._draw_child_open()
                self._record("child_focused_visual_region_open", now_ns)
                self._child_stage = 1
            elif self._child_stage == 1 and child_elapsed_ms >= 1_450:
                self._draw_baseline()
                self._record("child_focused_visual_region_closed", now_ns)
                self._child_stage = 2
        self._root.update_idletasks()
        self._root.update()

    def begin_child_phase(self) -> None:
        if self._parent_stage != 2:
            raise RuntimeError("child phase requires closed parent event")
        if self._child_started_ns is not None or self._child_phase_armed:
            raise RuntimeError("Package 129 child phase already started")
        self._child_phase_armed = True

    def begin_parent_phase(self) -> None:
        if self._child_started_ns is not None or self._child_phase_armed:
            raise RuntimeError("Package 129 parent phase already ended")
        self._started_ns = None
        self._parent_phase_armed = True
        self._parent_stage = 0

    def mark_finished(self) -> None:
        self._finished_ns = monotonic_ns()

    def manifest(self) -> dict[str, Any]:
        if self._started_ns is None:
            raise RuntimeError("Package 129 fixture has not started")
        return {
            "schema_version": "ashl_package_129_external_visual_fixture_v0",
            "experiment_run_id": self.experiment_run_id,
            "created_at": utc_now(),
            "window_title": self.window_title,
            "client_width": self.client_width,
            "client_height": self.client_height,
            "started_monotonic_ns": self._started_ns,
            "finished_monotonic_ns": self._finished_ns or monotonic_ns(),
            "child_started_monotonic_ns": self._child_started_ns,
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

    def _draw_baseline(self) -> None:
        assert self._canvas is not None
        self._canvas.delete("all")
        self._canvas.configure(bg="black")

    def _draw_parent_open(self) -> None:
        assert self._canvas is not None
        self._canvas.create_rectangle(
            24, 14, 63, 35, fill="#ffffff", outline="#ffffff"
        )
        self._canvas.create_rectangle(
            86, 40, 105, 50, fill="#686868", outline="#686868"
        )

    def _draw_child_open(self) -> None:
        assert self._canvas is not None
        self._canvas.create_rectangle(
            24, 14, 63, 35, fill="#ffffff", outline="#ffffff"
        )
        self._canvas.create_rectangle(
            86, 40, 99, 47, fill="#303030", outline="#303030"
        )

    def _record(self, stage: str, issued_ns: int) -> None:
        self._transitions.append(
            {
                "transition_index": len(self._transitions),
                "stage": stage,
                "issued_monotonic_ns": int(issued_ns),
                "consumed_by_perception_runtime": False,
            }
        )
