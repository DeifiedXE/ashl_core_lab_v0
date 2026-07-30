from __future__ import annotations

import math
import re
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from ashl_core_v1.host_body import (
    host_body_readback_internal_action_influence,
    internal_action_home_surface_link,
)
from ashl_core_v1.host_body.host_body_internal_action_choice import (
    ALLOWED_INTERNAL_ACTION_KINDS,
)
from ashl_core_v1.runtime.bounded_multimodal_perception_session_runtime import (
    BoundedMultimodalPerceptionSessionRuntime,
)
from ashl_core_v1.runtime.focused_visual_region_view import (
    build_focus_context_sidecar,
    build_focus_release_record,
    build_focused_visual_region_view,
)
from ashl_core_v1.runtime.host_sensor_types import stable_id, utc_now
from ashl_core_v1.runtime.internal_perception_focus_action import (
    create_internal_perception_focus_shift_action,
)
from ashl_core_v1.runtime.internal_perception_focus_candidate import (
    create_focus_candidates,
    select_focus_candidate,
)
from ashl_core_v1.runtime.internal_perception_focus_policy import (
    create_focus_authorization,
    create_focus_plan,
    decide_focus_policy,
)
from ashl_core_v1.runtime.internal_perception_focus_types import (
    BASELINE_COMMIT,
    FOCUS_ACTION_KIND,
    MAXIMUM_FOCUS_CANDIDATES,
)
from ashl_core_v1.runtime.local_operator_console_store import (
    build_default_console_store,
)
from ashl_core_v1.runtime.local_operator_event_stream import (
    LocalOperatorEventStream,
)
from ashl_core_v1.runtime.package_127_internal_focus_audit import (
    audit_package_127_internal_focus,
)
from ashl_core_v1.runtime.package_127_internal_focus_cli import build_parser
from ashl_core_v1.runtime.package_127_internal_focus_runtime import (
    PACKAGE_127_EVENT_KINDS,
    _emit_focus_event,
    _synthetic_change,
    _synthetic_frame,
    _synthetic_parent,
    _synthetic_view,
    run_synthetic_package_127_controls,
    run_synthetic_package_127_smoke,
)
from ashl_core_v1.runtime.package_127_internal_focus_store import (
    Package127InternalFocusStore,
)


