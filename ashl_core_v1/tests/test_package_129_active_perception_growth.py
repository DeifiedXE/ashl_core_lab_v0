from __future__ import annotations

import contextlib
import io
import os
import shutil
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from ashl_core_v1.host_body.host_body_internal_action_choice import (
    ALLOWED_INTERNAL_ACTION_KINDS,
)
from ashl_core_v1.migration_audit import (
    D_LAPLACE_QM0_AUDIT_STATUS,
    QINGYIN_MIGRATION_STATUS,
)
from ashl_core_v1.runtime.active_perception_growth_types import (
    BASELINE_COMMIT,
    EXPERIMENT_ID,
    PASS_STATUS,
    STAGE_ACTION_KINDS,
    STAGE_KINDS,
    ActivePerceptionReadbackInfluenceRecord,
    ActivePerceptionStageRecord,
)
from ashl_core_v1.runtime.active_perception_readback_influence import (
    reject_stimulus_matching_provenance,
    score_extension_candidate_with_working_readback,
    validate_readback_loaded_before_candidate,
)
from ashl_core_v1.runtime.internal_perception_focus_types import (
    PACKAGE_127_PASS_STATUS,
)
from ashl_core_v1.runtime.local_operator_console_store import (
    build_default_console_store,
)
from ashl_core_v1.runtime.observation_window_types import (
    PACKAGE_125_PASS_STATUS,
)
from ashl_core_v1.runtime.package_125_observation_extension_store import (
    Package125ObservationExtensionStore,
)
from ashl_core_v1.runtime.package_126_reacquisition_store import (
    Package126ReacquisitionStore,
)
from ashl_core_v1.runtime.package_129_active_perception_growth_audit import (
    audit_package_129_active_perception_growth,
)
from ashl_core_v1.runtime.package_129_active_perception_growth_cli import (
    _run_cycle_worker,
    main as package_129_cli_main,
)
from ashl_core_v1.runtime.package_129_active_perception_growth_preflight import (
    run_package_129_preflight,
)
from ashl_core_v1.runtime.package_129_active_perception_growth_runtime import (
    PARTICIPATING_LANES,
    TEACHER_INTERPRETATION,
    _artifact_sets_distinct,
    _four_stage_lineage_complete,
    _processes_distinct,
    review_cycle_one,
)
from ashl_core_v1.runtime.package_129_active_perception_growth_store import (
    Package129ActivePerceptionGrowthStore,
)
from ashl_core_v1.runtime.perception_reacquisition_types import (
    PACKAGE_126_PASS_STATUS,
)
from ashl_core_v1.runtime.session_learning_evidence_identity import (
    FULL_COMMIT_APPROVAL_SCOPE,
    validate_canonical_evidence_context,
)
from ashl_core_v1.runtime.structural_evidence_sufficiency_types import (
    PACKAGE_128_PASS_STATUS,
)
from ashl_core_v1.runtime.teacher_gated_session_store import (
    TeacherGatedSessionStore,
)