class Package127CandidateAndSelectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.parent = _synthetic_parent()
        self.frame = _synthetic_frame()
        self.change = _synthetic_change()

    def candidates(self, change=None):
        return create_focus_candidates(
            parent=self.parent,
            visual_change=change or self.change,
            current_visual_frame=self.frame,
        )

    def test_baseline_and_exact_action_registration(self) -> None:
        self.assertEqual(
            BASELINE_COMMIT,
            "65b3f4fd5ee73011d8fe8be061b8aa3b78079d43",
        )
        self.assertIn(FOCUS_ACTION_KIND, ALLOWED_INTERNAL_ACTION_KINDS)
        self.assertEqual(
            tuple(
                item
                for item in ALLOWED_INTERNAL_ACTION_KINDS
                if item == FOCUS_ACTION_KIND
            ),
            (FOCUS_ACTION_KIND,),
        )

    def test_actual_changed_cells_create_nonsemantic_candidates(self) -> None:
        batch, candidates = self.candidates()
        self.assertEqual(batch.candidate_count, 2)
        self.assertEqual(len(candidates), 2)
        for candidate in candidates:
            self.assertIsNone(candidate.semantic_label)
            self.assertIsNone(candidate.object_identity)
            self.assertIsNone(candidate.object_class)
            self.assertFalse(candidate.memory_used)
            self.assertFalse(candidate.novelty_signal_used)
            self.assertFalse(candidate.uncertainty_signal_used)
            self.assertEqual(
                candidate.reason_codes,
                ("changed_grid_cell_present",),
            )

    def test_stable_frame_creates_no_candidate(self) -> None:
        change = dict(self.change)
        change["changed_grid_cells"] = tuple()
        batch, candidates = self.candidates(change)
        selection = select_focus_candidate(
            parent_observation_window_id=(
                self.parent.observation_window_id
            ),
            candidates=candidates,
        )
        self.assertTrue(batch.stable_frame)
        self.assertEqual(batch.candidate_count, 0)
        self.assertEqual(selection.selection_status, "no_candidate")

    def test_floor_filters_without_calling_cells_unimportant(self) -> None:
        change = dict(self.change)
        change["changed_grid_cells"] = (
            {"grid_x": 1, "grid_y": 1, "difference_strength": 0.07},
        )
        batch, candidates = self.candidates(change)
        self.assertEqual(candidates, tuple())
        self.assertFalse(batch.stable_frame)
        self.assertEqual(batch.changed_grid_cell_count, 1)

    def test_nonfinite_difference_rejected(self) -> None:
        for value in (math.nan, math.inf, -math.inf):
            change = dict(self.change)
            change["changed_grid_cells"] = (
                {
                    "grid_x": 1,
                    "grid_y": 1,
                    "difference_strength": value,
                },
            )
            with self.assertRaises(ValueError):
                self.candidates(change)

    def test_invalid_coordinate_rejected(self) -> None:
        for x, y in ((-1, 0), (0, -1), (8, 0), (0, 8)):
            change = dict(self.change)
            change["changed_grid_cells"] = (
                {
                    "grid_x": x,
                    "grid_y": y,
                    "difference_strength": 0.8,
                },
            )
            with self.assertRaises(ValueError):
                self.candidates(change)

    def test_source_lineage_required(self) -> None:
        change = dict(self.change)
        change["current_visual_primitive_id"] = "other-frame"
        with self.assertRaisesRegex(ValueError, "lineage"):
            self.candidates(change)

    def test_candidate_limit_and_omitted_count(self) -> None:
        change = dict(self.change)
        change["changed_grid_cells"] = tuple(
            {
                "grid_x": index % 8,
                "grid_y": index // 8,
                "difference_strength": 1.0 - index / 100,
            }
            for index in range(32)
        )
        batch, candidates = self.candidates(change)
        self.assertEqual(len(candidates), MAXIMUM_FOCUS_CANDIDATES)
        self.assertEqual(batch.omitted_candidate_count, 16)
        self.assertEqual(candidates[0].grid_x, 0)
        self.assertEqual(candidates[0].grid_y, 0)

    def test_highest_difference_selected(self) -> None:
        _, candidates = self.candidates()
        selection = select_focus_candidate(
            parent_observation_window_id=(
                self.parent.observation_window_id
            ),
            candidates=candidates,
        )
        self.assertEqual(selection.selection_status, "selected")
        self.assertEqual(
            selection.selected_difference_strength,
            max(item.difference_strength for item in candidates),
        )
        self.assertTrue(selection.candidate_set_preserved)

    def test_tie_breaks_grid_y_then_grid_x_deterministically(self) -> None:
        change = dict(self.change)
        change["changed_grid_cells"] = (
            {"grid_x": 5, "grid_y": 3, "difference_strength": 0.8},
            {"grid_x": 6, "grid_y": 1, "difference_strength": 0.8},
            {"grid_x": 2, "grid_y": 1, "difference_strength": 0.8},
        )
        _, candidates = self.candidates(change)
        selected = tuple(
            select_focus_candidate(
                parent_observation_window_id=(
                    self.parent.observation_window_id
                ),
                candidates=candidates,
            )
            for _ in range(3)
        )
        self.assertEqual(
            {
                (item.selected_grid_x, item.selected_grid_y)
                for item in selected
            },
            {(2, 1)},
        )
        self.assertTrue(
            all(item.deterministic_tie_break_used for item in selected)
        )

    def test_wrong_parent_candidate_blocks_selection(self) -> None:
        _, candidates = self.candidates()
        wrong = replace(
            candidates[0],
            parent_observation_window_id="window:other",
        )
        selection = select_focus_candidate(
            parent_observation_window_id=(
                self.parent.observation_window_id
            ),
            candidates=(wrong,),
        )
        self.assertEqual(selection.selection_status, "blocked")

    def test_semantic_injection_rejected(self) -> None:
        _, candidates = self.candidates()
        for field in ("semantic_label", "object_identity", "object_class"):
            with self.assertRaises(ValueError):
                replace(candidates[0], **{field: "injected"})


class Package127PolicyActionAndViewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.parent = _synthetic_parent()
        _, candidates = create_focus_candidates(
            parent=self.parent,
            visual_change=_synthetic_change(),
            current_visual_frame=_synthetic_frame(),
        )
        self.candidates = candidates
        self.selection = select_focus_candidate(
            parent_observation_window_id=(
                self.parent.observation_window_id
            ),
            candidates=candidates,
        )
        self.selected = next(
            item
            for item in candidates
            if item.focus_candidate_id
            == self.selection.selected_candidate_id
        )
        self.authorization = create_focus_authorization(
            parent=self.parent
        )

    def decide(self, **kwargs):
        return decide_focus_policy(
            selection=kwargs.pop("selection", self.selection),
            candidate=kwargs.pop("candidate", self.selected),
            parent=kwargs.pop("parent", self.parent),
            authorization=kwargs.pop(
                "authorization",
                self.authorization,
            ),
            **kwargs,
        )

    def test_explicit_authorization_does_not_choose_region(self) -> None:
        self.assertEqual(
            self.authorization.authorization_source,
            "explicit_session_configuration",
        )
        self.assertEqual(
            self.authorization.maximum_focus_shift_count,
            1,
        )
        self.assertFalse(
            hasattr(self.authorization, "selected_candidate_id")
        )

    def test_valid_policy_allows(self) -> None:
        decision = self.decide()
        self.assertEqual(decision.decision, "allow")
        self.assertTrue(decision.transport_integrity_valid)

    def test_missing_and_expired_authorization_block(self) -> None:
        self.assertEqual(
            self.decide(authorization=None).decision,
            "block",
        )
        self.assertEqual(
            self.decide(authorization_expired=True).decision,
            "expired",
        )

    def test_authorization_bound_to_parent_chain(self) -> None:
        other = replace(
            self.authorization,
            parent_observation_window_id="window:other",
        )
        result = self.decide(authorization=other)
        self.assertEqual(result.decision, "block")
        self.assertFalse(result.authorization_valid)

    def test_second_shift_and_operator_stop_block(self) -> None:
        second = self.decide(prior_focus_shift_count=1)
        stopped = self.decide(operator_stop_requested=True)
        self.assertEqual(second.decision, "block")
        self.assertFalse(second.focus_budget_available)
        self.assertEqual(stopped.decision, "block")
        self.assertFalse(stopped.operator_stop_absent)

    def test_transport_failure_and_wrong_session_block(self) -> None:
        fault_parent = replace(
            self.parent,
            compile_failure_count=1,
        )
        fault = self.decide(parent=fault_parent)
        wrong_candidate = replace(
            self.selected,
            parent_perception_session_id="perception:other",
        )
        wrong_selection = replace(
            self.selection,
            candidate_ids=(wrong_candidate.focus_candidate_id,),
            selected_candidate_id=wrong_candidate.focus_candidate_id,
            source_record_refs=(wrong_candidate.focus_candidate_id,),
        )
        wrong = self.decide(
            selection=wrong_selection,
            candidate=wrong_candidate,
        )
        self.assertFalse(fault.transport_integrity_valid)
        self.assertFalse(wrong.source_lineage_valid)

    def test_focus_plan_bounds_derive_from_grid(self) -> None:
        plan = create_focus_plan(
            decision=self.decide(),
            candidate=self.selected,
        )
        self.assertIsNotNone(plan)
        assert plan is not None
        self.assertEqual(
            plan.normalized_left,
            self.selected.grid_x / self.selected.source_grid_width,
        )
        self.assertFalse(plan.raw_capture_region_changed)
        self.assertFalse(plan.raw_capture_target_changed)
        self.assertTrue(plan.full_frame_capture_preserved)

    def test_action_is_internal_only_and_not_readback_or_home_sourced(self) -> None:
        plan = create_focus_plan(
            decision=self.decide(),
            candidate=self.selected,
        )
        assert plan is not None
        action = create_internal_perception_focus_shift_action(plan=plan)
        self.assertTrue(action.internal_only)
        self.assertFalse(action.external_side_effect)
        self.assertFalse(action.selected_action_created)
        self.assertFalse(action.final_action_created)
        self.assertFalse(action.direct_command_created)
        self.assertNotIn(
            FOCUS_ACTION_KIND,
            host_body_readback_internal_action_influence.ALLOWED_INTERNAL_ACTION_KINDS,
        )
        self.assertNotIn(
            FOCUS_ACTION_KIND,
            internal_action_home_surface_link.ALLOWED_INTERNAL_ACTION_KINDS,
        )

    def test_view_indexes_primitive_grid_without_raw_crop(self) -> None:
        plan = create_focus_plan(
            decision=self.decide(),
            candidate=self.selected,
        )
        assert plan is not None
        view = _synthetic_view(plan)
        self.assertEqual(view.grid_x, plan.grid_x)
        self.assertEqual(view.grid_y, plan.grid_y)
        self.assertFalse(view.raw_pixel_payload_present)
        self.assertFalse(view.image_crop_persisted)
        self.assertTrue(view.read_only_context)
        self.assertFalse(view.memory_write_authority)
        self.assertFalse(view.scoring_authority)
        self.assertFalse(view.output_authority)

    def test_raw_crop_and_semantic_view_are_rejected(self) -> None:
        plan = create_focus_plan(
            decision=self.decide(),
            candidate=self.selected,
        )
        assert plan is not None
        view = _synthetic_view(plan)
        with self.assertRaises(ValueError):
            replace(view, image_crop_persisted=True)
        with self.assertRaises(ValueError):
            replace(view, raw_pixel_payload_present=True)
        with self.assertRaises(ValueError):
            replace(view, semantic_label="thing")

    def test_full_frame_sidecar_attaches_to_package_122_lineage(self) -> None:
        plan = create_focus_plan(
            decision=self.decide(),
            candidate=self.selected,
        )
        assert plan is not None
        view = _synthetic_view(plan)
        sidecar = build_focus_context_sidecar(
            plan=plan,
            view=view,
            full_frame_perception_readable_data_id="readable:child",
            active_from_event_time_ns=10,
            active_until_event_time_ns=20,
        )
        with tempfile.TemporaryDirectory() as tmp:
            runtime = BoundedMultimodalPerceptionSessionRuntime(tmp)
            runtime.store.append_payload(
                "perception_lane_items",
                "lane_item_id",
                "lane:screen",
                {
                    "lane_item_id": "lane:screen",
                    "created_at": utc_now(),
                    "session_id": "perception:child",
                    "source_kind": "screen",
                    "perception_readable_data_id": "readable:child",
                },
            )
            payload = runtime.attach_internal_perception_focus_context(
                sidecar
            )
            self.assertEqual(
                payload["full_frame_perception_readable_data_id"],
                "readable:child",
            )
            self.assertEqual(
                len(
                    runtime.store.list_payloads(
                        "internal_perception_focus_context_sidecars"
                    )
                ),
                1,
            )

    def test_sidecar_rejects_wrong_full_frame_lineage(self) -> None:
        plan = create_focus_plan(
            decision=self.decide(),
            candidate=self.selected,
        )
        assert plan is not None
        view = _synthetic_view(plan)
        sidecar = build_focus_context_sidecar(
            plan=plan,
            view=view,
            full_frame_perception_readable_data_id="wrong",
            active_from_event_time_ns=10,
            active_until_event_time_ns=20,
        )
        with tempfile.TemporaryDirectory() as tmp:
            runtime = BoundedMultimodalPerceptionSessionRuntime(tmp)
            with self.assertRaisesRegex(ValueError, "lineage"):
                runtime.attach_internal_perception_focus_context(sidecar)

    def test_focus_release_is_append_only_one_child(self) -> None:
        plan = create_focus_plan(
            decision=self.decide(),
            candidate=self.selected,
        )
        assert plan is not None
        view = _synthetic_view(plan)
        sidecar = build_focus_context_sidecar(
            plan=plan,
            view=view,
            full_frame_perception_readable_data_id="readable:child",
            active_from_event_time_ns=10,
            active_until_event_time_ns=20,
        )
        release = build_focus_release_record(sidecar=sidecar)
        self.assertEqual(sidecar.focus_state, "released")
        self.assertTrue(sidecar.automatically_released)
        self.assertEqual(release.child_window_count, 1)
        self.assertTrue(release.history_preserved)

    def test_interrupted_focus_is_preserved_then_released(self) -> None:
        plan = create_focus_plan(
            decision=self.decide(),
            candidate=self.selected,
        )
        assert plan is not None
        view = _synthetic_view(plan)
        sidecar = build_focus_context_sidecar(
            plan=plan,
            view=view,
            full_frame_perception_readable_data_id="readable:child",
            active_from_event_time_ns=10,
            active_until_event_time_ns=15,
            focus_state="interrupted",
        )
        release = build_focus_release_record(
            sidecar=sidecar,
            interrupted=True,
        )
        self.assertEqual(sidecar.focus_state, "interrupted")
        self.assertFalse(sidecar.automatically_released)
        self.assertEqual(release.previous_focus_state, "interrupted")
        self.assertEqual(release.new_focus_state, "released")
        self.assertTrue(release.history_preserved)