class Package129UnitTests(unittest.TestCase):
    def test_baseline_and_predecessor_statuses_are_locked(self) -> None:
        self.assertEqual(
            BASELINE_COMMIT,
            "6feaf9c5122adb63c10616f4acfaa1f93c2b6b62",
        )
        self.assertEqual(
            PACKAGE_128_PASS_STATUS,
            "passed_structural_evidence_sufficiency_and_observation_stop_policy_v0",
        )
        self.assertEqual(
            PACKAGE_127_PASS_STATUS,
            "passed_internal_perception_focus_shift_v0",
        )
        self.assertEqual(
            PACKAGE_126_PASS_STATUS,
            "passed_bounded_re_sampling_and_listen_again_internal_action_v0",
        )
        self.assertEqual(
            PACKAGE_125_PASS_STATUS,
            "passed_bounded_observation_window_extension_internal_action_v0",
        )
        self.assertEqual(
            D_LAPLACE_QM0_AUDIT_STATUS,
            "passed_d_laplace_qm0_read_only_migration_audit_v0",
        )
        self.assertEqual(
            QINGYIN_MIGRATION_STATUS,
            "QINGYIN_MIGRATION_INCOMPLETE_AUDIT_LAYER",
        )

    def test_no_fifth_action_or_new_sensor_lane_is_added(self) -> None:
        self.assertEqual(
            tuple(STAGE_ACTION_KINDS[item] for item in STAGE_KINDS),
            (
                "extend_observation_window",
                "shift_internal_perception_focus",
                "capture_again",
                "stop_observation",
            ),
        )
        self.assertEqual(PARTICIPATING_LANES, ("screen", "host_state"))
        self.assertTrue(
            set(STAGE_ACTION_KINDS.values()).issubset(
                ALLOWED_INTERNAL_ACTION_KINDS
            )
        )
        self.assertNotIn("active_perception_growth", ALLOWED_INTERNAL_ACTION_KINDS)

    def test_stage_is_semantic_free_and_requires_actual_lineage(self) -> None:
        stage = ActivePerceptionStageRecord(
            stage_record_id="stage:1",
            schema_version="ashl_package_129_active_perception_stage_v0",
            created_at="2026-01-01T00:00:00+00:00",
            cycle_index=1,
            stage_index=1,
            stage_kind="late_event_extension",
            runtime_session_id="runtime:1",
            perception_session_id="perception:1",
            observation_window_id="window:1",
            source_evidence_refs=("evidence:1",),
            policy_decision_refs=("policy:1",),
            internal_action_kind="extend_observation_window",
            internal_action_id="action:1",
            execution_record_id="execution:1",
            stage_status="completed",
            required_lane_drop_count=0,
            backpressure_fault_count=0,
            capture_failure_count=0,
            compile_failure_count=0,
            flush_remaining_count=0,
            semantic_label=None,
            source_record_refs=("action:1", "execution:1"),
            source_trace_refs=("trace:1",),
        )
        with self.assertRaises(ValueError):
            replace(stage, semantic_label="important region")
        with self.assertRaises(ValueError):
            replace(stage, internal_action_id=None)
        with self.assertRaises(ValueError):
            replace(stage, internal_action_kind="capture_again")

    def test_package_112_readback_match_is_structural_and_advisory(self) -> None:
        candidate = {
            "extension_candidate_id": "extension_candidate:test",
            "source_trace_refs": ("trace:candidate",),
        }
        readback = {
            "evidence_theme": "active_perception_sequence_observed",
            "source_evidence_snapshot_id": "snapshot:approved",
            "evidence_identity_sha256": "a" * 64,
            "working_readback_commit_id": "working_readback:test",
            "source_trace_refs": ("trace:readback",),
            "reviewed_interpretation": "bounded structural sequence",
            "scope": "low_level_active_perception_sequence_only",
            "counterexample_boundary": tuple(),
        }
        empty = score_extension_candidate_with_working_readback(
            extension_candidate=candidate,
            working_readback_items=tuple(),
            expected_evidence_snapshot_id="snapshot:approved",
            expected_evidence_identity_sha256="a" * 64,
        )
        matched = score_extension_candidate_with_working_readback(
            extension_candidate=candidate,
            working_readback_items=(readback,),
            expected_evidence_snapshot_id="snapshot:approved",
            expected_evidence_identity_sha256="a" * 64,
        )
        wrong = score_extension_candidate_with_working_readback(
            extension_candidate=candidate,
            working_readback_items=(
                {**readback, "evidence_identity_sha256": "b" * 64},
            ),
            expected_evidence_snapshot_id="snapshot:approved",
            expected_evidence_identity_sha256="a" * 64,
        )
        self.assertEqual(empty["contribution"], 0)
        self.assertFalse(empty["matched"])
        self.assertEqual(matched["contribution"], 3)
        self.assertTrue(matched["matched"])
        self.assertFalse(matched["policy_authority_created"])
        self.assertEqual(wrong["contribution"], 0)
        self.assertFalse(wrong["matched"])

    def test_late_readback_and_stimulus_matching_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            validate_readback_loaded_before_candidate(
                readback_loaded_monotonic_ns=20,
                candidate_evaluated_monotonic_ns=10,
            )
        for key in (
            "experiment_id",
            "stimulus_config_hash",
            "stimulus_schedule",
            "expected_focus_grid",
            "expected_event_start_time",
            "expected_stop_time",
            "window_title",
            "process_id",
        ):
            with self.subTest(key=key), self.assertRaises(ValueError):
                reject_stimulus_matching_provenance({key: "forbidden"})

    def test_teacher_context_rejects_ground_truth_and_semantics(self) -> None:
        validate_canonical_evidence_context(
            {
                "scope": "low_level_active_perception_sequence_only",
                "semantic_boundaries": {
                    "object_identity": None,
                    "semantic_label": None,
                    "recognition": None,
                },
            }
        )
        with self.assertRaises(ValueError):
            validate_canonical_evidence_context(
                {"stimulus_schedule": {"open_at": 1}}
            )
        with self.assertRaises(ValueError):
            validate_canonical_evidence_context(
                {"object_identity": "object"}
            )
        lowered = TEACHER_INTERPRETATION.lower()
        for forbidden in (
            "object identity",
            "curiosity",
            "recognition",
            "causality",
        ):
            self.assertNotIn(forbidden, lowered)

    def test_process_and_artifact_guards_are_strict(self) -> None:
        self.assertTrue(_processes_distinct(1, 2))
        self.assertFalse(_processes_distinct(1, 1))
        self.assertTrue(
            _artifact_sets_distinct(("artifact:1",), ("artifact:2",))
        )
        self.assertFalse(
            _artifact_sets_distinct(("artifact:1",), ("artifact:1",))
        )
        self.assertTrue(
            _four_stage_lineage_complete(("a", "b", "c", "d"))
        )
        self.assertFalse(
            _four_stage_lineage_complete(("a", "b", "c"))
        )

    def test_store_is_append_only_and_empty_audit_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = Package129ActivePerceptionGrowthStore(temp_dir)
            payload = {
                "process_receipt_id": "receipt:1",
                "created_at": "2026-01-01T00:00:00+00:00",
            }
            store.append_payload(
                "active_perception_process_receipts",
                "process_receipt_id",
                "receipt:1",
                payload,
            )
            self.assertEqual(
                store.get_payload(
                    "active_perception_process_receipts",
                    "receipt:1",
                )["process_receipt_id"],
                "receipt:1",
            )
            with self.assertRaises(ValueError):
                store.append_payload(
                    "active_perception_process_receipts",
                    "process_receipt_id",
                    "receipt:1",
                    payload,
                )
            audit = audit_package_129_active_perception_growth(
                state_dir=temp_dir,
                append=False,
            )
            self.assertNotEqual(audit.audit_status, PASS_STATUS)
            self.assertTrue(audit.failure_reasons)

    def test_preflight_and_nonmutating_cli_views(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_package_129_preflight(state_dir=temp_dir)
            self.assertTrue(result["required_baseline_present"])
            self.assertEqual(result["branch"], "main")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = package_129_cli_main(
                    [
                        "show-comparison",
                        "--state-dir",
                        temp_dir,
                    ]
                )
            self.assertEqual(code, 0)
            self.assertIn("no_two_cycle_comparison", output.getvalue())

    def test_guided_run_stops_after_cycle_one_worker(self) -> None:
        worker_result = {
            "status": "cycle_1_waiting_teacher_review",
            "cycle_record": {
                "evidence_identity_hash": "a" * 64,
            },
        }
        output = io.StringIO()
        with (
            patch(
                "ashl_core_v1.runtime."
                "package_129_active_perception_growth_cli."
                "_run_cycle_worker",
                return_value=(worker_result, 0),
            ) as worker,
            contextlib.redirect_stdout(output),
        ):
            code = package_129_cli_main(
                ["guided-run", "--state-dir", "external-state"]
            )
        self.assertEqual(code, 0)
        worker.assert_called_once_with("external-state", 1)
        rendered = output.getvalue()
        self.assertIn("review-cycle-1", rendered)
        self.assertIn('"guided_run_terminated": true', rendered)
        self.assertIn('"cycle_2_started": false', rendered)

    def test_influence_record_rejects_policy_bypass(self) -> None:
        record = ActivePerceptionReadbackInfluenceRecord(
            influence_record_id="influence:1",
            schema_version=(
                "ashl_package_129_active_perception_readback_influence_v0"
            ),
            created_at="2026-01-01T00:00:00+00:00",
            cycle_1_working_readback_id="readback:1",
            cycle_2_stage_record_id="stage:2",
            cycle_2_internal_action_candidate_id="candidate:2",
            cycle_2_action_kind="extend_observation_window",
            package_112_scorer_id=(
                "host_body_readback_internal_action_influence"
            ),
            package_112_scorer_version=(
                "qingyin_host_body_internal_action_candidate_readback_score_v0"
            ),
            score_without_readback=5.0,
            score_with_readback=8.0,
            readback_contribution=3.0,
            influencing_readback_refs=("readback:1",),
            matching_evidence_refs=("snapshot:1",),
            actual_runtime_hot_path=True,
            hard_policy_gate_bypassed=False,
            hard_coded_experiment_match_used=False,
            stimulus_ground_truth_used=False,
            source_record_refs=("candidate:2",),
            source_trace_refs=("trace:1",),
        )
        with self.assertRaises(ValueError):
            replace(record, hard_policy_gate_bypassed=True)
        with self.assertRaises(ValueError):
            replace(record, readback_contribution=0.0)


@unittest.skipUnless(os.name == "nt", "real capture requires Windows")
class Package129RealTwoCycleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._temp = tempfile.TemporaryDirectory()
        root = Path(cls._temp.name)
        cls.state = root / "approved"
        cls.cycle_one_result, code = _run_cycle_worker(cls.state, 1)
        if code != 0:
            raise RuntimeError(cls.cycle_one_result)
        cycle = cls.cycle_one_result["cycle_record"]
        cls.identity = str(cycle["evidence_identity_hash"])

        cls.reject_state = root / "rejected"
        cls.defer_state = root / "deferred"
        cls.wrong_state = root / "wrong_identity"
        cls.scope_state = root / "wrong_scope"
        for target in (
            cls.reject_state,
            cls.defer_state,
            cls.wrong_state,
            cls.scope_state,
        ):
            shutil.copytree(cls.state, target)

        cls.approval = review_cycle_one(
            state_dir=cls.state,
            decision="approve",
            reviewer="local_teacher",
            expected_evidence_identity=cls.identity,
            approval_scope=FULL_COMMIT_APPROVAL_SCOPE,
            confirm=True,
        )
        cls.cycle_two_result, code = _run_cycle_worker(cls.state, 2)
        if code != 0:
            raise RuntimeError(cls.cycle_two_result)
        cls.audit = audit_package_129_active_perception_growth(
            state_dir=cls.state,
            append=True,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls._temp.cleanup()

    def test_cycle_one_exact_real_four_stage_sequence(self) -> None:
        self.assertEqual(
            self.cycle_one_result["status"],
            "cycle_1_waiting_teacher_review",
        )
        stages = self.cycle_one_result["stage_records"]
        self.assertEqual(
            tuple(item["internal_action_kind"] for item in stages),
            (
                "extend_observation_window",
                "shift_internal_perception_focus",
                "capture_again",
                "stop_observation",
            ),
        )
        self.assertTrue(
            self.cycle_one_result["sequence"]["structural_stop"][
                "stopped_before_hard_deadline"
            ]
        )
        self.assertGreaterEqual(
            self.cycle_one_result["sequence"]["focus"]["candidate_count"],
            2,
        )
        for stage in stages:
            for field in (
                "required_lane_drop_count",
                "backpressure_fault_count",
                "capture_failure_count",
                "compile_failure_count",
                "flush_remaining_count",
            ):
                self.assertEqual(stage[field], 0)

    def test_package_125_records_only_real_participating_lanes(self) -> None:
        stage = self.cycle_one_result["stage_records"][0]
        execution = Package125ObservationExtensionStore(
            self.state
        ).get_payload(
            "observation_extension_executions",
            stage["execution_record_id"],
        )
        self.assertEqual(
            tuple(execution["participating_lanes"]),
            ("screen", "host_state"),
        )
        self.assertTrue(execution["screen_deadline_updated"])
        self.assertTrue(execution["host_state_deadline_updated"])
        self.assertFalse(execution["audio_deadline_updated"])

    def test_cycle_one_exact_approval_commits_full_provenance(self) -> None:
        self.assertEqual(self.approval["status"], "cycle_1_committed")
        self.assertEqual(
            self.approval["teacher_decision"]["approval_scope"],
            FULL_COMMIT_APPROVAL_SCOPE,
        )
        self.assertEqual(
            self.approval["teacher_decision"][
                "target_evidence_identity_sha256"
            ],
            self.identity,
        )
        readback = self.approval["working_readback"]
        self.assertEqual(len(readback), 1)
        for field in (
            "source_reviewed_concept_ref",
            "memory_learning_trace_ref",
            "memory_routing_trace_ref",
            "memory_application_data_ref",
        ):
            self.assertTrue(readback[0][field])

    def test_teacher_snapshot_excludes_fixture_and_semantic_truth(self) -> None:
        cycle = self.cycle_one_result["cycle_record"]
        snapshot = TeacherGatedSessionStore(
            self.state
        ).load_evidence_snapshot(cycle["evidence_snapshot_id"])
        context = snapshot.canonical_evidence_payload[
            "canonical_evidence_context"
        ]
        serialized = str(context).lower()
        for forbidden in (
            "stimulus_schedule",
            "expected_selected_grid",
            "expected_stop_checkpoint",
            "expected_stop_time",
        ):
            self.assertNotIn(forbidden, serialized)
        semantic = context["semantic_boundaries"]
        self.assertTrue(all(value is None for value in semantic.values()))

    def test_cycle_two_is_new_process_with_fresh_evidence(self) -> None:
        first = self.cycle_one_result["cycle_record"]
        second = self.cycle_two_result["cycle_record"]
        self.assertNotEqual(
            first["operating_system_process_id"],
            second["operating_system_process_id"],
        )
        self.assertNotEqual(
            first["process_instance_id"],
            second["process_instance_id"],
        )
        for field in (
            "parent_runtime_session_id",
            "parent_perception_session_id",
            "parent_observation_window_id",
            "child_runtime_session_id",
            "child_perception_session_id",
            "child_observation_window_id",
            "experiment_run_id",
        ):
            self.assertNotEqual(first[field], second[field], field)
        comparison = self.cycle_two_result["comparison"]
        self.assertTrue(comparison["raw_artifacts_distinct"])
        self.assertTrue(comparison["stimulus_config_hash_equal"])
        self.assertTrue(comparison["source_plan_hash_equal"])

    def test_cycle_two_preloads_readback_and_uses_package_112(self) -> None:
        timing = self.cycle_two_result["readback_load_timing"]
        for field in (
            "loaded_before_parent_capture",
            "loaded_before_candidate_evaluation",
            "loaded_before_action_scoring",
            "loaded_before_action_execution",
        ):
            self.assertTrue(timing[field])
        influence = self.cycle_two_result["readback_influence"]
        self.assertEqual(
            influence["package_112_scorer_id"],
            "host_body_readback_internal_action_influence",
        )
        self.assertEqual(
            influence["cycle_2_action_kind"],
            "extend_observation_window",
        )
        self.assertEqual(influence["score_without_readback"], 5.0)
        self.assertEqual(influence["score_with_readback"], 8.0)
        self.assertGreater(influence["readback_contribution"], 0)
        self.assertTrue(influence["actual_runtime_hot_path"])
        self.assertFalse(influence["hard_policy_gate_bypassed"])
        self.assertFalse(influence["hard_coded_experiment_match_used"])
        self.assertFalse(influence["stimulus_ground_truth_used"])

    def test_cycle_two_remains_unapproved_and_uncommitted(self) -> None:
        cycle = self.cycle_two_result["cycle_record"]
        self.assertEqual(
            cycle["final_session_state"],
            "WAITING_TEACHER_REVIEW",
        )
        preservation = self.cycle_two_result[
            "cycle_2_review_preservation"
        ]
        self.assertEqual(preservation["teacher_decision_count"], 0)
        self.assertEqual(preservation["reviewed_memory_commit_count"], 0)
        self.assertTrue(preservation["preserved_unresolved"])
        teacher_store = TeacherGatedSessionStore(self.state)
        self.assertEqual(
            teacher_store.count_rows(
                "teacher_decisions",
                cycle["bounded_embodied_session_id"],
            ),
            0,
        )

    def test_all_twelve_controls_pass(self) -> None:
        controls = self.cycle_two_result["controls"]
        self.assertEqual(len(controls), 12)
        self.assertTrue(all(controls.values()))

    def test_reject_and_defer_create_no_readback_and_block_cycle_two(
        self,
    ) -> None:
        rejected = review_cycle_one(
            state_dir=self.reject_state,
            decision="reject",
            reviewer="local_teacher",
            expected_evidence_identity=self.identity,
            approval_scope=FULL_COMMIT_APPROVAL_SCOPE,
            confirm=True,
        )
        deferred = review_cycle_one(
            state_dir=self.defer_state,
            decision="defer",
            reviewer="local_teacher",
            expected_evidence_identity=self.identity,
            approval_scope=FULL_COMMIT_APPROVAL_SCOPE,
            confirm=True,
        )
        self.assertNotEqual(rejected["status"], "cycle_1_committed")
        self.assertNotEqual(deferred["status"], "cycle_1_committed")
        for state in (self.reject_state, self.defer_state):
            self.assertEqual(
                TeacherGatedSessionStore(
                    state
                ).load_active_working_readback(),
                tuple(),
            )
            blocked, code = _run_cycle_worker(state, 2)
            self.assertNotEqual(code, 0)
            self.assertIn("blocked", blocked["status"])

    def test_wrong_identity_and_scope_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            review_cycle_one(
                state_dir=self.wrong_state,
                decision="approve",
                reviewer="local_teacher",
                expected_evidence_identity="0" * 64,
                approval_scope=FULL_COMMIT_APPROVAL_SCOPE,
                confirm=True,
            )
        with self.assertRaises(ValueError):
            review_cycle_one(
                state_dir=self.scope_state,
                decision="approve",
                reviewer="local_teacher",
                expected_evidence_identity=self.identity,
                approval_scope="teacher_decision_only",
                confirm=True,
            )

    def test_cli_views_and_audit_are_operator_only(self) -> None:
        for command in (
            "show-cycle-1-review",
            "show-readback-influence",
            "show-comparison",
            "audit",
        ):
            with self.subTest(command=command):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    code = package_129_cli_main(
                        [
                            command,
                            "--state-dir",
                            str(self.state),
                        ]
                    )
                self.assertEqual(code, 0)
        self.assertEqual(
            build_default_console_store(self.state).list_payloads(
                "raw_output_sequences"
            ),
            tuple(),
        )

    def test_final_audit_passes_without_capability_expansion(self) -> None:
        self.assertEqual(self.audit.audit_status, PASS_STATUS)
        self.assertEqual(self.audit.failure_reasons, tuple())
        self.assertEqual(self.audit.cycle_2_readback_contribution, 3.0)
        for field in (
            "new_perception_action_kind_created",
            "new_sensor_source_created",
            "new_primitive_compiler_created",
            "new_focus_mode_created",
            "new_sufficiency_contract_kind_created",
            "semantic_vision_created",
            "object_recognition_created",
            "auditory_concept_created",
            "auditory_prediction_created",
            "uncertainty_signal_created",
            "novelty_signal_created",
            "curiosity_signal_created",
            "thought_engine_used",
            "endocrine_signal_used",
            "qingyin_output_created",
            "external_control_created",
            "package_130_implemented",
            "package_131_implemented",
            "package_132_milestone_claimed",
            "d_laplace_component_used",
            "dlm_1_implemented",
        ):
            self.assertFalse(getattr(self.audit, field), field)
        self.assertEqual(self.audit.llm_runtime_calls, 0)
        self.assertEqual(self.audit.codex_runtime_calls, 0)
        self.assertEqual(self.audit.network_runtime_calls, 0)

    def test_raw_artifacts_are_not_copied_into_package_129_store(self) -> None:
        package_root = (
            Path(self.state)
            / "package_129_active_perception_growth_v0"
        )
        self.assertEqual(
            {item.name for item in package_root.iterdir()},
            {"package_129.sqlite3"},
        )
        cycle = Package129ActivePerceptionGrowthStore(
            self.state
        ).latest_cycle(2)
        execution = Package126ReacquisitionStore(
            self.state
        ).get_payload(
            "reacquisition_capture_executions",
            self.cycle_two_result["stage_records"][2][
                "execution_record_id"
            ],
        )
        self.assertEqual(
            execution["child_observation_window_id"],
            cycle["child_observation_window_id"],
        )


if __name__ == "__main__":
    unittest.main()