class Package127StoreEventCliAndBoundaryTests(unittest.TestCase):
    def test_store_is_external_append_only_and_schema_complete(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = Package127InternalFocusStore(tmp)
            self.assertTrue(store.validate_schema()["valid"])
            self.assertTrue(str(store.db_path).startswith(tmp))
            payload = {
                "control_result_id": "same-id",
                "created_at": utc_now(),
            }
            store.append_payload(
                "package_127_control_results",
                "control_result_id",
                "same-id",
                payload,
            )
            with self.assertRaises(Exception):
                store.append_payload(
                    "package_127_control_results",
                    "control_result_id",
                    "same-id",
                    payload,
                )

    def test_all_event_kinds_require_and_accept_identities(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            stream = LocalOperatorEventStream(
                build_default_console_store(tmp)
            )
            for event_kind in PACKAGE_127_EVENT_KINDS:
                event = stream.append_event(
                    event_kind=event_kind,
                    runtime_session_id="runtime",
                    perception_session_id="perception",
                    observation_window_id="window",
                    source_record_refs=("record",),
                )
                self.assertFalse(event.llm_used)
                self.assertFalse(event.codex_used)
                self.assertFalse(event.network_used)
            with self.assertRaises(ValueError):
                stream.append_event(
                    event_kind="internal_focus_selected"
                )

    def test_event_delivery_failure_is_visible_and_strict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = Package127InternalFocusStore(tmp)
            with patch.object(
                LocalOperatorEventStream,
                "append_event",
                side_effect=RuntimeError("delivery fault"),
            ):
                self.assertFalse(
                    _emit_focus_event(
                        Path(tmp),
                        store=store,
                        event_kind="internal_focus_selected",
                        runtime_session_id="runtime",
                        perception_session_id="perception",
                        observation_window_id="window",
                        refs=("selection",),
                        strict=False,
                    )
                )
                with self.assertRaises(RuntimeError):
                    _emit_focus_event(
                        Path(tmp),
                        store=store,
                        event_kind="internal_focus_selected",
                        runtime_session_id="runtime",
                        perception_session_id="perception",
                        observation_window_id="window",
                        refs=("selection",),
                        strict=True,
                    )
            self.assertEqual(
                len(
                    store.list_payloads(
                        "operator_event_delivery_failures"
                    )
                ),
                2,
            )

    def test_synthetic_smoke_all_controls_and_no_runtime_effects(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_synthetic_package_127_smoke(state_dir=tmp)
            self.assertTrue(all(result["controls"].values()))
            self.assertFalse(result["sensor_opened"])
            self.assertFalse(result["raw_crop_created"])
            self.assertFalse(result["semantic_vision_created"])
            self.assertFalse(result["memory_write_created"])
            self.assertFalse(result["output_created"])
            self.assertFalse(result["external_control_created"])

    def test_control_record_contains_all_ten_controls(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            controls = run_synthetic_package_127_controls(
                state_dir=tmp
            )
            self.assertEqual(len(controls), 10)
            self.assertTrue(all(controls.values()))

    def test_cli_exposes_required_commands(self) -> None:
        parser = build_parser()
        commands = (
            "synthetic-smoke",
            "run-real-focus-shift",
            "show-candidates",
            "show-selection",
            "show-focus-context",
            "cancel-pending-focus",
            "stop-focused-child",
            "audit",
        )
        for command in commands:
            args = [command, "--state-dir", "state"]
            if command == "run-real-focus-shift":
                args.append("--allow-internal-focus-shift")
            parsed = parser.parse_args(args)
            self.assertEqual(parsed.command, command)

    def test_audit_blocks_without_real_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_synthetic_package_127_controls(state_dir=tmp)
            audit = audit_package_127_internal_focus(
                state_dir=tmp,
                append=True,
            )
            self.assertEqual(
                audit.audit_status,
                "blocked_internal_perception_focus_shift_v0",
            )
            self.assertIn(
                "real_parent_capture_not_verified",
                audit.failure_reasons,
            )

    def test_runtime_has_no_future_or_d_laplace_import(self) -> None:
        runtime = Path(__file__).parents[1] / "runtime"
        files = (
            "internal_perception_focus_types.py",
            "internal_perception_focus_candidate.py",
            "internal_perception_focus_policy.py",
            "internal_perception_focus_action.py",
            "focused_visual_region_view.py",
            "package_127_internal_focus_store.py",
            "package_127_internal_focus_runtime.py",
            "package_127_internal_focus_audit.py",
        )
        text = "\n".join(
            (runtime / name).read_text(encoding="utf-8")
            for name in files
        )
        self.assertIsNone(
            re.search(
                r"^\s*(?:from|import)\s+.*(?:d_laplace|package_128|package_129)",
                text,
                flags=re.IGNORECASE | re.MULTILINE,
            )
        )
        self.assertNotIn("ACTION_BID", text)

    def test_no_repository_data_or_raw_crop_store(self) -> None:
        runtime = Path(__file__).parents[1] / "runtime"
        store_text = (
            runtime / "package_127_internal_focus_store.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("ashl_core_v1/data", store_text)
        self.assertNotIn("raw_image", store_text)
        self.assertNotIn("image_crop", store_text)


if __name__ == "__main__":
    unittest.main()
